/* Source-native danger and official warnings, kept distinct from simulations. */
const $=id=>document.getElementById(id),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels=['Bassa','Moderata','Alta','Molto alta','Estrema','Molto estrema'],fireColors=['#79a880','#e7d351','#eb983c','#df5a32','#bd3445','#823e86'],floodColors=['#8caaa0','#e5c647','#e58636','#cb4553'];
const local=v=>v?new Date(v).toLocaleString('it-IT',{timeZone:'Europe/Rome',dateStyle:'short',timeStyle:'short'})+' Roma':'Non comunicata dalla fonte';
export function territorialAttention(map){
 map.createPane('attentionFire');map.getPane('attentionFire').style.zIndex=390;
 map.createPane('attentionFlood');map.getPane('attentionFlood').style.zIndex=380;
 const panel=$('attention-heading').closest('.attention-panel'),toggle=document.createElement('button');toggle.type='button';toggle.id='attention-open';toggle.className='small-button';toggle.textContent='Attenzione territoriale';toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls','attention-panel');panel.id='attention-panel';panel.hidden=true;
 const control=L.control({position:'topright'});control.onAdd=()=>panel;control.addTo(map);L.DomEvent.disableClickPropagation(panel);L.DomEvent.disableScrollPropagation(panel);
 const close=document.createElement('button');close.type='button';close.className='small-button attention-close';close.textContent='Chiudi';close.setAttribute('aria-label','Chiudi attenzione territoriale');panel.prepend(close);
 function open(on){panel.hidden=!on;toggle.setAttribute('aria-expanded',String(on));}
 toggle.onclick=()=>open(panel.hidden);close.onclick=()=>{open(false);toggle.focus();};document.querySelector('.monitor-map-toolbar').append(toggle);
 let snapshot=null,selected=null,generation=0,visible=true,loaded={},pending={},poll,renderedKey='',weather=null;
 const layers={effis:L.layerGroup().addTo(map),dpc:L.layerGroup().addTo(map)};
 map.attributionControl.addAttribution('© European Union · EFFIS/Copernicus EMS · DPC · CC BY4.0');
 function fresh(p){return p.freshness==='FRESH'&&Date.now()<Date.parse(p.valid_until)&&Date.now()-Date.parse(snapshot.acquired_at)<snapshot.refresh_s*1000;}
 function products(key){return snapshot?.sources[key]?.products||[];}
 function product(key){return products(key).find(p=>p.day===$('attention-day').value);}
 function select(feature,kind,point){selected={feature,kind,point};open(true);inspect();}
 function examine(point){for(const key of ['effis','dpc']){const prod=product(key),enabled=$(key==='effis'?'monitor-fire':'monitor-flood').checked;if(!prod||!enabled||!$('attention-enabled').checked)continue;const feature=loaded[prod.url]?.features.find(f=>contains(f.geometry,point));if(feature){select(feature,key,point);return;}}open(true);$('attention-detail').open=true;$('attention-inspector').textContent='Nessuna fonte territoriale disponibile in questa posizione per il giorno selezionato. Non equivale a basso rischio.';}
 map.on('click',e=>examine(e.latlng));
 const inspectCenter=document.createElement('button');inspectCenter.id='attention-inspect-center';inspectCenter.type='button';inspectCenter.className='small-button';inspectCenter.textContent='Esamina il centro della mappa';inspectCenter.onclick=()=>examine(map.getCenter());$('attention-detail').before(inspectCenter);const fitCoverage=document.createElement('button');fitCoverage.type='button';fitCoverage.id='attention-fit';fitCoverage.className='small-button';fitCoverage.textContent='Inquadra copertura delle fonti';fitCoverage.onclick=()=>{const b=snapshot?.sources.effis?.bounds;if(b){open(false);map.fitBounds([[b[1],b[0]],[b[3],b[2]]],{padding:[20,20],animate:false});}};inspectCenter.after(fitCoverage);
 function contains(geometry,point){
  const inside=ring=>{let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const [x,y]=ring[i],[a,b]=ring[j];if(((y>point.lat)!==(b>point.lat))&&point.lng<(a-x)*(point.lat-y)/(b-y)+x)yes=!yes;}return yes;};
  const polys=geometry.type==='Polygon'?[geometry.coordinates]:geometry.coordinates;
  return polys.some(poly=>inside(poly[0])&&!poly.slice(1).some(inside));
 }
 function inspect(){
  if(!selected)return;const {feature:f,kind}=selected,p=f.properties,source=snapshot.sources[kind],prod=product(kind),stale=!prod||!fresh(prod),part=kind==='effis';
  let html='<div class="attention-evidence-title">'+esc(part?(p.name||'Condizioni favorevoli al fuoco'):p.name)+'</div><p class="attention-origin">'+esc(part?'PREVISIONE EFFIS · non è un incendio rilevato':'BOLLETTINO UFFICIALE DPC')+'</p>';
  if(stale)html+='<p class="attention-warning">Dati scaduti o copertura non verificata. Nessuna valutazione attuale.</p>';
  if(part){html+='<dl><dt>Pericolosità incendio · FWI</dt><dd>'+esc(p.fwi??'Non disponibile')+' · '+esc(p.level===null?'Non classificabile':labels[p.level])+'</dd><dt>Secchezza del combustibile profondo · DC</dt><dd>'+esc(p.dc??'Non disponibile')+' · '+esc(p.dc_level===null?'Non classificabile':labels[p.dc_level])+'</dd></dl><p>Indici meteorologici EFFIS: non misurano un innesco, il combustibile locale o l’efficacia delle squadre. Modello circa 10 km. Sintesi sulle zone meteo-idro DPC: massimo dei campioni EFFIS nella zona, non allerta incendio ufficiale. La zona non è un perimetro d’incendio.</p>';}
  else{if(p.geometry_warning)html+='<p class="attention-warning">Geometria della fonte non valida: classificazione cartografica sospesa su questa zona. Il testo ufficiale è riportato sotto.</p>';html+='<dl>'+Object.entries(p.reasons).map(([k,v])=>'<dt>'+esc(k)+'</dt><dd>'+esc(v||'Non disponibile')+'</dd>').join('')+'</dl><details><summary>Comuni della zona · '+p.municipalities.length+'</summary><p>'+p.municipalities.map(esc).join(', ')+'</p></details><p>È una valutazione per zona: non rappresenta il perimetro di un allagamento.</p>';}
  if(part&&p.spatial_support)html+='<dl><dt>Sintesi FWI nella zona</dt><dd>Min '+esc(p.fwi_min??'—')+' · media '+esc(p.fwi_mean??'—')+' · max '+esc(p.fwi??'—')+'</dd><dt>Campioni validi FWI / presenti</dt><dd>'+esc(p.fwi_samples)+' / '+esc(p.sample_count)+'</dd></dl><p>'+esc(p.geometry_warning||p.coverage_warning||'I campioni mancanti non sono interpretati come basso rischio. Il massimo non indica condizioni uniformi in tutta la zona.')+'</p>';
  html+='<dl><dt>Giorno del prodotto</dt><dd>'+esc(prod?.day)+'</dd><dt>Emissione</dt><dd>'+esc(local(source.issued_at))+'</dd><dt>Acquisizione nella VM</dt><dd>'+esc(local(snapshot.acquired_at))+'</dd><dt>Snapshot riproducibile</dt><dd>'+esc(snapshot.id)+'</dd></dl>';
  const location=selected.point,other=part?'dpc':'effis',otherProduct=product(other),otherFeature=location&&otherProduct&&loaded[otherProduct.url]?.features.find(f=>contains(f.geometry,location));
  if(otherFeature){const o=otherFeature.properties;html+='<h4>Altre evidenze nella stessa posizione</h4>';
   if(part)html+='<p>DPC · '+esc(o.name)+' · '+esc(fresh(otherProduct)?'bollettino aggiornato':'dati scaduti')+'</p><dl>'+Object.entries(o.reasons).map(([k,v])=>'<dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd>').join('')+'</dl>'+(o.geometry_warning?'<p>Geometria DPC non verificata: appartenenza da confermare.</p>':'');
   else html+='<p>EFFIS · FWI '+esc(o.fwi??'non disponibile')+'; DC '+esc(o.dc??'non disponibile')+' · '+esc(fresh(otherProduct)?'previsione aggiornata':'dati scaduti')+'</p>';
  }else html+='<p>Altra fonte nella posizione: non disponibile o copertura non verificata.</p>';
  const field=weather?.forecast,point=selected.point;
  if(field&&point&&point.lat>=field.bounds[0][0]&&point.lat<=field.bounds[1][0]&&point.lng>=field.bounds[0][1]&&point.lng<=field.bounds[1][1]){
   const nearest=(array,value)=>array.reduce((best,n,i)=>Math.abs(n-value)<Math.abs(array[best]-value)?i:best,0),yi=nearest(field.lats,point.lat),xi=nearest(field.lons,point.lng),index=yi*field.lons.length+xi,day=$('attention-day').value,records=field.records.filter(r=>r.at.startsWith(day)),r=records.find(r=>r.at.includes('T12:'))||records[0],fmt=n=>Number(n).toLocaleString('it-IT',{maximumFractionDigits:1});
   const stale=Date.now()-Date.parse(field.available_at)>=10800000||weather.status!=='FRESH';
   if(r){const rain=records.length===24?records.reduce((sum,h)=>sum+h.precipitation[index],0):null;
    html+='<h4>Contesto meteo della posizione</h4><p>'+esc(field.model)+' · campione più vicino '+field.lats[yi].toFixed(2)+', '+field.lons[xi].toFixed(2)+'. '+(stale?'CACHE SCADUTA · ':'')+esc(local(r.at))+'</p><dl><dt>Temperatura a 2 m</dt><dd>'+fmt(r.temperature[index])+' °C</dd><dt>Vento a 10 m</dt><dd>'+fmt(Math.hypot(r.u[index],r.v[index]))+' m/s</dd><dt>Precipitazione prevista nel giorno UTC</dt><dd>'+(rain===null?'Intervallo incompleto: accumulo non disponibile':fmt(rain)+' mm · 24 ore complete')+'</dd><dt>Umidità relativa aria</dt><dd>'+(r.humidity?fmt(r.humidity[index])+' %':'Non disponibile in questo snapshot')+'</dd><dt>Raffiche</dt><dd>'+(r.gusts?fmt(r.gusts[index])+' m/s':'Non disponibili')+'</dd></dl><p>Contesto da modello distinto: non modifica il bollettino DPC o gli indici EFFIS e non dimostra un allagamento.</p>';
   }else html+='<p>Meteo locale: giorno non coperto.</p>';
  }else html+='<p>Meteo della posizione: campo non disponibile o fuori copertura.</p>';
  html+='<p class="attention-warning">Valutazione d’impatto locale non disponibile: mancano suolo e vulnerabilità qualificati, radar/idrometri e osservazioni satellitari live.</p><a href="'+esc(source.source_url)+'" target="_blank" rel="noreferrer">Fonte e metodologia ↗</a>';
  $('attention-inspector').innerHTML=html;$('attention-detail').open=true;
 }
 function draw(){
  generation++;const current=generation;for(const l of Object.values(layers))l.clearLayers();
  const kind=$('attention-fire-field').value,showLow=$('attention-low').checked;
  for(const key of ['effis','dpc']){
   const p=product(key);if(!visible||!p||!$('attention-enabled').checked||!$(key==='effis'?'monitor-fire':'monitor-flood').checked||!loaded[p.url])continue;
   const stale=!fresh(p),geo=loaded[p.url];
   L.geoJSON(geo,{pane:key==='effis'?'attentionFire':'attentionFlood',filter:f=>{if(key==='dpc')return true;const level=f.properties[kind==='dc'?'dc_level':'level'];return L.geoJSON(f).getBounds().intersects(map.getBounds().pad(.15))&&(showLow||level===null||level>=1);},style:f=>{const level=f.properties[key==='effis'&&kind==='dc'?'dc_level':'level'],unknown=level===null;return {color:stale||unknown?'#6c7d8b':key==='effis'?fireColors[level]:floodColors[level],weight:1.3,opacity:.8,fillColor:stale||unknown?'#83909b':key==='effis'?fireColors[level]:floodColors[level],fillOpacity:key==='effis'?.32:level===0?.025:.28,dashArray:stale||unknown?'4 4':undefined};},onEachFeature:(f,l)=>{const p=f.properties,level=p[key==='effis'&&kind==='dc'?'dc_level':'level'];l.bindTooltip(esc(key==='effis'?(p.name?p.name+' · ':'')+(kind==='dc'?'Secchezza DC':'Pericolosità FWI')+' · '+(level===null?'Dati mancanti':labels[level]):p.name+' · '+(level===null?'Non classificata':['Nessuna allerta nel bollettino','Gialla','Arancione','Rossa'][level])));l.on('click',e=>select(f,key,e.latlng));}}).addTo(layers[key]);
  }
  const parts=['effis','dpc'].map(key=>{const p=product(key),source=snapshot?.sources[key];return (key==='effis'?'Incendio':'Meteo-idro')+': '+(!p?'dati non disponibili':!loaded[p.url]?'livello in caricamento o non disponibile':fresh(p)?'fonte aggiornata':'dati scaduti')+(source?.status==='PARTIAL'?' · copertura parziale':'');});
  $('attention-map-status').textContent=parts.join(' · ');$('attention-map-status').hidden=!$('attention-enabled').checked;
  $('monitor-map').dataset.attention=$('attention-enabled').checked?['effis','dpc'].filter(k=>product(k)&&loaded[product(k).url]&&$(k==='effis'?'monitor-fire':'monitor-flood').checked).join(','):'';
  $('attention-legend').innerHTML='<span>EFFIS per zona · massimo FWI/DC</span>'+labels.map((n,i)=>'<span><i style="background:'+fireColors[i]+'"></i>'+n+'</span>').join('')+'<span>DPC</span>'+['Nessuna allerta nel bollettino','Gialla','Arancione','Rossa'].map((n,i)=>'<span><i style="background:'+floodColors[i]+'"></i>'+n+'</span>').join('')+'<span><i style="background:#83909b"></i>Mancante / scaduto</span>';
  if(selected&&current===generation)inspect();
 }
 async function render(){
  const days=[...new Set(['effis','dpc'].flatMap(k=>products(k).map(p=>p.day)))].sort(),old=$('attention-day').value;
  $('attention-day').innerHTML=days.map(d=>'<option value="'+esc(d)+'">'+esc(new Date(d+'T12:00:00Z').toLocaleDateString('it-IT',{weekday:'short',day:'numeric',month:'long'}))+'</option>').join('');
  if(days.includes(old))$('attention-day').value=old;$('attention-day').disabled=!days.length;
  const reports=['effis','dpc'].map(key=>{const s=snapshot.sources[key];return '<div class="attention-source"><strong>'+esc(key==='effis'?'EFFIS · incendio e secchezza':'DPC · criticità meteo-idro')+'</strong><span>'+esc(s?.status==='AVAILABLE'?'Disponibile':s?.status==='PARTIAL'?'Parziale':'Non disponibile')+'</span><small>'+esc(s?.error||s?.errors?.map(e=>e.day+': '+e.error).join('; ')||s?.name||'Previsione Météo-France · circa 10 km')+'</small></div>';}).join('');
  $('attention-sources').innerHTML=reports;
  $('attention-state').textContent=(snapshot.fetching?'Aggiornamento in corso… · ':'')+(snapshot.status==='STALE'?'Cache scaduta · ':'')+'Copertura parziale · rischio d’impatto locale non stimato. Acquisito '+local(snapshot.acquired_at)+'. Copertura iniziale Italia; fuori copertura: non disponibile.';
  $('attention-clock').textContent=snapshot.clock_status==='HTTPS_REFERENCE_VM_SKEW'?'Orologio VM disallineato: date controllate con il riferimento HTTPS delle fonti.':'Riferimento temporale: '+snapshot.clock_status;
  const jobs=days.flatMap(day=>['effis','dpc'].map(key=>products(key).find(p=>p.day===day))).filter(Boolean).filter(p=>p.day===$('attention-day').value&&!loaded[p.url]).map(p=>{if(!pending[p.url])pending[p.url]=(async()=>{try{const r=await fetch(p.url);if(!r.ok)throw Error('HTTP '+r.status);loaded[p.url]=await r.json();}catch(e){$('attention-state').textContent+=' Livello non disponibile: '+e.message;}finally{delete pending[p.url];}})();return pending[p.url];});
  draw();await Promise.all(jobs);draw();$('monitor-map').dataset.attentionReady=String(['effis','dpc'].filter(k=>product(k)).every(k=>loaded[product(k).url]));
 }
 async function update(){try{const r=await fetch('/api/monitoring');if(!r.ok)throw Error('HTTP '+r.status);const value=await r.json();if(snapshot?.id!==value.id)loaded={};snapshot=value;const key=JSON.stringify([value.id,value.status,value.fetching,value.error]);if(key!==renderedKey){renderedKey=key;await render();}else draw();}catch(e){for(const l of Object.values(layers))l.clearLayers();$('attention-state').textContent='Monitoraggio territoriale non disponibile: '+e.message+'. Nessuna indicazione di sicurezza.';$('attention-map-status').textContent='Fonti di attenzione non disponibili';}}
 async function refresh(){try{await fetch('/api/monitoring/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:'{}'});await update();}catch(e){$('attention-state').textContent='Aggiornamento non disponibile; nessuna indicazione di sicurezza.';}}
 for(const id of ['attention-enabled','attention-fire-field','attention-day','attention-low','monitor-fire','monitor-flood'])$(id).addEventListener('change',()=>{selected=null;if(id==='attention-day')render();else draw();});
 $('attention-refresh').onclick=refresh;$('attention-day').addEventListener('change',()=>{$('attention-inspector').textContent='Seleziona una zona o una cella sulla mappa per vedere motivi, valori e fonti.';});
 fetch('/api/weather/map').then(r=>r.json()).then(v=>weather=v).catch(()=>{});
 let moveTimer;map.on('moveend zoomend',()=>{clearTimeout(moveTimer);moveTimer=setTimeout(draw,80);});
 update().then(refresh);poll=setInterval(()=>{if(visible)update().then(()=>{if(snapshot?.retry_after_s===0)refresh();});},10000);
 return {visible(on){visible=on;if(on)update();else for(const l of Object.values(layers))l.clearLayers();},draw};
}
