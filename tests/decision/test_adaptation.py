import unittest,tempfile
from hazardia.adaptation.control import ResearchControl,replay_forecast
from hazardia.adaptation.alerts import AlertBook
from hazardia.io import HazardError
class AdaptationTests(unittest.TestCase):
    def test_persistence_and_fresh_revision(self):
        with tempfile.TemporaryDirectory() as d:
            c=ResearchControl(d);c.action(dict(action='inject',fault='safety_unknown',expected_revision=0));self.assertEqual(c.vector()[0]['state'],'UNAVAILABLE')
            with self.assertRaises(HazardError):c.action(dict(action='recover',expected_revision=0))
            r=c.action(dict(action='recover',expected_revision=1));self.assertIsNotNone(r['positive_evidence']);self.assertEqual(ResearchControl(d).state,c.state)
    def test_alert_order_identity_and_lifecycle(self):
        b=AlertBook();f=replay_forecast(1);kwargs=dict(event_id='event',at=f['available_at'],predicted_exposure=45,threshold=35,effect_known=True,qualification='SYNTHETIC_RESEARCH');a=b.update(f,**kwargs);self.assertEqual(a,b.update(f,**kwargs));self.assertEqual(len(b.history),1)
        with self.assertRaises(HazardError):b.update(replay_forecast(0),**kwargs)
        f['payload']['members'][0]['weight']=None
        with self.assertRaises(HazardError):b.update(f,**kwargs)
        b.acknowledge(a['id'],a['at']);self.assertEqual(b.alerts[a['id']]['state'],'ACKNOWLEDGED');b.expire(a['valid_until']);self.assertEqual(b.alerts[a['id']]['state'],'EXPIRED')
    def test_critical_unknown_and_flood_isolation(self):
        with tempfile.TemporaryDirectory() as d:
            c=ResearchControl(d);c.action(dict(action='inject',fault='flood_worker',expected_revision=0));self.assertEqual(c.apply({'events':[{'hazard':'FIRE','id':'fire','region':'ABR-NORTH'}],'resources':[],'options':[]})['events'][0]['hazard'],'FIRE')
            with self.assertRaises(HazardError):c.apply({'events':[{'hazard':'FLOOD'}]})
            c.action(dict(action='inject',fault='safety_unknown',expected_revision=1))
            with self.assertRaises(HazardError):c.apply({})
