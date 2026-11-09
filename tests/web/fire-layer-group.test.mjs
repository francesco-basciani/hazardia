import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const nodes=[];class Element extends EventTarget{constructor(tag){super();this.tag=tag;this.children=[];this.dataset={};this.attrs={};this.checked=false;this._value='';nodes.push(this);}append(...cs){for(const c of cs){this.children.push(c);c.parent=this;}}setAttribute(k,v){this.attrs[k]=v;}get value(){return this._value||this.children[0]?.value||'';}set value(v){this._value=v;}closest(tag){return this.parent?.tag===tag?this.parent:this.parent?.closest(tag);}}
globalThis.document={createElement:t=>new Element(t),createTextNode:text=>({textContent:text})};globalThis.Option=class extends Element{constructor(t,v){super('option');this.textContent=t;this.value=v;}};
const code=readFileSync(new URL('../../src/hazardia/web/static/fire-layer-group.js',import.meta.url),'utf8');const {createFireLayerGroup}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const visible=new Set(),entries=[],unloads=[];let master;const child=id=>{const panel=new Element('section'),label=new Element('label'),input=new Element('input');label.append(input);panel.append(label);input.addEventListener('change',()=>input.checked?visible.add(id):visible.delete(id));return {panel,input};};
const e=child('effis'),w=child('wii');const g=createFireLayerGroup({map:{on:(event,fn)=>unloads.push(fn)},entry:(name,node,icon,input)=>{entries.push(name);master=input;},refresh:()=>{}},e.panel,e.input);
assert.deepEqual(entries,['Incendi']);g.addWii(w.panel,w.input);assert.deepEqual(entries,['Incendi']);assert.equal(visible.size,0);
const mode=nodes.find(n=>n.attrs['aria-label']==='Visualizzazione incendi');assert.equal(mode.value,'wii','default WII when available');master.checked=true;master.onchange();assert.deepEqual([...visible],['wii']);
g.select('effis');assert.deepEqual([...visible],['effis']);assert(w.panel.hidden);assert(!e.panel.hidden);
master.checked=false;master.onchange();assert.equal(visible.size,0);g.select('wii');assert.equal(visible.size,0);
master.checked=true;master.onchange();assert.deepEqual([...visible],['wii']);e.input.checked=true;e.input.dispatchEvent(new Event('change'));assert.equal(mode.value,'effis');assert.deepEqual([...visible],['effis']);
master.checked=false;master.onchange();assert(!w.input.checked&&!e.input.checked);unloads.forEach(f=>f());master.checked=true;master.onchange();assert.equal(visible.size,0);
console.log('PASS one Incendi entry, dynamic WII attachment/default, exclusive EFFIS/WII views, external inspection sync, parent off and unload');
