import {withI18n} from "./i18n-fixture.mjs";
import {readFileSync} from 'node:fs';import assert from 'node:assert/strict';
const uri=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');const sample=await import(uri(withI18n(readFileSync('src/hazardia/web/static/weather-sampling.js','utf8'))));
let checks=0,calls=0,pan=0;const check=v=>{assert.ok(v);checks++;};const field={lats:[-2,0,2],lons:[-4,0,4]},record={temperature:[1,2,3,4,5,6,7,8,9]};
const map={getBounds:()=>({getSouth:()=>-3,getWest:()=>-5+pan,getNorth:()=>3,getEast:()=>5+pan}),containerPointToLatLng:([x,y])=>{calls++;return{lat:3-y/10,lng:-5+x/10+pan};}};
const cols=100,rows=60,plan=sample.screenSamplePlan(map,field,cols,rows,1,1);const projected=calls;check(projected===6000);
check(sample.screenSamplePlan(map,field,cols,rows,1,1)===plan);check(calls===projected);
for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const p=map.containerPointToLatLng([x+.5,y+.5]),a=sample.sampleScalar(field,record,'temperature',p.lat,p.lng),b=sample.plannedScalar(plan,record.temperature,y*cols+x);check(a===null?b===null:Math.abs(a-b)<1e-12);}
const i=30*cols+50;check(sample.plannedScalar(plan,record.temperature,i)!==sample.plannedScalar(plan,record.temperature.map(v=>v+2),i));
check(sample.plannedScalar(plan,[NaN,...record.temperature.slice(1)],0)===null);
pan=1;check(sample.screenSamplePlan(map,field,cols,rows,1,1)!==plan);
const fine=sample.screenSamplePlan(map,field,cols,rows,1,1,0,'wind-fine');check(fine!==plan);check(sample.plannedScalar(null,record.temperature,i)===null);
console.log(`PASS ${checks} checks: exact bilinear equivalence, no extrapolation, changing values, geometry reuse, pan invalidation and separate wind plans`);
// Development DOM fixture: update text in place instead of recreating every label.
class Element{constructor(){this.children=[];this.dataset={};this.style={};}append(...nodes){for(const n of nodes){n.parent=this;this.children.push(n);}}replaceChildren(...nodes){this.children=[];this.append(...nodes);}remove(){if(this.parent)this.parent.children.splice(this.parent.children.indexOf(this),1);}get lastElementChild(){return this.children.at(-1);}}
globalThis.document={createElement:()=>new Element()};const display=await import(uri(withI18n(readFileSync('src/hazardia/web/static/weather-display.js','utf8')).replace("'/weather-sampling.js'",JSON.stringify(uri(withI18n(readFileSync('src/hazardia/web/static/weather-sampling.js','utf8')))))));
const host=new Element(),labelMap={getSize:()=>({x:380,y:250}),getContainer:()=>({getBoundingClientRect:()=>({left:0,top:0}),querySelectorAll:()=>[],querySelector:()=>null}),containerPointToLatLng:()=>({lat:0,lng:0})};
display.weatherLabels(host,labelMap,field,{...record,at:'2026-10-21T06:00:00Z'},['temperature']);const first=host.children[0];check(host.children.length===4);
display.weatherLabels(host,labelMap,field,{temperature:record.temperature.map(v=>v+2),at:'2026-10-21T07:00:00Z'},['temperature']);check(host.children[0]===first);check(host.dataset.createdLabels==='4');check(first.children[0].textContent==='7 °C');
display.weatherLabels(host,labelMap,field,null,['temperature']);check(host.children.length===0);
console.log(`PASS ${checks} total checks including retained DOM nodes, changed values and missing-data clearing`);

// Clouds and rain remain independently composited; no wet pixel invented in dry cells.
const rasterMap={getSize:()=>({x:20,y:20}),getBounds:()=>({getSouth:()=>-1,getWest:()=>-1,getNorth:()=>1,getEast:()=>1}),containerPointToLatLng:([x,y])=>({lat:1-y/10,lng:-1+x/10})};
const context={canvas:{width:2,height:2,dataset:{}},createImageData:(w,h)=>({width:w,height:h,data:new Uint8ClampedArray(w*h*4)}),putImageData(im){this.image=im;}};
const wetRecord={precipitation:Array(9).fill(4),cloud:Array(9).fill(80)};
check(display.paintRain(context,rasterMap,field,wetRecord,{rain:true,cloud:true})===1);check(context.canvas.dataset.wetPixels==='4');check(context.canvas.dataset.cloudPixels==='4');
const bothAlpha=context.image.data[3];display.paintRain(context,rasterMap,field,wetRecord,{rain:false,cloud:true});check(context.canvas.dataset.wetPixels==='0');check(context.canvas.dataset.cloudPixels==='4');
display.paintRain(context,rasterMap,field,{...wetRecord,precipitation:Array(9).fill(0)},{rain:true,cloud:true});check(context.canvas.dataset.wetPixels==='0');check(context.canvas.dataset.cloudPixels==='4');check(context.image.data[3]<bothAlpha);
display.paintRain(context,rasterMap,field,wetRecord,{rain:true,cloud:false});check(context.canvas.dataset.wetPixels==='4');check(context.canvas.dataset.cloudPixels==='0');
console.log(`PASS ${checks} total checks including independent cloud/rain compositing and dry-cell semantics`);
