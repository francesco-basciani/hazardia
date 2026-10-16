/* Place controls by task while retaining existing data/qualification panels. */
export function arrangeWorkspace(){
 const $=id=>document.getElementById(id),move=(parent,...nodes)=>nodes.filter(Boolean).forEach(n=>parent.append(n));
 document.querySelector('button[data-view="results"]').lastChild.textContent='Simulazioni e risorse';
 document.querySelector('.decision-heading h2').textContent='Simulazioni e risorse';
 document.querySelector('.sidebar h1').textContent='Scenario e unità';
 document.querySelector('.sidebar>.subtle').textContent='Unità per evacuazione · laboratorio di ricerca';
 document.querySelector('.evac-controls').open=true;document.querySelector('label[for=disabled]').hidden=true;$('disabled').hidden=true;
 document.querySelector('.evac-controls summary').textContent='Unità di evacuazione';
 document.querySelector('.monitor-heading .section-label').remove();$('monitor-heading').textContent='Monitoraggio · Abruzzo';document.querySelector('.monitor-heading p').remove();
 document.querySelector('.notice p').innerHTML='<strong>Ambiente di ricerca.</strong> Scenari ipotetici, non allerte operative.';
 const old=document.querySelector('.monitor-panel'),dialog=document.createElement('dialog');dialog.id='map-settings';dialog.className='monitor-panel settings-dialog';dialog.setAttribute('aria-labelledby','settings-title');while(old.firstChild)dialog.append(old.firstChild);old.replaceWith(dialog);
 dialog.querySelector('.section-label').remove();dialog.querySelector('h2').id='settings-title';dialog.querySelector('h2').textContent='Configurazione';dialog.querySelector('.monitor-disclaimer').remove();
 const close=document.createElement('button');close.type='button';close.className='small-button settings-close';close.textContent='Chiudi';close.onclick=()=>dialog.close();dialog.prepend(close);
 const open=document.createElement('button');open.type='button';open.className='small-button';open.id='map-settings-open';open.textContent='Configurazione';open.onclick=()=>dialog.showModal();document.querySelector('.monitor-map-toolbar').append(open);
 const cart=document.createElement('details');cart.className='settings-group';cart.open=true;cart.innerHTML='<summary>Cartografia</summary><label class="check"><input id="config-regions" type="checkbox" checked> Confini regionali nella vista d’insieme</label><small id="regions-status">Istat · 2026</small>';
 const basemap=$('monitor-basemap'),baseLabel=dialog.querySelector('label[for="monitor-basemap"]'),names=$('monitor-labels').closest('label');move(cart,baseLabel,basemap,names);dialog.querySelector('#monitor-search-status').after(cart);
 const meteo=document.querySelector('.regional-wind-panel'),bar=document.createElement('div');bar.className='map-weather-toolbar';bar.setAttribute('aria-label','Meteo sulla mappa');
 for(const id of ['wind-hour','map-weather-field']){const label=meteo.querySelector('label[for="'+id+'"]');label.textContent=id==='wind-hour'?'Previsione':'Livello meteo';const wrap=document.createElement('div');move(wrap,label,$(id));bar.append(wrap);}
 move(bar,$('wind-animation'),$('wind-fit'));const readout=document.createElement('div');readout.id='map-weather-readout';readout.className='map-weather-readout';readout.setAttribute('role','status');readout.textContent='Caricamento delle condizioni meteo…';document.querySelector('.monitor-map-toolbar').after(bar,readout,$('map-weather-key'));
 $('map-weather-field').value='temperature';$('simulation-weather').value='FORECAST';
 dialog.querySelector('.monitor-inspector').removeAttribute('open');document.querySelector('.monitor-canvas').append(dialog.querySelector('.monitor-inspector'));
 $('weather-use').addEventListener('click',()=>dialog.close());$('monitor-to-decisions').addEventListener('click',()=>dialog.close());
 let baseSync=false;for(const [source,target] of [['monitor-basemap','basemap'],['basemap','monitor-basemap']])$(source).addEventListener('change',()=>{if(baseSync)return;baseSync=true;$(target).value=$(source).value;$(target).dispatchEvent(new Event('change'));baseSync=false;});
 const details=document.createElement('details');details.className='settings-group';details.innerHTML='<summary>Meteo · dati e opzioni</summary>';meteo.replaceWith(details);details.append(meteo);const point=document.querySelector('.weather-panel'),pointDetails=document.createElement('details');pointDetails.className='settings-group';pointDetails.innerHTML='<summary>Meteo per nuove simulazioni · punto L’Aquila</summary>';point.replaceWith(pointDetails);pointDetails.append(point);
 const cases=document.createElement('details');cases.className='settings-group';cases.innerHTML='<summary>Scenari e trasparenza</summary>';cart.after(cases);move(cases,$('monitor-all'),document.querySelector('.fire-layer'),document.querySelector('.flood-layer'),dialog.querySelector('label[for="monitor-opacity"]'),$('monitor-opacity'),$('monitor-summary'));
 const foot=document.querySelector('.monitor-footnote');foot.hidden=true;details.append(foot);foot.hidden=false;
 // Keep map mode immediately adjacent to the maps, with annotation tools below.
 const modes=document.querySelector('.comparison .map-controls');modes.classList.add('comparison-map-toolbar');$('map-pair').before(modes);
 const annotations=document.createElement('details');annotations.className='map-annotations';annotations.id='map-annotations';annotations.innerHTML='<summary>Strumenti e annotazioni</summary>';document.querySelector('.comparison').append(annotations);move(annotations,document.querySelector('.drawing-toolbar'),$('drawing-status'));
 const geo=document.querySelector('.geographic-tools');const gDetails=document.createElement('details');gDetails.className='comparison-settings';gDetails.innerHTML='<summary>Ricerca e configurazione mappa</summary>';geo.replaceWith(gDetails);gDetails.append(geo);const configButton=document.createElement('button');configButton.type='button';configButton.className='small-button';configButton.textContent='Configurazione';configButton.onclick=()=>dialog.showModal();modes.append(configButton);
 const timeline=document.querySelector('.comparison .timeline');$('map-pair').after(timeline);
 const diagnostics=document.createElement('details');diagnostics.className='comparison-settings';diagnostics.innerHTML='<summary>Dati e limiti dello scenario</summary>';document.querySelector('.comparison').append(diagnostics);for(const sel of ['#map-source','.geo-precision','.physical-inline','#time-note'])move(diagnostics,document.querySelector(sel));
 const context=document.createElement('p');context.id='scenario-weather-context';context.className='scenario-weather-context';modes.before(context);
 const unitBox=document.createElement('section');unitBox.id='resource-editor';unitBox.innerHTML='<h3>Posiziona le unità di evacuazione</h3><p class="subtle">Clicca «Posiziona», poi sulla mappa. Imposta disponibilità e arrivo previsto.</p><div id="resource-rows"></div><p id="resource-editor-status" role="status">Evacuazione di ricerca. Posizioni e arrivi sono manuali; propagazione invariata. Squadre antincendio, Canadair ed elicotteri non sono ancora collegati al confronto fisico.</p>';
 const resourceFieldset=document.querySelector('.evac-controls fieldset'),pool=document.createElement('div');move(pool,document.querySelector('label[for=resources]'),$('resources'));resourceFieldset.prepend(pool,unitBox);
 const advanced=document.createElement('details');advanced.className='settings-group';advanced.innerHTML='<summary>Vincoli e priorità</summary>';for(const node of [...resourceFieldset.children])if(![pool,unitBox].includes(node)&&node.tagName!=='LEGEND')advanced.append(node);resourceFieldset.append(advanced);
 $('save-case').textContent='Salva impostazioni di base';
}
