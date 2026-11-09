// Historical descriptive shares only; never a simulator/optimizer input.
export const shareColor=(value,level)=>level==='neighborhood'?(value===null?'#c9cfce':value<.05?'#487862':value<.1?'#96ad68':value<.2?'#e2c761':value<.3?'#db9350':'#b85547'):value===null?'#c9cfce':value<.01?'#487862':value<.03?'#96ad68':value<.06?'#e2c761':value<.10?'#db9350':'#b85547';
const escapeText=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const percent=value=>value===null?'Non disponibile':new Intl.NumberFormat('it-IT',{style:'percent',maximumFractionDigits:2}).format(value);
const number=value=>value===null?'Non disponibile':Number(value).toLocaleString('it-IT');
export const crimeLayers=(items,code)=>items.filter(item=>(item.crime_code||'unclassified')===code);
export const nationalLayer=items=>items.find(item=>item.profile==='tcip.regional-historical-share/1.0') || null;
export function attachTcipLayers({map,entry,refresh}){
 const panel=document.createElement('section');panel.dataset.category='tcip';panel.dataset.revealOnActivate='true';
 const heading=document.createElement('h3');heading.textContent='TCIP · quote storiche (archivio)';
 const visible=document.createElement('input');visible.type='checkbox';visible.setAttribute('aria-label','Mostra TCIP sulla mappa');
 const label=document.createElement('label');label.append(visible,document.createTextNode(' Mostra livello storico'));
 const crime=document.createElement('select');crime.setAttribute('aria-label','Tipo di reato TCIP');
 const crimeLabel=document.createElement('label');crimeLabel.textContent='Tipo di reato';crimeLabel.append(crime);
 const categoryStatus=document.createElement('p');categoryStatus.setAttribute('aria-live','polite');
 const release=document.createElement('select');release.setAttribute('aria-label','Rilascio TCIP');
 const period=document.createElement('select');period.setAttribute('aria-label','Periodo TCIP');
 for(const [value,text] of [['all','Tutto il periodo disponibile'],['last','Ultimi X anni disponibili']]){const option=new Option(text,value);period.append(option);}
 const years=document.createElement('input');years.type='number';years.min='1';years.max='100';years.value='3';years.disabled=true;years.setAttribute('aria-label','Numero di anni TCIP');
 const zone=document.createElement('select');zone.setAttribute('aria-label','Dettaglio zona TCIP');zone.disabled=true;
 const zoneDetail=document.createElement('div');zoneDetail.setAttribute('aria-live','polite');
 const apply=document.createElement('button');apply.type='button';apply.textContent='Applica / aggiorna TCIP';
 const national=document.createElement('button');national.type='button';national.textContent='Italia · quote storiche';
 const fit=document.createElement('button');fit.type='button';fit.textContent='Inquadra il livello TCIP';fit.disabled=true;
 const status=document.createElement('p');status.setAttribute('role','status');status.textContent='Livello disattivato. Servizio TCIP indipendente.';
 const note=document.createElement('p');note.textContent='Percentuale degli episodi nel dataset e nel periodo scelto. Non è una probabilità futura o un rischio personale. Categorie e coperture dipendono dal dataset selezionato: regioni, comuni o quartieri verificati. Gli ultimi X anni terminano all’ultimo anno disponibile, non all’anno corrente.';
 const legend=document.createElement('div');legend.setAttribute('aria-label','Legenda quote TCIP');
 for(const [value,text] of [[0,'<1%'],[.01,'1–3%'],[.03,'3–6%'],[.06,'6–10%'],[.1,'≥10%'],[null,'Non disponibile']]){const line=document.createElement('p'),swatch=document.createElement('span');swatch.style.cssText='display:inline-block;width:1em;height:1em;margin-right:.5em';swatch.style.backgroundColor=shareColor(value);line.append(swatch,document.createTextNode(text));legend.append(line);}
 const attribution=document.createElement('p');attribution.textContent='Dati e confini: provenienza specifica nel dataset selezionato.';
 panel.append(heading,label,national,crimeLabel,release,period,years,apply,fit,categoryStatus,status,zone,zoneDetail,note,legend,attribution);
 let layer=null,controller=null,generation=0,disposed=false,currentData=null,selectedZone='';
 const clear=()=>{categoryStatus.textContent='';note.textContent='';attribution.textContent='';legend.replaceChildren();if(layer){map.removeLayer(layer);layer=null;}fit.disabled=true;zone.disabled=true;zone.replaceChildren();zoneDetail.replaceChildren();currentData=null;};
 const showZone=()=>{zoneDetail.replaceChildren();const f=currentData?.features.find(f=>String(f.id)===selectedZone);if(!f)return;for(const text of [f.properties.source_region+' · '+percent(f.properties.share),number(f.properties.count)+' / '+number(currentData.metadata.denominator)+' episodi del campione',currentData.metadata.years.join(', ')+' · '+(currentData.metadata.periods?.map(p=>p.start+' → '+p.end+(p.partial?' (parziale)':'')).join('; ')||'copertura parziale')]){const row=document.createElement('p');row.textContent=text;zoneDetail.append(row);}};
 zone.onchange=()=>{selectedZone=zone.value;showZone();};
 const read=async(url,signal)=>{const r=await fetch(url,{signal,cache:'no-store'});if(!r.ok)throw Error(r.status===503?'Servizio o autorizzazione TCIP non disponibili':'Richiesta TCIP non disponibile (HTTP '+r.status+')');return r.json();};
 async function load(){
  const current=++generation;controller?.abort();
  if(!visible.checked){clear();status.textContent='Livello disattivato.';return;}
  const amount=period.value==='last'?Number(years.value):null;
  if(amount!==null&&(!Number.isInteger(amount)||amount<1||amount>100)){clear();status.textContent='Indica un numero intero di anni tra1e100.';return;}
  controller=new AbortController();status.textContent='Caricamento TCIP…';
  // The earlier product is withdrawn before revalidation, not left as a silent fallback.
  clear();
  try{
   const catalog=await read('/api/tcip/layers',controller.signal);if(current!==generation||disposed)return;
   const preferred=nationalLayer(catalog.items);
   const previousCrime=crime.value || preferred?.crime_code || '';
   const choices=[...new Map(catalog.items.map(item=>[item.crime_code||'unclassified',item.crime_label||'Categoria non dichiarata'])).entries()];
   crime.replaceChildren();for(const [code,text] of choices)crime.append(new Option(text,code));
   for(const [code,text] of [['robbery','Rapine'],['fraud','Truffe'],['property_damage','Danneggiamenti'],['burglary.residential','Furti in abitazione']])if(!choices.some(([c])=>c===code)){const option=new Option(text+' — dati non pubblicati',code);option.disabled=true;crime.append(option);}
   if(previousCrime&&!choices.some(([code])=>code===previousCrime))throw Error('Categoria precedente non più disponibile: nessun dato mantenuto sulla mappa.');
   if(previousCrime)crime.value=previousCrime;
   const eligible=crimeLayers(catalog.items,crime.value);
   const previous=release.value || (preferred?.crime_code===crime.value ? preferred.release_id : '');release.replaceChildren();
   for(const item of eligible){release.append(new Option(item.title+' · '+item.years.join(', '),item.release_id));}
   if(previous&&!eligible.some(item=>item.release_id===previous))throw Error('Rilascio precedente non più disponibile per la categoria scelta.');
   if(previous)release.value=previous;
   if(!release.value)throw Error('Nessun rilascio TCIP disponibile per questo client.');
   const data=await read('/api/tcip/layers/'+encodeURIComponent(release.value)+(amount===null?'':'?years='+amount),controller.signal);if(current!==generation||disposed||!visible.checked)return;
   if(data.type!=='FeatureCollection'||data.metadata?.probability_kind!=='empirical_location_share_given_recorded_dataset_episode')throw Error('Contratto storico TCIP non riconosciuto.');
   if((data.metadata.crime_code||'unclassified')!==crime.value)throw Error('Categoria del layer diversa da quella selezionata.');
   categoryStatus.textContent='Categoria visualizzata: '+(data.metadata.crime_label||'non dichiarata')+'. '+(data.metadata.is_total?'Totale aggregato di tutti i reati; non è una singola categoria.':'Conteggi e quote riferiti solo a questa categoria.');
   layer=L.geoJSON(data,{bubblingMouseEvents:false,attribution:escapeText(data.geometry_context.attribution),style:f=>({color:'#ebeee9',weight:1.2,fillColor:shareColor(f.properties.share,data.metadata.level),fillOpacity:.48}),onEachFeature:(f,item)=>{
    const detail=document.createElement('div');
    for(const [key,value] of [['Tipo di reato',data.metadata.crime_label||'Categoria non dichiarata'],['Zona',f.properties.source_region],['Quota storica',percent(f.properties.share)],['Episodi nella zona',number(f.properties.count)],['Episodi nel dataset selezionato',number(data.metadata.denominator)],['Anni',data.metadata.years.join(', ')],['Copertura',data.metadata.coverage],['Interpretazione','Distribuzione del dataset, non previsione di un nuovo reato']]){const row=document.createElement('p');row.textContent=key+': '+value;detail.append(row);}
    item.bindPopup(detail);item.bindTooltip(escapeText(data.metadata.level==='neighborhood'?(f.properties.code?.split(':').at(-1)||f.properties.source_region):f.properties.source_region)+' · '+percent(f.properties.share),{permanent:data.metadata.level==='neighborhood',direction:'center'});
    item.on('add',()=>{const element=item.getElement();if(element){element.setAttribute('role','button');element.setAttribute('tabindex','0');element.setAttribute('aria-label','TCIP · '+f.properties.source_region+' · '+percent(f.properties.share));element.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();event.stopPropagation();item.openPopup();}});}});
   }}).addTo(map);
   legend.replaceChildren();for(const [value,text] of (data.metadata.level==='neighborhood'?[[0,'<5%'],[.05,'5–10%'],[.1,'10–20%'],[.2,'20–30%'],[.3,'≥30%'],[null,'Non disponibile']]:[[0,'<1%'],[.01,'1–3%'],[.03,'3–6%'],[.06,'6–10%'],[.1,'≥10%'],[null,'Non disponibile']])){const row=document.createElement('p'),swatch=document.createElement('span');swatch.style.cssText='display:inline-block;width:1em;height:1em;margin-right:.5em';swatch.style.backgroundColor=shareColor(value,data.metadata.level);row.append(swatch,document.createTextNode(text));legend.append(row);}
   attribution.textContent=data.geometry_context.attribution+' · '+data.geometry_context.edition;note.textContent=data.metadata.coverage+' Formula: q(z,T) = N(z,T) / Σ N(z,T). Quote descrittive del dataset, non probabilità future. Il modello log λ = β₀ + Σ βₖXₖ non è ancora validato per una superficie nazionale dettagliata. '+(data.metadata.periods?.map(p=>p.start+' → '+p.end+(p.partial?' (periodo parziale)':'')).join('; ')||'');
   currentData=data;zone.disabled=false;zone.append(new Option('Scegli una zona per i dettagli',''));for(const f of data.features){zone.append(new Option(f.properties.source_region+' · '+percent(f.properties.share),String(f.id)));}zone.value=selectedZone;showZone();
   fit.disabled=false;status.textContent=data.features.length+' zone · '+data.metadata.years.join(', ')+' · '+number(data.metadata.denominator)+' episodi nel campione · verifica '+new Date().toLocaleTimeString('it-IT')+'. Disponibilità ricontrollata ogni60s mentre il livello è attivo.';
  }catch(error){if(current===generation&&error.name!=='AbortError'){clear();status.textContent='TCIP: '+error.message;}}
 }
 national.onclick=()=>{crime.replaceChildren();release.replaceChildren();visible.checked=true;visible.dispatchEvent(new Event('hazardia-state'));load();};
 crime.onchange=()=>{release.replaceChildren();categoryStatus.textContent='';load();};
 visible.onchange=async()=>{const enabled=visible.checked;await load();if(enabled&&visible.checked&&!fit.disabled)fit.onclick();};release.onchange=load;apply.onclick=load;period.onchange=()=>years.disabled=period.value==='all';fit.onclick=()=>{if(layer){const inspector=document.getElementById('console-inspector');const width=inspector&&!inspector.hidden?inspector.getBoundingClientRect().width:0;map.fitBounds(layer.getBounds(),{paddingTopLeft:[25,25],paddingBottomRight:[width+25,40]});}};
 const timer=setInterval(()=>{if(visible.checked&&!document.hidden)load();},60000);
 entry('TCIP · quote storiche (archivio)',panel,'▦',visible);refresh();
 map.on('unload',()=>{disposed=true;clearInterval(timer);++generation;controller?.abort();clear();});
}
