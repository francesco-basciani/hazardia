import json,tempfile,unittest
from pathlib import Path
from hazardia.web.fire_progress import progress
class ProgressTests(unittest.TestCase):
 def run_case(self,state,text):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'jobs/job-test';p.mkdir(parents=True);(p/'request.json').write_text(json.dumps(dict(options=dict(duration_s=72*3600))));(p/'stdout.log').write_text(text);return progress(d,dict(id='job-test',state=state))
 def test_startup_has_no_invented_progress(self):self.assertEqual(self.run_case('RUNNING','compiling')['stage'],'STARTUP')
 def test_queue_is_distinct(self):self.assertEqual(self.run_case('QUEUED','')['stage'],'QUEUED')
 def test_native_quarter_hour_is_read(self):
  r=self.run_case('RUNNING','HOUR 36.5 CELLS 72\n');self.assertEqual(r['native_hours'],36.5);self.assertEqual(r['total_hours'],72);self.assertEqual(r['stage'],'MODEL')
 def test_model_end_is_not_job_success(self):self.assertEqual(self.run_case('RUNNING','HOUR 72.0 CELLS 33\n')['stage'],'PRODUCTS')
 def test_tail_read_is_bounded_and_clamped(self):
  r=self.run_case('RUNNING','x'*1000000+'\nHOUR 80.0 CELLS 33\n');self.assertEqual(r['native_hours'],72)
