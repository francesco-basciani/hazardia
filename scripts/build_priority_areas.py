"""VM geospatial environment: classify a bounded OSM map snapshot, retain real shapes."""
import argparse,json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,Point,mapping
from hazardia.io import utcnow,write_new

def build(raw,bounds,source):
    osm=json.loads(raw);nodes={e['id']:[e['lon'],e['lat']] for e in osm['elements'] if e['type']=='node'};features=[];skipped=[]
    for e in osm['elements']:
        t=e.get('tags',{});amenity=t.get('amenity');kind='hospital' if amenity in ['hospital','nursing_home'] else 'school' if amenity in ['school','kindergarten','university'] else 'fire_station' if amenity=='fire_station' else 'residential' if t.get('landuse')=='residential' else 'settlement' if t.get('place') in ['city','town','village','hamlet','suburb'] else None
        if not kind:continue
        geom=None
        if e['type']=='node':geom=Point(nodes[e['id']])
        elif e['type']=='way':
            ids=e.get('nodes',[])
            if len(ids)>3 and ids[0]==ids[-1] and all(n in nodes for n in ids):geom=Polygon([nodes[n] for n in ids])
        if geom is None or not geom.is_valid or geom.is_empty:skipped.append(dict(type=e['type'],id=e['id'],reason='Incomplete/unsupported relation or invalid geometry'));continue
        features.append(dict(type='Feature',id=e['type']+'/'+str(e['id']),geometry=mapping(geom),properties=dict(id=e['type']+'/'+str(e['id']),name=t.get('name',kind+' OSM '+str(e['id'])),category=kind,source='OpenStreetMap',license='ODbL-1.0',geometry_qualification='MAPPED_OSM_GEOMETRY_NOT_OFFICIAL_BOUNDARY',population=None)))
    return dict(type='FeatureCollection',features=features,coverage_bbox_wgs84=bounds,source_url=source,source_sha256=hashlib.sha256(raw).hexdigest(),available_at=utcnow(),source_timestamp=osm.get('osm3s',{}).get('timestamp_osm_base'),attribution='© OpenStreetMap contributors · ODbL 1.0',license_url='https://www.openstreetmap.org/copyright',skipped=skipped,coverage='PARTIAL_MAPPED_FEATURES_ONLY',missing=['Completeness not guaranteed','Population and occupancy unavailable','Relations not reconstructed; missing geometry is not low risk'])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raw',required=True);ap.add_argument('--out',required=True);ap.add_argument('--bounds',nargs=4,type=float,required=True);ap.add_argument('--source',required=True);a=ap.parse_args();p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);v=build(Path(a.raw).read_bytes(),a.bounds,a.source);p.write_text(json.dumps(v,ensure_ascii=False));print(json.dumps(dict(features=len(v['features']),skipped=len(v['skipped']),categories={k:sum(f['properties']['category']==k for f in v['features']) for k in ['hospital','school','fire_station','residential','settlement']})))
