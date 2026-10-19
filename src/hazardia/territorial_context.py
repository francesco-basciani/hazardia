"""Bounded mapped exposure and overhead-wire context. No aviation authorization."""
import datetime as dt,hashlib,json,math,sys,urllib.request,urllib.parse,uuid
from pathlib import Path
from hazardia.io import load,write_new,sha256,utcnow,HazardError
PROVIDERS=('https://overpass.private.coffee/api/interpreter','https://overpass-api.de/api/interpreter','https://maps.mail.ru/osm/tools/overpass/api/interpreter')
AIR=('canadair','helicopter')
AVIATION_MISSING=['Complete obstacle inventory','Conductor height and sag','Flight paths and terrain clearance','Aircraft/crew night qualification and operational authority']
def bounds_checked(b):
 if not isinstance(b,list) or len(b)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in b):raise HazardError('INVALID_INPUT','Finite bounds [west,south,east,north] required')
 x,y,X,Y=b
 if not (-180<=x<X<=180 and -80<=y<Y<=80):raise HazardError('INVALID_INPUT','Invalid geographic bounds')
 if X-x>1 or Y-y>1:raise HazardError('AREA_TOO_LARGE','Ingrandisci la mappa: contesto dettagliato disponibile per aree fino a1°×1°')
 return b

def parse_osm(raw):
 features=[];skipped=0
 for e in raw.get('elements',[]):
  t=e.get('tags',{});power=t.get('power');g=e.get('geometry',[]);category=None;geometry=None
  if power in ('line','minor_line','cable'):
   if t.get('location') in ('underground','underwater') or power=='cable' and t.get('location')!='overhead':continue
   if 2<=len(g)<=2000:category='power_line';geometry=dict(type='LineString',coordinates=[[p['lon'],p['lat']] for p in g])
  elif power in ('tower','pole') and 'lat' in e:category='power_tower';geometry=dict(type='Point',coordinates=[e['lon'],e['lat']])
  else:
   category={'hospital':'hospital','school':'school','fire_station':'fire_station'}.get(t.get('amenity'),'residential' if t.get('landuse')=='residential' else 'settlement' if t.get('place') in ('city','town','village','hamlet') else None)
   c=e.get('center',e)
   if category and c.get('lat') is not None:geometry=dict(type='Point',coordinates=[c['lon'],c['lat']])
   if category and 4<=len(g)<=2000 and g[0]==g[-1]:geometry=dict(type='Polygon',coordinates=[[[p['lon'],p['lat']] for p in g]])
  if not category or not geometry:skipped+=1;continue
  props=dict(name=t.get('name') or t.get('ref') or {'power_line':'Linea elettrica','power_tower':'Sostegno elettrico'}.get(category,category+' OSM'),category=category,source='OpenStreetMap',osm_type=e['type'],osm_id=e['id'])
  for k in ('voltage','height','operator','ref','location','power','cables','wires'):props[k]=t.get(k)
  features.append(dict(type='Feature',id=f'osm-{e["type"]}-{e["id"]}',geometry=geometry,properties=props))
 return features,skipped

def local_context(root,bounds):
 """Reuse verified existing snapshots; never extrapolate their geographic coverage."""
 root=Path(root);x,y,X,Y=bounds;features=[];sources=[];names=root/'web-assets/map-context.json'
 if names.exists():
  data=load(names);sources.append(dict(name='GeoNames / cached cartographic context',sha256=sha256(names),available_at=data.get('timestamp')))
  for f in data.get('features',[]):
   if f.get('kind')=='place' and f.get('provider')=='GeoNames' and x<=f['lon']<=X and y<=f['lat']<=Y:
    features.append(dict(type='Feature',id='geonames-'+str(f['id']),geometry=dict(type='Point',coordinates=[f['lon'],f['lat']]),properties=dict(name=f['name'],category='settlement',source='GeoNames CC BY4.0; cached locality point, not a town boundary',optimization_eligible=False)))
 raw=root/'runs/map-detail-20261015T204352Z/osm-map-final-raw.json';catalog=root/'web-assets/priority-areas.json'
 if raw.exists() and catalog.exists() and sha256(raw)==load(catalog).get('source_sha256'):
  data=load(raw);nodes={e['id']:dict(lat=e['lat'],lon=e['lon']) for e in data['elements'] if e['type']=='node'};elements=[]
  for e in data['elements']:
   e=dict(e)
   if e['type']=='way':
    g=[nodes[n] for n in e.get('nodes',[]) if n in nodes]
    if not g:continue
    e.update(geometry=g,center=dict(lat=sum(p['lat'] for p in g)/len(g),lon=sum(p['lon'] for p in g)/len(g)))
   elements.append(e)
  mapped,_=parse_osm(dict(elements=elements))
  for f in mapped:
   g=f['geometry'];pts=[g['coordinates']] if g['type']=='Point' else g['coordinates'][0] if g['type']=='Polygon' else g['coordinates']
   if max(p[0] for p in pts)>=x and min(p[0] for p in pts)<=X and max(p[1] for p in pts)>=y and min(p[1] for p in pts)<=Y:
    f['properties']['source']='OpenStreetMap cached extract15Oct2026, partial';features.append(f)
  sources.append(dict(name='OSM cached local extract',sha256=sha256(raw),coverage_bbox=load(catalog)['coverage_bbox_wgs84'],source_url=load(catalog)['source_url']))
 for file in sorted((root/'territorial-imports').glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:20]:
  if file.stat().st_size>4*1024**2:continue
  imported=load(file)
  if imported.get('license')!='ODbL-1.0':continue
  sources.append({k:imported.get(k) for k in ['source_url','source_sha256','source_available_at','source_data_at','available_at','coverage_bbox_wgs84']})
  for f in imported['features']:
   def points(a):return [a] if isinstance(a[0],(int,float)) else [p for child in a for p in points(child)]
   pts=points(f['geometry']['coordinates'])
   if max(p[0] for p in pts)>=x and min(p[0] for p in pts)<=X and max(p[1] for p in pts)>=y and min(p[1] for p in pts)<=Y:features.append(f)
 unique={f['id']:f for f in features};return list(unique.values()),sources

def acquire(root,bounds,terrain_id=None):
 root=Path(root);bounds_checked(bounds);key=hashlib.sha256(json.dumps([bounds,terrain_id,'context/5'],sort_keys=True).encode()).hexdigest()[:24];dest=root/'web-state/territorial-cache'/key;dest.mkdir(parents=True,exist_ok=True)
 for p in sorted(dest.glob('snapshot-*.json'),key=lambda p:p.stat().st_mtime,reverse=True):
  v=load(p)
  if (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(v['available_at'].replace('Z','+00:00'))).total_seconds()<(300 if v.get('osm_status')=='MISSING' else 10800):return v
 x,y,X,Y=bounds;box=f'{y},{x},{Y},{X}'
 query=f'[out:json][timeout:12];(nwr[amenity~"^(hospital|school|fire_station)$"]({box});way[landuse=residential]({box});node[place~"^(city|town|village|hamlet)$"]({box});way[power~"^(line|minor_line|cable)$"]({box});node[power~"^(tower|pole)$"]({box}););out center geom 2000;'
 errors=[];features=[];source=None;truncated=False;raw_hash=None;quota=root/'web-state/priority-requests';quota.mkdir(parents=True,exist_ok=True);today=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d');skipped=0
 for url in PROVIDERS:
  if len(list(quota.glob(today+'-*')))>=10:errors.append('SOURCE_QUOTA: local daily OSM budget reached');break
  write_new(quota/(today+'-'+uuid.uuid4().hex+'.json'),dict(at=utcnow(),bounds=bounds,source=url))
  try:
   req=urllib.request.Request(url+'?'+urllib.parse.urlencode({'data':query}),headers={'User-Agent':'HAZARDIA-research/0.1'})
   with urllib.request.urlopen(req,timeout=14) as response:data=response.read(2*1024**2+1)
   if len(data)>2*1024**2:raise ValueError('Response exceeds2MiB')
   raw=json.loads(data)
   if raw.get('remark'):raise ValueError('Incomplete query: '+raw['remark'])
   if not isinstance(raw.get('elements'),list):raise ValueError('Missing elements')
   features,skipped=parse_osm(raw);truncated=len(raw['elements'])>=2000 or skipped>0;source=url;raw_hash=hashlib.sha256(data).hexdigest();write_new(dest/('raw-'+uuid.uuid4().hex+'.json'),raw);break
  except Exception as e:errors.append(url+': '+str(e))
 # Last bounded fallback: one small official OSM map extract, never a whole-country dump.
 osm_bounds=bounds
 if source is None and len(list(quota.glob(today+'-*')))<10:
  try:
   import xml.etree.ElementTree as ET
   cx,cy=(x+X)/2,(y+Y)/2;osm_bounds=[max(x,cx-.06),max(y,cy-.06),min(X,cx+.06),min(Y,cy+.06)]
   url='https://api.openstreetmap.org/api/0.6/map?'+urllib.parse.urlencode({'bbox':','.join(map(str,osm_bounds))})
   write_new(quota/(today+'-'+uuid.uuid4().hex+'.json'),dict(at=utcnow(),bounds=osm_bounds,source='https://api.openstreetmap.org/api/0.6/map'))
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HAZARDIA-research/0.1'}),timeout=14) as response:data=response.read(4*1024**2+1)
   if len(data)>4*1024**2:raise ValueError('Official map extract exceeds4MiB')
   xml=ET.fromstring(data);nodes={e.attrib['id']:dict(lat=float(e.attrib['lat']),lon=float(e.attrib['lon'])) for e in xml.findall('node')};elements=[]
   for e in xml:
    tags={t.attrib['k']:t.attrib['v'] for t in e.findall('tag')}
    if e.tag=='node':elements.append(dict(type='node',id=int(e.attrib['id']),tags=tags,**nodes[e.attrib['id']]))
    elif e.tag=='way':
     g=[nodes[n.attrib['ref']] for n in e.findall('nd') if n.attrib['ref'] in nodes]
     if g:elements.append(dict(type='way',id=int(e.attrib['id']),tags=tags,geometry=g,center=dict(lat=sum(p['lat'] for p in g)/len(g),lon=sum(p['lon'] for p in g)/len(g))))
   raw=dict(elements=elements);features,_=parse_osm(raw);source='https://api.openstreetmap.org/api/0.6/map';raw_hash=hashlib.sha256(data).hexdigest();(dest/('raw-'+uuid.uuid4().hex+'.osm')).write_bytes(data);truncated=True
  except Exception as e:errors.append('Official OSM small extract: '+str(e))
 missing=['Population and occupancy','Vulnerability','OSM completeness',*AVIATION_MISSING]
 if not any(f['properties']['category'] in ('settlement','residential') for f in features) and terrain_id:
  from hazardia.ingest.fire_priorities import builtup
  fallback=builtup(root,terrain_id,bounds,'; '.join(errors) or 'No mapped residential geometry in this query',limit=1200,min_area=900)
  features+=fallback['features'];missing+=fallback['missing']
 local,sources=local_context(root,bounds);known={f['id'] for f in features};features=[f for f in local if f['id'] not in known]+features
 result=dict(type='FeatureCollection',sources=sources,schema='territorial-context/1',features=features,coverage_bbox_wgs84=bounds,osm_coverage_bbox_wgs84=osm_bounds if source else None,available_at=utcnow(),source_url=source or ('https://esa-worldcover.org/en/data-access' if any('WorldCover' in f['properties'].get('source','') for f in features) else 'https://www.openstreetmap.org/copyright' if any(f['id'].startswith('osm-') for f in features) else 'https://www.geonames.org/' if features else None),source_data_at=raw.get('osm3s',{}).get('timestamp_osm_base') if source else None,source_sha256=raw_hash or hashlib.sha256(json.dumps(features,sort_keys=True).encode()).hexdigest(),osm_status='PARTIAL' if source else 'CACHED_PARTIAL' if any(f['id'].startswith('osm-') for f in features) else 'MISSING',truncated_possible=truncated,errors=errors,missing=missing,license='ODbL OpenStreetMap; GeoNames CC BY4.0; WorldCover2021 CC BY4.0 where present',qualification='PARTIAL_MAPPED_EXPOSURE_NOT_OPERATIONAL_RISK',aviation=dict(qualified=False,missing=AVIATION_MISSING,absence_of_mapped_lines_proves_clearance=False))
 write_new(dest/('snapshot-'+uuid.uuid4().hex+'.json'),result);return result

def assess(root,job_id):
 import numpy as np
 from rasterio.transform import Affine
 from rasterio.features import geometry_mask
 from pyproj import Transformer
 from shapely.geometry import shape,mapping
 from shapely.ops import transform
 root=Path(root);job=root/'jobs'/job_id;req=load(job/'request.json');manifest=load(job/'manifest.json');series=load(job/'fire-series.json')
 for n in ('fire-output.npz','fire-series.json'):
  if sha256(job/n)!=manifest['artifacts'][n]:raise HazardError('CHECKSUM','Native product changed')
 b=req['territory']['bbox_wgs84'];terrain=series['plan'].get('forcing',{}).get('terrain_id');data=acquire(root,b,terrain);data=json.loads(json.dumps(data));tr=Affine(*req['grid']['transform']);project=Transformer.from_crs(4326,req['grid']['crs'],always_xy=True).transform
 with np.load(job/'fire-output.npz',allow_pickle=False) as a:p=a['probability'];arrival=a['arrival'];burned=a['fire']
 duration=req['options']['duration_s'];times=np.arange(0,duration+1,900);count=0
 for f in data['features']:
  if f['properties']['category'].startswith('power_'):continue
  if count>=1600:f['exposure']=dict(status='NOT_EVALUATED_LIMIT');continue
  geom=transform(project,shape(f['geometry']));geom=geom.buffer(75 if geom.geom_type=='Point' else 100);mask=geometry_mask([mapping(geom)],p.shape,tr,invert=True);n=int(mask.sum());count+=1
  if not n:f['exposure']=dict(status='OUTSIDE_MODEL_GRID');continue
  values=arrival[mask];hits=(burned[mask]>0)&np.isfinite(values)&(values>=0);reached=np.sort(values[hits]);first=np.min(np.where(hits,values,np.inf),axis=0);first=first[np.isfinite(first)]
  f['exposure']=dict(status='MODELLED',cells=n,probability_final_mean=float(p[mask].mean()),probability_final_max=float(p[mask].max()),probability_contact_final=float(len(first)/arrival.shape[2]),timeline_contact=(np.searchsorted(np.sort(first),times,side='right')/arrival.shape[2]).tolist(),timeline_mean=(np.searchsorted(reached,times,side='right')/(n*arrival.shape[2])).tolist(),first_contact_minutes=float(first.min()/60) if len(first) else None,median_contact_minutes=float(np.median(first)/60) if len(first) else None,contact_members=int(len(first)),realizations=int(arrival.shape[2]),analysis='Mapped polygon plus100m / point75m research buffer; conditional stochastic contact, no population estimate')
 data.update(job_id=job_id,valid_from=req['valid_from'],valid_until=req['valid_until'],step_s=900,native_sha256=manifest['artifacts']['fire-output.npz'],evaluated_features=count,qualification='CONDITIONAL_NATIVE_EXPOSURE_UNCALIBRATED_NOT_OFFICIAL_ALERT')
 return data

if __name__=='__main__':
 root,request,out=sys.argv[1:];body=load(request)
 try:write_new(out,assess(root,body['job_id']) if 'job_id' in body else acquire(root,body['bounds']))
 except Exception as e:write_new(str(out)+'.error',dict(code=e.code if isinstance(e,HazardError) else 'CONTEXT_FAILED',detail=str(e)));raise
