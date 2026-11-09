import unittest,re,json
from pathlib import Path
import quickjs
BASE=Path(__file__).resolve().parents[2]/'src/hazardia/web/static'
class SnowSupportTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context()
  for name in ['avalanche-real-snow.js','avalanche-gran-sasso.js','avalanche-snow-depth.js','avalanche-snow-support.js','avalanche-overview.js']:
   self.js.eval(re.sub(r'^import .*?$','',(BASE/name).read_text(),flags=re.M).replace('export ',''))
  self.js.eval('''var now=Date.parse('2026-11-04T16:00Z'),g={width:4,height:1,crs:'EPSG:3857',projected_bounds:[0,0,400,100],labels:{1:'A',2:'B',3:'C',4:'D'}},view=new DataView(new Uint16Array([1,2,3,4]).buffer),feature=id=>({properties:{profile_id:id}}),entry=hs=>({history_start:'2026-11-02T14:00Z',history_hours:48,hourly:{quantities:{hs:{0:hs,24:0,48:hs,72:hs}}},result:{forecast_windows:{24:{forecast_hs_max_cm:hs}}}}),model={raster_index:g,index_view:view,metadata:{reference_utc:'2026-11-04T14:00Z',weather_run_utc:'2026-11-04T12:00Z'},features:['A','B','C','D'].map(feature),models:{A:{NWP_INITIAL:entry(8),ZERO_INITIAL:entry(0)},B:{NWP_INITIAL:entry(10),ZERO_INITIAL:entry(5)},C:{NWP_INITIAL:entry(0),ZERO_INITIAL:entry(0)}}},eo={...g,sources:[{observed_at:'2026-10-31T10:00Z'},{observed_at:'2026-11-04T15:00Z'}],index_view:new DataView(new Uint8Array([9,2,9,2,9,2,9,2]).buffer),memory_views:[new DataView(new Uint8Array([4,1,11,1,4,1,4,1]).buffer)]};''')
 def evaluate(self,expr):return self.js.eval(expr)
 def test_cloud_after_old_bare_uses_model_history_not_old_no_snow(self):
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).evidence[0]'),3)
  self.assertEqual(self.evaluate('satelliteSnowMask(eo,now)[0]'),0)
 def test_old_observed_snow_is_retained_under_cloud_with_original_kind(self):
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).evidence[1]'),2)
 def test_current_clear_bare_reports_model_disagreement_not_observed_snow(self):
  self.evaluate('eo.index_view.setUint8(0,4)')
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).mask[0]'),0)
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).stats.disagreement'),1)
 def test_model_zero_under_cloud_is_unconfirmed_not_observed_absence(self):
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).evidence[2]'),6)
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).mask[2]'),0)
 def test_missing_model_remains_missing(self):
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).evidence[3]'),5)
 def test_stale_or_uninitialized_model_cannot_fill_cloud(self):
  self.evaluate('model.models.A.NWP_INITIAL.history_hours=0')
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).evidence[0]'),5)
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now+12*3600000).evidence[0]'),5)
 def test_initial_condition_sensitivity_is_preserved(self):
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).stats.initialSensitive'),1)
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,0,now).values.get("A").supportMin'),0)
 def test_missing_or_misaligned_satellite_does_not_disable_qualified_model(self):
  self.assertEqual(self.evaluate('buildSnowSupport(model,null,0,now).evidence[0]'),4)
  self.assertFalse(self.evaluate('buildSnowSupport(model,{...eo,width:3},0,now).eoAligned'))
  self.assertEqual(self.evaluate('buildSnowSupport(model,{...eo,width:3},0,now).evidence[0]'),4)
 def test_future_window_can_contain_snow_even_if_it_has_melted_at_end(self):
  self.evaluate('eo.index_view.setUint8(0,4)')
  self.assertGreater(self.evaluate('buildSnowSupport(model,eo,24,now).mask[0]'),0)
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,24,now).values.get("A").max'),0)
  self.assertEqual(self.evaluate('buildSnowSupport(model,eo,24,now).values.get("A").supportMax'),8)
 def test_estimated_raster_and_alert_mask_exclude_missing_cells(self):
  self.evaluate('var s=buildSnowSupport(model,eo,0,now),rgba=new Uint8Array(16);paintEstimatedSnowRows(g,s,0,1,rgba);var palette=new Uint8Array(65536*4);for(var i=1;i<=4;i++)palette.set(conditionColor("candidate"),i*4);var alerts=new Uint8Array(16);paintConditionRows({width:4,height:1,view},palette,0,1,alerts,s.mask)')
  self.assertGreater(self.evaluate('rgba[3]'),0);self.assertEqual(self.evaluate('rgba[7]'),0)
  self.assertEqual(self.evaluate('JSON.stringify([0,1,2,3].map(i=>alerts[i*4+3]>0))'),'[true,true,false,false]')
 def test_pin_can_be_anchored_on_estimated_snow_with_explicit_provenance(self):
  self.evaluate('var s=buildSnowSupport(model,eo,0,now),pins=supportedSnowPins([{id:"A"},{id:"B"},{id:"D"}],g,s)')
  self.assertEqual(self.evaluate('pins.length'),2)
  self.assertEqual(self.evaluate('pins[0].snowEvidence'),'ESTIMATED');self.assertEqual(self.evaluate('pins[1].snowEvidence'),'HISTORICAL')
 def test_estimated_alert_hatching_is_distinct_from_observed_alert(self):
  self.evaluate('var s=buildSnowSupport(model,eo,0,now),palette=new Uint8Array(65536*4);palette.set(conditionColor("factors"),4);palette.set(conditionColor("factors"),8);var out=new Uint8Array(16);paintSupportedConditionRows({width:4,height:1,view},palette,s,0,1,out)')
  self.assertEqual(self.evaluate('out[3]'),0);self.assertGreater(self.evaluate('out[7]'),0);self.assertEqual(self.evaluate('out[15]'),0)
 def test_map_cell_reports_estimate_and_preserves_outside(self):
  self.evaluate('var s=buildSnowSupport(model,eo,0,now),lon=x=>x/6378137*180/Math.PI,lat=y=>(2*Math.atan(Math.exp(y/6378137))-Math.PI/2)*180/Math.PI')
  self.assertEqual(self.evaluate('snowSupportCell(model,s,lon(50),lat(50)).code'),3)
  self.assertFalse(self.evaluate('snowSupportCell(model,s,lon(350),lat(50)).snow'))
  self.assertTrue(self.evaluate('snowSupportCell(model,s,lon(999),lat(50))===null'))
