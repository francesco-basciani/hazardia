import copy,json,tempfile,unittest
from pathlib import Path
from hazardia.io import HazardError,loads,write_new,load,sha256
from hazardia.contracts import validate_request,validate_weather,migrate_observation_010
from hazardia.ingest.providers import LocalSnapshotProvider,StacProvider
from tests.support import fixture

class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.request,self.weather=fixture(self.root)
    def tearDown(self):self.temp.cleanup()
    def reject(self,code,fn):
        with self.assertRaises(HazardError) as caught:fn()
        self.assertEqual(caught.exception.code,code)
    def test_roundtrip_and_staging_hashes(self):
        value=loads(json.dumps(self.request));self.assertEqual(validate_request(value,self.root),self.request)
    def test_strict_json_duplicate_nan_infinity(self):
        for raw in ['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}']:
            self.reject('INVALID_JSON',lambda:loads(raw))
    def test_unknown_fields_and_versions_rejected(self):
        for field,value in [('schema_version','0.1.0'),('unexpected',True)]:
            v=copy.deepcopy(self.request);v[field]=value;self.reject('INVALID_CONTRACT',lambda:validate_request(v))
    def test_critical_missing_values_rejected(self):
        for field in ['territory','grid','snapshot_at','assets','assumptions']:
            v=copy.deepcopy(self.request);v[field]=None;self.reject('INVALID_CONTRACT',lambda:validate_request(v))
    def test_negative_grid_and_impossible_calendar(self):
        v=copy.deepcopy(self.request);v['grid']['transform'][0]=-30;self.reject('GRID_MISMATCH',lambda:validate_request(v))
        v=copy.deepcopy(self.request);v['valid_from']='2024-02-30T13:00:00Z';self.reject('INVALID_TIME',lambda:validate_request(v))
    def test_bad_timezone_bbox_and_grid_identity(self):
        v=copy.deepcopy(self.request);v['territory']['timezone']='Moon/Sea';self.reject('INVALID_PROFILE',lambda:validate_request(v))
        v=copy.deepcopy(self.request);v['territory']['bbox_wgs84']=[14,42,13,43];self.reject('INVALID_PROFILE',lambda:validate_request(v))
        v=copy.deepcopy(self.request);v['grid']['crs']='EPSG:4326';self.reject('GRID_MISMATCH',lambda:validate_request(v))
    def test_unit_unsupported_and_missing_weather(self):
        for field,value in [('wind_speed_10m','km/h'),('precipitation','kg')]:
            v=copy.deepcopy(self.weather);v['units'][field]=value;self.reject('SOURCE_UNIT',lambda:validate_weather(v,self.request))
        v=copy.deepcopy(self.weather);v['records'][0]['values']['precipitation']=None;self.reject('SOURCE_MISSING',lambda:validate_weather(v,self.request))
    def test_forecast_issue_and_future_availability(self):
        v=copy.deepcopy(self.weather);v['data_kind']='FORECAST';self.reject('INVALID_TIME',lambda:validate_weather(v,self.request))
        v=copy.deepcopy(self.weather);v['available_at']='2025-01-01T00:00:00Z';self.reject('FUTURE_SOURCE',lambda:validate_weather(v,self.request))
    def test_weather_stale_duplicate_and_out_of_range(self):
        v=copy.deepcopy(self.weather);v['valid_until']='2024-07-13T13:00:00Z';self.reject('STALE_FORECAST',lambda:validate_weather(v,self.request))
        v=copy.deepcopy(self.weather);v['records'][1]['at']=v['records'][0]['at'];self.reject('SOURCE_TIME',lambda:validate_weather(v,self.request))
        v=copy.deepcopy(self.weather);v['records'][0]['values']['relative_humidity_2m']=101;self.reject('SOURCE_RANGE',lambda:validate_weather(v,self.request))
    def test_missing_hour_must_not_be_silently_interpolated(self):
        v=copy.deepcopy(self.weather);del v['records'][13];self.reject('SOURCE_TIME',lambda:validate_weather(v,self.request))
    def test_declared_duration_matches_product_window(self):
        v=copy.deepcopy(self.request);v['valid_until']='2024-07-13T14:00:00Z';self.reject('INVALID_TIME',lambda:validate_request(v))
    def test_checksum_and_path_escape(self):
        (self.root/'dem.tif').write_bytes(b'changed');self.reject('CHECKSUM',lambda:validate_request(self.request,self.root))
        v=copy.deepcopy(self.request);v['assets'][0]['path']='../outside';self.reject('ASSET_PATH',lambda:validate_request(v,self.root))
    def test_immutable_json_publication(self):
        p=self.root/'manifest.json';write_new(p,{'value':1})
        with self.assertRaises(FileExistsError):write_new(p,{'value':2})
        self.assertEqual(load(p),{'value':1})
    def test_explicit_migration_preserves_provenance(self):
        old=dict(schema_version='0.1.0',kind='observation',id='obs',provenance=dict(source='synthetic metadata',license='SYNTHETIC'),payload=dict(territory_id='territory',sensed_at='2024-07-13T12:00:00Z',available_at='2024-07-13T12:01:00Z',ingested_at='2024-07-13T12:02:00Z',footprint_bbox=[13,42,14,43],crs='EPSG:4326',resolution_m=10,coverage_fraction=1,quality='VALID',asset=dict(path='dem.tif',sha256='0'*64)))
        new=migrate_observation_010(old);self.assertEqual(new['asset'],old['payload']['asset']);self.assertEqual(new['sensed_at'],old['payload']['sensed_at']);self.assertEqual(new['schema_version'],'0.2.0');self.assertTrue(new['migration']['metadata_only'])
    def test_local_source_replacement_preserves_weather_contract(self):
        # Same normalized contract accepted through a different concrete source provider.
        other=LocalSnapshotProvider(self.root/'weather.json').acquire();self.assertEqual(other,self.weather);validate_weather(other,self.request)
    def test_stac_partial_coverage_is_rejected(self):
        items={'features':[{'id':'partial','bbox':[13,42,13.5,43],'properties':{'eo:cloud_cover':0}}]}
        self.reject('SOURCE_COVERAGE',lambda:StacProvider.choose_covering(items,[13,42,14,43]))
    def test_product_units_and_provenance_are_not_trusted(self):
        from hazardia.contracts import validate_product
        req=self.request
        product=dict(schema_version='0.2.0',kind='hazard_product',job_id='unit',request_id=req['id'],hazard='FIRE',qualification='UNQUALIFIED_RESEARCH',grid=req['grid'],valid_from=req['valid_from'],valid_until=req['valid_until'],engine=dict(name='UNIT_DOUBLE',source_commit='UNIT_ONLY',patch_sha256=None),layers=[dict(name=n,unit=u,path='unit.tif',sha256='0'*64,statistics=dict(valid_cells=6,positive_cells=1,minimum=0,maximum=1)) for n,u in [('FIRE_PROBABILITY','1'),('ARRIVAL_TIME','s')]],assumptions=['UNIT'],input_hashes=[dict(role=v['role'],sha256=v['sha256']) for v in req['assets']],validation=dict(status='PASS',scope='TECHNICAL_CONTENT_ONLY'))
        validate_product(product,req)
        bad=copy.deepcopy(product);bad['layers'][0]['unit']='m';self.reject('PRODUCT_UNIT',lambda:validate_product(bad,req))
        bad=copy.deepcopy(product);bad['input_hashes'][0]['sha256']='0'*64;self.reject('PRODUCT_MISMATCH',lambda:validate_product(bad,req))
        bad=copy.deepcopy(product);bad['valid_until']='2024-07-13T14:00:00Z';self.reject('PRODUCT_MISMATCH',lambda:validate_product(bad,req))
    def test_legacy_run_manifest_migration_retains_unknowns_and_outcome(self):
        from hazardia.contracts import migrate_run_manifest_020,validate
        old=dict(schema_version='0.2.0',kind='run_manifest',run_id='legacy',parent_job=None,request_id=self.request['id'],status='ERROR',error_code='INVALID_OUTPUT',detail='Original failed output',started_at='2024-07-13T13:00:00Z',ended_at='2024-07-13T13:00:01Z',metrics={},artifacts={},qualification='UNQUALIFIED_RESEARCH',code=dict(git_sha='0'*40,dirty=False,source_sha256={}))
        self.reject('INVALID_CONTRACT',lambda:validate('run_manifest',old))
        new=migrate_run_manifest_020(old,self.request,'1'*64);self.assertEqual(new['status'],'ERROR');self.assertEqual(new['environment']['status'],'UNKNOWN_LEGACY_ENVIRONMENT');self.assertEqual(old['schema_version'],'0.2.0');self.assertEqual(new['schema_version'],'0.3.0')
