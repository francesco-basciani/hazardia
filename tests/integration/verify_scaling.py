"""Declared synthetic boundary scaling; not calibrated multi-event performance."""
import argparse,copy,time,resource,statistics
from pathlib import Path
from hazardia.io import load,write_new,sha256
from hazardia.domain.state import GeoIndex,identity
from hazardia.decision.research_fixture import problem
from hazardia.decision.supervisor import bounded_decide
from hazardia.decision.verifier import verify

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--run',required=True);a=ap.parse_args();root=Path(a.runtime);out=Path(a.run);out.mkdir(exist_ok=False);results=[];profile=load('profiles/research/abruzzo.json')
    for n in [100,1000,10000,100000]:
        def rows():
            for i in range(n):
                yield dict(schema_version='0.4.0',kind='exposure',id='synthetic-%07d'%i,available_at='2024-07-13T13:00:00Z',provenance=dict(source='HAZARDIA scaling generator, not population',license='AUTHORED_RESEARCH_FIXTURE',qualification='SYNTHETIC_RESEARCH'),payload=dict(territory_id=profile['id'],point_wgs84=[13.37+(i%100)*.0001,42.34+((i//100)%100)*.0001],category='POPULATION',people=1,vulnerability=None,valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-13T14:00:00Z'))
        index=GeoIndex(out/('geo-%d.sqlite'%n));start=time.monotonic();index.build(rows());build=time.monotonic()-start;times=[]
        for _ in range(30):
            start=time.monotonic();window=index.window([13.37,42.34,13.38,42.35],'2024-07-13T13:00:00Z',1000);times.append(time.monotonic()-start);assert len(window)<=1000
        row=dict(test='geo-index-'+str(n),status='PASS',records=n,build_s=build,query_n=30,query_p95_s=sorted(times)[28],query_times_s=times,returned=len(window),db_bytes=Path(index.path).stat().st_size,result_sha256=identity(window),process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='VM index/window only; not browser rendering/physical simulation');write_new(out/(row['test']+'.json'),row);results.append(row)
    cat=load(root/'web-assets/catalog.json');refs={h:next(s['reference'] for s in cat['scenarios'] if s['hazard']==h) for h in ['FIRE','FLOOD']}
    for count,scenario_count in [(4,2),(20,5),(100,10)]:
        p=problem(refs,'JOINT',count);p['settings'].update(horizon_slots=12,slot_s=30,budget_s=60);p['scenarios']=[dict(id='w'+str(i),weight=1/scenario_count,qualification='SYNTHETIC_RESEARCH') for i in range(scenario_count)]
        for e in p['events']:e['exposure']={s['id']:30*(1+.5*(i%2)) for i,s in enumerate(p['scenarios'])}
        for o in p['options']:
            o['end_slot']=12;o['benefit']={s['id']:o['benefit']['nominal' if i%2==0 else 'stress'] for i,s in enumerate(p['scenarios'])}
        start=time.monotonic();r=bounded_decide(p,out/('decision-'+str(count)),str(root/'decision-env/bin/python'));elapsed=time.monotonic()-start;assert elapsed<=60;assert r['status']=='VALIDATED_FOR_SIMULATION';assert verify(p,r['selected'])['status']=='VALIDATED_FOR_SIMULATION';row=dict(test='decision-'+str(count),status='PASS',resources=count,events=2,scenarios=scenario_count,slots=12,options=len(p['options']),elapsed_s=elapsed,response=r,qualification='One timing per size; no p95 estimate; authored repeated coefficients, not calibrated event population');results.append(row)
    # Explicit boundary, not silently described as supported L workload.
    p['settings']['horizon_slots']=24;r=bounded_decide(p,out/'unsupported-24slots',str(root/'decision-env/bin/python'));assert r['status']=='INVALID_INPUT';results.append(dict(test='24-slot-boundary',status='PASS',observed=r['status'],limitation='Current decision contract supports<=12slots; candidate M/L workloads with24/48slots not supported'))
    write_new(out/'results.json',dict(status='PASS',results=results,limitations='100k geo index is not100k displayed map features. Original full M/L physical/UI workloads remain NOT RUN. No second-machine/full-geography claim.'));print('PASS',len(results),'scaling cases')
if __name__=='__main__':main()
