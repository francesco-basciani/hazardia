"""Fixed small archived workloads, >=30 bounded decisions per existing policy.
Not a load/scientific release benchmark or a general deadline qualification.
"""
import argparse
import copy
import json
from pathlib import Path
import platform
import statistics
import sys
import time
from hazardia.io import load,write_new,sha256
from hazardia.decision.supervisor import bounded_decide

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--differential',required=True);ap.add_argument('--solver-python',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    assert platform.system()=='Linux'
    ref=Path(a.differential);out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    expected={r['case']:r for r in load(ref/'verification.json')['model_cases']}
    workloads={name:load(ref/(name+'.json')) for name in ['saved-exposure','saved-ideal']}
    for name,p in workloads.items():p['settings']['budget_s']=60;write_new(out/(name+'.json'),p)
    protocol=dict(repetitions_per_policy=30,scope='PINNED_SMALL_WORKLOAD_BOUNDED_DECISION_PILOT',meaning='Fresh controller/solver processes; OS caches not cleared; acceptance starts at invocation, no HTTP queue or service load',inputs={n:sha256(out/(n+'.json')) for n in workloads},threshold_s=60,solver_python=a.solver_python,core_python=sys.version,platform=platform.platform(),script_sha256=sha256(__file__))
    write_new(out/'protocol.json',protocol);rows=[]
    for name,p in workloads.items():
        elapsed=[];statuses=[]
        for i in range(30):
            start=time.perf_counter();r=bounded_decide(copy.deepcopy(p),out/(name+'-'+str(i)),a.solver_python);elapsed.append(time.perf_counter()-start);statuses.append(r['status'])
            assert r['status']=='VALIDATED_FOR_SIMULATION' and r['selected']==expected[name]['selected'] and r['loss']==expected[name]['loss'] and r['operationally_approvable'] is False
        rows.append(dict(case=name,status='PASS',requests=30,p50_s=statistics.median(elapsed),p95_s=sorted(elapsed)[28],max_s=max(elapsed),all_within_60s=all(t<=60 for t in elapsed),samples_s=elapsed,statuses=statuses))
    result=dict(status='PASS' if all(r['all_within_60s'] for r in rows) else 'FAIL',workloads=rows,protocol=protocol);write_new(out/'verification.json',result);print(json.dumps(result),flush=True)
