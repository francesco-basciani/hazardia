"""Run production pure JS in QuickJS on Linux; optional test dependency only."""
import json,unittest
from pathlib import Path
try:import quickjs
except ImportError:quickjs=None

@unittest.skipUnless(quickjs,'QuickJS test dependency not installed')
class AvalancheModelJSTests(unittest.TestCase):
 def test_polygon_holes_multipolygon_and_no_safety_claim(self):
  context=quickjs.Context();source=(Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-model.js').read_text();context.eval(source.replace('export ',''))
  data=dict(type='FeatureCollection',metadata=dict(reference_utc='2026-10-29T21:00:00Z',end_utc='2026-11-01T21:00:00Z',weather_run_utc='2026-10-29T18:00:00Z'),features=[dict(properties=dict(factor_class=4,id='a'),geometry=dict(type='Polygon',coordinates=[[[0,0],[4,0],[4,4],[0,4],[0,0]],[[1,1],[2,1],[2,2],[1,2],[1,1]]])),dict(properties=dict(factor_class=0,id='missing'),geometry=dict(type='MultiPolygon',coordinates=[[[[6,0],[8,0],[8,2],[6,2],[6,0]]]]))])
  context.eval('const data='+json.dumps(data)+';')
  self.assertEqual(context.eval('locateSample(data,.5,.5).properties.id'),'a');self.assertTrue(context.eval('locateSample(data,1.5,1.5)===null'));self.assertEqual(context.eval('locateSample(data,7,1).properties.id'),'missing');self.assertTrue(context.eval('locateSample(data,100,70)===null'))
  self.assertFalse(context.eval('positionAssessment(data,7,1).reliableReleaseDetection'));self.assertEqual(context.eval('positionAssessment(data,7,1).code'),'MISSING')
  context.eval("data.features[0].properties.factor_class=1;data.metadata.reference_utc=new Date(Date.now()-3600000).toISOString();data.metadata.end_utc=new Date(Date.now()+71*3600000).toISOString();data.metadata.weather_run_utc=data.metadata.reference_utc;")
  self.assertEqual(context.eval('positionAssessment(data,.5,.5).code'),'NOT_DETECTED_UNRESOLVED');context.eval('data.features[0].properties.factor_class=4;');self.assertEqual(context.eval('positionAssessment(data,.5,.5).code'),'PHYSICAL_SIGNALS');self.assertEqual(context.eval('positionAssessment(data,100,70).code'),'OUTSIDE_COVERAGE')
  context.eval("data.metadata.freshness_status='STALE';");self.assertEqual(context.eval('positionAssessment(data,.5,.5).code'),'STALE')
 def test_staleness_and_missing_snow_never_zero(self):
  context=quickjs.Context();context.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-model.js').read_text().replace('export ',''))
  self.assertEqual(context.eval("category({forecast_hs_cm:null},'snow72')[1]"),'Dato mancante');self.assertEqual(context.eval("category({forecast_hs_cm:[0,0,0,0]},'snow72')[1]"),'0 cm modellati')
  context.eval("const meta={reference_utc:'2026-10-29T21:00:00Z',end_utc:'2026-11-01T21:00:00Z',weather_run_utc:'2026-10-29T18:00:00Z'};")
  self.assertFalse(context.eval("isStale(meta,Date.parse('2026-10-29T22:00:00Z'))"));self.assertTrue(context.eval("isStale(meta,Date.parse('2026-10-30T07:00:00Z'))"));self.assertTrue(context.eval("isStale(meta,Date.parse('2026-11-02T07:00:00Z'))"))
 def test_fine_footprint_takes_precedence_over_coarse_forecast_cell(self):
  context=quickjs.Context();context.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-model.js').read_text().replace('export ',''))
  context.eval("const now=Date.now();const data={metadata:{reference_utc:new Date(now-3600000).toISOString(),weather_run_utc:new Date(now-7200000).toISOString(),end_utc:new Date(now+71*3600000).toISOString()},features:[{properties:{factor_class:4},geometry:{type:'Polygon',coordinates:[[[0,0],[4,0],[4,4],[0,4],[0,0]]]}}],potential_areas:[{properties:{potential_class:6},geometry:{type:'Polygon',coordinates:[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}}]};")
  self.assertEqual(context.eval('positionAssessment(data,.5,.5).code'),'POTENTIAL_HAZARD');self.assertFalse(context.eval('positionAssessment(data,.5,.5).reliableReleaseDetection'));self.assertEqual(context.eval('positionAssessment(data,3,3).code'),'OUTSIDE_COVERAGE')
  context.eval('data.potential_areas[0].properties.potential_class=2');self.assertEqual(context.eval('positionAssessment(data,.5,.5).code'),'TERRAIN_SNOW_UNVERIFIED')
  context.eval('data.metadata.freshness_status="STALE"');self.assertEqual(context.eval('positionAssessment(data,.5,.5).code'),'STALE')
 def test_potential_and_missing_are_independent_display_channels(self):
  context=quickjs.Context();context.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-model.js').read_text().replace('export ',''))
  context.eval("const p={potential_class:6,soil_association:'WRB',substrate:'Calcari',soil_missing_samples:1,substrate_missing_samples:0};")
  self.assertTrue(context.eval('potentialDisplay(p).potential'));self.assertEqual(context.eval('potentialDisplay(p).uncertainty'),'ground_gap')
  context.eval('p.potential_class=0');self.assertFalse(context.eval('potentialDisplay(p).potential'));self.assertEqual(context.eval('potentialDisplay(p).uncertainty'),'missing')
  context.eval('p.potential_class=2');self.assertFalse(context.eval('potentialDisplay(p).potential'));self.assertEqual(context.eval('potentialDisplay(p).uncertainty'),'snow_unverified')
  context.eval('p.potential_class=6;p.soil_missing_samples=0');self.assertTrue(context.eval('potentialDisplay(p).uncertainty===null'));context.eval('p.potential_class=1;p.soil_association=null');self.assertTrue(context.eval('potentialDisplay(p).uncertainty===null'))

@unittest.skipUnless(quickjs,'QuickJS test dependency not installed')
class AvalancheEvolutionJSTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-model.js').read_text().replace('export ',''))
  self.js.eval("const base={forecast_hs_max_cm:10,liquid_water_max_kg_m2:0,max_net_swe_increase_kg_m2:0};const raw={metadata:{forecast_windows:{A:{'0':{...base,max_net_swe_increase_kg_m2:null},'24':{...base,liquid_water_max_kg_m2:2},'48':{...base,max_net_swe_increase_kg_m2:3},'72':base}}},potential_areas:[{properties:{model_sample_id:'A',terrain_steep:true,potential_class:6,potential_missing:['Observed stability']}}]};const original=JSON.stringify(raw);")
 def test_windows_change_class_without_mutating_original(self):
  self.assertEqual(self.js.eval("JSON.stringify([0,24,48,72].map(h=>projectPotentialAt(raw,h).potential_areas[0].properties.potential_class))"),'[3,5,4,3]')
  self.assertTrue(self.js.eval('original===JSON.stringify(raw)'))
  self.assertIn('precedente',self.js.eval('projectPotentialAt(raw,0).potential_areas[0].properties.potential_missing.join()'))
 def test_missing_window_or_load_cannot_reuse_whole_period(self):
  self.js.eval("delete raw.metadata.forecast_windows.A['48'];raw.metadata.forecast_windows.A['24'].max_net_swe_increase_kg_m2=null;")
  for lead in (24,48):self.assertEqual(self.js.eval(f'projectPotentialAt(raw,{lead}).potential_areas[0].properties.potential_class'),0)
 def test_local_missing_does_not_use_unrelated_national_column(self):
  self.js.eval("raw.potential_areas[0].properties.model_sample_id='LOCAL_MISSING';")
  self.assertEqual(self.js.eval('projectPotentialAt(raw,72).potential_areas[0].properties.potential_class'),0)
 def test_no_snow_and_below_slope_not_safety(self):
  self.js.eval('raw.metadata.forecast_windows.A[72].forecast_hs_max_cm=0;')
  self.assertEqual(self.js.eval('projectPotentialAt(raw,72).potential_areas[0].properties.potential_class'),2)
  self.js.eval('raw.potential_areas[0].properties.terrain_steep=false;')
  self.assertEqual(self.js.eval('projectPotentialAt(raw,72).potential_areas[0].properties.potential_class'),1)
 def test_unsupported_lead_rejected(self):
  with self.assertRaises(Exception):self.js.eval('projectPotentialAt(raw,6)')
