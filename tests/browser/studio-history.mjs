import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const code=readFileSync('src/hazardia/web/static/studio-history.js','utf8');
const {authoringHistory}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const state=(n,name='Reference')=>({scenarios:[{id:'a',name,input:{ignitions:[{point:[42,n]}],resources:[]}}],selectedId:'a',compared:['a']});
const h=authoringHistory();h.record(state(1));assert(!h.canUndo);h.record(state(2));assert(h.canUndo);assert.equal(h.undo().scenarios[0].input.ignitions[0].point[1],1);assert(h.canRedo);assert.equal(h.redo().scenarios[0].input.ignitions[0].point[1],2);
h.undo();h.record(state(3));assert(!h.canRedo);assert.equal(h.undo().scenarios[0].input.ignitions[0].point[1],1);
const returned=h.redo();returned.scenarios[0].name='mutated';assert.equal(h.undo().scenarios[0].name,'Reference');assert.equal(h.redo().scenarios[0].name,'Reference');
const group=authoringHistory();group.record(state(1));const two=state(1);two.scenarios.push({id:'b',name:'Alternative',input:{ignitions:[],resources:[{id:'crew'}]}});group.record(two);assert.equal(group.undo().scenarios.length,1);assert.equal(group.redo().scenarios.length,2);
assert(!group.record({...two,selectedId:'b'})); // View changes are not edits.
const bounded=authoringHistory({limit:3});for(let i=0;i<8;i++)bounded.record(state(i));assert.equal(bounded.size,3);assert.equal(bounded.undo().scenarios[0].input.ignitions[0].point[1],6);assert.equal(bounded.undo().scenarios[0].input.ignitions[0].point[1],5);assert.equal(bounded.undo(),null);
const tiny=authoringHistory({maxBytes:400});assert(!tiny.record({scenarios:[{name:'a'.repeat(500)}]}));assert(!tiny.canUndo);
console.log('PASS history: deep snapshots, undo/redo, branch truncation, create/delete, selection excluded, count and byte bounds');
