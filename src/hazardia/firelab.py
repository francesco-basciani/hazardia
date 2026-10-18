"""Bounded native comparison staging. Resource actions are upstream research parameters."""
import copy,datetime as dt,math,os,subprocess,uuid
from pathlib import Path
from hazardia.io import load,write_new,sha256,timestamp,utcnow,HazardError

CATEGORIES=('waterline_action','canadair','helicopter','heavy_action')
def number(v,lo,hi):
    if type(v) not in (int,float) or not math.isfinite(v) or not lo<=v<=hi:raise HazardError('INVALID_INPUT','Finite bounded number required')
    return v
def validate(body,*,allow_empty_ignitions=False):
    if not isinstance(body,dict):raise HazardError('INVALID_INPUT','Fire input object required')
    if set(body)-{'ignition','hours','seed','moisture_percent','resources','start_at','forecast_id','weather_source','weather_changes','ignitions','comparison_times','moisture_model','forcing_id'}:raise HazardError('INVALID_INPUT','Unknown fire experiment fields')
    if body.get('moisture_model','HFFMC_1977') not in ['HFFMC_1977','MANUAL']:raise HazardError('INVALID_INPUT','Unknown fuel moisture model')
    if 'forcing_id' in body and (__import__('re').fullmatch('map-weather-[a-f0-9]{24}',str(body['forcing_id'])) is None):raise HazardError('INVALID_INPUT','Invalid distributed forcing identifier')
    for k in ['hours','seed']:
        if type(body.get(k)) is not int:raise HazardError('INVALID_INPUT','Integer duration/seed required')
    number(body['hours'],1,72);number(body['seed'],0,2**31-1);number(body.get('moisture_percent'),0,100)
    def point(p):
        if not isinstance(p,list) or len(p)!=2:raise HazardError('INVALID_INPUT','WGS84 [latitude,longitude] required')
        number(p[0],-85,85);number(p[1],-180,180)
    if 'ignitions' in body:
        ignitions=body['ignitions']
        if 'ignition' in body or not isinstance(ignitions,list) or not (0 if allow_empty_ignitions else 1)<=len(ignitions)<=16:raise HazardError('INVALID_INPUT','Use1..16 timed ignitions or one legacy ignition')
        seen=[]
        for r in ignitions:
            if not isinstance(r,dict) or set(r)!={'id','point','at_minutes'} or not isinstance(r['id'],str) or not 1<=len(r['id'])<=40:raise HazardError('INVALID_INPUT','Strict timed ignition required')
            point(r['point']);number(r['at_minutes'],0,body['hours']*60-1);seen.append(r['id'])
        if len(seen)!=len(set(seen)):raise HazardError('INVALID_INPUT','Duplicate ignition IDs')
    else:point(body.get('ignition'))
    clock=body.get('comparison_times',[])
    if not isinstance(clock,list) or len(clock)>64 or any(type(t) is not int or not 0<=t<body['hours']*3600 for t in clock) or clock!=sorted(set(clock)):raise HazardError('INVALID_TIME','Invalid comparison event clock')
    resources=body.get('resources',[])
    if not isinstance(resources,list) or len(resources)>8:raise HazardError('INVALID_INPUT','At most8 authored action lines')
    ids=[]
    for r in resources:
        if not isinstance(r,dict) or not {'id','category','at_minutes'}<=set(r) or set(r)-{'id','category','line','area','at_minutes','effect'}:raise HazardError('INVALID_INPUT','Strict action row required')
        if not isinstance(r['id'],str) or not 1<=len(r['id'])<=40 or r['category'] not in CATEGORIES:raise HazardError('INVALID_INPUT','Unknown action category/id')
        ids.append(r['id']);number(r['at_minutes'],0,body['hours']*60-1)
        if ('line' in r)==('area' in r):raise HazardError('INVALID_INPUT','Exactly one line or area required')
        if r.get('effect','native') not in ['native','fuel_removal'] or 'area' in r and r.get('effect')!='fuel_removal':raise HazardError('INVALID_INPUT','Area requires explicit fuel removal hypothesis')
        geometry=r.get('line',r.get('area'))
        if not isinstance(geometry,list) or not (len(geometry)==2 if 'line' in r else 3<=len(geometry)<=32):raise HazardError('INVALID_INPUT','Two line endpoints or3..32 polygon vertices required')
        for p in geometry:point(p)
        if len({tuple(p) for p in geometry})!=len(geometry):raise HazardError('INVALID_INPUT','Duplicate geometry vertices')
    if len(ids)!=len(set(ids)):raise HazardError('INVALID_INPUT','Duplicate resource IDs')
    changes=body.get('weather_changes',[])
    if not isinstance(changes,list) or len(changes)>72:raise HazardError('INVALID_INPUT','Bounded weather revisions required')
    hours=[]
    for c in changes:
        if not isinstance(c,dict) or set(c)!={'hour','speed_ms','direction_deg'} or type(c['hour']) is not int:raise HazardError('INVALID_INPUT','Hourly hypothetical wind row required')
        number(c['hour'],0,body['hours']-1);number(c['speed_ms'],0,60);number(c['direction_deg'],0,360);hours.append(c['hour'])
    if len(set(hours))!=len(hours):raise HazardError('INVALID_INPUT','Duplicate wind revision hour')
    if body.get('weather_source') not in ['FORECAST','HISTORICAL']:raise HazardError('INVALID_INPUT','Explicit weather source required')
    return body

def dataset(root):return Path(root)/'runs/physical-days-20261016T040414Z/expanded'

def validate_plan(plan,req,weather):
    expected={'case','ignition_wgs84','weather_source','records','resources','action_times','weather_changes','qualification','moisture_percent'}
    if not isinstance(plan,dict) or not expected<=set(plan) or set(plan)-expected-{'ignitions_wgs84','comparison_times','forcing'} or plan['case'] not in ['A','B']:raise HazardError('INVALID_INPUT','Strict native fire plan required')
    input_body=dict(hours=req['options']['duration_s']//3600,seed=req['options']['seed'],moisture_percent=plan['moisture_percent'],resources=plan['resources'],weather_changes=plan['weather_changes'],weather_source=plan['weather_source'],comparison_times=plan.get('comparison_times',[]))
    input_body.update(ignitions=plan['ignitions_wgs84']) if 'ignitions_wgs84' in plan else input_body.update(ignition=plan['ignition_wgs84'])
    validate(input_body)
    if 'ignitions_wgs84' in plan and plan['ignition_wgs84']!=plan['ignitions_wgs84'][0]['point']:raise HazardError('INVALID_INPUT','Primary ignition mismatch')
    if plan.get('comparison_times') and not (set(plan['action_times'])|{int(i['at_minutes']*60) for i in plan.get('ignitions_wgs84',[])})<=set(plan['comparison_times']):raise HazardError('INVALID_TIME','Comparison clock misses events')
    if plan['moisture_percent']!=req['options']['moisture_percent'] or plan['qualification']!='UNQUALIFIED_RESEARCH' or plan['case']=='A' and (plan['resources'] or plan['weather_changes']):raise HazardError('INVALID_INPUT','Unqualified matching baseline required')
    if 'forcing' in plan:
        f=plan['forcing'];field=weather.get('distributed_field')
        if set(f)!={'version','terrain_id','field_id','moisture_model','initial_ffmc','field_sha256','landcover_crosswalk'} or f['version']!='distributed/1' or f['moisture_model'] not in ['HFFMC_1977','MANUAL'] or not field or field['id']!=f['field_id'] or f['initial_ffmc']!=85:raise HazardError('SOURCE_MISMATCH','Distributed forcing contract mismatch')
    count=req['options']['duration_s']//3600
    if req['options']['duration_s']%3600 or len(plan['records'])!=count:raise HazardError('INVALID_TIME','Whole-hour complete native fire schedule required')
    times=plan['action_times']
    if not isinstance(times,list) or len(times)>8 or any(type(t) is not int or not 0<=t<req['options']['duration_s'] for t in times) or times!=sorted(set(times)):raise HazardError('INVALID_TIME','Invalid action event clock')
    if plan['case']=='B' and times!=sorted(set(int(r['at_minutes']*60) for r in plan['resources'])):raise HazardError('INVALID_TIME','Action times differ from resource plan')
    source={r['at']:r['values'] for r in weather['records']};changes={r['hour']:r for r in plan['weather_changes']}
    for h,r in enumerate(plan['records']):
        at=(timestamp(req['valid_from'])+dt.timedelta(hours=h)).isoformat().replace('+00:00','Z')
        if set(r)!={'time','at','values'} or r['at']!=at or type(r['time']) is not int or r['time']!=h*3600 or at not in source:raise HazardError('INVALID_TIME','Native wind schedule gap/mismatch')
        values=copy.deepcopy(source[at])
        if h in changes:values.update(wind_speed_10m=changes[h]['speed_ms'],wind_direction_10m=changes[h]['direction_deg'])
        if r['values']!=values:raise HazardError('SOURCE_MISMATCH','Consumed weather differs from frozen source or declared hypothetical revision')
    return plan

def stage(root,body,forecast=None):
    validate(body);root=Path(root);source=dataset(root)
    if not (source/'expanded-arrays.npz').exists():raise HazardError('SOURCE_MISSING','Prepare the demo terrain using bootstrap days; no invented terrain fallback')
    weather=copy.deepcopy(forecast) if body['weather_source']=='FORECAST' else load(source/'weather-4days.json')
    start=body.get('start_at') if body['weather_source']=='FORECAST' else '2024-07-13T13:00:00Z';begin=timestamp(start)
    if begin.minute or begin.second or begin.microsecond:raise HazardError('INVALID_TIME','Whole-hour start required')
    if body['weather_source']=='FORECAST' and (forecast is None or begin<timestamp(utcnow())):raise HazardError('STALE_FORECAST','Future fresh forecast required')
    by_time={r['at']:r['values'] for r in weather['records']};records=[]
    for h in range(body['hours']):
        at=(begin+dt.timedelta(hours=h)).isoformat().replace('+00:00','Z')
        if at not in by_time:raise HazardError('SOURCE_MISSING','Complete hourly weather required; shorten horizon or select another start')
        records.append(dict(time=h*3600,at=at,values=copy.deepcopy(by_time[at])))
    dest=root/'runs'/('firelab-'+uuid.uuid4().hex);dest.mkdir();write_new(dest/'body.json',body);write_new(dest/'weather.json',weather)
    cfg=load(root/'runtime-v2.json');env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]),PROJ_LIB='/usr/share/proj')
    command=[cfg['geo_python'],'-m','hazardia.firelab','prepare',str(root),str(dest)]
    with (dest/'prepare.log').open('xb') as log:
        try:subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30)
        except (OSError,subprocess.SubprocessError) as e:
            detail=(dest/'prepare.log').read_text()[-3000:]
            if 'Research line length' in detail:raise HazardError('INVALID_INPUT','Action line must be1..2000m: draw a shorter line or zoom in') from e
            if 'Invalid intervention geometry' in detail or 'Research intervention area' in detail:raise HazardError('INVALID_INPUT','Draw a valid non-self-intersecting area, up to4km2') from e
            if 'Position outside prepared terrain' in detail:raise HazardError('OUTSIDE_COVERAGE','Position outside prepared terrain interior: select inside the study boundary') from e
            raise HazardError('PREPARATION_FAILED','Fire terrain preparation rejected; inspect immutable prepare.log') from e
    template=load(dest/'template.json');plans={}
    for case in ['A','B']:
        plan=dict(case=case,ignition_wgs84=body.get('ignition',body.get('ignitions',[{}])[0].get('point')),weather_source=body['weather_source'],records=copy.deepcopy(records),resources=body.get('resources',[]) if case=='B' else [],action_times=sorted(set(int(r['at_minutes']*60) for r in body.get('resources',[]))),weather_changes=body.get('weather_changes',[]) if case=='B' else [],qualification='UNQUALIFIED_RESEARCH',moisture_percent=body['moisture_percent'])
        if 'ignitions' in body:plan['ignitions_wgs84']=copy.deepcopy(body['ignitions'])
        if 'comparison_times' in body:plan['comparison_times']=body['comparison_times']
        for change in plan['weather_changes']:
            v=plan['records'][change['hour']]['values'];v['wind_speed_10m']=change['speed_ms'];v['wind_direction_10m']=change['direction_deg']
        write_new(dest/('plan-'+case+'.json'),plan);req=copy.deepcopy(template);req.update(id=dest.name+'-'+case,valid_from=start,valid_until=(begin+dt.timedelta(hours=body['hours'])).isoformat().replace('+00:00','Z'),snapshot_at=utcnow(),mode='RESEARCH_FORECAST' if body['weather_source']=='FORECAST' else 'RESEARCH_RETROSPECTIVE',schema_version='0.4.0')
        req['assets']=[dict(role=role,path=name,sha256=sha256(dest/name)) for role,name in [('dem','dem.tif'),('fire_arrays','arrays.npz'),('weather','weather.json'),('fire_plan','plan-'+case+'.json')]]
        req['assumptions']=['Native paired fire experiment '+case,'Real cached terrain; uniform legacy vegetation fuel5; manually authored fuel moisture (not atmospheric RH)','Hourly point wind consumed by native model; weather table also includes T/RH/rain/pressure/radiation, not yet a qualified fuel-moisture estimator','Native upstream line actions: idealized parameter effects, not calibrated personnel/aircraft efficacy or dispatch feasibility','Identical seed, realizations, quarter-hour output stepping and action-event schedule in matched A/B; wind remains hourly; B weather edits are hypothetical','Domain exit fails the job, never a clipped successful forecast']
        req['options'].update(seed=body['seed'],duration_s=body['hours']*3600,moisture_percent=body['moisture_percent']);write_new(dest/('request-'+case+'.json'),req);plans[case]=req
    return dest,plans

def prepare(root,dest):
    import numpy as np,rasterio,pyproj
    from rasterio.transform import Affine
    from rasterio.warp import transform_bounds
    source=dataset(root);g=load(source/'grid.json');tr=Affine(*g['transform']);body=load(dest/'body.json');project=pyproj.Transformer.from_crs('EPSG:4326',g['crs'],always_xy=True)
    def cell(point):
        x,y=project.transform(point[1],point[0]);c,r=(~tr)*(x,y)
        if not 2<=r<g['shape'][0]-2 or not 2<=c<g['shape'][1]-2:raise HazardError('OUTSIDE_COVERAGE','Position outside prepared terrain interior')
        return [int(r),int(c)]
    ignition=cell(body['ignition']) if 'ignition' in body else cell(body['ignitions'][0]['point'])
    for i in body.get('ignitions',[]):cell(i['point'])
    from shapely.geometry import Polygon,LineString
    for r in body.get('resources',[]):
        points=r.get('line',r.get('area'))
        for point in points:cell(point)
        projected=[project.transform(p[1],p[0]) for p in points]
        geom=LineString(projected) if 'line' in r else Polygon(projected)
        if not geom.is_valid or geom.is_empty:raise HazardError('INVALID_INPUT','Invalid intervention geometry')
        if 'line' in r and not 1<=geom.length<=2000:raise HazardError('INVALID_INPUT','Research line length must be1..2000m')
        if 'area' in r and not 1<=geom.area<=4000000:raise HazardError('INVALID_INPUT','Research intervention area must be1..4000000m2')
    with np.load(source/'expanded-arrays.npz',allow_pickle=False) as a:
        dem=a['dem'];veg=a['veg'];np.savez_compressed(dest/'arrays.npz',dem=dem,veg=veg,wind_speed_kmh=np.zeros_like(dem),wind_dir_deg=np.zeros_like(dem))
    with rasterio.open(dest/'dem.tif','w',driver='GTiff',height=dem.shape[0],width=dem.shape[1],count=1,dtype=dem.dtype,crs=g['crs'],transform=tr,nodata=-9999,compress='deflate') as dst:dst.write(dem,1)
    bounds=rasterio.transform.array_bounds(*dem.shape,tr);bbox=transform_bounds(g['crs'],'EPSG:4326',*bounds)
    old=load(Path(root)/'runs/m1-abruzzo-20261015T161041Z/fire-request.json');old['grid'].update(shape=list(dem.shape),transform=list(tr)[:6],crs=g['crs']);old['territory']['bbox_wgs84']=list(bbox);old['options'].update(ignition=ignition,realizations=2);old.update(timeout_s=900,max_log_bytes=1048576);write_new(dest/'template.json',old)

if __name__=='__main__':
    import sys
    prepare(Path(sys.argv[2]),Path(sys.argv[3]))
