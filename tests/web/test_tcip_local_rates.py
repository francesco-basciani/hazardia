import copy,hashlib,json,unittest
from uuid import UUID
from hazardia.io import HazardError
from hazardia.web.tcip_local_rates import local_path,layer_contract,context_contract,lookup_contract


def payload():
    key=hashlib.sha256(json.dumps(['municipality','theft','2025-01-01','2025-12-31'],separators=(',',':')).encode()).hexdigest()[:20]
    row={'code':'033032','name':'Fixture city','level':'municipality','crime_code':'theft','crime_label':'Furti','count':100,'population':10000,'population_date':'2025-01-01','population_provisional':False,'population_basis':'census_stock_start_of_year','period_start':'2025-01-01','period_end':'2025-12-31','count_source_id':str(UUID(int=1)),'count_source_url':'https://example.org/count','population_source_id':str(UUID(int=2)),'population_source_url':'https://example.org/pop','territory_matched':True,'count_provisional':False,'geometry_edition':'fixture','rate_per_100000':1000,'status':'observed'}
    return {'type':'FeatureCollection','profile':'tcip.territorial-population-rate/1.0','dataset_id':key,'features':[{'type':'Feature','id':'033032','geometry':{'type':'Polygon','coordinates':[[[9,44],[10,44],[10,45],[9,44]]]},'properties':row}],
            'metadata':{'private_research':True,'metric':'recorded_offences_per_100000_resident_stock','population_normalized':True,'forecast_probability':None,'annualized':False,'crime_code':'theft','level':'municipality','period_start':'2025-01-01','period_end':'2025-12-31','national_reference':None,'rates_are_probabilities':False}}


class LocalRatesTest(unittest.TestCase):
    def test_country_composition_requires_complete_base_and_nonadditive_order(self):
        d=payload();d['profile']='tcip.territorial-population-rate/1.1'
        d['metadata'].update(level='best_available',overlapping_geographic_levels=True,counts_additive=False,complete_country_display=True)
        d['dataset_id']=hashlib.sha256(json.dumps(['best_available','theft','2025-01-01','2025-12-31'],separators=(',',':')).encode()).hexdigest()[:20]
        city=copy.deepcopy(d['features'][0]);regions=[]
        for n in range(1,21):
            f=copy.deepcopy(city);f['id']=f'R{n:02d}';f['properties'].update(code=f['id'],level='region',source_area_code='ITC1');regions.append(f)
        d['features']=regions+[city]
        self.assertEqual(len(layer_contract(d)['features']),21)
        for kind in ['missing_region','addition','order','wrong_code']:
            bad=copy.deepcopy(d)
            if kind=='missing_region':bad['features'].pop(0)
            if kind=='addition':bad['metadata']['counts_additive']=True
            if kind=='order':bad['features']=list(reversed(bad['features']))
            if kind=='wrong_code':bad['features'][0]['properties']['level']='municipality'
            with self.assertRaises(HazardError,msg=kind):layer_contract(bad)

    def test_province_remains_a_province_instead_of_a_municipal_estimate(self):
        d=payload();d['profile']='tcip.territorial-population-rate/1.1';d['metadata']['level']='province'
        d['dataset_id']=hashlib.sha256(json.dumps(['province','theft','2025-01-01','2025-12-31'],separators=(',',':')).encode()).hexdigest()[:20]
        d['features'][0]['id']='P033';d['features'][0]['properties'].update(code='P033',level='province',source_area_code='ITD51')
        self.assertEqual(layer_contract(d)['features'][0]['properties']['level'],'province')
        d['features'][0]['properties']['source_area_code']='private-person-location'
        with self.assertRaises(HazardError):layer_contract(d)

    def test_fixed_paths_do_not_allow_arbitrary_requests(self):
        for path in ['/api/v1/geo/territorial-rates','/api/v1/geo/territorial-rates?dataset='+'a'*20,'/api/v1/geo/territorial-lookup?q=Roma&year=2025','/api/v1/geo/territorial-context?bbox=9,44,10,45&level=municipality&year=2025']:
            self.assertTrue(local_path(path))
        for path in ['https://example.org/','/api/v1/admin/sources','/api/v1/geo/territorial-rates?dataset=all','/api/v1/geo/territorial-lookup?q=Roma&year=2025&year=2024','/api/v1/geo/territorial-context?bbox=5,35,20,49&level=municipality&year=2025']:
            self.assertFalse(local_path(path))
    def test_rates_are_calculated_from_matching_resident_stock(self):
        self.assertEqual(layer_contract(payload())['features'][0]['properties']['rate_per_100000'],1000)
        for kind in ['population','date','rate','territory','crime','raw','point','dataset']:
            d=copy.deepcopy(payload());p=d['features'][0]['properties']
            if kind=='population':p['population']=0
            if kind=='date':p['population_date']='2021-12-31'
            if kind=='rate':p['rate_per_100000']=.01
            if kind=='territory':p['territory_matched']=False
            if kind=='crime':p['crime_code']='robbery'
            if kind=='raw':p['raw_body']='Forbidden'
            if kind=='point':d['features'][0]['geometry']={'type':'Point','coordinates':[9,44]}
            if kind=='dataset':d['dataset_id']='a'*20
            with self.assertRaises(HazardError,msg=kind):layer_contract(d)
    def test_context_does_not_infer_missing_counts(self):
        d=payload();d['profile']='tcip.population-coverage/1.0';p=d['features'][0]['properties']
        d['features'][0]['properties']={key:p[key] for key in ['code','name','level','population','population_date','population_provisional','population_basis']}
        d['features'][0]['properties'].update(count=None,rate_per_100000=None,status='crime_count_unavailable')
        d['metadata']={'private_research':True,'context_only':True,'missing_crime_is_zero':False,'truncated':False}
        self.assertIsNone(context_contract(d)['features'][0]['properties']['rate_per_100000'])
        d['features'][0]['properties']['rate_per_100000']=0
        with self.assertRaises(HazardError):context_contract(d)
    def test_lookup_bounds_and_no_count_inference(self):
        d={'items':[{'code':'033032','name':'Fixture','bounds':[9,44,10,45],'population':10000,'population_date':'2025-01-01'}],'counts_not_inferred':True}
        self.assertEqual(len(lookup_contract(d)['items']),1)
        d['items'][0]['bounds']=[9,44,float('nan'),45]
        with self.assertRaises(HazardError):lookup_contract(d)


class CumulativeRatesTest(unittest.TestCase):
    def fixture(self):
        d=payload();p=d['features'][0]['properties'];component={k:v for k,v in p.items() if k not in ('name','crime_label','territory_matched','status')}
        p.update(population=None,components=[component],years=[2025],omitted_periods=[],status='cumulative_observed')
        for k in ('population_date','population_basis','geometry_edition','count_source_id','count_source_url','population_source_id','population_source_url'):p.pop(k)
        d['profile']='tcip.cumulative-population-rate/1.0';d['dataset_id']=hashlib.sha256(json.dumps(['cumulative','municipality','theft','all'],separators=(',',':')).encode()).hexdigest()[:20]
        d['metadata'].update(metric='sum_nonoverlapping_period_rates_per_100000',aggregation='cumulative',window='all',reference_year=2026,variable_territorial_periods=True,counts_additive=False)
        return d
    def test_components_verified_and_tampering_rejected(self):
        self.assertEqual(layer_contract(self.fixture())['features'][0]['properties']['count'],100)
        for kind in ('total','rate','overlap','code','population','raw','years','crime'):
            d=self.fixture();p=d['features'][0]['properties'];c=p['components'][0]
            if kind=='total':p['count']+=1
            if kind=='rate':p['rate_per_100000']+=1
            if kind=='overlap':p['components'].append(copy.deepcopy(c))
            if kind=='code':c['code']='015146'
            if kind=='population':c['population']=0
            if kind=='raw':c['raw_body']='forbidden'
            if kind=='years':p['years']=[2024]
            if kind=='crime':c['crime_code']='robbery'
            with self.assertRaises(HazardError,msg=kind):layer_contract(d)


def test_fixed_continuous_consumer_rejects_a_gap_or_partial_year():
    test=CumulativeRatesTest();d=test.fixture();p=d['features'][0]['properties'];component=p['components'][0]
    p['components']=[dict(component,period_start=f'{y}-01-01',period_end=f'{y}-12-31',population_date=f'{y}-01-01') for y in range(2018,2025)]
    p.update(count=700,rate_per_100000=7000,years=list(range(2018,2025)),period_start='2018-01-01',period_end='2024-12-31')
    d['metadata'].update(window='2018-2024',variable_territorial_periods=False,period_start='2018-01-01',period_end='2024-12-31')
    d['dataset_id']=hashlib.sha256(json.dumps(['cumulative','municipality','theft','2018-2024'],separators=(',',':')).encode()).hexdigest()[:20]
    assert layer_contract(d)['features'][0]['properties']['count']==700
    for kind in ('gap','partial','outside','periodflag'):
        bad=copy.deepcopy(d);q=bad['features'][0]['properties']
        if kind=='gap':q['components'].pop(2)
        if kind=='partial':q['components'][2]['period_end']='2020-06-30'
        if kind=='outside':q['components'][0]['period_start']='2017-01-01'
        if kind=='periodflag':bad['metadata']['variable_territorial_periods']=True
        try:layer_contract(bad)
        except HazardError:pass
        else:raise AssertionError(kind)


def test_person_crime_categories_explicitly_allowed_without_arbitrary_scores():
    for crime in ('attempted_homicide','battery','threats','sexual_violence'):
        d=payload();d['metadata']['crime_code']=crime;d['features'][0]['properties']['crime_code']=crime
        d['dataset_id']=hashlib.sha256(json.dumps(['municipality',crime,'2025-01-01','2025-12-31'],separators=(',',':')).encode()).hexdigest()[:20]
        assert layer_contract(d)['metadata']['crime_code']==crime
    d=payload();d['metadata']['crime_code']='global_safety_score'
    with unittest.TestCase().assertRaises(HazardError):layer_contract(d)


def test_category_menu_contract_rejects_fabricated_availability_and_unknown_codes():
    from hazardia.web.tcip_local_rates import catalogue_contract
    item={'id':'a'*20,'level':'municipality','crime_code':'theft','crime_label':'Furti','period_start':'2025-01-01','period_end':'2025-12-31','title':'Fixture','areas':1}
    data={'schema':'tcip.territorial-rate-catalog/1.0','items':[item],'private_research':True,'complete_national_crime_counts':False,'coverage':{},'crime_types':[{'code':'theft','label':'Furti','definition':'','definition_source':'','availability':'available'},{'code':'femicide','label':'Femminicidio','definition':'Solo classificazioni esplicite della fonte.','definition_source':'https://www.istat.it/','availability':'no_qualified_territorial_data'}]}
    assert catalogue_contract(data)==data
    for mutation in ('availability','unknown','duplicate','missing','unsafe_url'):
        d=copy.deepcopy(data)
        if mutation=='availability':d['crime_types'][1]['availability']='available'
        if mutation=='unknown':d['crime_types'][1]['code']='global_safety_score'
        if mutation=='duplicate':d['crime_types'].append(d['crime_types'][0])
        if mutation=='missing':d['crime_types'].pop(0)
        if mutation=='unsafe_url':d['crime_types'][1]['definition_source']='javascript:alert(1)'
        with unittest.TestCase().assertRaises(HazardError):catalogue_contract(d)


def test_national_victim_series_require_explicit_unit_definition_and_country():
    from hazardia.web.tcip_local_rates import VICTIM_SERIES
    for code,(kind,definition) in VICTIM_SERIES.items():
        d=payload();d['metadata'].update(crime_code=code,level='country',metric='victims_per_100000_resident_stock',count_unit='victims',count_kind=kind,definition_id=definition,national_only=True,denominator_scope='all_residents')
        d['dataset_id']=hashlib.sha256(json.dumps(['country',code,'2025-01-01','2025-12-31'],separators=(',',':')).encode()).hexdigest()[:20]
        d['features'][0]['id']='IT';d['features'][0]['properties'].update(code='IT',level='country',crime_code=code)
        assert layer_contract(d)['features'][0]['id']=='IT'
        for field,value in [('count_unit','offences'),('count_kind','recorded_offences'),('definition_id','all_women_equal_femicide'),('national_only',False),('denominator_scope','women_only')]:
            bad=copy.deepcopy(d);bad['metadata'][field]=value
            with unittest.TestCase().assertRaises(HazardError):layer_contract(bad)
        bad=copy.deepcopy(d);bad['features'][0]['id']='P001';bad['features'][0]['properties'].update(code='P001',level='province')
        with unittest.TestCase().assertRaises(HazardError):layer_contract(bad)
