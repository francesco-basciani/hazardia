/* Display policy only: never changes acquisition, exposure or model inputs. */
export const layerMinZoom=Object.freeze({buildings:15});
export const displayMinZoom=category=>layerMinZoom[category]??2;
export const layerVisible=(category,zoom,monitor=true)=>!monitor||zoom>=(layerMinZoom[category]??0);
export const menuGroups=Object.freeze([
 ['forecast','Previsioni e criticità'],['observations','Osservazioni'],
 ['places','Abitati e servizi'],['territory','Reti, trasporti e ambiente'],['cartography','Catalogo territoriale']
]);
export function menuGroup(category,name){
 if(['wii','fire','avalanche'].includes(category))return 'forecast';
 if(['thermal','perimeters','hydrometers'].includes(category))return 'observations';
 if(category==='tcip')return 'observations';
 if(['boundaries','other'].includes(category)||['Confini','Catalogo territoriale'].includes(name))return 'cartography';
 if(['healthcare','emergency','education','buildings'].includes(category)||name==='Centri abitati')return 'places';
 if(category||name==='Cavi aerei e tralicci')return 'territory';
 if(['Meteo e osservazioni','Criticità territoriali','Pericolosità incendio · EFFIS'].includes(name))return 'forecast';
 return 'observations';
}
