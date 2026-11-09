"""Pinned synthetic scale/timing checks; never an ignition-skill evaluation."""
import argparse
import json
import math
import time
from pathlib import Path

from hazardia.io import write_new,utcnow


def summary(values):
    import numpy as np
    return dict(n=len(values),p50_s=float(np.quantile(values,.5)),p95_s=float(np.quantile(values,.95)),max_s=max(values))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=False);root=Path(a.runtime)
    from wii.inventory import Inventory,time_key
    from tests.wii.fixtures import source,event,product
    from wii.scenarios import sample
    from tests.wii.test_api_decisions import DecisionAdmission
    from wii.decisions import decide
    import numpy as np
    write_new(out/'protocol.json',dict(scope='SYNTHETIC_PERFORMANCE_ONLY',inventory_events=100000,grid_cells=100000,
                                      repetitions=30,seed=1729,at=utcnow()))
    inv=Inventory(out/'inventory');s=source();doc=inv.document(s,external_id='synthetic-benchmark',text='SYNTHETIC PERFORMANCE FIXTURE',available_at='2024-07-15T00:00:00Z')
    rng=np.random.default_rng(1729);rows=[];index=[]
    for i in range(100000):
        e=event(doc,ident='synthetic-'+str(i));lon=float(rng.uniform(13,14));lat=float(rng.uniform(42,43));e['location']['geometry']['coordinates']=[lon,lat]
        rows.append((i+1,e['id'],1,time_key(e['available_at']),time_key(e['start']),time_key(e['end']),s['id'],doc['id'],json.dumps(e)))
        index.append((i+1,lon,lon,lat,lat))
    with inv.connect() as db:
        db.executemany('INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)',rows);db.executemany('INSERT INTO spatial VALUES(?,?,?,?,?)',index)
    del rows,index
    query=[]
    for _ in range(30):
        start=time.perf_counter();r=inv.query([13.2,42.2,13.3,42.3],'2024-07-13T00:00:00Z','2024-07-14T00:00:00Z',limit=100)
        assert len(r['events'])==100;query.append(time.perf_counter()-start)
    p=product(.1);p['cells']=[]
    for i in range(100000):
        x=4000000+(i%400)*1000;y=2000000+(i//400)*1000;mu=.1/100000
        p['cells'].append(dict(id=str(i),x=x,y=y,area_km2=1,mu=mu,p=-math.expm1(-mu),features=[]))
    p['provenance']['mask_geometry']['coordinates'][0]=[[4000000,2000000],[4400000,2000000],[4400000,2250000],[4000000,2250000],[4000000,2000000]]
    sampling=[]
    for i in range(31):
        start=time.perf_counter();value=sample(p,count=10,seed=i,exploratory=True);elapsed=time.perf_counter()-start
        if i==0:cold=elapsed
        else:sampling.append(elapsed)
        assert abs(sum(m['weight'] for m in value['members'])-1)<1e-9
    decision=[];statuses=[]
    for i in range(30):
        problem=DecisionAdmission().problem();problem['id']='wii-timing-'+str(i)
        start=time.perf_counter();value=decide(problem,out/('decision-'+str(i)),str(root/'decision-env/bin/python'))
        decision.append(time.perf_counter()-start);statuses.append(value['status'])
        assert value['status']=='VALIDATED_FOR_SIMULATION' and not value['operationally_approvable']
    record=dict(scope='SYNTHETIC_PINNED_WORKLOAD_ONLY',inventory_query=summary(query),sampling_warm=summary(sampling),
        sampling_cold_s=cold,decisions=summary(decision),decision_statuses=statuses,
        gates=dict(query_500ms=summary(query)['p95_s']<=.5,sampling_2s=summary(sampling)['p95_s']<=2,
                   decision_each_60s=max(decision)<=60),scientific_validation=False)
    write_new(out/'benchmark.json',record);print(json.dumps(record,indent=2))


if __name__=='__main__':main()
