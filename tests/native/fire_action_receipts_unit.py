"""Execute with the pinned fire environment and source path in the Linux VM."""
import unittest
import numpy as np
from affine import Affine
from pyproj import CRS,Transformer
from propagator.io.geo import GeographicInfo
from propagator.io.boundary_conditions import TimedInput
from propagator.io.actions import ACTION_CLASSES
from shapely.geometry import LineString
from hazardia.adapters.workers.fire_action_receipts import action_receipt

class ReceiptTest(unittest.TestCase):
 def setUp(self):
  self.geo=GeographicInfo(crs=CRS.from_epsg(3857),trans=Affine(30,0,1500000,0,-30,5300000),bounds=(1500000,5299700,1500300,5300000),shape=(10,10))
  tr=Transformer.from_crs(3857,4326,always_xy=True)
  self.points=[[tr.transform(x,5299850)[1],tr.transform(x,5299850)[0]] for x in (1500090,1500210)]
  self.veg=np.full((10,10),5)
 def test_each_native_category_matches_applied_boundary_conditions(self):
  for category in ACTION_CLASSES:
   with self.subTest(category=category):
    u=dict(id='unit',category=category,effect='native',line=self.points,at_minutes=0)
    receipt=action_receipt(u,self.geo,self.veg,0)
    action=ACTION_CLASSES[category](geometries=[LineString([(p[1],p[0]) for p in self.points])],epsg=4326)
    bc=TimedInput(time=0,actions=[action]).get_boundary_conditions(self.geo,0)
    affected=np.zeros((10,10),dtype=bool)
    if bc.additional_moisture is not None:affected|=np.isfinite(bc.additional_moisture)&(bc.additional_moisture!=0)
    if bc.vegetation_changes is not None:affected|=np.isfinite(bc.vegetation_changes)
    self.assertGreater(receipt['affected_cells'],0);self.assertEqual(receipt['affected_cells'],int(affected.sum()))
    self.assertEqual(receipt,action_receipt(u,self.geo,self.veg,0))
 def test_no_initial_fuel_does_not_become_protection_claim(self):
  u=dict(id='u',category='canadair',effect='native',line=self.points,at_minutes=0)
  r=action_receipt(u,self.geo,np.zeros((10,10)),0)
  self.assertGreater(r['affected_cells'],0);self.assertEqual(r['initial_fuel_cells'],0)
 def test_ideal_barrier_matches_geometry_cells(self):
  u=dict(id='u',category='waterline_action',effect='fuel_removal',line=self.points,at_minutes=0)
  r=action_receipt(u,self.geo,self.veg,0)
  self.assertEqual(r['geometry_cells'],r['affected_cells']);self.assertIsNone(r['added_moisture_percent_range'])
if __name__=='__main__':unittest.main()
