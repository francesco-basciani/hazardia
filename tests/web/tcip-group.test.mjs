import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const nodes=[];
class Element extends EventTarget{
 constructor(tag){super();this.tag=tag;this.dataset={};this.children=[];this.checked=false;this.hidden=false;this.attrs={};this._value='';nodes.push(this);}
 append(...children){for(const child of children){child.parent=this;this.children.push(child);}}
 setAttribute(k,v){this.attrs[k]=v;}
 get value(){return this._value||this.children[0]?.value||'';}
 set value(v){this._value=v;}
 closest(tag){return this.parent?.tag===tag?this.parent:this.parent?.closest(tag);}
 querySelector(selector){return this.children.find(x=>selector==='button[data-tcip-total]'&&x.dataset?.tcipTotal);}
 click(){this.onclick?.();}
}
globalThis.document={createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})};
globalThis.Option=class extends Element{constructor(label,value){super('option');this.textContent=label;this.value=value;}};
const source=readFileSync(new URL('../../src/hazardia/web/static/tcip-group.js',import.meta.url),'utf8');
const {attachTcipGroup}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const children=[],visible=new Set(),unload=[],registrations=[];let master,panel,refreshes=0;
const views=['rates','documents','regional','archive'].map(id=>({id,label:id,attach({entry,refresh}){
 const node=new Element('section'),input=new Element('input'),label=new Element('label');label.append(input);node.append(label);
 const child={id,node,input,label,loads:0,cancels:0};children.push(child);
 input.onchange=()=>{child.loads++;if(input.checked)visible.add(id);else{child.cancels++;visible.delete(id);}};
 input.addEventListener('change',()=>input.onchange());
 const preset=new Element('button');preset.dataset.tcipTotal='true';preset.onclick=()=>{child.reset=true;input.checked=true;input.dispatchEvent(new Event('hazardia-state'));input.onchange();};node.append(preset);
 entry('legacy '+id,node,'x',input);refresh();
}}));
attachTcipGroup({map:{on:(event,fn)=>unload.push(fn)},entry:(name,node,_icon,input)=>{registrations.push(name);master=input;panel=node;},refresh:()=>refreshes++},views);
assert.deepEqual(registrations,['TCIP']);assert.equal(refreshes,1);assert.equal(panel.dataset.revealOnActivate,'true');assert.equal(visible.size,0);
const mode=nodes.find(x=>x.attrs['aria-label']==='Visualizzazione TCIP');assert.equal(mode.value,'rates');assert(children.every(x=>x.label.hidden));
master.checked=true;master.onchange();assert.deepEqual([...visible],['rates']);
mode.value='documents';mode.onchange();assert.deepEqual([...visible],['documents']);assert(children[0].node.hidden);assert(!children[1].node.hidden);assert(children[0].cancels>0);
master.checked=false;master.onchange();assert.equal(visible.size,0);
mode.value='archive';mode.onchange();assert.equal(visible.size,0,'choosing an option cannot enable a disabled parent');
master.checked=true;master.onchange();assert.deepEqual([...visible],['archive']);
let syncs=0;master.addEventListener('hazardia-state',()=>syncs++);
const reset=nodes.find(x=>x.textContent==='Totale reati · tutto il DB · massimo dettaglio');reset.click();assert.equal(mode.value,'rates');assert(master.checked);assert(children[0].reset);assert.deepEqual([...visible],['rates']);assert(syncs>0);
// A child preset is still owned by the single parent visibility switch.
children[2].input.checked=true;children[2].input.dispatchEvent(new Event('hazardia-state'));children[2].input.onchange();assert.equal(mode.value,'regional');assert.deepEqual([...visible],['regional']);
master.checked=false;master.onchange();assert.equal(visible.size,0);assert(children.every(x=>!x.input.checked));
unload.forEach(f=>f());master.checked=true;master.onchange();assert.equal(visible.size,0);
console.log('PASS one TCIP entry; default rates; exclusive nested views; parent disable clears all; presets/reset synchronize master; no activation after unload');
