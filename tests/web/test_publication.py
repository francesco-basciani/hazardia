import importlib.util,tempfile,unittest,subprocess
from pathlib import Path
spec=importlib.util.spec_from_file_location('publication',Path(__file__).resolve().parents[2]/'scripts/prepare_publication.py');pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
class PublicationTests(unittest.TestCase):
 def fixture(self,d,files):
  r=Path(d)/'repo';r.mkdir();subprocess.run(['git','init','-q',str(r)],check=True)
  for name,data in files.items():p=r/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
  for args in [['config','user.name','Fixture'],['config','user.email','fixture@example.invalid'],['add','-f','.'],['commit','-qm','Fixture']]:subprocess.run(['git','-C',str(r),*args],check=True)
  return r
 def test_exports_source_and_omits_private_state_media(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.fixture(d,{'app.py':'print(1)','.m0-runtime/ssh-key':'private-local-placeholder','view.png':'image-placeholder'});out=Path(d)/'public';v=pub.prepare(r,'HEAD',out)
   self.assertTrue((out/'app.py').exists());self.assertEqual(set(v['excluded_paths']),{'.m0-runtime/ssh-key','view.png'});self.assertFalse((out/'.git').exists())
 def test_rejects_embedded_private_key(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.fixture(d,{'app.py':'-----BEGIN '+'OPENSSH PRIVATE KEY-----'})
   with self.assertRaises(ValueError):pub.prepare(r,'HEAD',Path(d)/'public')
   self.assertFalse((Path(d)/'public').exists())
 def test_untracked_content_never_exported(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.fixture(d,{'app.py':'known'});(r/'private.txt').write_text('untracked');out=Path(d)/'public';pub.prepare(r,'HEAD',out);self.assertFalse((out/'private.txt').exists())
 def test_refuses_existing_destination(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.fixture(d,{'app.py':'known'});out=Path(d)/'existing';out.mkdir()
   with self.assertRaises(ValueError):pub.prepare(r,'HEAD',out)

 def test_regenerated_manifest_has_no_stale_self_hash(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.fixture(d,{'app.py':'known','PUBLICATION.json':'{}'});out=Path(d)/'public';result=pub.prepare(r,'HEAD',out)
   self.assertNotIn('PUBLICATION.json',result['files']);self.assertIn('PUBLICATION.json',result['excluded_paths'])
