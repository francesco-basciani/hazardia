import {scheduledTiles} from '/scheduled-tiles.js';
import {monitorWorkbench} from '/monitor-workbench.js';
import {basemapController} from '/basemap-controller.js';
import {mapSymbols} from '/map-symbols.js?v=1';
import {rainZones} from '/rain-zones.js?v=1';
import {territorialLayers} from '/territorial-layers.js';
import {territorialAttention} from '/attention.js?v=1';
import {resilientTiles} from '/tile-retry.js?v=1';
import {regionBoundaries} from '/region-boundaries.js?v=workspace1';
import {eventMarkers,scenarioReference} from '/event-markers.js?v=1';
import {regionalWind} from '/wind-particles.js?v=workspace1';
/* Read-only hazard overview: one chosen product per hazard, never a fused forecast. */
const $=id=>document.getElementById(id);
const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names={FIRE:'Incendio',FLOOD:'Alluvione'};
function date(v){return new Date(v).toLocaleString('it-IT',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'})+' · Roma';}
export function monitoringMap(initial,feedback){
 let catalog=initial,context=[],selected=null,failures=0,visible=true,labelsTimer,weatherRecord=null,weatherForecast=null,workbenchUI=null;
 const map=L.map('monitor-map',{preferCanvas:true,scrollWheelZoom:false,keyboard:true,worldCopyJump:false}).setView([42.35,13.38],8);
 const territoryHost=document.createElement('div');map.getContainer().parentElement.append(territoryHost);const territory=territorialLayers({api:async(path,body)=>{const r=await fetch(path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json','X-Hazardia-Research':'1'}:{},body:body?JSON.stringify(body):undefined});const v=await r.json();if(!r.ok)throw Error(v.detail);return v;},host:territoryHost,monitor:true});territory.add(map);
 window.addEventListener('hazardia-map-resize',()=>map.invalidateSize({pan:false}));
 map.getContainer().dataset.zoom=String(map.getZoom());map.getContainer().dataset.center=JSON.stringify([map.getCenter().lat,map.getCenter().lng]);map.on('moveend zoomend',()=>{map.getContainer().dataset.zoom=String(map.getZoom());map.getContainer().dataset.center=JSON.stringify([map.getCenter().lat,map.getCenter().lng]);});
 map.setMinZoom(2);map.setMaxZoom(20);map.setMaxBounds([[-85,-180],[85,180]]);map.options.maxBoundsViscosity=1;const worldZoom=()=>map.setMinZoom(Math.max(2,Math.ceil(Math.log2(Math.max(256,map.getSize().x)/256))));worldZoom();map.on('resize',worldZoom);map.attributionControl.setPrefix('HAZARDIA · Ricerca');
 map.createPane('monitorSatellite');map.getPane('monitorSatellite').style.zIndex=190;
 const satellite=L.imageOverlay('/assets/satellite.png',[[42.30,13.32],[42.40,13.44]],{opacity:1,pane:'monitorSatellite',attribution:'Contains modified Copernicus Sentinel data2024'});
 // Keep flood below fire independent of filter/case toggle order.
 for(const [name,z] of [['monitorFlood',410],['monitorFire',420],['monitorNames',610]]){map.createPane(name);map.getPane(name).style.zIndex=z;}
 const ortho=scheduledTiles('/api/maps/ortho/{z}/{x}/{y}',{minZoom:12,maxZoom:20,maxNativeZoom:19,keepBuffer:1,updateWhenIdle:true,updateWhenZooming:false,bounds:[[41.6607,12.9714],[42.9053,14.7922]],attribution:'Ortofoto Regione Abruzzo 2018–2019 · 20 cm/px dichiarati'});
 const regional=scheduledTiles('/api/maps/regional/{z}/{x}/{y}',{minZoom:2,maxZoom:20,maxNativeZoom:14,keepBuffer:0,updateWhenIdle:true,updateWhenZooming:false,bounds:[[-85,-180],[85,180]],attribution:'<a href="https://s2maps.eu">Sentinel-2 cloudless</a> by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2024) · CC BY-NC-SA4.0'});
 const osm=scheduledTiles('/api/maps/osm/{z}/{x}/{y}?v=2',{minZoom:2,maxZoom:20,maxNativeZoom:19,keepBuffer:0,updateWhenIdle:true,updateWhenZooming:false,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · ODbL'});let osmErrors=0;
 regionBoundaries(map);
 const wind=regionalWind(map);
 const attention=territorialAttention(map);
 const rain=rainZones(map);
 const references=eventMarkers(map);
 const weatherLayer=L.layerGroup().addTo(map);
 const labels=L.layerGroup().addTo(map),roads=L.layerGroup().addTo(map),point=L.layerGroup().addTo(map),products={FIRE:L.layerGroup().addTo(map),FLOOD:L.layerGroup().addTo(map)};
 L.control.scale({imperial:false,maxWidth:120}).addTo(map);
 map.attributionControl.addAttribution('© OpenStreetMap contributors · ODbL · GeoNames CC BY4.0 · <a href="https://open-meteo.com/">Open-Meteo</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY4.0</a>');
 let backgroundState={mode:'ortho',reason:'',errors:0};
 const backgroundWarning=document.createElement('p');backgroundWarning.className='monitor-background-warning';backgroundWarning.setAttribute('role','status');backgroundWarning.hidden=true;document.querySelector('.monitor-map-toolbar').after(backgroundWarning);
 function source(){const mode=$('monitor-basemap').value;const outside=mode==='sentinel'&&!satellite.getBounds().contains(map.getBounds());backgroundWarning.hidden=!backgroundState.reason&&!outside&&!backgroundState.loading;backgroundWarning.textContent=(backgroundState.reason||'')+(outside?' Il ritaglio Sentinel offline non copre tutta la vista. Scegli uno sfondo online.':backgroundState.loading?' Caricamento dello sfondo…':'');$('monitor-source').textContent=mode==='osm'?'OpenStreetMap · ODbL · cache secondo gli header della fonte, almeno7giorni se non dichiarati · consultazione nella VM':mode==='ortho'?'EOX Sentinel-2 cloudless2024 · CC BY-NC-SA4.0 · ortofoto Regione Abruzzo2018–2019 dove disponibili. Non sono immagini in tempo reale.':'Sentinel-2 ·13/07/2024 ·10m · ritaglio locale';}
 const backgrounds=basemapController(map,{select:$('monitor-basemap'),satellite,regional,ortho,osm,onChange:()=>{source();renderLabels();},onStatus:state=>{backgroundState=state;source();}});
 map.on('zoomend',source);
 function chosen(kind){return catalog.scenarios.find(s=>s.hazard===kind&&s.id===$('monitor-'+kind.toLowerCase()+'-case').value);}
 function shown(){return ['FIRE','FLOOD'].filter(k=>$('monitor-'+k.toLowerCase()).checked).map(chosen).filter(Boolean);}
 function draw(){
  for(const kind of ['FIRE','FLOOD']){const key=kind.toLowerCase(),s=chosen(kind),enabled=$('monitor-'+key).checked;products[kind].clearLayers();$('monitor-'+key+'-case').disabled=!enabled||!s;const info=$('monitor-'+key+'-info');
   if(!s){info.textContent='Nessun risultato disponibile nel catalogo.';continue;}
   const legend=kind==='FIRE'?'Arancio · probabilità di combustione 0–1':(s.maximum===0?'Nessun allagamento mappato dal modello; non è una garanzia di sicurezza':'Blu · profondità massima 0–'+Number(s.maximum).toLocaleString('it-IT',{maximumFractionDigits:3})+' m');
   info.textContent=(enabled?'Visibile':'Nascosto')+' · '+legend+'\n'+date(s.valid_from)+' → '+date(s.valid_until)+'\n'+(kind==='FIRE'?'PROPAGATOR':'HMC + REFlEx')+' · '+(s.mode==='RESEARCH_FORECAST'?'METEO REALE · ':'STORICO · ')+s.positive_cells+' celle positive · non calibrato';
   if(!enabled||!$('monitor-simulated').checked)continue;const opacity=Number($('monitor-opacity').value)/100,pane=kind==='FIRE'?'monitorFire':'monitorFlood';
   if(s.overlay)L.imageOverlay(s.overlay,s.bounds,{opacity,pane}).addTo(products[kind]);
   else L.geoJSON(s.cells,{pane,style:()=>({color:'#d14a11',weight:.6,fillColor:'#ed4d13',fillOpacity:opacity}),onEachFeature:(f,l)=>l.bindPopup(escape(names[kind])+' · simulato<br>Probabilità '+escape(f.properties.probability)+'<br>Primo arrivo '+escape(f.properties.arrival_s)+' s<br>Job '+escape(s.id)).on('click',e=>inspect(e.latlng))}).addTo(products[kind]);
  }
  const active=shown();references.update($('monitor-simulated').checked?active.map(scenarioReference):[]);mapSymbols(map).set('simulation-products',$('monitor-simulated').checked?active.map(s=>({label:(s.hazard==='FIRE'?'Incendio':'Alluvione')+' · risultato simulato',kind:'area',color:s.hazard==='FIRE'?'#ed4d13':'#267ab7',note:'Prodotto congelato '+date(s.valid_from)+' → '+date(s.valid_until)+'. Stato finale del proprio orizzonte, indipendente dalla timeline meteo di Monitoraggio. Non è un evento osservato o una previsione aggiornata. Per il replay temporale usa Simulazioni e risorse.'})):[]);$('monitor-summary').textContent=active.length?active.length+' pericol'+(active.length===1?'o visibile':'i visibili')+' · risultati simulati, nessuna allerta operativa.':'Nessun pericolo visibile. Attiva Incendi o Alluvioni; lo sfondo resta consultabile.';
  if(!$('monitor-simulated').checked)$('monitor-summary').textContent='Scenari di ricerca nascosti. I livelli di attenzione territoriale hanno fonti e date proprie.';
  // Small, bounded inspectable state for QA; no geographic/physics computation on client.
  $('monitor-map').dataset.hazards=active.map(s=>s.hazard).join(',');$('monitor-map').dataset.products=active.map(s=>s.id).join(',');
 }
 function weather(forecast,record){weatherForecast=forecast;weatherRecord=record;weatherLayer.clearLayers();wind.toggle();$('weather-map-legend').hidden=true;/* Distributed map weather owns its timeline. Point forcing remains in its own builder. */}
 for(const id of ['monitor-weather','weather-layer-wind','weather-layer-temperature','weather-layer-rain'])$(id).onchange=()=>weather(weatherForecast,weatherRecord);
 $('weather-center').onclick=()=>{if(weatherForecast)map.setView([weatherForecast.model_point.latitude,weatherForecast.model_point.longitude],14,{animate:false});};
 function fit(){const active=shown();if(!active.length)return;map.fitBounds(active.reduce((b,s)=>b.extend(s.bounds),L.latLngBounds(active[0].bounds)),{padding:[35,35],maxZoom:16,animate:false});}
 function update(next){catalog=next;for(const kind of ['FIRE','FLOOD']){const select=$('monitor-'+kind.toLowerCase()+'-case'),old=select.value,list=catalog.scenarios.filter(s=>s.hazard===kind);select.innerHTML=list.map((s,i)=>'<option value="'+escape(s.id)+'">Caso '+(i+1)+' · '+escape(date(s.valid_from))+' · '+(kind==='FIRE'?Math.round(s.options.duration_s/60)+' min':'max6h')+'</option>').join('');if(list.some(s=>s.id===old))select.value=old;}draw();}
 for(const id of ['monitor-fire','monitor-flood','monitor-fire-case','monitor-flood-case'])$(id).onchange=()=>{const t=performance.now();draw();feedback(t,'monitor-filter');};
 $('monitor-all').onclick=()=>{const t=performance.now();$('monitor-fire').checked=true;$('monitor-flood').checked=true;draw();feedback(t,'monitor-filter');};
 $('monitor-opacity').oninput=()=>{const t=performance.now();$('monitor-opacity-value').textContent=$('monitor-opacity').value+'%';const opacity=Number($('monitor-opacity').value)/100;Object.values(products).forEach(g=>g.eachLayer(l=>{if(l.setOpacity)l.setOpacity(opacity);else if(l.setStyle)l.setStyle({fillOpacity:opacity});}));feedback(t,'monitor-opacity');};
 $('monitor-fit').onclick=fit;
 function applyBasemap(manual=false){return backgrounds.apply(manual);}
 $('monitor-basemap').onchange=()=>{const t=performance.now();applyBasemap(true);feedback(t,'monitor-basemap');};
 function renderLabels(){labels.clearLayers();roads.clearLayers();if(!$('monitor-labels').checked||!visible||$('monitor-basemap').value==='osm'){mapSymbols(map).set('place-labels',[]);return;}const bounds=map.getBounds(),z=map.getZoom(),occupied=[];let roadCount=0;
  for(const f of context){if(f.kind==='place'&&bounds.contains([f.lat,f.lon])&&(z>=13||['city','town','capoluogo amministrativo'].includes(f.type))&&occupied.length<80){const px=map.latLngToContainerPoint([f.lat,f.lon]);if(occupied.some(p=>Math.abs(px.x-p.x)<100&&Math.abs(px.y-p.y)<24))continue;occupied.push(px);L.marker([f.lat,f.lon],{pane:'monitorNames',interactive:false,keyboard:false,icon:L.divIcon({className:'geo-label place',html:escape(f.name),iconSize:[140,22],iconAnchor:[70,11]})}).addTo(labels);}
   if(z>=14&&f.kind==='road'&&roadCount<150&&f.geometry.some(p=>bounds.contains([p[1],p[0]]))){roadCount++;L.polyline(f.geometry.map(p=>[p[1],p[0]]),{color:'#fff',weight:2,opacity:.65,interactive:false}).addTo(roads);}}
  mapSymbols(map).set('place-labels',occupied.length?[{label:'Nome di località',kind:'point',priority:3,color:'#fff',fill:'#19334c',fillOpacity:1,note:'Punto scuro e nome geografico: non è un evento o un valore meteorologico.'}]:[]);
  map.fire('contextnames');
 }
 $('monitor-labels').onchange=renderLabels;map.on('moveend',()=>{clearTimeout(labelsTimer);labelsTimer=setTimeout(renderLabels,100)});
 function inspect(latlng){selected=latlng;point.clearLayers();L.circleMarker(latlng,{radius:6,color:'#fff',weight:2,fillColor:'#3d375f',fillOpacity:1}).addTo(point);$('monitor-coordinates').textContent=latlng.lat.toFixed(6)+', '+latlng.lng.toFixed(6)+' · WGS84';const nearby=context.filter(f=>f.kind==='place'||f.kind==='poi').map(f=>({...f,distance:latlng.distanceTo([f.lat,f.lon])})).filter(f=>f.distance<30000).sort((a,b)=>a.distance-b.distance).slice(0,3);$('monitor-point').textContent=latlng.lat.toFixed(6)+', '+latlng.lng.toFixed(6)+' · WGS84. '+(nearby.length?nearby.map(f=>f.name+' a '+Math.round(f.distance)+' m').join('; '):'Inventario locale non disponibile nella vista; i nomi dello sfondo hanno una fonte indipendente')+'. Riferimenti vicini, non appartenenza amministrativa. Copertura locale incompleta. '+wind.at(latlng);document.querySelector('.monitor-inspector').open=true;}
 map.on('click',e=>inspect(e.latlng));
 let searchGeneration=0,searchAbort=null;
 const searchResults=document.createElement('div');searchResults.className='map-search-results';searchResults.setAttribute('aria-label','Risultati ricerca geografica');$('monitor-search').append(searchResults);
 function locate(p,name){map.setView(p,12,{animate:true});inspect(L.latLng(p));$('monitor-search-status').textContent=name+' · coordinate WGS84. Copertura dei livelli indipendente dalla cartografia.';searchResults.replaceChildren();}
 $('monitor-search').onsubmit=async e=>{e.preventDefault();const token=++searchGeneration;searchAbort?.abort();searchAbort=new AbortController();searchResults.replaceChildren();const q=$('monitor-query').value.trim(),match=q.match(/^(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)$/);
  if(match){const p=[Number(match[1]),Number(match[2])];if(p[0]<-85||p[0]>85||p[1]<-180||p[1]>180){$('monitor-search-status').textContent='Coordinate fuori intervallo: latitudine±85°, longitudine±180°.';return;}locate(p,q);return;}
  const key=q.toLocaleLowerCase('it').replace(/[’']/g,''),local=context.find(f=>f.kind!=='road'&&f.name.toLocaleLowerCase('it').replace(/[’']/g,'')===key);
  if(local){locate([local.lat,local.lon],local.name);return;}
  $('monitor-search-status').textContent='Ricerca località…';try{const response=await fetch('/api/maps/search?q='+encodeURIComponent(q),{signal:searchAbort.signal});const result=await response.json();if(token!==searchGeneration)return;if(!response.ok)throw Error(result.detail||'Ricerca non disponibile');if(!result.places.length){$('monitor-search-status').textContent='Nessuna località trovata. Puoi inserire coordinate.';return;}$('monitor-search-status').textContent='Scegli una località · '+result.source;for(const p of result.places){const b=document.createElement('button');b.type='button';b.textContent=[p.name,p.region,p.country].filter(Boolean).join(' · ');b.onclick=()=>locate([p.latitude,p.longitude],b.textContent);searchResults.append(b);}}catch(error){if(error.name!=='AbortError'&&token===searchGeneration)$('monitor-search-status').textContent=error.message;}
 };
 const navigation=L.control({position:'topleft'});navigation.onAdd=()=>{const host=L.DomUtil.create('div','map-navigation');for(const [label,action] of [['Area di studio',()=>{if(shown().length)fit();else map.setView([42.35,13.38],8);}],['Vista iniziale',()=>map.setView([42.35,13.38],8)]]){const b=document.createElement('button');b.type='button';b.textContent=label;b.onclick=action;host.append(b);}L.DomEvent.disableClickPropagation(host);return host;};navigation.addTo(map);
 fetch('/assets/map-context.json').then(r=>{if(!r.ok)throw Error();return r.json()}).then(v=>{context=v.features;const places=[...new Set(context.filter(f=>f.kind==='place').map(f=>f.name))];$('monitor-places').innerHTML=places.map(n=>'<option value="'+escape(n)+'"></option>').join('');renderLabels();}).catch(()=>{$('monitor-search-status').textContent='Nomi geografici non disponibili. Ricerca per coordinate attiva.';});
 $('monitor-simulated').addEventListener('change',draw);
 update(initial);applyBasemap();
 return {update,weather,decorate(){workbenchUI=monitorWorkbench(map);map.invalidateSize({pan:false});},visible(on){visible=on;workbenchUI?.visible(on);attention.visible(on);rain.visible(on);wind.visible(on);backgrounds.visible(on);requestAnimationFrame(()=>{map.invalidateSize({pan:false});if(on)renderLabels();});}};
}
