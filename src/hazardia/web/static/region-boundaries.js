/* Administrative context, never a jurisdiction or physics input. */
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sourceCache=new Map();
export function regionBoundaries(map,{url='/assets/administrative-regions.json',highlightCode='13'}={}){
 const pane='regionContext';map.createPane(pane);map.getPane(pane).style.zIndex=530;map.getPane(pane).style.pointerEvents='none';
 const labelPane='regionNames';map.createPane(labelPane);map.getPane(labelPane).style.zIndex=600;map.getPane(labelPane).style.pointerEvents='none';
 const group=L.layerGroup(),labels=L.layerGroup();let data=null,outline,ink,on=true;
 const control=L.control({position:'topright'});let input,status;
 control.onAdd=()=>{const box=L.DomUtil.create('div','region-control');const label=document.createElement('label');input=document.createElement('input');input.type='checkbox';input.checked=true;input.setAttribute('aria-label','Confini regionali');label.append(input,document.createTextNode('Confini regionali'));status=document.createElement('small');status.textContent='Caricamento confini…';box.append(label,status);L.DomEvent.disableClickPropagation(box);L.DomEvent.disableScrollPropagation(box);input.onchange=()=>{on=input.checked;draw();};return box;};control.addTo(map);
 function draw(){const z=map.getZoom(),show=on&&data&&z<=11;map.getContainer().dataset.regionBoundaries=show?'visible':data?'hidden':'unavailable';
  if(!show){group.remove();labels.remove();if(data)status.textContent=on?'Visibili nella vista d’insieme':'Nascosti';return;}
  if(!outline){const base={pane,fill:false,interactive:false,smoothFactor:1.5};outline=L.geoJSON(data,{...base,style:{color:'#172d3b',weight:4.5,opacity:.8}}).addTo(group);ink=L.geoJSON(data,{...base,style:f=>({color:f.properties.code===highlightCode?'#ffe2a3':'#f1f5f8',weight:1.4,opacity:.95})}).addTo(group);}
  group.addTo(map);labels.addTo(map);labels.clearLayers();outline.setStyle({weight:z===11?3:4.5,opacity:z===11?.45:.8});ink.setStyle(f=>({weight:f.properties.code===highlightCode?2.3:1.4,opacity:z===11?.5:.95}));status.textContent='Istat · 2026 · zoom8–11';
  if(z>10)return;const b=map.getBounds(),used=[];
  for(const f of data.features){const p=f.properties.label_point;if(!b.contains(p))continue;const pt=map.latLngToContainerPoint(p),size=map.getSize();if(pt.x<80||pt.x>size.x-80||pt.y<15||pt.y>size.y-15)continue;if(used.some(q=>Math.abs(q.x-pt.x)<120&&Math.abs(q.y-pt.y)<30))continue;used.push(pt);L.marker(p,{pane:labelPane,interactive:false,keyboard:false,icon:L.divIcon({className:'region-name'+(f.properties.code===highlightCode?' highlighted':''),html:esc(f.properties.name),iconSize:[180,26],iconAnchor:[90,13]})}).addTo(labels);}
 }
 map.on('zoomend moveend',draw);
 if(!sourceCache.has(url)){if(sourceCache.size>=4)sourceCache.delete(sourceCache.keys().next().value);sourceCache.set(url,fetch(url).then(async r=>{if(!r.ok)throw Error();const text=await r.text();if(text.length>4*1024**2)throw Error();const d=JSON.parse(text);if(d.type!=='FeatureCollection'||!Array.isArray(d.features)||d.features.length>100||!d.features.length||d.features.some(f=>!['Polygon','MultiPolygon'].includes(f.geometry?.type)||!f.properties?.name||!Array.isArray(f.properties.label_point)||f.properties.label_point.length!==2))throw Error();return d;}));}
 sourceCache.get(url).then(d=>{data=d;map.getContainer().dataset.regionCount=String(d.features.length);map.attributionControl.addAttribution('© Istat · confini2026 · CC BY4.0 · generalizzati a fini statistici');draw();}).catch(()=>{status.textContent='Confini non disponibili';input.disabled=true;map.getContainer().dataset.regionBoundaries='unavailable';});
 return {refresh:draw};
}
