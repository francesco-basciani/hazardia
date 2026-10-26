import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {formatObservedDate}=await import('data:text/javascript;base64,'+Buffer.from(readFileSync(new URL('../../src/hazardia/web/static/observed-layer-time.js',import.meta.url))).toString('base64'));
for(const value of [null,undefined,'','invalid','2026-not-a-date'])assert.equal(formatObservedDate(value),'—');
const source='2026-10-26T12:34:56Z',it=formatObservedDate(source),en=formatObservedDate(source,'en-GB');
assert(it.includes('26 ott 2026'));assert(it.includes('13:34:56'));assert(it.includes('CET'));assert(en.includes('26 Oct 2026'));assert(en.includes('13:34:56'));assert(!it.includes('T12:'));assert.equal(source,'2026-10-26T12:34:56Z');
// Repeated local clock hour must retain a different offset across autumn DST.
const summer=formatObservedDate('2026-10-25T00:30:00Z'),winter=formatObservedDate('2026-10-25T01:30:00Z');assert(summer.includes('02:30:00'));assert(winter.includes('02:30:00'));assert.notEqual(summer,winter);
assert(formatObservedDate('2026-10-25T23:30:00Z').includes('26 ott 2026'));
console.log('PASS readable Italian/English dates, seconds, Rome timezone, DST repeated hour, midnight, missing values, immutable UTC inputs');
