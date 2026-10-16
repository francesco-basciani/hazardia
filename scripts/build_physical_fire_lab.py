"""Guest-only publication of a qualified native comparison, never synthetic shrinking."""
import argparse,json,hashlib,datetime as dt
from pathlib import Path
import numpy as np,rasterio,pyproj
from rasterio.transform import Affine,from_bounds
from rasterio.warp import reproject,Resampling,transform_bounds
from PIL import Image
from hazardia.io import load,write_new,sha256,utcnow

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--run',required=True);a=ap.parse_args();root=Path(a.runtime);run=Path(a.run);expanded=run/'expanded';cfg=load(root/'runtime-v2.json');grid=load(expanded/'grid.json');transform=Affine(*grid['transform']);shape=tuple(grid['shape']);native_bounds=rasterio.transform.array_bounds(*shape,transform);projected=transform_bounds(grid['crs'],'EPSG:3857',*native_bounds);geo=transform_bounds(grid['crs'],'EPSG:4326',*native_bounds);target_transform=from_bounds(*projected,1024,1024);name='physical-days-20261016T040414Z';out=root/'web-assets'/name;out.mkdir(exist_ok=False)
    results={case:load(expanded/(case+'-result.json')) for case in ['noop','fuelbreak']};assert all(d['status']=='PASS' and d['actual_model_time_s']==259200 and len(d['frames'])==72 for d in results.values());assert all(sha256(p)==h for p,h in cfg['engine_files'].items());rows=[];positive=[]
    for hour in range(1,73):
        row={'hour':hour}
        for case,key in [('noop','baseline'),('fuelbreak','fuelbreak')]:
            native=expanded/(case+f'-frame-{hour:02d}.npz')
            with np.load(native,allow_pickle=False) as source:prob=source['probability']
            assert prob.shape==shape and np.isfinite(prob).all() and (prob>=0).all() and (prob<=1).all();assert not any((v>0).any() for v in [prob[0,:],prob[-1,:],prob[:,0],prob[:,-1]])
            expected=float(prob.sum(dtype=np.float64)*900/10000);assert np.isclose(expected,results[case]['frames'][hour-1]['expected_area_m2']/10000,rtol=1e-6,atol=1e-6)
            projected_prob=np.zeros((1024,1024),dtype='float32');reproject(prob,projected_prob,src_transform=transform,src_crs=grid['crs'],dst_transform=target_transform,dst_crs='EPSG:3857',resampling=Resampling.nearest)
            rgba=np.zeros((1024,1024,4),dtype='uint8');rgba[:,:,:3]=[238,76,21];rgba[:,:,3]=np.where(projected_prob>0,100+130*projected_prob,0).astype('uint8');path=out/(key+f'-{hour:02d}.png');Image.fromarray(rgba,'RGBA').save(path)
            row[key]=dict(url='/assets/'+name+'/'+path.name,expected_area_ha=expected,positive_cells=int((prob>0).sum()),native_sha256=sha256(native),png_sha256=sha256(path))
            if hour==72:positive.append(np.argwhere(prob>0))
        rows.append(row)
    indices=np.concatenate(positive);minimum=indices.min(axis=0);maximum=indices.max(axis=0);west,north=transform*(int(minimum[1]),int(minimum[0]));east,south=transform*(int(maximum[1])+1,int(maximum[0])+1);affected=transform_bounds(grid['crs'],'EPSG:4326',west,south,east,north);project=pyproj.Transformer.from_crs(grid['crs'],'EPSG:4326',always_xy=True)
    r,c=grid['ignition'];x,y=transform*(c+.5,r+.5);lon,lat=project.transform(x,y);ring=[]
    for col,row in [(c-5,r-5),(c+6,r-5),(c+6,r+6),(c-5,r+6),(c-5,r-5)]:
        x,y=transform*(col,row);ring.append(list(project.transform(x,y)))
    summary=dict(status='PASS',run_id=run.name,at=utcnow(),engine_commit=cfg['engines']['PROPAGATOR'],grid_shape=list(shape),cell_m=30,realizations=2,seed=1729,weather_sha256=sha256(expanded/'weather-4days.json'),completed_hours=[72,72],valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-16T13:00:00Z',bounds=[[geo[1],geo[0]],[geo[3],geo[2]]],affected_bounds=[[affected[1],affected[0]],[affected[3],affected[2]]],ignition=[lat,lon],intervention='Idealized native vegetation_changes ring at +900s, 40cells of non-burnable fuel; no resource construction model/field calibration',intervention_geometry=dict(type='Feature',properties={},geometry=dict(type='Polygon',coordinates=[ring])),baseline_control='Native no-op allNaN vegetation event at900s matches action schedule; no physical change',qualification='UNQUALIFIED_RESEARCH: uniformfuel5,constantmoisture10percent,hourly retrospective pointERA5,no wind ensemble or real suppression qualification',rendering='Native1024x1024 probability, nearest-neighbour reprojection toEPSG3857 1024x1024RGBA; no artificial area change',frames=rows)
    write_new(out/'comparison.json',summary);write_new(run/'publication.json',dict(status='PASS',manifest=str(out/'comparison.json'),manifest_sha256=sha256(out/'comparison.json'),frames=144,at=utcnow(),final=rows[-1]));print(json.dumps(dict(status='PASS',manifest_sha256=sha256(out/'comparison.json'),frames=144,final=rows[-1],engine_hashes_unchanged=len(cfg['engine_files'])),indent=2))
if __name__=='__main__':main()
