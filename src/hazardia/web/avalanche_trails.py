"""Bounded optional trail catalogue and asynchronous spatial assessment in Linux."""
import pathlib,json,hashlib,gzip,io,math,datetime,time,threading,subprocess,os,urllib.request,urllib.parse,fcntl
from hazardia.io import HazardError
from hazardia.web.avalanche_layer import Snapshot,freshness
SOURCE='https://overpass-api.de/api/interpreter'
DAY_LIMIT=32*1024**2;CACHE_LIMIT=64*1024**2;RESERVE=2*1024**3+64*1024**2

def atomic(path,data):
 temp=path.with_name(path.name+'.tmp');temp.write_text(json.dumps(data,separators=(',',':'),allow_nan=False));temp.replace(path)
def checked_bounds(value):
 if not isinstance(value,list) or len(value)!=4 or any(type(x) not in (float,int) or not math.isfinite(x) for x in value):raise HazardError('INVALID_INPUT','Four finite WGS84 bounds required')
 w,s,e,n=value
 if not 6<=w<e<=19.2 or not 35<=s<n<=48 or e-w>1 or n-s>.7 or (e-w)*(n-s)*111**2*math.cos(math.radians((n+s)/2))>2500:raise HazardError('INVALID_INPUT','Avvicina la mappa: area italiana di massimo2500km2')
 rounded=[round(x,5) for x in value]
 if rounded[0]>=rounded[2] or rounded[1]>=rounded[3]:raise HazardError('INVALID_INPUT','Area troppo piccola')
 return rounded
def key_for(bounds):return hashlib.sha256(json.dumps(bounds).encode()).hexdigest()[:20]
def signature(runtime):
 folder=pathlib.Path(runtime)/'avalanche';parts=[json.loads((folder/'manifest.json').read_text())['sha256'],json.loads((folder/'terrain-manifest.json').read_text())['sha256']]
 local=folder/'local-forecasts.json'
 if local.exists():parts.append(hashlib.sha256(local.read_bytes()).hexdigest())
 parts.append('trail-geometry-v4-lossless-lengths');return hashlib.sha256(':'.join(parts).encode()).hexdigest()[:24]
def query_text(bounds):
 w,s,e,n=bounds;b=','.join(map(str,(s,w,n,e)))
 return '[out:json][timeout:45][maxsize:67108864];relation["type"="route"]["route"~"^(hiking|foot)$"]('+b+')->.routes;(way["highway"~"^(path|footway|steps|bridleway)$"]('+b+');way(r.routes)('+b+');)->.ways;.ways out body geom;.routes out body;'

class AvalancheTrails:
 def __init__(self,runtime):
  self.runtime=pathlib.Path(runtime);self.root=self.runtime/'avalanche/trails';self.root.mkdir(exist_ok=True);self.lock=threading.Lock();self.active=False;self.pending={}
 def guard(self,extra=0):
  import shutil
  if shutil.disk_usage(self.root).free<RESERVE+extra:raise ValueError('FREE_DISK_RESERVE')
  if sum(p.stat().st_size for p in self.root.glob('*') if p.is_file())+extra>CACHE_LIMIT:raise ValueError('TRAIL_CACHE_QUOTA_64MIB')
 def fetch(self,bounds,key):
  self.guard(20*1024**2);now=datetime.datetime.now(datetime.timezone.utc);quota=self.root/'network.json';budget=json.loads(quota.read_text()) if quota.exists() else {};day=now.date().isoformat()
  if budget.get('day')!=day:budget=dict(day=day,bytes=0,last_request=0)
  if time.time()-budget.get('last_request',0)<60:raise ValueError('OSM_COOLDOWN_60_SECONDS')
  if budget['bytes']>=DAY_LIMIT:raise ValueError('OSM_DAILY_QUOTA_32MIB')
  budget['last_request']=time.time();allowance=min(16*1024**2,DAY_LIMIT-budget['bytes']);budget['bytes']+=allowance;atomic(quota,budget);query=query_text(bounds)
  request=urllib.request.Request(SOURCE,data=urllib.parse.urlencode(dict(data=query)).encode(),headers={'User-Agent':'HAZARDIA research trails/0.1','Accept-Encoding':'gzip'})
  with urllib.request.urlopen(request,timeout=65) as response:
   if urllib.parse.urlsplit(response.url).hostname!=urllib.parse.urlsplit(SOURCE).hostname:raise ValueError('UNEXPECTED_SOURCE_REDIRECT')
   raw=response.read(allowance+1);encoding=response.headers.get('Content-Encoding')
  budget['bytes']+=len(raw)-allowance;atomic(quota,budget)
  if len(raw)>16*1024**2 or budget['bytes']>DAY_LIMIT:raise ValueError('OSM_SOURCE_BYTE_LIMIT')
  if encoding=='gzip':
   with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:decoded=stream.read(32*1024**2+1)
  else:decoded=raw
  if len(decoded)>32*1024**2:raise ValueError('OSM_EXPANDED_BYTE_LIMIT')
  data=json.loads(decoded)
  if data.get('remark') or not isinstance(data.get('elements'),list):raise ValueError('INCOMPLETE_OVERPASS_RESPONSE')
  rec=dict(url=SOURCE,query=query,bounds=bounds,at=now.isoformat(),bytes=len(raw),decoded_bytes=len(decoded),sha256=hashlib.sha256(decoded).hexdigest(),osm_base=data.get('osm3s',{}).get('timestamp_osm_base'),license='ODbL-1.0 © OpenStreetMap contributors')
  # Immutable source versions; current area pointer retains every earlier source.
  source=self.root/(key+'-'+rec['sha256']+'.source.json.gz')
  with gzip.open(source,'wb') as stream:stream.write(decoded)
  receipt=self.root/(key+'-'+rec['sha256']+'.receipt.json');atomic(receipt,rec);atomic(self.root/(key+'.catalog.json'),dict(source=source.name,receipt=receipt.name));return source,receipt
 def catalog(self,key):
  pointer=json.loads((self.root/(key+'.catalog.json')).read_text());return self.root/pointer['source'],self.root/pointer['receipt']
 def assessment_signature(self,key):
  source,receipt=self.catalog(key);sha=json.loads(receipt.read_text())['sha256'];return hashlib.sha256((signature(self.runtime)+sha).encode()).hexdigest()[:24]
 def query(self,bounds,refresh=False):
  bounds=checked_bounds(bounds);key=key_for(bounds)
  with self.lock:
   if self.active:return dict(status='BUSY',detail='One trail acquisition/assessment at a time; retry shortly',key=key)
   if not refresh and (self.root/(key+'.catalog.json')).exists():
    result=self.read_result(key)
    if result:return result
   self.active=True;self.pending[key]=dict(status='RUNNING',key=key,bounds=bounds);threading.Thread(target=self.work,args=(key,bounds,refresh),daemon=True,name='avalanche-trails').start();return dict(self.pending[key])
 def work(self,key,bounds,refresh):
  try:
   with (self.root/'worker.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:source,receipt=self.catalog(key);rec=json.loads(receipt.read_text());aged=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(rec['at'].replace('Z','+00:00'))).total_seconds()>7*86400
    except (OSError,ValueError,KeyError):aged=True
    if refresh or aged:source,receipt=self.fetch(bounds,key)
    self.guard(32*1024**2);sig=self.assessment_signature(key);output=self.root/(key+'-'+sig+'.geojson.gz');script=pathlib.Path(__file__).with_name('avalanche_trails_geo.py');python=pathlib.Path.home()/'m0/reflex-env/bin/python';env=dict(os.environ,PYTHONPATH=str(script.parents[2]),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    with (self.root/(key+'-'+sig+'.log')).open('w') as log:subprocess.run([str(python),str(script),'--runtime',str(self.runtime),'--source',str(source),'--receipt',str(receipt),'--output',str(output)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True,pass_fds=(lock.fileno(),))
    self.guard();atomic(self.root/(key+'.assessment.json'),dict(signature=sig,file=output.name,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(script.read_bytes()).hexdigest()));atomic(self.root/'latest.json',dict(key=key));self.pending.pop(key,None)
  except Exception as exc:
   detail='Fonte OSM o analisi non disponibile; riprova con un’area più piccola.'
   if str(exc)=='OSM_COOLDOWN_60_SECONDS':detail='Attendi60secondi tra due acquisizioni OSM.'
   elif 'QUOTA' in str(exc) or str(exc)=='FREE_DISK_RESERVE':detail='Limite dati o riserva di spazio raggiunto; copia precedente conservata.'
   self.pending[key]=dict(status='FAILED',key=key,detail=detail);atomic(self.root/(key+'.failure.json'),dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=str(exc),bounds=bounds))
  finally:
   with self.lock:self.active=False
 def read_result(self,key):
  try:
   pointer=json.loads((self.root/(key+'.assessment.json')).read_text())
   if pointer['signature']!=self.assessment_signature(key):return None
   compressed=(self.root/pointer['file']).read_bytes()
   if pointer.get('sha256') and hashlib.sha256(compressed).hexdigest()!=pointer['sha256']:raise ValueError('TRAIL_RESULT_CHECKSUM')
   with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(32*1024**2+1)
   if len(raw)>32*1024**2:raise ValueError('TRAIL_RESULT_BYTE_LIMIT')
   data=json.loads(raw);meta=data['metadata'];meta['analysis_code_sha256']=pointer.get('code_sha256');meta['derived_database_license']='ODbL-1.0';meta['assessment_base_sha256']=pointer.get('sha256');meta['terrain_sources']=json.loads((self.runtime/'avalanche/terrain-manifest.json').read_text()).get('metadata',{}).get('sources',[]);meta['snow_source']='SNOWPACK3.7.0 / ICON-EU via Open-Meteo CC BY4.0, synthetic initial snow state';meta['avalanche_source_url']='/api/avalanche/layer';meta['freshness_status']=freshness(meta,datetime.datetime.now(datetime.timezone.utc));meta['source_stale']=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(meta['source_acquired_at'].replace('Z','+00:00'))).total_seconds()>7*86400
   return dict(status='READY',key=key,data=data)
  except FileNotFoundError:return None
 def snapshot(self,key=None):
  if key is None:
   if not (self.root/'latest.json').exists():return dict(status='NOT_LOADED')
   key=json.loads((self.root/'latest.json').read_text())['key']
  import re
  if not re.fullmatch('[a-f0-9]{20}',key or ''):raise HazardError('INVALID_INPUT','Invalid trail area key')
  with self.lock:
   if key in self.pending:return dict(self.pending[key])
  result=self.read_result(key)
  if result:return result
  if (self.root/(key+'.catalog.json')).exists():
   source,receipt=self.catalog(key);return self.query(json.loads(receipt.read_text())['bounds'])
  return dict(status='NOT_LOADED',key=key)

def service(app):
 with app.lock:
  if not hasattr(app,'avalanche_trails'):app.avalanche_trails=AvalancheTrails(app.root)
  return app.avalanche_trails
