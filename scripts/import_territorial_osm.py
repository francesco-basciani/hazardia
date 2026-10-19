"""Import a bounded, licensed OSM JSON snapshot in the VM; no download or model run."""
import argparse,hashlib,json
from pathlib import Path
from hazardia.territorial_context import parse_osm,bounds_checked
from hazardia.io import utcnow,write_new
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--raw',required=True);ap.add_argument('--bounds',nargs=4,type=float,required=True);ap.add_argument('--source-url',required=True);ap.add_argument('--source-available-at',default=None);a=ap.parse_args();bounds_checked(a.bounds);p=Path(a.raw)
if p.stat().st_size>32*1024**2:raise ValueError('Snapshot exceeds32MiB; prepare a smaller extract')
raw=p.read_bytes();data=json.loads(raw);nodes={e['id']:dict(lat=e['lat'],lon=e['lon']) for e in data['elements'] if e['type']=='node'};elements=[]
for original in data['elements']:
 e=dict(original)
 if e['type']=='way' and not e.get('geometry'):
  g=[nodes[n] for n in e.get('nodes',[]) if n in nodes]
  if not g:continue
  e.update(geometry=g,center=dict(lat=sum(p['lat'] for p in g)/len(g),lon=sum(p['lon'] for p in g)/len(g)))
 elements.append(e)
features,skipped=parse_osm(dict(elements=elements))
if len(features)>5000:raise ValueError('More than5000 mapped features; split the snapshot')
sha=hashlib.sha256(raw).hexdigest();out=Path(a.root)/'territorial-imports'/(sha+'.json');out.parent.mkdir(parents=True,exist_ok=True)
value=dict(type='FeatureCollection',features=features,coverage_bbox_wgs84=a.bounds,source_url=a.source_url,source_sha256=sha,license='ODbL-1.0',available_at=utcnow(),source_available_at=a.source_available_at,source_data_at=data.get('osm3s',{}).get('timestamp_osm_base'),missing=['Inventory completeness','Height and sag','Population and occupancy','Unsupported relations'],skipped=skipped)
if len(json.dumps(value).encode())>4*1024**2:raise ValueError('Derived inventory exceeds4MiB; split the extract')
if not out.exists():write_new(out,value)
print(json.dumps(dict(path=str(out),features=len(features),power_lines=sum(f['properties']['category']=='power_line' for f in features),source_sha256=sha)))
