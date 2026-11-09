import copy
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from http.server import ThreadingHTTPServer

from wii.io import HazardError as WIIError
from hazardia.io import HazardError as HostError
HazardError=(WIIError,HostError)
from wii.contracts import digest


class DecisionAdmission(unittest.TestCase):
    def problem(self):
        from tests.decision.test_fire_ideal import fixture
        from wii.decisions import prepare
        p=fixture()
        self.scenarios=dict(schema='hazardia.wii.scenarios/0.1.0',id='s',measure='JOINT_CONDITIONAL_INDEPENDENT_POISSON',
             qualification='EXPERIMENTAL_UNCALIBRATED',weight_semantics='MONTE_CARLO_OR_STRATUM_ESTIMATOR_WEIGHTS',members=[
             dict(id='none',state='NO_IGNITION',weight=.6),dict(id='fire',state='READY',weight=.4)])
        consequence={e['id']:dict(none=0,fire=10) for e in p['events']}
        benefit={o['id']:dict(none=0,fire=4) for o in p['options']}
        return prepare(p,self.scenarios,consequence,benefit)

    def test_expected_loss_no_double_probability_and_verifier(self):
        from hazardia.decision.verifier import verify,losses
        p=self.problem();base=losses(p,[]);self.assertAlmostEqual(base['expected'],4*len(p['events']))
        chosen=[p['options'][0]['id']];self.assertEqual(verify(p,chosen)['status'],'VALIDATED_FOR_SIMULATION')
        self.assertFalse(verify(p,chosen)['operationally_approvable'])
        self.assertLess(losses(p,chosen)['expected'],base['expected'])

    def test_unknown_missing_failed_or_nonzero_no_event_rejected(self):
        from hazardia.decision.problem import validate
        p=self.problem()
        changes=[lambda p:p['ensemble'].update(unresolved_weight=.1),
                 lambda p:p['events'][0]['exposure'].update(none=1),
                 lambda p:p['scenarios'][0].update(qualification='SYNTHETIC_RESEARCH'),
                 lambda p:p['scenarios'][1].update(state='ERROR'),
                 lambda p:p['options'][0]['benefit'].pop('none')]
        for change in changes:
            bad=copy.deepcopy(p);change(bad)
            with self.assertRaises(HazardError):validate(bad)

    def test_critical_unknown_and_rolling_remain_checked(self):
        from hazardia.decision.verifier import verify
        p=self.problem();p['resources'][0]['record']['payload']['maintenance']=None
        result=verify(p,[p['options'][0]['id']]);self.assertIn('UNKNOWN_SAFETY',{r['id'] for r in result['rules']})
        from hazardia.decision.rolling import advance
        p=self.problem();future,progress=advance(p,dict(status='VALIDATED_FOR_SIMULATION',selected=[]),1)
        self.assertEqual(future['schema_version'],'0.7.0');self.assertEqual(future['ensemble'],p['ensemble'])


class APITests(unittest.TestCase):
    def setUp(self):
        from hazardia.web.server import Handler
        from wii.service import Service
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.app=SimpleNamespace(root=root,state=root/'web-state',stop=threading.Event(),lock=threading.Lock(),metrics=[])
        self.app.wii=Service(self.app,start_worker=False)
        from wii.server import Handler as WIIHandler
        from hazardia.web.wii_client import APIClient
        self.backend=ThreadingHTTPServer(('127.0.0.1',0),WIIHandler);self.backend.app=self.app
        self.backend_thread=threading.Thread(target=self.backend.serve_forever,daemon=True);self.backend_thread.start()
        self.host_app=SimpleNamespace(**vars(self.app));self.host_app.wii=APIClient(self.backend.server_port)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.app=self.host_app
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):self.server.shutdown();self.server.server_close();self.backend.shutdown();self.backend.server_close();self.tmp.cleanup()
    def request(self,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        h={'X-Hazardia-Research':'1','Content-Type':'application/json'};h.update(headers or {})
        c.request('GET' if body is None else 'POST',path,body=None if body is None else json.dumps(body),headers=h)
        r=c.getresponse();status=r.status;value=r.read();c.close();return status,json.loads(value)

    def test_locations_keep_native_points_and_exclude_area_centroids_aliases(self):
        from tests.wii.fixtures import source,event
        store=self.app.wii.store;doc=store.document(source(),external_id='location-test',text='SYNTHETIC')
        point=event(doc);store.put_event(point)
        polygon=event(doc,'area',dict(type='Polygon',coordinates=[[[13,42],[14,42],[14,43],[13,43],[13,42]]]))
        polygon['location'].update(precision='ADMIN_AREA');store.put_event(polygon)
        alias=event(doc,'alias');alias['attributes']['canonical_event_id']='e1';store.put_event(alias)
        status,value=self.request('/api/wii/locations');self.assertEqual(status,200)
        self.assertEqual([e['id'] for e in value['events']],['e1'])
        self.assertEqual(value['events'][0]['location']['geometry']['coordinates'],[13.4,42.3])
        point['location']['geometry']['coordinates']=[14,42.5];store.put_event(point)
        self.assertEqual(len(self.request('/api/wii/locations')[1]['events']),1)
        self.assertEqual(self.request('/api/wii/locations?limit=15001')[0],400)
        self.assertEqual(self.request('/api/wii/locations?from=2025-01-01T00:00:00Z&until=2026-01-01T00:00:00Z')[1]['events'],[])

    def test_structured_inventory_riskmap_and_crawler_api(self):
        from tests.wii.fixtures import product
        from wii.national import setup
        store=self.app.wii.store;setup(store)
        self.assertEqual(self.request('/api/wii/inventory?limit=501')[0],400)
        self.assertEqual(self.request('/api/wii/inventory/summary')[1]['records'],0)
        ident=store.artifact('probability',product())
        status,value=self.request('/api/wii/riskmap?artifact_id='+ident)
        self.assertEqual(status,200);self.assertEqual(len(value['levels']),5)
        self.assertEqual(value['classification'][0]['level'],'MODERATE')
        body=dict(idempotency_key='crawl-api',source_ids=['pressenza-italy'],pages=1,max_articles=2)
        status,value=self.request('/api/wii/crawler/runs',body);self.assertEqual(status,202)
        self.assertEqual(self.request('/api/wii/crawler/runs/'+value['run_id']+'/pause',{})[1]['state'],'PAUSED')
        self.assertEqual(self.request('/api/wii/crawler/runs',body|dict(source_ids=['ansa-restricted']))[0],400)

    def test_calibration_endpoint_is_lazy_and_accepts_frozen_model_reference(self):
        self.assertFalse(self.request('/api/wii/calibration/italy')[1]['available'])
        status,value=self.request('/api/wii/calibration/italy',dict(idempotency_key='calibration-api',base_model_id='frozen-test-reference'))
        self.assertEqual(status,202);self.assertTrue(value['task_id'].startswith('wii-'))

    def test_inventory_binary_download_is_bounded_and_path_guarded(self):
        import sqlite3
        from hazardia.io import sha256
        root=self.app.root;folder=root/'runs/wii-crawler-20261024';folder.mkdir(parents=True)
        path=folder/'event-inventory-aaaaaaaaaaaa.sqlite';db=sqlite3.connect(path);db.execute('CREATE TABLE fixture(id TEXT)');db.close()
        queued=self.app.wii.submit('inventory_export',dict(idempotency_key='export-test'));ident=queued['task_id']
        result=dict(path=str(path),sha256=sha256(path),sqlite_integrity='ok')
        with self.app.wii.store.connect() as db:db.execute("UPDATE tasks SET state='SUCCEEDED',result=? WHERE id=?",(json.dumps(result),ident))
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port);c.request('GET','/api/wii/inventory/exports/'+ident+'.sqlite');r=c.getresponse();self.assertEqual(r.status,200);self.assertEqual(r.getheader('Content-Type'),'application/vnd.sqlite3');self.assertTrue(r.read().startswith(b'SQLite format 3'));c.close()
        result['path']=str(root/'outside.sqlite')
        with self.app.wii.store.connect() as db:db.execute('UPDATE tasks SET result=? WHERE id=?',(json.dumps(result),ident))
        self.assertEqual(self.request('/api/wii/inventory/exports/'+ident+'.sqlite')[0],404)

    def test_enabled_status_and_disabled_no_side_effect(self):
        status,value=self.request('/api/wii/status');self.assertEqual(status,200);self.assertTrue(value['enabled'])
        self.assertEqual(self.request('/api/wii/v1/manifest')[1]['api_version'],'1')
        self.assertEqual(self.request('/api/wii/v1/openapi')[1]['openapi'],'3.0.3')
        self.assertEqual(len(self.request('/api/wii/v1/layers')[1]['layers']),1)
        self.assertEqual(self.request('/api/wii/v1/unknown')[0],404)
        self.host_app.wii=None
        self.assertEqual(self.request('/api/wii/v1/manifest')[0],409)
        self.assertEqual(self.request('/api/wii/status')[1]['enabled'],False)
        self.assertEqual(self.request('/api/wii/scenarios',dict(idempotency_key='x'))[0],409)

    def test_api_validation_queue_idempotency_and_cancel(self):
        self.assertEqual(self.request('/api/wii/events')[0],400)
        status,a=self.request('/api/wii/scenarios',dict(idempotency_key='a',product_id='unknown'))
        self.assertEqual(status,202)
        status,b=self.request('/api/wii/scenarios',dict(idempotency_key='a',product_id='unknown'));self.assertEqual(a['task_id'],b['task_id'])
        self.assertEqual(self.request('/api/wii/scenarios',dict(idempotency_key='a',product_id='changed'))[0],409)
        for i in range(3):self.request('/api/wii/scenarios',dict(idempotency_key=str(i)))
        self.assertEqual(self.request('/api/wii/scenarios',dict(idempotency_key='overflow'))[0],429)
        self.assertTrue(self.request('/api/wii/tasks/'+a['task_id']+'/cancel',{})[1]['cancel_accepted'])
        self.assertEqual(self.request('/api/wii/tasks/'+a['task_id'])[1]['state'],'CANCELLED')

    def test_same_origin_host_and_source_rights(self):
        self.assertEqual(self.request('/api/wii/sources',{},headers={'Origin':'https://attacker.invalid'})[0],403)
        self.assertEqual(self.request('/api/wii/status',headers={'Host':'attacker.invalid'})[0],403)
        from tests.wii.fixtures import source
        s=source();s['license']['processing']=False
        self.assertEqual(self.request('/api/wii/sources',dict(expected_revision=0,sources=[s],selection=dict(regions=[],source_ids=[])))[0],400)

    def test_national_coverage_is_cached_and_region_guarded(self):
        status,value=self.request('/api/wii/coverage');self.assertEqual(status,200);self.assertEqual(value['status'],'NOT_READY')
        self.assertEqual(self.request('/api/wii/coverage/events?region=IT-999')[0],400)
        status,queued=self.request('/api/wii/datasets/italy',dict(idempotency_key='national',dataset='effis'))
        self.assertEqual(status,202);self.assertTrue(queued['task_id'].startswith('wii-'))

    def test_news_archive_task_and_empty_persistent_queue(self):
        status,value=self.request('/api/wii/news/backfill');self.assertEqual(status,200);self.assertEqual(value['states'],{})
        status,value=self.request('/api/wii/news/discover',dict(idempotency_key='discover',source_id='pressenza-italy',page=1))
        self.assertEqual(status,202)
