"""Single predeclared native replay: aircraft west, ground resources unchanged. VM only."""
import copy,json,pathlib,sys,time,os,shutil
if sys.platform!='linux':raise RuntimeError('VM only')
import numpy as np
from pyproj import CRS,Transformer
from rasterio.transform import Affine,array_bounds
from rasterio.features import geometry_mask,rasterize
from scipy.ndimage import binary_dilation
from shapely.geometry import Point,LineString,shape,mapping
from shapely.ops import transform
from hazardia.io import load,write_new,sha256,utcnow
from hazardia.jobs import JobStore
R=pathlib.Path('/home/hazardia/hazardia-runtime');P=R/'runs/three-resource-exercise-20261106';O=R/'runs/three-resource-west-20261106'
def main():
 assert shutil.disk_usage(R).free>2*1024**3+150*1024**2
 O.mkdir(exist_ok=False);prior=load(P/'results.json');q=load(P/'request.json');g=q['grid'];tr=Affine(*g['transform']);to=Transformer.from_crs(4326,g['crs'],always_xy=True);back=Transformer.from_crs(g['crs'],4326,always_xy=True);p=load(P/'protocol.json');X,Y=to.transform(p['ignition']['point'][1],p['ignition']['point'][0])
 def ll(x,y):lon,lat=back.transform(x,y);return [lat,lon]
 # Fixed before execution: 180m west of ignition, north/south 240m, activation+20min.
 aircraft=dict(id='canadair-1',category='canadair',effect='native',at_minutes=20,line=[ll(X-180,Y-120),ll(X-180,Y+120)])
 resources=copy.deepcopy(prior['manual']['resources'])+[aircraft];geom=LineString([to.transform(v[1],v[0]) for v in aircraft['line']]);foot=binary_dilation(rasterize([(mapping(geom),1)],out_shape=tuple(g['shape']),transform=tr,all_touched=True,dtype='uint8').astype(bool));forbidden=np.load(P/'no-drop-mask.npy',allow_pickle=False)
 with np.load(P/'baseline/arrays.npz',allow_pickle=False) as z:vegetation=z['veg'];counts={str(int(v)):int(n) for v,n in zip(*np.unique(vegetation[foot],return_counts=True))}
 assert not (foot&forbidden).any() and not foot[tuple(q['options']['ignition'])]
 protocol=dict(run_id=O.name,at=utcnow(),code_commit='57390ef',script_sha256=sha256(pathlib.Path(__file__)),parent_protocol_sha256=sha256(P/'protocol.json'),workspace_sha256=sha256(R/'web-state/fire-workspace/workspace.json'),budget_native_runs=1,resources=resources,ground_unchanged=resources[:2]==prior['manual']['resources'],aircraft_position='180m west,240m north-south',footprint_cells=int(foot.sum()),vegetation_native_categories=counts,no_drop_overlap=0,seed=p['seed'],valid_from=q['valid_from'],valid_until=q['valid_until'],hypothesis='West drop treats the wooded flank, while the eastern built-up interface remains reached; existing optimised plan reduces interface. Test, never force the outcome.',qualification='HYPOTHETICAL_ARCHIVED_FORECAST_RESEARCH_NOT_FLIGHT_CLEARANCE')
 write_new(O/'protocol.json',protocol);folder=O/'input';folder.mkdir();plan=load(P/'baseline/plan.json');plan.update(resources=resources,action_times=[0,600,1200]);q['id']='three-resources-west-20261106'
 for asset in q['assets']:
  src=P/'baseline'/asset['path'];dst=folder/asset['path'];dst.parent.mkdir(parents=True,exist_ok=True)
  if asset['role']=='fire_plan':write_new(dst,plan)
  else:os.link(src,dst)
  asset['sha256']=sha256(dst)
 write_new(O/'request.json',q);store=JobStore(R/'jobs',R/'runtime-fire-studio.json');started=time.monotonic();job=store.submit(q,folder);write_new(O/'accepted.json',dict(job_id=job));print(job,flush=True)
 while store.get(job)['state'] in ['QUEUED','RUNNING']:
  if time.monotonic()-started>950:store.cancel(job);raise RuntimeError('Deadline')
  time.sleep(1)
 assert store.get(job)['state']=='SUCCEEDED';values={};targets=[]
 for feature in load(P/'targets.geojson')['features']:
  if feature['geometry']['type'] not in ['Polygon','MultiPolygon']:continue
  geom=transform(to.transform,shape(feature['geometry']));targets.append((feature['id'],geom,geometry_mask([mapping(geom.buffer(100))],tuple(g['shape']),tr,all_touched=True,invert=True),geometry_mask([mapping(geom)],tuple(g['shape']),tr,all_touched=True,invert=True)))
 fixed=None;clock=None
 for key,j in [('baseline',prior['baseline']['job_id']),('west',job),('optimized',prior['selected']['job_id'])]:
  base=R/'jobs'/j;s=load(base/'fire-series.json');req=load(base/'request.json');m=load(base/'manifest.json');assert sha256(base/'fire-output.npz')==m['artifacts']['fire-output.npz'];f=dict(assets={v['role']:v['sha256'] for v in req['assets'] if v['role']!='fire_plan'},options=req['options'],grid=req['grid'],valid_from=req['valid_from'],valid_until=req['valid_until']);c=[v['elapsed_s'] for v in s['frames']]
  if fixed is None:fixed=f;clock=c
  assert fixed==f and clock==c
  with np.load(base/'fire-output.npz',allow_pickle=False) as z:prob=z['probability']
  values[key]=dict(job_id=j,total_ha=float(prob.sum())*.09,interface_ha=float(prob[np.load(P/'interface-mask.npy',allow_pickle=False)].sum())*.09,targets=[dict(id=id,interface_ha=float(prob[mask].sum())*.09,builtup_cells_reached_ha=float(prob[built].sum())*.09) for id,geom,mask,built in targets],native_receipts=[u for e in s['consumed_events'] for u in e['resource_receipts']])
 assert resources[:2]==prior['manual']['resources'];assert sha256(R/'web-state/fire-workspace/workspace.json')==protocol['workspace_sha256'];assert len(values['west']['native_receipts'])==3
 write_new(O/'results.json',dict(values=values,wall_seconds=time.monotonic()-started,ground_unchanged=True,identical_nonplan_inputs_and_clock=True,main_workspace_preserved=True));print(json.dumps(values),flush=True)
if __name__=='__main__':main()
