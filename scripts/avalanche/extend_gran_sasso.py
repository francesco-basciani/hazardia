"""Extend real30m terrain around Gran Sasso; frozen physical forecasts are unchanged."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj',MPLCONFIGDIR='/dev/shm/avalanche-gran-sasso-detail/mpl')
import pathlib,json,gzip,hashlib,math,collections,datetime,resource
import numpy as np,rasterio
from rasterio.warp import reproject,Resampling
from rasterio.transform import Affine
from rasterio.windows import from_bounds,Window
from rasterio.features import shapes,rasterize
from shapely.geometry import shape,mapping,box,Polygon,MultiPolygon,GeometryCollection
from shapely.ops import transform,unary_union
from pyproj import Transformer
from slope_contours import filled_slope_contours
resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
r=pathlib.Path('/dev/shm/avalanche-gran-sasso-detail');runtime=pathlib.Path.home()/'hazardia-runtime';source=pathlib.Path('/dev/shm/copdem-N42E013.tif');assert hashlib.sha256(source.read_bytes()).hexdigest()=='ce66eaaa51ec82ab45533544cd49be663deb9bfd2f0a42ccd9a64a1a10a83a79'
manifest=json.loads((runtime/'avalanche/terrain-manifest.json').read_text());raw=gzip.decompress((runtime/'avalanche'/manifest['file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==manifest['sha256'];context=json.loads(raw);(r/'before-manifest.json').write_text(json.dumps(manifest,indent=2));(r/'before-context.json.gz').write_bytes(gzip.compress(raw))
aoi=box(13.38,42.28,13.92,42.65);oldbox=box(13.49,42.4,13.64,42.52);forward=Transformer.from_crs(4326,32633,always_xy=True).transform;back=Transformer.from_crs(32633,4326,always_xy=True).transform;gridforward=Transformer.from_crs(4326,3035,always_xy=True).transform
left,bottom,right,top=transform(forward,aoi).bounds;left=math.floor((left-120)/30)*30;top=math.ceil((top+120)/30)*30;width=math.ceil((right+120-left)/30);height=math.ceil((top-bottom+120)/30);aff=Affine(30,0,left,0,-30,top);z=np.full((height,width),np.nan,np.float32)
with rasterio.open(source) as ds:reproject(rasterio.band(ds,1),z,src_nodata=ds.nodata,dst_transform=aff,dst_crs=32633,dst_nodata=np.nan,resampling=Resampling.bilinear,num_threads=1)
gy,gx=np.gradient(z,30,30);slope=np.degrees(np.arctan(np.hypot(gx,gy)));slope[[0,-1],:]=np.nan;slope[:,[0,-1]]=np.nan
for name,a in [('elevation',z),('slope',slope)]:
 with rasterio.open(r/(name+'-30m.tif'),'w',driver='GTiff',height=height,width=width,count=1,dtype='float32',crs=32633,transform=aff,nodata=np.nan,compress='deflate') as ds:ds.write(a,1)
print('GRID',height,width,'valid',int(np.isfinite(slope).sum()),flush=True)
steep=filled_slope_contours(slope,aff,30,3);print('CONTOURS',steep.geom_type,steep.area/1e6,flush=True)
valid=unary_union([shape(g) for g,v in shapes(np.isfinite(slope).astype(np.uint8),mask=np.isfinite(slope),transform=aff)])
seed=json.loads((pathlib.Path.home()/'avalanche-runtime/seed.geojson').read_text());parents={f['properties']['id']:f for f in seed['features']}
# Keep the original operational relief support rather than broadening lowland coverage.
mountpath=pathlib.Path('/dev/shm/avalanche-terrain-build/experiments/italy-72h-20261029-01/results/mountain-screening.tif')
with rasterio.open(mountpath) as ds:
 b=transform(gridforward,aoi).bounds;w=from_bounds(*b,transform=ds.transform).round_offsets().round_lengths();arr=ds.read(1,window=w);tr=ds.window_transform(w);relief=unary_union([shape(g) for g,v in shapes(arr,mask=arr==1,transform=tr)])
relief_wgs=transform(Transformer.from_crs(3035,4326,always_xy=True).transform,relief)
base=pathlib.Path('/dev/shm/avalanche-national-ground');soillegend=json.loads((base/'wrb-legend').read_text());litholegend=json.loads((base/'lithology-legend.json').read_text())
with rasterio.open(base/'lithology-1km.tif') as ds:litho=ds.read(1);gaff=ds.transform;gsize=ds.shape
soil=np.zeros(gsize,np.uint8)
with rasterio.open(base/'soil-wrb.tif') as ds:reproject(ds.read(1),soil,src_transform=ds.transform,src_crs=ds.crs,src_nodata=0,dst_transform=gaff,dst_crs=3035,dst_nodata=0,resampling=Resampling.nearest,num_threads=1)

def polygon_only(g):
 if not g.is_valid:g=g.buffer(0)
 if g.geom_type in ('Polygon','MultiPolygon'):return g
 return unary_union([p for p in g.geoms if p.geom_type in ('Polygon','MultiPolygon')]) if hasattr(g,'geoms') else GeometryCollection()

def ground(p,g):
 gg=transform(gridforward,g);w=from_bounds(*gg.bounds,transform=gaff);row=max(0,math.floor(w.row_off));col=max(0,math.floor(w.col_off));er=min(gsize[0],math.ceil(w.row_off+w.height));ec=min(gsize[1],math.ceil(w.col_off+w.width));win=Window(col,row,ec-col,er-row);mask=rasterize([(mapping(gg),1)],out_shape=(er-row,ec-col),transform=rasterio.windows.transform(win,gaff),all_touched=True,dtype='uint8').astype(bool);s=soil[row:er,col:ec][mask];l=litho[row:er,col:ec][mask];sc=collections.Counter(map(int,s[(s>0)&(s<30)]));lc=collections.Counter(map(int,l[(l>0)&(l<255)]));sm=len(s)-sum(sc.values());lm=len(l)-sum(lc.values());complete=bool(sc and lc and sm==0 and lm==0)
 p.update(soil_association='SoilGrids WRB stimato: '+', '.join(soillegend[str(c)] for c,n in sc.most_common()) if sc else None,substrate='ISPRA litologie nel supporto: '+'; '.join(litholegend[str(c)]['label'] for c,n in lc.most_common()) if lc else None,soil_classes=[dict(code=c,name=soillegend[str(c)],support_samples=n) for c,n in sc.most_common()],substrate_classes=[dict(code=litholegend[str(c)]['code'],name=litholegend[str(c)]['label'],support_samples=n) for c,n in lc.most_common()],soil_missing_samples=sm,substrate_missing_samples=lm,ground_support_samples=len(s),ground_complete=complete,ground_status='NATIONAL_CARTOGRAPHIC_CONTEXT_AVAILABLE' if complete else 'NATIONAL_GROUND_PARTIAL_OR_MISSING',soil_support_m=1000)

features=[];templates={};preserved_inner=0
for f in context['features']:
 p=f['properties'];geom=shape(f['geometry'])
 if p['terrain_display_m']==30:
  features.append(f);preserved_inner+=1;continue
 templates.setdefault(p['model_sample_id'],p)
 outside=polygon_only(geom.difference(aoi)) if geom.intersects(aoi) else geom
 if not outside.is_empty:features.append(dict(type='Feature',geometry=mapping(outside),properties=dict(p)))
print('PRESERVED INNER',preserved_inner,'OUTSIDE',len(features),flush=True)
new=[]
for ident,parent in parents.items():
 domain_wgs=shape(parent['geometry']).intersection(aoi).intersection(relief_wgs).difference(oldbox)
 if domain_wgs.is_empty:continue
 domain=polygon_only(transform(forward,domain_wgs));known=domain.intersection(valid);parts=[('steep',True,known.intersection(steep)),('other',False,known.difference(steep)),('unknown',None,domain.difference(valid))]
 for tag,issteep,g in parts:
  g=polygon_only(g)
  if g.is_empty or g.area<.01:continue
  geowgs=polygon_only(transform(back,g).intersection(domain_wgs))
  if geowgs.is_empty:continue
  p=dict(templates[ident]);p.update(id='GS30-'+ident+'-'+tag,model_sample_id=ident,terrain_steep=issteep,terrain_native_m=30,terrain_display_m=30,gran_sasso_extended=True,terrain_meaning='GLO30 DSM to30m UTM, continuous30deg slope contour with linear interpolation; simplify3m; not snow precision or release boundary',area_support_km2=g.area/1e6,local_sample_id=None,local_profile_status=None)
  w=from_bounds(*g.bounds,transform=aff);rr=max(0,math.floor(w.row_off));cc=max(0,math.floor(w.col_off));er=min(height,math.ceil(w.row_off+w.height));ec=min(width,math.ceil(w.col_off+w.width));win=Window(cc,rr,ec-cc,er-rr);mask=rasterize([(mapping(g),1)],out_shape=(er-rr,ec-cc),transform=rasterio.windows.transform(win,aff),all_touched=False,dtype='uint8').astype(bool);ss=slope[rr:er,cc:ec][mask];zz=z[rr:er,cc:ec][mask];ss=ss[np.isfinite(ss)];zz=zz[np.isfinite(zz)]
  p.update(slope_min_deg=float(ss.min()) if len(ss) else None,slope_max_deg=float(ss.max()) if len(ss) else None,elevation_min_m=float(zz.min()) if len(zz) else None,elevation_max_m=float(zz.max()) if len(zz) else None)
  # Recompute source mixtures for this new support; do not inherit a larger unit's class.
  ground(p,geowgs);new.append(dict(type='Feature',geometry=mapping(geowgs),properties=p))
 print('DETAILED',ident,flush=True)
context['features']=features+new;meta=context['metadata'];meta.update(gran_sasso_detail_bbox=[13.38,42.28,13.92,42.65],gran_sasso_original_soil_bbox=[13.49,42.4,13.64,42.52],gran_sasso_extended_feature_count=len(new),gran_sasso_preserved_inner_features=preserved_inner,gran_sasso_detail_area_km2=transform(forward,aoi).area/1e6,gran_sasso_contour_method='Actual30m slope, linear filled30deg contour, simplify3m; original inner30m units preserved',gran_sasso_dem_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),gran_sasso_derived_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),gran_sasso_external_cover_support_m=1000,gran_sasso_missing_geometry='Separate uncertainty overlay, not filled potential',gran_sasso_extended_local_profiles=False)
summary=meta['national_ground_summary'];national=[f['properties'] for f in context['features'] if f['properties'].get('soil_support_m')]
summary.update(national_areas=len(national),national_soil_present=sum(bool(p.get('soil_association')) for p in national),national_substrate_present=sum(bool(p.get('substrate')) for p in national),national_ground_complete=sum(p.get('ground_status')=='NATIONAL_CARTOGRAPHIC_CONTEXT_AVAILABLE' for p in national),national_ground_partial_or_missing=sum(p.get('ground_status')!='NATIONAL_CARTOGRAPHIC_CONTEXT_AVAILABLE' for p in national))
raw=json.dumps(context,separators=(',',':'),allow_nan=False).encode();assert len(raw)<=64*1024**2
with gzip.open(r/'terrain-context.json.gz','wb') as stream:stream.write(raw)
manifest=dict(schema=context['schema'],sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),compressed_bytes=(r/'terrain-context.json.gz').stat().st_size,features=len(context['features']),metadata=meta,parent_context_sha256=manifest['sha256'],builder_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),contour_module_sha256=hashlib.sha256((r/'slope_contours.py').read_bytes()).hexdigest())
(r/'terrain-manifest.json').write_text(json.dumps(manifest,indent=2));print('FINAL',len(features),len(new),len(raw),manifest['compressed_bytes'],flush=True)
