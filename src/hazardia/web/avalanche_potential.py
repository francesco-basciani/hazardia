"""Indicative crossed-support potential. No calibrated probability/danger grade."""
import gzip,hashlib,json,re
from functools import lru_cache
from pathlib import Path

COVER={10:'Copertura arborea',20:'Arbusti',30:'Prateria',40:'Coltivi',50:'Edificato',60:'Nudo / vegetazione rada',70:'Neve / ghiaccio cartografati nel2021',80:'Acqua',90:'Zona umida',95:'Mangrovie',100:'Muschi / licheni'}

@lru_cache(maxsize=2)
def _context(path,digest):
    with gzip.open(path,'rb') as stream:raw=stream.read(64*1024**2+1)
    if len(raw)>64*1024**2 or hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Terrain context checksum/size')
    value=json.loads(raw)
    if value.get('schema')!='hazardia.avalanche-terrain-context/1.0' or len(value['features'])>16000:raise ValueError('Terrain context schema/size')
    ids=set()
    for f in value['features']:
        p=f['properties']
        if p['id'] in ids or f['geometry']['type'] not in ('Polygon','MultiPolygon') or (p['terrain_steep'] is not None and type(p['terrain_steep']) is not bool):raise ValueError('Terrain geometry/identity')
        ids.add(p['id'])
    return value

def assess(model,terrain):
    reasons=[];missing=['Stabilità e strati deboli non osservati','Vento e accumuli locali non simulati','Acqua basale, rugosità e attrito neve-suolo non misurati','Runout, persone e beni esposti non valutati']
    ground=dict(terrain)
    cover=ground.get('cover') or COVER.get(ground.get('cover_code'),'Copertura vegetale mancante')
    ground['cover']=cover
    if not ground.get('soil_association'):missing.append('Suolo cartografico mancante in questa zona')
    if not ground.get('substrate'):missing.append('Substrato cartografico mancante in questa zona')
    if ground.get('soil_missing_samples',0)>0:missing.append('Suolo con campioni di supporto mancanti o ambigui: '+str(ground['soil_missing_samples'])+'/'+str(ground['ground_support_samples']))
    if ground.get('substrate_missing_samples',0)>0:missing.append('Substrato con campioni di supporto mancanti o ambigui: '+str(ground['substrate_missing_samples'])+'/'+str(ground['ground_support_samples']))
    if not ground.get('cover') or cover=='Copertura vegetale mancante':missing.append('Copertura vegetale mancante')
    steep=ground.get('terrain_steep');hs=model.get('forecast_hs_max_cm');gain=model.get('max_net_swe_increase_kg_m2');water=model.get('liquid_water_max_kg_m2')
    if steep is None:missing.append('Pendenza non disponibile in questo supporto cartografico')
    if model.get('factor_class')==0 or hs is None or steep is None:
        code=0;reasons.append('Dati necessari alla combinazione non disponibili')
    elif not steep:
        code=1;reasons.append('Il criterio di terreno ripido non è rilevato nel supporto cartografico; non esclude valanghe o arrivi da monte')
    elif hs<=0:
        code=2;reasons.append('Terreno con pendenze ≥30°; neve locale non verificata: il campione meteo non rappresenta tutte le quote')
    else:
        load=gain is not None and gain>.001;wet=water is not None and water>.001
        code=6 if load and wet else 4 if load else 5 if wet else 3
        reasons.append('Terreno con pendenze ≥30° e neve presente nel modello della cella')
        if load:reasons.append('Incremento netto massimo di SWE nel modello: '+format(gain,'.4f')+' kg/m²; non soglia critica di distacco')
        if wet:reasons.append('Acqua liquida nel manto modellata: '+format(water,'.4f')+' kg/m²; posizione dell’acqua basale sconosciuta')
        tmin=model.get('air_temperature_min_c');tmax=model.get('air_temperature_max_c')
        if tmax is not None and tmax>0:
            reasons.append('Aria prevista sopra0°C mentre il modello contiene neve; influenza termica condizionata alla colonna')
            if tmin is not None and tmin<0:reasons.append('Temperature previste su entrambi i lati di0°C, senza verifica locale della crosta o della stabilità')
        if 'Prateria' in cover:
            reasons.append('Fondo prativo cartografato: possibile predisposizione allo scivolamento da verificare; altezza dell’erba e attrito non misurati')
        elif cover=='Copertura arborea':reasons.append('Bosco cartografato: nessuna riduzione automatica del pericolo senza altezza/densità e stato del manto')
        elif 'Nudo' in cover:reasons.append('Suolo nudo/vegetazione rada: roccia liscia e detrito rugoso non distinti come attrito misurato')
    if ground.get('soil_association'):
        support='classi di suolo stimate, campioni1km; litologia ISPRA1:100000 generalizzata250m, campioni1km' if ground.get('soil_support_m') else 'associazione1:250000'
        reasons.append('Suolo consultato: '+ground['soil_association']+'; substrato: '+str(ground.get('substrate'))+' ('+support+', non parametro di attrito)')
    elif ground.get('substrate'):
        reasons.append('Substrato consultato: '+ground['substrate']+'; suolo mancante, nessun attrito meccanico inferito')
    result=dict(model);result.update(ground);result.update(potential_class=code,potential_reasons=reasons,potential_missing=missing,potential_status='INDICATIVE_UNCALIBRATED',model_sample_id=ground.get('model_sample_id',model['id']),model_sample_elevation_m=model.get('elevation_m'),model_sample_slope_deg=model.get('slope_deg'),release_probability=None,hazard_grade=None)
    result['vegetation_status']='CARTOGRAPHIC_2021' if cover!='Copertura vegetale mancante' else 'MISSING'
    result['soil_substrate_status']=ground.get('ground_status') or ('CARTOGRAPHIC_1_250000' if ground.get('soil_association') else 'MISSING')
    result['missing_reasons']=[r for r in result.get('missing_reasons',[]) if r!='NATIONAL_VEGETATION_SOIL_SUBSTRATE']
    return result

def enrich(data,directory):
    directory=Path(directory);native={f['properties']['id']:f['properties'] for f in data['features']};meta=data['metadata']
    try:
        manifest=json.loads((directory/'terrain-manifest.json').read_text());digest=manifest['sha256'];filename=manifest.get('file','terrain-context.json.gz')
        if filename!='terrain-context.json.gz' and not re.fullmatch(r'terrain-objects/[a-f0-9]{64}\.json\.gz',filename):raise ValueError('Invalid terrain object path')
        context=_context(str(directory/filename),digest)
        local_models=meta.get('local_forecasts',{});local_digest='embedded'
        override=directory/'local-forecasts.json'
        if override.exists():
            raw=override.read_bytes();local=json.loads(raw)
            if local['reference_utc']==meta['reference_utc'] and local['weather_run_utc']==meta['weather_run_utc']:
                local_models=local['models'];local_digest=hashlib.sha256(raw).hexdigest()
        data['local_forecasts']=local_models
        data['potential_areas']=[]
        for f in context['features']:
            ground=dict(f['properties']);parent=native[ground['model_sample_id']];local_id=ground.get('local_sample_id');model=local_models.get(local_id) if local_id else None
            if model and model.get('factor_class')!=0:
                ground['national_parent_model_id']=ground['model_sample_id'];ground['model_sample_id']=local_id;ground['local_profile_status']='AVAILABLE_SYNTHETIC_REPRESENTATIVE'
            elif local_id:
                ground['national_parent_model_id']=ground['model_sample_id'];ground['model_sample_id']=local_id;ground['local_profile_status']='LOCAL_PROFILE_MISSING'
                model=model or dict(id=local_id,factor_class=0,forecast_hs_max_cm=None,forecast_hs_cm=None,release_probability=None,hazard_grade=None)
            else:model=parent
            properties=assess(model,ground)
            if ground.get('local_profile_status')=='LOCAL_PROFILE_MISSING':properties['potential_missing'].append('Profilo locale mancante o rifiutato; non sostituito con zero o con un altro profilo')
            data['potential_areas'].append(dict(type='Feature',geometry=f['geometry'],properties=properties))
        meta['potential_local_profile_counts']=dict(total=len(local_models),valid=sum(p.get('factor_class')!=0 for p in local_models.values()))
        digest+=':'+local_digest
        meta['potential_terrain']=context['metadata'];meta['potential_context_status']='AVAILABLE_WITH_EXPLICIT_GAPS'
    except (OSError,ValueError,TypeError,KeyError):
        digest='missing';meta['potential_context_status']='MISSING_OR_INVALID_TERRAIN_CONTEXT'
        data['potential_areas']=[dict(type='Feature',geometry=f['geometry'],properties=assess(f['properties'],dict(id=f['properties']['id'],terrain_steep=None,terrain_meaning='Terrain context missing'))) for f in data['features']]
    thermal=directory/'thermal-context.json'
    if thermal.exists():
        try:
            temperatures=json.loads(thermal.read_text())
            if temperatures['reference_utc']==meta['reference_utc'] and temperatures['weather_run_utc']==meta['weather_run_utc']:
                for f in data['potential_areas']:
                    p=f['properties'];p.update(temperatures['points'].get(p['model_sample_id'],{}))
        except (ValueError,KeyError,TypeError):pass
    for f in data['potential_areas']:
        p=f['properties']
        if p['potential_class']>=3 and p.get('ground_temperature_max_c') is not None:
            p['potential_reasons'].append('Forzante termica del terreno valutata: '+format(p['ground_temperature_min_c'],'.1f')+'–'+format(p['ground_temperature_max_c'],'.1f')+' °C; contatto neve-suolo non misurato')
    meta['potential_counts']=dict(total_areas=len(data['potential_areas']),areas_with_modeled_snow_and_steep_support=sum(f['properties']['potential_class']>=3 for f in data['potential_areas']),areas_with_only_terrain_and_unverified_snow=sum(f['properties']['potential_class']==2 for f in data['potential_areas']))
    meta['potential_scope']='Indicative potential avalanche hazard, not calibrated release probability; snow/meteo10km plus representative synthetic GranSasso profiles; terrain200m/GranSasso30m; national soil/lithology context1km and explicit gaps, local ARSSA1:250000'
    data['native_version']=data['version'];data['version']+=':'+digest
    return data
