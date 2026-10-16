/* Screen-sized geographic references; never infer an ignition from a raster extent. */
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const symbols={FIRE:'<path d="M14 2c2 7-4 8-1 12 2-1 3-3 3-5 6 5 6 13-3 13C3 22 3 13 8 8c-1 5 1 5 2 6-1-5 5-7 4-12Z"/>',FLOOD:'<path d="M12 2C9 7 5 11 5 15a7 7 0 0 0 14 0c0-4-4-8-7-13Z"/>',ALERT:'<path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5m0 3v1" stroke="#fff" stroke-width="2"/>'};
export function eventMarkers(map){
 const pane='eventReferences';if(!map.getPane(pane)){map.createPane(pane);map.getPane(pane).style.zIndex=650;}
 const group=L.layerGroup().addTo(map);let entries=[];
 const control=L.control({position:'topright'});let box;
 control.onAdd=()=>{box=L.DomUtil.create('div','event-locator');box.setAttribute('aria-label','Eventi fuori inquadratura');L.DomEvent.disableClickPropagation(box);L.DomEvent.disableScrollPropagation(box);return box;};control.addTo(map);
 function locate(){box.replaceChildren();const size=map.getSize();for(const e of entries){const pixel=map.latLngToContainerPoint(e.point);if(pixel.x>=64&&pixel.x<=size.x-64&&pixel.y>=48&&pixel.y<=size.y-12)continue;const b=document.createElement('button');b.type='button';b.textContent=e.label+' · fuori vista ↗';b.title='Centra la mappa sul punto di riferimento';b.onclick=()=>map.panTo(e.point,{animate:false});box.append(b);}box.hidden=!box.children.length;}
 function update(next){entries=next.filter(e=>e.point&&e.point.length===2&&e.point.every(Number.isFinite));group.clearLayers();for(const e of entries){const kind=symbols[e.kind]?e.kind:'ALERT';const marker=L.marker(e.point,{pane,keyboard:true,bubblingMouseEvents:false,zIndexOffset:1000,title:e.label+' · '+e.meaning,alt:e.label,icon:L.divIcon({className:'hazard-event-icon '+kind.toLowerCase(),iconSize:[40,40],iconAnchor:[20,40],popupAnchor:[0,-40],html:'<span class="event-pin"><svg aria-hidden="true" viewBox="0 0 24 24">'+symbols[kind]+'</svg></span>'})}).addTo(group);marker.bindPopup('<strong>'+esc(e.label)+'</strong><br>'+esc(e.meaning)+'<br>'+e.point.map(v=>v.toFixed(5)).join(', ')+' · WGS84'+(e.detail?'<br>'+esc(e.detail):''));}layout();}
 function layout(){// Keep neighbouring references individually identifiable without moving their geographic anchor.
 const used=[];group.eachLayer(m=>{const p=map.latLngToContainerPoint(m.getLatLng()),near=used.filter(q=>p.distanceTo(q)<46).length;used.push(p);const el=m.getElement()?.firstElementChild;if(el){const shift=near?Math.ceil(near/2)*44*(near%2?1:-1):0;el.style.transform='translateX('+shift+'px)';el.classList.toggle('offset',shift!==0);}});locate();}
 map.on('zoomend moveend resize',layout);return {update};
}
export function scenarioReference(s){
 const c=L.latLngBounds(s.bounds).getCenter();let point=[c.lat,c.lng],meaning='Centro del dominio simulato; non è un innesco o un rilevamento osservato.';
 if(s.hazard==='FIRE'){
  let first=null;for(const f of s.cells?.features||[]){if(Number(f.properties?.probability)>0&&Number.isFinite(f.properties?.arrival_s)&&(!first||f.properties.arrival_s<first.properties.arrival_s))first=f;}
  const ring=first?.geometry?.type==='Polygon'?first.geometry.coordinates[0]:null;
  if(ring?.length){const bounds=L.latLngBounds(ring.map(p=>[p[1],p[0]])),q=bounds.getCenter();point=[q.lat,q.lng];meaning='Riferimento sulla cella con primo arrivo simulato minimo; non è un innesco osservato o un rilevamento reale.';}
 }
 return {kind:s.hazard,point,label:s.hazard==='FIRE'?'Incendio simulato':'Scenario alluvionale',meaning,detail:s.id+' · '+s.valid_from+' → '+s.valid_until+' · '+s.positive_cells+' celle positive · ricerca non calibrata'};
}
