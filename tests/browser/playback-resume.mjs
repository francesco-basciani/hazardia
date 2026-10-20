import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const source=readFileSync('src/hazardia/web/static/fire-studio.js','utf8');
const handlers=source.slice(source.indexOf('function pause(){'),source.indexOf('const restartPlayback='));
function player(code,asyncRender){
 let now=0,id=0;const timers=new Map(),frames=new Map(),errors=[];
 const elements={play:{textContent:'',setAttribute(){}},hour:{value:0,max:72},'play-speed':{value:1000}};
 const deps={elements,errors,asyncRender,performance:{now:()=>now},setTimeout:fn=>{timers.set(++id,fn);return id;},clearTimeout:id=>timers.delete(id),requestAnimationFrame:fn=>{frames.set(++id,fn);return id;},cancelAnimationFrame:id=>frames.delete(id)};
 const api=new Function('d',`const {performance,setTimeout,clearTimeout,requestAnimationFrame,cancelAnimationFrame}=d;
 let playing=null,hour=0,paintedHour=0,renderToken=0;const scenarios=[{}],reducedMotion={matches:false};
 const $=id=>d.elements[id],playableScenarios=()=>scenarios,comparedScenarios=()=>scenarios,dirty=()=>false,result=()=>({frames:[{}]}),nextSample=(_,h)=>(Math.floor((h+1e-8)/.25)+1)*.25,nativeStep=()=>.25;
 const storeView=()=>{},calculationFeedback=()=>{},startComparison=()=>{},message=m=>d.errors.push(m),readyAt=async()=>true;
 function paintVisual(h){hour=paintedHour=h;d.elements.hour.value=h;}
 function renderTimeline(){paintedHour=hour;return d.asyncRender?Promise.resolve(true):true;}
 ${code}
 return {play,pause,state:()=>({hour,playing:!!playing,label:d.elements.play.textContent,errors:[...d.errors]})};`)(deps);
 return {...api,async step(ms=1000){now+=ms;const ts=[...timers.values()];timers.clear();ts.forEach(f=>f());for(let i=0;i<12;i++)await Promise.resolve();const fs=[...frames.values()];frames.clear();fs.forEach(f=>f(now));for(let i=0;i<12;i++)await Promise.resolve();}};
}
let checks=0;
for(const asyncRender of [false,true]){
 const p=player(handlers,asyncRender);p.play();await p.step(0);await p.step(100);const initial=p.state().hour;assert(initial>0);checks++;
 for(let n=0;n<4;n++){
  p.pause();const paused=p.state().hour;await p.step(1000);assert.equal(p.state().hour,paused);checks++;
  p.play();await p.step(0);await p.step(1000);assert(p.state().playing,'resume must survive native sample boundary');assert(p.state().hour>paused,'resume must advance from pause point');assert.deepEqual(p.state().errors,[]);checks+=3;
 }
 p.pause();assert.equal(p.state().playing,false);checks++;
}
// Same actual handlers with the pre-fix call reproduce the cached-render failure.
const old=player(handlers.replace('Promise.resolve(renderTimeline()).then','renderTimeline().then'),false);old.play();await old.step(0);await old.step(1000);assert(!old.state().playing);assert(old.state().errors.some(e=>e.includes('then is not a function')));checks+=2;
console.log(`PASS ${checks} assertions: actual play/pause handlers, sync/async render, repeated resume, stale callbacks, pre-fix negative control`);
