"""Geospatial display correctness fixture, not radar skill/calibration."""
import tempfile,unittest
from pathlib import Path
import numpy as np,rasterio
from rasterio.transform import from_origin
from PIL import Image
from hazardia.web.radar_worker import render,validate_product_url
class RadarRender(unittest.TestCase):
 def test_provider_cannot_substitute_time_or_host(self):
  import datetime as dt
  at=dt.datetime(2026,10,23,9,tzinfo=dt.timezone.utc).timestamp()*1000
  correct='https://s3-prod-dpc-radar.s3.eu-south-1.amazonaws.com/SRI/23-10-2026-09-00.tif'
  self.assertEqual(validate_product_url(correct,at).path,'/SRI/23-10-2026-09-00.tif')
  for bad in [correct.replace('09-00','09-05'),correct.replace('s3-prod-dpc-radar.s3.eu-south-1.amazonaws.com','example.org'),correct.replace('https:','http:')]:
   with self.assertRaises(ValueError):validate_product_url(bad,at)
 def test_missing_is_distinct_from_dry_and_wet_is_visible(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);source=out/'fixture.tif';a=np.zeros((30,30),dtype='float32');a[:10,:]=-9999;a[10:20,:]=5
   with rasterio.open(source,'w',driver='GTiff',height=30,width=30,count=1,dtype='float32',crs='EPSG:3857',transform=from_origin(1000000,5000000,1000,1000)) as r:r.write(a,1)
   result=render(source,out);rain=np.asarray(Image.open(out/'rain.png'));missing=np.asarray(Image.open(out/'missing.png'))
   self.assertGreater(result['wet_fraction'],0);self.assertLess(result['valid_fraction'],1);self.assertEqual(result['max_mm_h'],5);self.assertEqual(result['native_resolution_m'],[1000,1000]);self.assertGreater(rain[:,:,3].max(),0);self.assertEqual(rain[:,:,3].min(),0);self.assertGreater(missing[:,:,3].max(),0);self.assertFalse(np.any((rain[:,:,3]>0)&(missing[:,:,3]>0)))
if __name__=='__main__':unittest.main()
