"""Versioned concrete M1 boundaries. No domain solver or simulator imports."""
import math
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from jsonschema import Draft7Validator
from hazardia.io import HazardError, load, timestamp, verify_asset

VERSION='0.2.0'
SCHEMAS=Path(__file__).with_name('schemas')

def validate(kind, value):
    schema=load(SCHEMAS/(kind+'.schema.json'))
    errors=sorted(Draft7Validator(schema).iter_errors(value),key=lambda e:str(list(e.path)))
    if errors:
        raise HazardError('INVALID_CONTRACT',str(list(errors[0].path))+': '+errors[0].message)
    return value

def validate_request(value, root=None):
    validate('simulation_request',value)
    try:
        ZoneInfo(value['territory']['timezone'])
    except (ZoneInfoNotFoundError,ValueError) as exc:
        raise HazardError('INVALID_PROFILE','Unknown time zone') from exc
    b=value['territory']['bbox_wgs84']
    if not (-180<=b[0]<b[2]<=180 and -90<=b[1]<b[3]<=90):
        raise HazardError('INVALID_PROFILE','Invalid CRS84 bbox')
    if timestamp(value['valid_from'])>=timestamp(value['valid_until']):
        raise HazardError('INVALID_TIME','Empty scenario interval')
    timestamp(value['snapshot_at'])
    duration=(timestamp(value['valid_until'])-timestamp(value['valid_from'])).total_seconds()
    expected=value['options']['duration_s'] if value['hazard']=='FIRE' else value['options']['hours']*3600
    if duration!=expected:
        raise HazardError('INVALID_TIME','Declared model duration differs from product validity interval')
    if value['hazard']=='FLOOD' and len(value['options']['rain_mm'])!=value['options']['hours']+1:
        raise HazardError('INVALID_INPUT','Flood forcing requires hours+1samples')
    if value['grid']['crs']!=value['territory']['work_crs'] and value['hazard']=='FIRE':
        raise HazardError('GRID_MISMATCH','Fire grid differs from configured work CRS')
    roles=[v['role'] for v in value['assets']]
    if len(set(roles))!=len(roles) or not {'dem','weather'}.issubset(roles):
        raise HazardError('INVALID_INPUT','Unique dem/weather assets required')
    if value['hazard']=='FIRE' and 'fire_arrays' not in roles:
        raise HazardError('INVALID_INPUT','Fire arrays required')
    grid=value['grid'];tr=grid['transform']
    if tr[0]<=0 or tr[4]>=0 or tr[1]!=0 or tr[3]!=0:
        raise HazardError('GRID_MISMATCH','North-up regular grid required')
    if any(not math.isfinite(v) for v in tr):
        raise HazardError('GRID_MISMATCH','Nonfinite transform')
    if root is not None:
        for asset in value['assets']:
            verify_asset(root,asset)
        weather=load(verify_asset(root,next(v for v in value['assets'] if v['role']=='weather')))
        validate_weather(weather,value)
    return value

def validate_weather(weather, request):
    required={'schema_version','kind','data_kind','issued_at','available_at','valid_from','valid_until','units','records','source','license'}
    if not isinstance(weather,dict) or not required.issubset(weather) or weather['schema_version'] not in [VERSION,'0.3.0'] or weather['kind']!='weather':
        raise HazardError('INVALID_CONTRACT','Versioned weather record required')
    expected={'precipitation':'mm','wind_speed_10m':'m/s','wind_direction_10m':'°','temperature_2m':'°C','relative_humidity_2m':'%','surface_pressure':'hPa','shortwave_radiation':'W/m²'}
    if any(weather['units'].get(k)!=v for k,v in expected.items()):
        raise HazardError('SOURCE_UNIT','Unsupported weather units')
    available=timestamp(weather['available_at'])
    if available>timestamp(request['snapshot_at']):
        raise HazardError('FUTURE_SOURCE','Weather unavailable at acceptance snapshot')
    if not (timestamp(weather['valid_from'])<=timestamp(request['valid_from']) and timestamp(request['valid_until'])<=timestamp(weather['valid_until'])):
        raise HazardError('STALE_FORECAST','Scenario outside weather validity')
    if weather['data_kind']=='FORECAST':
        unknown=weather['issued_at'] is None
        if unknown:
            if not (weather['schema_version']=='0.3.0' and request['schema_version']=='0.3.0' and request['mode']=='RESEARCH_FORECAST' and weather.get('issued_at_status')=='UNKNOWN_PROVIDER' and weather['source'].get('provider')=='Open-Meteo'):
                raise HazardError('INVALID_TIME','Forecast issue time missing without explicit research unknown-issue semantics')
        elif timestamp(weather['issued_at'])>available:raise HazardError('INVALID_TIME','Forecast issue must precede availability')
        if request['mode']=='RESEARCH_FORECAST' and timestamp(request['valid_from'])<available:raise HazardError('FUTURE_SOURCE','Forecast simulation must start after first observed availability')
    elif weather['data_kind']=='REANALYSIS':
        if weather['issued_at'] is not None or request['mode']!='RESEARCH_RETROSPECTIVE':
            raise HazardError('SOURCE_KIND','Reanalysis is not an issued predictive forecast')
    else:
        raise HazardError('SOURCE_KIND','Unsupported weather source class')
    times=[]
    for record in weather['records']:
        times.append(timestamp(record['at']))
        values=record['values']
        if any(k not in values or not isinstance(values[k],(int,float)) or isinstance(values[k],bool) or not math.isfinite(values[k]) for k in expected):
            raise HazardError('SOURCE_MISSING','Missing/nonfinite weather value')
        if values['precipitation']<0 or values['wind_speed_10m']<0 or not 0<=values['wind_direction_10m']<=360 or not 0<=values['relative_humidity_2m']<=100:
            raise HazardError('SOURCE_RANGE','Weather value outside declared physical range')
    if not times or len(set(times))!=len(times) or times!=sorted(times):
        raise HazardError('SOURCE_TIME','Missing/duplicate/disordered weather timestamps')
    if any((b-a).total_seconds()!=3600 for a,b in zip(times,times[1:])) or times[0]>timestamp(request['valid_from']) or times[-1]+__import__('datetime').timedelta(hours=1)<timestamp(request['valid_until']):
        raise HazardError('SOURCE_TIME','Hourly weather gap or uncovered simulation interval')
    return weather

def migrate_observation_010(old):
    """Explicit metadata-only migration of a frozen M0 observation; no asset qualification."""
    if old.get('schema_version')!='0.1.0' or old.get('kind')!='observation':
        raise HazardError('UNSUPPORTED_MIGRATION','Only M0 observation0.1.0 supported')
    p=old['payload'];prov=old['provenance']
    new=dict(schema_version=VERSION,kind='observation',id=old['id'],territory_id=p['territory_id'],
             sensed_at=p['sensed_at'],available_at=p['available_at'],ingested_at=p['ingested_at'],
             bbox_wgs84=p['footprint_bbox'],crs=p['crs'],native_resolution_m=p['resolution_m'],
             coverage_fraction=p['coverage_fraction'],quality=p['quality'],asset=p['asset'],
             license=prov['license'],source=prov['source'],migration=dict(from_version='0.1.0',metadata_only=True))
    validate_observation(new)
    return new


def validate_product(product,request,root=None):
    validate('hazard_product',product)
    if product['request_id']!=request['id'] or product['hazard']!=request['hazard'] or product['grid']!=request['grid'] or (product['valid_from'],product['valid_until'])!=(request['valid_from'],request['valid_until']):
        raise HazardError('PRODUCT_MISMATCH','Product differs from accepted request')
    if sorted(product['input_hashes'],key=lambda v:v['role'])!=sorted([dict(role=v['role'],sha256=v['sha256']) for v in request['assets']],key=lambda v:v['role']):
        raise HazardError('PRODUCT_MISMATCH','Product input provenance differs')
    expected={'FIRE_PROBABILITY':'1','ARRIVAL_TIME':'s'} if request['hazard']=='FIRE' else {'MAXIMUM_DEPTH':'m'}
    if len(product['layers'])!=len(expected) or {v['name']:v['unit'] for v in product['layers']}!=expected:
        raise HazardError('PRODUCT_UNIT','Unsupported/mismatched product field or units')
    for layer in product['layers']:
        s=layer['statistics']
        if s['minimum']<0 or s['maximum']<s['minimum'] or s['positive_cells']>s['valid_cells'] or s['valid_cells']>math.prod(request['grid']['shape']):
            raise HazardError('INVALID_OUTPUT','Invalid spatial statistics')
        if layer['name']=='FIRE_PROBABILITY' and s['maximum']>1:
            raise HazardError('INVALID_OUTPUT','Probability exceeds1')
        if layer['name']=='ARRIVAL_TIME' and s['maximum']>request['options']['duration_s']+1e-4:
            raise HazardError('INVALID_TIME','Arrival exceeds horizon')
        if root is not None:verify_asset(root,layer)
    return product


def validate_observation(value):
    validate('observation',value)
    if not timestamp(value['sensed_at'])<=timestamp(value['available_at'])<=timestamp(value['ingested_at']):
        raise HazardError('SOURCE_TIME','Observation sensing/availability/ingestion inconsistent')
    if value['coverage_fraction']<1 and value['quality']=='VALID':
        raise HazardError('SOURCE_COVERAGE','Partial observation incorrectly labeled valid')
    return value


def migrate_run_manifest_020(old,request,original_sha256):
    """Explicit legacy draft migration; retain unknown environment and original identity."""
    if old.get('schema_version')!='0.2.0' or old.get('kind')!='run_manifest':
        raise HazardError('UNSUPPORTED_MIGRATION','Only draft M1manifest0.2.0 supported')
    new=__import__('copy').deepcopy(old)
    if new.get('request_id',request['id'])!=request['id']:
        raise HazardError('PRODUCT_MISMATCH','Manifest/request identity differs')
    new.update(schema_version='0.3.0',request_id=request['id'],seed=request['options'].get('seed'),environment=dict(status='UNKNOWN_LEGACY_ENVIRONMENT',migration_from='0.2.0',original_manifest_sha256=original_sha256))
    new.setdefault('metrics',None);new.setdefault('detail','Legacy metadata migration; no experiment rerun')
    validate('run_manifest',new)
    return new
