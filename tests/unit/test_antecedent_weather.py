import datetime as dt,unittest,tempfile
from unittest.mock import patch
from pathlib import Path
import numpy as np
from hazardia.ingest.antecedent_weather import history_rows,acquire
from hazardia.fire_forcing import initialize_moisture
from hazardia.firelab import validate
from hazardia.io import HazardError
class AntecedentTests(unittest.TestCase):
 def field(self):
  begin=dt.datetime(2026,10,11,16,tzinfo=dt.timezone.utc);records=[]
  for i in range(169):records.append(dict(at=(begin+dt.timedelta(hours=i)).isoformat().replace('+00:00','Z'),u=[1]*4,v=[0]*4,temperature=[20]*4,humidity=[30,80,30,80],precipitation=[0]*4))
  return dict(lats=[40,45],lons=[10,16],records=records)
 def test_only_168_prior_hours(self):
  f=self.field();rows=history_rows(f,'2026-10-18T16:00:00Z');self.assertEqual(len(rows),168);self.assertEqual(rows[-1]['at'],'2026-10-18T15:00:00Z')
 def test_missing_hour_rejected(self):
  f=self.field();f['records'].pop(4)
  with self.assertRaisesRegex(HazardError,'168h'):history_rows(f,'2026-10-18T16:00:00Z')
 def test_native_grid_has_spatial_variation(self):
  g=dict(shape=[2,2],transform=[30,0,414000,0,-30,4700000],crs='EPSG:32633');m=initialize_moisture(g,self.field(),'2026-10-18T16:00:00Z');self.assertEqual(m.shape,(2,2));self.assertTrue(np.isfinite(m).all());self.assertGreater(float(m.max()),float(m.min()))
 def test_later_weather_cannot_affect_initialization(self):
  g=dict(shape=[2,2],transform=[30,0,414000,0,-30,4700000],crs='EPSG:32633');f=self.field();a=initialize_moisture(g,f,'2026-10-18T16:00:00Z');f['records'][-1]['precipitation']=[100]*4;self.assertTrue(np.array_equal(a,initialize_moisture(g,f,'2026-10-18T16:00:00Z')))
 def test_parameter_bounds_and_mode(self):
  b=dict(ignitions=[dict(id='i',point=[42,13],at_minutes=0)],hours=72,seed=1729,moisture_percent=10,resources=[],weather_source='FORECAST',weather_changes=[],moisture_model='HFFMC_1977',antecedent_hours=168,realizations=8);validate(b)
  for k,v in [('realizations',100),('antecedent_hours',24),('moisture_model','MANUAL'),('weather_source','HISTORICAL')]:
   with self.assertRaises(HazardError):validate(dict(b,**{k:v}))
 def acquisition_fixture(self):
  import io,json
  from test_map_weather import fixture,receipt
  from hazardia.ingest.map_weather import normalize
  field=normalize(fixture(),receipt());raw=fixture();times=[(dt.datetime(2026,10,11)+dt.timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M') for i in range(216)]
  for n in raw:
   keep=['time','wind_speed_10m','wind_direction_10m','temperature_2m','precipitation','relative_humidity_2m'];n['hourly_units']={k:v for k,v in n['hourly_units'].items() if k in keep};n['hourly']={k:times if k=='time' else [n['hourly'][k][0]]*216 for k in keep}
  class Response(io.BytesIO):
   status=200
   def geturl(self):return 'https://api.open-meteo.com/v1/forecast'
  return field,raw,lambda data:Response(json.dumps(data).encode())
 def test_acquisition_shared_budget_and_exact_cache(self):
  from hazardia.ingest.map_weather import MapWeatherStore
  field,raw,response=self.acquisition_fixture();calls=[]
  def opener(*a,**k):calls.append(1);return response(raw)
  with tempfile.TemporaryDirectory() as root:
   store=MapWeatherStore(root,opener=opener);a=acquire(store,field,'2026-10-18T16:00:00Z');b=acquire(store,field,'2026-10-18T16:00:00Z');self.assertEqual(a,b);self.assertEqual(calls,[1]);self.assertEqual(store.snapshot()['quota']['attempts_today'],1);self.assertIsNone(store.snapshot()['forecast'])
 def test_missing_response_and_rate_limit_do_not_fallback(self):
  from hazardia.ingest.map_weather import MapWeatherStore
  field,raw,response=self.acquisition_fixture();raw.pop()
  with tempfile.TemporaryDirectory() as root:
   store=MapWeatherStore(root,opener=lambda *a,**k:response(raw))
   with self.assertRaises(HazardError):acquire(store,field,'2026-10-18T16:00:00Z')
   with self.assertRaisesRegex(HazardError,'65s'):acquire(store,field,'2026-10-18T16:00:00Z')
 def test_daily_quota_never_bypassed(self):
  from hazardia.ingest.map_weather import MapWeatherStore
  field,_,_=self.acquisition_fixture()
  with tempfile.TemporaryDirectory() as root:
   store=MapWeatherStore(root,opener=lambda *a,**k:self.fail('Network called after quota'));now=store.clock()
   with store.connect() as db:
    for i in range(48):db.execute('INSERT INTO attempts VALUES(?)',(now-now%86400+i,))
   with self.assertRaisesRegex(HazardError,'daily budget'):acquire(store,field,'2026-10-18T16:00:00Z')
 def test_corrupt_history_cache_is_not_reused(self):
  from hazardia.ingest.map_weather import MapWeatherStore
  field,raw,response=self.acquisition_fixture()
  with tempfile.TemporaryDirectory() as root:
   store=MapWeatherStore(root,opener=lambda *a,**k:response(raw));acquire(store,field,'2026-10-18T16:00:00Z');next(Path(root).glob('raw-*.json')).write_text('[]')
   with self.assertRaisesRegex(HazardError,'integrity'):acquire(store,field,'2026-10-18T16:00:00Z')
