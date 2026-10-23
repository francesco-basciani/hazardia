import concurrent.futures,json,tempfile,threading,time,unittest
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from hazardia.web.tile_cache import ConsultationCache
from hazardia.web.consultation_maps import OSMTiles,CachedImagery
from hazardia.web.maps import RegionalSatellite
from hazardia.io import HazardError
class Response:
    def __init__(self,raw=b'\x89PNG\r\n\x1a\nfixture',cache='max-age=604800'):
        self.raw=raw;self.headers=Message();self.headers['Content-Type']='image/png';self.headers['Cache-Control']=cache;self.headers['ETag']='fixture'
    def read(self,n):return self.raw[:n]
    def __enter__(self):return self
    def __exit__(self,*a):pass
class Tests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.now=100000.;self.calls=0
    def cache(self,opener=None):
        def fetch(*a,**k):self.calls+=1;return Response()
        return ConsultationCache(self.temp.name,opener=opener or fetch,clock=lambda:self.now)
    def get(self,c,key='8-137-94'):return c.get(key,'https://tile.openstreetmap.org/8/137/94.png',b'\x89PNG','image/png')
    def test_persistent_cache_survives_restart(self):
        c=self.cache();raw=self.get(c);other=self.cache();self.assertEqual(raw,self.get(other));self.assertEqual(self.calls,1);self.assertEqual(other.status()['cache_hits'],1)
    def test_rolling_limit_recovers_without_resetting_total(self):
        c=self.cache();self.get(c);total=c.traffic['total_bytes'];c.hour_limit=1
        with self.assertRaises(HazardError):self.get(c,'8-138-94')
        self.now+=3601;c.hour_limit=c.tile_limit;self.get(c,'8-138-94');self.assertEqual(c.traffic['total_bytes'],2*total)
    def test_singleflight_and_independent_concurrency(self):
        lock=threading.Lock();active=0;peak=0;calls=[]
        def fetch(req,**kwargs):
            nonlocal active,peak
            with lock:active+=1;peak=max(peak,active);calls.append(req.full_url)
            time.sleep(.04)
            with lock:active-=1
            return Response()
        c=self.cache(fetch)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(lambda key:self.get(c,key),['a']*4+['b','c','d','e']))
        self.assertEqual(len(calls),5);self.assertGreaterEqual(peak,2);self.assertLessEqual(peak,4)
    def test_invalid_payload_not_cached(self):
        c=self.cache(lambda *a,**k:Response(b'no'))
        with self.assertRaises(OSError):self.get(c)
        self.assertEqual(c.status()['cache_bytes'],0)
    def test_no_store_is_not_persisted(self):
        c=self.cache(lambda *a,**k:Response(cache='no-store'));self.get(c);self.assertFalse(list(Path(self.temp.name).glob('*.tile')))
    def test_full_disk_does_not_evict_fresh_tiles(self):
        c=self.cache();self.get(c);c.disk_limit=1
        self.assertTrue(self.get(c))
        with self.assertRaises(HazardError):self.get(c,'new')
    def test_old_satellite_counter_retained(self):
        Path(self.temp.name,'regional-satellite-traffic.json').write_text(json.dumps({'downloaded_bytes':65017285}))
        service=CachedImagery(self.temp.name,RegionalSatellite);self.assertEqual(service.status()['legacy_downloaded_bytes'],65017285);self.assertTrue(service.status()['can_download_tiles'])
    def test_identified_osm_and_cache_migration(self):
        root=Path(self.temp.name)/'osm-tiles';root.mkdir();raw=Response().raw;(root/'8-137-94.png').write_bytes(raw);(root/'8-137-94.json').write_text(json.dumps({'expires':time.time()+1000,'etag':'fixture'}))
        c=OSMTiles(self.temp.name)
        with patch('urllib.request.urlopen') as fetch:self.assertEqual(c.tile(8,137,94,'http://localhost/'),raw);fetch.assert_not_called()
        self.assertGreater(c.status()['cache_bytes'],0)
