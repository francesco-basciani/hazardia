import copy,tempfile,unittest
from hazardia.web.fire_workspace import FireWorkspace
from hazardia.io import HazardError
class WorkspaceTests(unittest.TestCase):
 def body(self):
  return dict(revision=0,scenarios=[dict(id='s1',name='Scenario',input=dict(ignitions=[dict(id='i',point=[42.35,13.38],at_minutes=0)],hours=3,seed=1729,moisture_percent=10,resources=[],weather_source='HISTORICAL',weather_changes=[]),job_id=None,submitted_input=None)])
 def test_revision_and_reopen(self):
  with tempfile.TemporaryDirectory() as root:
   store=FireWorkspace(root);b=self.body();self.assertEqual(store.read()['scenarios'],[]);r=store.save(b);self.assertEqual(r['revision'],1);self.assertEqual(FireWorkspace(root).read(),r)
   with self.assertRaises(HazardError):store.save(b)
 def test_many_scenarios_and_unique_ids(self):
  with tempfile.TemporaryDirectory() as root:
   b=self.body();b['scenarios']=[dict(copy.deepcopy(b['scenarios'][0]),id='s'+str(i)) for i in range(12)];self.assertEqual(len(FireWorkspace(root).save(b)['scenarios']),12)
   b['scenarios'][1]['id']='s0'
   with self.assertRaises(HazardError):FireWorkspace(root).save(b)
 def test_invalid_job_not_saved(self):
  with tempfile.TemporaryDirectory() as root:
   b=self.body();b['scenarios'][0]['job_id']='../bad'
   with self.assertRaises(HazardError):FireWorkspace(root).save(b)
   self.assertEqual(FireWorkspace(root).read()['revision'],0)

 def test_empty_draft_allowed_but_not_submitted(self):
  from hazardia.firelab import validate
  with tempfile.TemporaryDirectory() as root:
   b=self.body();b['scenarios'][0]['input']['ignitions']=[]
   self.assertEqual(FireWorkspace(root).save(b)['scenarios'][0]['input']['ignitions'],[])
   with self.assertRaises(HazardError):validate(b['scenarios'][0]['input'])
   b['revision']=1;b['scenarios'][0]['submitted_input']=copy.deepcopy(b['scenarios'][0]['input'])
   with self.assertRaises(HazardError):FireWorkspace(root).save(b)
