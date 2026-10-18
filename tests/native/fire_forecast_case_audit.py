"""Read-only paired forecast audit inside the VM; never effectiveness certification."""
import json,sys
from pathlib import Path
from hazardia.io import load,sha256

def audit(root,case):
 import numpy as np
 root=Path(root);definition=load(root/'web-assets/fire-cases'/f'{case}.json');scenarios=definition['scenarios'];folders=[root/'jobs'/s['job_id'] for s in scenarios];requests=[load(p/'request.json') for p in folders];series=[load(p/'fire-series.json') for p in folders];rows=[]
 for p,r,s in zip(folders,requests,series):
  m=load(p/'manifest.json');assert all(sha256(p/name)==digest for name,digest in m['artifacts'].items());assert all(sha256(p/a['path'])==a['sha256'] for a in r['assets']);assert r['options']['realizations']==8 and r['options']['duration_s']==259200
  forcing=s['plan']['forcing'];assert forcing['version']=='distributed/2' and forcing['initialization']['hours']==168
  weather=load(p/next(a['path'] for a in r['assets'] if a['role']=='weather'));history=weather['antecedent_field'];assert len(history['lats'])==9 and len(history['lons'])==9
  from hazardia.ingest.antecedent_weather import history_rows
  assert len(history_rows(history,r['valid_from']))==168
  with np.load(p/next(a['path'] for a in r['assets'] if a['role']=='fire_arrays'),allow_pickle=False) as arrays:
   moisture=arrays['initial_moisture'];assert moisture.shape==tuple(r['grid']['shape']) and np.isfinite(moisture).all();initial=[float(moisture.min()),float(moisture.max())]
  consumed=s['consumed_events'];assert next(e for e in consumed if e['time']==0)['moisture_grid_range_percent']==initial
  frames=s['frames'];assert len(frames)==288 and frames[-1]['elapsed_s']==259200
  rows.append(dict(job_id=p.name,request_id=r['id'],artifacts=len(m['artifacts']),assets=len(r['assets']),frames=len(frames),initial_moisture_range_percent=initial,native_initialization_matches=True,final_area_ha=frames[-1]['expected_area_ha'],last_active_realizations=frames[-1]['realizations_with_front'],wind_hours=sum(e['spatial_forcing'] for e in consumed),history_bytes=history['source']['bytes']))
 static=lambda r:{a['role']:a['sha256'] for a in r['assets'] if a['role']!='fire_plan'}
 assert static(requests[0])==static(requests[1]);assert all(requests[0][k]==requests[1][k] for k in ['grid','options','valid_from','valid_until']);assert not series[0]['plan']['resources'];assert series[1]['plan']['resources'][0]['effect']=='native'
 prefix=[f for f in series[0]['frames'] if f['elapsed_s']<3600];assert all(np.array_equal(np.load(folders[0]/f['path'])['probability'],np.load(folders[1]/f['path'])['probability']) for f in prefix)
 event=next(e for e in series[1]['consumed_events'] if e['time']==3600);assert event['moisture_changed_cells']>0
 end=[np.load(p/'fire-output.npz',allow_pickle=False)['probability'] for p in folders];different=int(np.count_nonzero(end[0]!=end[1]));assert all(np.allclose(p*8,np.round(p*8)) for p in end)
 return dict(status='PASS',qualification='REAL_INPUT_CONDITIONAL_FORECAST_NOT_CALIBRATED_OPERATIONAL_VALIDATION',start=requests[0]['valid_from'],end=requests[0]['valid_until'],rows=rows,identical_pre_action_samples=len(prefix),different_final_probability_cells=different,canadair_consumed_event=event,static_inputs_identical=True,known_limits=['Fuel2021 research crosswalk/seasonality','ICON global11km mountain forecast not local sensors','HFFMC estimate, not RISICO/field moisture','Eight realizations of one forecast are not a weather ensemble','Native aircraft action not calibrated efficacy/logistics','No observed-event/held-out validation'])
if __name__=='__main__':
 if sys.platform!='linux':raise RuntimeError('VM only')
 print(json.dumps(audit(sys.argv[1],sys.argv[2]),indent=2))
