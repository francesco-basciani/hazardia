import copy,tempfile,unittest
from pathlib import Path
from hazardia.web.fire_exports import FireExports
from hazardia.io import HazardError
class ExportTests(unittest.TestCase):
 def body(self):return dict(scenarios=[dict(id='s1',name='Area triangolare',job_id=None,submitted_input=None,input=dict(ignitions=[],hours=3,seed=1729,moisture_percent=10,weather_source='FORECAST',weather_changes=[],resources=[dict(id='u1',category='waterline_action',effect='fuel_removal',at_minutes=30,area=[[42.4,13.7],[42.41,13.71],[42.4,13.72]])]))])
 def test_roundtrip_keeps_unsaved_triangle_and_no_workspace(self):
  with tempfile.TemporaryDirectory() as root:
   store=FireExports(root);body=self.body();receipt=store.create(body);self.assertEqual(store.read(receipt['id']),body);self.assertFalse((Path(root)/'fire-workspace').exists());self.assertEqual(store.create(copy.deepcopy(body)),receipt)
 def test_bad_payload_rejected_before_write(self):
  with tempfile.TemporaryDirectory() as root:
   for body in [{},dict(self.body(),revision=1),dict(scenarios=[dict(self.body()['scenarios'][0],job_id='../escape')])]:
    with self.assertRaises(HazardError):FireExports(root).create(body)
   self.assertFalse((Path(root)/'fire-exports').exists())
 def test_bound_preserves_existing_files_and_duplicate(self):
  with tempfile.TemporaryDirectory() as root:
   store=FireExports(root);first=store.create(self.body())
   for i in range(1,32):
    b=self.body();b['scenarios'][0]['name']='Case '+str(i);store.create(b)
   b=self.body();b['scenarios'][0]['name']='Overflow'
   with self.assertRaises(HazardError):store.create(b)
   self.assertEqual(len(list(store.directory.glob('*.json'))),32);self.assertEqual(store.create(self.body()),first)
 def test_read_rejects_traversal_and_missing(self):
  with tempfile.TemporaryDirectory() as root:
   for key in ['../workspace','f'*32]:
    with self.assertRaises(HazardError):FireExports(root).read(key)
