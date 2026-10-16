import {checkedForecastTime} from '/weather-clock.js?v=1';
/* Bounded transparent display advection, not physical air-parcel trajectories. */
const $=id=>document.getElementById(id);
const clock=t=>new Date(t).toLocaleString('it-IT',{timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})+' Roma';
export function sampleVector(field,record,lat,lon){
 const ys=field.lats,xs=field.lons,ny=ys.length,nx=xs.length;
 if(lat<ys[0]||lat>ys[ny-1]||lon<xs[0]||lon>xs[nx-1])return null;
 const gx=(lon-xs[0])/(xs[1]-xs[0]),gy=(lat-ys[0])/(ys[1]-ys[0]),x=Math.min(nx-2,Math.floor(gx)),y=Math.min(ny-2,Math.floor(gy)),dx=gx-x,dy=gy-y;
 const sum=a=>a[y*nx+x]*(1-dx)*(1-dy)+a[y*nx+x+1]*dx*(1-dy)+a[(y+1)*nx+x]*(1-dx)*dy+a[(y+1)*nx+x+1]*dx*dy;
 return [sum(record.u),sum(record.v)];
}
export function regionalWind(map){
 let field=null,record=null,fieldStatus=null,visible=true,canvas=null,ctx=null,frame=null,last=0,previous=0,particles=[],screen=null,cols=0,width=0,height=0,busy=false,poll=null,disposed=false;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),metrics={active:false,frames:0,particleCount:0,lastFrameCostMs:0,frameIntervals:[],frameCosts:[],updates:0};
 window.__hazardiaWindMetrics=metrics;
 let paused=reduced.matches;
 const colors=['#b6efff','#61e5c1','#f4dc8c','#ffac80'];
 function color(s){return colors[s<3?0:s<7?1:s<12?2:3];}
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
  ctx.globalCompositeOperation='destination-in';ctx.fillStyle='rgba(0,0,0,0.90)';ctx.fillRect(0,0,width,height);ctx.globalCompositeOperation='source-over';ctx.globalAlpha=.8;ctx.lineWidth=1.15;
  for(const p of particles){const v=velocity(p.x,p.y);if(!v||p.age>p.life||p.x<0||p.x>width||p.y<0||p.y>height){spawn(p);continue;}const speed=Math.hypot(...v),x=p.x+v[0]*dt*3.5,y=p.y-v[1]*dt*3.5;p.age+=dt;if(speed<.1)continue;ctx.strokeStyle=color(speed);ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(x,y);ctx.stroke();p.x=x;p.y=y;}
  ctx.globalAlpha=1;metrics.frames++;metrics.lastFrameCostMs=performance.now()-started;metrics.frameCosts.push(metrics.lastFrameCostMs);if(metrics.frameCosts.length>120)metrics.frameCosts.shift();metrics.active=true;
 }
 function button(){const b=$('wind-animation');b.textContent=paused?'Riprendi particelle':'Pausa particelle';b.setAttribute('aria-pressed',String(!paused));}
 function reset(){
  $('wind-map-time').hidden=!enabled();
  stop();if(!canvas){canvas=L.DomUtil.create('canvas','wind-particles',map.getPane('regionalWind'));canvas.setAttribute('aria-hidden','true');ctx=canvas.getContext('2d');}
  const size=map.getSize();width=size.x;height=size.y;const dpr=Math.min(devicePixelRatio||1,1.5);canvas.width=Math.ceil(width*dpr);canvas.height=Math.ceil(height*dpr);canvas.style.width=width+'px';canvas.style.height=height+'px';L.DomUtil.setPosition(canvas,map.containerPointToLayerPoint([0,0]));ctx.setTransform(dpr,0,0,dpr,0,0);clear();metrics.updates++;
  if(!enabled())return;
  cols=Math.ceil(width/16)+2;const rows=Math.ceil(height/16)+2;screen=new Float32Array(cols*rows*2);screen.fill(NaN);
  for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const ll=map.containerPointToLatLng([x*16,y*16]),v=sampleVector(field,record,ll.lat,ll.lng);if(v){screen[(y*cols+x)*2]=v[0];screen[(y*cols+x)*2+1]=v[1];}}
  const count=width<600?180:width<1000?320:650;particles=Array.from({length:count},()=>{const p={};spawn(p);return p;});metrics.particleCount=count;canvas.dataset.at=record.at;canvas.dataset.field=field.id;button();if(paused)still();else frame=requestAnimationFrame(tick);
 }
 function render(s){
  s=checkedForecastTime(s,10800);
  const f=s.forecast;fieldStatus=s.status;$('wind-status').textContent=s.status==='EMPTY'?'Campo regionale non disponibile. '+(s.error||'Acquisizione nella VM…'):(s.status==='STALE'?'Previsione in cache scaduta · ':'Previsione reale · ')+f.model+' · '+f.requested_nodes+' punti · campionamento 0,1° (circa 8–11 km).';
  if(s.error&&f)$('wind-status').textContent+=' '+s.error;if(s.clock_warning)$('wind-status').textContent+=' '+s.clock_warning;
  if(!f)return;
  const changed=field?.id!==f.id;field=f;
  if(changed){const selected=$('wind-hour').value,options=f.records.filter(r=>Date.parse(r.at)+3600000>Date.now());$('wind-hour').innerHTML=options.map(r=>'<option value="'+r.at+'">'+clock(r.at)+'</option>').join('');if(options.some(r=>r.at===selected))$('wind-hour').value=selected;record=f.records.find(r=>r.at===$('wind-hour').value)||null;reset();}
  $('wind-hour').disabled=false;$('wind-fit').disabled=false;$('wind-animation').disabled=false;
  $('wind-provenance').textContent='Acquisita '+clock(f.available_at)+'. ICON-EU: griglia circa 7 km; vettori ricampionati e interpolati per il disegno. Rettangolo Abruzzo e aree limitrofe. '+s.quota.attempts_today+'/'+s.quota.local_daily_limit+' acquisizioni oggi; massimo '+s.quota.max_location_equivalents_daily+' località/giorno. Emissione modello non fornita.';
  $('wind-map-time').textContent=(s.status==='STALE'?'CACHE SCADUTA · ':'')+'Vento a 10 m · '+(record?clock(record.at):'ora non coperta')+' · m/s';
 }
 async function load(refresh=true){
  if(busy||disposed)return;busy=true;
  try{const r=await fetch('/api/weather/wind');if(!r.ok)throw Error('Servizio regionale non disponibile');const s=await r.json();render(s);
   if(refresh&&['EMPTY','STALE'].includes(s.status)&&!s.fetching){await fetch('/api/weather/wind/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Hazardia-Research':'1'},body:'{}'});poll=setTimeout(()=>load(false),1500);}
   else if(s.fetching)poll=setTimeout(()=>load(false),1500);
  }catch(e){$('wind-status').textContent=e.message+' · Nessun campo di vento inventato.';}finally{busy=false;}
 }
 map.createPane('regionalWind');map.getPane('regionalWind').style.zIndex=450;map.getPane('regionalWind').style.pointerEvents='none';
 map.on('movestart zoomstart',()=>{stop();clear();});map.on('moveend zoomend resize',reset);
 $('wind-regional').onchange=()=>{if($('wind-regional').checked&&!field)load();reset();};
 $('wind-hour').onchange=()=>{record=field?.records.find(r=>r.at===$('wind-hour').value)||null;$('wind-map-time').textContent=(fieldStatus==='STALE'?'CACHE SCADUTA · ':'')+'Vento a 10 m · '+(record?clock(record.at):'ora non coperta')+' · m/s';reset();};
 $('wind-animation').onclick=()=>{paused=!paused;button();reset();};$('wind-fit').onclick=()=>{if(field){map.fitBounds(field.bounds,{padding:[12,12],maxZoom:9,animate:false});map.getContainer().scrollIntoView({block:'center',behavior:'auto'});}};
 document.addEventListener('visibilitychange',reset);reduced.addEventListener('change',()=>{paused=reduced.matches;button();reset();});button();
 const timer=setInterval(()=>{if(visible&&$('wind-regional').checked&&$('monitor-weather').checked)load();},300000);load();
 return {toggle(){reset();},hour(at){if(field?.records.some(r=>r.at===at)&&record?.at!==at){$('wind-hour').value=at;$('wind-hour').dispatchEvent(new Event('change'));}},visible(on){visible=on;reset();},dispose(){disposed=true;stop();clearTimeout(poll);clearInterval(timer);canvas?.remove();}};
}
