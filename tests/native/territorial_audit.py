"""Read-only audit of territorial exposure against original native arrays and hashes."""
import json,sys
from pathlib import Path
import numpy as np
from rasterio.transform import Affine
from rasterio.features import geometry_mask
from pyproj import Transformer
from shapely.geometry import shape,mapping
from shapely.ops import transform
from hazardia.io import load,sha256
root=Path(sys.argv[1]);rows=[];identities=[]
for ident in sys.argv[2:]:
 d=load(root/'web-state/territorial-jobs'/ident/'result.json');job=root/'jobs'/d['job_id'];req=load(job/'request.json');manifest=load(job/'manifest.json');assert d['native_sha256']==manifest['artifacts']['fire-output.npz']
 for name,expected in manifest['artifacts'].items():assert sha256(job/name)==expected
 for a in req['assets']:assert sha256(job/a['path'])==a['sha256']
 with np.load(job/'fire-output.npz',allow_pickle=False) as a:p=a['probability'];arrival=a['arrival'];fire=a['fire']
 project=Transformer.from_crs(4326,req['grid']['crs'],always_xy=True).transform;tr=Affine(*req['grid']['transform']);positive=[];checked=0
 for f in d['features']:
  e=f.get('exposure',{})
  if e.get('status')!='MODELLED':continue
  g=transform(project,shape(f['geometry']));mask=geometry_mask([mapping(g.buffer(75 if g.geom_type=='Point' else 100))],p.shape,tr,invert=True)
  assert np.isclose(e['probability_final_mean'],p[mask].mean());values=arrival[mask];hits=(fire[mask]>0)&np.isfinite(values)&(values>=0);first=np.min(np.where(hits,values,np.inf),axis=0);first=first[np.isfinite(first)]
  assert e['contact_members']==len(first)
  for hour in [0,12,24,48,72]:assert np.isclose(e['timeline_contact'][hour*4],np.count_nonzero(first<=hour*3600)/arrival.shape[2])
  if len(first):positive.append(dict(id=f['id'],members=len(first),first_minutes=e['first_contact_minutes'],mean_probability=e['probability_final_mean']))
  checked+=1
 identities.append(sorted(f['id'] for f in d['features']));rows.append(dict(job_id=d['job_id'],features=len(d['features']),evaluated=checked,assets_verified=len(req['assets']),artifacts_verified=len(manifest['artifacts']),positive=positive))
assert all(x==identities[0] for x in identities)
print(json.dumps(dict(status='PASS',same_feature_inventory=True,rows=rows,qualification='Native input/output consistency, no calibrated risk or suppression-efficacy claim'),indent=2))
