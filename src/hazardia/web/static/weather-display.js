// Display-only bilinear samples: denser labels never increase model resolution.
import {sampleScalar,screenSamplePlan,plannedScalar} from '/weather-sampling.js';
export const rainClasses=[
 {min:.1,color:[64,174,244],label:'0,1–1'},
 {min:1,color:[36,108,228],label:'1–2,5'},
 {min:2.5,color:[118,71,216],label:'2,5–5'},
 {min:5,color:[207,62,157],label:'5–10'},
 {min:10,color:[229,68,56],label:'≥10'}
];
const mix=(stops,value)=>{if(value<=stops[0][0])return stops[0][1];for(let i=1;i<stops.length;i++){if(value<=stops[i][0]){const [a,x]=stops[i-1],[b,y]=stops[i],t=(value-a)/(b-a);return x.map((v,j)=>Math.round(v+(y[j]-v)*t));}}return stops.at(-1)[1];};
export function temperatureColor(v){return Number.isFinite(v)?mix([[-20,[170,162,255]],[0,[112,213,255]],[10,[133,240,209]],[20,[255,230,117]],[30,[255,167,98]],[40,[255,112,135]]],v):[255,255,255];}
export function rainColor(value){if(!Number.isFinite(value)||value<.1)return null;return mix(rainClasses.map(c=>[c.min,c.color]),value);}
export const cloudStops=[[0,[104,169,196]],[25,[132,184,211]],[50,[180,206,238]],[75,[217,205,246]],[100,[246,237,255]]];
export function cloudColor(value){return Number.isFinite(value)?mix(cloudStops,Math.max(0,Math.min(100,value))):null;}
export function cloudOpacity(value){return Number.isFinite(value)?Math.pow(Math.max(0,Math.min(1,value/100)),1.25)*.68:0;}
const rasterBuffers=new WeakMap();
export function paintRain(ctx,map,field,record,{rain=true,cloud=false}={}){
 const w=ctx.canvas.width,h=ctx.canvas.height,size=map.getSize();if(!w||!h||!size.x||!size.y){ctx.canvas.dataset.wetPixels='0';ctx.canvas.dataset.cloudPixels='0';return 0;}let image=rasterBuffers.get(ctx);if(!image||image.width!==w||image.height!==h){image=ctx.createImageData(w,h);rasterBuffers.set(ctx,image);}image.data.fill(0);const plan=screenSamplePlan(map,field,w,h,size.x/w,size.y/h);let covered=0,wet=0,cloudy=0;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x,v=rain?plannedScalar(plan,record?.precipitation,i):null,c=cloud?plannedScalar(plan,record?.cloud,i):null;if(!Number.isFinite(v)&&!Number.isFinite(c))continue;covered++;
  const ca=cloudOpacity(c),cr=cloudColor(c)||[0,0,0],rgb=rainColor(v),ra=rgb?(35+120*Math.min(1,(v-.1)/.9))/255:0,a=ra+ca*(1-ra);if(ca)cloudy++;if(ra)wet++;if(a)image.data.set([...(rgb||[0,0,0]).map((n,j)=>Math.round((n*ra+cr[j]*ca*(1-ra))/a)),Math.round(a*255)],(y*w+x)*4);
 }
 ctx.putImageData(image,0,0);ctx.canvas.dataset.wetPixels=String(wet);ctx.canvas.dataset.cloudPixels=String(cloudy);return covered/Math.max(1,w*h);
}
const numbers=new Intl.NumberFormat('it-IT',{maximumFractionDigits:1});const n=v=>numbers.format(v);
const short={temperature:['','°C'],humidity:['UR','%'],gusts:['Raff.','m/s'],cloud:['Nubi','%'],rain_probability:['Prob. pioggia','%'],pressure:['','hPa'],radiation:['Sole','W/m²'],precipitation:['Pioggia','mm']};
export function weatherLabels(host,map,field,record,keys){
 if(!field||!record||!keys.length){host.replaceChildren();return;}
 keys=keys.filter(k=>(!['precipitation','cloud'].includes(k)||keys.length===1)&&(k!=='rain_probability'||Array.isArray(record.rain_probability)));
 const rect=map.getContainer().getBoundingClientRect(),obstacles=[...map.getContainer().querySelectorAll('.map-place-name,.geo-label.place,.region-name')].map(el=>el.getBoundingClientRect());
 let count=0;const size=map.getSize(),cols=Math.max(1,Math.floor(size.x/190)),rows=Math.max(1,Math.floor(size.y/(keys.length>4?155:125))),cw=size.x/cols,ch=size.y/rows;
 // At most 32 indicators/window; pointer-transparent so map authoring remains usable.
 for(let row=0;row<rows;row++)for(let col=0;col<cols;col++){
  if(count>=32)break;const x=(col+.5)*cw;let y=(row+.5)*ch;if(map.getContainer().querySelector('.scenario-weather-legend')&&x>size.x-250&&y>size.y-120)continue;
  if(obstacles.some(o=>Math.abs((o.left+o.right)/2-rect.left-x)<115&&Math.abs((o.top+o.bottom)/2-rect.top-y)<45))y=Math.min(size.y-42,y+48);const p=map.containerPointToLatLng([x,y]);
  const values=keys.map(k=>[k,sampleScalar(field,record,k,p.lat,p.lng)]);if(!values.some(([,v])=>Number.isFinite(v)))continue;
  let card=host.children[count];const signature=keys.join(',');if(!card){card=document.createElement('div');card.className='weather-site';host.append(card);host.dataset.createdLabels=String(Number(host.dataset.createdLabels||0)+1);}if(card.dataset.keys!==signature){card.replaceChildren(...keys.map(key=>{const line=document.createElement(key==='temperature'?'strong':'span');line.dataset.variable=key;return line;}));card.dataset.keys=signature;}card.style.left=x+'px';card.style.top=y+'px';card.dataset.lat=p.lat;card.dataset.lon=p.lng;card.dataset.at=record.at;
  for(const [index,[key,v]] of values.entries()){const line=card.children[index],[label,unit]=short[key];line.dataset.variable=key;line.dataset.value=v;if(key==='temperature')line.style.color='rgb('+temperatureColor(v).join(',')+')';line.textContent=(label?label+' ':'')+(Number.isFinite(v)?n(v)+' '+unit:'n/d');}
  count++;
 }
 while(host.children.length>count)host.lastElementChild.remove();
}
export function labelSurface(map){const pane='weatherReadings';if(!map.getPane(pane)){map.createPane(pane);map.getPane(pane).style.zIndex=550;map.getPane(pane).style.pointerEvents='none';}return L.DomUtil.create('div','weather-sites',map.getPane(pane));}
export function positionLabels(host,map){L.DomUtil.setPosition(host,map.containerPointToLayerPoint([0,0]));}
// Low winds retain their direction but are visually amplified; calm has no flow.
export function windGain(speed){return speed<.1?0:Math.max(22,48/speed);}
export function rainLegend(host){
 for(const [name,gradient,ticks] of [['Temperatura · °C','rgb(170,162,255) 0%,rgb(112,213,255) 33.33%,rgb(133,240,209) 50%,rgb(255,230,117) 66.67%,rgb(255,167,98) 83.33%,rgb(255,112,135) 100%','−20 · 0 · 10 · 20 · 30 · 40'],['Pioggia · mm nell’ora successiva','rgb(64,174,244) 0%,rgb(36,108,228) 9.09%,rgb(118,71,216) 24.24%,rgb(207,62,157) 49.49%,rgb(229,68,56) 100%','0,1 · 1 · 2,5 · 5 · ≥10'],['Nuvole · copertura %','rgba(104,169,196,0) 0%,rgba(132,184,211,.12) 25%,rgba(180,206,238,.29) 50%,rgba(217,205,246,.47) 75%,rgba(246,237,255,.68) 100%','0 · 25 · 50 · 75 · 100'],['Prob. pioggia · prossima ora','rgb(185,222,247),rgb(71,150,220)','0–100% · precipitazioni >0,1 mm · ensemble']]){const el=document.createElement('div');el.className='weather-color-key';const label=document.createElement('span'),ramp=document.createElement('i'),values=document.createElement('small');label.textContent=name;ramp.style.background='linear-gradient(90deg,'+gradient+')';values.textContent=ticks;el.append(label,ramp,values);host.append(el);}
}
