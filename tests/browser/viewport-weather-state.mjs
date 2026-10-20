import {readFileSync} from 'node:fs';import assert from 'node:assert/strict';
const {viewportWeatherState:state,retainCoveredForecast:retain}=await import('data:text/javascript;base64,'+readFileSync('src/hazardia/web/static/viewport-weather-state.js').toString('base64'));
const now=Date.parse('2026-10-20T09:00:00Z'),view=[[35,6],[48,20]],large=[[-5,-30],[72,55]];
const field=bounds=>({bounds,available_at:'2026-10-20T08:00:00Z',records:[Object.fromEntries(['u','v','temperature','precipitation','humidity','pressure','cloud','gusts','radiation','rain_probability'].map(k=>[k,[1]]))]});
let n=0;const eq=(a,b)=>{assert.equal(a,b);n++;};const fresh={status:'FRESH',forecast:field(view)};
eq(state(fresh,view).kind,'ready');eq(state(fresh,large).kind,'fetch');eq(state({...fresh,fetching:true},large).kind,'poll');eq(state({...fresh,fetching:true},large).delayMs,1200);
eq(state({...fresh,retry_after_s:45},large).kind,'wait');eq(state({...fresh,retry_after_s:45},large).delayMs,45000);
eq(state(fresh,large,{now,nextRequestAt:now+65000}).delayMs,65000);
eq(state({...fresh,status:'STALE'},view).kind,'fetch');eq(state({status:'EMPTY'},view).kind,'fetch');
const legacy=field(view);delete legacy.records[0].humidity;eq(state({...fresh,forecast:legacy},view).kind,'fetch');
const previous=field(large),partial={status:'FRESH',forecast:field([[41,12],[43,15]])};eq(retain(partial,previous,view,now).forecast,previous);eq(retain(fresh,previous,view,now),fresh);
eq(retain(partial,{...previous,available_at:'2026-10-19T08:00:00Z'},view,now),partial);eq(retain(partial,{...previous,available_at:'2026-10-21T08:00:00Z'},view,now),partial);
// A pending acquisition returning another tab's area must request the latest view afterwards.
eq(state({...partial,fetching:false},large).kind,'fetch');eq(state({...fresh,forecast:field([[-85,-180],[85,180]])},[[42,13],[43,14]]).kind,'fetch');
console.log(`PASS ${n} assertions: coverage, pending acquisition, retries, free cooldown, complete variables and per-view retention`);
