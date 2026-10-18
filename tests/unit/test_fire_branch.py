"""Synthetic admission checks: no model/data acquisition in these tests."""
import tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from hazardia.io import HazardError
from hazardia.web.dynamic_fire import DynamicFire
class BranchAdmissionTests(unittest.TestCase):
 def app(self,p,state='ERROR'):
  return SimpleNamespace(state=Path(p),store=SimpleNamespace(get=lambda _:dict(state=state)))
 def test_bad_identity_or_fields_rejected(self):
  with tempfile.TemporaryDirectory() as p:
   service=DynamicFire(self.app(p))
   for body in [{},dict(job_id='../x',input={}),dict(job_id='job-'+'a'*32,input={},extra=1)]:
    with self.assertRaises(HazardError):service.submit_branch(body)
 def test_unfinished_parent_rejected(self):
  with tempfile.TemporaryDirectory() as p:
   service=DynamicFire(self.app(p));body=dict(job_id='job-'+'a'*32,input=dict(hours=3,seed=1,moisture_percent=10,weather_source='FORECAST',weather_changes=[],resources=[],ignitions=[dict(id='i',point=[42,13],at_minutes=0)]))
   with self.assertRaises(HazardError) as e:service.submit_branch(body)
   self.assertEqual(e.exception.code,'DEPENDENCY_UNAVAILABLE');self.assertEqual(list(service.base.iterdir()),[])
