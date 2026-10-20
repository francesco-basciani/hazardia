/* Presentation only: reuse controls and preserve their data/event contracts. */
export function cleanRoom(){
 const map=document.getElementById('monitor-map');if(!map||document.querySelector('.monitor-dock'))return;
 const el=(tag,cls,content)=>{const e=document.createElement(tag);e.className=cls;if(content)e.textContent=content;return e;};
 const layout=document.querySelector('.monitor-layout'),dock=el('aside','monitor-dock');dock.setAttribute('aria-label','Livelli e contesto');const title=el('div','dock-heading','Livelli e contesto');dock.append(title);layout.append(dock);
 const heading=document.querySelector('.monitor-heading');heading.querySelector('h1').textContent='Monitoraggio';const sub=el('span','workspace-caption','Territorio · meteo · criticità');heading.append(sub);
 const search=document.getElementById('monitor-search');search.classList.add('room-search');search.querySelector('input').placeholder='Cerca un luogo o coordinate';heading.append(search);const searchStatus=document.getElementById('monitor-search-status');heading.after(searchStatus);
 const weather=el('section','dock-section');weather.append(el('h2','','Meteo e previsioni'));dock.append(weather);
 for(const s of ['.map-weather-toolbar','#map-weather-readout','#map-weather-key']){const n=document.querySelector(s);if(n)weather.append(n);}
 const picker=weather.querySelector('.map-weather-picker');if(picker)picker.open=true;
 const territory=document.querySelector('#monitor-section .territorial-panel');if(territory){const details=el('details','dock-section territory-drawer');details.append(el('summary','','Territorio e infrastrutture'),territory);dock.append(details);}
 const metadata=el('details','monitor-metadata');metadata.append(el('summary','','Stato delle fonti e dettagli della mappa'));
 for(const id of ['attention-map-status','attention-legend','wind-map-time','weather-map-legend']){const n=document.getElementById(id);if(n)metadata.append(n);}
 const canvas=document.querySelector('.monitor-canvas');canvas.append(metadata);
 const toolbar=document.querySelector('.monitor-map-toolbar');for(const [id,name,title] of [['monitor-fit','Centra','Centra le aree disponibili'],['map-settings-open','Configura','Configurazione della mappa'],['attention-open','Criticità','Fonti e aree di attenzione territoriale']]){const b=document.getElementById(id);b.textContent=name;b.title=title;}const base=el('label','room-basemap');base.append(document.createTextNode('Sfondo'),document.getElementById('monitor-basemap'));toolbar.querySelector('fieldset').after(base);const layers=el('button','small-button dock-toggle','Livelli');layers.type='button';layers.id='monitor-dock-toggle';layers.setAttribute('aria-expanded','true');layers.setAttribute('aria-controls','monitor-dock');dock.id='monitor-dock';layers.onclick=()=>{const open=layers.getAttribute('aria-expanded')!=='true';layers.setAttribute('aria-expanded',String(open));dock.hidden=!open;layout.classList.toggle('dock-hidden',!open);window.dispatchEvent(new Event('resize'));};dock.hidden=true;layout.classList.add('dock-hidden');layers.setAttribute('aria-expanded','false');toolbar.append(layers);
 const brand=document.querySelector('.brand');if(brand)brand.title='HAZARDIA · Hazard-Aware Adaptive Resource and Decision Intelligence Architecture';
 document.body.classList.add('clean-room');
 new ResizeObserver(()=>window.dispatchEvent(new Event('hazardia-map-resize'))).observe(map);
}
