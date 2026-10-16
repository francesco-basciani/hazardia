"""Rebuild the native 1024-square DSM and frozen 72-hour experiment inputs."""
import argparse,json,shutil,sqlite3
from pathlib import Path
import numpy as np,rasterio
from rasterio.warp import reproject,Resampling
from rasterio.transform import from_origin
from hazardia.io import write_new,load
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);a=p.parse_args();root=Path(a.runtime);source=Path(__file__).parent/'snapshots';run=root/'runs/physical-days-20261016T040414Z';out=run/'expanded'
if not (root/'installation/demo.json').exists():raise RuntimeError('Run demo before days')
with sqlite3.connect(root/'jobs/jobs.sqlite') as db:
    if db.execute("SELECT count(*) FROM jobs WHERE state IN ('RUNNING','QUEUED')").fetchone()[0]:raise RuntimeError('Wait until model queue is idle')
if not out.exists():
    out.mkdir(parents=True);grid=load(source/'physical-days/grid.json');transform=rasterio.Affine(*grid['transform']);dem=np.full((1024,1024),-9999,dtype='float32')
    with rasterio.open(root/'runs/m1-abruzzo-20261015T161041Z/cache/dem-original.tif') as src:reproject(rasterio.band(src,1),dem,src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs=grid['crs'],dst_nodata=-9999,resampling=Resampling.bilinear)
    assert np.isfinite(dem).all() and not (dem==-9999).any()
    np.savez_compressed(out/'expanded-arrays.npz',dem=dem,veg=np.full(dem.shape,5,dtype=np.int32));write_new(out/'grid.json',grid);shutil.copyfile(source/'physical-days/weather-4days.json',out/'weather-4days.json')
    write_new(run/'reconstruction.json',dict(scope='Frozen original idealized experiment configuration, freshly regenerated, not independent field validation',original_run='physical-days-20261016T040414Z',negative_evidence='No-op scheduler sensitivity; only paired no-op/fuelbreak clock compared'))
print('Native day inputs ready:',out)
