"""VM-only opt-in Castelli fixture. Reuses verified frozen source assets; no provider calls."""
import copy,datetime as dt,json,math,os,pathlib,shutil,sys,uuid
if sys.platform!='linux':raise RuntimeError('VM only')
import numpy as np
from pyproj import Transformer
from rasterio.transform import Affine
from shapely.geometry import shape,Point
from shapely.ops import transform
from hazardia.io import load,sha256,write_new
from hazardia.jobs import JobStore
r=pathlib.Path('/home/hazardia/hazardia-runtime');out=r/'runs/castelli-plan-20261028';out.mkdir(exist_ok=False)
if shutil.disk_usage(r).free<2*1024**3+200*1024**2:raise RuntimeError('Preserve2GiB reserve plus200MiB run allowance')
source=r/'jobs/job-ebe51c3a0c4b4832bda1ab3f117e6ec6';req=load(source/'request.json');series=load(source/'fire-series.json');manifest=load(source/'manifest.json');assert sha256(source/'fire-series.json')==manifest['artifacts']['fire-series.json']
context=next((r/'web-state/territorial-cache').glob('*/snapshot-6e4d6c712da948b49f76eb6085f86834.json'));assets=load(context);target=next(f for f in assets['features'] if f['id']=='builtup-1336');project=Transformer.from_crs(4326,req['grid']['crs'],always_xy=True);back=Transformer.from_crs(req['grid']['crs'],4326,always_xy=True);g=transform(project.transform,shape(target['geometry']));center=g.representative_point();desired=Point(center.x-300,center.y)
tr=Affine(*req['grid']['transform']);arrays=next(a for a in req['assets'] if a['role']=='fire_arrays');a=np.load(source/arrays['path'],allow_pickle=False);veg=a['veg'];c,row=(~tr)*(desired.x,desired.y);choices=[]
for y in range(int(row)-5,int(row)+6):
 for x in range(int(c)-5,int(c)+6):
  if 2<=x<veg.shape[1]-2 and 2<=y<veg.shape[0]-2 and veg[y,x]!=0:
   X,Y=tr*(x+.5,y+.5);choices.append((math.hypot(X-desired.x,Y-desired.y),y,x,X,Y))
assert choices,'No burnable cell within150m of declared point';distance,row,col,X,Y=min(choices);lon,lat=back.transform(X,Y);ignition=[lat,lon]
plan=copy.deepcopy(series['plan']);plan.update(case='A',ignition_wgs84=ignition,ignitions_wgs84=[dict(id='castelli-hypothetical',point=ignition,at_minutes=0)],resources=[],action_times=[],comparison_times=[0,900,1800,2700]);plan['records']=plan['records'][:12];plan['weather_changes']=[]
weather=load(source/next(a['path'] for a in req['assets'] if a['role']=='weather'));field=weather['distributed_field'];ys,xs=field['lats'],field['lons'];gx=(lon-xs[0])/(xs[1]-xs[0]);gy=(lat-ys[0])/(ys[1]-ys[0]);ix=min(7,int(gx));iy=min(7,int(gy));dx=gx-ix;dy=gy-iy;index=iy*9+ix
assert 0<=gx<=8 and 0<=gy<=8
for record in weather['records']:
 f=next(f for f in field['records'] if f['at']==record['at'])
 def value(key):
  z=f[key];return z[index]*(1-dx)*(1-dy)+z[index+1]*dx*(1-dy)+z[index+9]*(1-dx)*dy+z[index+10]*dx*dy
 u,v=value('u'),value('v');record['values']=dict(wind_speed_10m=math.hypot(u,v),wind_direction_10m=(math.degrees(math.atan2(-u,-v))+360)%360,temperature_2m=value('temperature'),relative_humidity_2m=value('humidity'),precipitation=value('precipitation'),surface_pressure=value('pressure'),shortwave_radiation=value('radiation'))
by={v['at']:v['values'] for v in weather['records']}
for v in plan['records']:v['values']=by[v['at']]
req['id']='castelli-reference-'+uuid.uuid4().hex;req['options'].update(duration_s=43200,realizations=4,ignition=[row,col]);req['valid_until']=(dt.datetime.fromisoformat(req['valid_from'].replace('Z','+00:00'))+dt.timedelta(hours=12)).isoformat().replace('+00:00','Z');req['assumptions']+=['Castelli hypothetical ignition near classified built-up footprint; frozen18Oct2026 weather, not a current forecast','All scenario positions/arrival/availability are research assumptions; no dispatch','Shared action clock; no independent intervention expiry or calibrated duration']
fleet=[dict(id='squadra-1',category='waterline_action',available=True,arrival_minutes=0),dict(id='squadra-2',category='waterline_action',available=True,arrival_minutes=15),dict(id='squadra-3',category='waterline_action',available=True,arrival_minutes=30),dict(id='mezzo-pesante-1',category='heavy_action',available=True,arrival_minutes=45),dict(id='canadair-1',category='canadair',available=True,arrival_minutes=30),dict(id='elicottero-1',category='helicopter',available=True,arrival_minutes=15)]
protocol=dict(run_id=out.name,source_job=source.name,source_request_sha256=sha256(source/'request.json'),frozen_context_path=str(context),frozen_context_sha256=sha256(context),target=target,locality_reference=dict(name='Castelli',source='GeoNames3179626, locality point not a town boundary',point=[42.48476,13.71201]),ignition=ignition,distance_to_builtup_m=g.distance(Point(X,Y)),selection_rule='Nearest existing burnable grid cell within150m of a point300m west of builtup1336 representative point; fixed before simulation',duration_h=12,realizations=4,seed=1729,fleet=fleet,unit_duration='Available from declared arrival through the end of this12hscenario; selected ideal barriers persist; no independent work-duration/consumable/expiry model',optimization='Highest authored priority for settlement/residential; HiGHS checked allocation and verified greedy fallback on same problem; joint PROPAGATOR replay required',qualification='HYPOTHETICAL_FROZEN_REPLAY_NOT_CURRENT_FORECAST',workspace_sha256=sha256(r/'web-state/fire-workspace/workspace.json'))
write_new(out/'protocol.json',protocol);write_new(out/'assets.json',assets);stage=out/'baseline-input';stage.mkdir()
for asset in req['assets']:
 src=source/asset['path'];assert sha256(src)==asset['sha256'];dest=stage/asset['path'];dest.parent.mkdir(parents=True,exist_ok=True)
 if asset['role']=='fire_plan':write_new(dest,plan)
 elif asset['role']=='weather':write_new(dest,weather)
 else:os.link(src,dest)
 asset['sha256']=sha256(dest)
store=JobStore(r/'jobs',r/'runtime-fire-studio.json');job=store.submit(req,stage);write_new(out/'baseline.json',dict(job_id=job,request=req));print(json.dumps(dict(job_id=job,ignition=ignition,distance_to_builtup_m=protocol['distance_to_builtup_m'],out=str(out))))
