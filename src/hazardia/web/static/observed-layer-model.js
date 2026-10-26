/* Display filters only. Never hazard, damage, flight or optimizer criteria. */
export const powerColor=v=>v==null?'#b5c1ca':v>=380000?'#ef637d':v>=220000?'#f6a749':v>=132000?'#f4d76a':'#65d4d1';
export function powerVisible(p,{minVoltage=35000,unknown=false,cables=false,stations=false,towers=false,aerial=false}={}){
 if(aerial)return ['tower','pole'].includes(p.power_kind)||(['line','minor_line','cable'].includes(p.power_kind)&&p.location==='overhead');
 const v=p.max_voltage;
 if(p.power_kind==='substation')return stations&&(v==null||v>=minVoltage);
 if(['tower','pole'].includes(p.power_kind))return towers;
 if(!['line','minor_line','cable'].includes(p.power_kind))return false;
 if(p.location!=='overhead'&&!cables)return false;
 return v==null?unknown:v>=minVoltage;
}

export const quakeVisible=(p,minimum=0)=>p.event_type==='earthquake'&&Number.isFinite(p.magnitude)&&p.magnitude>=minimum;

export const quakeClasses=[{min:-Infinity,label:'M < 1',color:'#75d5dd'},{min:1,label:'1 ≤ M < 2',color:'#48bca0'},{min:2,label:'2 ≤ M < 3',color:'#f1d25c'},{min:3,label:'3 ≤ M < 4',color:'#f39a48'},{min:4,label:'4 ≤ M < 5',color:'#ed605c'},{min:5,label:'M ≥ 5',color:'#c97ccf'}];
export function quakeStyle(m){if(!Number.isFinite(m))return {radius:3,color:'#e8edf1',fillColor:'#8897a3',fillOpacity:.6,weight:1.2};const band=quakeClasses.filter(c=>m>=c.min).at(-1);return {radius:3+2*Math.max(0,Math.min(9,m)),color:'#f2f6fa',fillColor:band.color,fillOpacity:.65,weight:1.2};}

// Acquire a padded, degree-aligned catalogue window to avoid a request per pan.
export function quakeQueryBounds(view,regional=false){
 const limits=regional?[6,35,19,48]:[-180,-85,180,85];
 if(view.some(v=>!Number.isFinite(v))||view[0]>=view[2]||view[1]>=view[3])return view;
 // Do not disguise a dateline/out-of-coverage request as a valid regional one.
 if(regional&&view.some((v,i)=>i<2?v<limits[i]:v>limits[i]))return view;
 return view.map((v,i)=>i<2?Math.max(limits[i],Math.floor(v-.5)):Math.min(limits[i],Math.ceil(v+.5)));
}
export function quakeSnapshotCovers(data,view,{provider,days,min_magnitude},now=Date.now()){
 if(!data||data.status!=='READY'||!data.bounds||!data.quality)return false;
 if(provider==='auto')return quakeAcquisitionPlan(view,{provider,days,min_magnitude}).every(leg=>(data.catalogues||[data]).some(part=>quakeSnapshotCovers(part,leg.view,leg.body,now)));
 const q=data.quality,age=now-Date.parse(data.acquired_at),duration=Date.parse(q.window_end)-Date.parse(q.window_start);
 return age>=0&&age<600000&&q.provider===provider&&q.min_magnitude<=min_magnitude&&(!q.limit_reached||q.min_magnitude===min_magnitude)&&duration===days*86400000&&view.every((v,i)=>i<2?v>=data.bounds[i]-.0001:v<=data.bounds[i]+.0001);
}

const italianCatalogue=[6,35,19,48];
export function quakeAcquisitionPlan(view,{provider='auto',days=7,min_magnitude=0}={}){
 const clipped=[Math.max(view[0],6),Math.max(view[1],35),Math.min(view[2],19),Math.min(view[3],48)],intersects=clipped[0]<clipped[2]&&clipped[1]<clipped[3],inside=view.every((v,i)=>i<2?v>=italianCatalogue[i]:v<=italianCatalogue[i]);
 const part=(p,v)=>({view:v,body:{bounds:quakeQueryBounds(v,p==='ingv'),provider:p,days,min_magnitude}});
 if(provider!=='auto')return [part(provider,view)];
 return [...(intersects?[part('ingv',clipped)]:[]),...(!inside?[part('usgs',view)]:[])];
}
export function combineQuakeSnapshots(parts){
 if(parts.length===1)return parts[0];
 const regional=parts.find(p=>p.quality.provider==='ingv'),global=parts.find(p=>p.quality.provider==='usgs');
 const features=parts.flatMap(p=>p.features.filter(f=>{const [x,y]=f.geometry.coordinates;return !(p===global&&regional&&x>=regional.bounds[0]&&x<=regional.bounds[2]&&y>=regional.bounds[1]&&y<=regional.bounds[3]);}).map(f=>({...f,id:p.quality.provider+':'+f.id,properties:{...f.properties,catalogue_provider:p.quality.provider}})));
 features.sort((a,b)=>Date.parse(b.properties.at)-Date.parse(a.properties.at));
 return {status:'READY',type:'FeatureCollection',features,bounds:(global||regional).bounds,acquired_at:parts.map(p=>p.acquired_at).sort()[0],catalogues:parts,quality:{provider:'ingv+usgs',min_magnitude:parts[0].quality.min_magnitude,window_start:parts.map(p=>p.quality.window_start).sort()[0],window_end:parts.map(p=>p.quality.window_end).sort().at(-1),window_semantics:'ENVELOPE_OF_SOURCE_WINDOWS',license:'INGV CC BY4.0; USGS public-domain data',limit_reached:parts.some(p=>p.quality.limit_reached),skipped:parts.reduce((n,p)=>n+(p.quality.skipped||0),0)}};
}
