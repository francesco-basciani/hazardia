import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const queueURL='data:text/javascript;base64,'+Buffer.from(readFileSync('src/hazardia/web/static/tile-queue.js')).toString('base64');
const elements=[];globalThis.document={createElement(){const img={alt:'',setAttribute(){},removeAttribute(key){delete this[key];}};elements.push(img);return img;}};
globalThis.L={TileLayer:{extend(methods){return class {constructor(url){this.url=url;this.handlers={};this._map={getContainer:()=>({dataset:{}})};}on(names,cb){for(const name of names.split(' '))this.handlers[name]=cb;return this;}getTileUrl(c){return this.url+'/'+c.x;}createTile(...a){return methods.createTile.apply(this,a);}};}}};
const source=readFileSync('src/hazardia/web/static/scheduled-tiles.js','utf8').replace("'/tile-queue.js'",JSON.stringify(queueURL));
const {scheduledTiles}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const layer=scheduledTiles('/test',{});let completed=0;const imgs=Array.from({length:6},(_,x)=>layer.createTile({x},()=>completed++));
assert.equal(imgs.filter(i=>i.src).length,4);assert.ok(layer.handlers.tileabort);layer.handlers.tileabort({tile:imgs[0]});assert.equal(imgs[4].src,'/test/4');layer.handlers.tileunload({tile:imgs[1]});assert.equal(imgs[5].src,'/test/5');assert.equal(completed,0);for(const img of imgs.slice(2))img.onload();assert.equal(completed,4);assert.equal(imgs[0].src,undefined);console.log('PASS7 native image adapter checks including Leaflet tileabort releasing admission');
