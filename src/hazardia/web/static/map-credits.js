/* Preserve Leaflet's live provider credits; keep their details in Info and guide.
 * OSM initial attribution remains visible until interaction or five seconds.
 */
export function compactMapCredits(map){
 const attribution=map.attributionControl.getContainer();
 const control=L.control({position:'bottomright'});
 control.onAdd=()=>{
  const button=document.createElement('button');button.type='button';
  button.className='map-credit-link';button.textContent='ⓘ Info e licenze';
  button.setAttribute('aria-label','Apri Info e guida: fonti e licenze della mappa');
  L.DomEvent.disableClickPropagation(button);L.DomEvent.disableScrollPropagation(button);
  button.addEventListener('click',()=>document.querySelector('[data-view="help"]')?.click());
  return button;
 };
 control.addTo(map);
 const sync=()=>{
  const target=document.getElementById('map-credit-details');
  if(target)target.replaceChildren(...[...attribution.childNodes].map(node=>node.cloneNode(true)));
 };
 new MutationObserver(sync).observe(attribution,{childList:true,subtree:true,characterData:true});sync();
 const collapse=()=>attribution.classList.add('map-credit-collapsed');
 map.once('movestart click zoomstart',collapse);setTimeout(collapse,5000);
}
