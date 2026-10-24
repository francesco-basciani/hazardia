"""Acquire official Istat regions and build display-only WGS84 context in Linux VM."""
import argparse,datetime as dt,hashlib,json,platform,urllib.request,zipfile
from pathlib import Path
URL='https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/2026/Limiti01012026_g.zip'
EXPECTED='b011a590656c3a3ebc297fba80726a376aa843b6f164641cf6a4a990021a81d6'

def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);a=p.parse_args()
 if platform.system()!='Linux':raise SystemExit('Run only in the Linux VM')
 import fiona
 from shapely.geometry import shape,mapping
 from shapely.ops import transform
 from pyproj import Transformer
 r=Path(a.runtime);cache=r/'downloads/istat-regions2026';cache.mkdir(parents=True,exist_ok=True);archive=cache/'Limiti01012026_g.zip';cap=16*1024**2
 if not archive.exists():
  with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'HAZARDIA-local-research/0.1'}),timeout=30) as response:
   if int(response.headers.get('Content-Length',0))>cap:raise RuntimeError('Source exceeds16MiB download cap')
   data=response.read(cap+1)
   if len(data)>cap:raise RuntimeError('Source exceeds16MiB download cap')
  archive.write_bytes(data)
 digest=hashlib.sha256(archive.read_bytes()).hexdigest()
 if EXPECTED and digest!=EXPECTED:raise RuntimeError('Source archive hash changed; review source revision')
 receipt=cache/'receipt.json'
 if not receipt.exists():receipt.write_text(json.dumps(dict(url=URL,sha256=digest,bytes=archive.stat().st_size,available_at=dt.datetime.now(dt.timezone.utc).isoformat(),reference_date='2026-01-01',license='CC-BY-4.0',license_url='https://www.istat.it/note-legali/'),indent=2))
 source=json.loads(receipt.read_text());assert source['sha256']==digest
 with zipfile.ZipFile(archive) as z:
  names=[n for n in z.namelist() if Path(n).name.startswith('Reg01012026_g_WGS84.')]
  if not names or sum(z.getinfo(n).file_size for n in names)>8*1024**2:raise RuntimeError('Missing/oversized region shapefile')
  for n in names:(cache/Path(n).name).write_bytes(z.read(n))
 # The pinned Istat DBF stores UTF-8 without a CPG sidecar. GDAL's default
 # fallback misreads accented bilingual names as Latin-1.
 with fiona.open(cache/'Reg01012026_g_WGS84.shp',encoding='UTF-8') as src:
  print('SOURCE',src.crs,dict(src.schema));project=Transformer.from_crs(src.crs,'EPSG:4326',always_xy=True).transform;features=[]
  for f in src:
   props=dict(f['properties']);g=shape(f['geometry'])
   if g.is_empty or not g.is_valid:raise RuntimeError('Invalid source region geometry')
   label=transform(project,g.representative_point());geo=transform(project,g)
   if not geo.is_valid:raise RuntimeError('Invalid projected region')
   features.append(dict(type='Feature',properties=dict(code=str(int(props['COD_REG'])),name=props['DEN_REG'],label_point=[label.y,label.x]),geometry=mapping(geo)))
 if len(features)!=20 or {f['properties']['code'] for f in features}!={str(i) for i in range(1,21)}:raise RuntimeError('Expected all20Italian regions')
 output=dict(type='FeatureCollection',features=features,metadata=dict(source=source,territory='italy',meaning='Administrative boundaries for statistical purposes; generalized source; display only, no jurisdiction/dispatch inference',attribution='© Istat · Confini amministrativi2026 · CC BY4.0',source_text_encoding='UTF-8'))
 dest=r/'web-assets/administrative-regions.json';data=json.dumps(output,ensure_ascii=False,separators=(',',':')).encode()
 if len(data)>4*1024**2:raise RuntimeError('Display asset exceeds4MiB')
 dest.write_bytes(data);result=dict(status='PASS',regions=20,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),source=source,source_crs=str(src.crs),output_crs='EPSG:4326',fiona=fiona.__version__)
 (cache/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
