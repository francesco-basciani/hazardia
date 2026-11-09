import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../../src/hazardia/web/static/tcip-population-map.js',import.meta.url),'utf8');
const {rateColor}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
assert.notEqual(rateColor(null),rateColor(0));
assert.notEqual(rateColor(.4),rateColor(1.6));
assert.equal(rateColor(1),rateColor(1.1));
console.log('PASS population rate ratio classes, unknown distinct from observed zero');
