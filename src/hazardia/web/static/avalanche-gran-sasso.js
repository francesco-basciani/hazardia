export function localForcingDescription(m){
 if(m?.weather_fallback_reason)return 'METEO DEGRADATO: ICON‑2I non aggiornato; previsione temporanea NOAA GFS circa25km. Dettaglio meteorologico sui versanti mancante, nessuna correzione altimetrica. Ritorno automatico alla sorgente fine quando disponibile. Motivo: '+m.weather_fallback_reason;
 if(m?.weather_provider==='icon2i_hybrid')return 'Meteo ICON‑2I ItaliaMeteo/ARPAE: modello2,2km, griglia WCS0,022°. Temperatura, umidità, vento, precipitazione e nuvole più dettagliati; radiazione e bordo superficiale restano GFS circa25km. ICON‑2I disponibile fino al '+m.high_resolution_end_utc+'; ore successive e campi non utilizzabili: GFS, senza inventare dettaglio. Supporti rappresentativi entro5km; nessuna correzione altimetrica.';
 if(m?.weather_provider==='noaa_gfs')return 'Storico di previsioni ICON-EU e nuove previsioni NOAA GFS circa25km; nessuna correzione altimetrica, rappresentatività degradata in alta quota. Prodotti meteo, non misure sul versante.';
 return 'Previsioni meteorologiche archiviate, non misure locali; risoluzione e limiti nella provenienza.';
}
export function localSnowEvidenceText(feature){
 const rows=feature?.properties?.snow_observations||[];
 if(!rows.length)return ['Neve osservata: nessun pixel recente classificabile acquisito per questa unità; nubi, ombre, dati mancanti o scaduti non significano assenza di neve.'];
 return rows.map(r=>'Satellite '+r.observed_at+': '+r.snow_pixels+' pixel di visualizzazione classificati neve/ghiaccio, '+r.clear_land_pixels+' di terreno osservabile senza neve rilevata. '+(r.model_comparison?'Confronto con manto storico simulato '+r.model_comparison.hs_cm+'cm al '+r.model_comparison.at_utc+' (scarto '+Math.round(r.model_comparison.offset_seconds/60)+'min): '+(r.model_comparison.status==='PRESENCE_AGREES'?'presenza coerente':'evidenza mista o discordante, da verificare')+'.':'Nessuno stato simulato entro1ora: confronto temporale non disponibile.')+' '+({OBSERVED_SNOW_MODEL_ZERO:'Neve osservata dove il modello indicava0cm: possibile sottostima.',CLEAR_LAND_MODEL_SNOW:'Terreno osservabile senza neve rilevata dove il modello indicava neve: possibile sovrastima.',MIXED_SURFACE:'Superficie mista: la differenza non dimostra da sola un errore del modello.'}[r.evidence_status]||'')+' Non è una misura degli strati e non è stata assimilata.');
}
// Representative native SNOWPACK columns, selected by terrain. No spatial interpolation.
export const localLegend={missing:['#9aa7b1','Dati insufficienti / controllo fallito'],snow:['#52cfea','Neve plausibile · simulata'],candidate:['#ffbc51','Neve + pendio ripido · candidato'],factors:['#ff7556','Candidato con carico/acqua simulati'],zero:['#718491','Neve non simulata · non osservazione']};
export function localMember(m,k){const e=m?.[k];return e?.alias==='NWP_INITIAL'?m.NWP_INITIAL:e;}
export function localAssessment(product,feature,lead=0,now=Date.now()){
 const p=feature.properties,m=product.metadata,age=(now-Date.parse(m.reference_utc))/3600000,weatherAge=(now-Date.parse(m.weather_run_utc))/3600000;
 const missing=reason=>({kind:'missing',reason,hs:null,lead});
 if(m.temporal_mode==='RETROSPECTIVE_CACHED_FORCING')return missing('Ricostruzione storica datata: non è una valutazione corrente del pericolo');
 if(![0,24,48,72].includes(lead))return missing('Orizzonte non supportato');
 if(!Number.isFinite(age)||age<0||age>9||!Number.isFinite(weatherAge)||weatherAge<0||weatherAge>12)return missing('Prodotto scaduto o data non verificabile');
 const members=product.models[p.profile_id],entries=['NWP_INITIAL','ZERO_INITIAL'].map(k=>localMember(members,k));
 if(entries.some(x=>!x)&&String(m.failures?.[p.profile_id]||'').startsWith('WEATHER_SUPPORT_UNAVAILABLE'))return missing(['noaa_gfs','icon2i_hybrid'].includes(m.weather_provider)?'Meteo o storico non utilizzabile per questo supporto; dati GFS mancanti o qualità insufficiente':'Meteo mancante: acquisizione in attesa della quota della sorgente pubblica');
 if(entries.some(x=>!x))return missing(p.quality_code==='FOREST_CANOPY_NOT_MODELED'?'Bosco noto: modello della chioma non disponibile':p.profile_id?(m.status==='RUNNING'?'Calcolo ancora in corso per questo supporto':'Profilo non disponibile o rifiutato dai controlli fisici'):'Nessuna colonna rappresentativa compatibile');
 const windows=entries.map(x=>x.result.forecast_windows[String(lead)]),hs=entries.map(x=>x.hourly.quantities.hs[lead]);
 if(hs.some(x=>typeof x!=='number'||!Number.isFinite(x)||x<0)||windows.some(x=>!x))return missing('Output incompleto');
 const load=entries.map((x,i)=>lead===0?x.recent24?.net_swe_increase_kg_m2:windows[i].max_net_swe_increase_kg_m2),water=entries.map((x,i)=>lead===0?x.recent24?.water_max_kg_m2:windows[i].liquid_water_max_kg_m2);
 if([...load,...water].some(x=>typeof x!=='number'||!Number.isFinite(x)))return missing('Storico o finestra incompleta');
 const hsMax=entries.map((x,i)=>lead===0?hs[i]:windows[i].forecast_hs_max_cm);if(hsMax.some(x=>typeof x!=='number'||!Number.isFinite(x)||x<0))return missing('Massimo neve nella finestra incompleto');
 const snow=hs.some(x=>x>0),windowSnow=hsMax.some(x=>x>0),steep=p.terrain_steep===true,signal=load.some(x=>x>.001)||water.some(x=>x>.001);
 return {kind:steep&&windowSnow?(signal?'factors':'candidate'):snow?'snow':'zero',hs,hsMax,load,water,entries,windows,lead,identicalInitial:entries[0].history_initial_hs_m===entries[1].history_initial_hs_m,reason:'Indicatori condizionali, instabilità e distacco non validati'};
}
export async function verifiedLocalAsset(product,descriptor){
 if(!descriptor||!/^assets\/[a-f0-9]{64}\.(bin|png|json)$/.test(descriptor.file)||!Number.isInteger(descriptor.bytes)||descriptor.bytes>8*1024*1024)throw Error('Asset locale non valido');
 const r=await fetch(product.asset_base+'/'+descriptor.file,{cache:'force-cache'});if(!r.ok)throw Error('Asset locale assente');const buffer=await r.arrayBuffer();
 const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',buffer))].map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==descriptor.sha256||buffer.byteLength!==descriptor.bytes)throw Error('Integrità asset locale fallita');return buffer;
}
async function loadExplanationTrace(p){
 try{const base='/assets/avalanche-explanation-history',response=await fetch(base+'/manifest.json',{cache:'no-store'});if(!response.ok)throw Error('Cronologia non disponibile');const m=await response.json();if(p.explanation_trace?.trace_sha256===m.sha256)return;const raw=await verifiedLocalAsset({asset_base:base},m),t=JSON.parse(new TextDecoder().decode(raw));if(t.schema!=='hazardia.avalanche.explanation-history/1.0'||t.model_sha256!==p.content_sha256)throw Error('Cronologia non corrispondente al prodotto');p.explanation_trace={...t,trace_sha256:m.sha256,status:'AVAILABLE'};
 }catch(error){p.explanation_trace={status:'UNAVAILABLE',reason:error.message};}
}
export async function fetchLocal(previous=null){
 let base='/assets/avalanche-gran-sasso-full';let response=await fetch(base+'/manifest.json',{cache:'no-store'});
 if(response.status===404){base='/assets/avalanche-gran-sasso-local';response=await fetch(base+'/manifest.json',{cache:'no-store'});}
 if(!response.ok)throw Error('Prodotto locale non disponibile');const manifest=await response.json();
 if(!/^[a-f0-9]{64}$/.test(manifest.sha256)||manifest.file!=='objects/'+manifest.sha256+'.json'||manifest.bytes>24*1024*1024)throw Error('Manifest locale non valido');
 let product=previous;
 if(previous?.content_sha256!==manifest.sha256){
  const file=await fetch(base+'/'+manifest.file,{cache:'no-store'});if(!file.ok)throw Error('Output locale assente');const buffer=await file.arrayBuffer();
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',buffer))].map(x=>x.toString(16).padStart(2,'0')).join('');if(buffer.byteLength!==manifest.bytes||hash!==manifest.sha256)throw Error('Integrità prodotto locale fallita');
  product=JSON.parse(new TextDecoder().decode(buffer));if(!['hazardia.avalanche.local-terrain-assessment/1.0','hazardia.avalanche.local-terrain-assessment/1.1'].includes(product.schema)||product.type!=='FeatureCollection')throw Error('Schema locale incompatibile');product.content_sha256=manifest.sha256;product.asset_base=base;
  if(product.raster_index){
   const index=await verifiedLocalAsset(product,product.raster_index);if(index.byteLength!==product.raster_index.width*product.raster_index.height*2)throw Error('Dimensione indice non valida');product.index_view=new DataView(index);product.features_by_id=new Map(product.features.map(f=>[f.properties.profile_id,f]));product.images={};const blobs=new Map();
   for(const [key,d] of Object.entries(product.raster_views)){if(!blobs.has(d.sha256)){const bytes=await verifiedLocalAsset(product,d);blobs.set(d.sha256,URL.createObjectURL(new Blob([bytes],{type:'image/png'})));}product.images[key]=blobs.get(d.sha256);}
  }
  if(previous?.images)for(const url of new Set(Object.values(previous.images)))URL.revokeObjectURL(url);
 }
 try{const r=await fetch(base+'/status.json',{cache:'no-store'});if(r.ok)product.operational_status=await r.json();}catch{}await loadExplanationTrace(product);return product;
}
export function localFeatureAt(product,lon,lat){
 const g=product.raster_index;if(!g||!product.index_view)return null;const [west,south,east,north]=g.bounds;if(lon<west||lon>=east||lat<=south||lat>north)return null;
 let col,row;if(g.crs==='EPSG:3857'){const [x0,y0,x1,y1]=g.projected_bounds,x=6378137*lon*Math.PI/180,y=6378137*Math.log(Math.tan(Math.PI/4+lat*Math.PI/360));col=Math.floor((x-x0)/(x1-x0)*g.width);row=Math.floor((y1-y)/(y1-y0)*g.height);}else{col=Math.floor((lon-west)/(east-west)*g.width);row=Math.floor((north-lat)/(north-south)*g.height);}if(col<0||row<0||col>=g.width||row>=g.height)return null;const label=product.index_view.getUint16((row*g.width+col)*2,true);if(label===0)return null;
 if(label===65535)return {type:'Feature',properties:{id:'GS-FOREST',profile_id:null,quality_code:'FOREST_CANOPY_NOT_MODELED'}};
 return product.features_by_id?.get(g.labels[String(label)])||null;
}
export function localPopupDetail(product,feature,lead){
 if(!product.profile_assets?.[feature.properties.profile_id])return localDetail(product,feature,lead);
 const box=document.createElement('div');box.textContent='Caricamento profilo nivologico e provenienza…';product.full_profiles??=new Map();const id=feature.properties.profile_id;
 if(!product.full_profiles.has(id)&&product.full_profiles.size>=64)product.full_profiles.delete(product.full_profiles.keys().next().value);
 if(!product.full_profiles.has(id))product.full_profiles.set(id,verifiedLocalAsset(product,product.profile_assets[id]).then(bytes=>JSON.parse(new TextDecoder().decode(bytes))));
 product.full_profiles.get(id).then(members=>box.replaceChildren(localDetail({...product,models:{...product.models,[id]:members}},feature,lead))).catch(error=>{box.replaceChildren(localDetail(product,feature,lead));const p=document.createElement('p');p.textContent='Profilo completo non disponibile: '+error.message;box.append(p);});return box;
}

export function localDetail(product,feature,lead,now=Date.now()){
 const div=document.createElement('div');div.dataset.avalancheLocal=feature.properties.id;
 const add=(tag,text)=>{const el=document.createElement(tag);el.textContent=text;div.append(el);return el;},fmt=x=>Number.isFinite(x)?x.toLocaleString('it-IT',{maximumFractionDigits:2}):'mancante',range=xs=>xs.map(fmt).join(' / '),p=feature.properties,a=localAssessment(product,feature,lead,now);
 add('h3',localLegend[a.kind][1]);add('p','Origine: terreno e previsioni meteo reali; neve e strati simulati. Inizializzazione schematica NWP/zero, non profilo misurato. Sperimentale significa metodo di segnalazione non ancora validato con eventi e misure locali.');add('p',p.id+' · '+(lead?'Previsione al ':'Stato ricostruito al ')+new Date(Date.parse(product.metadata.reference_utc)+lead*3600000).toLocaleString('it-IT',{timeZone:'Europe/Rome'})+' · '+(lead?'+'+lead+'ore':'riferimento simulato'));
 add('p','Quota '+fmt(p.elevation_min_m)+'–'+fmt(p.elevation_max_m)+'m · pendenza '+fmt(p.slope_min_deg)+'–'+fmt(p.slope_max_deg)+'°.');
 add('p',localForcingDescription(product.metadata));for(const text of localSnowEvidenceText(feature))add('p',text);
 if(a.kind==='missing'){
  add('p',a.reason+'. Non significa assenza di neve o sicurezza.');
  const archived=localMember(product.models[p.profile_id],'NWP_INITIAL');
  if(archived){add('h4','Manto simulato conservato · consultazione storica');add('p','Profilo '+p.profile_id+' · riferimento '+product.metadata.reference_utc+' · ciclo meteo '+product.metadata.weather_run_utc+'. Questi valori non qualificano il pericolo corrente.');add('p','Storico '+archived.history_start+' → '+product.metadata.reference_utc+' · '+archived.history_hours+' ore; '+archived.profile_at_reference.layers+' strati simulati, non misurati.');for(const h of [0,24,48,72])add('p',new Date(Date.parse(product.metadata.reference_utc)+h*3600000).toLocaleString('it-IT',{timeZone:'Europe/Rome'})+' · manto simulato '+fmt(archived.hourly.quantities.hs[h])+'cm');for(const row of archived.profile_at_reference.rows||[])add('p','Strato simulato: spessore normale al pendio '+fmt(Number(row.Layer_Thick)*100)+'cm · T '+fmt(Number(row.T)-273.15)+'°C');}
  return div;
 }
 add('p','Profilo '+p.profile_id+' · quota '+fmt(p.profile_elevation_m)+'m · inclinazione '+fmt(p.profile_slope_deg)+'° · esposizione '+fmt(p.profile_aspect_deg)+'°; distanza massima '+fmt(p.max_profile_distance_m/1000)+'km. Selezione per fasce di quota/pendenza/esposizione, non interpolazione.');
 add('strong','Manto simulato '+(lead?'al termine della finestra':'al riferimento')+': '+range(a.hs)+'cm');if(lead)add('p','Massimo manto nelle24ore precedenti: '+range(a.hsMax)+'cm. I colori caldi descrivono fattori nella finestra, anche se la neve fonde prima del termine.');
 add('p','Due ipotesi iniziali (neve NWP / terreno inizialmente senza neve). '+(a.identicalInitial?'In questo caso coincidono: non sono due evidenze indipendenti.':'La differenza descrive solo la sensibilità iniziale, non un intervallo di confidenza.'));
 const e=a.entries[0],pr=e.profile_at_reference;
 if(e.forcing_support){const w=e.forcing_support;if(w.native_grid&&product.metadata.weather_provider!=='icon2i_hybrid')add('p','Forzante NOAA GFS0,25°: cella nativa '+fmt(w.native_grid.lat)+'N, '+fmt(w.native_grid.lon)+'E, quota modello '+fmt(w.native_grid.elevation_m)+'m. Nessuna correzione altimetrica; dato a circa25km, rappresentatività degradata su questi pendii.');add('p','Forzante meteo rappresentativa: distanza '+fmt(w.distance_m/1000)+'km, differenza di quota '+fmt(w.elevation_difference_m)+'m. Nessuna correzione termica locale aggiunta; meteo non risolto a30m.');}
 add('p','Posizione del profilo simulato: '+fmt(e.terrain_point.lat)+'N, '+fmt(e.terrain_point.lon)+'E.');
 add('p','Storico ricostruito: '+e.history_start+' → '+product.metadata.reference_utc+' ('+e.history_hours+' ore). Forzanti: previsioni meteorologiche archiviate concatenate, non misure locali. Stato SNO/HAZ conservato nel passaggio alla previsione.');
 add('p','Manto al riferimento: '+pr.layers+' livelli nel file simulato. Profilo stratigrafico non misurato; strati deboli e stabilità non verificati.');
 const layers=add('details',''),summary=document.createElement('summary');summary.textContent='Profilo simulato al riferimento · spessore e temperatura';layers.append(summary);
 for(const row of pr.rows){const line=document.createElement('div');line.textContent='Spessore normale al pendio '+fmt(Number(row.Layer_Thick)*100)+'cm · T '+fmt(Number(row.T)-273.15)+'°C · acqua '+fmt(Number(row.Vol_Frac_W)*100)+'%';layers.append(line);}
 add('p',(lead?'Finestra precedente di24ore: ':'Ultime24ore ricostruite: ')+'incremento netto massimo SWE '+range(a.load)+'kg/m² · acqua massima '+range(a.water)+'kg/m². Soglia0,001: tolleranza descrittiva, non soglia di instabilità; massimi anche in istanti diversi.');
 const w=a.windows[0];add('p',(lead?'Meteo previsto nella finestra: T ':'Forzante meteo al riferimento (NWP): T ')+fmt(w.air_temperature_min_c)+'–'+fmt(w.air_temperature_max_c)+'°C · vento massimo '+fmt(w.wind_max_ms)+'m/s. Radiazione sul pendio elaborata da SNOWPACK; ombre topografiche e trasporto eolico locale non simulati.');
 const reset=product.models[p.profile_id].RESET_BASELINE; if(reset)add('p','Confronto senza ricostruzione storica: '+fmt(reset.hourly.quantities.hs[lead])+'cm, rispetto a '+fmt(a.hs[0])+'cm con storico. È una differenza tra simulazioni, non una misura di accuratezza.');
 add('p','Vegetazione nota su '+fmt(100*p.cover_known_pixels/p.pixels)+'% del supporto. Bosco noto escluso dal modello senza chioma; suolo/substrato non determinano attrito calibrato.');
 add('p','Neve plausibile e combinazioni da verificare: non previsione certa di valanga. Mancano profili osservati, stabilità, vento locale e propagazione; anche aree a valle possono essere coinvolte.');
 add('p','Bollettino ufficiale non collegato a questo esperimento; nessun grado EAWS locale attribuito.');
 add('p','Esperimento '+product.metadata.experiment_id+' · '+product.metadata.qualification);return div;
}

// Screen-space aggregation affects only symbols, never the underlying assessment.
export function groupAvalanchePins(candidates,zoom){
 const size=256*2**Math.max(2,Math.min(20,zoom)),groups=new Map();
 for(const item of candidates){
  if(!Number.isFinite(item.lat)||!Number.isFinite(item.lon)||Math.abs(item.lat)>85||Math.abs(item.lon)>180)continue;
  const x=(item.lon+180)/360*size,y=(1-Math.log(Math.tan(Math.PI/4+item.lat*Math.PI/360))/Math.PI)/2*size;
  const key=Math.floor(x/64)+':'+Math.floor(y/64);let g=groups.get(key);
  if(!g){g={members:[],lat:0,lon:0,kind:'candidate'};groups.set(key,g);}
  g.members.push(item);g.lat+=item.lat;g.lon+=item.lon;if(item.kind==='factors')g.kind='factors';
 }
 return [...groups.values()].map(g=>({...g,lat:g.lat/g.members.length,lon:g.lon/g.members.length,count:g.members.length}));
}
export function localAvalanchePins(product,lead,now=Date.now()){
 const out=[];
 for(const feature of product.features){
  const a=localAssessment(product,feature,lead,now);if(!['candidate','factors'].includes(a.kind))continue;
  const id=feature.properties.profile_id,p=product.models[id]?.NWP_INITIAL?.terrain_point;
  if(p)out.push({id,feature,lat:p.lat,lon:p.lon,kind:a.kind});
 }
 return out;
}

export function selectedTerrainLabels(product,ids){
 const selected=new Set(ids),labels=new Uint8Array(65536);
 for(const [label,id] of Object.entries(product.raster_index.labels))if(selected.has(id)&&Number(label)>0&&Number(label)<65535)labels[Number(label)]=1;
 return labels;
}
export function paintSelectedTerrain(index,selected,firstRow,lastRow,rgba,extent=null,mask=null){
 const w=index.width,h=index.height,view=index.view;let count=0;
 const yes=(r,c)=>r>=0&&r<h&&c>=0&&c<w&&(!mask||mask[r*w+c])&&selected[view.getUint16((r*w+c)*2,true)]===1;
 for(let r=firstRow;r<Math.min(h,lastRow);r++)for(let c=0;c<w;c++)if(yes(r,c)){
  const edge=!yes(r-1,c)||!yes(r+1,c)||!yes(r,c-1)||!yes(r,c+1),i=(r*w+c)*4;
  rgba[i]=255;rgba[i+1]=235;rgba[i+2]=35;rgba[i+3]=edge?255:95;count++;if(extent){extent[0]=Math.min(extent[0],c);extent[1]=Math.min(extent[1],r);extent[2]=Math.max(extent[2],c+1);extent[3]=Math.max(extent[3],r+1);}
 }
 return count;
}
export function pinForecastRows(product,features,now=Date.now()){
 return [0,24,48,72].map(lead=>{
  const assessments=features.map(f=>localAssessment(product,f,lead,now)),valid=assessments.filter(a=>a.kind!=='missing');
  const values=key=>valid.flatMap(a=>a[key]||[]).filter(Number.isFinite),hs=values('hs'),load=values('load'),water=values('water');
  return {lead,total:features.length,missing:assessments.length-valid.length,candidates:valid.filter(a=>['candidate','factors'].includes(a.kind)).length,loadUnits:valid.filter(a=>['candidate','factors'].includes(a.kind)&&a.load.some(v=>v>.001)).length,waterUnits:valid.filter(a=>['candidate','factors'].includes(a.kind)&&a.water.some(v=>v>.001)).length,hsMin:hs.length?Math.min(...hs):null,hsMax:hs.length?Math.max(...hs):null,loadMax:load.length?Math.max(...load):null,waterMax:water.length?Math.max(...water):null};
 });
}
