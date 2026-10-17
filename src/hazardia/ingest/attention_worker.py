"""Bounded real-source acquisition in the existing geospatial VM environment.
Never manufactures warning levels or infers inundation from rainfall.
"""
import datetime as dt
import hashlib
import json
import math
import re
import sys
import time
import urllib.request
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

DPC='https://api.github.com/repos/'
RAW='https://raw.githubusercontent.com/'
EFFIS='https://maps.effis.emergency.copernicus.eu/effis?'
FWI=[11.2,21.3,38.,50.,70.]
DC=[256.1,334.1,450.6,600.,749.4]

def classify(value,thresholds):
    # WMS TIFF has no declared nodata; zero cannot distinguish sea/no-data from true zero.
    if not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:return None
    return sum(value>=v for v in thresholds[:-1])+int(value>thresholds[-1])

def level(value):
    if not isinstance(value,str):return None
    upper=value.upper()
    for text,n in [('ALLERTA ROSSA',3),('ALLERTA ARANCIONE',2),('ALLERTA GIALLA',1),('NESSUNA ALLERTA',0)]:
        if text in upper:return n
    return None

def topology(raw):
    """Decode original TopoJSON without coordinate simplification or reprojection."""
    if raw.get('type')!='Topology':raise ValueError('Expected DPC topology')
    scale=raw['transform']['scale'];translate=raw['transform']['translate'];arcs=[]
    for arc in raw['arcs']:
        x=y=0;points=[]
        for a,b in arc:
            x+=a;y+=b;lon=x*scale[0]+translate[0];lat=y*scale[1]+translate[1]
            if not (6<=lon<=20 and 35<=lat<=49):raise ValueError('DPC coordinate outside Italian source coverage')
            points.append([lon,lat])
        arcs.append(points)
    def ring(indices):
        points=[]
        for i in indices:
            part=arcs[i] if i>=0 else list(reversed(arcs[~i]))
            points.extend(part if not points else part[1:])
        if len(points)<4 or points[0]!=points[-1]:raise ValueError('Unclosed DPC ring')
        return points
    objs=list(raw['objects'].values())
    if len(objs)!=1 or objs[0]['type']!='GeometryCollection':raise ValueError('Unexpected DPC objects')
    features=[]
    for i,g in enumerate(objs[0]['geometries']):
        if g['type']=='Polygon':coords=[ring(a) for a in g['arcs']]
        elif g['type']=='MultiPolygon':coords=[[ring(a) for a in p] for p in g['arcs']]
        else:raise ValueError('Unexpected DPC geometry')
        p=g.get('properties',{});keys=['Per rischio idraulico','Per rischio temporali','Per rischio idrogeologico']
        values={k:p.get(k) for k in keys};levels={k:level(v) for k,v in values.items()}
        features.append(dict(type='Feature',geometry=dict(type=g['type'],coordinates=coords),properties=dict(id=str(i),name=p.get('Nome zona','Zona senza nome'),municipalities=p.get('Comuni',[]),reasons=values,levels=levels,level=max(levels.values()) if all(v is not None for v in levels.values()) else None)))
    if not 50<=len(features)<=250:raise ValueError('Unexpected number of DPC zones')
    return dict(type='FeatureCollection',features=features)

class Acquisition:
    def __init__(self,folder):self.folder=Path(folder);self.receipts=[];self.reference=None;self.total=0
    def fetch(self,url,label,cap=2*1024**2):
        if not url.startswith((DPC,RAW,EFFIS)):raise ValueError('Source outside allowlist')
        req=urllib.request.Request(url,headers={'User-Agent':'HAZARDIA/0.1 research','Accept-Encoding':'identity','Cache-Control':'no-cache'})
        with urllib.request.urlopen(req,timeout=25) as response:
            if response.status!=200 or not response.geturl().startswith((DPC,RAW,EFFIS)):raise ValueError('Unexpected source response')
            data=response.read(cap+1)
            if len(data)>cap:raise ValueError('Source size limit exceeded')
            date=response.headers.get('Date')
            epoch=parsedate_to_datetime(date).timestamp() if date else None
            if epoch:self.reference=max(self.reference or epoch,epoch)
        self.total+=len(data)
        if self.total>16*1024**2:raise ValueError('Acquisition total exceeds16MiB')
        (self.folder/label).write_bytes(data)
        rec=dict(url=url,file=label,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),retrieved_local_epoch=time.time(),http_date=date)
        self.receipts.append(rec);return data
    def js(self,url,label,cap=2*1024**2):return json.loads(self.fetch(url,label,cap))

def dpc(acq,profile):
    from shapely.geometry import shape,mapping
    repo=profile['dpc_repository'];commits=acq.js(DPC+repo+'/commits?path=files&per_page=1','dpc-head.json')
    head=commits[0]['sha']
    if not re.fullmatch('[a-f0-9]{40}',head):raise ValueError('Invalid DPC revision')
    detail=acq.js(DPC+repo+'/commits/'+head,'dpc-commit.json')
    candidates=[m.group(1) for f in detail.get('files',[]) if (m:=re.search(r'(\d{8}_\d{4})',f['filename']))]
    if not candidates:raise ValueError('No bulletin timestamp in latest source revision')
    ident=max(candidates);prefix=RAW+repo+'/'+head+'/'
    bulletin=acq.js(prefix+'files/'+ident+'.json','dpc-bulletin.json')
    stamp=dt.datetime.strptime(ident,'%Y%m%d_%H%M').replace(tzinfo=ZoneInfo('Europe/Rome'))
    issued_at=stamp.astimezone(dt.timezone.utc).isoformat().replace('+00:00','Z')
    products=[]
    for offset,key in enumerate(['today','tomorrow']):
        # Build pinned paths; ignore arbitrary URLs and all untrusted bulletin HTML.
        path='files/topojson/'+ident+'_'+key+'.json'
        geo=topology(acq.js(prefix+path,'dpc-'+key+'.json'))
        for feature in geo['features']:
            geom=shape(feature['geometry'])
            feature['properties']['source_geometry_valid']=geom.is_valid
            feature['geometry']=mapping(geom.simplify(.001,preserve_topology=True))
            feature['properties']['cartographic_simplification_degrees']=.001
            if not geom.is_valid:
                feature['properties']['source_level']=feature['properties']['level']
                feature['properties']['level']=None
                feature['properties']['geometry_warning']='Source geometry invalid after TopoJSON decoding; classification withheld on this footprint'
        valid=(stamp+dt.timedelta(days=offset)).date().isoformat()
        name='dpc-'+valid+'.geojson';(acq.folder/name).write_text(json.dumps(geo,separators=(',',':')))
        end=dt.datetime.combine(stamp.date()+dt.timedelta(days=offset+1),dt.time.min,ZoneInfo('Europe/Rome'))
        products.append(dict(day=valid,file=name,valid_until=end.astimezone(dt.timezone.utc).isoformat().replace('+00:00','Z'),zones=len(geo['features']),unknown_zones=sum(f['properties']['level'] is None for f in geo['features']),attention_zones=sum(f['properties']['level'] is not None and f['properties']['level']>0 for f in geo['features'])))
    return dict(provider='Dipartimento della Protezione Civile',kind='OFFICIAL_BULLETIN',license='CC-BY-4.0',source_url='https://github.com/'+repo,issued_at=issued_at,bulletin_metadata_date=bulletin.get('date'),name=bulletin.get('name',ident),revision=head,products=products)

def effis(acq,profile,day):
    import rasterio
    bounds=profile['bounds'];width,height=profile['display_grid'];arrays={};receipts=[]
    for var in ['fwi','dc']:
        label=var+'-'+day+'.tif'
        params=dict(SERVICE='WMS',VERSION='1.1.1',REQUEST='GetMap',FORMAT='image/tiff',LAYERS=profile['effis_model']+'.'+var,STYLES='',SRS='EPSG:4326',BBOX=','.join(map(str,bounds)),WIDTH=width,HEIGHT=height,TIME=day)
        acq.fetch(EFFIS+urlencode(params),label,1024**2)
        with rasterio.open(acq.folder/label) as src:
            if src.count!=1 or src.shape!=(height,width) or str(src.crs)!='EPSG:4326' or any(abs(a-b)>1e-5 for a,b in zip(src.bounds,bounds)):raise ValueError('Unexpected EFFIS TIFF georeference')
            arrays[var]=src.read(1,masked=True).filled(float('nan'))
    features=[];x0,y0,x1,y1=bounds;dx=(x1-x0)/width;dy=(y1-y0)/height
    for row in range(height):
        for col in range(width):
            fwi=float(arrays['fwi'][row,col]);dc=float(arrays['dc'][row,col]);fc=classify(fwi,FWI);dcclass=classify(dc,DC)
            if fc is None and dcclass is None:continue
            left=x0+col*dx;top=y1-row*dy;right=left+dx;bottom=top-dy
            coords=[[round(left,6),round(top,6)],[round(right,6),round(top,6)],[round(right,6),round(bottom,6)],[round(left,6),round(bottom,6)],[round(left,6),round(top,6)]]
            features.append(dict(type='Feature',geometry=dict(type='Polygon',coordinates=[coords]),properties=dict(id=f'{row}-{col}',fwi=round(fwi,3) if fc is not None else None,dc=round(dc,3) if dcclass is not None else None,level=fc,dc_level=dcclass)))
    if not features:raise ValueError('No positive EFFIS values: source coverage unverified')
    name='effis-'+day+'.geojson';(acq.folder/name).write_text(json.dumps(dict(type='FeatureCollection',features=features),separators=(',',':')))
    return dict(day=day,file=name,valid_until=day+'T23:59:59Z',cells=len(features),attention_cells=sum(f['properties']['level'] is not None and f['properties']['level']>=1 for f in features))

def run(folder,profile_path):
    folder=Path(folder);profile=json.loads(Path(profile_path).read_text());acq=Acquisition(folder);sources={}
    try:
        source=dpc(acq,profile)
        sources['dpc']=dict(status='PARTIAL' if any(p['unknown_zones'] for p in source['products']) else 'AVAILABLE',**source)
    except Exception as e:sources['dpc']=dict(status='UNAVAILABLE',error=type(e).__name__+': '+str(e)[:240])
    now=dt.datetime.fromtimestamp(acq.reference or time.time(),dt.timezone.utc);products=[];errors=[]
    for offset in range(profile['days']):
        day=(now+dt.timedelta(days=offset)).date().isoformat()
        try:products.append(effis(acq,profile,day))
        except Exception as e:errors.append(dict(day=day,error=type(e).__name__+': '+str(e)[:240]))
    sources['effis']=dict(status='AVAILABLE' if products and not errors else 'PARTIAL' if products else 'UNAVAILABLE',provider='EFFIS / Copernicus EMS · Météo-France',kind='FIRE_WEATHER_DANGER_FORECAST',license='CC-BY-4.0',source_url='https://forest-fire.emergency.copernicus.eu/about-effis/technical-background/fire-danger-forecast',issued_at=None,issued_at_status='NOT_SUPPLIED_BY_WMS',native_resolution_km=profile['native_resolution_km'],sampling_grid_deg=.1,products=products,errors=errors,bounds=profile['bounds'],zero_policy='Zero/nonfinite is unknown: WMS does not distinguish missing coverage from true zero')
    local=max((r['retrieved_local_epoch'] for r in acq.receipts),default=time.time());ref=acq.reference
    result=dict(schema_version='0.1.0',profile=profile['id'],sources=sources,receipts=acq.receipts,download_bytes=acq.total,local_epoch=local,reference_epoch=ref,clock_offset_s=None if ref is None else ref-local,acquired_at=dt.datetime.fromtimestamp(ref or local,dt.timezone.utc).isoformat().replace('+00:00','Z'),missing=['Live satellite hotspots','Radar / rain and river gauges','Qualified soil saturation','Local fuel and vulnerability inventories','Validated local impact-risk model'],qualification='RESEARCH_SITUATIONAL_AWARENESS_NOT_DISPATCH')
    result['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}
    (folder/'result.json').write_text(json.dumps(result,separators=(',',':')))

if __name__=='__main__':run(*sys.argv[1:])
