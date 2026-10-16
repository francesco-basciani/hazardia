/* Read-only hazard overview: one chosen product per hazard, never a fused forecast. */
const $=id=>document.getElementById(id);
const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names={FIRE:'Incendio',FLOOD:'Alluvione'};
function date(v){return new Date(v).toLocaleString('it-IT',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'})+' · Roma';}
export function monitoringMap(initial,feedback){
 let catalog=initial,context=[],selected=null,failures=0,visible=true,labelsTimer;
 const map=L.map('monitor-map',{preferCanvas:true,scrollWheelZoom:false,keyboard:true}).setView([42.35,13.38],14);
 map.setMinZoom(8);map.setMaxZoom(20);map.setMaxBounds([[41.60,12.90],[42.97,14.86]]);map.attributionControl.setPrefix('HAZARDIA · Ricerca');
 map.createPane('monitorSatellite');map.getPane('monitorSatellite').style.zIndex=190;
 const satellite=L.imageOverlay('/assets/satellite.png',[[42.30,13.32],[42.40,13.44]],{opacity:1,pane:'monitorSatellite',attribution:'Contains modified Copernicus Sentinel data2024'}).addTo(map);
 // Keep flood below fire independent of filter/case toggle order.
 for(const [name,z] of [['monitorFlood',410],['monitorFire',420],['monitorNames',610]]){map.createPane(name);map.getPane(name).style.zIndex=z;}
 const ortho=L.tileLayer('/api/maps/ortho/{z}/{x}/{y}',{minZoom:8,maxZoom:20,maxNativeZoom:19,keepBuffer:1,updateWhenIdle:true,updateWhenZooming:false,bounds:[[41.6607,12.9714],[42.9053,14.7922]],attribution:'Ortofoto Regione Abruzzo 2018–2019 · 20 cm/px dichiarati'}).addTo(map);
 const labels=L.layerGroup().addTo(map),roads=L.layerGroup().addTo(map),point=L.layerGroup().addTo(map),products={FIRE:L.layerGroup().addTo(map),FLOOD:L.layerGroup().addTo(map)};
 L.control.scale({imperial:false,maxWidth:120}).addTo(map);
 map.attributionControl.addAttribution('© OpenStreetMap contributors · ODbL · GeoNames CC BY4.0');
 function source(){const online=$('monitor-basemap').value==='ortho';$('monitor-source').textContent=online?'Ortofoto aeree 2018–2019 · 20 cm/px dichiarati · online.'+(failures?' Alcune tessere non disponibili: scegli Sentinel offline.':''):'Sentinel-2 · 13/07/2024 · pixel10m · ritaglio offline. Fuori dal ritaglio lo sfondo non è disponibile.';}
 ortho.on('tileerror',()=>{failures++;source()});source();
 function chosen(kind){return catalog.scenarios.find(s=>s.hazard===kind&&s.id===$('monitor-'+kind.toLowerCase()+'-case').value);}
 function shown(){return ['FIRE','FLOOD'].filter(k=>$('monitor-'+k.toLowerCase()).checked).map(chosen).filter(Boolean);}
 function draw(){
  for(const kind of ['FIRE','FLOOD']){const key=kind.toLowerCase(),s=chosen(kind),enabled=$('monitor-'+key).checked;products[kind].clearLayers();$('monitor-'+key+'-case').disabled=!enabled||!s;const info=$('monitor-'+key+'-info');
   if(!s){info.textContent='Nessun risultato disponibile nel catalogo.';continue;}
   const legend=kind==='FIRE'?'Arancio · probabilità di combustione 0–1':'Blu · profondità massima 0–'+Number(s.maximum).toLocaleString('it-IT',{maximumFractionDigits:3})+' m';
   info.textContent=(enabled?'Visibile':'Nascosto')+' · '+legend+'\n'+date(s.valid_from)+' → '+date(s.valid_until)+'\n'+(kind==='FIRE'?'PROPAGATOR':'HMC + REFlEx')+' · '+s.positive_cells+' celle positive · non calibrato';
   if(!enabled)continue;const opacity=Number($('monitor-opacity').value)/100,pane=kind==='FIRE'?'monitorFire':'monitorFlood';
   if(s.overlay)L.imageOverlay(s.overlay,s.bounds,{opacity,pane}).addTo(products[kind]);
   else L.geoJSON(s.cells,{pane,style:()=>({color:'#d14a11',weight:.6,fillColor:'#ed4d13',fillOpacity:opacity}),onEachFeature:(f,l)=>l.bindPopup(escape(names[kind])+' · simulato<br>Probabilità '+escape(f.properties.probability)+'<br>Primo arrivo '+escape(f.properties.arrival_s)+' s<br>Job '+escape(s.id))}).addTo(products[kind]);
  }
  const active=shown();$('monitor-summary').textContent=active.length?active.length+' pericol'+(active.length===1?'o visibile':'i visibili')+' · risultati simulati, nessuna allerta operativa.':'Nessun pericolo visibile. Attiva Incendi o Alluvioni; lo sfondo resta consultabile.';
  // Small, bounded inspectable state for QA; no geographic/physics computation on client.
  $('monitor-map').dataset.hazards=active.map(s=>s.hazard).join(',');$('monitor-map').dataset.products=active.map(s=>s.id).join(',');
 }
 function fit(){const active=shown();if(!active.length)return;map.fitBounds(active.reduce((b,s)=>b.extend(s.bounds),L.latLngBounds(active[0].bounds)),{padding:[35,35],maxZoom:16,animate:false});}
 function update(next){catalog=next;for(const kind of ['FIRE','FLOOD']){const select=$('monitor-'+kind.toLowerCase()+'-case'),old=select.value,list=catalog.scenarios.filter(s=>s.hazard===kind);select.innerHTML=list.map((s,i)=>'<option value="'+escape(s.id)+'">Caso '+(i+1)+' · '+escape(date(s.valid_from))+' · '+(kind==='FIRE'?Math.round(s.options.duration_s/60)+' min':'max6h')+'</option>').join('');if(list.some(s=>s.id===old))select.value=old;}draw();}
 for(const id of ['monitor-fire','monitor-flood','monitor-fire-case','monitor-flood-case'])$(id).onchange=()=>{const t=performance.now();draw();feedback(t,'monitor-filter');};
 $('monitor-all').onclick=()=>{const t=performance.now();$('monitor-fire').checked=true;$('monitor-flood').checked=true;draw();feedback(t,'monitor-filter');};
 $('monitor-opacity').oninput=()=>{const t=performance.now();$('monitor-opacity-value').textContent=$('monitor-opacity').value+'%';const opacity=Number($('monitor-opacity').value)/100;Object.values(products).forEach(g=>g.eachLayer(l=>{if(l.setOpacity)l.setOpacity(opacity);else if(l.setStyle)l.setStyle({fillOpacity:opacity});}));feedback(t,'monitor-opacity');};
 $('monitor-fit').onclick=fit;
 $('monitor-basemap').onchange=()=>{const t=performance.now();if($('monitor-basemap').value==='ortho'&&visible)ortho.addTo(map);else ortho.remove();source();feedback(t,'monitor-basemap');};
 function renderLabels(){labels.clearLayers();roads.clearLayers();if(!$('monitor-labels').checked||!visible)return;const bounds=map.getBounds(),z=map.getZoom(),occupied=[];let roadCount=0;
  for(const f of context){if(f.kind==='place'&&bounds.contains([f.lat,f.lon])&&(z>=13||['city','town','capoluogo amministrativo'].includes(f.type))&&occupied.length<80){const px=map.latLngToContainerPoint([f.lat,f.lon]);if(occupied.some(p=>Math.abs(px.x-p.x)<100&&Math.abs(px.y-p.y)<24))continue;occupied.push(px);L.marker([f.lat,f.lon],{pane:'monitorNames',interactive:false,keyboard:false,icon:L.divIcon({className:'geo-label place',html:escape(f.name),iconSize:[140,22],iconAnchor:[70,11]})}).addTo(labels);}
   if(z>=14&&f.kind==='road'&&roadCount<150&&f.geometry.some(p=>bounds.contains([p[1],p[0]]))){roadCount++;L.polyline(f.geometry.map(p=>[p[1],p[0]]),{color:'#fff',weight:2,opacity:.65,interactive:false}).addTo(roads);}}
 }
 $('monitor-labels').onchange=renderLabels;map.on('moveend',()=>{clearTimeout(labelsTimer);labelsTimer=setTimeout(renderLabels,100)});
 function inspect(latlng){selected=latlng;point.clearLayers();L.circleMarker(latlng,{radius:6,color:'#fff',weight:2,fillColor:'#3d375f',fillOpacity:1}).addTo(point);$('monitor-coordinates').textContent=latlng.lat.toFixed(6)+', '+latlng.lng.toFixed(6)+' · WGS84';const nearby=context.filter(f=>f.kind==='place'||f.kind==='poi').map(f=>({...f,distance:latlng.distanceTo([f.lat,f.lon])})).sort((a,b)=>a.distance-b.distance).slice(0,3);$('monitor-point').textContent=latlng.lat.toFixed(6)+', '+latlng.lng.toFixed(6)+' · WGS84. '+nearby.map(f=>f.name+' a '+Math.round(f.distance)+' m').join('; ')+'. Riferimenti vicini, non appartenenza amministrativa. Copertura locale incompleta.';document.querySelector('.monitor-inspector').open=true;}
 map.on('click',e=>inspect(e.latlng));
 $('monitor-search').onsubmit=e=>{e.preventDefault();const q=$('monitor-query').value.trim(),match=q.match(/^(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)$/);let p;if(match)p=[Number(match[1]),Number(match[2])];else{const key=q.toLocaleLowerCase('it').replace(/[’']/g,''),f=context.find(f=>f.kind!=='road'&&f.name.toLocaleLowerCase('it').replace(/[’']/g,'')===key);if(f)p=[f.lat,f.lon];}
  if(!p||p[0]<41.60||p[0]>42.97||p[1]<12.90||p[1]>14.86){$('monitor-search-status').textContent='Luogo non trovato nella copertura disponibile. Inserisci coordinate in Abruzzo.';return;}map.setView(p,16,{animate:false});inspect(L.latLng(p));$('monitor-search-status').textContent='Posizione trovata · riferimenti di contesto disponibili.';};
 fetch('/assets/map-context.json').then(r=>{if(!r.ok)throw Error();return r.json()}).then(v=>{context=v.features;const places=[...new Set(context.filter(f=>f.kind==='place').map(f=>f.name))];$('monitor-places').innerHTML=places.map(n=>'<option value="'+escape(n)+'"></option>').join('');renderLabels();}).catch(()=>{$('monitor-search-status').textContent='Nomi geografici non disponibili. Ricerca per coordinate attiva.';});
 update(initial);fit();
 return {update,visible(on){visible=on;if(!on)ortho.remove();else if($('monitor-basemap').value==='ortho')ortho.addTo(map);requestAnimationFrame(()=>{map.invalidateSize({pan:false});if(on)renderLabels();});}};
}
