"""Prepare real-terrain, explicitly unqualified Abruzzo research scenarios in Linux."""
import argparse,math,datetime as dt
from pathlib import Path
import numpy as np,rasterio,pyproj
from rasterio.windows import from_bounds,Window
from rasterio.warp import reproject,Resampling
from rasterio.transform import from_origin
from hazardia.io import load,write_new,sha256,utcnow,HazardError
from hazardia.contracts import validate,validate_request,validate_observation

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);args=ap.parse_args();r=Path(args.root).resolve()
    plan=load(r/'plan.json');bbox=plan['territory']['bbox_wgs84'];out=r/'prepared';out.mkdir()
    source=load(r/'dem-item.json');image=load(r/'sentinel-item.json');weather=load(r/'weather.json');date=image['properties']['datetime'][:10]
    with rasterio.open(r/'cache/dem-original.tif') as src:
        w=from_bounds(*bbox,src.transform);win=Window(math.floor(w.col_off),math.floor(w.row_off),math.ceil(w.col_off+w.width)-math.floor(w.col_off),math.ceil(w.row_off+w.height)-math.floor(w.row_off))
        z=src.read(1,window=win,masked=True);transform=src.window_transform(win)
        if z.count()!=z.size or not np.isfinite(z.compressed()).all():raise HazardError('SOURCE_MISSING','DEM coverage incomplete')
        profile=dict(driver='GTiff',height=z.shape[0],width=z.shape[1],count=1,dtype='float32',crs='EPSG:4326',transform=transform,nodata=-9999,compress='deflate')
        with rasterio.open(out/'flood-dem.tif','w',**profile) as dst:dst.write(z.filled(-9999).astype('float32'),1)
    height,width=z.shape;rgb=np.zeros((3,height,width),dtype='uint8');scl=np.zeros((height,width),dtype='uint8')
    with rasterio.open(r/'cache/sentinel-original.tif') as src:
        for b in range(3):reproject(rasterio.band(src,b+1),rgb[b],src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs='EPSG:4326',resampling=Resampling.bilinear)
    with rasterio.open(r/'cache/sentinel-scl.tif') as src:reproject(rasterio.band(src,1),scl,src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs='EPSG:4326',resampling=Resampling.nearest)
    coverage=float((scl!=0).mean());cloud=float(np.isin(scl,[3,8,9,10]).mean())
    if coverage!=1:raise HazardError('SOURCE_COVERAGE','Sentinel does not fully cover AOI')
    p=dict(profile,count=3,dtype='uint8',nodata=None)
    with rasterio.open(out/'satellite.tif','w',**p) as dst:dst.write(rgb)
    transformer=pyproj.Transformer.from_crs('EPSG:4326','EPSG:32633',always_xy=True);x,y=transformer.transform((bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2);ft=from_origin(x-960,y+960,30,30);fdem=np.full((64,64),-9999,dtype='float32')
    with rasterio.open(r/'cache/dem-original.tif') as src:reproject(rasterio.band(src,1),fdem,src_transform=src.transform,src_crs=src.crs,dst_transform=ft,dst_crs='EPSG:32633',dst_nodata=-9999,resampling=Resampling.bilinear)
    if not np.isfinite(fdem).all() or (fdem==-9999).any():raise HazardError('SOURCE_MISSING','Fire DEM coverage incomplete')
    fp=dict(profile,height=64,width=64,transform=ft,crs='EPSG:32633')
    with rasterio.open(out/'fire-dem.tif','w',**fp) as dst:dst.write(fdem,1)
    chosen=next(v for v in weather['records'] if v['at']==date+'T13:00:00Z');v=chosen['values']
    np.savez(out/'fire-arrays.npz',dem=fdem,veg=np.full((64,64),5,np.int32),wind_speed_kmh=np.full_like(fdem,v['wind_speed_10m']*3.6),wind_dir_deg=np.full_like(fdem,v['wind_direction_10m']))
    write_new(out/'weather.json',weather)
    obs=dict(schema_version='0.2.0',kind='observation',id=image['id'],territory_id=plan['territory']['id'],sensed_at=image['properties']['datetime'],available_at=load(r/'cache/sentinel-original.tif.source.json')['available_at'],ingested_at=utcnow(),bbox_wgs84=bbox,crs='EPSG:4326',native_resolution_m=10,coverage_fraction=coverage,quality='PARTIAL' if cloud else 'VALID',asset=dict(path='prepared/satellite.tif',sha256=sha256(out/'satellite.tif')),license='Copernicus Sentinel legal notice',source=image['assets']['visual']['href'],migration=None)
    validate_observation(obs);write_new(r/'observation.json',obs)
    territory=dict(id=plan['territory']['id'],region='Abruzzo',bbox_wgs84=bbox,work_crs='EPSG:32633',timezone='Europe/Rome',calibration='UNKNOWN',complete_catchment=False)
    def grid(prof):return dict(shape=[prof['height'],prof['width']],crs=str(prof['crs']),vertical_datum='EGM2008_DSM_UNQUALIFIED',transform=list(prof['transform'])[:6],nodata=-9999)
    def asset(role,path):return dict(role=role,path='prepared/'+path,sha256=sha256(out/path))
    shared=[asset('weather','weather.json'),asset('satellite','satellite.tif')]
    base=dict(schema_version='0.2.0',kind='simulation_request',mode='RESEARCH_RETROSPECTIVE',territory=territory,snapshot_at=utcnow(),max_log_bytes=32*1024**2)
    fire=dict(base,id='abruzzo-fire-research',hazard='FIRE',grid=grid(fp),valid_from=date+'T13:00:00Z',valid_until=date+'T13:10:00Z',assets=shared+[asset('dem','fire-dem.tif'),asset('fire_arrays','fire-arrays.npz')],assumptions=['Scenario ignition, not an observed incident','Uniform synthetic legacy5 fuel, not inferred from satellite imagery','Synthetic fuel moisture10percent; no local calibration','Real DSM and retrospective ERA5pointwind; partial territory, no historical skill'],options=dict(duration_s=600,realizations=2,seed=1729,ignition=[32,32],moisture_percent=10,fuel_legacy=5),timeout_s=180)
    flood=dict(base,id='abruzzo-flood-research',hazard='FLOOD',grid=grid(profile),valid_from=date+'T00:00:00Z',valid_until=date+'T06:00:00Z',assets=shared+[asset('dem','flood-dem.tif')],assumptions=['Partial AOI, not complete hydrological catchment','Synthetic rainfall pulse overrides historical precipitation for technical wet control','Uncalibrated HMC soil/default parameters, roughness and initial state','Q0zero is explicitly synthetic bankfull-reference placeholder, not first HMC sample','Q100/return_period100 is upstream column label only, not recurrence','Maximum inundation only, not arrival-time prediction','Declared experimental2line REFlExcompatibilitycopy'],options=dict(hours=6,rain_mm=[10,30,30,10,0,0,0],q0_m3_s=0,q0_evidence='SYNTHETIC_RESEARCH_REFERENCE',flow_threshold_cells=500,allow_experimental_patch=True),timeout_s=600)
    for name,value in [('fire-request.json',fire),('flood-request.json',flood)]:validate_request(value,r);write_new(r/name,value)
    write_new(r/'preparation-result.json',dict(status='PASS',prepared_at=utcnow(),flood_shape=list(z.shape),fire_shape=[64,64],dsm_range_m=[float(z.min()),float(z.max())],scl_coverage_fraction=coverage,scl_cloud_shadow_cirrus_fraction=cloud,weather_record_used=chosen,provenance=dict(dem_id=source['id'],sentinel_id=image['id']),scope='Real Abruzzo geography, unqualified conditional research scenarios, not historical fire/flood reconstruction'))
    print('Prepared',z.shape,coverage,cloud)
if __name__=='__main__':main()
