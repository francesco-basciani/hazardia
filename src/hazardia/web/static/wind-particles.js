import {interpolateWeather} from '/weather-interpolation.js';
import {forecastPlayback} from '/forecast-playback.js';
import {sampleVector,sampleScalar} from '/weather-sampling.js';
export {sampleVector,sampleScalar} from '/weather-sampling.js';
import {paintRain,weatherLabels,labelSurface,positionLabels,windGain,rainLegend} from '/weather-display.js';
import {checkedForecastTime} from '/weather-clock.js?v=1';
/* Bounded transparent display advection, not physical air-parcel trajectories. */
const $=id=>document.getElementById(id);
const scalarFields={temperature:['Temperatura a 2 m','°C',-10,40],precipitation:['Pioggia nell’ora successiva','mm',0,10],humidity:['Umidità relativa aria','%',0,100],gusts:['Raffica massima nell’ora successiva','m/s',0,30],cloud:['Copertura nuvolosa','%',0,100],pressure:['Pressione al suolo','hPa',800,1050],radiation:['Radiazione media nell’ora successiva','W/m²',0,1000]};
const clock=t=>new Date(t).toLocaleString('it-IT',{timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})+' Roma';
export function regionalWind(map){
 let field=null,record=null,fieldStatus=null,visible=true,canvas=null,ctx=null,frame=null,last=0,previous=0,particles=[],screen=null,cols=0,width=0,height=0,busy=false,poll=null,disposed=false;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),metrics={active:false,frames:0,particleCount:0,lastFrameCostMs:0,frameIntervals:[],frameCosts:[],updates:0};
 window.__hazardiaWindMetrics=metrics;
 const readings=labelSurface(map),chosen=new Set(['temperature','humidity','precipitation']);
 const options=$('regional-weather-options');for(const [key,[name,unit]] of Object.entries(scalarFields)){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=chosen.has(key);input.dataset.regionalWeather=key;label.append(input,document.createTextNode(name+' · '+unit));options?.append(label);input.onchange=()=>{input.checked?chosen.add(key):chosen.delete(key);reset();};}
 let fineField=null,fineRecord=null,scalarCanvas=null,scalarCtx=null,viewTimer=null,requestKey=null;
 let paused=reduced.matches;
 const playback=forecastPlayback({select:$('wind-hour'),mount:$('monitor-weather-playback'),getTimes:()=>field?.records.filter(r=>Date.parse(r.at)+3600000>Date.now()).map(r=>r.at)||[],getCurrent:()=>record?.at,active:()=>visible&&$('monitor-weather').checked});
 const colors=['#b6efff','#61e5c1','#f4dc8c','#ffac80'];
 function color(s){return colors[s<3?0:s<7?1:s<12?2:3];}
 function viewport(){const b=map.getBounds();return [[Math.max(-85,b.getSouth()),Math.max(-180,b.getWest())],[Math.min(85,b.getNorth()),Math.min(180,b.getEast())]];}
 function acquisitionBounds(){return viewport();}
 function weatherText(p,keys=Object.keys(scalarFields)){const n=x=>Number(x).toLocaleString('it-IT',{maximumFractionDigits:1});return Object.entries(scalarFields).filter(([key])=>keys.includes(key)).map(([key,[label,unit]])=>{const v=sampleScalar(field,record,key,p.lat,p.lng);return label+': '+(v===null?'non disponibile':n(v)+' '+unit);}).join(' · ');}
 function readout(){const el=$('map-weather-readout');if(!el)return;el.hidden=!$('monitor-weather').checked;if(!record||!field){el.textContent='Meteo in caricamento';return;}const p=map.getCenter(),v=(fineRecord&&Date.now()-Date.parse(fineField.available_at)>=0&&Date.now()-Date.parse(fineField.available_at)<10800000&&sampleVector(fineField,fineRecord,p.lat,p.lng))||sampleVector(field,record,p.lat,p.lng);el.textContent=(!L.latLngBounds(field.bounds).contains(map.getBounds())?'COPERTURA PARZIALE · ':'')+(fieldStatus==='FRESH'?'':'CACHE METEO NON ATTUALE · ')+(v?'Vento '+Math.hypot(...v).toFixed(1)+' m/s · ':'Vento non disponibile · ')+weatherText(p,[...chosen])+' · '+clock(record.at)+' · centro della mappa';}
 function scalar(){
  if(!scalarCanvas){scalarCanvas=L.DomUtil.create('canvas','weather-field',map.getPane('mapWeatherFill'));scalarCanvas.setAttribute('aria-hidden','true');scalarCtx=scalarCanvas.getContext('2d');}
  scalarCanvas.width=Math.ceil(width/8);scalarCanvas.height=Math.ceil(height/8);scalarCanvas.style.width=width+'px';scalarCanvas.style.height=height+'px';L.DomUtil.setPosition(scalarCanvas,map.containerPointToLayerPoint([0,0]));
  scalarCtx.clearRect(0,0,scalarCanvas.width,scalarCanvas.height);readings.replaceChildren();positionLabels(readings,map);
  if(!width||!height||!visible||!$('monitor-weather').checked||!record)return;
  const coverage=paintRain(scalarCtx,map,field,record,{rain:chosen.has('precipitation'),cloud:chosen.has('cloud')});
  weatherLabels(readings,map,field,record,[...chosen]);scalarCanvas.dataset.field=field.id;scalarCanvas.dataset.variable=[...chosen].join(',');scalarCanvas.dataset.coverage=String(coverage);
 }
 function enabled(){return visible&&!document.hidden&&$('monitor-weather').checked&&$('wind-regional').checked&&!!record;}
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
  ctx.globalCompositeOperation='destination-in';ctx.fillStyle='rgba(0,0,0,0.92)';ctx.fillRect(0,0,width,height);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=.95;ctx.lineWidth=2;ctx.lineCap='round';ctx.shadowColor='#071929';ctx.shadowBlur=2;
  for(const p of particles){const v=velocity(p.x,p.y);if(!v||p.age>p.life||p.x<0||p.x>width||p.y<0||p.y>height){spawn(p);continue;}const speed=Math.hypot(...v),x=p.x+v[0]*dt*windGain(speed),y=p.y-v[1]*dt*windGain(speed);p.age+=dt;if(speed<.1)continue;ctx.strokeStyle=color(speed);ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(x,y);ctx.stroke();p.x=x;p.y=y;}
  ctx.globalAlpha=1;metrics.frames++;metrics.lastFrameCostMs=performance.now()-started;metrics.frameCosts.push(metrics.lastFrameCostMs);if(metrics.frameCosts.length>120)metrics.frameCosts.shift();metrics.active=true;
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
  cols=Math.ceil(width/16)+2;const rows=Math.ceil(height/16)+2;screen=new Float32Array(cols*rows*2);screen.fill(NaN);
  const useFine=fineRecord&&Date.now()-Date.parse(fineField.available_at)>=0&&Date.now()-Date.parse(fineField.available_at)<10800000;
  for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const ll=map.containerPointToLatLng([x*16,y*16]),v=(useFine&&sampleVector(fineField,fineRecord,ll.lat,ll.lng))||sampleVector(field,record,ll.lat,ll.lng);if(v){screen[(y*cols+x)*2]=v[0];screen[(y*cols+x)*2+1]=v[1];}}
 }
 function render(s){
  s=checkedForecastTime(s,10800);
  const f=s.forecast;fieldStatus=s.status;$('wind-status').textContent=!f?'Campo regionale non disponibile. '+(s.error||'Acquisizione nella VM…'):(s.status==='STALE'?'Previsione in cache scaduta · ':'Previsione reale · ')+f.model+' · '+f.requested_nodes+' punti · campo adattato all’inquadratura.';
  if(s.error&&f)$('wind-status').textContent+=' '+s.error;if(s.clock_warning)$('wind-status').textContent+=' '+s.clock_warning;
  readout();if(!f){playback.stop();field=null;record=null;fineRecord=null;reset();return;}
  const changed=field?.id!==f.id;field=f;
  if(changed){playback.stop();const selected=$('wind-hour').value,options=f.records.filter(r=>Date.parse(r.at)+3600000>Date.now());$('wind-hour').innerHTML=options.map(r=>'<option value="'+r.at+'">'+clock(r.at)+'</option>').join('');if(options.some(r=>r.at===selected))$('wind-hour').value=selected;record=f.records.find(r=>r.at===$('wind-hour').value)||null;fineRecord=fineField?.records.find(r=>r.at===record?.at)||null;reset();}
  $('wind-hour').disabled=false;$('wind-fit').disabled=false;$('wind-animation').disabled=false;
  $('wind-provenance').textContent='Acquisita '+clock(f.available_at)+'. ICON Global: griglia distribuita0,1° (circa11km); campionamento della vista '+Math.abs(f.lats[1]-f.lats[0]).toFixed(2)+'° × '+Math.abs(f.lons[1]-f.lons[0]).toFixed(2)+'°. Vento ICON-EU più dettagliato nell’Abruzzo, quando disponibile alla stessa ora. '+s.quota.attempts_today+'/'+s.quota.local_daily_limit+' acquisizioni oggi; massimo '+s.quota.max_location_equivalents_daily+' località/giorno. Emissione modello non fornita.';
  $('wind-map-time').textContent=(s.status==='STALE'?'CACHE SCADUTA · ':'')+'Vento a 10 m · '+(record?clock(record.at):'ora non coperta')+' · m/s';
 }
 async function load(refresh=true){
  if(busy||disposed||!visible)return;busy=true;
  try{const r=await fetch('/api/weather/map');if(!r.ok)throw Error('Servizio meteo della mappa non disponibile');const s=await r.json();render(s);
   const b=viewport(),f=s.forecast,adequate=f&&(f.bounds[1][0]-f.bounds[0][0])<=4*Math.max(.8,(b[1][0]-b[0][0])*1.3)&&(f.bounds[1][1]-f.bounds[0][1])<=4*Math.max(.8,(b[1][1]-b[0][1])*1.3),covers=adequate&&b.every((p,i)=>p.every((v,j)=>i===0?v>=f.bounds[0][j]:v<=f.bounds[1][j]));
   if((!covers||s.status==='STALE'||f&&!f.records[0]?.humidity)&&refresh&&!s.fetching){const key=JSON.stringify(acquisitionBounds())+':'+Math.floor(Date.now()/65000);if(key!==requestKey){requestKey=key;await fetch('/api/weather/map/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:JSON.stringify({bounds:acquisitionBounds()})});clearTimeout(poll);poll=setTimeout(()=>load(false),1200);}}
   else if(s.fetching){clearTimeout(poll);poll=setTimeout(()=>load(false),1200);}
   if(!covers&&f)$('wind-status').textContent+=' Copertura parziale della vista: acquisizione o attesa del limite gratuito.';
  }catch(e){$('wind-status').textContent=e.message+' · Nessun campo meteo inventato.';}finally{busy=false;}
 }
 map.createPane('mapWeatherFill');map.getPane('mapWeatherFill').style.zIndex=390;map.getPane('mapWeatherFill').style.pointerEvents='none';
 map.createPane('regionalWind');map.getPane('regionalWind').style.zIndex=450;map.getPane('regionalWind').style.pointerEvents='none';
 map.on('contextnames',reset);map.on('movestart zoomstart',()=>{stop();clear();readings.style.visibility='hidden';});map.on('moveend zoomend resize',()=>{reset();clearTimeout(viewTimer);viewTimer=setTimeout(()=>load(),700);});
 $('wind-regional').onchange=()=>{if($('wind-regional').checked&&!field)load();reset();};
 $('wind-hour').onchange=e=>{record=interpolateWeather(field?.records,e.forecastPhase)||field?.records.find(r=>r.at===$('wind-hour').value)||null;fineRecord=e.forecastPhase?interpolateWeather(fineField?.records,e.forecastPhase):fineField?.records.find(r=>r.at===record?.at)||null;$('wind-map-time').textContent=(fieldStatus==='STALE'?'CACHE SCADUTA · ':'')+'Vento a 10 m · '+(record?clock(record.at):'ora non coperta')+' · m/s';if(e.forecastReplay){scalar();readout();updateScreen();canvas.dataset.at=record?.at||'';if(paused)still();}else reset();};
 $('wind-animation').onclick=()=>{paused=!paused;button();reset();};$('wind-fit').onclick=()=>{if(field){map.fitBounds([[41.6,12.9],[43,14.9]],{padding:[12,12],maxZoom:9,animate:false});map.getContainer().scrollIntoView({block:'center',behavior:'auto'});}};
 document.addEventListener('visibilitychange',reset);reduced.addEventListener('change',()=>{paused=reduced.matches;button();reset();});button();const key=$('map-weather-key');key.replaceChildren();rainLegend(key);const note=document.createElement('small');note.textContent='Valori interpolati · UR: umidità relativa · modello ~11km. Meno di0,1mm: trasparente. Colori di pioggia, non livelli di allerta.';key.append(note);
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
 return {at,toggle(){reset();},hour(at){if(field?.records.some(r=>r.at===at)&&record?.at!==at){$('wind-hour').value=at;$('wind-hour').dispatchEvent(new Event('change'));}},visible(on){visible=on;if(!on)playback.stop();reset();},dispose(){disposed=true;playback.stop();stop();clearTimeout(poll);clearInterval(timer);clearInterval(fineTimer);clearTimeout(viewTimer);canvas?.remove();scalarCanvas?.remove();readings.remove();}};
}
