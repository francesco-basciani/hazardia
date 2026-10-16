import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from hazardia.ingest.http import Cache
from hazardia.io import HazardError

class Response:
    url='https://example.test/data';status=200
    def __init__(self,body,declared=None):
        self.body=body;self.headers={'Content-Type':'application/octet-stream','Set-Cookie':'private=discard'}
        if declared is not None:self.headers['Content-Length']=str(declared)
        self.reads=0
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,size):
        self.reads+=1;part=self.body[:size];self.body=self.body[size:];return part

class CacheTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.cache=Cache(self.root,budget_bytes=10)
    def tearDown(self):self.tmp.cleanup()
    def test_rejects_declared_oversize_before_body_and_streaming_oversize(self):
        for declared in [11,None]:
            response=Response(b'x'*11,declared)
            with patch('urllib.request.urlopen',return_value=response):
                with self.assertRaises(HazardError) as exc:self.cache.fetch('data',response.url,cap=10)
            self.assertEqual(exc.exception.code,'DOWNLOAD_BUDGET');self.assertFalse((self.root/'data').exists());self.assertFalse((self.root/'data.partial').exists())
            if declared:self.assertEqual(response.reads,0)
    def test_verified_warm_reuse_and_corruption_rejection(self):
        response=Response(b'data',4)
        with patch('urllib.request.urlopen',return_value=response):cold=self.cache.fetch('data',response.url)
        with patch('urllib.request.urlopen') as network:
            warm=self.cache.fetch('data',response.url);network.assert_not_called()
        self.assertFalse(cold['cache_hit']);self.assertTrue(warm['cache_hit']);self.assertNotIn('Set-Cookie',warm['headers'])
        (self.root/'data').write_bytes(b'bad')
        with self.assertRaises(HazardError) as exc:self.cache.fetch('data',response.url)
        self.assertEqual(exc.exception.code,'CACHE_CORRUPT')
    def test_snapshot_refresh_and_unsafe_sources_are_rejected(self):
        for url in ['http://example.test/a','https://user:secret@example.test/a']:
            with self.assertRaises(HazardError) as exc:self.cache.fetch('data',url)
            self.assertEqual(exc.exception.code,'SOURCE_URL')
        with patch('urllib.request.urlopen',return_value=Response(b'data',4)):self.cache.fetch('data',Response.url)
        with self.assertRaises(HazardError) as exc:self.cache.fetch('data',Response.url,refresh=True)
        self.assertEqual(exc.exception.code,'IMMUTABLE_CACHE')
