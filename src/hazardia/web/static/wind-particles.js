import {viewportWeatherState,retainCoveredForecast} from '/viewport-weather-state.js';
import {interpolateWeather} from '/weather-interpolation.js';
import {forecastPlayback} from '/forecast-playback.js';
import {sampleVector,sampleScalar,screenSamplePlan,plannedScalar} from '/weather-sampling.js';
export {sampleVector,sampleScalar} from '/weather-sampling.js';
import {paintRain,weatherLabels,labelSurface,positionLabels,windGain,rainLegend,rainClasses,weatherViews,cloudStops} from '/weather-display.js';
import {checkedForecastTime} from '/weather-clock.js?v=1';
/* Bounded transparent display advection, not physical air-parcel trajectories. */
const $=id=>document.getElementById(id);
const scalarFields={temperature:['Temperatura a 2 m','°C',-10,40],precipitation:['Pioggia nell’ora successiva','mm',0,10],rain_probability:['Probabilità di pioggia · prossima ora','%',0,100],humidity:['Umidità relativa aria','%',0,100],gusts:['Raffica massima nell’ora successiva','m/s',0,30],cloud:['Copertura nuvolosa','%',0,100],pressure:['Pressione al suolo','hPa',800,1050],radiation:['Radiazione media nell’ora successiva','W/m²',0,1000]};
const dates=new Intl.DateTimeFormat('it-IT',{timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}),numbers=new Intl.NumberFormat('it-IT',{maximumFractionDigits:1});const clock=t=>dates.format(new Date(t))+' Roma';
export function regionalWind(map){
 let field=null,record=null,fieldStatus=null,visible=true,canvas=null,ctx=null,frame=null,last=0,previous=0,particles=[],screen=null,cols=0,width=0,height=0,busy=false,poll=null,disposed=false,moving=false;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),metrics={active:false,frames:0,particleCount:0,lastFrameCostMs:0,frameIntervals:[],frameCosts:[],updates:0};
 window.__hazardiaWindMetrics=metrics;
 const readings=labelSurface(map),chosen=new Set(weatherViews.overview.fields),quickOptions=[];
 function syncQuick(){for(const input of quickOptions)input.checked=input.dataset.weatherQuick==='wind'?$('wind-regional').checked:chosen.has(input.dataset.weatherQuick);}
 const options=$('regional-weather-options');for(const [key,[name,unit]] of Object.entries(scalarFields)){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=chosen.has(key);input.dataset.regionalWeather=key;label.append(input,document.createTextNode(name+' · '+unit));options?.append(label);input.onchange=()=>{input.checked?chosen.add(key):chosen.delete(key);if(input.checked&&['precipitation','cloud'].includes(key)){const other=key==='cloud'?'precipitation':'cloud';chosen.delete(other);options.querySelector('[data-regional-weather='+other+']').checked=false;}focusSelect.value='custom';syncQuick();reset();};}
 let fineField=null,fineRecord=null,scalarCanvas=null,scalarCtx=null,viewTimer=null,nextRequestAt=0;
 let paused=reduced.matches,zoneMode=false;
 map.on('basemapchange',()=>reset());
 map.on('rainzonesmode',e=>{zoneMode=e.enabled;reset();});
 const playback=forecastPlayback({select:$('wind-hour'),mount:$('monitor-weather-playback'),getTimes:()=>field?.records.filter(r=>Date.parse(r.at)+3600000>Date.now()).map(r=>r.at)||[],getCurrent:()=>record?.at,active:()=>visible&&$('monitor-weather').checked});
 let coverageMessage='';function notice(text){coverageMessage=text||'';legend();}
 const focusControl=L.control({position:'topright'}),legendControl=L.control({position:'bottomright'});let focusEl,focusSelect,legendEl,legendTitle,legendTime,legendBody,legendState,legendMode='';
 focusControl.onAdd=()=>{focusEl=L.DomUtil.create('div','weather-focus');const text=document.createElement('span');text.textContent='Meteo sulla mappa';focusSelect=document.createElement('select');focusSelect.setAttribute('aria-label','Meteo da visualizzare');for(const [key,view] of Object.entries(weatherViews)){const o=document.createElement('option');o.value=key;o.textContent=view.label;focusSelect.append(o);}const custom=document.createElement('option');custom.value='custom';custom.textContent='Livelli personalizzati';custom.disabled=true;focusSelect.append(custom);focusEl.append(text,focusSelect);const detail=document.createElement('details'),summary=document.createElement('summary'),quick=document.createElement('div');detail.className='weather-quick-levels';summary.textContent='Scegli i livelli';detail.append(summary,quick);for(const [key,label] of [['temperature','Temperatura'],['humidity','Umidità'],['wind','Vento'],['precipitation','Pioggia'],['rain_probability','Prob. pioggia'],['cloud','Nuvole']]){const line=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.dataset.weatherQuick=key;input.setAttribute('aria-label',label+' sulla mappa');quickOptions.push(input);line.append(input,document.createTextNode(label));quick.append(line);input.onchange=()=>{const target=key==='wind'?$('wind-regional'):options.querySelector('[data-regional-weather='+key+']');target.checked=input.checked;target.dispatchEvent(new Event('change'));syncQuick();};}focusEl.append(detail);L.DomEvent.disableClickPropagation(focusEl);L.DomEvent.disableScrollPropagation(focusEl);focusSelect.onchange=()=>{const key=focusSelect.value;chosen.clear();for(const k of weatherViews[key].fields)chosen.add(k);$('wind-regional').checked=key==='wind'||weatherViews[key].wind===true;for(const input of options.querySelectorAll('input'))input.checked=chosen.has(input.dataset.regionalWeather);syncQuick();reset();load();if($('wind-regional').checked)loadFine();};return focusEl;};focusControl.addTo(map);$('wind-regional').checked=true;syncQuick();
 legendControl.onAdd=()=>{legendEl=L.DomUtil.create('div','weather-map-legend');legendEl.setAttribute('role','group');legendEl.setAttribute('aria-label','Legenda meteo sulla mappa');legendTitle=document.createElement('strong');legendTime=document.createElement('span');legendBody=document.createElement('div');legendState=document.createElement('small');legendState.setAttribute('role','status');const details=document.createElement('details'),summary=document.createElement('summary');details.className='weather-legend-details';details.addEventListener('toggle',()=>reset());summary.append(legendTitle);details.append(summary,legendBody);legendEl.append(details,legendTime,legendState);return legendEl;};legendControl.addTo(map);
 function completeView(){return !!field&&L.latLngBounds(field.bounds).contains(map.getBounds());}
 function legend(){
  const on=visible&&$('monitor-weather').checked;focusEl.hidden=!on;legendEl.hidden=!on;if(!on)return;if(!chosen.size&&!$('wind-regional').checked){legendTitle.textContent='Nessun livello meteo attivo';legendTime.textContent='';legendBody.replaceChildren();legendMode='';if(legendState.textContent!=='Scegli un dato dal selettore sulla mappa.')legendState.textContent='Scegli un dato dal selettore sulla mappa.';return;}
  const key=focusSelect.value==='overview'?'overview':chosen.has('precipitation')?'rain':chosen.has('cloud')?'cloud':focusSelect.value==='custom'?([...chosen][0]||'wind'):focusSelect.value,view=weatherViews[key]||weatherViews.rain;
  legendTitle.textContent=view.label+' · '+view.unit;legendTime.textContent=record?clock(record.at)+(fieldStatus==='FRESH'?' · previsione Open-Meteo':' · cache non attuale'):'Caricamento della previsione';
  if(legendMode!==key){legendMode=key;legendBody.replaceChildren();if(key==='rain'||key==='overview'){const scale=document.createElement('div');scale.className='weather-rain-bins';for(const c of rainClasses){const item=document.createElement('span'),dot=document.createElement('i');dot.style.background='rgb('+c.color.join(',')+')';item.append(dot,document.createTextNode(c.label));scale.append(item);}legendBody.append(scale);const dry=document.createElement('small');dry.textContent=key==='overview'?'Numeri: °C, UR e probabilità di pioggia. Scie: vento. Colori: mm di pioggia; meno di 0,1 mm trasparente.':'Trasparente: meno di 0,1 mm';legendBody.append(dry);}else if(key==='cloud'){const ramp=document.createElement('i');ramp.className='weather-cloud-ramp';ramp.style.background='linear-gradient(90deg,'+cloudStops.map(([value,rgb])=>'rgb('+rgb.join(',')+') '+value+'%').join(',')+')';legendBody.append(ramp,document.createTextNode('0% sereno · 25 · 50 · 75 · 100% coperto'));}else if(key==='wind'){legendBody.textContent='Scie: direzione del vento · colore: 0–3 / 3–7 / 7–12 / ≥12 m/s';}else if(key==='rain_probability'){legendBody.textContent='Probabilità da ensemble · non quantità di pioggia';}else legendBody.textContent='Valori interpolati della previsione';}
  const message=coverageMessage||(!completeView()?'Copertura incompleta: aggiornamento per tutta la vista. Il meteo precedente è nascosto.':!record?'Dati mancanti per l’ora selezionata.':key==='rain'&&scalarCanvas?.dataset.wetPixels==='0'?'Meno di 0,1 mm nei campioni della vista.':'Modello ~11 km · valori interpolati.');if(legendState.textContent!==message)legendState.textContent=message;
 }
 const colors=['#b6efff','#61e5c1','#f4dc8c','#ffac80'];
 function color(s){return colors[s<3?0:s<7?1:s<12?2:3];}
 function viewport(){const b=map.getBounds();return [[Math.max(-85,b.getSouth()),Math.max(-180,b.getWest())],[Math.min(85,b.getNorth()),Math.min(180,b.getEast())]];}
 function acquisitionBounds(){return viewport();}
 function weatherText(p,keys=Object.keys(scalarFields)){const n=x=>numbers.format(Number(x));return Object.entries(scalarFields).filter(([key])=>keys.includes(key)).map(([key,[label,unit]])=>{const v=sampleScalar(field,record,key,p.lat,p.lng);return label+': '+(v===null?'non disponibile':n(v)+' '+unit);}).join(' · ');}
 function readout(){const el=$('map-weather-readout');if(!el)return;el.hidden=!$('monitor-weather').checked;if(!record||!field){el.textContent='Meteo in caricamento';return;}const p=map.getCenter(),v=(fineRecord&&Date.now()-Date.parse(fineField.available_at)>=0&&Date.now()-Date.parse(fineField.available_at)<10800000&&sampleVector(fineField,fineRecord,p.lat,p.lng))||sampleVector(field,record,p.lat,p.lng);el.textContent=(!L.latLngBounds(field.bounds).contains(map.getBounds())?'COPERTURA PARZIALE · ':'')+(fieldStatus==='FRESH'?'':'CACHE METEO NON ATTUALE · ')+(v?'Vento '+Math.hypot(...v).toFixed(1)+' m/s · ':'Vento non disponibile · ')+weatherText(p,[...chosen])+' · '+clock(record.at)+' · centro della mappa';}
 function scalar(){
  if(!scalarCanvas){scalarCanvas=L.DomUtil.create('canvas','weather-field',map.getPane('mapWeatherFill'));scalarCanvas.setAttribute('aria-hidden','true');scalarCtx=scalarCanvas.getContext('2d');}
  const rw=Math.ceil(width/8),rh=Math.ceil(height/8);if(scalarCanvas.width!==rw)scalarCanvas.width=rw;if(scalarCanvas.height!==rh)scalarCanvas.height=rh;scalarCanvas.style.width=width+'px';scalarCanvas.style.height=height+'px';L.DomUtil.setPosition(scalarCanvas,map.containerPointToLayerPoint([0,0]));
  scalarCtx.clearRect(0,0,scalarCanvas.width,scalarCanvas.height);positionLabels(readings,map);
  scalarCanvas.style.visibility=moving?'hidden':'visible';if(!width||!height||!visible||zoneMode||!$('monitor-weather').checked||!record||moving||!completeView()){readings.replaceChildren();scalarCanvas.dataset.coverage='0';scalarCanvas.dataset.wetPixels='0';scalarCanvas.dataset.cloudPixels='0';legend();return;}
  const coverage=paintRain(scalarCtx,map,field,record,{rain:chosen.has('precipitation'),cloud:chosen.has('cloud')});
  weatherLabels(readings,map,field,record,[...chosen]);scalarCanvas.dataset.field=field.id;scalarCanvas.dataset.variable=[...chosen].join(',');scalarCanvas.dataset.coverage=String(coverage);legend();
 }
 function enabled(){return !zoneMode&&visible&&!document.hidden&&!moving&&completeView()&&$('monitor-weather').checked&&$('wind-regional').checked&&!!record;}
 function stop(){if(frame!==null)cancelAnimationFrame(frame);frame=null;last=0;previous=0;metrics.active=false;}
 function clear(){if(ctx)ctx.clearRect(0,0,width,height);}
 function velocity(x,y){
  const gx=x/16,gy=y/16,a=Math.floor(gx),b=Math.floor(gy),fx=gx-a,fy=gy-b;
  if(a<0||b<0||a+1>=cols||!screen)return null;
  const index=(b*cols+a)*2;if(index+cols*2+3>=screen.length)return null;
  const u=screen[index]*(1-fx)*(1-fy)+screen[index+2]*fx*(1-fy)+screen[index+cols*2]*(1-fx)*fy+screen[index+cols*2+2]*fx*fy;
  const v=screen[index+1]*(1-fx)*(1-fy)+screen[index+3]*fx*(1-fy)+screen[index+cols*2+1]*(1-fx)*fy+screen[index+cols*2+3]*fx*fy;
  return Number.isFinite(u)&&Number.isFinite(v)?[u,v]:null;
 }
 function spawn(p){p.x=Math.random()*width;p.y=Math.random()*height;p.age=0;p.life=4+Math.random()*5;}
 function still(){
  clear();if(!enabled())return;ctx.lineWidth=1.2;
  for(let y=24;y<height;y+=40)for(let x=24;x<width;x+=40){const v=velocity(x,y);if(!v)continue;const speed=Math.hypot(...v);if(speed<.15)continue;const dx=v[0]/speed*10,dy=-v[1]/speed*10;ctx.strokeStyle=color(speed);ctx.beginPath();ctx.moveTo(x-dx*.5,y-dy*.5);ctx.lineTo(x+dx*.5,y+dy*.5);ctx.lineTo(x+dx*.5-dx*.4+dy*.25,y+dy*.5-dy*.4-dx*.25);ctx.moveTo(x+dx*.5,y+dy*.5);ctx.lineTo(x+dx*.5-dx*.4-dy*.25,y+dy*.5-dy*.4+dx*.25);ctx.stroke();}
 }
 function tick(t){
  frame=null;if(!enabled()||paused){stop();return;}
  frame=requestAnimationFrame(tick);if(last&&t-last<32)return;
  const started=performance.now(),dt=last?Math.min(.08,(t-last)/1000):.033;last=t;
  if(previous){metrics.frameIntervals.push(t-previous);if(metrics.frameIntervals.length>120)metrics.frameIntervals.shift();}previous=t;
  ctx.globalCompositeOperation='destination-in';ctx.fillStyle='rgba(0,0,0,0.92)';ctx.fillRect(0,0,width,height);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=.95;ctx.lineWidth=2;ctx.lineCap='round';ctx.shadowBlur=0;const paths=colors.map(()=>[]);
  for(const p of particles){const v=velocity(p.x,p.y);if(!v||p.age>p.life||p.x<0||p.x>width||p.y<0||p.y>height){spawn(p);continue;}const speed=Math.hypot(...v),x=p.x+v[0]*dt*windGain(speed),y=p.y-v[1]*dt*windGain(speed);p.age+=dt;if(speed<.1)continue;paths[speed<3?0:speed<7?1:speed<12?2:3].push(p.x,p.y,x,y);p.x=x;p.y=y;}
  for(let j=0;j<paths.length;j++){const path=paths[j];if(!path.length)continue;ctx.beginPath();for(let i=0;i<path.length;i+=4){ctx.moveTo(path[i],path[i+1]);ctx.lineTo(path[i+2],path[i+3]);}ctx.globalAlpha=.35;ctx.strokeStyle='#071929';ctx.lineWidth=3.5;ctx.stroke();ctx.globalAlpha=.95;ctx.strokeStyle=colors[j];ctx.lineWidth=2;ctx.stroke();}
  ctx.globalAlpha=1;metrics.frames++;metrics.lastFrameCostMs=performance.now()-started;metrics.frameCosts.push(metrics.lastFrameCostMs);if(metrics.frameCosts.length>120)metrics.frameCosts.shift();canvas.dataset.frameP95Ms=String([...metrics.frameCosts].sort((a,b)=>a-b)[Math.ceil(metrics.frameCosts.length*.95)-1]);canvas.dataset.frameIntervalP95Ms=String([...metrics.frameIntervals].sort((a,b)=>a-b)[Math.ceil(metrics.frameIntervals.length*.95)-1]);canvas.dataset.frames=String(metrics.frames);metrics.active=true;
 }
 function button(){const b=$('wind-animation');b.textContent=paused?'Riprendi particelle':'Pausa particelle';b.setAttribute('aria-pressed',String(!paused));}
 function reset(){
  readings.style.visibility='visible';playback.sync();
  $('wind-map-time').hidden=!(visible&&!document.hidden&&$('monitor-weather').checked&&record&&($('wind-regional').checked||chosen.size>0));
  stop();if(!canvas){canvas=L.DomUtil.create('canvas','wind-particles',map.getPane('regionalWind'));canvas.setAttribute('aria-hidden','true');ctx=canvas.getContext('2d');}
  const size=map.getSize();width=size.x;height=size.y;const dpr=Math.min(devicePixelRatio||1,1.5);canvas.width=Math.ceil(width*dpr);canvas.height=Math.ceil(height*dpr);canvas.style.width=width+'px';canvas.style.height=height+'px';L.DomUtil.setPosition(canvas,map.containerPointToLayerPoint([0,0]));ctx.setTransform(dpr,0,0,dpr,0,0);clear();metrics.updates++;if(width<1||height<1)return;scalar();readout();
  if(!enabled())return;
  updateScreen();
  const count=width<600?140:width<1000?240:420;particles=Array.from({length:count},()=>{const p={};spawn(p);return p;});metrics.particleCount=count;canvas.dataset.at=record.at;canvas.dataset.field=field.id;canvas.dataset.fineField=fineRecord?fineField.id:'';button();if(paused)still();else frame=requestAnimationFrame(tick);
 }
 function updateScreen(){
  if(moving||!$('wind-regional').checked||!completeView())return;
  cols=Math.ceil(width/16)+2;const rows=Math.ceil(height/16)+2;screen=new Float32Array(cols*rows*2);screen.fill(NaN);
  const useFine=fineRecord&&Date.now()-Date.parse(fineField.available_at)>=0&&Date.now()-Date.parse(fineField.available_at)<10800000;
  const main=screenSamplePlan(map,field,cols,rows,16,16,0,'wind-main'),fine=useFine?screenSamplePlan(map,fineField,cols,rows,16,16,0,'wind-fine'):null;
  for(let i=0;i<cols*rows;i++){let u=plannedScalar(fine,fineRecord?.u,i),v=plannedScalar(fine,fineRecord?.v,i);if(u===null||v===null){u=plannedScalar(main,record.u,i);v=plannedScalar(main,record.v,i);}if(u!==null&&v!==null){screen[i*2]=u;screen[i*2+1]=v;}}
 }
 function render(s){
  s=checkedForecastTime(s,10800);
  const f=s.forecast;fieldStatus=s.status;$('wind-status').textContent=!f?'Campo regionale non disponibile. '+(s.error||'Acquisizione nella VM…'):(s.status==='STALE'?'Previsione in cache scaduta · ':'Previsione reale · ')+f.model+' · '+f.requested_nodes+' punti · campo adattato all’inquadratura.';
  if(s.error&&f)$('wind-status').textContent+=' '+s.error;if(s.clock_warning)$('wind-status').textContent+=' '+s.clock_warning;
  readout();if(!f){playback.stop();field=null;record=null;fineRecord=null;reset();return;}
  const changed=field?.id!==f.id;field=f;
  if(changed){playback.stop();const selected=$('wind-hour').value,options=f.records.filter(r=>Date.parse(r.at)+3600000>Date.now());$('wind-hour').innerHTML=options.map(r=>'<option value="'+r.at+'">'+clock(r.at)+'</option>').join('');if(options.some(r=>r.at===selected))$('wind-hour').value=selected;record=f.records.find(r=>r.at===$('wind-hour').value)||null;fineRecord=fineField?.records.find(r=>r.at===record?.at)||null;reset();document.dispatchEvent(new CustomEvent('hazardia-weather-field',{detail:{id:f.id,at:record?.at}}));}
  $('wind-hour').disabled=false;$('wind-fit').disabled=false;$('wind-animation').disabled=false;
  $('wind-provenance').textContent='Acquisita '+clock(f.available_at)+'. ICON Global: griglia distribuita0,1° (circa11km); campionamento della vista '+Math.abs(f.lats[1]-f.lats[0]).toFixed(2)+'° × '+Math.abs(f.lons[1]-f.lons[0]).toFixed(2)+'°. Vento ICON-EU più dettagliato nell’Abruzzo, quando disponibile alla stessa ora. '+s.quota.attempts_today+'/'+s.quota.local_daily_limit+' acquisizioni oggi; massimo '+s.quota.max_location_equivalents_daily+' località/giorno. Probabilità di precipitazioni >0,1 mm nella prossima ora da ensemble Open-Meteo; non derivata dai mm previsti. Emissione modello non fornita.';
  $('wind-map-time').textContent=(s.status==='STALE'?'CACHE SCADUTA · ':'')+'Vento a 10 m · '+(record?clock(record.at):'ora non coperta')+' · m/s';
 }
 async function load(){
  if(busy||disposed||!visible||document.hidden||!$('monitor-weather').checked)return;busy=true;clearTimeout(poll);
  try{const r=await fetch('/api/weather/map');if(!r.ok)throw Error('Servizio meteo della mappa non disponibile');const b=viewport(),s=retainCoveredForecast(await r.json(),field,b);render(s);
   const state=viewportWeatherState(s,b,{nextRequestAt});
   if(state.kind==='ready'){notice('');legend();return;}
   const partial=!state.contains||!state.complete;
   if(state.kind==='fetch'){
    notice((partial?'Copertura meteo incompleta · ':'')+'aggiornamento dell’intera vista…');
    nextRequestAt=Date.now()+65000;
    const response=await fetch('/api/weather/map/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:JSON.stringify({bounds:b})});
    if(!response.ok)throw Error('Richiesta meteo non accettata');
    poll=setTimeout(()=>load(),1200);
   }else{
    notice((partial?'Copertura meteo incompleta · ':'Meteo da aggiornare · ')+(state.kind==='poll'?'acquisizione nella VM…':'nuova area tra '+Math.ceil(state.delayMs/1000)+' s (limite gratuito)'));
    poll=setTimeout(()=>load(),state.delayMs);
   }
   if(partial)$('wind-status').textContent+=' Mancano dati fuori dalla copertura acquisita; aggiornamento automatico della vista in attesa.';
  }catch(e){$('wind-status').textContent=e.message+' · Nessun campo meteo inventato.';notice('Meteo incompleto · servizio non disponibile, nuovo tentativo automatico');poll=setTimeout(()=>load(),65000);}finally{busy=false;}
 }
 map.createPane('mapWeatherFill');map.getPane('mapWeatherFill').style.zIndex=390;map.getPane('mapWeatherFill').style.pointerEvents='none';
 map.createPane('regionalWind');map.getPane('regionalWind').style.zIndex=450;map.getPane('regionalWind').style.pointerEvents='none';
 map.on('contextnames',reset);map.on('movestart zoomstart',()=>{moving=true;stop();clear();readings.style.visibility='hidden';if(scalarCanvas)scalarCanvas.style.visibility='hidden';});map.on('moveend zoomend resize',()=>{moving=false;reset();clearTimeout(viewTimer);viewTimer=setTimeout(()=>load(),700);});
 $('wind-regional').onchange=()=>{focusSelect.value='custom';syncQuick();if($('wind-regional').checked&&!field)load();reset();};
 $('wind-hour').onchange=e=>{record=interpolateWeather(field?.records,e.forecastPhase)||field?.records.find(r=>r.at===$('wind-hour').value)||null;fineRecord=e.forecastPhase?interpolateWeather(fineField?.records,e.forecastPhase):fineField?.records.find(r=>r.at===record?.at)||null;$('wind-map-time').textContent=(fieldStatus==='STALE'?'CACHE SCADUTA · ':'')+'Vento a 10 m · '+(record?clock(record.at):'ora non coperta')+' · m/s';if(e.forecastReplay){scalar();readout();updateScreen();canvas.dataset.at=record?.at||'';if(paused)still();}else{reset();document.dispatchEvent(new CustomEvent('hazardia-weather-time',{detail:{at:record?.at}}));}};
 $('wind-animation').onclick=()=>{paused=!paused;button();reset();};$('wind-fit').onclick=()=>{if(field){map.fitBounds([[41.6,12.9],[43,14.9]],{padding:[12,12],maxZoom:9,animate:false});map.getContainer().scrollIntoView({block:'center',behavior:'auto'});}};
 document.addEventListener('visibilitychange',()=>{reset();if(!document.hidden)load();});reduced.addEventListener('change',()=>{paused=reduced.matches;button();reset();});button();const key=$('map-weather-key');key.replaceChildren();rainLegend(key);const note=document.createElement('small');note.textContent='Valori interpolati · UR: umidità relativa · modello ~11km. Meno di0,1mm: trasparente. Colori di pioggia, non livelli di allerta.';key.append(note);
 async function loadFine(){if(!visible||disposed||!$('monitor-weather').checked||!$('wind-regional').checked)return;try{const r=await fetch('/api/weather/wind');if(!r.ok)return;let s=checkedForecastTime(await r.json(),10800);if(s.status==='FRESH'){const changed=fineField?.id!==s.forecast.id;fineField=s.forecast;fineRecord=fineField.records.find(r=>r.at===record?.at)||null;if(changed)reset();}else{fineField=null;fineRecord=null;if(!s.fetching)await fetch('/api/weather/wind/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:'{}'});}}catch{}}
 const timer=setInterval(()=>{if(visible&&$('monitor-weather').checked)load();},65000),fineTimer=setInterval(loadFine,300000);loadFine();load();
 function at(latlng){
  if(!record||!field)return 'Meteo distribuito non ancora disponibile.';
  const temperature=sampleScalar(field,record,'temperature',latlng.lat,latlng.lng),rain=sampleScalar(field,record,'precipitation',latlng.lat,latlng.lng);
  const fine=fineRecord&&Date.now()-Date.parse(fineField.available_at)>=0&&Date.now()-Date.parse(fineField.available_at)<10800000&&sampleVector(fineField,fineRecord,latlng.lat,latlng.lng),v=fine||sampleVector(field,record,latlng.lat,latlng.lng);
  if(temperature===null||rain===null||!v)return 'Punto fuori dalla copertura meteo acquisita; nessuna estrapolazione.';
  const n=v=>Number(v).toLocaleString('it-IT',{maximumFractionDigits:1}),from=(Math.atan2(-v[0],-v[1])*180/Math.PI+360)%360;
  return 'Previsione '+clock(record.at)+': '+weatherText(latlng)+'; vento '+n(Math.hypot(...v))+'m/s da '+n(from)+'° ('+(fine?'ICON-EU':'ICON Global')+'). Valori interpolati per consultazione, non osservazioni locali.';
 }
 return {at,toggle(){reset();load();},hour(at){if(field?.records.some(r=>r.at===at)&&record?.at!==at){$('wind-hour').value=at;$('wind-hour').dispatchEvent(new Event('change'));}},visible(on){visible=on;if(!on){playback.stop();notice('');}reset();if(on)load();},dispose(){disposed=true;playback.stop();stop();clearTimeout(poll);clearInterval(timer);clearInterval(fineTimer);clearTimeout(viewTimer);focusControl.remove();legendControl.remove();canvas?.remove();scalarCanvas?.remove();readings.remove();}};
}
