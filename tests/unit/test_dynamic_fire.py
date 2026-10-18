import unittest,tempfile,json
from pathlib import Path
import numpy as np
from hazardia.fire_forcing import hourly_moisture,SpatialForcing
from hazardia.firelab import validate
from hazardia.io import HazardError
class DynamicForcingTests(unittest.TestCase):
 def test_rain_wets_and_hot_dry_weather_drives_drying(self):
  dry=hourly_moisture(np.array([20.]),30.,15.,20.,0.);wet=hourly_moisture(np.array([20.]),30.,15.,20.,5.)
  self.assertLess(dry[0],20);self.assertGreater(wet[0],dry[0]);self.assertGreater(wet[0],20)
 def test_humidity_changes_moisture_without_substituting_relative_humidity(self):
  low=hourly_moisture(np.array([16.3]),20.,20.,10.,0.);high=hourly_moisture(np.array([16.3]),20.,95.,10.,0.)
  self.assertLess(low[0],high[0]);self.assertNotEqual(high[0],95)
 def test_missing_inputs_never_become_dry_fuel(self):
  with self.assertRaises(ValueError):hourly_moisture(np.array([16.3]),np.nan,50.,10.,0.)
 def test_invalid_humidity_and_negative_rain(self):
  for rh,rain in [(101,0),(50,-1)]:
   with self.assertRaises(ValueError):hourly_moisture(np.array([16.3]),20.,rh,10.,rain)
 def test_spatial_interpolation_and_rotation_are_finite(self):
  grid=dict(shape=[2,2],transform=[30,0,414000,0,-30,4700000],crs='EPSG:32633');field=dict(lats=[40,45],lons=[10,16]);s=SpatialForcing(grid,field);r=dict(u=[1,3,1,3],v=[0,0,0,0]);speed,direction=s.wind(r)
  self.assertEqual(speed.shape,(2,2));self.assertTrue(np.isfinite(direction).all());self.assertGreater(float(speed.max()),float(speed.min()));self.assertTrue((speed>3.6).all());self.assertTrue(np.allclose(direction,(270-s.convergence)%360,atol=.01))
 def test_weather_outside_domain_rejected(self):
  with self.assertRaises(HazardError):SpatialForcing(dict(shape=[2,2],transform=[30,0,414000,0,-30,4700000],crs='EPSG:32633'),dict(lats=[0,1],lons=[0,1]))
 def test_dynamic_parameters_versioned(self):
  b=dict(ignitions=[dict(id='i',point=[42.48,13.94],at_minutes=0)],hours=3,seed=1,moisture_percent=10,resources=[],weather_source='FORECAST',weather_changes=[],moisture_model='HFFMC_1977',forcing_id='map-weather-'+'a'*24)
  validate(b)
  for key,value in [('moisture_model','AUTO_MAGIC'),('forcing_id','../../file')]:
   bad=dict(b);bad[key]=value
   with self.assertRaises(HazardError):validate(bad)
