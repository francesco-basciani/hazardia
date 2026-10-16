"""Installer boundary checks; no network/system installation in these tests."""
import importlib.util,tempfile,unittest,tarfile,io,hashlib
from pathlib import Path
spec=importlib.util.spec_from_file_location('bootstrap',Path(__file__).resolve().parents[2]/'scripts/bootstrap.py');boot=importlib.util.module_from_spec(spec);spec.loader.exec_module(boot)
class BootstrapTests(unittest.TestCase):
 def test_verified_reuse_and_drift_rejection(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);src=r/'cache';src.write_bytes(b'known');h=hashlib.sha256(src.read_bytes()).hexdigest();boot.fetch('https://example.invalid/x',r/'out',h,20,src);self.assertEqual((r/'out').read_bytes(),b'known')
   (r/'out').write_bytes(b'changed')
   with self.assertRaises(RuntimeError):boot.fetch('https://example.invalid/x',r/'out',h,20,src)
 def test_archive_traversal_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)
   with tarfile.open(r/'bad.tar','w') as t:
    m=tarfile.TarInfo('../escaped');m.size=1;t.addfile(m,io.BytesIO(b'x'))
   with self.assertRaises(tarfile.TarError):boot.unpack(r/'bad.tar',r/'destination')
   self.assertFalse((r/'escaped').exists())
 def test_write_never_changes_existing_record(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.json';boot.write(p,{'a':1});boot.write(p,{'a':1})
   with self.assertRaises(RuntimeError):boot.write(p,{'a':2})
