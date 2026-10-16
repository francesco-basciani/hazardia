import copy,datetime as dt,io,json,tempfile,threading,time,unittest
from pathlib import Path
from hazardia.ingest.forecast import ForecastStore,normalize,VARIABLES,TTL,DAILY_LIMIT,CAP
from hazardia.io import HazardError
from hazardia.contracts import validate_weather,validate_request
from tests.support import fixture

def raw():
 t=dt.datetime(2026,10,16,tzinfo=dt.timezone.utc)
 h={'time':[(t+dt.timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M') for i in range(12)]}
 for k,v in {'temperature_2m':15,'relative_humidity_2m':50,'precipitation':2,'wind_speed_10m':3,'wind_direction_10m':90,'surface_pressure':900,'shortwave_radiation':100}.items():h[k]=[v+i if k in ['precipitation','shortwave_radiation'] else v for i in range(12)]
 return dict(timezone='GMT',utc_offset_seconds=0,hourly_units=VARIABLES.copy(),hourly=h)

def receipt():return dict(provider='Open-Meteo',available_at='2026-10-16T00:30:00Z',sha256='a'*64)
class Response(io.BytesIO):
 headers={};status=200
 def geturl(self):return 'https://api.open-meteo.com/v1/forecast'
class ForecastTests(unittest.TestCase):
 def reject(self,code,fn):
  with self.assertRaises(HazardError) as e:fn()
  self.assertEqual(e.exception.code,code)
 def test_interval_mapping_and_unknown_issue(self):
  n=normalize(raw(),receipt());self.assertEqual(n['records'][0]['values']['precipitation'],3);self.assertEqual(n['records'][0]['values']['shortwave_radiation'],101);self.assertEqual(n['records'][0]['values']['temperature_2m'],15);self.assertIsNone(n['issued_at']);self.assertEqual(n['valid_until'],'2026-10-16T11:00:00Z')
 def test_units_missing_and_nonfinite_rejected(self):
  for transform,code in [(lambda r:r['hourly_units'].update(surface_pressure='Pa'),'SOURCE_UNIT'),(lambda r:r['hourly']['temperature_2m'].__setitem__(0,None),'SOURCE_MISSING'),(lambda r:r['hourly']['wind_speed_10m'].__setitem__(0,float('nan')),'SOURCE_MISSING')]:
   r=raw();transform(r);self.reject(code,lambda:normalize(r,receipt()))
 def test_bad_time_gaps_and_ranges(self):
  for transform,code in [(lambda r:r.update(utc_offset_seconds=3600),'SOURCE_TIME'),(lambda r:r['hourly']['time'].__setitem__(1,r['hourly']['time'][0]),'SOURCE_TIME'),(lambda r:r['hourly']['precipitation'].__setitem__(1,-1),'SOURCE_RANGE')]:
   r=raw();transform(r);self.reject(code,lambda:normalize(r,receipt()))
 def test_contract_requires_new_forecast_mode_and_explicit_unknown(self):
  with tempfile.TemporaryDirectory() as tmp:
   req,_=fixture(tmp);n=normalize(raw(),receipt());req.update(schema_version='0.3.0',mode='RESEARCH_FORECAST',valid_from='2026-10-16T01:00:00Z',valid_until='2026-10-16T01:10:00Z',snapshot_at='2026-10-16T00:45:00Z');validate_request(req);validate_weather(n,req)
   bad=copy.deepcopy(n);bad.pop('issued_at_status');self.reject('INVALID_TIME',lambda:validate_weather(bad,req))
   bad=copy.deepcopy(req);bad['valid_from']='2026-10-16T00:00:00Z';self.reject('FUTURE_SOURCE',lambda:validate_weather(n,bad))
   bad=copy.deepcopy(req);bad['schema_version']='0.2.0';self.reject('INVALID_CONTRACT',lambda:validate_request(bad))
 def test_cache_durable_throttle(self):
  with tempfile.TemporaryDirectory() as tmp:
   calls=[]
   def get(*a,**kw):calls.append(a);return Response(json.dumps(raw()).encode())
   s=ForecastStore(tmp,opener=get);s.refresh();s.refresh();ForecastStore(tmp,opener=get).refresh();self.assertEqual(len(calls),1);self.assertEqual(s.snapshot()['quota']['attempts_today'],1);self.assertIsNone(s.snapshot()['error'])
 def test_error_backoff_and_no_fabrication(self):
  with tempfile.TemporaryDirectory() as tmp:
   calls=[]
   def fail(*a,**kw):calls.append(1);raise OSError('offline')
   s=ForecastStore(tmp,opener=fail);s.refresh();s.refresh();self.assertEqual(len(calls),1);self.assertIsNone(s.snapshot()['forecast']);self.assertIsNotNone(s.snapshot()['error'])
 def test_response_size_limit(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=ForecastStore(tmp,opener=lambda *a,**k:Response(b' '* (CAP+1)));s.refresh();self.assertIsNone(s.snapshot()['forecast']);self.assertIn('DOWNLOAD_BUDGET',s.snapshot()['error'])
 def test_stale_and_identity_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=ForecastStore(tmp,opener=lambda *a,**k:Response(json.dumps(raw()).encode()));s.refresh();f=s.snapshot()['forecast'];self.reject('STALE_CONTEXT',lambda:s.fresh('wrong'));s.clock=lambda:time.time()+TTL+1;self.reject('STALE_FORECAST',lambda:s.fresh(f['id']))
 def test_daily_quota(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=ForecastStore(tmp);now=time.time()
   with s.connect() as db:
    for i in range(DAILY_LIMIT):db.execute('INSERT INTO attempts VALUES(?)',(now-now%86400+1+i,))
   self.reject('WEATHER_QUOTA',s.refresh)

 def test_cross_instance_atomic_reservation(self):
  with tempfile.TemporaryDirectory() as tmp:
   calls=[];barrier=threading.Barrier(2);errors=[]
   def get(*a,**kw):calls.append(1);time.sleep(.1);return Response(json.dumps(raw()).encode())
   stores=[ForecastStore(tmp,opener=get),ForecastStore(tmp,opener=get)]
   def worker(s):
    try:barrier.wait();s.refresh()
    except Exception as e:errors.append(str(e))
   threads=[threading.Thread(target=worker,args=(s,)) for s in stores]
   for t in threads:t.start()
   for t in threads:t.join()
   self.assertEqual(errors,[]);self.assertEqual(len(calls),1);self.assertEqual(stores[0].snapshot()['quota']['attempts_today'],1)

 def test_native_dry_acceptance_preserves_invalid_output_checks(self):
  from hazardia.adapters.flood_checks import verify_dry_map
  verify_dry_map(0,[0.,0.,0.])
  for count,values in [(1,[0.]),(0,[]),(0,[float('nan')]),(0,[.0001]),(0,[-1.])]:
   self.reject('INVALID_OUTPUT',lambda:verify_dry_map(count,values))

 def test_cache_corruption_blocks_simulation(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=ForecastStore(tmp,opener=lambda *a,**k:Response(json.dumps(raw()).encode()));s.refresh()
   with s.connect() as db:name=db.execute('SELECT snapshot FROM state WHERE id=1').fetchone()[0]
   p=Path(tmp)/name;data=json.loads(p.read_text());data['records'][0]['values']['temperature_2m']=25;p.write_text(json.dumps(data));self.reject('CACHE_CORRUPT',s.snapshot)
