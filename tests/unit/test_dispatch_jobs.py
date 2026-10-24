"""Real supervisor/dispatcher, synthetic sleeping interpreter: no CIMA evidence."""
import concurrent.futures
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

from hazardia.io import load, write_new
from hazardia.jobs import JobStore
from hazardia.package_catalog import APPROVED_MODELS
from tests.support import fixture


class DispatchJobTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.request,_=fixture(self.root/'inputs')
        shim=self.root/'synthetic-interpreter'
        shim.write_text('#!'+sys.executable+'''\nimport subprocess,sys,time,pathlib
root=pathlib.Path(sys.argv[-1])
p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
(root/'synthetic-child.pid').write_text(str(p.pid))
time.sleep(30)
''');shim.chmod(0o755)
        cfg=dict(core_python=sys.executable,fire_python=str(shim),geo_python=sys.executable,
                 fire_source='/not-used-by-synthetic-interpreter',engine_files={},
                 engines={e:r for rows in APPROVED_MODELS.values() for e,_,r in rows},
                 minimum_free_bytes=1,max_job_bytes=1024**2)
        path=self.root/'config.json';write_new(path,cfg)
        self.store=JobStore(self.root/'jobs',path)

    def tearDown(self):self.tmp.cleanup()

    def check_terminal(self,job,status):
        root=self.store.root/job
        self.assertEqual(self.store.get(job)['state'],status)
        self.assertFalse(self.store.get(job)['usable_product'])
        receipt=load(root/'adapter-binding.json')
        self.assertEqual(receipt['package']['package_id'],'hazardia.wildfire')
        manifest=load(root/'manifest.json');self.assertIn('adapter-binding.json',manifest['artifacts'])
        pid=int((root/'synthetic-child.pid').read_text());stat=Path('/proc')/str(pid)/'stat'
        self.assertTrue(not stat.exists() or stat.read_text().rsplit(')',1)[1].split()[0]=='Z')

    def test_runtime_binding_error_reaches_supervisor_without_starting_worker(self):
        import json
        config=load(self.root/'config.json');config['engines']['PROPAGATOR']='0'*40
        (self.root/'config.json').write_text(json.dumps(config))
        job=self.store.submit(self.request,self.root/'inputs');result=self.store.work_once()
        self.assertEqual(result['state'],'ERROR');self.assertEqual(result['error_code'],'PACKAGE_RUNTIME')
        self.assertFalse(result['usable_product'])
        self.assertFalse((self.store.root/job/'synthetic-child.pid').exists())
        self.assertFalse((self.store.root/job/'adapter-binding.json').exists())

    def test_real_dispatch_timeout_kills_worker_descendants(self):
        job=self.store.submit(self.request,self.root/'inputs')
        self.store.work_once()
        self.check_terminal(job,'TIMEOUT')

    def test_real_dispatch_cancel_then_explicit_retry_retains_receipt(self):
        req=dict(self.request,timeout_s=8);job=self.store.submit(req,self.root/'inputs')
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(self.store.work_once);deadline=time.monotonic()+4
            while not (self.store.root/job/'synthetic-child.pid').exists() and time.monotonic()<deadline:time.sleep(.02)
            self.assertTrue((self.store.root/job/'synthetic-child.pid').exists())
            self.assertTrue(self.store.cancel(job));future.result(timeout=5)
        self.check_terminal(job,'CANCELLED')
        raw=(self.store.root/job/'adapter-binding.json').read_bytes();retry=self.store.retry(job)
        self.assertNotEqual(job,retry);self.assertEqual(self.store.get(retry)['parent'],job)
        self.assertEqual(self.store.get(retry)['state'],'QUEUED')
        self.assertEqual((self.store.root/job/'adapter-binding.json').read_bytes(),raw)
        self.assertFalse((self.store.root/retry/'adapter-binding.json').exists())
