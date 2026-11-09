"""Run with pinned PROPAGATOR fire-env in VM; evaluates native footprint admissibility."""
import json,pathlib,sys
if sys.platform!='linux':raise RuntimeError('VM only')
import numpy as np
from propagator.io.actions import ACTION_CLASSES
from propagator.io.geo import GeographicInfo
from rasterio.transform import Affine,array_bounds
from pyproj import CRS,Transformer
from shapely.geometry import LineString
r=pathlib.Path('/home/hazardia/hazardia-runtime');o=r/'runs/same-fleet-settlement-20261105';p=json.loads((o/'protocol.json').read_text());q=json.loads((o/'request.json').read_text());g=q['grid'];tr=Affine(*g['transform']);geo=GeographicInfo(crs=CRS.from_user_input(g['crs']),trans=tr,bounds=array_bounds(*g['shape'],tr),shape=tuple(g['shape']));to=Transformer.from_crs(4326,g['crs'],always_xy=True);i=p['ignition']['point'];x,y=to.transform(i[1],i[0]);c,row=(~tr)*(x,y);row,col=int(row),int(c);out=[]
for plan in p['plans']:
 a=[]
 for u in plan['resources']:
  action=ACTION_CLASSES[u['category']](geometries=[LineString([(v[1],v[0]) for v in u['line']])],epsg=4326);m=action.rasterize_action_moisture(geo) if u['category']=='waterline_action' else action.rasterize_action_fuel(geo,0);a.append(dict(id=u['id'],native_affected_cells=int(np.isfinite(m).sum()),touches_initial_cell=bool(np.isfinite(m[row,col]))))
 out.append(dict(id=plan['id'],resources=a,admissible=not any(v['touches_initial_cell'] for v in a)))
value=dict(rule='Predeclared exclusion of initial-cell treatment evaluated against native dilated footprint, not only authored line. Candidate results retained unchanged.',rows=out)
dest=o/'native-footprint-audit.json'
if dest.exists():assert json.loads(dest.read_text())==value
else:dest.write_text(json.dumps(value,indent=2))
print(json.dumps(value))
