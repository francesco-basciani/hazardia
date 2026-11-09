import unittest,tempfile,json,hashlib
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('evidence_pack',Path(__file__).resolve().parents[2]/'scripts/avalanche/evidence_pack.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
pack_closed,read_file=module.pack_closed,module.read_file
class PackTests(unittest.TestCase):
 def fixture(self,root,complete=True):
  p=root/'20261101T000000Z';p.mkdir();body=b'original source bytes\n'*100;(p/'code-worker.py').write_bytes(body);(p/'host-receipt.json').write_text(json.dumps(dict(archive_protocol_version=2,complete=complete,files={'code-worker.py':hashlib.sha256(body).hexdigest()})));return p,body
 def test_roundtrip_without_direct_copy(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p,body=self.fixture(root);reports=pack_closed(root);self.assertFalse((p/'code-worker.py').exists());self.assertEqual(read_file(root,'20261101T000000Z/code-worker.py'),body);self.assertEqual(reports[0]['files'],1);self.assertEqual(pack_closed(root),[])
 def test_unverified_or_inflight_is_preserved(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p,body=self.fixture(root,False);self.assertEqual(pack_closed(root),[]);self.assertEqual((p/'code-worker.py').read_bytes(),body)
 def test_mismatching_receipt_preserves_direct_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p,body=self.fixture(root);(p/'code-worker.py').write_bytes(b'changed');self.assertEqual(pack_closed(root),[]);self.assertEqual((p/'code-worker.py').read_bytes(),b'changed')
 def test_paths_cannot_escape_archive(self):
  with self.assertRaises(ValueError):read_file(Path('/tmp'),'../private')
