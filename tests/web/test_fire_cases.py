import tempfile,unittest,json,copy
from pathlib import Path
from hazardia.web.fire_cases import FireCases
from hazardia.web.fire_workspace import FireWorkspace
from hazardia.io import HazardError
class CaseTests(unittest.TestCase):
 def seed(self,root):
  p=Path(root)/'web-assets/fire-cases';p.mkdir(parents=True)
  s=dict(id='sample-scenario',name='Baseline',job_id=None,submitted_input=None,input=dict(ignitions=[],resources=[],hours=3,seed=1,moisture_percent=10,weather_source='FORECAST',weather_changes=[]))
  d=dict(id='sample',title='Prova',description='Ipotesi',qualification='RESEARCH',initial_hour=2,source_url='https://example.org/news',scenarios=[s]);(p/'sample.json').write_text(json.dumps(d));return d
 def test_opt_in_and_independent_revision(self):
  with tempfile.TemporaryDirectory() as root:
   self.seed(root);main=FireWorkspace(Path(root)/'web-state');cases=FireCases(root);before=main.read();self.assertFalse(cases.state.exists());self.assertEqual(len(cases.catalog()),1);self.assertFalse(cases.state.exists());r=cases.read('sample');self.assertEqual(r['revision'],1);self.assertEqual(r['case']['title'],'Prova');self.assertEqual(r['case']['initial_hour'],2);store=cases.workspace('sample');body={k:r[k] for k in ['revision','scenarios']};body['scenarios'][0]['name']='Edited';store.save(body);self.assertEqual(cases.read('sample')['scenarios'][0]['name'],'Edited');self.assertEqual(main.read(),before)
 def test_unknown_and_traversal_do_not_create_workspace(self):
  with tempfile.TemporaryDirectory() as root:
   self.seed(root);cases=FireCases(root)
   for ident in ['../sample','missing','/sample','Sample']:
    with self.assertRaises(HazardError):cases.read(ident)
   self.assertFalse(cases.state.exists())
 def test_invalid_seed_never_saved(self):
  with tempfile.TemporaryDirectory() as root:
   d=self.seed(root);d['scenarios'][0]['job_id']='../unsafe';(Path(root)/'web-assets/fire-cases/sample.json').write_text(json.dumps(d));cases=FireCases(root)
   with self.assertRaises(HazardError):cases.read('sample')
   self.assertFalse((cases.state/'sample/workspace.json').exists())

 def test_saved_plan_metadata_is_opt_in_validated_and_returned(self):
  from hazardia.decision.fire_priorities import DEFAULT_WEIGHTS
  with tempfile.TemporaryDirectory() as root:
   d=self.seed(root);body=dict(job_id='job-'+'a'*32,fleet=[dict(id='ground',category='waterline_action',available=True,arrival_minutes=15)],weights=DEFAULT_WEIGHTS,robust=.5,assumptions_confirmed=True)
   d['planning']=dict(decision_id='decision-'+'b'*32,evaluation_id='decision-'+'c'*32,request=body,duration_note='Disponibilità ipotetica fino alla fine; barriera persistente.')
   path=Path(root)/'web-assets/fire-cases/sample.json';path.write_text(json.dumps(d));self.assertEqual(FireCases(root).read('sample')['case']['planning'],d['planning'])
   for key,value in [('decision_id','../escape'),('evaluation_id',7),('duration_note','x'*1201),('request',dict(body,fleet=[]))]:
    bad=copy.deepcopy(d);bad['planning'][key]=value;path.write_text(json.dumps(bad))
    with self.assertRaises(HazardError):FireCases(root).definition('sample')
