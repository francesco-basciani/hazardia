export function sampleVector(field,record,lat,lon){
 if(!field||!record?.u||!record?.v)return null;
 const ys=field.lats,xs=field.lons,ny=ys.length,nx=xs.length;
 if(lat<ys[0]||lat>ys[ny-1]||lon<xs[0]||lon>xs[nx-1])return null;
 const gx=(lon-xs[0])/(xs[1]-xs[0]),gy=(lat-ys[0])/(ys[1]-ys[0]),x=Math.min(nx-2,Math.floor(gx)),y=Math.min(ny-2,Math.floor(gy)),dx=gx-x,dy=gy-y;
 const sum=a=>a[y*nx+x]*(1-dx)*(1-dy)+a[y*nx+x+1]*dx*(1-dy)+a[(y+1)*nx+x]*(1-dx)*dy+a[(y+1)*nx+x+1]*dx*dy;
 const corners=[y*nx+x,y*nx+x+1,(y+1)*nx+x,(y+1)*nx+x+1];if(corners.some(i=>!Number.isFinite(record.u[i])||!Number.isFinite(record.v[i])))return null;
 return [sum(record.u),sum(record.v)];
}
export function sampleScalar(field,record,key,lat,lon){
 if(!record?.[key])return null;const v=sampleVector(field,{u:record[key],v:record[key]},lat,lon);return v?v[0]:null;
}

// Geometry only: bounded per-map plans. Values/time are always sampled anew.
const screenPlans=new WeakMap();
export function screenSamplePlan(map,field,cols,rows,stepX,stepY,offset=.5,slot='raster'){
 if(!field?.lats||!field?.lons||cols<1||rows<1)return null;
 const b=map.getBounds?.(),view=b?[b.getSouth(),b.getWest(),b.getNorth(),b.getEast()]:[];
 const key=[cols,rows,stepX,stepY,offset,field.lats.length,field.lons.length,...view,...field.lats,...field.lons].join(',');
 let slots=screenPlans.get(map);if(!slots){slots=new Map();screenPlans.set(map,slots);}const cached=slots.get(slot);if(cached?.key===key)return cached;
 const ys=field.lats,xs=field.lons,nx=xs.length,ny=ys.length,base=new Int32Array(cols*rows),weights=new Float64Array(cols*rows*4);base.fill(-1);
 for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){
  const p=map.containerPointToLatLng([(x+offset)*stepX,(y+offset)*stepY]);if(p.lat<ys[0]||p.lat>ys[ny-1]||p.lng<xs[0]||p.lng>xs[nx-1])continue;
  const gx=(p.lng-xs[0])/(xs[1]-xs[0]),gy=(p.lat-ys[0])/(ys[1]-ys[0]),a=Math.min(nx-2,Math.floor(gx)),b=Math.min(ny-2,Math.floor(gy)),dx=gx-a,dy=gy-b,i=y*cols+x;base[i]=b*nx+a;weights.set([(1-dx)*(1-dy),dx*(1-dy),(1-dx)*dy,dx*dy],i*4);
 }
 const plan={key,base,weights,nx};slots.set(slot,plan);return plan;
}
export function plannedScalar(plan,values,i){
 if(!plan||!values)return null;const j=plan.base[i];if(j<0)return null;const nx=plan.nx,a=values[j],b=values[j+1],c=values[j+nx],d=values[j+nx+1];if(!Number.isFinite(a)||!Number.isFinite(b)||!Number.isFinite(c)||!Number.isFinite(d))return null;const k=i*4,w=plan.weights;return a*w[k]+b*w[k+1]+c*w[k+2]+d*w[k+3];
}
