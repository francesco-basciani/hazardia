// Display-only bilinear samples: denser labels never increase model resolution.
import {sampleScalar} from '/weather-sampling.js';
export const rainClasses=[
 {min:.1,color:[64,174,244],label:'0,1–1'},
 {min:1,color:[36,108,228],label:'1–2,5'},
 {min:2.5,color:[118,71,216],label:'2,5–5'},
 {min:5,color:[207,62,157],label:'5–10'},
 {min:10,color:[229,68,56],label:'≥10'}
];
export function rainColor(value){if(!Number.isFinite(value)||value<.1)return null;return [...rainClasses].reverse().find(c=>value>=c.min).color;}
export function paintRain(ctx,map,field,record){
 const w=ctx.canvas.width,h=ctx.canvas.height,size=map.getSize(),image=ctx.createImageData(w,h);let covered=0,wet=0;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){const p=map.containerPointToLatLng([(x+.5)*size.x/w,(y+.5)*size.y/h]),v=sampleScalar(field,record,'precipitation',p.lat,p.lng);if(!Number.isFinite(v))continue;covered++;const rgb=rainColor(v);if(rgb){wet++;image.data.set([...rgb,145],(y*w+x)*4);}}
 ctx.putImageData(image,0,0);ctx.canvas.dataset.wetPixels=String(wet);return covered/Math.max(1,w*h);
}
const n=v=>v.toLocaleString('it-IT',{maximumFractionDigits:1});
const short={temperature:['','°C'],humidity:['UR','%'],gusts:['Raff.','m/s'],cloud:['Nubi','%'],pressure:['','hPa'],radiation:['Sole','W/m²'],precipitation:['Pioggia','mm']};
export function weatherLabels(host,map,field,record,keys){
 host.replaceChildren();if(!field||!record||!keys.length)return;
 keys=keys.filter(k=>k!=='precipitation'||keys.length===1);
 const rect=map.getContainer().getBoundingClientRect(),obstacles=[...map.getContainer().querySelectorAll('.map-place-name,.geo-label.place,.region-name')].map(el=>el.getBoundingClientRect());
 const size=map.getSize(),cols=Math.max(1,Math.floor(size.x/190)),rows=Math.max(1,Math.floor(size.y/(keys.length>4?155:125))),cw=size.x/cols,ch=size.y/rows;
 // At most 32 indicators/window; pointer-transparent so map authoring remains usable.
 for(let row=0;row<rows;row++)for(let col=0;col<cols;col++){
  if(host.childElementCount>=32)break;const x=(col+.5)*cw;let y=(row+.5)*ch;if(map.getContainer().querySelector('.scenario-weather-legend')&&x>size.x-250&&y>size.y-120)continue;
  if(obstacles.some(o=>Math.abs((o.left+o.right)/2-rect.left-x)<115&&Math.abs((o.top+o.bottom)/2-rect.top-y)<45))y=Math.min(size.y-42,y+48);const p=map.containerPointToLatLng([x,y]);
  const values=keys.map(k=>[k,sampleScalar(field,record,k,p.lat,p.lng)]);if(!values.some(([,v])=>Number.isFinite(v)))continue;
  const card=document.createElement('div');card.className='weather-site';card.style.left=x+'px';card.style.top=y+'px';card.dataset.lat=p.lat;card.dataset.lon=p.lng;card.dataset.at=record.at;
  for(const [key,v] of values){const line=document.createElement(key==='temperature'?'strong':'span'),[label,unit]=short[key];line.dataset.variable=key;line.dataset.value=v;line.textContent=(label?label+' ':'')+(Number.isFinite(v)?n(v)+' '+unit:'n/d');card.append(line);}
  host.append(card);
 }
}
export function labelSurface(map){const pane='weatherReadings';if(!map.getPane(pane)){map.createPane(pane);map.getPane(pane).style.zIndex=550;map.getPane(pane).style.pointerEvents='none';}return L.DomUtil.create('div','weather-sites',map.getPane(pane));}
export function positionLabels(host,map){L.DomUtil.setPosition(host,map.containerPointToLayerPoint([0,0]));}
// Low winds retain their direction but are visually amplified; calm has no flow.
export function windGain(speed){return speed<.1?0:Math.max(22,48/speed);}
export function rainLegend(host){const el=document.createElement('div');el.className='rain-scale';const title=document.createElement('span');title.textContent='Pioggia · mm nell’ora successiva';el.append(title);for(const c of rainClasses){const part=document.createElement('span'),dot=document.createElement('i');dot.style.background='rgb('+c.color.join(',')+')';part.append(dot,document.createTextNode(c.label));el.append(part);}host.append(el);}
