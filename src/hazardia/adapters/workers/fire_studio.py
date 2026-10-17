"""Pinned upstream actions and timed wind; no geometry-based output shrinking."""
import dataclasses
import numpy as np
from propagator.core import Propagator,BoundaryConditions,FUEL_SYSTEM_LEGACY
from propagator.io.boundary_conditions import TimedInput
from propagator.io.actions import ACTION_CLASSES
from shapely.geometry import LineString,Polygon
from propagator.io.actions import build_mask
from pyproj import Transformer
from propagator.io.geo import GeographicInfo
from rasterio.transform import Affine,array_bounds
from pyproj import CRS
from hazardia.adapters.workers.fire import seed_worker
from hazardia.io import write_new,sha256,HazardError

def run_studio(root,req,dem,veg,plan):
    opt=req['options'];tr=Affine(*req['grid']['transform']);geo=GeographicInfo(crs=CRS.from_user_input(req['grid']['crs']),trans=tr,bounds=array_bounds(*dem.shape,tr),shape=dem.shape)
    events={r['time']:dict(time=r['time'],w_speed=r['values']['wind_speed_10m']*3.6,w_dir=r['values']['wind_direction_10m']) for r in plan['records']}
    ignitions=plan.get('ignitions_wgs84',[dict(point=plan['ignition_wgs84'],at_minutes=0)])
    for t in set(plan['action_times']+plan.get('comparison_times',[])+[int(i['at_minutes']*60) for i in ignitions]):events.setdefault(t,dict(time=t))
    project=Transformer.from_crs('EPSG:4326',req['grid']['crs'],always_xy=True)
    ignitions_at={}
    for i in ignitions:
        x,y=project.transform(i['point'][1],i['point'][0]);c,r=(~tr)*(x,y);ignitions_at.setdefault(int(i['at_minutes']*60),[]).append((int(r),int(c)))
    for r in plan['resources']:
        t=int(r['at_minutes']*60)
        if r.get('effect')=='fuel_removal':continue
        geometry=LineString([(p[1],p[0]) for p in r['line']]);events[t].setdefault('actions',[]).append(ACTION_CLASSES[r['category']](geometries=[geometry],epsg=4326))
    conditions=[];proof=[]
    for t,e in sorted(events.items()):
        timed=TimedInput.model_validate(dict(e,epsg=4326));bc=timed.get_boundary_conditions(geo,FUEL_SYSTEM_LEGACY.get_non_vegetated())
        # Matching empty events avoids changing the native numerical schedule between A/B.
        masks=[]
        for r in plan['resources']:
            if int(r['at_minutes']*60)==t and r.get('effect')=='fuel_removal':
                points=[(p[1],p[0]) for p in r.get('line',r.get('area'))];geometry=LineString(points) if 'line' in r else Polygon(points);masks.append(build_mask([geometry],geo,src_epsg=4326))
        if masks:
            fuel=bc.vegetation_changes.copy() if bc.vegetation_changes is not None else np.full(dem.shape,np.nan,dtype='float32')
            fuel[np.logical_or.reduce(masks)]=FUEL_SYSTEM_LEGACY.get_non_vegetated();bc=dataclasses.replace(bc,vegetation_changes=fuel)
        if t in set(plan['action_times']+plan.get('comparison_times',[])) and bc.vegetation_changes is None and bc.additional_moisture is None:bc=dataclasses.replace(bc,vegetation_changes=np.full(dem.shape,np.nan,dtype='float32'))
        if t in ignitions_at:bc=dataclasses.replace(bc,ignitions=ignitions_at[t])
        if t==0:bc=dataclasses.replace(bc,moisture=np.full(dem.shape,opt['moisture_percent'],dtype='float32'))
        conditions.append(bc)
        proof.append(dict(time=t,ignition_count=len(ignitions_at.get(t,[])),fuel_removal_geometries=len(masks),wind_kmh=e.get('w_speed'),wind_from_deg=e.get('w_dir'),moisture_changed_cells=int(np.count_nonzero(bc.additional_moisture)) if bc.additional_moisture is not None else 0,vegetation_changed_cells=int(np.isfinite(bc.vegetation_changes).sum()) if bc.vegetation_changes is not None else 0))
    def model():
        m=Propagator(dem=dem,veg=veg.copy(),cellsize=tr.a,realizations=opt['realizations'],fuels=FUEL_SYSTEM_LEGACY,do_spotting=False,out_of_bounds_mode='raise')
        for bc in conditions:m.set_boundary_conditions(bc)
        return m
    model().step(seconds=1);seed_proof=seed_worker(opt['seed'],1).tolist();m=model();frames=[]
    for index in range(1,opt['duration_s']//900+1):
        hour=index/4
        m.step(seconds=900);p=m.compute_fire_probability()
        if any((a>0).any() for a in [p[0,:],p[-1,:],p[:,0],p[:,-1]]):raise HazardError('DOMAIN_EXIT','Fire reached prepared terrain boundary; no complete forecast claimed')
        file=root/('frame-%03d.npz'%index);np.savez_compressed(file,probability=p);frames.append(dict(index=index,elapsed_s=index*900,hour=hour,path=file.name,sha256=sha256(file),expected_area_ha=float(p.sum(dtype=np.float64)*tr.a**2/10000),positive_cells=int((p>0).sum()),queued_front_events=int(m._front_sizes.sum()),realizations_with_front=int((m._front_sizes>0).sum())))
        print('HOUR',hour,'CELLS',frames[-1]['positive_cells'],flush=True)
    np.savez_compressed(root/'fire-output.npz',probability=m.compute_fire_probability(),fire=m.fire,arrival=m.arrival_time)
    write_new(root/'fire-native-result.json',dict(case=plan['case'],seed=opt['seed'],worker_seed_proof=seed_proof,threads=1,realizations=opt['realizations'],duration_s=int(m.time),consumed_events=proof,frames=frames,qualification='UNQUALIFIED_RESEARCH',actual_inputs='Hourly point wind; upstream actions or authored ideal fuel removal; real DEM; uniform fuel5 and manual fuel moisture'))
