"""Prepare bounded research jobs from an immutable real forecast in the same VM."""
import datetime as dt,os,shutil,subprocess,uuid
from pathlib import Path
from hazardia.io import load,write_new,sha256,utcnow,timestamp,HazardError,verify_asset

def stage(runtime,forecast,body,cache_root):
    runtime=Path(runtime);old=runtime/'runs/m1-abruzzo-20261015T161041Z';hazard=body.get('hazard')
    if hazard not in ['FIRE','FLOOD']:raise HazardError('INVALID_INPUT','Select FIRE/FLOOD')
    start=body.get('start_at','');begin=timestamp(start)
    if begin.minute or begin.second or begin.microsecond or begin<timestamp(utcnow()):raise HazardError('INVALID_TIME','Select a future whole UTC hour')
    hours=1 if hazard=='FIRE' else 6
    samples={r['at']:r['values'] for r in forecast['records']}
    required=[(begin+dt.timedelta(hours=i)).isoformat().replace('+00:00','Z') for i in range(hours+1)]
    if any(t not in samples for t in required):raise HazardError('SOURCE_MISSING','Forecast does not cover the complete simulation window')
    minutes=body.get('minutes',30);seed=body.get('seed',1729);row=body.get('row',32);col=body.get('col',32)
    if not all(type(v) is int for v in [minutes,seed,row,col]) or minutes not in [10,30,60] or not 0<=seed<2**31 or not 0<=row<64 or not 0<=col<64:raise HazardError('INVALID_INPUT','Invalid forecast simulation controls')
    req=load(old/(hazard.lower()+'-request.json'));req.update(schema_version='0.3.0',mode='RESEARCH_FORECAST',id='forecast-'+uuid.uuid4().hex,valid_from=start,snapshot_at=utcnow())
    req['valid_until']=(begin+dt.timedelta(minutes=minutes) if hazard=='FIRE' else begin+dt.timedelta(hours=6)).isoformat().replace('+00:00','Z')
    dest=runtime/'runs'/req['id'];dest.mkdir();write_new(dest/'weather.json',forecast)
    assets=[dict(role='weather',path='weather.json',sha256=sha256(dest/'weather.json'))]
    for asset in req['assets']:
        if asset['role'] in ['weather','fire_arrays']:continue
        src=verify_asset(old,asset);name=asset['role']+src.suffix;shutil.copyfile(src,dest/name);assets.append(dict(role=asset['role'],path=name,sha256=sha256(dest/name)))
    raw=Path(cache_root)/('raw-'+forecast['source']['sha256']+'.json')
    if sha256(raw)!=forecast['source']['sha256']:raise HazardError('CACHE_CORRUPT','Raw forecast bytes changed')
    shutil.copyfile(raw,dest/'weather-raw.json');assets.append(dict(role='weather_raw',path='weather-raw.json',sha256=sha256(dest/'weather-raw.json')))
    req['assumptions']=[v for v in req['assumptions'] if not any(term in v.lower() for term in ['era5','retrospect','rain','wind'])]+['Real Open-Meteo DWD ICON-EU point forecast '+forecast['id']+'; first observed availability '+forecast['available_at']+'; model initialization UNKNOWN','Point forcing uniform over the small existing research AOI; not a calibrated/distributed catchment forecast','Terrain and optical background are dated; ignition/fuel/moisture/soil/Q0 and model initial states remain hypothetical','Open-Meteo precipitation/shortwave end-hour statistics shifted to following simulation-hour interval; no invented missing values']
    if hazard=='FIRE':
        req['options'].update(seed=seed,duration_s=minutes*60,ignition=[row,col]);value=samples[start];cfg=load(runtime/'runtime-v2.json');original=verify_asset(old,next(a for a in req['assets'] if a['role']=='fire_arrays'))
        command=[cfg['geo_python'],str(Path(__file__).resolve().parents[3]/'scripts/prepare_forecast_arrays.py'),'--source',str(original),'--output',str(dest/'fire-arrays.npz'),'--speed-kmh',str(value['wind_speed_10m']*3.6),'--direction',str(value['wind_direction_10m'])]
        env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]))
        try:
            with (dest/'preparation.log').open('xb') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env,check=True,timeout=20)
        except (subprocess.SubprocessError,OSError) as e:raise HazardError('PREPARATION_FAILED','Forecast input preparation failed; see immutable preparation.log') from e
        assets.append(dict(role='fire_arrays',path='fire-arrays.npz',sha256=sha256(dest/'fire-arrays.npz')))
        req['assumptions'].append('Native fire uses forecast wind at start held constant for <=1h; fuel moisture remains declared synthetic percent, not inferred from air relative humidity')
    else:
        req['options'].update(hours=6,rain_mm=[samples[t]['precipitation'] for t in required])
        req['assumptions'].append('Native HMC cold-start uncalibrated scenario; actual forecast rainfall used unchanged, dry/no-excess outcomes may produce classified non-success')
    req['assets']=assets;write_new(dest/'request.json',req);return req,dest
