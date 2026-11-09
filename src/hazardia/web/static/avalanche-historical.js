// Public-source history, separate from current candidate alerts and snow simulations.
const ROOT='/assets/avalanche-historical-inventory/';
export function historyKind(p){return ['EVENT_LOCATION','EVENT_FOOTPRINT'].includes(p?.record_kind)?'event':['POTENTIAL_SITE','DOCUMENTED_SITE'].includes(p?.record_kind)?'site':'unknown';}
export function historyDate(p){return p?.date_precision==='UNQUALIFIED_DATE'?'Data della fonte da verificare: '+(p.date_raw||'—'):p?.date_precision==='DAY'?p.event_date:p?.date_precision==='YEAR'?'Anno '+p.event_date:'Data dell’evento non disponibile';}
export function sarStale(r,now=Date.now()){const age=(now-Date.parse(r?.observed_at))/3600000;return !Number.isFinite(age)||age<0||age>72;}
export function sarMessage(r){if(r?.status!=='CLASSIFICATION_AND_QA_ARCHIVED')return 'Nessuna osservazione utilizzabile; presenza di neve sconosciuta.';const n=r.statistics?.wet_snow_good_qa_pixels;return (r.last_valid_retained?'Ultima osservazione valida conservata · ':'')+(r.stale||sarStale(r)?'Dato storico · ':'')+(n?n+' pixel nativi di neve bagnata con qualità alta/media.':'Nessuna conferma utilizzabile di neve bagnata; non significa assenza di neve.');}
async function jsonFile(url,limit){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error('Archivio non disponibile · HTTP '+r.status);const b=await r.arrayBuffer();if(b.byteLength>limit)throw Error('Archivio oltre il limite');return {raw:b,value:JSON.parse(new TextDecoder().decode(b))};}
async function verified(ref,extension='json'){
 if(!new RegExp('^assets/[a-f0-9]{64}\\.'+extension+'$').test(ref?.file)||!Number.isInteger(ref.bytes)||ref.bytes>4*1024*1024)throw Error('Asset storico non compatibile');
 const r=await fetch(ROOT+ref.file,{cache:'force-cache'});if(!r.ok)throw Error('Asset storico mancante');const b=await r.arrayBuffer();if(b.byteLength!==ref.bytes)throw Error('Dimensione asset storico errata');const h=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('');if(h!==ref.sha256)throw Error('Integrità archivio non verificata');return b;
}
export function attachHistoricalInventory({map,node,visible,primary=null}){
 const host=primary||node,cache=new Map(),group=L.layerGroup().addTo(map);
 if(!map.getPane('avalancheHistory'))map.createPane('avalancheHistory').style.zIndex=435;
 const renderer=L.canvas({padding:.2,pane:'avalancheHistory'});
 const add=(tag,text,parent=host)=>{const e=document.createElement(tag);e.textContent=text;parent.append(e);return e;};
 const makeCheck=(text,on=false)=>{const label=add('label',''),input=document.createElement('input');input.type='checkbox';input.checked=on;input.setAttribute('aria-label',text);label.append(input,document.createTextNode(text));label.style.cssText='display:flex;align-items:center;gap:10px;min-height:40px;margin:0;padding:6px 0;box-sizing:border-box;font-size:13px;line-height:1.35;cursor:pointer';input.style.cssText='width:19px;height:19px;flex:none';return input;};
 const events=makeCheck('Storico valanghe documentate',true),sites=makeCheck('Zone valanghive censite'),sar=makeCheck('Neve bagnata SAR');
 events.dataset.avalancheEventsToggle='true';events.parentElement.style.fontWeight='700';events.parentElement.style.color='#ffd078';host.prepend(events.parentElement);
 sites.parentElement.hidden=sar.parentElement.hidden=true;
 let product=null,features=[],loading=null,generation=0,error=null,sarLayers=[],sarUrls=[],lastManifest=null;
 const caption=L.control({position:'bottomleft'}),captionBox=document.createElement('div');captionBox.setAttribute('data-i18n-skip','');captionBox.style.cssText='display:none;background:#182d38;color:#fff;padding:7px 10px;border-radius:6px;max-width:320px;font-size:12px';caption.onAdd=()=>captionBox;caption.addTo(map);
 const date=x=>x?new Date(x).toLocaleString('it-IT',{timeZone:'Europe/Rome',timeZoneName:'short'}):'data non disponibile';
 function popup(f){const p=f.properties,box=document.createElement('div');box.setAttribute('data-i18n-skip','');add('strong',String(p.name||'').trim()||'Zona documentata',box);add('p',historyKind(p)==='event'?'Evento del passato · '+historyDate(p):'Zona censita · non è un evento datato',box);if(p.municipality)add('p',p.municipality,box);if(p.native_attributes?.TIPO_VAL)add('p',p.native_attributes.TIPO_VAL,box);if(p.location_role==='REPRESENTATIVE_SITE_CENTROID_NOT_RELEASE_POINT')add('p','Posizione rappresentativa del sito, non punto di distacco.',box);add('small',f.id,box);return box;}
 function makeLayer(f){return L.geoJSON(f,{renderer,style:()=>({color:historyKind(f.properties)==='event'?'#ffbe42':'#c59c6c',weight:1.7,fillOpacity:0,bubblingMouseEvents:false,dashArray:historyKind(f.properties)==='site'?'5 4':null}),pointToLayer:(_,latlng)=>L.circleMarker(latlng,{renderer,radius:5,color:'#492b05',weight:1.4,fillColor:'#ffd265',fillOpacity:1,bubblingMouseEvents:false}),onEachFeature:(_,layer)=>layer.bindPopup(()=>popup(f),{maxWidth:330})});}
 const clearSar=()=>{for(const l of sarLayers)map.removeLayer(l);sarLayers=[];for(const u of sarUrls)URL.revokeObjectURL(u);sarUrls=[];};
 async function draw(){const token=++generation;clearSar();captionBox.replaceChildren();captionBox.style.display='none';const ds=map.getContainer().dataset;
  if(!visible.checked||!product){group.clearLayers();ds.avalancheHistoricalVisible='0';return;}
  const bounds=map.getBounds(),keep=new Set();let drawn=0,processed=0;
  for(const f of features){const kind=historyKind(f.properties);if(!f.geometry||!(kind==='event'&&events.checked||kind==='site'&&sites.checked))continue;
   if(token!==generation)return;let layer=cache.get(f.id);if(!layer){layer=makeLayer(f);cache.set(f.id,layer);}const b=layer.getBounds();
   if(b.isValid()&&bounds.intersects(b)){keep.add(f.id);if(!group.hasLayer(layer))group.addLayer(layer);drawn++;}
   if(++processed%64===0)await new Promise(requestAnimationFrame);
  }
  if(token!==generation)return;for(const [id,l]of cache)if(!keep.has(id)&&group.hasLayer(l))group.removeLayer(l);
  ds.avalancheHistoricalVisible=String(drawn);ds.avalancheHistoricalTotal=String(features.filter(f=>historyKind(f.properties)==='event').length);ds.avalancheHistoricalRendering='ALL_IN_VIEWPORT_NO_500_CAP';
  if(events.checked||sites.checked){captionBox.style.display='block';add('div','Oro: eventi del passato · '+drawn+' geometrie in vista',captionBox);}
  if(sar.checked)for(const row of product.sar?.rows||[]){if(!row.view||!row.statistics?.wet_snow_good_qa_pixels)continue;const [w,s,e,n]=row.view.bounds_wgs84;if(!bounds.intersects([[s,w],[n,e]]))continue;
   try{const bytes=await verified(row.view,'png');if(token!==generation)return;const u=URL.createObjectURL(new Blob([bytes],{type:'image/png'}));sarUrls.push(u);const l=L.imageOverlay(u,[[s,w],[n,e]],{opacity:.9,interactive:false}).addTo(map);sarLayers.push(l);captionBox.style.display='block';add('div','SAR · '+row.area+' · '+date(row.observed_at)+(sarStale(row)?' · storico':''),captionBox);}catch(e){error=e.message;}
  }
 }
 async function load(){if(loading)return loading;loading=(async()=>{try{const m=(await jsonFile(ROOT+'manifest.json',65536)).value;if(product&&lastManifest===m.sha256){await draw();return;}
  const p=JSON.parse(new TextDecoder().decode(await verified(m)));if(p.schema!=='hazardia.avalanche.historical-inventory/1.0'||!Array.isArray(p.chunks)||p.chunks.length>100)throw Error('Contratto storico non compatibile');
  let ff=[],bytes=0;for(const c of p.chunks){bytes+=c.bytes;if(bytes>24*1024*1024)throw Error('Inventario oltre il limite browser');const part=JSON.parse(new TextDecoder().decode(await verified(c)));if(part.type!=='FeatureCollection'||part.features.length!==c.features)throw Error('Conteggio archivio errato');ff.push(...part.features);}
  if(ff.length!==p.records||new Set(ff.map(f=>f.id)).size!==ff.length)throw Error('Inventario incompleto o identificativi duplicati');
  group.clearLayers();cache.clear();product=p;features=ff;lastManifest=m.sha256;error=null;
  sites.parentElement.hidden=!features.some(f=>historyKind(f.properties)==='site');sar.parentElement.hidden=!(p.sar?.rows||[]).some(r=>r.view&&r.statistics?.wet_snow_good_qa_pixels>0);events.title='Tutte le geometrie documentate acquisite; copertura nazionale parziale.';
  const ds=map.getContainer().dataset;ds.avalancheHistoricalRecords=String(p.records);ds.avalancheHistoricalError='';await draw();
 }catch(e){error=e.message;events.title=error;map.getContainer().dataset.avalancheHistoricalError=error;if(!product){captionBox.style.display=visible.checked?'block':'none';captionBox.textContent='Storico temporaneamente non disponibile';}}})().finally(()=>loading=null);return loading;}
 for(const input of [events,sites,sar])input.onchange=()=>{if(product)draw();else load();};
 const move=()=>draw();map.on('moveend',move);visible.addEventListener('change',()=>product?draw():load());
 const timer=setInterval(()=>{if(visible.checked&&!document.hidden)load();},300000);
 map.on('unload',()=>{++generation;clearInterval(timer);map.off('moveend',move);group.clearLayers();clearSar();caption.remove();cache.clear();});
 load();
 return {load,events,sites,sar,reportData:()=>({product,features,error,manifestSha:lastManifest})};
}
