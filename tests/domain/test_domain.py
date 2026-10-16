import copy,tempfile,unittest
from pathlib import Path
from hazardia.io import HazardError,load
from hazardia.domain.contracts import validate_record,select_weather
from hazardia.domain.events import associate
from hazardia.domain.state import snapshot,GeoIndex,identity
from hazardia.domain.consequences import constraint_inputs,check_route,impact_only
from tests.domain.fixtures import *

class Domain(unittest.TestCase):
    def reject(self,code,fn):
        with self.assertRaises(HazardError) as e:fn()
        self.assertEqual(e.exception.code,code)
    def test_all_seven_records_roundtrip(self):
        for value in [profile(),detection(),exposure(),resource(),road(),effect(),ensemble()]:self.assertEqual(validate_record(copy.deepcopy(value)),value)
    def test_versions_fields_and_nonfinite(self):
        for field,value in [('schema_version','0.2.0'),('extra',True)]:
            p=profile();p[field]=value;self.reject('INVALID_CONTRACT',lambda:validate_record(p))
        p=exposure();p['payload']['people']=float('nan');self.reject('INVALID_JSON',lambda:validate_record(p))
    def test_profile_bbox_timezone_and_calibration(self):
        for field,value,code in [('timezone','Moon/Sea','INVALID_PROFILE'),('bbox_wgs84',[14,42,13,43],'INVALID_GEOMETRY'),('calibration','DOCUMENTED','UNKNOWN_CALIBRATION')]:
            p=profile();p['payload'][field]=value;self.reject(code,lambda:validate_record(p))
    def test_duplicate_and_correlated_no_confidence_inflation(self):
        a=detection();b=detection('d2');result=associate([a,a,b],profile(),T)
        self.assertEqual(result['duplicate_count'],1);self.assertEqual(len(result['events']),1);self.assertEqual(result['events'][0]['confidence_score'],.8)
    def test_conflicting_sources_retained(self):
        result=associate([detection(),detection('d2',assessment='ABSENT',sensor='synthetic-radar',correlation_group='other',confidence=.6)],profile(),T)
        self.assertEqual(result['events'][0]['status'],'CONFLICT');self.assertEqual(len(result['events'][0]['observations']),2);self.assertEqual(result['events'][0]['confidence_score'],.6)
    def test_distinct_hazards_and_disjoint_areas_not_merged(self):
        r=associate([detection(),detection('d2',hazard='FLOOD'),detection('d3',bbox_wgs84=[13.39,42.36,13.40,42.37])],profile(),T);self.assertEqual(len(r['events']),3)
    def test_ambiguous_detection_not_chain_merged(self):
        a=detection('a',bbox_wgs84=[13.36,42.34,13.37,42.35]);b=detection('b',bbox_wgs84=[13.39,42.34,13.40,42.35]);c=detection('c',bbox_wgs84=[13.365,42.34,13.395,42.35])
        r=associate([a,b,c],profile(),T);self.assertEqual(len(r['events']),2);self.assertEqual(len(r['ambiguous']),1);self.assertEqual(len(r['ambiguous'][0]['candidate_event_ids']),2)
    def test_future_stale_partial_observations_excluded(self):
        future=detection('future');future['available_at']=END
        old=detection('old',sensed_at='2024-07-13T01:00:00Z');partial=detection('partial',coverage=.3)
        r=associate([future,old,partial],profile(),T);self.assertFalse(r['events']);self.assertEqual({x['reason'] for x in r['excluded']},{'FUTURE_SOURCE','STALE','PARTIAL'})
    def test_changed_id_conflicts_and_reordered_replay(self):
        a=detection();b=detection('b');changed=copy.deepcopy(a);changed['payload']['confidence']=.1
        self.reject('CONFLICTING_REVISION',lambda:associate([a,changed],profile(),T))
        self.assertEqual(associate([a,b],profile(),T),associate([b,a],profile(),T))
    def test_weather_issue_weights_units_and_coverage(self):
        w=ensemble();select_weather(w,T,T,END)
        for mutate,code in [(lambda p:p.update(issued_at=None),'INVALID_TIME'),(lambda p:p['units'].update(wind_speed_10m='km/h'),'INVALID_CONTRACT'),(lambda p:p['members'][0].update(weight=.5),'INVALID_ENSEMBLE'),(lambda p:p['members'][0].update(records=[]),'SOURCE_TIME')]:
            v=ensemble();mutate(v['payload']);self.reject(code,lambda:validate_record(v))
    def test_weather_future_stale_and_reanalysis(self):
        w=ensemble();w['available_at']=END;self.reject('FUTURE_SOURCE',lambda:select_weather(w,T,T,END))
        w=ensemble();self.reject('STALE_FORECAST',lambda:select_weather(w,T,T,'2024-07-13T15:00:00Z'))
        w['payload'].update(data_kind='REANALYSIS',issued_at=None);self.reject('SOURCE_KIND',lambda:select_weather(w,T,T,END));select_weather(w,T,T,END,forecast_required=False)
    def test_unknown_resource_fields_never_unconstrained(self):
        for field in ['skills','equipment','capabilities','schedule','rest_hours','maintenance','autonomy_h','consumables','cost_per_hour','reliability','mass_kg']:
            r=resource();r['payload'][field]=None;validate_record(r);self.reject('UNKNOWN_SAFETY',lambda:constraint_inputs(r,T))
    def test_road_closed_unknown_weight_disconnected(self):
        self.assertAlmostEqual(check_route([road()],resource(),T)['travel_s'],120)
        for changes,code in [({'status':'CLOSED'},'UNKNOWN_ACCESS'),({'load_limit_kg':None},'UNKNOWN_ACCESS'),({'load_limit_kg':1000},'UNSAFE_ACCESS')]:self.reject(code,lambda:check_route([road(**changes)],resource(),T))
        self.reject('INVALID_ROUTE',lambda:check_route([road(),road('second',from_node='c')],resource(),T))
    def test_impact_only_changes_exposure_not_hazard(self):
        baseline=dict(territory_id=profile()['id'],hazard='FLOOD',hazard_sha256='a'*64,exposed_people=10,as_of=T);old=copy.deepcopy(baseline)
        after=impact_only(effect(),baseline);self.assertEqual(baseline,old);self.assertEqual(after['hazard_sha256'],old['hazard_sha256']);self.assertEqual(after['remaining_exposed_people'],5);self.assertFalse(after['physical_hazard_changed'])
        for changes,code in [({'effect':'PHYSICAL_EFFECT'},'UNSUPPORTED_EFFECT'),({'effect':'UNKNOWN_EFFECT'},'UNSUPPORTED_EFFECT'),({'model_id':None},'UNKNOWN_EFFECT'),({'parameters':dict(evacuated_people=11)},'UNKNOWN_EFFECT')]:self.reject(code,lambda:impact_only(effect(**changes),baseline))
    def test_snapshot_future_cutoff_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'snapshot.json';future=exposure('future');future['available_at']=END
            s=snapshot(profile(),[exposure(),future],T,p);self.assertEqual(len(s['records']),1);self.assertEqual(s['excluded_future_ids'],['future']);self.assertEqual(load(p),s)
            with self.assertRaises(FileExistsError):snapshot(profile(),[],T,p)
    def test_index_exact_spatial_temporal_filter_and_limit(self):
        with tempfile.TemporaryDirectory() as d:
            index=GeoIndex(Path(d)/'geo.sqlite');future=exposure('future');future['available_at']=END;records=[exposure('inside'),exposure('outside',[13.399,42.369]),future];index.build(records)
            self.assertEqual([x['id'] for x in index.window([13.37,42.34,13.39,42.36],T)],['inside'])
            self.reject('PAYLOAD_LIMIT',lambda:index.window([13,42,14,43],T,1001))
            with self.assertRaises(FileExistsError):index.build(records)

    def test_route_expiry_shift_and_autonomy(self):
        short=road(valid_until='2024-07-13T13:01:00Z');self.reject('STALE_ACCESS',lambda:check_route([short],resource(),T))
        r=resource();r['payload']['autonomy_h']=.01;self.reject('UNSAFE_ACCESS',lambda:check_route([road()],r,T))
        r=resource();r['payload']['schedule'][0]['end']='2024-07-13T13:01:00Z';self.reject('UNAVAILABLE_RESOURCE',lambda:check_route([road()],r,T))
    def test_observation_outside_territory_rejected(self):
        self.reject('INVALID_GEOMETRY',lambda:associate([detection(bbox_wgs84=[0,0,1,1])],profile(),T))

    def test_geographic_or_unknown_work_CRS_not_assumed_metric(self):
        for crs in ['EPSG:4326','EPSG:999999']:
            p=profile();p['payload']['work_crs']=crs;self.reject('UNSUPPORTED_CRS',lambda:validate_record(p))
