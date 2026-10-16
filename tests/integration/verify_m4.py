import argparse,copy
from pathlib import Path
from hazardia.io import load,write_new
from hazardia.decision.research_fixture import problem
from hazardia.decision.controller import decide
from hazardia.decision.verifier import verify,losses

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--run',required=True);a=ap.parse_args();root=Path(a.runtime);run=Path(a.run);cat=load(root/'web-assets/catalog.json');refs={h:next(s['reference'] for s in cat['scenarios'] if s['hazard']==h) for h in ['FIRE','FLOOD']};p=problem(refs,'JOINT',4);py=str(root/'decision-env/bin/python');records=[]
    r=decide(p,run/'joint-highs',py);assert r['status']=='VALIDATED_FOR_SIMULATION';selected=r['selected'];assert len(selected)==4 and len({next(o['resource_id'] for o in p['options'] if o['id']==i) for i in selected})==4
    p2=copy.deepcopy(p);p2['settings']['solver']='enumeration';q=decide(p2,run/'joint-reference',py);assert q['status']=='VALIDATED_FOR_SIMULATION' and abs(q['loss']['objective']-r['loss']['objective'])<1e-6
    local=copy.deepcopy(p)
    for o in local['options']:
        res=next(x for x in local['resources'] if x['id']==o['resource_id']);event=next(x for x in local['events'] if x['id']==o['event_id']);o['authorization']=res['home_region']==event['region']
    baseline=decide(local,run/'home-only-baseline',py);assert baseline['status']=='VALIDATED_FOR_SIMULATION'
    invalid=[o['id'] for o in p['options']];v=verify(p,invalid);assert v['status']=='INVALID' and 'OVERBOOKING' in {x['id'] for x in v['rules']}
    for tag,key,value in [('unauthorized','authorization',False),('unknown-road','road_open',None)]:
        modified=copy.deepcopy(p)
        for o in modified['options']:o[key]=value
        out=decide(modified,run/tag,py);assert out['status']=='VALIDATED_FOR_SIMULATION' and out['selected']==[]
    donor=copy.deepcopy(p);donor['regions'][0]['minimum_donor_reserve']=2
    d=decide(donor,run/'donor-floor',py);assert d['status']=='VALIDATED_FOR_SIMULATION'
    for oid in d['selected']:
        o=next(o for o in donor['options'] if o['id']==oid);rs=next(x for x in donor['resources'] if x['id']==o['resource_id']);es=next(x for x in donor['events'] if x['id']==o['event_id']);assert rs['home_region']!='ABR-NORTH' or es['region']=='ABR-NORTH'
    result=dict(status='PASS',joint=r,home_only=baseline,reference_objective=q['loss']['objective'],joint_objective_improvement=baseline['loss']['objective']-r['loss']['objective'],independent_naive_rejected=v,scope='Two synthetic authority regions/resources/effects on genuine CIMA product context, not field performance; no presumption of superiority outside authored coefficients')
    write_new(run/'results.json',result);print({k:result[k] for k in ['status','reference_objective','joint_objective_improvement']})
if __name__=='__main__':main()
