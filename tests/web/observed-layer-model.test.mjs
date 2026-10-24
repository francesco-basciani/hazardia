import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const source=await fs.readFile(new URL('../../src/hazardia/web/static/observed-layer-model.js',import.meta.url),'utf8');
const {powerVisible,powerColor,quakeClasses,quakeStyle,quakeQueryBounds,quakeSnapshotCovers}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const line={power_kind:'line',location:'overhead',max_voltage:132000};
assert.equal(powerVisible(line),true);
assert.equal(powerVisible(line,{minVoltage:220000}),false);
assert.equal(powerVisible({...line,max_voltage:null}),false);
assert.equal(powerVisible({...line,max_voltage:null},{unknown:true}),true);
assert.equal(powerVisible({...line,max_voltage:15000},{unknown:true}),false);
assert.equal(powerVisible({...line,location:'underground'}),false);
assert.equal(powerVisible({...line,power_kind:'cable',location:'underground'},{cables:true}),true);
assert.equal(powerVisible({...line,location:'unknown'}),false);
assert.equal(powerVisible({...line,power_kind:'substation',max_voltage:null},{stations:true}),true);
assert.equal(powerVisible({...line,power_kind:'substation',max_voltage:15000},{stations:true}),false);
assert.equal(powerVisible({...line,power_kind:'tower',max_voltage:null}),false);
assert.equal(powerVisible({...line,power_kind:'tower',max_voltage:null},{towers:true}),true);
assert.equal(powerVisible({...line,power_kind:'generator'}),false);
assert.equal(powerColor(null),'#b5c1ca');
assert.equal(powerColor(132000),'#f4d76a');
assert.equal(powerColor(220000),'#f6a749');
assert.equal(powerColor(380000),'#ef637d');
assert.notEqual(powerColor(35000),powerColor(null));
console.log('PASS18 display-filter checks (not physical qualification)');

for(let m=0;m<9;m+=.25)assert(quakeStyle(m+.25).radius>quakeStyle(m).radius);
assert.equal(new Set(quakeClasses.map(c=>quakeStyle(Number.isFinite(c.min)?c.min:0).fillColor)).size,6);
for(const c of quakeClasses.filter(c=>Number.isFinite(c.min))){assert.equal(quakeStyle(c.min).fillColor,c.color);assert.notEqual(quakeStyle(c.min-.001).fillColor,c.color);}
assert.equal(quakeStyle(null).fillColor,'#8897a3');assert.equal(quakeStyle(NaN).radius,3);assert.equal(quakeStyle(Infinity).radius,3);assert.equal(quakeStyle(20).radius,quakeStyle(9).radius);assert(quakeStyle(-1).radius>0);
console.log('PASS magnitude radius ordering, six exact colour boundaries, missing/nonfinite values, bounds and negative magnitudes; display scale only');

// Aviation consultation preset retains unknown and low-voltage overhead obstacles.
for(const max_voltage of [null,15000,35000,132000,380000])assert.equal(powerVisible({...line,max_voltage},{aerial:true}),true);
for(const location of ['underground','underwater','unknown'])assert.equal(powerVisible({...line,location},{aerial:true}),false);
for(const power_kind of ['tower','pole'])assert.equal(powerVisible({...line,power_kind,max_voltage:null},{aerial:true}),true);
assert.equal(powerVisible({...line,power_kind:'substation'},{aerial:true}),false);
console.log('PASS aerial obstacles preset: all overhead voltages, supports, underground/unknown placement excluded; no flight clearance claim');

// Regression: the empty small Safari snapshot must not cover the zoomed-out view.
const local=[13.26942,42.28315,13.57018,42.408],wide=[10.6,39.8,16.2,43.9],now=Date.parse('2026-10-24T21:20:00Z'),opts={provider:'ingv',days:7,min_magnitude:0};
const snapshot={status:'READY',bounds:local,acquired_at:'2026-10-24T21:16:59Z',features:[],quality:{provider:'ingv',min_magnitude:0,window_start:'2026-10-17T21:10:00Z',window_end:'2026-10-24T21:10:00Z'}};
assert.equal(quakeSnapshotCovers(snapshot,local,opts,now),true); // Empty is valid data.
assert.equal(quakeSnapshotCovers(snapshot,wide,opts,now),false);
assert.deepEqual(quakeQueryBounds(local,true),[12,41,15,43]);
assert.deepEqual(quakeQueryBounds([13.3,42.3,13.6,42.45],true),[12,41,15,43]); // nearby pans share request/cache
assert.equal(quakeSnapshotCovers({...snapshot,bounds:quakeQueryBounds(local,true)},local,opts,now),true);
assert.equal(quakeSnapshotCovers(snapshot,local,{...opts,days:30},now),false);
assert.equal(quakeSnapshotCovers(snapshot,local,{...opts,provider:'usgs'},now),false);
assert.equal(quakeSnapshotCovers(snapshot,local,{...opts,min_magnitude:1},now),false);
assert.equal(quakeSnapshotCovers(snapshot,local,opts,now+600000),false);
assert.equal(quakeSnapshotCovers(snapshot,local,opts,now-600000),false);
assert.equal(quakeSnapshotCovers({...snapshot,status:'ERROR'},local,opts,now),false);
assert.equal(quakeSnapshotCovers(null,local,opts,now),false);
assert.deepEqual(quakeQueryBounds([6.1,35.1,18.9,47.9],true),[6,35,19,48]);
assert.deepEqual(quakeQueryBounds([-179.9,-84.9,179.9,84.9]),[-180,-85,180,85]);
assert.deepEqual(quakeQueryBounds([5,35,19,48],true),[5,35,19,48]); // explicit outside-coverage retained
assert.deepEqual(snapshot.features,[]);assert.deepEqual(snapshot.bounds,local);
console.log('PASS seismic viewport refresh: empty/local vs uncovered, buffered cache area, freshness, filters and source boundaries');
