// Private aggregate rates normalized by resident population; never a personal probability.
export const rateColor=v=>v==null?'#c9cfce':v<.5?'#487862':v<.8?'#96ad68':v<1.2?'#e2c761':v<1.5?'#db9350':'#b85547';
const number=v=>v==null?'Non disponibile':new Intl.NumberFormat('it-IT',{maximumFractionDigits:2}).format(v);
export function attachPopulationRates({map,entry,refresh}){
 const panel=document.createElement('section');panel.dataset.category='tcip';panel.dataset.revealOnActivate='true';
 const title=document.createElement('h3');title.textContent='TCIP · incidenza per abitante';
 const toggle=document.createElement('input');toggle.type='checkbox';toggle.setAttribute('aria-label','Mostra TCIP per abitante');
 const label=document.createElement('label');label.append(toggle,document.createTextNode(' Mostra tassi per 100.000 residenti'));
 const crime=document.createElement('select');crime.setAttribute('aria-label','Reato dei tassi TCIP');for(const [v,t] of [['theft','Furti'],['robbery','Rapine']])crime.append(new Option(t,v));
 const period=document.createElement('select');period.setAttribute('aria-label','Periodo dei tassi TCIP');for(const [v,t] of [['2023','2023 · anno completo'],['2024-H1','2024 · primo semestre (provvisorio)']])period.append(new Option(t,v));
 const fit=document.createElement('button');fit.type='button';fit.textContent='Inquadra incidenza Italia';fit.disabled=true;
 const update=document.createElement('button');update.type='button';update.textContent='Aggiorna tassi TCIP';
 const status=document.createElement('p');status.setAttribute('role','status');status.textContent='Livello disattivato.';
 const note=document.createElement('p');note.textContent='R = reati registrati / residenti × 100.000. Valori già normalizzati dalla fonte; nessuna popolazione ricostruita dai tassi arrotondati. Dettaglio regionale: nessun valore interpolato a comuni/quartieri, nessuna probabilità individuale. Semestre non annualizzato e non sommato all’anno completo.';
 const legend=document.createElement('div');legend.setAttribute('aria-label','Legenda incidenza rispetto a Italia');
 for(const [v,t] of [[.2,'<0,5 × Italia'],[.6,'0,5–0,8 ×'],[1,'0,8–1,2 ×'],[1.3,'1,2–1,5 ×'],[2,'≥1,5 ×'],[null,'Non disponibile']]){const p=document.createElement('p'),i=document.createElement('span');i.style.cssText='display:inline-block;width:1em;height:1em;margin-right:.5em';i.style.backgroundColor=rateColor(v);p.append(i,document.createTextNode(t));legend.append(p);}
 panel.append(title,label,crime,period,update,fit,status,note,legend);
 let layer=null,controller=null,generation=0,disposed=false;
 const clear=()=>{if(layer){map.removeLayer(layer);layer=null;}fit.disabled=true;};
 async function load(){const id=++generation;controller?.abort();clear();if(!toggle.checked){status.textContent='Livello disattivato.';return;}
  controller=new AbortController();status.textContent='Caricamento tassi per abitante…';
  try{const response=await fetch('/api/tcip/population-rates?crime='+crime.value+'&period='+period.value,{cache:'no-store',signal:controller.signal});const data=await response.json();if(id!==generation||disposed||!toggle.checked)return;if(!response.ok)throw Error(data.detail||'Tassi TCIP non disponibili');
   if(data.profile!=='tcip.population-rates/1.0'||data.metadata?.population_normalized!==true)throw Error('Contratto tassi TCIP non valido');
   const m=data.metadata;
   layer=L.geoJSON(data,{style:f=>({color:'#fff',weight:1.5,fillOpacity:.72,fillColor:rateColor(f.properties.relative_to_national)}),onEachFeature:(f,l)=>{const p=f.properties,box=document.createElement('div');for(const t of [p.name,number(p.rate_per_100000)+' per 100.000 residenti',m.crime_label+' · '+m.period_start+' → '+m.period_end,number(p.relative_to_national)+' × tasso Italia','Tasso osservato pubblicato, non probabilità personale']){const line=document.createElement('p');line.textContent=t;box.append(line);}l.bindPopup(box);}}).addTo(map);
   status.textContent='20 regioni · '+m.crime_label+' · '+m.period_start+' → '+m.period_end+(m.partial_period?' · SEMESTRE NON ANNUALIZZATO · non consolidato':'')+'. Italia: '+number(m.national_rate_per_100000)+' reati per 100.000 residenti. Colore: rapporto con il tasso nazionale, Italia=1. Fonte: Ministero Interno / Rapporto OSSIF-ABI2024, dati SDI. Verifica disponibilità ogni60s.';fit.disabled=false;
  }catch(e){if(id===generation&&e.name!=='AbortError'){clear();status.textContent=e.message;}}}
 toggle.onchange=async()=>{const enabled=toggle.checked;await load();if(enabled&&toggle.checked&&!fit.disabled)fit.onclick();};crime.onchange=load;period.onchange=load;update.onclick=load;
 fit.onclick=()=>{if(layer){const inspector=document.getElementById('console-inspector');const width=inspector&&!inspector.hidden?inspector.getBoundingClientRect().width:0;map.fitBounds(layer.getBounds(),{paddingTopLeft:[25,25],paddingBottomRight:[width+25,35]});}};
 const timer=setInterval(()=>{if(toggle.checked&&!document.hidden)load();},60000);
 entry('TCIP · incidenza per abitante',panel,'▦',toggle);refresh();
 map.on('unload',()=>{disposed=true;clearInterval(timer);controller?.abort();clear();});
}
