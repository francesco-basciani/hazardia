"""Display-only country/province context. Run in existing Linux geospatial VM env."""
import argparse,datetime as dt,hashlib,json,platform,urllib.request,zipfile
from pathlib import Path
COUNTRIES='https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip'
ISTAT_SHA='b011a590656c3a3ebc297fba80726a376aa843b6f164641cf6a4a990021a81d6'
COUNTRY_SHA='5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139'

def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);a=p.parse_args()
 if platform.system()!='Linux':raise SystemExit('Run in Linux VM only')
 import fiona
 from shapely.geometry import shape,mapping
 from shapely.ops import transform
 from pyproj import Transformer
 r=Path(a.runtime);cache=r/'downloads/administrative-levels';cache.mkdir(exist_ok=True);out=r/'web-assets';results=[]
 nation=cache/'ne_50m_admin_0_countries.zip'
 if not nation.exists():
  with urllib.request.urlopen(urllib.request.Request(COUNTRIES,headers={'User-Agent':'HAZARDIA research/1'}),timeout=30) as response:raw=response.read(2*1024**2+1)
  if len(raw)>2*1024**2:raise ValueError('Country download exceeds2MiB')
  nation.write_bytes(raw)
 digest=hashlib.sha256(nation.read_bytes()).hexdigest()
 if COUNTRY_SHA and digest!=COUNTRY_SHA:raise ValueError('Natural Earth revision changed; review checksum')
 for kind,archive,stem,expected in [('countries',nation,'ne_50m_admin_0_countries',digest),('provinces',r/'downloads/istat-regions2026/Limiti01012026_g.zip','ProvCM01012026_g_WGS84',ISTAT_SHA)]:
  assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
  dest=cache/kind;dest.mkdir(exist_ok=True)
  with zipfile.ZipFile(archive) as z:
   names=[n for n in z.namelist() if Path(n).stem==stem and Path(n).suffix in ['.shp','.shx','.dbf','.prj','.cpg']]
   if not names or sum(z.getinfo(n).file_size for n in names)>16*1024**2:raise ValueError('Invalid/oversized shapefile')
   for n in names:(dest/Path(n).name).write_bytes(z.read(n))
  features=[]
  with fiona.open(dest/(stem+'.shp'),encoding='UTF-8') as source:
   project=Transformer.from_crs(source.crs,'EPSG:4326',always_xy=True).transform
   for f in source:
    props=dict(f['properties']);g=shape(f['geometry'])
    if g.is_empty or not g.is_valid:raise ValueError('Invalid source geometry; no silent repair')
    geo=transform(project,g);label=geo.representative_point()
    if not geo.is_valid:raise ValueError('Invalid projected geometry')
    name=props.get('NAME_IT') or props.get('ADMIN') if kind=='countries' else props['DEN_UTS']
    code=props['ADM0_A3'] if kind=='countries' else str(props['COD_UTS'])
    def rounded(coords):return [round(v,6 if kind=='countries' else 7) if isinstance(v,(int,float)) else rounded(v) for v in coords]
    geometry=mapping(geo);geometry['coordinates']=rounded(geometry['coordinates'])
    if not shape(geometry).is_valid:raise ValueError('Coordinate quantization invalidated geometry')
    features.append(dict(type='Feature',properties=dict(name=name,code=code,label_point=[round(label.y,6),round(label.x,6)]),geometry=geometry))
  if kind=='provinces':
   assert len(features)==110 and len({f['properties']['code'] for f in features})==110
   assert {'L’Aquila','Teramo','Pescara','Chieti'} <= {f['properties']['name'] for f in features} or {"L'Aquila",'Teramo','Pescara','Chieti'} <= {f['properties']['name'] for f in features}
  else:assert 200<=len(features)<=300 and {'Senegal','Italia'} <= {f['properties']['name'] for f in features}
  metadata=dict(attribution='Made with Natural Earth · public domain · 1:50m · v5.1.1' if kind=='countries' else '© Istat · confini2026 · CC BY4.0 · province/città metropolitane',source=COUNTRIES if kind=='countries' else 'https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/2026/Limiti01012026_g.zip',source_sha256=expected,coverage='world' if kind=='countries' else 'Italy',meaning='Generalized display context only; not hazard/operational or legal jurisdiction input',available_at=dt.datetime.now(dt.timezone.utc).isoformat())
  raw=json.dumps(dict(type='FeatureCollection',features=features,metadata=metadata),ensure_ascii=False,separators=(',',':')).encode()
  if len(raw)>4*1024**2:raise ValueError('Asset exceeds4MiB')
  (out/('administrative-'+kind+'.json')).write_bytes(raw)
  results.append(dict(level=kind,features=len(features),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),metadata=metadata))
 result=dict(status='PASS',levels=results,new_download_bytes=nation.stat().st_size)
 (cache/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
