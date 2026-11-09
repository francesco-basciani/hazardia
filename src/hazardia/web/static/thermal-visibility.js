/* Satellite observations follow the fire parent, independently of its background view. */
export function bindThermalVisibility(master,selection,onEnable,onDisable){
 let active=false,disposed=false;
 const sync=()=>{if(disposed)return;const next=master.checked&&selection.checked;if(next===active)return;active=next;if(active)onEnable();else onDisable();};
 for(const name of ['change','hazardia-state'])master.addEventListener(name,sync);
 selection.addEventListener('change',sync);sync();
 return {sync,dispose(){if(disposed)return;disposed=true;for(const name of ['change','hazardia-state'])master.removeEventListener(name,sync);selection.removeEventListener('change',sync);if(active){active=false;onDisable();}}};
}
