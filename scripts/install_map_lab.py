"""Optional VM-only Cesium trial asset bootstrap from official pinned npm package.
No npm install scripts, keys, privileged dependencies or main-map migration.
"""
import argparse,hashlib,io,json,tarfile,urllib.request
from pathlib import Path
VERSION='1.138.0'
def main():
    p=argparse.ArgumentParser();p.add_argument('--assets',required=True);a=p.parse_args();target=Path(a.assets)/'vendor/cesium';target.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(f'https://registry.npmjs.org/cesium/{VERSION}',timeout=15) as r:meta=json.load(r)
    with urllib.request.urlopen(meta['dist']['tarball'],timeout=30) as r:raw=r.read(32*1024**2+1)
    if len(raw)>32*1024**2:raise SystemExit('Package exceeds trial cap')
    import base64
    actual='sha512-'+base64.b64encode(hashlib.sha512(raw).digest()).decode()
    if actual!=meta['dist']['integrity']:raise SystemExit('npm integrity mismatch')
    count=0
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tar:
        for m in tar:
            prefix='package/Build/Cesium/'
            if m.isfile() and m.name in ['package/LICENSE.md','package/CHANGES.md','package/ThirdParty.extra.json']:
                (target/Path(m.name).name).write_bytes(tar.extractfile(m).read())
            if m.isfile() and m.name.startswith(prefix):
                rel=m.name[len(prefix):];path=(target/rel).resolve()
                if not path.is_relative_to(target.resolve()):raise SystemExit('Unsafe archive member')
                path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(tar.extractfile(m).read());count+=1
    (target/'HAZARDIA-PIN.json').write_text(json.dumps(dict(version=VERSION,integrity=actual,bytes=len(raw),files=count),indent=2));print('Cesium',VERSION,'verified bytes',len(raw),'files',count)
if __name__=='__main__':main()
