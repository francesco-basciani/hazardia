import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
class Element extends EventTarget{
 constructor(tag){super();this.tag=tag;this.children=[];this.dataset={};this.value='';this.attrs={};}
 append(...items){this.children.push(...items);if(this.tag==='select'&&!this.value)this.value=this.children[0]?.value;}
 setAttribute(k,v){this.attrs[k]=v;}
 getClientRects(){return [{}];}
}
globalThis.document=Object.assign(new EventTarget(),{hidden:false,createElement:tag=>new Element(tag)});
globalThis.window=Object.assign(new EventTarget(),{frameElement:null});
let id=0;const frames=new Map();globalThis.requestAnimationFrame=fn=>{frames.set(++id,fn);return id;};globalThis.cancelAnimationFrame=id=>frames.delete(id);
const step=t=>{const callbacks=[...frames.values()];frames.clear();callbacks.forEach(fn=>fn(t));};
const {forecastPlayback}=await import('data:text/javascript;base64,'+Buffer.from(readFileSync('src/hazardia/web/static/forecast-playback.js','utf8')).toString('base64'));
const times=['2026-10-23T14:00:00Z','2026-10-23T15:00:00Z','2026-10-23T16:00:00Z'];let current=times[0],active=true;const ticks=[];
const select=new Element('select'),mount=new Element('div');const player=forecastPlayback({select,mount,getTimes:()=>times,getCurrent:()=>current,active:()=>active,onTime:(at,phase)=>{current=at;ticks.push({at,phase});}});
const [title,back,play,next,slider]=player.element.children;
assert.equal(title.textContent,'Previsioni e criticità');assert.equal(play.disabled,false);play.onclick();step(0);step(750);assert.equal(current,'2026-10-23T14:30:00.000Z');assert.equal(select.value,'');assert.equal(ticks.at(-1).phase.fraction,.5);
play.onclick();const paused=current;step(1100);assert.equal(current,paused);assert.equal(play.attrs['aria-pressed'],'false');
play.onclick();step(1200);step(1575);assert(Date.parse(current)>Date.parse(paused));assert.equal(player.element.dataset.at,current);
player.stop();next.onclick();assert.equal(current,times[1]);back.onclick();assert.equal(current,times[0]);
play.onclick();step(2000);active=false;step(2500);assert.equal(play.attrs['aria-pressed'],'false');assert.equal(current,times[0]);
active=true;times.splice(1,1);player.sync();slider.value=.5;slider.oninput();assert.equal(current,times[0]);assert.equal(player.element.dataset.fraction,'0');
times.splice(0);player.sync();assert(play.disabled);assert.equal(player.element.dataset.at,current);
console.log('PASS shared playback: continuous clock, no weather-select dependency, pause/resume, reverse/seek, inactive view, no interpolation across gaps and empty horizon');
