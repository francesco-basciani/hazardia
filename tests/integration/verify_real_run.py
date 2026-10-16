"""Offline content verification of real M1 artifacts. Execute in the Linux geo env.

Requires an independently saved PROPAGATOR.compute_arrival_time_min control array.
No fake engine is accepted here. Does not measure physical predictive accuracy.
"""
import argparse,ast,gzip,platform
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from netCDF4 import Dataset
from hazardia.io import load,write_new,sha256,verify_asset
from hazardia.contracts import validate,validate_request,validate_product,validate_observation

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--jobs',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    run=Path(a.run);jobs=Path(a.jobs);results=[]
    def check(name,fn):
        try:detail=fn();results.append(dict(name=name,status='PASS',detail=detail))
        except Exception as e:results.append(dict(name=name,status='FAIL',detail=type(e).__name__+': '+str(e)))
    fire=jobs/load(run/'final-fire-integration.json')['id'];flood=jobs/load(run/'shallow-flood-integration.json')['id']
    def products():
        assert platform.system()=='Linux'
        out=[]
        for directory in [fire,flood]:
            manifest=load(directory/'manifest.json');request=load(directory/'request.json');product=load(directory/'product.json')
            validate('run_manifest',manifest);validate_request(request,directory);validate_product(product,request,directory)
            assert manifest['status']=='SUCCEEDED' and manifest['error_code'] is None and manifest['code']['dirty'] is False
            assert manifest['environment']['fire_freeze'] and manifest['environment']['flood_freeze']
            assert manifest['code']['git_sha'] and manifest['seed']==request['options'].get('seed')
            for relative,digest in manifest['artifacts'].items():assert sha256(directory/relative)==digest,relative
            for layer in product['layers']:
                with rasterio.open(verify_asset(directory,layer)) as src:
                    data=src.read(1,masked=True).compressed();s=layer['statistics']
                    assert src.shape==tuple(request['grid']['shape']) and str(src.crs)==request['grid']['crs']
                    assert np.allclose(list(src.transform)[:6],request['grid']['transform'],atol=1e-12,rtol=0)
                    assert data.size==s['valid_cells'] and np.isfinite(data).all() and (data>=0).all()
                    assert int((data>0).sum())==s['positive_cells'] and float(data.max())==s['maximum']
            out.append(dict(job=directory.name,engine=product['engine'],metrics=manifest['metrics']))
        return out
    check('real_products_manifests_bytes_grids_units',products)
    def arrival():
        control=np.load(run/'arrival-upstream-control.npy',allow_pickle=False)
        with np.load(fire/'fire-output.npz',allow_pickle=False) as n:mask=np.any(n['fire']>0,axis=2)
        with rasterio.open(fire/'products/earliest-realization-arrival.tif') as src:
            array=src.read(1,masked=True);assert np.array_equal(~array.mask,mask)
            assert np.array_equal(array.data[mask],control[mask])
        return dict(oracle='Pinned upstream PROPAGATOR.compute_arrival_time_min',burned_cells=int(mask.sum()))
    check('arrival_compared_with_upstream_method',arrival)
    def replay():
        earlier=jobs/'job-f3c0a247e5d1417891923273fed3f4c3'
        with np.load(earlier/'fire-output.npz',allow_pickle=False) as a,np.load(fire/'fire-output.npz',allow_pickle=False) as b:
            for key in ['probability','fire','arrival']:assert np.array_equal(a[key],b[key]),key
        return 'Exact two-process same-seed comparison; one thread, one fixture, not independent statistical samples'
    check('fire_narrow_seeded_replay',replay)
    def bridge():
        record=load(flood/'hmc-reflex-bridge.json');mapping=load(flood/'hmc-input-mapping.json');request=load(flood/'request.json')
        files=sorted((flood/'flood-work/hmc/output').glob('*.nc.gz'));assert len(files)==6
        section_map={s['stream']:s for s in mapping['sections']}
        for file in files:
            with Dataset('verification',memory=gzip.decompress(file.read_bytes())) as ds:
                assert ds['Discharge'].units=='m^3/s'
                for row in [v for v in record['records'] if v['time']==ds.time_coverage_end]:
                    s=section_map[row['stream']];lo=ds['Longitude'][:];la=ds['Latitude'][:]
                    rc=np.unravel_index(np.argmin((lo-s['longitude'])**2+(la-s['latitude'])**2),lo.shape)
                    assert float(ds['Discharge'][rc])==row['Q_m3_s']
        csv=pd.read_csv(flood/'flood-work/discharge.csv')
        for row in csv.itertuples():
            values=[v['Q_m3_s'] for v in record['records'] if v['stream']==row.stream]
            assert len(values)==6 and np.isclose(row.Q100,max(values),atol=1e-12,rtol=0)
            assert row.Q0==request['options']['q0_m3_s']==0
        hand=load(flood/'hand-validation.json');assert len(hand['hands'])==len(csv)
        for item in hand['hands']:
            path=flood/'flood-work/hand/rst/ext_no_ce'/('hand_d8_ext_no_ce_'+str(item['stream'])+'.tif')
            assert sha256(path)==item['sha256']
            with rasterio.open(path) as src:
                values=src.read(1,masked=True).compressed();assert values.size==item['valid_cells'] and np.isfinite(values).all()
        info=load(flood/'flood-native-result.json');assert info['max_relative_optimizer_residual']<=.01
        return dict(outputs=len(files),reaches=len(csv),maximum_relative_fit_residual=info['max_relative_optimizer_residual'],physics='UNQUALIFIED',rain='SYNTHETIC')
    check('actual_HMC_discharge_bridge_and_nonempty_HAND',bridge)
    def provenance():
        obs=load(run/'observation.json');validate_observation(obs)
        assert obs['territory_id']=='abruzzo-laquila-research' and obs['coverage_fraction']==1
        assert obs['sensed_at'].startswith('2024-07-13') and obs['available_at'].startswith('2026-10-15')
        assert sha256(verify_asset(run,obs['asset']))==obs['asset']['sha256']
        weather=load(run/'prepared/weather.json');assert weather['data_kind']=='REANALYSIS' and weather['issued_at'] is None
        for directory in [fire,flood]:
            request=load(directory/'request.json');assert request['territory']['region']=='Abruzzo'
            assert request['territory']['calibration']=='UNKNOWN' and request['territory']['complete_catchment'] is False
        return dict(scene=obs['id'],sensed_at=obs['sensed_at'],available_at=obs['available_at'],qualification='Retrospective conditional scenarios')
    check('source_timestamps_rights_and_explicit_unknowns',provenance)
    def boundaries():
        src=Path(__file__).resolve().parents[2]/'src/hazardia'
        files=list(src.glob('*.py'))+list((src/'ingest').glob('*.py'))
        forbidden={'propagator','rasterio','numpy','scipy','geopandas','netCDF4','langchain','langgraph'}
        for path in files:
            for node in ast.walk(ast.parse(path.read_text())):
                modules=[x.name for x in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
                assert not forbidden.intersection(m.split('.')[0] for m in modules),str(path)
        return dict(reviewed_files=len(files),scope='AST imports in concrete core/ingestion; subprocess simulator workers separate; no decision core yet')
    check('core_and_provider_dependency_boundary',boundaries)
    write_new(a.output,dict(run_id=run.name,checks=results,passed=sum(v['status']=='PASS' for v in results),failed=sum(v['status']=='FAIL' for v in results),reviewer='Codex self-check; no external physical validation'))
    for result in results:print(result)
    if any(v['status']=='FAIL' for v in results):raise SystemExit(1)
if __name__=='__main__':main()
