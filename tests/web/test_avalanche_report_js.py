import unittest,re,json
from pathlib import Path
import quickjs
BASE=Path(__file__).resolve().parents[2]/'src/hazardia/web/static'
class AvalancheReportTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context()
  for name in ['avalanche-gran-sasso.js','avalanche-report.js']:
   self.js.eval(re.sub(r'^import .*?$','',(BASE/name).read_text(),flags=re.M).replace('export ',''))
  self.js.eval('''var start=Date.parse('2026-11-05T02:00Z'),e={history_start:'2026-11-03T02:00Z',history_hours:48,history_initial_hs_m:.08,recent24:{net_swe_increase_kg_m2:1,water_max_kg_m2:0},hourly:{quantities:{hs:{0:8,24:9,48:10,72:11}}},result:{forecast_windows:{}}};for(var h of [0,24,48,72])e.result.forecast_windows[h]={forecast_hs_max_cm:11,max_net_swe_increase_kg_m2:2,liquid_water_max_kg_m2:0};var f={geometry:{type:'Point',coordinates:[13.55,42.44]},properties:{profile_id:'A',profile_slope_deg:35,terrain_steep:true,profile_elevation_m:2000,profile_aspect_deg:0}},model={content_sha256:'hash-model',metadata:{reference_utc:'2026-11-05T02:00Z',end_utc:'2026-11-08T02:00Z',weather_run_utc:'2026-11-05T00:00Z',experiment_id:'fixture',unique_sites:3,usable_sites:1,status:'DEGRADED'},features:[f],models:{A:{NWP_INITIAL:e,ZERO_INITIAL:{alias:'NWP_INITIAL'}}}};''')
 def data(self,expr='avalancheReportData(model,null,null,start)'):
  return json.loads(self.js.eval('JSON.stringify('+expr+')'))
 def test_existing_native_values_and_four_windows(self):
  r=self.data();self.assertEqual([w['hs'][0] for w in r['rows'][0]['windows']],[8,9,10,11]);self.assertEqual(r['modelSha'],'hash-model');self.assertEqual(r['missing'],2)
 def test_stale_keeps_archived_values_but_cannot_claim_current(self):
  r=self.data('avalancheReportData(model,null,null,start+13*3600000)');self.assertTrue(r['dated']);self.assertEqual(r['rows'][0]['windows'][0]['hs'],[8,8])
 def test_missing_source_is_not_zero_observation(self):
  r=self.data();self.assertIsNone(r['eo']);self.assertEqual(r['stations'],[])
 def test_selection_does_not_export_entire_domain(self):
  self.assertEqual(self.data('avalancheReportData(model,null,[{properties:{profile_id:"other"}}],start)')['rows'],[])
 def test_selection_missing_profile_is_explicit(self):
  self.js.eval('model.models={}')
  r=self.data('avalancheReportData(model,null,[f],start)');self.assertEqual(r['rows'][0]['windows'][0]['kind'],'missing');self.assertIsNone(r['rows'][0]['windows'][0]['hs'])
 def test_unmatched_explanation_trace_is_not_used(self):
  self.js.eval('model.explanation_trace={status:"AVAILABLE",model_sha256:"wrong"}')
  self.assertIsNone(self.data()['trace'])
 def test_no_candidates_does_not_mean_safe(self):
  self.js.eval('f.properties.terrain_steep=false')
  self.assertEqual(self.data()['rows'],[])
  html=self.js.eval('renderAvalancheReport(avalancheReportData(model,null,null,start))');self.assertIn('Non significa assenza di pericolo',html)
 def test_report_escapes_all_external_text(self):
  self.js.eval('model.metadata.experiment_id="<script>alert(1)</script>"')
  html=self.js.eval('renderAvalancheReport(avalancheReportData(model,null,null,start))');self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
 def test_sensor_measurement_keeps_time_and_is_separate(self):
  r=self.data('avalancheReportData(model,{stations:[{name:"Campo",hs_cm:75,observed_at:"2026-11-05T04:00Z"}]},null,start)');self.assertEqual(r['stations'][0]['hs'],75);self.assertEqual(r['stations'][0]['observedAt'],'2026-11-05T04:00Z');self.assertEqual(r['rows'][0]['windows'][0]['hs'],[8,8])

 def test_report_includes_all_history_records_and_sources(self):
  self.js.eval('var extras={inventory:{product:{generated_at:"2026-11-06T00:00Z",sources:[{name:"Fonte A",url:"https://example.org"}]},features:[{id:"event:1",geometry:{type:"Point",coordinates:[13.5,42.4]},properties:{name:"Zona storica",event_date:"2020-01-02",date_precision:"DAY",record_kind:"EVENT_LOCATION",source_url:"https://example.org/events"}}]},observationSources:[{id:"s2",observed_at:"2026-11-05T10:00Z"}]}')
  html=self.js.eval('renderAvalancheReport(avalancheReportData(model,null,null,start,extras))');self.assertIn('Zona storica',html);self.assertIn('Fonte A',html);self.assertIn('2020-01-02',html);self.assertIn('https://example.org/events',html)
 def test_inventory_text_is_escaped_in_report(self):
  self.js.eval('var extras={inventory:{product:{sources:[{name:"<script>bad</script>"}]},features:[]}}')
  html=self.js.eval('renderAvalancheReport(avalancheReportData(model,null,null,start,extras))');self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
