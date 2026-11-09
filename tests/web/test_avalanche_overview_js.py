import json,unittest
from pathlib import Path
import quickjs
class OverviewTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-overview.js').read_text().replace('export ',''))
 def overview(self,p,now='2026-11-04T13:00:00Z'):
  return json.loads(self.js.eval('JSON.stringify(observationOverview('+json.dumps(p)+',Date.parse('+json.dumps(now)+')))'))
 def test_old_or_cloudy_snow_is_not_current_coverage(self):
  p=dict(sources=[dict(observed_at='2026-11-02T10:00Z')],counts=dict(recent_classified_pixels=15,recent_snow_pixels=9),temporal_memory=dict(last_clear_snow_pixels=2207))
  o=self.overview(p);self.assertTrue(o['unobservable']);self.assertEqual(o['snow'],0);self.assertEqual(o['historicalSnow'],2207)
 def test_current_clouds_are_unknown_not_snow_absence(self):
  p=dict(sources=[dict(observed_at='2026-11-04T10:00Z')],counts=dict(recent_classified_pixels=0,recent_snow_pixels=0))
  self.assertTrue(self.overview(p)['unobservable'])
 def test_recent_clear_pixels_are_explicit_partial_observation(self):
  p=dict(sources=[dict(observed_at='2026-11-04T10:00Z')],counts=dict(recent_classified_pixels=8,recent_snow_pixels=3))
  o=self.overview(p);self.assertFalse(o['unobservable']);self.assertEqual(o['snow'],3)
 def test_future_station_or_satellite_not_current(self):
  o=self.overview(dict(sources=[dict(observed_at='2026-11-05T10:00Z')],stations=[dict(hs_cm=73,observed_at='2026-11-05T10:00Z')]))
  self.assertTrue(o['unobservable']);self.assertFalse(o['stations'][0]['current'])
 def test_aspect_is_geometric_not_risk_weight(self):
  for a,b in [(0,'N'),(90,'E'),(180,'S'),(270,'O'),(360,'N')]:self.assertEqual(self.js.eval('aspectName('+str(a)+')'),b)
 def test_context_exposes_only_existing_model_values(self):
  p=dict(properties=dict(profile_aspect_deg=315,slope_min_deg=32,slope_max_deg=40));a=dict(kind='factors',entries=[dict(history_hours=96,history_start='2026-10-31T13:00Z')],windows=[dict(wind_max_ms=12,air_temperature_min_c=-5,air_temperature_max_c=1)],load=[2],water=[0])
  c=json.loads(self.js.eval('JSON.stringify(conditionContext({},'+json.dumps(p)+','+json.dumps(a)+'))'));self.assertEqual(c['aspectName'],'NO');self.assertEqual(c['wind'],[12,12]);self.assertEqual(c['historyHours'],[96,96]);self.assertEqual(len(c['mechanisms']),1)
 def test_condition_map_does_not_fill_non_candidate_snow(self):
  self.assertEqual(json.loads(self.js.eval("JSON.stringify(conditionColor('snow'))")),[0,0,0,0]);self.assertEqual(json.loads(self.js.eval("JSON.stringify(conditionColor('zero'))")),[0,0,0,0]);self.assertGreater(self.js.eval("conditionColor('factors')[3]"),0)
 def test_condition_raster_keeps_native_terrain_labels_and_gaps(self):
  self.js.eval("var palette=new Uint8Array(65536*4);palette.set(conditionColor('factors'),4);palette.set(conditionColor('missing'),8);var pixels=new Uint8Array(12);paintConditionRows({width:3,height:1,view:new DataView(new Uint16Array([1,2,0]).buffer)},palette,0,1,pixels)")
  self.assertEqual(self.js.eval('pixels[3]'),195);self.assertEqual(self.js.eval('pixels[7]'),48);self.assertEqual(self.js.eval('pixels[11]'),0)
 def test_snow_history_reports_existing_mass_and_depth_without_invented_snowfall(self):
  e=dict(history_sample_times=['2026-11-02T10:00Z','2026-11-02T11:00Z','2026-11-04T10:00Z'],history_hs_cm=[20,18,10],history_swe_kg_m2=[50,50,30])
  out=json.loads(self.js.eval('JSON.stringify(snowHistoryRows('+json.dumps(e)+',"2026-11-02T11:00Z"))'));self.assertEqual(out['future'],1);self.assertEqual(out['days'][0]['hsFirst'],20);self.assertEqual(out['days'][0]['hsLast'],18);self.assertEqual(out['days'][0]['sweLast'],50)
 def test_incomplete_snow_history_is_not_zero_filled(self):
  e=dict(history_sample_times=['2026-11-02T10:00Z'],history_hs_cm=[None],history_swe_kg_m2=[10]);out=json.loads(self.js.eval('JSON.stringify(snowHistoryRows('+json.dumps(e)+',"2026-11-02T11:00Z"))'));self.assertEqual(out['invalid'],1);self.assertEqual(out['days'],[])
