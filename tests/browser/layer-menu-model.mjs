import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const uri=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const {layerVisible,layerMinZoom,menuGroups,menuGroup}=await import(uri(readFileSync(new URL('../../src/hazardia/web/static/layer-menu-model.js',import.meta.url),'utf8')));
assert.equal(layerVisible('buildings',14),false);
assert.equal(layerVisible('buildings',15),true);
assert.equal(layerVisible('buildings',2,false),true,'Studio/scientific context must retain prior display behavior');
assert.equal(layerVisible('emergency',8),true,'No invented zoom restriction for emergency features');
assert.deepEqual(Object.keys(layerMinZoom),['buildings']);
const groups=new Set(menuGroups.map(([id])=>id));
for(const [category,name,expected] of [
 ['buildings','Edifici','territory'],['utilities','Reti e impianti','territory'],
 [null,'Centri abitati','territory'],[null,'Cavi aerei e tralicci','territory'],
 ['healthcare','Sanità e assistenza','territory'],['emergency','Emergenze e soccorso','territory'],
 [null,'Terremoti osservati','observations'],[null,'Radar pioggia osservata','observations'],
 [null,'Meteo e osservazioni','forecast'],[null,'Criticità territoriali','forecast'],
 [null,'Confini','cartography'],['boundaries','Confini OSM','cartography'],
 [null,'Catalogo territoriale','cartography']]){
 const group=menuGroup(category,name);assert.equal(group,expected);assert(groups.has(group));
}
console.log('PASS zoom-boundary, studio preservation and catalogue category checks');
