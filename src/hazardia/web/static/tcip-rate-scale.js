// Presentation only: classify existing per-capita rates, never modify observations.
export const RATE_PALETTE=Object.freeze(['#fff3b0','#f9c75a','#ed8a4b','#bc5069','#64265d']);
export const MISSING_RATE_COLOR='#c9cfce';
const valid=value=>typeof value==='number'&&Number.isFinite(value)&&value>=0;
export function createRateScale(input){
 const values=input.filter(valid).slice().sort((a,b)=>a-b),unique=[...new Set(values)];
 const quantile=p=>{const index=(values.length-1)*p,lo=Math.floor(index),fraction=index-lo;return values[lo]*(1-fraction)+values[Math.ceil(index)]*fraction;};
 const target=Math.min(5,unique.length);
 let thresholds=target>1?[...new Set(Array.from({length:target-1},(_,i)=>quantile((i+1)/target)))].filter(x=>x<values.at(-1)):[];
 if(unique.length>1&&!thresholds.length)thresholds=[values[0]];
 const mode=!values.length?'missing':unique.length===1?'single':'quantiles';
 const colors=mode==='quantiles'?Array.from({length:thresholds.length+1},(_,i)=>RATE_PALETTE[Math.round(i*(RATE_PALETTE.length-1)/thresholds.length)]):[RATE_PALETTE[2]];
 const color=value=>!valid(value)?MISSING_RATE_COLOR:mode==='quantiles'?colors[thresholds.filter(cut=>value>cut).length]:colors[0];
 let digits=2;
 while(digits<10&&new Set(thresholds.map(x=>x.toFixed(digits))).size<thresholds.length)digits++;
 const fmt=value=>{const fixed=new Intl.NumberFormat('it-IT',{useGrouping:true,maximumFractionDigits:digits}).format(value);return value!==0&&Number(value.toFixed(digits))===0?value.toExponential(3):fixed;};
 const entries=mode==='missing'?[]:mode==='single'?[{color:colors[0],label:'Valore unico: '+fmt(values[0])}]:colors.map((fill,index)=>({color:fill,label:index===0?'≤ '+fmt(thresholds[0]):index===thresholds.length?'> '+fmt(thresholds.at(-1)):'> '+fmt(thresholds[index-1])+' e ≤ '+fmt(thresholds[index])}));
 entries.push({color:MISSING_RATE_COLOR,label:'Dato non disponibile'});
 const description=mode==='missing'?'Nessun valore disponibile.':mode==='single'?'Un solo valore osservato: nessuna differenza spaziale rappresentabile.':colors.length+' classi relative per quantili sui '+values.length+' poligoni della selezione. Soglie arrotondate in legenda; classificazione sui valori completi.';
 return {method:'selected-area-quantiles-v1',mode,thresholds,colors,entries,validCount:values.length,distinctCount:unique.length,color,description};
}
