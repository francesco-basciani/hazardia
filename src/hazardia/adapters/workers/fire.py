"""Real PROPAGATOR core, isolated Python3.12/Numba environment."""
import sys
from pathlib import Path
import numpy as np
from numba import njit,prange,get_num_threads
from propagator.core import Propagator,BoundaryConditions,FUEL_SYSTEM_LEGACY
from hazardia.io import load,write_new,verify_asset,HazardError

@njit(parallel=True)
def seed_worker(seed,n):
    proof=np.empty(n)
    for i in prange(n):
        np.random.seed(seed+i);proof[i]=np.random.random()
    return proof

def run(root):
    req=load(root/'request.json');opt=req['options'];asset=next(v for v in req['assets'] if v['role']=='fire_arrays');path=verify_asset(root,asset)
    with np.load(path,allow_pickle=False) as values:
        dem=values['dem'];veg=values['veg'];speed=values['wind_speed_kmh'];direction=values['wind_dir_deg']
    expected=tuple(req['grid']['shape'])
    if any(v.shape!=expected for v in [dem,veg,speed,direction]) or any(not np.isfinite(v).all() for v in [dem,veg,speed,direction]):raise HazardError('INVALID_INPUT','Fire input shape/nonfinite values')
    if (veg!=opt['fuel_legacy']).any() or (speed<0).any() or (direction<0).any() or (direction>360).any():raise HazardError('INVALID_INPUT','Unsupported fuel/wind input')
    row,col=opt['ignition']
    if not (0<=row<expected[0] and 0<=col<expected[1]):raise HazardError('INVALID_INPUT','Ignition outside grid')
    if get_num_threads()!=1:raise HazardError('UNSUPPORTED_CONFIGURATION','Only tested one-thread RNG policy enabled')
    def model(seconds,prime=False):
        m=Propagator(dem=dem,veg=veg,cellsize=req['grid']['transform'][0],realizations=opt['realizations'],fuels=FUEL_SYSTEM_LEGACY,do_spotting=False,out_of_bounds_mode='raise')
        m.set_boundary_conditions(BoundaryConditions(time=0,ignitions=[(row,col)],wind_speed=speed,wind_dir=direction,moisture=np.full_like(dem,opt['moisture_percent'])))
        m.step(seconds=seconds);return m
    # Prime the actual worker context before setting Numba per-worker RNG state.
    model(1,True);proof=seed_worker(opt['seed'],1).tolist();m=model(opt['duration_s']);prob=m.compute_fire_probability()
    np.savez(root/'fire-output.npz',probability=prob,fire=m.fire,arrival=m.arrival_time)
    write_new(root/'fire-native-result.json',dict(seed=opt['seed'],worker_seed_proof=proof,threads=1,spotting=False,moisture_native_unit='percent',wind_native_unit='km/h',wind_direction='meteorological FROM, clockwise north; upstream NEIGHBOURS_ANGLE convention',duration_s=opt['duration_s'],probability_shape=list(prob.shape),realizations=opt['realizations']))

if __name__=='__main__':
    root=Path(sys.argv[1])
    try:run(root)
    except Exception as exc:
        write_new(root/'worker-error.json',dict(code=exc.code if isinstance(exc,HazardError) else 'FIRE_ERROR',message=str(exc)));raise
