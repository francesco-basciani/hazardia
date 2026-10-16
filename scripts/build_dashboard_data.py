"""Geo preprocessing and local satellite assets, run only in the Linux geo env."""
import argparse,datetime as dt,sqlite3,os,shutil
from pathlib import Path
import numpy as np,rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject,Resampling,transform_bounds,transform
from PIL import Image
from hazardia.io import load,write_new,sha256,utcnow

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);a=ap.parse_args();root=Path(a.runtime);out=root/'web-assets';out.mkdir(exist_ok=True);(out/'products').mkdir(exist_ok=True)
    m1=root/'runs/m1-abruzzo-20261015T161041Z';m3=root/'runs'/load(root/'m3-plan.json')['run_id']
    vendor=out/'vendor';vendor.mkdir(exist_ok=True)
    for name in ['leaflet.js','leaflet.css','LICENSE']:
        src=m3/'vendor'/name;dst=vendor/name
        if dst.exists():assert sha256(dst)==sha256(src)
        else:shutil.copyfile(src,dst)
    background=out/'satellite.png';bbox=[13.32,42.30,13.44,42.40]
    if not background.exists():
        b=transform_bounds('EPSG:4326','EPSG:3857',*bbox);w=1200;h=round(w*(b[3]-b[1])/(b[2]-b[0]));rgb=np.zeros((3,h,w),dtype='uint8');tr=from_bounds(*b,w,h)
        with rasterio.open(m1/'cache/sentinel-original.tif') as src:
            for band in range(3):reproject(rasterio.band(src,band+1),rgb[band],src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs='EPSG:3857',resampling=Resampling.bilinear)
        assert (rgb.sum(axis=0)>0).mean()>.95,'Context image does not fully cover selected Abruzzo bounds'
        Image.fromarray(np.transpose(rgb,(1,2,0))).save(background)
    with sqlite3.connect(root/'jobs/jobs.sqlite') as db:jobs=db.execute("SELECT id FROM jobs WHERE state='SUCCEEDED' ORDER BY rowid DESC LIMIT 20").fetchall()
    scenarios=[]
    for (job,) in jobs:
        directory=root/'jobs'/job
        if not (directory/'product.json').exists():continue
        p=load(directory/'product.json');req=load(directory/'request.json');hazard=p['hazard'];layer=p['layers'][0];target=out/'products'/job;target.mkdir(exist_ok=True)
        with rasterio.open(directory/layer['path']) as src:
            data=src.read(1,masked=True);bounds=transform_bounds(src.crs,'EPSG:4326',*src.bounds);positive=np.argwhere(data.filled(0)>0);points=[];cells=[]
            for i,(row,col) in enumerate(positive[:3]):
                x,y=src.xy(int(row),int(col));lon,lat=transform(src.crs,'EPSG:4326',[x],[y]);points.append(dict(id='group-'+str(i+1),lat=lat[0],lon=lon[0],people=10,label='Gruppo sintetico '+str(i+1)))
            if hazard=='FIRE':
                with rasterio.open(directory/'products/earliest-realization-arrival.tif') as arr:arrival=arr.read(1,masked=True)
                for row,col in positive:
                    corners=[src.transform*(x,y) for x,y in [(col,row),(col+1,row),(col+1,row+1),(col,row+1),(col,row)]];lon,lat=transform(src.crs,'EPSG:4326',[c[0] for c in corners],[c[1] for c in corners]);cells.append(dict(type='Feature',geometry=dict(type='Polygon',coordinates=[list(zip(lon,lat))]),properties=dict(probability=float(data[row,col]),arrival_s=float(arrival[row,col]))))
            else:
                overlay=target/'depth.png'
                if not overlay.exists():
                    merc=transform_bounds(src.crs,'EPSG:3857',*src.bounds);w=512;h=round(w*(merc[3]-merc[1])/(merc[2]-merc[0]));values=np.zeros((h,w),dtype='float32');reproject(rasterio.band(src,1),values,src_transform=src.transform,src_crs=src.crs,dst_transform=from_bounds(*merc,w,h),dst_crs='EPSG:3857',dst_nodata=0,resampling=Resampling.nearest)
                    fraction=np.clip(values/max(float(data.max()),1e-9),0,1);rgba=np.zeros((h,w,4),dtype='uint8');rgba[:,:,0]=18;rgba[:,:,1]=180-120*fraction;rgba[:,:,2]=250;rgba[:,:,3]=np.where(values>0,210,0);Image.fromarray(rgba).save(overlay)
        ref=dict(job_id=job,hazard=hazard,sha256=layer['sha256'],valid_from=p['valid_from'],valid_until=p['valid_until'],weather_hash=next(v['sha256'] for v in p['input_hashes'] if v['role']=='weather'),qualification=p['qualification'])
        scenarios.append(dict(id=job,hazard=hazard,title=('Incendio' if hazard=='FIRE' else 'Alluvione')+' · L’Aquila',reference=ref,engine=p['engine'],valid_from=p['valid_from'],valid_until=p['valid_until'],bounds=[[bounds[1],bounds[0]],[bounds[3],bounds[2]]],overlay=None if hazard=='FIRE' else '/assets/products/'+job+'/depth.png',cells=dict(type='FeatureCollection',features=cells),exposure_points=points,maximum=layer['statistics']['maximum'],positive_cells=layer['statistics']['positive_cells'],unit=layer['unit'],assumptions=p['assumptions'],options=req['options'],mode=req['mode'],weather={k:v for k,v in load(directory/next(a['path'] for a in req['assets'] if a['role']=='weather')).items() if k!='records'}))
    catalog=dict(schema_version='0.5.0',built_at=utcnow(),background=dict(url='/assets/satellite.png',bounds=[[bbox[1],bbox[0]],[bbox[3],bbox[2]]],sha256=sha256(background),scene='S2A_33TUG_20240713_0_L2A',sensed_at='2024-07-13T10:09:10.545Z'),scenarios=scenarios,attribution='Contains modified Copernicus Sentinel data 2024; produced using Copernicus WorldDEM-30 © DLR e.V.2010-2014 / © Airbus2014-2018 provided under COPERNICUS by EU and ESA; rights reserved. Weather data by Open-Meteo.com / ERA5 CC BY4.0. All scenarios unqualified research.',no_operational_authority=True)
    frozen=out/('catalog-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');write_new(frozen,catalog);tmp=out/'catalog.pending';tmp.write_bytes(frozen.read_bytes());os.replace(tmp,out/'catalog.json');print('Catalog',len(scenarios),'satellite',background.stat().st_size)
if __name__=='__main__':main()
