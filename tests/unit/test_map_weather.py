import copy,datetime as dt,io,json,tempfile,unittest
from hazardia.ingest.map_weather import grid,url,normalize,MapWeatherStore,EXTRA
from hazardia.io import HazardError
from urllib.parse import parse_qs,urlsplit
B=[[39.,8.],[46.,20.]]
def fixture():
 q=parse_qs(urlsplit(url(B)).query);ys=q['latitude'][0].split(',');xs=q['longitude'][0].split(',');times=[(dt.datetime(2026,10,16)+dt.timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M') for i in range(24)]
 return [dict(location_id=i,latitude=float(y),longitude=float(x),utc_offset_seconds=0,timezone='GMT',hourly_units={'time':'iso8601','wind_speed_10m':'m/s','wind_direction_10m':'°','temperature_2m':'°C','precipitation':'mm',**{k:v[0] for k,v in EXTRA.items()}},hourly=dict(time=times,wind_speed_10m=[5]*24,wind_direction_10m=[90]*24,temperature_2m=[20]*24,precipitation=list(range(24)),**{k:[{'humidity':65,'pressure':950,'cloud':30,'gusts':8,'radiation':100,'rain_probability':40}[v[1]]]*24 for k,v in EXTRA.items()})) for i,(y,x) in enumerate(zip(ys,xs))]
def receipt():return dict(normalization_version=2,url=url(B),sha256='a'*64,available_at='2026-10-16T00:00:00Z')
class MapWeatherTests(unittest.TestCase):
 def test_global_geography_and_bounds(self):
  for b in [B,[[12.,-17.],[17.,-11.]],[[42.35,13.38],[42.351,13.381]]]:
   y,x=grid(b);self.assertEqual((len(y),len(x)),(9,9));self.assertLessEqual(y[0],b[0][0]);self.assertGreaterEqual(x[-1],b[1][1]);self.assertIn('icon_global',url(b))
 def test_invalid_bounds(self):
  for b in [None,[[91,0],[92,1]],[[0,170],[1,-170]],[[True,0],[1,1]],[[0,0],[0,1]],[[0,0],[1,float('nan')]]]:
   with self.assertRaises(HazardError):grid(b)
 def test_units_alignment_and_vectors(self):
  f=normalize(fixture(),receipt());self.assertEqual(len(f['records']),23);self.assertEqual(set(f['records'][0]['precipitation']),{1.});self.assertEqual(set(f['records'][0]['u']),{-5.});self.assertIsNone(f['issued_at'])
 def test_legacy_cache_has_explicitly_missing_extra(self):
  r=fixture();rec=receipt();rec['url']=rec['url'].replace(','.join([*__import__('hazardia.ingest.map_weather',fromlist=['VARS']).VARS,*EXTRA]),','.join(__import__('hazardia.ingest.map_weather',fromlist=['VARS']).VARS))
  for node in r:
   for key in EXTRA:node['hourly_units'].pop(key);node['hourly'].pop(key)
  self.assertNotIn('humidity',normalize(r,rec)['records'][0])
 def test_interval_alignment_gusts_and_radiation(self):
  r=fixture()
  for node in r:
   node['hourly']['wind_gusts_10m']=list(range(24));node['hourly']['shortwave_radiation']=list(range(24))
  f=normalize(r,receipt());self.assertEqual(f['records'][0]['gusts'],[1.]*81);self.assertEqual(f['records'][0]['radiation'],[1.]*81)
 def test_probability_is_independent_and_next_hour_aligned(self):
  r=fixture()
  for node in r:
   node['hourly']['precipitation_probability']=[0,80]+[20]*22
   node['hourly']['precipitation']=[0]*24
  f=normalize(r,receipt());self.assertEqual(f['records'][0]['rain_probability'],[80.]*81);self.assertEqual(f['records'][0]['precipitation'],[0.]*81)
  self.assertEqual(f['units']['rain_probability'],'%');self.assertIn('ensemble',f['model']);self.assertIn('>0.1mm',f['interval_semantics'])
 def test_probability_missing_invalid_and_legacy(self):
  for value in [None,-1,101,True]:
   r=fixture();r[0]['hourly']['precipitation_probability'][1]=value
   with self.assertRaises(HazardError):normalize(r,receipt())
  r=fixture();rec=receipt();rec['url']=rec['url'].replace(',precipitation_probability','')
  for n in r:
   n['hourly'].pop('precipitation_probability');n['hourly_units'].pop('precipitation_probability')
  f=normalize(r,rec);self.assertNotIn('rain_probability',f['records'][0]);self.assertEqual(f['model'],'DWD ICON Global via Open-Meteo')
 def test_supporting_weather_values(self):
  f=normalize(fixture(),receipt());self.assertEqual(f['records'][0]['humidity'],[65.]*81);self.assertEqual(f['units']['pressure'],'hPa')
  r=fixture();r[0]['hourly']['relative_humidity_2m'][0]=101
  with self.assertRaises(HazardError):normalize(r,receipt())
 def test_incomplete_and_invalid_fields(self):
  for mutate in [lambda r:r.pop(),lambda r:r[0]['hourly']['temperature_2m'].__setitem__(0,None),lambda r:r[0]['hourly']['precipitation'].__setitem__(0,-1),lambda r:r[0]['hourly_units'].__setitem__('wind_speed_10m','km/h'),lambda r:r[0].__setitem__('latitude',0),lambda r:r[1]['hourly']['time'].__setitem__(1,'2026-10-16T00:00')]:
   r=fixture();mutate(r)
   with self.assertRaises(HazardError):normalize(r,receipt())
 def test_cache_reuse_and_tamper(self):
  class Response(io.BytesIO):
   status=200
   def geturl(self):return 'https://api.open-meteo.com/v1/forecast'
  with tempfile.TemporaryDirectory() as root:
   calls=[]
   def get(*a,**k):calls.append(1);return Response(json.dumps(fixture()).encode())
   s=MapWeatherStore(root,opener=get);s.acquire(B);s.acquire([[41.,12.],[43.,14.]]);self.assertEqual(len(calls),1);self.assertEqual(s.snapshot()['quota']['attempts_today'],1)
   from pathlib import Path
   next(Path(root).glob('raw-*.json')).write_text('[]')
   with self.assertRaises(HazardError):s.snapshot()
 def test_failed_acquisitions_and_rate_limit(self):
  with tempfile.TemporaryDirectory() as root:
   def get(*a,**k):raise OSError('offline')
   s=MapWeatherStore(root,opener=get);s.acquire(B);s.acquire([[12.,-17.],[17.,-11.]])
   self.assertEqual(s.snapshot()['quota']['attempts_today'],1);self.assertIn('WEATHER_THROTTLED',s.snapshot()['error']);self.assertIsNone(s.snapshot()['forecast'])
 def test_daily_budget(self):
  with tempfile.TemporaryDirectory() as root:
   now=1792195000;s=MapWeatherStore(root,clock=lambda:now)
   with s.connect() as db:
    for i in range(48):db.execute('INSERT INTO attempts VALUES(?)',(now-now%86400+i,))
   s.acquire(B);self.assertIn('WEATHER_QUOTA',s.snapshot()['error']);self.assertEqual(s.snapshot()['quota']['attempts_today'],48)


class CompressedMapWeatherTests(unittest.TestCase):
 def test_lossless_compaction_and_reuse(self):
  from pathlib import Path
  import gzip
  class Response(io.BytesIO):
   status=200
   def geturl(self):return 'https://api.open-meteo.com/v1/forecast'
  with tempfile.TemporaryDirectory() as root:
   calls=[]
   def get(*a,**k):calls.append(1);return Response(json.dumps(fixture()).encode())
   store=MapWeatherStore(root,opener=get);store.acquire(B)
   before=store.snapshot()['forecast'];original={p.name:p.read_bytes() for p in Path(root).glob('*.json')};size=store.storage_bytes()
   self.assertEqual(store.compact(),len(original));self.assertLess(store.storage_bytes(),size)
   for name,data in original.items():self.assertEqual(gzip.decompress((Path(root)/(name+'.gz')).read_bytes()),data)
   self.assertEqual(store.read(before['id']+'.json'),before);store.acquire(B);self.assertEqual(len(calls),1)
   self.assertEqual(store.snapshot()['forecast'],before);self.assertEqual(store.snapshot()['quota']['attempts_today'],1)
   next(Path(root).glob('raw-*.json.gz')).write_bytes(gzip.compress(b'[]'))
   with self.assertRaises(HazardError):store.snapshot()
 def test_retry_after_respects_global_cooldown(self):
  with tempfile.TemporaryDirectory() as root:
   now=1792195000;store=MapWeatherStore(root,clock=lambda:now)
   with store.connect() as db:db.execute('INSERT INTO attempts VALUES(?)',(now-20,))
   self.assertEqual(store.snapshot()['retry_after_s'],45)
 def test_compaction_conflict_preserves_original(self):
  from pathlib import Path
  import gzip
  with tempfile.TemporaryDirectory() as root:
   store=MapWeatherStore(root);p=Path(root)/'raw-test.json';p.write_bytes(b'original');p.with_name(p.name+'.gz').write_bytes(gzip.compress(b'different'))
   with self.assertRaises(HazardError):store.compact()
   self.assertEqual(p.read_bytes(),b'original')

 def test_smallest_complete_fresh_field_is_reused(self):
  import time
  class Response(io.BytesIO):
   status=200
   def geturl(self):return 'https://api.open-meteo.com/v1/forecast'
  with tempfile.TemporaryDirectory() as root:
   now=[time.time()];calls=[]
   def get(request,**kwargs):
    calls.append(1);r=fixture();q=parse_qs(urlsplit(request.full_url).query)
    for n,y,x in zip(r,q['latitude'][0].split(','),q['longitude'][0].split(',')):n.update(latitude=float(y),longitude=float(x))
    return Response(json.dumps(r).encode())
   store=MapWeatherStore(root,opener=get,clock=lambda:now[0]);store.acquire(B);first=store.snapshot()['forecast']['id'];now[0]+=66;store.acquire([[36.,4.],[50.,23.]])
   self.assertNotEqual(store.snapshot()['forecast']['id'],first);store.acquire(B);self.assertEqual(store.snapshot()['forecast']['id'],first);self.assertEqual(len(calls),2)
