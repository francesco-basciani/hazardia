import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
from email.message import Message
from hazardia.web.osm_tiles import OSMTiles
from hazardia.io import HazardError
class Response:
 def __init__(self,raw=b'\x89PNG\r\n\x1a\nfixture'):
  self.raw=raw;self.headers=Message();self.headers['Content-Type']='image/png';self.headers['ETag']='fixture'
 def read(self,n):return self.raw[:n]
 def __enter__(self):return self
 def __exit__(self,*args):pass
class TileTests(unittest.TestCase):
 def test_cache_identified_request_and_no_second_fetch(self):
  with tempfile.TemporaryDirectory() as d:
   service=OSMTiles(d)
   with patch('urllib.request.urlopen',return_value=Response()) as request:
    service.cache.opener=request
    first=service.tile(8,137,94,'http://127.0.0.1:8080/');self.assertEqual(first,service.tile(8,137,94,'http://127.0.0.1:8080/'));self.assertEqual(request.call_count,1);headers=dict(request.call_args.args[0].header_items());self.assertIn('HAZARDIA',headers['User-agent']);self.assertEqual(headers['Referer'],'http://127.0.0.1:8080/');self.assertNotIn('Cache-control',headers)
   self.assertGreater(json.loads(next((Path(d)/'osm-tiles').glob('8-*.json')).read_text())['expires'],0)
 def test_invalid_coordinates_no_network(self):
  with tempfile.TemporaryDirectory() as d:
   with patch('urllib.request.urlopen') as request:
    for coords in [(1,0,0),(20,0,0),(8,256,0),(8,-1,0)]:
     with self.assertRaises(HazardError):OSMTiles(d).tile(*coords,'http://localhost/')
    request.assert_not_called()
 def test_non_image_not_cached(self):
  with tempfile.TemporaryDirectory() as d:
   with patch('urllib.request.urlopen',return_value=Response(b'<html>no</html>')):
    with self.assertRaises(OSError):OSMTiles(d).tile(8,137,94,'http://localhost/')
   self.assertFalse(list((Path(d)/'osm-tiles').glob('*.tile')))
 def test_budget_is_explicit(self):
  with tempfile.TemporaryDirectory() as d:
   service=OSMTiles(d);service.cache.day_limit=1
   with patch('urllib.request.urlopen') as request:
    with self.assertRaises(HazardError):service.tile(8,137,94,'http://localhost/')
    request.assert_not_called()
