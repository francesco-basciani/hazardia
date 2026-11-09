"""VM-only research exercise: three-category fleet with an authored no-drop constraint."""
import copy,gzip,json,math,os,pathlib,shutil,sys,time,uuid
if sys.platform!='linux':raise RuntimeError('VM scientific runtime required')
import numpy as np
from pyproj import Transformer
from rasterio.transform import Affine
from rasterio.features import geometry_mask,rasterize
from scipy.ndimage import binary_dilation
from shapely.geometry import shape,Point,LineString,mapping
from shapely.ops import transform,nearest_points,unary_union
from hazardia.io import load,sha256,write_new,utcnow
from hazardia.jobs import JobStore
R=pathlib.Path('/home/hazardia/hazardia-runtime');O=R/'runs/three-resource-exercise-20261106';PARENT=R/'runs/three-plan-demonstration-20261105';CASE='castelli-tre-risorse-20261106'

def prepare():
 if shutil.disk_usage(R).free<2*1024**3+500*1024**2:raise RuntimeError('2GiB reserve plus500MiB allowance')
 O.mkdir(exist_ok=False);prior=load(PARENT/'protocol.json');q=load(PARENT/'request.json');g=q['grid'];tr=Affine(*g['transform']);to=Transformer.from_crs(4326,g['crs'],always_xy=True);back=Transformer.from_crs(g['crs'],4326,always_xy=True)
 features=load(PARENT/'targets.geojson')['features'];towns=[transform(to.transform,shape(f['geometry'])) for f in features];primary=next(transform(to.transform,shape(f['geometry'])) for f in features if f['id']=='builtup-1336');p=prior['ignition']['point'];X,Y=to.transform(p[1],p[0]);ign=Point(X,Y);near=nearest_points(primary,ign)[0];d=near.distance(ign);ux,uy=(near.x-X)/d,(near.y-Y)/d;vx,vy=-uy,ux
 with np.load(PARENT/'baseline/arrays.npz',allow_pickle=False) as z:veg=z['veg']
 built=unary_union(towns);excluded=built.buffer(60);no_drop=geometry_mask([mapping(excluded)],tuple(g['shape']),tr,all_touched=True,invert=True);np.save(O/'no-drop-mask.npy',no_drop,allow_pickle=False);shutil.copyfile(PARENT/'interface-mask.npy',O/'interface-mask.npy');shutil.copyfile(PARENT/'targets.geojson',O/'targets.geojson')
 write_new(O/'no-drop.geojson',dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(kind='AUTHORED_NO_DROP',buffer_m=60,meaning='Exercise only. Not a legal stand-off distance, flight clearance or verified residential boundary.'),geometry=mapping(transform(back.transform,excluded)))]))
 def latlon(x,y):lon,lat=back.transform(x,y);return [lat,lon]
 def line(cx,cy,ax,ay,length):return [latlon(cx-ax*length/2,cy-ay*length/2),latlon(cx+ax*length/2,cy+ay*length/2)]
 fleet=[dict(id='ground-1',category='waterline_action',at_minutes=0,length_m=90),dict(id='heavy-1',category='heavy_action',at_minutes=10,length_m=120),dict(id='canadair-1',category='canadair',at_minutes=20,length_m=240)]
 def u(index,points):f=fleet[index];return dict(id=f['id'],category=f['category'],at_minutes=f['at_minutes'],effect='native',line=points)
 def ground(offset):cx,cy=X+offset*ux,Y+offset*uy;return [u(0,line(cx+45*vx,cy+45*vy,vx,vy,90)),u(1,line(cx-60*vx,cy-60*vy,vx,vy,120))]
 proposed=u(2,line(primary.representative_point().x,primary.representative_point().y,vx,vy,240));plans=[]
 for offset in [120,150]:plans.append(dict(id='uncoordinated-'+str(offset),proposed_resources=ground(offset)+[proposed]))
 for ground_offset in [180,210]:
  for air_offset in [60,90]:plans.append(dict(id='combined-'+str(ground_offset)+'-'+str(air_offset),proposed_resources=ground(ground_offset)+[u(2,line(X+air_offset*ux,Y+air_offset*uy,vx,vy,240))]))
 row,col=q['options']['ignition'];preflight=[]
 for plan in plans:
  executed=[];rejected=[];checks=[]
  for unit in plan['proposed_resources']:
   coords=[to.transform(v[1],v[0]) for v in unit['line']];geom=LineString(coords);assert abs(geom.length-next(f['length_m'] for f in fleet if f['id']==unit['id']))<1e-5
   for x,y in coords:
    c,r=(~tr)*(x,y);assert 2<=c<g['shape'][1]-2 and 2<=r<g['shape'][0]-2
   native=binary_dilation(rasterize([(mapping(geom),1)],out_shape=tuple(g['shape']),transform=tr,all_touched=True,dtype='uint8').astype(bool));touches_initial=bool(native[row,col]);overlap=int((native&no_drop).sum()) if unit['category']=='canadair' else 0
   check=dict(resource_id=unit['id'],category=unit['category'],affected_cells=int(native.sum()),initial_fuel_cells=int((native&(veg!=0)).sum()),touches_initial_cell=touches_initial,no_drop_cells=overlap);checks.append(check)
   assert not touches_initial,'No treatment of initial ignition cell'
   if overlap:rejected.append(dict(resource=unit,reason='EXERCISE_NO_DROP_OVERLAP',overlap_cells=overlap))
   else:executed.append(unit)
  plan.update(resources=executed,rejected=rejected);preflight.append(dict(id=plan['id'],checks=checks,rejected=len(rejected)))
  assert len(rejected)==(1 if plan['id'].startswith('uncoordinated') else 0)
 protocol=dict(run_id=O.name,at=utcnow(),code_commit='1d99ee0c71957d82e3cb33b6fcbc9164c0f41043',dirty_tree=True,script_sha256=sha256(pathlib.Path(__file__)),python=sys.version,host=os.uname().nodename,runtime_sha256=sha256(R/'runtime-fire-studio.json'),parent_protocol_sha256=sha256(PARENT/'protocol.json'),parent_request_sha256=sha256(PARENT/'request.json'),source=prior['weather_source'],weather_issued_at=prior['weather_issued_at'],valid_from=q['valid_from'],valid_until=q['valid_until'],seed=1729,realizations=4,duration_h=12,ignition=prior['ignition'],territory_source=load(R/'terrain-cache'/prior['terrain_id']/'manifest.json'),fleet=fleet,plans=plans,exclusion=dict(source='ESA WorldCover2021 mapped built-up footprints',buffer_m=60,status='AUTHORED_EXERCISE_CONSTRAINT_NOT_LEGAL_DISTANCE',native_mask_sha256=sha256(O/'no-drop-mask.npy'),flight_authority='NOT_GRANTED',unassessed=['wire clearance','flight envelope','drop drift','people locations','pilot/DOS authorization','water/refill/arrival logistics']),budget=dict(native_runs=8,timeout_per_run_s=950,additional_runs=0),objective='Minimise expected vegetated hectares reached within100m of all8mapped built-up clusters; total area breaks ties. Same inventory/activation/authored lengths. Reject an entire aircraft proposal whose native dilated footprint intersects the exercise no-drop mask; never clip a drop or simulate a forbidden proposal.',selection='Baseline plus two uncoordinated ground positions120/150m with same rejected aircraft proposal; four combined plans(ground180/210m, air60/90m). Choose an illustrative uncoordinated plan below baseline if available, then combined plan improving interface/area. One final no-air fallback using exactly the selected ground resources. Preserve all outputs, including negative results. Didactic selection, not held-out validation.',qualification='HYPOTHETICAL_ARCHIVED_FORECAST_CONSTRAINT_EXERCISE_NO_FLIGHT_CLEARANCE',workspace_sha256=sha256(R/'web-state/fire-workspace/workspace.json'),limitations=['Fuel moisture initialFFMC85 assumed, weather-driven hFFMC; not observed fuel moisture','30m DSM/WorldCover2021, mapped builtup not individual residential occupancy or house damage','Native waterline/moisture and heavy vegetation actions, no calibrated line-production/duration/aircraft capacity','One modelled aircraft action at+20min, no recurring sorties or night drops; no flight clearance from this exercise','60m buffer authored for the example, not an official prohibition or safe stand-off distance','Generic aerial-replay qualification guard remains unchanged; these are isolated research JobStore runs'])
 write_new(O/'protocol.json',protocol);write_new(O/'preflight.json',preflight);base=O/'baseline';base.mkdir();q['options']['realizations']=4;plan=load(PARENT/'baseline/plan.json');plan.update(resources=[],action_times=[],comparison_times=sorted(set(plan['comparison_times']+[1200])))
 for a in q['assets']:
  src=PARENT/'baseline'/a['path'];dst=base/a['path'];dst.parent.mkdir(parents=True,exist_ok=True)
  if a['role']=='fire_plan':write_new(dst,plan)
  else:os.link(src,dst)
  a['sha256']=sha256(dst)
 q['assumptions']+=protocol['limitations'];write_new(O/'request.json',q);print(json.dumps(dict(out=str(O),plans=len(plans),preflight=preflight)),flush=True)

def run():
 p=load(O/'protocol.json');store=JobStore(R/'jobs',R/'runtime-fire-studio.json');mask=np.load(O/'interface-mask.npy',allow_pickle=False);results=[];clock=None
 def solve(spec):
  nonlocal clock
  if shutil.disk_usage(R).free<2*1024**3+50*1024**2:raise RuntimeError('Disk reserve')
  folder=O/('run-'+spec['id']);folder.mkdir();q=copy.deepcopy(load(O/'request.json'));q['id']='three-resources-'+uuid.uuid4().hex;plan=load(O/'baseline/plan.json');plan.update(resources=spec['resources'],action_times=sorted({int(u['at_minutes']*60) for u in spec['resources']}))
  for a in q['assets']:
   src=O/'baseline'/a['path'];dst=folder/a['path'];dst.parent.mkdir(parents=True,exist_ok=True)
   if a['role']=='fire_plan':write_new(dst,plan)
   else:os.link(src,dst)
   a['sha256']=sha256(dst)
  started=time.monotonic();job=store.submit(q,folder);write_new(folder/'accepted.json',dict(job_id=job));print(json.dumps(dict(plan=spec['id'],job_id=job,state='QUEUED')),flush=True)
  while store.get(job)['state'] in ['QUEUED','RUNNING']:
   if time.monotonic()-started>950:store.cancel(job);raise RuntimeError('Native deadline')
   time.sleep(1)
  assert store.get(job)['state']=='SUCCEEDED',store.get(job)
  s=load(R/'jobs'/job/'fire-series.json');m=load(R/'jobs'/job/'manifest.json');assert sha256(R/'jobs'/job/'fire-output.npz')==m['artifacts']['fire-output.npz'];times=[f['elapsed_s'] for f in s['frames']]
  if clock is None:clock=times
  assert clock==times
  with np.load(R/'jobs'/job/'fire-output.npz',allow_pickle=False) as z:a=z['probability'][mask]
  value=dict(id=spec['id'],job_id=job,resources=spec['resources'],interface_expected_ha=float(a.sum())*.09,total_expected_ha=s['frames'][-1]['expected_area_ha'],wall_seconds=time.monotonic()-started,rejected=spec.get('rejected',[]));results.append(value);write_new(folder/'metrics.json',value);print(json.dumps(value),flush=True);return value
 baseline=solve(dict(id='baseline',resources=[]))
 for spec in p['plans']:solve(spec)
 candidates=[v for v in results if v['id'].startswith('uncoordinated') and v['total_expected_ha']<baseline['total_expected_ha']];manual=max(candidates,key=lambda v:(v['interface_expected_ha'],v['total_expected_ha'])) if candidates else results[1]
 combined=[v for v in results if v['id'].startswith('combined') and v['total_expected_ha']<manual['total_expected_ha'] and v['interface_expected_ha']<=manual['interface_expected_ha']];selected=min(combined,key=lambda v:(v['interface_expected_ha'],v['total_expected_ha'])) if combined else min([v for v in results if v['id'].startswith('combined')],key=lambda v:(v['interface_expected_ha'],v['total_expected_ha']))
 fallback=solve(dict(id='fallback-no-air',resources=[u for u in selected['resources'] if u['category']!='canadair']))
 write_new(O/'results.json',dict(candidates=results,baseline=baseline,manual=manual,selected=selected,fallback=fallback,rank_at_12h=baseline['total_expected_ha']>manual['total_expected_ha']>selected['total_expected_ha'],aircraft_increment_ha=fallback['total_expected_ha']-selected['total_expected_ha'],main_workspace_preserved=sha256(R/'web-state/fire-workspace/workspace.json')==p['workspace_sha256']));print('COMPLETE',flush=True)

if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
