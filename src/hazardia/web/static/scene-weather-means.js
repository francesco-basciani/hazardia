/* Display-only spatial estimates, bounded at 384 points. Never changes a model input. */
const landOnly=new Set(['temperature','humidity','pressure','radiation']);
export function sceneWeatherMeans(bounds,keys,scalar,vector,onLand){
 const stats=Object.fromEntries([...new Set(keys)].map(k=>[k,{sum:0,weight:0,eligible:0,covered:0,u:0,v:0}]));
 const entries=Object.entries(stats);
 for(let y=0;y<16;y++)for(let x=0;x<24;x++){
  const lat=bounds.south+(y+.5)*(bounds.north-bounds.south)/16,lon=bounds.west+(x+.5)*(bounds.east-bounds.west)/24,w=Math.cos(lat*Math.PI/180);let land;
  for(const [key,s] of entries){
   if(landOnly.has(key)){if(!onLand)continue;if(land===undefined)land=onLand(lat,lon);if(!land)continue;}
   s.eligible++;const wind=key==='wind'?vector(lat,lon):null,value=key==='wind'?(wind&&wind.every(Number.isFinite)?Math.hypot(...wind):null):scalar(key,lat,lon);
   if(!Number.isFinite(value))continue;s.sum+=value*w;s.weight+=w;s.covered++;if(wind){s.u+=wind[0]*w;s.v+=wind[1]*w;}
  }
 }
 return Object.fromEntries(Object.entries(stats).map(([key,s])=>[key,{value:s.weight?s.sum/s.weight:null,covered:s.covered,eligible:s.eligible,partial:s.covered<s.eligible,landPending:landOnly.has(key)&&!onLand,direction:key==='wind'&&s.weight&&Math.hypot(s.u,s.v)>1e-6?(Math.atan2(-s.u,-s.v)*180/Math.PI+360)%360:null}]));
}
