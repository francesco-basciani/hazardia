/* Controlled adapter test: real UI module, synthetic responses; not source/physics evidence. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const uri=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const read=name=>readFileSync(new URL('../../src/hazardia/web/static/'+name,import.meta.url),'utf8');
class Element{
 constructor(tag,text=''){this.tagName=tag.toUpperCase();this.children=[];this.attributes={};this.dataset={};this.style={};this._text=text;this.value='';this.listeners={};}
 append(...nodes){for(const node of nodes){this.children.push(node);node.parentElement=this;if(this.tagName==='SELECT'&&this.children.length===1)this.value=node.value;}}
 insertBefore(node,before){const i=this.children.indexOf(before);if(i<0)throw Error('Missing DOM insertion reference');this.children.splice(i,0,node);node.parentElement=this;}
 replaceChildren(...nodes){this.children=[];this._text='';this.append(...nodes);}
 set textContent(v){this._text=v;this.children=[];}get textContent(){return this._text+this.children.map(n=>n.textContent).join('');}
 querySelector(selector){return this.children.flatMap(n=>[n,...nodes(n).slice(1)]).find(n=>n.tagName===selector.toUpperCase());}
 setAttribute(k,v){this.attributes[k]=v;}addEventListener(k,fn){this.listeners[k]=fn;}dispatchEvent(e){this.listeners[e.type]?.(e);}
}
globalThis.document={addEventListener(){},createElement:tag=>new Element(tag),createTextNode:text=>new Element('#text',text)};
globalThis.Option=class extends Element{constructor(text,value){super('option',text);this.value=String(value);}};
globalThis.CustomEvent=class{constructor(type,options={}){this.type=type;Object.assign(this,options);}};
globalThis.window={addEventListener(){}};
const group=()=>({clearLayers(){},addTo(){return this;},remove(){}});
globalThis.L={canvas(){},layerGroup:group,control:()=>({addTo(m){this.onAdd(m);}}),DomUtil:{create:tag=>new Element(tag)},geoJSON:()=>({addTo(){}})};
let now=Date.parse('2026-10-26T12:00:00Z');Date.now=()=>now;
let tasks=[],requests=[];globalThis.setTimeout=(fn,ms)=>{const id={fn,at:now+ms};tasks.push(id);return id;};globalThis.clearTimeout=id=>{tasks=tasks.filter(t=>t!==id);};
globalThis.fetch=(path,options)=>new Promise(resolve=>requests.push({path,body:JSON.parse(options.body),resolve}));
const bounds={getWest:()=>13,getSouth:()=>42,getEast:()=>14,getNorth:()=>43,contains:()=>true};
const container=new Element('div'),map={getContainer:()=>container,getBounds:()=>bounds,getCenter:()=>({lat:42.5,lng:13.5}),createPane(){},getPane:()=>({style:{}}),on(){},fire(){},attributionControl:{addAttribution(){}}};
let source=read('observed-layers.js').replace('import {locale} from "/i18n.js";',"const locale=()=> 'it-IT';").replace("from '/observed-layer-model.js'",'from '+JSON.stringify(uri(read('observed-layer-model.js')))).replace("from '/observed-layer-time.js'",'from '+JSON.stringify(uri(read('observed-layer-time.js')))).replace("import {mapSymbols} from '/map-symbols.js?v=1';",'const mapSymbols=()=>({set(){}});');
const {observedLayer}=await import(uri(source)),host=new Element('section');observedLayer(map,host,'earthquakes');
const nodes=(root=host)=>[root,...root.children.flatMap(n=>nodes(n))],find=label=>nodes().find(e=>e.attributes['aria-label']===label),check=nodes().find(e=>e.id==='earthquakes-enabled'),box=host.children[0];
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
const advance=async(ms)=>{now+=ms;const due=tasks.filter(t=>t.at<=now);tasks=tasks.filter(t=>t.at>now);for(const t of due)t.fn();await flush();};
const snapshot=body=>({status:'READY',type:'FeatureCollection',bounds:body.bounds,acquired_at:new Date(now).toISOString(),quality:{provider:body.provider,min_magnitude:body.min_magnitude,window_start:new Date(now-body.days*86400000).toISOString(),window_end:new Date(now).toISOString(),license:'SYNTHETIC_TEST_ONLY'},features:[1,2,3].filter(m=>m>=body.min_magnitude).map(m=>({type:'Feature',id:String(m),geometry:{type:'Point',coordinates:[13.5,42.5]},properties:{event_type:'earthquake',magnitude:m,at:new Date(now).toISOString(),place:'Synthetic test '+m}}))});
const answer=async r=>{r.resolve({ok:true,json:async()=>snapshot(r.body)});await flush();};
// Activation alone requests data; no manual update/load action is present.
assert(!nodes().some(e=>e.tagName==='BUTTON'&&/aggiorna|carica|mostra e/i.test(e.textContent)));
check.checked=true;check.onchange();await flush();assert.equal(requests.length,1);assert.equal(box.dataset.acquisitionStatus,'LOADING');
// An in-flight old response cannot apply after a newer selection.
find('Magnitudo minima').value='3';find('Magnitudo minima').onchange();find('Magnitudo minima').value='1';find('Magnitudo minima').onchange();await answer(requests[0]);assert.notEqual(box.dataset.acquisitionStatus,'READY');await advance(6000);assert.equal(requests.length,2);assert.equal(requests[1].body.min_magnitude,1);await answer(requests[1]);assert.equal(container.dataset.earthquakesRendered,'3');
// Narrowing a complete snapshot updates synchronously and does not fetch.
find('Magnitudo minima').value='3';find('Magnitudo minima').onchange();assert.equal(container.dataset.earthquakesRendered,'1');assert.equal(requests.length,2);assert(!box.textContent.includes('Synthetic test 1'));
find('Magnitudo minima').value='1';find('Magnitudo minima').onchange();assert.equal(container.dataset.earthquakesRendered,'3');assert.equal(requests.length,2);
// Rapid period changes likewise retain only the latest result.
find('Periodo osservazioni').value='1';find('Periodo osservazioni').onchange();await advance(6000);assert.equal(requests[2].body.days,1);find('Periodo osservazioni').value='7';find('Periodo osservazioni').onchange();await answer(requests[2]);assert.notEqual(box.dataset.acquisitionStatus,'READY');await advance(6000);assert.equal(requests[3].body.days,7);await answer(requests[3]);assert.equal(box.dataset.acquisitionStatus,'READY');
// Disabled layers remain network-idle even if their filters change.
check.checked=false;check.onchange();find('Periodo osservazioni').value='30';find('Periodo osservazioni').onchange();await advance(6000);assert.equal(requests.length,4);assert.equal(container.dataset.earthquakesRendered,'0');
console.log('PASS automatic activation, no load button, immediate map/list filtering, complete-cache reuse, obsolete responses rejected, latest period wins and disabled-layer network silence; synthetic adapter test');
