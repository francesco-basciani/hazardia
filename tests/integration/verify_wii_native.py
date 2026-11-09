"""Genuine PROPAGATOR integration on a clearly synthetic ignition-process fixture.

Uses an isolated JobStore and existing frozen real-terrain/static-weather inputs.
This is NOT a validated ignition prediction or historical incident reconstruction.
"""
import argparse
import copy
import datetime as dt
import json
import math
from pathlib import Path

from hazardia.io import load,write_new,sha256,timestamp
from hazardia.jobs import JobStore


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();root=Path(args.runtime).resolve();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=False)
    import numpy as np
    from pyproj import Transformer
    from shapely.geometry import box,mapping
    from shapely.ops import transform
    from wii.scenarios import sample
    from wii.propagator import grid_cell,bind_prepared_request
    from wii.contracts import digest
    from hazardia.contracts import validate_request
    context=root/'runs/m1-abruzzo-20261015T161041Z';req=load(context/'fire-request.json')
    cfg=load(root/'runtime-v2.json');engine_before={p:sha256(p) for p in cfg['engine_files']}
    grid=req['grid'];a,b,c,d,e,f=grid['transform'];row,col=req['options']['ignition'];cx=c+a*(col+.5);cy=f+e*(row+.5)
    project=Transformer.from_crs(grid['crs'],3035,always_xy=True);back=Transformer.from_crs(3035,4326,always_xy=True)
    x,y=project.transform(cx,cy);x=math.floor(x/1000)*1000;y=math.floor(y/1000)*1000
    native=box(c,f+e*grid['shape'][0],c+a*grid['shape'][1],f)
    mask=box(x,y,x+1000,y+1000).intersection(transform(project.transform,native))
    begin=timestamp(req['valid_from']);end=begin+dt.timedelta(minutes=10);mu=.1
    product=dict(schema='hazardia.wii.probability/0.1.0',id='synthetic-native-test',model_id='SYNTHETIC_PROCESS_FIXTURE',
        issue_at=(begin-dt.timedelta(hours=1)).isoformat().replace('+00:00','Z'),
        available_at=(begin-dt.timedelta(minutes=59)).isoformat().replace('+00:00','Z'),valid_from=req['valid_from'],valid_until=end.isoformat().replace('+00:00','Z'),
        crs='EPSG:3035',cell_size_m=1000,cells=[dict(id='c',x=x,y=y,area_km2=mask.area/1e6,mu=mu,p=-math.expm1(-mu),features=[])],
        calibration=dict(status='EXPERIMENTAL_UNCALIBRATED',evidence=None,limitations='SYNTHETIC ADAPTER TEST ONLY; no true prediction'),
        provenance=dict(mask_geometry=mapping(mask),synthetic=True,context='Existing frozen retrospective terrain/weather, hypothetical ignition/fuel'),
        definition='P_AT_LEAST_ONE_WILDFIRE_IGNITION_PER_CELL_INTERVAL',process='CONDITIONAL_INDEPENDENT_POISSON')
    protocol=dict(scope='NATIVE_PROPAGATOR_TECHNICAL_TEST_SYNTHETIC_IGNITION_PROCESS',source_request_sha256=sha256(context/'fire-request.json'),
                  code={str(p):sha256(p) for p in Path(__import__('wii').__file__).parent.glob('*.py')},
                  product=product,seed=1729,engine_files=engine_before)
    write_new(out/'protocol.json',protocol)
    scenarios=sample(product,count=2,method='stratified',seed=1729,exploratory=True)
    member=scenarios['members'][1];assert member['event_count']==1 and scenarios['members'][0]['state']=='NO_IGNITION'
    origin=member['origins'][0];request=copy.deepcopy(req);request['id']='wii-native-fixture'
    request['valid_from']=origin['ignition_at'];request['valid_until']=(timestamp(origin['ignition_at'])+dt.timedelta(seconds=600)).isoformat().replace('+00:00','Z')
    request['options'].update(ignition=grid_cell(origin['point'],grid),duration_s=600,seed=member['propagation_seed'])
    validate_request(request,context);link=bind_prepared_request(request,scenarios,member['id'],context)
    write_new(out/'scenarios.json',scenarios);write_new(out/'bound-request.json',request)
    store=JobStore(out/'jobs',root/'runtime-v2.json');jobs=[]
    for _ in range(2):
        ident=store.submit(request,context);result=store.work_once();assert result['state']=='SUCCEEDED',result
        jobs.append(ident)
    arrays=[]
    for ident in jobs:
        with np.load(store.root/ident/'fire-output.npz',allow_pickle=False) as data:
            arrays.append({k:data[k].copy() for k in data.files})
    equal={k:bool(np.array_equal(arrays[0][k],arrays[1][k])) for k in arrays[0]};assert all(equal.values())
    link.update(job_id=jobs[0],manifest_sha256=sha256(store.root/jobs[0]/'manifest.json'),
                product_sha256=sha256(store.root/jobs[0]/'product.json'))
    write_new(out/'execution-link.json',link)
    assert engine_before=={p:sha256(p) for p in cfg['engine_files']}
    record=dict(status='PASS',scope=protocol['scope'],jobs=jobs,exact_array_replay=equal,
        no_event_weight=scenarios['members'][0]['weight'],no_event_job_created=False,
        sampled_origin=origin,native_row_column=request['options']['ignition'],link=link,
        engine_files_unchanged=True,scientific_validation='NOT_ESTABLISHED')
    write_new(out/'verification.json',record);print(json.dumps(record,indent=2))


if __name__=='__main__':main()
