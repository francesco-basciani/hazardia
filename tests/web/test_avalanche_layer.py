import copy
import datetime as dt
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from hazardia.web.avalanche_layer import SCHEMA, Snapshot, validate


def fixture():
    p=dict(id='test',release_probability=None,hazard_grade=None,factor_class=4,status='CONDITIONAL_FACTORS_ONLY',forecast_hs_cm=[0,2,3,4],slope_deg=35,max_net_swe_increase_kg_m2=4,liquid_water_max_kg_m2=.1)
    return dict(type='FeatureCollection',schema=SCHEMA,metadata=dict(reference_utc='2026-10-29T20:00:00Z',end_utc='2026-11-01T20:00:00Z',release_probability=None,hazard_grade=None,counts=dict(total_points=1,missing_physical_output=0)),features=[dict(type='Feature',geometry=dict(type='Polygon',coordinates=[[[12,42],[13,42],[13,43],[12,42]]]),properties=p)])


class AvalancheLayerTests(unittest.TestCase):
    def test_categories_are_physical_not_probability(self):
        data=fixture();self.assertIsNone(validate(data)['metadata']['release_probability'])
        for field,value in [('factor_class',3),('release_probability',.4),('hazard_grade',2),('forecast_hs_cm',[0,None,2,3])]:
            altered=copy.deepcopy(data);altered['features'][0]['properties'][field]=value
            with self.assertRaises(ValueError):validate(altered)

    def test_failed_output_remains_missing(self):
        data=fixture();p=data['features'][0]['properties'];p.update(factor_class=0,forecast_hs_cm=None,status='UNKNOWN_MODEL_OUTPUT');data['metadata']['counts']['missing_physical_output']=1
        self.assertIsNone(validate(data)['features'][0]['properties']['forecast_hs_cm'])
        p['forecast_hs_cm']=[0,0,0,0]
        with self.assertRaises(ValueError):validate(data)

    def test_wrong_horizon_and_duplicate_rejected(self):
        data=fixture();data['metadata']['end_utc']='2026-11-02T20:00:00Z'
        with self.assertRaises(ValueError):validate(data)
        data=fixture();data['features']*=2;data['metadata']['counts']['total_points']=2
        with self.assertRaises(ValueError):validate(data)

    def test_checksum_and_expiry_no_automatic_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/'avalanche';directory.mkdir();raw=json.dumps(fixture()).encode()
            (directory/'layer.geojson').write_bytes(raw)
            (directory/'manifest.json').write_text(json.dumps(dict(sha256=hashlib.sha256(raw).hexdigest())))
            service=Snapshot(tmp)
            self.assertEqual(service.response(dt.datetime(2026,10,30,tzinfo=dt.timezone.utc))['metadata']['delivery_status'],'FROZEN_FORECAST_SNAPSHOT')
            expired=service.response(dt.datetime(2026,11,2,tzinfo=dt.timezone.utc))
            self.assertEqual(expired['metadata']['delivery_status'],'EXPIRED_SNAPSHOT');self.assertFalse(expired['metadata']['automatic_refresh'])
            (directory/'layer.geojson').write_bytes(raw+b' ')
            with self.assertRaisesRegex(ValueError,'checksum'):service.read()


if __name__=='__main__':unittest.main()

class AutomaticAvalancheTests(unittest.TestCase):
    def test_freshness_expires_before_end_when_reference_old(self):
        from hazardia.web.avalanche_layer import freshness
        meta=fixture()['metadata'];meta['weather_run_utc']='2026-10-29T18:00:00Z'
        self.assertEqual(freshness(meta,dt.datetime(2026,10,29,22,tzinfo=dt.timezone.utc)),'CURRENT_MODEL_ESTIMATE')
        self.assertEqual(freshness(meta,dt.datetime(2026,10,30,6,tzinfo=dt.timezone.utc)),'STALE')
        self.assertEqual(freshness(meta,dt.datetime(2026,11,2,tzinfo=dt.timezone.utc)),'EXPIRED')
        self.assertEqual(freshness(meta,dt.datetime(2026,10,29,19,tzinfo=dt.timezone.utc)),'FUTURE_REFERENCE_INVALID')

    def test_atomic_object_and_worker_heartbeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/'avalanche';objects=directory/'objects';objects.mkdir(parents=True)
            raw=json.dumps(fixture()).encode();digest=hashlib.sha256(raw).hexdigest()
            (objects/(digest+'.geojson')).write_bytes(raw)
            (directory/'manifest.json').write_text(json.dumps(dict(sha256=digest)))
            (Path(tmp)/'avalanche-auto-config.json').write_text('{"enabled":true}')
            (directory/'auto-state.json').write_text(json.dumps(dict(status='READY',heartbeat_at='2026-10-29T21:00:00Z')))
            result=Snapshot(tmp).response(dt.datetime(2026,10,29,22,tzinfo=dt.timezone.utc))
            self.assertEqual(result['native_version'],digest);self.assertTrue(result['metadata']['automatic_refresh'])
            self.assertEqual(result['pipeline']['status'],'WORKER_HEARTBEAT_STALE')
