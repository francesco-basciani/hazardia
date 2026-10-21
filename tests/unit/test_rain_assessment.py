import copy,datetime as dt,json,tempfile,unittest
from pathlib import Path
from hazardia.rain_assessment import assess
from hazardia.ingest.attention import AttentionStore
class RainTests(unittest.TestCase):
 def fixture(self):
  start=dt.datetime(2026,10,21,tzinfo=dt.timezone.utc)
  field=dict(id='test',available_at='2026-10-21T00:00:00Z',model='fixture',source={},bounds=[[40,10],[42,12]],lats=[40+i/4 for i in range(9)],lons=[10+i/4 for i in range(9)],records=[dict(at=(start+dt.timedelta(hours=i)).isoformat().replace('+00:00','Z'),precipitation=[2.]*81,rain_probability=[100]*81) for i in range(72)])
  polygon=lambda a,b,c,d:dict(type='Polygon',coordinates=[[[a,b],[c,b],[c,d],[a,d],[a,b]]])
  zones=dict(type='FeatureCollection',features=[dict(type='Feature',geometry=polygon(10.1,40.1,10.9,40.9),properties=dict(id='z',name='Test',source_geometry_valid=True))])
  return field,zones
 def test_complete_hourly_totals_and_no_probability_as_amount(self):
  f,z=self.fixture();p=assess(f,z,'2026-10-22T00:00:00Z')['features'][0]['properties']
  self.assertEqual([p['windows'][str(h)]['mean_mm'] for h in (1,3,6,12,24,48)],[2,6,12,24,48,96]);self.assertEqual(p['previous_24h_forecast']['mean_mm'],48);self.assertEqual(p['risk_status'],'NOT_EVALUABLE')
 def test_reused_spatial_plan_preserves_all_values(self):
  f,z=self.fixture();a=assess(f,z,'2026-10-21T00:00:00Z');b=assess(f,z,'2026-10-21T00:00:00Z',json.loads(json.dumps(a['sampling_plan'])));self.assertEqual(a['features'],b['features'])
 def test_hourly_series_tracks_variable_rain_not_probability(self):
  f,z=self.fixture()
  for i,r in enumerate(f['records']):r['precipitation']=[float(i)]*81
  p=assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties'];s=p['hourly_forecast']
  self.assertEqual(len(s),48);self.assertEqual([r['mean_mm'] for r in s],list(range(48)))
  self.assertEqual(s[0]['until'],s[1]['at']);self.assertEqual(s[-1]['until'],'2026-10-23T00:00:00Z')
  for h in (1,3,6,12,24,48):self.assertAlmostEqual(sum(r['mean_mm'] for r in s[:h]),p['windows'][str(h)]['mean_mm'])
 def test_hourly_gap_is_unknown_and_later_hours_survive(self):
  f,z=self.fixture();f['records'].pop(3);s=assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties']['hourly_forecast']
  self.assertEqual(s[3]['status'],'UNAVAILABLE');self.assertNotIn('mean_mm',s[3]);self.assertEqual(s[4]['mean_mm'],2.)
 def test_hourly_partial_and_end_of_forecast_remain_unknown(self):
  f,z=self.fixture();s=assess(f,z,'2026-10-23T23:00:00Z')['features'][0]['properties']['hourly_forecast']
  self.assertEqual(s[0]['mean_mm'],2.);self.assertTrue(all(r['status']=='UNAVAILABLE' for r in s[1:]))
  z['features'][0]['properties']['source_geometry_valid']=False
  self.assertTrue(all(r['status']=='UNAVAILABLE' for r in assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties']['hourly_forecast']))
 def test_missing_hour_never_zero_and_short_window_survives(self):
  f,z=self.fixture();f['records'].pop(3);p=assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties'];self.assertEqual(p['windows']['3']['mean_mm'],6);self.assertEqual(p['windows']['6']['status'],'UNAVAILABLE');self.assertNotIn('mean_mm',p['windows']['6']);self.assertEqual(p['previous_24h_forecast']['status'],'UNAVAILABLE')
 def test_partial_zone_not_extrapolated(self):
  f,z=self.fixture();z['features'][0]['geometry']['coordinates'][0][0][0]=9.5
  p=assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties'];self.assertEqual(p['windows']['1']['status'],'UNAVAILABLE')
 def test_invalid_zone_withheld(self):
  f,z=self.fixture();z['features'][0]['properties']['source_geometry_valid']=False
  self.assertEqual(assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties']['spatial_status'],'UNAVAILABLE')
 def test_negative_or_missing_value_withheld(self):
  for bad in [-1,None,float('nan')]:
   f,z=self.fixture();f['records'][0]['precipitation'][0]=bad
   self.assertEqual(assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties']['windows']['1']['status'],'UNAVAILABLE')
 def test_subhour_rejected(self):
  f,z=self.fixture()
  with self.assertRaises(ValueError):assess(f,z,'2026-10-21T00:30:00Z')
 def test_holes_excluded_and_weighted_spatial_variation(self):
  f,z=self.fixture();f['records'][0]['precipitation']=[float(i%9) for i in range(81)]
  p=assess(f,z,'2026-10-21T00:00:00Z')['features'][0]['properties']['windows']['1'];self.assertAlmostEqual(p['mean_mm'],2.,places=2);self.assertLess(p['sampled_min_mm'],p['sampled_max_mm'])
 def test_lossless_attention_compaction_manifest_and_layer(self):
  from test_attention import AttentionTests
  with tempfile.TemporaryDirectory() as root:
   store,ident,name=AttentionTests().fixture(root);before=store.snapshot();layer=store.layer(ident,name)
   store.compact();self.assertEqual(store.snapshot(),before);self.assertEqual(store.layer(ident,name),layer)
   self.assertTrue((Path(root)/ident/'result.json.gz').exists())
