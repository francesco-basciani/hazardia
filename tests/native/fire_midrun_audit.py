"""Read-only VM audit of two frozen resource replays against their exact parent."""
import json,sys
from pathlib import Path
from hazardia.io import load,sha256

def audit(root,parent,children):
 import numpy as np
 root=Path(root);base=root/'jobs'/parent;request=load(base/'request.json');series=load(base/'fire-series.json');before=np.load(base/'frame-096.npz',allow_pickle=False)['probability'];final=np.load(base/'fire-output.npz',allow_pickle=False)['probability'];rows=[]
 for kind,ident in children.items():
  job=root/'jobs'/ident;r=load(job/'request.json');m=load(job/'manifest.json');s=load(job/'fire-series.json')
  assert all(sha256(job/name)==digest for name,digest in m['artifacts'].items())
  assert all(sha256(job/a['path'])==a['sha256'] for a in r['assets'])
  assert all(r[k]==request[k] for k in ['valid_from','valid_until','grid','options'])
  static=lambda req:{a['role']:a['sha256'] for a in req['assets'] if a['role']!='fire_plan'}
  assert static(r)==static(request)
  prefix=[f for f in series['frames'] if f['elapsed_s']<86400]
  assert all(np.array_equal(np.load(base/f['path'],allow_pickle=False)['probability'],np.load(job/f['path'],allow_pickle=False)['probability']) for f in prefix)
  p=np.load(job/'fire-output.npz',allow_pickle=False)['probability'];event=next(e for e in s['consumed_events'] if e['time']==86400);u=s['plan']['resources'][0]
  assert u['at_minutes']==1440 and u['effect']==('native' if kind=='canadair' else 'fuel_removal')
  assert event['moisture_changed_cells']>0 if kind=='canadair' else event['vegetation_changed_cells']>0
  cumulative=bool(np.all(p>=before));assert cumulative
  rows.append(dict(case=kind,job_id=ident,parent=parent,start=r['valid_from'],assets_verified=len(r['assets']),artifacts_verified=len(m['artifacts']),pngs_verified=sum(n.endswith('.png') for n in m['artifacts']),frames=len(s['frames']),prefix_frames_identical=len(prefix),area_ha=s['frames'][-1]['expected_area_ha'],different_final_cells=int(np.count_nonzero(final!=p)),past_burn_probability_preserved=cumulative,event_at24=event,action=u))
 return dict(status='PASS',rows=rows,parent_final_ha=series['frames'][-1]['expected_area_ha'],qualification='Frozen research replay, one seed and2realizations; no extinction or operational efficacy claim')
if __name__=='__main__':
 if sys.platform!='linux':raise RuntimeError('VM only')
 print(json.dumps(audit(sys.argv[1],sys.argv[2],json.loads(sys.argv[3])),indent=2))
