import datetime as dt,unittest,json,tempfile,time
from pathlib import Path
from unittest.mock import patch
from hazardia.ingest.hydrometers import HydrometerStore
from hazardia.io import HazardError
from hazardia.ingest.hydrometers import normalize,moment
NOW=dt.datetime(2026,10,26,12,tzinfo=dt.timezone.utc)
REGISTRY=[dict(id_network='PIE',station_code='099',lat=45.3,lng=7.9,name='CANDIA LAGO',river_name='LAGO DI CANDIA',hydrometric_zero='')]
def payload(value=-.15,date='2026-10-24T22:00:00+02:00'):
 return dict(total_pages=1,total_items=1,data=[dict(id_network='PIE',station_code='099',date=date,hydrometric_level=value)])
class HydrometerTests(unittest.TestCase):
 def test_negative_height_unknown_datum_and_old_time_preserved(self):
  v=normalize(REGISTRY,payload(),NOW);p=v['features'][0]['properties'];self.assertEqual(p['level_m'],-.15);self.assertIsNone(p['gauge_zero']);self.assertEqual(p['at'],'2026-10-24T20:00:00Z');self.assertEqual(p['freshness'],'STALE');self.assertFalse(v['coupled_to_models']);self.assertIn('NOT_FLOOD',p['qualification'])
 def test_no_naive_time_and_no_future_observation(self):
  with self.assertRaises(ValueError):moment('2026-10-24T22:00:00')
  self.assertEqual(normalize(REGISTRY,payload(date='2026-10-27T12:00:00Z'),NOW)['features'],[])
 def test_null_and_nan_are_not_zero(self):
  for value in [None,float('nan'),True]:self.assertEqual(normalize(REGISTRY,payload(value),NOW)['features'],[])
 def test_truncation_rejected(self):
  for update in [dict(total_pages=2),dict(data=None),dict(total_items=3)]:
   p=payload();p.update(update)
   with self.assertRaises(ValueError):normalize(REGISTRY,p,NOW)
 def test_invalid_coordinate_is_not_a_station(self):
  self.assertEqual(normalize([dict(REGISTRY[0],lng=180.5)],payload(),NOW)['features'],[])

 def wait(self,store):
  for _ in range(100):
   value=store.snapshot()
   if not value['busy']:return value
   time.sleep(.01)
  self.fail('Hydrometer worker did not complete')
 def test_async_archive_preserves_old_date_and_survives_source_failure(self):
  class Frozen(dt.datetime):
   @classmethod
   def now(cls,tz=None):return NOW
  calls=[]
  def fetch(url):
   calls.append(url);return json.dumps(REGISTRY if url.endswith('pie_anag') else payload()).encode()
  with tempfile.TemporaryDirectory() as tmp,patch('hazardia.ingest.hydrometers.dt.datetime',Frozen):
   store=HydrometerStore(tmp,fetch=fetch);store.refresh();first=self.wait(store)
   self.assertEqual(first['data']['features'][0]['properties']['freshness'],'STALE');self.assertEqual(len(calls),3)
   store.refresh();self.assertEqual(len(calls),3)
   (Path(tmp)/'attempts.json').write_text(json.dumps([time.time()-7200]))
   def fail(url):raise TimeoutError('source unavailable')
   store.fetch=fail;store.refresh();last=self.wait(store)
   self.assertEqual(last['data'],first['data']);self.assertIn('unavailable',last['error'])
 def test_daily_budget_blocks_before_io(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=HydrometerStore(tmp,fetch=lambda url:self.fail('No new source requests'))
   (Path(tmp)/'attempts.json').write_text(json.dumps([time.time()-7200]*4))
   with self.assertRaises(HazardError):store.refresh()
