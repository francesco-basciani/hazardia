import assert from 'node:assert/strict';
import fs from 'node:fs';
const {dpcZoneStyle,dpcColors,dpcCounts}=await import('data:text/javascript;base64,'+Buffer.from(fs.readFileSync(new URL('../../src/hazardia/web/static/dpc-display.js',import.meta.url))).toString('base64'));
for(let level=0;level<=3;level++)assert.equal(dpcZoneStyle({level},false).fillColor,dpcColors[level]);
for(const p of [{level:null},{},{level:0,geometry_warning:'invalid'},{level:-1},{level:4}])assert.equal(dpcZoneStyle(p,false).fillColor,'#83909b');
assert.equal(dpcZoneStyle({level:0},true).fillColor,'#83909b');
assert.ok(dpcZoneStyle({level:0},false).fillOpacity>=.2);
assert.deepEqual(dpcCounts([{properties:{level:0}},{properties:{level:1}},{properties:{level:null}},{properties:{level:0,geometry_warning:'bad'}}]),{levels:[1,1,0,0],unknown:2});
console.log('PASS 12 checks: valid green/yellow/orange/red; missing, invalid and stale never green; counts');
