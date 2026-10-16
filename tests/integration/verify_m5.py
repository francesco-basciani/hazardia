import argparse,copy,time,statistics,datetime as dt
from pathlib import Path
from hazardia.io import load,write_new,HazardError
from hazardia.decision.research_fixture import problem
from hazardia.decision.supervisor import bounded_decide
from hazardia.decision.rolling import advance
from hazardia.decision.verifier import verify,losses
from hazardia.adaptation.alerts import AlertBook
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"domain"))
from fixtures import ensemble

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--run',required=True);a=ap.parse_args();root=Path(a.runtime);run=Path(a.run);cat=load(root/'web-assets/catalog.json');refs={h:next(s['reference'] for s in cat['scenarios'] if s['hazard']==h) for h in ['FIRE','FLOOD']};py=str(root/'decision-env/bin/python');p=problem(refs,'JOINT',4);p['settings']['budget_s']=60
    timings=[];statuses=[]
    for i in range(30):
        trial=copy.deepcopy(p);trial['id']='fixed-timing-'+str(i);trial['settings']['seed']=1729+i;t=time.monotonic();r=bounded_decide(trial,run/('timing-%02d'%i),py);elapsed=time.monotonic()-t;timings.append(elapsed);statuses.append(r['status']);assert elapsed<=60 and r['elapsed_s']<=60 and r['status']=='VALIDATED_FOR_SIMULATION';assert verify(trial,r['selected'])['status']=='VALIDATED_FOR_SIMULATION'
    sorted_times=sorted(timings);write_new(run/'deadline-benchmark.json',dict(n=30,latencies_s=timings,statuses=statuses,p50_s=statistics.median(timings),p95_s=sorted_times[28],worst_s=max(timings),deadline_s=60,useful_strategy_rate=statuses.count('VALIDATED_FOR_SIMULATION')/30,terminal_deadline_rate=sum(t<=60 for t in timings)/30,note='Fixed small synthetic workload on genuine product contexts; repetitions are timing trials, not independent physics/quality samples'))
    long=copy.deepcopy(p);long['settings'].update(horizon_slots=2,slot_s=600)
    for o in long['options']:o['end_slot']=2
    first=bounded_decide(long,run/'rolling-first',py);assert first['status']=='VALIDATED_FOR_SIMULATION'
    new,history=advance(long,first,1);replanned=bounded_decide(new,run/'rolling-next',py);assert replanned['status']=='VALIDATED_FOR_SIMULATION';assert {c['option_id'] for c in new['commitments']}.issubset(replanned['selected']);assert all(v>=0 for pool in history['delivered'].values() for v in pool.values());write_new(run/'rolling-progress.json',dict(status='PASS',previous=first['id'],next=replanned['id'],commitments=new['commitments'],progress=history))
    book=AlertBook();forecast=ensemble();forecast['available_at']='2024-07-13T12:00:00Z';forecast['payload']['issued_at']=forecast['available_at'];forecast['id']='controlled-forecast-12'
    opened=book.update(forecast,event_id='flood-event',at='2024-07-13T12:00:00Z',predicted_exposure=45,threshold=35,effect_known=True,qualification='SYNTHETIC_RESEARCH');assert opened['state']=='OPEN' and opened['lead_s']==3600
    book.acknowledge(opened['id'],'2024-07-13T12:05:00Z');forecast['id']='controlled-forecast-1215';forecast['available_at']='2024-07-13T12:15:00Z';forecast['payload']['issued_at']=forecast['available_at'];updated=book.update(forecast,event_id='flood-event',at=forecast['available_at'],predicted_exposure=50,threshold=35,effect_known=True,qualification='SYNTHETIC_RESEARCH');assert updated['state']=='UPDATED'
    forecast['id']='controlled-forecast-1230';forecast['available_at']='2024-07-13T12:30:00Z';forecast['payload']['issued_at']=forecast['available_at'];resolved=book.update(forecast,event_id='flood-event',at=forecast['available_at'],predicted_exposure=20,threshold=35,effect_known=True,qualification='SYNTHETIC_RESEARCH');assert resolved['state']=='RESOLVED'
    for tag,at,effect in [('stale','2024-07-13T15:00:00Z',True),('unknown-effect','2024-07-13T12:30:00Z',False)]:
        try:book.update(forecast,event_id=tag,at=at,predicted_exposure=45,threshold=35,effect_known=effect,qualification='SYNTHETIC_RESEARCH')
        except HazardError:pass
        else:raise AssertionError('Invalid forecast/effect accepted')
    # Explicit authored truth: one true warning, one false alarm, no measured real skill.
    write_new(run/'alert-replay.json',dict(status='PASS',history=book.history,controlled_cases=[dict(predicted=45,observed_synthetic=40,threshold=35,classification='TRUE_WARNING'),dict(predicted=45,observed_synthetic=20,threshold=35,classification='FALSE_ALARM')],false_alarm_fraction=.5,scope='Two authored cases only; not observed forecast performance'))
    # Expected-only versus robust under identical inputs and scenario set.
    expected=copy.deepcopy(p);expected['settings']['lambda']=1;reactive=bounded_decide(expected,run/'expected-only',py);robust=copy.deepcopy(p);robust['settings']['lambda']=0;risk=bounded_decide(robust,run/'worst-only',py);assert reactive['status']==risk['status']=='VALIDATED_FOR_SIMULATION';assert reactive['loss']['expected']<=risk['loss']['expected']+1e-7;assert risk['loss']['worst']<=reactive['loss']['worst']+1e-7
    write_new(run/'results.json',dict(status='PASS',timing_trials=30,benchmark=load(run/'deadline-benchmark.json'),rolling='PASS',alert_lifecycle='PASS on synthetic replay',comparison=dict(expected_only=reactive['loss'],worst_only=risk['loss']),qualification='Research-only synthetic decisions/effects; no field accuracy or certified latency'))
    print(load(run/'results.json'))
if __name__=='__main__':main()
