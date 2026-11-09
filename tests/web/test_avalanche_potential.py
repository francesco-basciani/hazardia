import copy,unittest
from hazardia.web.avalanche_potential import assess

def snow():return dict(id='IT1',factor_class=1,forecast_hs_max_cm=8,forecast_hs_cm=[0,2,4,8],slope_deg=5,elevation_m=1700,max_net_swe_increase_kg_m2=4,liquid_water_max_kg_m2=.1,air_temperature_min_c=-4,air_temperature_max_c=3)
def ground():return dict(id='GS1',model_sample_id='IT1',terrain_steep=True,cover='Prateria',soil_association='Associazione A/B',substrate='Calcareo',soil_source_scale=250000)

class PotentialTests(unittest.TestCase):
 def test_subgrid_steepness_does_not_use_flat_column_as_safety(self):
  s=snow();p=assess(s,ground());self.assertEqual(p['potential_class'],6);self.assertEqual(p['model_sample_slope_deg'],5);self.assertEqual(p['id'],'GS1');self.assertEqual(p['model_sample_id'],'IT1');self.assertEqual(s['factor_class'],1)
 def test_temperature_and_ground_are_explicit_without_friction_guess(self):
  p=assess(snow(),ground());text=' '.join(p['potential_reasons']);self.assertIn('sopra0°C',text);self.assertIn('prativo',text);self.assertIn('non parametro di attrito',text);self.assertIsNone(p['release_probability']);self.assertIsNone(p['hazard_grade'])
 def test_missing_soil_retained_without_setting_zero(self):
  g=ground();g.update(soil_association=None,substrate=None);p=assess(snow(),g);self.assertTrue(any('Suolo' in s for s in p['potential_missing']));self.assertEqual(p['potential_class'],6)
 def test_no_modeled_snow_does_not_exclude_snow_on_local_peaks(self):
  s=snow();s['forecast_hs_max_cm']=0;p=assess(s,ground());self.assertEqual(p['potential_class'],2);self.assertIn('non verificata',' '.join(p['potential_reasons']))
 def test_missing_model_or_terrain_is_incomplete(self):
  s=snow();s['factor_class']=0;self.assertEqual(assess(s,ground())['potential_class'],0)
  g=ground();g['terrain_steep']=None;self.assertEqual(assess(snow(),g)['potential_class'],0)
 def test_bosco_is_not_automatic_protection(self):
  g=ground();g['cover']='Copertura arborea';p=assess(snow(),g);self.assertEqual(p['potential_class'],6);self.assertIn('nessuna riduzione automatica',' '.join(p['potential_reasons']))
 def test_other_terrain_does_not_exclude_arrival_from_above(self):
  g=ground();g['terrain_steep']=False;p=assess(snow(),g);self.assertEqual(p['potential_class'],1);self.assertIn('arrivi da monte',' '.join(p['potential_reasons']))

class EnrichmentTests(unittest.TestCase):
 def make_context(self,directory):
  import json,gzip,hashlib
  from pathlib import Path
  directory=Path(directory);g=ground();g['local_sample_id']='GSL01';value=dict(schema='hazardia.avalanche-terrain-context/1.0',metadata={},features=[dict(type='Feature',properties=g,geometry=dict(type='Polygon',coordinates=[[[13,42],[14,42],[14,43],[13,42]]]))]);raw=json.dumps(value).encode()
  with gzip.open(directory/'terrain-context.json.gz','wb') as stream:stream.write(raw)
  (directory/'terrain-manifest.json').write_text(json.dumps(dict(sha256=hashlib.sha256(raw).hexdigest())))
 def data(self):return dict(features=[dict(properties=snow(),geometry=dict(type='Polygon',coordinates=[[[13,42],[14,42],[14,43],[13,42]]]))],version='a'*64,metadata=dict(reference_utc='2026-10-29T21:00:00Z',weather_run_utc='2026-10-29T18:00:00Z'))
 def test_local_profile_same_cycle_and_missing_is_not_imputed(self):
  import tempfile,json
  from pathlib import Path
  from hazardia.web.avalanche_potential import enrich
  with tempfile.TemporaryDirectory() as temp:
   self.make_context(temp);local=snow();local.update(id='GSL01',forecast_hs_max_cm=25)
   value=dict(reference_utc='2026-10-29T21:00:00Z',weather_run_utc='2026-10-29T18:00:00Z',models=dict(GSL01=local));path=Path(temp)/'local-forecasts.json';path.write_text(json.dumps(value))
   p=enrich(self.data(),temp)['potential_areas'][0]['properties'];self.assertEqual(p['model_sample_id'],'GSL01');self.assertEqual(p['forecast_hs_max_cm'],25)
   value['models']['GSL01'].update(factor_class=0,forecast_hs_max_cm=None,forecast_hs_cm=None);path.write_text(json.dumps(value));p=enrich(self.data(),temp)['potential_areas'][0]['properties'];self.assertEqual(p['potential_class'],0);self.assertIsNone(p['forecast_hs_cm'])
   value['reference_utc']='2026-10-29T22:00:00Z';path.write_text(json.dumps(value));p=enrich(self.data(),temp)['potential_areas'][0]['properties'];self.assertEqual(p['potential_class'],0);self.assertEqual(p['local_profile_status'],'LOCAL_PROFILE_MISSING')
 def test_corrupt_or_absent_context_is_explicit_missing(self):
  import tempfile
  from hazardia.web.avalanche_potential import enrich
  with tempfile.TemporaryDirectory() as temp:
   d=enrich(self.data(),temp);self.assertEqual(d['potential_areas'][0]['properties']['potential_class'],0);self.assertEqual(d['metadata']['potential_context_status'],'MISSING_OR_INVALID_TERRAIN_CONTEXT')

class NationalGroundTests(unittest.TestCase):
 def national(self):
  return dict(id='IT1-native1',model_sample_id='IT1',terrain_steep=True,cover='Prateria',soil_association='SoilGrids WRB stimato: Leptosols, Cambisols',substrate='ISPRA litologie nel supporto: A1 Calcari; B1 Marne',soil_support_m=1000,soil_missing_samples=2,substrate_missing_samples=0,ground_support_samples=10,ground_status='NATIONAL_GROUND_PARTIAL_OR_MISSING')
 def test_partial_soil_does_not_become_complete_or_mechanical_friction(self):
  p=assess(snow(),self.national());self.assertTrue(any('2/10' in s for s in p['potential_missing']));self.assertIn('campioni1km',' '.join(p['potential_reasons']));self.assertNotIn('associazione1:250000',' '.join(p['potential_reasons']));self.assertEqual(p['potential_class'],6);self.assertIsNone(p['release_probability'])
 def test_missing_soil_does_not_discard_available_substrate(self):
  g=self.national();g['soil_association']=None;p=assess(snow(),g);self.assertTrue(any('Suolo cartografico mancante' in s for s in p['potential_missing']));self.assertFalse(any('Substrato cartografico mancante' in s for s in p['potential_missing']));self.assertIn('ISPRA',' '.join(p['potential_reasons']))
 def test_ground_types_do_not_invent_release_weights_or_safe_forest(self):
  g=self.national();g.update(soil_association='Andosols',substrate='Vulcaniti',cover='Copertura arborea');p=assess(snow(),g);self.assertEqual(p['potential_class'],6);self.assertIsNone(p['hazard_grade']);self.assertIn('nessuna riduzione automatica',' '.join(p['potential_reasons']))
