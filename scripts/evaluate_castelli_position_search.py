"""Apply the existing full-context physical objective to every finite-search candidate."""
from pathlib import Path
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform
from rasterio.transform import Affine
from hazardia.io import load,write_new,sha256
from hazardia.decision.fire_ideal import local_analysis_mask
r=Path('/home/hazardia/hazardia-runtime');out=r/'runs/castelli-dry-v2-plan-20261028';search=out/'position-search';data=load(search/'results.json');context=load(out/'prepared/context.json');q=load(r/'jobs'/data['candidates'][0]['job_id']/'request.json');tr=Affine(*q['grid']['transform']);project=Transformer.from_crs(4326,q['grid']['crs'],always_xy=True).transform;robust=context['body']['robust'];masks=[]
write_new(search/'full-objective-protocol.json',dict(objective='Existing fire_ideal_evaluation objective on all retained mapped priorities, not solely the initially exposed target',purpose='Guard against displaced exposure of an initially unexposed asset',selection='Lowest full-context native mean/max index, then total expected area, then candidate ID',qualification='Exploratory finite search with same4realizations; no independent held-out validation'))
for g in context['assets']:
 geom=transform(project,shape(g['geometry']));geom=geom.buffer(75 if geom.geom_type=='Point' else 100);window,mask=local_analysis_mask(geom,tr,tuple(q['grid']['shape']));masks.append((g['priority_weight'],window,mask))
for row in data['candidates']:
 with np.load(r/'jobs'/row['job_id']/'fire-output.npz') as a:p=a['probability']
 score=0
 for weight,window,mask in masks:
  vals=p[window][mask]
  if vals.size:score+=weight*((1-robust)*float(vals.mean())+robust*float(vals.max()))
 row['full_context_native_priority_index']=score
 data['selected']={}
for variant in ['primary','reduced-fleet']:data['selected'][variant]=min([v for v in data['candidates'] if v['variant']==variant],key=lambda v:(v['full_context_native_priority_index'],v['expected_area_ha'],v['candidate']))
write_new(search/'full-objective-results.json',data);print(data['selected'])
