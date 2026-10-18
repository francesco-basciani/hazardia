"""Ignition-centred terrain, real global DEM/land-cover, no fixed example AOI."""
import hashlib,json,math,os,sys
from pathlib import Path
from hazardia.io import load,write_new,sha256,HazardError,utcnow
# ESA WorldCover2021 to PROPAGATOR legacy: research crosswalk, trees not species resolved.
CROSSWALK={10:1,20:2,30:4,40:6,50:0,60:0,70:0,80:0,90:4,95:1,100:4}
def prepare(root,body):
 import numpy as np,rasterio
 from rasterio.transform import from_origin
 from rasterio.warp import reproject,Resampling,transform_bounds
 from rasterio.windows import from_bounds,Window
 from pyproj import Transformer
 from hazardia.ingest.range_cache import RangeCache
 points=[i['point'] for i in body['ignitions']];lat=sum(p[0] for p in points)/len(points);lon=sum(p[1] for p in points)/len(points)
 if not -60<lat<80:raise HazardError('TERRAIN_UNAVAILABLE','DEM global source covers60S..80N; no invented polar terrain')
 zone=max(1,min(60,int((lon+180)//6)+1));crs='EPSG:'+str((32600 if lat>=0 else 32700)+zone);to=Transformer.from_crs(4326,crs,always_xy=True);xy=[to.transform(p[1],p[0]) for p in points];x=round(sum(p[0] for p in xy)/len(xy)/30)*30;y=round(sum(p[1] for p in xy)/len(xy)/30)*30;n=1024;tr=from_origin(x-n*15,y+n*15,30,30)
 if any(abs(px-x)>13000 or abs(py-y)>13000 for px,py in xy):raise HazardError('DOMAIN_SPAN','Ignitions span more than the bounded30km domain; use separate simulation groups')
 spec=dict(version='dynamic-terrain/1',crs=crs,shape=[n,n],transform=list(tr)[:6],native_cell_m=30,crosswalk=CROSSWALK);key=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest();dest=Path(root)/'terrain-cache'/key
 if (dest/'manifest.json').exists():
  m=load(dest/'manifest.json')
  if any(sha256(dest/p)!=s for p,s in m['artifacts'].items()):raise HazardError('CHECKSUM','Prepared terrain cache changed')
  return dest
 if dest.exists():
  import uuid
  dest.rename(dest.with_name(dest.name+'-failed-'+uuid.uuid4().hex[:8]))
 dest.mkdir(parents=True);write_new(dest/'grid.json',spec);bbox=transform_bounds(crs,4326,x-n*15,y-n*15,x+n*15,y+n*15,densify_pts=32);dem=np.full((n,n),-9999,np.float32);cover=np.zeros((n,n),np.uint8);sources=[];gateway=RangeCache(Path(root)/'cog-cache').start()
 def read_tile(url,target,method):
  sources.append(url)
  with rasterio.open(gateway.local(url)) as src:
   sb=transform_bounds(4326,src.crs,*bbox,densify_pts=16);w=from_bounds(*sb,src.transform);window=Window(math.floor(w.col_off)-2,math.floor(w.row_off)-2,math.ceil(w.width)+5,math.ceil(w.height)+5);window=window.intersection(Window(0,0,src.width,src.height));a=src.read(1,window=window)
   reproject(a,target,src_transform=src.window_transform(window),src_crs=src.crs,src_nodata=src.nodata,dst_transform=tr,dst_crs=crs,dst_nodata=-9999 if target.dtype==np.float32 else 0,init_dest_nodata=False,resampling=method)
 try:
  with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_MULTIRANGE='NO',GDAL_HTTP_MAX_RETRY='0',GDAL_CACHEMAX=64):
   for iy in range(math.floor(bbox[1]),math.ceil(bbox[3])):
    for ix in range(math.floor(bbox[0]),math.ceil(bbox[2])):
     tag=f'{"N" if iy>=0 else "S"}{abs(iy):02d}_00_{"E" if ix>=0 else "W"}{abs(ix):03d}_00';name='Copernicus_DSM_COG_10_'+tag+'_DEM';read_tile(f'https://copernicus-dem-30m.s3.amazonaws.com/{name}/{name}.tif',dem,Resampling.bilinear)
   for iy in range(math.floor(bbox[1]/3)*3,math.ceil(bbox[3]/3)*3,3):
    for ix in range(math.floor(bbox[0]/3)*3,math.ceil(bbox[2]/3)*3,3):
     tag=f'{"N" if iy>=0 else "S"}{abs(iy):02d}{"E" if ix>=0 else "W"}{abs(ix):03d}';read_tile(f'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tag}_Map.tif',cover,Resampling.nearest)
  if gateway.error:raise HazardError('SOURCE_MISSING',gateway.error)
  write_new(dest/'coverage-diagnostic.json',dict(dem_missing=int((dem==-9999).sum()),landcover={str(int(v)):int((cover==v).sum()) for v in np.unique(cover)},dem_range=[float(dem.min()),float(dem.max())]))
  if not np.isfinite(dem).all() or (dem==-9999).any() or not set(np.unique(cover))<=set(CROSSWALK):raise HazardError('SOURCE_MISSING','DEM or WorldCover incomplete; no synthetic fallback')
  veg=np.zeros((n,n),np.int32)
  for code,fuel in CROSSWALK.items():veg[cover==code]=fuel
  np.savez_compressed(dest/'expanded-arrays.npz',dem=dem,veg=veg,landcover=cover)
  with rasterio.open(dest/'dem.tif','w',driver='GTiff',height=n,width=n,count=1,dtype='float32',crs=crs,transform=tr,nodata=-9999,compress='deflate') as dst:dst.write(dem,1)
  write_new(dest/'manifest.json',dict(id=key,available_at=utcnow(),bbox_wgs84=bbox,grid=spec,landcover_counts={str(int(v)):int((cover==v).sum()) for v in np.unique(cover)},sources=sources,downloaded_bytes=gateway.bytes,artifacts={p:sha256(dest/p) for p in ['grid.json','expanded-arrays.npz','dem.tif']},qualification='REAL_LANDCOVER_RESEARCH_FUEL_CROSSWALK',licenses=['Copernicus DEM licence','ESA WorldCover2021 CC BY4.0'],uncertainty='Tree cover mapped to broadleaves, not species resolved; crops/wetlands seasonal fuel unresolved; no local calibration'))
  return dest
 except Exception as e:write_new(dest/'failure.json',dict(at=utcnow(),detail=str(e),gateway_error=gateway.error));raise
 finally:gateway.close()
if __name__=='__main__':print(prepare(Path(sys.argv[1]),load(Path(sys.argv[2]))))
