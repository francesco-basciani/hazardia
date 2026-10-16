"""Independent raster/array content reader and versioned hazard-product publisher."""
import shutil,sys
from pathlib import Path
import numpy as np,rasterio
from rasterio.transform import Affine
from hazardia.io import load,write_new,sha256,verify_asset,HazardError

def run(root):
    req=load(root/'request.json');cfg=load(root/'runtime.json');grid=req['grid'];shape=tuple(grid['shape']);transform=Affine(*grid['transform']);out=root/'products';out.mkdir()
    # Verify actual DEM metadata independently from the simulator implementation.
    with rasterio.open(verify_asset(root,next(v for v in req['assets'] if v['role']=='dem'))) as src:
        if src.shape!=shape or str(src.crs)!=grid['crs'] or not np.allclose(list(src.transform)[:6],grid['transform'],atol=1e-12,rtol=0):raise HazardError('GRID_MISMATCH','Accepted DEM metadata differs from product grid')
    specs=[]
    if req['hazard']=='FIRE':
        with np.load(root/'fire-output.npz',allow_pickle=False) as native:
            probability=native['probability'];arrival=native['arrival'];fire=native['fire']
        if probability.shape!=shape or not np.isfinite(probability).all() or (probability<0).any() or (probability>1).any():raise HazardError('INVALID_OUTPUT','Fire probability shape/range')
        if arrival.shape!=fire.shape or arrival.shape[:2]!=shape:raise HazardError('INVALID_OUTPUT','Arrival/fire array shapes')
        valid=np.isfinite(arrival)&(arrival>=0)&(fire>0)
        values=np.where(valid,arrival,np.inf)
        if values.ndim==3:values=np.min(values,axis=2)
        if values.ndim!=2:raise HazardError('INVALID_OUTPUT','Unsupported arrival dimensions')
        values=np.where((probability>0)&np.isfinite(values),values,-9999).astype('float32')
        if (values[values!=-9999]>req['options']['duration_s']+1e-4).any():raise HazardError('INVALID_TIME','Published arrival exceeds simulation horizon')
        for filename,a,name,unit in [('fire-probability.tif',probability,'FIRE_PROBABILITY','1'),('earliest-realization-arrival.tif',values,'ARRIVAL_TIME','s')]:
            with rasterio.open(out/filename,'w',driver='GTiff',height=shape[0],width=shape[1],count=1,dtype='float32',crs=grid['crs'],transform=transform,nodata=-9999,compress='deflate') as dst:dst.write(a.astype('float32'),1)
            specs.append((filename,name,unit))
        engine=dict(name='PROPAGATOR',source_commit=cfg['engines']['PROPAGATOR'],patch_sha256=None)
    else:
        info=load(root/'flood-native-result.json')
        if info['max_relative_optimizer_residual']>.01:raise HazardError('OPTIMIZER_RESIDUAL','Numerical volume fit residual exceeds1percent technical diagnostic, not physical skill threshold')
        native=root/info['depth_path'];shutil.copyfile(native,out/'maximum-depth.tif');specs=[('maximum-depth.tif','MAXIMUM_DEPTH','m')]
        engine=dict(name='HMC+REFLEX',source_commit='HMC='+cfg['engines']['HMC']+';REFLEX='+cfg['engines']['REFLEX'],patch_sha256=cfg['reflex_patch_sha256'])
    layers=[]
    for filename,name,unit in specs:
        path=out/filename
        with rasterio.open(path) as src:
            array=src.read(1,masked=True);values=array.compressed()
            if src.shape!=shape or str(src.crs)!=grid['crs'] or not np.allclose(list(src.transform)[:6],grid['transform'],atol=1e-12,rtol=0):raise HazardError('GRID_MISMATCH','Result grid differs from accepted input')
            if not values.size or not np.isfinite(values).all() or (values<0).any():raise HazardError('INVALID_OUTPUT','Empty/nonfinite/negative spatial product')
            if name=='FIRE_PROBABILITY' and (values>1).any():raise HazardError('INVALID_OUTPUT','Probability exceeds1')
            layers.append(dict(name=name,unit=unit,path=str(path.relative_to(root)),sha256=sha256(path),statistics=dict(valid_cells=int(values.size),positive_cells=int((values>0).sum()),minimum=float(values.min()),maximum=float(values.max()))))
    write_new(root/'product.json',dict(schema_version='0.2.0',kind='hazard_product',job_id=root.name,request_id=req['id'],hazard=req['hazard'],qualification='UNQUALIFIED_RESEARCH',grid=grid,valid_from=req['valid_from'],valid_until=req['valid_until'],engine=engine,layers=layers,assumptions=req['assumptions']+(['Native REFlEx executed and returned zero depths: all rounded triangular reach volumes below its unchanged1m3 research cutoff; no real-world safety claim'] if req['hazard']=='FLOOD' and info.get('mapping_status')=='NO_INCLUDED_RUNOFF_VOLUME' else [])+(['Arrival is earliest across realizations, masked to burned cells; not a calibrated probabilistic arrival forecast'] if req['hazard']=='FIRE' else []),input_hashes=[dict(role=v['role'],sha256=v['sha256']) for v in req['assets']],validation=dict(status='PASS',scope='TECHNICAL_CONTENT_ONLY')))
    if any(a['role']=='fire_plan' for a in req['assets']):
        from hazardia.adapters.workers.studio_render import render
        render(root,req)

if __name__=='__main__':
    root=Path(sys.argv[1])
    try:run(root)
    except Exception as exc:
        write_new(root/'worker-error.json',dict(code=exc.code if isinstance(exc,HazardError) else 'PRODUCT_ERROR',message=str(exc)));raise
