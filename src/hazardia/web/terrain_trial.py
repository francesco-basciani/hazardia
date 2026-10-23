"""Lazy experimental quantized-mesh transport, through the VM only."""
import gzip,json,urllib.request
from hazardia.web.tile_cache import ConsultationCache,UA
from hazardia.io import HazardError
BASE='https://terrain.reearth.land/cesium-mesh/ellipsoid/'
class TerrainTrial:
    def __init__(self,state):self.cache=ConsultationCache(state/'terrain-trial',disk_limit=8*1024**2,memory_limit=2*1024**2,ttl=86400);self.metadata=None
    def layer(self):
        if self.metadata is None:
            with urllib.request.urlopen(urllib.request.Request(BASE+'layer.json',headers={'User-Agent':UA}),timeout=10) as r:raw=r.read(262145)
            if len(raw)>262144:raise OSError('Terrain metadata too large')
            source=json.loads(raw)
            if source.get('format')!='quantized-mesh-1.0':raise OSError('Unexpected terrain format')
            # Never expose upstream URIs that would bypass the VM acquisition boundary.
            self.metadata={k:v for k,v in source.items() if k not in ['tiles','parentUrl']};self.metadata['tiles']=['{z}/{x}/{y}.terrain'];self.metadata['attribution']='Re:Earth Terrain · Mapterhorn (CC BY 4.0) · NGA EGM2008 public domain';self.metadata['maxzoom']=min(source.get('maxzoom',14),14)
        return self.metadata
    def tile(self,z,x,y):
        if not 0<=z<=14 or not 0<=x<2**(z+1) or not 0<=y<2**z:raise HazardError('INVALID_INPUT','Invalid terrain tile')
        return self.cache.get(f'{z}-{x}-{y}',BASE+f'{z}/{x}/{y}.terrain',b'','application/vnd.quantized-mesh')
