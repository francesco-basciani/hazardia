"""Lossless tagged-object catalogue within a bounded OSM snapshot.
Raw source remains authoritative; incomplete relations have explicit point proxies.
"""
import math
CATALOG_VERSION='osm-catalog/2'
EXPOSURE_CATEGORIES={'settlement','residential','hospital','school','fire_station','clinic','doctors','pharmacy','healthcare','social_facility','emergency_service'}

def classify(t):
    amenity=t.get('amenity');power=t.get('power')
    if power in ('line','minor_line','cable') and t.get('location') not in ('underground','underwater') and (power!='cable' or t.get('location')=='overhead'):return 'power_line','electrical'
    if power in ('tower','pole'):return 'power_tower','electrical'
    if t.get('healthcare') or amenity in ('hospital','clinic','doctors','dentist','pharmacy','blood_donation'):
        return (amenity if amenity in ('hospital','clinic','doctors','pharmacy') else 'hospital' if t.get('healthcare')=='hospital' else 'healthcare'),'healthcare'
    if amenity=='social_facility' or t.get('social_facility'):return 'social_facility','healthcare'
    if amenity=='fire_station':return 'fire_station','emergency'
    if amenity=='police' or t.get('emergency') or t.get('rescue'):return 'emergency_service','emergency'
    if t.get('place') in ('city','town','village','hamlet','suburb','neighbourhood'):return 'settlement','settlements'
    if t.get('landuse')=='residential':return 'residential','settlements'
    if amenity in ('school','kindergarten','university','college'):return 'school','education'
    if t.get('boundary') or t.get('admin_level'):return 'boundary','boundaries'
    if t.get('highway') or t.get('railway') or t.get('aeroway') or t.get('public_transport') or t.get('route') or amenity in ('bus_station','ferry_terminal','parking'):return 'transport','transport'
    if power or t.get('man_made') in ('pipeline','water_tower','water_works','wastewater_plant','reservoir_covered','communications_tower') or t.get('telecom') or t.get('pipeline'):return 'utility','utilities'
    if t.get('building') or t.get('building:part'):return 'building','buildings'
    if t.get('natural') or t.get('waterway') or t.get('water') or t.get('landuse') or t.get('leisure'):return 'environment','environment'
    return 'other','other'

def _coords(points):
    if not isinstance(points,list) or len(points)>20000:return None
    result=[]
    for p in points:
        if not isinstance(p,dict):return None
        x,y=p.get('lon'),p.get('lat')
        if type(x) not in (int,float) or type(y) not in (int,float) or not math.isfinite(x+y) or not -180<=x<=180 or not -90<=y<=90:return None
        result.append([x,y])
    return result

def parse_osm(raw):
    elements=raw.get('elements',[]); nodes={e['id']:e for e in elements if e.get('type')=='node' and 'lat' in e};ways={e['id']:e for e in elements if e.get('type')=='way'};features=[];skipped=0
    def line(e):
        if e.get('geometry') is not None:return _coords(e['geometry'])
        ids=e.get('nodes',[])
        if ids and all(n in nodes for n in ids):return _coords([nodes[n] for n in ids])
        return None
    def rings(parts):
        pending=[p[:] for p in parts];result=[]
        while pending:
            ring=pending.pop(0)
            while ring[0]!=ring[-1]:
                match=next(((i,False) if p[0]==ring[-1] else (i,True) for i,p in enumerate(pending) if p[0]==ring[-1] or p[-1]==ring[-1]),None)
                if match is None:return None
                i,reverse=match;p=pending.pop(i);ring+=(p[::-1] if reverse else p)[1:]
            if len(ring)<4:return None
            result.append(ring)
        return result
    for e in elements:
        t=e.get('tags',{})
        if not t:continue
        category,group=classify(t);geometry=None;quality='SOURCE_GEOMETRY';g=line(e) if e.get('type')=='way' else None
        if e.get('type')=='node':
            c=_coords([e]);geometry=dict(type='Point',coordinates=c[0]) if c else None
        elif g and len(g)>=2:
            area=t.get('area')=='yes' or category in ('residential','hospital','school','clinic','pharmacy','healthcare','social_facility','fire_station','building','environment') and not (t.get('waterway') or t.get('natural') in ('coastline','cliff','ridge'))
            geometry=dict(type='Polygon',coordinates=[g]) if len(g)>=4 and g[0]==g[-1] and area and t.get('area')!='no' else dict(type='LineString',coordinates=g)
        elif e.get('type')=='relation' and t.get('type') in ('multipolygon','boundary'):
            outer=[];inner=[];complete=True
            for member in e.get('members',[]):
                if member.get('type')!='way' or member.get('role','') not in ('','outer','inner'):continue
                p=_coords(member['geometry']) if member.get('geometry') else line(ways.get(member.get('ref'),{}))
                if not p or len(p)<2:complete=False;break
                (inner if member.get('role')=='inner' else outer).append(p)
            outers=rings(outer) if complete else None;inners=rings(inner) if complete else None
            if outers and inners is not None:
                try:
                    from shapely.geometry import Polygon,MultiPolygon,mapping
                    shells=[Polygon(r) for r in outers];holes=[[] for _ in shells]
                    for r in inners:
                        h=Polygon(r);i=next(i for i,s in enumerate(shells) if s.covers(h));holes[i].append(r)
                    poly=MultiPolygon([Polygon(r,holes[i]) for i,r in enumerate(outers)])
                    if poly.is_valid:geometry=dict(mapping(poly))
                except (ImportError,ValueError,StopIteration):pass
        if not geometry:
            c=e.get('center',{});coords=_coords([c])
            if coords:geometry=dict(type='Point',coordinates=coords[0]);quality='CENTER_PROXY_GEOMETRY_MISSING'
        if not geometry:skipped+=1;continue
        props=dict(name=t.get('name') or t.get('ref') or category+' OSM',category=category,catalog_group=group,source='OpenStreetMap',osm_type=e['type'],osm_id=e['id'],osm_tags=dict(t),geometry_quality=quality,optimization_eligible=category in ('settlement','residential','hospital','school','fire_station') and quality=='SOURCE_GEOMETRY',exposure_eligible=category in EXPOSURE_CATEGORIES and quality=='SOURCE_GEOMETRY',osm_version=e.get('version'),osm_timestamp=e.get('timestamp'))
        for k in ('voltage','height','operator','ref','location','power','cables','wires'):props[k]=t.get(k)
        features.append(dict(type='Feature',id=f'osm-{e["type"]}-{e["id"]}',geometry=geometry,properties=props))
    return features,skipped

def summary(features):
    from collections import Counter
    return dict(version=CATALOG_VERSION,groups=dict(Counter(f['properties'].get('catalog_group','settlements') for f in features)),geometry_proxies=sum(f['properties'].get('geometry_quality')=='CENTER_PROXY_GEOMETRY_MISSING' for f in features),scope='All tagged objects representable in this bounded extract; not a complete territorial census')
