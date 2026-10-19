"""Spatial policy adapter0.6: real mapped assets, explicit synthetic priority coverage."""
import copy,datetime as dt,json,re,math,sys
from pathlib import Path
from hazardia.io import HazardError,load,write_new,sha256,utcnow,timestamp
CATEGORIES=('waterline_action','canadair','helicopter','heavy_action')
from hazardia.decision.fire_priorities import WEIGHTS,LEGACY_WEIGHTS,priority_category
POLICY=dict(domain='FIRE_IDEAL_ASSIGNMENT',loss_unit='weighted_priority_points',benefit_model='EXCLUSIVE_AREA_COVERAGE_PROXY')
def available_for_automatic_plan(unit):
    return unit['available'] and unit['category'] not in ('canadair','helicopter')

def validate_input(body):
    if not isinstance(body,dict) or set(body) not in ({'job_id','fleet','weights','robust','assumptions_confirmed'},{'job_id','fleet','weights','robust','assumptions_confirmed','planning_minutes'}) or body['assumptions_confirmed'] is not True:raise HazardError('INVALID_INPUT','Explicit research ideal assumptions required')
    if not isinstance(body['job_id'],str) or not re.fullmatch('job-[a-f0-9]{32}',body['job_id']):raise HazardError('INVALID_INPUT','Completed baseline job required')
    if not isinstance(body['fleet'],list) or not 1<=len(body['fleet'])<=8:raise HazardError('INVALID_INPUT','Choose1..8available or unavailable units')
    if any(not isinstance(r,dict) or not isinstance(r.get('id'),str) for r in body['fleet']):raise HazardError('INVALID_INPUT','Strict resource rows required')
    if len({r['id'] for r in body['fleet']})!=len(body['fleet']):raise HazardError('INVALID_INPUT','Unique resource IDs')
    for r in body['fleet']:
        if set(r)!={'id','category','available','arrival_minutes'} or not re.fullmatch('[a-zA-Z0-9_-]{1,40}',r['id']) or r['category'] not in CATEGORIES or type(r['available']) is not bool:raise HazardError('INVALID_INPUT','Strict typed fleet row')
        if type(r['arrival_minutes']) not in [int,float] or not math.isfinite(r['arrival_minutes']) or not 0<=r['arrival_minutes']<4320:raise HazardError('INVALID_INPUT','Authored activation0..<4320min; bounded by baseline horizon; no routing estimate')
    if not isinstance(body['weights'],dict) or set(body['weights']) not in (set(WEIGHTS),set(LEGACY_WEIGHTS)) or any(type(v) not in [int,float] or not math.isfinite(v) or not 0<=v<=100 for v in body['weights'].values()) or not any(body['weights'].values()):raise HazardError('INVALID_INPUT','Explicit nonzero bounded priority weights')
    if type(body['robust']) not in [int,float] or not 0<=body['robust']<=1:raise HazardError('INVALID_INPUT','Robust fraction0..1')
    if type(body.get('planning_minutes',0)) not in (int,float) or not math.isfinite(body.get('planning_minutes',0)) or not 0<=body.get('planning_minutes',0)<4320:raise HazardError('INVALID_TIME','Planning time must be within the horizon')
    if any(r['arrival_minutes']<body.get('planning_minutes',0) for r in body['fleet']):raise HazardError('INVALID_TIME','No retroactive unit activation before planning time')
    return body

def local_analysis_mask(geometry,transform,shape):
    import numpy as np
    from rasterio.transform import Affine
    from rasterio.features import geometry_mask
    from shapely.geometry import mapping
    x,y,X,Y=geometry.bounds;corners=[(~transform)*(a,b) for a,b in [(x,y),(x,Y),(X,y),(X,Y)]]
    c0=max(0,math.floor(min(c for c,r in corners))-1);c1=min(shape[1],math.ceil(max(c for c,r in corners))+1)
    r0=max(0,math.floor(min(r for c,r in corners))-1);r1=min(shape[0],math.ceil(max(r for c,r in corners))+1)
    if c1<=c0 or r1<=r0:return (slice(0,0),slice(0,0)),np.zeros((0,0),dtype=bool)
    return (slice(r0,r1),slice(c0,c1)),geometry_mask([mapping(geometry)],(r1-r0,c1-c0),transform*Affine.translation(c0,r0),invert=True)

def prepare(root,body,out):
    # Heavy dependencies only in the isolated geospatial worker, never HTTP/UI threads.
    import numpy as np
    from rasterio.transform import Affine
    from rasterio.features import geometry_mask
    from pyproj import Transformer
    from shapely.geometry import shape,mapping,box
    from shapely.ops import transform
    validate_input(body);root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False);job=root/'jobs'/body['job_id'];manifest=load(job/'manifest.json');req=load(job/'request.json');series=load(job/'fire-series.json');plan=series['plan']
    for name in ['fire-output.npz','fire-series.json','fire-native-result.json']:
        if sha256(job/name)!=manifest['artifacts'][name]:raise HazardError('CHECKSUM','Baseline product mismatch')
    if plan['resources']:raise HazardError('INVALID_INPUT','Use a baseline without interventions, not an already suppressed fire')

    if plan.get('forcing'):
        from hazardia.territorial_context import acquire
        b=series['affected_bounds'];full=req['territory']['bbox_wgs84'];margin=.03
        context_bounds=full # Reuse the same bounded territorial snapshot shown on the scenario maps.
        assets=acquire(root,context_bounds,plan['forcing']['terrain_id'])
    else:assets=load(root/'web-assets/priority-areas.json')
    tr=Affine(*req['grid']['transform']);project=Transformer.from_crs(4326,req['grid']['crs'],always_xy=True).transform;back=Transformer.from_crs(req['grid']['crs'],4326,always_xy=True).transform
    with np.load(job/'fire-output.npz',allow_pickle=False) as a:p=a['probability'];arrival=a['arrival'];burned=a['fire']
    if p.shape!=tuple(req['grid']['shape']) or not np.isfinite(p).all() or (p<0).any() or (p>1).any():raise HazardError('INVALID_INPUT','Native probability grid invalid')
    if body.get('planning_minutes',0)*60>=req['options']['duration_s']:raise HazardError('INVALID_TIME','Planning time must precede simulation end')
    future_probability=np.mean((arrival>body.get('planning_minutes',0)*60)&(burned>0),axis=2)
    from shapely.geometry import Point
    rr,cc=np.where(future_probability>0);future_center=Point(*(tr*(float(cc.mean())+.5,float(rr.mean())+.5))) if len(rr) else None
    goals=[];goal_masks={};inventory_counts={key:0 for key in WEIGHTS}
    for f in assets['features']:
        category=priority_category(f)
        if category not in WEIGHTS:continue
        inventory_counts[category]+=1
        weight=body['weights'].get(category,0)
        if not weight:continue
        g=transform(project,shape(f['geometry']));analysis=g.buffer(75) if g.geom_type=='Point' else g.buffer(100)
        # Mask uses the model grid; centre-based rasterization and point75m influence are disclosed.
        window,mask=local_analysis_mask(analysis,tr,p.shape);vals=p[window][mask]
        if not vals.size:continue
        nominal=float(vals.mean());stress=float(vals.max());score=weight*nominal
        if assets.get('qualification')=='SATELLITE_CLASSIFIED_BUILTUP_UNCALIBRATED' or 'WorldCover' in f['properties'].get('source',''):
            from shapely.geometry import Point
            from shapely.ops import nearest_points
            center=nearest_points(g,future_center or g.representative_point())[0]
        elif g.geom_type in ('LineString','MultiLineString'):
            # Local protection target at the segment with greatest sampled baseline exposure.
            from shapely.geometry import Point
            from shapely.ops import nearest_points
            rr,cc=np.where(mask & (future_probability[window]>0));center=nearest_points(g,Point(*(tr*(float(cc.mean())+window[1].start+.5,float(rr.mean())+window[0].start+.5))))[0] if len(rr) else g.representative_point()
        else:center=g.representative_point()
        lon,lat=back(center.x,center.y)
        footprint=transform(back,box(center.x-150,center.y-150,center.x+150,center.y+150));area=[[y,x] for x,y in list(footprint.exterior.coords)[:-1]]
        corners=[(~tr)*project(lon,lat) for lat,lon in area]
        if any(not 0<=c<p.shape[1] or not 0<=r<p.shape[0] for c,r in corners):continue
        if stress>0:goal_masks['asset-'+str(len(goals)+1)]=(window,mask) # Zero-exposure masks are never used by assignment; do not retain them.
        goals.append(dict(id='asset-'+str(len(goals)+1),feature_id=f['id'],name=('Edificato '+f['id'].replace('builtup-','')+' · WorldCover2021' if 'WorldCover' in f['properties'].get('source','') else f['properties']['name']),category=category,source_category=f['properties']['category'],source_voltage=f['properties'].get('voltage'),point=[lat,lon],area=area,priority_weight=weight,nominal_probability=nominal,stress_probability=stress,nominal_points=score,stress_points=weight*stress,geometry=f['geometry'],analysis='Point75m authored influence' if g.geom_type=='Point' else 'Mapped footprint plus100m research interface buffer; grid centre rasterization'))
    goals.sort(key=lambda g:(g['stress_points'],g['nominal_points']),reverse=True)
    clustered=[];suppressed=[]
    for g in goals:
        near=next((v for v in clustered if v['category']==g['category'] and g['geometry']['type']=='Point' and v['geometry']['type']=='Point' and math.hypot((g['point'][0]-v['point'][0])*111195,(g['point'][1]-v['point'][1])*111195*math.cos(math.radians(g['point'][0])))<100),None)
        if near:suppressed.append(dict(feature_id=g['feature_id'],represented_by=near['feature_id'],reason='Same-category mapped points within100m; experimental anti-duplication grouping'))
        else:clustered.append(g)
    goals=clustered;omitted=max(0,len(goals)-80);goals=goals[:80];active=[g for g in goals if g['stress_points']>0]
    if not active:raise HazardError('NO_EXPOSED_ASSETS','No mapped target overlaps the baseline in this snapshot; outside coverage is unknown')
    at=req['valid_from'];finish=req['valid_until'];duration_s=req['options']['duration_s'];hours=duration_s/3600;
    if any(r['arrival_minutes']*60>=duration_s for r in body['fleet']):raise HazardError('INVALID_TIME','Unit activation must precede simulation end')
    resources=[];options=[];mapping_options={}
    product=dict(job_id=body['job_id'],hazard='FIRE',sha256=manifest['artifacts']['fire-output.npz'],valid_from=at,valid_until=req['valid_until'],weather_hash=next(a['sha256'] for a in req['assets'] if a['role']=='weather'),qualification='UNQUALIFIED_RESEARCH')
    for r in body['fleet']:
        payload=dict(territory_id=req['territory']['id'],home_authority='IDEAL_LOCAL',point_wgs84=list(reversed(plan['ignitions_wgs84'][0]['point'])),skills=['FIRE_SUPPRESSION'],equipment=[r['category']],capabilities=['FIRE'],schedule=[dict(start=at,end=finish)],rest_hours=12,maintenance='READY' if available_for_automatic_plan(r) else 'UNAVAILABLE',autonomy_h=hours,consumables=dict(fuel_l=100,water_l=100),cost_per_hour=1,reliability=1,mass_kg=1000)
        record=dict(schema_version='0.4.0',kind='resource',id=r['id'],available_at=utcnow(),provenance=dict(source='User ideal availability and arrival; remaining logistics explicitly hypothetical',license='AUTHORED_RESEARCH_FIXTURE',qualification='SYNTHETIC_RESEARCH'),payload=payload)
        resources.append(dict(id=r['id'],home_region='IDEAL_LOCAL',category=r['category'],record=record))
        future=np.mean((arrival>r['arrival_minutes']*60)&(burned>0),axis=2)
        for g in active:
            window,mask=goal_masks[g['id']];v=future[window][mask];nominal=g['priority_weight']*float(v.mean());stress=g['priority_weight']*float(v.max())
            oid=r['id']+'-'+g['id'];option=dict(id=oid,resource_id=r['id'],event_id=g['id'],start_slot=0,end_slot=1,arrival_s=r['arrival_minutes']*60,benefit=dict(nominal=min(nominal,g['nominal_points']),stress=min(stress,g['stress_points'])),cost=1+r['arrival_minutes']/60,fuel_l=1,water_l=1,road_open=True,road_limit_kg=100000,authorization=True,effect='IDEAL_ASSET_COVERAGE',evidence='SYNTHETIC_RESEARCH');options.append(option);mapping_options[oid]=dict(id=r['id'],category=r['category'],area=g['area'],at_minutes=r['arrival_minutes'],effect='fuel_removal',target_id=g['feature_id'],target_name=g['name'])
    problem=dict(schema_version='0.6.0',kind='decision_problem',id=out.name,planning_at=at,data_cutoff=utcnow(),mode='RESEARCH_IDEAL',policy=POLICY,resources=resources,events=[dict(id=g['id'],hazard='FIRE',region='IDEAL_LOCAL',product=copy.deepcopy(product),exposure=dict(nominal=g['nominal_points'],stress=g['stress_points'])) for g in active],scenarios=[dict(id='nominal',weight=None,qualification='SYNTHETIC_RESEARCH'),dict(id='stress',weight=None,qualification='SYNTHETIC_RESEARCH')],options=options,regions=[dict(id='IDEAL_LOCAL',minimum_donor_reserve=0)],commitments=[],settings=dict(budget_s=60,**{'lambda':0},cost_weight=.0001,horizon_slots=1,slot_s=duration_s,seed=1729,solver='highs'))
    # No reliable scenario probabilities: worst-case set. User robust fraction controls nominal/stress blending explicitly.
    for event in problem['events']:
        nominal=event['exposure']['nominal'];stress=event['exposure']['stress'];event['exposure']['stress']=(1-body['robust'])*nominal+body['robust']*stress
    for option in problem['options']:
        n=option['benefit']['nominal'];v=option['benefit']['stress'];option['benefit']['stress']=(1-body['robust'])*n+body['robust']*v
    bounds=assets.get('osm_coverage_bbox_wgs84') or assets['coverage_bbox_wgs84'];affected=series['affected_bounds'];complete=bounds[0]<=affected[0][1] and bounds[1]<=affected[0][0] and bounds[2]>=affected[1][1] and bounds[3]>=affected[1][0]
    baseline_input=dict(ignitions=plan.get('ignitions_wgs84',[dict(id='ignition-1',point=plan['ignition_wgs84'],at_minutes=0)]),hours=req['options']['duration_s']//3600,seed=req['options']['seed'],moisture_percent=req['options']['moisture_percent'],resources=[],weather_source=plan['weather_source'],weather_changes=plan['weather_changes'])
    if plan['weather_source']=='FORECAST':baseline_input['start_at']=req['valid_from']
    if plan.get('forcing'):baseline_input.update(moisture_model=plan['forcing']['moisture_model'],antecedent_hours=plan['forcing'].get('initialization',{}).get('hours',0),realizations=req['options']['realizations'])
    context=dict(aviation=dict(qualified=False,excluded_air_units=[r['id'] for r in body['fleet'] if r['category'] in ('canadair','helicopter')],reason='Obstacle completeness, conductor heights, flight path and crew/aircraft night qualification unavailable; no automatic aerial proposal'),baseline_input=baseline_input,assets=goals,option_resources=mapping_options,body=body,source=dict(priority_policy='critical-assets/1; authored weights, not official severity ranking',inventory_counts=inventory_counts,missing_priority_categories=[k for k,v in inventory_counts.items() if not v],osm_status=assets.get('osm_status'),inventory_kinds=sorted({f['properties'].get('source','OpenStreetMap') for f in assets['features']}),grouped_points=suppressed,url=assets['source_url'],sha256=assets['source_sha256'],available_at=assets['available_at'],coverage_bbox=bounds,fire_footprint_covered=complete,omitted=omitted,missing=assets['missing'],qualification=assets.get('qualification','MAPPED_OSM_PARTIAL')),assumptions=['IDEAL ONLY; no operational approval','Priority points are not population or people saved','Mean footprint probability and maximum are not weather-ensemble members','One chosen unit ideally covers one target; no differential efficacy by category','Native check uses a300m square fuel-removal hypothesis, not an actual asset perimeter','Unit activation manual within the full simulation horizon; full-horizon availability/autonomy hypothetical, no verified travel/roads/consumables/fatigue', 'Benefit excludes cells already reached before unit activation in the sampled baseline; not a calibrated suppression prediction','Outside OSM coverage unknown, not low risk','Full joint native rerun required; additive proxy is not a physical effect prediction'])
    write_new(out/'problem.json',problem);write_new(out/'context.json',context);return problem,context

if __name__=='__main__':
    try:prepare(sys.argv[1],load(sys.argv[2]),sys.argv[3])
    except HazardError as e:
        write_new(Path(sys.argv[3]).parent/'prepare-error.json',dict(code=e.code,detail=str(e)));raise
