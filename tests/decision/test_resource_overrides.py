import copy,unittest
from hazardia.decision.resource_overrides import apply
from hazardia.io import HazardError
from hazardia.decision.research_fixture import problem
from hazardia.decision.verifier import verify
class ResourceOverrideTests(unittest.TestCase):
 def setup_problem(self):
  refs={'FIRE':dict(job_id='j',hazard='FIRE',sha256='a'*64,valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-13T14:00:00Z',weather_hash='b'*64,qualification='UNQUALIFIED_RESEARCH')}
  return problem(refs,'FIRE',1),[dict(id='unit-1',lat=42.36,lon=13.39,arrival_minutes=2,available=True)]
 def test_coordinates_and_baseline_arrival(self):
  p,r=self.setup_problem();before=p['options'][0]['benefit'].copy();apply(p,r);self.assertEqual(p['resources'][0]['record']['payload']['point_wgs84'],[13.39,42.36]);self.assertEqual(p['options'][0]['benefit'],before);self.assertEqual(verify(p,[p['options'][0]['id']])['status'],'VALIDATED_FOR_SIMULATION')
 def test_unavailable_and_late_are_inadmissible(self):
  for field,value in [('available',False),('arrival_minutes',11)]:
   p,r=self.setup_problem();r[0][field]=value;apply(p,r);self.assertEqual(verify(p,[p['options'][0]['id']])['status'],'INVALID')
 def test_negative_unknown_nonfinite_and_ids(self):
  for key,value in [('lat',91),('lon',float('nan')),('available','UNKNOWN'),('arrival_minutes',-1),('id','other')]:
   p,r=self.setup_problem();r[0][key]=value
   with self.assertRaises(HazardError):apply(p,r)
 def test_synthetic_delay_changes_effect_not_physical_type(self):
  p,r=self.setup_problem();r[0]['arrival_minutes']=8;apply(p,r);self.assertAlmostEqual(p['options'][0]['benefit']['nominal'],1.5);self.assertEqual(p['options'][0]['effect'],'IMPACT_ONLY')
