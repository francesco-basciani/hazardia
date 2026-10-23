"""Fixed free place search; bounded, explicit requests only (no autocomplete)."""
import json,threading,time,urllib.parse,urllib.request
from pathlib import Path
from hazardia.io import HazardError
from hazardia.web.tile_cache import UA
class Geocoder:
    def __init__(self,state):self.path=Path(state)/'place-search.json';self.lock=threading.Lock();self.last=0
    def search(self,q):
        if not isinstance(q,str) or not 2<=len(q.strip())<=120:raise HazardError('INVALID_INPUT','Place query must have 2–120 characters')
        q=q.strip();key=q.casefold();now=time.time()
        with self.lock:
            cache=json.loads(self.path.read_text()) if self.path.exists() else {}
            if key in cache and now-cache[key]['at']<86400:return cache[key]['result']
            if now-self.last<1:raise HazardError('SOURCE_BUSY','Wait one second between place searches')
            self.last=now
            url='https://geocoding-api.open-meteo.com/v1/search?'+urllib.parse.urlencode(dict(name=q,count=5,language='it',format='json'))
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=8) as r:
                raw=r.read(65537)
                if len(raw)>65536:raise OSError('Place response too large')
            data=json.loads(raw);places=[]
            for p in data.get('results',[])[:5]:
                lat,lon=p.get('latitude'),p.get('longitude')
                if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)) or not -85<=lat<=85 or not -180<=lon<=180:continue
                places.append(dict(name=p.get('name',''),region=p.get('admin1',''),country=p.get('country',''),latitude=lat,longitude=lon))
            result=dict(places=places,source='Open-Meteo Geocoding / GeoNames',license='CC BY 4.0',available_at=now)
            cache={k:v for k,v in cache.items() if now-v['at']<86400}
            if len(cache)>=100:cache.pop(min(cache,key=lambda k:cache[k]['at']))
            cache[key]={'at':now,'result':result};tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(cache));tmp.replace(self.path);return result

def terrain_metadata():
    # Experimental read only. Do not hide denial or silently describe flat terrain as relief.
    url='https://terrain.reearth.land/cesium-mesh/ellipsoid/layer.json'
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=10) as r:raw=r.read(262145)
        if len(raw)>262144:raise OSError('Terrain metadata too large')
        data=json.loads(raw)
        return dict(status='METADATA_ONLY',source=url,format=data.get('format'),attribution=data.get('attribution'),detail='Terrain mesh transport not enabled in the production map')
    except Exception as e:return dict(status='UNAVAILABLE',source=url,detail=str(e),fallback='Flat ellipsoid is not terrain')
