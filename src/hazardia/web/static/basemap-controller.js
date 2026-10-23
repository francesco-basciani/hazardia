/* A single Leaflet map: layer switching never resets camera, data or clock. */
export function basemapController(map,{select,satellite,regional,ortho,osm,onChange,onStatus}){
 let visible=true,generation=0,reason='',errors=0,attempted=new Set(),active=null,loading=false;
 const groups={osm:[osm],ortho:[regional,ortho],sentinel:[satellite]};
 function clear(){for(const layer of [satellite,regional,ortho,osm])layer.remove();}
 function publish(){onStatus({mode:select.value,reason,errors,loading});}
 async function apply(manual=false){
  const token=++generation;if(manual){reason='';errors=0;attempted=new Set();}clear();active=null;
  if(!visible)return;let mode=select.value;attempted.add(mode);
  if(mode==='ortho'){
   try{const response=await fetch('/api/maps/regional/status');if(!response.ok)throw Error('Stato sorgente non disponibile');const status=await response.json();if(token!==generation||!visible)return;if(!status.can_download_tiles&&!status.cache_bytes){reason='Satellite temporaneamente limitato: OpenStreetMap attiva. Le tessere già in cache restano consultabili.';select.value=mode='osm';attempted.add(mode);}}
   catch(error){if(token!==generation)return;reason='Satellite non disponibile: OpenStreetMap attiva.';select.value=mode='osm';attempted.add(mode);}
  }
  if(token!==generation||!visible)return;active=mode;loading=mode!=='sentinel';for(const layer of groups[mode])layer.addTo(map);map.getContainer().classList.toggle('basemap-streets',mode==='osm');map.getContainer().dataset.basemap=mode;map.fire('basemapchange');onChange(mode);publish();
 }
 function failure(layer){
  if(!visible||!active||!map.hasLayer(layer))return;
  // Regional backdrop remains under the optional high-resolution orthophotos.
  if(layer===ortho){ortho.remove();reason='Ortofoto locale non disponibile; resta il mosaico satellitare.';publish();return;}
  errors++;publish();if(errors<2)return;
  const next=['osm','ortho','sentinel'].find(k=>!attempted.has(k));if(!next){reason='Sfondi online non disponibili. Il ritaglio offline copre soltanto l’area di studio.';publish();return;}
  const old=active;select.value=next;reason='Sfondo '+(old==='osm'?'OpenStreetMap':'satellitare')+' non disponibile: '+(next==='osm'?'OpenStreetMap':next==='ortho'?'satellite':'ritaglio offline')+' attivo.';errors=0;apply();
 }
 for(const layer of [regional,ortho,osm]){layer.on('tileerror',()=>failure(layer));layer.on('loading',()=>{if(visible&&map.hasLayer(layer)){loading=true;publish();}});layer.on('load',()=>{if(visible&&map.hasLayer(layer)){loading=false;map.getContainer().dataset.basemapLoadedAt=String(performance.now());publish();}});}
 return {apply,visible(on){visible=on;if(!on){generation++;clear();active=null;}else apply();},status:()=>({mode:select.value,reason,errors})};
}
