"""M2 replay against frozen M1 genuine spatial outputs; Linux geo env only."""
import argparse,copy,json,platform,resource as usage,time,subprocess
from pathlib import Path
import rasterio
from rasterio.warp import transform
from pyproj import CRS
from hazardia.io import load,write_new,sha256,HazardError
from hazardia.domain.contracts import validate_record,select_weather
from hazardia.domain.state import snapshot,GeoIndex,identity
from hazardia.domain.events import associate
from hazardia.domain.geo import exposed_points
from hazardia.domain.consequences import impact_only,check_route
from tests.domain.fixtures import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);a=ap.parse_args();out=Path(a.run);app=Path(__file__).resolve().parents[2];results=[];generated={}
    def check(name,fn):
        try:detail=fn();results.append(dict(name=name,status='PASS',detail=detail))
        except Exception as e:results.append(dict(name=name,status='FAIL',detail=type(e).__name__+': '+str(e)))
    def profiles():
        assert platform.system()=='Linux';reports=[]
        for filename in ['abruzzo','senegal-synthetic']:
            prof=load(app/'profiles/research'/ (filename+'.json'));validate_record(prof);p=prof['payload'];crs=CRS(p['work_crs']);assert crs.is_projected and all(axis.unit_name=='metre' for axis in crs.axis_info)
            center=[(p['bbox_wgs84'][0]+p['bbox_wgs84'][2])/2,(p['bbox_wgs84'][1]+p['bbox_wgs84'][3])/2]
            point=exposure();point['payload'].update(territory_id=prof['id'],point_wgs84=center)
            obs=detection();obs['payload'].update(territory_id=prof['id'],bbox_wgs84=[center[0]-.001,center[1]-.001,center[0]+.001,center[1]+.001])
            snap=snapshot(prof,[point,obs,obs],T,out/(filename+'-snapshot.json'));assert len(snap['records'])==2
            event=associate([obs,copy.deepcopy(obs)],prof,T);assert len(event['events'])==1 and event['duplicate_count']==1;write_new(out/(filename+'-events.json'),event)
            generated[filename+'-observations.json']=[obs,obs];write_new(out/(filename+'-observations.json'),[obs,obs]);reports.append(dict(profile=prof['id'],crs=p['work_crs'],timezone=p['timezone'],snapshot_hash=snap['content_sha256']))
        return reports
    check('two_profiles_same_snapshot_event_workflow_and_real_CRS',profiles)
    def weather_history():
        old=load('/home/hazardia/hazardia-runtime/runs/m1-abruzzo-20261015T161041Z/weather.json');w=ensemble();w['available_at']=old['available_at'];w['provenance'].update(source=old['source']['url'],license=old['license'],qualification='UNQUALIFIED_RESEARCH');p=w['payload'];p.update(data_kind='REANALYSIS',issued_at=None,valid_from=old['records'][0]['at'],valid_until='2024-07-14T00:00:00Z',members=[dict(id='era5',weight=None,records=old['records'])]);select_weather(w,'2026-10-15T19:00:00Z',T,END,forecast_required=False)
        try:select_weather(w,'2026-10-15T19:00:00Z',T,END)
        except HazardError as e:assert e.code=='SOURCE_KIND'
        else:raise AssertionError('Reanalysis accepted as forecast')
        write_new(out/'real-history-ensemble.json',w);write_new(out/'synthetic-forecast-ensemble.json',ensemble());return 'Real history normalized without fabricated issue/weights; two-member authored forecast validated separately'
    check('real_reanalysis_boundary_and_synthetic_forecast_distinction',weather_history)
    def real_products():
        cases=[]
        for hazard,job in [('FIRE','job-7f7c35a549494a118219cd98bcf70093'),('FLOOD','job-78cd5d14b5234865b715bd8f090c0caf')]:
            root=Path('/home/hazardia/hazardia-runtime/jobs')/job;product=load(root/'product.json');request=load(root/'request.json');layer=product['layers'][0];path=root/layer['path'];before=sha256(path)
            with rasterio.open(path) as src:
                values=src.read(1,masked=True);indices=list(zip(*((values.filled(0)>0).nonzero())))[:3];assert len(indices)==3;exposures=[]
                for n,(row,col) in enumerate(indices):
                    x,y=src.xy(row,col);lon,lat=transform(src.crs,'EPSG:4326',[x],[y]);v=exposure('synthetic-pop-'+str(n),[lon[0],lat[0]]);v['payload'].update(valid_from=product['valid_from'],valid_until=product['valid_until']);exposures.append(v)
            base=exposed_points(product,request,root,exposures,at=product['valid_from'],as_of='2026-10-15T19:00:00Z');assert base['exposed_people']==30
            e=effect(hazard=hazard);after=impact_only(e,base);assert after['remaining_exposed_people']==25 and sha256(path)==before and after['hazard_sha256']==base['hazard_sha256']
            write_new(out/(hazard.lower()+'-exposures.json'),exposures);write_new(out/(hazard.lower()+'-baseline.json'),base);write_new(out/(hazard.lower()+'-impact-only.json'),after)
            outside=exposure(point=[0,0]);outside['payload'].update(valid_from=product['valid_from'],valid_until=product['valid_until'])
            try:exposed_points(product,request,root,[outside],at=product['valid_from'],as_of='2026-10-15T19:00:00Z')
            except HazardError as err:assert err.code=='UNKNOWN_COVERAGE'
            else:raise AssertionError('Outside coverage accepted as safe')
            bad=copy.deepcopy(product);req=copy.deepcopy(request);bad['grid']['transform'][2]+=.01;req['grid']=bad['grid']
            try:exposed_points(bad,req,root,exposures,at=product['valid_from'],as_of='2026-10-15T19:00:00Z')
            except HazardError as err:assert err.code=='GRID_MISMATCH'
            else:raise AssertionError('Grid drift accepted')
            cases.append(dict(hazard=hazard,job=job,raster_sha256=before,co_located_synthetic_people=30,remaining_under_synthetic_effect=25))
        return cases
    check('genuine_products_exposure_vs_effect_and_negative_grid_coverage',real_products)
    def benchmark():
        records=[exposure('point-%05d'%i,[13.36+(i%100)*.0004,42.33+(i//100)*.0004]) for i in range(10000)];bbox=[13.37,42.34,13.38,42.35];index=GeoIndex(out/'spatial.sqlite');t=time.monotonic();index.build(records);build_s=time.monotonic()-t
        t=time.monotonic();query=index.window(bbox,T,100);query_s=time.monotonic()-t
        baseline=[r for r in records if bbox[0]<=r['payload']['point_wgs84'][0]<=bbox[2] and bbox[1]<=r['payload']['point_wgs84'][1]<=bbox[3]][:100];assert query==baseline
        t=time.monotonic();raw=json.dumps(query,allow_nan=False).encode();serialization_s=time.monotonic()-t;assert len(query)==100 and len(raw)<100000
        metrics=dict(records=10000,returned=len(query),build_s=build_s,indexed_query_s=query_s,serialization_s=serialization_s,payload_bytes=len(raw),index_bytes=(out/'spatial.sqlite').stat().st_size,process_peak_rss_bytes=usage.getrusage(usage.RUSAGE_SELF).ru_maxrss*1024,measurement='one execution; RSS includes imports/integration; no p95 or UI target')
        write_new(out/'spatial-metrics.json',metrics);return metrics
    check('indexed_window_matches_full_scan_bounded_payload_and_metrics',benchmark)
    def source_integrity():
        config=load('/home/hazardia/hazardia-runtime/runtime-v2.json')
        for p,h in config['engine_files'].items():assert sha256(p)==h
        manifest=load('/home/hazardia/hazardia-runtime/runs/m1-abruzzo-20261015T161041Z/manifest.json')
        root=Path('/home/hazardia/hazardia-runtime');r=root/'runs/m1-abruzzo-20261015T161041Z'
        for p,h in manifest['artifacts'].items():
            actual=r/p[4:] if p.startswith('run/') else root/p if p.startswith('jobs/') else None
            if actual is not None:assert sha256(actual)==h,p
        return dict(engine_files=len(config['engine_files']),M1_run_and_job_artifacts='unchanged; archived app source is historical, live app now M2')
    check('M1_frozen_evidence_and_engines_unchanged',source_integrity)
    write_new(out/'integration.json',dict(run_id=out.name,checks=results,passed=sum(v['status']=='PASS' for v in results),failed=sum(v['status']=='FAIL' for v in results),reviewer='Codex self-check; no physical/operational qualification'))
    for r in results:print(r)
    if any(r['status']=='FAIL' for r in results):raise SystemExit(1)
if __name__=='__main__':main()
