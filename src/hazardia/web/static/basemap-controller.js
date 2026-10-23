/* Preserve successful tiles/camera/clock. Offline crop is always an explicit choice. */
export function basemapController(map,{select,satellite,regional,ortho,osm,onChange,onStatus}){
 let visible=true,generation=0,reason='',errors=0,active=null,loading=false,fallback=false;
 const failed=new Map([regional,ortho,osm].map(l=>[l,new Set()]));const key=e=>e.coords?e.coords.z+'-'+e.coords.x+'-'+e.coords.y:'tile';
 const groups={osm:[osm],ortho:[regional,ortho],sentinel:[satellite]};
 osm.setZIndex?.(0);regional.setZIndex?.(1);ortho.setZIndex?.(2);
 function clear(){for(const layer of [satellite,regional,ortho,osm])layer.remove();for(const s of failed.values())s.clear();}
 function publish(){onStatus({mode:select.value,reason,errors,loading,fallback});}
 function streets(message){if(!map.hasLayer(osm))osm.addTo(map);fallback=true;reason=message;publish();}
 async function apply(manual=false){
  const token=++generation;if(manual){reason='';errors=0;}clear();active=null;fallback=false;
  if(!visible)return;const mode=select.value;active=mode;loading=mode!=='sentinel';for(const layer of groups[mode])layer.addTo(map);
  map.getContainer().classList.toggle('basemap-streets',mode==='osm');map.getContainer().dataset.basemap=mode;map.fire('basemapchange');onChange(mode);publish();
  // Status is informative, never a blocking request ahead of the first image.
  if(mode==='ortho')try{const r=await fetch('/api/maps/regional/status');if(!r.ok)return;const status=await r.json();if(token!==generation||!visible)return;if(!status.can_download_tiles)streets('Satellite limitato: cartografia sotto le immagini disponibili. Nessun passaggio al ritaglio locale.');}catch{/* Tile errors provide the source signal. */}
 }
 function failure(layer){
  if(!visible||!active||!map.hasLayer(layer))return;errors++;
  if(layer===ortho){reason='Alcune ortofoto non disponibili; resta lo sfondo satellitare.';publish();return;}
  if(layer===regional){if(errors>=2)streets('Alcune immagini non disponibili: cartografia di supporto nelle aree mancanti. Le immagini già caricate restano visibili.');else publish();return;}
  reason='Alcune tessere cartografiche non disponibili. Mantengo quelle caricate; riprova lo sfondo. Il ritaglio locale non viene scelto automaticamente.';publish();
 }
 for(const layer of [regional,ortho,osm]){layer.on('tileerror',e=>{failed.get(layer).add(key(e||{}));failure(layer);});layer.on('tileload tileunload tileabort',e=>{failed.get(layer).delete(key(e||{}));if(![...failed.values()].some(s=>s.size)){reason='';publish();}});layer.on('loading',()=>{if(visible&&map.hasLayer(layer)){loading=true;publish();}});layer.on('load',()=>{if(visible&&map.hasLayer(layer)){loading=false;map.getContainer().dataset.basemapLoadedAt=String(performance.now());publish();}});}
 return {apply,visible(on){if(visible===on&&active)return;visible=on;if(!on){generation++;clear();active=null;}else apply();},status:()=>({mode:select.value,reason,errors,fallback})};
}
