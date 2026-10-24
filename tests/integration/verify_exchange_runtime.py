"""Frozen CIMA replays through an isolated real JobStore and exchange adapters.
Linux geo environment only. Never edits the dashboard DB, archives or workspace.
"""
import argparse
import copy
import datetime as dt
import json
from pathlib import Path
import platform
import subprocess
import time
from hazardia.io import load,sha256,write_new,verify_asset,timestamp
from hazardia.jobs import JobStore
from hazardia.exchange import validate_product,check_compatibility
from hazardia.adapters.legacy_exchange import export_legacy_product


def requirement(product):
    return dict(schema='hazardia.exchange-requirement/0.1.0',domain_id=product['domain_id'],allowed_origins=['SIMULATED'],allowed_qualifications=['UNQUALIFIED_RESEARCH'],grid=copy.deepcopy(product['grid']),time=dict(valid_from=product['time']['valid_from'],valid_until=product['time']['valid_until'],as_of=product['time']['available_at']['value']),variables=[dict(id=v['id'],quantity=v['quantity'],unit=v['unit'],support=v['support'],accepted_uncertainty=[v['uncertainty']['kind']],require_known_calibration=False,minimum_members=None) for v in product['variables']],require_known_license=False,maximum_age_s=0)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',required=True);ap.add_argument('--output',required=True);ap.add_argument('--fire',required=True);ap.add_argument('--flood',required=True);ap.add_argument('--studio',required=True);ap.add_argument('--case',choices=['fire','flood','studio']);a=ap.parse_args()
    assert platform.system()=='Linux'
    import numpy as np
    import rasterio
    root=Path(a.runtime).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    cases=[dict(name='fire',job=a.fire),dict(name='flood',job=a.flood),dict(name='studio',job=a.studio)]
    if a.case:cases=[c for c in cases if c['name']==a.case]
    source=Path(__file__).resolve().parents[2]
    protocol=dict(scope='NATIVE_TECHNICAL_REGRESSION_AND_METADATA_ONLY',cases=cases,source_files={str(p.relative_to(source)):sha256(p) for p in [source/'src/hazardia/adapters/pipeline.py',source/'src/hazardia/adapters/legacy_exchange.py',*sorted((source/'src/hazardia/exchange').glob('*.py')),*sorted((source/'src/hazardia/schemas').glob('exchange_*.json'))] if not p.name.startswith('._')},baseline_inputs={},hypotheses=['Existing request/product bytes and native behavior preserved','New sidecar matches validated legacy metadata and hashes','Common consumer rejects wrong units and refuses unknown required license','Main dashboard job DB and archived data untouched'],python=__import__('sys').version,platform=platform.platform(),script_sha256=sha256(__file__))
    for c in cases:
        folder=root/'jobs'/c['job'];protocol['baseline_inputs'][c['job']]={n:sha256(folder/n) for n in ['request.json','runtime.json','product.json']}
    write_new(out/'protocol.json',protocol);results=[]
    for case in cases:
        old=root/'jobs'/case['job'];request=load(old/'request.json');store=JobStore(out/(case['name']+'-jobs'),old/'runtime.json');started=time.monotonic();ident=store.submit(copy.deepcopy(request),old);result=store.work_once();folder=store.root/ident
        assert result['state']=='SUCCEEDED',result
        legacy=load(folder/'product.json');product=load(folder/'exchange-product.json');validate_product(product,folder)
        manifest=load(folder/'manifest.json');assert manifest['artifacts']['exchange-product.json']==sha256(folder/'exchange-product.json')
        assert product==export_legacy_product(folder,available_at=product['time']['available_at']['value'])
        assert product['time']['source_cutoff']==request['snapshot_at'] and product['time']['available_at']['state']=='KNOWN'
        assert product['provenance']['license']['state']=='UNKNOWN'
        assert [(v['id'],v['unit'],v['asset']['sha256']) for v in product['variables']]==[(v['name'],v['unit'],v['sha256']) for v in legacy['layers']]
        need=requirement(product);compatible=check_compatibility(product,need,root=folder);assert compatible['status']=='COMPATIBLE'
        need['require_known_license']=True;assert check_compatibility(product,need,root=folder)['status']=='UNKNOWN'
        need=requirement(product);need['variables'][0]['unit']='INTENTIONALLY_WRONG';assert check_compatibility(product,need,root=folder)['status']=='INCOMPATIBLE'
        before=load(old/'product.json');checks={};diagnostics={}
        for new_layer,old_layer in zip(legacy['layers'],before['layers'],strict=True):
            with rasterio.open(verify_asset(folder,new_layer)) as x,rasterio.open(verify_asset(old,old_layer)) as y:
                av=x.read(1);bv=y.read(1);checks[new_layer['name']]=bool(x.crs==y.crs and x.transform==y.transform and np.array_equal(av,bv))
                if request['hazard']=='FLOOD':
                    valid=(av>=0)&(bv>=0);diagnostics=dict(changed_cells=int(np.count_nonzero(av!=bv)),max_abs_difference_m=float(np.abs(av[valid]-bv[valid]).max()),wet_mask_equal=bool(np.array_equal(av>0,bv>0)),maximum_equal=bool(av[valid].max()==bv[valid].max()))
        if request['hazard']=='FIRE':
            with np.load(folder/'fire-output.npz',allow_pickle=False) as x,np.load(old/'fire-output.npz',allow_pickle=False) as y:
                for key in y.files:checks[key]=bool(np.array_equal(x[key],y[key]))
            frames=load(old/'fire-native-result.json').get('frames',[])
            checks['all_probability_frames']=all(np.array_equal(np.load(folder/f['path'],allow_pickle=False)['probability'],np.load(old/f['path'],allow_pickle=False)['probability']) for f in frames)
            assert all(checks.values()),checks
        else:
            checks['HMC_bridge']=load(folder/'hmc-reflex-bridge.json')==load(old/'hmc-reflex-bridge.json');assert checks['HMC_bridge']
        record=dict(case=case['name'],isolated_job=ident,execution_status='PASS',exchange_status='PASS',manifest_hash_verified=True,compatibility='PASS',native_exact_comparison='PASS' if all(checks.values()) else 'FAIL',native_checks=checks,diagnostics=diagnostics,elapsed_s=time.monotonic()-started)
        results.append(record);write_new(out/(case['name']+'-verification.json'),record);print(json.dumps(record),flush=True)
    for job,hashes in protocol['baseline_inputs'].items():
        assert all(sha256(root/'jobs'/job/name)==h for name,h in hashes.items())
    write_new(out/'verification.json',dict(status='PASS',scope=protocol['scope'],cases=results))


if __name__=='__main__':main()
