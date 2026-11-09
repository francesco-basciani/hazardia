import {localMember} from './avalanche-gran-sasso.js?v=snow-depth-20261102';
// Display existing native HS; never infer snowfall from a change in depth.
export const snowDepthLegend=[
 ['#cdf8ff','>0–5 cm'],['#7bddf5','5–20 cm'],['#389edb','20–50 cm'],
 ['#2165b6','50–100 cm'],['#253d83','oltre 100 cm'],['#a3adb8','Dato mancante']
];
export function snowDepthValue(product,feature,lead=0,now=Date.now(),allowDated=false){
 const m=product.metadata,age=(now-Date.parse(m.reference_utc))/3600000,wxAge=(now-Date.parse(m.weather_run_utc))/3600000;
 const dated=m.temporal_mode==='RETROSPECTIVE_CACHED_FORCING'||!Number.isFinite(age)||age<0||age>9||!Number.isFinite(wxAge)||wxAge<0||wxAge>12;
 if(![0,24,48,72].includes(lead)||dated&&!allowDated)return {missing:true,dated};
 const entries=product.models[feature.properties.profile_id],values=['NWP_INITIAL','ZERO_INITIAL'].map(k=>localMember(entries,k)?.hourly?.quantities?.hs?.[lead]);
 if(values.some(v=>typeof v!=='number'||!Number.isFinite(v)||v<0))return {missing:true,dated};
 return {missing:false,dated,min:Math.min(...values),max:Math.max(...values),values};
}
export function snowDepthRGBA(value,showMissing=true){
 if(value?.missing||!value)return showMissing?[163,173,184,28]:[0,0,0,0];
 const hs=value.max;if(hs===0)return [0,0,0,0];
 return hs<=5?[205,248,255,190]:hs<=20?[123,221,245,200]:hs<=50?[56,158,219,210]:hs<=100?[33,101,182,220]:[37,61,131,230];
}
export function snowDepthPalette(product,lead,now=Date.now(),allowDated=false,showMissing=true){
 const values=new Map(product.features.map(f=>[f.properties.profile_id,snowDepthValue(product,f,lead,now,allowDated)])),palette=new Map([[65535,snowDepthRGBA(null,showMissing)]]);
 for(const [label,id]of Object.entries(product.raster_index.labels))palette.set(Number(label),snowDepthRGBA(values.get(id),showMissing));
 return palette;
}
export function paintSnowDepth(grid,palette,startRow,endRow,output,extent=null){
 let snowPixels=0,missingPixels=0;
 for(let row=startRow;row<Math.min(endRow,grid.height);row++)for(let col=0;col<grid.width;col++){
  const i=row*grid.width+col,label=grid.view.getUint16(i*2,true),color=label===0?[0,0,0,0]:palette.get(label)||[0,0,0,0];
  output.set(color,i*4);if(color[3]&&color[0]===163)missingPixels++;else if(color[3]){snowPixels++;if(extent){extent[0]=Math.min(extent[0],col);extent[1]=Math.min(extent[1],row);extent[2]=Math.max(extent[2],col+1);extent[3]=Math.max(extent[3],row+1);}}
 }
 return {snowPixels,missingPixels};
}
