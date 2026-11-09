import {potentialDisplay} from './avalanche-model.js';
// Quality annotations only: source polygons stay intact for inspection and export.
const extents=new WeakMap();
function polygons(g){if(g.type==='Polygon')return [g.coordinates];if(g.type==='MultiPolygon')return g.coordinates;throw Error('Geometria qualità non supportata');}
function extent(g){if(extents.has(g))return extents.get(g);const b=[Infinity,Infinity,-Infinity,-Infinity];for(const poly of polygons(g))for(const p of poly[0]){if(!p.every(Number.isFinite))throw Error('Coordinate qualità non valide');b[0]=Math.min(b[0],p[0]);b[1]=Math.min(b[1],p[1]);b[2]=Math.max(b[2],p[0]);b[3]=Math.max(b[3],p[1]);}extents.set(g,b);return b;}
function clip(a,b,v){let lo=0,hi=1;const dx=b[0]-a[0],dy=b[1]-a[1];for(const [p,q]of [[-dx,a[0]-v[0]],[dx,v[2]-a[0]],[-dy,a[1]-v[1]],[dy,v[3]-a[1]]]){if(p===0){if(q<0)return null;}else{const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return null;}}return [a[0]+lo*dx,a[1]+lo*dy];}
function inRing(ring,p){let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;}return inside;}
function anchor(g,v){for(const poly of polygons(g)){for(const ring of poly)for(let i=1;i<ring.length;i++){const p=clip(ring[i-1],ring[i],v);if(p)return p;}const p=[(v[0]+v[2])/2,(v[1]+v[3])/2];if(inRing(poly[0],p)&&!poly.slice(1).some(ring=>inRing(ring,p)))return p;}return null;}
export function qualityAnnotations(features,view,project){
 if(view.length!==4||!view.every(Number.isFinite)||view[0]>=view[2]||view[1]>=view[3])throw Error('Vista qualità non valida');
 const groups=new Map();
 for(const feature of features){const info=potentialDisplay(feature.properties);if(!info.uncertainty)continue;const b=extent(feature.geometry);if(b[2]<view[0]||b[0]>view[2]||b[3]<view[1]||b[1]>view[3])continue;const p=anchor(feature.geometry,view);if(!p)continue;const pixel=project(p);if(!pixel.every(Number.isFinite))throw Error('Proiezione qualità non valida');const channel=info.uncertainty==='ground_gap'?'ground_gap':'unknown',key=channel+':'+Math.floor(pixel[0]/64)+':'+Math.floor(pixel[1]/64);let group=groups.get(key);if(!group){group={anchor:p,channel,colour:info.colour,features:[],counts:{missing:0,snow_unverified:0,ground_gap:0}};groups.set(key,group);}group.features.push(feature);group.counts[info.uncertainty]++;
 }return [...groups.values()];
}
