// One catalogue entry and one visibility owner; existing readers stay independent.
export function attachTcipGroup({map,entry,refresh},views){
 const panel=document.createElement('section');panel.dataset.category='tcip';panel.dataset.revealOnActivate='true';
 const title=document.createElement('h3');title.textContent='TCIP';
 const master=document.createElement('input');master.type='checkbox';master.setAttribute('aria-label','Mostra TCIP');
 const enabled=document.createElement('label');enabled.append(master,document.createTextNode(' Mostra TCIP sulla mappa'));
 const mode=document.createElement('select');mode.setAttribute('aria-label','Visualizzazione TCIP');
 const modeLabel=document.createElement('label');modeLabel.append(document.createTextNode('Visualizzazione'),mode);
 const reset=document.createElement('button');reset.type='button';reset.textContent='Totale reati · tutto il DB · massimo dettaglio';
 const note=document.createElement('p');note.textContent='Vista iniziale: totale reati per100.000 residenti, cumulato di tutti gli anni disponibili, al dettaglio osservato più fine. Le viste alternative hanno misure e coperture proprie; non vengono sommate ai tassi.';
 const content=document.createElement('div');panel.append(title,enabled,modeLabel,reset,note,content);
 const children=new Map();let syncing=false,disposed=false;
 const signal=()=>master.dispatchEvent(new Event('hazardia-state'));
 const notify=input=>input.dispatchEvent(new Event('change',{bubbles:true}));
 function hideOthers(selected){for(const [id,child] of children){child.panel.hidden=id!==selected;if(id!==selected&&child.input.checked){child.input.checked=false;notify(child.input);}}}
 function apply(){if(disposed)return;syncing=true;try{hideOthers(mode.value);const selected=children.get(mode.value);if(selected){selected.input.checked=master.checked;notify(selected.input);}}finally{syncing=false;}signal();}
 for(const view of views){
  mode.append(new Option(view.label,view.id));
  view.attach({map,refresh:()=>{},entry:(_name,node,_icon,input)=>{
   node.dataset.tcipView=view.id;input.closest('label').hidden=true;content.append(node);children.set(view.id,{panel:node,input});
   const sync=()=>{if(syncing||disposed)return;syncing=true;try{if(input.checked){mode.value=view.id;master.checked=true;hideOthers(view.id);}else if(mode.value===view.id){master.checked=false;}}finally{syncing=false;}signal();};
   input.addEventListener('change',sync);input.addEventListener('hazardia-state',sync);
  }});
 }
 mode.value=views[0].id;hideOthers(mode.value);
 master.onchange=apply;mode.onchange=apply;
 reset.onclick=()=>{mode.value=views[0].id;master.checked=true;syncing=true;try{hideOthers(mode.value);const child=children.get(mode.value);const preset=child.panel.querySelector('button[data-tcip-total]');if(preset)preset.click();else{child.input.checked=true;notify(child.input);}}finally{syncing=false;}signal();};
 entry('TCIP',panel,'▦',master);refresh();
 map.on('unload',()=>{disposed=true;});
}
