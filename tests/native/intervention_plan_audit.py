"""Actual solver and failed-dependency fallback on an existing native baseline. No model runs."""
import json,time,pathlib,argparse,urllib.request,uuid,copy,hashlib
from hazardia.decision.supervisor import bounded_decide
from hazardia.decision.verifier import verify
from hazardia.decision.fire_priorities import DEFAULT_WEIGHTS
from hazardia.io import load
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();r=pathlib.Path(a.root);out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=False)
def get(path,body=None):
 req=urllib.request.Request('http://127.0.0.1:8080'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json','X-Hazardia-Research':'1'})
 with urllib.request.urlopen(req,timeout=10) as response:return json.load(response)
before=[get('/api/fire-workspace'),get('/api/fire-workspace?case=forecast-fonte-vetica-20261018')];checks=[]
def check(name,ok):checks.append(dict(id=name,status='PASS' if ok else 'FAIL'));assert ok,name
body=dict(job_id='job-ebe51c3a0c4b4832bda1ab3f117e6ec6',fleet=[dict(id='audit-ground',category='waterline_action',available=True,arrival_minutes=0),dict(id='audit-heavy',category='heavy_action',available=True,arrival_minutes=60),dict(id='audit-air',category='canadair',available=True,arrival_minutes=0),dict(id='audit-unavailable',category='waterline_action',available=False,arrival_minutes=0)],weights=DEFAULT_WEIGHTS,robust=1,assumptions_confirmed=True)
(out/'request.json').write_text(json.dumps(body));accepted=get('/api/fire-ideal',body);t=time.monotonic()
while True:
 decision=get('/api/decisions/'+accepted['id'])
 if decision['status'] not in ('RUNNING','QUEUED'):break
 if time.monotonic()-t>65:raise RuntimeError('No terminal status within deadline')
 time.sleep(.5)
(out/'normal.json').write_text(json.dumps(decision));check('real-normal-decision-verified',decision['status']=='VALIDATED_FOR_SIMULATION');check('new-priority-inventory-explicit','railway' in decision['ideal']['source']['inventory_counts']);check('no-operational-authority',decision['operationally_approvable'] is False);check('unqualified-air-and-unavailable-not-assigned',not {'audit-air','audit-unavailable'}&{u['id'] for u in decision['ideal']['proposed_resources']});p=load(r/'web-state'/accepted['id']/'problem.json');check('normal-selection-independent-verifier',verify(p,decision['selected'])['status']=='VALIDATED_FOR_SIMULATION')
p['settings']['budget_s']=10;fallback=bounded_decide(p,out/('decision-'+uuid.uuid4().hex),'/nonexistent/intervention-plan-solver-python');(out/'fallback.json').write_text(json.dumps(fallback));check('actual-missing-process-fallback',fallback['status']=='VALIDATED_FOR_SIMULATION' and fallback['degradation']['state']=='DEGRADED');check('fallback-not-claimed-optimal',not fallback['solver']['optimal']);check('fallback-independent-verifier',verify(p,fallback['selected'])['status']=='VALIDATED_FOR_SIMULATION');check('fallback-bounded',fallback['elapsed_s']<10)
blocked=copy.deepcopy(p)
for unit in blocked['resources']:unit['record']['payload']['maintenance']='UNKNOWN'
negative=bounded_decide(blocked,out/('decision-'+uuid.uuid4().hex),'/nonexistent/intervention-plan-solver-python');(out/'blocked.json').write_text(json.dumps(negative));check('unknown-safety-no-assignment',not negative['selected'] and negative['status']!='VALIDATED_FOR_SIMULATION');check('workspaces-preserved',before==[get('/api/fire-workspace'),get('/api/fire-workspace?case=forecast-fonte-vetica-20261018')]);cfg=load(r/'runtime-v2.json');check('engines-unchanged',all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h for p,h in cfg['engine_files'].items()));summary=dict(checks=checks,normal_id=accepted['id'],normal_elapsed_s=decision['elapsed_s'],normal_assigned=len(decision['ideal']['proposed_resources']),inventory=decision['ideal']['source']['inventory_counts'],missing=decision['ideal']['source']['missing_priority_categories'],fallback_elapsed_s=fallback['elapsed_s'],fallback_assigned=len(fallback['selected']),no_new_physical_jobs=True,engine_pins=len(cfg['engine_files']),qualification='Engineering verification on existing uncalibrated native forecast; not efficacy, p95 or optimal firefighting');(out/'verification.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
