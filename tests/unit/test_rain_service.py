import datetime as dt,gzip,hashlib,json,tempfile,threading,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from hazardia.web.rain_service import RainService
from hazardia.io import HazardError
class RainServiceTests(unittest.TestCase):
 def fixture(self,root):
  field=dict(id='wx',lats=list(range(9)),lons=list(range(9)),available_at=dt.datetime.now(dt.timezone.utc).isoformat(),records=[dict(at='2026-10-21T10:00:00Z')])
  weather=SimpleNamespace(snapshot=lambda:dict(status='FRESH',forecast=field))
  sources={'dpc':dict(issued_at='2026-10-20T13:00:00Z',source_url='https://example.org',products=[dict(day='2026-10-21',freshness='FRESH',valid_until='2026-10-21T22:00:00Z',url='/dpc-2026-10-21.geojson')])}
  snapshot=dict(id='snapshot-test',sources=sources)
  zones=dict(type='FeatureCollection',features=[dict(properties=dict(id='z',name='Zona',level=1),geometry={})])
  app=SimpleNamespace(state=Path(root),root=Path(root),map_weather=weather,attention=SimpleNamespace(snapshot=lambda:snapshot,layer=lambda *a:zones),capacity=threading.BoundedSemaphore(4),pool=SimpleNamespace(submit=Mock()))
  return RainService(app),app,snapshot
 def test_official_validity_and_no_new_network(self):
  with tempfile.TemporaryDirectory() as root:
   service,app,s=self.fixture(root);result=service.submit(dict(at='2026-10-21T10:00:00Z'));body=json.loads((service.root/result['id']/'request.json').read_text());self.assertEqual(body['official']['status'],'AVAILABLE');self.assertEqual(app.pool.submit.call_count,1)
 def test_expired_bulletin_withheld(self):
  with tempfile.TemporaryDirectory() as root:
   service,app,s=self.fixture(root);s['sources']['dpc']['products'][0]['freshness']='STALE'
   result=service.submit(dict(at='2026-10-21T10:00:00Z'));body=json.loads((service.root/result['id']/'request.json').read_text());self.assertEqual(body['official']['status'],'UNAVAILABLE')
 def test_future_issued_bulletin_not_backdated(self):
  with tempfile.TemporaryDirectory() as root:
   service,app,s=self.fixture(root);s['sources']['dpc']['issued_at']='2026-10-21T11:00:00Z'
   result=service.submit(dict(at='2026-10-21T10:00:00Z'));body=json.loads((service.root/result['id']/'request.json').read_text());self.assertEqual(body['official']['status'],'UNAVAILABLE')
 def test_stale_weather_and_unknown_hour_rejected(self):
  with tempfile.TemporaryDirectory() as root:
   service,app,s=self.fixture(root)
   with self.assertRaises(HazardError):service.submit(dict(at='2026-10-22T10:00:00Z'))
   app.map_weather.snapshot=lambda:dict(status='STALE',forecast={})
   with self.assertRaises(HazardError):service.submit(dict(at='2026-10-21T10:00:00Z'))
 def test_one_worker_and_deduplication(self):
  with tempfile.TemporaryDirectory() as root:
   service,app,s=self.fixture(root);a=service.submit(dict(at='2026-10-21T10:00:00Z'));b=service.submit(dict(at='2026-10-21T10:00:00Z'));self.assertEqual(a['id'],b['id']);self.assertEqual(app.pool.submit.call_count,1)
 def test_bad_id_and_input_rejected(self):
  with tempfile.TemporaryDirectory() as root:
   service,app,s=self.fixture(root)
   for body in [dict(at='2026-10-21T10:30:00Z'),dict(at='bad'),dict(at='2026-10-21T10:00:00Z',risk=3)]:
    with self.assertRaises((HazardError,ValueError)):service.submit(body)
   with self.assertRaises(HazardError):service.read('../x')
 def test_corrupt_result_never_served(self):
  with tempfile.TemporaryDirectory() as root:
   service,app,s=self.fixture(root);key='rain-'+'a'*24;dest=service.root/key;dest.mkdir();(dest/'result.json.gz').write_bytes(gzip.compress(b'{}'));(dest/'receipt.json').write_text(json.dumps(dict(raw_sha256={'result.json':'a'*64})))
   with self.assertRaises(HazardError):service.read(key)
