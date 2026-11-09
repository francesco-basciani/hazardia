"""Replace filled1km max-slope supports with native90m-derived200m masks, Linux only."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj')
import pathlib,json,gzip,hashlib,collections,resource,time
import numpy as np,rasterio
from rasterio.warp import reproject,Resampling
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.geometry import shape,mapping
from shapely.ops import transform,unary_union
from pyproj import Transformer,Geod
resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
r=pathlib.Path('/dev/shm/avalanche-terrain-build');out=pathlib.Path('/dev/shm/avalanche-national-ground');base=r/'experiments/italy-72h-20261029-01'
context=json.loads(gzip.decompress((r/'output/terrain-context-support.json.gz').read_bytes()));seed=json.loads(pathlib.Path('/home/hazardia/avalanche-runtime/seed.geojson').read_text());parents={f['properties']['id']:f['properties'] for f in seed['features']}
with rasterio.open(base/'results/mountain-screening.tif') as ds:aff=ds.transform*Affine.scale(.2,.2);size=(ds.height*5,ds.width*5)
slope=np.full(size,np.nan,np.float32);geod=Geod(ellps='WGS84')
for n,tile in enumerate(json.loads((base/'manifests/dem-tiles.json').read_text())):
 with rasterio.open(r/tile['path']) as ds:
  a=ds.read(1).astype(np.float32);a[a==ds.nodata]=np.nan;lat=ds.transform.f+(np.arange(ds.height)+.5)*ds.transform.e;lon=np.zeros_like(lat)+ds.transform.c
  dx=np.asarray(geod.inv(lon,lat,lon+2*ds.transform.a,lat)[2]);dy=np.asarray(geod.inv(lon,lat+ds.transform.e,lon,lat-ds.transform.e)[2]);native=np.full(a.shape,np.nan,np.float32)
  native[1:-1,1:-1]=np.degrees(np.arctan(np.hypot((a[1:-1,2:]-a[1:-1,:-2])/dx[1:-1,None],(a[:-2,1:-1]-a[2:,1:-1])/dy[1:-1,None])))
  reproject(native,slope,src_transform=ds.transform,src_crs=ds.crs,src_nodata=np.nan,dst_transform=aff,dst_crs=3035,dst_nodata=np.nan,init_dest_nodata=False,resampling=Resampling.average,num_threads=1)
 if n%10==0:print('native terrain',n+1,flush=True)
forward=Transformer.from_crs(4326,3035,always_xy=True).transform;back=Transformer.from_crs(3035,4326,always_xy=True).transform
features=[];stats=collections.Counter();started=time.time()
for n,f in enumerate(context['features']):
 p=f['properties']
 if p['terrain_display_m']!=1000 or p['terrain_steep'] is not True:features.append(f);continue
 parent=parents[p['model_sample_id']];row,col=parent['grid_row']*50,parent['grid_col']*50;v=slope[row:row+50,col:col+50];labels=np.where(np.isfinite(v),(v>=30).astype(np.uint8),2).astype(np.uint8);tr=aff*Affine.translation(col,row);coarse=transform(forward,shape(f['geometry']));groups=collections.defaultdict(list)
 for geo,label in shapes(labels,transform=tr):groups[int(label)].append(shape(geo))
 for label,geoms in groups.items():
  geom=unary_union(geoms).intersection(coarse).simplify(75,preserve_topology=True)
  if geom.is_empty:continue
  if geom.geom_type not in ('Polygon','MultiPolygon'):geom=unary_union([g for g in geom.geoms if g.geom_type in ('Polygon','MultiPolygon')])
  if geom.is_empty:continue
  coords=transform(back,geom);coords=transform(lambda x,y,z=None:(np.round(x,6),np.round(y,6)),coords)
  if not coords.is_valid:coords=coords.buffer(0)
  props=dict(p);props.update(id=p['id']+'-native'+str(label),terrain_steep=None if label==2 else bool(label),terrain_display_m=200,terrain_native_m=90,terrain_meaning='Native90m slope averaged200m, contour simplification<=75m; not release boundary or snow forecast200m',area_support_km2=geom.area/1e6)
  if label!=1:props['slope_max_deg']=None
  features.append(dict(type='Feature',geometry=mapping(coords),properties=props));stats[label]+=1
 if n%300==0:print('contours',n,len(features),'elapsed',int(time.time()-started),flush=True)
context['features']=features;context['metadata'].update(national_grid_m=200,national_native_slope_m=90,national_geometry_method='Native90m slope averaged200m>=30; simplified75m; coarse1km supports no longer filled as hazard footprints',national_geometry_is_release_boundary=False,geometry_refinement_counts=dict(stats))
raw=json.dumps(context,separators=(',',':'),allow_nan=False).encode();print('raw bytes',len(raw),flush=True);assert len(raw)<=64*1024**2
with gzip.open(out/'terrain-refined.json.gz','wb') as stream:stream.write(raw)
manifest=dict(schema=context['schema'],sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),features=len(features),compressed_bytes=(out/'terrain-refined.json.gz').stat().st_size,metadata=context['metadata'],builder_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
(out/'terrain-refined-manifest.json').write_text(json.dumps(manifest,indent=2));print({k:v for k,v in manifest.items() if k!='metadata'},flush=True)
