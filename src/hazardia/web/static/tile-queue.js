/* Fair, bounded admission for visible map images. No prefetch or URL rewriting. */
export function tileQueue(limit=4){
 const queue=[];let active=0,previous=null;const counts={started:0,cancelled:0,peak:0};
 function drain(){while(active<limit&&queue.length){let i=queue.findIndex(t=>t.owner!==previous);if(i<0)i=0;const task=queue.splice(i,1)[0];if(task.cancelled)continue;previous=task.owner;const same=queue.filter(t=>t.owner===task.owner),others=queue.filter(t=>t.owner!==task.owner);queue.splice(0,queue.length,...others,...same);task.started=true;active++;counts.started++;counts.peak=Math.max(counts.peak,active);let ended=false;task.release=()=>{if(ended)return;ended=true;active--;drain();};task.start(task.release);}}
 return {add(owner,start){const task={owner,start,cancelled:false,started:false};queue.push(task);drain();return ()=>{if(task.cancelled)return;task.cancelled=true;counts.cancelled++;if(task.started)task.release();else{const i=queue.indexOf(task);if(i>=0)queue.splice(i,1);}drain();};},status(){return {...counts,active,queued:queue.length,limit};}};
}
