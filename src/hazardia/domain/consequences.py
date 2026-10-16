"""Consequence/constraint input semantics only; no dispatch or optimization."""
import math,datetime as dt
from hazardia.io import timestamp
from hazardia.domain.contracts import validate_record,require

def constraint_inputs(resource,at):
    validate_record(resource);require(resource['kind']=='resource','INVALID_CONTRACT','Resource required');p=resource['payload']
    require(timestamp(resource['available_at'])<=timestamp(at),'FUTURE_SOURCE','Resource unavailable at cutoff')
    for key in ['skills','equipment','capabilities','schedule','rest_hours','maintenance','autonomy_h','consumables','cost_per_hour','reliability','mass_kg']:
        require(p[key] is not None and p[key]!='UNKNOWN','UNKNOWN_SAFETY','Unknown resource '+key)
    require(p['maintenance']=='READY','UNAVAILABLE_RESOURCE','Resource in maintenance')
    require(any(timestamp(s['start'])<=timestamp(at)<timestamp(s['end']) for s in p['schedule']),'UNAVAILABLE_RESOURCE','Outside schedule')
    return p

def check_route(roads,resource,at):
    p=constraint_inputs(resource,at);require(bool(roads),'UNKNOWN_ACCESS','No route evidence');duration=0
    for i,road in enumerate(roads):
        validate_record(road);r=road['payload'];require(road['kind']=='road' and r['territory_id']==p['territory_id'],'TERRITORY_MISMATCH','Wrong route territory')
        require(timestamp(road['available_at'])<=timestamp(at) and timestamp(r['valid_from'])<=timestamp(at)<timestamp(r['valid_until']),'STALE_ACCESS','Road validity/availability mismatch')
        require(r['status']=='OPEN' and r['load_limit_kg'] is not None,'UNKNOWN_ACCESS','Closed or unknown access')
        require(p['mass_kg']<=r['load_limit_kg'],'UNSAFE_ACCESS','Resource exceeds load limit')
        require(not i or roads[i-1]['payload']['to_node']==r['from_node'],'INVALID_ROUTE','Disconnected route')
        duration+=r['length_m']/(r['speed_kmh']/3.6)
        require(timestamp(at)+dt.timedelta(seconds=duration)<=timestamp(r['valid_until']),'STALE_ACCESS','Road evidence expires before traversal finishes')
    arrival=timestamp(at)+dt.timedelta(seconds=duration)
    require(duration<=p['autonomy_h']*3600,'UNSAFE_ACCESS','Route exceeds known autonomy')
    require(any(timestamp(s['start'])<=timestamp(at) and arrival<=timestamp(s['end']) for s in p['schedule']),'UNAVAILABLE_RESOURCE','Route exceeds shift')
    return dict(status='RESEARCH_INPUTS_VALID',travel_s=duration,authority='NOT_AUTHORIZED',safety='Not a complete deployment safety check')

def impact_only(intervention,baseline):
    validate_record(intervention);p=intervention['payload'];require(intervention['kind']=='intervention','INVALID_CONTRACT','Intervention required')
    require(isinstance(baseline,dict) and {'territory_id','hazard','hazard_sha256','exposed_people','as_of'}.issubset(baseline),'UNKNOWN_EXPOSURE','Baseline provenance required')
    require(isinstance(baseline['exposed_people'],(int,float)) and not isinstance(baseline['exposed_people'],bool) and math.isfinite(baseline['exposed_people']) and baseline['exposed_people']>=0,'UNKNOWN_EXPOSURE','Finite nonnegative baseline required')
    require(isinstance(baseline['hazard_sha256'],str) and len(baseline['hazard_sha256'])==64 and all(c in '0123456789abcdef' for c in baseline['hazard_sha256']),'UNKNOWN_EXPOSURE','Hazard hash required')
    require(timestamp(intervention['available_at'])<=timestamp(baseline['as_of']),'FUTURE_SOURCE','Effect unavailable at cutoff')
    require(p['effect']=='IMPACT_ONLY','UNSUPPORTED_EFFECT','No qualified physical-effect implementation in M2')
    require(p['action']=='EVACUATION' and p['model_id']=='synthetic-evacuation-count-v1' and p['evidence']=='SYNTHETIC_RESEARCH' and intervention['provenance']['qualification']=='SYNTHETIC_RESEARCH','UNKNOWN_EFFECT','Explicit research effect model required')
    require(p['territory_id']==baseline['territory_id'] and p['hazard']==baseline['hazard'],'TERRITORY_MISMATCH','Effect/hazard territory mismatch')
    count=p['parameters']['evacuated_people'];require(count is not None and count<=baseline['exposed_people'],'UNKNOWN_EFFECT','Evacuation count unknown or exceeds exposure')
    return dict(baseline,remaining_exposed_people=baseline['exposed_people']-count,evacuated_people=count,effect_model=p['model_id'],qualification='SYNTHETIC_RESEARCH',physical_hazard_changed=False)
