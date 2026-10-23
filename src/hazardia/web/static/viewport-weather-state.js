/* Acquisition policy only; never extrapolate data beyond the returned field. */
export function viewportWeatherState(snapshot,bounds,{now=Date.now(),nextRequestAt=0}={}){
 const f=snapshot?.forecast;
 const contains=!!f&&bounds.every((p,i)=>p.every((v,j)=>i?v<=f.bounds[1][j]:v>=f.bounds[0][j]));
 const adequate=!!f&&[0,1].every(j=>f.bounds[1][j]-f.bounds[0][j]<=4*Math.max(.8,(bounds[1][j]-bounds[0][j])*1.3));
 const complete=!!f&&['u','v','temperature','precipitation','humidity','pressure','cloud','gusts','radiation','rain_probability'].every(k=>Array.isArray(f.records?.[0]?.[k]));
 const needed=!contains||!adequate||!complete||snapshot?.status!=='FRESH';
 if(!needed)return{kind:'ready',contains,adequate,complete,delayMs:0};
 if(snapshot?.fetching)return{kind:'poll',contains,adequate,complete,delayMs:1200};
 const delayMs=Math.max(0,nextRequestAt-now,Number(snapshot?.retry_after_s||0)*1000);
 return{kind:delayMs?'wait':'fetch',contains,adequate,complete,delayMs:Math.max(1200,delayMs)};
}
export function retainCoveredForecast(snapshot,previous,bounds,now=Date.now()){
 const usable=f=>{if(!f)return false;const age=now-Date.parse(f.available_at);return age>=0&&age<10800000&&bounds.every((p,i)=>p.every((v,j)=>i?v<=f.bounds[1][j]:v>=f.bounds[0][j]));};
 if(usable(snapshot?.forecast)||!usable(previous))return snapshot;
 return{...snapshot,forecast:previous,status:'FRESH',age_s:(now-Date.parse(previous.available_at))/1000,error:snapshot.error,retained_previous:true};
}
