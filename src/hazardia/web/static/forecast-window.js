/* Complete source hours only. These are rainfall quantities, not warning levels. */
export const rainColors=['#dceaf3','#acd7ee','#68b3dc','#367faf','#614b99'];
export function forecastWindow(rows,at,hours){
 const start=Math.floor(Date.parse(at)/3600000)*3600000;
 if(!Number.isFinite(start)||![1,3,6,12,24].includes(hours))return {status:'UNAVAILABLE'};
 const lookup=new Map((rows||[]).map(r=>[Date.parse(r.at),r]));let mean=0;
 for(let i=0;i<hours;i++){
  const r=lookup.get(start+i*3600000);
  if(!r||r.status!=='AVAILABLE'||Date.parse(r.until)!==start+(i+1)*3600000||!Number.isFinite(r.mean_mm)||r.mean_mm<0)return {status:'UNAVAILABLE'};
  mean+=r.mean_mm;
 }
 return {status:'AVAILABLE',mean_mm:mean,band:mean<1?0:mean<10?1:mean<30?2:mean<60?3:4};
}
export function usesForecast(mode,at,now=Date.now()){
 return mode==='forecast'||mode==='auto'&&Date.parse(at)>=Math.floor(now/3600000)*3600000+3600000;
}
