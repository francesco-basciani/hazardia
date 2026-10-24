"""Synthetic metadata/bytes fixture for the legacy boundary, not native CIMA."""
import copy
from pathlib import Path
import tempfile
import unittest
from hazardia.adapters.legacy_exchange import export_legacy_product,write_legacy_exchange
from hazardia.exchange import validate_product
from hazardia.io import write_new,load,sha256,HazardError
from tests.support import fixture


def prepared(root,hazard='FIRE'):
    root=Path(root);req,_=fixture(root)
    if hazard=='FLOOD':
        req.update(hazard=hazard,valid_until='2024-07-13T15:00:00Z',options=dict(hours=2,rain_mm=[0,0,0],q0_m3_s=0,q0_evidence='SYNTHETIC_RESEARCH_REFERENCE',flow_threshold_cells=1,allow_experimental_patch=True))
        req['grid'].update(crs='EPSG:4326',transform=[.001,0,13,0,-.001,43]);req['territory']['work_crs']='EPSG:4326'
    write_new(root/'request.json',req)
    specs=[('FIRE_PROBABILITY','1'),('ARRIVAL_TIME','s')] if hazard=='FIRE' else [('MAXIMUM_DEPTH','m')]
    layers=[]
    for name,unit in specs:
        path=root/(name+'.bin');path.write_bytes(b'SYNTHETIC_NOT_A_RASTER')
        layers.append(dict(name=name,unit=unit,path=path.name,sha256=sha256(path),statistics=dict(minimum=0,maximum=.5,valid_cells=6,positive_cells=2)))
    p=dict(schema_version='0.2.0',kind='hazard_product',job_id='fixture',request_id=req['id'],hazard=hazard,qualification='UNQUALIFIED_RESEARCH',grid=copy.deepcopy(req['grid']),valid_from=req['valid_from'],valid_until=req['valid_until'],engine=dict(name='SYNTHETIC',source_commit='test-not-an-upstream-claim',patch_sha256=None),layers=layers,assumptions=['SYNTHETIC TEST, NOT A PHYSICAL PRODUCT'],input_hashes=[dict(role=a['role'],sha256=a['sha256']) for a in req['assets']],validation=dict(status='PASS',scope='TECHNICAL_CONTENT_ONLY'))
    write_new(root/'product.json',p);return req,p


class LegacyExchangeTests(unittest.TestCase):
    def test_views_preserve_legacy_hashes_paths_units_and_unknowns(self):
        for hazard in ['FIRE','FLOOD']:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);req,p=prepared(root,hazard);before={str(x):sha256(x) for x in root.iterdir() if x.is_file()}
                view=export_legacy_product(root);validate_product(view,root)
                self.assertEqual(view['time']['available_at']['state'],'UNKNOWN')
                self.assertEqual(view['provenance']['license']['state'],'UNKNOWN')
                self.assertEqual(view['grid']['horizontal_unit']['value'],'m' if hazard=='FIRE' else 'degree')
                self.assertEqual(view['qualification'],'UNQUALIFIED_RESEARCH')
                self.assertEqual([(v['id'],v['unit'],v['asset']['sha256']) for v in view['variables']],[(l['name'],l['unit'],l['sha256']) for l in p['layers']])
                self.assertEqual({str(x):sha256(x) for x in root.iterdir() if x.is_file()},before)
    def test_semantics_are_not_interchangeable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);prepared(root);v=export_legacy_product(root)['variables']
            self.assertEqual(v[0]['uncertainty']['kind'],'EMPIRICAL_FREQUENCY')
            self.assertEqual(v[0]['support'],'CUMULATIVE_REACHED_AT_HORIZON')
            self.assertEqual(v[1]['support'],'EARLIEST_REALIZATION_OFFSET_FROM_WINDOW_START')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);prepared(root,'FLOOD');v=export_legacy_product(root)['variables'][0]
            self.assertEqual(v['support'],'WINDOW_MAXIMUM');self.assertIsNone(v['uncertainty']['members']);self.assertEqual(v['uncertainty']['kind'],'NOT_QUANTIFIED')
    def test_new_execution_sidecar_is_exclusive_and_legacy_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);prepared(root);old=sha256(root/'product.json');value=write_legacy_exchange(root)
            self.assertEqual(value['time']['available_at']['state'],'KNOWN');self.assertEqual(sha256(root/'product.json'),old)
            saved=sha256(root/'exchange-product.json')
            with self.assertRaises(FileExistsError):write_legacy_exchange(root)
            self.assertEqual(sha256(root/'exchange-product.json'),saved)
    def test_old_validator_rejection_is_not_weakened(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);prepared(root);p=load(root/'product.json');p['layers'][0]['unit']='m';(root/'product.json').write_text(__import__('json').dumps(p))
            with self.assertRaises(HazardError) as e:export_legacy_product(root)
            self.assertEqual(e.exception.code,'PRODUCT_UNIT')
