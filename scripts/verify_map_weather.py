"""Read-only field/source transformation check; execute in the Linux VM."""
import argparse,hashlib,json,math,platform,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--output',required=True);a=p.parse_args()
assert platform.system()=='Linux','Use the VM'
r=Path(a.runtime);out=Path(a.output);assert not out.exists();cache=r/'web-state/map-weather'
with sqlite3.connect(cache/'quota.sqlite') as db:name=db.execute('SELECT snapshot FROM state WHERE id=1').fetchone()[0];attempts=db.execute('SELECT count(*) FROM attempts').fetchone()[0]
f=json.loads((cache/name).read_text());raw=(cache/('raw-'+f['source']['sha256']+'.json')).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['source']['sha256'];nodes=json.loads(raw);assert len(nodes)==81 and f['issued_at'] is None
count=0;max_error=0
for hour in [0,24,len(f['records'])-1]:
 row=f['records'][hour]
 for j,(y,x) in enumerate((y,x) for y in f['lats'] for x in f['lons']):
  near=sorted((((n['latitude']-y)**2+((n['longitude']-x)*math.cos(math.radians(y)))**2,i) for i,n in enumerate(nodes)))[:4]
  weights=[(near[0][1],1.)] if near[0][0]<1e-14 else [(i,(1/d)/sum(1/d2 for d2,i2 in near)) for d,i in near]
  expected=[0.,0.,0.,0.]
  for i,w in weights:
   h=nodes[i]['hourly'];assert h['time'][hour]+':00Z'==row['at'];ang=math.radians(h['wind_direction_10m'][hour]);s=h['wind_speed_10m'][hour]
   for k,value in enumerate([-s*math.sin(ang),-s*math.cos(ang),h['temperature_2m'][hour],h['precipitation'][hour+1]]):expected[k]+=w*value
  for axis,value in zip(['u','v','temperature','precipitation'],expected):
   err=abs(row[axis][j]-value);assert err<=.000051;max_error=max(max_error,err);count+=1
cfg=json.loads((r/'runtime-v2.json').read_text())
for path,h in cfg['engine_files'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
result=dict(status='PASS',field_id=f['id'],raw_sha256=f['source']['sha256'],raw_bytes=len(raw),available_at=f['available_at'],hours=len(f['records']),source_checks=count,max_rounding_error=max_error,units='separately m/s, degreesC, mm; rounding only, not accuracy',engine_hashes_unchanged=len(cfg['engine_files']),attempts=attempts,bounds=f['bounds'],python=platform.python_version(),platform=platform.platform())
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
