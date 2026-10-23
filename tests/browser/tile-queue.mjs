import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const {tileQueue}=await import('data:text/javascript;base64,'+Buffer.from(readFileSync('src/hazardia/web/static/tile-queue.js')).toString('base64'));
const q=tileQueue(2),started=[],release={};const add=(name,owner)=>q.add(owner,done=>{started.push(name);release[name]=done;});
const c1=add('a1','a'),c2=add('a2','a'),c3=add('a3','a'),c4=add('b1','b'),c5=add('b2','b');
assert.deepEqual(started,['a1','a2']);assert.equal(q.status().active,2);c3();release.a1();assert.deepEqual(started,['a1','a2','b1']);release.a2();assert.equal(q.status().active,2);assert.deepEqual(started,['a1','a2','b1','b2']);c4();c4();assert.equal(q.status().active,1);release.b1();assert.equal(q.status().active,1);release.b2();assert.equal(q.status().active,0);assert.equal(q.status().queued,0);assert.equal(q.status().peak,2);assert.ok(!started.includes('a3'));
const fair=tileQueue(1),order=[],ends={};for(const [id,owner] of [['a0','a'],['a1','a'],['a2','a'],['b1','b'],['c1','c']])fair.add(owner,done=>{order.push(id);ends[id]=done;});ends.a0();assert.equal(order.at(-1),'b1');ends.b1();assert.equal(order.at(-1),'a1');ends.a1();assert.equal(order.at(-1),'c1');ends.c1();ends.a2();assert.equal(fair.status().active,0);
console.log('PASS15 queue checks: limit, cancellation, fairness, release-once');
