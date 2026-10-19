"""Asynchronous bounded geospatial read models; no modification of physical jobs."""
import hashlib,json,os,re,subprocess,threading,uuid,time,datetime as dt
from pathlib import Path
from hazardia.io import load,write_new,HazardError
from hazardia.territorial_context import bounds_checked
class TerritorialService:
 def __init__(self,app):self.app=app;self.lock=threading.Lock();self.active=set();self.root=app.state/'territorial-jobs';self.root.mkdir(exist_ok=True)
 def submit(self,body):
  refresh=body.get('refresh',False)
  if type(refresh) is not bool:raise HazardError('INVALID_INPUT','Boolean refresh required')
  body={k:v for k,v in body.items() if k!='refresh'}
  if set(body)=={'job_id'}:
   if not re.fullmatch('job-[a-f0-9]{32}',str(body['job_id'])):raise HazardError('INVALID_INPUT','Valid model job required')
   if self.app.store.get(body['job_id'])['state']!='SUCCEEDED':raise HazardError('DEPENDENCY_UNAVAILABLE','Completed physical result required')
  elif set(body)=={'bounds'}:bounds_checked(body['bounds'])
  else:raise HazardError('INVALID_INPUT','job_id or bounds required')
  key='context-'+hashlib.sha256(json.dumps(['territorial/7',body, int(time.time()//300) if refresh else None if 'job_id' in body else dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d')+str(dt.datetime.now(dt.timezone.utc).hour//3)],sort_keys=True).encode()).hexdigest()[:24];dest=self.root/key;dest.mkdir(exist_ok=True)
  with self.lock:
   if (dest/'result.json').exists():return dict(id=key,status='SUCCEEDED')
   if key in self.active:return dict(id=key,status='RUNNING')
   if len(self.active)>=2 or not self.app.capacity.acquire(False):raise HazardError('QUEUE_FULL','Territorial workers busy; retry later')
   self.active.add(key)
  if not (dest/'request.json').exists():write_new(dest/'request.json',body)
  def work():
   try:
    cfg=load(self.app.root/'runtime-v2.json');env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),PROJ_LIB='/usr/share/proj')
    # New attempt file avoids overwriting scientific source artifacts or stale errors.
    out=dest/('attempt-'+uuid.uuid4().hex+'.json')
    with (dest/(out.stem+'.log')).open('xb') as log:subprocess.run([cfg['geo_python'],'-m','hazardia.territorial_context',str(self.app.root),str(dest/'request.json'),str(out)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=100)
    write_new(dest/'result.json',load(out))
   except Exception as e:
    error=load(str(out)+'.error') if 'out' in locals() and Path(str(out)+'.error').exists() else dict(code='CONTEXT_FAILED',detail=str(e))
    # Status record is replaceable service state, never physical evidence.
    (dest/'error.json').write_text(json.dumps(error))
   finally:
    self.app.capacity.release()
    with self.lock:self.active.discard(key)
  self.app.pool.submit(work);return dict(id=key,status='QUEUED')
 def read(self,key):
  if not re.fullmatch('context-[a-f0-9]{24}',key):raise HazardError('INVALID_INPUT','Invalid context ID')
  dest=self.root/key
  if (dest/'result.json').exists():return dict(id=key,status='SUCCEEDED',data=load(dest/'result.json'))
  with self.lock:active=key in self.active
  if active:return dict(id=key,status='RUNNING')
  if (dest/'error.json').exists():return dict(id=key,status='ERROR',**load(dest/'error.json'))
  raise HazardError('NOT_FOUND','Context not available; submit again')
