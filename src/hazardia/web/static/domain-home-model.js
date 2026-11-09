/* Presentation catalogue only. Never a model registry or scientific capability grant. */
export const domains=Object.freeze([
 {id:'fire',name:'Incendi',description:'Osservazioni satellitari, suscettibilità, propagazione e interventi.',icon:'fire',image:'fire',label:'Monitoraggio e scenari',primary:'Incendi',lab:'fire'},
 {id:'water',name:'Acque e alluvioni',description:'Bacini, precipitazioni, allerte e risultati dei modelli idrologici.',icon:'hydrometers',image:'water',label:'Monitoraggio e modelli',primary:'Criticità territoriali',lab:'flood'},
 {id:'snow',name:'Neve e valanghe',description:'Neve osservata, evoluzione del manto e condizioni valanghive.',icon:'environment',image:'snow',label:'Monitoraggio sperimentale',primary:'Valanghe'},
 {id:'seismic',name:'Terremoti e fenomeni geologici',description:'Sismicità osservata. Frane e altri fenomeni geologici da integrare.',icon:'quake',image:'seismic',label:'Sismicità osservata',primary:'Terremoti osservati'},
 {id:'infrastructure',name:'Infrastrutture e reti',description:'Reti elettriche, cavi aerei, impianti e contesto territoriale.',icon:'utilities',image:'infrastructure',label:'Cartografia e contesto',primary:'Reti e impianti'},
 {id:'mobility',name:'Mobilità e trasporti',description:'Rete stradale, accessibilità e traffico simulato su strade reali.',icon:'transport',image:'mobility',label:'Cartografia e simulazione visuale',primary:'Strade e trasporti',lab:'traffic'},
 {id:'security',name:'Sicurezza territoriale',description:'TCIP: dati sui reati registrati, distribuzioni territoriali e fonti.',icon:'critical',image:'security',label:'Analisi territoriale',primary:'TCIP'},
 {id:'health',name:'Sanità ed emergenze',description:'Dati cartografici già consultabili; dominio e scenari sanitari da sviluppare.',icon:'healthcare',planned:true},
 {id:'environment',name:'Ambiente e inquinamento',description:'Qualità dell’aria, fumo e contaminazione: dominio da sviluppare.',icon:'environment',planned:true}
].map(Object.freeze));
export const domainById=id=>domains.find(d=>d.id===id&&!d.planned)||null;
export const validViews=new Set(['home','map','results','sources','help']);
export function portalRoute(search){const p=new URLSearchParams(search),view=p.get('view');return {view:validViews.has(view)?view:(p.has('case')||p.has('a')||p.has('b')?'results':'home'),domain:domainById(p.get('domain'))?.id||(view==='results'&&p.get('lab')==='traffic'?'mobility':view==='results'&&(['evacuation','flood'].includes(p.get('lab'))||p.get('flood-rescue')==='1')?'water':'all')};}
export function portalURL(search,view,domain='all'){const p=new URLSearchParams(search);p.set('view',validViews.has(view)?view:'home');if(domainById(domain))p.set('domain',domain);else p.delete('domain');return '/?'+p;}
