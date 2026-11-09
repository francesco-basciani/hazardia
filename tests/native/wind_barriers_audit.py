"""VM-only synthetic pinned-engine wind/barrier audit; not operational validation."""
import hashlib,json,os,pathlib,shutil,sys,time
if sys.platform!='linux':raise RuntimeError('VM only')
import numpy as np
from propagator.core import Propagator,BoundaryConditions,FUEL_SYSTEM_LEGACY
from hazardia.adapters.workers.fire import seed_worker
root=pathlib.Path('/home/hazardia/hazardia-runtime');out=root/'runs/wind-barriers-20261029';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
cfg=json.loads((root/'runtime-fire-studio.json').read_text());ws=root/'web-state/fire-workspace/workspace.json';before=sha(ws)
assert shutil.disk_usage(root).free>2*1024**3+20*1024**2
assert all(sha(p)==h for p,h in cfg['engine_files'].items())
n=201;center=100;cell=30;shape=(n,n);duration=7200;seed=1729;realizations=4
cases=[('calm',0,270,None),('from-west',18,270,None),('from-east',18,90,None),('strong-west',36,270,None),('full-barrier',18,270,'full'),('partial-barrier',18,270,'partial'),('late-barrier',18,270,'late')]
protocol=dict(run_id=out.name,qualification='SYNTHETIC_FLAT_UNIFORM_FUEL_TECHNICAL_TEST_NOT_FIELD_FORECAST',cases=cases,grid=[n,n],cell_m=cell,fuel=5,moisture_percent=10,duration_s=duration,seed=seed,realizations=realizations,spotting=False,barrier_column=103,partial_rows=[98,103],late_at_s=3600,schedule_s=[0,3600],workspace_sha256=before,engine_files=cfg['engine_files'],script_sha256=sha(__file__),hypotheses=['Reversing meteorological FROM wind reverses longitudinal spread centroid','Changing speed changes spread with all other inputs fixed','Full immediate nonfuel barrier prevents spread beyond it without spotting','Partial barrier can be bypassed; late action cannot erase past arrivals'])
(out/'protocol.json').write_text(json.dumps(protocol,indent=2))
dem=np.zeros(shape,np.float32);veg=np.full(shape,5,np.int16);none=np.full(shape,np.nan,np.float32)
def model(speed,direction,barrier):
 m=Propagator(dem=dem,veg=veg.copy(),cellsize=cell,realizations=realizations,fuels=FUEL_SYSTEM_LEGACY,do_spotting=False,out_of_bounds_mode='raise')
 f=none.copy();late=none.copy()
 if barrier=='full':f[:,103]=FUEL_SYSTEM_LEGACY.get_non_vegetated()
 if barrier=='partial':f[98:103,103]=FUEL_SYSTEM_LEGACY.get_non_vegetated()
 if barrier=='late':late[:,103]=FUEL_SYSTEM_LEGACY.get_non_vegetated()
 m.set_boundary_conditions(BoundaryConditions(time=0,ignitions=[(center,center)],wind_speed=speed,wind_dir=direction,moisture=10,vegetation_changes=f))
 m.set_boundary_conditions(BoundaryConditions(time=3600,vegetation_changes=late));return m
model(18,270,None).step(seconds=1)
result={};arrays={}
for name,speed,direction,barrier in cases:
 seed_worker(seed,1);m=model(speed,direction,barrier);start=time.monotonic();m.step(seconds=3600);prefix=m.compute_fire_probability().copy();m.step(seconds=3600);p=m.compute_fire_probability();arrays[name]=p.copy();ys,xs=np.indices(shape);mass=float(p.sum())
 edge=bool((p[0]>0).any() or (p[-1]>0).any() or (p[:,0]>0).any() or (p[:,-1]>0).any())
 result[name]=dict(seconds=time.monotonic()-start,area_ha=mass*cell*cell/10000,east_centroid_m=float(((xs-center)*p).sum()/mass*cell),north_centroid_m=float(((center-ys)*p).sum()/mass*cell),east_of_barrier_cells=int((p[:,104:]>0).sum()),barrier_burned_cells=int((p[:,103]>0).sum()),before_late_east_cells=int((prefix[:,104:]>0).sum()),edge_reached=edge,probability_sha256=hashlib.sha256(p.tobytes()).hexdigest())
 np.savez_compressed(out/(name+'.npz'),probability=p,prefix=prefix)
 (out/'progress.json').write_text(json.dumps(result,indent=2));print(name,json.dumps(result[name]),flush=True)
checks=dict(west_pushes_east=result['from-west']['east_centroid_m']>0,east_pushes_west=result['from-east']['east_centroid_m']<0,speed_changes_output=not np.array_equal(arrays['strong-west'],arrays['from-west']),complete_immediate_barrier_blocks=result['full-barrier']['east_of_barrier_cells']==0,partial_can_be_bypassed=result['partial-barrier']['east_of_barrier_cells']>0,late_does_not_erase_prior_arrivals=result['late-barrier']['before_late_east_cells']>0 and result['late-barrier']['east_of_barrier_cells']>=result['late-barrier']['before_late_east_cells'],no_domain_exit=not any(r['edge_reached'] for r in result.values()),workspace_preserved=sha(ws)==before,engine_pins_preserved=all(sha(p)==h for p,h in cfg['engine_files'].items()))
summary=dict(cases=result,checks=checks,status='PASS' if all(checks.values()) else 'FAIL',qualification=protocol['qualification']);(out/'verification.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if not all(checks.values()):sys.exit(1)
