/* Optional, zoom-dependent gazetteer labels; no terrain or forecast input changes. */
let source;
export function mountainAltitude(f,language='it'){const v=f.elevation;return typeof v==='number'&&Number.isFinite(v)&&v>=-500&&v<=10000?(['MTS','PKS'].includes(f.code)?(language==='en'?'ref. ':'rif. '):'')+Math.round(v)+' m':language==='en'?'elevation n/a':'quota n/d';}

export const mountainMinZoom=f=>['MTS','PKS'].includes(f.code)?8:f.code==='VLC'?9:f.code==='MT'?(f.elevation>=2000?9:10):f.code==='PK'?12:14;
export function selectMountainLabels(features,zoom,project,size,occupied=[]){
 if(zoom<8)return [];
 const used=occupied.map(p=>({x:p.x,y:p.y,w:p.w||140,h:p.h||24})),result=[];
 const sorted=features.filter(f=>typeof f.name==='string'&&f.name.length<=160&&Number.isFinite(f.lat)&&Number.isFinite(f.lon)&&zoom>=mountainMinZoom(f)).sort((a,b)=>mountainMinZoom(a)-mountainMinZoom(b)||(b.elevation??-9999)-(a.elevation??-9999)||Number(a.id)-Number(b.id));
 const limit=zoom>=14?100:zoom>=12?75:45;
 for(const f of sorted){const p=project(f);if(!p)continue;const w=Math.min(300,Math.max(100,(f.name.length+Math.max(mountainAltitude(f).length,mountainAltitude(f,'en').length)+3)*6.6+16)),h=23;if(p.x<12||p.y<12||p.x+w>size.x-8||p.y+h>size.y-8||used.some(q=>p.x<q.x+q.w+8&&p.x+w+8>q.x&&p.y<q.y+q.h+5&&p.y+h+5>q.y))continue;if(result.some(q=>q.name.toLocaleLowerCase()===f.name.toLocaleLowerCase()&&Math.abs(q.pixel.x-p.x)<200&&Math.abs(q.pixel.y-p.y)<100))continue;result.push({...f,pixel:p,width:w});used.push({x:p.x,y:p.y,w,h});if(result.length>=limit)break;}
 return result;
}
export function mountainOptions(id='mountain-names'){
 const root=document.createElement('section'),label=document.createElement('label'),input=document.createElement('input'),status=document.createElement('p');root.className='mountain-options';input.type='checkbox';input.id=id;label.append(input,document.createTextNode(' Nomi dei monti e delle cime'));status.setAttribute('role','status');status.textContent='Italia · GeoNames · nomi da zoom8, cime da12 e valichi da14. Copertura non esaustiva; i nomi stampati nello sfondo restano indipendenti. Quote GeoNames non verificate; quota n/d se assente. Per catene e gruppi, rif. indica la quota di un punto di riferimento, non il massimo della catena.';root.append(label,status);return {root,input,status};
}
export function mountainNames(map,{input,status}){
 const pane='mountainNames';if(!map.getPane(pane))map.createPane(pane);map.getPane(pane).style.zIndex=609;map.getPane(pane).style.pointerEvents='none';const group=L.layerGroup().addTo(map);let data=null,disposed=false,frame=null;
 const original=status.textContent;
 function draw(){frame=null;if(disposed)return;group.clearLayers();map.getContainer().dataset.mountainNames='0';if(!input.checked){status.textContent=original;return;}if(map.getZoom()<8){status.textContent='Nomi dei monti: aumenta lo zoom ad almeno8.';return;}if(!data)return;
  const b=map.getBounds(),size=map.getSize();const occupied=[...map.getContainer().querySelectorAll('.map-place-name,.geo-label.place,.region-name,.weather-site')].map(n=>{const r=n.getBoundingClientRect(),base=map.getContainer().getBoundingClientRect();return {x:r.left-base.left,y:r.top-base.top,w:r.width,h:r.height};});
  const selected=selectMountainLabels(data.features.filter(f=>b.contains([f.lat,f.lon])),map.getZoom(),f=>map.latLngToContainerPoint([f.lat,f.lon]),size,occupied);
  for(const f of selected){const span=document.createElement('span'),name=document.createElement('span'),altitude=document.createElement('span');name.className='mountain-label-name';name.textContent=(['PASS','SDL','GAP'].includes(f.code)?'⋈ ':'▲ ')+f.name;altitude.className='mountain-label-elevation';altitude.textContent=' · '+mountainAltitude(f,document.documentElement.lang);span.append(name,altitude);L.marker([f.lat,f.lon],{pane,interactive:false,keyboard:false,icon:L.divIcon({className:'map-mountain-name',html:span,iconSize:[f.width,23],iconAnchor:[0,0]})}).addTo(group);}
  map.getContainer().dataset.mountainNames=String(selected.length);status.textContent=selected.length?original:'Nessun nome montano disponibile in questa inquadratura a questo zoom. Fonte limitata all’Italia; non significa assenza di rilievi.';
 }
 const schedule=()=>{if(frame!==null)cancelAnimationFrame(frame);frame=requestAnimationFrame(draw);};
 async function update(){if(!input.checked){schedule();return;}if(!data){status.textContent='Caricamento nomi dei monti…';if(!source)source=fetch('/assets/mountain-names.json').then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).catch(e=>{source=null;throw e;});try{data=await source;if(data.schema!=='hazardia-mountain-names/1'||!Array.isArray(data.features))throw Error('Formato non valido');if(!disposed)map.attributionControl.addAttribution('GeoNames · CC BY4.0');}catch(e){if(!disposed)status.textContent='Nomi dei monti non disponibili: '+e.message;return;}}schedule();}
 document.addEventListener('hazardia-language',schedule);input.addEventListener('change',update);map.on('moveend zoomend contextnames resize',schedule);if(input.checked)void update();
 return {remove(){disposed=true;if(frame!==null)cancelAnimationFrame(frame);document.removeEventListener('hazardia-language',schedule);input.removeEventListener('change',update);map.off('moveend zoomend contextnames resize',schedule);group.remove();}};
}
