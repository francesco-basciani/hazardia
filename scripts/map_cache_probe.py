from pathlib import Path
import json,time,hashlib,statistics
from hazardia.web.consultation_maps import CachedImagery
from hazardia.web.maps import RegionalSatellite
import argparse
p=argparse.ArgumentParser(description='One on-demand tile already viewed by a human: empty cache, RAM hits, disk hit. No prefetch/bulk use.');p.add_argument('--out',required=True);p.add_argument('--tile',required=True,nargs=3,type=int,metavar=('Z','X','Y'));args=p.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True);state=out/'isolated-cache-pilot'
if state.exists():raise SystemExit('Refusing to label populated cache cold')
state.mkdir();c=CachedImagery(state,RegionalSatellite);samples=[]
for i in range(11):
 start=time.perf_counter();raw=c.tile(*args.tile);samples.append((time.perf_counter()-start)*1000)
c2=CachedImagery(state,RegionalSatellite);start=time.perf_counter();again=c2.tile(*args.tile);disk=(time.perf_counter()-start)*1000
assert again==raw
result=dict(scope='Single previously viewed EOX tile, isolated empty proxy cache, then10RAMhits and restart/diskhit; internet cold n1, not p95 qualification',cold_ms=samples[0],warm_ms=samples[1:],warm_median_ms=statistics.median(samples[1:]),restart_disk_ms=disk,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),status=c.status(),restart_status=c2.status())
(out/'cache-pilot.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
