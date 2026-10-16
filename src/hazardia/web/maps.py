"""Bounded consultation proxy for the fixed public Abruzzo WMS (no bulk archive).

The visual background carries no physical-model resolution/accuracy claim.
"""
import collections,json,math,threading,urllib.parse,urllib.request
from pathlib import Path
from hazardia.io import HazardError

class Orthophotos:
    endpoint='https://geocatalogo.regione.abruzzo.it/erdas-iws/ogc/wms/'
    layer='Mosaici_UTM-WGS84_2018_2019_Regione_Abruzzo.ecw'
    memory_limit=16*1024**2
    download_limit=256*1024**2
    tile_limit=1024**2
    traffic_name="map-traffic.json"
    extent=(12.9714,41.6607,14.7922,42.9053)
    max_zoom=19
    def __init__(self,state,fetch=None):
        self.state=Path(state)/self.traffic_name;self.lock=threading.Lock();self.slots=threading.BoundedSemaphore(4);self.admission=threading.BoundedSemaphore(16);self.cache=collections.OrderedDict();self.size=0;self.downloaded=0;self.requests=0;self.errors=0;self.fetch=fetch or self._fetch
        if self.state.exists():self.downloaded=json.loads(self.state.read_text())['downloaded_bytes']
    @classmethod
    def bounds(cls,z,x,y):
        if any(type(v) is not int for v in [z,x,y]) or not 8<=z<=cls.max_zoom or not 0<=x<2**z or not 0<=y<2**z:raise HazardError('INVALID_INPUT','Invalid map tile')
        n=2**z;west=x/n*360-180;east=(x+1)/n*360-180
        north=math.degrees(math.atan(math.sinh(math.pi*(1-2*y/n))));south=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y+1)/n))))
        if east<cls.extent[0] or west>cls.extent[2] or north<cls.extent[1] or south>cls.extent[3]:raise HazardError('INVALID_INPUT','Outside Abruzzo imagery extent')
        half=20037508.342789244;span=2*half/n
        return [x*span-half,half-(y+1)*span,(x+1)*span-half,half-y*span]
    def _fetch(self,url):
        req=urllib.request.Request(url,headers={'User-Agent':'HAZARDIA-local-research/0.1 (Abruzzo map consultation)'})
        with urllib.request.urlopen(req,timeout=8) as response:
            raw=response.read(self.tile_limit+1)
            if response.headers.get_content_type()!='image/jpeg' or not raw.startswith(b'\xff\xd8') or len(raw)>self.tile_limit:raise OSError('Invalid/oversize WMS image')
            return raw
    def url(self,z,x,y,bbox):
        params=dict(service='WMS',version='1.3.0',request='GetMap',layers=self.layer,styles='',crs='EPSG:3857',bbox=','.join(map(str,bbox)),width=256,height=256,format='image/jpeg')
        return self.endpoint+'?'+urllib.parse.urlencode(params)
    def tile(self,z,x,y):
        bbox=self.bounds(z,x,y);key=(z,x,y)
        with self.lock:
            if key in self.cache:self.cache.move_to_end(key);return self.cache[key]
        if not self.admission.acquire(False):raise HazardError('QUEUE_FULL','Map queue full; retry or select offline Sentinel')
        acquired=False
        try:
            acquired=self.slots.acquire(timeout=10)
            if not acquired:raise OSError('Map provider busy')
            with self.lock:
                if key in self.cache:self.cache.move_to_end(key);return self.cache[key]
                # Reserve maximum payload for all four in-flight fetches.
                if self.downloaded+4*self.tile_limit>self.download_limit:raise HazardError('DOWNLOAD_LIMIT','Map consultation budget reached; select offline Sentinel')
            raw=self.fetch(self.url(z,x,y,bbox))
            if not raw.startswith(b'\xff\xd8') or len(raw)>self.tile_limit:raise OSError('Invalid image')
            with self.lock:
                self.downloaded+=len(raw);self.requests+=1
                temp=self.state.with_suffix('.tmp');temp.write_text(json.dumps(dict(downloaded_bytes=self.downloaded)));temp.replace(self.state)
                if key not in self.cache:self.cache[key]=raw;self.size+=len(raw)
                while self.size>self.memory_limit:self.size-=len(self.cache.popitem(last=False)[1])
            return raw
        except Exception:
            with self.lock:self.errors+=1
            raise
        finally:
            if acquired:self.slots.release()
            self.admission.release()
    def status(self):
        with self.lock:return dict(source='Regione Abruzzo · ortofoto 2018–2019 · 20 cm/px dichiarati',downloaded_bytes=self.downloaded,download_limit_bytes=self.download_limit,cache_bytes=self.size,cache_limit_bytes=self.memory_limit,tiles=len(self.cache),upstream_requests=self.requests,errors=self.errors,mode='Live consultation; bounded RAM cache, no persistent imagery archive')


class RegionalSatellite(Orthophotos):
    """EOX Sentinel-2 cloudless2024, optional free noncommercial consultation.
    Separate bounded RAM cache/traffic; no offline redistribution archive.
    """
    memory_limit=8*1024**2
    download_limit=16*1024**2
    tile_limit=512*1024
    traffic_name='regional-satellite-traffic.json'
    extent=(10.,40.5,18.,44.)
    max_zoom=11
    def url(self,z,x,y,bbox):
        if z>11:raise HazardError('INVALID_INPUT','Regional background only at zoom8–11')
        return f'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2024_3857/default/g/{z}/{y}/{x}.jpg'
    def status(self):
        r=super().status();r.update(source='Sentinel-2 cloudless2024 by EOX; Contains modified Copernicus Sentinel data2024',license='CC-BY-NC-SA-4.0',license_url='https://www.eox.at/2025/03/sentinel-2-cloudless-2024/');return r
