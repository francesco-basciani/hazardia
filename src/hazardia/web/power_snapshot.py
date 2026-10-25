"""Read-only fallback to a pinned existing OSM snapshot, never extrapolate coverage."""
import hashlib,json
from pathlib import Path

def cached_power_snapshot(runtime,requested):
 root=Path(runtime);raw=root/'runs/map-detail-20261015T204352Z/osm-map-final-raw.json';meta=root/'web-assets/priority-areas.json'
 if not raw.exists() or not meta.exists() or raw.stat().st_size>16*1024**2:return None
 info=json.loads(meta.read_text());source=raw.read_bytes();digest=hashlib.sha256(source).hexdigest()
 if digest!=info.get('source_sha256'):return None
 cover=info.get('coverage_bbox_wgs84');
 if not isinstance(cover,list) or len(cover)!=4:return None
 clip=[max(requested[0],cover[0]),max(requested[1],cover[1]),min(requested[2],cover[2]),min(requested[3],cover[3])]
 if clip[0]>=clip[2] or clip[1]>=clip[3]:return None
 data=json.loads(source);elements=[e for e in data.get('elements',[]) if e.get('tags',{}).get('power') in ('line','minor_line','cable','tower','pole','substation')]
 refs={n for e in elements if e.get('type')=='way' and not e.get('geometry') for n in e.get('nodes',[])}
 included={e.get('id') for e in elements if e.get('type')=='node'}
 elements.extend(e for e in data.get('elements',[]) if e.get('type')=='node' and e.get('id') in refs and e.get('id') not in included)
 if len(elements)>=5001:return None
 # Same native geometry/tags; filtering is recorded, not a new observation.
 derived=json.dumps(dict(elements=elements,osm3s=data.get('osm3s',{})),allow_nan=False).encode()
 return dict(raw=derived,bounds=clip,source=info.get('source_url','OpenStreetMap verified local snapshot'),quality=dict(fallback=True,source_mode='VERIFIED_LOCAL_OSM_SNAPSHOT_FALLBACK',source_snapshot_sha256=digest,source_snapshot_path=str(raw.relative_to(root)),source_snapshot_available_at=info.get('available_at'),source_timestamp=info.get('source_timestamp'),source_bounds=cover,requested_bounds=requested,complete=False,transformation='Power-tag filtering of existing pinned OSM snapshot; no geometry interpolation or new observation'))
