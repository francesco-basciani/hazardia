"""Controlled rolling-horizon progress model; effects are synthetic linear progress."""
import copy,datetime as dt,uuid
from hazardia.io import timestamp,HazardError
from hazardia.decision.problem import validate
from hazardia.decision.verifier import verify

def advance(previous,response,elapsed_slots=1,*,exposure_update=None):
    validate(previous)
    if response['status']!='VALIDATED_FOR_SIMULATION' or verify(previous,response['selected'])['status']!='VALIDATED_FOR_SIMULATION':raise HazardError('CONTINUITY_UNKNOWN','Cannot continue an unverified plan')
    if type(elapsed_slots) is not int or elapsed_slots<=0:raise HazardError('INVALID_INPUT','Positive whole-slot progress required')
    p=copy.deepcopy(previous);p['id']='rolling-'+uuid.uuid4().hex;p['planning_at']=(timestamp(p['planning_at'])+dt.timedelta(seconds=elapsed_slots*p['settings']['slot_s'])).isoformat().replace('+00:00','Z');p['commitments']=[];chosen=set(response['selected']);old=p['options'];options=[];delivered={e['id']:{w['id']:0 for w in p['scenarios']} for e in p['events']};spent={r['id']:{'fuel_l':0,'water_l':0} for r in p['resources']}
    for o in old:
        if o['id'] in chosen:
            fraction=max(0,min(1,(elapsed_slots-o['start_slot'])/(o['end_slot']-o['start_slot'])))
            for w,value in o['benefit'].items():delivered[o['event_id']][w]+=value*fraction
            for k in ['fuel_l','water_l']:spent[o['resource_id']][k]+=o[k]*fraction
            if o['end_slot']<=elapsed_slots:continue
            o['start_slot']=max(0,o['start_slot']-elapsed_slots);o['end_slot']-=elapsed_slots;o['arrival_s']=0
            o['benefit']={w:v*(1-fraction) for w,v in o['benefit'].items()}
            for k in ['fuel_l','water_l','cost']:o[k]*=1-fraction
            options.append(o);p['commitments'].append(dict(option_id=o['id']))
        else:
            o['id']+='-deferred';o['start_slot']=1;o['end_slot']=min(2,p['settings']['horizon_slots'])
            if o['end_slot']>o['start_slot']:
                o['benefit']={w:v*.5 for w,v in o['benefit'].items()};options.append(o)
    for e in p['events']:
        e['exposure']={w:max(0,v-delivered[e['id']][w]) for w,v in e['exposure'].items()}
        if exposure_update and e['id'] in exposure_update:
            # Update describes the remaining exposed pool, not an extra repeat of past progress.
            e['exposure']=copy.deepcopy(exposure_update[e['id']])
    for r in p['resources']:
        for k in ['fuel_l','water_l']:
            if r['record']['payload']['consumables'] is not None:r['record']['payload']['consumables'][k]-=spent[r['id']][k]
    p['options']=options;validate(p)
    return p,dict(effect_model='synthetic-linear-mission-progress-v1',delivered=delivered,spent=spent,operational_authority=False)
