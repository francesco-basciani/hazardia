"""Independent pinned-native footprint and product checks, VM fire-env only."""
import hashlib,json,pathlib,sys
if sys.platform!='linux':raise RuntimeError('VM only')
import numpy as np
from pyproj import CRS,Transformer
from rasterio.transform import Affine,array_bounds
from propagator.io.geo import GeographicInfo
from propagator.io.actions import ACTION_CLASSES
from shapely.geometry import LineString
r=pathlib.Path('/home/hazardia/hazardia-runtime');o=r/'runs/three-resource-exercise-20261106'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(o/'protocol.json');d=read(o/'results.json');q=read(o/'request.json');g=q['grid'];tr=Affine(*g['transform']);geo=GeographicInfo(crs=CRS.from_user_input(g['crs']),trans=tr,bounds=array_bounds(*g['shape'],tr),shape=tuple(g['shape']));forbidden=np.load(o/'no-drop-mask.npy',allow_pickle=False);interface=np.load(o/'interface-mask.npy',allow_pickle=False);row,col=q['options']['ignition'];projection=Transformer.from_crs(4326,g['crs'],always_xy=True)
def footprint(u):
 a=ACTION_CLASSES[u['category']](geometries=[LineString([(v[1],v[0]) for v in u['line']])],epsg=4326);m=a.rasterize_action_fuel(geo,0) if u['category']=='heavy_action' else a.rasterize_action_moisture(geo);return np.isfinite(m)
proposals=[]
for spec in p['plans']:
 for u in spec['proposed_resources']:
  m=footprint(u);touch=bool(m[row,col]);overlap=int((m&forbidden).sum()) if u['category']=='canadair' else 0;assert not touch
  rejected=any(v['resource']['id']==u['id'] for v in spec['rejected']);assert rejected==bool(overlap)
  assert (u in spec['resources'])==(not rejected)
  proposals.append(dict(plan=spec['id'],resource_id=u['id'],cells=int(m.sum()),no_drop_overlap_cells=overlap,rejected=rejected))
reference=None;clock=None;events=None;checked=[]
for v in d['candidates']:
 job=r/'jobs'/v['job_id'];req=read(job/'request.json');s=read(job/'fire-series.json');manifest=read(job/'manifest.json');fixed=dict(assets={a['role']:a['sha256'] for a in req['assets'] if a['role']!='fire_plan'},options=req['options'],grid=req['grid'],valid_from=req['valid_from'],valid_until=req['valid_until']);c=[f['elapsed_s'] for f in s['frames']];e=[z['time'] for z in s['consumed_events']]
 if reference is None:reference=fixed;clock=c;events=e
 assert fixed==reference and c==clock and e==events
 assert sha(job/'fire-output.npz')==manifest['artifacts']['fire-output.npz'] and sha(job/'fire-series.json')==manifest['artifacts']['fire-series.json']
 assert s['plan']['resources']==v['resources'];receipts=[u for z in s['consumed_events'] for u in z['resource_receipts']];assert len(receipts)==len(v['resources']);assert all(x['affected_cells']>0 and x['initial_fuel_cells']>0 for x in receipts)
 for u in v['resources']:
  f=next(z for z in p['fleet'] if z['id']==u['id']);assert all(u[k]==f[k] for k in ['category','at_minutes']);assert u['effect']=='native';geom=LineString([projection.transform(x[1],x[0]) for x in u['line']]);assert abs(geom.length-f['length_m'])<1e-5
  if u['category']=='canadair':assert not (footprint(u)&forbidden).any()
 with np.load(job/'fire-output.npz',allow_pickle=False) as z:
  a=z['probability'];assert abs(float(a.sum())*.09-v['total_expected_ha'])<1e-6;assert abs(float(a[interface].sum())*.09-v['interface_expected_ha'])<1e-6
 checked.append(dict(id=v['id'],job_id=v['job_id'],native_actions=len(receipts),aircraft_actions=sum(u['category']=='canadair' for u in receipts),total_expected_ha=v['total_expected_ha'],interface_expected_ha=v['interface_expected_ha']))
assert d['rank_at_12h'] and d['aircraft_increment_ha']>0
assert d['manual']['interface_expected_ha']>d['selected']['interface_expected_ha']
assert d['fallback']['resources']==[u for u in d['selected']['resources'] if u['category']!='canadair']
config=read(r/'runtime-fire-studio.json');hashes={path:sha(pathlib.Path(path))==h for path,h in config['engine_files'].items() if '/fire-src/' in path};assert all(hashes.values());assert sha(r/'web-state/fire-workspace/workspace.json')==p['workspace_sha256']
value=dict(status='PASS',checked=checked,proposals=proposals,all_clocks_and_nonplan_inputs_identical=True,blocked_drop_never_submitted=True,aircraft_outside_exercise_mask=True,initial_cell_untreated=True,exact_native_fallback_checked=True,upstream_fire_files_unchanged=len(hashes),main_workspace_preserved=True,qualification='EXERCISE_GEOMETRY_ONLY_NOT_FLIGHT_CLEARANCE')
(o/'independent-audit.json').write_text(json.dumps(value,indent=2));print(json.dumps(dict(status='PASS',runs=len(checked),proposals=len(proposals),blocked_drops=sum(v['rejected'] for v in proposals),fallback_increment_ha=d['aircraft_increment_ha'])))
