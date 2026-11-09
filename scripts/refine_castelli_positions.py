"""Exploratory finite native position search after the preserved proxy assignment. VM only."""
import copy,json,pathlib,math,time,uuid,urllib.request,shutil
from hazardia.io import load,write_new,sha256
from hazardia.jobs import JobStore
from pyproj import Transformer
from shapely.geometry import Polygon,Point,shape,mapping
from shapely.ops import transform
import numpy as np
from rasterio.features import geometry_mask
from rasterio.transform import Affine
r=pathlib.Path('/home/hazardia/hazardia-runtime');out=r/'runs/castelli-dry-v2-plan-20261028';dest=out/'position-search';dest.mkdir(exist_ok=False)
if shutil.disk_usage(r).free<2*1024**3+150*1024**2:raise RuntimeError('Reserve2GiB plus150MiB for bounded search')
rows=load(out/'comparisons.json');q=load(r/'jobs'/rows[0]['jobs']['A']/'request.json');project=Transformer.from_crs(4326,q['grid']['crs'],always_xy=True);back=Transformer.from_crs(q['grid']['crs'],4326,always_xy=True);baseunit=rows[0]['selected'][0];area=Polygon([project.transform(p[1],p[0]) for p in baseunit['area']]);center=area.centroid;ignition=load(r/'jobs'/rows[0]['jobs']['A']/'fire-series.json')['plan']['ignitions_wgs84'][0]['point'];ix,iy=project.transform(ignition[1],ignition[0]);dx,dy=ix-center.x,iy-center.y;length=math.hypot(dx,dy);candidates=[]
for distance in [0,100,200]:
 points=[[lat,lon] for lon,lat in [back.transform(x+distance*dx/length,y+distance*dy/length) for x,y in list(area.exterior.coords)[:-1]]];g=Polygon([project.transform(p[1],p[0]) for p in points]);assert not g.covers(Point(ix,iy)),'Do not suppress the authored ignition cell before it is ignited'
 assert abs(g.area-area.area)<1;pixels=[(~Affine(*q['grid']['transform']))*project.transform(p[1],p[0]) for p in points];assert all(2<=c<q['grid']['shape'][1]-2 and 2<=y<q['grid']['shape'][0]-2 for c,y in pixels)
 candidates.append(dict(id='toward-ignition-'+str(distance)+'m',distance_m=distance,area=points))
write_new(dest/'protocol.json',dict(algorithm='EXPLORATORY_FINITE_NATIVE_POSITION_SEARCH',candidate_rule='Translate the assigned300m square by0/100/200m along the metric vector toward ignition; exclude ignition coverage and out-of-grid candidates; fixed before new runs',candidates=candidates,assignment='Keep the existing checked ground unit and its arrival; this refines positions, not a global joint fleet/continuous-space search',objective='Minimize native weighted interface mean/max index; total area breaks ties',cases=['primary','reduced-fleet'],all_inputs_frozen=True,qualification='UNQUALIFIED_IDEAL_RESEARCH'))
context=load(out/'prepared/context.json');target=next(a for a in context['assets'] if a['feature_id']=='builtup-1279');geom=transform(project.transform,shape(target['geometry'])).buffer(100);mask=geometry_mask([mapping(geom)],tuple(q['grid']['shape']),Affine(*q['grid']['transform']),invert=True);robust=context['body']['robust'];store=JobStore(r/'jobs',r/'runtime-fire-studio.json');results=[]
for variant in ['primary','reduced-fleet']:
 original=next(v for v in rows if v['variant']==variant);source=r/'jobs'/original['jobs']['B'];request=load(source/'request.json');oldplan=load(source/'fire-series.json')['plan'];unit=original['selected'][0]
 for candidate in candidates:
  if candidate['distance_m']==0:job=original['jobs']['B']
  else:
   stage=dest/(variant+'-'+candidate['id']);stage.mkdir();req=copy.deepcopy(request);req['id']='castelli-position-'+uuid.uuid4().hex;plan=copy.deepcopy(oldplan);plan['resources'][0]['area']=candidate['area'];req['assumptions']+=['Declared finite position-search candidate '+candidate['id']+'; keep assignment and activation; no initial ignition coverage']
   for a in req['assets']:
    src=source/a['path'];assert sha256(src)==a['sha256'];p=stage/a['path'];p.parent.mkdir(parents=True,exist_ok=True)
    if a['role']=='fire_plan':write_new(p,plan)
    else:p.hardlink_to(src)
    a['sha256']=sha256(p)
   job=store.submit(req,stage);write_new(stage/'accepted.json',dict(job_id=job));started=time.monotonic()
   while store.get(job)['state'] in ['QUEUED','RUNNING']:
    if time.monotonic()-started>950:raise RuntimeError('Bounded native wait expired '+job)
    time.sleep(1)
   assert store.get(job)['state']=='SUCCEEDED',store.get(job)
  series=load(r/'jobs'/job/'fire-series.json')
  with np.load(r/'jobs'/job/'fire-output.npz') as a:p=a['probability'][mask]
  score=target['priority_weight']*((1-robust)*float(p.mean())+robust*float(p.max()));record=dict(variant=variant,candidate=candidate['id'],distance_m=candidate['distance_m'],job_id=job,area=candidate['area'],unit=unit['id'],activation_minutes=unit['at_minutes'],native_priority_index=score,expected_area_ha=series['frames'][-1]['expected_area_ha']);results.append(record);write_new(dest/(variant+'-'+candidate['id']+'.json'),record);print(json.dumps(record),flush=True)
selected={variant:min([v for v in results if v['variant']==variant],key=lambda v:(v['native_priority_index'],v['expected_area_ha'],v['candidate'])) for variant in ['primary','reduced-fleet']};write_new(dest/'results.json',dict(candidates=results,selected=selected));print('POSITION_SEARCH_COMPLETED',flush=True)
