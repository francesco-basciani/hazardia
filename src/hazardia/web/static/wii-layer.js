// HAZARDIA consumes one autonomous WII risk product, not regional model variants.
export function attachWiiLayers({map,entry,refresh,fireLayer},catalog){
 const panel=document.createElement('section');panel.dataset.category='wii';
 const title=document.createElement('h3');title.textContent='WII · rischio di innesco';
 const visible=document.createElement('input');visible.type='checkbox';visible.setAttribute('aria-label','Mostra WII sulla mappa');
 const label=document.createElement('label');label.append(visible,document.createTextNode(' Mostra livello'));
 const reload=document.createElement('button');reload.type='button';reload.textContent='Aggiorna prodotto';
 const status=document.createElement('p');status.setAttribute('role','status');status.textContent='Unico inventario nazionale · aggiornamento automatico.';
 const note=document.createElement('p');note.textContent='Storico istituzionale e notizie localizzate nello stesso modello. Verde indica suscettibilità relativa minore, non assenza di rischio. Dati mancanti in grigio. Modello sperimentale: non è pericolo meteo giornaliero o allerta ufficiale.';
 const legend=document.createElement('div');legend.setAttribute('aria-label','Legenda WII');
 const link=document.createElement('a');link.href='/wii.html';link.style.color='#b9e6f4';link.textContent='Database, fonti e validazione WII';
 panel.append(title,label,reload,status,note,legend,link);
 let layer=null,controller=null,generation=0,version=null,polling=false,summary='';
 const renderer=L.canvas({padding:.25});
 const endpoint=catalog.layers[0]?.href||'/api/wii/v1/layers/italy-susceptibility';
 const clear=()=>{if(layer){map.removeLayer(layer);layer=null;}};
 async function load({fitAfter=false}={}){
  const request=++generation;controller?.abort();
  if(!visible.checked){clear();status.textContent='Livello disattivato.';return;}
  controller=new AbortController();status.textContent='Caricamento inventario nazionale unificato…';
  try{
   const response=await fetch(endpoint,{signal:controller.signal});if(!response.ok)throw Error('HTTP '+response.status);
   const data=await response.json();if(request!==generation)return;
   if(data.type!=='FeatureCollection'||data.metadata?.status!=='AVAILABLE'){clear();status.textContent='Calcolo in corso · dati non ancora disponibili.';return;}
   const metadata=data.metadata;clear();legend.replaceChildren();version=metadata.product_id;
   layer=L.geoJSON(data,{renderer,style:f=>({color:f.properties.color||'#87939c',weight:.4,fillOpacity:.6}),onEachFeature:(f,item)=>{const detail=document.createElement('div');for(const [key,value] of Object.entries(f.properties||{})){if(value===null||typeof value==='object')continue;const row=document.createElement('p');row.textContent=key+': '+value;detail.append(row);}item.bindPopup(detail);}}).addTo(map);
   summary=data.features.length+' celle · storico nazionale unificato · aggiornato '+metadata.created_at;
   status.textContent=summary+(metadata.last_error?' · aggiornamento bloccato: '+metadata.last_error:metadata.pending?' · aggiornamento in attesa':'');
   if(fitAfter){const inspector=document.getElementById('console-inspector');const width=inspector&&!inspector.hidden?inspector.getBoundingClientRect().width:0;map.fitBounds(layer.getBounds(),{paddingTopLeft:[25,25],paddingBottomRight:[width+25,35],maxZoom:9});}
   const description=document.createElement('p');description.textContent='Indice rispetto alla media nazionale del supporto storico annualizzato. Aggiornamento automatico; nuovi dati verificati ogni30s.';legend.append(description);
   for(const level of data.legend||[]){const row=document.createElement('p'),swatch=document.createElement('span');swatch.style.cssText='display:inline-block;width:1em;height:1em;margin-right:.5em';swatch.style.backgroundColor=level.color;row.append(swatch,document.createTextNode(level.label_it+' · '+level.lower+'–'+(level.upper??'∞')+' × media'));legend.append(row);}
   const rights=document.createElement('p');rights.textContent='Fonti e precisione documentate nell’inventario. Include dati CC BY-NC3.0, uso di ricerca non commerciale.';legend.append(rights);
  }catch(error){if(request===generation&&error.name!=='AbortError'){clear();version=null;status.textContent='WII: '+error.message;}}
 }
 async function poll(){if(!visible.checked||document.hidden||polling)return;polling=true;try{const r=await fetch('/api/wii/pipeline');if(!r.ok)throw Error('HTTP '+r.status);const state=await r.json();if(state.artifact_id!==version)await load();else status.textContent=summary+(state.last_error?' · aggiornamento bloccato: '+state.last_error:state.pending?' · aggiornamento in attesa':'');}catch(error){status.textContent='Aggiornamento WII non disponibile · '+error.message;}finally{polling=false;}}
 visible.onchange=()=>load({fitAfter:visible.checked});reload.onclick=()=>load();const timer=setInterval(poll,30000);
 if(fireLayer)fireLayer.addWii(panel,visible);else{entry('Incendi',panel,'◈',visible);refresh();}
 map.on('unload',()=>{clearInterval(timer);++generation;controller?.abort();clear();});
}
