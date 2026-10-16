import copy,unittest
from hazardia.firelab import validate
from hazardia.io import HazardError
class FireLabTests(unittest.TestCase):
 def body(self):return dict(ignition=[42.35,13.38],hours=24,seed=1729,moisture_percent=10,resources=[dict(id='u',category='canadair',line=[[42.35,13.38],[42.351,13.38]],at_minutes=15)],weather_source='HISTORICAL',weather_changes=[dict(hour=1,speed_ms=6,direction_deg=270)])
 def test_categories(self):
  for category in ['waterline_action','canadair','helicopter','heavy_action']:
   b=self.body();b['resources'][0]['category']=category;self.assertEqual(validate(b),b)
 def test_invalid_core(self):
  for key,val in [('hours',73),('hours',True),('seed',-1),('moisture_percent',float('nan')),('ignition',[91,13]),('weather_source','AUTOMATIC_FAKE')]:
   b=self.body();b[key]=val
   with self.assertRaises(HazardError):validate(b)
 def test_invalid_actions(self):
  for key,val in [('category','magic'),('line',[[42,13],[42,13]]),('at_minutes',-1),('at_minutes',1440),('id',[])]:
   b=self.body();b['resources'][0][key]=val
   with self.assertRaises(HazardError):validate(b)
 def test_duplicates(self):
  for key in ['resources','weather_changes']:
   b=self.body();b[key]*=2
   with self.assertRaises(HazardError):validate(b)
 def test_unknown_fields(self):
  b=self.body();b['operational_dispatch']=True
  with self.assertRaises(HazardError):validate(b)
 def test_invalid_weather(self):
  for key,val in [('hour',24),('speed_ms',float('inf')),('direction_deg',-1)]:
   b=self.body();b['weather_changes'][0][key]=val
   with self.assertRaises(HazardError):validate(b)
 def plan(self):
  req=dict(valid_from='2024-07-13T13:00:00Z',options=dict(duration_s=3600,seed=1729,moisture_percent=10));v=dict(wind_speed_10m=2,wind_direction_10m=90,temperature_2m=20,precipitation=0,relative_humidity_2m=50);weather=dict(records=[dict(at=req['valid_from'],values=v)]);p=dict(case='A',ignition_wgs84=[42.35,13.38],weather_source='HISTORICAL',records=[dict(time=0,at=req['valid_from'],values=v.copy())],resources=[],action_times=[],weather_changes=[],qualification='UNQUALIFIED_RESEARCH',moisture_percent=10);return p,req,weather
 def test_consumed_plan_matches_source(self):
  from hazardia.firelab import validate_plan
  p,q,w=self.plan();self.assertEqual(validate_plan(p,q,w),p)
 def test_undeclared_weather_and_clock_rejected(self):
  from hazardia.firelab import validate_plan
  for change in ['wind','rain','clock','missing']:
   p,q,w=self.plan()
   if change=='wind':p['records'][0]['values']['wind_speed_10m']=8
   elif change=='rain':p['records'][0]['values']['precipitation']=50
   elif change=='clock':p['records'][0]['time']=1
   else:p['records']=[]
   with self.assertRaises(HazardError):validate_plan(p,q,w)
