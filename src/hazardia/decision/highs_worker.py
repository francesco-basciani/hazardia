"""HiGHS MIP worker in isolated decision-env; independently checked by controller."""
import datetime as dt,json,sys,time
import highspy
from hazardia.io import load,write_new,timestamp
from hazardia.decision.policies import policy_for

def solve(p,out):
    h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1);h.setOptionValue('random_seed',p['settings']['seed']);h.setOptionValue('time_limit',max(.01,p['settings']['budget_s']-1))
    policy=policy_for(p)
    s=p['settings'];rs={r['id']:r for r in p['resources']};es={e['id']:e for e in p['events']};variables={};options=p['options'];start=timestamp(p['planning_at'])
    for o in options:
        r=rs[o['resource_id']]['record'];v=r['payload'];e=es[o['event_id']];good=True
        keys=['skills','equipment','capabilities','schedule','rest_hours','maintenance','autonomy_h','consumables','cost_per_hour','reliability','mass_kg']
        if any(v[k] is None or v[k]=='UNKNOWN' for k in keys):good=False
        if good:
            a=start+dt.timedelta(seconds=o['start_slot']*s['slot_s']);b=start+dt.timedelta(seconds=o['end_slot']*s['slot_s'])
            good=(v['maintenance']=='READY' and e['hazard'] in v['capabilities'] and policy.required_skill in v['skills'] and policy.equipment_for(rs[o['resource_id']]) in v['equipment'] and any(timestamp(i['start'])<=a and timestamp(i['end'])>=b for i in v['schedule']) and timestamp(r['available_at'])<=timestamp(p['data_cutoff']) and v['rest_hours']>=1 and v['autonomy_h']*3600>=(b-a).total_seconds() and o['arrival_s']<=(b-a).total_seconds() and o['road_open'] is True and o['road_limit_kg'] is not None and o['road_limit_kg']>=v['mass_kg'] and o['authorization'] is True and o['effect']==policy.effect and o['evidence']=='SYNTHETIC_RESEARCH' and b<=timestamp(e['product']['valid_until']))
        variables[o['id']]=h.addVariable(lb=0,ub=1 if good else 0,type=highspy.HighsVarType.kInteger,name=o['id'])
    def total(group,coefficient=lambda o:1):return h.qsum(coefficient(o)*variables[o['id']] for o in group)
    for rid,r in rs.items():
        own=[o for o in options if o['resource_id']==rid]
        for slot in range(s['horizon_slots']):h.addConstr(total([o for o in own if o['start_slot']<=slot<o['end_slot']])<=1)
        if r['record']['payload']['consumables'] is not None:
            for key in ['fuel_l','water_l']:h.addConstr(total(own,lambda o:o[key])<=r['record']['payload']['consumables'][key])
    for region in p['regions']:
        home=[r['id'] for r in p['resources'] if r['home_region']==region['id']]
        for slot in range(s['horizon_slots']):h.addConstr(total([o for o in options if o['resource_id'] in home and es[o['event_id']]['region']!=region['id'] and o['start_slot']<=slot<o['end_slot']])<=len(home)-region['minimum_donor_reserve'])
    for e in p['events']:
        if policy.exclusive_targets:h.addConstr(total([o for o in options if o['event_id']==e['id']])<=1)
        for wid,exposed in e['exposure'].items():h.addConstr(total([o for o in options if o['event_id']==e['id']],lambda o:o['benefit'][wid])<=exposed)
    for c in p['commitments']:h.addConstr(variables[c['option_id']]==1)
    z=h.addVariable(lb=0,name='worst_loss')
    expressions={}
    for w in p['scenarios']:
        wid=w['id'];loss=sum(e['exposure'][wid] for e in p['events'])-total(options,lambda o:o['benefit'][wid]);expressions[wid]=loss;h.addConstr(z>=loss)
    lam=s['lambda'] if all(w['weight'] is not None for w in p['scenarios']) else 0
    mean=h.qsum(w['weight']*expressions[w['id']] for w in p['scenarios']) if lam else 0
    h.minimize(lam*mean+(1-lam)*z+s['cost_weight']*total(options,lambda o:o['cost']))
    state=h.getModelStatus();sol=h.getSolution();selected=[o['id'] for o in options if sol.value_valid and h.val(variables[o['id']])>.5]
    write_new(out,dict(solver='highs-1.12.0',termination=h.modelStatusToString(state),selected=selected,has_incumbent=bool(sol.value_valid),optimal=state==highspy.HighsModelStatus.kOptimal,infeasible=state==highspy.HighsModelStatus.kInfeasible))
if __name__=='__main__':solve(load(sys.argv[1]),sys.argv[2])
