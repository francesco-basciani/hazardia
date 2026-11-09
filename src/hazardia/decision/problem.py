"""Explicit 0.5.0 discrete allocation boundary, independent of simulator internals."""
import json,math
from hazardia.io import HazardError,timestamp
from hazardia.domain.contracts import validate_record,require
from hazardia.decision.policies import validate_header

def validate(p):
    try:json.dumps(p,allow_nan=False)
    except (TypeError,ValueError) as e:raise HazardError('INVALID_INPUT',str(e)) from e
    policy=validate_header(p)
    timestamp(p['planning_at']);timestamp(p['data_cutoff']);s=p['settings']
    require(set(s)=={'budget_s','lambda','cost_weight','horizon_slots','slot_s','seed','solver'},'INVALID_INPUT','Strict settings required')
    require(0<s['budget_s']<=60 and 0<=s['lambda']<=1 and s['cost_weight']>=0 and isinstance(s['horizon_slots'],int) and 1<=s['horizon_slots']<=12 and s['slot_s']>0,'INVALID_INPUT','Invalid limits/preferences')
    require(0<len(p['events'])<=100 and 0<len(p['scenarios'])<=50 and len(p['resources'])<=200 and len(p['options'])<=10000,'INVALID_INPUT','Bounded problem dimensions')
    for records in [p['events'],p['scenarios'],p['resources'],p['options'],p['regions']]:require(len({r['id'] for r in records})==len(records),'INVALID_INPUT','Duplicate IDs')
    weather={w['id'] for w in p['scenarios']};weights=[w['weight'] for w in p['scenarios']]
    require(all(w is None for w in weights) or all(w is not None and isinstance(w,(int,float)) and 0<=w<=1 for w in weights) and abs(sum(weights)-1)<1e-9,'INVALID_INPUT','Scenario weights unknown or normalized')
    if p['schema_version']=='0.7.0':
        ensemble=p['ensemble']
        require(isinstance(ensemble,dict) and set(ensemble)=={'schema','scenario_set_id','scenario_set_sha256',
                'measure','complete_empirical_ensemble','unresolved_weight','calibration','weight_semantics','operational_authority','target_definition'},
                'INVALID_INPUT','Strict traceable ensemble required')
        require(ensemble['schema']=='hazardia.wii.decision-ensemble/0.1.0' and
                isinstance(ensemble['scenario_set_id'],str) and ensemble['scenario_set_id'] and
                isinstance(ensemble['scenario_set_sha256'],str) and len(ensemble['scenario_set_sha256'])==64 and
                all(c in '0123456789abcdef' for c in ensemble['scenario_set_sha256']) and
                ensemble['measure']=='JOINT_CONDITIONAL_INDEPENDENT_POISSON' and
                ensemble['complete_empirical_ensemble'] is True and ensemble['unresolved_weight']==0 and
                ensemble['calibration'] in ('EXPERIMENTAL_UNCALIBRATED','CALIBRATED_WITHIN_SCOPE') and
                ensemble['target_definition'] in ('P_AT_LEAST_ONE_WILDFIRE_IGNITION_PER_CELL_INTERVAL',
                    'P_REGISTERED_ORIGIN_PROXY_PER_CELL_INTERVAL','SYNTHETIC_PROCESS_FIXTURE') and
                (ensemble['calibration']!='CALIBRATED_WITHIN_SCOPE' or ensemble['target_definition']=='P_AT_LEAST_ONE_WILDFIRE_IGNITION_PER_CELL_INTERVAL') and
                ensemble['weight_semantics'] in ('MONTE_CARLO_OR_STRATUM_ESTIMATOR_WEIGHTS','SELF_NORMALIZED_IMPORTANCE_FINITE_SAMPLE_BIASED') and
                ensemble['operational_authority'] is False and all(w is not None for w in weights),
                'INVALID_INPUT','Incomplete/unknown/untraceable ensemble is not admissible')
        for w in p['scenarios']:
            require(set(w)=={'id','weight','qualification','member_sha256','state'} and
                    w['qualification']=='PROBABILISTIC_RESEARCH' and
                    type(w['weight']) in (int,float) and math.isfinite(w['weight']) and
                    w['state'] in ('READY','NO_IGNITION') and len(w['member_sha256'])==64,
                    'INVALID_INPUT','Probabilistic research member identity required')
        no_event={w['id'] for w in p['scenarios'] if w['state']=='NO_IGNITION'}
        require(all(all(e['exposure'].get(w)==0 for w in no_event) for e in p['events']) and
                all(all(o['benefit'].get(w)==0 for w in no_event) for o in p['options']),
                'INVALID_INPUT','No-ignition states must have zero fire consequence/benefit')
    else:
        for w in p['scenarios']:require(set(w)=={'id','weight','qualification'} and w['qualification']=='SYNTHETIC_RESEARCH','INVALID_INPUT','Stress scenarios explicitly synthetic')
    for r in p['resources']:
        require(set(r)==policy.resource_fields,'INVALID_INPUT','Resource wrapper fields');validate_record(r['record']);require(r['record']['kind']=='resource' and r['id']==r['record']['id'],'INVALID_INPUT','Resource identity')
        if policy.resource_categories:require(r['category'] in policy.resource_categories,'INVALID_INPUT','Unknown ideal resource category')
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
