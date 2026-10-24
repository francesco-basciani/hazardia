"""Paired metadata-selection pilot only; not simulation or decision deadline."""
import inspect
import json
import os
import platform
import statistics
import subprocess
import sys
import time

if __name__ == '__main__':
    assert platform.system()=='Linux'
    from tests.unit.test_dispatch import legacy,DispatchTests
    from hazardia.adapters.dispatch import prepare
    fixture=DispatchTests();fixture.setUp();req=fixture.req();cfg=fixture.cfg;env=fixture.env
    protocol=dict(repetitions=30,scope='FIXED_METADATA_SELECTION_MICROBENCHMARK',cold='Fresh interpreter; OS page cache not cleared',warm='Same process, no cache in discovery',source_equivalence='Old selector function vs new approved lookup; same request/config/env',python=sys.version,platform=platform.platform(),threshold='No new SLO; report overhead without relaxing existing targets')
    print(json.dumps(dict(protocol=protocol)),flush=True)
    cold_old=[];cold_new=[];warm_old=[];warm_new=[]
    bootstrap='import os,json\nfrom hazardia.io import HazardError\nreq,cfg,env=json.loads('+repr(json.dumps([req,cfg,env]))+')\n'
    for _ in range(30):
        for samples,code in [(cold_old,bootstrap+inspect.getsource(legacy)+'\nlegacy(req,cfg,"/job",env)'),(cold_new,bootstrap+'from hazardia.adapters.dispatch import prepare\nprepare(req,cfg,"/job",env)')]:
            start=time.perf_counter();subprocess.run([sys.executable,'-B','-c',code],env=dict(os.environ),check=True,stdout=subprocess.DEVNULL);samples.append((time.perf_counter()-start)*1000)
    for _ in range(30):
        for samples,fn in [(warm_old,legacy),(warm_new,prepare)]:
            start=time.perf_counter();fn(req,cfg,'/job',env);samples.append((time.perf_counter()-start)*1000)
    def summary(samples):return dict(p50_ms=statistics.median(samples),p95_ms=sorted(samples)[28],max_ms=max(samples),samples_ms=samples)
    print(json.dumps(dict(protocol=protocol,cold_old=summary(cold_old),cold_new=summary(cold_new),warm_old=summary(warm_old),warm_new=summary(warm_new))),flush=True)
