import json,tempfile,unittest
from unittest.mock import patch
from hazardia.web.map_navigation import Geocoder
from hazardia.io import HazardError
class Response:
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def read(self,n):return json.dumps({'results':[{'name':'Dakar','latitude':14.69,'longitude':-17.44,'country':'Senegal'}]}).encode()
class Tests(unittest.TestCase):
 def test_fixed_origin_cache_and_world_coordinates(self):
  with tempfile.TemporaryDirectory() as d:
   g=Geocoder(d)
   with patch('urllib.request.urlopen',return_value=Response()) as request:
    result=g.search('Dakar');self.assertEqual(result['places'][0]['longitude'],-17.44);self.assertEqual(g.search('dakar'),result);self.assertEqual(request.call_count,1);self.assertTrue(request.call_args.args[0].full_url.startswith('https://geocoding-api.open-meteo.com/v1/search?'))
 def test_invalid_inputs_never_request_provider(self):
  with tempfile.TemporaryDirectory() as d:
   with patch('urllib.request.urlopen') as request:
    for text in ['',None,'x'*121]:
     with self.assertRaises(HazardError):Geocoder(d).search(text)
    request.assert_not_called()
