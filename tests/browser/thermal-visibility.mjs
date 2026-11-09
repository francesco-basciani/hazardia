import assert from 'node:assert/strict';import fs from 'node:fs';
const {bindThermalVisibility}=await import('data:text/javascript;base64,'+Buffer.from(fs.readFileSync(new URL('../../src/hazardia/web/static/thermal-visibility.js',import.meta.url))).toString('base64'));
const master=new EventTarget(),selection=new EventTarget();master.checked=false;selection.checked=true;
let loads=0,clears=0;const binding=bindThermalVisibility(master,selection,()=>loads++,()=>clears++);
assert.equal(loads,0);assert.equal(clears,0);
master.checked=true;master.dispatchEvent(new Event('hazardia-state'));assert.equal(loads,1);
master.dispatchEvent(new Event('change'));assert.equal(loads,1);
// Background switches trigger parent synchronization but must not reload or hide points.
for(let i=0;i<6;i++)master.dispatchEvent(new Event('hazardia-state'));
assert.equal(loads,1);assert.equal(clears,0);
selection.checked=false;selection.dispatchEvent(new Event('change'));assert.equal(clears,1);assert(master.checked);
selection.checked=true;selection.dispatchEvent(new Event('change'));assert.equal(loads,2);
master.checked=false;master.dispatchEvent(new Event('change'));assert.equal(clears,2);
selection.checked=false;selection.dispatchEvent(new Event('change'));assert.equal(loads,2);
master.checked=true;master.dispatchEvent(new Event('change'));assert.equal(loads,2);
selection.checked=true;selection.dispatchEvent(new Event('change'));assert.equal(loads,3);
binding.dispose();assert.equal(clears,3);binding.dispose();master.dispatchEvent(new Event('change'));assert.equal(loads,3);
console.log('PASS parent/selection/default state, background switches, deduplication and disposal');
