import copy
import tempfile
import unittest
from pathlib import Path
from hazardia.io import HazardError
from hazardia.web.tcip_client import APIClient,document_map_contract


def payload():
 return {'type':'FeatureCollection','profile':'tcip.document-event-geography/1.0','metadata':{'private_research':True,'forecast_probability':None,'counts_are_unique_crimes':False},'features':[{'type':'Feature','id':'048017','properties':{'code':'048017','area_id':'opaque','name':'Synthetic municipality','level':'municipality','document_count':2,'counts':{'theft':2},'location_basis':'document_assertion_not_source_office','verification_status':'unreviewed_document_assertion'},'geometry':{'type':'Polygon','coordinates':[[[11,43],[12,43],[12,44],[11,43]]]}}]}


class DocumentMapTest(unittest.TestCase):
 def test_fixed_profile_and_semantics(self):
  self.assertEqual(len(document_map_contract(payload())['features']),1)
  for key,value in [('private_research',False),('forecast_probability',.2),('counts_are_unique_crimes',True)]:
   data=payload();data['metadata'][key]=value
   with self.assertRaises(HazardError):document_map_contract(data)
 def test_no_points_raw_text_or_invalid_counts(self):
  for change in ['raw','point','negative','malformed']:
   data=payload()
   if change=='raw':data['features'][0]['properties']['raw_body']='Forbidden'
   elif change=='point':data['features'][0]['geometry']={'type':'Point','coordinates':[11,43]}
   elif change=='malformed':data['features'][0]['geometry']['coordinates']=[None]
   else:data['features'][0]['properties']['counts']['theft']=-1
   with self.assertRaises(HazardError):document_map_contract(data)
 def test_separate_private_reader_file(self):
  with tempfile.TemporaryDirectory() as tmp:
   client=APIClient(tmp);path=Path(tmp)/'tcip-document-reader.token';path.write_text('tcip_'+'x'*43);path.chmod(0o600)
   self.assertTrue(client.credential(document_map=True).startswith('tcip_'))
   with self.assertRaises(HazardError):client.credential()

class ExtendedDocumentMapTest(unittest.TestCase):
 def test_official_asc_identifier_and_bounded_publication_windows(self):
  data=payload();f=data['features'][0];f['id']=f['properties']['code']='063049:A2-26'
  f['properties']['level']='neighborhood';f['properties']['publication_windows']={'90':{'document_count':1,'counts':{'theft':1}}}
  self.assertEqual(document_map_contract(data)['features'][0]['id'],'063049:A2-26')
  for change in ['window','count','identifier']:
   bad=copy.deepcopy(data)
   if change=='window':bad['features'][0]['properties']['publication_windows']['999']={'document_count':0,'counts':{}}
   elif change=='count':bad['features'][0]['properties']['publication_windows']['90']['document_count']=100
   else:bad['features'][0]['id']='063049:street-household'
   with self.assertRaises(HazardError):document_map_contract(bad)
