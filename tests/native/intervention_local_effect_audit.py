"""Read-only per-unit audit using the exact pinned upstream intervention rasterizer."""
import argparse,json,sys
from pathlib import Path
from hazardia.io import load,sha256

def audit(root,comparison):
 import numpy as np
 from propagator.io.actions import build_mask
 from propagator.io.geo import GeographicInfo
 from shapely.geometry import Polygon
 from pyproj import CRS
 from rasterio.transform import Affine,array_bounds
 root=Path(root);replay=load(root/'web-state'/comparison/'replay.json');paths={k:root/'jobs'/j for k,j in replay['jobs'].items()};request=load(paths['A']/'request.json');series={k:load(p/'fire-series.json') for k,p in paths.items()};grid=request['grid'];tr=Affine(*grid['transform']);geo=GeographicInfo(crs=CRS.from_user_input(grid['crs']),trans=tr,bounds=array_bounds(*grid['shape'],tr),shape=tuple(grid['shape']));data={}
 for k,p in paths.items():
  m=load(p/'manifest.json');assert sha256(p/'fire-output.npz')==m['artifacts']['fire-output.npz']
  with np.load(p/'fire-output.npz',allow_pickle=False) as a:data[k]={n:a[n].copy() for n in ['probability','fire','arrival']}
 rows=[]
 for u in series['B']['plan']['resources']:
  assert u['effect']=='fuel_removal' and 'area' in u
  mask=build_mask([Polygon([(p[1],p[0]) for p in u['area']])],geo,src_epsg=4326);cases={}
  for k,d in data.items():
   fire=d['fire'][mask];times=d['arrival'][mask];burned=fire>0;prob=d['probability'][mask];valid=times[burned]
   cases[k]=dict(positive_cells=int((prob>0).sum()),mean_probability=float(prob.mean()),max_probability=float(prob.max()),expected_reached_area_ha=float(prob.sum(dtype=np.float64)*tr.a**2/10000),first_native_contact_minutes=float(valid.min()/60) if valid.size else None)
  rows.append(dict(unit_id=u['id'],effect=u['effect'],activation_minutes=u['at_minutes'],cells=int(mask.sum()),geometry_area_ha=float(mask.sum()*tr.a**2/10000),cases=cases))
 assert rows and all(r['cells']>0 for r in rows)
 cfg=load(root/'runtime-v2.json');assert all(sha256(Path(p))==h for p,h in cfg['engine_files'].items())
 return dict(run_id='intervention-local-effect-20261019',status='PASS',comparison_id=comparison,rows=rows,engine_pins=len(cfg['engine_files']),qualification='Exact native fuel-removal masks; local effect is an ideal barrier, not category effectiveness or global containment; no new model run.')
if __name__=='__main__':
 if sys.platform!='linux':raise RuntimeError('VM only')
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--comparison',required=True);p.add_argument('--out',required=True);a=p.parse_args();r=audit(a.runtime,a.comparison);Path(a.out).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
