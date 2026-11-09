import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const uri=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const {landIndex}=await import(uri(readFileSync('src/hazardia/web/static/weather-sampling.js','utf8')));
const mask=landIndex({features:[{geometry:{type:'Polygon',coordinates:[[[0,0],[4,0],[4,4],[0,4],[0,0]],[[1,1],[2,1],[2,2],[1,2],[1,1]]]}},{geometry:{type:'MultiPolygon',coordinates:[[[[7,7],[8,7],[8,8],[7,8],[7,7]]],[[[-5,-5],[-4,-5],[-4,-4],[-5,-4],[-5,-5]]]]}}]});
for(let i=0;i<600;i++){assert.equal(mask(.5,.5),true);assert.equal(mask(1.5,1.5),false);assert.equal(mask(7.5,7.5),true);assert.equal(mask(-4.5,-4.5),true);assert.equal(mask(5,i*.01),false);}
assert.equal(mask(NaN,0),false);assert.equal(landIndex({features:[]})(0,0),false);
console.log('PASS: land, holes, islands, multipolygon, ocean, invalid coordinate, bounded-cache rollover');
