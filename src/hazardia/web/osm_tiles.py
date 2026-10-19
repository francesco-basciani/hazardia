"""Optional OSM Carto consultation: identified requests, 7-day cache, no prefetch."""
import json,time,threading,urllib.request,urllib.error
from pathlib import Path
from hazardia.io import HazardError
class OSMTiles:
 def __init__(self,state):
  self.root=Path(state)/'osm-tiles';self.root.mkdir(exist_ok=True);self.lock=threading.Lock();self.slots=threading.BoundedSemaphore(4);self.admission=threading.BoundedSemaphore(16);self.limit=32*1024**2
 def tile(self,z,x,y,referer):
  if not 4<=z<=19 or not 0<=x<2**z or not 0<=y<2**z:raise HazardError('INVALID_INPUT','Invalid OSM tile')
  if not self.admission.acquire(False):raise HazardError('QUEUE_FULL','OSM consultation busy; retry')
  acquired=False
  try:
   acquired=self.slots.acquire(timeout=10)
   if not acquired:raise HazardError('QUEUE_FULL','OSM consultation busy; retry')
   # Serialize the small optional cache: duplicate views never fetch the same tile twice.
   with self.lock:
    path=self.root/f'{z}-{x}-{y}.png';meta=path.with_suffix('.json');m=json.loads(meta.read_text()) if meta.exists() else {}
    if path.exists() and m.get('expires',0)>time.time():return path.read_bytes()
    traffic=self.root/'traffic.json';downloaded=json.loads(traffic.read_text()).get('bytes',0) if traffic.exists() else 0
    size=sum(p.stat().st_size for p in self.root.glob('*.png'))
    if downloaded+1024**2>self.limit or size+1024**2>self.limit:raise HazardError('DOWNLOAD_LIMIT','OSM consultation cache/budget reached; select satellite')
    headers={'User-Agent':'HAZARDIA-local-research/0.1 (+https://github.com/francesco-basciani/hazardia)','Referer':referer}
    if path.exists() and m.get('etag'):headers['If-None-Match']=m['etag']
    try:
     with urllib.request.urlopen(urllib.request.Request(f'https://tile.openstreetmap.org/{z}/{x}/{y}.png',headers=headers),timeout=8) as response:
      raw=response.read(1024**2+1)
      if len(raw)>1024**2 or not raw.startswith(b'\x89PNG\r\n\x1a\n') or response.headers.get_content_type()!='image/png':raise OSError('Invalid OSM image')
      m=dict(etag=response.headers.get('ETag'));path.write_bytes(raw);traffic.write_text(json.dumps(dict(bytes=downloaded+len(raw))))
    except urllib.error.HTTPError as e:
     if e.code!=304 or not path.exists():raise
     raw=path.read_bytes()
    m['expires']=time.time()+7*86400;meta.write_text(json.dumps(m));return raw
  finally:
   if acquired:self.slots.release()
   self.admission.release()
