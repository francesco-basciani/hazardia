"""VM-only conversion of bounded OSM snapshots, retain source/ODbL provenance."""
import argparse,hashlib,json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',required=True);parser.add_argument('--run',required=True);a=parser.parse_args();root=Path(a.runtime);run=Path(a.run)
    source=run/'osm-context-raw.json';raw=source.read_bytes();osm=json.loads(raw);assert not osm.get('remark');features=[]
    for el in osm['elements']:
        tags=el.get('tags',{});name=tags.get('name')
        if not name:continue
        road=el['type']=='way' and 'highway' in tags
        geom=[[p['lon'],p['lat']] for p in el.get('geometry',[]) if 'lon' in p]
        if road and len(geom)<2:continue
        if not road and ('lon' not in el or 'lat' not in el):continue
        lon,lat=geom[len(geom)//2] if road else [el['lon'],el['lat']]
        features.append(dict(provider='OpenStreetMap',id=el['id'],osm_type=el['type'],name=name,kind='road' if road else 'place' if 'place' in tags else 'poi',type=tags.get('place',tags.get('highway',tags.get('amenity','punto di interesse'))),lat=lat,lon=lon,geometry=geom if road else None,address=', '.join(tags[k] for k in ['addr:street','addr:housenumber','addr:postcode','addr:city'] if k in tags)))
    osm_names={f['name'].casefold() for f in features if f['kind']=='place'}
    for place in json.loads((run/'geonames-places.json').read_text()):
        if place['admin1']!='01' or place['name'].casefold() in osm_names:continue
        features.append(dict(provider='GeoNames',id=place['id'],osm_type=None,name=place['name'],kind='place',type='capoluogo amministrativo' if place['type'] in ['PPLA','PPLA2'] else 'centro abitato',lat=place['lat'],lon=place['lon'],geometry=None,address='',modified=place['modified']))
    # Deterministic priority: place labels, major roads, then other named ways.
    rank={'city':0,'capoluogo amministrativo':1,'town':1,'suburb':2,'village':3,'motorway':4,'trunk':5,'primary':6,'secondary':7,'tertiary':8}
    features.sort(key=lambda f:(rank.get(f['type'],20),f['name'],f['id']))
    result=dict(schema='hazardia-map-context/1',timestamp=osm['osm3s']['timestamp_osm_base'],source=(run/'overpass-source.txt').read_text(),source_sha256=hashlib.sha256(raw).hexdigest(),license='ODbL 1.0',attribution='© OpenStreetMap contributors',places_bbox=[12.90,41.60,14.86,42.97],roads_bbox=[13.375,42.345,13.405,42.36],features=features)
    result['geonames']=dict(source='https://download.geonames.org/export/dump/IT.zip',license='CC BY 4.0',sha256=hashlib.sha256((run/'geonames-IT.zip').read_bytes()).hexdigest(),filter='featureclass P/admin1 01 (Abruzzo)',qualification='Locations are gazetteer points, not administrative boundaries; updated-at differs by record')
    result['timestamp_meaning']=osm['osm3s'].get('timestamp_meaning','OSM database snapshot time')
    encoded=json.dumps(result,ensure_ascii=False,separators=(',',':')).encode();snapshot=run/('map-context-'+hashlib.sha256(encoded).hexdigest()+'.json')
    if snapshot.exists():assert snapshot.read_bytes()==encoded
    else:snapshot.write_bytes(encoded)
    dest=root/'web-assets/map-context.json';temp=dest.with_suffix('.tmp');temp.write_bytes(encoded);temp.replace(dest)
    print(json.dumps(dict(features=len(features),places=sum(f['kind']=='place' for f in features),roads=sum(f['kind']=='road' for f in features),pois=sum(f['kind']=='poi' for f in features),bytes=len(encoded),sha256=hashlib.sha256(encoded).hexdigest(),timestamp=result['timestamp'])))
if __name__=='__main__':main()
