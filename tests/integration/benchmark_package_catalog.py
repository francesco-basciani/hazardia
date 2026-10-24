"""Opt-in metadata microbenchmark, not a simulator or 60s decision benchmark."""
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

if __name__ == '__main__':
    assert platform.system() == 'Linux'
    from hazardia.package_catalog import discover, ROOT
    protocol=dict(scope='METADATA_ONLY_MICROBENCHMARK',cold='New Python process; OS page cache not cleared',warm='Repeated lookup in one process',repetitions=30,threshold='No new latency SLO; zero network/scientific import/write tested separately',python=sys.version,platform=platform.platform(),descriptor_bytes=sum(p.stat().st_size for p in (ROOT/'domain_packages').glob('*.json')))
    print(json.dumps(dict(protocol=protocol)),flush=True)
    cold=[];baseline=[];warm=[]
    for _ in range(30):
        for samples,code in [(baseline,'import json;print("baseline")'),(cold,'from hazardia.package_catalog import discover;assert len(discover().describe()["packages"])==2')]:
            t=time.perf_counter();subprocess.run([sys.executable,'-B','-c',code],env=dict(os.environ),check=True,stdout=subprocess.DEVNULL);samples.append((time.perf_counter()-t)*1000)
    for _ in range(30):
        t=time.perf_counter();discover().describe();warm.append((time.perf_counter()-t)*1000)
    def stats(samples):return dict(p50_ms=statistics.median(samples),p95_ms=sorted(samples)[28],max_ms=max(samples),samples_ms=samples)
    print(json.dumps(dict(protocol=protocol,interpreter_baseline=stats(baseline),cold=stats(cold),warm=stats(warm))),flush=True)
