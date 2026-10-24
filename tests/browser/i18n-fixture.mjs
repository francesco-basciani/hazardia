import {readFileSync} from 'node:fs';
export const moduleURI=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const root=new URL('../../src/hazardia/web/static/',import.meta.url);
export const i18nURI=moduleURI(readFileSync(new URL('i18n.js',root),'utf8').replace("'./i18n-catalog.js'",JSON.stringify(moduleURI(readFileSync(new URL('i18n-catalog.js',root),'utf8')))));
export const withI18n=s=>s.replaceAll('"/i18n.js"',JSON.stringify(i18nURI));
