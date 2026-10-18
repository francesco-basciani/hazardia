// Display interpolation only. Never feed these records to a simulator.
export function interpolateWeather(records,phase){
 if(!phase)return null;
 const a=records?.find(r=>r.at===phase.from),b=records?.find(r=>r.at===phase.to);
 if(!a||!b||Date.parse(b.at)-Date.parse(a.at)!==3600000)return null;
 const t=Math.max(0,Math.min(1,phase.fraction));if(!t)return a;if(t===1)return b;
 const out={at:phase.at,display_interpolation:true,from:a.at,to:b.at};
 for(const key of ['u','v','temperature','humidity','pressure','cloud','precipitation','gusts','radiation']){
  if(!Array.isArray(a[key])||!Array.isArray(b[key])||a[key].length!==b[key].length)continue;
  out[key]=a[key].map((v,i)=>Number.isFinite(v)&&Number.isFinite(b[key][i])?v+(b[key][i]-v)*t:NaN);
 }
 return out;
}

// Resolve the shared absolute scenario time. No nearest-hour substitution across gaps.
export function weatherAt(records,at){
 const target=Date.parse(at);if(!Number.isFinite(target))return null;
 const exact=records?.find(r=>Date.parse(r.at)===target);if(exact)return exact;
 const from=records?.find(r=>Date.parse(r.at)<target&&target-Date.parse(r.at)<3600000);
 const to=records?.find(r=>Date.parse(r.at)>target&&Date.parse(r.at)-target<3600000);
 if(!from||!to)return null;
 return interpolateWeather(records,{from:from.at,to:to.at,fraction:(target-Date.parse(from.at))/3600000,at:new Date(target).toISOString().replace('.000Z','Z')});
}
