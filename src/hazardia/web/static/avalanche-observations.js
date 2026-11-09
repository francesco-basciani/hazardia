// EO snow presence is independent of modeled snow and is never a stability test.
export function observationState(area,now=Date.now()){
 if(!area)return 'MISSING';
 const start=Date.parse(area.observed_from),end=Date.parse(area.observed_at);
 if(!Number.isFinite(start)||!Number.isFinite(end)||start>end||end>now)return 'INVALID_TIME';
 return now-start>24*3600000?'STALE':'RECENT';
}
export function compatibleObservations(product,version){
 return product?.schema==='hazardia.observed-snow/1.0'&&product.assimilated===false&&
  product.terrain_version===version?.split(':')[1]&&Array.isArray(product.areas)&&typeof product.units==='object';
}
export function observationFor(product,p,now=Date.now()){
 const unit=product?.units?.[p.id],area=product?.areas?.find(a=>a.id===unit?.area),state=observationState(area,now);
 const conflict=state==='RECENT'&&unit?.snow_pixels>0&&Array.isArray(p.forecast_hs_cm)&&p.forecast_hs_cm[0]===0;
 return {unit,area,state,conflict};
}
export function forecastEvidence(p){
 if(p.potential_class===0)return 'MISSING';
 if(p.potential_class===2)return 'SNOW_UNVERIFIED';
 if(p.potential_class===3)return 'MORPHOLOGY_AND_MODELED_SNOW_ONLY';
 if(p.potential_class>=4&&p.potential_class<=6)return 'MODELED_LOADING_OR_WATER';
 return 'NO_SELECTED_COMBINATION';
}
