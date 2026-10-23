import tempfile,unittest
from hazardia.web.maps import RegionalSatellite
from hazardia.io import HazardError
class RegionalSatelliteTests(unittest.TestCase):
    def test_optional_fixed_source_cache_and_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            def fetch(url):calls.append(url);return b'\xff\xd8bounded-test'
            s=RegionalSatellite(tmp,fetch=fetch);a=s.tile(8,137,94);self.assertEqual(s.tile(8,137,94),a);self.assertEqual(len(calls),1);self.assertEqual(calls[0],'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2024_3857/default/g/8/94/137.jpg');self.assertEqual(s.status()['license'],'CC-BY-NC-SA-4.0');self.assertEqual(s.status()['download_limit_bytes'],64*1024**2)
    def test_global_coverage_with_bounded_zoom_and_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=RegionalSatellite(tmp,fetch=lambda url:b'\xff\xd8bounded-test')
            self.assertTrue(s.tile(2,0,0).startswith(b'\xff\xd8'))
            self.assertTrue(s.tile(8,0,0).startswith(b'\xff\xd8'))
            self.assertTrue(s.tile(14,8192,8192).startswith(b'\xff\xd8'))
            for args in [(-1,0,0),(15,0,0),(8,-1,0),(8,256,0),(8,'137',94)]:
                with self.assertRaises(HazardError):s.tile(*args)
            with self.assertRaises(HazardError):s.url(15,1,1,[])
