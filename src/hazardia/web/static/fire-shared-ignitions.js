/* Shared authoring input only. Never modifies submitted inputs or calculated outputs. */
export function sharedIgnitions(scenarios,ignitions){
 if(!Array.isArray(ignitions)||ignitions.length>16)throw Error('Massimo 16 inneschi comuni.');
 for(const i of ignitions)if(!Number.isFinite(i.at_minutes)||i.at_minutes<0||scenarios.some(s=>i.at_minutes>=s.input.hours*60))throw Error('L’orario di ogni innesco deve rientrare nella durata di tutti gli scenari.');
 for(const s of scenarios)s.input.ignitions=structuredClone(ignitions);
}
