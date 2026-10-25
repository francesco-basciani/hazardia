/* Display policy only: never changes acquisition, exposure or model inputs. */
export const layerMinZoom=Object.freeze({buildings:15});
export const layerVisible=(category,zoom,monitor=true)=>!monitor||zoom>=(layerMinZoom[category]??0);
export const menuGroups=Object.freeze([
 ['forecast','Previsioni e criticità'],['observations','Osservazioni'],
 ['territory','Territorio e infrastrutture'],['cartography','Cartografia e catalogo']
]);
export function menuGroup(category,name){
 if(['boundaries','other'].includes(category)||['Confini','Catalogo territoriale'].includes(name))return 'cartography';
 if(category||name==='Centri abitati'||name==='Cavi aerei e tralicci')return 'territory';
 if(['Meteo e osservazioni','Criticità territoriali'].includes(name))return 'forecast';
 return 'observations';
}
