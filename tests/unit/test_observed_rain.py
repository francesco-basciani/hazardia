import copy
import datetime as dt
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from hazardia.ingest.observed_rain import normalize, ObservedRainStore, UTC, MAX_BYTES, DOWNLOAD_BUDGET

NOW=dt.datetime(2026,10,21,21,40,tzinfo=UTC)
CAT=[dict(id='mnw',category='OBS',is_public=True,license='CCBY4.0',license_url='https://creativecommons.org/licenses/by/4.0/legalcode',group_license='CCBY_COMPLIANT',attribution='MeteoNetwork',name='meteonetwork',description='Amateur stations')]
def payload(value=3.2,at='2026-10-21T21:00:00',rel=1):
 return dict(descr={'B13011':{'unit':'KG/M**2'}},data=[dict(stat=dict(lat=42.3,lon=13.4,net='mnw',details=[dict(var='B01019',val='abr001')]),prod=[dict(var='B13011',val=[dict(val=value,ref=at,rel=rel)])])])
class ObservedRainTests(unittest.TestCase):
 def test_actual_interval_not_forecast_or_counter(self):
  x=normalize(payload(),CAT,NOW)['features'][0]['properties'];self.assertEqual(x['mm'],3.2);self.assertEqual(x['from_at'],'2026-10-21T20:00:00Z');self.assertEqual(x['until'],'2026-10-21T21:00:00Z');self.assertIn('Amateur',x['network_description'])
 def test_true_zero_kept(self):self.assertEqual(normalize(payload(0),CAT,NOW)['features'][0]['properties']['mm'],0)
 def test_missing_trace_bad_values_not_zero(self):
  for value in [None,-1,-9999,True,'2',float('nan'),float('inf')]:self.assertEqual(normalize(payload(value),CAT,NOW)['features'],[])
 def test_bad_future_old_quality(self):
  for at,rel in [('2026-10-21T22:00:00',1),('2026-10-21T17:00:00',1),('invalid',1),('2026-10-21T21:00:00',0),('2026-10-21T21:00:00',None),('2026-10-21T21:00:00',True)]:self.assertFalse(normalize(payload(at=at,rel=rel),CAT,NOW)['features'])
 def test_license_fail_closed(self):
  for key,value in [('license','CCBY-NC'),('group_license','OTHER'),('attribution',''),('is_public',False)]:
   catalog=copy.deepcopy(CAT);catalog[0][key]=value;self.assertFalse(normalize(payload(),catalog,NOW)['features'])
 def test_unit_fail_closed(self):
  p=payload();p['descr']['B13011']['unit']='counter';self.assertRaises(ValueError,normalize,p,CAT,NOW)
 def test_bad_coordinates(self):
  for value in [91,True,float('nan'),'42']:
   p=payload();p['data'][0]['stat']['lat']=value;self.assertFalse(normalize(p,CAT,NOW)['features'])
 def test_conflicting_interval_rejected(self):
  p=payload();p['data'][0]['prod'][0]['trange']='1,0,600';self.assertFalse(normalize(p,CAT,NOW)['features'])
 def test_latest_deduplicated(self):
  p=payload();p['data']+=payload(2,'2026-10-21T20:00:00')['data'];x=normalize(p,CAT,NOW)['features'];self.assertEqual(len(x),1);self.assertEqual(x[0]['properties']['mm'],3.2)
 def test_missing_is_explicit(self):
  with tempfile.TemporaryDirectory() as root:self.assertEqual(ObservedRainStore(root).snapshot()['status'],'MISSING')
 def test_stale_survives_source_failure(self):
  with tempfile.TemporaryDirectory() as root:
   store=ObservedRainStore(root);data=normalize(payload(),CAT,NOW);data['acquired_at']='2020-01-01T01:00:00Z';data['features'][0]['properties']['until']='2020-01-01T00:00:00Z';store._write('latest.json',data);store._write('state.json',dict(error='HTTP 503'))
   x=store.snapshot();self.assertEqual(x['status'],'STALE');self.assertEqual(x['data']['features'][0]['properties']['mm'],3.2);self.assertEqual(x['error'],'HTTP 503')
 def test_hour_limit_persists_after_restart(self):
  with tempfile.TemporaryDirectory() as root:
   store=ObservedRainStore(root);store._write('ledger.json',dict(last_attempt=time.time(),reserved_bytes=0));self.assertEqual(ObservedRainStore(root).refresh()['status'],'CACHED')
 def test_download_budget_before_network(self):
  with tempfile.TemporaryDirectory() as root:
   store=ObservedRainStore(root)
   with patch('urllib.request.urlopen',side_effect=AssertionError('No I/O')):
    self.assertRaises(ValueError,store._get,'https://example.invalid',dict(reserved_bytes=DOWNLOAD_BUDGET,last_attempt=0))
if __name__=='__main__':unittest.main()
