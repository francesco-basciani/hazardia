/* Bounded authoring history. Jobs, outputs and timestamps of results are never stored here. */
export function authoringHistory({limit=50,maxBytes=2*1024*1024}={}){
 let entries=[],index=-1;
 const copy=v=>JSON.parse(JSON.stringify(v));
 const key=s=>JSON.stringify(s.scenarios);
 return {
  record(state){const value=copy(state);if(index>=0&&key(entries[index])===key(value))return false;const bytes=JSON.stringify(value).length*2;if(bytes>maxBytes){entries=[];index=-1;return false;}entries=entries.slice(0,index+1);entries.push(value);index=entries.length-1;while(entries.length>limit||entries.reduce((n,e)=>n+JSON.stringify(e).length*2,0)>maxBytes){entries.shift();index--;}return true;},
  undo(){if(index<=0)return null;return copy(entries[--index]);},
  redo(){if(index>=entries.length-1)return null;return copy(entries[++index]);},
  get canUndo(){return index>0;},get canRedo(){return index>=0&&index<entries.length-1;},get size(){return entries.length;},get ids(){return new Set(entries.flatMap(e=>e.scenarios.map(s=>s.id)));}
 };
}
