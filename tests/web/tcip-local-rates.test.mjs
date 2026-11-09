import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
let code=readFileSync(new URL('../../src/hazardia/web/static/tcip-local-rates.js',import.meta.url),'utf8');
const helper=readFileSync(new URL('../../src/hazardia/web/static/tcip-rate-scale.js',import.meta.url),'utf8');
code=code.replace("from '/tcip-rate-scale.js'","from 'data:text/javascript;base64,"+Buffer.from(helper).toString('base64')+"'");
assert.match(code,/Non è un indice di sicurezza/);
const {categorySelection}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const fixture={items:[
 {id:'all-theft',level:'best_available',aggregation:'cumulative',window:'all',crime_code:'theft',crime_label:'Furti',areas:20,period_start:'2018-01-01',period_end:'2024-12-31'},
 {id:'province-attempt',level:'province',crime_code:'attempted_homicide',crime_label:'Tentati omicidi',areas:28,period_start:'2025-01-01',period_end:'2025-12-31'},
 {id:'city-snatch',level:'municipality',crime_code:'theft.snatch',crime_label:'Furti con strappo',areas:1,period_start:'2025-01-01',period_end:'2025-12-31'}
],crime_types:[{code:'theft',label:'Furti'},{code:'attempted_homicide',label:'Tentati omicidi'},{code:'theft.snatch',label:'Furti con strappo'},{code:'femicide',label:'Femminicidio',definition:'Nessun conteggio territoriale qualificato.'}]};
let selection=categorySelection(fixture,{level:'best_available',window:'all',crime:'theft'});
assert.equal(selection.categories.length,4);assert.equal(selection.period,'all-theft');
selection=categorySelection(fixture,{level:'best_available',window:'all',crime:'attempted_homicide',period:'all-theft'});
assert.equal(selection.crime,'attempted_homicide');assert.equal(selection.period,'');
selection=categorySelection(fixture,{level:'province',window:'period',crime:selection.crime,period:'all-theft'});
assert.equal(selection.period,'province-attempt');
selection=categorySelection(fixture,{level:'municipality',window:'period',crime:'theft.snatch'});
assert.equal(selection.period,'city-snatch');
selection=categorySelection(fixture,{level:'province',window:'period',crime:'femicide',period:'province-attempt'});
assert.equal(selection.crime,'femicide');assert.equal(selection.periods.length,0);assert.equal(selection.period,'');assert.match(selection.definition,/Nessun conteggio/);
selection=categorySelection(fixture,{level:'best_available',window:'all',crime:'theft',period:''});
assert.equal(selection.period,'all-theft');
assert.match(code,/legend.replaceChildren\(\)/);
console.log('PASS all categories remain selectable across geography/time; unavailable categories never retain another crime period');
const extended=structuredClone(fixture);extended.items.push({...fixture.items[1],id:'cumulative-attempt',aggregation:'cumulative',window:'all'});
selection=categorySelection(extended,{level:'best_available',window:'all',crime:'attempted_homicide'});
assert.equal(selection.period,'cumulative-attempt');assert.equal(selection.level,'province');
selection=categorySelection(extended,{level:'neighborhood',window:'all',crime:'attempted_homicide'});
assert.equal(selection.level,'neighborhood');assert.equal(selection.period,'');
console.log('PASS national best-available selector uses an explicit available level without replacing the crime or time window');
const national={items:[{id:'istat',level:'country',crime_code:'femicide',crime_label:'Femminicidio · stime ISTAT',aggregation:'cumulative',window:'all',areas:1,period_start:'2019-01-01',period_end:'2024-12-31'}],crime_types:[{code:'femicide',label:'Femminicidio · stime ISTAT',definition:'Unico dato nazionale, non conteggi comunali.'}]};
selection=categorySelection(national,{level:'best_available',window:'all',crime:'femicide'});
assert.equal(selection.level,'country');assert.equal(selection.period,'istat');
selection=categorySelection(national,{level:'municipality',window:'all',crime:'femicide'});
assert.equal(selection.period,'');assert.equal(selection.level,'municipality');
console.log('PASS national femicide series retains its own country level and victim definitions');
