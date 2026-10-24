"""Isolated native regression of existing jobs after opt-in catalog discovery.

Linux geo environment only. Reuses frozen request/runtime/assets; never submits
jobs to the application DB, fetches data, or edits an existing workspace. The
protocol is written before execution and result files are created exclusively.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--fire', required=True)
    ap.add_argument('--flood', required=True)
    ap.add_argument('--only', choices=['FIRE','FLOOD'])
    args = ap.parse_args()
    assert platform.system() == 'Linux'
    from hazardia.package_catalog import discover
    from hazardia.contracts import validate_request, validate_product
    from hazardia.io import verify_asset
    import numpy as np
    import rasterio
    root = Path(args.runtime).resolve()
    out = root / 'runs' / args.run_id
    out.mkdir()  # Never overwrite a prior run.
    source = Path(__file__).resolve().parents[2]
    protocol = dict(run_id=args.run_id, scope='NATIVE_TECHNICAL_REGRESSION_NOT_PHYSICAL_SKILL',
                    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
                    catalog=discover().describe(), source_files={},
                    cases=[dict(hazard='FIRE',job=args.fire),dict(hazard='FLOOD',job=args.flood)],
                    hypotheses=['Frozen same-seed fire native arrays are exactly unchanged',
                                'Frozen HMC discharge and REFlEx flood raster are exactly unchanged',
                                'Catalog does not change existing validators or pipeline'],
                    timeout_s_per_case=900, platform=platform.platform())
    if args.only:protocol['cases']=[c for c in protocol['cases'] if c['hazard']==args.only]
    protocol['verifier_sha256']=digest(Path(__file__))
    protocol['execution_source_files']={str(p.relative_to(source)):digest(p) for p in [source/'src/hazardia/adapters/pipeline.py',source/'src/hazardia/adapters/dispatch.py',source/'src/hazardia/package_catalog.py',*sorted((source/'src/hazardia/domain_packages').glob('*.json'))]}
    for case in protocol['cases']:
        baseline = root/'jobs'/case['job']
        for name in ['request.json','runtime.json','product.json']:
            protocol['source_files'][str(baseline/name)] = digest(baseline/name)
    with (out/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    results=[]
    for case in protocol['cases']:
        baseline=root/'jobs'/case['job'];target=out/case['hazard'].lower();target.mkdir()
        req=json.loads((baseline/'request.json').read_bytes());cfg=json.loads((baseline/'runtime.json').read_bytes())
        assert req['hazard']==case['hazard']
        for name in ['request.json','runtime.json']:shutil.copy2(baseline/name,target/name)
        for asset in req['assets']:
            src=verify_asset(baseline,asset);dest=target/asset['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        validate_request(req,target)
        env=dict(os.environ,PYTHONPATH=str(source/'src'),PROJ_LIB='/usr/share/proj',NUMBA_NUM_THREADS='1',OMP_NUM_THREADS='1')
        if cfg.get('grass_addon_base'):env['GRASS_ADDON_BASE']=cfg['grass_addon_base']
        start=time.monotonic()
        with (target/'pipeline.log').open('xb') as log:
            p=subprocess.run([cfg['core_python'],'-m','hazardia.adapters.pipeline',str(target)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900)
        assert p.returncode==0,str(target/'pipeline.log')
        product=json.loads((target/'product.json').read_bytes());validate_product(product,req,target)
        old=json.loads((baseline/'product.json').read_bytes());checks={}
        assert product['engine']==old['engine']
        receipt=json.loads((target/'adapter-binding.json').read_bytes())
        assert receipt['package']['legacy_hazard']==case['hazard']
        assert receipt['request_sha256']==digest(target/'request.json') and receipt['runtime_sha256']==digest(target/'runtime.json')
        checks['catalog_binding_receipt']=True
        for layer,previous in zip(product['layers'],old['layers'],strict=True):
            assert layer['name']==previous['name'] and layer['unit']==previous['unit']
            with rasterio.open(verify_asset(target,layer)) as a,rasterio.open(verify_asset(baseline,previous)) as b:
                checks[layer['path']]=bool(a.crs==b.crs and a.transform==b.transform and np.array_equal(a.read(),b.read()))
        if case['hazard']=='FIRE':
            with np.load(target/'fire-output.npz',allow_pickle=False) as a,np.load(baseline/'fire-output.npz',allow_pickle=False) as b:
                checks.update({key:bool(np.array_equal(a[key],b[key])) for key in b.files})
            native=json.loads((baseline/'fire-native-result.json').read_bytes())
            frames=native.get('frames',[])
            checks['all_studio_probability_frames']=all(np.array_equal(np.load(target/f['path'],allow_pickle=False)['probability'],np.load(baseline/f['path'],allow_pickle=False)['probability']) for f in frames)
        else:
            checks['HMC_REFlEx_discharge_bridge']=json.loads((target/'hmc-reflex-bridge.json').read_bytes())==json.loads((baseline/'hmc-reflex-bridge.json').read_bytes())
        results.append(dict(hazard=case['hazard'],baseline_job=case['job'],elapsed_s=time.monotonic()-start,checks=checks,status='PASS' if all(checks.values()) else 'FAIL'))
        with (out/(case['hazard'].lower()+'-verification.json')).open('x') as f:json.dump(results[-1],f,indent=2)
        print(json.dumps(results[-1]),flush=True)
    assert all(digest(Path(p))==h for p,h in protocol['source_files'].items())
    with (out/'verification.json').open('x') as f:json.dump(dict(results=results,status='PASS' if all(r['status']=='PASS' for r in results) else 'FAIL'),f,indent=2)
    assert all(r['status']=='PASS' for r in results)


if __name__ == '__main__':main()
