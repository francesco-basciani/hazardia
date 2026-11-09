import datetime as dt,gzip,hashlib,json,tempfile,time,unittest
from pathlib import Path
from hazardia.ingest.thermal import normalize,ThermalStore
from hazardia.io import HazardError
NOW=dt.datetime(2026,10,26,12,tzinfo=dt.timezone.utc)
HEADER='latitude,longitude,scan,track,acq_date,acq_time,satellite,confidence,version,frp\n'
RAW=(HEADER+'42.3,13.4,0.4,0.5,2026-10-26,0130,N20,nominal,2.0NRT,3.5\n').encode()
class ThermalTests(unittest.TestCase):
 def test_utc_native_values_and_semantics(self):
  value=normalize(RAW,NOW);p=value['features'][0]['properties'];self.assertEqual(p['at'],'2026-10-26T01:30:00Z');self.assertEqual(p['frp_mw'],3.5);self.assertEqual(value['features'][0]['geometry']['coordinates'],[13.4,42.3]);self.assertIn('NOT_CONFIRMED',p['qualification'])
 def test_bad_header_and_all_invalid_never_empty_success(self):
  for raw in [b'<html>error</html>',RAW.replace(b'3.5',b'nan'),RAW.replace(b'0130',b'2530'),RAW.replace(b'2026-10-26',b'2026-10-27')]:
   with self.subTest(raw=raw),self.assertRaises(ValueError):normalize(raw,NOW)
 def test_empty_valid_source_and_dedup(self):
  self.assertEqual(normalize(HEADER.encode(),NOW)['features'],[])
  self.assertEqual(len(normalize(RAW+RAW.splitlines()[1]+b'\n',NOW)['features']),1)
 def wait(self,store):
  for _ in range(100):
   value=store.snapshot('Europe')
   if not value['busy']:return value
   time.sleep(.01)
  self.fail('Worker timeout')
 def test_async_cache_immutable_source_and_quota(self):
  raw=RAW;calls=[]
  from unittest.mock import patch
  class Frozen(dt.datetime):
   @classmethod
   def now(cls,tz=None):return NOW
  with tempfile.TemporaryDirectory() as tmp,patch('hazardia.ingest.thermal.dt.datetime',Frozen):
   s=ThermalStore(tmp,fetch=lambda url:calls.append(url) or raw);s.refresh({'region':'Europe'});value=self.wait(s);self.assertEqual(value['status'],'AVAILABLE');self.assertFalse(value['data']['coupled_to_models']);self.assertEqual(len(calls),1)
   s.refresh({'region':'Europe'});self.assertEqual(len(calls),1)
   digest=value['data']['raw_sha256'];self.assertEqual(hashlib.sha256(gzip.decompress((Path(tmp)/(digest+'.csv.gz')).read_bytes())).hexdigest(),digest)
 def test_invalid_selection_never_fetches_and_failure_not_zero(self):
  with tempfile.TemporaryDirectory() as tmp:
   def fail(url):raise TimeoutError('upstream unavailable')
   s=ThermalStore(tmp,fetch=fail)
   for body in [{'region':'Global'},{'region':[]},{'region':{}},{'region':'Europe','url':'http://localhost'},{}]:
    with self.assertRaises(HazardError):s.refresh(body)
   s.refresh({'region':'Europe'});v=self.wait(s);self.assertEqual(v['status'],'MISSING');self.assertIn('unavailable',v['error']);self.assertIsNone(v['data'])
 def test_oversize_never_published(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=ThermalStore(tmp,fetch=lambda url:b'x'*(2*1024**2+1));s.refresh({'region':'Europe'});self.assertEqual(self.wait(s)['status'],'MISSING')

 def test_daily_quota_blocks_without_io(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=ThermalStore(tmp,fetch=lambda url:self.fail('Quota must prevent I/O'))
   (Path(tmp)/'attempts.json').write_text(json.dumps([dict(at=time.time()-7200,region='Europe')]*16))
   with self.assertRaises(HazardError):store.refresh({'region':'Europe'})
 def test_failed_refresh_retains_original_observations(self):
  from unittest.mock import patch
  class Frozen(dt.datetime):
   @classmethod
   def now(cls,tz=None):return NOW
  with tempfile.TemporaryDirectory() as tmp,patch('hazardia.ingest.thermal.dt.datetime',Frozen):
   store=ThermalStore(tmp,fetch=lambda url:RAW);store.refresh({'region':'Europe'});old=self.wait(store)['data']
   attempts=Path(tmp)/'attempts.json';attempts.write_text(json.dumps([dict(at=time.time()-7200,region='Europe')]))
   def fail(url):raise TimeoutError('upstream unavailable')
   store.fetch=fail;store.refresh({'region':'Europe'});value=self.wait(store)
   self.assertEqual(value['data'],old);self.assertIn('unavailable',value['error'])
