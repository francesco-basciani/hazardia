import {sourceText} from '/i18n.js';
import {layerMinZoom,layerVisible,menuGroups,menuGroup} from '/layer-menu-model.js';
const paths={
 weather:'M3 16h14a4 4 0 0 0 0-8 5 5 0 0 0-9-1A5 5 0 0 0 3 16m4 3-1 2m6-2-1 2m6-2-1 2',
 buildings:'M4 21V5h10v16M14 11h6v10M7 8h4M7 12h4M7 16h4M2 21h20',
 settlements:'m2 11 5-5 5 5m-8-1v10h7V10m2-3 4-4 5 5m-7 0v12h5V8',
 healthcare:'M5 21V5h14v16M2 21h20M12 7v6m-3-3h6m-6 11v-5h6v5',
 emergency:'M3 6h11v12H3Zm11 5h4l3 4v3h-7M6 9v5m-2-3h4M6 21a2 2 0 1 0 0-4 2 2 0 0 0 0 4m12 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4',
 education:'m2 8 10-5 10 5-10 5Zm4 3v6l6 3 6-3v-6m4-3v8',
 transport:'m7 2-4 20m14-20 4 20M12 3v4m0 4v3m0 4v3',
 utilities:'M4 21 9 3h6l5 18M7 9h10M5 15h14M9 3l8 12M15 3 7 15',
 environment:'M2 20c4-5 6 5 10 0s6 5 10 0M12 3 5 13h14ZM12 13v5',
 boundaries:'M3 3h6v6H3Zm12 12h6v6h-6ZM9 6h9v9M6 9v9h9',
 other:'M4 4h6v6H4Zm10 0h6v6h-6ZM4 14h6v6H4Zm10 0h6v6h-6Z',
 critical:'m12 3 10 18H2ZM12 9v5m0 3v1',
 quake:'M2 12h4l3-8 4 16 3-8h6',
 radar:'M12 3a9 9 0 1 0 9 9M12 7a5 5 0 1 0 5 5m-5 0 8-8',
 rain:'M12 2C9 6 5 11 5 15a7 7 0 0 0 14 0c0-4-4-9-7-13Z',
 satellite:'m8 7 9 9-4 4-9-9Zm6-4 7 7-3 3-7-7ZM3 15l6 6m-6-3 3 3',
};
export const icon=(key)=>'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="'+(paths[key]||paths.other)+'"/></svg>';
export function organiseLayers(map,list,choices){
 const containers=new Map();list.replaceChildren();
 for(const [id,name] of menuGroups){const group=document.createElement('section');group.className='console-layer-group';group.dataset.group=id;const h=document.createElement('h3');h.textContent=name;group.append(h);list.append(group);containers.set(id,group);}
 for(const [button,node] of choices){
  const row=button.layerRow,name=sourceText(button.querySelector('span:nth-child(2)')),category=node.dataset.category;
  const group=menuGroup(category,name);containers.get(group).append(row);
  const key=category||({'Centri abitati':'settlements','Cavi aerei e tralicci':'utilities','Confini':'boundaries','Criticità territoriali':'critical','Terremoti osservati':'quake','Radar pioggia osservata':'radar','Pluviometri':'rain','Immagini satellitari recenti':'satellite','Meteo e osservazioni':'weather'}[name]);
  button.querySelector('.console-layer-icon').innerHTML=icon(key);
  const check=row.querySelector(':scope>input');if(check){const label=document.createElement('label');label.className='console-visibility';const eye=document.createElement('span');eye.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/><path class="eye-off" d="m3 3 18 18"/></svg>';check.before(label);label.append(check,eye);}
  if(layerMinZoom[category]){
   const badge=document.createElement('span');badge.className='console-zoom-badge';badge.innerHTML='<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="7" cy="7" r="4"/><path d="m10 10 4 4M7 5v4M5 7h4"/></svg>';badge.append(document.createTextNode(layerMinZoom[category]+'+')); button.querySelector('.console-chevron').before(badge);
   const note=document.createElement('p');note.className='console-zoom-note';node.prepend(note);
   const sync=()=>{const available=layerVisible(category,map.getZoom());row.dataset.zoomAvailable=String(available);badge.title=available?'Visibile a questo zoom':'Visibile da zoom '+layerMinZoom[category];badge.setAttribute('aria-label',badge.title);note.textContent=available?'Zoom sufficiente per mostrare gli edifici disponibili nell’estratto.':'Edifici visibili da zoom '+layerMinZoom[category]+'. Avvicina la mappa; i dati scientifici restano invariati.';};map.on('zoomend',sync);sync();
  }
 }
 for(const group of containers.values())if(group.children.length===1)group.remove();
}
export function consolidateMapKeys(map,stage,body,open){
 const host=document.createElement('section');host.className='console-map-key';host.hidden=true;
 const intro=document.createElement('p');intro.textContent='Simboli, scale e stato dei livelli attivi. I dati previsti, osservati e simulati restano distinti.';host.append(intro);
 for(const node of [...map.getContainer().querySelectorAll('.critical-map-legend,.map-symbols,.weather-map-legend,.traffic-badge,.map-credit-link')]){node.classList.remove('leaflet-control');host.append(node);}
 body.append(host);
 const button=document.createElement('button');button.type='button';button.className='console-legend-toggle';button.textContent='ⓘ  Legenda e stato';button.setAttribute('aria-controls','console-inspector');button.onclick=()=>open('Legenda e stato',host);stage.append(button);
 const statusNodes=[...host.querySelectorAll('.weather-map-legend,.traffic-badge')];
 const status=()=>{const incomplete=statusNodes.some(n=>!n.hidden&&/mancant|incomplet|non disponibili|errore|scadut|missing|incomplete|unavailable|error|expired/i.test(n.matches('.traffic-badge')?n.textContent:n.querySelector('[role=status]')?.textContent||''));button.dataset.warning=String(incomplete);const title=incomplete?'Dati mancanti o copertura parziale: apri la legenda.':'Scale, simboli e stato dei livelli attivi.';if(button.title!==title)button.title=title;};
 const observer=new MutationObserver(status);for(const n of statusNodes)observer.observe(n,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['hidden']});status();map.on('unload',()=>observer.disconnect());
 L.DomEvent.disableClickPropagation(button);L.DomEvent.disableScrollPropagation(button);
}
