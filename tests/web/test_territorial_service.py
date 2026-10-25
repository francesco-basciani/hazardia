import json,tempfile,time,threading,unittest
from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from hazardia.web.territorial_service import TerritorialService
from hazardia.io import HazardError
class TerritorialStorageTests(unittest.TestCase):
 def fixture(self,root):
  root=Path(root);state=root/'web-state';state.mkdir();(root/'runtime-v2.json').write_text(json.dumps({'geo_python':'fixture-only'}));return SimpleNamespace(root=root,state=state,capacity=threading.BoundedSemaphore(2),pool=ThreadPoolExecutor(1))
 def worker(self,args,**kw):Path(args[-1]).write_text('{"features":[],"qualification":"SYNTHETIC_TEST_ONLY"}')
 def wait(self,service,key):
  for _ in range(100):
   value=service.read(key)
   if value['status']=='SUCCEEDED':return value
   time.sleep(.01)
  self.fail('Read model did not complete')
 def test_output_is_immutable_link_and_cache_does_not_reexecute(self):
  with tempfile.TemporaryDirectory() as d:
   app=self.fixture(d);service=TerritorialService(app)
   with patch('hazardia.web.territorial_service.subprocess.run',side_effect=self.worker) as worker:
    r=service.submit({'bounds':[13,42,13.1,42.1]});self.wait(service,r['id']);folder=service.root/r['id'];attempt=next(folder.glob('attempt-*.json'));self.assertEqual(attempt.stat().st_ino,(folder/'result.json').stat().st_ino);self.assertEqual(attempt.read_bytes(),(folder/'result.json').read_bytes());again=service.submit({'bounds':[13,42,13.1,42.1]});self.assertEqual(again['id'],r['id']);self.assertEqual(worker.call_count,1)
   app.pool.shutdown()
 def test_storage_reserve_blocks_new_but_keeps_cached_read_models(self):
  with tempfile.TemporaryDirectory() as d:
   app=self.fixture(d);service=TerritorialService(app);body={'bounds':[13,42,13.1,42.1]}
   with patch('hazardia.web.territorial_service.subprocess.run',side_effect=self.worker):r=service.submit(body);self.wait(service,r['id'])
   with patch('hazardia.web.territorial_service.os.statvfs',return_value=SimpleNamespace(f_bavail=0,f_frsize=4096)):
    self.assertEqual(service.submit(body)['status'],'SUCCEEDED')
    with self.assertRaises(HazardError) as error:service.submit({'bounds':[14,42,14.1,42.1]})
    self.assertEqual(error.exception.code,'STORAGE_RESERVE')
   app.pool.shutdown()
