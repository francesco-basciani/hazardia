"""VM-only derived snapshot from archived bulletin + its official SHP attachment.
No new warning date, no destructive archive edits, no implicit source refresh.
"""
import argparse,hashlib,json,platform,re,shutil,uuid
from pathlib import Path
from hazardia.ingest.attention import AttentionStore
from hazardia.ingest.attention_worker import topology,official_shapes,recover_official_shapes,qualify_footprints,geometry_coverage,zone_summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--receipt',required=True);p.add_argument('--archive',required=True);p.add_argument('--expected-snapshot',required=True);p.add_argument('--report',required=True);a=p.parse_args()
    if platform.system()!='Linux':raise SystemExit('VM Linux only')
    root=Path(a.runtime);store=AttentionStore(root/'web-state/attention',root);state=store.state();ident,base=store.bundle()
    if ident!=a.expected_snapshot:raise ValueError('Snapshot changed; review new bulletin first')
    receipt=json.loads(Path(a.receipt).read_text());raw=Path(a.archive).read_bytes()
    if len(raw)>8*1024**2 or hashlib.sha256(raw).hexdigest()!=receipt['sha256']:raise ValueError('SHP receipt mismatch')
    source=base['sources']['dpc'];pattern=r'https://raw.githubusercontent.com/pcm-dpc/DPC-Bollettini-Criticita-Idrogeologica-Idraulica/'+source['revision']+r'/files/shp/(\d{8}_\d{4})_shp.zip'
    match=re.fullmatch(pattern,receipt['url'])
    if not match:raise ValueError('SHP not from pinned bulletin revision')
    folder=store.root/('snapshot-'+uuid.uuid4().hex);folder.mkdir();old=store.root/ident
    for name,digest in base['files'].items():
        if Path(name).name!=name:raise ValueError('Invalid manifest path')
        data=store.raw(old/name)
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Original hash mismatch')
        (folder/name).write_bytes(data)
    archive=folder/'dpc-official-shapes.zip';archive.write_bytes(raw);report=[]
    for index,product in enumerate(source['products']):
        key=['today','tomorrow'][index];geo=topology(json.loads((folder/('dpc-'+key+'.json')).read_text()))
        recover_official_shapes(geo,official_shapes(archive,match[1]+'_'+key),receipt['url']);qualify_footprints(geo)
        before=json.loads((folder/product['file']).read_text());assert len(geo['features'])==len(before['features'])
        for x,y in zip(before['features'],geo['features']):assert x['properties']['reasons']==y['properties']['reasons']
        (folder/product['file']).write_text(json.dumps(geo,separators=(',',':')))
        product.update(geometry_coverage(geo),unknown_zones=sum(f['properties']['level'] is None for f in geo['features']),attention_zones=sum((f['properties']['level'] or 0)>0 for f in geo['features']))
        for ep in base['sources']['effis']['products']:
            if ep['day']!=product['day'] or not ep.get('source_grid_file'):continue
            summary=zone_summary(json.loads((folder/ep['source_grid_file']).read_text()),geo)
            (folder/ep['file']).write_text(json.dumps(summary,separators=(',',':')))
            ep['unknown_zones']=sum(f['properties']['level'] is None for f in summary['features'])
        report.append(dict(day=product['day'],**geometry_coverage(geo)))
    source['status']='PARTIAL' if any(p['unknown_zones'] for p in source['products']) else 'AVAILABLE'
    base['sources']['effis']['status']='AVAILABLE' if all(p.get('spatial_support')=='DPC_METEO_HYDRO_ZONE' and not p.get('unknown_zones') for p in base['sources']['effis']['products']) and not base['sources']['effis'].get('errors') else 'PARTIAL'
    base['derived_from']=ident;base['geometry_derivation']=dict(source=receipt['url'],sha256=receipt['sha256'],method='Valid official same-bulletin SHP fallback only; no geometric repair; original warning/acquisition times retained')
    base['files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in folder.iterdir() if f.is_file()}
    data=json.dumps(base,separators=(',',':')).encode();(folder/'result.json').write_bytes(data)
    if store.state()!=state:raise ValueError('Concurrent state change; derived folder retained but not activated')
    store.write_state(dict(state,snapshot=folder.name,sha256=hashlib.sha256(data).hexdigest()))
    result=dict(status='PASS',before=ident,after=folder.name,products=report,acquired_at=base['acquired_at'],note='All official textual classifications retained; remaining invalid boundaries explicitly unavailable')
    Path(a.report).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
