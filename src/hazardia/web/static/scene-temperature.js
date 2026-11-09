/* Bounded display summary of the available land field; never a solver input. */
export function sceneTemperature(bounds,sample,onLand){
 let sum=0,weight=0,land=0,covered=0;
 for(let row=0;row<16;row++)for(let col=0;col<24;col++){
  const lat=bounds.south+(row+.5)*(bounds.north-bounds.south)/16,lon=bounds.west+(col+.5)*(bounds.east-bounds.west)/24;
  if(!onLand(lat,lon))continue;land++;const value=sample(lat,lon);if(!Number.isFinite(value))continue;
  const w=Math.cos(lat*Math.PI/180);sum+=value*w;weight+=w;covered++;
 }
 return {value:weight?sum/weight:null,land,covered,partial:covered<land};
}
