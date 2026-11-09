import json,unittest
from pathlib import Path
try:import quickjs
except ImportError:quickjs=None

@unittest.skipUnless(quickjs,'QuickJS required')
class SnowSurfaceTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-snow-surface.js').read_text().replace('export ',''))
 def feature(self,row,col,depth):
  return dict(type='Feature',geometry=dict(type='Polygon',coordinates=[]),properties=dict(id=str(row)+':'+str(col),grid_row=row,grid_col=col,lon=13+col*.1,lat=43-row*.1,forecast_hs_cm=[0,depth,depth,depth],slope_deg=0))
 def field(self,features,lead=72):
  return json.loads(self.js.eval('JSON.stringify(snowSurface('+json.dumps(features)+','+str(lead)+'))'))
 def grid(self,values):return [self.feature(r,c,values[r*2+c]) for r in range(2) for c in range(2)]
 def test_zero_has_no_opaque_background_or_grid(self):
  value=self.field(self.grid([0,0,0,0]));self.assertEqual(value['polygons'],[]);self.assertEqual(value['positive'],0);self.assertEqual(value['isolated'],[])
 def test_missing_corner_never_interpolated_as_zero(self):
  value=self.field(self.grid([10,0,0,None]));self.assertEqual(value['polygons'],[]);self.assertEqual(value['missing'],1);self.assertEqual(len(value['isolated']),1)
 def test_no_extrapolation_outside_complete_stencil(self):
  fs=self.grid([0,20,0,0]);value=self.field(fs)
  self.assertTrue(value['polygons'])
  for polygon in value['polygons']:
   for lon,lat,height in polygon['points']:
    self.assertTrue(13-1e-10<=lon<=13.1+1e-10);self.assertTrue(42.9-1e-10<=lat<=43+1e-10);self.assertTrue(-1e-10<=height<=20+1e-10)
 def test_all_snow_on_flat_terrain_is_retained(self):
  result=self.field(self.grid([10,10,10,10]));self.assertTrue(result['polygons']);self.assertEqual(result['positive'],4)
 def test_native_values_never_mutated(self):
  self.js.eval('const fs='+json.dumps(self.grid([0,1,10,30]))+';const before=JSON.stringify(fs);snowSurface(fs,72)');self.assertTrue(self.js.eval('before===JSON.stringify(fs)'))
 def test_endpoints_use_correct_source_index(self):
  fs=self.grid([0,0,0,0]);fs[0]['properties']['forecast_hs_cm']=[99,1,5,0]
  self.assertEqual(self.field(fs,24)['positive'],1);self.assertEqual(self.field(fs,48)['positive'],1);self.assertEqual(self.field(fs,72)['positive'],0)
 def test_invalid_depth_is_missing(self):
  fs=self.grid([1,0,0,-5]);self.assertEqual(self.field(fs)['missing'],1);self.assertFalse(self.field(fs)['polygons'])
 def test_unsupported_lead_rejected(self):
  with self.assertRaises(Exception):self.field(self.grid([0,0,0,0]),12)
 def test_snow_height_above_top_band_remains_bounded(self):
  value=self.field(self.grid([60,60,60,60]));self.assertTrue(value['polygons']);self.assertTrue(all(p['color']=='#254b78' for p in value['polygons']))
