"""Indicative terrain support, computed only in Linux; no release probability."""
import argparse,collections,datetime,gzip,hashlib,json,math,os,pathlib,resource,re
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj')
import numpy as np,rasterio
from rasterio.warp import reproject,Resampling
from rasterio.features import shapes
from rasterio.transform import Affine
from pyproj import Transformer,Geod
from shapely.geometry import shape,mapping,box
from shapely.ops import transform,unary_union
from scipy import ndimage
from hazardia.ingest.range_cache import RangeCache


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--output',required=True);args=ap.parse_args();root=pathlib.Path(args.root);output=pathlib.Path(args.output);output.mkdir(exist_ok=True)
 resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
 base=root/'experiments/italy-72h-20261029-01';seed=json.loads(pathlib.Path('/home/hazardia/avalanche-runtime/seed.geojson').read_text());parents={f['properties']['id']:f['properties'] for f in seed['features']};parentids=list(parents);parentindex={p:i+1 for i,p in enumerate(parentids)}
 with rasterio.open(base/'results/mountain-screening.tif') as ds:mount=ds.read(1)==1;aff=ds.transform;gridshape=ds.shape
 with rasterio.open(base/'results/elevation-1km.tif') as ds:z=ds.read(1)
 slope=np.full(gridshape,np.nan,dtype=np.float32);cover=np.zeros(gridshape,dtype=np.uint8);parent=np.zeros(gridshape,dtype=np.int32)
 for ident,p in parents.items():
  r,c=p['grid_row']*10,p['grid_col']*10;parent[r:r+10,c:c+10]=parentindex[ident]
 geod=Geod(ellps='WGS84');input_hashes={};tiles=json.loads((base/'manifests/dem-tiles.json').read_text())
 for n,tile in enumerate(tiles):
  path=root/tile['path'];input_hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
  with rasterio.open(path) as ds:
   a=ds.read(1).astype(np.float32);a[a==ds.nodata]=np.nan
   lat=ds.transform.f+(np.arange(ds.height)+.5)*ds.transform.e;lon=np.zeros_like(lat)+ds.transform.c;dx=np.asarray(geod.inv(lon,lat,lon+2*ds.transform.a,lat)[2]);dy=np.asarray(geod.inv(lon,lat+ds.transform.e,lon,lat-ds.transform.e)[2]);native=np.full(a.shape,np.nan,np.float32)
   gx=(a[1:-1,2:]-a[1:-1,:-2])/dx[1:-1,None];gy=(a[:-2,1:-1]-a[2:,1:-1])/dy[1:-1,None];native[1:-1,1:-1]=np.degrees(np.arctan(np.hypot(gx,gy)))
   reproject(native,slope,src_transform=ds.transform,src_crs=ds.crs,src_nodata=np.nan,dst_transform=aff,dst_crs=3035,dst_nodata=np.nan,init_dest_nodata=False,resampling=Resampling.max,num_threads=1)
  if n%10==0:print('DEM',n+1,'/',len(tiles),flush=True)
 # Sparse COG overview reads bounded by existing exact-Range gateway, scratch in RAM.
 gateway=RangeCache(root/'range-cache',cap=48*1024**2).start();cover_sources=[];cover_errors=[]
 try:
  with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_MULTIRANGE='NO',GDAL_HTTP_MAX_RETRY='0',GDAL_CACHEMAX=64):
   locations=sorted({(math.floor(p['lat']/3)*3,math.floor(p['lon']/3)*3) for p in parents.values()})
   for n,(lat,lon) in enumerate(locations):
    tag=f'N{lat:02d}E{lon:03d}';url=f'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tag}_Map.tif'
    try:
     with rasterio.open(gateway.local(url)) as ds:
      # Context sample from categorical overview; never claim native10m precision nationally.
      factor=64;h=math.ceil(ds.height/factor);w=math.ceil(ds.width/factor);a=ds.read(1,out_shape=(h,w),resampling=Resampling.nearest);valid=set(np.unique(a))<=set([0,10,20,30,40,50,60,70,80,90,95,100])
      if not valid:raise ValueError('Noncategorical overview; no vegetation inferred')
      reproject(a,cover,src_transform=ds.transform*Affine.scale(ds.width/w,ds.height/h),src_crs=ds.crs,src_nodata=0,dst_transform=aff,dst_crs=3035,dst_nodata=0,init_dest_nodata=False,resampling=Resampling.mode,num_threads=1)
      cover_sources.append(dict(url=url,overview_factor=factor,overview_factors_available=ds.overviews(1),interpretation='coarse categorical overview sampled and resampled mode to1km, not a local10m observation'))
    except Exception as exc:cover_errors.append(dict(url=url,error=str(exc)))
    print('COVER',n+1,'/',len(locations),'bytes',gateway.bytes,flush=True)
 finally:gateway.close()
 known=mount&(parent>0);native_known=np.isfinite(slope);steep=slope>=30;state=np.where(native_known,steep.astype(np.int32),2);labels=parent*3+state;labels[~known]=0
 country_json=json.loads((base/'downloads/italy-boundary.geojson').read_text());country=unary_union([shape(f['geometry']) for f in country_json['features']]);to_grid=Transformer.from_crs(4326,3035,always_xy=True).transform;back=Transformer.from_crs(3035,4326,always_xy=True).transform;country_grid=transform(to_grid,country);gs_bbox=box(13.49,42.4,13.64,42.52);gs_grid=transform(to_grid,gs_bbox)
 groups=collections.defaultdict(list)
 for geom,value in shapes(labels,mask=known,transform=aff):groups[int(value)].append(shape(geom))
 national=[]
 for code,geoms in groups.items():
  idx=code//3;statecode=code%3;ident=parentids[idx-1];mask=labels==code;v=cover[mask];counts=collections.Counter(map(int,v[v>0]));dominant=counts.most_common(1)[0][0] if counts else None;geom=unary_union(geoms).intersection(country_grid).difference(gs_grid)
  if geom.is_empty:continue
  props=dict(id=ident+('-unknown' if statecode==2 else '-steep' if statecode==1 else '-other'),model_sample_id=ident,terrain_steep=None if statecode==2 else bool(statecode),slope_max_deg=float(np.nanmax(slope[mask])) if statecode!=2 else None,elevation_min_m=float(np.min(z[mask])),elevation_max_m=float(np.max(z[mask])),terrain_display_m=1000,terrain_native_m=90,terrain_meaning='1km cells containing native steep terrain; not exact slope at selected coordinate',cover_code=dominant,cover_counts_1km=dict(counts),cover_display_m=1000,cover_year=2021,soil_association=None,substrate=None,ground_status='SOIL_AND_SUBSTRATE_MISSING',area_support_km2=geom.area/1e6)
  national.append(dict(type='Feature',geometry=mapping(transform(back,geom.simplify(5,preserve_topology=True))),properties=props))
 # Full crossed context within Gran Sasso: terrain30m, WorldCover10m→30m, ARSSA associations1:250000.
 gs=root/'experiments/combined-terrain-20261029-01/results';terrain=root/'experiments/terrain-20261029-01'
 with rasterio.open(gs/'combined_zone.tif') as ds:zones=ds.read(1);gstr=ds.transform;gscrs=ds.crs
 with rasterio.open(terrain/'slope.tif') as ds:gsslope=ds.read(1)
 with rasterio.open(terrain/'elevation.tif') as ds:gsz=ds.read(1)
 yy,xx=np.indices(zones.shape);x=gstr.c+(xx+.5)*gstr.a;y=gstr.f+(yy+.5)*gstr.e;project=Transformer.from_crs(gscrs,3035,always_xy=True);px,py=project.transform(x,y);rr=np.floor((2680000-py)/10000).astype(int);cc=np.floor((px-4040000)/10000).astype(int);pmap={(p['grid_row'],p['grid_col']):parentindex[i] for i,p in parents.items()};par=np.zeros(zones.shape,np.int32)
 for key,index in pmap.items():
  if key[0]<rr.min() or key[0]>rr.max() or key[1]<cc.min() or key[1]>cc.max():continue
  par[(rr==key[0])&(cc==key[1])]=index
 gslabels=(zones.astype(np.int32)*4096+par);gsmask=(zones>0)&(par>0);lookup={p['zone_id']:p for p in json.loads((gs/'combined-zones.json').read_text())};togswgs=Transformer.from_crs(gscrs,4326,always_xy=True).transform;ggroups=collections.defaultdict(list)
 for geom,value in shapes(gslabels,mask=gsmask,transform=gstr):ggroups[int(value)].append(shape(geom))
 local=[]
 for code,geoms in ggroups.items():
  zone=lookup[code//4096];ident=parentids[code%4096-1];mask=(gslabels==code)&gsmask;geom=unary_union(geoms).simplify(5,preserve_topology=True);geowgs=transform(togswgs,geom).intersection(gs_bbox)
  if geowgs.is_empty:continue
  props=dict(id='GS-'+str(code),model_sample_id=ident,terrain_steep=zone['slope_band'] in ('30–<45°','≥45°'),slope_min_deg=float(gsslope[mask].min()),slope_max_deg=float(gsslope[mask].max()),elevation_min_m=float(gsz[mask].min()),elevation_max_m=float(gsz[mask].max()),terrain_display_m=30,terrain_native_m=30,terrain_meaning='30m terrain and vegetation display; soil association scale1:250000',cover=zone['cover'],cover_year=2021,cover_display_m=30,soil_unit=zone['soil_unit'],soil_association=zone['soil_association'],substrate=zone['substrate'],soil_source_scale=250000,ground_status='CARTOGRAPHIC_CONTEXT_AVAILABLE_BASAL_STATE_UNMEASURED',area_support_km2=geom.area/1e6)
  local.append(dict(type='Feature',geometry=mapping(geowgs),properties=props))
 result=dict(schema='hazardia.avalanche-terrain-context/1.0',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type='FeatureCollection',features=local+national,metadata=dict(national_grid_m=1000,national_native_slope_m=90,gran_sasso_terrain_m=30,soil_scale=250000,worldcover_year=2021,worldcover_context='categorical640m overview→1km mode; GranSasso native10m→30m mode',ground_known_bbox=[13.49,42.4,13.64,42.52],native_dsm_files=len(tiles),known_1km_support_cells=int((known&native_known).sum()),missing_native_slope_1km_cells=int((known&~native_known).sum()),steep_1km_support_cells=int((known&steep).sum()),cover_known_1km_cells=int((known&(cover>0)).sum()),cover_download_bytes=gateway.bytes,cover_cache_bytes=sum(p.stat().st_size for p in (root/'range-cache').iterdir() if re.fullmatch(r'[a-f0-9]{64}-\d+-\d+',p.name)),cover_sources=cover_sources,cover_errors=cover_errors,local_features=len(local),national_features=len(national),snow_weather_support_m=10000,release_probability=None,official_danger_grade=None,missing=['Observed stability and weak layers','Basal water and friction','National soil and substrate outside mapped Gran Sasso','Current grass structure and forest density/height','Local snow drift, true snow depth per slope, runout and exposure'],sources=['Copernicus GLO90/GLO30 release2021','ESA WorldCover2021 CC BY4.0','ARSSA Abruzzo1994–2006 associations1:250000; substrate text same source, not independent geology']))
 raw=json.dumps(result,allow_nan=False,separators=(',',':')).encode();digest=hashlib.sha256(raw).hexdigest()
 with gzip.open(output/'terrain-context.json.gz','wb') as stream:stream.write(raw)
 manifest=dict(schema=result['schema'],sha256=digest,bytes=len(raw),compressed_bytes=(output/'terrain-context.json.gz').stat().st_size,features=len(result['features']),input_hashes=input_hashes,metadata=result['metadata'],builder_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
 (output/'terrain-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({k:manifest[k] for k in ('sha256','bytes','compressed_bytes','features')}) ,flush=True)

if __name__=='__main__':main()
