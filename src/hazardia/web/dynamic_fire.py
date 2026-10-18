"""Bounded asynchronous preparation service; all acquisitions and processing in VM."""
import copy,datetime as dt,os,subprocess,threading,uuid,math
from pathlib import Path
from hazardia.io import load,write_new,utcnow,timestamp,HazardError,sha256
from hazardia.firelab import validate
class DynamicFire:
 def __init__(self,app):
  self.app=app;self.slots=threading.BoundedSemaphore(4);self.serial=threading.Lock();self.processes={};self.cancelled=set();self.base=app.state/'fire-preparations';self.base.mkdir(exist_ok=True)
  for path in self.base.glob('prep-*/state.json'):
   old=load(path)
   if old['state'] in ['QUEUED','PREPARING']:self.write(path.parent,dict(old,state='ERROR',error='PREPARATION_INTERRUPTED',detail='Preparation interrupted by service restart; retry explicitly'))
 def write(self,folder,value):
  import json
  pending=folder/'state.pending';pending.write_text(json.dumps(value,allow_nan=False));pending.replace(folder/'state.json')
 def get(self,ident):
  import re
  if not re.fullmatch('prep-[a-f0-9]{32}',ident):raise HazardError('INVALID_INPUT','Invalid preparation ID')
  return load(self.base/ident/'state.json')
 def submit(self,body):
  validate(body)
  if 'source_stale' in self.app.replay.state['faults']:raise HazardError('STALE_FORECAST','Sorgente meteo indisponibile: nuovo calcolo bloccato, risultati conservati')
  if body['weather_source']!='FORECAST':raise HazardError('SOURCE_MISSING','Arbitrary territory requires its real forecast; frozen historical replay remains an explicit separate case')
  if not self.slots.acquire(False):raise HazardError('QUEUE_FULL','Four preparations already queued')
  ident='prep-'+uuid.uuid4().hex;folder=self.base/ident;folder.mkdir();write_new(folder/'body.json',body);self.write(folder,dict(id=ident,state='QUEUED',detail='Preparazione del territorio accodata nella VM'))
  threading.Thread(target=self.work,args=(ident,folder,copy.deepcopy(body)),daemon=True).start();return dict(preparation_id=ident,state='QUEUED')
 def cancel(self,ident):
  value=self.get(ident)
  if value['state']=='SUCCEEDED':return dict(cancel_accepted=self.app.store.cancel(value['jobs']['B']))
  if value['state'] not in ['QUEUED','PREPARING']:return dict(cancel_accepted=False)
  self.cancelled.add(ident);write_new(self.base/ident/'cancel.json',dict(at=utcnow()))
  process=self.processes.get(ident)
  if process is not None and process.poll() is None:process.terminate()
  return dict(cancel_accepted=True)
 def execute(self,ident,command,env,log,timeout):
  if ident in self.cancelled:raise HazardError('CANCELLED','Preparazione annullata')
  process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env);self.processes[ident]=process
  try:
   process.wait(timeout=timeout)
   if ident in self.cancelled:raise HazardError('CANCELLED','Preparazione annullata')
   return process
  except subprocess.TimeoutExpired:process.kill();process.wait();raise
  finally:self.processes.pop(ident,None)
 def work(self,ident,folder,body):
  app=self.app
  try:
   with self.serial:
    self.write(folder,dict(id=ident,state='PREPARING',detail='Acquisizione DEM e vegetazione attorno agli inneschi'))
    cfg=load(app.root/'runtime-v2.json');env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),PROJ_LIB='/usr/share/proj')
    with (folder/'terrain.log').open('xb') as log:
     result=self.execute(ident,[cfg['geo_python'],'-m','hazardia.dynamic_terrain',str(app.root),str(folder/'body.json')],env,log,240)
    if result.returncode:raise HazardError('TERRAIN_UNAVAILABLE','Preparazione del terreno o della vegetazione non riuscita; nessun terreno sintetico sostituito. Dettagli nel registro della preparazione.')
    terrain=Path((folder/'terrain.log').read_text().strip().splitlines()[-1]);manifest=load(terrain/'manifest.json');bbox=manifest['bbox_wgs84']
    self.write(folder,dict(id=ident,state='PREPARING',detail='Acquisizione meteo distribuito e allineamento alla griglia fisica'))
    if body.get('forcing_id'):
     field=app.map_weather.read(body['forcing_id']+'.json')
     if not 0<=(timestamp(utcnow())-timestamp(field['available_at'])).total_seconds()<10800:raise HazardError('STALE_FORECAST','La previsione congelata del confronto è scaduta; ricalcola il gruppo')
    else:
     app.map_weather.acquire([[bbox[1],bbox[0]],[bbox[3],bbox[2]]]);snap=app.map_weather.snapshot()
     if snap['status']!='FRESH':raise HazardError('WEATHER_UNAVAILABLE',snap.get('error') or 'Meteo distribuito non disponibile')
     field=snap['forecast']
     if not (field['bounds'][0][0]<=bbox[1] and field['bounds'][0][1]<=bbox[0] and field['bounds'][1][0]>=bbox[3] and field['bounds'][1][1]>=bbox[2]):raise HazardError('WEATHER_UNAVAILABLE',snap.get('error') or 'Il campo meteo disponibile non copre il nuovo territorio')
    start=body.get('start_at');times={r['at'] for r in field['records']}
    if not start or timestamp(start)<=timestamp(utcnow()):raise HazardError('STALE_FORECAST','Scegli un inizio futuro: l’ora salvata non è più valida')
    if any((timestamp(start)+dt.timedelta(hours=h)).isoformat().replace('+00:00','Z') not in times for h in range(body['hours'])):raise HazardError('SOURCE_MISSING','Meteo incompleto per la durata scelta; scegli un inizio più vicino o accorcia la durata')
    write_new(folder/'field.json',field);write_new(folder/'terrain.json',dict(path=str(terrain),sha256=sha256(terrain/'manifest.json')))
    with (folder/'stage.log').open('xb') as log:
     result=self.execute(ident,[cfg['geo_python'],'-m','hazardia.dynamic_stage',str(app.root),str(folder)],env,log,90)
    if result.returncode:
     detail=(folder/'stage.log').read_text()
     if 'Ignition on built-up' in detail:raise HazardError('NO_BURNABLE_FUEL','Il punto scelto è classificato come superficie non combustibile in WorldCover2021; scegli esplicitamente una posizione vegetata')
     raise HazardError('PREPARATION_FAILED','Input fisici rifiutati; controlla vegetazione nel punto d’innesco, geometrie e registro della preparazione')
    if ident in self.cancelled:raise HazardError('CANCELLED','Preparazione annullata')
    req=load(folder/'request.json')
    with app.lock:job=app.store.submit(req,folder)
    self.write(folder,dict(id=ident,state='SUCCEEDED',jobs={'B':job},forcing_id=field['id'],terrain_id=manifest['id'],input=body,detail='Territorio e forzanti verificati; PROPAGATOR accodato'))
  except Exception as e:self.write(folder,dict(id=ident,state='CANCELLED' if isinstance(e,HazardError) and e.code=='CANCELLED' else 'ERROR',error=e.code if isinstance(e,HazardError) else 'PREPARATION_FAILED',detail=str(e)))
  finally:self.slots.release()
