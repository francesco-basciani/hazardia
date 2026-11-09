import datetime as dt,json,tempfile,time,threading,unittest
from pathlib import Path
from hazardia.web.quake_cache import QuakeCache,stamp,epoch
from hazardia.web.observed_layers import earthquake_features
from hazardia.io import HazardError
HEADER='#EventID|Time|Latitude|Longitude|Depth/Km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|MagAuthor|EventLocationName|EventType\n'
def raw(now,mag=.4,event='1'):
 return (HEADER+f'{event}|{stamp(now-3600)}|42.4|13.5|8|INGV|x|x|1|ML|{mag}|INGV|Test|earthquake\n').encode()
class CacheTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.now=dt.datetime(2026,10,26,15,0,tzinfo=dt.timezone.utc).timestamp();self.calls=[]
  self.service=QuakeCache(self.root,lambda u:(self.calls.append(u) or raw(self.now)),earthquake_features,lambda:self.now)
  self.body=dict(bounds=[13,42,14,43],days=7,min_magnitude=0,provider='ingv')
 def tearDown(self):self.temp.cleanup()
 def wait(self,r):
  for _ in range(200):
   v=self.service.snapshot(r['request_id']) if r['status']=='LOADING' else r
   if v['status']!='LOADING':return v
   time.sleep(.005)
  self.fail('worker timeout')
 def get(self,**changes):
  b=dict(self.body,**changes);return self.wait(self.service.prepare(b,b['bounds'],b['provider'],b['days'],b['min_magnitude']))
 def seed(self):return self.get()
 def test_provider_time_contract_preserves_utc(self):
  from urllib.parse import urlsplit,parse_qs
  for provider in ['ingv','usgs']:
   with self.subTest(provider=provider),tempfile.TemporaryDirectory() as root:
    calls=[]
    def source(url):
     q=parse_qs(urlsplit(url).query)
     for key in ['starttime','endtime']:
      value=q[key][0]
      if provider=='ingv' and value.endswith('Z'):raise ValueError('INGV rejects timezone suffix')
      parsed=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
      if parsed.tzinfo is None:parsed=parsed.replace(tzinfo=dt.timezone.utc)
      calls.append((key,parsed.timestamp()))
     return raw(self.now)
    self.service=QuakeCache(root,source,earthquake_features,lambda:self.now)
    result=self.get(provider=provider)
    self.assertEqual(result['status'],'READY')
    self.assertEqual(dict(calls),dict(starttime=self.now-7*86400,endtime=self.now))

 def test_national_snapshot_reused_for_area_magnitude_and_shorter_period(self):
  d=self.seed();self.assertEqual(d['bounds'],[6,35,19,48]);self.assertEqual(len(self.calls),1)
  for change in [dict(bounds=[8,37,18,47]),dict(min_magnitude=3),dict(days=1)]:self.assertEqual(self.get(**change)['status'],'READY')
  self.assertEqual(len(self.calls),1)
 def test_restart_reuses_persistent_snapshot_with_exhausted_quota(self):
  d=self.seed();self.now+=7200;quota=next(self.root.glob('*.quota'));quota.write_text('24')
  self.service=QuakeCache(self.root,lambda u:self.fail('No source request with quota'),earthquake_features,lambda:self.now)
  v=self.get();self.assertEqual(len(v['features']),1);self.assertEqual(v['quality']['cache_status'],'STALE');self.assertEqual(v['quality']['cache_reason'],'LOCAL_DAILY_QUOTA');self.assertEqual(quota.read_text(),'24');self.assertEqual(v['acquired_at'],d['acquired_at'])
 def test_incremental_overlap_replaces_id_and_preserves_prior_archive(self):
  d=self.seed();original=(self.root/(d['request_id']+'.json.gz')).read_bytes();self.now+=7200
  payload=raw(self.now,1.4)+raw(self.now,2.4,'2').split(b'\n',1)[1]
  self.service.fetch=lambda u:(self.calls.append(u) or payload)
  v=self.get();self.assertEqual(v['quality']['update_mode'],'INCREMENTAL_48H_REVISION_OVERLAP');self.assertEqual(len(v['features']),2);self.assertEqual(next(f for f in v['features'] if f['id']=='1')['properties']['magnitude'],1.4)
  self.assertEqual((self.root/(d['request_id']+'.json.gz')).read_bytes(),original);self.assertIn('starttime=2026-10-24',self.calls[-1])
 def test_source_error_retains_dated_cache(self):
  d=self.seed();self.now+=7200
  def fail(u):raise TimeoutError('offline')
  self.service.fetch=fail;v=self.get();self.assertEqual(v['status'],'READY');self.assertEqual(v['features'],d['features']);self.assertIn('UPDATE_FAILED',v['quality']['cache_reason']);self.assertEqual(v['acquired_at'],d['acquired_at'])
 def test_quota_without_covering_archive_is_error(self):
  (self.root/'2026-10-26.quota').write_text('24')
  with self.assertRaises(HazardError):self.get()
  self.assertFalse(self.calls)
 def test_missing_30_day_window_explicit_at_quota(self):
  self.seed();(self.root/'2026-10-26.quota').write_text('24');v=self.get(days=30)
  self.assertTrue(v['quality']['partial_window']);self.assertEqual(v['quality']['requested_days'],30);self.assertEqual(len(self.calls),1)
 def test_truncated_increment_is_not_merged(self):
  d=self.seed();self.now+=7200;self.service.fetch=lambda u:raw(self.now);self.service.parse=lambda r:(earthquake_features(r)[0],dict(limit_reached=True,skipped=0))
  v=self.get();self.assertEqual(v['features'],d['features']);self.assertIn('Truncated',v['quality']['cache_reason'])
 def test_full_reconciliation_after_week(self):
  self.seed();self.now+=8*86400;v=self.get();self.assertEqual(v['quality']['update_mode'],'FULL_WINDOW')
 def test_truncated_full_cache_remains_visible_at_quota(self):
  self.service.parse=lambda r:(earthquake_features(r)[0],dict(limit_reached=True,skipped=0))
  self.seed();(self.root/'2026-10-26.quota').write_text('24');v=self.get()
  self.assertEqual(v['status'],'READY');self.assertTrue(v['quality']['partial_window']);self.assertTrue(v['quality']['limit_reached'])
 def test_reserve_blocks_new_acquisition(self):
  from unittest.mock import patch
  from collections import namedtuple
  Disk=namedtuple('Disk','total used free')
  with patch('hazardia.web.quake_cache.shutil.disk_usage',return_value=Disk(10**10,10**10,1024)):
   with self.assertRaises(HazardError):self.get()
  self.assertFalse(self.calls)
 def test_concurrent_different_provider_never_gets_wrong_catalogue(self):
  gate=threading.Event()
  def fetch(u):gate.wait(2);return raw(self.now)
  self.service.fetch=fetch
  b=self.body
  try:
   r=self.service.prepare(b,b['bounds'],'ingv',7,0)
   other=dict(b,provider='usgs')
   with self.assertRaises(HazardError):self.service.prepare(other,other['bounds'],'usgs',7,0)
   self.assertEqual(self.service.prepare(b,b['bounds'],'ingv',7,0)['request_id'],r['request_id'])
  finally:gate.set()
  for _ in range(100):
   if not self.service.active:break
   time.sleep(.005)
if __name__=='__main__':unittest.main()
