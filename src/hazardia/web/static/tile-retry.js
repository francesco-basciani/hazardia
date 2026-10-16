/* Bounded retries for local tile-proxy bursts; never contact provider directly. */
export function resilientTiles(layer,onStatus=()=>{}){
 const failed=new Set(),timers=new Set();const key=e=>e.tile?.src?.split('?')[0];
 layer.on('tileload',e=>{failed.delete(key(e));onStatus(failed.size);});
 layer.on('tileerror',e=>{const tile=e.tile,k=key(e);failed.add(k);onStatus(failed.size);const n=tile.dataset.retryCount?Number(tile.dataset.retryCount):0;if(n>=3)return;tile.dataset.retryCount=String(n+1);const timer=setTimeout(()=>{timers.delete(timer);if(tile.isConnected)tile.src=k+'?retry='+(n+1);},[800,2200,5000][n]+Math.random()*350);timers.add(timer);});
 layer.on('remove',()=>{for(const t of timers)clearTimeout(t);timers.clear();failed.clear();onStatus(0);});
}
