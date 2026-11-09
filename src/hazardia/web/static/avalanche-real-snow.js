import {verifiedLocalAsset} from './avalanche-gran-sasso.js?v=observations-first-20261031';
async function memoryAsset(p,d){
 const stored=await verifiedLocalAsset(p,d);if(d.encoding!=='gzip')return stored;
 if(!Number.isInteger(d.decoded_bytes)||d.decoded_bytes>8*1024*1024)throw Error('Memoria EO oltre limite');
 const reader=new Blob([stored]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();const chunks=[];let length=0;
 for(;;){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>d.decoded_bytes){await reader.cancel();throw Error('Memoria EO espansa oltre limite');}chunks.push(value);}
 const raw=new Uint8Array(length);let at=0;for(const v of chunks){raw.set(v,at);at+=v.length;}const sha=[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(n=>n.toString(16).padStart(2,'0')).join('');if(length!==d.decoded_bytes||sha!==d.decoded_sha256)throw Error('Integrità memoria EO fallita');return raw.buffer;
}
export function realSnowCell(product,lon,lat,now=Date.now()){
 const [x0,y0,x1,y1]=product.projected_bounds,x=6378137*lon*Math.PI/180,y=6378137*Math.log(Math.tan(Math.PI/4+lat*Math.PI/360)),c=Math.floor((x-x0)/(x1-x0)*product.width),r=Math.floor((y1-y)/(y1-y0)*product.height);
 if(!Number.isFinite(c)||!Number.isFinite(r)||c<0||r<0||c>=product.width||r>=product.height)return {status:'OUTSIDE',snow:null};
 const offset=(r*product.width+c)*2,scl=product.index_view.getUint8(offset),source=product.sources[product.index_view.getUint8(offset+1)-1],age=(now-Date.parse(source?.observed_at))/3600000;
 let remembered=null;const pixel=r*product.width+c;if(product.memory_views){const v=product.memory_views[0],before=product.memory_views[1],code=v.getUint8(pixel*2),last=product.sources[v.getUint8(pixel*2+1)-1],prior=product.sources[before.getUint8(pixel*2+1)-1];remembered={scl:code,source:last,previous_scl:before.getUint8(pixel*2),previous_source:prior,comparison:product.comparison_view.getUint8(pixel)};}
 const recent=Number.isFinite(age)&&age>=0&&age<=24,clear=[4,5,6,11].includes(scl);
 return {pixel,remembered,status:!source?'MISSING':!recent?'STALE':!clear?'UNCLASSIFIED':'OBSERVED',scl,source,snow:recent&&clear?scl===11:null,lastClass:scl===11?'Neve/ghiaccio classificati':[4,5].includes(scl)?'Terreno classificato senza neve rilevata':scl===6?'Acqua':'Nuvole, ombre o dato non classificabile'};
}
// Satellite classification only. Old clear snow remains historical, not imputed today.
export function satelliteSnowMask(p,now=Date.now()){
 const recent=new Uint8Array(256),past=new Uint8Array(256);p.sources.forEach((s,i)=>{const age=(now-Date.parse(s.observed_at))/3600000;recent[i+1]=Number.isFinite(age)&&age>=0&&age<=24;past[i+1]=Number.isFinite(age)&&age>=0;});
 const mask=new Uint8Array(p.width*p.height),memory=p.memory_views?.[0];
 for(let i=0;i<mask.length;i++){const at=i*2,code=p.index_view.getUint8(at),source=p.index_view.getUint8(at+1);
  if(code===11&&recent[source])mask[i]=1;
  else if(!([4,5,6].includes(code)&&past[source])){
   if(memory?.getUint8(at)===11&&past[memory.getUint8(at+1)])mask[i]=2;
   else if(code===11&&past[source])mask[i]=2;
  }
 }
 return mask;
}
export function satelliteSnowPixel(p,pixel,now=Date.now()){
 const latest=p.index_view.getUint8(pixel*2),src=p.sources[p.index_view.getUint8(pixel*2+1)-1],age=(now-Date.parse(src?.observed_at))/3600000;
 if([4,5,6].includes(latest)&&age>=0)return {kind:'NO_SNOW_OBSERVED',source:src};
 if(latest===11&&age>=0&&age<=24)return {kind:'RECENT_SNOW',source:src};
 if(p.memory_views){const v=p.memory_views[0],source=p.sources[v.getUint8(pixel*2+1)-1];if(v.getUint8(pixel*2)===11&&source&&Date.parse(source.observed_at)<=now)return {kind:'HISTORICAL_SNOW',source,latestSource:src};}
 if(latest===11&&age>=0)return {kind:'HISTORICAL_SNOW',source:src};
 return {kind:'UNKNOWN',source:src};
}
export function paintSatelliteSnow(p,first,last,rgba,now=Date.now(),mask=null){
 mask=mask||satelliteSnowMask(p,now);
 for(let r=first;r<Math.min(last,p.height);r++)for(let c=0;c<p.width;c++){const i=r*p.width+c,o=i*4;
  // Boundary follows classified satellite pixels; never clip snow to steep slopes or fill gaps.
  const edge=(c>0&&!mask[i-1])||(c+1<p.width&&!mask[i+1])||(r>0&&!mask[i-p.width])||(r+1<p.height&&!mask[i+p.width]);
  if(mask[i]===1)rgba.set([51,188,255,edge?210:170],o);
  else if(mask[i]===2)rgba.set((r+c)%9<2?[156,220,255,edge?205:190]:[48,157,224,edge?190:145],o);
 }
}
// No resampling: presentation intersection is permitted only on identical native grids.
export function intersectObservedTerrain(p,g,view,now=Date.now()){
 if(!p||!g||p.crs!=='EPSG:3857'||g.crs!==p.crs||p.width!==g.width||p.height!==g.height||!Array.isArray(g.projected_bounds)||!Array.isArray(p.projected_bounds)||g.projected_bounds.length!==4||g.projected_bounds.some((x,i)=>!Number.isFinite(x)||!Number.isFinite(p.projected_bounds[i])||Math.abs(x-p.projected_bounds[i])>1e-6)||view.byteLength!==g.width*g.height*2)return null;
 const mask=satelliteSnowMask(p,now),counts=new Uint32Array(65536),first=new Int32Array(65536).fill(-1);let recent=0,historical=0;
 for(let i=0;i<mask.length;i++)if(mask[i]){const label=view.getUint16(i*2,true);counts[label]++;if(first[label]<0)first[label]=i;if(mask[i]===1)recent++;else historical++;}
 return {mask,counts,first,recent,historical};
}
export function observedPinLocations(items,g,intersection){
 if(!intersection)return [];const labels=new Map(Object.entries(g.labels).map(([label,id])=>[id,Number(label)])),[x0,y0,x1,y1]=g.projected_bounds;
 return items.flatMap(item=>{const pixel=intersection.first[labels.get(item.id)];if(!Number.isInteger(pixel)||pixel<0)return [];
  const c=pixel%g.width,r=Math.floor(pixel/g.width),x=x0+(c+.5)/g.width*(x1-x0),y=y1-(r+.5)/g.height*(y1-y0);
  return [{...item,lon:x/6378137*180/Math.PI,lat:(2*Math.atan(Math.exp(y/6378137))-Math.PI/2)*180/Math.PI,snowEvidence:intersection.mask[pixel]===1?'RECENT':'HISTORICAL'}];
 });
}
export function avalancheForecastFrame(reference,selected){
 const hours=(Date.parse(selected)-Date.parse(reference))/3600000;
 if(!Number.isFinite(hours)||hours<0||hours>72)return null;
 const lead=hours===0?0:Math.ceil(hours/24)*24;return {lead,from:Math.max(0,lead-24),to:lead,selected,interval:lead!==0};
}
async function fetchSourceReview(){
 try{const r=await fetch('/assets/avalanche-source-review/manifest.json',{cache:'no-store'});if(!r.ok)return null;const descriptor=await r.json();const bytes=await verifiedLocalAsset({asset_base:'/assets/avalanche-source-review'},descriptor),review=JSON.parse(new TextDecoder().decode(bytes));return review.schema==='hazardia.avalanche-source-review/1.0'&&Array.isArray(review.sources)?review:null;}catch{return null;}
}
async function fetchLocalHistory(){
 try{const r=await fetch('/assets/avalanche-history/manifest.json',{cache:'no-store'});if(!r.ok)return null;const descriptor=await r.json(),raw=await verifiedLocalAsset({asset_base:'/assets/avalanche-history'},descriptor),h=JSON.parse(new TextDecoder().decode(raw));return h.schema==='hazardia.avalanche.LocalHistoryStatus/1.0.0'&&Array.isArray(h.recent)?h:null;}catch{return null;}
}
async function fetchForecastStatus(){
 try{const r=await fetch('/assets/avalanche-gran-sasso-full/status.json',{cache:'no-store'});return r.ok?await r.json():null;}catch{return null;}
}
export async function fetchRealSnow(previous=null){
 const base='/assets/avalanche-snow-observations',r=await fetch(base+'/manifest.json',{cache:'no-store'});if(!r.ok)throw Error('Osservazioni non disponibili');const m=await r.json();
 if(!/^[a-f0-9]{64}$/.test(m.sha256)||m.file!=='objects/'+m.sha256+'.json'||m.bytes>2*1024*1024)throw Error('Manifest osservazioni non valido');if(previous?.content_sha256===m.sha256){if(!previous.source_review)previous.source_review=await fetchSourceReview();previous.local_history=await fetchLocalHistory();previous.forecast_status=await fetchForecastStatus();return previous;}
 const response=await fetch(base+'/'+m.file,{cache:'no-store'});if(!response.ok)throw Error('Prodotto osservato assente');const bytes=await response.arrayBuffer(),sha=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');if(sha!==m.sha256||bytes.byteLength!==m.bytes)throw Error('Integrità osservazioni fallita');
 const p=JSON.parse(new TextDecoder().decode(bytes));if(p.schema!=='hazardia.snow-observations/2.0'||p.origin!=='OBSERVATIONS_ONLY'||p.crs!=='EPSG:3857')throw Error('Schema osservazioni non valido');p.asset_base=base;p.content_sha256=sha;p.source_review=await fetchSourceReview();p.local_history=await fetchLocalHistory();p.forecast_status=await fetchForecastStatus();
 const index=await verifiedLocalAsset(p,p.raster);if(index.byteLength!==p.width*p.height*2)throw Error('Indice osservato incompleto');p.index_view=new DataView(index);if(p.temporal_memory){p.memory_views=[];for(const d of p.temporal_memory.rasters){const raw=await memoryAsset(p,d);if(raw.byteLength!==p.width*p.height*2)throw Error('Memoria EO incompleta');p.memory_views.push(new DataView(raw));}const raw=await memoryAsset(p,p.temporal_memory.comparison);if(raw.byteLength!==p.width*p.height)throw Error('Confronto EO incompleto');p.comparison_view=new DataView(raw); }p.imagesLoaded={};for(const [key,d]of Object.entries(p.images)){const raw=await verifiedLocalAsset(p,d);p.imagesLoaded[key]=URL.createObjectURL(new Blob([raw],{type:'image/png'}));}if(previous?.imagesLoaded)for(const url of Object.values(previous.imagesLoaded))URL.revokeObjectURL(url);return p;
}
