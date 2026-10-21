"""Run in Linux VM: immutable observed-rain replay, receipts, HTTP and engine pins."""
import datetime as dt,gzip,hashlib,json,platform,sqlite3,statistics,sys,time,urllib.request
from pathlib import Path
from hazardia.ingest.observed_rain import normalize,parse_time,UTC
root=Path(sys.argv[1]);run=root/'runs/observed-rain-20261021';store=root/'web-state/observed-rain'
data=json.loads((store/'latest.json').read_bytes());raw=gzip.decompress((store/(data['id']+'.json.gz')).read_bytes());assert hashlib.sha256(raw).hexdigest()==data['raw_sha256']
cat=json.loads((store/'catalog.json').read_bytes());catraw=gzip.decompress((store/('catalog-'+data['catalog_sha256']+'.json.gz')).read_bytes());assert hashlib.sha256(catraw).hexdigest()==data['catalog_sha256']
replay=normalize(json.loads(raw),json.loads(catraw),parse_time(data['acquired_at']));assert replay['features']==data['features']
local=[f for f in data['features'] if 13<=f['geometry']['coordinates'][0]<=14.9 and 41.6<=f['geometry']['coordinates'][1]<=43]
from collections import Counter
cfg=json.loads((root/'runtime-v2.json').read_bytes())
for path,digest in cfg['engine_files'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
before=json.loads((run/'preserved-before.json').read_bytes())
for path,digest in before.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
u='http://127.0.0.1:8080/api/monitoring/observed-rain';times=[]
for i in range(30):
 begin=time.monotonic()
 with urllib.request.urlopen(u,timeout=3) as r:http=json.load(r)
 times.append((time.monotonic()-begin)*1000);assert http['data']['id']==data['id']
ledger_before=(store/'ledger.json').read_bytes()
with urllib.request.urlopen(urllib.request.Request(u+'/refresh',data=b'{}',headers={'Content-Type':'application/json','X-Hazardia-Research':'1'})) as r:cached=json.load(r)
assert cached['status']=='CACHED';assert (store/'ledger.json').read_bytes()==ledger_before
result=dict(status='PASS',run_id=run.name,source_id=data['id'],acquired_at=data['acquired_at'],raw_sha256=data['raw_sha256'],catalog_sha256=data['catalog_sha256'],stations=len(data['features']),abruzzo_bounding_box_stations=len(local),bbox_networks=dict(Counter(f['properties']['network'] for f in local)),unchanged_engine_files=len(cfg['engine_files']),preserved_workspace_files=len(before),http_cached_30=dict(n=30,p50_ms=statistics.median(times),p95_ms=sorted(times)[28],max_ms=max(times),QR_12='PASS' if sorted(times)[28]<=500 else 'FAIL'),refresh_no_new_download=True,platform=platform.platform(),python=platform.python_version(),limits='Engineering replay, not skill or operational qualification; bounding box not administrative regional membership')
(run/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
