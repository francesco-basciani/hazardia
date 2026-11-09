"""Attach soil/lithology mixtures to geographic support; never infer basal friction."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj')
import pathlib,json,gzip,hashlib,collections
import numpy as np,rasterio
from rasterio.warp import reproject,Resampling
from rasterio.features import rasterize
from rasterio.windows import from_bounds,Window
from shapely.geometry import shape,mapping,Polygon,MultiPolygon
from shapely.ops import unary_union
from shapely.ops import transform
from pyproj import Transformer
r=pathlib.Path('/dev/shm/avalanche-national-ground');context=json.loads(gzip.decompress((r/'terrain-refined.json.gz').read_bytes()));context['metadata']['degenerate_empty_geometries_removed']=sum(shape(f['geometry']).is_empty for f in context['features']);context['features']=[f for f in context['features'] if not shape(f['geometry']).is_empty];soil_legend=json.loads((r/'wrb-legend').read_text());litho_legend=json.loads((r/'lithology-legend.json').read_text())
with rasterio.open(r/'lithology-1km.tif') as ds:litho=ds.read(1);aff=ds.transform;size=ds.shape
soil=np.zeros(size,np.uint8)
with rasterio.open(r/'soil-wrb.tif') as ds:
 assert ds.crs.to_epsg()==4326 and ds.width==1560 and ds.height==1560
 a=ds.read(1);assert set(np.unique(a))<=set(range(30))
 reproject(a,soil,src_transform=ds.transform,src_crs=ds.crs,src_nodata=0,dst_transform=aff,dst_crs=3035,dst_nodata=0,resampling=Resampling.nearest,num_threads=1)
# Zero output is ambiguous with source class0 (Acrisols) and ocean fill in WCS.
# Treat ALL zeros conservatively as unknown, never invent an Acrisol classification.
soil_valid=(soil>0)&(soil<30);litho_valid=(litho>0)&(litho<255)
forward=Transformer.from_crs(4326,3035,always_xy=True).transform;back=Transformer.from_crs(3035,4326,always_xy=True).transform;summary=collections.Counter();kept=[]
original=json.loads(gzip.decompress(pathlib.Path('/dev/shm/avalanche-terrain-build/output/terrain-context-support.json.gz').read_bytes()));original_by_id={f['properties']['id']:f for f in original['features']}
for n,f in enumerate(context['features']):
 p=f['properties']
 if p['terrain_display_m']==30:summary['retained_local_arssa_areas']+=1;kept.append(f);continue
 g=transform(forward,shape(f['geometry']))
 if not g.is_valid:
  repaired=g.buffer(0);assert abs(repaired.area-g.area)<=max(1,abs(g.area)*1e-4);g=repaired;summary['projection_topology_repairs']+=1
 if '-native' in p['id']:
  coarse=transform(forward,shape(original_by_id[p['id'].split('-native')[0]]['geometry']))
  if not coarse.is_valid:coarse=coarse.buffer(0)
  g=g.intersection(coarse)
  if g.is_empty:summary['post_simplification_empty_removed']+=1;continue
  if g.geom_type not in ('Polygon','MultiPolygon'):
   from shapely.ops import unary_union
   g=unary_union([part for part in g.geoms if part.geom_type in ('Polygon','MultiPolygon')])
  if g.is_empty:summary['post_simplification_empty_removed']+=1;continue
  wgs=transform(back,g);parts=list(wgs.geoms) if wgs.geom_type=='MultiPolygon' else [wgs];rounded=[]
  def ring(coords):
   points=[]
   for x,y in coords:
    q=(round(x,6),round(y,6))
    if not points or q!=points[-1]:points.append(q)
   if points and points[-1]!=points[0]:points.append(points[0])
   return points if len(set(points))>=3 and len(points)>=4 else None
  for part in parts:
   exterior=ring(part.exterior.coords)
   if not exterior:continue
   holes=[points for interior in part.interiors if (points:=ring(interior.coords)) and Polygon(points).area>0]
   poly=Polygon(exterior,holes)
   if poly.area<=0:continue
   if not poly.is_valid:poly=poly.buffer(0);summary['quantization_topology_repairs']+=1
   if not poly.is_empty:rounded.append(poly)
  quantized=unary_union(rounded)
  if quantized.is_empty:summary['post_simplification_empty_removed']+=1;continue
  f['geometry']=mapping(quantized);p['area_support_km2']=g.area/1e6
 kept.append(f);w=from_bounds(*g.bounds,transform=aff);row=max(0,int(np.floor(w.row_off)));col=max(0,int(np.floor(w.col_off)));endrow=min(size[0],int(np.ceil(w.row_off+w.height)));endcol=min(size[1],int(np.ceil(w.col_off+w.width)));win=Window(col,row,endcol-col,endrow-row)
 if win.height<=0 or win.width<=0:continue
 mask=rasterize([(mapping(g),1)],out_shape=(int(win.height),int(win.width)),transform=rasterio.windows.transform(win,aff),all_touched=True,fill=0,dtype='uint8').astype(bool);s=soil[row:endrow,col:endcol][mask];l=litho[row:endrow,col:endcol][mask];sv=s[(s>0)&(s<30)];lv=l[(l>0)&(l<255)]
 sc=collections.Counter(map(int,sv));lc=collections.Counter(map(int,lv));soil_names=[soil_legend[str(code)] for code,count in sc.most_common()];litho_names=[litho_legend[str(code)]['label'] for code,count in lc.most_common()]
 sm=int(len(s)-len(sv));lm=int(len(l)-len(lv));complete=bool(sc and lc and sm==0 and lm==0)
 p.update(soil_association='SoilGrids WRB stimato: '+', '.join(soil_names) if sc else None,substrate='ISPRA litologie nel supporto: '+'; '.join(litho_names) if lc else None,soil_source_scale=None,soil_source='ISRIC SoilGrids WRB2017 rerun2022/23, classe più probabile modellata; CC BY4.0',soil_support_m=1000,substrate_source='ISPRA Litologica100k CC BY4.0; semplificazione servizio250m e campioni1km',substrate_source_scale=100000,ground_status='NATIONAL_CARTOGRAPHIC_CONTEXT_AVAILABLE' if complete else 'NATIONAL_GROUND_PARTIAL_OR_MISSING',soil_classes=[dict(code=code,name=soil_legend[str(code)],support_samples=count) for code,count in sc.most_common()],substrate_classes=[dict(code=litho_legend[str(code)]['code'],name=litho_legend[str(code)]['label'],support_samples=count) for code,count in lc.most_common()],soil_missing_samples=sm,substrate_missing_samples=lm,ground_support_samples=len(s),ground_support_meaning='Class mixtures from1km support samples intersecting this area; not the exact soil at every point, not percent area or calibrated confidence',soil_zero_policy='WCS zero ambiguous/ocean fill: unknown, never inferred Acrisols',ground_complete=complete)
 summary['national_areas']+=1;summary['national_soil_present']+=bool(sc);summary['national_substrate_present']+=bool(lc);summary['national_ground_complete']+=complete;summary['national_ground_partial_or_missing']+=not complete
 if n%1000==0:print('combined support',n,flush=True)
summary['soil_valid_1km_cells']=int(soil_valid.sum());summary['lithology_valid_1km_cells']=int(litho_valid.sum());summary['soil_zero_or_missing_1km_cells']=int((~soil_valid).sum());summary['lithology_ambiguous_1km_cells']=int((litho==255).sum())
with rasterio.open('/dev/shm/avalanche-terrain-build/experiments/italy-72h-20261029-01/results/mountain-screening.tif') as ds:eligible=ds.read(1)==1
parents=json.loads(pathlib.Path('/home/hazardia/avalanche-runtime/seed.geojson').read_text());domain=np.zeros(size,bool)
for f in parents['features']:
 q=f['properties'];rr,cc=q['grid_row']*10,q['grid_col']*10;domain[rr:rr+10,cc:cc+10]=True
eligible&=domain
summary.update(eligible_1km_cells=int(eligible.sum()),eligible_soil_known=int((eligible&soil_valid).sum()),eligible_substrate_known=int((eligible&litho_valid).sum()),eligible_both_known=int((eligible&soil_valid&litho_valid).sum()),eligible_soil_missing=int((eligible&~soil_valid).sum()),eligible_substrate_missing=int((eligible&~litho_valid).sum()))
context['features']=kept
meta=context['metadata'];meta['post_simplification_clip']='Clipped again to original eligible support after75m simplification; no extension beyond original coverage'
meta.update(national_ground_summary=dict(summary),ground_coverage='National sources; completeness explicit per support, not all positions guaranteed',national_soil_source='ISRIC SoilGrids WRB2017 rerun2022/23, predicted class sampled1km; CC BY4.0',national_substrate_source='ISPRA Litologica100k; simplified250m, samples1km; CC BY4.0',national_soil_support_m=1000,national_substrate_source_scale=100000,ground_sources_acquired_at=json.loads((r/'ground-ledger.json').read_text())[0]['at'],missing=['Observed stability and weak layers','Basal water and friction','Current grass structure and forest density/height','Local snow drift, true snow depth per slope, runout and exposure','Soil/substrate gaps and ambiguous samples explicitly retained'])
meta['sources']+=['ISRIC SoilGrids WRB2017 rerun2022/23 CC BY4.0','ISPRA Litologica100k CC BY4.0']
raw=json.dumps(context,separators=(',',':'),allow_nan=False).encode();assert len(raw)<=64*1024**2
with gzip.open(r/'terrain-combined.json.gz','wb') as stream:stream.write(raw)
manifest=dict(schema=context['schema'],sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),compressed_bytes=(r/'terrain-combined.json.gz').stat().st_size,features=len(context['features']),metadata=meta,builder_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),terrain_manifest_sha256=hashlib.sha256((r/'terrain-refined-manifest.json').read_bytes()).hexdigest())
(r/'terrain-combined-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(dict(summary),indent=2));print('FINAL BYTES',len(raw),manifest['compressed_bytes'],flush=True)
