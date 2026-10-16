import tempfile,sys,time,copy,os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from tests.decision.test_verifier import fixture
from hazardia.decision.supervisor import bounded_decide
from hazardia.io import load

class Supervisor(TestCase):
    def test_outer_watchdog_kills_entire_process_group(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture();p['settings']['budget_s']=.8;out=Path(d)/'job';script="import subprocess,sys,time,pathlib;p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);pathlib.Path(sys.argv[1]).write_text(str(p.pid));time.sleep(30)"
            with patch('hazardia.decision.supervisor._command',return_value=[sys.executable,'-c',script,str(Path(d)/'grandchild.pid')]):r=bounded_decide(p,out,sys.executable)
            self.assertEqual(r['status'],'TIMEOUT_UNPROVEN');self.assertFalse(r['selected']);self.assertLess(r['elapsed_s'],.8)
            pid=int((Path(d)/'grandchild.pid').read_text());stat=Path('/proc')/str(pid)/'stat';self.assertTrue(not stat.exists() or stat.read_text().rsplit(')',1)[1].split()[0]=='Z')
    def test_expired_acceptance_queue_cannot_publish_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture();p['settings']['budget_s']=1
            with patch('hazardia.decision.supervisor._command') as command:r=bounded_decide(p,Path(d)/'job',sys.executable,accepted_monotonic=time.monotonic()-2);command.assert_not_called()
            self.assertEqual(r['status'],'TIMEOUT_UNPROVEN');self.assertFalse(r['selected'])
