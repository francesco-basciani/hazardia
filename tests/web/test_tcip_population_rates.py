import copy
import unittest
from uuid import UUID
from hazardia.io import HazardError
from hazardia.web.tcip_client import population_rate_contract


def payload():
    return {'type':'FeatureCollection','profile':'tcip.population-rates/1.0',
            'metadata':{'private_research':True,'population_normalized':True,'annualized':False,
                        'forecast_probability':None,'metric':'reported_offences_per_100000_residents',
                        'crime_code':'theft','period':'2023','period_start':'2023-01-01','period_end':'2023-12-31',
                        'partial_period':False,'national_rate_per_100000':100},
            'features':[{'type':'Feature','id':str(i),'properties':{'code':str(i),'name':'Fixture region',
                        'level':'region','area_id':str(UUID(int=i)),'rate_per_100000':200,
                        'relative_to_national':2,'population':None,'count':None,'status':'observed'},
                        'geometry':{'type':'Polygon','coordinates':[[[10,40],[11,40],[11,41],[10,40]]]}}
                        for i in range(1,21)]}


class PopulationRatesTest(unittest.TestCase):
    def test_true_rates_are_not_shares(self):
        self.assertEqual(len(population_rate_contract(payload())['features']),20)
    def test_invalid_denominator_ratio_period_and_precision_rejected(self):
        for kind in ['ratio','nan','population','raw','point','duplicates','annualized','period']:
            d=copy.deepcopy(payload());p=d['features'][0]['properties']
            if kind=='ratio':p['relative_to_national']=.2
            if kind=='nan':p['rate_per_100000']=float('nan')
            if kind=='population':p['population']=1234
            if kind=='raw':p['raw_body']='Forbidden'
            if kind=='point':d['features'][0]['geometry']={'type':'Point','coordinates':[10,40]}
            if kind=='duplicates':d['features'][1]['id']='1'
            if kind=='annualized':d['metadata']['annualized']=True
            if kind=='period':d['metadata']['period_end']='2024-12-31'
            with self.assertRaises(HazardError,msg=kind):population_rate_contract(d)
    def test_missing_rate_never_zero(self):
        d=payload();d['features'][0]['properties'].update(rate_per_100000=None,relative_to_national=None,status='unavailable')
        self.assertIsNone(population_rate_contract(d)['features'][0]['properties']['rate_per_100000'])
