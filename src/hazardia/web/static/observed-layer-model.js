/* Display filters only. Never hazard, damage, flight or optimizer criteria. */
export const powerColor=v=>v==null?'#b5c1ca':v>=380000?'#ef637d':v>=220000?'#f6a749':v>=132000?'#f4d76a':'#65d4d1';
export function powerVisible(p,{minVoltage=35000,unknown=false,cables=false,stations=false,towers=false}={}){
 const v=p.max_voltage;
 if(p.power_kind==='substation')return stations&&(v==null||v>=minVoltage);
 if(['tower','pole'].includes(p.power_kind))return towers;
 if(!['line','minor_line','cable'].includes(p.power_kind))return false;
 if(p.location!=='overhead'&&!cables)return false;
 return v==null?unknown:v>=minVoltage;
}
