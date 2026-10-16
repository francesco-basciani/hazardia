import copy,unittest
from hazardia.decision.research_fixture import problem
from hazardia.decision.problem import validate
from hazardia.decision.verifier import verify,losses

def fixture():
    refs={h:dict(job_id='fixture-'+h,hazard=h,sha256='a'*64,valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-13T14:00:00Z',weather_hash='b'*64,qualification='UNQUALIFIED_RESEARCH') for h in ['FIRE','FLOOD']};return problem(refs,'JOINT',4)
class Verifier(unittest.TestCase):
    def test_baseline_and_known_assignment(self):
        p=fixture();self.assertEqual(verify(p,[])['status'],'VALIDATED_FOR_SIMULATION');self.assertEqual(verify(p,[p['options'][0]['id']])['status'],'VALIDATED_FOR_SIMULATION');self.assertFalse(verify(p,[])['operationally_approvable'])
    def test_independent_rejects_double_booking(self):
        p=fixture();r=verify(p,[p['options'][0]['id'],p['options'][1]['id']]);self.assertIn('OVERBOOKING',{v['id'] for v in r['rules']})
    def test_unknown_resource_never_free(self):
        p=fixture();p['resources'][0]['record']['payload']['autonomy_h']=None;self.assertIn('UNKNOWN_SAFETY',{v['id'] for v in verify(p,[p['options'][0]['id']])['rules']})
    def test_unauthorized_closed_and_unsupported_effect(self):
        for key,value,rule in [('authorization',False,'AUTHORIZATION'),('road_open',None,'ROAD'),('effect','PHYSICAL_EFFECT','EFFECT')]:
            p=fixture();p['options'][0][key]=value;self.assertIn(rule,{v['id'] for v in verify(p,[p['options'][0]['id']])['rules']})
    def test_donor_and_consumables(self):
        p=fixture();p['regions'][0]['minimum_donor_reserve']=2;self.assertIn('DONOR_RESERVE',{v['id'] for v in verify(p,[p['options'][1]['id']])['rules']})
        p=fixture();p['options'][0]['fuel_l']=100;self.assertIn('CONSUMABLES',{v['id'] for v in verify(p,[p['options'][0]['id']])['rules']})
    def test_time_qualifications_effect_and_duplicate(self):
        for key,value,rule in [('maintenance','UNAVAILABLE','QUALIFICATION'),('skills',[],'QUALIFICATION'),('rest_hours',0,'TRAVEL_AUTONOMY_REST')]:
            p=fixture();p['resources'][0]['record']['payload'][key]=value;self.assertIn(rule,{v['id'] for v in verify(p,[p['options'][0]['id']])['rules']})
        p=fixture();oid=p['options'][0]['id'];self.assertEqual(verify(p,[oid,oid])['status'],'INVALID')
    def test_exposure_no_double_count_and_continuity(self):
        p=fixture();p['options'][0]['benefit']={'nominal':100,'stress':100};self.assertIn('DOUBLE_COUNT_EXPOSURE',{v['id'] for v in verify(p,[p['options'][0]['id']])['rules']})
        p=fixture();p['commitments']=[dict(option_id=p['options'][0]['id'])];self.assertIn('CONTINUITY',{v['id'] for v in verify(p,[])['rules']})
    def test_unknown_weights_use_worst_not_fake_expected(self):
        p=fixture()
        for w in p['scenarios']:w['weight']=None
        loss=losses(p,[]);self.assertIsNone(loss['expected']);self.assertEqual(loss['objective'],loss['worst'])
    def test_stale_products_and_invalid_numbers(self):
        p=fixture();p['events'][0]['product']['valid_until']='2024-07-13T12:00:00Z';self.assertEqual(verify(p,[])['status'],'INVALID')
        p=fixture();p['options'][0]['cost']=float('nan');self.assertEqual(verify(p,[])['status'],'INVALID')
