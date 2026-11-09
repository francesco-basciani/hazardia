import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../../src/hazardia/web/static/tcip-layer.js',import.meta.url),'utf8');
const {shareColor,crimeLayers,nationalLayer}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
assert.equal(shareColor(null),'#c9cfce');
assert.equal(shareColor(0),'#487862');
assert.notEqual(shareColor(0),shareColor(null),'Missing must remain distinct from observed zero');
assert.equal(shareColor(.01),'#96ad68');assert.equal(shareColor(.03),'#e2c761');assert.equal(shareColor(.06),'#db9350');assert.equal(shareColor(.1),'#b85547');
console.log('PASS TCIP descriptive share classes and missing/zero distinction');

assert.notEqual(shareColor(.18,'neighborhood'),shareColor(.48,'neighborhood'));

const categories=[{release_id:'a',crime_code:'theft'},{release_id:'b',crime_code:'all_recorded_offences'},{release_id:'c',crime_code:'burglary.commercial'},{release_id:'d',crime_code:'theft'}];
assert.deepEqual(crimeLayers(categories,'theft').map(x=>x.release_id),['a','d']);
assert.deepEqual(crimeLayers(categories,'robbery'),[]);
assert.deepEqual(crimeLayers(categories,'all_recorded_offences').map(x=>x.release_id),['b']);

const nationalFixture=[{release_id:'local',profile:'tcip.spatial-observed-share/2.0',crime_code:'theft'},{release_id:'national',profile:'tcip.regional-historical-share/1.0',crime_code:'theft'}];
assert.equal(nationalLayer(nationalFixture).release_id,'national');
assert.equal(nationalLayer(nationalFixture.slice(0,1)),null,'A local share must never substitute a missing national profile');
console.log('PASS TCIP national profile selection without local fallback');
