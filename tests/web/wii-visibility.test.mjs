import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
class Element extends EventTarget{constructor(){super();this.dataset={};this.style={};this.children=[];}setAttribute(){}append(...c){this.children.push(...c);}replaceChildren(...c){this.children=c;}}
globalThis.document={hidden:false,createElement:()=>new Element(),createTextNode:t=>({textContent:t}),getElementById:()=>({hidden:false,getBoundingClientRect:()=>({width:340})})};
const visible=new Set(),fits=[];let poll,toggle,released;globalThis.setInterval=f=>{poll=f;return 1;};globalThis.clearInterval=()=>{};
const map={removeLayer:l=>visible.delete(l),fitBounds:(b,o)=>fits.push(o),on:()=>{}};globalThis.L={canvas:()=>({}),geoJSON:()=>({addTo(){visible.add(this);return this;},getBounds:()=>({})})};
const data={type:'FeatureCollection',features:[{}],metadata:{status:'AVAILABLE',product_id:'v1',created_at:'2026-10-28'},legend:[]};let deferred=false;
globalThis.fetch=async url=>url==='/api/wii/pipeline'?{ok:true,json:async()=>({artifact_id:'v1'})}:deferred?new Promise(resolve=>{released=()=>resolve({ok:true,json:async()=>data});}):{ok:true,json:async()=>data};
const code=readFileSync(new URL('../../src/hazardia/web/static/wii-layer.js',import.meta.url),'utf8');const {attachWiiLayers}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
let legacy=0;attachWiiLayers({map,entry:()=>legacy++,refresh:()=>{},fireLayer:{addWii:(_panel,input)=>toggle=input}},{layers:[]});assert.equal(legacy,0);
toggle.checked=true;await toggle.onchange();assert.equal(visible.size,1);assert.equal(fits.length,1);assert.equal(fits[0].paddingBottomRight[0],365);
await poll();assert.equal(fits.length,1,'poll does not reframe');deferred=true;const pending=toggle.onchange();toggle.checked=false;await toggle.onchange();released();await pending;assert.equal(visible.size,0,'disabled parent cannot receive a late WII layer');
console.log('PASS WII attaches inside Incendi without separate entry; activation frames coverage, polling preserves viewport, disable rejects late response');
