import gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from hazardia.ingest.archive_storage import compact,read_bytes,stored_bytes,deduplicate
from hazardia.io import HazardError
from hazardia.ingest.attention import AttentionStore

class ArchiveStorageTests(unittest.TestCase):
 def test_roundtrip_and_duplicate_names_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);raw=json.dumps({'values':[42.5]*500}).encode()
   for name in ['a','b']:
    p=root/name;p.mkdir();(p/'data.json').write_bytes(raw)
   before=stored_bytes(root);compact(root.glob('*/*.json'));deduplicate(root.glob('*/*.gz'))
   self.assertLess(stored_bytes(root),before//2)
   for name in ['a','b']:self.assertEqual(read_bytes(root/name/'data.json'),raw)
   self.assertEqual((root/'a/data.json.gz').stat().st_ino,(root/'b/data.json.gz').stat().st_ino)
 def test_conflicting_gzip_is_not_overwritten(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'data.json';p.write_bytes(b'a'*1000);Path(str(p)+'.gz').write_bytes(gzip.compress(b'b'*1000))
   with self.assertRaises(HazardError):compact([p])
   self.assertEqual(p.read_bytes(),b'a'*1000)
 def test_bounded_expansion_and_corrupt_archive(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'data.json';q=Path(str(p)+'.gz');q.write_bytes(gzip.compress(b'a'*200))
   with self.assertRaises(HazardError):read_bytes(p,limit=100)
   q.write_bytes(b'invalid')
   with self.assertRaises(HazardError):read_bytes(p)
 def test_attention_can_serve_unchanged_hardlinked_archives(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=AttentionStore(tmp,tmp);raw=b'{"type":"FeatureCollection","features":[]}'
   for ident in ['a'*32,'b'*32]:
    p=Path(tmp)/('snapshot-'+ident);p.mkdir();(p/'dpc-2026-10-26.geojson').write_bytes(raw)
    data=json.dumps(dict(sources={},files={'dpc-2026-10-26.geojson':hashlib.sha256(raw).hexdigest()})).encode();(p/'result.json').write_bytes(data)
   store.write_state(dict(snapshot='snapshot-'+'b'*32,sha256=hashlib.sha256(data).hexdigest()))
   store.compact();self.assertEqual(store.layer('snapshot-'+'b'*32,'dpc-2026-10-26.geojson')['features'],[])
