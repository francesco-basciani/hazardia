import {sampleScalar,sampleVector} from '/wind-particles.js';
import {checkedForecastTime} from '/weather-clock.js?v=1';

// One VM cache and acquisition request shared by all synchronized scenario windows.
// Display-only: no atmospheric field is silently substituted into a physical run.
const fields={wind:['Vento','m/s',0,20,[92,227,214]],temperature:['Temperatura','°C',-10,40,[245,130,64]],precipitation:['Pioggia nell’ora successiva','mm',0,10,[70,145,245]],humidity:['Umidità aria','%',0,100,[67,201,179]],gusts:['Raffica massima nell’ora successiva','m/s',0,30,[202,133,243]],cloud:['Nubi','%',0,100,[208,218,230]],pressure:['Pressione al suolo','hPa',800,1050,[167,145,236]],radiation:['Radiazione media nell’ora successiva','W/m²',0,1000,[255,211,76]]};
const clock=at=>new Date(at).toLocaleString('it-IT',{timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})+' Roma';
const number=v=>Number.isFinite(v)?v.toLocaleString('it-IT',{maximumFractionDigits:1}):'non disponibile';
export function scenarioWeather(primary){
 const $=id=>document.getElementById(id),layers=new Map(),selected=new Set(['wind']),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let snapshot=null,requestedAt=null,busy=false,refreshAt=0,timer=null,poll=null,paused=reduced.matches,opacity=.24;
 const options=$('map-weather-options');
 for(const [key,[label,unit,min,max,rgb]] of Object.entries(fields)){
  const wrap=document.createElement('label'),input=document.createElement('input'),dot=document.createElement('i');input.type='checkbox';input.value=key;input.checked=selected.has(key);input.dataset.weatherLayer=key;dot.style.background='rgb('+rgb.join(',')+')';dot.setAttribute('aria-hidden','true');wrap.append(input,dot,document.createTextNode(label+' · '+unit));options.append(wrap);input.onchange=()=>{input.checked?selected.add(key):selected.delete(key);redraw();if(selected.size)load();};
 }
 function chosenTime(){return $('map-weather-hour').value==='timeline'?requestedAt:$('map-weather-hour').value;}
 function record(){const f=snapshot?.forecast,at=chosenTime();return f?.records.find(r=>r.at===(at||f.records.find(r=>Date.parse(r.at)>Date.now())?.at))||null;}
 function status(){const f=snapshot?.forecast,r=record(),names=[...selected].map(k=>fields[k][0]);$('map-weather-status').textContent=!selected.size?'Nessun livello meteo attivo.':!f?'DATI MANCANTI · '+(snapshot?.error||'Campo meteo non disponibile.'):(snapshot.status==='FRESH'?'Previsione reale':'CACHE METEO SCADUTA')+' · '+f.model+' · '+(r?clock(r.at):'ORA NON COPERTA')+' · '+names.join(', ')+(snapshot.error?' · '+snapshot.error:'')+'. Modello circa11km · campioni '+Math.abs(f.lats[1]-f.lats[0]).toFixed(2)+'° × '+Math.abs(f.lons[1]-f.lons[0]).toFixed(2)+'°. Interpolazione visuale, nessun dettaglio stradale misurato.';}
 function redraw(){status();for(const layer of layers.values())layer.reset();}
 const WeatherLayer=L.Layer.extend({
  initialize(){this.frame=null;this.particles=[];this.hide=this.hide.bind(this);this.reset=this.reset.bind(this);this.tick=this.tick.bind(this);},
  onAdd(map){this.map=map;this.canvas=L.DomUtil.create('canvas','scenario-weather-canvas',map.getPane('scenarioWeather'));this.canvas.setAttribute('aria-hidden','true');this.ctx=this.canvas.getContext('2d');this.wind=L.DomUtil.create('canvas','scenario-weather-wind',map.getPane('scenarioWeather'));this.wind.setAttribute('aria-hidden','true');this.wctx=this.wind.getContext('2d');this.legend=L.control({position:'bottomright'});this.legend.onAdd=()=>{const el=L.DomUtil.create('div','scenario-weather-legend');el.setAttribute('role','status');el.tabIndex=0;L.DomEvent.disableClickPropagation(el);return this.legendEl=el;};this.legend.addTo(map);map.on('movestart zoomstart',this.hide);map.on('moveend zoomend resize',this.reset);this.reset();},
  onRemove(map){this.hide();map.off('movestart zoomstart',this.hide);map.off('moveend zoomend resize',this.reset);this.canvas.remove();this.wind.remove();this.legend.remove();},
  hide(){if(this.frame!==null)cancelAnimationFrame(this.frame);this.frame=null;this.canvas.style.visibility='hidden';this.wind.style.visibility='hidden';},
  reset(){
   if(!this.map)return;this.hide();const size=this.map.getSize(),w=size.x,h=size.y;this.width=w;this.height=h;
   for(const el of [this.canvas,this.wind]){el.style.width=w+'px';el.style.height=h+'px';el.style.visibility='visible';L.DomUtil.setPosition(el,this.map.containerPointToLayerPoint([0,0]));}
   this.canvas.width=Math.ceil(w/12);this.canvas.height=Math.ceil(h/12);this.wind.width=w;this.wind.height=h;
   const r=record(),f=snapshot?.forecast;this.canvas.dataset.at=r?.at||'';this.canvas.dataset.fields=[...selected].join(',');this.wind.dataset.at=r?.at||'';this.wind.dataset.active='false';this.legendEl.replaceChildren();this.legendEl.hidden=!selected.size;
   if(!selected.size)return;
   const title=document.createElement('strong');title.textContent=r?(snapshot.status==='FRESH'?'':'CACHE SCADUTA · ')+clock(r.at):'METEO NON DISPONIBILE A QUEST’ORA';this.legendEl.append(title);
   if(!r||!f)return;
   const keys=[...selected].filter(k=>k!=='wind'),image=this.ctx.createImageData(this.canvas.width,this.canvas.height);let covered=0;
   for(let y=0;y<image.height;y++)for(let x=0;x<image.width;x++){
    const p=this.map.containerPointToLatLng([(x+.5)*12,(y+.5)*12]);if(!sampleVector(f,r,p.lat,p.lng))continue;covered++;
    let rr=0,gg=0,bb=0,aa=0;
    for(const key of keys){const v=sampleScalar(f,r,key,p.lat,p.lng);if(!Number.isFinite(v))continue;const [,unit,min,max,base]=fields[key],t=Math.max(0,Math.min(1,(v-min)/(max-min)));if(key==='precipitation'&&v<.1)continue;const rgb=key==='temperature'?[35+210*t,140-60*t,235-195*t]:base,a=opacity*(key==='precipitation'?Math.min(1,.25+v/5):.4+.6*t)/Math.sqrt(Math.max(1,keys.length));rr=rgb[0]*a+rr*(1-a);gg=rgb[1]*a+gg*(1-a);bb=rgb[2]*a+bb*(1-a);aa=a+aa*(1-a);}
    if(aa)image.data.set([rr/aa,gg/aa,bb/aa,aa*255],(y*image.width+x)*4);
   }
   this.ctx.putImageData(image,0,0);this.canvas.dataset.coverage=String(covered/Math.max(1,image.width*image.height));
   const center=this.map.getCenter(),vector=sampleVector(f,r,center.lat,center.lng);
   for(const key of selected){const line=document.createElement('span'),v=key==='wind'?(vector?Math.hypot(...vector):null):sampleScalar(f,r,key,center.lat,center.lng);line.textContent=fields[key][0]+': '+number(v)+' '+fields[key][1]+(key==='wind'&&vector?' · da '+number((Math.atan2(-vector[0],-vector[1])*180/Math.PI+360)%360)+'°':'');this.legendEl.append(line);}
   const note=document.createElement('small');note.textContent=covered?'Valori al centro · '+(covered===image.width*image.height?'vista coperta':'COPERTURA PARZIALE'):'FUORI COPERTURA · nessun dato estrapolato';this.legendEl.append(note);
   if(!selected.has('wind')||!covered)return;
   this.particles=Array.from({length:Math.min(220,Math.max(60,Math.floor(w*h/1500)))},()=>({x:Math.random()*w,y:Math.random()*h,age:Math.random()*80}));this.last=0;
   if(paused||reduced.matches){for(let y=25;y<h;y+=45)for(let x=25;x<w;x+=45){const v=this.velocity(x,y);if(!v)continue;const s=Math.hypot(...v);if(s<.1)continue;const dx=v[0]/s*10,dy=-v[1]/s*10,c=this.wctx;c.strokeStyle='#9ceee1';c.lineWidth=1.5;c.beginPath();c.moveTo(x-dx/2,y-dy/2);c.lineTo(x+dx/2,y+dy/2);c.lineTo(x+dx/2-dx*.4+dy*.25,y+dy/2-dy*.4-dx*.25);c.stroke();}return;}
   this.frame=requestAnimationFrame(this.tick);
  },
  velocity(x,y){const p=this.map.containerPointToLatLng([x,y]);return sampleVector(snapshot.forecast,record(),p.lat,p.lng);},
  tick(t){this.frame=null;if(document.hidden||!selected.has('wind')||paused||!record())return;this.frame=requestAnimationFrame(this.tick);if(this.last&&t-this.last<32)return;const dt=this.last?Math.min(.08,(t-this.last)/1000):.033;this.last=t;const c=this.wctx;c.globalCompositeOperation='destination-in';c.fillStyle='rgba(0,0,0,.88)';c.fillRect(0,0,this.width,this.height);c.globalCompositeOperation='source-over';c.lineWidth=1.5;
   for(const p of this.particles){const v=this.velocity(p.x,p.y);if(!v||p.age>100||p.x<0||p.y<0||p.x>this.width||p.y>this.height){p.x=Math.random()*this.width;p.y=Math.random()*this.height;p.age=0;continue;}const speed=Math.hypot(...v),x=p.x+v[0]*dt*14,y=p.y-v[1]*dt*14;p.age++;c.strokeStyle=speed<3?'#b8f2ff':speed<7?'#70ead3':speed<12?'#f4dc8c':'#ffab80';c.beginPath();c.moveTo(p.x,p.y);c.lineTo(x,y);c.stroke();p.x=x;p.y=y;}
   this.wind.dataset.active='true';
  }
 });
 async function load(refresh=true){if(busy||document.hidden||!selected.size)return;busy=true;try{
  const response=await fetch('/api/weather/map');if(!response.ok)throw Error('Servizio meteo non disponibile');const old=snapshot?.forecast?.id;snapshot=checkedForecastTime(await response.json(),10800);const f=snapshot.forecast;
  if(f&&old!==f.id){const keep=$('map-weather-hour').value;$('map-weather-hour').replaceChildren();const follow=document.createElement('option');follow.value='timeline';follow.textContent='Segui la timeline';$('map-weather-hour').append(follow);for(const r of f.records){const o=document.createElement('option');o.value=r.at;o.textContent=clock(r.at);$('map-weather-hour').append(o);}if([...$('map-weather-hour').options].some(o=>o.value===keep))$('map-weather-hour').value=keep;}
  redraw();const b=primary.getBounds(),bounds=[[Math.max(-85,b.getSouth()),Math.max(-180,b.getWest())],[Math.min(85,b.getNorth()),Math.min(180,b.getEast())]],adequate=f&&(f.bounds[1][0]-f.bounds[0][0])<=4*Math.max(.8,(bounds[1][0]-bounds[0][0])*1.3)&&(f.bounds[1][1]-f.bounds[0][1])<=4*Math.max(.8,(bounds[1][1]-bounds[0][1])*1.3),covers=adequate&&bounds.every((p,i)=>p.every((v,j)=>i?v<=f.bounds[1][j]:v>=f.bounds[0][j]));
  if(refresh&&(!covers||snapshot.status!=='FRESH')&&!snapshot.fetching&&Date.now()-refreshAt>=65000){refreshAt=Date.now();await fetch('/api/weather/map/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:JSON.stringify({bounds})});clearTimeout(poll);poll=setTimeout(()=>load(false),1600);}else if(snapshot.fetching){clearTimeout(poll);poll=setTimeout(()=>load(false),1600);}
 }catch(e){snapshot={...snapshot,status:'UNAVAILABLE',error:e.message};redraw();}finally{busy=false;}}
 primary.on('moveend',()=>{clearTimeout(timer);timer=setTimeout(()=>load(),700);});
 $('map-weather-hour').onchange=redraw;$('map-weather-pause').onclick=()=>{paused=!paused;$('map-weather-pause').textContent=paused?'Riprendi vento':'Pausa vento';$('map-weather-pause').setAttribute('aria-pressed',String(paused));redraw();};
 reduced.addEventListener('change',()=>redraw());document.addEventListener('visibilitychange',()=>redraw());setInterval(()=>load(),65000);load();
 return {add(m){if(layers.has(m))return;m.createPane('scenarioWeather');m.getPane('scenarioWeather').style.zIndex=420;m.getPane('scenarioWeather').style.pointerEvents='none';const layer=new WeatherLayer();layers.set(m,layer);layer.addTo(m);},remove(m){const layer=layers.get(m);if(layer){layer.remove();layers.delete(m);}},setTime(at){if(requestedAt!==at){requestedAt=at;redraw();}}};
}
