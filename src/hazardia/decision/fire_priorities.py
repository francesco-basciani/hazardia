"""Explicit authored priority policy. Mapped infrastructure is not qualified availability."""
LEGACY_WEIGHTS=('hospital','school','fire_station','residential','settlement')
WEIGHTS=LEGACY_WEIGHTS+('healthcare','railway','power_line','critical_infrastructure')
DEFAULT_WEIGHTS=dict(hospital=10,school=7,fire_station=7,residential=8,settlement=8,healthcare=9,railway=6,power_line=6,critical_infrastructure=5)
def priority_category(feature):
 p=feature['properties'];t=p.get('osm_tags',{});category=p.get('category')
 if p.get('geometry_quality','SOURCE_GEOMETRY')!='SOURCE_GEOMETRY':return None
 if p.get('source','').startswith('GeoNames'):return None # A locality point is not an additional populated footprint.
 if category in LEGACY_WEIGHTS:return category
 if category in ('clinic','doctors','pharmacy','healthcare','social_facility') or t.get('healthcare'):return 'healthcare'
 if category=='power_line':return 'power_line' # Preserve unknown voltage; never relabel distribution as high voltage.
 if t.get('railway') in ('rail','light_rail','narrow_gauge','tram','station','halt'):return 'railway'
 if t.get('power') in ('substation','plant','generator') or t.get('man_made') in ('water_works','wastewater_plant','water_tower','reservoir_covered') or t.get('bridge')=='yes':return 'critical_infrastructure'
 return None
