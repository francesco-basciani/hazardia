import copy,tempfile,unittest
from pathlib import Path
from hazardia.web.notebook import Notebook,validate
from hazardia.io import HazardError

class NotebookTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.book=Notebook(self.tmp.name)
        self.empty=self.book.read()
    def test_persist_and_recover_history(self):
        body=dict(self.empty,annotations=[dict(name='Area',kind='area',points=[[42.35,13.38],[42.36,13.38],[42.36,13.39]])])
        saved=self.book.save(body);self.assertEqual(Notebook(self.tmp.name).read(),saved)
        self.book.save(dict(saved,annotations=[]))
        self.assertEqual(len(list(Path(self.tmp.name).glob('snapshot-*.json'))),2)
    def test_conflict_does_not_overwrite(self):
        self.book.save(self.empty)
        with self.assertRaises(HazardError):self.book.save(self.empty)
        self.assertEqual(self.book.read()['revision'],1)
    def test_reject_nonfinite_bounds_types_and_shape(self):
        for pts in [[[42.35,float('nan')]],[[0,0]],[[True,13.38]],[[42.35,13.38,1]]]:
            with self.subTest(pts=pts),self.assertRaises(HazardError):validate(dict(self.empty,annotations=[dict(name='x',kind='point',points=pts)]))
    def test_reject_unbounded_and_unknown_content(self):
        for body in [dict(self.empty,views=[{}]*21),dict(self.empty,annotations=[dict(name='a',kind='line',points=[[42.35,13.38]]*201)]),dict(self.empty,extra='x'),dict(self.empty,cases=[{'name':'x'}])]:
            with self.subTest(body=body),self.assertRaises(HazardError):validate(body)
    def test_text_stored_as_data_never_interpreted(self):
        a=dict(name='<img src=x onerror=alert(1)>',kind='point',points=[[42.35,13.38]])
        self.assertEqual(self.book.save(dict(self.empty,annotations=[a]))['annotations'][0]['name'],a['name'])
    def test_reject_executable_and_operational_case_fields(self):
        c=dict(name='test',hazard='FIRE',scenario='job-abc',resources=2,robust=50,road=True,transfer=False,disabled='',preparedness='')
        self.assertEqual(validate(dict(self.empty,cases=[c]))['cases'][0],c)
        with self.assertRaises(HazardError):validate(dict(self.empty,cases=[dict(c,dispatch=True)]))
        with self.assertRaises(HazardError):validate(dict(self.empty,cases=[dict(c,resources=True)]))
