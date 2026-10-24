import {locale} from "/i18n.js";
/* Explain native outcomes without turning a proxy tie into a protection claim. */
export function propagationStatus(series,hour){
 const frames=series?.frames||[],end=Number(series?.options?.duration_s||0)/3600;
 const frame=frames.filter(f=>f.hour<=hour).at(-1);if(!frame)return '';
 const exhausted=frame.queued_front_events===0,known=Number.isInteger(frame.realizations_with_front),members=series.options?.realizations;
 if(end&&hour>=end)return ' · fine previsione '+end+' h'+(exhausted?' · fronti esauriti':known?' · fronti ancora presenti in '+frame.realizations_with_front+'/'+members+' realizzazioni':' · evoluzione successiva non calcolata');
 return exhausted?' · fronti esauriti':'';
}
export function comparisonVerdict(evaluation){
 const a=evaluation.rows.find(r=>r.case==='A'),b=evaluation.rows.find(r=>r.case==='B');if(!a||!b)return 'Confronto incompleto: nessun beneficio dichiarato.';
 const fmt=(x,d=2)=>Number(x).toLocaleString(locale(),{minimumFractionDigits:d,maximumFractionDigits:d});
 const delta=b.area_ha-a.area_ha,tie=Math.abs(b.native_priority_index-a.native_priority_index)<1e-9;
 const outcome=tie?'Indice sulle priorità invariato; '+(delta<0?'la proposta prevale soltanto per la superficie media minore.':delta>0?'il riferimento prevale per la superficie media minore.':'anche la superficie è invariata.'):(b.native_priority_index<a.native_priority_index?'La proposta riduce l’indice sulle priorità nelle due simulazioni valutate.':'La proposta peggiora l’indice sulle priorità nelle due simulazioni valutate.');
 return outcome+' Indice: '+fmt(a.native_priority_index,3)+' → '+fmt(b.native_priority_index,3)+'. Superficie media simulata: '+fmt(a.area_ha)+' → '+fmt(b.area_ha)+' ha ('+(delta>0?'+':'')+fmt(delta)+' ha). Non è un ottimo fisico globale né efficacia operativa validata.';
}

export function growthReadout(series,hour){
 if(!(hour>0))return '';const frames=series?.frames||[];let i=frames.length-1;while(i>=0&&frames[i].hour>hour+1e-8)i--;if(i<0)return '';
 const f=frames[i],previous=frames[i-1],fmt=x=>Number(x).toLocaleString(locale(),{minimumFractionDigits:2,maximumFractionDigits:2});
 if(!Number.isFinite(f.expected_area_ha))return '';
 const base=' · '+fmt(f.expected_area_ha)+' ha medi · campione +'+Number(f.hour.toFixed(2))+' h';
 if(!previous||!Number.isFinite(previous.expected_area_ha))return base;
 const delta=f.expected_area_ha-previous.expected_area_ha,minutes=Math.round((f.hour-previous.hour)*60);
 return base+' · '+(delta>0?'+':'')+fmt(delta)+' ha / '+minutes+' min';
}
