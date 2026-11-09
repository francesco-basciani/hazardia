"""Bounded public category acquisition. Linux only; original encoded responses retained."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj')
import pathlib,json,urllib.request,urllib.parse,gzip,hashlib,datetime,time
import numpy as np,rasterio
from rasterio.features import rasterize
from rasterio.enums import MergeAlg
from rasterio.transform import Affine
from shapely.geometry import shape,mapping
r=pathlib.Path('/dev/shm/avalanche-national-ground');r.mkdir(exist_ok=True);ledger=[];used=0;cap=48*1024**2

def get(name,url,limit=8*1024**2):
 global used
 p=r/name
 if p.exists():
  raw=(r/(name+'.http')).read_bytes();used+=len(raw);assert used<=cap
  entry=dict(name=name,url=url,at=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),time_provenance='Retained original decoded-file mtime; source response reused',bytes=len(raw),decoded_bytes=p.stat().st_size,sha256=hashlib.sha256(raw).hexdigest(),content_encoding='gzip' if raw[:2]==b'\x1f\x8b' else 'identity',network_bytes_this_replay=0)
  ledger.append(entry);(r/'ground-ledger.json').write_text(json.dumps(ledger,indent=2));return p.read_bytes()
 entry=dict(name=name,url=url,at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept-Encoding':'gzip'}),timeout=55) as response:
   raw=response.read(min(limit,cap-used)+1);entry['content_encoding']=response.headers.get('Content-Encoding','identity')
  used+=len(raw);assert len(raw)<=limit and used<=cap
  decoded=gzip.decompress(raw) if entry['content_encoding']=='gzip' else raw;assert len(decoded)<=8*1024**2
  (r/(name+'.http')).write_bytes(raw);p.write_bytes(decoded);entry.update(bytes=len(raw),decoded_bytes=len(decoded),sha256=hashlib.sha256(raw).hexdigest());print(name,len(raw),len(decoded),flush=True);return decoded
 except Exception as e:entry['error']=str(e);raise
 finally:ledger.append(entry);(r/'ground-ledger.json').write_text(json.dumps(ledger,indent=2))
params=[('map','/map/wrb.map'),('SERVICE','WCS'),('VERSION','2.0.1'),('REQUEST','GetCoverage'),('COVERAGEID','MostProbable'),('FORMAT','image/tiff'),('SUBSET','lat(35,48)'),('SUBSET','long(6,19)'),('SCALESIZE','long(1560),lat(1560)')]
try:get('soil-wrb.tif','https://maps.isric.org/mapserv?'+urllib.parse.urlencode(params))
except Exception as e:print('SOIL ERROR',repr(e),flush=True)
service=json.loads((r/'lithology-service').read_text());labels={a['value']:a['label'] for a in service['drawingInfo']['renderer']['uniqueValueInfos']};codes={code:i+1 for i,code in enumerate(sorted(labels))};(r/'lithology-legend.json').write_text(json.dumps({str(v):dict(code=k,label=labels[k]) for k,v in codes.items()},indent=2))
base='/dev/shm/avalanche-terrain-build/experiments/italy-72h-20261029-01/results/mountain-screening.tif'
with rasterio.open(base) as ds:aff=ds.transform;size=ds.shape
litho=np.zeros(size,np.uint8);ambiguity=np.zeros(size,bool);total=json.loads((r/'lithology-count.json').read_text())['count'];seen=set();nulls=0;rows_seen=0;duplicate_ids=0;row_keys=set();duplicate_rows=0
for offset in range(0,total,2000):
 params=dict(f='json',where='1=1',outFields='cod_lito,SHAPE.fid',returnGeometry='true',outSR=3035,maxAllowableOffset=250,geometryPrecision=0,resultOffset=offset,resultRecordCount=2000,orderByFields='SHAPE.fid ASC')
 url='https://sinacloud.isprambiente.it/arcgisgeo/rest/services/geo/SGI_ISPRA_Litologica100k/MapServer/1/query?'+urllib.parse.urlencode(params)
 try:
  raw=get('lithology-'+str(offset).zfill(6)+'.json',url);d=json.loads(raw);assert 'features' in d,d;assert len(d['features'])==min(2000,total-offset);rows_seen+=len(d['features'])
  geoms=[]
  for f in d['features']:
   a=f['attributes'];ident=a['SHAPE.fid'];duplicate_ids+=ident in seen;seen.add(ident);row_key=hashlib.sha256(json.dumps(f,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   if row_key in row_keys:duplicate_rows+=1;continue
   row_keys.add(row_key);code=codes.get(a['cod_lito']);rings=(f.get('geometry') or {}).get('rings')
   if not code or not rings:nulls+=1;continue
   # ArcGIS rings have clockwise exteriors, opposite oriented holes.
   from shapely.geometry import Polygon
   ex=[];holes=[]
   for ring in rings:
    poly=Polygon(ring)
    if not poly.is_valid:poly=poly.buffer(0)
    if poly.is_empty:continue
    if not Polygon(ring).exterior.is_ccw:ex.append(poly)
    else:holes.append(poly)
   from shapely.ops import unary_union
   g=unary_union(ex)
   if holes:g=g.difference(unary_union(holes))
   if not g.is_empty:geoms.append((mapping(g),code))
  if geoms:
   page=rasterize(geoms,out_shape=size,transform=aff,fill=0,dtype='uint8')
   overlaps=rasterize([(g,1) for g,c in geoms],out_shape=size,transform=aff,fill=0,dtype='uint16',merge_alg=MergeAlg.add)>1
   ambiguity|=overlaps
   ambiguity|=(page>0)&(litho>0)&(page!=litho);litho[(page>0)&(litho==0)]=page[(page>0)&(litho==0)]
  if not d.get('exceededTransferLimit') and rows_seen<total:raise ValueError('Unexpected incomplete page')
 except Exception as e:
  print('LITHOLOGY ERROR',offset,repr(e),flush=True);break
 time.sleep(.15)
print('lithology records',len(seen),'/',total,'rows',rows_seen,'nulls',nulls,'bytes',used,flush=True)
# Uncertain overlaps are explicitly unknown, never resolved by arbitrary response order.
litho[ambiguity]=255
with rasterio.open(r/'lithology-1km.tif','w',driver='GTiff',height=size[0],width=size[1],count=1,dtype='uint8',crs=3035,transform=aff,nodata=0,compress='deflate') as ds:ds.write(litho,1)
(r/'ground-acquisition-summary.json').write_text(json.dumps(dict(total_source_records=total,acquired_records=rows_seen,unique_source_ids=len(seen),duplicate_id_rows=duplicate_ids,exact_duplicate_rows=duplicate_rows,null_or_unmapped_records=nulls,complete=rows_seen==total,ambiguous_1km_cells=int(ambiguity.sum()),payload_bytes=used,soil_source='ISRIC SoilGrids WRB, categories from2017 rerun2022/23',lithology_source='ISPRA100k CC BY4.0; simplified250m by service, centre-sampled1km, not local contact'),indent=2))
