import copy,datetime as dt,io,json,tempfile,unittest,time
from pathlib import Path
from hazardia.ingest.wind import normalize,vector,WindStore,POINTS
from hazardia.io import HazardError

def raw():
    times=[(dt.datetime(2026,10,16)+dt.timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M') for i in range(24)]
    return [dict(location_id=i,latitude=y,longitude=x,timezone='GMT',utc_offset_seconds=0,hourly_units={'time':'iso8601','wind_speed_10m':'m/s','wind_direction_10m':'°'},hourly=dict(time=times,wind_speed_10m=[5.]*24,wind_direction_10m=[90.]*24)) for i,(y,x) in enumerate(POINTS)]
def receipt():return dict(sha256='b'*64,available_at='2026-10-16T00:00:00Z')
class Response(io.BytesIO):
    headers={};status=200
    def geturl(self):return 'https://api.open-meteo.com/v1/forecast'
class RegionalWindTests(unittest.TestCase):
    def reject(self,code,fn):
        with self.assertRaises(HazardError) as e:fn()
        self.assertEqual(e.exception.code,code)
    def test_provider_multi_coordinate_parameters(self):
        from urllib.parse import urlsplit,parse_qs
        from hazardia.ingest.wind import URL
        q=parse_qs(urlsplit(URL).query)
        self.assertEqual(len(q['elevation'][0].split(',')),315)
        self.assertEqual(q['cell_selection'],['nearest'])
        self.assertLess(len(URL),8192)
    def test_cardinal_direction_is_flow_not_from(self):
        for d,want in [(0,(0,-5)),(90,(-5,0)),(180,(0,5)),(270,(5,0))]:
            got=vector(5,d)
            for a,b in zip(got,want):self.assertAlmostEqual(a,b,places=10)
    def test_actual_coordinates_and_complete_grid(self):
        n=normalize(raw(),receipt());self.assertEqual(n['requested_nodes'],315);self.assertEqual(len(n['records']),24);self.assertEqual(len(n['records'][0]['u']),315);self.assertEqual(set(n['records'][0]['u']),{-5.});self.assertEqual(set(n['records'][0]['v']),{0.});self.assertIsNone(n['issued_at']);self.assertEqual(n['bounds'],[[41.6,12.9],[43.,14.9]])
    def test_missing_node_or_hour_rejected(self):
        r=raw();self.reject('SOURCE_MISSING',lambda:normalize(r[:-1],receipt()));r[0]['hourly']['time']=r[0]['hourly']['time'][:-1];self.reject('SOURCE_TIME',lambda:normalize(r,receipt()))
    def test_inconsistent_time_and_units_rejected(self):
        r=raw();r[1]['hourly']['time'][0]='2026-10-15T00:00';self.reject('SOURCE_TIME',lambda:normalize(r,receipt()));r=raw();r[2]['hourly_units']['wind_speed_10m']='km/h';self.reject('SOURCE_UNIT',lambda:normalize(r,receipt()))
    def test_null_or_invalid_wind_rejected(self):
        for k,v in [('wind_speed_10m',None),('wind_speed_10m',-1),('wind_direction_10m',361),('wind_direction_10m',float('nan'))]:
            r=raw();r[3]['hourly'][k][0]=v;self.reject('SOURCE_RANGE',lambda:normalize(r,receipt()))
    def test_returned_coordinate_and_order_rejected(self):
        r=raw();r[4]['latitude']=0;self.reject('SOURCE_POSITION',lambda:normalize(r,receipt()));r=raw();r[4]['location_id']=7;self.reject('SOURCE_POSITION',lambda:normalize(r,receipt()))
    def test_idw_uses_components_across_north_wrap(self):
        r=raw()
        for i,l in enumerate(r):l['hourly']['wind_direction_10m']=[359 if i%2 else 1]*24;l['longitude']+=.02
        n=normalize(r,receipt());self.assertTrue(all(v< -4.9 for v in n['records'][0]['v']));self.assertTrue(all(abs(u)<.1 for u in n['records'][0]['u']))
    def test_shared_cache_and_weighted_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            def get(*a,**k):calls.append(1);return Response(json.dumps(raw()).encode())
            s=WindStore(tmp,opener=get);s.refresh();WindStore(tmp,opener=get).refresh();self.assertEqual(len(calls),1);self.assertEqual(s.snapshot()['quota']['max_location_equivalents_daily'],2520);self.assertEqual(s.snapshot()['quota']['refresh_s'],10800)
    def test_identical_payload_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=json.dumps(raw()).encode();s=WindStore(tmp,opener=lambda *a,**k:Response(data));s.refresh();first=s.snapshot()['forecast']['source'];s.clock=lambda:time.time()+10801;s.refresh();self.assertEqual(s.snapshot()['forecast']['source'],first)
            f=next(Path(tmp).glob('raw-*.json'));f.write_bytes(b'[]');self.reject('CACHE_CORRUPT',s.snapshot)
    def test_budget_and_failed_response_are_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            now=dt.datetime(2026,10,16,23,59,tzinfo=dt.timezone.utc).timestamp();s=WindStore(tmp,clock=lambda:now)
            with s.connect() as db:
                for i in range(8):db.execute('INSERT INTO attempts VALUES(?)',(now-now%86400+i,))
            self.reject('WEATHER_QUOTA',s.refresh)
        with tempfile.TemporaryDirectory() as tmp:
            s=WindStore(tmp,opener=lambda *a,**k:Response(b'[]'));s.refresh();self.assertIsNone(s.snapshot()['forecast']);self.assertIn('SOURCE_MISSING',s.snapshot()['error'])
