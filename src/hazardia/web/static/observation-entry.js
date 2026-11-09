import {attachObservations} from '/satellite-observations.js';
let attached=false;
const register=()=>{if(attached)return;document.dispatchEvent(new CustomEvent('hazardia-register-map-plugin',{detail:host=>{if(attached)return;attached=true;attachObservations(host);}}));};
document.addEventListener('hazardia-map-plugin-ready',register);register();

// Source references remain available outside the map; no acquisition is triggered here.
const sources=document.getElementById('sources-section');
if(sources&&!document.getElementById('observed-source-references')){
 const section=document.createElement('section');section.id='observed-source-references';
 const heading=document.createElement('h3');heading.textContent='Osservazioni satellitari';section.append(heading);
 for(const [label,url] of [
  ['NASA FIRMS · anomalie termiche NOAA-20 · CSV pubblico Europa','https://firms.modaps.eosdis.nasa.gov/active_fire/'],
  ['EFFIS · perimetri osservati storici, acquisiti tramite WII','https://forest-fire.emergency.copernicus.eu/about-effis/data-and-services']]){
   const row=document.createElement('p'),a=document.createElement('a');a.href=url;a.textContent=label;a.target='_blank';a.rel='noopener';row.append(a);section.append(row);
 }
 const note=document.createElement('p');note.textContent='Nei livelli sono indicati orario della misura, acquisizione, copertura e dati mancanti. I nuovi livelli osservati sono consultivi e non modificano automaticamente i simulatori o l’ottimizzatore.';section.append(note);sources.append(section);
}
