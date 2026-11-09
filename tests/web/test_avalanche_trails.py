import unittest,tempfile,pathlib,json,gzip,datetime
from hazardia.web.avalanche_trails import checked_bounds,key_for,AvalancheTrails,atomic
from hazardia.web.avalanche_trails_geo import parse_trails
from hazardia.io import HazardError
class TrailCatalogueTests(unittest.TestCase):
 def test_bounded_italian_area_and_tiny_or_nonfinite_rejected(self):
  self.assertEqual(checked_bounds([13.38,42.28,13.92,42.65]),[13.38,42.28,13.92,42.65])
  for b in [[6,35,19,48],[13,42,13.00000001,42.1],[13,42,float('nan'),43],[True,42,14,43]]:
   with self.assertRaises(HazardError):checked_bounds(b)
 def test_relation_labels_preserved_without_invented_cai_certification(self):
  raw=dict(elements=[dict(type='way',id=1,tags=dict(highway='path',access='private',sac_scale='mountain_hiking'),geometry=[dict(lon=13,lat=42),dict(lon=13.1,lat=42.1)]),dict(type='relation',id=2,tags=dict(type='route',route='hiking',ref='101',operator='CAI'),members=[dict(type='way',ref=1)])]);features,quality=parse_trails(raw);p=features[0]['properties'];self.assertEqual(p['routes'][0]['ref'],'101');self.assertTrue(p['cai_label_declared']);self.assertFalse(p['cai_certification_verified']);self.assertFalse(p['passability_verified']);self.assertEqual(p['access'],'private')
 def test_geometry_gaps_not_connected_by_artificial_line(self):
  f,q=parse_trails(dict(elements=[dict(type='way',id=1,tags=dict(highway='path'),geometry=[dict(lon=13,lat=42),dict(lon=13.1,lat=42),None,dict(lon=14,lat=42),dict(lon=14.1,lat=42)])]));self.assertEqual(len(f[0]['geometry']['coordinates']),2);self.assertEqual(q['missing_geometry_parts'],1)
 def test_partial_overpass_error_is_not_valid_empty_inventory(self):
  with self.assertRaises(ValueError):parse_trails(dict(remark='timeout',elements=[]))
  f,q=parse_trails(dict(elements=[]));self.assertEqual(f,[])
 def test_new_forecast_invalidates_old_assessment_without_network(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'avalanche').mkdir();atomic(root/'avalanche/manifest.json',dict(sha256='a'));atomic(root/'avalanche/terrain-manifest.json',dict(sha256='b'));service=AvalancheTrails(root);bounds=[13.38,42.28,13.92,42.65];key=key_for(bounds);receipt=service.root/'receipt.json';atomic(receipt,dict(sha256='c'));atomic(service.root/(key+'.catalog.json'),dict(source='source.gz',receipt=receipt.name));now=datetime.datetime.now(datetime.timezone.utc);meta=dict(reference_utc=(now-datetime.timedelta(hours=1)).isoformat(),end_utc=(now+datetime.timedelta(hours=71)).isoformat(),weather_run_utc=(now-datetime.timedelta(hours=2)).isoformat(),source_acquired_at=(now-datetime.timedelta(days=8)).isoformat());file=service.root/'result.gz';file.write_bytes(gzip.compress(json.dumps(dict(metadata=meta,features=[])).encode()));atomic(service.root/(key+'.assessment.json'),dict(signature=service.assessment_signature(key),file=file.name));r=service.read_result(key);self.assertEqual(r['status'],'READY');self.assertTrue(r['data']['metadata']['source_stale']);atomic(root/'avalanche/manifest.json',dict(sha256='new'));self.assertIsNone(service.read_result(key))
 def test_pedestrian_area_is_not_invented_as_a_trail(self):
  f,q=parse_trails(dict(elements=[dict(type='way',id=1,tags=dict(highway='footway',area='yes'),geometry=[dict(lon=13,lat=42),dict(lon=13.1,lat=42),dict(lon=13,lat=42)])]));self.assertEqual(f,[])
 def test_failed_network_read_keeps_conservative_quota_reservation(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'avalanche').mkdir();service=AvalancheTrails(root);service.guard=lambda extra=0:None
   with patch('urllib.request.urlopen',side_effect=TimeoutError('source timeout')):
    with self.assertRaises(TimeoutError):service.fetch([13.38,42.28,13.92,42.65],'x')
   self.assertEqual(json.loads((service.root/'network.json').read_text())['bytes'],16*1024**2)
