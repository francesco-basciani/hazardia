import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const {featureSymbol,featureStyle}=await import('data:text/javascript;base64,'+Buffer.from(readFileSync('src/hazardia/web/static/map-symbols.js','utf8')).toString('base64'));
const feature=(category,group,type='Point')=>({properties:{category,catalog_group:group},geometry:{type}});let checks=0;const check=x=>{assert.ok(x);checks++;};
const wire=feature('power_line','electrical','LineString'),tower=feature('power_tower','electrical');
check(featureSymbol(wire).label==='Linea elettrica aerea OSM');check(featureStyle(wire).dashArray==='8 5');check(featureStyle(wire).color===featureSymbol(wire).color);check(featureStyle(tower).radius<featureStyle(feature('school','education')).radius);
const colours=['settlements','healthcare','emergency','education','transport','utilities','buildings','environment'].map((g,i)=>featureSymbol(feature(['settlement','hospital','fire_station','school','transport','utility','building','environment'][i],g)).color);check(new Set(colours).size===colours.length);
for(const type of ['Point','Polygon','LineString']){const f=feature('school','education',type);check(featureSymbol(f).kind===({Point:'point',Polygon:'area',LineString:'line'})[type]);check(featureStyle(f).fillColor===featureSymbol(f).fill);}
const built=feature('settlement','settlements','Polygon');built.properties.source='ESA WorldCover2021';check(featureSymbol(built).label.includes('satellite'));check(featureSymbol(built).note.includes('non è un confine urbano'));
const settlement=feature('settlement','settlements');check(featureSymbol(settlement).note.includes('non è il confine'));
const rail=feature('transport','transport','LineString');rail.properties.osm_tags={railway:'rail'};check(featureSymbol(rail).label==='Ferrovia OSM');check(!!featureStyle(rail).dashArray);
const exposed=feature('school','education');exposed.exposure={status:'MODELLED',timeline_contact:[0,.25,.75]};check(featureSymbol(exposed,0).fill===featureSymbol(exposed,0).color);check(featureStyle(exposed,.25).fillColor==='#ffb64c');check(featureStyle(exposed,.5).fillColor==='#f04b3a');check(featureSymbol(exposed,.5).note.includes('non rischio per persone'));check(featureSymbol(exposed,.25).label.includes('>0–50%'));
exposed.exposure.status='UNAVAILABLE';check(featureStyle(exposed,.5).fillColor===featureSymbol(exposed).color);
const hydrant=feature('emergency_service','emergency');hydrant.properties.osm_tags={emergency:'fire_hydrant'};check(featureSymbol(hydrant).label==='Idrante antincendio');check(featureSymbol(hydrant).note.includes('Non indica una squadra'));const dae=feature('emergency_service','emergency');dae.properties.osm_tags={emergency:'defibrillator'};check(featureSymbol(dae).key!==featureSymbol(hydrant).key);
console.log(JSON.stringify({status:'PASS',checks,scope:'symbol meaning, actual style/legend identity, category separation, geometry and simulated contact semantics'}));
