"""Optional consultation adapters. No imports from decision/model workers.
Bounded asynchronous acquisition, explicit source time/coverage and missing data.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import math
import re
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from hazardia.io import HazardError, utcnow
from hazardia.osm_catalog import parse_osm

SOURCES = {'ingv':'https://webservices.ingv.it/fdsnws/event/1/query',
           'usgs':'https://earthquake.usgs.gov/fdsnws/event/1/query'}
POWER_SOURCE = 'https://overpass.private.coffee/api/interpreter'

def bounds(value):
    if not isinstance(value,list) or len(value)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in value):
        raise HazardError('INVALID_INPUT','Four finite WGS84 bounds required')
    w,s,e,n=value
    if not -180<=w<e<=180 or not -85<=s<n<=85:
        raise HazardError('INVALID_INPUT','Invalid bounds; dateline-crossing views must be narrowed')
    rounded=[round(v,5) for v in value]
    if rounded[0]>=rounded[2] or rounded[1]>=rounded[3]:raise HazardError('INVALID_INPUT','Area too small after coordinate quantization')
    return rounded

def voltage_values(value):
    """OSM volts, including multi-circuit values. Never infer from power=line."""
    if not isinstance(value,str):return []
    return sorted({int(v.strip()) for v in value.split(';') if re.fullmatch(r'\d{2,7}',v.strip()) and 0<int(v.strip())<=2000000})

def power_features(raw):
    if raw.lstrip().startswith(b'<'):
        root=ET.fromstring(raw);nodes={n.get('id'):n for n in root.findall('node')};elements=[]
        for e in list(root.findall('node'))+list(root.findall('way')):
            tags={t.get('k'):t.get('v') for t in e.findall('tag')}
            if tags.get('power') not in ('line','minor_line','cable','tower','pole','substation'):continue
            item=dict(type=e.tag,id=int(e.get('id')),tags=tags,version=e.get('version'),timestamp=e.get('timestamp'))
            if e.tag=='node':item.update(lat=float(e.get('lat')),lon=float(e.get('lon')))
            else:
                ids=[n.get('ref') for n in e.findall('nd')]
                if all(i in nodes for i in ids):item['geometry']=[dict(lat=float(nodes[i].get('lat')),lon=float(nodes[i].get('lon'))) for i in ids]
            elements.append(item)
        data=dict(elements=elements,osm3s=dict(timestamp_osm_base=None))
    else:data=json.loads(raw)
    if data.get('remark'):raise ValueError('Incomplete Overpass response: '+data['remark'])
    elements=data.get('elements')
    if not isinstance(elements,list):raise ValueError('Invalid OSM response')
    if len(elements)>5000:raise ValueError('More than5000 power objects; reduce area (no truncated map displayed)')
    features,skipped=parse_osm(data)
    for f in features:
        p=f['properties'];t=p['osm_tags'];p['voltage_values']=voltage_values(t.get('voltage'))
        p['max_voltage']=max(p['voltage_values'],default=None)
        p['power_kind']=t.get('power');p['location']=t.get('location') or ('overhead' if t.get('power') in ('line','minor_line') else 'unknown')
        p['qualification']='Mapped infrastructure; completeness, operating state, cable height and flight clearance unknown'
        # This standalone catalogue is consultation only, not qualified decision input.
        p['optimization_eligible']=p['exposure_eligible']=False
    return features, {'skipped_geometry':skipped,'unknown_voltage':sum(not f['properties']['voltage_values'] for f in features),'osm_base':data.get('osm3s',{}).get('timestamp_osm_base')}

def earthquake_features(raw):
    if not raw.strip():return [],{'skipped':0}
    text=raw.decode('utf-8-sig');lines=text.splitlines()
    if not lines[0].startswith('#EventID|'):raise ValueError('Invalid FDSN text header')
    features=[];skipped=0
    for row in csv.reader(lines[1:],delimiter='|'):
        try:
            lat,lon,depth,mag=float(row[2]),float(row[3]),float(row[4]),float(row[10])
            if not all(math.isfinite(x) for x in [lat,lon,depth,mag]) or not -90<=lat<=90 or not -180<=lon<=180:raise ValueError('coordinates')
            when=dt.datetime.fromisoformat(row[1].replace('Z','+00:00'));when=when.replace(tzinfo=dt.timezone.utc) if when.tzinfo is None else when
            f=dict(type='Feature',id=row[0],geometry=dict(type='Point',coordinates=[lon,lat]),properties=dict(event_id=row[0],at=when.isoformat().replace('+00:00','Z'),depth_km=depth,magnitude=mag,magnitude_type=row[9],place=row[12],author=row[5],event_type=row[13] if len(row)>13 else 'earthquake',qualification='Observed catalogue solution, revisable; magnitude is not felt intensity; not a forecast'))
            features.append(f)
        except (IndexError,ValueError,OverflowError):skipped+=1
    if skipped and not features:raise ValueError('All earthquake rows invalid; not an empty valid catalogue')
    return features,{'skipped':skipped,'limit_reached':len(features)+skipped>=1000}

class ObservedLayers:
    def __init__(self,state,kind,fetch=None):
        if kind not in ('earthquakes','power'):raise ValueError(kind)
        self.kind=kind;self.root=Path(state)/('observed-'+kind);self.root.mkdir(exist_ok=True)
        self.lock=threading.Lock();self.active=False;self.pending={};self.last=0;self.fetch=fetch or self._fetch
    @staticmethod
    def _fetch(url):
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HAZARDIA research consultation/1'}),timeout=30) as r:
            raw=r.read(8*1024**2+1)
        if len(raw)>8*1024**2:raise ValueError('Source exceeds8MiB; narrow area')
        return raw
    def snapshot(self,key):
        if not re.fullmatch('[a-f0-9]{24}',key or ''):raise HazardError('INVALID_INPUT','Acquisition request id required')
        with self.lock:
            if key in self.pending:return dict(self.pending[key])
            path=self.root/(key+'.json')
            if path.exists():return json.loads(path.read_text())
        raise HazardError('NOT_FOUND','Acquisition not available')
    def prepare(self,body):
        expected={'bounds','days','min_magnitude','provider'} if self.kind=='earthquakes' else {'bounds'}
        if set(body)!=expected:raise HazardError('INVALID_INPUT','Required fields: '+', '.join(sorted(expected)))
        b=bounds(body['bounds']);now=dt.datetime.now(dt.timezone.utc)
        if self.kind=='earthquakes':
            days=body['days'];mag=body['min_magnitude'];provider=body['provider']
            if type(days) is not int or days not in (1,7,30) or type(mag) not in (int,float) or not math.isfinite(mag) or not -1<=mag<=9 or provider not in SOURCES:
                raise HazardError('INVALID_INPUT','Use1/7/30days, magnitude-1..9 and INGV/USGS')
            if provider=='ingv' and not (6<=b[0]<b[2]<=19 and 35<=b[1]<b[3]<=48):
                raise HazardError('OUTSIDE_COVERAGE','INGV regional consultation: select Italy (6–19E,35–48N) or USGS global; small-event completeness is not global')
            end=now.replace(minute=(now.minute//10)*10,second=0,microsecond=0);start=end-dt.timedelta(days=days)
            query=dict(format='text',starttime=start.strftime('%Y-%m-%dT%H:%M:%S'),endtime=end.strftime('%Y-%m-%dT%H:%M:%S'),minlatitude=b[1],maxlatitude=b[3],minlongitude=b[0],maxlongitude=b[2],minmagnitude=mag,limit=1000,orderby='time')
            url=SOURCES[provider]+'?'+urllib.parse.urlencode(query);ttl=600
        else:
            if b[2]-b[0]>3 or b[3]-b[1]>3 or (b[2]-b[0])*(b[3]-b[1])>6:
                raise HazardError('AREA_TOO_LARGE','Power inventory: zoom to ≤3° per side and ≤6 square degrees; no complete world network cached')
            box=','.join(map(str,[b[1],b[0],b[3],b[2]]))
            query=f'[out:json][timeout:20];(way[power~"^(line|minor_line|cable|substation)$"]({box});node[power~"^(tower|pole|substation)$"]({box}););out meta geom 5001;'
            url=('https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,b))) if b[2]-b[0]<=.061 and b[3]-b[1]<=.061 else POWER_SOURCE+'?'+urllib.parse.urlencode({'data':query});ttl=86400
        key=hashlib.sha256(json.dumps([self.kind,body,int(time.time()//ttl)],sort_keys=True).encode()).hexdigest()[:24]
        path=self.root/(key+'.json')
        with self.lock:
            if path.exists():return json.loads(path.read_text())
            if key in self.pending and self.pending[key]['status']=='LOADING':return dict(self.pending[key])
            if self.active:raise HazardError('QUEUE_FULL','Acquisition already running; retry after completion')
            if time.time()-self.last<5:raise HazardError('SOURCE_QUOTA','Wait5seconds between new acquisitions; cached requests remain available')
            quota=self.root/(now.date().isoformat()+'.quota');n=int(quota.read_text()) if quota.exists() else 0
            if n>=(24 if self.kind=='earthquakes' else 8):raise HazardError('SOURCE_QUOTA','Daily consultation acquisitions reached; existing cache remains available')
            if sum(p.stat().st_size for p in self.root.iterdir())>32*1024**2:raise HazardError('CACHE_FULL','32MiB consultation cache reached; no scientific files deleted')
            quota.write_text(str(n+1));self.active=True;self.last=time.time();self.pending[key]=dict(status='LOADING',request_id=key)
        def work():
            try:
                raw=self.fetch(url)
                if len(raw)>8*1024**2:raise ValueError('Source response exceeds8MiB')
                features,quality=(earthquake_features(raw) if self.kind=='earthquakes' else power_features(raw))
                if self.kind=='earthquakes':
                    quality.update(coverage='Regional Italian catalogue' if provider=='ingv' else 'Global catalogue; small earthquakes incomplete outside well-instrumented regions',window_start=start.isoformat(),window_end=end.isoformat(),min_magnitude=mag,provider=provider,license='INGV CC BY4.0 (open-data policy)' if provider=='ingv' else 'USGS public-domain data; contributor attribution retained',missing=['Felt intensity','Damage and site vulnerability','Detection completeness and catalogue revision history'])
                else:quality.update(source_mode='OSM API bounded map extract' if 'api.openstreetmap.org' in url else 'Overpass power query',license='ODbL-1.0 © OpenStreetMap contributors',missing=['Complete operator-certified network','Cable heights, sag and aerial clearance','Operating state and real-time outages','Voltage for untagged objects','Substation relations not acquired'])
                value=dict(status='READY',request_id=key,type='FeatureCollection',features=features,bounds=b,source=url,acquired_at=utcnow(),raw_sha256=hashlib.sha256(raw).hexdigest(),quality=quality,kind=self.kind,coupled_to_optimizer=False)
                encoded=json.dumps(value,allow_nan=False).encode()
                if sum(p.stat().st_size for p in self.root.iterdir())+len(raw)+len(encoded)>32*1024**2:raise ValueError('32MiB cache admission limit')
                path.with_suffix('.source').write_bytes(raw);path.write_bytes(encoded)
            except Exception as e:value=dict(status='ERROR',request_id=key,detail=str(e),kind=self.kind)
            with self.lock:
                self.pending[key]=value
                # Keep only a few terminal states in RAM; disk holds successful acquisitions.
                for old in list(self.pending):
                    if len(self.pending)<=8:break
                    if self.pending[old]['status']!='LOADING':del self.pending[old]
                self.active=False
        threading.Thread(target=work,daemon=True).start()
        return dict(status='LOADING',request_id=key)
