"""VM-only M3 solver/product/API gate, no UI/operational qualification inferred."""
import argparse,copy,json,time,urllib.request,urllib.error,uuid
from pathlib import Path
from hazardia.io import load,write_new,sha256
from hazardia.decision.research_fixture import problem
from hazardia.decision.controller import decide
from hazardia.decision.verifier import verify
from hazardia.contracts import validate_product

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();root=Path(a.runtime);out=Path(a.output);out.mkdir();results=[];cat=load(root/'web-assets/catalog.json');refs={h:next(s['reference'] for s in cat['scenarios'] if s['hazard']==h) for h in ['FIRE','FLOOD']}
    def check(name,fn):
        try:detail=fn();results.append(dict(id=name,status='PASS',detail=detail))
        except Exception as e:results.append(dict(id=name,status='FAIL',detail=type(e).__name__+': '+str(e)))
    def solvepair():
        summary=[]
        for h in ['FIRE','FLOOD']:
            p=problem(refs,h,2);r=decide(p,out/(h+'-highs'),str(root/'decision-env/bin/python'));assert r['status']=='VALIDATED_FOR_SIMULATION'
            p['settings']['solver']='enumeration';q=decide(p,out/(h+'-reference'),str(root/'decision-env/bin/python'));assert q['status']=='VALIDATED_FOR_SIMULATION' and abs(r['loss']['objective']-q['loss']['objective'])<1e-6
            summary.append(dict(hazard=h,objective=r['loss']['objective'],selected=r['selected'],elapsed_s=r['elapsed_s']))
        return summary
    check('both_genuine_hazards_HiGHS_vs_reference',solvepair)
    def terminal():
        p=problem(refs,'FIRE',1);p['commitments']=[dict(option_id=p['options'][0]['id'])];p['options'][0]['road_open']=False
        r=decide(p,out/'infeasible-highs',str(root/'decision-env/bin/python'));assert r['status']=='PROVEN_INFEASIBLE'
        p['settings']['solver']='enumeration';q=decide(p,out/'infeasible-reference',str(root/'decision-env/bin/python'));assert q['status']=='PROVEN_INFEASIBLE'
        p=problem(refs,'FIRE',1);r=decide(p,out/'expired-queue',str(root/'decision-env/bin/python'),accepted_monotonic=time.monotonic()-100);assert r['status']=='TIMEOUT_UNPROVEN' and not r['selected']
        p['settings']['solver']='missing-backend';r=decide(p,out/'missing-solver',str(root/'decision-env/bin/python'));assert r['status']=='DEPENDENCY_UNAVAILABLE'
        p['options'][0]['cost']=None;r=decide(p,out/'unknown-input',str(root/'decision-env/bin/python'));assert r['status']=='INVALID_INPUT'
        return 'Proven infeasible matches exhaustive reference; expired queue, missing solver and invalid input retain distinct statuses'
    check('negative_terminal_statuses_and_deadline_start',terminal)
    def replacement():
        core=Path(__file__).resolve().parents[2]/'src/hazardia/decision';before={p.name:sha256(p) for p in core.glob('*.py')};job=root/'jobs'/refs['FIRE']['job_id'];raw=load(job/'product.json');req=load(job/'request.json');test=copy.deepcopy(raw);test['engine'].update(name='CONTROLLED_TEST_ADAPTER',source_commit='TEST_METADATA_ONLY',patch_sha256=None);validate_product(test,req,job);write_new(out/'controlled-compatible-product.json',test)
        p=problem(refs,'FIRE',2);old=decide(p,out/'original-adapter',str(root/'decision-env/bin/python'));p['events'][0]['product']['job_id']='controlled-compatible-adapter';new=decide(p,out/'controlled-adapter',str(root/'decision-env/bin/python'));assert old['loss']==new['loss'] and new['status']=='VALIDATED_FOR_SIMULATION';assert before=={p.name:sha256(p) for p in core.glob('*.py')}
        return dict(core_sha256=before,scope='Compatible controlled metadata adapter boundary only; no alternate physical-model accuracy claim')
    check('AT_EXT_01_02_04_compatible_consumer_core_unchanged',replacement)
    def api_checks():
        base='http://127.0.0.1:8080';samples=[]
        for _ in range(30):
            t=time.monotonic()
            with urllib.request.urlopen(base+'/api/catalog') as response:data=json.load(response)
            samples.append((time.monotonic()-t)*1000);assert data['no_operational_authority'] is True
        p95=sorted(samples)[28];assert p95<500
        cases=[(b'{"hazard":"FIRE"}',{},403),(b'{"hazard":"FIRE","hazard":"FLOOD"}',{'X-Hazardia-Research':'1'},400),(b'{}',{'X-Hazardia-Research':'1','Origin':'https://evil.example'},403)]
        for body,headers,expected in cases:
            try:urllib.request.urlopen(urllib.request.Request(base+'/api/decisions',data=body,headers=dict({'Content-Type':'application/json'},**headers)))
            except urllib.error.HTTPError as e:assert e.code==expected
            else:raise AssertionError('Unsafe request accepted')
        old=next(s for s in cat['scenarios'] if s['hazard']=='FLOOD' and s['valid_from'].endswith('T00:00:00Z'))
        body=json.dumps(dict(hazard='JOINT',scenario_ids={'FIRE':refs['FIRE']['job_id'],'FLOOD':old['id']})).encode()
        try:urllib.request.urlopen(urllib.request.Request(base+'/api/decisions',data=body,headers={'Content-Type':'application/json','X-Hazardia-Research':'1'}))
        except urllib.error.HTTPError as e:assert json.load(e)['code']=='MISMATCHED_WINDOWS'
        else:raise AssertionError('Mismatched genuine time windows accepted')
        write_new(out/'api-latency.json',dict(samples_ms=samples,p95_ms=p95,environment='Linux VM loopback; browser separate'))
        return dict(n=30,p95_ms=p95,negative_HTTP_cases=4)
    check('API_latency_CSRF_strictJSON_and_comparison_windows',api_checks)
    write_new(out/'results.json',dict(checks=results,passed=sum(c['status']=='PASS' for c in results),failed=sum(c['status']=='FAIL' for c in results)))
    for r in results:print(r)
    if any(r['status']=='FAIL' for r in results):raise SystemExit(1)
if __name__=='__main__':main()
