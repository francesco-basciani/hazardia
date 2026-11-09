import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {i18nURI} from './i18n-fixture.mjs';
const i18n=await import(i18nURI);i18n.setLanguage('en',{persist:false});
const reviewed=JSON.parse(readFileSync('reports/fire-console-summary-20261105/translations.json','utf8'));
for(const [it,en] of Object.entries(reviewed))assert.equal(i18n.t(it),en,it);
console.log('PASS '+Object.keys(reviewed).length+' mean-display, missing-data and execution messages');
