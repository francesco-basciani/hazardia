"""Audit a paired native intervention replay without assuming a benefit. Linux VM only."""
import argparse,json,sys
from pathlib import Path
from hazardia.io import load,sha256

def audit(root,comparison):
 import numpy as np
 root=Path(root);folder=root/'web-state'/comparison;replay=load(folder/'replay.json');decision=load(root/'web-state'/replay['decision_id']/'ideal-result.json');rows=[];requests=[];plans=[];arrays=[];checks=[]
 def check(name,value):
  checks.append(dict(id=name,status='PASS' if value else 'FAIL'));assert value,name
 for case in ['A','B']:
  ident=replay['jobs'][case];job=root/'jobs'/ident;req=load(job/'request.json');manifest=load(job/'manifest.json');series=load(job/'fire-series.json');native=load(job/'fire-native-result.json');requests.append(req);plans.append(series['plan'])
  check(case+'-assets-and-artifacts',all(sha256(job/a['path'])==a['sha256'] for a in req['assets']) and all(sha256(job/p)==h for p,h in manifest['artifacts'].items()))
  frames=series['frames'];check(case+'-full-horizon',len(frames)==req['options']['duration_s']//900 and frames[-1]['elapsed_s']==req['options']['duration_s']==native['duration_s'])
  with np.load(job/'fire-output.npz',allow_pickle=False) as data:arrays.append(data['probability'].copy())
  changed=[f for i,f in enumerate(frames) if i==0 or f['expected_area_ha']>frames[i-1]['expected_area_ha']+1e-9]
  exhausted=next((f['hour'] for f in frames if f.get('queued_front_events')==0),None)
  checkpoints=[]
  for h in [1,6,12,24,36,48,60,72]:
   f=next((f for f in frames if f['hour']==h),None)
   if f:checkpoints.append({k:f[k] for k in ['hour','expected_area_ha','positive_cells','queued_front_events','realizations_with_front']})
  rows.append(dict(case=case,job_id=ident,area_ha=frames[-1]['expected_area_ha'],last_growth_sample_hour=changed[-1]['hour'],first_front_exhaustion_hour=exhausted,front_events_at_end=frames[-1]['queued_front_events'],members_with_front_at_end=frames[-1]['realizations_with_front'],realizations=req['options']['realizations'],horizon_hours=req['options']['duration_s']/3600,checkpoints=checkpoints,consumed_events=native['consumed_events'],artifacts=len(manifest['artifacts']),assets=len(req['assets']),seed_proof=native['worker_seed_proof']))
 a,b=requests
 static=lambda req:{x['role']:x['sha256'] for x in req['assets'] if x['role']!='fire_plan'}
 check('same-static-inputs-including-distributed-weather',static(a)==static(b))
 check('same-grid-options-seed-clock',all(a[k]==b[k] for k in ['grid','options','valid_from','valid_until']))
 check('same-numerical-boundaries-and-ignitions',all(plans[0].get(k)==plans[1].get(k) for k in ['ignitions_wgs84','weather_changes','forcing','records','action_times','comparison_times','moisture_percent']))
 expected=[{k:v for k,v in u.items() if k in ['id','category','area','at_minutes','effect']} for u in decision['ideal']['proposed_resources']]
 check('only-selected-interventions-differ',plans[0]['resources']==[] and plans[1]['resources']==expected)
 check('same-worker-seeds',rows[0]['seed_proof']==rows[1]['seed_proof'])
 action_times={int(u['at_minutes']*60) for u in expected};events=rows[1]['consumed_events'];check('interventions-really-consumed',all(any(e['time']==t and e['vegetation_changed_cells']>0 for e in events) for t in action_times))
 check('complete-hourly-distributed-forcing',all(sum(e['spatial_forcing'] for e in row['consumed_events'])==int(row['horizon_hours']) for row in rows))
 baseline=root/'jobs'/replay['source_baseline'];first_action=min(action_times)
 prefix=[];reference=[];first_difference=None
 for f in load(root/'jobs'/replay['jobs']['A']/'fire-series.json')['frames']:
  paths=[root/'jobs'/replay['jobs'][k]/f['path'] for k in ['A','B']]
  with np.load(paths[0],allow_pickle=False) as x,np.load(paths[1],allow_pickle=False) as y,np.load(baseline/f['path'],allow_pickle=False) as z:
   reference.append(np.array_equal(x['probability'],z['probability']))
   if first_difference is None and not np.array_equal(x['probability'],y['probability']):first_difference=f['hour']
   if f['elapsed_s']<first_action:prefix.append(np.array_equal(x['probability'],y['probability']))
 check('all-A-frames-match-frozen-baseline',all(reference))
 check('pre-intervention-frames-identical',bool(prefix) and all(prefix))
 difference=int(np.count_nonzero(arrays[0]!=arrays[1]));delta=rows[1]['area_ha']-rows[0]['area_ha']
 return dict(run_id='optimized-physical-20261019',status='PASS',comparison_id=comparison,decision_id=replay['decision_id'],checks=checks,rows=rows,different_final_probability_cells=difference,first_difference_hour=first_difference,area_change_B_minus_A_ha=delta,evaluation=load(folder/'evaluation-native.json'),qualification='Paired 8-member pilot under frozen real forecast; ideal fuel-removal units, no efficacy calibration or global physical optimum. Outcome may improve, remain equal or worsen.')
if __name__=='__main__':
 if sys.platform!='linux':raise RuntimeError('VM Linux only')
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--comparison',required=True);p.add_argument('--out',required=True);a=p.parse_args();r=audit(a.runtime,a.comparison);Path(a.out).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2))
