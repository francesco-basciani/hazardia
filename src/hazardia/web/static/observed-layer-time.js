/* Display only: original UTC timestamps and source windows remain immutable. */
export function formatObservedDate(value,language='it-IT'){
 if(typeof value!=='string'||!value.trim()||!Number.isFinite(Date.parse(value)))return '—';
 return new Intl.DateTimeFormat(language,{timeZone:'Europe/Rome',day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23',timeZoneName:'short'}).format(new Date(value));
}
