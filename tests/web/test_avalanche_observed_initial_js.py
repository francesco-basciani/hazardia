import unittest,json,copy
from pathlib import Path
import quickjs
class ObservedInitialViewTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-hs-pilot.js').read_text().replace('export ',''))
  self.js.eval('''var start=Date.parse('2026-11-04T14:00Z'),rows=Array.from({length:73},(_,h)=>({lead_hours:h,at_utc:new Date(start+h*3600000).toISOString(),hs_cm:75-h*.01,swe_kg_m2:225,water_kg_m2:0})),p={schema:'hazardia.avalanche.hs-initialization/1.0',status:'OBSERVED_HEIGHT_INITIALIZED_RESEARCH',correction_applied:true,correction_kind:'OBSERVED_HEIGHT_COLD_INITIALIZATION',spatial_scope:'GSL22_POINT_ONLY',independent_validation:'NOT_RUN',regional_product_replaced:false,geometry:{type:'Point',coordinates:[13.57,42.44]},reference_utc:new Date(start).toISOString(),end_utc:new Date(start+72*3600000).toISOString(),observed_hs_cm:75,point:{id:'GSL22',flat_control:true},forecast:{original_archived:rows.map(x=>({...x})),restart_control:rows.map(x=>({...x})),hs_forced_trial:rows.map(x=>({...x}))},validation:{original_reproduction:{status:'NOT_APPLICABLE_COLD_START'}},initial_swe_origin:'MODELLED_FROM_ASSUMED_DENSITY_NOT_MEASURED',initialization_priors:{density_kg_m3:300,temperature_k:272.15}};''')
 def test_new_method_has_distinct_qualification(self):self.assertTrue(self.js.eval('validateHSPilot(p)===p'))
 def test_no_fake_replay_validation(self):
  self.js.eval('p.validation.original_reproduction.status="PASS"')
  with self.assertRaises(quickjs.JSException):self.js.eval('validateHSPilot(p)')
 def test_no_regional_extrapolation(self):
  self.js.eval('p.regional_product_replaced=true')
  with self.assertRaises(quickjs.JSException):self.js.eval('validateHSPilot(p)')
 def test_75cm_initial_measure_must_match(self):
  self.js.eval('p.forecast.hs_forced_trial[0].hs_cm=8')
  with self.assertRaises(quickjs.JSException):self.js.eval('validateHSPilot(p)')
 def test_shared_clock_uses_native_hour_without_extrapolating(self):
  self.assertEqual(self.js.eval('hsPilotFrame(p,new Date(start+72*3600000).toISOString()).trial.hs_cm'),74.28)
  self.assertTrue(self.js.eval('hsPilotFrame(p,new Date(start+73*3600000).toISOString())===null'))

 def test_reference_label_is_real_measurement_with_observation_date(self):
  self.js.eval('p.forecast.hs_forced_trial[0].hs_cm=74.999')
  value=json.loads(self.js.eval('JSON.stringify(observedHeightLabel(p,hsPilotFrame(p,p.reference_utc)))'))
  self.assertEqual(value,{'kind':'Misura reale','hs':75,'at':'2026-11-04T14:00:00.000Z'})
 def test_future_label_is_forecast_not_measurement(self):
  value=json.loads(self.js.eval('JSON.stringify(observedHeightLabel(p,hsPilotFrame(p,p.end_utc)))'))
  self.assertEqual(value['kind'],'Previsione +72h')
  self.assertEqual(value['hs'],74.28)
