/* Presentation-only bilingual adapter for legacy and dynamically created views.
 * Never rewrites application data, input values, source records or HTML markup.
 * Exact messages take precedence over explicit catalogue fragments. */
import {messages} from './i18n-catalog.js';
export const LANGUAGE_KEY='hazardia.language';
const supported=new Set(['it','en']);
const normalise=value=>supported.has(value)?value:'it';
let language='it';
try {language=normalise(globalThis.localStorage?.getItem(LANGUAGE_KEY));} catch {}
export const getLanguage=()=>language;
export const locale=()=>language==='en'?'en-GB':'it-IT';
const translatedCache=new Map(),preserved=new Set();let protectedPattern;
export function preserveTexts(values){let changed=false;for(const value of values){if(typeof value==='string'&&value.length>1&&!preserved.has(value)&&preserved.size<2048){preserved.add(value);changed=true;}}if(changed){protectedPattern=new RegExp([...preserved].sort((a,b)=>b.length-a.length).map(escapeRE).join('|'),'gu');translatedCache.clear();}}
const escapeRE=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const keys=Object.keys(messages).filter(k=>k!==messages[k]).sort((a,b)=>b.length-a.length);
const fragments=new RegExp('(?<![\\p{L}\\p{N}_-])(?:'+keys.map(escapeRE).join('|')+')(?![\\p{L}\\p{N}_-])','gu');
export function translate(value,lang=language){
 const raw=String(value),trim=raw.trim();if(lang!=='en'||!trim)return raw;
 if(translatedCache.has(raw))return translatedCache.get(raw);
 const protectedRanges=protectedPattern?[...raw.matchAll(protectedPattern)].map(m=>[m.index,m.index+m[0].length]):[];
 if(protectedRanges.some(([a,b])=>a===raw.indexOf(trim)&&b===a+trim.length))return raw;
 let result=!protectedRanges.length&&Object.prototype.hasOwnProperty.call(messages,trim)?messages[trim]:undefined;
 if(result!==undefined)return raw.slice(0,raw.indexOf(trim))+result+raw.slice(raw.indexOf(trim)+trim.length);
 // Explicit fragments support composed status text with identifiers and values.
 result=raw.replace(fragments,(s,offset)=>protectedRanges.some(([a,b])=>offset<b&&offset+s.length>a)?s:messages[s]);
 if(translatedCache.size>=2048)translatedCache.clear();translatedCache.set(raw,result);return result;
}
export const t=translate;
const formats=new Map();
function formatter(kind,options){return {format(value){const key=locale()+kind+JSON.stringify(options);if(!formats.has(key))formats.set(key,new Intl[kind](locale(),options));return formats.get(key).format(value);}};}
export const dateTimeFormatter=options=>formatter('DateTimeFormat',options);
export const numberFormatter=options=>formatter('NumberFormat',options);
const originals=new WeakMap(),attributes=new WeakMap();
export function sourceText(node){if(!node)return '';if(node.nodeType!==3&&node.childNodes)return [...node.childNodes].map(sourceText).join('');const item=originals.get(node);return item&&node.data===item.rendered?item.source:node.data??node.textContent;}
export function sourceAttribute(node,key){if(!node)return '';const value=node.getAttribute(key),item=attributes.get(node)?.get(key);return item&&value===item.rendered?item.source:value;}
const skip='script,style,code,pre,textarea,[contenteditable], [data-i18n-skip],.map-place-name,.region-name,.leaflet-control-attribution,.annotation-label';
const translatableAttributes=['aria-label','aria-valuetext','title','placeholder','alt'];
function ignored(node){return !!node?.closest?.(skip);}
function text(node){if(!node.parentElement||ignored(node.parentElement))return;const source=sourceText(node);if(!source?.trim())return;const rendered=translate(source);originals.set(node,{source,rendered});if(node.data!==rendered)node.data=rendered;}
function attrs(el){if(ignored(el))return;let record=attributes.get(el);if(!record){record=new Map();attributes.set(el,record);}for(const key of translatableAttributes){if(!el.hasAttribute(key))continue;const value=el.getAttribute(key),old=record.get(key),source=old&&value===old.rendered?old.source:value,rendered=translate(source);record.set(key,{source,rendered});if(value!==rendered)el.setAttribute(key,rendered);}}
function visit(node){if(node.nodeType===3){text(node);return;}if(node.nodeType!==1&&node.nodeType!==9)return;if(node.nodeType===1){if(ignored(node))return;attrs(node);}const walk=document.createTreeWalker(node,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT,{acceptNode:n=>n.nodeType===1&&ignored(n)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});while(walk.nextNode()){const n=walk.currentNode;n.nodeType===3?text(n):attrs(n);}}
let observer,scheduled=false;const pending=new Set();
const observeOptions={subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:translatableAttributes};
function flush(){scheduled=false;const work=[...pending];pending.clear();for(const node of work){if(!node.isConnected)continue;visit(node);}}
function schedule(node){pending.add(node);if(!scheduled){scheduled=true;queueMicrotask(flush);}}
export function setLanguage(value,{persist=true}={}){
 language=normalise(value);if(persist)try{localStorage.setItem(LANGUAGE_KEY,language);}catch{}
 if(typeof document==='undefined')return language;
 observer?.disconnect();pending.clear();
 document.documentElement.lang=language;
 document.querySelectorAll('[data-language-select]').forEach(el=>el.value=language);
 visit(document.documentElement);
 if(language==='en')observer?.observe(document.documentElement,observeOptions);
 document.dispatchEvent(new CustomEvent('hazardia-language',{detail:{language,locale:locale()}}));
 return language;
}
function install(){
 document.documentElement.lang=language;
 const embedded=window.parent!==window;
 if(!embedded){
  const host=document.querySelector('.topmeta')||document.querySelector('header')||document.body;
  const label=document.createElement('label');label.className='language-switch';label.dataset.i18nSkip='';
  const span=document.createElement('span');span.textContent='IT / EN';
  const select=document.createElement('select');select.dataset.languageSelect='';select.setAttribute('aria-label','Lingua / Language');
  for(const [value,name] of [['it','Italiano'],['en','English']]){const o=document.createElement('option');o.value=value;o.textContent=name;o.lang=value;select.append(o);}select.value=language;select.addEventListener('change',()=>setLanguage(select.value));label.append(span,select);const connection=host.querySelector('.connection');if(connection)host.insertBefore(label,connection);else host.append(label);
 }
 visit(document.documentElement);
 observer=new MutationObserver(records=>{for(const r of records){if(r.type==='characterData'){const old=originals.get(r.target);if(old?.rendered!==r.target.data)schedule(r.target);}else if(r.type==='attributes'){const old=attributes.get(r.target)?.get(r.attributeName);if(old?.rendered!==r.target.getAttribute(r.attributeName))schedule(r.target);}else for(const node of r.addedNodes)schedule(node);}});
 if(language==='en')observer.observe(document.documentElement,observeOptions);
 window.addEventListener('storage',e=>{if(e.key===LANGUAGE_KEY||e.key===null)setLanguage(e.newValue,{persist:false});});
 // Same-origin embedded studios share the choice without reloading their state.
 document.addEventListener('hazardia-language',()=>{for(const frame of document.querySelectorAll('iframe')){try{frame.contentWindow?.postMessage({type:'hazardia-language',language},location.origin);}catch{}}});
 window.addEventListener('message',e=>{if(e.origin===location.origin&&e.source===window.parent&&e.source!==window&&e.data?.type==='hazardia-language')setLanguage(e.data.language,{persist:false});});
 if(embedded)try{const preferred=localStorage.getItem(LANGUAGE_KEY);setLanguage(preferred,{persist:false});}catch{}
}
if(typeof document!=='undefined'&&document.head&&document.documentElement){
 for(const [rel,href,type] of [['icon','/favicon.svg','image/svg+xml'],['alternate icon','/favicon.ico','image/x-icon']]){if(document.querySelector('link[href="'+href+'"]'))continue;const icon=document.createElement('link');icon.rel=rel;icon.href=href;icon.type=type;document.head.append(icon);}
 const link=document.createElement('link');link.rel='stylesheet';link.href='/i18n.css';document.head.append(link);
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
}
