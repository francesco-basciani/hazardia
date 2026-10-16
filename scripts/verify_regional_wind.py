"""Read-only frozen-wind engineering verification; run in the Linux VM."""
import argparse,hashlib,json,math,platform,sqlite3
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--runtime',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    if platform.system()!='Linux':raise SystemExit('Execute data verification in the VM')
    out=Path(a.output)
    if out.exists():raise SystemExit('Refusing existing verification output')
    root=Path(a.cache)
    with sqlite3.connect(root/'quota.sqlite') as db:name=db.execute('SELECT snapshot FROM state WHERE id=1').fetchone()[0];attempts=db.execute('SELECT count(*) FROM attempts').fetchone()[0]
    field=json.loads((root/name).read_text());source=field['source'];raw=(root/('raw-'+source['sha256']+'.json')).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256'];nodes=json.loads(raw)
    assert len(nodes)==field['requested_nodes']==315
    assert field['issued_at'] is None and field['issued_at_status']=='UNKNOWN_PROVIDER'
    checks=0;max_error=0;offset=0
    for node,(lat,lon) in zip(nodes,[(y,x) for y in field['lats'] for x in field['lons']]):offset=max(offset,111000*math.hypot(node['latitude']-lat,(node['longitude']-lon)*math.cos(math.radians(lat))))
    for hour in [0,24,95]:
        row=field['records'][hour];assert all(n['hourly']['time'][hour]+':00Z'==row['at'] for n in nodes)
        for index,(lat,lon) in enumerate((y,x) for y in field['lats'] for x in field['lons']):
            near=sorted(((n['latitude']-lat)**2+((n['longitude']-lon)*math.cos(math.radians(lat)))**2,i) for i,n in enumerate(nodes))[:4]
            weights=[(near[0][1],1.)] if near[0][0]<1e-14 else [(i,(1/d)/sum(1/k for k,_ in near)) for d,i in near]
            expected=[0.,0.]
            for i,w in weights:
                h=nodes[i]['hourly'];s=h['wind_speed_10m'][hour];angle=math.radians(h['wind_direction_10m'][hour]);expected[0]-=w*s*math.sin(angle);expected[1]-=w*s*math.cos(angle)
            for axis,value in zip(['u','v'],expected):
                error=abs(row[axis][index]-value);max_error=max(max_error,error);assert error<=.000051;checks+=1
    config=json.loads((Path(a.runtime)/'runtime-v2.json').read_text())
    for f,digest in config['engine_files'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==digest
    result=dict(status='PASS',source_sha256=source['sha256'],field_id=field['id'],available_at=source['available_at'],nodes=len(nodes),hours=len(field['records']),component_comparisons=checks,max_rounding_error_ms=max_error,requested_to_returned_max_offset_m=offset,unchanged_engine_files=len(config['engine_files']),total_reserved_attempts=attempts,raw_bytes=len(raw),limits='Engineering transformations/checksums only, not forecast skill or observational validation',platform=platform.platform(),python=platform.python_version())
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
