"""Reconstruct the research runtime from public source + pinned inputs inside Linux.
Never runs sudo, changes a live runtime, starts a service, or dispatches real actions.
"""
import argparse,datetime,hashlib,json,os,platform,shutil,subprocess,sys,tarfile,tempfile,urllib.request
from pathlib import Path
APP=Path(__file__).resolve().parents[1]

def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        if read(p)!=value:raise RuntimeError('Refusing overwrite: '+str(p))
    else:p.write_text(json.dumps(value,indent=2,allow_nan=False))
def command(args,env=None):
    print('+',' '.join(map(str,args)),flush=True);subprocess.run(list(map(str,args)),check=True,cwd=APP,env=env)
def environment(root):
    return dict(os.environ,PYTHONPATH=str(APP/'src'),PROJ_LIB='/usr/share/proj',NUMBA_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',GRASS_ADDON_BASE=str(root/'engines/grass-addons'))
def fetch(url,dest,digest,cap,reuse=None):
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        if sha(dest)!=digest:raise RuntimeError('Cached checksum mismatch: '+str(dest))
        return
    if reuse and Path(reuse).is_file():
        if sha(reuse)!=digest:raise RuntimeError('Reuse checksum mismatch: '+str(reuse))
        shutil.copyfile(reuse,dest);return
    pending=dest.with_suffix('.partial')
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HAZARDIA-repro/1'}),timeout=60) as response,pending.open('xb') as out:
            if int(response.headers.get('Content-Length',0))>cap:raise RuntimeError('Payload cap exceeded')
            count=0
            while True:
                data=response.read(min(1024**2,cap-count+1))
                if not data:break
                count+=len(data)
                if count>cap:raise RuntimeError('Payload cap exceeded')
                out.write(data)
        if sha(pending)!=digest:raise RuntimeError('Source drift: '+url)
        pending.replace(dest)
    finally:pending.unlink(missing_ok=True)
def unpack(archive,dest):
    dest=Path(dest)
    if dest.exists():return
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp,tarfile.open(archive) as tar:
        if not hasattr(tarfile,'data_filter'):raise RuntimeError('Python tarfile security update required; do not bypass filtering')
        # The standalone Python distribution contains optional terminfo symlinks
        # that fail safe extraction. Omit that terminal-only database; retain
        # strict data filtering for every extracted file. Ubuntu supplies terminfo.
        members=[m for m in tar.getmembers() if '/share/terminfo/' not in m.name]
        tar.extractall(tmp,members=members,filter='data');contents=list(Path(tmp).iterdir())
        if len(contents)!=1 or not contents[0].is_dir():raise RuntimeError('Archive requires one root directory')
        shutil.move(str(contents[0]),dest)
def preflight(root):
    if platform.system()!='Linux' or platform.machine() not in ['aarch64','arm64']:raise RuntimeError('Reference installer requires Linux ARM64; Mac is only UTM host/display')
    release=Path('/etc/os-release').read_text()
    if 'VERSION_ID="22.04"' not in release or 'ID=ubuntu' not in release:raise RuntimeError('Reference OS is Ubuntu 22.04')
    if root/'app'!=APP:raise RuntimeError('Clone repository at RUNTIME/app; --runtime must be its parent')
    if os.geteuid()==0:raise RuntimeError('Run unprivileged; system prerequisites are a separate reviewed sudo step')
    for name in ['gfortran','make','gcc','nf-config','grass','curl','git']:
        if not shutil.which(name):raise RuntimeError('Missing '+name+'; review infra/guest/install-system.sh')
    command(['/usr/bin/python3','-c','import numpy,scipy,pandas,geopandas,rasterio,xarray,numba,netCDF4,rtree,skimage,PIL,jsonschema,osgeo.gdal; print("System geospatial imports PASS")'])
    if shutil.disk_usage(root).free<3*1024**3:raise RuntimeError('At least 3 GiB free disk required for reconstruction')
def install(root,args):
    eng=root/'engines/upstream';eng.mkdir(parents=True,exist_ok=True);logs=root/'installation';logs.mkdir(exist_ok=True);env=environment(root)
    if (logs/'installed.json').exists():
        print('Existing installation: run verify; not reinstalling automatically');return
    pins=read(APP/'reproducibility/sources.lock.json')
    for key,s in pins.items():
        archive=root/'downloads'/(key+'.tar.gz');reuse=Path(args.archive_cache)/(key+'.tar.gz') if args.archive_cache else None
        fetch(s['url'],archive,s['sha256'],s['cap'],reuse);unpack(archive,eng/s['directory'])
    for name,python,system,requirements in [('core-env','/usr/bin/python3',True,None),('fire-env',eng/'python312/bin/python3',False,'fire.txt'),('reflex-env','/usr/bin/python3',True,'geo-extra.txt'),('decision-env','/usr/bin/python3',False,'decision.txt')]:
        # Engines keep the historical relative environment layout expected by configure_runtime.
        dest=root/name if name in ['core-env','decision-env'] else eng/name
        if not (dest/'bin/python').exists():command([python,'-m','venv']+(['--system-site-packages'] if system else [])+[dest],env)
        if name=='core-env':
            command([dest/'bin/python','-m','pip','install','setuptools==69.5.1','wheel==0.43.0'],env)
            command([dest/'bin/python','-m','pip','install','--no-build-isolation','--no-deps','-e',APP],env)
        if requirements:command([dest/'bin/python','-m','pip','install']+(['--no-deps'] if name=='reflex-env' else ['--only-binary=:all:'])+['-r',APP/'requirements'/requirements],env)
        with (logs/(name+'-freeze.txt')).open('w') as f:subprocess.run([str(dest/'bin/python'),'-m','pip','freeze','--all'],stdout=f,check=True)
    binary=eng/'hmc-bin/HMC_Model_V3_Exec.x'
    if not binary.exists():
        binary.parent.mkdir(exist_ok=True)
        command(['bash',eng/'hmc-src/configure.sh',eng/'hmc-src','/usr',binary.parent,'true'],dict(env,NETCDF_DIR='/usr'))
    addon=root/'engines/grass-addons';addon.mkdir(exist_ok=True)
    for name in ['r.stream.basins','r.stream.order','r.stream.distance','r.accumulate']:
        if not (addon/'bin'/name).exists():command(['grass','--tmp-location','EPSG:4326','--exec','g.extension','extension='+name,'url='+str(eng/'grass-addons-src/src/raster'/name),'prefix='+str(addon)],env)
    sources={}
    for name in ['fire-src','hmc-src','reflex-src']:
        for p in (eng/name).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.o','.mod','.x']:sources[str(p.relative_to(eng))]=sha(p)
    write(eng/'expected-guest-source-hashes.json',sources)
    command([root/'core-env/bin/python',APP/'scripts/configure_runtime.py','--root',root,'--engine-root',eng,'--output','runtime-v2.json','--core-python',root/'core-env/bin/python','--grass-addon-base',addon],env)
    write(logs/'installed.json',dict(status='PASS',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Dependency installation/configuration; native execution tested separately',source_pins=pins))
def core(root,*args):command([root/'core-env/bin/python',*args],environment(root))
def geo(root,*args):command([read(root/'runtime-v2.json')['geo_python'],*args],environment(root))
def demo(root,args):
    from_boot=APP/'reproducibility/snapshots';m1=root/'runs/m1-abruzzo-20261015T161041Z';m1.mkdir(parents=True,exist_ok=True)
    if (root/'installation/demo.json').exists():print('Demo already generated; use verify');return
    for name in ['plan.json','dem-item.json','sentinel-item.json','weather.json']:
        src=from_boot/'abruzzo'/name;dest=m1/name
        if not dest.exists():shutil.copyfile(src,dest)
        elif sha(dest)!=sha(src):raise RuntimeError('Snapshot drift: '+name)
    cache=m1/'cache';cache.mkdir(exist_ok=True)
    for item in read(from_boot/'inputs.lock.json'):
        name=item['name']
        if name.startswith('leaflet/'):
            out=root/'runs/m3-dashboard-20261015T192310Z/vendor'/Path(name).name
            reuse=Path(args.input_cache)/name if args.input_cache else None
        else:
            out=cache/name;reuse=Path(args.input_cache)/name if args.input_cache else None
        fetch(item['url'],out,item['sha256'],item['bytes']+1024,reuse)
        if not name.startswith('leaflet/') and not (cache/(name+'.source.json')).exists():
            now=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
            write(cache/(name+'.source.json'),dict(url=item['url'],sha256=item['sha256'],bytes=out.stat().st_size,available_at=now,fetched_at=now,mode='HASH_VERIFIED_REUSE' if reuse and reuse.exists() else 'HTTPS_ACQUISITION',license=item['license']))
    if not (m1/'preparation-result.json').exists():geo(root,APP/'scripts/prepare_abruzzo.py','--root',m1)
    code='''from hazardia.jobs import JobStore
from hazardia.io import load,write_new
from pathlib import Path
import sys
r=Path(sys.argv[1]);m=r/'runs/m1-abruzzo-20261015T161041Z';s=JobStore(r/'jobs',r/'runtime-v2.json');done=[]
for hazard in ['fire','flood']:
 record=m/(hazard+'-bootstrap-job.json')
 if record.exists():
  job=load(record)['id'];result=s.get(job)
 else:
  req=load(m/(hazard+'-request.json'))
  if hazard=='fire':req['options']['duration_s']=3600;req['valid_until']='2024-07-13T14:00:00Z'
  else:req['valid_from']='2024-07-13T13:00:00Z';req['valid_until']='2024-07-13T19:00:00Z'
  job=s.submit(req,m);write_new(record,dict(id=job));result=s.work_once()
 if result['state']!='SUCCEEDED':raise RuntimeError(str(result))
 done.append(dict(hazard=hazard,id=job,state=result['state']))
write_new(r/'installation/demo-jobs.json',done)
'''
    core(root,'-c',code,root)
    write(root/'m3-plan.json',dict(run_id='m3-dashboard-20261015T192310Z',meaning='Compatibility fixture layout regenerated by bootstrap, not original execution time'))
    geo(root,APP/'scripts/build_dashboard_data.py','--runtime',root)
    shutil.copyfile(from_boot/'map-context.json',root/'web-assets/map-context.json')
    write(root/'installation/demo.json',dict(status='PASS',scope='Two genuine CIMA executions on frozen research inputs, not historical skill',at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
def days(root,args):
    geo(root,APP/'reproducibility/prepare_days.py','--runtime',root)
    cfg=read(root/'runtime-v2.json');run=root/'runs/physical-days-20261016T040414Z/expanded';env=environment(root);env['PYTHONPATH']+=os.pathsep+cfg['fire_source']
    for case in ['noop','fuelbreak']:
        if not (run/(case+'-result.json')).exists():command([cfg['fire_python'],APP/'reproducibility/run_fire_days.py',run,case],env)
    geo(root,APP/'scripts/build_physical_fire_lab.py','--runtime',root,'--run',run.parent)
def verify(root,args):
    core(root,APP/'reproducibility/verify_installation.py','--runtime',root)
    for directory in ['unit','domain','decision','web']:core(root,'-m','unittest','discover','-s',APP/'tests'/directory,'-v')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['preflight','install','demo','days','verify']);p.add_argument('--runtime',required=True);p.add_argument('--archive-cache');p.add_argument('--input-cache');args=p.parse_args();root=Path(args.runtime).expanduser().resolve();root.mkdir(parents=True,exist_ok=True)
    preflight(root)
    if args.stage!='preflight':globals()[args.stage](root,args)
if __name__=='__main__':main()
