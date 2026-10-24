import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {withI18n,moduleURI} from './i18n-fixture.mjs';
const timeline=moduleURI(readFileSync('src/hazardia/web/static/monitor-timeline.js','utf8'));
const source=withI18n(readFileSync('src/hazardia/web/static/monitor-clock.js','utf8')).replace("'/monitor-timeline.js'",JSON.stringify(timeline));
const {monitoredTime}=await import(moduleURI(source));
const now=Date.parse('2026-10-24T14:23:45Z');
assert.equal(monitoredTime(null,now).selected,null);assert.equal(monitoredTime('garbage',now).at,null);
const current=monitoredTime('2026-10-24T14:00:00Z',now);assert.equal(current.future,false);assert(current.selected.includes('16:00:00'));assert(current.now.includes('16:23:45'));assert(current.selected.includes('UTC+02:00'));
const future=monitoredTime('2026-10-25T02:00:00Z',now);assert(future.future);assert(future.selected.includes('03:00:00'));assert(future.selected.includes('UTC+01:00'));
const first=monitoredTime('2026-10-25T00:30:00Z',now),second=monitoredTime('2026-10-25T01:30:00Z',now);assert(first.selected.includes('02:30:00'));assert(second.selected.includes('02:30:00'));assert.notEqual(first.selected,second.selected); // Repeated local hour is disambiguated by UTC offset.
assert.equal(monitoredTime(future.at,now,'Europe/Rome','en-GB').at,future.at);
assert.equal(monitoredTime(future.at,now+1000).selected,future.selected);assert.notEqual(monitoredTime(future.at,now+1000).now,future.now);
console.log('PASS monitored time vs wall clock, missing/invalid time, future horizon, exact seconds, unchanged UTC instant and DST repeated-hour offset');

assert(current.compact.includes('16:00'));assert(!current.compact.includes('UTC'));assert(!current.compact.includes('2026'));assert.notEqual(first.selected,second.selected);assert.equal(monitoredTime(null,now).compact,null);
console.log('PASS compact clock keeps canonical UTC instant and detailed DST offset separately');
