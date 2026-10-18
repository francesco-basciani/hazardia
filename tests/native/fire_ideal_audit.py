"""Read-only audit of genuine optimized A/B jobs. Run in Linux VM only."""
import argparse,json,sys
from pathlib import Path
from hazardia.io import load,sha256

def audit(root,comparison):
 import numpy as np
 root=Path(root);folder=root/'web-state'/comparison;replay=load(folder/'replay.json');rows=[];plans=[];prob=[];counts={}
 for case,ident in replay['jobs'].items():
  job=root/'jobs'/ident;manifest=load(job/'manifest.json');request=load(job/'request.json');series=load(job/'fire-series.json');plans.append(series['plan'])
  assert all(sha256(job/name)==digest for name,digest in manifest['artifacts'].items())
  assert all(sha256(job/a['path'])==a['sha256'] for a in request['assets'])
  assert len(series['frames'])==288
  with np.load(job/'fire-output.npz',allow_pickle=False) as data:prob.append(data['probability'].copy())
  events=series['consumed_events'];rows.append(dict(case=case,job_id=ident,area_ha=series['frames'][-1]['expected_area_ha'],artifacts_verified=len(manifest['artifacts']),assets_verified=len(request['assets']),pngs_verified=sum(n.endswith('.png') for n in manifest['artifacts']),native_frames=len(series['frames']),unit_times_minutes=[u['at_minutes'] for u in series['plan']['resources']],changed_fuel_events=[dict(time=e['time'],cells=e['vegetation_changed_cells']) for e in events if e['vegetation_changed_cells']],spatial_forcing_events=sum(bool(e['spatial_forcing']) for e in events)))
 a,b=[root/'jobs'/replay['jobs'][case] for case in ['A','B']];baseline=root/'jobs'/replay['source_baseline'];series=load(a/'fire-series.json')
 counts['all_baseline_probability_frames_identical']=all(np.array_equal(np.load(a/f['path'],allow_pickle=False)['probability'],np.load(baseline/f['path'],allow_pickle=False)['probability']) for f in series['frames'])
 counts['different_final_probability_cells']=int(np.count_nonzero(prob[0]!=prob[1]));assert counts['different_final_probability_cells']>0
 assert not plans[0]['resources'];assert sorted(u['at_minutes'] for u in plans[1]['resources'])==[0,1440]
 assert all(row['spatial_forcing_events']==72 for row in rows)
 assert all(any(e['time']==t and e['cells']>0 for e in rows[1]['changed_fuel_events']) for t in [0,86400])
 assert counts['all_baseline_probability_frames_identical']
 return dict(status='PASS',comparison_id=comparison,rows=rows,checks=counts,evaluation=load(folder/'evaluation-native.json'),qualification='Engineering replay; same seed, two realizations; no operational or global-optimum claim')
if __name__=='__main__':
 if sys.platform!='linux':raise RuntimeError('VM Linux only')
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--comparison',required=True);p.add_argument('--out',required=True);args=p.parse_args();result=audit(args.runtime,args.comparison);Path(args.out).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
