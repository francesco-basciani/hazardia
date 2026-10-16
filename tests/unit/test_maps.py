import math,tempfile,unittest
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from hazardia.web.maps import Orthophotos
from hazardia.io import HazardError

class MapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.calls=[]
        def fetch(url):self.calls.append(url);return b'\xff\xd8'+b'x'*400
        self.maps=Orthophotos(Path(self.tmp.name),fetch=fetch);self.z=18;self.x=int((13.3995+180)/360*2**18);self.y=int((1-math.asinh(math.tan(math.radians(42.3498)))/math.pi)/2*2**18)
    def test_fixed_provider_bbox_and_reuse(self):
        self.assertEqual(self.maps.tile(self.z,self.x,self.y),self.maps.tile(self.z,self.x,self.y));self.assertEqual(len(self.calls),1)
        u=urlsplit(self.calls[0]);q=parse_qs(u.query);self.assertEqual(u.hostname,'geocatalogo.regione.abruzzo.it');self.assertEqual(q['crs'],['EPSG:3857']);self.assertEqual(q['width'],['256']);self.assertEqual(len(q['bbox'][0].split(',')),4)
    def test_reject_outside_or_malformed_no_network(self):
        for args in [(2,1,1),(20,1,1),(18,-1,0),(18,0,0),(True,1,1),(18,2**18,0)]:
            with self.assertRaises(HazardError):self.maps.tile(*args)
        self.assertFalse(self.calls)
    def test_lru_memory_and_persistent_download_budget(self):
        self.maps.memory_limit=500;self.maps.tile(self.z,self.x,self.y);self.maps.tile(self.z,self.x+1,self.y);self.assertLessEqual(self.maps.status()['cache_bytes'],500);self.assertEqual(self.maps.status()['tiles'],1)
        restarted=Orthophotos(Path(self.tmp.name));self.assertEqual(restarted.downloaded,804)
        self.maps.download_limit=804
        with self.assertRaises(HazardError):self.maps.tile(self.z,self.x+2,self.y)
        self.assertEqual(len(self.calls),2)
    def test_invalid_payload_does_not_enter_cache(self):
        self.maps.fetch=lambda _:b'<xml>error</xml>'
        with self.assertRaises(OSError):self.maps.tile(self.z,self.x,self.y)
        self.assertEqual(self.maps.status()['cache_bytes'],0);self.assertEqual(self.maps.status()['errors'],1)
    def test_network_failure_releases_slots(self):
        def fail(_):raise OSError('offline')
        self.maps.fetch=fail
        for _ in range(5):
            with self.assertRaises(OSError):self.maps.tile(self.z,self.x,self.y)
        self.assertEqual(self.maps.status()['errors'],5)
