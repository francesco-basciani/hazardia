// Read our local archive only: opening the panel never requests the provider.
export function radarHistorySummary(p,now=Date.now()){
 if(p?.schema!=='hazardia.avalanche.RadarHistoryStatus/1.0'||p.product!=='SRT1'||p.units!=='mm'||!Number.isInteger(p.frames)||!Array.isArray(p.recent)||p.recent.length>48)throw Error('Storico radar non compatibile');
 const age=(now-Date.parse(p.last_end))/3600000;
 return {frames:p.frames,stale:!Number.isFinite(age)||age<0||age>2,status:p.status,missingHours:p.missing_hours?.length||0};
}
export async function radarHistoryDetail(){
 const r=await fetch('/assets/avalanche-radar-history/status.json',{cache:'no-store'});if(!r.ok)throw Error('Archivio radar non disponibile (HTTP '+r.status+')');const raw=await r.arrayBuffer();if(raw.byteLength>256*1024)throw Error('Indice radar oltre il limite');const p=JSON.parse(new TextDecoder().decode(raw)),summary=radarHistorySummary(p);
 const box=document.createElement('div');box.dataset.avalancheRadarHistory='true';const add=(tag,text,parent=box)=>{const el=document.createElement(tag);el.textContent=text;parent.append(el);return el;},date=x=>x?new Date(x).toLocaleString('it-IT',{timeZone:'Europe/Rome'}):'non disponibile',fmt=x=>Number.isFinite(x)?x.toLocaleString('it-IT',{maximumFractionDigits:2}):'mancante';
 add('h3','Gran Sasso · storico radar e pluviometri');add('strong',summary.frames+(summary.frames===1?' finestra oraria archiviata · ':' finestre orarie archiviate · ')+(summary.stale?'ultimo dato scaduto o assente':p.status==='DEGRADED'||summary.missingHours?'raccolta degradata o con lacune':'raccolta oraria attiva'));
 add('p','SRT1: precipitazione cumulata in un’ora, in mm. Stima radar + pluviometri; non centimetri di neve o stratigrafia. Nessuna correzione automatica di SNOWPACK applicata.');
 add('p','Archivio dal '+date(p.first_end?new Date(Date.parse(p.first_end)-3600000).toISOString():null)+' al '+date(p.last_end)+'. Controllo '+date(p.checked_at)+'. '+summary.missingHours+' ore mancanti tra il primo e l’ultimo dato; le ore precedenti all’avvio non sono ricostruite.');
 if(p.error)add('p','Acquisizione non riuscita: '+p.error+'. I dati precedenti sono conservati.',box);
 add('p','File numerici regionali sulla griglia nativa, circa1km. Statistiche sull’inviluppo rettangolare del Gran Sasso, non su ogni pendio. Nessuna interpolazione al dettaglio del terreno.');
 for(const row of p.recent){const details=add('details',''),title=date(row.valid_from)+' → '+date(row.valid_until)+' · media '+fmt(row.mean_mm)+'mm · massimo '+fmt(row.max_mm)+'mm';add('summary',title,details);add('p','Pixel utilizzabili '+row.valid_pixels+'/'+row.total_pixels+'; mancanti '+row.missing_pixels+'. Origine: '+row.origin,details);add('p','Disponibile nel nostro archivio dal '+date(row.available_at)+'. Nessuna disponibilità retrodatata.',details);add('p','Qualità: prodotto informativo non validato. Copertura e anomalie radar possono ridurre l’affidabilità; dati mancanti non sono precipitazione zero.',details);
  if(/^assets\/[a-f0-9]{64}\.tif$/.test(row.file)){const a=add('a','Scarica raster numerico regionale · GeoTIFF',details);a.href='/assets/avalanche-radar-history/'+row.file;a.download='SRT1-'+row.valid_until+'.tif';a.style.color='#a8dff5';}
  add('p','SHA256 regionale '+row.sha256,details).style.overflowWrap='anywhere';
 }
 add('p','Archivio persistente con revisioni; limiti di rete/disco attivi. Quando lo spazio assegnato è pieno la raccolta si sospende senza eliminare lo storico. Consultazione locale, indipendente dal portale esterno.');const source=add('a','Fonte e licenza Radar-DPC · CC-BY-SA');source.href='https://dpc-radar.readthedocs.io/it/latest/';source.target='_blank';source.rel='noopener noreferrer';source.style.color='#a8dff5';return box;
}
