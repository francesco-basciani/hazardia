/* Forecast amounts per complete hour, never observations or alert thresholds. */
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number=v=>v.toLocaleString('it-IT',{maximumFractionDigits:2});
const date=v=>new Date(v).toLocaleString('it-IT',{timeZone:'Europe/Rome',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});
export function seriesModel(rows){
 const points=(Array.isArray(rows)?rows:[]).slice(0,48).map(r=>({...r,known:r.status==='AVAILABLE'&&Number.isFinite(r.mean_mm)&&r.mean_mm>=0}));
 const available=points.filter(r=>r.known),peak=available.reduce((best,r)=>!best||r.mean_mm>best.mean_mm?r:best,null);
 return {points,available:available.length,peak,scale:peak?.mean_mm>0?Math.max(.1,peak.mean_mm):1};
}
export function seriesMarkup(rows){
 const {points,available,peak,scale}=seriesModel(rows);
 if(!points.length)return '<p class="rain-zone-note">Andamento orario non disponibile in questo archivio.</p>';
 const reading=r=>r.known?number(r.mean_mm)+' mm medi':'dato mancante';
 const title=available?available+'/'+points.length+' ore coperte. Massimo orario medio '+number(peak.mean_mm)+' mm, il '+date(peak.at)+' Roma.':'Nessuna ora coperta integralmente.';
 return '<section class="rain-series"><h5>Quando pioverà · prossime 48 ore</h5><p class="rain-zone-note">Media della zona · mm per ora · previsione, non misura.</p><div class="rain-series-scale">'+number(scale)+' mm / ora</div><div class="rain-series-bars" tabindex="0" role="img" aria-label="'+esc(title)+' I valori sono nella tabella oraria.">'+points.map(r=>'<span class="rain-series-hour '+(r.known?'known':'missing')+'" title="'+esc(date(r.at)+'–'+date(r.until)+' Roma · '+reading(r))+'">'+(r.known?'<i style="height:'+Math.max(1,r.mean_mm/scale*100)+'%"></i>':'')+'</span>').join('')+'</div><div class="rain-series-axis"><span>'+esc(date(points[0].at))+'</span><span>'+esc(date(points.at(-1).until))+' Roma</span></div><p class="rain-zone-note">'+esc(title)+' Tratteggio: dato mancante; barra minima: zero o quantità molto bassa.</p><details><summary>Valori orari e copertura</summary><table><caption>Pioggia media prevista · ora di Roma</caption><thead><tr><th scope="col">Inizio ora</th><th scope="col">mm nell’ora</th></tr></thead><tbody>'+points.map(r=>'<tr><th scope="row">'+esc(date(r.at))+'</th><td>'+esc(reading(r))+'</td></tr>').join('')+'</tbody></table></details></section>';
}
