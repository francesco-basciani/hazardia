import {locale} from '/i18n.js';
import {monitorTimeline} from '/monitor-timeline.js';
import {forecastWindow,rainColors,usesForecast} from '/forecast-window.js';
/* Reuses the VM zonal rainfall calculation. No rainfall-to-impact model or DPC
   warning is manufactured. One 48-hour series supports many timeline frames. */
export function forecastAttention(map,host,enabled){
 const box=document.createElement('section');box.className='attention-validity forecast-attention';
 box.innerHTML='<h4>Evoluzione prevista del territorio</h4><label>Vista temporale<select aria-label="Vista temporale delle criticità"><option value="auto">Automatica · previsioni nelle ore future</option><option value="official">Solo bollettino ufficiale DPC</option><option value="forecast">Precipitazioni previste per zona</option></select></label><label>Intervallo di previsione<select aria-label="Intervallo della previsione territoriale">'+[1,3,6,12,24].map(h=>'<option value="'+h+'"'+(h===3?' selected':'')+'>'+h+' h</option>').join('')+'</select></label><p>Le aree previste cambiano con l’ora selezionata. Quantità di precipitazione calcolate dal modello, non allerte ufficiali né rischio di allagamento validato.</p><p class="forecast-attention-state" role="status"></p><div class="forecast-attention-key"></div>';
 host.prepend(box);
 const mode=box.querySelector('select'),period=box.querySelectorAll('select')[1],status=box.querySelector('[role=status]'),key=box.querySelector('.forecast-attention-key');
 key.innerHTML=['<1','1–10','10–30','30–60','≥60'].map((n,i)=>'<span><i style="background:'+rainColors[i]+'"></i>'+n+' mm</span>').join('')+'<p>Tinta chiara: meno di 1 mm nel periodo. Non indica assenza di allerta. Grigio: dati incompleti.</p>';
 map.createPane('territorialForecast');map.getPane('territorialForecast').style.zIndex=415;
 const layer=L.layerGroup().addTo(map);let at=monitorTimeline.at,field=null,result=null,pending=false,revision=0,timer,retryTimer,controller,active=false,failure='';
 const fmt=n=>n.toLocaleString(locale(),{maximumFractionDigits:2}),date=t=>new Date(t).toLocaleString(locale(),{timeZone:'Europe/Rome',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});
 const currentHour=()=>new Date(Math.floor(Date.parse(at)/3600000)*3600000).toISOString().replace('.000Z','Z');
 function clear(){layer.clearLayers();delete map.getContainer().dataset.territorialForecastAt;map.getContainer().dataset.territorialForecastZones='0';}
 function allowed(){return enabled.checked&&usesForecast(mode.value,at);}
 function draw(){
  clear();const next=!!allowed();if(next!==active){active=next;map.getContainer().dataset.territorialForecastMode=String(active);map.fire('territorialforecastmode',{enabled:active});}
  period.closest('label').hidden=!active;key.hidden=!active;
  if(!active){status.textContent='Vista bollettino: l’allerta ufficiale resta valida nel suo intervallo di emissione.';return;}
  if(!result){status.textContent=failure||'Calcolo delle previsioni per zona nella VM…';return;}
  if(Date.now()-Date.parse(result.forecast_available_at)>=10800000){result=null;status.textContent='Previsione scaduta: nessuna indicazione attuale.';return;}
  const hours=Number(period.value),readings=new Map(result.features.map(f=>[f.properties.id,forecastWindow(f.properties.hourly_forecast,at,hours)]));
  const local=result.features.filter(f=>{const b=f.properties.bounds_wgs84;return b&&L.latLngBounds([[b[1],b[0]],[b[3],b[2]]]).intersects(map.getBounds());}),known=local.filter(f=>readings.get(f.properties.id).status==='AVAILABLE');
  L.geoJSON({type:'FeatureCollection',features:local},{pane:'territorialForecast',bubblingMouseEvents:false,style:f=>{const r=readings.get(f.properties.id),ok=r.status==='AVAILABLE';return {fillColor:ok?rainColors[r.band]:'#83909b',color:ok?rainColors[r.band]:'#83909b',fillOpacity:ok?.34:.10,weight:1.5,dashArray:ok?undefined:'4 4'};},onEachFeature:(f,l)=>{const r=readings.get(f.properties.id);l.bindTooltip(String(f.properties.name).replace(/[&<>"']/g,'')+' · '+(r.status==='AVAILABLE'?fmt(r.mean_mm)+' mm / '+hours+' h':'dati incompleti')+' · previsione, non allerta');}}).addTo(layer);
  status.textContent=date(at)+' → '+date(Date.parse(currentHour())+hours*3600000)+' Roma · '+known.length+'/'+local.length+' zone nella vista coperte. Massimo delle medie di zona: '+(known.length?fmt(Math.max(...known.map(f=>readings.get(f.properties.id).mean_mm))):'—')+' mm. '+result.model+' · acquisito '+date(result.forecast_available_at)+'. Previsione di precipitazione, non allerta DPC.';
  map.getContainer().dataset.territorialForecastAt=at;map.getContainer().dataset.territorialForecastZones=String(known.length);map.getContainer().dataset.territorialForecastAssessment=result.assessment_id;
 }
 async function api(url,body,signal){const r=await fetch(url,{signal,...(body?{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:JSON.stringify(body)}:{})});const v=await r.json();if(!r.ok||v.status==='ERROR'){const error=new Error(v.detail||v.code||'Fonte non disponibile');error.code=v.code;throw error;}return v;}
 async function load(){
  if(!allowed()||pending||!at)return;const hour=currentHour();
  // A window may be incomplete at the horizon. Do not repeatedly request it.
  if(result&&Date.parse(hour)>=Date.parse(result.at)&&Date.parse(hour)<Date.parse(result.at)+48*3600000){draw();return;}
  const token=revision,requestedField=field;pending=true;controller=new AbortController();draw();
  try{
   let submitted;for(let attempt=0;attempt<8;attempt++){if(token!==revision||!allowed())return;try{submitted=await api('/api/monitoring/rain',requestedField?{at:hour,field_id:requestedField}:{at:hour},controller.signal);break;}catch(error){if(error.code!=='QUEUE_FULL'||attempt===7)throw error;status.textContent='Worker occupato: attendo il calcolo in corso…';await new Promise(resolve=>{retryTimer=setTimeout(resolve,1000);});}}let response;
   for(let i=0;i<45;i++){
    if(token!==revision||!allowed())return;
    response=await api('/api/monitoring/rain/'+submitted.id,null,controller.signal);
    if(response.status==='SUCCEEDED')break;
    await new Promise(resolve=>{retryTimer=setTimeout(resolve,1000);});
   }
   if(response?.status!=='SUCCEEDED'||response.freshness!=='FRESH')throw Error('Calcolo non disponibile o previsione scaduta');
   if(requestedField&&response.data.forecast_id!==requestedField)throw Error('Campo meteo diverso dalla mappa');
   if(token===revision&&allowed()){result=response.data;draw();}
  }catch(e){if(token===revision&&e.name!=='AbortError'){result=null;clear();failure='Previsione territoriale non disponibile: '+e.message;status.textContent=failure;}}
  finally{pending=false;controller=null;if(allowed()&&(token!==revision||result&&(Date.parse(currentHour())<Date.parse(result.at)||Date.parse(currentHour())>=Date.parse(result.at)+48*3600000)))schedule();}
 }
 function schedule(){clearTimeout(timer);failure='';draw();timer=setTimeout(load,250);}
 mode.onchange=()=>{revision++;controller?.abort();schedule();};period.onchange=draw;
 enabled.addEventListener('change',()=>{revision++;controller?.abort();schedule();});
 document.addEventListener('hazardia-monitor-time',e=>{if(!e.detail?.at)return;const next=new Date(Math.floor(Date.parse(e.detail.at)/3600000)*3600000).toISOString().replace('.000Z','Z');if(next===at)return;at=next;schedule();});
 document.addEventListener('hazardia-weather-field',e=>{const id=e.detail?.id||null;if(id===field)return;field=id;revision++;controller?.abort();result=null;schedule();});
 map.on('moveend',draw);map.on('unload',()=>{revision++;controller?.abort();clearTimeout(timer);clearTimeout(retryTimer);});
 schedule();
}
