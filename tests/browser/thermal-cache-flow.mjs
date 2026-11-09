import assert from 'node:assert/strict';import fs from 'node:fs';
class Element extends EventTarget{
 constructor(tag){super();this.tag=tag;this.children=[];this.dataset={};this.attrs={};this.checked=false;this.value='';this.style={};this.textContent='';}
 get value(){return this._value||(this.tag==='select'?this.children[0]?.value:'')||'';}set value(v){this._value=v;}
 prepend(...items){for(const n of items.reverse()){this.children.unshift(n);n.parent=this;}}
 append(...items){for(const n of items){this.children.push(n);n.parent=this;}}setAttribute(k,v){this.attrs[k]=v;}
 closest(tag){return this.parent?.tag===tag?this.parent:this.parent?.closest(tag);}
 querySelector(selector){return this.children.find(n=>n.tag==='input')||this.children.map(n=>n.querySelector?.(selector)).find(Boolean);}
 after(n){const a=this.parent.children,index=a.indexOf(this);a.splice(index+1,0,n);n.parent=this.parent;}
}
const events=new EventTarget();globalThis.document={createElement:t=>new Element(t),createTextNode:text=>({textContent:text}),addEventListener:events.addEventListener.bind(events),removeEventListener:events.removeEventListener.bind(events),body:{dataset:{view:'map'}},hidden:false};
globalThis.Option=class extends Element{constructor(t,v){super('option');this.textContent=t;this.value=v;}};
const dataset={},unloads=[],map={createPane(){},getPane:()=>({style:{}}),getContainer:()=>({dataset}),getBounds:()=>({contains:()=>true}),on(event,fn){if(event==='unload')unloads.push(fn);}};
globalThis.L={canvas:()=>({}),layerGroup:()=>({clearLayers(){},addTo(){return this;}}),circleMarker:()=>({bindPopup(){return this;},addTo(){return this;}})};
const uri=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const visibility=uri(fs.readFileSync(new URL('../../src/hazardia/web/static/thermal-visibility.js',import.meta.url),'utf8'));
let code=fs.readFileSync(new URL('../../src/hazardia/web/static/satellite-observations.js',import.meta.url),'utf8');
code=code.replace("import {getLanguage,locale} from '/i18n.js';","const getLanguage=()=> 'en',locale=()=> 'en-GB';").replace("import {bindThermalVisibility} from '/thermal-visibility.js';","import {bindThermalVisibility} from '"+visibility+"';").replace("import {mapSymbols} from '/map-symbols.js';","const mapSymbols=()=>({set(){}});").replace("import {monitorTimeline} from '/monitor-timeline.js';","const monitorTimeline={at:new Date().toISOString()};");
const data={features:[{id:'observed',geometry:{coordinates:[13,42]},properties:{at:new Date(Date.now()-3600000).toISOString(),frp_mw:4,satellite:'NOAA-20',confidence:'n'}}],acquired_at:new Date().toISOString(),region:'Europe',observation_until:new Date(Date.now()-3600000).toISOString()};
const calls=[];globalThis.fetch=async(url)=>{calls.push(url);if(url==='/api/wii/status')return {ok:true,json:async()=>({enabled:false})};if(url.includes('/refresh'))return {ok:false,status:429};return {ok:true,json:async()=>({data,busy:false})};};
const panel=new Element('section'),label=new Element('label'),master=new Element('input');label.append(master);panel.append(label);master.checked=true;
const {attachObservations}=await import(uri(code));attachObservations({map,entry:()=>{},refresh:()=>{},fireLayer:{panel}});
await new Promise(setImmediate);assert.equal(dataset.thermalStations,'1','cached points retained on refresh HTTP429');
const satelliteBox=panel.children[1],selection=satelliteBox.querySelector('input');assert.equal(selection.checked,true);
const status=satelliteBox.children.find(n=>n.attrs?.role==='status');assert.match(status.textContent,/cached observations/);
const before=calls.length;master.dispatchEvent(new Event('hazardia-state'));await new Promise(setImmediate);assert.equal(calls.length,before,'view synchronization does not acquire again');
const future=new Event('hazardia-monitor-time');future.detail={at:new Date(Date.now()+86400000).toISOString()};events.dispatchEvent(future);assert.equal(dataset.thermalStations,'0');assert.match(status.textContent,/Future time/);
master.checked=false;master.dispatchEvent(new Event('change'));assert.equal(dataset.thermalStations,'0');unloads.forEach(fn=>fn());
console.log('PASS actual observation module: attached checkbox, cached points on refresh failure, no reload on view sync, future hidden, parent off');
