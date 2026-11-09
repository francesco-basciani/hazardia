// Optional consumer registration only; TCIP has its own service and database.
let attach=null,attached=false;
const register=()=>{if(!attach||attached)return;document.dispatchEvent(new CustomEvent('hazardia-register-map-plugin',{detail:host=>{if(!attached){attached=true;attach(host);}}}));};
document.addEventListener('hazardia-map-plugin-ready',register);
try {
 const response=await fetch('/api/tcip/status');const state=await response.json();
 if(response.ok&&state.enabled){
  const [{attachTcipGroup},{attachLocalRates},{attachDocumentMap},{attachPopulationRates},{attachTcipLayers}]=await Promise.all([import('/tcip-group.js'),import('/tcip-local-rates.js'),import('/tcip-document-map.js'),import('/tcip-population-map.js'),import('/tcip-layer.js')]);
  attach=host=>attachTcipGroup(host,[
   {id:'rates',label:'Reati per abitante · massimo dettaglio',attach:attachLocalRates},
   {id:'documents',label:'Luoghi nelle notizie · da verificare',attach:attachDocumentMap},
   {id:'regional',label:'Confronto con Italia · serie regionali storiche',attach:attachPopulationRates},
   {id:'archive',label:'Quote del dataset · archivio storico',attach:attachTcipLayers}
  ]);register();
 }
} catch {/* Optional consumer cannot block the monitoring application. */}
