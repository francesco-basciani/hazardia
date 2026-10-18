import copy,unittest
from hazardia.decision.research_fixture import problem
from hazardia.decision.fire_ideal import POLICY,validate_input
from hazardia.decision.problem import validate
from hazardia.decision.verifier import verify,losses
from hazardia.io import HazardError

def fixture():
 p=problem({'FIRE':dict(job_id='job-fixture',hazard='FIRE',sha256='a'*64,valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-13T14:00:00Z',weather_hash='b'*64,qualification='UNQUALIFIED_RESEARCH')},'FIRE',2)
 p.update(schema_version='0.6.0',mode='RESEARCH_IDEAL',policy=copy.deepcopy(POLICY))
 for r in p['resources']:r['category']='waterline_action';r['record']['payload'].update(skills=['FIRE_SUPPRESSION'],equipment=['waterline_action'])
 for o in p['options']:o['effect']='IDEAL_ASSET_COVERAGE'
 return p
class IdealTests(unittest.TestCase):
 def test_versioned_policy_and_units(self):
  p=fixture();validate(p);self.assertIn('priority',losses(p,[])['unit']);self.assertEqual(verify(p,[p['options'][0]['id']])['status'],'VALIDATED_FOR_SIMULATION');self.assertFalse(verify(p,[])['operationally_approvable'])
 def test_duplicate_target_rejected(self):
  p=fixture();self.assertIn('DUPLICATE_TARGET',{x['id'] for x in verify(p,[o['id'] for o in p['options']])['rules']})
 def test_unavailable_and_unknown_effect_rejected(self):
  p=fixture();p['resources'][0]['record']['payload']['maintenance']='UNAVAILABLE';self.assertEqual(verify(p,[p['options'][0]['id']])['status'],'INVALID');p=fixture();p['options'][0]['effect']='PHYSICAL_EFFECT';self.assertIn('EFFECT',{x['id'] for x in verify(p,[p['options'][0]['id']])['rules']})
 def test_policy_cannot_claim_people(self):
  p=fixture();p['policy']['loss_unit']='people';self.assertEqual(verify(p,[])['status'],'INVALID')
 def test_bad_inputs_classified(self):
  for body in [[],{},dict(job_id='bad')]:
   with self.assertRaises(HazardError):validate_input(body)
  with self.assertRaises(HazardError):validate([])

 def test_multi_day_activation_is_explicit_and_bounded(self):
  body=dict(job_id='job-'+'a'*32,fleet=[dict(id='u1',category='helicopter',available=True,arrival_minutes=1440)],weights=dict(hospital=5,school=3,fire_station=3,residential=2,settlement=2),robust=.5,assumptions_confirmed=True)
  validate_input(body)
  for invalid in [-1,4320,float('nan')]:
   bad=copy.deepcopy(body);bad['fleet'][0]['arrival_minutes']=invalid
   with self.assertRaises(HazardError):validate_input(bad)

 def test_queued_request_has_independent_deadline(self):
  import tempfile,threading,time
  from pathlib import Path
  from types import SimpleNamespace
  from unittest.mock import patch
  from hazardia.web.fire_ideal_service import submit
  from hazardia.io import load
  body=dict(job_id='job-'+'a'*32,fleet=[dict(id='u1',category='waterline_action',available=True,arrival_minutes=0)],weights=dict(hospital=5,school=3,fire_station=3,residential=2,settlement=2),robust=1,assumptions_confirmed=True)
  with tempfile.TemporaryDirectory() as root:
   app=SimpleNamespace(root=Path(root),state=Path(root),lock=threading.Lock(),results={},capacity=threading.BoundedSemaphore(4),store=SimpleNamespace(get=lambda _:dict(state='SUCCEEDED')),pool=SimpleNamespace(submit=lambda fn:None))
   with patch('hazardia.web.fire_ideal_service.DEADLINE_S',.02):accepted=submit(app,body)
   limit=time.monotonic()+3
   while not (Path(root)/(accepted['id']+'-input')/'deadline.json').exists() and time.monotonic()<limit:time.sleep(.01)
   self.assertEqual(app.results[accepted['id']]['status'],'TIMEOUT_UNPROVEN');self.assertFalse(app.results[accepted['id']]['operationally_approvable']);self.assertTrue((Path(root)/(accepted['id']+'-input')/'deadline.json').exists())
