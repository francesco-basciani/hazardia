import unittest,tempfile
from hazardia.web.recent_imagery import thumbnail_url,RecentImagery
class ImageryTest(unittest.TestCase):
 def test_thumbnail_allowlist(self):
  for host in ['datahub','zipper']:self.assertEqual(thumbnail_url('https://'+host+'.creodias.eu/odata/v1/Assets(2eec3e78-b936-492d-8614-2ae151a95307)/$value'),'https://'+host+'.creodias.eu/odata/v1/Assets(2eec3e78-b936-492d-8614-2ae151a95307)/$value')
 def test_no_arbitrary_urls(self):
  for u in ['http://datahub.creodias.eu/x','https://evil.invalid/','http://127.0.0.1/','https://datahub.creodias.eu.evil.invalid/odata/v1/Assets(2eec3e78-b936-492d-8614-2ae151a95307)/$value']:
   with self.assertRaises(ValueError):thumbnail_url(u)
 def test_local_state_and_image_path(self):
  with tempfile.TemporaryDirectory() as d:
   service=RecentImagery(d);self.assertEqual(service.snapshot()['status'],'IDLE')
   with self.assertRaises(Exception):service.image('../../etc/passwd')
 def test_bounds(self):
  with tempfile.TemporaryDirectory() as d:
   service=RecentImagery(d)
   for body in [{},{'bounds':[0,0,2,2]},{'bounds':[0,0,1,1],'url':'https://evil.invalid'}]:
    with self.assertRaises(Exception):service.prepare(body)
if __name__=='__main__':unittest.main()
