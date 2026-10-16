"""Single-VM local HTTP controlled faults + actual owned native-worker crash."""
import argparse,json,time,urllib.request,urllib.error,os,signal
from pathlib import Path
from hazardia.io import write_new,load
from hazardia.decision.verifier import verify

def api(path,body=None):
    r=urllib.request.Request('http://127.0.0.1:8080/api/'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json','X-Hazardia-Research':'1'})
    try:
        with urllib.request.urlopen(r,timeout=15) as f:return f.status,json.load(f)
    except urllib.error.HTTPError as e:return e.code,json.load(e)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--run',required=True);a=ap.parse_args();root=Path(a.runtime);out=Path(a.run);out.mkdir(exist_ok=False);results=[]
    def action(name,**kwargs):
        revision=api('research')[1]['revision'];status,data=api('research',dict(action=name,expected_revision=revision,**kwargs));assert status==200,(status,data);return data
    def decide(hazard='FIRE',**extra):
        code,r=api('decisions',dict(hazard=hazard,resources=4,**extra))
        if code!=202:return r
        for _ in range(400):
            time.sleep(.05);r=api('decisions/'+r['id'])[1]
            if r['status'] not in ['QUEUED','RUNNING']:
                if r['status']=='VALIDATED_FOR_SIMULATION':assert verify(api('decisions/'+r['id']+'/problem')[1],r['selected'])['status']=='VALIDATED_FOR_SIMULATION'
                return r
        raise AssertionError('decision did not terminate')
    def record(name,**detail):
        item=dict(test=name,status='PASS',**detail);results.append(item);write_new(out/(name+'.json'),item)
    action('recover');baseline=decide();assert baseline['status']=='VALIDATED_FOR_SIMULATION'
    for fault in ['flood_worker','safety_unknown','source_stale','coordinator_down','solver_down','road_closed','resource_loss']:
        action('recover');health=action('inject',fault=fault);assert api('catalog')[0]==200;assert api('decisions/'+baseline['id'])[1]['status']=='STALE_CONTEXT'
        if fault=='flood_worker':
            assert decide('FLOOD')['code']=='DEPENDENCY_UNAVAILABLE';r=decide('FIRE');assert r['status']=='VALIDATED_FOR_SIMULATION'
        elif fault in ['safety_unknown','source_stale','solver_down']:
            r=decide();assert r['code']=={'safety_unknown':'SAFETY_UNVERIFIED','source_stale':'STALE_PRODUCT','solver_down':'DEPENDENCY_UNAVAILABLE'}[fault]
        else:
            r=decide('JOINT');assert r['status']=='VALIDATED_FOR_SIMULATION';p=api('decisions/'+r['id']+'/problem')[1];selected=[o for o in p['options'] if o['id'] in r['selected']]
            if fault=='coordinator_down':
                homes={x['id']:x['home_region'] for x in p['resources']};regions={e['id']:e['region'] for e in p['events']};assert all(homes[o['resource_id']]==regions[o['event_id']] for o in selected)
            if fault=='road_closed':assert not selected
            if fault=='resource_loss':assert not any(o['resource_id']=='unit-1' for o in selected)
        weights=[3,2,2,1,1,1];quality={'NOMINAL':1,'DEGRADED':.5,'UNAVAILABLE':0};score=sum(w*quality[c['state']] for w,c in zip(weights,health['capabilities']))/sum(weights)
        record('controlled-'+fault,capabilities=health['capabilities'],retained_research_score=score,illustrative_fail_stop_score=0,weight_policy=weights,decision=r)
    revision=api('research')[1]['revision'];assert api('research',dict(action='recover',expected_revision=revision-1))[1]['code']=='STALE_REVISION';record('reject-stale-recovery')
    action('recover');late=decide(preparedness='DELAYED');early=decide(preparedness='PREPOSITIONED');assert early['loss']['expected']<late['loss']['expected'];record('authored-preparedness',delayed=late,prepositioned=early,qualification='synthetic linear benefit vs arrival; no real effectiveness')
    first=decide();next_=decide(rolling_from=first['id']);assert next_['status']=='VALIDATED_FOR_SIMULATION' and next_['rolling_progress'];record('rolling-http',previous=first,next=next_)
    action('forecast_reset');states=[]
    for action_name in ['forecast','ack','forecast','forecast','forecast','expire']:
        h=action(action_name);states.append(next(iter(h['alerts'].values()))['state'])
    assert states==['OPEN','ACKNOWLEDGED','UPDATED','RESOLVED','OPEN','EXPIRED'],states;record('ui-api-advisory-lifecycle',states=states)
    action('inject',fault='source_stale');assert api('research',dict(action='forecast',expected_revision=api('research')[1]['revision']))[1]['code']=='STALE_FORECAST';action('recover')
    # Kill ONLY the worker of the job just submitted here, never another user's job.
    assert not any(j['state'] in ['RUNNING','QUEUED'] for j in api('jobs')[1]),'User model activity: do not interfere'
    code,job=api('jobs',dict(hazard='FLOOD'));assert code==202;ident=job['id'];pid=None
    for _ in range(200):
        j=next(j for j in api('jobs')[1] if j['id']==ident)
        if j['state']=='RUNNING' and j['worker_pid']:pid=j['worker_pid'];break
        time.sleep(.1)
    assert pid;cmd=Path('/proc/'+str(pid)+'/cmdline').read_bytes().replace(b'\0',b' ').decode();assert ident in cmd and 'hazardia.adapters.pipeline' in cmd,cmd
    time.sleep(2);os.killpg(pid,signal.SIGKILL)
    for _ in range(200):
        j=next(j for j in api('jobs')[1] if j['id']==ident)
        if j['state'] not in ['QUEUED','RUNNING']:break
        time.sleep(.1)
    assert j['state']=='ERROR' and not j['usable_product'],j
    fire=decide();assert fire['status']=='VALIDATED_FOR_SIMULATION';record('actual-owned-flood-worker-crash',job=j,command=cmd,fire=fire,manifest=load(root/'jobs'/ident/'manifest.json') if (root/'jobs'/ident/'manifest.json').exists() else 'See job store manifest')
    write_new(out/'results.json',dict(status='PASS',scope='Controlled adaptation + separately real owned worker crash; no field/forecast skill',results=results));print('PASS',len(results),'integration groups')
if __name__=='__main__':main()
