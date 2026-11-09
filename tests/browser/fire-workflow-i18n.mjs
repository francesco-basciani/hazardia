import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {i18nURI} from './i18n-fixture.mjs';
const i18n=await import(i18nURI);i18n.setLanguage('en',{persist:false});
const reviewed=JSON.parse(readFileSync('reports/fire-workflow-20261105/translations.json','utf8'));
for(const [source,expected] of Object.entries(reviewed))assert.equal(i18n.t(source),expected,source);
assert(!i18n.t('MODIFICHE NON CALCOLATE · risultato precedente').includes('UNCOMPUTED'));
i18n.setLanguage('it',{persist:false});assert.equal(i18n.t('Centra inneschi'),'Centra inneschi');
console.log('PASS '+Object.keys(reviewed).length+' reviewed wildfire/weather messages, clear recalculation wording, Italian fallback');
