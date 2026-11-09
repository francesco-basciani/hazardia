import copy,json,unittest
from pathlib import Path
import quickjs
class HSPilotViewTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-hs-pilot.js').read_text().replace('export ',''))
  import datetime as dt
  t=dt.datetime(2026,11,1,7,tzinfo=dt.timezone.utc);rows=[dict(lead_hours=i,at_utc=(t+dt.timedelta(hours=i)).isoformat().replace('+00:00','Z'),hs_cm=i,swe_kg_m2=i,water_kg_m2=0) for i in range(73)]
  self.p=dict(schema='hazardia.avalanche.hs-pilot/1.0',status='NOT_QUALIFIED',correction_applied=False,regional_product_replaced=False,geometry=dict(type='Point',coordinates=[13.57,42.44]),reference_utc=rows[0]['at_utc'],end_utc=rows[-1]['at_utc'],forecast={k:copy.deepcopy(rows) for k in ['original_archived','restart_control','hs_forced_trial']})
 def valid(self):return self.js.eval('!!validateHSPilot('+json.dumps(self.p)+')')
 def test_failed_trial_remains_visible_without_claiming_applied_correction(self):
  self.assertTrue(self.valid());self.p['correction_applied']=True
  with self.assertRaises(Exception):self.valid()
 def test_success_label_cannot_replace_nonqualified_trial(self):
  self.p['status']='PASS'
  with self.assertRaises(Exception):self.valid()
 def test_no_extrapolation_outside_common72h(self):
  for at in ['2026-11-01T06:00:00Z','2026-11-04T08:00:00Z','bad']:
   self.assertTrue(self.js.eval('hsPilotFrame('+json.dumps(self.p)+','+json.dumps(at)+')===null'))
 def test_every_native_hour_is_selected_including72(self):
  for h in [0,1,6,12,24,48,72]:
   r=self.p['forecast']['original_archived'][h];self.assertEqual(self.js.eval('hsPilotFrame('+json.dumps(self.p)+','+json.dumps(r['at_utc'])+').trial.hs_cm'),h)
 def test_incomplete_negative_or_misaligned_series_rejected(self):
  for change in ['negative','time','missing']:
   p=copy.deepcopy(self.p)
   if change=='negative':p['forecast']['hs_forced_trial'][4]['swe_kg_m2']=-1
   elif change=='time':p['forecast']['restart_control'][3]['at_utc']=p['reference_utc']
   else:p['forecast']['original_archived'].pop()
   with self.assertRaises(Exception):self.js.eval('validateHSPilot('+json.dumps(p)+')')
 def test_fake_corrected_area_not_accepted_as_point_trial(self):
  self.p['geometry']['type']='Polygon'
  with self.assertRaises(Exception):self.valid()
 def conditioned(self):
  self.p.update(schema='hazardia.avalanche.hs-pilot/2.0',status='OBSERVATION_CONDITIONED_RESEARCH',correction_applied=True,correction_kind='NATIVE_HS_HISTORY_CONDITIONING',spatial_scope='GSL22_ONLY',independent_validation='NOT_RUN',observed_hs_cm=1,validation=dict(original_reproduction=dict(status='PASS',max_hs_difference_cm=0)))
  self.p['forecast']['restart_control'][0]['hs_cm']=1.77;self.p['forecast']['hs_forced_trial'][0]['hs_cm']=1.25
 def test_conditioned_research_requires_actual_improvement(self):
  self.conditioned();self.assertTrue(self.valid());self.p['forecast']['hs_forced_trial'][0]['hs_cm']=2
  with self.assertRaises(Exception):self.valid()
 def test_conditioned_column_cannot_be_promoted_to_regional_correction(self):
  self.conditioned();self.p['regional_product_replaced']=True
  with self.assertRaises(Exception):self.valid()
 def test_conditioned_result_requires_reproduction_and_local_scope(self):
  for field in ['scope','reproduction','validation']:
   self.conditioned()
   if field=='scope':self.p['spatial_scope']='ITALY'
   elif field=='reproduction':self.p['validation']['original_reproduction']['max_hs_difference_cm']=.61
   else:self.p['independent_validation']='PASS'
   with self.assertRaises(Exception):self.valid()
