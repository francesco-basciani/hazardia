import {tileQueue} from '/tile-queue.js';
const pool=tileQueue(4),targets=new Set();
const updateAll=()=>{const state=JSON.stringify(pool.status());for(const target of targets){if(target.isConnected===false)targets.delete(target);else target.dataset.tileQueue=state;}};
/* Native image loading preserves HTTP cache/validators and avoids Blob copies. */
const Scheduled=L.TileLayer.extend({
 createTile(coords,done){
  const tile=document.createElement('img');tile.alt='';tile.setAttribute('role','presentation');tile.decoding='async';let cancelled=false,cancel;
  if(this._map)targets.add(this._map.getContainer());const update=updateAll;
  cancel=pool.add(this,release=>{if(cancelled){release();return;}const finish=error=>{if(cancelled)return;tile.onload=tile.onerror=null;release();update();done(error,tile);};tile.onload=()=>finish(null);tile.onerror=()=>finish(Error('Tessera non disponibile'));tile.src=this.getTileUrl(coords);update();});
  tile._cancelTile=()=>{if(cancelled)return;cancelled=true;tile.onload=tile.onerror=null;tile.removeAttribute('src');cancel();update();};update();return tile;
 }
});
export function scheduledTiles(url,options){const layer=new Scheduled(url,options);layer.on('tileunload tileabort',e=>e.tile._cancelTile?.());return layer;}
