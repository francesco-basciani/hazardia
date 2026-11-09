let attached=false;
const register=()=>document.dispatchEvent(new CustomEvent('hazardia-register-map-plugin',{detail:async host=>{
 if(attached)return;attached=true;
 const {attachAvalancheLayer}=await import('/avalanche-layer.js?v=map-checks-20261106');attachAvalancheLayer(host);
}}));
document.addEventListener('hazardia-map-plugin-ready',register);
register();
