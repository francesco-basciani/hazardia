/* Display only. Green means a valid bulletin explicitly says no warning. */
export const dpcColors=Object.freeze(['#38a76c','#e5c647','#e58636','#cb4553']);
export function dpcZoneStyle(p,stale){
 const known=!stale&&!p.geometry_warning&&Number.isInteger(p.level)&&p.level>=0&&p.level<=3;
 const color=known?dpcColors[p.level]:'#83909b';
 return {fill:true,color,weight:known&&p.level===0?1:2,opacity:.9,fillColor:color,fillOpacity:!known?.18:p.level===0?.24:.42,dashArray:known?undefined:'4 4'};
}
export function dpcCounts(features){
 const levels=[0,0,0,0];let unknown=0;
 for(const f of features){const p=f.properties;if(p.geometry_warning||!Number.isInteger(p.level)||p.level<0||p.level>3)unknown++;else levels[p.level]++;}
 return {levels,unknown};
}
