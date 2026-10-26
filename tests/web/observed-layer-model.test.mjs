import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const source=await fs.readFile(new URL('../../src/hazardia/web/static/observed-layer-model.js',import.meta.url),'utf8');
const {powerVisible,powerColor,quakeClasses,quakeVisible,quakeStyle,quakeQueryBounds,quakeSnapshotCovers,quakeAcquisitionPlan,combineQuakeSnapshots}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
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
assert.equal(quakeSnapshotCovers(snapshot,local,{...opts,min_magnitude:1},now),true); // Complete broader catalogue supports immediate local filtering.
assert.equal(quakeSnapshotCovers(snapshot,local,{...opts,min_magnitude:-1},now),false);
assert.equal(quakeSnapshotCovers({...snapshot,quality:{...snapshot.quality,limit_reached:true}},local,{...opts,min_magnitude:1},now),false); // Truncated source cannot prove a complete narrower catalogue.
assert.equal(quakeSnapshotCovers({...snapshot,quality:{...snapshot.quality,limit_reached:true}},local,opts,now),true);
assert.equal(quakeSnapshotCovers(snapshot,local,opts,now+600000),false);
assert.equal(quakeSnapshotCovers(snapshot,local,opts,now-600000),false);
assert.equal(quakeSnapshotCovers({...snapshot,status:'ERROR'},local,opts,now),false);
assert.equal(quakeSnapshotCovers(null,local,opts,now),false);
assert.deepEqual(quakeQueryBounds([6.1,35.1,18.9,47.9],true),[6,35,19,48]);
assert.deepEqual(quakeQueryBounds([-179.9,-84.9,179.9,84.9]),[-180,-85,180,85]);
assert.deepEqual(quakeQueryBounds([5,35,19,48],true),[5,35,19,48]); // explicit outside-coverage retained
assert.deepEqual(snapshot.features,[]);assert.deepEqual(snapshot.bounds,local);
console.log('PASS seismic viewport refresh: empty/local vs uncovered, buffered cache area, freshness, filters and source boundaries');

// An Italian view crossing the regional rectangle keeps small INGV events.
const crossing=[8.8,39.5,19.5,44.5],auto={...opts,provider:'auto'},plan=quakeAcquisitionPlan(crossing,auto);
assert.deepEqual(plan.map(p=>p.body.provider),['ingv','usgs']);assert.deepEqual(plan[0].body.bounds,[8,39,19,45]);assert.deepEqual(plan[1].body.bounds,[8,39,20,45]);
assert.deepEqual(quakeAcquisitionPlan(local,auto).map(p=>p.body.provider),['ingv']);assert.deepEqual(quakeAcquisitionPlan([-18,12,-11,17],auto).map(p=>p.body.provider),['usgs']);assert.equal(quakeAcquisitionPlan(crossing,opts).length,1);
const event=(id,x,y,at)=>({type:'Feature',id,geometry:{type:'Point',coordinates:[x,y]},properties:{at,event_type:'earthquake'}});
const italian={...snapshot,bounds:[8,39,19,45],features:[event('i',13,42,'2026-10-24T12:00:00Z')]};
const world={...snapshot,bounds:[8,39,20,45],quality:{...snapshot.quality,provider:'usgs'},features:[event('g-duplicate',13,42,'2026-10-24T12:00:00Z'),event('outside',19.3,42,'2026-10-24T13:00:00Z')]};
const combined=combineQuakeSnapshots([italian,world]);assert.equal(combined.features.length,2);assert.equal(combined.features[0].id,'usgs:outside');assert.equal(combined.features[1].properties.catalogue_provider,'ingv');assert.equal(combined.quality.provider,'ingv+usgs');assert.equal(italian.features[0].id,'i');assert.equal(world.features.length,2);
assert.equal(quakeSnapshotCovers(combined,crossing,auto,now),true);assert.equal(quakeSnapshotCovers(world,crossing,auto,now),false);assert.equal(quakeSnapshotCovers(italian,crossing,auto,now),false);assert.equal(quakeSnapshotCovers(combined,[8.8,39.5,20.5,44.5],auto,now),false);
assert.equal(combineQuakeSnapshots([italian]),italian);assert.equal(quakeSnapshotCovers(italian,local,auto,now),true);
assert.equal(quakeSnapshotCovers(combineQuakeSnapshots([italian,{...world,acquired_at:'2026-10-24T19:00:00Z'}]),crossing,auto,now),false);
console.log('PASS composite seismic catalogue: INGV retained at Italy edge, global-only elsewhere, spatial source priority without duplicates, source provenance, reuse and stale/missing-part rejection');

const shifted={...world,quality:{...world.quality,window_start:'2026-10-17T21:20:00Z',window_end:'2026-10-24T21:20:00Z'}};
const envelope=combineQuakeSnapshots([italian,shifted]);assert.equal(envelope.quality.window_start,italian.quality.window_start);assert.equal(envelope.quality.window_end,shifted.quality.window_end);assert.equal(envelope.quality.window_semantics,'ENVELOPE_OF_SOURCE_WINDOWS');

// Selection changes must filter both map and event list, without changing source records.
const quake=(magnitude,event_type='earthquake')=>({magnitude,event_type});
for(const threshold of [-1,0,1,2,3,4])for(const magnitude of [-1,0,.9,1,1.5,2,3,4,5])assert.equal(quakeVisible(quake(magnitude),threshold),magnitude>=threshold);
for(const magnitude of [null,undefined,NaN,Infinity,'3'])assert.equal(quakeVisible(quake(magnitude),0),false);
assert.equal(quakeVisible(quake(4,'explosion'),0),false);
const original=quake(2);assert.equal(quakeVisible(original,3),false);assert.deepEqual(original,quake(2));
console.log('PASS immediate magnitude selection, missing values, event-type filtering and complete/truncated snapshot reuse');
