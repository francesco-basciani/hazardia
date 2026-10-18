"""Bounded ideal spatial policy and explicit frozen-forcing native replays."""
import copy,json,os,re,subprocess,time,uuid,threading
from pathlib import Path
from hazardia.io import load,write_new,sha256,HazardError,utcnow
from hazardia.decision.fire_ideal import validate_input
from hazardia.decision.supervisor import bounded_decide

DEADLINE_S=60

def submit(app,body):
    validate_input(body)
    if app.store.get(body['job_id'])['state']!='SUCCEEDED':raise HazardError('DEPENDENCY_UNAVAILABLE','Completed baseline required')
    if not app.capacity.acquire(False):raise HazardError('QUEUE_FULL','Decision queue full')
    accepted=time.monotonic();ident='decision-'+uuid.uuid4().hex;stage=app.state/(ident+'-input');stage.mkdir();write_new(stage/'request.json',body)
    with app.lock:app.results[ident]=dict(id=ident,status='QUEUED',operationally_approvable=False)
    expired=threading.Event();done=threading.Event()
    def expire():
        with app.lock:
            if done.is_set():return
            expired.set();r=dict(id=ident,status='TIMEOUT_UNPROVEN',selected=[],detail='Outer deadline including queued preparation',operationally_approvable=False,elapsed_s=time.monotonic()-accepted)
            app.results[ident]=r
        write_new(stage/'deadline.json',r)
    timer=threading.Timer(max(.001,DEADLINE_S-.25 if DEADLINE_S>1 else DEADLINE_S),expire);timer.daemon=True;timer.start()
    def work():
        try:
            if expired.is_set():return
            with app.lock:app.results[ident]=dict(id=ident,status='RUNNING',operationally_approvable=False)
            cfg=load(app.root/'runtime-v2.json');env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),PROJ_LIB='/usr/share/proj')
            remaining=60-(time.monotonic()-accepted)
            if remaining<=0:raise subprocess.TimeoutExpired('queue',60)
            with (stage/'prepare.log').open('xb') as log:proc=subprocess.run([cfg['geo_python'],'-m','hazardia.decision.fire_ideal',str(app.root),str(stage/'request.json'),str(stage/'prepared')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=min(30,remaining))
            if proc.returncode:raise HazardError('INVALID_INPUT','Geographic policy could not be prepared; check coverage, baseline without interventions and logs')
            p=load(stage/'prepared/problem.json');context=load(stage/'prepared/context.json')
            with app.lock:p=app.replay.apply(p);health=app.replay.snapshot()
            r=bounded_decide(p,app.state/ident,str(app.root/'decision-env/bin/python'),accepted_monotonic=accepted)
            chosen=[context['option_resources'][oid] for oid in r['selected']];r.update(replay_health_revision=health['revision'],ideal=dict(baseline_job_id=body['job_id'],baseline_input=context['baseline_input'],assets=[{k:v for k,v in a.items() if k!='geometry'} for a in context['assets']],proposed_resources=chosen,assumptions=context['assumptions'],source=context['source'],fleet=body['fleet'],effect_qualification='IDEAL_PROXY_NOT_PHYSICAL_OPTIMUM',unavailable_units=[x['id'] for x in p['resources'] if x['record']['payload']['maintenance']!='READY']))
            write_new(app.state/ident/'context.json',dict(health=health,ideal=r['ideal']));write_new(app.state/ident/'ideal-result.json',r)
        except Exception as e:
            r=dict(id=ident,status='TIMEOUT_UNPROVEN' if isinstance(e,subprocess.TimeoutExpired) else e.code if isinstance(e,HazardError) else 'ERROR',detail=str(e),selected=[],operationally_approvable=False,elapsed_s=time.monotonic()-accepted)
            if not (app.state/ident).exists():(app.state/ident).mkdir()
            if not (app.state/ident/'response.json').exists():write_new(app.state/ident/'response.json',r)
        finally:app.capacity.release()
        with app.lock:
            done.set();timer.cancel()
            if expired.is_set():return
            app.results[ident]=r
            while len(app.results)>100:app.results.pop(next(iter(app.results)))
    app.pool.submit(work);return dict(id=ident,status='QUEUED',budget_s=60)

def replay(app,body):
    if set(body)!={'decision_id'}:raise HazardError('INVALID_INPUT','Decision ID only')
    result=app.decision(body['decision_id'])
    if result['status']!='VALIDATED_FOR_SIMULATION' or 'ideal' not in result:raise HazardError('SAFETY_UNVERIFIED','Current independently checked ideal decision required')
    p=load(app.state/body['decision_id']/'problem.json');baseline=p['events'][0]['product']['job_id'];source=app.root/'jobs'/baseline
    # Capture verified frozen input, never relabel it as a newly acquired forecast.
    original=load(source/'request.json')
    for asset in original['assets']:
        if sha256(source/asset['path'])!=asset['sha256']:raise HazardError('CHECKSUM','Frozen input changed')
    plan=load(source/'input/fire_plan.json');manifest=load(source/'manifest.json')
    if sha256(source/'fire-output.npz')!=manifest['artifacts']['fire-output.npz']:raise HazardError('CHECKSUM','Baseline changed')
    units=[{k:v for k,v in u.items() if k in ['id','category','area','at_minutes','effect']} for u in result['ideal']['proposed_resources']]
    action_times=sorted(set(int(u['at_minutes']*60) for u in units));clock=sorted(set([*plan.get('comparison_times',[]),*plan['action_times'],*action_times]));folder=app.state/('ideal-native-'+uuid.uuid4().hex);folder.mkdir();jobs={}
    with app.lock:
        with app.store.connect() as db:
            if db.execute("SELECT count(*) FROM jobs WHERE state='QUEUED'").fetchone()[0]>app.store.capacity-2:raise HazardError('QUEUE_FULL','Two paired queue places required')
        try:
            for case in ['A','B']:
                dest=folder/case;dest.mkdir();req=copy.deepcopy(original);req['id']='ideal-replay-'+case+'-'+uuid.uuid4().hex;req['assumptions']+=['Frozen forcing replay; ideal geometry hypothesis; not a fresh forecast','A/B share all action and comparison timestamps']
                current=copy.deepcopy(plan);current.update(case=case,resources=units if case=='B' else [],action_times=action_times,comparison_times=clock)
                write_new(dest/'plan.json',current)
                for asset in req['assets']:
                    if asset['role']=='fire_plan':asset.update(path=str((dest/'plan.json').relative_to(folder)),sha256=sha256(dest/'plan.json'))
                    else:
                        import shutil
                        target=dest/Path(asset['path']).name;shutil.copyfile(source/asset['path'],target);asset['path']=str(target.relative_to(folder))
                jobs[case]=app.store.submit(req,folder)
        except Exception:
            for job in jobs.values():app.store.cancel(job)
            raise
    write_new(folder/'replay.json',dict(decision_id=body['decision_id'],source_baseline=baseline,jobs=jobs,qualification='UNQUALIFIED_IDEAL_FROZEN_REPLAY'));return dict(jobs=jobs,qualification='UNQUALIFIED_IDEAL_FROZEN_REPLAY')
