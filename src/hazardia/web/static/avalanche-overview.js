// Presentation of existing evidence: no new snow estimate or hazard classifier.
export function observationOverview(product,now=Date.now()){
 const sources=product?.sources||[],dates=sources.map(s=>Date.parse(s.observed_at)).filter(Number.isFinite),latest=dates.length?Math.max(...dates):NaN,age=(now-latest)/3600000;
 const recent=Number.isFinite(age)&&age>=0&&age<=24,counts=product?.counts||{};
 const stations=(product?.stations||[]).map(s=>({...s,current:Number.isFinite(s.hs_cm)&&s.hs_cm>=0&&Number.isFinite(Date.parse(s.observed_at))&&now>=Date.parse(s.observed_at)&&now-Date.parse(s.observed_at)<=24*3600000}));
 return {latest:Number.isFinite(latest)?new Date(latest).toISOString():null,classified:recent?(counts.recent_classified_pixels||0):0,snow:recent?(counts.recent_snow_pixels||0):0,unobservable:!recent||!(counts.recent_classified_pixels>0),historicalSnow:product?.temporal_memory?.last_clear_snow_pixels||0,stations,checkedAt:product?.generated_at||null};
}
export function aspectName(degrees){return Number.isFinite(degrees)?['N','NE','E','SE','S','SO','O','NO'][Math.round(((degrees%360)+360)%360/45)%8]:null;}
export function conditionContext(product,feature,assessment){
 const p=feature.properties||{},entries=assessment.entries||[],windows=assessment.windows||[],finite=xs=>xs.filter(Number.isFinite),range=xs=>{const v=finite(xs);return v.length?[Math.min(...v),Math.max(...v)]:null;};
 return {elevation:range([p.elevation_min_m,p.elevation_max_m]),slope:range([p.slope_min_deg,p.slope_max_deg]),aspect:p.profile_aspect_deg,aspectName:aspectName(p.profile_aspect_deg),historyHours:range(entries.map(e=>e.history_hours)),historyStart:entries.map(e=>e.history_start).filter(Boolean).sort()[0]||null,temperature:range(windows.flatMap(w=>[w.air_temperature_min_c,w.air_temperature_max_c])),wind:range(windows.map(w=>w.wind_max_ms)),mechanisms:[...(assessment.load?.some(v=>v>.001)?['Aumento del carico di neve simulato']:[]),...(assessment.water?.some(v=>v>.001)?['Acqua nel manto simulato']:[])],kind:assessment.kind,reason:assessment.reason};
}
export function conditionColor(kind){return {candidate:[255,188,81,180],factors:[255,117,86,195],missing:[154,167,177,48]}[kind]||[0,0,0,0];}
export function paintConditionRows(index,palette,first,last,rgba,mask=null){
 for(let r=first;r<Math.min(last,index.height);r++)for(let c=0;c<index.width;c++){const i=r*index.width+c,label=index.view.getUint16(i*2,true);if(mask&&!mask[i]){rgba.fill(0,i*4,i*4+4);continue;}rgba.set(palette.subarray(label*4,label*4+4),i*4);}
}
export function snowHistoryRows(entry,reference){
 const limit=Date.parse(reference),times=entry?.history_sample_times||[],hs=entry?.history_hs_cm||[],swe=entry?.history_swe_kg_m2||[],groups=new Map(),seen=new Set();let invalid=0,future=0;
 for(let i=0;i<times.length;i++){const at=Date.parse(times[i]);if(!Number.isFinite(at)||seen.has(at)||!Number.isFinite(hs[i])||hs[i]<0||!Number.isFinite(swe[i])||swe[i]<0){invalid++;continue;}if(at>limit){future++;continue;}seen.add(at);const date=new Date(at).toISOString().slice(0,10);if(!groups.has(date))groups.set(date,[]);groups.get(date).push({at,hs:hs[i],swe:swe[i]});}
 return {invalid,future,scope:entry?.history_series_scope||'NOT_DECLARED',days:[...groups.entries()].sort().map(([date,rows])=>{rows.sort((a,b)=>a.at-b.at);const a=rows[0],b=rows[rows.length-1];return {date,first:new Date(a.at).toISOString(),last:new Date(b.at).toISOString(),hsFirst:a.hs,hsLast:b.hs,sweFirst:a.swe,sweLast:b.swe,samples:rows.length};})};
}
