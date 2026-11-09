"""VM-only, preregistered finite native placement search. No upstream changes."""
import copy, datetime as dt, json, math, os, pathlib, shutil, sys, time, uuid
if sys.platform != 'linux': raise RuntimeError('Scientific runtime requires Linux VM')
import numpy as np
from pyproj import Transformer
from rasterio.transform import Affine
from rasterio.features import geometry_mask
from shapely.geometry import Point, LineString, shape, mapping
from shapely.ops import transform, nearest_points, unary_union
from hazardia.io import load, write_new, sha256, utcnow
from hazardia.jobs import JobStore
from hazardia.dynamic_stage import stage
R=pathlib.Path('/home/hazardia/hazardia-runtime')
OUT=R/'runs/same-fleet-settlement-20261105'
TERRAIN=R/'terrain-cache/e97be42ecdae76e0a67e32ae3869c23edda7de8516287df69686b0a4cd21e684'
FIELD=R/'web-state/map-weather/map-weather-81451f63bfbdc9968e91b285.json'
CASE='castelli-stessa-flotta-20261105'

def prepare():
 if shutil.disk_usage(R).free < 2*1024**3+350*1024**2: raise RuntimeError('Disk reserve')
 OUT.mkdir(exist_ok=False)
 g=load(TERRAIN/'grid.json');tr=Affine(*g['transform']);to=Transformer.from_crs(4326,g['crs'],always_xy=True);back=Transformer.from_crs(g['crs'],4326,always_xy=True)
 context=next((R/'web-state/territorial-cache').glob('*/snapshot-6e4d6c712da948b49f76eb6085f86834.json'));features=load(context)['features'];target=next(f for f in features if f['id']=='builtup-1336');town=transform(to.transform,shape(target['geometry']));rep=town.representative_point();desired=Point(town.bounds[2]+150,rep.y)
 with np.load(TERRAIN/'expanded-arrays.npz',allow_pickle=False) as z:veg=z['veg'];dem=z['dem']
 col,row=(~tr)*(desired.x,desired.y);candidates=[]
 for y in range(int(row)-3,int(row)+4):
  for x in range(int(col)-3,int(col)+4):
   X,Y=tr*(x+.5,y+.5);p=Point(X,Y)
   if veg[y,x] and 115<=town.distance(p)<=200:candidates.append((p.distance(desired),y,x,X,Y))
 assert candidates,'No admissible nearby burnable ignition'
 _,row,col,X,Y=min(candidates);ign=Point(X,Y);near=nearest_points(town,ign)[0];d=ign.distance(near);ux,uy=(near.x-X)/d,(near.y-Y)/d;vx,vy=-uy,ux
 def latlon(x,y):lon,lat=back.transform(x,y);return [lat,lon]
 def line(cx,cy,ax,ay,length):return [latlon(cx-ax*length/2,cy-ay*length/2),latlon(cx+ax*length/2,cy+ay*length/2)]
 def unit(id,cat,at,points):return dict(id=id,category=cat,at_minutes=at,line=points,effect='native')
 # Same categories, lengths, arrival and native effects; only translation/rotation varies.
 manual=[unit('ground-1','waterline_action',0,line(X+90*vx+45*ux,Y+90*vy+45*uy,ux,uy,90)),unit('heavy-1','heavy_action',10,line(X-90*vx+45*ux,Y-90*vy+45*uy,ux,uy,120))]
 plans=[dict(id='manual',resources=manual)]
 for offset in [30,60,90]:
  cx,cy=X+offset*ux,Y+offset*uy
  plans.append(dict(id='front-'+str(offset)+'m',resources=[unit('ground-1','waterline_action',0,line(cx+45*vx,cy+45*vy,vx,vy,90)),unit('heavy-1','heavy_action',10,line(cx-60*vx,cy-60*vy,vx,vy,120))]))
 for plan in plans:
  for u in plan['resources']:
   coords=[to.transform(p[1],p[0]) for p in u['line']];geom=LineString(coords);assert not geom.buffer(15).covers(ign),'No ignition-cell treatment';assert abs(geom.length-({'waterline_action':90,'heavy_action':120}[u['category']]))<1e-5
   for x,y in coords:
    c,r=(~tr)*(x,y);assert 2<=c<g['shape'][1]-2 and 2<=r<g['shape'][0]-2
 # All mapped built-up footprints within1km, not an isolated cherry-picked target.
 nearby=[f for f in features if f.get('properties',{}).get('category')=='settlement' and transform(to.transform,shape(f['geometry'])).distance(ign)<1000]
 interface=unary_union([transform(to.transform,shape(f['geometry'])).buffer(100) for f in nearby]);mask=geometry_mask([mapping(interface)],tuple(g['shape']),tr,invert=True)&(veg!=0)
 assert mask.any() and not mask[row,col], 'Initial ignition must be outside the scored interface'
 np.save(OUT/'interface-mask.npy',mask,allow_pickle=False);write_new(OUT/'targets.geojson',dict(type='FeatureCollection',features=nearby));write_new(OUT/'interface.geojson',dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(label='100m research interface, not a safety buffer'),geometry=mapping(transform(back.transform,interface)))]))
 field=load(FIELD);start='2026-11-05T16:00:00Z';body=dict(ignitions=[dict(id='castelli-interface',point=latlon(X,Y),at_minutes=0)],hours=12,seed=1729,moisture_percent=15,resources=[],weather_source='FORECAST',weather_changes=[],start_at=start,moisture_model='HFFMC_1977',antecedent_hours=0,realizations=4,comparison_times=sorted(set([0,300,600,900,1800,2700]+list(range(3600,43200,3600)))))
 protocol=dict(run_id=OUT.name,created_at=utcnow(),code_commit='f3356f53ceccd05bb849fff6c872fcce461422d7',dirty_tree=True,script_sha256=sha256(pathlib.Path(__file__)),host=os.uname().nodename,python=sys.version,versions={k:__import__(k).__version__ for k in ['numpy','rasterio','shapely','pyproj']},runtime_sha256=sha256(R/'runtime-fire-studio.json'),terrain_manifest_sha256=sha256(TERRAIN/'manifest.json'),field_sha256=sha256(FIELD),weather_source=field['source'],weather_issued_at=field.get('issued_at'),weather_valid_from=start,weather_valid_until='2026-11-06T04:00:00Z',context_sha256=sha256(context),context_path=str(context),terrain_id=TERRAIN.name,target_ids=[f['id'] for f in nearby],primary_target='builtup-1336',ignition=body['ignitions'][0],distance_to_primary_builtup_m=d,initial_elevation_m=float(dem[row,col]),body=body,plans=plans,objective='Lexicographic: minimum ensemble expected vegetated area reached within100m of all mapped builtup footprints within1km, then maximum per-cell probability in that interface, then total expected area. These are research proxies, not loss of houses.',budget=dict(native_runs=5,timeout_per_run_s=950,realizations=4,additional_runs=0),selection_rule='One fixed manual flank plan plus three fixed front lines30/60/90m from ignition toward nearest mapped builtup. Ground90m at0min, heavy120m at10min; translate/rotate only. Exclude initial-cell treatment and out-of-grid endpoints before simulations.',hypothesis='A front placement may reduce builtup-interface exposure relative to same-fleet flank placement; preserve ties and negative outcomes.',qualification='HYPOTHETICAL_REAL_FORECAST_UNQUALIFIED_RESEARCH',limitations=['WorldCover2021 builtup occupancy/population not known; not a per-house damage model','30m cells; line length is a scenario assumption, not certified crew production or safe deployment','Native waterline moisture27percent and heavy vegetation removal; no independent work duration, refill, access/safety or suppression calibration','HFFMC responds hourly to real temperature/RH/wind/rain; initial FFMC85 assumed, no measured fuel moisture or antecedent initialization','Forecast issue time not supplied by provider; acquisition time is not model issue time','Finite four-placement comparison, no global optimum or operational validation'],workspace_sha256=sha256(R/'web-state/fire-workspace/workspace.json'))
 write_new(OUT/'protocol.json',protocol)
 baseline=OUT/'baseline';baseline.mkdir();write_new(baseline/'body.json',body);write_new(baseline/'terrain.json',dict(path=str(TERRAIN),sha256=sha256(TERRAIN/'manifest.json')));write_new(baseline/'field.json',field)
 stage(R,baseline);q=load(baseline/'request.json');q['assumptions']+=protocol['limitations'];write_new(OUT/'request.json',q)
 print(json.dumps(dict(protocol=str(OUT/'protocol.json'),ignition=protocol['ignition'],distance_m=d,targets=len(nearby))),flush=True)

def run():
 p=load(OUT/'protocol.json');store=JobStore(R/'jobs',R/'runtime-fire-studio.json');mask=np.load(OUT/'interface-mask.npy',allow_pickle=False);results=[];clock=None
 for spec in [dict(id='baseline',resources=[])]+p['plans']:
  stage_dir=OUT/('run-'+spec['id']);stage_dir.mkdir();req=copy.deepcopy(load(OUT/'request.json'));req['id']='settlement-'+uuid.uuid4().hex;plan=load(OUT/'baseline/plan.json');plan.update(case='B',resources=spec['resources'],action_times=sorted({int(u['at_minutes']*60) for u in spec['resources']}))
  for a in req['assets']:
   src=OUT/'baseline'/a['path'];dst=stage_dir/a['path'];dst.parent.mkdir(parents=True,exist_ok=True)
   if a['role']=='fire_plan':write_new(dst,plan)
   else:os.link(src,dst)
   a['sha256']=sha256(dst)
  t=time.monotonic();job=store.submit(req,stage_dir);write_new(stage_dir/'accepted.json',dict(job_id=job));print(json.dumps(dict(plan=spec['id'],job_id=job,state='QUEUED')),flush=True)
  while store.get(job)['state'] in ['QUEUED','RUNNING']:
   if time.monotonic()-t>950:store.cancel(job);raise RuntimeError('Native deadline '+job)
   time.sleep(1)
  assert store.get(job)['state']=='SUCCEEDED',store.get(job)
  s=load(R/'jobs'/job/'fire-series.json');m=load(R/'jobs'/job/'manifest.json');assert sha256(R/'jobs'/job/'fire-output.npz')==m['artifacts']['fire-output.npz']
  with np.load(R/'jobs'/job/'fire-output.npz',allow_pickle=False) as a:prob=a['probability'][mask]
  times=[x['elapsed_s'] for x in s['frames']]
  if clock is None:clock=times
  assert times==clock,'Clock mismatch'
  metrics=dict(id=spec['id'],job_id=job,resources=spec['resources'],interface_expected_ha=float(prob.sum())*.09,interface_max_probability=float(prob.max()),interface_cells_with_nonzero_probability=int((prob>0).sum()),total_expected_ha=s['frames'][-1]['expected_area_ha'],wall_seconds=time.monotonic()-t,series_sha256=sha256(R/'jobs'/job/'fire-series.json'))
  results.append(metrics);write_new(stage_dir/'metrics.json',metrics);print(json.dumps(metrics),flush=True)
 rank=lambda x:(x['interface_expected_ha'],x['interface_max_probability'],x['total_expected_ha'],x['id'])
 selected=min(results[1:],key=rank);manual=results[1];all_requests=[load(R/'jobs'/v['job_id']/'request.json') for v in results];static=lambda q:{a['role']:a['sha256'] for a in q['assets'] if a['role']!='fire_plan'}
 assert all(static(q)==static(all_requests[0]) and all(q[k]==all_requests[0][k] for k in ['options','grid','valid_from','valid_until']) for q in all_requests)
 assert all([(u['id'],u['category'],u['at_minutes'],u['effect']) for u in x['resources']]==[(u['id'],u['category'],u['at_minutes'],u['effect']) for u in manual['resources']] for x in results[1:])
 write_new(OUT/'results.json',dict(selection_status='PROVISIONAL_REQUIRES_NATIVE_FOOTPRINT_AUDIT',candidates=results,selected=selected,manual=manual,improved=rank(selected)<rank(manual),shared_inputs_verified=True,main_workspace_unchanged=sha256(R/'web-state/fire-workspace/workspace.json')==p['workspace_sha256']))
 print('COMPLETE',flush=True)

if __name__=='__main__': {'prepare':prepare,'run':run}[sys.argv[1]]()
