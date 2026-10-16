/* Geographic context is separate from simulator products; all snapshot data served by VM. */
const $=id=>document.getElementById(id);
const safe=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export async function geographicMaps(maps,feedback){
 let context={features:[],places_bbox:[13.375,42.345,13.405,42.36],roads_bbox:[13.375,42.345,13.405,42.36]},active='ortho',selected=null;
 const imagery=[],names=[],markers=[],contextGroups=[];let failures=0,labelsTimer;
 try{const r=await fetch('/assets/map-context.json');if(!r.ok)throw Error('Snapshot non disponibile');context=await r.json();$('context-source').textContent=`© OpenStreetMap contributors · ODbL 1.0 · snapshot ${context.timestamp.slice(0,10)} · ${context.features.length} elementi con GeoNames (CC BY 4.0). Località Abruzzo, strade/POI nel centro dell’Aquila; copertura incompleta; nessun indirizzo o confine viene dedotto.`;}catch(e){$('context-source').textContent='Contesto cartografico non disponibile: coordinate e sfondi restano utilizzabili.';}
 const places=context.features.filter(f=>f.kind==='place'),roads=context.features.filter(f=>f.kind==='road'),pois=context.features.filter(f=>f.kind==='poi');
 const searchable=[...new Map(context.features.map(f=>[f.name,f])).values()].sort((a,b)=>a.name.localeCompare(b.name,'it'));
 $('map-place-list').innerHTML=searchable.map(f=>`<option value="${safe(f.name)}"></option>`).join('');
 function sourceText(){return active==='ortho'?`Ortofoto aeree Regione Abruzzo · 2018–2019 · 20 cm/px dichiarati · consultazione online${imagery.some(l=>l.isLoading())?' · Caricamento dettaglio…':''}${failures?' · Alcune tessere non disponibili: riprova o scegli Sentinel offline.':''}`:'Sentinel-2 · 13/07/2024 · pixel nativo 10 m · ritaglio locale offline';}
 function status(){ $('map-source').textContent=sourceText();$('map-source').classList.toggle('error',active==='ortho'&&failures>0);$('map-position').textContent=`Centro ${maps[0].getCenter().lat.toFixed(6)}, ${maps[0].getCenter().lng.toFixed(6)} · WGS84 · zoom ${maps[0].getZoom()} · N ↑`; }
 function renderNames(){
  maps.forEach((m,i)=>{names[i].clearLayers();contextGroups[i].clearLayers();if(!$('map-labels').checked)return;const bounds=m.getBounds().pad(.1),z=m.getZoom(),occupied=[];
   const label=(f,point,kind)=>{if(!bounds.contains(point))return;const px=m.latLngToContainerPoint(point);if(occupied.some(p=>Math.abs(p.x-px.x)<100&&Math.abs(p.y-px.y)<24))return;occupied.push(px);L.marker(point,{pane:'geographicNames',keyboard:false,interactive:false,icon:L.divIcon({className:'geo-label '+kind,html:safe(f.name),iconSize:[140,22],iconAnchor:[70,11]})}).addTo(names[i]);};
   places.filter(f=>bounds.contains([f.lat,f.lon])&&(z>=13||['city','town','capoluogo amministrativo'].includes(f.type))).slice(0,120).forEach(f=>label(f,[f.lat,f.lon],'place'));
   if(z>=14){let count=0;for(const f of roads){if(count>=200)break;if(!f.geometry.some(p=>bounds.contains([p[1],p[0]])))continue;count++;L.polyline(f.geometry.map(p=>[p[1],p[0]]),{pane:'geographicRoads',color:'#fff',weight:2.6,opacity:.72,interactive:false}).addTo(contextGroups[i]);L.polyline(f.geometry.map(p=>[p[1],p[0]]),{pane:'geographicRoads',color:'#576772',weight:1,opacity:.85,interactive:false}).addTo(contextGroups[i]);if(z>=16&&count<=55){const p=f.geometry[Math.floor(f.geometry.length/2)];label(f,[p[1],p[0]],'road');}}}
   if(z>=17)pois.filter(f=>bounds.contains([f.lat,f.lon])).slice(0,40).forEach(f=>label(f,[f.lat,f.lon],'poi'));
  });
 }
 maps.forEach((m,i)=>{
  m.setMaxZoom(20);m.setMinZoom(8);m.setMaxBounds([[41.60,12.90],[42.97,14.86]]);
  m.createPane('geographicRoads');m.getPane('geographicRoads').style.zIndex=390;m.getPane('geographicRoads').style.pointerEvents='none';
  m.createPane('geographicNames');m.getPane('geographicNames').style.zIndex=610;m.getPane('geographicNames').style.pointerEvents='none';
  names[i]=L.layerGroup().addTo(m);contextGroups[i]=L.layerGroup().addTo(m);
  // Renderer pane keeps roads below model layers; labels remain legible above them.
  contextGroups[i].on('layeradd',e=>{if(e.layer.options)e.layer.options.pane='geographicRoads';});
  names[i].on('layeradd',e=>{if(e.layer.options)e.layer.options.pane='geographicNames';});
  imagery[i]=L.tileLayer('/api/maps/ortho/{z}/{x}/{y}',{minZoom:8,maxZoom:20,maxNativeZoom:19,tileSize:256,keepBuffer:1,updateWhenIdle:true,updateWhenZooming:false,zIndex:2,bounds:[[41.6607,12.9714],[42.9053,14.7922]],attribution:'Ortofoto 2018–2019 © Regione Abruzzo · <a href="https://geoportale.regione.abruzzo.it/Cartanet/catalogo/cartografia-di-sfondo-raster/copy_of_ortofoto-regione-abruzzo-2007-a-colori-1">20 cm/px</a>'});
  imagery[i].on('loading',status);imagery[i].on('tileerror',()=>{failures++;status()});imagery[i].on('load',status).addTo(m);
  m.attributionControl.addAttribution('<a href="https://www.geonames.org/">GeoNames · CC BY 4.0</a> · © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · ODbL');
  L.control.scale({imperial:false,maxWidth:110}).addTo(m);
  m.on('movestart',()=>{failures=0});m.on('moveend',()=>{status();clearTimeout(labelsTimer);labelsTimer=setTimeout(renderNames,80)});
  m.on('mousemove',e=>{$('map-cursor').textContent=`Puntatore ${e.latlng.lat.toFixed(6)}, ${e.latlng.lng.toFixed(6)} · WGS84`;});
  m.on('click',e=>inspect(e.latlng));
 });
 const distance=(lat,lon,f)=>{const dy=(f.lat-lat)*111195,dx=(f.lon-lon)*111195*Math.cos(lat*Math.PI/180);return Math.hypot(dx,dy)};
 function roadDistance(lat,lon,f){let best=Infinity;const sx=111195*Math.cos(lat*Math.PI/180),sy=111195;for(let j=1;j<f.geometry.length;j++){const a=f.geometry[j-1],b=f.geometry[j],ax=(a[0]-lon)*sx,ay=(a[1]-lat)*sy,dx=(b[0]-a[0])*sx,dy=(b[1]-a[1])*sy,t=Math.max(0,Math.min(1,-(ax*dx+ay*dy)/(dx*dx+dy*dy||1)));best=Math.min(best,Math.hypot(ax+t*dx,ay+t*dy));}return best;}
 const nearest=(items,lat,lon,fn)=>items.map(f=>({f,d:fn(lat,lon,f)})).sort((a,b)=>a.d-b.d)[0];
 const covered=(bbox,p)=>p.lng>=bbox[0]&&p.lng<=bbox[2]&&p.lat>=bbox[1]&&p.lat<=bbox[3];
 function entry(title,item){return item?`<div><dt>${title}</dt><dd><strong>${safe(item.f.name)}</strong> · circa ${Math.round(item.d)} m<br><small>${safe(item.f.type||'')} · <a href="${item.f.provider==='GeoNames'?'https://www.geonames.org/'+item.f.id:'https://www.openstreetmap.org/'+item.f.osm_type+'/'+item.f.id}" target="_blank" rel="noreferrer">${safe(item.f.provider||'OpenStreetMap')} ${item.f.id}</a>${item.f.address?' · '+safe(item.f.address):''}</small></dd></div>`:`<div><dt>${title}</dt><dd>Non disponibile nello snapshot locale</dd></div>`;}
 function inspect(p){
  const t=performance.now();selected=p;markers.forEach(v=>v.remove());markers.length=0;maps.forEach(m=>markers.push(L.circleMarker(p,{radius:9,color:'#fff',weight:3,fillColor:'#0c5553',fillOpacity:1}).addTo(m)));
  $('point-title').textContent='Punto selezionato';$('point-details').innerHTML=`<div><dt>Coordinate WGS84 · EPSG:4326</dt><dd>${p.lat.toFixed(6)}° N, ${p.lng.toFixed(6)}° E</dd></div>`+entry('Località più vicina · non confine amministrativo',covered(context.places_bbox,p)?nearest(places,p.lat,p.lng,distance):null)+entry('Quartiere o frazione più vicini · riferimento puntuale',covered(context.roads_bbox,p)?nearest(places.filter(f=>f.provider==='OpenStreetMap'&&['quarter','suburb','neighbourhood','hamlet','village'].includes(f.type)),p.lat,p.lng,distance):null)+entry('Strada nominata più vicina',covered(context.roads_bbox,p)?nearest(roads,p.lat,p.lng,roadDistance):null)+entry('Punto di interesse più vicino',covered(context.roads_bbox,p)?nearest(pois,p.lat,p.lng,distance):null);
  $('point-hint').textContent='Distanze planimetriche approssimate sui punti GeoNames e sullo snapshot OSM; non indicano accessibilità o appartenenza amministrativa. Indirizzi presenti solo quando dichiarati dalla fonte. Quota, particelle catastali e confini ufficiali non disponibili.';feedback(t,'map-inspect');
 }
 $('basemap').onchange=()=>{const t=performance.now();active=$('basemap').value;failures=0;imagery.forEach((l,i)=>active==='ortho'?l.addTo(maps[i]):l.remove());status();feedback(t,'map-basemap')};
 $('map-retry').onclick=()=>{failures=0;if(active==='ortho')imagery.forEach(l=>l.redraw());status()};
 $('map-labels').onchange=()=>{const t=performance.now();renderNames();feedback(t,'map-labels')};
 $('map-search').onsubmit=e=>{e.preventDefault();const t=performance.now(),q=$('map-query').value.trim(),f=searchable.find(f=>f.name.toLocaleLowerCase('it')===q.toLocaleLowerCase('it'));const c=q.match(/^(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)$/);let p=f?L.latLng(f.lat,f.lon):c?L.latLng(Number(c[1]),Number(c[2])):null;
  if(!p||p.lat<41.60||p.lat>42.97||p.lng<12.90||p.lng>14.86){$('map-search-message').textContent='Scegli un nome dello snapshot oppure latitudine, longitudine in Abruzzo.';return;}
  maps.forEach(m=>m.setView(p,18,{animate:false}));inspect(p);$('map-search-message').textContent=f?`${f.name} · ${f.type} · fonte ${f.provider||'OpenStreetMap'}`:'Coordinate inserite manualmente';feedback(t,'map-search');};
 $('map-expand').onclick=()=>{const t=performance.now(),expanded=$('map-pair').classList.toggle('expanded');$('map-expand').setAttribute('aria-pressed',String(expanded));$('map-expand').textContent=expanded?'Affianca mappe':'Mappe più grandi';requestAnimationFrame(()=>maps.forEach(m=>m.invalidateSize({pan:false})));feedback(t,'map-expand');};
 status();renderNames();
}
