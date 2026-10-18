"""Synthetic metadata/geometry checks, not a native physics qualification."""
import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
from pyproj import Transformer
from hazardia.io import sha256,HazardError
from hazardia.decision.fire_ideal_evaluation import evaluate
class EvaluationTests(unittest.TestCase):
 def fixture(self,root,a=1.,b=0.):
  folder=root/'web-state/ideal-native-test';folder.mkdir(parents=True);decision='decision-'+'a'*32
  fleet=[dict(id='u1',category='waterline_action',area=[[42,15],[42,15.001],[42.001,15]],at_minutes=0,effect='fuel_removal')]
  ctx=root/'web-state'/(decision+'-input')/'prepared';ctx.mkdir(parents=True);lon,lat=Transformer.from_crs(32633,4326,always_xy=True).transform(500000,4640000)
  (ctx/'context.json').write_text(json.dumps(dict(body=dict(robust=.5),assets=[dict(priority_weight=2,geometry=dict(type='Point',coordinates=[lon,lat]))])))
  d=root/'web-state'/decision;d.mkdir();(d/'ideal-result.json').write_text(json.dumps(dict(ideal=dict(proposed_resources=fleet))))
  jobs={}
  for case,value in [('A',a),('B',b)]:
   job='job-'+case.lower()*32;jobs[case]=job;p=root/'jobs'/job;p.mkdir(parents=True);np.savez(p/'fire-output.npz',probability=np.full((2,2),value));(p/'weather.json').write_text('{}')
   plan=dict(resources=[] if case=='A' else fleet,ignitions_wgs84=[dict(point=[lat,lon],at_minutes=0)],weather_changes=[],forcing=dict(id='frozen'),records=[],action_times=[0],comparison_times=[0],moisture_percent=10)
   (p/'fire-series.json').write_text(json.dumps(dict(plan=plan,frames=[dict(expected_area_ha=value*.36)])))
   req=dict(grid=dict(shape=[2,2],transform=[30,0,499970,0,-30,4640030],crs='EPSG:32633'),options=dict(seed=1),valid_from='2026-10-18T13:00:00Z',valid_until='2026-10-21T13:00:00Z',assets=[dict(role='weather',path='weather.json',sha256=sha256(p/'weather.json'))]);(p/'request.json').write_text(json.dumps(req));(p/'manifest.json').write_text(json.dumps(dict(artifacts={n:sha256(p/n) for n in ['fire-output.npz','fire-series.json']})))
  (folder/'replay.json').write_text(json.dumps(dict(jobs=jobs,decision_id=decision)));return folder,jobs
 def test_proposal_can_win_on_actual_evaluated_grid(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);folder,_=self.fixture(root);r=evaluate(root,folder);self.assertEqual(r['best_case'],'B');self.assertFalse(r['operationally_approvable']);self.assertIn('NOT_GLOBAL',r['qualification'])
 def test_baseline_remains_best_when_proposal_is_worse(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);folder,_=self.fixture(root,.1,1.);self.assertEqual(evaluate(root,folder)['best_case'],'A')
 def test_mismatched_seed_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);folder,jobs=self.fixture(root);p=root/'jobs'/jobs['B']/'request.json';r=json.loads(p.read_text());r['options']['seed']=2;p.write_text(json.dumps(r))
   with self.assertRaises(HazardError):evaluate(root,folder)
 def test_changed_native_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);folder,jobs=self.fixture(root);(root/'jobs'/jobs['B']/'fire-output.npz').write_bytes(b'changed')
   with self.assertRaises(HazardError):evaluate(root,folder)

 def test_different_frozen_terrain_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);folder,jobs=self.fixture(root)
   for case in ['A','B']:
    p=root/'jobs'/jobs[case];(p/'terrain.npz').write_bytes(case.encode());request=p/'request.json';r=json.loads(request.read_text());r['assets'].append(dict(role='fire_arrays',path='terrain.npz',sha256=sha256(p/'terrain.npz')));request.write_text(json.dumps(r))
   with self.assertRaises(HazardError):evaluate(root,folder)
