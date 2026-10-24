/* Display filters only. Never hazard, damage, flight or optimizer criteria. */
export const powerColor=v=>v==null?'#b5c1ca':v>=380000?'#ef637d':v>=220000?'#f6a749':v>=132000?'#f4d76a':'#65d4d1';
export function powerVisible(p,{minVoltage=35000,unknown=false,cables=false,stations=false,towers=false,aerial=false}={}){
 if(aerial)return ['tower','pole'].includes(p.power_kind)||(['line','minor_line','cable'].includes(p.power_kind)&&p.location==='overhead');
 const v=p.max_voltage;
 if(p.power_kind==='substation')return stations&&(v==null||v>=minVoltage);
 if(['tower','pole'].includes(p.power_kind))return towers;
 if(!['line','minor_line','cable'].includes(p.power_kind))return false;
 if(p.location!=='overhead'&&!cables)return false;
 return v==null?unknown:v>=minVoltage;
}

export const quakeClasses=[{min:-Infinity,label:'M < 1',color:'#75d5dd'},{min:1,label:'1 ≤ M < 2',color:'#48bca0'},{min:2,label:'2 ≤ M < 3',color:'#f1d25c'},{min:3,label:'3 ≤ M < 4',color:'#f39a48'},{min:4,label:'4 ≤ M < 5',color:'#ed605c'},{min:5,label:'M ≥ 5',color:'#c97ccf'}];
export function quakeStyle(m){if(!Number.isFinite(m))return {radius:3,color:'#e8edf1',fillColor:'#8897a3',fillOpacity:.6,weight:1.2};const band=quakeClasses.filter(c=>m>=c.min).at(-1);return {radius:3+2*Math.max(0,Math.min(9,m)),color:'#f2f6fa',fillColor:band.color,fillOpacity:.65,weight:1.2};}
