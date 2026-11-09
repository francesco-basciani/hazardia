import {paintConditionRows} from './avalanche-overview.js?v=cloud-history-20261104';
import {intersectObservedTerrain,observedPinLocations} from './avalanche-real-snow.js?v=cloud-history-20261104';
import {localMember} from './avalanche-gran-sasso.js?v=cloud-history-20261104';
import {snowDepthValue} from './avalanche-snow-depth.js?v=cloud-history-20261104';
// Presentation of existing native SNOWPACK results; no new mass balance or EO assimilation.
// Codes: 1 recent EO snow; 2 historical EO snow; 3 model/last scene cloud;
// 4 model/other unobservable; 5 insufficient model; 6 model zero, not observed bare;
// 7 recent clear bare/model disagreement. 0 outside or observed bare.
export function buildSnowSupport(product,eo,lead=0,now=Date.now()){
 const g=product.raster_index,observed=eo?intersectObservedTerrain(eo,g,product.index_view,now):null;
 const mask=observed?observed.mask.slice():new Uint8Array(g.width*g.height),evidence=mask.slice(),counts=new Uint32Array(65536),first=new Int32Array(65536).fill(-1),values=new Map();
 const palette=new Uint8Array(65536),sensitive=new Uint8Array(65536),rank=new Uint8Array(65536).fill(255),stats={observed:0,estimated:0,underCloud:0,missing:0,modelZero:0,disagreement:0,initialSensitive:0};
 const reference=Date.parse(product.metadata.reference_utc);
 for(const f of product.features){
  const id=f.properties.profile_id,entries=['NWP_INITIAL','ZERO_INITIAL'].map(k=>localMember(product.models[id],k)),depth=snowDepthValue(product,f,lead,now);
  const historyValid=entries.every(e=>Number.isFinite(e?.history_hours)&&e.history_hours>0&&Number.isFinite(Date.parse(e.history_start))&&Date.parse(e.history_start)<reference);
  const windows=lead?entries.map(e=>e?.result?.forecast_windows?.[String(lead)]?.forecast_hs_max_cm):depth.values;
  const windowValid=windows?.every(v=>Number.isFinite(v)&&v>=0),max=windowValid?Math.max(...windows):depth.max,min=windowValid?Math.min(...windows):depth.min;
  values.set(id,{...depth,missing:depth.missing||!historyValid,historyValid,supportMax:max,supportMin:min,window:lead>0&&windowValid});
 }
 for(const [label,id]of Object.entries(g.labels)){const v=values.get(id);palette[Number(label)]=!v||v.missing?5:v.supportMax>0?4:6;sensitive[Number(label)]=v&&!v.missing&&v.supportMin===0&&v.supportMax>0?1:0;}
 const sourceAge=eo?.sources.map(s=>(now-Date.parse(s.observed_at))/3600000)||[];
 for(let i=0;i<mask.length;i++){
  const label=product.index_view.getUint16(i*2,true);if(!label||label===65535)continue;
  if(mask[i])stats.observed++;
  else{
   const scl=observed?eo.index_view.getUint8(i*2):0,source=observed?eo.index_view.getUint8(i*2+1):0,age=sourceAge[source-1],recent=Number.isFinite(age)&&age>=0&&age<=24;
   const bare=lead===0&&recent&&[4,5,6].includes(scl),kind=palette[label]||5;
   if(bare){if(kind===4){evidence[i]=7;stats.disagreement++;}}
   else if(kind===4){evidence[i]=[3,8,9,10].includes(scl)&&age>=0?3:4;mask[i]=evidence[i];stats.estimated++;if(evidence[i]===3)stats.underCloud++;if(sensitive[label])stats.initialSensitive++;}
   else {evidence[i]=kind;if(kind===5)stats.missing++;else if(kind===6)stats.modelZero++;}
  }
  if(mask[i]){counts[label]++;if(mask[i]<rank[label]){first[label]=i;rank[label]=mask[i];}}
 }
 return {schema:'hazardia.avalanche.snow-support-view/1.0',model_sha256:product.content_sha256||null,observation_sha256:eo?.content_sha256||null,reference_utc:product.metadata.reference_utc,generated_at:new Date(now).toISOString(),mask,evidence,counts,first,values,stats,eoAligned:!!observed,lead};
}
export function supportedSnowPins(items,g,support){
 return observedPinLocations(items,g,support).map(item=>{const label=Object.entries(g.labels).find(([,id])=>id===item.id)?.[0],code=support.mask[support.first[Number(label)]];return {...item,snowEvidence:code===1?'RECENT':code===2?'HISTORICAL':'ESTIMATED',evidenceCode:code};});
}
export function paintEstimatedSnowRows(g,support,first,last,rgba){
 for(let r=first;r<Math.min(last,g.height);r++)for(let c=0;c<g.width;c++){
  const i=r*g.width+c,code=support.evidence[i],o=i*4;
  if(code===3||code===4)rgba.set((r+c)%8<2?[218,239,255,160]:[35,104,196,125],o);
  else if((code===5||code===6||code===7)&&(r-c+g.width)%16===0&&r%4<2)rgba.set([176,185,191,95],o);
 }
}
export function snowSupportCell(product,support,lon,lat){
 if(!support)return null;const g=product.raster_index,[x0,y0,x1,y1]=g.projected_bounds,x=6378137*lon*Math.PI/180,y=6378137*Math.log(Math.tan(Math.PI/4+lat*Math.PI/360)),c=Math.floor((x-x0)/(x1-x0)*g.width),r=Math.floor((y1-y)/(y1-y0)*g.height);
 if(!Number.isFinite(c)||!Number.isFinite(r)||r<0||r>=g.height||c<0||c>=g.width)return null;
 const pixel=r*g.width+c;return {pixel,code:support.evidence[pixel],snow:support.mask[pixel]>0};
}

export function paintSupportedConditionRows(g,palette,support,first,last,rgba){
 paintConditionRows(g,palette,first,last,rgba,support.mask);
 // The gaps reveal the blue estimate below; observed evidence keeps solid color.
 for(let r=first;r<Math.min(last,g.height);r++)for(let c=0;c<g.width;c++){const i=r*g.width+c;if([3,4].includes(support.evidence[i])&&(r+c)%8<3)rgba[i*4+3]=0;}
}
