/* Dated observed national radar, independent of forecast graphics and forcing. */
export function radarLayer(map,host){
 const box=document.createElement('details');box.className='dock-section radar-layer';box.innerHTML='<summary>Radar osservato · Italia</summary><label><input type="checkbox" aria-label="Mostra radar pioggia osservata"> Pioggia radar SRI</label><p role="status">Attiva per consultare il radar all’ora della timeline.</p><div class="radar-key"><span><i style="background:#3a9edc"></i>0,1–1</span><span><i style="background:#256fda"></i>1–2,5</span><span><i style="background:#6a44c7"></i>2,5–5</span><span><i style="background:#bf3789"></i>5–10</span><span><i style="background:#dc3835"></i>≥10 mm/h</span></div><small>Trasparente: &lt;0,1 mm/h. Tratteggio grigio: dati mancanti. Radar-DPC · CC BY-SA · griglia nominale1km. Prodotto divulgativo; manutenzioni e anomalie possibili. Non è una previsione o un’allerta.</small>';
 host.append(box);const check=box.querySelector('input'),state=box.querySelector('[role=status]'),key=box.querySelector('.radar-key');let enabled=false,visible=true,at=null,gen=0,timer=null,abort=null;
 map.createPane('observedRadar');map.getPane('observedRadar').style.zIndex=430;const layers=L.layerGroup().addTo(map);const legend=L.control({position:'bottomleft'});let legendEl=null;legend.onAdd=()=>{legendEl=L.DomUtil.create('div','radar-map-legend');legendEl.hidden=true;return legendEl;};legend.addTo(map);
 const credit='<a href="https://mappe.protezionecivile.gov.it/it/mappe-e-dashboard-rischi/piattaforma-radar/">Radar-DPC</a> · CC BY-SA';
 function clear(){layers.clearLayers();if(legendEl)legendEl.hidden=true;map.getContainer().dataset.radarAt='';}
 async function load(refresh=true){
  if(!enabled||!visible||!at)return;const token=++gen;abort?.abort();abort=new AbortController();clear();state.textContent='Caricamento dell’osservazione radar per '+at+'…';
  try{const response=await fetch('/api/monitoring/radar?at='+encodeURIComponent(at),{signal:abort.signal});if(!response.ok)throw Error('Servizio radar non disponibile');const result=await response.json();if(token!==gen||!enabled||!visible)return;
   if(result.status==='AVAILABLE'){
    const data=result.data;const bounds=L.latLngBounds(data.bounds);if(!bounds.intersects(map.getBounds())){state.textContent='Radar-DPC non copre la vista selezionata. Copertura nazionale, non globale.';return;}
    for(const image of [data.image,data.missing_image])L.imageOverlay(image,data.bounds,{pane:'observedRadar',opacity:1,interactive:false}).addTo(layers);
    map.getContainer().dataset.radarAt=data.at;map.getContainer().dataset.radarWetFraction=String(data.wet_fraction);state.textContent='OSSERVAZIONE · '+data.at+' · passo5min · '+data.units+' · acquisita '+data.updated_at+'. Copertura valida nel mosaico: '+Math.round(data.valid_fraction*100)+'%. Mancanze indicate con tratteggio; la mappa non certifica l’assenza di pioggia.';
    legendEl.replaceChildren();const title=document.createElement('strong');title.textContent='Radar osservato · '+new Date(data.at).toLocaleTimeString('it-IT',{timeZone:'Europe/Rome',hour:'2-digit',minute:'2-digit'})+' Roma';legendEl.append(title,key.cloneNode(true));const note=document.createElement('small');note.textContent='mm/h · tratteggio: dato mancante · fonte Radar-DPC';legendEl.append(note);legendEl.hidden=false;return;
   }
   state.textContent=(result.status==='OUTSIDE_VALIDITY'?'Nessuna osservazione radar per quest’ora. Copertura temporale: ultime24h, nessuna previsione.':result.error||'Osservazione non ancora disponibile per l’ora selezionata.')+' '+(result.detail||'');
   if(result.busy){timer=setTimeout(()=>load(false),1200);return;}
   if(refresh&&result.status!=='OUTSIDE_VALIDITY'&&!result.error){await fetch('/api/monitoring/radar/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:JSON.stringify({at}),signal:abort.signal});if(token===gen)timer=setTimeout(()=>load(false),1200);}
  }catch(error){if(error.name!=='AbortError'&&token===gen)state.textContent=error.message+' · Nessun radar sostitutivo mostrato.';}
 }
 function schedule(value){if(value)at=value;gen++;abort?.abort();clearTimeout(timer);clear();if(enabled&&visible)timer=setTimeout(()=>load(),600);}
 check.onchange=()=>{enabled=check.checked;if(enabled){map.attributionControl.addAttribution(credit);at=document.getElementById('wind-hour')?.value||at;if(!at)state.textContent='Seleziona un’ora dalla timeline meteo.';schedule();}else{map.attributionControl.removeAttribution(credit);schedule();state.textContent='Radar nascosto.';}};
 document.addEventListener('hazardia-weather-time',e=>schedule(e.detail?.at));document.addEventListener('hazardia-weather-field',e=>schedule(e.detail?.at));map.on('moveend',()=>schedule());
 return {visible(on){visible=on;schedule();}};
}
