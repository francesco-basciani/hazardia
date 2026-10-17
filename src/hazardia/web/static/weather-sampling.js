export function sampleVector(field,record,lat,lon){
 const ys=field.lats,xs=field.lons,ny=ys.length,nx=xs.length;
 if(lat<ys[0]||lat>ys[ny-1]||lon<xs[0]||lon>xs[nx-1])return null;
 const gx=(lon-xs[0])/(xs[1]-xs[0]),gy=(lat-ys[0])/(ys[1]-ys[0]),x=Math.min(nx-2,Math.floor(gx)),y=Math.min(ny-2,Math.floor(gy)),dx=gx-x,dy=gy-y;
 const sum=a=>a[y*nx+x]*(1-dx)*(1-dy)+a[y*nx+x+1]*dx*(1-dy)+a[(y+1)*nx+x]*(1-dx)*dy+a[(y+1)*nx+x+1]*dx*dy;
 return [sum(record.u),sum(record.v)];
}
export function sampleScalar(field,record,key,lat,lon){
 if(!record?.[key])return null;const v=sampleVector(field,{u:record[key],v:record[key]},lat,lon);return v?v[0]:null;
}
