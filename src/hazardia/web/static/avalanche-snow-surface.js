// Presentation only. Never use interpolated graphics as snow/hazard model input.
const bands=[[0,1,'#c7ddeb'],[1,10,'#88b6d3'],[10,30,'#487ea7'],[30,Infinity,'#254b78']];
const cached=new WeakMap();
function cut(polygon,level,above){
 const result=[];
 for(let i=0;i<polygon.length;i++){
  const a=polygon[i],b=polygon[(i+1)%polygon.length],inside=above?a[2]>level:a[2]<=level,next=above?b[2]>level:b[2]<=level;
  if(inside)result.push(a);
  if(inside!==next){const t=(level-a[2])/(b[2]-a[2]);result.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),level]);}
 }
 return result;
}
export function snowSurface(features,lead){
 const index={24:1,48:2,72:3}[lead];if(index===undefined)throw Error('INVALID_SNOW_LEAD');
 let memo=cached.get(features);if(memo?.has(lead))return memo.get(lead);
 if(!memo){memo=new Map();cached.set(features,memo);}
 const grid=new Map(),used=new Set(),polygons=[];let missing=0,positive=0;
 for(const feature of features){const p=feature.properties,value=p.forecast_hs_cm?.[index];
  if(typeof value!=='number'||!Number.isFinite(value)||value<0){missing++;continue;}
  if(value>0)positive++;
  if(!Number.isInteger(p.grid_row)||!Number.isInteger(p.grid_col)||!Number.isFinite(p.lon)||!Number.isFinite(p.lat))continue;
  grid.set(p.grid_row+':'+p.grid_col,{point:[p.lon,p.lat,value],feature});
 }
 for(const [key,a]of grid){const [row,col]=key.split(':').map(Number),b=grid.get(row+':'+(col+1)),c=grid.get((row+1)+':'+col),d=grid.get((row+1)+':'+(col+1));
  if(!b||!c||!d||Math.max(a.point[2],b.point[2],c.point[2],d.point[2])<=0)continue;
  const nodes=[a,b,c,d];for(const node of nodes)used.add(node.feature.properties.id);
  const point=(u,v)=>[0,1,2].map(k=>(1-u)*(1-v)*a.point[k]+u*(1-v)*b.point[k]+(1-u)*v*c.point[k]+u*v*d.point[k]);
  // Three display subdivisions round the iso-bands; native support stays10km.
  for(let y=0;y<3;y++)for(let x=0;x<3;x++){
   const p=point(x/3,y/3),q=point((x+1)/3,y/3),r=point(x/3,(y+1)/3),s=point((x+1)/3,(y+1)/3);
   for(const triangle of [[p,q,s],[p,s,r]])for(const [low,high,color]of bands){
    let polygon=cut(triangle,low,true);if(Number.isFinite(high)&&polygon.length)polygon=cut(polygon,high,false);
    if(polygon.length>=3)polygons.push({points:polygon,color,low,high});
   }
  }
 }
 const isolated=[...grid.values()].filter(n=>n.point[2]>0&&!used.has(n.feature.properties.id)).map(n=>n.feature);
 const result={polygons,isolated,positive,missing,method:'DISPLAY_ONLY_BILINEAR',spacing_m:10000};memo.set(lead,result);return result;
}

export function snowSurfaceLayer({map,features,lead,stale=false}){
 const field=snowSurface(features,lead),bounds=new WeakMap();
 const polygonsOf=geometry=>geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
 function extent(feature){let box=bounds.get(feature);if(box)return box;box=[Infinity,Infinity,-Infinity,-Infinity];for(const rings of polygonsOf(feature.geometry))for(const ring of rings)for(const [x,y]of ring){box[0]=Math.min(box[0],x);box[1]=Math.min(box[1],y);box[2]=Math.max(box[2],x);box[3]=Math.max(box[3],y);}bounds.set(feature,box);return box;}
 const Surface=L.Layer.extend({
  onAdd(host){this.host=host;this.canvas=L.DomUtil.create('canvas','leaflet-layer leaflet-zoom-hide');this.canvas.style.pointerEvents='none';this.canvas.setAttribute('aria-hidden','true');host.getPane('overlayPane').append(this.canvas);host.on('moveend zoomend resize',this.paint,this);this.paint();},
  onRemove(host){host.off('moveend zoomend resize',this.paint,this);this.canvas.remove();},
  paint(){const host=this.host,size=host.getSize(),origin=host.containerPointToLayerPoint([0,0]),scale=Math.min(window.devicePixelRatio||1,2),canvas=this.canvas;
   canvas.width=Math.ceil(size.x*scale);canvas.height=Math.ceil(size.y*scale);canvas.style.width=size.x+'px';canvas.style.height=size.y+'px';L.DomUtil.setPosition(canvas,origin);
   const ctx=canvas.getContext('2d');ctx.scale(scale,scale);const at=([x,y])=>host.latLngToContainerPoint([y,x]);
   // Original native domain is the clipping mask, including coastline and holes.
   // No snow extrapolation to the sea or across absent mountain-domain supports.
   const view=host.getBounds();ctx.save();ctx.beginPath();
   for(const feature of features){const box=extent(feature);if(box[2]<view.getWest()||box[0]>view.getEast()||box[3]<view.getSouth()||box[1]>view.getNorth())continue;
    for(const rings of polygonsOf(feature.geometry))for(const ring of rings){ring.forEach((coordinate,i)=>{const p=at(coordinate);if(i)ctx.lineTo(p.x,p.y);else ctx.moveTo(p.x,p.y);});ctx.closePath();}
   }
   ctx.clip('evenodd');
   for(let band=0;band<bands.length;band++){const color=bands[band][2];ctx.globalAlpha=[.06,.28,.46,.62][band]*(stale?.45:1);ctx.beginPath();for(const polygon of field.polygons){if(polygon.color!==color)continue;polygon.points.forEach((coordinate,i)=>{const p=at(coordinate);if(i)ctx.lineTo(p.x,p.y);else ctx.moveTo(p.x,p.y);});ctx.closePath();}ctx.fillStyle=stale?'#7c8c96':color;ctx.fill();}
   // A solitary native column does not justify inventing an area around it.
   ctx.globalAlpha=stale?.25:.8;for(const feature of field.isolated){const p=feature.properties,point=at([p.lon,p.lat]);ctx.beginPath();ctx.arc(point.x,point.y,4,0,2*Math.PI);ctx.fillStyle=stale?'#7c8c96':'#6cb8dd';ctx.fill();}
   ctx.restore();canvas.dataset.snowLead=String(lead);canvas.dataset.snowNativeSpacingM='10000';canvas.dataset.snowSurfaceMethod=field.method;canvas.dataset.snowPolygons=String(field.polygons.length);canvas.dataset.snowIsolatedColumns=String(field.isolated.length);
  }
 });
 return new Surface().addTo(map);
}
