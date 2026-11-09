"""VM-only paired regression: exact pinned inputs, native actions and per-unit receipts."""
import copy,hashlib,json,os,pathlib,shutil,subprocess,sys,time
if sys.platform!='linux':raise RuntimeError('VM only')
root=pathlib.Path('/home/hazardia/hazardia-runtime');source=root/'runs/fire-interventions-20261026';out=root/'runs/fire-action-receipts-20261028'
if shutil.disk_usage(root).free<2*1024**3+100*1024**2:raise RuntimeError('2GiB reserve plus bounded run allowance required')
out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((root/'runtime-fire-studio.json').read_text());ws=root/'web-state/fire-workspace/workspace.json';before=sha(ws)
cases=['no-intervention','native-canadair','ideal-fuel-barrier','native-far-control','native-ground']
protocol={'run_id':out.name,'qualification':'FROZEN_CONDITIONAL_SOFTWARE_REGRESSION_NOT_CURRENT_FORECAST','cases':cases,'seed':1729,'hours':6,'realizations':2,'resource_time_minutes':30,'source':str(source),'workspace_sha256':before,'engine_pins_checked':len(cfg['engine_files']),'hypotheses':['Unchanged four existing cases reproduce every probability frame','Native ground action affects only post-activation propagation on this fixture','Per-unit receipt footprints are nonempty and distant control leaves output unchanged'],'code_sha256':{n:sha(root/'app/src/hazardia/adapters/workers'/n) for n in ['fire_studio.py','fire_action_receipts.py']}}
assert all(sha(pathlib.Path(p))==h for p,h in cfg['engine_files'].items())
(out/'protocol.json').write_text(json.dumps(protocol,indent=2))
summary={'cases':{},'checks':{}}
env=dict(os.environ,PYTHONPATH=str(root/'app/src')+':'+cfg['fire_source'],PROJ_LIB='/usr/share/proj',NUMBA_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
for name in cases:
 template=source/('native-canadair' if name=='native-ground' else name);folder=out/name;folder.mkdir();req=json.loads((template/'request.json').read_text())
 for asset in req['assets']:
  src=template/asset['path'];dest=folder/asset['path'];dest.parent.mkdir(parents=True,exist_ok=True);assert sha(src)==asset['sha256']
  if asset['role']=='fire_plan':
   plan=json.loads(src.read_text())
   if name=='native-ground':plan['resources'][0]['category']='waterline_action'
   dest.write_text(json.dumps(plan));asset['sha256']=sha(dest)
  else:os.link(src,dest)
 (folder/'request.json').write_text(json.dumps(req));start=time.monotonic()
 with (folder/'stdout.log').open('w') as log:
  subprocess.run([cfg['fire_python'],'-m','hazardia.adapters.workers.fire',str(folder)],cwd=root/'app',env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
 native=json.loads((folder/'fire-native-result.json').read_text());summary['cases'][name]={'seconds':time.monotonic()-start,'final_ha':native['frames'][-1]['expected_area_ha'],'receipts':[r for e in native['consumed_events'] for r in e['resource_receipts']]}
 if name!='no-intervention':assert summary['cases'][name]['receipts'][0]['affected_cells']>0
 (out/'progress.json').write_text(json.dumps(summary,indent=2));print(name,summary['cases'][name],flush=True)
import numpy as np
load=lambda folder,f:np.load(folder/f,allow_pickle=False)['probability']
base=out/'no-intervention';native=json.loads((base/'fire-native-result.json').read_text());frames=native['frames']
for name in cases:
 folder=out/name;diff=int(np.count_nonzero(load(folder,'fire-output.npz')!=load(base,'fire-output.npz')));summary['cases'][name]['changed_probability_cells']=diff
 summary['checks'][name+'_pre_activation_identical']=all(np.array_equal(load(folder,f['path']),load(base,f['path'])) for f in frames if f['elapsed_s']<=1800)
 if name!='native-ground':summary['checks'][name+'_unchanged_from_previous_worker']=all(np.array_equal(load(folder,f['path']),load(source/name,f['path'])) for f in frames)
summary['checks']['distant_control_unchanged']=summary['cases']['native-far-control']['changed_probability_cells']==0
for name in ['native-canadair','native-ground','ideal-fuel-barrier']:summary['checks'][name+'_effect_after_activation']=summary['cases'][name]['changed_probability_cells']>0
summary['checks']['workspace_preserved']=sha(ws)==before
summary['checks']['engine_pins_preserved']=all(sha(pathlib.Path(p))==h for p,h in cfg['engine_files'].items())
summary['status']='PASS' if all(summary['checks'].values()) else 'FAIL';(out/'verification.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True);assert summary['status']=='PASS'
