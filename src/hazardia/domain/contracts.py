"""M2 strict contracts. M0/M1 versions stay frozen and separately validated."""
import json,math
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from hazardia.io import HazardError,timestamp
from hazardia.contracts import validate

def require(condition,code,message):
    if not condition:raise HazardError(code,message)

def bounds(b):
    require(-180<=b[0]<b[2]<=180 and -90<=b[1]<b[3]<=90,'INVALID_GEOMETRY','Invalid CRS84 bbox')

def within(point,b):return b[0]<=point[0]<=b[2] and b[1]<=point[1]<=b[3]

def validate_record(record):
    # jsonschema alone considers some nonfinite Python floats numbers.
    try:json.dumps(record,allow_nan=False)
    except (ValueError,TypeError) as exc:raise HazardError('INVALID_JSON',str(exc)) from exc
    validate('domain_record',record);available=timestamp(record['available_at']);p=record['payload'];kind=record['kind']
    if 'bbox_wgs84' in p:bounds(p['bbox_wgs84'])
    if 'point_wgs84' in p:
        lon,lat=p['point_wgs84'];require(-180<=lon<=180 and -90<=lat<=90,'INVALID_GEOMETRY','Point outside WGS84')
    if 'valid_from' in p:require(timestamp(p['valid_from'])<timestamp(p['valid_until']),'INVALID_TIME','Empty validity window')
    if kind=='territory':
        try:ZoneInfo(p['timezone'])
        except (ZoneInfoNotFoundError,ValueError) as exc:raise HazardError('INVALID_PROFILE','Unknown timezone') from exc
        require(p['work_crs'].startswith('EPSG:') and p['work_crs'][5:].isdigit(),'INVALID_PROFILE','Declared EPSG work CRS required')
        code=int(p['work_crs'][5:])
        require(32601<=code<=32660 or 32701<=code<=32760,'UNSUPPORTED_CRS','M2 metric profile supports WGS84 UTM zones only; no silent unit assumption')
        require(bool(p['jurisdictions']) and len(set(p['jurisdictions']))==len(p['jurisdictions']),'INVALID_PROFILE','Unique jurisdictions required')
        require(p['calibration']!='DOCUMENTED' or bool(p['calibration_refs']),'UNKNOWN_CALIBRATION','Documented calibration needs evidence')
    elif kind=='detection':require(timestamp(p['sensed_at'])<=available,'INVALID_TIME','Detection available before sensing')
    elif kind=='weather_ensemble':
        if p['data_kind']=='FORECAST':require(p['issued_at'] is not None and timestamp(p['issued_at'])<=available,'INVALID_TIME','Forecast needs issue <= availability')
        else:require(p['issued_at'] is None,'SOURCE_KIND','Reanalysis has no reconstructed issue')
        members=p['members'];require(bool(members) and len({m['id'] for m in members})==len(members),'INVALID_ENSEMBLE','Nonempty unique members required')
        weights=[m['weight'] for m in members]
        require(all(w is None for w in weights) or all(w is not None for w in weights) and abs(sum(weights)-1)<1e-9,'INVALID_ENSEMBLE','Weights all unknown or sum to one')
        reference=None
        for member in members:
            times=[timestamp(r['at']) for r in member['records']]
            require(bool(times) and times==sorted(set(times)),'SOURCE_TIME','Ordered unique member times required')
            require(all((b-a).total_seconds()==p['step_s'] for a,b in zip(times,times[1:])),'SOURCE_TIME','Weather gap')
            require(times[0]==timestamp(p['valid_from']) and (timestamp(p['valid_until'])-times[-1]).total_seconds()==p['step_s'],'SOURCE_TIME','Exact member coverage required')
            require(reference is None or times==reference,'SOURCE_TIME','Member windows differ');reference=times
            for row in member['records']:
                v=row['values'];require(v['precipitation']>=0 and v['wind_speed_10m']>=0 and 0<=v['wind_direction_10m']<=360 and 0<=v['relative_humidity_2m']<=100,'SOURCE_RANGE','Invalid weather range')
    elif kind=='resource' and p['schedule'] is not None:
        for interval in p['schedule']:require(timestamp(interval['start'])<timestamp(interval['end']),'INVALID_TIME','Empty resource interval')
    return record

def select_weather(record,as_of,start,end,*,forecast_required=True):
    validate_record(record);require(record['kind']=='weather_ensemble','INVALID_CONTRACT','Weather ensemble required');p=record['payload']
    require(timestamp(record['available_at'])<=timestamp(as_of),'FUTURE_SOURCE','Weather unavailable at cutoff')
    require(timestamp(start)<timestamp(end) and timestamp(p['valid_from'])<=timestamp(start) and timestamp(end)<=timestamp(p['valid_until']),'STALE_FORECAST','Requested interval outside ensemble')
    require(not forecast_required or p['data_kind']=='FORECAST','SOURCE_KIND','Reanalysis cannot become forecast')
    return record
