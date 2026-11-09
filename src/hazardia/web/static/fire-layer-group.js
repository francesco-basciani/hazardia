// One fire menu entry; forecast indices and historical susceptibility keep their own meaning.
export function createFireLayerGroup({map,entry,refresh},effisPanel,effisInput){
 const panel=document.createElement('section');panel.dataset.category='fire';panel.dataset.revealOnActivate='true';
 const heading=document.createElement('h3');heading.textContent='Incendi';
 const master=document.createElement('input');master.type='checkbox';master.checked=effisInput.checked;master.setAttribute('aria-label','Mostra livello Incendi');
 const label=document.createElement('label');label.append(master,document.createTextNode(' Mostra incendi sulla mappa'));
 const mode=document.createElement('select');mode.setAttribute('aria-label','Visualizzazione incendi');
 const modeLabel=document.createElement('label');modeLabel.append(document.createTextNode('Visualizzazione'),mode);
 const note=document.createElement('p');note.textContent='WII: suscettibilità storica di innesco. EFFIS: pericolosità meteo FWI e secchezza DC per la data selezionata. Scegli una vista; scale e periodi rimangono distinti.';
 const content=document.createElement('div');panel.append(heading,label,modeLabel,note,content);
 const views=new Map();let syncing=false,disposed=false;
 const changed=input=>input.dispatchEvent(new Event('change',{bubbles:true}));
 const signal=()=>master.dispatchEvent(new Event('hazardia-state'));
 function apply(){if(disposed)return;syncing=true;try{for(const [id,view] of views){view.panel.hidden=id!==mode.value;const enabled=master.checked&&id===mode.value;if(view.input.checked!==enabled){view.input.checked=enabled;changed(view.input);}}}finally{syncing=false;}signal();}
 function add(id,title,node,input){
  views.set(id,{panel:node,input});mode.append(new Option(title,id));input.closest('label').hidden=true;content.append(node);
  const sync=()=>{if(syncing||disposed)return;if(input.checked){mode.value=id;master.checked=true;}else if(mode.value===id)master.checked=false;apply();};
  input.addEventListener('change',sync);input.addEventListener('hazardia-state',sync);
 }
 add('effis','Pericolosità e secchezza · EFFIS',effisPanel,effisInput);mode.value='effis';apply();
 master.onchange=apply;mode.onchange=apply;
 entry('Incendi',panel,'◈',master);
 map.on('unload',()=>{disposed=true;});
 return {panel,select(id){if(views.has(id)){mode.value=id;apply();}},addWii(node,input){if(disposed||views.has('wii'))return;add('wii','Rischio di innesco · WII',node,input);if(!master.checked)mode.value='wii';apply();refresh();}};
}
