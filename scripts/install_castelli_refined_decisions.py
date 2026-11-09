"""Keep assignment verification separate from finite native spatial refinement; reuse checked outputs."""
import copy,json,pathlib,uuid,time,urllib.request
from hazardia.io import load,write_new,sha256
from hazardia.decision.supervisor import bounded_decide
from hazardia.decision.verifier import verify
r=pathlib.Path('/home/hazardia/hazardia-runtime');out=r/'runs/castelli-dry-v2-plan-20261028';old=load(out/'comparisons.json');search=load(out/'position-search/full-objective-results.json')
def api(path,body=None):
 req=urllib.request.Request('http://127.0.0.1:8080'+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Hazardia-Research':'1'})
 with urllib.request.urlopen(req,timeout=15) as f:return json.load(f)
health=api('/api/research');records=[]
for parent in old:
 variant=parent['variant'];selected=search['selected']['reduced-fleet' if variant=='reduced-fleet' else 'primary'];job=selected['job_id'];s=load(r/'jobs'/job/'fire-series.json');unit=s['plan']['resources'][0];p=load(r/'web-state'/parent['decision_id']/'problem.json');c=load(r/'web-state'/(parent['decision_id']+'-input')/'prepared/context.json');ident='decision-'+uuid.uuid4().hex;p['id']=ident
 solver=str(r/'decision-env/bin/python') if variant!='solver-fallback' else '/nonexistent/castelli-primary-solver-python'
 result=bounded_decide(p,r/'web-state'/ident,solver);assert result['status']=='VALIDATED_FOR_SIMULATION' and result['selected']==parent['solver']['selected'];assert verify(p,result['selected'])['status']=='VALIDATED_FOR_SIMULATION'
 chosen=[]
 for oid in result['selected']:
  oldunit=c['option_resources'][oid];assert unit['id']==oldunit['id'] and unit['category']==oldunit['category'] and unit['at_minutes']==oldunit['at_minutes'];u=dict(unit,target_id=oldunit['target_id'],target_name=oldunit['target_name']);c['option_resources'][oid]=u;chosen.append(u)
 result.update(replay_health_revision=health['revision'],ideal=copy.deepcopy(load(out/(variant+'-decision.json'))['ideal']),capability_profile=load(out/(variant+'-decision.json'))['capability_profile'],spatial_refinement=dict(method='Finite native search after independently checked target assignment',scope='Best of three evaluated300m square positions for the selected ground unit and activation time; not a global continuous/joint optimum',candidate=selected['candidate'],selected_job_id=job,source_assignment_decision=parent['decision_id'],full_context_native_priority_index=selected['full_context_native_priority_index'],expected_area_ha=selected['expected_area_ha'],all_candidates=[v for v in search['candidates'] if v['variant']==('reduced-fleet' if variant=='reduced-fleet' else 'primary')],fallback_reuse='Same assignment, geometry, arrival, weather and seed reuse the checked native output' if variant=='solver-fallback' else None))
 result['ideal']['proposed_resources']=chosen;result['ideal']['effect_qualification']='BEST_OF_THREE_NATIVE_POSITION_CANDIDATES_IDEAL_UNQUALIFIED';result['ideal']['assumptions']+=['Assignment is independently checked; spatial refinement is an exploratory finite3position native search, not a global spatial/fleet optimum','The initial central placement increased area to5.31ha; all candidates including a7.1775ha result are retained; selected100m translation yields0.63ha in4realizations']
 write_new(r/'web-state'/ident/'ideal-result.json',result);write_new(r/'web-state'/ident/'context.json',dict(health=health,ideal=result['ideal']));prep=r/'web-state'/(ident+'-input')/'prepared';prep.mkdir(parents=True);write_new(prep/'context.json',c);write_new(prep/'problem.json',p)
 comparison='ideal-native-'+uuid.uuid4().hex;folder=r/'web-state'/comparison;folder.mkdir();write_new(folder/'replay.json',dict(decision_id=ident,source_baseline=c['body']['job_id'],jobs=dict(A=parent['jobs']['A'],B=job),qualification='FROZEN_NATIVE_RESULT_REUSE_CHECKED_INPUTS'))
 accepted=api('/api/fire-ideal/evaluate',dict(comparison_id=comparison));start=time.monotonic()
 while True:
  evaluated=api('/api/decisions/'+accepted['id'])
  if evaluated['status'] not in ['RUNNING','QUEUED']:break
  if time.monotonic()-start>40:raise RuntimeError('Evaluation deadline')
  time.sleep(.5)
 assert evaluated['status']=='COMPARISON_EVALUATED',evaluated
 b=next(v for v in evaluated['rows'] if v['case']=='B');assert abs(b['native_priority_index']-selected['full_context_native_priority_index'])<1e-8
 row=dict(variant=variant,decision_id=ident,degradation=result['degradation'],selected=chosen,jobs=dict(A=parent['jobs']['A'],B=job),evaluation=evaluated,solver=result['solver'],elapsed_s=result['elapsed_s'],spatial_refinement=result['spatial_refinement']);records.append(row);write_new(out/('refined-'+variant+'.json'),row);print(json.dumps(dict(variant=variant,decision=ident,selected=selected['candidate'],score=b['native_priority_index'],ha=b['area_ha'])),flush=True)
write_new(out/'refined-comparisons.json',records)
