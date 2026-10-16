"""Authored research-only resources/effects. No actual emergency inventory implied."""
import copy,uuid,datetime as dt
from hazardia.io import utcnow,timestamp,HazardError

def problem(products,hazard='FIRE',resource_count=3,*,robust=.5,road_open=True,transfer=True,disabled=None):
    kinds=list(products) if hazard=='JOINT' else [hazard]
    start=max(timestamp(products[h]['valid_from']) for h in kinds);end=min(timestamp(products[h]['valid_until']) for h in kinds)
    if (end-start).total_seconds()<600:raise HazardError('MISMATCHED_WINDOWS','Joint comparison needs matching >=600s genuine product windows')
    at=start.isoformat().replace('+00:00','Z');finish=(start+dt.timedelta(hours=8)).isoformat().replace('+00:00','Z')
    events=[dict(id=h.lower()+'-event',hazard=h,region='ABR-NORTH' if h=='FIRE' else 'ABR-SOUTH',product=copy.deepcopy(products[h]),exposure={'nominal':30,'stress':45}) for h in kinds]
    scenarios=[dict(id='nominal',weight=.6,qualification='SYNTHETIC_RESEARCH'),dict(id='stress',weight=.4,qualification='SYNTHETIC_RESEARCH')]
    regions=[dict(id=x,minimum_donor_reserve=0) for x in ['ABR-NORTH','ABR-SOUTH']];resources=[];options=[]
    for n in range(resource_count):
        rid='unit-'+str(n+1);home='ABR-NORTH' if n%2==0 else 'ABR-SOUTH'
        payload=dict(territory_id='abruzzo-laquila-research',home_authority=home,point_wgs84=[13.38+n*.001,42.35],skills=['EVACUATION'],equipment=['VEHICLE'],capabilities=['FIRE','FLOOD'],schedule=[dict(start=at,end=finish)],rest_hours=12,maintenance='UNAVAILABLE' if rid==disabled else 'READY',autonomy_h=4,consumables=dict(fuel_l=60,water_l=0),cost_per_hour=10,reliability=.9,mass_kg=2000)
        rec=dict(schema_version='0.4.0',kind='resource',id=rid,available_at=at,provenance=dict(source='HAZARDIA authored research fixture, not actual regional inventory',license='AUTHORED_RESEARCH_FIXTURE',qualification='SYNTHETIC_RESEARCH'),payload=payload)
        resources.append(dict(id=rid,home_region=home,record=rec))
        for e in events:
            options.append(dict(id=rid+'-'+e['id'],resource_id=rid,event_id=e['id'],start_slot=0,end_slot=1,arrival_s=120,benefit=dict(nominal=6+n%3,stress=4+n%3),cost=1+n*.1,fuel_l=2,water_l=0,road_open=road_open,road_limit_kg=3000,authorization=(transfer or e['region']==home),effect='IMPACT_ONLY',evidence='SYNTHETIC_RESEARCH'))
    if hazard=='JOINT':
        matrix=[{'FIRE':(15,1),'FLOOD':(7,7)},{'FIRE':(6,6),'FLOOD':(6,6)},{'FIRE':(1,1),'FLOOD':(14,10)},{'FIRE':(8,7),'FLOOD':(3,2)}]
        for region in regions:region['minimum_donor_reserve']=1
        for option in options:
            index=next(i for i,r in enumerate(resources) if r['id']==option['resource_id']);kind=next(e['hazard'] for e in events if e['id']==option['event_id']);nominal,stress=matrix[index%4][kind];option['benefit']={'nominal':nominal,'stress':stress}
    return dict(schema_version='0.5.0',kind='decision_problem',id='decision-'+uuid.uuid4().hex,planning_at=at,data_cutoff=utcnow(),mode='RESEARCH_RETROSPECTIVE',resources=resources,events=events,scenarios=scenarios,options=options,regions=regions,commitments=[],settings=dict(budget_s=8,**{'lambda':robust},cost_weight=.01,horizon_slots=1,slot_s=600,seed=1729,solver='highs'))
