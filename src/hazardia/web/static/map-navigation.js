import {layerMinZoom} from '/layer-menu-model.js';
/* Consultation only: a navigation pin is never a simulation ignition or an asset. */
export function zoomChoices(min,max){return Array.from({length:19},(_,i)=>i+2).filter(z=>z>=min&&z<=max);}
export function navigationView(pin,center,zoom,min,max){if(!Number.isFinite(zoom)||zoom<min||zoom>max)return null;return {point:pin||center,zoom};}
export function mapNavigation(map){
 const bar=map.zoomControl.getContainer(),center=document.getElementById('monitor-fit'),fallback=center.onclick;
 let pin=null;const extra=document.createElement('div');extra.className='map-zoom-extra';
 const place=document.createElement('button');place.type='button';place.className='map-pin-place';place.innerHTML='<svg viewBox="0 0 24 28" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 2a8 8 0 0 0-8 8c0 6 8 15 8 15s8-9 8-15a8 8 0 0 0-8-8Z"/><circle cx="12" cy="10" r="3"/></svg>';place.setAttribute('aria-label','Posiziona pin sulla mappa');place.title='Clicca sulla mappa per posizionare il pin';place.setAttribute('aria-pressed','false');
 const select=document.createElement('select');select.className='map-zoom-select';select.setAttribute('aria-label','Livello di zoom');
 const clear=document.createElement('button');clear.type='button';clear.textContent='×';clear.className='map-pin-clear';clear.setAttribute('aria-label','Rimuovi pin');clear.title='Rimuovi pin';clear.disabled=true;
 extra.append(place,select,clear);bar.append(extra);
 const sync=()=>{const levels=zoomChoices(map.getMinZoom(),map.getMaxZoom());if(select.dataset.levels!==levels.join()){select.replaceChildren(...levels.map(z=>{const o=document.createElement('option');o.value=String(z);o.textContent='Zoom '+z+(z===layerMinZoom.buildings?' · Edifici':'');return o;}));select.dataset.levels=levels.join();}select.value=String(map.getZoom());map.getContainer().dataset.navigationZoom=String(map.getZoom());};
 const go=zoom=>{const view=navigationView(pin,map.getCenter(),zoom,map.getMinZoom(),map.getMaxZoom());if(view)map.setView(view.point,view.zoom,{animate:false,reset:true});sync();};
 select.onchange=()=>go(Number(select.value));center.onclick=()=>{if(pin)go(map.getZoom());else fallback?.();};
 place.onclick=()=>{const armed=place.getAttribute('aria-pressed')!=='true';place.setAttribute('aria-pressed',String(armed));map.getContainer().classList.toggle('navigation-pin-armed',armed);};
 map.on('navigationpin',e=>{pin=e.latlng;clear.disabled=false;place.setAttribute('aria-pressed','false');map.getContainer().classList.remove('navigation-pin-armed');center.setAttribute('aria-label','Centra sul pin');map.getContainer().dataset.navigationPin=JSON.stringify([pin.lat,pin.lng]);});
 clear.onclick=()=>{pin=null;clear.disabled=true;place.setAttribute('aria-pressed','false');map.getContainer().classList.remove('navigation-pin-armed');delete map.getContainer().dataset.navigationPin;center.setAttribute('aria-label','Centra le aree disponibili');map.fire('navigationpinclear');};
 map.on('zoomend resize zoomlevelschange',sync);sync();L.DomEvent.disableClickPropagation(extra);L.DomEvent.disableScrollPropagation(extra);
}
