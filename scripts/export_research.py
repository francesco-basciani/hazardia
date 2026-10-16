"""Local-only bounded research supplement; never packages credentials or public uploads."""
import argparse,datetime,hashlib,json,os,shutil,sqlite3,subprocess,tarfile
from pathlib import Path
from hazardia.io import load,write_new,sha256,utcnow
RUNS=['m3-dashboard-20261015T192310Z','m4-joint-20261015T194711Z','m5-adaptive-20261015T195150Z','m6-degradation-20261015T200034Z','m7-verification-20261015T200759Z']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--name',required=True);a=ap.parse_args();root=Path(a.runtime).resolve();assert a.name.replace('-','').isalnum();out=root/'exports'/a.name;out.mkdir(parents=True,exist_ok=False);app=Path(__file__).resolve().parents[1];cutoff=utcnow();copies=[]
    def copy(source,relative):
        source=Path(source);target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);before=sha256(source);shutil.copyfile(source,target);assert sha256(source)==before==sha256(target),'Source changed during copy: '+str(source);copies.append(dict(path=str(relative),bytes=target.stat().st_size,sha256=before))
    for ident in RUNS:
        parent=root/'runs'/ident
        for p in sorted(parent.rglob('*')):
            if p.is_file() and 'replay-checkout' not in p.parts and not p.name.endswith(('-journal','-wal','-shm')):copy(p,Path('runs')/ident/p.relative_to(parent))
    cfg=load(root/'runtime-v2.json');assert all(sha256(p)==h for p,h in cfg['engine_files'].items());copy(root/'runtime-v2.json',Path('runtime-v2.json'))
    for p in sorted((root/'web-assets').rglob('*')):
        if p.is_file():copy(p,Path('web-assets')/p.relative_to(root/'web-assets'))
    # A consistent SQLite backup, and only terminal job directories: never claim running logs immutable.
    with sqlite3.connect(root/'jobs/jobs.sqlite') as db:
        (out/'jobs').mkdir(exist_ok=True)
        with sqlite3.connect(out/'jobs/jobs.sqlite') as dest:
            db.backup(dest);rows=dest.execute('SELECT id,state FROM jobs ORDER BY id').fetchall()
        assert not any(state in ['RUNNING','QUEUED'] for _,state in rows),'User jobs active at backup snapshot: defer evidence export'
    for ident,state in rows:
        parent=root/'jobs'/ident
        for p in sorted(parent.rglob('*')):
            if p.is_file():copy(p,Path('jobs')/ident/p.relative_to(parent))
    for parent in sorted((root/'web-state').glob('decision-*')):
        if not (parent/'response.json').exists() or not (parent/'context.json').exists():continue
        for p in sorted(parent.rglob('*')):
            if p.is_file():copy(p,Path('web-state')/parent.name/p.relative_to(parent))
    for p in sorted((root/'web-state/research-replay').glob('event-*.json')):copy(p,Path('web-state/research-replay')/p.name)
    # Host evidence contains logs/screenshots/test scripts only; separate from VM scientific execution.
    host=root/'host-evidence-m3-m7'
    if host.exists():
        for p in sorted(host.rglob('*')):
            if p.is_file():copy(p,Path('host-client-evidence')/p.relative_to(host))
    subprocess.run(['git','bundle','create',str(out/'source.bundle'),'main','HEAD'],cwd=app,check=True)
    with (out/'source.tar').open('xb') as f:subprocess.run(['git','archive','--format=tar','--prefix=hazardia/','HEAD'],cwd=app,stdout=f,check=True)
    code=subprocess.check_output(['git','rev-parse','HEAD'],cwd=app,text=True).strip();dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=app,text=True);assert not dirty
    # Include every exported byte, including the DB backup/bundles created above.
    files=[dict(path=str(p.relative_to(out)),bytes=p.stat().st_size,sha256=sha256(p)) for p in sorted(out.rglob('*')) if p.is_file()]
    manifest=dict(schema_version='0.5.0',kind='research_supplement_manifest',created_at=utcnow(),snapshot_started_at=cutoff,git_sha=code,dirty=False,files=files,engine_files_unchanged=len(cfg['engine_files']),job_states=dict(rows),scope='Local supplement M3-M7, not a complete independently qualified research release',excluded=['SSH keys and host credentials','Raw large M1parent Sentinel/DSM/ERA5 cache; retained in original VM with hashes/locators','Original upstream source/dependency setup; pins/config/licenses retained, rebuild prerequisites remain','Operational/private external data'],parent_runs=['m1-abruzzo-20261015T161041Z','m2-domain-20261015T190836Z'],limitations=['No independent fresh-machine install validation','No calibrated historical fire/flood hindcast','M5realforecast integration and large-UI scaling gate not complete'])
    write_new(out/'MANIFEST.json',manifest)
    for r in files:assert sha256(out/r['path'])==r['sha256']
    archive=root/'exports'/(a.name+'.tar.gz')
    with tarfile.open(archive,'x:gz') as tar:tar.add(out,arcname=a.name)
    write_new(root/'exports'/(a.name+'-verification.json'),dict(status='PASS',files=len(files),manifest_sha256=sha256(out/'MANIFEST.json'),archive_sha256=sha256(archive),archive_bytes=archive.stat().st_size,expanded_bytes=sum(x['bytes'] for x in files),scope='Byte integrity/transport source, not scientific qualification'))
    print(json.dumps(load(root/'exports'/(a.name+'-verification.json')),indent=2));print(archive)
if __name__=='__main__':main()
