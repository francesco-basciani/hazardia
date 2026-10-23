import datetime as dt,json,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from hazardia.web.radar_service import RadarService
from hazardia.io import HazardError
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.app=SimpleNamespace(state=Path(self.tmp.name),root=Path(self.tmp.name));self.r=RadarService(self.app)
 def test_utc_and_period_are_explicit(self):
  at='2026-10-23T09:04:59Z';expected=int(dt.datetime(2026,10,23,9,tzinfo=dt.timezone.utc).timestamp());self.assertEqual(self.r.time_key(at),expected)
  for at in ['today','2026-10-23T09:00:00',None]:
   with self.assertRaises(HazardError):self.r.time_key(at)
 def test_future_never_fetches_or_substitutes_latest(self):
  future=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=1)).isoformat().replace('+00:00','Z');result=self.r.refresh(future);self.assertEqual(result['status'],'OUTSIDE_VALIDITY');self.assertIsNone(result['data']);self.assertFalse((self.r.root/'attempts.json').exists())
 def test_cached_observation_matches_selected_interval(self):
  at='2026-10-23T09:00:00Z';key=self.r.time_key(at);p=self.r.root/str(key);p.mkdir();(p/'result.json').write_text(json.dumps({'at':at,'kind':'OBSERVATION','units':'mm/h'}));self.assertEqual(self.r.snapshot('2026-10-23T09:04:59Z')['data']['at'],at);self.assertIsNone(self.r.snapshot('2026-10-23T09:05:00Z')['data'])
 def test_asset_path_cannot_escape_cache(self):
  with self.assertRaises(HazardError):self.r.image('../anything','rain.png')
  with self.assertRaises(HazardError):self.r.image('1','source.tif')
 def test_rate_limit_does_not_launch_worker(self):
  at=dt.datetime.fromtimestamp(time.time()-600,dt.timezone.utc).isoformat().replace('+00:00','Z');(self.r.root/'attempts.json').write_text(json.dumps([time.time()]));value=self.r.refresh(at);self.assertIn('limitata',value['error']);self.assertIsNone(self.r.active)
