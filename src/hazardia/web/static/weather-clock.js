/* Conservative display/job-builder gate: a paused VM can retain a stale wall clock. */
export function checkedForecastTime(snapshot,ttl,now=Date.now()){
 const f=snapshot.forecast;if(!f)return snapshot;
 const age=(now-Date.parse(f.available_at))/1000;
 const skew=!Number.isFinite(snapshot.age_s)||Math.abs(age-snapshot.age_s)>120;
 if(snapshot.status==='FRESH'&&(skew||age< -120||age>=ttl))return {...snapshot,status:'STALE',clock_warning:skew?'Orari browser/VM incoerenti: verifica la sincronizzazione; dati da riconfermare.':'Cache scaduta secondo l’orologio del browser.'};
 return snapshot;
}
