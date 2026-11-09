import {locale,getLanguage} from "/i18n.js";
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

// Authored interventions remain visible in both plan and comparison modes.
export function interventionReadout(resources=[],hour=0){
 if(!resources.length)return ' · senza squadre';
 const known=resources.filter(u=>Number.isFinite(u.at_minutes)),active=known.filter(u=>u.at_minutes<=hour*60).length,pending=known.length-active,unknown=resources.length-known.length;
 return ' · interventi: '+resources.length+' · attivi: '+active+' · futuri: '+pending+(unknown?' · orario da verificare: '+unknown:'');
}

export function interventionTiming(series,minutes,hour){
 if(!Number.isFinite(minutes))return 'Orario dell’intervento non disponibile.';
 const prior=series?.frames?.filter(f=>(f.elapsed_s??f.hour*3600)<minutes*60).at(-1),start='Attivazione: +'+Math.floor(minutes/60)+' h '+Number((minutes%60).toFixed(2)).toLocaleString(locale())+' min.';
 return (hour*60<minutes?'Non ancora attivo. ':'')+start+(prior?.queued_front_events===0?' Nel risultato calcolato i fronti risultavano già esauriti prima dell’intervento.':'');
}

// Input receipt proves rasterization, never extinction or saved area. Older results stay explicit.
export function interventionReceipt(series,unit){
 const event=series?.consumed_events?.find(e=>e.time===Math.floor(unit.at_minutes*60));
 const receipt=event?.resource_receipts?.find(r=>r.resource_id===unit.id);
 if(!receipt)return '';
 const en=getLanguage()==='en';
 if(!receipt.affected_cells)return en?'No simulation grid cells are affected by this intervention.':'Intervento senza celle interessate nella griglia del modello.';
 const footprint=en?'Engine received this intervention: '+receipt.affected_cells+' affected cells ('+receipt.initial_fuel_cells+' with initial fuel).':'Intervento ricevuto dal motore: '+receipt.affected_cells+' celle interessate ('+receipt.initial_fuel_cells+' con combustibile iniziale).';
 if(en)return footprint+(receipt.initial_fuel_cells===0?' No initial fuel within the footprint: check your line or area.':'')+' This receipt verifies inputs; it does not by itself demonstrate an effect on the fire front.';
 return footprint+(receipt.initial_fuel_cells===0?' Nessun combustibile iniziale nell’impronta: verifica dove hai disegnato la linea o l’area.':'')+' Questa ricevuta verifica gli input; non dimostra da sola un effetto sul fronte.';
}

export function lateInterventionReadout(series,resources=[]){
 if(!series?.frames?.length)return '';
 const late=resources.filter(u=>Number.isFinite(u.at_minutes)&&series.frames.filter(f=>(f.elapsed_s??f.hour*3600)<u.at_minutes*60).at(-1)?.queued_front_events===0);
 return late.length?(getLanguage()==='en'?' · '+late.length+(late.length===1?' late intervention':' late interventions')+': simulated fronts already exhausted':' · '+late.length+(late.length===1?' intervento tardivo':' interventi tardivi')+': fronti simulati già esauriti'):'';
}
