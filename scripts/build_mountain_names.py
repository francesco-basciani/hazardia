"""VM-only cartographic extraction from the already acquired GeoNames IT archive."""
import collections,datetime,hashlib,json,math,pathlib,sys,zipfile
if sys.platform!='linux':raise RuntimeError('Run in the VM')
root=pathlib.Path('/home/hazardia/hazardia-runtime');src=root/'runs/map-detail-20261015T204352Z/geonames-IT.zip';out=root/'runs/mountain-names-20261030';out.mkdir(exist_ok=False)
codes={'MT','MTS','PK','PKS','VLC','PASS','SDL','GAP','RDGE'};features=[]
with zipfile.ZipFile(src) as z:
 for line in z.open('IT.txt'):
  r=line.decode('utf-8').rstrip('\n').split('\t')
  if len(r)!=19 or r[6]!='T' or r[7] not in codes or r[8]!='IT':continue
  lat,lon=float(r[4]),float(r[5]);assert math.isfinite(lat+lon) and -90<=lat<=90 and -180<=lon<=180
  elev=float(r[15]) if r[15] else None
  features.append(dict(id=r[0],name=r[1],lat=lat,lon=lon,code=r[7],elevation=elev,modified=r[18]))
assert len({f['id'] for f in features})==len(features) and len(features)>6000
features.sort(key=lambda f:int(f['id']))
data=dict(schema='hazardia-mountain-names/1',country='IT',source='https://download.geonames.org/export/dump/IT.zip',license='CC BY 4.0',attribution='GeoNames',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),built_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),qualification='GAZETTEER_POINTS_NOT_SURVEYED_SUMMITS; source elevation only used for display ranking; no DEM value substituted',features=features)
raw=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode();assert len(raw)<2*1024*1024
(out/'mountain-names.json').write_bytes(raw);(root/'web-assets/mountain-names.json').write_bytes(raw)
receipt=dict(features=len(features),by_code=dict(collections.Counter(f['code'] for f in features)),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),source_sha256=data['source_sha256'],no_new_download=True)
(out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
