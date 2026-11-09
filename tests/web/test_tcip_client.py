import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hazardia.io import HazardError
from hazardia.web.tcip_client import APIClient, NoRedirect, catalog_contract, layer_contract

IDENT='0e073b2b-5824-40f5-82e1-615d207e4e64'
TOKEN='tcip_'+'x'*43


def layer():
    return dict(type='FeatureCollection',release_id=IDENT,metadata=dict(probability_kind='empirical_location_share_given_recorded_dataset_episode',forecast_probability=None,years=[2019,2020],denominator=2000),geometry_context=dict(edition='ISTAT-2020-01-01-generalized-display150m'),features=[dict(type='Feature',id=str(i),properties=dict(source_region='Synthetic zone '+str(i),count=100,share=.05),geometry=dict(type='Polygon',coordinates=[[[12,42],[13,42],[13,43],[12,42]]])) for i in range(1,21)])


class TcipClientTest(unittest.TestCase):
    def test_contract_shares_and_missing(self):
        data=layer();self.assertEqual(layer_contract(data)['metadata']['denominator'],2000)
        missing=copy.deepcopy(data);missing['metadata']['denominator']=None
        for f in missing['features']:f['properties']['share']=None
        missing['features'][0]['properties']['count']=None
        self.assertIsNone(layer_contract(missing)['features'][0]['properties']['share'])
        for mutate in [lambda x:x['features'][0]['properties'].update(share=.5),lambda x:x['features'][0]['properties'].update(count=-1),lambda x:x['features'][0]['geometry'].update(type='Point'),lambda x:x['metadata'].update(probability_kind='forecast'),lambda x:x['features'][0]['geometry']['coordinates'][0][0].__setitem__(0,float('nan')),lambda x:x['features'][0].update(id='2'),lambda x:x.update(metadata=[]),lambda x:x['metadata'].update(years='2020')]:
            changed=copy.deepcopy(data);mutate(changed)
            with self.assertRaises(HazardError):layer_contract(changed)

    def test_discovery_is_explicit_historical_profile(self):
        value=dict(schema='tcip.map-catalog/1.0',forecast_probability_available=False,items=[dict(release_id=IDENT,profile='tcip.regional-historical-share/1.0',years=[2018,2019,2020])])
        self.assertEqual(len(catalog_contract(value)['items']),1)
        value['items'].append(value['items'][0])
        with self.assertRaises(HazardError):catalog_contract(value)

    def test_private_credential_and_loopback_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=APIClient(tmp);path=Path(tmp)/'tcip-reader.token'
            with self.assertRaises(HazardError):client.credential()
            path.write_text(TOKEN);path.chmod(0o600);self.assertEqual(client.credential(),TOKEN)
            path.chmod(0o644)
            with self.assertRaises(HazardError):client.credential()
            for bad in ['http://example.org',80,True,65536]:
                with self.assertRaises(HazardError):APIClient(tmp,bad)
            for identity,years in [('../private',None),(IDENT,0),(IDENT,101),(IDENT,True)]:
                with self.assertRaises(HazardError):client.layer(identity,years)
            with self.assertRaises(HazardError):client.request('/api/v1/admin/events')
            with self.assertRaises(HazardError):NoRedirect().redirect_request(None,None,None,None,None,None)

    def test_bounded_http_credentials_and_no_error_echo(self):
        class Response:
            def __init__(self,raw):self.raw=raw
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return self.raw[:n]
        with tempfile.TemporaryDirectory() as tmp:
            client=APIClient(tmp);path=Path(tmp)/'tcip-reader.token';path.write_text(TOKEN);path.chmod(0o600)
            with patch('hazardia.web.tcip_client.build_opener') as build:
                build.return_value.open.return_value=Response(json.dumps(layer()).encode())
                self.assertEqual(client.layer(IDENT,1)['release_id'],IDENT)
                request=build.return_value.open.call_args.args[0]
                self.assertEqual(request.get_header('Authorization'),'Bearer '+TOKEN)
                self.assertNotIn(TOKEN,request.full_url);self.assertTrue(request.full_url.endswith('?years=1'))
                build.return_value.open.return_value=Response(b'x'*2_000_001)
                with self.assertRaises(HazardError):client.layer(IDENT)
                build.return_value.open.side_effect=OSError(TOKEN)
                with self.assertRaises(HazardError) as error:client.layer(IDENT)
                self.assertNotIn(TOKEN,str(error.exception))




class TcipDetailedClientTest(unittest.TestCase):
    def test_reviewed_municipality_and_neighborhood_profiles(self):
        data=layer();data['profile']='tcip.spatial-observed-share/2.0'
        data['geometry_context']['edition']='Firenze-quartieri-2012-context'
        data['metadata'].update(level='neighborhood',coverage='Synthetic public-aggregate contract fixture')
        data['features']=data['features'][:2]
        for i,f in enumerate(data['features']):
            f['id']='10000000-0000-4000-8000-'+str(i).zfill(12);f['properties'].update(share=.5)
        data['metadata']['denominator']=200
        self.assertEqual(len(layer_contract(data)['features']),2)
        catalog=dict(schema='tcip.map-catalog/1.0',forecast_probability_available=False,items=[dict(release_id=IDENT,profile=data['profile'],years=[2025])])
        self.assertEqual(len(catalog_contract(catalog)['items']),1)
        for mutate in [lambda x:x['metadata'].update(level='household'),lambda x:x['geometry_context'].update(edition='guessed-boundaries'),lambda x:x['features'][0].update(id='raw-point'),lambda x:x['features'][0]['properties'].update(share=.9)]:
            changed=copy.deepcopy(data);mutate(changed)
            with self.assertRaises(HazardError):layer_contract(changed)

if __name__=='__main__':unittest.main()
