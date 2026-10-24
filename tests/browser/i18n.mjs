import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {i18nURI} from './i18n-fixture.mjs';
const i18n=await import(i18nURI);
let checks=0;const check=(a,b)=>{assert.equal(a,b);checks++;};
check(i18n.getLanguage(),'it'); // Browser/OS language does not override the Italian default.
check(i18n.t('Simulazioni e risorse'),'Simulazioni e risorse');
i18n.setLanguage('en',{persist:false});check(i18n.locale(),'en-GB');
check(i18n.t('Simulazioni e risorse'),'Simulations and resources');
check(i18n.t('  Criticità territoriali  '),'  Areas of concern  ');
check(i18n.t('job-0123 · Calcolo in corso'),'job-0123 · Computation in progress');
check(i18n.t('SOURCE_MISSING / FIRE / FLOOD / 2026-10-24T14:00:00Z'),'SOURCE_MISSING / FIRE / FLOOD / 2026-10-24T14:00:00Z');
check(i18n.t('1,234.5 / 13.38 / 42.35'),'1,234.5 / 13.38 / 42.35');
check(i18n.t('constructor'),'constructor');check(i18n.t('__proto__'),'__proto__');
check(i18n.t('Open-Meteo / /api/map-weather / job-0123'),'Open-Meteo / /api/map-weather / job-0123');
check(i18n.t('Traffico simulato — scenario ipotetico'),'Simulated traffic — hypothetical scenario');
check(i18n.t('Assenza di cavi cartografati ≠ area libera.'),'No mapped wires ≠ clear area.');
check(i18n.t('Dati mancanti per l’ora selezionata.'),'Missing data for the selected time.');
i18n.preserveTexts(['Alta Irpinia e Sannio','Incendio di prova — squadra Alfa']);
check(i18n.t('Alta Irpinia e Sannio'),'Alta Irpinia e Sannio');
check(i18n.t('Scenario · Incendio di prova — squadra Alfa · Calcolo in corso'),'Scenario · Incendio di prova — squadra Alfa · Computation in progress');
const n=i18n.numberFormatter({maximumFractionDigits:1});check(n.format(1234.5),'1,234.5');
const d=i18n.dateTimeFormatter({timeZone:'Europe/Rome',hour:'2-digit',minute:'2-digit',hourCycle:'h23'});check(d.format(new Date('2026-10-24T12:00:00Z')),'14:00');
i18n.setLanguage('it',{persist:false});check(n.format(1234.5),'1.234,5');check(d.format(new Date('2026-10-24T12:00:00Z')),'14:00');
check(i18n.t('Criticità territoriali'),'Criticità territoriali');
i18n.setLanguage('unsupported',{persist:false});check(i18n.getLanguage(),'it');
// Every public entry point loads the shared locale controller.
for(const f of ['index','fire-studio','traffic-studio','physical-fire','map-lab']){assert(readFileSync('src/hazardia/web/static/'+f+'.html','utf8').includes('src="/i18n.js"'));checks++;}
const {messages}=await import('data:text/javascript;base64,'+Buffer.from(readFileSync('src/hazardia/web/static/i18n-catalog.js')).toString('base64'));
assert(Object.keys(messages).length>1000);checks++;
for(const [it,en] of Object.entries(messages)){assert(it.trim()&&en.trim());assert(!en.includes('<script'));}
console.log(`PASS ${checks} bilingual checks: Italian default, exact/composed messages, safety meaning, immutable IDs/numbers, dynamic locale formatters, fallback and all five entry points; ${Object.keys(messages).length} catalogue entries`);
