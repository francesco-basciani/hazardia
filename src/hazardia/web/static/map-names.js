// Cached geographic names have a finite footprint, never invent names outside it.
let source;
export function mapNames(map,{input=document.getElementById('config-names'),status=document.getElementById('cartography-status')}={}){
 const pane='placeNames';map.createPane(pane);map.getPane(pane).style.zIndex=610;map.getPane(pane).style.pointerEvents='none';const group=L.layerGroup().addTo(map);let data=null,disposed=false;
 function draw(){if(disposed)return;group.clearLayers();if(!data||input&&!input.checked)return;const b=map.getBounds(),z=map.getZoom(),used=[];
  const places=data.features.filter(f=>f.kind==='place'&&b.contains([f.lat,f.lon])&&(z>=12||['city','town','capoluogo amministrativo'].includes(f.type))).sort((a,b)=>Number(!['city','town'].includes(a.type))-Number(!['city','town'].includes(b.type)));
  for(const f of places){const p=map.latLngToContainerPoint([f.lat,f.lon]),size=map.getSize();if(p.x<45||p.x>size.x-45||p.y<18||p.y>size.y-22||used.some(q=>Math.abs(q.x-p.x)<115&&Math.abs(q.y-p.y)<30))continue;used.push(p);const span=document.createElement('span');span.textContent=f.name;L.marker([f.lat,f.lon],{pane,interactive:false,keyboard:false,icon:L.divIcon({className:'map-place-name',html:span,iconSize:[160,22],iconAnchor:[80,11]})}).addTo(group);if(used.length>=50)break;}
  map.getContainer().dataset.placeNames=String(used.length);map.fire('contextnames');if(status)status.textContent='Confini Istat Italia 2026, generalizzati. Nomi GeoNames/OSM: copertura locale incompleta'+(used.length?' · '+used.length+' nomi in vista.':', nessun nome disponibile in vista.');
 }
 if(!source)source=fetch('/assets/map-context.json').then(r=>{if(!r.ok)throw Error();return r.json();});source.then(d=>{if(disposed)return;data=d;map.attributionControl.addAttribution('GeoNames CC BY4.0 · © OpenStreetMap contributors ODbL');draw();}).catch(()=>{if(status)status.textContent='Nomi geografici non disponibili';});map.on('moveend zoomend',draw);input?.addEventListener('change',draw);
 return {remove(){disposed=true;map.off('moveend zoomend',draw);input?.removeEventListener('change',draw);group.remove();}};
}
