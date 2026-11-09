"""Verified read-only OSM archive fallback, never extrapolate coverage or source time."""
import hashlib,json,re,math
import xml.etree.ElementTree as ET
from pathlib import Path

def _pinned_power_snapshot(runtime,requested):
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


def cached_power_snapshot(runtime,requested):
 """Prefer checksummed live consultation archives; never refresh their source time."""
 from hazardia.ingest.archive_storage import read_bytes
 from hazardia.web.observed_layers import power_features
 from hazardia.io import HazardError
 root=Path(runtime);folder=root/'web-state/observed-power';candidates=[]
 for meta in list(folder.glob('*.json'))[:128]:
  if not re.fullmatch(r'[a-f0-9]{24}\.json',meta.name) or meta.stat().st_size>8*1024**2:continue
  try:
   info=json.loads(meta.read_text())
   if not isinstance(info,dict) or not isinstance(info.get('quality'),dict):continue
   cover=info.get('bounds')
   if info.get('status')!='READY' or info.get('quality',{}).get('fallback'):continue
   if not isinstance(cover,list) or len(cover)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in cover):continue
   clip=[max(requested[0],cover[0]),max(requested[1],cover[1]),min(requested[2],cover[2]),min(requested[3],cover[3])]
   if clip[0]>=clip[2] or clip[1]>=clip[3]:continue
   if not isinstance(info.get('source'),str) or not isinstance(info.get('acquired_at'),str):continue
   candidates.append(((clip[2]-clip[0])*(clip[3]-clip[1]),info['acquired_at'],meta,info,clip))
  except (ValueError,OSError,KeyError,TypeError,HazardError):continue
 total=0
 for _,_,meta,info,clip in sorted(candidates,key=lambda x:(x[0],x[1]),reverse=True):
  try:
   raw=read_bytes(meta.with_suffix('.source'),limit=8*1024**2);total+=len(raw)
   if total>32*1024**2:break
   if hashlib.sha256(raw).hexdigest()!=info.get('raw_sha256'):continue
   power_features(raw)  # Reject incomplete/truncated or invalid archived responses.
   break
  except (ValueError,OSError,KeyError,TypeError,HazardError,ET.ParseError):continue
 else:return _pinned_power_snapshot(runtime,requested)
 if total>32*1024**2:return _pinned_power_snapshot(runtime,requested)
 return dict(raw=raw,bounds=clip,source=info['source'],quality=dict(fallback=True,source_mode='VERIFIED_CONSULTATION_CACHE_FALLBACK',source_snapshot_sha256=info['raw_sha256'],source_snapshot_path=str(meta.relative_to(root)),source_snapshot_available_at=info['acquired_at'],source_timestamp=info.get('quality',{}).get('osm_base'),source_bounds=info['bounds'],requested_bounds=requested,complete=False,transformation='Reuse of verified archived OSM response; retained acquisition/source times, no geometry interpolation'))
