"""Consultation adapters: fixed providers, no arbitrary URL proxy."""
import json
from pathlib import Path
from hazardia.web.maps import Orthophotos,RegionalSatellite
from hazardia.web.tile_cache import ConsultationCache
from hazardia.io import HazardError

class CachedImagery:
    def __init__(self,state,provider):
        self.provider=provider;self.state=Path(state);self.legacy=provider(state);self.cache=ConsultationCache(self.state/('consultation-'+provider.traffic_name.removesuffix('.json')),disk_limit=64*1024**2,memory_limit=provider.memory_limit,ttl=86400,tile_limit=provider.tile_limit)
    def tile(self,z,x,y):
        bbox=self.provider.bounds(z,x,y);url=self.legacy.url(z,x,y,bbox)
        return self.cache.get(f'{z}-{x}-{y}',url,b'\xff\xd8','image/jpeg')
    def status(self):
        old=self.legacy.status();new=self.cache.status();old.pop('download_limit_bytes',None);return {**old,**new,'downloaded_bytes':old['downloaded_bytes']+new['downloaded_bytes'],'new_policy_downloaded_bytes':new['downloaded_bytes'],'legacy_downloaded_bytes':old['downloaded_bytes'],'legacy_limit_bytes':self.provider.download_limit,'policy':'Rolling traffic and bounded consultation cache; old cumulative counter preserved, not reset'}

class OSMTiles:
    def __init__(self,state):
        self.root=Path(state)/'osm-tiles';self.root.mkdir(exist_ok=True);self.cache=ConsultationCache(self.root,disk_limit=64*1024**2,tile_limit=512*1024)
        # Convert the previous bounded PNG cache once; retain every fresh object.
        import hashlib
        for old in self.root.glob('*.png'):
            meta=old.with_suffix('.json');target=old.with_suffix('.tile')
            if meta.exists() and not target.exists():
                raw=old.read_bytes();m=json.loads(meta.read_text());m['sha256']=hashlib.sha256(raw).hexdigest();old.replace(target);self.cache._save(meta,m);self.cache.disk[target.name]=(len(raw),target.stat().st_mtime);self.cache.disk_bytes+=len(raw)
    def tile(self,z,x,y,referer):
        if any(type(v) is not int for v in (z,x,y)) or not 2<=z<=19 or not 0<=x<2**z or not 0<=y<2**z:raise HazardError('INVALID_INPUT','Invalid OSM tile')
        # Lossless migration of previously consulted cache: no new network request.
        key=f'{z}-{x}-{y}';old=self.root/(key+'.png');meta=old.with_suffix('.json')
        with self.cache.lock:
            if old.exists() and meta.exists() and not old.with_suffix('.tile').exists():
                import hashlib
                raw=old.read_bytes();m=json.loads(meta.read_text());m['sha256']=hashlib.sha256(raw).hexdigest();target=old.with_suffix('.tile');old.replace(target);self.cache._save(meta,m);self.cache.disk[target.name]=(len(raw),target.stat().st_mtime);self.cache.disk_bytes+=len(raw)
        return self.cache.get(key,f'https://tile.openstreetmap.org/{z}/{x}/{y}.png',b'\x89PNG\r\n\x1a\n','image/png',referer)
    def status(self):
        data=self.cache.status();legacy=self.root/'traffic.json';old=json.loads(legacy.read_text()).get('bytes',0) if legacy.exists() else 0
        return dict(data,downloaded_bytes=old+data['downloaded_bytes'],legacy_downloaded_bytes=old,new_policy_downloaded_bytes=data['downloaded_bytes'])
