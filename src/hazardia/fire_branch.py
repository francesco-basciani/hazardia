"""Resource-only conditional replay on verified frozen inputs, never a fresh forecast."""
import copy,shutil,sys,uuid
from pathlib import Path
from hazardia.io import load,write_new,sha256,HazardError,utcnow
from hazardia.firelab import validate

def prepare(root,folder):
 from rasterio.transform import Affine
 from pyproj import Transformer
 from shapely.geometry import LineString,Polygon
 root,folder=Path(root),Path(folder);body=load(folder/'branch.json');input=validate(body['input']);source=root/'jobs'/body['job_id'];req=load(source/'request.json');manifest=load(source/'manifest.json')
 if sha256(source/'fire-series.json')!=manifest['artifacts']['fire-series.json']:raise HazardError('CHECKSUM','Original result changed')
 plan=load(source/'fire-series.json')['plan']
 expected=dict(hours=req['options']['duration_s']//3600,seed=req['options']['seed'],moisture_percent=plan['moisture_percent'],weather_source=plan['weather_source'],weather_changes=plan['weather_changes'],ignitions=plan['ignitions_wgs84'])
 if any(input.get(k)!=v for k,v in expected.items()) or input.get('start_at')!=req['valid_from'] or input.get('moisture_model','HFFMC_1977')!=plan.get('forcing',{}).get('moisture_model','HFFMC_1977'):raise HazardError('SOURCE_MISMATCH','Resource-only replay requires the original ignition, duration, weather and model settings')
 tr=Affine(*req['grid']['transform']);project=Transformer.from_crs(4326,req['grid']['crs'],always_xy=True)
 for unit in input['resources']:
  points=unit.get('line',unit.get('area'));coords=[project.transform(p[1],p[0]) for p in points]
  pixels=[(~tr)*(x,y) for x,y in coords]
  if any(not (2<=c<req['grid']['shape'][1]-2 and 2<=r<req['grid']['shape'][0]-2) for c,r in pixels):raise HazardError('DOMAIN_SPAN','Intervention outside frozen terrain; start a new territory simulation')
  g=LineString(coords) if 'line' in unit else Polygon(coords)
  if g.is_empty or not g.is_valid or ('line' in unit and not 1<=g.length<=50000) or ('area' in unit and not 1<=g.area<=250000000):raise HazardError('INVALID_INPUT','Invalid intervention geometry')
 for asset in req['assets']:
  if sha256(source/asset['path'])!=asset['sha256']:raise HazardError('CHECKSUM','Frozen input changed')
  target=folder/asset['path'];target.parent.mkdir(parents=True,exist_ok=True)
  if asset['role']!='fire_plan':shutil.copyfile(source/asset['path'],target)
 plan=copy.deepcopy(plan);plan.update(case='B',resources=input['resources'],action_times=sorted({int(u['at_minutes']*60) for u in input['resources']}),comparison_times=sorted(set(input.get('comparison_times',[]))|{int(u['at_minutes']*60) for u in input['resources']}|{int(i['at_minutes']*60) for i in input['ignitions']}))
 asset=next(a for a in req['assets'] if a['role']=='fire_plan');write_new(folder/asset['path'],plan);asset['sha256']=sha256(folder/asset['path']);req.update(id='resource-replay-'+uuid.uuid4().hex,snapshot_at=utcnow());req['assumptions']+=['Explicit conditional replay of frozen parent '+body['job_id']+'; original start/weather retained, not a fresh forecast; resource edits only']
 from hazardia.contracts import validate_request
 validate_request(req,folder);write_new(folder/'request.json',req)
if __name__=='__main__':
 try:prepare(sys.argv[1],sys.argv[2])
 except HazardError as e:write_new(Path(sys.argv[2])/'prepare-error.json',dict(code=e.code,detail=str(e)));raise
