"""VM-only source audit and conservative preservation for the HS repair protocol."""
import fcntl, hashlib, json, pathlib, shutil, sys, tarfile

H = pathlib.Path.home()
R = H / 'avalanche-runtime'
W = pathlib.Path('/dev/shm/hs-repair-20261101')
D = H / 'hazardia-runtime/web-assets/avalanche-gran-sasso-full'
W.mkdir(exist_ok=True)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def protected():
    m = json.loads((D / 'manifest.json').read_text())
    raw = (D / m['file']).read_bytes()
    assert sha(raw) == m['sha256']
    p = json.loads(raw)
    return m, {v['file'] for v in p['profile_assets'].values()}

def plan():
    m, keep = protected()
    files = [p for p in (D / 'assets').glob('*.json') if str(p.relative_to(D)) not in keep]
    inventory = {str(p.relative_to(D)): sha(p.read_bytes()) for p in files}
    result = dict(files=inventory, bytes=sum(p.stat().st_size for p in files), protected_manifest=m)
    (W / 'space-plan.json').write_text(json.dumps(result))
    with tarfile.open(W / 'inactive-assets.tgz', 'w:gz') as archive:
        for p in files: archive.add(p, arcname=str(p.relative_to(D)))
    print(json.dumps(dict(files=len(files), bytes=result['bytes'], archive_sha256=sha((W/'inactive-assets.tgz').read_bytes()))))

def move(host_sha):
    archive_sha = sha((W / 'inactive-assets.tgz').read_bytes())
    assert archive_sha == host_sha
    plan = json.loads((W/'space-plan.json').read_text())
    with (R/'worker.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        m, keep = protected()
        assert m == plan['protected_manifest']
        before = shutil.disk_usage(R).free
        with tarfile.open(W/'inactive-assets.tgz') as archive:
            for name, digest in plan['files'].items():
                assert name not in keep
                assert sha((D/name).read_bytes()) == digest == sha(archive.extractfile(name).read())
        for name, digest in plan['files'].items():
            target=W/'preserved-assets'/name; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(D/name),str(target)); assert sha(target.read_bytes()) == digest
        receipt=dict(before_free=before,after_free=shutil.disk_usage(R).free,archive_sha256=archive_sha,files=len(plan['files']),protected_manifest=m['sha256'],host_verified=True)
        (W/'space-receipt.json').write_text(json.dumps(receipt));print(json.dumps(receipt))

def sources():
    from hazardia_avalanche.worker import Refresh
    fetch=Refresh(R,R/'local-assessment/control')
    api='https://gitlabext.wsl.ch/api/v4/projects/snow-models%2Fsnowpack/repository/'
    for path in ['applications/snowpack']:
        raw=fetch.fetch(api+'tree?ref=Snowpack-3.7.0&per_page=100&path='+path,'hs-repair-tree',262144)
        tree=json.loads(raw);(W/(path.replace('/','-')+'-tree.json')).write_bytes(raw)
        for f in tree:
            if f['type']!='blob' or not f['name'].endswith(('.cc','.h')):continue
            data=fetch.fetch(api+'blobs/'+f['id']+'/raw','hs-repair-'+f['name'],524288)
            (W/f['name']).write_bytes(data)
    (W/'source-ledger.json').write_text(json.dumps(fetch.ledger,indent=2))
    print([p.name for p in W.glob('*.cc')])

if __name__=='__main__':
    if sys.argv[1]=='plan':plan()
    elif sys.argv[1]=='move':move(sys.argv[2])
    elif sys.argv[1]=='sources':sources()
