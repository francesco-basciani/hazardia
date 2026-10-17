import json,tempfile,unittest
from pathlib import Path
from hazardia.ingest.attention_worker import zone_summary,qualify_footprints

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
if __name__=='__main__':unittest.main()
