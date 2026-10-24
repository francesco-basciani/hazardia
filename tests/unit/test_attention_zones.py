import json,tempfile,unittest
from pathlib import Path
from hazardia.ingest.attention_worker import zone_summary,qualify_footprints,recover_official_shapes,geometry_coverage

def polygon(coords,**props):return dict(type='Feature',geometry=dict(type='Polygon',coordinates=[coords]),properties=props)
class ZonalTests(unittest.TestCase):
 def test_territory_max_mean_missing_invalid(self):
  cells=dict(features=[polygon([[0,0],[1,0],[1,1],[0,1],[0,0]],fwi=12,dc=300),polygon([[1,0],[2,0],[2,1],[1,1],[1,0]],fwi=40,dc=None),polygon([[5,5],[6,5],[6,6],[5,6],[5,5]],fwi=100,dc=800)])
  z=polygon([[0,0],[2,0],[2,1],[0,1],[0,0]],id='river',name='Bacino',source_geometry_valid=True)
  bad=polygon([[0,0],[2,1],[0,1],[2,0],[0,0]],id='bad',name='Invalid')
  empty=polygon([[8,8],[9,8],[9,9],[8,9],[8,8]],id='empty',name='No coverage')
  out=zone_summary(cells,dict(features=[z,bad,empty]))['features'];p=out[0]['properties']
  self.assertEqual(out[0]['geometry'],z['geometry']);self.assertEqual(p['fwi'],40);self.assertEqual(p['fwi_mean'],26);self.assertEqual(p['sample_count'],2);self.assertEqual(p['dc_samples'],1);self.assertEqual(p['level'],3)
  for f in out[1:]:self.assertIsNone(f['properties']['level'])
 def test_invalid_display_keeps_exact_valid_source(self):
  from unittest.mock import patch
  from shapely.geometry import Polygon,shape
  from shapely.geometry.base import BaseGeometry
  z=polygon([[0,0],[2,0],[2,1],[0,1],[0,0]],id='valid',name='Valid',level=1)
  original=shape(z['geometry']);bad=Polygon([[0,0],[2,1],[0,1],[2,0],[0,0]])
  with patch.object(BaseGeometry,'simplify',return_value=bad):f=qualify_footprints(dict(features=[z]))['features'][0]
  self.assertTrue(shape(f['geometry']).equals_exact(original,0));self.assertTrue(f['properties']['display_geometry_valid']);self.assertEqual(f['properties']['cartographic_simplification_degrees'],0);self.assertEqual(f['properties']['level'],1)
class OfficialGeometryTests(unittest.TestCase):
 def fixtures(self):
  z=polygon([[10,40],[11,41],[10,41],[11,40],[10,40]],id='z',name='Zona',level=1,levels={'Per rischio idraulico':0,'Per rischio temporali':1,'Per rischio idrogeologico':0})
  row=polygon([[10,40],[11,40],[11,41],[10,41],[10,40]],Nome_zona='Zona',Zona_all='TEST',Idraulico='NESSUNA ALLERTA',Temporali='ALLERTA GIALLA',Idrogeo='NESSUNA ALLERTA')
  return dict(features=[z]),row
 def test_valid_same_bulletin_fallback_preserves_level(self):
  geo,row=self.fixtures();self.assertEqual(recover_official_shapes(geo,[row],'pinned'),1);qualify_footprints(geo)
  p=geo['features'][0]['properties'];self.assertEqual(p['level'],1);self.assertTrue(p['source_geometry_valid']);self.assertFalse(p['topology_geometry_valid']);self.assertEqual(p['geometry_source_url'],'pinned')
  self.assertEqual(geometry_coverage(geo)['geometry_qualified_zones'],1)
 def test_invalid_alternative_stays_unqualified_with_bulletin(self):
  geo,row=self.fixtures();row['geometry']=geo['features'][0]['geometry'];self.assertEqual(recover_official_shapes(geo,[row],'pinned'),0);qualify_footprints(geo)
  p=geo['features'][0]['properties'];self.assertIsNone(p['level']);self.assertEqual(p['source_level'],1);self.assertEqual(geometry_coverage(geo)['bulletin_known_zones'],1)
 def test_mismatched_warning_or_name_rejected(self):
  geo,row=self.fixtures();row['properties']['Temporali']='ALLERTA ROSSA'
  with self.assertRaises(ValueError):recover_official_shapes(geo,[row],'pinned')
  geo,row=self.fixtures();row['properties']['Nome_zona']='Other'
  with self.assertRaises(ValueError):recover_official_shapes(geo,[row],'pinned')
  geo,row=self.fixtures();geo['features']*=2
  with self.assertRaises(ValueError):recover_official_shapes(geo,[row,row],'pinned')
 def test_distant_valid_geometry_never_substituted(self):
  geo,row=self.fixtures();row['geometry']['coordinates']=[[[12,40],[13,40],[13,41],[12,41],[12,40]]]
  self.assertEqual(recover_official_shapes(geo,[row],'pinned'),0)

if __name__=='__main__':unittest.main()
