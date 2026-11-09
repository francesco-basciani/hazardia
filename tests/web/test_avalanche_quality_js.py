"""Production quality annotations: clip/group display only, never hazard geometry."""
import json,unittest
from pathlib import Path
try:import quickjs
except ImportError:quickjs=None
@unittest.skipUnless(quickjs,'QuickJS required')
class QualityAnnotationsTests(unittest.TestCase):
 def setUp(self):
  self.c=quickjs.Context();root=Path(__file__).resolve().parents[2]/'src/hazardia/web/static'
  self.c.eval((root/'avalanche-model.js').read_text().replace('export ',''));self.c.eval('\n'.join(x for x in (root/'avalanche-quality.js').read_text().splitlines() if not x.startswith('import ')).replace('export ',''))
  self.c.eval("function feature(code,coordinates){return {geometry:{type:'Polygon',coordinates},properties:{id:'sample',potential_class:code,soil_association:'known',substrate:'known'}}}const square=[[[-10,-10],[10,-10],[10,10],[-10,10],[-10,-10]]];const project=p=>p.map(x=>x*10);")
 def test_enclosing_polygon_still_has_annotation_in_view(self):
  self.c.eval('const f=feature(0,square);const before=JSON.stringify(f);const out=qualityAnnotations([f],[-1,-1,1,1],project);')
  self.assertEqual(self.c.eval('out.length'),1);self.assertEqual(self.c.eval('JSON.stringify(out[0].anchor)'),'[0,0]');self.assertTrue(self.c.eval('before===JSON.stringify(f)'))
 def test_hole_is_not_marked_as_missing_area(self):
  self.c.eval('const f=feature(0,[square[0],[[-2,-2],[2,-2],[2,2],[-2,2],[-2,-2]]]);')
  self.assertEqual(self.c.eval('qualityAnnotations([f],[-1,-1,1,1],project).length'),0)
 def test_clip_edge_when_no_vertices_in_view(self):
  self.c.eval('const f=feature(2,[[[-10,-.5],[10,-.5],[10,.5],[-10,.5],[-10,-.5]]]);const p=qualityAnnotations([f],[-1,-1,1,1],project)[0].anchor;')
  self.assertTrue(self.c.eval('p[0]>=-1&&p[0]<=1&&Math.abs(p[1])===.5'))
 def test_counts_types_and_zoom_grouping(self):
  self.c.eval('const fs=[feature(0,square),feature(2,square),feature(6,square),feature(1,square)];fs[2].properties.soil_missing_samples=1;const out=qualityAnnotations(fs,[-20,-20,20,20],project);')
  self.assertEqual(self.c.eval('out.length'),2);self.assertEqual(self.c.eval('out.reduce((n,g)=>n+g.features.length,0)'),3);self.assertEqual(self.c.eval('out.find(g=>g.channel==="unknown").counts.missing'),1);self.assertEqual(self.c.eval('out.find(g=>g.channel==="unknown").counts.snow_unverified'),1)
 def test_outside_or_no_gap_not_counted(self):
  self.assertEqual(self.c.eval('qualityAnnotations([feature(0,square),feature(6,square)],[30,30,40,40],project).length'),0)
  self.assertEqual(self.c.eval('qualityAnnotations([feature(6,square)],[-20,-20,20,20],project).length'),0)
 def test_multipolygon_and_bad_view(self):
  self.c.eval('const f=feature(0,square);f.geometry={type:"MultiPolygon",coordinates:[square]};');self.assertEqual(self.c.eval('qualityAnnotations([f],[-1,-1,1,1],project).length'),1)
  with self.assertRaises(Exception):self.c.eval('qualityAnnotations([f],[1,1,-1,-1],project)')
