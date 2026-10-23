import {mapSymbols} from '/map-symbols.js?v=1';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>Number(n).toLocaleString('it-IT',{maximumFractionDigits:1});
const date=v=>new Date(v).toLocaleString('it-IT',{timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});
export const observedColor=mm=>mm===0?'#ffffff':mm<1?'#7bc9ed':mm<5?'#228ac1':mm<10?'#7554bb':mm<20?'#bd3977':'#a11e32';
export function observedRain(map,host){
 let enabled=false,visible=true,result=null,fetching=false,selectedHour=null,pointLayers=new Map();
 const renderer=L.canvas({padding:.1}),layer=L.layerGroup().addTo(map);
 const box=document.createElement('details');box.className='observed-rain-config';box.open=true;
 box.innerHTML='<summary>Pioggia osservata · pluviometri</summary><label><input type="checkbox"> Mostra le misure delle stazioni</label><label>Esamina stazione<select aria-label="Stazione pluviometrica"><option value="">Seleziona un sensore…</option></select></label><div class="observed-rain-detail" aria-live="polite"></div><p class="observed-rain-state" role="status">Attiva per acquisire le ultime misure disponibili.</p><p class="rain-zone-note">Cerchi: accumulo misurato nell’ora precedente l’orario della stazione. Bianco 0 · azzurro &lt;1 · blu 1–5 · viola 5–10 · fucsia 10–20 · rosso ≥20 mm. Cerchio tratteggiato: dato vecchio (&gt;90 min). Le aree senza sensori restano sconosciute.</p><p class="rain-zone-note">Reti regionali e amatoriali, dati provvisori non validati. Clicca un punto per fonte, orario, qualità e licenza. Le misure non sono allerte e non sono previsioni.</p>';
 host.append(box);const check=box.querySelector('input'),state=box.querySelector('[role="status"]'),select=box.querySelector('select');
 document.getElementById('monitor-weather').addEventListener('change',draw);
 select.onchange=()=>pointLayers.get(select.value)?.openPopup();
 function draw(){
  layer.clearLayers();pointLayers.clear();box.querySelector('.observed-rain-detail').textContent='';select.innerHTML='<option value="">Seleziona un sensore…</option>';mapSymbols(map).set('observed-rain',[]);map.getContainer().dataset.observedRainStations='0';
  if(!enabled||!visible||!document.getElementById('monitor-weather')?.checked)return;
  if(!result?.data){state.textContent=result?.error||'Misure non disponibili. Nessuna osservazione sostituita con una previsione.';return;}
  if(selectedHour&&Date.parse(selectedHour)>Date.now()+3600000){state.textContent='Ora futura: osservazioni non ancora disponibili. Torna all’ora attuale per vedere le misure.';return;}
  const inView=result.data.features.filter(f=>map.getBounds().contains([f.geometry.coordinates[1],f.geometry.coordinates[0]]));
  const all=inView.filter(f=>!selectedHour||(Date.parse(f.properties.until)>Date.parse(selectedHour)-7200000&&Date.parse(f.properties.until)<=Date.parse(selectedHour)));
  // One station per 36 px cell, highest observed amount first. No area interpolation.
  const cells=new Set(),points=[];
  for(const f of all.slice().sort((a,b)=>b.properties.mm-a.properties.mm||a.properties.id.localeCompare(b.properties.id))){const p=map.latLngToContainerPoint([f.geometry.coordinates[1],f.geometry.coordinates[0]]),cell=Math.floor(p.x/36)+','+Math.floor(p.y/36);if(cells.has(cell)||points.length>=350)continue;cells.add(cell);points.push(f);}
  const fresh=points.filter(f=>f.properties.freshness==='FRESH').length;
  state.textContent=points.length+'/'+all.length+' sensori nell’inquadratura · '+fresh+' recenti.'+(selectedHour?' Misure disponibili all’ora '+date(selectedHour)+' Roma.':' Ultime misure disponibili.')+(!all.length?' Nessuna misura disponibile per questa area/ora; non significa assenza di pioggia.':'')+' Ultima acquisizione '+date(result.data.acquired_at)+' Roma.'+(all.length>points.length?' Punti diradati per leggibilità, con precedenza agli accumuli maggiori; ingrandisci per più dettaglio.':'')+(result.status==='STALE'?' CACHE SCADUTA.':'')+(result.error?' Ultimo aggiornamento fallito: '+result.error:'');
  for(const f of points){const p={...result.data.networks?.[f.properties.network],...f.properties},stale=p.freshness!=='FRESH',time=date(p.from_at)+' → '+date(p.until)+' Roma';
   const title=p.name+' · '+fmt(p.mm)+' mm osservati · '+time;
   const popup='<strong>'+esc(p.name)+'</strong><br><strong>'+fmt(p.mm)+' mm osservati / 1 h</strong><br>'+esc(time)+'<br>'+esc(p.network_name)+' · '+esc(p.network_description)+'<br>'+esc(p.attribution_description)+' · <a target="_blank" rel="noopener" href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a><br>'+(stale?'DATO VECCHIO':'Dato recente')+' · ritardo '+fmt(p.age_minutes)+' min<br>Controllo sorgente rel=1; misura provvisoria non validata. Equivalente d’acqua, può includere neve.<br>Nessuna indicazione di rischio per le aree circostanti.<br><a target="_blank" rel="noopener" href="https://meteohub.agenziaitaliameteo.it/app/maps/observations">Fonte: ItaliaMeteo / MeteoHub</a>';
   select.insertAdjacentHTML('beforeend','<option value="'+esc(p.id)+'">'+esc(p.name)+' · '+fmt(p.mm)+' mm · '+esc(p.network_name)+'</option>');
   const marker=L.circleMarker([f.geometry.coordinates[1],f.geometry.coordinates[0]],{renderer,radius:p.mm===0?3:map.getZoom()>=10?7:5,color:stale?'#61727c':'#183c55',weight:2,dashArray:stale?'3 3':undefined,fillColor:observedColor(p.mm),fillOpacity:stale?.35:p.mm===0?.65:.95,bubblingMouseEvents:false}).bindTooltip(esc(title)).bindPopup(popup,{autoPan:false}).addTo(layer);marker.on('popupopen',()=>{box.querySelector('.observed-rain-detail').innerHTML=popup;});pointLayers.set(p.id,marker);
  }
  mapSymbols(map).set('observed-rain',points.length?[{label:'Pluviometri · pioggia osservata',kind:'point',count:points.length,color:'#183c55',fill:'#228ac1',fillOpacity:1,note:'Punti misurati, non aree di pioggia. Colori per accumulo orario: bianco 0; azzurro <1; blu 1–5; viola 5–10; fucsia 10–20; rosso ≥20 mm. Tratteggio: oltre 90 minuti. Fonte e orario nel popup.'}]:[]);
  map.getContainer().dataset.observedRainStations=String(points.length);
 }
 async function refresh(){
  if(!enabled||!visible||fetching||document.hidden)return;fetching=true;
  try{
   const accepted=await fetch('/api/monitoring/observed-rain/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:'{}'});if(!accepted.ok)throw Error('Acquisizione non disponibile');
   for(let i=0;i<25;i++){const r=await fetch('/api/monitoring/observed-rain');if(!r.ok)throw Error('Lettura osservazioni non disponibile');result=await r.json();if(!enabled||!visible)return;draw();if(!result.busy)break;await new Promise(resolve=>setTimeout(resolve,1500));}
  }catch(e){state.textContent=e.message+' · Le eventuali misure precedenti conservano il proprio orario.';}
  finally{fetching=false;}
 }
 const attribution='Misure: <a href="https://meteohub.agenziaitaliameteo.it/app/maps/observations">ItaliaMeteo / MeteoHub</a> · reti nei dettagli · CC BY 4.0';
 check.onchange=()=>{enabled=check.checked;if(enabled)map.attributionControl.addAttribution(attribution);else map.attributionControl.removeAttribution(attribution);selectedHour=document.getElementById('wind-hour')?.value||selectedHour;if(enabled){state.textContent='Acquisizione delle misure nella VM…';refresh();}else{state.textContent='Misure nascoste.';draw();}};
 map.on('moveend',draw);
 document.addEventListener('hazardia-weather-field',e=>{selectedHour=e.detail?.at||selectedHour;draw();});
 document.addEventListener('hazardia-monitor-time',e=>{selectedHour=e.detail?.at||null;draw();});
 setInterval(()=>{if(enabled&&visible)refresh();},65000);
 return {visible(on){visible=on;draw();if(on&&enabled)refresh();}};
}
