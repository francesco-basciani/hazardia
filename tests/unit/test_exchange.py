"""Synthetic metadata/bytes only; never a physical product or a new domain model."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from hazardia.exchange import validate_product,validate_requirement,check_compatibility
from hazardia.io import HazardError,sha256


def known(value):return dict(state='KNOWN',value=value,reason='Synthetic declared metadata')
def unknown():return dict(state='UNKNOWN',value=None,reason='Not available in synthetic fixture')


def fixture(root):
    root=Path(root);(root/'values.bin').write_bytes(b'FIXTURE_NOT_A_RASTER');(root/'source.json').write_text('{}')
    grid=dict(shape=[2,3],crs='EPSG:32633',axis_order='X_Y',transform=[30,0,500000,0,-30,4700000],nodata=-9999,horizontal_unit=known('m'),vertical_datum=known('TEST_DATUM'))
    variable=dict(id='temperature',quantity='urn:test:air-temperature',unit='degC',support='FIXTURE_WINDOW_VALUE',uncertainty=dict(kind='NOT_QUANTIFIED',members=None,calibration=unknown(),note='Synthetic fixture, not observations'),asset=dict(path='values.bin',sha256=sha256(root/'values.bin')),statistics=dict(minimum=-20,maximum=10,valid_cells=6,positive_cells=3))
    product=dict(schema='hazardia.exchange-product/0.1.0',id='test-product',domain_id='test.environmental-example',origin='OBSERVED',qualification='SYNTHETIC_FIXTURE',grid=grid,time=dict(valid_from='2024-07-13T00:00:00Z',valid_until='2024-07-13T01:00:00Z',source_cutoff='2024-07-13T00:00:00Z',available_at=known('2024-07-13T01:00:00Z')),variables=[variable],provenance=dict(records=[dict(role='source',asset=dict(path='source.json',sha256=sha256(root/'source.json')))],license=unknown(),engine=dict(state='NOT_APPLICABLE',reason='Synthetic observation fixture has no engine')),assumptions=['SYNTHETIC METADATA ONLY; NOT A DOMAIN SIMULATOR'])
    need=dict(schema='hazardia.exchange-requirement/0.1.0',domain_id=product['domain_id'],allowed_origins=['OBSERVED'],allowed_qualifications=['SYNTHETIC_FIXTURE'],grid=copy.deepcopy(grid),time=dict(valid_from=product['time']['valid_from'],valid_until=product['time']['valid_until'],as_of='2024-07-13T02:00:00Z'),variables=[dict(id=variable['id'],quantity=variable['quantity'],unit=variable['unit'],support=variable['support'],accepted_uncertainty=['NOT_QUANTIFIED'],require_known_calibration=False,minimum_members=None)],require_known_license=False,maximum_age_s=3600)
    return product,need


class ExchangeTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.p,self.r=fixture(self.root)
    def tearDown(self):self.tmp.cleanup()
    def test_domain_independent_round_trip_no_mutation(self):
        before=copy.deepcopy((self.p,self.r));validate_product(self.p,self.root);validate_requirement(self.r)
        result=check_compatibility(self.p,self.r,root=self.root)
        self.assertEqual(result['status'],'COMPATIBLE');self.assertTrue(result['asset_hashes_verified']);self.assertFalse(result['operationally_approvable']);self.assertEqual((self.p,self.r),before)
        self.p['domain_id']=self.r['domain_id']='another.domain'
        self.assertEqual(check_compatibility(self.p,self.r)['status'],'COMPATIBLE')
    def test_metadata_match_is_not_a_claim_of_verified_bytes(self):
        self.assertFalse(check_compatibility(self.p,self.r)['asset_hashes_verified'])
    def test_semantic_units_support_origin_and_qualification_mismatch(self):
        for path,value in [('unit','K'),('quantity','urn:test:different-quantity'),('support','INSTANTANEOUS')]:
            r=copy.deepcopy(self.r);r['variables'][0][path]=value;self.assertEqual(check_compatibility(self.p,r)['status'],'INCOMPATIBLE')
        for path,value in [('domain_id','other'),('allowed_origins',['SIMULATED']),('allowed_qualifications',['OPERATIONAL'])]:
            r=copy.deepcopy(self.r);r[path]=value;self.assertEqual(check_compatibility(self.p,r)['status'],'INCOMPATIBLE')
    def test_grid_mismatch_never_reprojects_or_resamples(self):
        for path,value in [('crs','EPSG:4326'),('shape',[3,2]),('transform',[60,0,500000,0,-60,4700000]),('nodata',-1)]:
            r=copy.deepcopy(self.r);r['grid'][path]=value;self.assertEqual(check_compatibility(self.p,r)['status'],'INCOMPATIBLE')
    def test_unknown_spatial_references_are_not_assumed_equal(self):
        for field in ['horizontal_unit','vertical_datum']:
            p=copy.deepcopy(self.p);p['grid'][field]=unknown();self.assertEqual(check_compatibility(p,self.r)['status'],'UNKNOWN')
        self.r['grid']['vertical_datum']=dict(state='NOT_APPLICABLE',value=None,reason='Consumer explicitly needs no absolute vertical reference')
        self.p['grid']['vertical_datum']=unknown();self.assertEqual(check_compatibility(self.p,self.r)['status'],'COMPATIBLE')
    def test_unknown_license_calibration_members_and_availability(self):
        r=copy.deepcopy(self.r);r['require_known_license']=True;self.assertEqual(check_compatibility(self.p,r)['status'],'UNKNOWN')
        r=copy.deepcopy(self.r);r['variables'][0]['require_known_calibration']=True;self.assertEqual(check_compatibility(self.p,r)['status'],'UNKNOWN')
        r=copy.deepcopy(self.r);r['variables'][0]['minimum_members']=3;self.assertEqual(check_compatibility(self.p,r)['status'],'UNKNOWN')
        p=copy.deepcopy(self.p);p['time']['available_at']=unknown();self.assertEqual(check_compatibility(p,self.r)['status'],'UNKNOWN')
    def test_explicit_uncertainty_kind_and_sample_count(self):
        r=copy.deepcopy(self.r);r['variables'][0]['accepted_uncertainty']=['EMPIRICAL_FREQUENCY'];self.assertEqual(check_compatibility(self.p,r)['status'],'INCOMPATIBLE')
        self.p['variables'][0]['uncertainty']['members']=2;self.r['variables'][0]['minimum_members']=3
        self.assertEqual(check_compatibility(self.p,self.r)['status'],'INCOMPATIBLE')
    def test_exact_window_future_cutoff_and_stale_data(self):
        for field,value in [('valid_from','2024-07-13T00:30:00Z'),('valid_until','2024-07-13T00:45:00Z'),('as_of','2024-07-13T00:30:00Z'),('as_of','2024-07-13T03:00:00Z')]:
            r=copy.deepcopy(self.r);r['time'][field]=value;self.assertEqual(check_compatibility(self.p,r)['status'],'INCOMPATIBLE')
    def test_nonfinite_fields_duplicates_and_invalid_knowledge(self):
        variants=[]
        p=copy.deepcopy(self.p);p['grid']['nodata']=float('nan');variants.append(p)
        p=copy.deepcopy(self.p);p['variables']*=2;variants.append(p)
        p=copy.deepcopy(self.p);p['provenance']['license']['value']='invented';variants.append(p)
        p=copy.deepcopy(self.p);p['extra']=True;variants.append(p)
        p=copy.deepcopy(self.p);p['grid']['transform'][1]=.1;variants.append(p)
        for p in variants:
            with self.assertRaises(HazardError):validate_product(p)
    def test_asset_integrity_and_path_escape(self):
        (self.root/'values.bin').write_bytes(b'CHANGED')
        with self.assertRaises(HazardError) as e:validate_product(self.p,self.root)
        self.assertEqual(e.exception.code,'CHECKSUM')
        self.p['variables'][0]['asset']['path']='../outside'
        with self.assertRaises(HazardError) as e:validate_product(self.p,self.root)
        self.assertEqual(e.exception.code,'ASSET_PATH')
    def test_cli_unknowns_and_bounded_read_only_inspection(self):
        path=self.root/'product.json';path.write_text(json.dumps(self.p));req=self.root/'need.json';req.write_text(json.dumps(self.r))
        a=subprocess.run([sys.executable,'-B','-m','hazardia.exchange','--product',str(path),'--root',str(self.root)],text=True,capture_output=True)
        self.assertEqual(a.returncode,0,a.stderr);self.assertIn('provenance.license',json.loads(a.stdout)['unknown_fields'])
        self.r['require_known_license']=True;req.write_text(json.dumps(self.r))
        b=subprocess.run([sys.executable,'-B','-m','hazardia.exchange','--product',str(path),'--requirement',str(req)],text=True,capture_output=True)
        self.assertEqual(b.returncode,3,b.stderr);self.assertEqual(json.loads(b.stdout)['status'],'UNKNOWN')
    def test_public_facade_preserves_legacy_and_exposes_generic_contracts(self):
        import hazardia.contracts as public
        from hazardia.adapters import legacy_contracts
        self.assertIs(public.validate_request,legacy_contracts.validate_request)
        self.assertIs(public.validate_product,legacy_contracts.validate_product)
        self.assertIs(public.validate_exchange_product,validate_product)
        self.assertEqual(public.check_exchange_compatibility(self.p,self.r)['status'],'COMPATIBLE')
        self.assertTrue((public.SCHEMAS/'simulation_request.schema.json').exists())

    def test_schema_resolution_is_local_and_preserves_named_properties(self):
        from hazardia.exchange.contracts import _local_schema
        with patch('urllib.request.urlopen',side_effect=AssertionError('no remote resolution')) as network:
            validate_product(self.p,self.root);validate_requirement(self.r);network.assert_not_called()
        for schema in [{'$ref':'https://example.invalid/schema'}, {'definitions':{'x':{'$ref':'#/definitions/x'}},'$ref':'#/definitions/x'}]:
            with self.assertRaises(HazardError):_local_schema(schema)
        schema={'properties':{'definitions':{'type':'string'}}}
        self.assertEqual(_local_schema(schema),schema)

    def test_core_has_no_legacy_hazard_enum_or_simulator_imports(self):
        root=Path(__file__).resolve().parents[2]/'src/hazardia/exchange'
        for p in root.glob('*.py'):
            source=p.read_text()
            for forbidden in ['FIRE','FLOOD','propagator','rasterio','numpy','highspy']:
                self.assertNotIn(forbidden,source)
