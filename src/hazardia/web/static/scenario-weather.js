import {viewportWeatherState,retainCoveredForecast} from '/viewport-weather-state.js';
import {weatherAt} from '/weather-interpolation.js';
import {sampleScalar,sampleVector} from '/wind-particles.js';
import {paintRain,weatherLabels,labelSurface,positionLabels,windGain,rainLegend} from '/weather-display.js';
import {checkedForecastTime} from '/weather-clock.js?v=1';

// One VM cache and acquisition request shared by all synchronized scenario windows.
// Display-only: no atmospheric field is silently substituted into a physical run.
const fields={wind:['Vento','m/s',0,20,[92,227,214]],temperature:['Temperatura','°C',-10,40,[245,130,64]],precipitation:['Pioggia nell’ora successiva','mm',0,10,[70,145,245]],humidity:['Umidità aria','%',0,100,[67,201,179]],gusts:['Raffica massima nell’ora successiva','m/s',0,30,[202,133,243]],cloud:['Nubi','%',0,100,[208,218,230]],pressure:['Pressione al suolo','hPa',800,1050,[167,145,236]],radiation:['Radiazione media nell’ora successiva','W/m²',0,1000,[255,211,76]]};
const clock=at=>new Date(at).toLocaleString('it-IT',{timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})+' Roma';
const number=v=>Number.isFinite(v)?v.toLocaleString('it-IT',{maximumFractionDigits:1}):'non disponibile';
export function scenarioWeather(primary){
 const $=id=>document.getElementById(id),layers=new Map(),selected=new Set(['wind','temperature','humidity','precipitation']),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let snapshot=null,requestedAt=null,busy=false,refreshAt=0,timer=null,poll=null,paused=reduced.matches;
 const options=$('map-weather-options'),rainKey=$('scenario-rain-key');rainLegend(rainKey);
 for(const [key,[label,unit,min,max,rgb]] of Object.entries(fields)){
  const wrap=document.createElement('label'),input=document.createElement('input'),dot=document.createElement('i');input.type='checkbox';input.value=key;input.checked=selected.has(key);input.dataset.weatherLayer=key;dot.style.background='rgb('+rgb.join(',')+')';dot.setAttribute('aria-hidden','true');wrap.append(input,dot,document.createTextNode(label+' · '+unit));options.append(wrap);input.onchange=()=>{input.checked?selected.add(key):selected.delete(key);redraw();if(selected.size)load();};
 }
 function record(){return weatherAt(snapshot?.forecast?.records,requestedAt);}
 function status(){const frozen=[...layers.values()].some(l=>l.forcing);if(frozen){ $('map-weather-status').textContent='Meteo del risultato: fonte congelata distinta per ogni scenario. Le modifiche al vento sono rappresentate sulla relativa mappa. Ora condivisa con lo scenario. Previsioni aggiornate mostra la stessa validità da una fonte più recente; non ricalcola i risultati.';return;}const f=snapshot?.forecast,r=record(),names=[...selected].map(k=>fields[k][0]);$('map-weather-status').textContent=!selected.size?'Nessun livello meteo attivo.':!f?'DATI MANCANTI · '+(snapshot?.error||'Campo meteo non disponibile.'):(snapshot.status==='FRESH'?'Previsione reale':'CACHE METEO SCADUTA')+' · '+f.model+' · '+(r?clock(r.at):'ORA NON COPERTA')+' · '+names.join(', ')+(snapshot.error?' · '+snapshot.error:'')+'. Modello circa11km · campioni '+Math.abs(f.lats[1]-f.lats[0]).toFixed(2)+'° × '+Math.abs(f.lons[1]-f.lons[0]).toFixed(2)+'°. Scie amplificate; etichette interpolate, non stazioni. Interpolazione visuale, nessun dettaglio stradale misurato.';}
 function redraw(){rainKey.hidden=false;status();for(const layer of layers.values())layer.reset();}
 const WeatherLayer=L.Layer.extend({
  initialize(){this.frame=null;this.particles=[];this.hide=this.hide.bind(this);this.reset=this.reset.bind(this);this.tick=this.tick.bind(this);},
  onAdd(map){this.map=map;this.readings=labelSurface(map);this.canvas=L.DomUtil.create('canvas','scenario-weather-canvas',map.getPane('scenarioWeather'));this.canvas.setAttribute('aria-hidden','true');this.ctx=this.canvas.getContext('2d');this.wind=L.DomUtil.create('canvas','scenario-weather-wind',map.getPane('scenarioWeather'));this.wind.setAttribute('aria-hidden','true');this.wctx=this.wind.getContext('2d');this.legend=L.control({position:'bottomright'});this.legend.onAdd=()=>{const el=L.DomUtil.create('div','scenario-weather-legend');el.setAttribute('role','status');el.tabIndex=0;L.DomEvent.disableClickPropagation(el);return this.legendEl=el;};this.legend.addTo(map);map.on('movestart zoomstart',this.hide);map.on('moveend zoomend resize contextnames',this.reset);this.reset();},
  onRemove(map){this.hide();map.off('movestart zoomstart',this.hide);map.off('moveend zoomend resize contextnames',this.reset);this.canvas.remove();this.wind.remove();this.readings.remove();this.legend.remove();this.map=null;},
  hide(){if(this.frame!==null)cancelAnimationFrame(this.frame);this.frame=null;this.canvas.style.visibility='hidden';this.wind.style.visibility='hidden';this.readings.style.visibility='hidden';},
  reset(){
   if(!this.map)return;this.hide();const size=this.map.getSize(),w=size.x,h=size.y;this.width=w;this.height=h;if(w<1||h<1){this.readings.replaceChildren();return;}
   for(const el of [this.canvas,this.wind]){el.style.width=w+'px';el.style.height=h+'px';el.style.visibility='visible';L.DomUtil.setPosition(el,this.map.containerPointToLayerPoint([0,0]));}
   positionLabels(this.readings,this.map);this.readings.style.visibility='visible';this.readings.replaceChildren();
   this.canvas.width=Math.ceil(w/8);this.canvas.height=Math.ceil(h/8);this.wind.width=w;this.wind.height=h;
   this.draw();
   const r=this.record(),f=this.field();
   if(!selected.has('wind')||!r||!f||!this.map.getBounds().intersects(f.bounds))return;
   this.particles=Array.from({length:Math.min(420,Math.max(100,Math.floor(w*h/1300)))},()=>({x:Math.random()*w,y:Math.random()*h,age:Math.random()*80}));this.last=0;
   if(paused||reduced.matches){this.arrows();return;}
   this.frame=requestAnimationFrame(this.tick);
  },
  draw(){
   if(!this.map||!this.width||!this.height)return;
   const detailsOpen=this.legendEl.querySelector('details')?.open;const r=this.record(),f=this.field();this.canvas.dataset.at=r?.at||'';this.canvas.dataset.requestedAt=this.at||requestedAt||'';this.canvas.dataset.field=f?.id||'';this.canvas.dataset.origin=this.forcing?'FROZEN_JOB':'LIVE_CONSULTATION';this.canvas.dataset.job=this.forcing?.id||'';this.canvas.dataset.fields=[...selected].join(',');this.wind.dataset.at=r?.at||'';this.wind.dataset.active='false';this.legendEl.replaceChildren();this.legendEl.hidden=!selected.size;
   if(!selected.size)return;
   const title=document.createElement('strong');title.textContent=r?(this.forcing?'METEO USATO · ':snapshot?.status==='FRESH'?'PREVISIONE · ':'CACHE SCADUTA · ')+clock(r.at):'METEO NON DISPONIBILE A QUEST’ORA';this.legendEl.append(title);
   if(!r||!f)return;
   const keys=[...selected].filter(k=>k!=='wind');
   const coverage=paintRain(this.ctx,this.map,f,r,{rain:selected.has('precipitation'),cloud:selected.has('cloud')});
   this.canvas.dataset.coverage=String(coverage);
   weatherLabels(this.readings,this.map,f,r,keys);
   const covered=this.map.getBounds().intersects(f.bounds),full=L.latLngBounds(f.bounds).contains(this.map.getBounds());
   const center=this.map.getCenter(),vector=sampleVector(f,r,center.lat,center.lng),values=document.createElement('details'),summary=document.createElement('summary');values.open=!!detailsOpen;summary.textContent='Valori al centro';values.append(summary);this.legendEl.append(values);
   for(const key of selected){const line=document.createElement('span'),v=key==='wind'?(vector?Math.hypot(...vector):null):sampleScalar(f,r,key,center.lat,center.lng);line.textContent=fields[key][0]+': '+number(v)+' '+fields[key][1]+(key==='wind'&&vector?' · da '+number((Math.atan2(-vector[0],-vector[1])*180/Math.PI+360)%360)+'°':'');values.append(line);}
   const note=document.createElement('small');note.textContent=covered?''+(full?'':'COPERTURA PARZIALE · ')+'etichette interpolate, modello ~11km'+(r.display_interpolation?' · transizione fra quadri orari':''):'FUORI COPERTURA · nessun dato estrapolato';this.legendEl.append(note);
  },
  arrows(){const w=this.width,h=this.height;
   for(let y=25;y<h;y+=45)for(let x=25;x<w;x+=45){const v=this.velocity(x,y);if(!v)continue;const s=Math.hypot(...v);if(s<.1)continue;const dx=v[0]/s*10,dy=-v[1]/s*10,c=this.wctx;c.strokeStyle='#9ceee1';c.lineWidth=2;c.lineCap='round';c.shadowColor='#071929';c.shadowBlur=2;c.beginPath();c.moveTo(x-dx/2,y-dy/2);c.lineTo(x+dx/2,y+dy/2);c.lineTo(x+dx/2-dx*.4+dy*.25,y+dy/2-dy*.4-dx*.25);c.stroke();}
  },
  field(){return this.forcing?this.forcing.field:snapshot?.forecast;},
  record(){const f=this.field();if(!f)return null;const at=this.at||requestedAt,key=f.id+':'+(this.forcing?.id||'')+':'+at;if(this.recordKey===key)return this.recordValue;this.recordKey=key;let r=weatherAt(f.records,at);if(!r){this.recordValue=null;return null;}const edit=this.forcing?.changes?.find(c=>c.hour===Math.floor((Date.parse(at)-Date.parse(this.forcing.start))/3600000));if(edit){const a=edit.direction_deg*Math.PI/180;r={...r,u:f.lats.flatMap(()=>f.lons.map(()=>-edit.speed_ms*Math.sin(a))),v:f.lats.flatMap(()=>f.lons.map(()=>-edit.speed_ms*Math.cos(a)))};}this.recordValue=r;return r;},
  velocity(x,y){const p=this.map.containerPointToLatLng([x,y]);return sampleVector(this.field(),this.record(),p.lat,p.lng);},
  tick(t){this.frame=null;if(document.hidden||!selected.has('wind')||paused||!this.record())return;this.frame=requestAnimationFrame(this.tick);if(this.last&&t-this.last<32)return;const dt=this.last?Math.min(.08,(t-this.last)/1000):.033;this.last=t;const c=this.wctx;c.globalCompositeOperation='destination-in';c.fillStyle='rgba(0,0,0,.92)';c.fillRect(0,0,this.width,this.height);c.globalCompositeOperation='source-over';c.lineWidth=2;c.lineCap='round';c.shadowColor='#071929';c.shadowBlur=2;
   for(const p of this.particles){const v=this.velocity(p.x,p.y);if(!v||p.age>100||p.x<0||p.y<0||p.x>this.width||p.y>this.height){p.x=Math.random()*this.width;p.y=Math.random()*this.height;p.age=0;continue;}const speed=Math.hypot(...v),x=p.x+v[0]*dt*windGain(speed),y=p.y-v[1]*dt*windGain(speed);p.age++;c.strokeStyle=speed<3?'#e5faff':speed<7?'#70ead3':speed<12?'#f4dc8c':'#ffab80';c.beginPath();c.moveTo(p.x,p.y);c.lineTo(x,y);c.stroke();p.x=x;p.y=y;}
   this.wind.dataset.active='true';
  }
 });
 async function load(){if(busy||document.hidden||!selected.size||!layers.size||[...layers.values()].every(l=>l.forcing))return;busy=true;clearTimeout(poll);try{
  const b=primary.getBounds(),bounds=[[Math.max(-85,b.getSouth()),Math.max(-180,b.getWest())],[Math.min(85,b.getNorth()),Math.min(180,b.getEast())]];
  const response=await fetch('/api/weather/map');if(!response.ok)throw Error('Servizio meteo non disponibile');snapshot=checkedForecastTime(retainCoveredForecast(await response.json(),snapshot?.forecast,bounds),10800);
  redraw();const state=viewportWeatherState(snapshot,bounds,{nextRequestAt:refreshAt+65000});
  if(state.kind==='fetch'){refreshAt=Date.now();await fetch('/api/weather/map/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:JSON.stringify({bounds})});poll=setTimeout(()=>load(),1600);}
  else if(state.kind!=='ready')poll=setTimeout(()=>load(),state.delayMs);
 }catch(e){snapshot={...snapshot,status:'UNAVAILABLE',error:e.message};redraw();poll=setTimeout(()=>load(),65000);}finally{busy=false;}}
 primary.on('moveend resize',()=>{clearTimeout(timer);timer=setTimeout(()=>load(),700);});
 reduced.addEventListener('change',()=>redraw());document.addEventListener('visibilitychange',()=>redraw());setInterval(()=>load(),65000);load();
 return {use(m,context){const layer=layers.get(m);if(!layer)return;const frozen=$('weather-view').value!=='forecast',key=JSON.stringify([context?.id,context?.at,frozen,!!context?.field]);if(layer.forcingKey!==key){layer.forcingKey=key;layer.at=context?.at||null;layer.forcing=frozen&&context?.id?context:null;layer.reset();status();if(!layer.forcing)load();}},add(m){if(layers.has(m))return;m.createPane('scenarioWeather');m.getPane('scenarioWeather').style.zIndex=420;m.getPane('scenarioWeather').style.pointerEvents='none';const layer=new WeatherLayer();layers.set(m,layer);layer.addTo(m);},remove(m){const layer=layers.get(m);if(layer){layer.remove();layers.delete(m);}},animate(m,at,draw=true){const layer=layers.get(m);if(!layer)return;layer.at=at;const r=layer.record();layer.canvas.dataset.at=r?.at||'';layer.canvas.dataset.requestedAt=at||'';layer.wind.dataset.at=r?.at||'';if(draw)layer.draw();},setTime(at){if(requestedAt!==at){requestedAt=at;status();for(const layer of layers.values())if(!layer.forcing)layer.draw();}}};
}
