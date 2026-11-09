"""Bounded local SNOWPACK columns, same cycle/reference as national delivery."""
import sys,pathlib,json,datetime,fcntl,resource,tempfile,tarfile,gzip,hashlib
sys.path.insert(0,'/home/hazardia/avalanche-runtime/app/src')
from hazardia_avalanche.worker import Refresh,parse,iso,atomic
root=pathlib.Path('/home/hazardia/avalanche-runtime');work=pathlib.Path('/dev/shm/avalanche-terrain-build');out=work/'output';run=work/'local-snowpack';run.mkdir(exist_ok=True);delivery=pathlib.Path('/home/hazardia/hazardia-runtime/avalanche');manifest=json.loads((delivery/'manifest.json').read_text());data=json.loads((delivery/'objects'/(manifest['sha256']+'.geojson')).read_text());meta=data['metadata'];reference=parse(meta['reference_utc']);end=parse(meta['end_utc']);cycle=parse(meta['weather_run_utc']);points=json.loads((out/'local-sites.json').read_text())
with (root/'worker.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
 refresh=Refresh(root,delivery);refresh.run=run;atomic(run/'protocol.json',dict(at=iso(datetime.datetime.now(datetime.timezone.utc)),reference_utc=iso(reference),end_utc=iso(end),weather_run_utc=iso(cycle),sites=points,scope='Stratified local synthetic columns; no observed stability or release probability',selector_sha256=hashlib.sha256((out/'local-protocol.json').read_bytes()).hexdigest(),code_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()))
 weather=refresh.weather(points,cycle,'local-weather');models={};evidence=[]
 with tempfile.TemporaryDirectory(dir='/dev/shm') as tmp:
  base=pathlib.Path(tmp);(base/'input').mkdir();(base/'output').mkdir();prepared={p['id']:refresh.prepare(p,d,base,reference,end) for p,d in zip(points,weather)};process=refresh.solve(base,[p['id'] for p in points],end);(base/'solver.stdout').write_bytes(process.stdout);(base/'solver.stderr').write_bytes(process.stderr);traces={}
  def addtrace(raw):
   for line in raw.decode(errors='replace').splitlines():
    if line.startswith('PRECIP_ITALY,'):
     parts=line.split(',');traces.setdefault(parts[1],[]).append(parts[2:])
  addtrace(process.stderr)
  for p in points:
   cid=p['id']
   if not(base/f'output/{cid}_cur.met').exists():
    recovery=refresh.solve(base,[cid],end);(base/f'recovery-{cid}.stderr').write_bytes(recovery.stderr);addtrace(recovery.stderr)
   try:
    value,record=refresh.collect(p,prepared[cid],base,traces.get(cid,[]),reference);models[cid]=dict(p,**value);evidence.append(record)
   except Exception as exc:models[cid]=refresh.missing(p,'LOCAL_MODEL_REJECTED:'+repr(exc))
  with tarfile.open(run/'native-local-output.tgz','w:gz') as archive:archive.add(base,arcname='local')
 result=dict(reference_utc=iso(reference),weather_run_utc=iso(cycle),models=models,scope='Local representative synthetic profiles with explicit missing; not snow forecast30m',protocol_sha256=hashlib.sha256((run/'protocol.json').read_bytes()).hexdigest())
 atomic(out/'local-forecasts.json',result);atomic(run/'models.json',result);atomic(run/'ledger.json',refresh.ledger)
 with gzip.open(run/'hourly-evidence.json.gz','wt') as stream:json.dump(evidence,stream)
 print(json.dumps(dict(total=len(models),valid=sum(p['factor_class']!=0 for p in models.values()),missing=sum(p['factor_class']==0 for p in models.values()))))
