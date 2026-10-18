"""VM-only input qualification audit; integrity is separate from scientific realism."""
import json,sys
from pathlib import Path
from hazardia.io import load,sha256

def audit(root,identifiers):
 import numpy as np
 rows=[]
 for ident in identifiers:
  folder=Path(root)/'jobs'/ident;req=load(folder/'request.json');series=load(folder/'fire-series.json');plan=series['plan'];manifest=load(folder/'manifest.json')
  assert all(sha256(folder/name)==digest for name,digest in manifest['artifacts'].items())
  assert all(sha256(folder/a['path'])==a['sha256'] for a in req['assets'])
  arrays=folder/next(a['path'] for a in req['assets'] if a['role']=='fire_arrays');weather=load(folder/next(a['path'] for a in req['assets'] if a['role']=='weather'));field=weather['distributed_field'];proof=series['consumed_events'];spatial=[p for p in proof if p['spatial_forcing']]
  assert len(spatial)==req['options']['duration_s']//3600
  with np.load(arrays,allow_pickle=False) as a:classes,counts=np.unique(a['veg'],return_counts=True)
  rows.append(dict(job_id=ident,input_hashes_verified=len(req['assets']),artifact_hashes_verified=len(manifest['artifacts']),realizations=req['options']['realizations'],model_start=req['valid_from'],model_end=req['valid_until'],native_cell_m=req['grid']['transform'][0],fuel_codes_counts={str(int(k)):int(v) for k,v in zip(classes,counts)},moisture_initial_ffmc=plan['forcing']['initial_ffmc'],moisture_estimator=plan['forcing']['moisture_model'],spatial_forcing_events=len(spatial),moisture_range_percent=[min(p['moisture_grid_range_percent'][0] for p in spatial),max(p['moisture_grid_range_percent'][1] for p in spatial)],wind_range_kmh=[min(p['wind_grid_range_kmh'][0] for p in spatial),max(p['wind_grid_range_kmh'][1] for p in spatial)],provider=field['model'],provider_initialization=field['issued_at_status'],resource_count=len(plan['resources']),qualification='TECHNICAL_INTEGRITY_PASS_PHYSICAL_REALISM_UNQUALIFIED'))
 return dict(status='PASS',qualification='AUDIT_ONLY_NO_NEW_NATIVE_RUNS',rows=rows,blocked=['Observed ignition/perimeter/timing for historical reconstruction','Local seasonal fuels and species, measured/validated moisture','Spatial forecast accuracy in complex terrain','Calibrated aircraft/ground-resource effectiveness and logistics','Adequate stochastic and forecast ensemble plus independent held-out validation'])
if __name__=='__main__':
 if sys.platform!='linux':raise RuntimeError('VM only')
 print(json.dumps(audit(sys.argv[1],sys.argv[2:]),indent=2))
