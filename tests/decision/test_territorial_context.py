import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
from hazardia.territorial_context import parse_osm,bounds_checked,assess
from hazardia.decision.fire_ideal import available_for_automatic_plan
from hazardia.io import HazardError,sha256
class ContextTests(unittest.TestCase):
 def test_overhead_not_underground_and_no_height_inference(self):
  rows=[]
  for n,t in enumerate([{'power':'line','voltage':'150000'},{'power':'minor_line'},{'power':'cable'},{'power':'cable','location':'overhead'},{'power':'line','location':'underground'},{'power':'line','location':'underwater'}]):rows.append(dict(type='way',id=n,tags=t,geometry=[dict(lat=42,lon=13),dict(lat=42.1,lon=13.1)]))
  f,_=parse_osm(dict(elements=rows));self.assertEqual([v['id'] for v in f if v['properties']['category']=='power_line'],['osm-way-0','osm-way-1','osm-way-3']);self.assertEqual(len(f),6);self.assertIsNone(f[0]['properties']['height']);self.assertIsNone(f[1]['properties']['voltage'])
 def test_named_assets_and_polygon(self):
  f,_=parse_osm(dict(elements=[dict(type='node',id=1,lat=42,lon=13,tags=dict(place='town',name='Comune')),dict(type='way',id=2,center=dict(lat=42,lon=13),tags=dict(amenity='school'),geometry=[dict(lat=42,lon=13),dict(lat=42,lon=13.1),dict(lat=42.1,lon=13.1),dict(lat=42,lon=13)])]));self.assertEqual(f[0]['properties']['name'],'Comune');self.assertEqual(f[1]['geometry']['type'],'Polygon')
 def test_world_bounds_and_budgets(self):
  self.assertEqual(bounds_checked([-17,14,-16.5,14.5]),[-17,14,-16.5,14.5])
  for b in [[0,0,2,2],[0,0,0,1],[0,0,float('nan'),1],[1,2,3]]:
   with self.assertRaises(HazardError):bounds_checked(b)
 def test_air_excluded_even_when_requested_available(self):
  for category in ['canadair','helicopter']:self.assertFalse(available_for_automatic_plan(dict(category=category,available=True)))
  self.assertTrue(available_for_automatic_plan(dict(category='waterline_action',available=True)));self.assertFalse(available_for_automatic_plan(dict(category='heavy_action',available=False)))
 def test_single_native_builtup_cell_can_be_included_explicitly(self):
  import numpy as np
  from hazardia.ingest.fire_priorities import builtup
  with tempfile.TemporaryDirectory() as folder:
   terrain=Path(folder)/'terrain-cache/example';terrain.mkdir(parents=True);(terrain/'grid.json').write_text(json.dumps(dict(crs='EPSG:3857',transform=[30,0,0,0,-30,60])));(terrain/'manifest.json').write_text(json.dumps(dict(available_at='2026-10-19T00:00:00Z')));np.savez(terrain/'expanded-arrays.npz',landcover=np.array([[50,10],[10,10]]))
   self.assertEqual(len(builtup(folder,'example',[-.001,-.001,.001,.001],'fixture')['features']),0)
   self.assertEqual(len(builtup(folder,'example',[-.001,-.001,.001,.001],'fixture',limit=1200,min_area=900)['features']),1)
 def test_native_probability_and_conditional_contact(self):
  import numpy as np
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);job=root/'jobs/job-test';job.mkdir(parents=True);p=np.array([[1.,0],[0,0]]);arrival=np.full((2,2,2),np.inf);arrival[0,0]=[60,120];fire=np.zeros((2,2,2));fire[0,0]=1;np.savez(job/'fire-output.npz',probability=p,arrival=arrival,fire=fire)
   series=dict(plan={});(job/'fire-series.json').write_text(json.dumps(series));(job/'request.json').write_text(json.dumps(dict(grid=dict(shape=[2,2],transform=[100,0,0,0,-100,200],crs='EPSG:3857'),territory=dict(bbox_wgs84=[0,0,.01,.01]),options=dict(duration_s=1800),valid_from='2026-10-19T12:00:00Z',valid_until='2026-10-19T12:30:00Z')));(job/'manifest.json').write_text(json.dumps(dict(artifacts={n:sha256(job/n) for n in ['fire-output.npz','fire-series.json']})))
   feature=dict(type='Feature',id='fixture',properties=dict(category='settlement'),geometry=dict(type='Point',coordinates=[.000449157642,.001347472926]))
   with patch('hazardia.territorial_context.acquire',return_value=dict(features=[feature])):data=assess(root,'job-test')
   e=data['features'][0]['exposure'];self.assertEqual(e['cells'],1);self.assertEqual(e['first_contact_minutes'],1);self.assertEqual(e['median_contact_minutes'],1.5);self.assertEqual(e['timeline_mean'],[0,1,1]);self.assertEqual(e['probability_final_mean'],1);self.assertEqual(e['timeline_contact'],[0,1,1]);self.assertEqual(e['probability_contact_final'],1)
   (job/'fire-series.json').write_text('{}')
   with self.assertRaises(HazardError):assess(root,'job-test')
if __name__=='__main__':unittest.main()

class CatalogTests(unittest.TestCase):
 def test_all_health_tags_preserved_and_unknown_not_discarded(self):
  tags={'healthcare':'laboratory','healthcare:speciality':'blood_check','beds':'12','wheelchair':'yes','opening_hours':'24/7','name':'Lab <test>'}
  raw=dict(elements=[dict(type='node',id=1,lat=42,lon=13,tags=tags),dict(type='node',id=2,lat=42,lon=13,tags={'future:custom':'value'})])
  f,n=parse_osm(raw);self.assertEqual(n,0);self.assertEqual(len(f),2);self.assertEqual(f[0]['properties']['catalog_group'],'healthcare');self.assertEqual(f[0]['properties']['osm_tags'],tags);self.assertEqual(f[1]['properties']['catalog_group'],'other');self.assertFalse(f[1]['properties']['optimization_eligible']);self.assertFalse(f[1]['properties']['exposure_eligible'])
 def test_incomplete_way_not_silently_joined(self):
  raw=dict(elements=[dict(type='node',id=1,lat=42,lon=13),dict(type='node',id=3,lat=43,lon=14),dict(type='way',id=2,nodes=[1,2,3],tags={'highway':'primary'})])
  f,n=parse_osm(raw);self.assertEqual(f,[]);self.assertEqual(n,1)
 def test_relation_hole_and_missing_geometry_proxy(self):
  outer=[dict(lon=x,lat=y) for x,y in [(13,42),(14,42),(14,43),(13,43),(13,42)]];inner=[dict(lon=x,lat=y) for x,y in [(13.2,42.2),(13.4,42.2),(13.4,42.4),(13.2,42.2)]]
  raw=dict(elements=[dict(type='relation',id=1,tags={'type':'multipolygon','amenity':'hospital'},members=[dict(type='way',role='outer',geometry=outer),dict(type='way',role='inner',geometry=inner)]),dict(type='relation',id=2,tags={'type':'multipolygon','healthcare':'clinic'},center=dict(lon=13,lat=42),members=[dict(type='way',ref=999,role='outer')])])
  f,n=parse_osm(raw);self.assertEqual(f[0]['geometry']['type'],'MultiPolygon');self.assertEqual(len(f[0]['geometry']['coordinates'][0]),2);self.assertEqual(f[1]['properties']['geometry_quality'],'CENTER_PROXY_GEOMETRY_MISSING');self.assertFalse(f[1]['properties']['exposure_eligible'])
 def test_no_resource_assumption_from_mapped_hospital(self):
  f,_=parse_osm(dict(elements=[dict(type='node',id=1,lat=42,lon=13,tags={'amenity':'hospital'})]));self.assertNotIn('beds',f[0]['properties']['osm_tags']);self.assertNotIn('available',f[0]['properties'])
