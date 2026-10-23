import json,tempfile,time,unittest
from pathlib import Path
from hazardia.web.observed_layers import ObservedLayers,earthquake_features,power_features,voltage_values,bounds
from hazardia.io import HazardError
HEADER=b'#EventID|Time|Latitude|Longitude|Depth/Km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|MagAuthor|EventLocationName|EventType\n'
QUAKE=HEADER+b'1|2026-10-23T12:00:00.100000|42.4|13.5|8|INGV|x|x|1|ML|0.4|INGV|Test area|earthquake\n'
POWER=json.dumps({'elements':[{'type':'way','id':1,'version':2,'timestamp':'2026-10-20T00:00:00Z','tags':{'power':'line','voltage':'380000;132000'},'geometry':[{'lat':42,'lon':13},{'lat':42.1,'lon':13.1}]},{'type':'node','id':2,'lat':42,'lon':13,'tags':{'power':'tower'}},{'type':'way','id':3,'tags':{'power':'cable','location':'underground','voltage':'220000'},'geometry':[{'lat':42,'lon':13},{'lat':42.1,'lon':13.1}]}]}).encode()
class LayersTest(unittest.TestCase):
 def wait(self,service,request):
  for _ in range(100):
   value=service.snapshot(request['request_id'])
   if value['status']!='LOADING':return value
   time.sleep(.005)
  self.fail('Worker did not finish')
 def test_small_magnitude_and_time(self):
  f,q=earthquake_features(QUAKE);self.assertEqual(f[0]['properties']['magnitude'],.4);self.assertTrue(f[0]['properties']['at'].endswith('Z'));self.assertEqual(q['skipped'],0)
 def test_zero_rows_distinct_invalid(self):
  self.assertEqual(earthquake_features(b'')[0],[]);self.assertEqual(earthquake_features(HEADER)[0],[])
  for raw in [b'HTML error',HEADER+b'1|bad|x\n']:
   with self.assertRaises(ValueError):earthquake_features(raw)
 def test_nan_skipped_never_json(self):
  f,q=earthquake_features(QUAKE+QUAKE.splitlines()[1].replace(b'|0.4|',b'|nan|')+b'\n');self.assertEqual(len(f),1);self.assertEqual(q['skipped'],1)
 def test_voltage_units_and_missing(self):
  self.assertEqual(voltage_values('380000;132000'),[132000,380000]);self.assertEqual(voltage_values('15 kV;unknown'),[])
  f,q=power_features(POWER);self.assertEqual(f[0]['properties']['max_voltage'],380000);self.assertIsNone(f[1]['properties']['max_voltage']);self.assertEqual(f[2]['properties']['location'],'underground');self.assertFalse(any(x['properties']['optimization_eligible'] for x in f));self.assertEqual(q['unknown_voltage'],1)
 def test_xml_power_extract_ignores_roads_preserves_voltage(self):
  raw=b'<osm><node id="1" lat="42" lon="13"/><node id="2" lat="42.1" lon="13.1"/><way id="3"><nd ref="1"/><nd ref="2"/><tag k="power" v="line"/><tag k="voltage" v="132000"/></way><way id="4"><tag k="highway" v="primary"/></way></osm>'
  features,quality=power_features(raw);self.assertEqual(len(features),1);self.assertEqual(features[0]['properties']['max_voltage'],132000);self.assertEqual(features[0]['properties']['location'],'overhead')
 def test_incomplete_power_is_error(self):
  with self.assertRaises(ValueError):power_features(b'{"remark":"timeout","elements":[]}')
  with self.assertRaises(ValueError):power_features(json.dumps({'elements':[{}]*5001}).encode())
 def test_invalid_queries_and_source_allowlist(self):
  with tempfile.TemporaryDirectory() as root:
   service=ObservedLayers(root,'earthquakes',fetch=lambda u:self.fail('Must not fetch invalid request'))
   base=dict(bounds=[13,42,14,43],provider='ingv',days=7,min_magnitude=0)
   for change in [{'provider':'http://localhost'},{'days':365},{'min_magnitude':float('nan')},{'bounds':[0,0,100,60]},{'url':'http://bad'}]:
    with self.assertRaises(HazardError):service.prepare(dict(base,**change))
   with self.assertRaises(HazardError):service.snapshot('../../etc/passwd')
   with self.assertRaises(HazardError):bounds([13,42,13.0000001,43])
   power=ObservedLayers(root,'power')
   with self.assertRaises(HazardError):power.prepare({'bounds':[0,0,5,5]})
 def test_real_adapter_shape_cache_and_restart(self):
  with tempfile.TemporaryDirectory() as root:
   calls=[];service=ObservedLayers(root,'earthquakes',fetch=lambda u:(calls.append(u) or QUAKE));body=dict(bounds=[13,42,14,43],provider='ingv',days=7,min_magnitude=0)
   value=self.wait(service,service.prepare(body));self.assertEqual(value['status'],'READY');self.assertFalse(value['coupled_to_optimizer']);self.assertEqual(len(value['features']),1)
   self.assertEqual(service.prepare(body)['request_id'],value['request_id']);self.assertEqual(len(calls),1)
   restarted=ObservedLayers(root,'earthquakes',fetch=lambda u:self.fail('No new fetch'));self.assertEqual(restarted.snapshot(value['request_id'])['features'],value['features'])
 def test_source_error_not_empty_ready(self):
  with tempfile.TemporaryDirectory() as root:
   def fail(url):raise TimeoutError('source unavailable')
   service=ObservedLayers(root,'power',fetch=fail);value=self.wait(service,service.prepare({'bounds':[13,42,14,43]}));self.assertEqual(value['status'],'ERROR');self.assertNotIn('features',value)
 def test_request_isolation_and_quota(self):
  with tempfile.TemporaryDirectory() as root:
   service=ObservedLayers(root,'power',fetch=lambda u:POWER);first=self.wait(service,service.prepare({'bounds':[13,42,14,43]}));service.last=0
   second=self.wait(service,service.prepare({'bounds':[14,42,15,43]}));self.assertNotEqual(first['request_id'],second['request_id']);self.assertEqual(service.snapshot(first['request_id'])['bounds'],[13,42,14,43])
   service.last=0;list(Path(service.root).glob('*.quota'))[0].write_text('8')
   with self.assertRaises(HazardError):service.prepare({'bounds':[15,42,16,43]})
   self.assertEqual(service.prepare({'bounds':[13,42,14,43]})['status'],'READY')
if __name__=='__main__':unittest.main()
