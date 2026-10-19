"""Import a bounded, licensed OSM JSON snapshot in the VM; no download or model run."""
import argparse,hashlib,json
from pathlib import Path
from hazardia.territorial_context import parse_osm,bounds_checked
from hazardia.osm_catalog import CATALOG_VERSION,summary
from hazardia.io import utcnow,write_new
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--raw',required=True);ap.add_argument('--bounds',nargs=4,type=float,required=True);ap.add_argument('--source-url',required=True);ap.add_argument('--source-available-at',default=None);a=ap.parse_args();bounds_checked(a.bounds);p=Path(a.raw)
if p.stat().st_size>32*1024**2:raise ValueError('Snapshot exceeds32MiB; prepare a smaller extract')
raw=p.read_bytes();data=json.loads(raw)
features,skipped=parse_osm(data)
if len(features)>20000:raise ValueError('More than20000 mapped features; split the snapshot')
sha=hashlib.sha256(raw).hexdigest();archive=Path(a.root)/'territorial-sources'/(sha+'.json');archive.parent.mkdir(parents=True,exist_ok=True)
if not archive.exists():
 with archive.open('xb') as source:source.write(raw)
if hashlib.sha256(archive.read_bytes()).hexdigest()!=sha:raise ValueError('Archived source checksum mismatch')
out=Path(a.root)/'territorial-imports'/(sha+'-catalog2.json');out.parent.mkdir(parents=True,exist_ok=True)
value=dict(catalog=summary(features),type='FeatureCollection',features=features,coverage_bbox_wgs84=a.bounds,source_url=a.source_url,source_sha256=sha,raw_source_relative_path=str(archive.relative_to(a.root)),license='ODbL-1.0',available_at=utcnow(),source_available_at=a.source_available_at,source_data_at=data.get('osm3s',{}).get('timestamp_osm_base'),missing=['Inventory completeness','Height and sag','Population and occupancy','Unresolved relations use labelled center proxies or remain in raw only'],skipped=skipped)
if len(json.dumps(value).encode())>16*1024**2:raise ValueError('Derived inventory exceeds16MiB; split the extract')
if not out.exists():write_new(out,value)
print(json.dumps(dict(path=str(out),features=len(features),power_lines=sum(f['properties']['category']=='power_line' for f in features),source_sha256=sha)))
