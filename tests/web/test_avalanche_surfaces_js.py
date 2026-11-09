import json,unittest
from pathlib import Path
try:import quickjs
except ImportError:quickjs=None
@unittest.skipUnless(quickjs,'QuickJS required')
class AvalancheSurfaceTests(unittest.TestCase):
 def setUp(self):
  self.c=quickjs.Context();self.c.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-surfaces.js').read_text().replace('export ',''))
 def classify(self,p):return json.loads(self.c.eval('JSON.stringify(potentialSurface('+json.dumps(p)+'))'))
 def test_all_existing_potential_categories_kept(self):
  for code in [3,4,5,6]:self.assertEqual(self.classify(dict(potential_class=code,terrain_steep=True))['kind'],'potential')
 def test_steep_without_verified_snow_is_visible_as_uncertain_surface(self):
  self.assertEqual(self.classify(dict(potential_class=2,terrain_steep=True)),dict(visible=True,kind='unverified_slope'))
 def test_missing_model_keeps_actual_mapped_slope(self):
  self.assertEqual(self.classify(dict(potential_class=0,terrain_steep=True))['kind'],'unverified_slope')
 def test_missing_terrain_rectangle_is_not_a_slope(self):
  for steep in [None,False]:self.assertFalse(self.classify(dict(potential_class=0,terrain_steep=steep))['visible'])
 def test_flat_support_does_not_become_snow_or_safety(self):
  self.assertFalse(self.classify(dict(potential_class=1,terrain_steep=False))['visible'])
 def test_input_not_mutated(self):
  self.c.eval('const p={potential_class:2,terrain_steep:true,forecast_hs_cm:[0,0,0,0]};const before=JSON.stringify(p);potentialSurface(p)');self.assertTrue(self.c.eval('before===JSON.stringify(p)'))
