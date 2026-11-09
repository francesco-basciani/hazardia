"""Bounded decisions + real paired native replays on the explicit frozen Castelli fixture."""
import copy,json,pathlib,time,uuid,urllib.request,sys
from hazardia.io import load,write_new,sha256
from hazardia.decision.supervisor import bounded_decide
from hazardia.decision.verifier import verify
r=pathlib.Path('/home/hazardia/hazardia-runtime');out=r/'runs/castelli-dry-v2-plan-20261028';context=load(out/'prepared/context.json');base=load(out/'prepared/problem.json')
def api(path,body=None):
 req=urllib.request.Request('http://127.0.0.1:8080'+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Hazardia-Research':'1'})
 with urllib.request.urlopen(req,timeout=15) as response:return json.load(response)
def poll(path,field,pending,deadline):
 start=time.monotonic()
 while True:
  v=api(path)
  if v[field] not in pending:return v
  if time.monotonic()-start>deadline:raise RuntimeError('Bounded wait expired; retained '+path)
  time.sleep(1)
health=api('/api/research');records=[]
protocol=dict(kind='FROZEN_DECISION_AND_NATIVE_COMPARISON',variants=['primary','solver-fallback','reduced-fleet'],fallback='Nonexistent solver executable only within isolated bounded_decide call; no global service fault injected',reduced_fleet='squadra1 and squadra2 unavailable; other declarations unchanged',weights=context['body']['weights'],robust=context['body']['robust'],physical_effect='Existing ideal300m square persistent fuel removal; not calibrated ground suppression',unit_duration='Available through end12h; no separate work/expiry model',start_at=load(r/'jobs'/context['body']['job_id']/'request.json')['valid_from'],source_snapshot_sha256=sha256(out/'assets.json'),research_health_revision=health['revision'])
write_new(out/'comparison-protocol.json',protocol)
for variant in protocol['variants']:
 p=copy.deepcopy(base);c=copy.deepcopy(context);ident='decision-'+uuid.uuid4().hex;p['id']=ident
 if variant=='reduced-fleet':
  for unit in p['resources']:
   if unit['id'] in ['squadra-1','squadra-2']:unit['record']['payload']['maintenance']='UNAVAILABLE'
  for unit in c['body']['fleet']:
   if unit['id'] in ['squadra-1','squadra-2']:unit['available']=False
 solver=str(r/'decision-env/bin/python') if variant!='solver-fallback' else '/nonexistent/castelli-primary-solver-python'
 result=bounded_decide(p,r/'web-state'/ident,solver)
 assert result['status']=='VALIDATED_FOR_SIMULATION',result
 assert verify(p,result['selected'])['status']=='VALIDATED_FOR_SIMULATION'
 if variant=='solver-fallback':assert result['degradation']['state']=='DEGRADED' and not result['solver']['optimal']
 chosen=[c['option_resources'][key] for key in result['selected']];assert chosen and all(u['category'] not in ['canadair','helicopter'] for u in chosen)
 result.update(replay_health_revision=health['revision'],ideal=dict(aviation=c['aviation'],baseline_job_id=c['body']['job_id'],baseline_input=c['baseline_input'],assets=[{k:v for k,v in x.items() if k!='geometry'} for x in c['assets']],proposed_resources=chosen,assumptions=c['assumptions'],source=c['source'],fleet=c['body']['fleet'],effect_qualification='IDEAL_PROXY_NOT_PHYSICAL_OPTIMUM',unassigned_units=[x['id'] for x in p['resources'] if x['id'] not in {u['id'] for u in chosen}],unavailable_units=[x['id'] for x in p['resources'] if x['record']['payload']['maintenance']!='READY']))
 result['capability_profile']=dict(scope='Frozen Castelli research fixture',assignment='DEGRADED' if variant!='primary' else 'AVAILABLE',priority_inventory='PARTIAL',aerial_assignment='UNAVAILABLE',physical_effect='UNQUALIFIED')
 write_new(r/'web-state'/ident/'ideal-result.json',result);write_new(r/'web-state'/ident/'context.json',dict(health=health,ideal=result['ideal']))
 prepared=r/'web-state'/(ident+'-input')/'prepared';prepared.mkdir(parents=True);write_new(prepared/'context.json',c);write_new(prepared/'problem.json',p)
 write_new(out/(variant+'-decision.json'),result)
 replay=api('/api/fire-ideal/replay',dict(decision_id=ident));write_new(out/(variant+'-replay.json'),replay)
 for job in replay['jobs'].values():
  state=poll('/api/firelab/'+job,'state',['RUNNING','QUEUED'],950);assert state['state']=='SUCCEEDED',state
 evaluation=api('/api/fire-ideal/evaluate',dict(comparison_id=replay['comparison_id']));evaluated=poll('/api/decisions/'+evaluation['id'],'status',['RUNNING','QUEUED'],40);assert evaluated['status']=='COMPARISON_EVALUATED',evaluated
 write_new(out/(variant+'-evaluation.json'),evaluated)
 records.append(dict(variant=variant,decision_id=ident,degradation=result['degradation'],selected=chosen,jobs=replay['jobs'],evaluation=evaluated,solver=result['solver'],elapsed_s=result['elapsed_s']))
 write_new(out/('completed-'+variant+'.json'),records[-1]);print(json.dumps(records[-1]),flush=True)
write_new(out/'comparisons.json',records)
assert sha256(r/'web-state/fire-workspace/workspace.json')==load(out/'protocol.json')['workspace_sha256']
print('ALL_COMPARISONS_COMPLETED',flush=True)
