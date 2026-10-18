import datetime as dt,importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('fire_initialization_assessment',Path(__file__).resolve().parents[2]/'scripts/assess_fire_initialization.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class InitializationAssessmentTests(unittest.TestCase):
 def fixture(self):
  start=dt.datetime(2026,10,11,16);times=[(start+dt.timedelta(hours=i)).isoformat(timespec='minutes') for i in range(171)]
  return dict(timezone='GMT',utc_offset_seconds=0,latitude=42.375,longitude=13.75,elevation=1233,hourly_units={'time':'iso8601','temperature_2m':'°C','relative_humidity_2m':'%','wind_speed_10m':'m/s','precipitation':'mm'},hourly=dict(time=times,temperature_2m=[20.]*171,relative_humidity_2m=[50.]*171,wind_speed_10m=[2.]*171,precipitation=[0.]*171))
 def run_case(self,r):return module.assess(r,'2026-10-18T16:00:00Z')
 def test_exact_complete_window(self):
  r=self.run_case(self.fixture());self.assertEqual(r['antecedent_hours'],168);self.assertEqual([x['initial_ffmc_assumption'] for x in r['histories']],[65,85,95]);self.assertTrue(all(len(x['trace_percent'])==168 for x in r['histories']))
 def test_later_rain_does_not_leak(self):
  a=self.fixture();b=self.fixture();b['hourly']['precipitation'][169:]=[80.,80.];self.assertEqual(self.run_case(a),self.run_case(b))
 def test_completed_interval_rain_is_consumed(self):
  a=self.fixture();b=self.fixture();b['hourly']['precipitation'][168]=40.;self.assertGreater(self.run_case(b)['histories'][1]['at_ignition_percent'],self.run_case(a)['histories'][1]['at_ignition_percent'])
 def test_incomplete_history_rejected(self):
  r=self.fixture()
  for a in r['hourly'].values():a.pop(0)
  with self.assertRaisesRegex(ValueError,'168h'):self.run_case(r)
 def test_gap_rejected(self):
  r=self.fixture();r['hourly']['time'][10]='2026-10-12T08:00'
  with self.assertRaisesRegex(ValueError,'gap'):self.run_case(r)
 def test_unknown_and_units_rejected(self):
  r=self.fixture();r['hourly']['relative_humidity_2m'][4]=None
  with self.assertRaisesRegex(ValueError,'Missing'):self.run_case(r)
  r=self.fixture();r['hourly_units']['wind_speed_10m']='km/h'
  with self.assertRaisesRegex(ValueError,'units'):self.run_case(r)
