import json
import unittest
from pathlib import Path
try:
    import quickjs
except ImportError:
    quickjs = None

@unittest.skipUnless(quickjs, 'QuickJS required')
class ObservedSnowTests(unittest.TestCase):
    def setUp(self):
        self.js=quickjs.Context()
        self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-observations.js').read_text().replace('export ',''))
        self.now=1793390400000  # 2026-10-30T20:00Z

    def call(self,name,*args):
        return json.loads(self.js.eval('JSON.stringify('+name+'('+','.join(json.dumps(x) for x in args)+'))'))

    def test_missing_never_recent(self):
        self.assertEqual(self.call('observationState',None,self.now),'MISSING')

    def test_cloudy_scene_can_be_recent_but_not_snow(self):
        area=dict(observed_from='2026-10-30T09:00Z',observed_at='2026-10-30T09:01Z')
        product=dict(areas=[dict(area,id='GS')],units={'p':dict(area='GS',snow_pixels=0,unknown_pixels=100)})
        result=self.call('observationFor',product,dict(id='p',forecast_hs_cm=[0,20,30,40]),self.now)
        self.assertEqual(result['state'],'RECENT');self.assertFalse(result['conflict']);self.assertEqual(result['unit']['snow_pixels'],0)

    def test_stale_and_future_are_not_current(self):
        for time,expected in [('2026-10-29T10:00Z','STALE'),('2026-10-31T10:00Z','INVALID_TIME'),('bogus','INVALID_TIME')]:
            self.assertEqual(self.call('observationState',dict(observed_from=time,observed_at=time),self.now),expected)

    def test_oldest_time_controls_mosaic_freshness(self):
        self.assertEqual(self.call('observationState',dict(observed_from='2026-10-28T10:00Z',observed_at='2026-10-30T10:00Z'),self.now),'STALE')

    def test_terrain_mismatch_rejected(self):
        p=dict(schema='hazardia.observed-snow/1.0',assimilated=False,terrain_version='abc',areas=[],units={})
        self.assertTrue(self.call('compatibleObservations',p,'native:abc:local'))
        self.assertFalse(self.call('compatibleObservations',p,'native:other:local'))
        p['assimilated']=True;self.assertFalse(self.call('compatibleObservations',p,'native:abc:local'))

    def test_model_zero_does_not_erase_observed_snow(self):
        p=dict(areas=[dict(id='GS',observed_from='2026-10-30T10:00Z',observed_at='2026-10-30T10:00Z')],units={'p':dict(area='GS',snow_pixels=5)})
        self.assertTrue(self.call('observationFor',p,dict(id='p',forecast_hs_cm=[0,0,0,0]),self.now)['conflict'])

    def test_snow_only_not_dynamic_instability(self):
        self.assertEqual(self.call('forecastEvidence',dict(potential_class=3)),'MORPHOLOGY_AND_MODELED_SNOW_ONLY')
        for code in [4,5,6]:self.assertEqual(self.call('forecastEvidence',dict(potential_class=code)),'MODELED_LOADING_OR_WATER')
        self.assertEqual(self.call('forecastEvidence',dict(potential_class=0)),'MISSING')

    def test_no_mutation(self):
        self.js.eval('const p={id:"x",forecast_hs_cm:[0,1,2,3],potential_class:3};const original=JSON.stringify(p);observationFor(null,p);forecastEvidence(p)')
        self.assertTrue(self.js.eval('original===JSON.stringify(p)'))
