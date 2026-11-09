import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const clone=value=>JSON.parse(JSON.stringify(value));
const nodes=[];
class Element extends EventTarget {
 constructor(tag){super();this.tag=tag;this.children=[];this.dataset={};this.style={};this.attrs={};this._value='';this.checked=false;this.hidden=false;nodes.push(this);}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this.children=[...children];this._value='';}
 setAttribute(key,value){this.attrs[key]=value;}
 get value(){return this.tag==='select'?(this._value||this.children[0]?.value||''):this._value;}
 set value(value){this._value=this.tag==='select'?(this.children.some(x=>x.value===value)?value:''):value;}
 get options(){return this.children;}
 get selectedIndex(){return this.children.findIndex(x=>x.value===this.value);}
}
globalThis.Option=class extends Element {constructor(text,value){super('option');this.text=this.textContent=text;this.value=value;}};
globalThis.document={hidden:false,createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text}),getElementById:()=>({hidden:false,getBoundingClientRect:()=>({width:340})})};
let poll,clock=0;Date.now=()=>clock;const advance=()=>{clock+=60000;};
globalThis.setInterval=callback=>{poll=callback;return 1;};globalThis.clearInterval=()=>{};
const visible=new Set(),fits=[],requests=[];
const map={removeLayer:l=>visible.delete(l),getZoom:()=>5,getBounds:()=>({getWest:()=>6,getEast:()=>19,getSouth:()=>35,getNorth:()=>48}),fitBounds:(b,o)=>fits.push({b,o}),on:()=>{}};
globalThis.L={geoJSON:data=>({data,addTo(){visible.add(this);return this;},getBounds:()=>({fixture:true}),bringToFront(){}})};
const item={id:'fixture-all',level:'best_available',crime_code:'theft',crime_label:'Furti',aggregation:'cumulative',window:'all',areas:1,period_start:'2024-01-01',period_end:'2024-12-31'};
const catalog={items:[item],crime_types:[{code:'theft',label:'Furti',definition:''}],coverage:{}};
const data={type:'FeatureCollection',features:[{properties:{}}],metadata:{crime_code:'theft',crime_label:'Furti',period_start:item.period_start,period_end:item.period_end,aggregation:'cumulative',reference_year:2024}};
let deferred=null,failNext=false;
globalThis.fetch=async url=>{requests.push(url);if(url==='/api/tcip/local-rates')return {ok:true,json:async()=>clone(catalog)};if(failNext){failNext=false;return {ok:false,json:async()=>({detail:'revoked'})};}if(deferred)return new Promise(resolve=>{deferred.resolve=()=>{deferred=null;resolve({ok:true,json:async()=>clone(data)});};});return {ok:true,json:async()=>clone(data)};};
let code=readFileSync(new URL('../../src/hazardia/web/static/tcip-local-rates.js',import.meta.url),'utf8');
const helper=readFileSync(new URL('../../src/hazardia/web/static/tcip-rate-scale.js',import.meta.url),'utf8');
code=code.replace("from '/tcip-rate-scale.js'","from 'data:text/javascript;base64,"+Buffer.from(helper).toString('base64')+"'");
const {attachLocalRates}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
let toggle,panel;
attachLocalRates({map,entry:(_name,p,_icon,t)=>{panel=p;toggle=t;},refresh:()=>{}});
const settle=()=>new Promise(resolve=>setImmediate(resolve));
await settle();
assert.equal(visible.size,0,'disabled layer does not draw data');assert.equal(requests.length,0,'disabled layer makes no requests');
assert.equal(panel.dataset.revealOnActivate,'true');
toggle.checked=true;await toggle.onchange();
assert.equal(visible.size,1,'activation draws data without the fit button');assert.equal(fits.length,1,'activation automatically frames its coverage');
assert.equal(fits[0].o.paddingBottomRight[0],365,'framing reserves inspector width');
const first=[...visible][0];deferred={};advance();const refreshing=poll();await settle();
assert(visible.has(first),'old layer stays visible while background replacement is pending');const during=requests.length;advance();await poll();assert.equal(requests.length,during,'polling never overlaps an in-flight request');
deferred.resolve();await refreshing;
assert.equal(visible.size,1);assert(!visible.has(first),'fresh data replaces the old layer');assert.equal(fits.length,1,'polling preserves user viewport');
advance();failNext=true;await poll();assert.equal(visible.size,0,'revoked/unavailable data clears immediately after the failed response');
assert(nodes.some(n=>n.attrs.role==='status'&&n.textContent?.includes('TCIP non disponibile')));
assert.match(nodes.find(n=>n.attrs.role==='status').textContent,/tentativo automatico/);const beforeRetry=requests.length;clock+=9999;await poll();assert.equal(requests.length,beforeRetry);clock+=1;await poll();assert.equal(visible.size,1,'recovery retries automatically after ten seconds without user action');
deferred={};advance();const pending=poll();await settle();const release=deferred.resolve;
toggle.checked=false;await toggle.onchange();release();await pending;
assert.equal(visible.size,0,'late response cannot redraw a disabled layer');
toggle.checked=true;await toggle.onchange();
const detail=nodes.find(n=>n.attrs['aria-label']==='Dettaglio tassi locali TCIP');detail.value='neighborhood';await detail.onchange();
assert.equal(visible.size,0,'a filter with no data removes stale polygons');
assert(nodes.some(n=>n.attrs.role==='status'&&n.textContent?.includes('nessun dato territoriale qualificato')));
console.log('PASS activation frames coverage; polling keeps visible data without moving the map; errors, no-data and disable reject stale layers');

// First activation may fail before any coverage has ever been framed.
toggle.checked=false;await toggle.onchange();detail.value='best_available';failNext=true;toggle.checked=true;await toggle.onchange();
const fitsBeforeRecovery=fits.length;clock+=10000;await poll();assert.equal(visible.size,1);assert.equal(fits.length,fitsBeforeRecovery+1,'automatic recovery completes the pending initial framing');
console.log('PASS first-activation outage automatically recovers and frames the returned data');

map.getSize=()=>({x:669});nodes.find(n=>n.textContent==='Inquadra tassi locali').onclick();assert.equal(fits.at(-1).o.paddingBottomRight[0],25,'narrow overlay does not push Italy outside the viewport when zooming');
