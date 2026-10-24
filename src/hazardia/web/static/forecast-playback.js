import {dateTimeFormatter} from "/i18n.js";
// Continuous visual replay of hourly VM snapshots: no acquisition or jobs per frame.
const dates=dateTimeFormatter({timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});const clock=at=>dates.format(new Date(at))+' Roma';
export function forecastPlayback({select,mount,getTimes,getCurrent,active=()=>true,onTime=null}){
 const bar=document.createElement('section');bar.className='forecast-playback';bar.setAttribute('aria-label','Riproduzione temporale del monitoraggio');
 const title=document.createElement('strong');title.textContent='Previsioni e criticità';const back=document.createElement('button'),play=document.createElement('button'),next=document.createElement('button'),slider=document.createElement('input'),out=document.createElement('output'),speedLabel=document.createElement('label'),speed=document.createElement('select'),note=document.createElement('small');
 back.textContent='−1 h';back.setAttribute('aria-label','Ora precedente');next.textContent='+1 h';next.setAttribute('aria-label','Ora successiva');slider.type='range';slider.min=0;slider.max=0;slider.step=.001;slider.value=0;slider.setAttribute('aria-label','Ora delle previsioni sulla mappa');out.className='forecast-time';speedLabel.textContent='Velocità';speed.setAttribute('aria-label','Velocità riproduzione previsioni');
 note.className='forecast-interpolation-note';note.textContent='Ora comune a meteo, indici incendio e criticità. Ogni fonte conserva validità e passo propri; osservazioni datate, nessuna previsione inventata.';
 for(const [value,label] of [[1500,'1 h / 1,5 s'],[750,'1 h / 0,75 s'],[3000,'1 h / 3 s']]){const o=document.createElement('option');o.value=value;o.textContent=label;speed.append(o);}speedLabel.append(speed);bar.append(title,back,play,next,slider,out,speedLabel,note);mount.append(bar);
 let timer=null,internal=false,times=[],position=0,phase=null,previous=null,lastPaint=0;
 const playing=()=>{play.textContent=timer!==null?'Ⅱ Pausa':'▶ Riproduci';play.setAttribute('aria-label',timer!==null?'Pausa previsioni':'Riproduci previsioni');play.setAttribute('aria-pressed',String(timer!==null));};
 function stop(){if(timer!==null)cancelAnimationFrame(timer);timer=null;previous=null;playing();}
 function sync(){
  const fresh=[...new Set(getTimes()||[])].filter(at=>Number.isFinite(Date.parse(at))).sort();
  if(times.join()!==fresh.join()){stop();phase=null;}times=fresh;
  const current=getCurrent(),i=times.indexOf(current);if(!phase||current!==phase.at){phase=null;position=Math.max(0,i);if(i<0&&current){const t=Date.parse(current),j=times.findIndex((at,n)=>n+1<times.length&&Date.parse(at)<t&&t<Date.parse(times[n+1]));if(j>=0){const fraction=(t-Date.parse(times[j]))/(Date.parse(times[j+1])-Date.parse(times[j]));phase={from:times[j],to:times[j+1],fraction,at:current};position=j+fraction;}}}
  slider.max=Math.max(0,times.length-1);slider.value=position;slider.setAttribute('aria-valuetext',current?clock(current):'Ora non disponibile');out.textContent=times.length?(current?clock(current):'Seleziona un’ora'):'Previsioni non disponibili';
  for(const el of [back,play,next,slider,speed])el.disabled=!times.length;
  if(!times.length||!active())stop();back.disabled=!times.length||position<=0;next.disabled=!times.length||position>=times.length-1;play.disabled=!times.length||!active();bar.dataset.at=current||'';bar.dataset.from=phase?.from||current||'';bar.dataset.to=phase?.to||current||'';bar.dataset.fraction=String(phase?.fraction||0);playing();
 }
 function set(value){
  position=Math.max(0,Math.min(times.length-1,value));const i=Math.floor(position),fraction=position-i;
  if(fraction&&Date.parse(times[i+1])-Date.parse(times[i])!==3600000){stop();position=i;}
  const j=Math.floor(position),t=position-j;
  phase=t?{from:times[j],to:times[j+1],fraction:t,at:new Date(Date.parse(times[j])+t*3600000).toISOString()}:null;
  internal=true;if(onTime)onTime(phase?.at||times[j],phase);else{select.value=times[j];const event=new Event('change',{bubbles:true});event.forecastPhase=phase;event.forecastReplay=true;select.dispatchEvent(event);}internal=false;sync();
 }
 function tick(now){
  if(document.hidden||!active()||!bar.getClientRects().length||window.frameElement&&!window.frameElement.getClientRects().length){stop();return;}
  if(previous!==null){const delta=(now-previous)/Number(speed.value);position=Math.min(times.length-1,position+delta);}previous=now;
  if(now-lastPaint>=50||position>=times.length-1){lastPaint=now;const started=performance.now();set(position);const costs=bar._frameCosts||(bar._frameCosts=[]);costs.push(performance.now()-started);if(costs.length>120)costs.shift();bar.dataset.frameSamples=String(costs.length);bar.dataset.frameP95Ms=String([...costs].sort((a,b)=>a-b)[Math.ceil(costs.length*.95)-1]);bar.dataset.lastFrameCostMs=String(costs.at(-1));}
  if(position>=times.length-1||timer===null){stop();return;}timer=requestAnimationFrame(tick);
 }
 function start(){if(timer!==null){stop();return;}sync();if(!times.length||!active())return;if(position>=times.length-1)set(0);previous=null;timer=requestAnimationFrame(tick);playing();}
 back.onclick=()=>{stop();set(Math.max(0,Math.ceil(position)-1));};next.onclick=()=>{stop();set(Math.min(times.length-1,Math.floor(position)+1));};play.onclick=start;slider.oninput=()=>{stop();set(Number(slider.value));};
 speed.onchange=()=>{previous=null;};select.addEventListener('change',()=>{if(internal)return;stop();phase=null;queueMicrotask(sync);});document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});window.addEventListener('pagehide',stop);sync();return {sync,stop,element:bar};
}
