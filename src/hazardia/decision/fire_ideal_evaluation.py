"""Compare native results on the same mapped priorities. No global optimum claim."""
import json,sys
from pathlib import Path
from hazardia.io import load,write_new,sha256,HazardError

def evaluate(root,folder):
 import numpy as np
 from pyproj import Transformer
 from rasterio.transform import Affine
 from rasterio.features import geometry_mask
 from shapely.geometry import shape,mapping
 from shapely.ops import transform
 root,folder=Path(root),Path(folder);replay=load(folder/'replay.json');context=load(root/'web-state'/(replay['decision_id']+'-input')/'prepared/context.json')
 rows=[];requests=[];plans=[];hashes=[]
 for kind in ['A','B']:
  job=root/'jobs'/replay['jobs'][kind];req=load(job/'request.json');manifest=load(job/'manifest.json');series=load(job/'fire-series.json');plan=series['plan']
  for name in ['fire-output.npz','fire-series.json']:
   if sha256(job/name)!=manifest['artifacts'][name]:raise HazardError('CHECKSUM','Native comparison changed')
  for a in req['assets']:
   if sha256(job/a['path'])!=a['sha256']:raise HazardError('CHECKSUM','Native input changed')
  requests.append(req);plans.append(plan);hashes.append(manifest['artifacts']['fire-output.npz'])
  with np.load(job/'fire-output.npz',allow_pickle=False) as a:p=a['probability']
  if p.shape!=tuple(req['grid']['shape']) or not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise HazardError('INVALID_INPUT','Probability grid')
  tr=Affine(*req['grid']['transform']);project=Transformer.from_crs(4326,req['grid']['crs'],always_xy=True).transform;nominal=stress=0
  for g in context['assets']:
   geom=transform(project,shape(g['geometry']));geom=geom.buffer(75 if geom.geom_type=='Point' else 100);mask=geometry_mask([mapping(geom)],p.shape,tr,invert=True);values=p[mask]
   if values.size:nominal+=g['priority_weight']*float(values.mean());stress+=g['priority_weight']*float(values.max())
  robust=context['body']['robust'];score=(1-robust)*nominal+robust*stress
  rows.append(dict(case=kind,job_id=replay['jobs'][kind],native_priority_index=score,nominal=nominal,stress=stress,area_ha=series['frames'][-1]['expected_area_ha']))
 a,b=requests
 for key in ['grid','options','valid_from','valid_until']:
  if a[key]!=b[key]:raise HazardError('SOURCE_MISMATCH','Comparison differs: '+key)
 static=lambda request:{asset['role']:asset['sha256'] for asset in request['assets'] if asset['role']!='fire_plan'}
 if static(a)!=static(b):raise HazardError('SOURCE_MISMATCH','Frozen terrain or forcing inputs differ')
 for key in ['ignitions_wgs84','weather_changes','forcing','records','action_times','comparison_times','moisture_percent']:
  if plans[0].get(key)!=plans[1].get(key):raise HazardError('SOURCE_MISMATCH','Comparison plan differs: '+key)
 expected=load(root/'web-state'/replay['decision_id']/'ideal-result.json')['ideal']['proposed_resources'];expected=[{k:v for k,v in u.items() if k in ['id','category','area','at_minutes','effect']} for u in expected]
 if plans[1]['resources']!=expected:raise HazardError('SOURCE_MISMATCH','Proposed resources differ from checked decision')
 if plans[0]['resources']:raise HazardError('INVALID_INPUT','Reference has interventions')
 wa=next(x['sha256'] for x in a['assets'] if x['role']=='weather');wb=next(x['sha256'] for x in b['assets'] if x['role']=='weather')
 if wa!=wb:raise HazardError('SOURCE_MISMATCH','Weather mismatch')
 best=min(rows,key=lambda row:(row['native_priority_index'],row['area_ha'],row['case']))
 result=dict(status='COMPARISON_EVALUATED',rows=rows,best_job_id=best['job_id'],best_case=best['case'],objective='Weighted native fire probability on mapped priority areas; mean/max blend as configured, area breaks ties',qualification='BEST_OF_TWO_EVALUATED_NOT_GLOBAL_PHYSICAL_OPTIMUM',operationally_approvable=False,weather_sha256=wa,native_output_sha256=hashes)
 write_new(folder/'evaluation-native.json',result);return result
if __name__=='__main__':evaluate(sys.argv[1],sys.argv[2])
