"""Independent direct invariant checks, no solver imports or solver row reuse."""
import datetime as dt
from hazardia.io import timestamp,HazardError
from hazardia.decision.problem import validate

def verify(problem,selection):
    try:validate(problem)
    except (HazardError,KeyError,TypeError,ValueError) as e:return dict(status='INVALID',rules=[dict(id='INPUT',detail=str(e))],operationally_approvable=False)
    rules=[];byid={o['id']:o for o in problem['options']};resources={r['id']:r for r in problem['resources']};events={e['id']:e for e in problem['events']};s=problem['settings'];start=timestamp(problem['planning_at'])
    def fail(code,detail):rules.append(dict(id=code,detail=detail))
    if not isinstance(selection,list) or not all(isinstance(x,str) for x in selection) or len(set(selection))!=len(selection):return dict(status='INVALID',rules=[dict(id='DUPLICATE',detail='Selection must contain unique IDs')],operationally_approvable=False)
    chosen=[]
    for oid in selection:
        if oid not in byid:fail('UNKNOWN_OPTION',str(oid));continue
        o=byid[oid];chosen.append(o);r=resources[o['resource_id']];p=r['record']['payload'];e=events[o['event_id']]
        required=['skills','equipment','capabilities','schedule','rest_hours','maintenance','autonomy_h','consumables','cost_per_hour','reliability','mass_kg']
        if any(p[k] is None or p[k]=='UNKNOWN' for k in required):fail('UNKNOWN_SAFETY',oid);continue
        if p['maintenance']!='READY' or e['hazard'] not in p['capabilities'] or 'EVACUATION' not in p['skills'] or 'VEHICLE' not in p['equipment']:fail('QUALIFICATION',oid)
        a=start+dt.timedelta(seconds=o['start_slot']*s['slot_s']);b=start+dt.timedelta(seconds=o['end_slot']*s['slot_s'])
        if not any(timestamp(w['start'])<=a and b<=timestamp(w['end']) for w in p['schedule']):fail('SHIFT',oid)
        if timestamp(r['record']['available_at'])>timestamp(problem['data_cutoff']):fail('RESOURCE_CUTOFF',oid)
        if o['arrival_s']>(o['end_slot']-o['start_slot'])*s['slot_s'] or (b-a).total_seconds()>p['autonomy_h']*3600 or p['rest_hours']<1:fail('TRAVEL_AUTONOMY_REST',oid)
        if o['road_open'] is not True or o['road_limit_kg'] is None or o['road_limit_kg']<p['mass_kg']:fail('ROAD',oid)
        if o['authorization'] is not True:fail('AUTHORIZATION',oid)
        if o['effect']!='IMPACT_ONLY' or o['evidence']!='SYNTHETIC_RESEARCH':fail('EFFECT',oid)
        if b>timestamp(e['product']['valid_until']):fail('PRODUCT_HORIZON',oid)
    for rid,r in resources.items():
        own=[o for o in chosen if o['resource_id']==rid];p=r['record']['payload']
        for i,o in enumerate(own):
            if any(o['start_slot']<v['end_slot'] and v['start_slot']<o['end_slot'] for v in own[i+1:]):fail('OVERBOOKING',rid)
        if own and p['consumables'] is not None:
            if sum(o['fuel_l'] for o in own)>p['consumables']['fuel_l']+1e-9 or sum(o['water_l'] for o in own)>p['consumables']['water_l']+1e-9:fail('CONSUMABLES',rid)
    for region in problem['regions']:
        # Reserve protects the number of home resources not transferred away.
        home=[r['id'] for r in problem['resources'] if r['home_region']==region['id']]
        for slot in range(s['horizon_slots']):
            transferred={o['resource_id'] for o in chosen if o['resource_id'] in home and events[o['event_id']]['region']!=region['id'] and o['start_slot']<=slot<o['end_slot']}
            if len(home)-len(transferred)<region['minimum_donor_reserve']:fail('DONOR_RESERVE',region['id'])
    for e in problem['events']:
        for w,total in e['exposure'].items():
            if sum(o['benefit'][w] for o in chosen if o['event_id']==e['id'])>total+1e-7:fail('DOUBLE_COUNT_EXPOSURE',e['id'])
    for c in problem['commitments']:
        if c['option_id'] not in selection:fail('CONTINUITY',c['option_id'])
    return dict(status='INVALID' if rules else 'VALIDATED_FOR_SIMULATION',rules=rules,operationally_approvable=False,scope='Synthetic research constraints only; rest>=1h is a declared fixture threshold, not operational policy')

def losses(problem,selection):
    chosen=[o for o in problem['options'] if o['id'] in selection];cost=sum(o['cost'] for o in chosen)
    values={w['id']:sum(e['exposure'][w['id']]-sum(o['benefit'][w['id']] for o in chosen if o['event_id']==e['id']) for e in problem['events']) for w in problem['scenarios']}
    weights=[w['weight'] for w in problem['scenarios']]
    # Missing probabilities never turn into silently invented expected weights.
    expected=None if any(v is None for v in weights) else sum(w['weight']*values[w['id']] for w in problem['scenarios'])
    worst=max(values.values());lam=problem['settings']['lambda'];objective=worst if expected is None else lam*expected+(1-lam)*worst
    return dict(by_scenario=values,expected=expected,worst=worst,cost=cost,objective=objective+problem['settings']['cost_weight']*cost,unit='synthetic remaining exposed people; configured research cost preference')
