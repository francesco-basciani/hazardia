// Categories describe physical combinations, never a calibrated danger ranking.
export const factors=[
 ['#66717b','Dati del modello mancanti'],
 ['#ded8c9','Combinazioni selezionate non rilevate · non significa sicuro'],
 ['#22b9be','Pendenza ≥30° + acqua nel manto modellata'],
 ['#09a7cf','Pendenza ≥30° + incremento netto di SWE'],
 ['#006c86','Entrambe le combinazioni nelle 72 ore']
];
export const snowLegend=[['#66717b','Dato mancante'],['#ded8c9','0 cm modellati'],['#c7ddeb','>0–1 cm'],['#88b6d3','>1–10 cm'],['#487ea7','>10–30 cm'],['#254b78','>30 cm']];
export const potentialLegend=[
 ['#66717b','Valutazione incompleta · dati necessari mancanti'],
 ['#ded8c9','Combinazione non rilevata · pericolo non escluso'],
 ['#929aa8','Terreno ripido · neve locale non verificata'],
 ['#8db9c5','Sola predisposizione · neve modellata + terreno ripido'],
 ['#f6b547','Attenzione sperimentale · carico nevoso simulato in aumento'],
 ['#ef7950','Attenzione sperimentale · acqua nel manto simulata'],
 ['#e9553f','Carico e acqua simulati · non grado di pericolo']
];
export function potentialDisplay(p){
 const potential=p.potential_class>=3;
 const kind=p.potential_class===0?'missing':p.potential_class===2?'snow_unverified':
  potential&&(!p.soil_association||!p.substrate||p.soil_missing_samples>0||p.substrate_missing_samples>0)?'ground_gap':null;
 return {potential,uncertainty:kind,colour:kind==='ground_gap'?'#efbd58':'#aab4c0'};
}
export function category(p,mode){
 if(mode==='potential')return potentialLegend[p.potential_class]||potentialLegend[0];
 if(mode==='factors')return factors[p.factor_class]||factors[0];
 const index={snow24:1,snow48:2,snow72:3}[mode];
 if(index===undefined)throw Error('Vista valanghe sconosciuta');
 const value=p.forecast_hs_cm?.[index];
 return snowLegend[value==null?0:value===0?1:value<=1?2:value<=10?3:value<=30?4:5];
}
export function validAt(meta,at){const t=Date.parse(at);return Number.isFinite(t)&&Date.parse(meta.reference_utc)<=t&&t<=Date.parse(meta.end_utc);}

function inRing(ring,x,y){
 let inside=false;
 for(let i=0,j=ring.length-1;i<ring.length;j=i++){
  const [a,b]=ring[i],[c,d]=ring[j];
  if(Math.abs((x-a)*(d-b)-(y-b)*(c-a))<1e-10&&x>=Math.min(a,c)&&x<=Math.max(a,c)&&y>=Math.min(b,d)&&y<=Math.max(b,d))return true;
  if((b>y)!==(d>y)&&x<(c-a)*(y-b)/(d-b)+a)inside=!inside;
 }return inside;
}
export function locateSample(data,lon,lat){
 if(!Number.isFinite(lon)||!Number.isFinite(lat)||Math.abs(lon)>180||Math.abs(lat)>90)return null;
 return data.features.find(f=>{
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
  return polygons.some(rings=>inRing(rings[0],lon,lat)&&!rings.slice(1).some(ring=>inRing(ring,lon,lat)));
 })||null;
}
export function positionAssessment(data,lon,lat){
 if(Array.isArray(data.potential_areas)){
  const feature=locateSample({features:data.potential_areas},lon,lat),stale=isStale(data.metadata),p=feature?.properties;
  return {feature,reliableReleaseDetection:false,code:!feature?'OUTSIDE_COVERAGE':p.potential_class===0?'MISSING':stale?'STALE':p.potential_class===2?'TERRAIN_SNOW_UNVERIFIED':p.potential_class===1?'NOT_DETECTED_UNRESOLVED':'POTENTIAL_HAZARD'};
 }
 const feature=locateSample(data,lon,lat),stale=isStale(data.metadata);
 return {feature,reliableReleaseDetection:false,code:!feature?'OUTSIDE_COVERAGE':feature.properties.factor_class===0?'MISSING':stale?'STALE':feature.properties.factor_class===1?'NOT_DETECTED_UNRESOLVED':'PHYSICAL_SIGNALS'};
}
export function isStale(meta,now=Date.now()){
 const reference=Date.parse(meta.reference_utc),end=Date.parse(meta.end_utc),cycle=Date.parse(meta.weather_run_utc||meta.reference_utc);
 return !Number.isFinite(reference)||!Number.isFinite(end)||!Number.isFinite(cycle)||reference>now+300000||now>end||now-reference>9*3600000||now-cycle>12*3600000||['EXPIRED','STALE','FUTURE_REFERENCE_INVALID'].includes(meta.freshness_status);
}

// Same descriptive combinations as the existing backend, applied to distinct time supports.
export function projectPotentialAt(raw,lead){
 if(![0,24,48,72].includes(lead))throw Error('Orizzonte valanghe non supportato');
 const areas=(raw.potential_areas||[]).map(feature=>{
  const p=feature.properties,w=raw.metadata.forecast_windows?.[p.model_sample_id]?.[String(lead)];
  const missingReason=p.terrain_steep==null?'Pendenza locale necessaria mancante':'Output temporale della colonna mancante o rifiutato';
  const note=lead===0?'Stato al riferimento; carico recente precedente non ricostruito.':'Finestra '+(lead-24)+'–'+lead+' ore; massimi interni alla finestra, non necessariamente simultanei.';
  if(!w||!Number.isFinite(w.forecast_hs_max_cm)||!Number.isFinite(w.liquid_water_max_kg_m2)||(lead!==0&&!Number.isFinite(w.max_net_swe_increase_kg_m2))||p.terrain_steep==null){return {...feature,properties:{...p,potential_class:0,temporal_active:true,temporal_lead:lead,temporal_note:note,potential_reasons:[missingReason],potential_missing:[...(p.potential_missing||[]),missingReason],temporal_model:null}};}
  const load=Number.isFinite(w.max_net_swe_increase_kg_m2)&&w.max_net_swe_increase_kg_m2>.001,wet=w.liquid_water_max_kg_m2>.001;
  const code=!p.terrain_steep?1:w.forecast_hs_max_cm<=0?2:load&&wet?6:load?4:wet?5:3;
  const reasons=[note,code===1?'Il criterio di terreno ripido non è rilevato; possibili arrivi da monte non simulati':code===2?'Terreno ripido; neve locale non verificata dal campione':code>=3?'Terreno ripido e neve presente nella colonna modellata':'Valutazione incompleta'];
  if(code>=3&&load)reasons.push('Incremento netto massimo SWE nella finestra: '+w.max_net_swe_increase_kg_m2.toFixed(4)+' kg/m²; non soglia di distacco');
  if(code>=3&&wet)reasons.push('Acqua nel manto modellata nella finestra: '+w.liquid_water_max_kg_m2.toFixed(4)+' kg/m²; non acqua basale misurata');
  if(code>=3&&w.air_temperature_max_c>0)reasons.push('Temperature dell’aria sopra0°C nel periodo; stabilità e acqua basale non verificate');
  const missing=[...(p.potential_missing||[])];if(lead===0)missing.push('Carico nevoso precedente al riferimento non ricostruito');
  return {...feature,properties:{...p,...w,potential_class:code,temporal_active:true,temporal_lead:lead,temporal_note:note,temporal_model:w,potential_reasons:reasons,potential_missing:missing}};
 });
 return {...raw,potential_areas:areas};
}
