"""Prepare an opt-in research case in the VM; never replace the main workspace."""
import argparse,copy,datetime as dt,hashlib,json,re,time,urllib.request
from pathlib import Path

def api(base,path,body=None):
 r=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Hazardia-Research':'1'})
 with urllib.request.urlopen(r,timeout=40) as f:return json.load(f)
def exclusive(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False)
def poll(base,path,pending,seconds):
 end=time.monotonic()+seconds
 while True:
  value=api(base,path)
  if value.get('state') not in pending:return value
  if time.monotonic()>end:raise RuntimeError('Terminal state not received; retained ID '+path)
  time.sleep(1)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',required=True);ap.add_argument('--spec',required=True);ap.add_argument('--base',default='http://127.0.0.1:8080');ap.add_argument('--from-run',help='Register already completed case-i-body/result/preparation records; verify against live job store');a=ap.parse_args();root=Path(a.runtime);spec_path=Path(a.spec);spec=json.loads(spec_path.read_text());
 if not isinstance(spec.get('id'),str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',spec['id']):raise RuntimeError('Invalid case identifier')
 dest=root/'web-assets/fire-cases'/(spec['id']+'.json')
 import sys
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
 from hazardia.web.fire_cases import FireCases
 from hazardia.web.fire_workspace import FireWorkspace
 from hazardia.io import sha256
 from hazardia.firelab import validate
 from urllib.parse import urlsplit
 if sys.platform!='linux' or not (root/'runtime-v2.json').is_file():raise RuntimeError('Run inside the configured Linux VM')
 if urlsplit(a.base).scheme!='http' or urlsplit(a.base).hostname not in ['localhost','127.0.0.1']:raise RuntimeError('Local VM HTTP service required')
 if not isinstance(spec.get('scenarios'),list) or not 1<=len(spec['scenarios'])<=12:raise RuntimeError('Expected1..12 declared scenarios')
 for row in spec['scenarios']:validate(row['input'])
 if dest.exists():raise RuntimeError('Saved case exists; use a new case ID to preserve the previous snapshot')
 before=api(a.base,'/api/fire-workspace');out=Path(a.from_run) if a.from_run else root/'runs'/(spec['id']+'-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
 if not a.from_run:out.mkdir();exclusive(out/'protocol.json',dict(spec=spec,source_sha256=sha256(spec_path),registered_at=dt.datetime.now(dt.timezone.utc).isoformat(),qualification='PROSPECTIVE_RESEARCH_NOT_EVENT_RECONSTRUCTION'))
 start=(dt.datetime.now(dt.timezone.utc).replace(minute=0,second=0,microsecond=0)+dt.timedelta(hours=2)).isoformat().replace('+00:00','Z');forcing=None;cases=[]
 for i,row in enumerate(spec['scenarios']):
  if a.from_run:body=json.loads((out/f'case-{i}-body.json').read_text());v=json.loads((out/f'case-{i}-result.json').read_text())
  else:
   body=copy.deepcopy(row['input']);body['start_at']=start
   if forcing:body['forcing_id']=forcing
   exclusive(out/f'case-{i}-body.json',body);accepted=api(a.base,'/api/firelab/dynamic',body);exclusive(out/f'case-{i}-accepted.json',accepted);p=poll(a.base,'/api/fire-preparations/'+accepted['preparation_id'],['QUEUED','PREPARING'],360);exclusive(out/f'case-{i}-preparation.json',p)
   if p['state']!='SUCCEEDED':raise RuntimeError(p)
   forcing=p['forcing_id'];v=poll(a.base,'/api/firelab/'+p['jobs']['B'],['RUNNING','QUEUED'],960);exclusive(out/f'case-{i}-result.json',v)
  if v['state']!='SUCCEEDED' or api(a.base,'/api/firelab/'+v['id'])!=v:raise RuntimeError('Completed job differs from retained result')
  expected=copy.deepcopy(row['input']);actual=copy.deepcopy(body)
  for b in [expected,actual]:
   for key in ['start_at','forcing_id','forecast_id']:b.pop(key,None)
  if expected!=actual:raise RuntimeError('Run inputs differ from declared case; no silent substitution')
  req=json.loads((root/'jobs'/v['id']/'request.json').read_text())
  for asset in req['assets']:
   if sha256(root/'jobs'/v['id']/asset['path'])!=asset['sha256']:raise RuntimeError('Input asset checksum differs')
  authored=copy.deepcopy(body);authored.pop('forcing_id',None)
  cases.append(dict(row,input=authored,submitted_input=body,job_id=v['id']))
 # Validate the full seed before registering it. Validation copy is isolated from user data.
 validation=out/'registration-validation';validation.mkdir(exist_ok=True)
 store=FireWorkspace(validation)
 if not (validation/'workspace.json').exists():store.save(dict(revision=0,scenarios=cases))
 starts={c['input']['start_at'] for c in cases};fields={next(x['sha256'] for x in json.loads((root/'jobs'/c['job_id']/'request.json').read_text())['assets'] if x['role']=='weather') for c in cases}
 if len(starts)!=1 or len(fields)!=1:raise RuntimeError('Case comparison must share start and frozen base weather')
 value={k:spec[k] for k in ['id','title','description','source_url','qualification']};value.update(scenarios=cases,initial_hour=spec.get('initial_hour',0),initial_start_at=cases[0]['input']['start_at'],source_spec_sha256=hashlib.sha256(spec_path.read_bytes()).hexdigest());dest.parent.mkdir(exist_ok=True);exclusive(dest,value);FireCases(root).definition(spec['id'])
 if before!=api(a.base,'/api/fire-workspace'):raise RuntimeError('Main workspace changed during registration')
 print(json.dumps(dict(status='PASS',case=spec['id'],jobs=[c['job_id'] for c in cases],url='/?view=results&case='+spec['id'],main_workspace_preserved=True)))
if __name__=='__main__':main()
