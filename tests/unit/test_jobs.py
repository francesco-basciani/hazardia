import copy,sys,tempfile,time,unittest,concurrent.futures
from pathlib import Path
from unittest.mock import patch
from hazardia.jobs import JobStore
from hazardia.io import HazardError,write_new,load
from tests.support import fixture

class Jobs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.inputs=self.root/'inputs';self.request,_=fixture(self.inputs);self.cfg=self.root/'runtime.json';write_new(self.cfg,dict(core_python=sys.executable,minimum_free_bytes=1,max_job_bytes=1024**2));self.store=JobStore(self.root/'jobs',self.cfg,queue_capacity=2)
    def tearDown(self):self.temp.cleanup()
    def submit(self,**changes):
        req=copy.deepcopy(self.request);req.update(changes);return self.store.submit(req,self.inputs)
    def test_bounded_fifo_and_one_running(self):
        one=self.submit();two=self.submit()
        with self.assertRaises(HazardError) as e:self.submit()
        self.assertEqual(e.exception.code,'QUEUE_FULL');self.assertEqual(self.store.claim(),one);self.assertIsNone(self.store.claim());self.assertEqual(self.store.get(two)['state'],'QUEUED')
    def test_queued_cancel_manifest_and_explicit_retry(self):
        one=self.submit();self.assertTrue(self.store.cancel(one));self.assertFalse(self.store.cancel(one));self.assertEqual(self.store.get(one)['state'],'CANCELLED');self.assertFalse(self.store.get(one)['usable_product']);self.assertEqual(load(self.store.root/one/'manifest.json')['status'],'CANCELLED')
        retry=self.store.retry(one);self.assertNotEqual(one,retry);self.assertEqual(self.store.get(retry)['parent'],one);self.assertEqual(self.store.get(one)['state'],'CANCELLED')
    def test_input_drift_rejected_before_worker(self):
        one=self.submit();(self.store.root/one/'input/dem.tif').write_bytes(b'changed')
        with patch('hazardia.jobs.build_command') as command:result=self.store.work_once();command.assert_not_called()
        self.assertEqual(result['state'],'ERROR');self.assertEqual(result['error_code'],'CHECKSUM')
    def test_zero_exit_without_product_cannot_succeed(self):
        one=self.submit()
        with patch('hazardia.jobs.build_command',return_value=[sys.executable,'-c',"print('STOP: no data')"]):result=self.store.work_once()
        self.assertEqual(result['state'],'ERROR');self.assertFalse(result['usable_product']);self.assertTrue((self.store.root/one/'manifest.json').exists())
    def test_timeout_terminates_descendant_and_keeps_evidence(self):
        one=self.submit();code="import subprocess,sys,time,pathlib;p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);pathlib.Path('child.pid').write_text(str(p.pid));time.sleep(30)"
        tic=time.monotonic()
        with patch('hazardia.jobs.build_command',return_value=[sys.executable,'-c',code]):result=self.store.work_once()
        self.assertEqual(result['state'],'TIMEOUT');self.assertLess(time.monotonic()-tic,6);self.assertFalse(result['usable_product'])
        pid=int((self.store.root/one/'child.pid').read_text());stat=Path(f'/proc/{pid}/stat');self.assertTrue(not stat.exists() or stat.read_text().rsplit(')',1)[1].split()[0]=='Z')
        manifest=load(self.store.root/one/'manifest.json');self.assertGreater(manifest['metrics']['rss_samples'],0);self.assertGreater(manifest['metrics']['sampled_peak_process_group_rss_bytes'],0)
    def test_running_cancel_is_classified(self):
        one=self.submit(timeout_s=8)
        with patch('hazardia.jobs.build_command',return_value=[sys.executable,'-c','import time;time.sleep(30)']):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.store.work_once);deadline=time.monotonic()+3
                while not self.store.get(one)['worker_pid'] and time.monotonic()<deadline:time.sleep(.02)
                self.assertTrue(self.store.cancel(one));result=future.result(timeout=6)
        self.assertEqual(result['state'],'CANCELLED');self.assertFalse(result['usable_product']);self.assertIn('CANCEL_REQUESTED',[v['state'] for v in self.store.events(one)])
    def test_log_limit_is_classified(self):
        one=self.submit(timeout_s=8,max_log_bytes=1024)
        with patch('hazardia.jobs.build_command',return_value=[sys.executable,'-c',"import time;print('x'*4096,flush=True);time.sleep(30)"]):result=self.store.work_once()
        self.assertEqual(result['state'],'ERROR');self.assertEqual(result['error_code'],'LOG_LIMIT')
    def test_fault_does_not_change_other_queued_job(self):
        one=self.submit();two=self.submit()
        with patch('hazardia.jobs.build_command',return_value=[sys.executable,'-c','raise SystemExit(7)']):result=self.store.work_once()
        self.assertEqual(result['id'],one);self.assertEqual(result['state'],'ERROR');self.assertEqual(self.store.get(two)['state'],'QUEUED');self.assertEqual(self.store.claim(),two)
    def test_disappearing_grass_scratch_file_is_not_job_failure(self):
        from hazardia.jobs import _disk_usage
        from unittest.mock import MagicMock
        gone=MagicMock();gone.is_file.return_value=True;gone.stat.side_effect=FileNotFoundError('Concurrent GRASS journal removal')
        directory=MagicMock();directory.rglob.return_value=[gone]
        self.assertEqual(_disk_usage(directory),(0,0))
    def test_accepted_request_and_runtime_drift_are_rejected(self):
        one=self.submit();p=self.store.root/one/'request.json';p.write_text(p.read_text().replace('"seed": 1729','"seed": 1730'))
        with patch('hazardia.jobs.build_command') as command:result=self.store.work_once();command.assert_not_called()
        self.assertEqual(result['state'],'ERROR');self.assertEqual(result['error_code'],'CHECKSUM')
    def test_missing_request_is_terminal_error_not_stuck_running(self):
        one=self.submit();(self.store.root/one/'request.json').unlink()
        result=self.store.work_once();self.assertEqual(result['state'],'ERROR');self.assertFalse(result['usable_product'])
    def test_explicit_recovery_records_interruption_and_preserves_queue(self):
        one=self.submit();two=self.submit();self.assertEqual(self.store.claim(),one)
        with patch('hazardia.jobs.os.kill',side_effect=ProcessLookupError):self.assertEqual(self.store.recover(),[one])
        result=self.store.get(one);self.assertEqual(result['state'],'ERROR');self.assertFalse(result['usable_product'])
        manifest=load(self.store.root/one/'manifest.json');self.assertEqual(manifest['error_code'],'INTERRUPTED');self.assertIsNone(manifest['metrics'])
        self.assertEqual(self.store.get(two)['state'],'QUEUED');self.assertEqual(self.store.recover(),[])
