"""Pinned upstream actions and timed wind; no geometry-based output shrinking."""
import dataclasses
import numpy as np
from propagator.core import Propagator,BoundaryConditions,FUEL_SYSTEM_LEGACY
from propagator.io.boundary_conditions import TimedInput
from propagator.io.actions import ACTION_CLASSES
from shapely.geometry import LineString
from propagator.io.geo import GeographicInfo
from rasterio.transform import Affine,array_bounds
from pyproj import CRS
from hazardia.adapters.workers.fire import seed_worker
from hazardia.io import write_new,sha256,HazardError

def run_studio(root,req,dem,veg,plan):
    opt=req['options'];tr=Affine(*req['grid']['transform']);geo=GeographicInfo(crs=CRS.from_user_input(req['grid']['crs']),trans=tr,bounds=array_bounds(*dem.shape,tr),shape=dem.shape)
    events={r['time']:dict(time=r['time'],w_speed=r['values']['wind_speed_10m']*3.6,w_dir=r['values']['wind_direction_10m']) for r in plan['records']}
    for t in plan['action_times']:events.setdefault(t,dict(time=t))
    for r in plan['resources']:
        t=int(r['at_minutes']*60);geometry=LineString([(p[1],p[0]) for p in r['line']]);events[t].setdefault('actions',[]).append(ACTION_CLASSES[r['category']](geometries=[geometry],epsg=4326))
    conditions=[];proof=[]
    for t,e in sorted(events.items()):
        timed=TimedInput.model_validate(dict(e,epsg=4326));bc=timed.get_boundary_conditions(geo,FUEL_SYSTEM_LEGACY.get_non_vegetated())
        # Matching empty events avoids changing the native numerical schedule between A/B.
        if t in plan['action_times'] and bc.vegetation_changes is None and bc.additional_moisture is None:bc=dataclasses.replace(bc,vegetation_changes=np.full(dem.shape,np.nan,dtype='float32'))
        if t==0:bc=dataclasses.replace(bc,ignitions=[tuple(opt['ignition'])],moisture=np.full(dem.shape,opt['moisture_percent'],dtype='float32'))
        conditions.append(bc)
        proof.append(dict(time=t,wind_kmh=e.get('w_speed'),wind_from_deg=e.get('w_dir'),moisture_changed_cells=int(np.count_nonzero(bc.additional_moisture)) if bc.additional_moisture is not None else 0,vegetation_changed_cells=int(np.isfinite(bc.vegetation_changes).sum()) if bc.vegetation_changes is not None else 0))
    def model():
        m=Propagator(dem=dem,veg=veg.copy(),cellsize=tr.a,realizations=opt['realizations'],fuels=FUEL_SYSTEM_LEGACY,do_spotting=False,out_of_bounds_mode='raise')
        for bc in conditions:m.set_boundary_conditions(bc)
        return m
    model().step(seconds=1);seed_proof=seed_worker(opt['seed'],1).tolist();m=model();frames=[]
    for hour in range(1,opt['duration_s']//3600+1):
        m.step(seconds=3600);p=m.compute_fire_probability()
        if any((a>0).any() for a in [p[0,:],p[-1,:],p[:,0],p[:,-1]]):raise HazardError('DOMAIN_EXIT','Fire reached prepared terrain boundary; no complete forecast claimed')
        file=root/('frame-%03d.npz'%hour);np.savez_compressed(file,probability=p);frames.append(dict(hour=hour,path=file.name,sha256=sha256(file),expected_area_ha=float(p.sum(dtype=np.float64)*tr.a**2/10000),positive_cells=int((p>0).sum())))
        print('HOUR',hour,'CELLS',frames[-1]['positive_cells'],flush=True)
    np.savez_compressed(root/'fire-output.npz',probability=m.compute_fire_probability(),fire=m.fire,arrival=m.arrival_time)
    write_new(root/'fire-native-result.json',dict(case=plan['case'],seed=opt['seed'],worker_seed_proof=seed_proof,threads=1,realizations=opt['realizations'],duration_s=int(m.time),consumed_events=proof,frames=frames,qualification='UNQUALIFIED_RESEARCH',actual_inputs='Hourly point wind; upstream line actions; real DEM; uniform fuel5 and manual fuel moisture'))
