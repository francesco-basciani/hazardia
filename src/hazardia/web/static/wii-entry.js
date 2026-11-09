// Opt-in navigation only; no WII controls appear when the module is disabled.
import {getLanguage} from './i18n.js';
let attach=null,attached=false;
const register=()=>{if(!attach||attached)return;document.dispatchEvent(new CustomEvent('hazardia-register-map-plugin',{detail:host=>{if(!attached){attached=true;attach(host);}}}));};
document.addEventListener('hazardia-map-plugin-ready',register);
try {
 const r=await fetch('/api/wii/status');const state=await r.json();
 if(state.enabled){
  const response=await fetch('/api/wii/v1/layers');if(!response.ok)throw Error('WII catalog unavailable');
  const catalog=await response.json();const {attachWiiLayers}=await import('/wii-layer.js');
  attach=host=>attachWiiLayers(host,catalog);register();
  const nav=document.querySelector('#sources-section'),a=document.createElement('a');a.href='/wii.html';
  a.style.cssText='display:block;padding:1rem;margin:1rem 0;color:inherit;border:1px solid #7793a3;border-radius:8px;font-size:1rem';
  const update=()=>a.textContent=getLanguage()==='en'?'Ignition intelligence':'Intelligence incendi';
  update();document.addEventListener('hazardia-language',update);nav?.prepend(a);
 }
} catch {/* Optional module unavailable; existing navigation remains usable. */}
