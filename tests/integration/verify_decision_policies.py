"""Differential policy audit against explicitly supplied trusted baseline source.

Run in the Linux decision environment. Baseline files must be extracted from the
reviewed pre-A4 Git commit, never downloaded executable descriptors. Frozen input
copies and protocol are written exclusively before execution. No application DB,
workspace, source acquisition or simulator execution is involved.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import os
import subprocess
import time
from unittest.mock import patch


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reference-dir',required=True);ap.add_argument('--output',required=True);ap.add_argument('--saved-exposure',required=True);ap.add_argument('--saved-ideal',required=True);ap.add_argument('--solver-python',required=True);a=ap.parse_args()
    assert platform.system()=='Linux'
    from hazardia.decision import problem,controller,verifier
    from hazardia.decision.research_fixture import problem as make_problem
    from tests.decision.test_fire_ideal import fixture as make_ideal
    from hazardia.io import write_new
    ref=Path(a.reference_dir);out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).resolve().parents[2]
    products={h:dict(job_id='frozen-'+h,hazard=h,sha256='a'*64,valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-13T14:00:00Z',weather_hash='b'*64,qualification='UNQUALIFIED_RESEARCH') for h in ['FIRE','FLOOD']}
    cases={h.lower():make_problem(products,h,3) for h in ['FIRE','FLOOD','JOINT']};cases['ideal']=make_ideal()
    cases['saved-exposure']=json.loads(Path(a.saved_exposure).read_bytes());cases['saved-ideal']=json.loads(Path(a.saved_ideal).read_bytes())
    for name,p in cases.items():write_new(out/(name+'.json'),p)
    protocol=dict(scope='SOFTWARE_POLICY_EQUIVALENCE_NOT_PHYSICAL_OR_OPERATIONAL_SKILL',baseline_sources={p.name:sha(p) for p in ref.glob('legacy_*.py')},new_sources={str(p.relative_to(source)):sha(p) for p in (source/'src/hazardia/decision').glob('*.py')},inputs={name:sha(out/(name+'.json')) for name in cases},solver_python=a.solver_python,platform=platform.platform(),hypotheses=['Same input acceptance/errors','Identical HiGHS LP model, result and independently verified losses','Same controller response semantics including empty and degraded cases','Independent verifier source unchanged'],verifier_sha256=sha(source/'src/hazardia/decision/verifier.py'),script_sha256=sha(__file__))
    write_new(out/'protocol.json',protocol)
    oldp=load_module('legacy_problem',ref/'legacy_problem.py');oldc=load_module('legacy_controller',ref/'legacy_controller.py');oldc.validate=oldp.validate
    results=[];negative_count=0
    def outcome(fn,p):
        try:fn(p);return ['ACCEPTED']
        except Exception as e:return [type(e).__name__,getattr(e,'code',None),str(e)]
    for name,p in cases.items():
        variants=[p]
        for field in list(p):
            v=copy.deepcopy(p);del v[field];variants.append(v)
        for value in ['UNKNOWN',None,[],{},True]:v=copy.deepcopy(p);v['schema_version']=value;variants.append(v)
        if p['schema_version']=='0.6.0':
            for key in p['policy']:v=copy.deepcopy(p);v['policy'][key]='UNKNOWN';variants.append(v)
        for v in variants:assert outcome(oldp.validate,v)==outcome(problem.validate,v),(name,outcome(oldp.validate,v),outcome(problem.validate,v));negative_count+=1
        pair=[]
        for label in ['old','new']:
            file=out/(name+'-'+label+'-solver.json');model=out/(name+'-'+label+'.lp')
            wrapper="""import highspy,importlib.util,json,sys
module_path,input_path,output_path,model_path=sys.argv[1:]
spec=importlib.util.spec_from_file_location('audited_worker',module_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
captured=[];original=highspy.Highs
def factory():
 h=original();captured.append(h);return h
highspy.Highs=factory
assert not {'jsonschema','rasterio','propagator'}.intersection(sys.modules)
module.solve(json.load(open(input_path)),output_path)
captured[0].writeModel(model_path)
"""
            module=ref/'legacy_highs.py' if label=='old' else source/'src/hazardia/decision/highs_worker.py'
            subprocess.run([a.solver_python,'-B','-c',wrapper,str(module),str(out/(name+'.json')),str(file),str(model)],env=dict(os.environ,PYTHONPATH=str(source/'src')),check=True)
            raw=json.loads(file.read_bytes());checked=verifier.verify(p,raw['selected']);loss=verifier.losses(p,raw['selected']);pair.append((raw,checked,loss,model.read_bytes()))
        assert pair[0]==pair[1],name
        results.append(dict(case=name,status='PASS',LP_sha256=sha(out/(name+'-new.lp')),selected=pair[1][0]['selected'],verifier_status=pair[1][1]['status'],loss=pair[1][2]))
    flows=[]
    for kind,factory in [('exposure',lambda:copy.deepcopy(cases['fire'])),('ideal',lambda:copy.deepcopy(cases['ideal']))]:
        for mode in ['enumeration','unknown-safety','no-resources','missing-solver']:
            p=factory();p['settings']['budget_s']=8;p['settings']['solver']='highs' if mode=='missing-solver' else 'enumeration'
            if mode=='unknown-safety':
                for r in p['resources']:r['record']['payload']['maintenance']='UNKNOWN'
            if mode=='no-resources':p['resources']=[];p['options']=[]
            responses=[]
            for label,fn in [('old',oldc.decide),('new',controller.decide)]:
                if label=='old':
                    with patch.object(verifier,'validate',oldp.validate):r=fn(copy.deepcopy(p),out/(kind+'-'+mode+'-'+label),'/deliberately-missing/solver-python')
                else:r=fn(copy.deepcopy(p),out/(kind+'-'+mode+'-'+label),'/deliberately-missing/solver-python')
                responses.append({k:v for k,v in r.items() if k not in ['id','elapsed_s','ended_at']})
            assert responses[0]==responses[1],(kind,mode)
            flows.append(dict(policy=kind,mode=mode,status='PASS',response_status=responses[1]['status'],selected=responses[1]['selected'],degradation=responses[1]['degradation']))
    result=dict(status='PASS',model_cases=results,validation_comparisons=negative_count,controller_flows=flows,scope=protocol['scope']);write_new(out/'verification.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
