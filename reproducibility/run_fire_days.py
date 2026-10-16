"""Guest-only predeclared feasibility run; native unmodified PROPAGATOR API."""
import sys,json,time,hashlib,datetime as dt
from pathlib import Path
import numpy as np
from propagator.core import Propagator,BoundaryConditions,FUEL_SYSTEM_LEGACY
from hazardia.adapters.workers.fire import seed_worker
from hazardia.io import write_new,load,utcnow
r=Path(sys.argv[1]);case=sys.argv[2];weather=load(r/'weather-4days.json');start=dt.datetime(2024,7,13,13,tzinfo=dt.timezone.utc);duration=259200
values=np.load(r/'expanded-arrays.npz',allow_pickle=False);dem=values['dem'];veg=values['veg'];mask=np.zeros_like(dem,dtype=bool)
row,col=512,512
mask[row-5:row+6,col-5]=True;mask[row-5:row+6,col+5]=True;mask[row-5,col-5:col+6]=True;mask[row+5,col-5:col+6]=True
# This ring is an idealized prepared test geometry, not a dispatch/resource effectiveness model.
def model(prime=False):
 m=Propagator(dem=dem,veg=veg.copy(),cellsize=30,realizations=2,fuels=FUEL_SYSTEM_LEGACY,do_spotting=False,out_of_bounds_mode='raise')
 m.set_boundary_conditions(BoundaryConditions(time=0,ignitions=[(row,col)],moisture=np.full_like(dem,10)))
 for record in weather['records']:
  moment=dt.datetime.fromisoformat(record['at'].replace('Z','+00:00'));seconds=int((moment-start).total_seconds())
  if 0<=seconds<=duration:
   v=record['values'];m.set_boundary_conditions(BoundaryConditions(time=seconds,wind_speed=np.full_like(dem,v['wind_speed_10m']*3.6),wind_dir=np.full_like(dem,v['wind_direction_10m'])))
 if case in ['fuelbreak','noop'] and not prime:m.set_boundary_conditions(BoundaryConditions(time=900,vegetation_changes=np.where(mask if case=='fuelbreak' else np.zeros_like(mask),m.fuels.get_non_vegetated(),np.nan).astype('float32')))
 return m
started=time.monotonic();model(True).step(seconds=1);seed_worker(1729,1)
m=model();frames=[];status='PASS';error=None
try:
 for hour in range(1,73):
  m.step(seconds=3600);p=m.compute_fire_probability();np.savez_compressed(r/(case+f'-frame-{hour:02d}.npz'),probability=p);print('HOUR',hour,'CELLS',int((p>0).sum()),flush=True);frames.append(dict(hour=hour,positive_cells=int((p>0).sum()),expected_area_m2=float(p.sum()*900),boundary_positive=bool((p[0,:]>0).any()or(p[-1,:]>0).any()or(p[:,0]>0).any()or(p[:,-1]>0).any())))
except Exception as e:status='FAIL';error=dict(type=type(e).__name__,detail=str(e))
p=m.compute_fire_probability();np.savez_compressed(r/(case+'-native.npz'),probability=p,arrival=m.arrival_time,fire=m.fire)
result=dict(at=utcnow(),case=case,status=status,error=error,requested_hours=72,actual_model_time_s=int(m.time),frames=frames,elapsed_s=time.monotonic()-started,native_sha256=hashlib.sha256((r/(case+'-native.npz')).read_bytes()).hexdigest(),qualification='Idealized native parameter intervention; not qualified field efficacy; incomplete if domain exited')
write_new(r/(case+'-result.json'),result);print(json.dumps(result,indent=2))
