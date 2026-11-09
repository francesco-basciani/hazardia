"""Explicit dry-fuel sensitivity following the preserved no-exposed-target result."""
import copy,json,os,pathlib,sys,uuid
if sys.platform!='linux':raise RuntimeError('VM only')
from hazardia.io import load,write_new,sha256
from hazardia.jobs import JobStore
r=pathlib.Path('/home/hazardia/hazardia-runtime');old=r/'runs/castelli-plan-20261028';out=r/'runs/castelli-dry-v2-plan-20261028';out.mkdir(exist_ok=False)
previous=load(old/'baseline.json');source=r/'jobs'/previous['job_id'];req=load(source/'request.json');s=load(source/'fire-series.json');plan=copy.deepcopy(s['plan']);plan['forcing']['moisture_model']='MANUAL';plan['forcing']['version']='distributed/1';plan['forcing'].pop('initialization',None);req['id']='castelli-dry-reference-'+uuid.uuid4().hex
req['assumptions']+=['EXPLICIT DRY-FUEL SENSITIVITY: uniform manual10percent fuel moisture, not a measured value; hourly hFFMC estimation disabled','Source wind still distributed hourly real frozen18Oct2026 forecast; not a current forecast or observed fire']
protocol=load(old/'protocol.json');protocol.update(run_id=out.name,parent_run=old.name,parent_baseline_job=previous['job_id'],negative_control='HFFMC baseline0.585ha and NO_EXPOSED_ASSETS preserved in parent',hypothesis='Manual10percent dry-fuel scenario with same ignition/terrain/wind; no synthetic relocation of assets or numerical suppression',fuel_moisture=dict(model='MANUAL',percent=10,measured=False,weather_hffmc=False));write_new(out/'protocol.json',protocol);os.link(old/'assets.json',out/'assets.json')
stage=out/'baseline-input';stage.mkdir()
for a in req['assets']:
 src=source/a['path'];assert sha256(src)==a['sha256'];dest=stage/a['path'];dest.parent.mkdir(parents=True,exist_ok=True)
 if a['role']=='fire_plan':write_new(dest,plan)
 else:os.link(src,dest)
 a['sha256']=sha256(dest)
store=JobStore(r/'jobs',r/'runtime-fire-studio.json');job=store.submit(req,stage);write_new(out/'baseline.json',dict(job_id=job,request=req));print(json.dumps(dict(job_id=job,out=str(out))))
