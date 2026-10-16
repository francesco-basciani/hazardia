"""Acquire the preregistered Abruzzo research inputs; run inside Linux only."""
import argparse,platform
from pathlib import Path
from hazardia.io import load,write_new,HazardError,utcnow
from hazardia.ingest.http import Cache
from hazardia.ingest.providers import StacProvider,OpenMeteoHistoryProvider

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);args=ap.parse_args()
    if platform.system()!='Linux':raise SystemExit('Runtime must execute in Linux')
    root=Path(args.root).resolve();plan=load(root/'plan.json');bbox=plan['territory']['bbox_wgs84']
    cache=Cache(root/'cache',plan['limits']['new_source_payload_bytes']);provider=StacProvider('https://earth-search.aws.element84.com/v1',cache)
    results={};receipts=[]
    for kind,collection,interval in [('dem','cop-dem-glo-30',None),('sentinel','sentinel-2-l2a','2024-07-01T00:00:00Z/2024-07-31T23:59:59Z')]:
        items,receipt=provider.search(collection,bbox,interval,kind+'-search.json');receipts.append(receipt)
        item=provider.choose_covering(items,bbox)
        target=root/(kind+'-item.json')
        if target.exists():
            if load(target)!=item:raise HazardError('SOURCE_DRIFT','Selected source changed; new snapshot required')
        else:write_new(target,item)
        results[kind]=item
        print(kind,item['id'],item['properties'].get('datetime'),flush=True)
        for asset,label,cap in ([('data','dem-original.tif',80*1024**2)] if kind=='dem' else [('visual','sentinel-original.tif',384*1024**2),('scl','sentinel-scl.tif',8*1024**2)]):
            url=item['assets'][asset]['href']
            if url.startswith('s3://'):
                bucket,key=url[5:].split('/',1);url='https://'+bucket+'.s3.amazonaws.com/'+key
            result=cache.fetch(label,url,cap=cap);receipts.append(result);print(label,result['bytes'],result['sha256'],flush=True)
    date=results['sentinel']['properties']['datetime'][:10]
    weather,receipt=OpenMeteoHistoryProvider(cache).acquire((bbox[1]+bbox[3])/2,(bbox[0]+bbox[2])/2,date)
    write_new(root/'weather.json',weather);receipts.append(receipt)
    warm=[]
    for record in receipts:
        label=next(p.name[:-12] for p in cache.root.glob('*.source.json') if load(p)['url']==record['url'])
        warm.append(cache.fetch(label,record['url'],cap=max(record['bytes'],4*1024**2)))
    write_new(root/'ingestion-result.json',dict(status='PASS',executed_utc=utcnow(),receipts=receipts,warm_receipts=warm,weather_date=date,notes='Metadata timings are acquisition-only; no simulation or historic skill inferred'))
    print('INGESTION PASS',flush=True)
if __name__=='__main__':main()
