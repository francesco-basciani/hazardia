import copy,tempfile,unittest
from pathlib import Path
from hazardia.decision.fire_priorities import priority_category,DEFAULT_WEIGHTS
from hazardia.decision.fire_ideal import validate_input
from hazardia.decision.controller import decide
from hazardia.decision.verifier import verify
from hazardia.adaptation.control import ResearchControl
from hazardia.io import HazardError
from tests.decision.test_fire_ideal import fixture
class PlanTests(unittest.TestCase):
 def test_explicit_priority_classes(self):
  def f(category='transport',**tags):return dict(properties=dict(category=category,source='OpenStreetMap',osm_tags=tags))
  self.assertEqual(priority_category(f(railway='rail')),'railway');self.assertIsNone(priority_category(f(railway='abandoned')));self.assertEqual(priority_category(f('power_line')),'power_line');self.assertEqual(priority_category(f('utility',power='substation')),'critical_infrastructure');self.assertEqual(priority_category(f('clinic')),'healthcare');self.assertIsNone(priority_category(f(highway='residential')))
 def test_unknown_voltage_is_not_invented_and_proxy_not_assigned(self):
  f=dict(properties=dict(category='power_line',source='OpenStreetMap',osm_tags={},voltage=None));self.assertEqual(priority_category(f),'power_line');self.assertIsNone(f['properties']['voltage']);f['properties']['geometry_quality']='CENTER_PROXY_GEOMETRY_MISSING';self.assertIsNone(priority_category(f))
 def test_new_and_legacy_contracts(self):
  b=dict(job_id='job-'+'a'*32,fleet=[dict(id='u1',category='waterline_action',available=True,arrival_minutes=0)],weights=DEFAULT_WEIGHTS,robust=1,assumptions_confirmed=True);validate_input(b);b=copy.deepcopy(b);b['weights']['invented']=3
  with self.assertRaises(HazardError):validate_input(b)
 def test_real_missing_solver_recovers_with_checked_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   p=fixture();p['settings'].update(solver='highs',budget_s=5);r=decide(p,Path(d)/'decision','/nonexistent/hazardia-python');self.assertEqual(r['status'],'VALIDATED_FOR_SIMULATION');self.assertTrue(r['selected']);self.assertEqual(r['degradation']['state'],'DEGRADED');self.assertFalse(r['solver']['optimal']);self.assertEqual(verify(p,r['selected'])['status'],'VALIDATED_FOR_SIMULATION');self.assertLess(r['elapsed_s'],5)
 def test_unavailable_unit_is_never_selected_in_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   p=fixture();p['settings'].update(solver='highs',budget_s=5);p['resources'][0]['record']['payload']['maintenance']='UNAVAILABLE';r=decide(p,Path(d)/'decision','/nonexistent/hazardia-python');chosen={o['resource_id'] for o in p['options'] if o['id'] in r['selected']};self.assertNotIn(p['resources'][0]['id'],chosen);self.assertFalse(r['operationally_approvable'])
 def test_unknown_safety_never_turns_into_dispatch(self):
  with tempfile.TemporaryDirectory() as d:
   p=fixture();p['settings'].update(solver='highs',budget_s=5)
   for unit in p['resources']:unit['record']['payload']['maintenance']='UNKNOWN'
   r=decide(p,Path(d)/'decision','/nonexistent/hazardia-python');self.assertFalse(r['selected']);self.assertNotEqual(r['status'],'VALIDATED_FOR_SIMULATION');self.assertFalse(r['operationally_approvable'])
 def test_controlled_solver_failure_and_recovery(self):
  with tempfile.TemporaryDirectory() as d:
   c=ResearchControl(Path(d)/'health');c.action(dict(action='inject',fault='solver_down',expected_revision=0));p=fixture();p['settings']['budget_s']=5;p=c.apply(p);r=decide(p,Path(d)/'decision','/not-used');self.assertEqual(r['status'],'VALIDATED_FOR_SIMULATION');self.assertEqual(r['degradation']['state'],'DEGRADED');c.action(dict(action='recover',expected_revision=1));self.assertEqual(c.apply(fixture())['settings']['solver'],fixture()['settings']['solver'])
 def test_controlled_critical_unknown_still_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   c=ResearchControl(d);c.action(dict(action='inject',fault='safety_unknown',expected_revision=0))
   with self.assertRaises(HazardError):c.apply(fixture())

class WindowTests(unittest.TestCase):
 def test_local_mask_matches_full_grid(self):
  import numpy as np
  from shapely.geometry import box,mapping,Point
  from rasterio.transform import Affine
  from rasterio.features import geometry_mask
  from hazardia.decision.fire_ideal import local_analysis_mask
  tr=Affine(30,0,100,0,-30,1000);shape=(40,40);values=np.arange(1600).reshape(shape)
  for geom in [box(140,150,250,300),box(-100,900,200,1100),Point(300,400).buffer(75),box(5000,5000,5100,5100)]:
   window,mask=local_analysis_mask(geom,tr,shape);full=geometry_mask([mapping(geom)],shape,tr,invert=True);self.assertTrue(np.array_equal(values[window][mask],values[full]))
 def test_planning_time_cannot_retrodate_unit(self):
  b=dict(job_id='job-'+'a'*32,fleet=[dict(id='u1',category='waterline_action',available=True,arrival_minutes=120)],weights=DEFAULT_WEIGHTS,robust=1,assumptions_confirmed=True,planning_minutes=120);validate_input(b);b['fleet'][0]['arrival_minutes']=0
  with self.assertRaises(HazardError):validate_input(b)

class InfrastructureGeometryTests(unittest.TestCase):
 def test_railway_and_overhead_geometry_enter_native_priority_problem(self):
  import json,numpy as np
  from unittest.mock import patch
  from pyproj import Transformer
  from hazardia.io import sha256
  from hazardia.decision.fire_ideal import prepare
  back=Transformer.from_crs(3857,4326,always_xy=True).transform
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);job_id='job-'+'a'*32;job=root/'jobs'/job_id;job.mkdir(parents=True);np.savez(job/'fire-output.npz',probability=np.ones((20,20)),arrival=np.full((20,20,2),1800.),fire=np.ones((20,20,2)))
   plan=dict(resources=[],forcing=dict(terrain_id='fixture',moisture_model='MANUAL'),ignition_wgs84=[.01,.01],ignitions_wgs84=[dict(id='i',point=[.01,.01],at_minutes=0)],weather_source='FORECAST',weather_changes=[]);(job/'fire-series.json').write_text(json.dumps(dict(plan=plan,affected_bounds=[[0,0],[.02,.02]])));(job/'fire-native-result.json').write_text('{}');(job/'manifest.json').write_text(json.dumps(dict(artifacts={n:sha256(job/n) for n in ['fire-output.npz','fire-series.json','fire-native-result.json']})));(job/'request.json').write_text(json.dumps(dict(grid=dict(shape=[20,20],transform=[100,0,0,0,-100,2000],crs='EPSG:3857'),territory=dict(id='fixture',bbox_wgs84=[0,0,.02,.02]),options=dict(duration_s=3600,seed=1,moisture_percent=10,realizations=2),valid_from='2026-10-19T12:00:00Z',valid_until='2026-10-19T13:00:00Z',assets=[dict(role='weather',sha256='a'*64)])))
   features=[dict(type='Feature',id='rail',geometry=dict(type='LineString',coordinates=[back(500,800),back(1500,800)]),properties=dict(name='Fixture railway',category='transport',osm_tags=dict(railway='rail'),optimization_eligible=False)),dict(type='Feature',id='wire',geometry=dict(type='LineString',coordinates=[back(1000,500),back(1000,1500)]),properties=dict(name='Fixture overhead wire',category='power_line',voltage=None,optimization_eligible=False))]
   source=dict(features=features,coverage_bbox_wgs84=[0,0,.02,.02],source_url='fixture',source_sha256='b'*64,available_at='2026-10-19T00:00:00Z',missing=['Synthetic fixture'])
   body=dict(job_id=job_id,fleet=[dict(id='ground',category='waterline_action',available=True,arrival_minutes=0)],weights=DEFAULT_WEIGHTS,robust=1,assumptions_confirmed=True,planning_minutes=0)
   with patch('hazardia.territorial_context.acquire',return_value=source):problem,context=prepare(root,body,root/'prepared')
   self.assertEqual({g['category'] for g in context['assets']},{'railway','power_line'});self.assertEqual(len(problem['options']),2);self.assertIsNone(next(g['source_voltage'] for g in context['assets'] if g['category']=='power_line'));self.assertEqual(context['source']['inventory_counts']['railway'],1)
