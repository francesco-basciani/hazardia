import copy
T='2024-07-13T13:00:00Z';END='2024-07-13T14:00:00Z'
def record(kind,payload,id='fixture',territory='abruzzo-laquila-research'):
    p=copy.deepcopy(payload)
    if kind!='territory':p.setdefault('territory_id',territory)
    return dict(schema_version='0.4.0',kind=kind,id=id,available_at=T,provenance=dict(source='HAZARDIA authored controlled fixture; not observed field data',license='AUTHORED_RESEARCH_FIXTURE',qualification='SYNTHETIC_RESEARCH'),payload=p)
def profile(id='abruzzo-laquila-research'):
    return record('territory',dict(bbox_wgs84=[13.36,42.33,13.40,42.37],work_crs='EPSG:32633',timezone='Europe/Rome',jurisdictions=['IT-ABR-RESEARCH'],horizontal_unit='m',vertical_datum='UNKNOWN',calibration='UNKNOWN',calibration_refs=[],missing_data_policy='BLOCK_CRITICAL_UNKNOWN',source_policy=dict(max_age_s=7200,min_coverage=.8)),id)
def detection(id='d1',**updates):
    p=dict(hazard='FIRE',bbox_wgs84=[13.37,42.34,13.38,42.35],sensed_at=T,sensor='synthetic-optical',correlation_group='same-acquisition',assessment='PRESENT',confidence=.8,coverage=1);p.update(updates);return record('detection',p,id)
def exposure(id='x1',point=None):
    return record('exposure',dict(point_wgs84=point or [13.38,42.35],category='POPULATION',people=10,vulnerability=None,valid_from=T,valid_until=END),id)
def resource():
    return record('resource',dict(home_authority='IT-ABR-RESEARCH',point_wgs84=[13.38,42.35],skills=['RESEARCH'],equipment=['VEHICLE'],capabilities=['FIRE','FLOOD'],schedule=[dict(start=T,end=END)],rest_hours=12,maintenance='READY',autonomy_h=4,consumables=dict(fuel_l=20,water_l=0),cost_per_hour=10,reliability=.9,mass_kg=2000),'res')
def road(id='road',**updates):
    p=dict(from_node='a',to_node='b',bbox_wgs84=[13.37,42.34,13.38,42.35],status='OPEN',load_limit_kg=3000,length_m=1000,speed_kmh=30,valid_from=T,valid_until=END);p.update(updates);return record('road',p,id)
def effect(**updates):
    p=dict(hazard='FLOOD',effect='IMPACT_ONLY',action='EVACUATION',model_id='synthetic-evacuation-count-v1',evidence='SYNTHETIC_RESEARCH',parameters=dict(evacuated_people=5));p.update(updates);return record('intervention',p,'effect')
def ensemble():
    values=dict(precipitation=0,wind_speed_10m=2,wind_direction_10m=90,temperature_2m=20,relative_humidity_2m=50,surface_pressure=1000,shortwave_radiation=100)
    p=dict(bbox_wgs84=[13.36,42.33,13.40,42.37],spatial_resolution_m=25000,data_kind='FORECAST',issued_at=T,valid_from=T,valid_until=END,step_s=3600,units=dict(precipitation='mm',wind_speed_10m='m/s',wind_direction_10m='°',temperature_2m='°C',relative_humidity_2m='%',surface_pressure='hPa',shortwave_radiation='W/m²'),members=[dict(id=m,weight=None,records=[dict(at=T,values=copy.deepcopy(values))]) for m in ['control','wet']])
    return record('weather_ensemble',p,'weather')
