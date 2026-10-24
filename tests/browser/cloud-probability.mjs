import {readFileSync} from 'node:fs';import assert from 'node:assert/strict';
const uri=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const sampler=uri(readFileSync('src/hazardia/web/static/weather-sampling.js','utf8'));
const display=await import(uri(readFileSync('src/hazardia/web/static/weather-display.js','utf8').replace("'/weather-sampling.js'",JSON.stringify(sampler))));
const {weatherAt}=await import(uri(readFileSync('src/hazardia/web/static/weather-interpolation.js','utf8')));
let checks=0;const check=(v)=>{assert.ok(v);checks++;};
check(display.cloudOpacity(0)===0);check(display.cloudOpacity(100)>.34&&display.cloudOpacity(100)<.75);
check(display.cloudOpacity(25)<display.cloudOpacity(50)&&display.cloudOpacity(50)<display.cloudOpacity(75));
check(JSON.stringify(display.cloudColor(25))!==JSON.stringify(display.cloudColor(75)));check(display.cloudColor(null)===null);
const record={at:'2026-10-20T12:00:00Z',rain_probability:[20,40,60,80],precipitation:[0,0,0,0],cloud:[75,75,75,75]},next={...record,at:'2026-10-20T13:00:00Z',rain_probability:[40,60,80,100]};
check(weatherAt([record,next],'2026-10-20T12:30:00Z').rain_probability[0]===30);
check(weatherAt([{at:record.at},{at:next.at}],'2026-10-20T12:30:00Z').rain_probability===undefined);
const field={lats:[0,1],lons:[0,1]},map={getSize:()=>({x:8,y:8}),containerPointToLatLng:()=>({lat:.5,lng:.5})};let image;
const ctx={canvas:{width:1,height:1,dataset:{}},createImageData:()=>({width:1,height:1,data:new Uint8ClampedArray(4)}),putImageData:x=>image=x};
check(display.paintRain(ctx,map,field,record,{rain:false,cloud:true})===1);check(image.data[3]>100&&image.data[3]<200);check(ctx.canvas.dataset.cloudPixels==='1'&&ctx.canvas.dataset.wetPixels==='0');
display.paintRain(ctx,map,field,{...record,cloud:[0,0,0,0]},{rain:false,cloud:true});check(image.data[3]===0);
display.paintRain(ctx,map,field,record,{rain:false,cloud:false});check(image.data[3]===0);
console.log(`PASS ${checks} checks: distinct cloud colours, stronger transparent alpha, clear sky, toggles, probability interpolation and missing legacy data`);

// Probability is a separate real field, not inferred from cloud cover or millimetres.
const probable={...record,rain_probability:[80,80,80,80],precipitation:[0,0,0,0],cloud:[90,90,90,90]};
display.paintRain(ctx,map,field,probable,{rain:false,probability:true,cloud:false});check(ctx.canvas.dataset.probabilityPixels==='1');check(ctx.canvas.dataset.wetPixels==='0');check(ctx.canvas.dataset.cloudPixels==='0');const probabilityPixel=[...image.data];check(probabilityPixel[3]>0);
display.paintRain(ctx,map,field,probable,{rain:false,probability:false,cloud:true});check(ctx.canvas.dataset.probabilityPixels==='0');check(ctx.canvas.dataset.cloudPixels==='1');check(JSON.stringify([...image.data])!==JSON.stringify(probabilityPixel));
display.paintRain(ctx,map,field,probable,{rain:false,probability:true,cloud:true});check(ctx.canvas.dataset.probabilityPixels==='1'&&ctx.canvas.dataset.cloudPixels==='1'&&ctx.canvas.dataset.wetPixels==='0');
display.paintRain(ctx,map,field,{...probable,rain_probability:undefined},{rain:false,probability:true,cloud:false});check(image.data[3]===0);check(ctx.canvas.dataset.probabilityPixels==='0');
for(const [_,color] of display.cloudStops)check(Math.max(...color)-Math.min(...color)<=32);
check(display.probabilityColor(0)===null);check(display.probabilityOpacity(null)===0);check(display.probabilityOpacity(90)>display.probabilityOpacity(10));check(display.cloudOpacity(0)===0);
console.log(`PASS ${checks} total weather-semantics checks: real probability/rain independence, neutral clouds, combination and absent data`);
