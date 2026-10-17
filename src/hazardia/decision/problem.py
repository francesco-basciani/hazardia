"""Explicit 0.5.0 discrete allocation boundary, independent of simulator internals."""
import json,math
from hazardia.io import HazardError,timestamp
from hazardia.domain.contracts import validate_record,require

def validate(p):
    try:json.dumps(p,allow_nan=False)
    except (TypeError,ValueError) as e:raise HazardError('INVALID_INPUT',str(e)) from e
    ideal=isinstance(p,dict) and p.get('schema_version')=='0.6.0'
    fields={'schema_version','kind','id','planning_at','data_cutoff','mode','resources','events','scenarios','options','regions','commitments','settings'}
    if ideal:fields.add('policy')
    require(isinstance(p,dict) and set(p)==fields and p['schema_version'] in ['0.5.0','0.6.0'] and p['kind']=='decision_problem','INVALID_INPUT','Strict decision_problem0.5.0 required')
    if ideal:require(p['policy']==dict(domain='FIRE_IDEAL_ASSIGNMENT',loss_unit='weighted_priority_points',benefit_model='EXCLUSIVE_AREA_COVERAGE_PROXY'),'INVALID_INPUT','Explicit ideal priority policy required')
    require(p['mode']==('RESEARCH_IDEAL' if ideal else 'RESEARCH_RETROSPECTIVE'),'INVALID_INPUT','Only retrospective research decisions enabled')
    timestamp(p['planning_at']);timestamp(p['data_cutoff']);s=p['settings']
    require(set(s)=={'budget_s','lambda','cost_weight','horizon_slots','slot_s','seed','solver'},'INVALID_INPUT','Strict settings required')
    require(0<s['budget_s']<=60 and 0<=s['lambda']<=1 and s['cost_weight']>=0 and isinstance(s['horizon_slots'],int) and 1<=s['horizon_slots']<=12 and s['slot_s']>0,'INVALID_INPUT','Invalid limits/preferences')
    require(0<len(p['events'])<=100 and 0<len(p['scenarios'])<=50 and len(p['resources'])<=200 and len(p['options'])<=10000,'INVALID_INPUT','Bounded problem dimensions')
    for records in [p['events'],p['scenarios'],p['resources'],p['options'],p['regions']]:require(len({r['id'] for r in records})==len(records),'INVALID_INPUT','Duplicate IDs')
    weather={w['id'] for w in p['scenarios']};weights=[w['weight'] for w in p['scenarios']]
    require(all(w is None for w in weights) or all(w is not None and isinstance(w,(int,float)) and 0<=w<=1 for w in weights) and abs(sum(weights)-1)<1e-9,'INVALID_INPUT','Scenario weights unknown or normalized')
    for w in p['scenarios']:require(set(w)=={'id','weight','qualification'} and w['qualification']=='SYNTHETIC_RESEARCH','INVALID_INPUT','Stress scenarios explicitly synthetic')
    for r in p['resources']:
        require(set(r)==({'id','home_region','record','category'} if ideal else {'id','home_region','record'}),'INVALID_INPUT','Resource wrapper fields');validate_record(r['record']);require(r['record']['kind']=='resource' and r['id']==r['record']['id'],'INVALID_INPUT','Resource identity')
        if ideal:require(r['category'] in ['waterline_action','canadair','helicopter','heavy_action'],'INVALID_INPUT','Unknown ideal resource category')
        require(r['home_region'] in {x['id'] for x in p['regions']},'INVALID_INPUT','Unknown home region')
    for region in p['regions']:require(set(region)=={'id','minimum_donor_reserve'} and isinstance(region['minimum_donor_reserve'],int) and region['minimum_donor_reserve']>=0,'INVALID_INPUT','Region reserve required')
    for e in p['events']:
        require(set(e)=={'id','hazard','region','product','exposure'},'INVALID_INPUT','Event fields')
        require(e['hazard'] in ['FIRE','FLOOD'] and e['region'] in {x['id'] for x in p['regions']} and set(e['exposure'])==weather and all(isinstance(v,(int,float)) and not isinstance(v,bool) and v>=0 for v in e['exposure'].values()),'INVALID_INPUT','Event/exposure units: people')
        product=e['product'];require(set(product)=={'job_id','hazard','sha256','valid_from','valid_until','weather_hash','qualification'},'INVALID_INPUT','Product reference')
        require(product['hazard']==e['hazard'] and len(product['sha256'])==64 and product['qualification']=='UNQUALIFIED_RESEARCH','INVALID_INPUT','Product identity/qualification')
        require(timestamp(product['valid_from'])<=timestamp(p['planning_at'])<timestamp(product['valid_until']),'STALE_PRODUCT','Product outside planning time')
    for o in p['options']:
        require(set(o)=={'id','resource_id','event_id','start_slot','end_slot','arrival_s','benefit','cost','fuel_l','water_l','road_open','road_limit_kg','authorization','effect','evidence'},'INVALID_INPUT','Option fields')
        require(o['resource_id'] in {r['id'] for r in p['resources']} and o['event_id'] in {e['id'] for e in p['events']} and isinstance(o['start_slot'],int) and isinstance(o['end_slot'],int) and 0<=o['start_slot']<o['end_slot']<=s['horizon_slots'],'INVALID_INPUT','Option references/interval')
        require(set(o['benefit'])==weather and all(isinstance(v,(int,float)) and not isinstance(v,bool) and v>=0 for v in o['benefit'].values()) and all(isinstance(o[k],(int,float)) and not isinstance(o[k],bool) and o[k]>=0 for k in ['cost','fuel_l','water_l','arrival_s']),'INVALID_INPUT','Nonnegative synthetic coefficients')
    for c in p['commitments']:require(set(c)=={'option_id'} and c['option_id'] in {o['id'] for o in p['options']},'CONTINUITY_UNKNOWN','Committed option missing')
    return p
