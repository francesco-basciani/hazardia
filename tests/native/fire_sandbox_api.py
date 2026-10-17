import json,urllib.request,time,pathlib,sys
out=pathlib.Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);base='http://127.0.0.1:8080'
def api(path,body=None):
 data=json.dumps(body).encode() if body is not None else None
 r=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json','X-Hazardia-Research':'1'})
 with urllib.request.urlopen(r,timeout=60) as f:return json.load(f)
b=dict(ignitions=[dict(id='i1',point=[42.35,13.38],at_minutes=0),dict(id='i2',point=[42.352,13.382],at_minutes=60)],hours=3,seed=1729,moisture_percent=10,resources=[],comparison_times=[0,3600],weather_source='HISTORICAL',weather_changes=[])
area=dict(id='ground',category='waterline_action',effect='fuel_removal',area=[[42.346,13.374],[42.346,13.388],[42.356,13.388],[42.356,13.374]],at_minutes=60)
line=dict(id='ground-line',category='waterline_action',effect='fuel_removal',line=[[42.3495,13.38],[42.3505,13.38]],at_minutes=0)
cases={'baseline':b,'area':dict(b,resources=[area]),'noop':b,'line':dict(b,resources=[line])}
ids={}
for name,body in cases.items():
 (out/(name+'-input.json')).write_text(json.dumps(body,indent=2));ids[name]=api('/api/firelab/scenario',body)['jobs']['B'];print(name,ids[name],flush=True)
(out/'native-jobs.json').write_text(json.dumps(ids,indent=2))
start=time.monotonic();states={}
while time.monotonic()-start<500:
 states={name:api('/api/firelab/'+job) for name,job in ids.items()}
 if all(v['state'] in ['SUCCEEDED','ERROR','TIMEOUT','CANCELLED'] for v in states.values()):break
 time.sleep(3)
for name,value in states.items():(out/(name+'-result.json')).write_text(json.dumps(value,indent=2))
checks={name+'_succeeded':v['state']=='SUCCEEDED' for name,v in states.items()}
if all(checks.values()):
 a=states['baseline']['series'];b=states['area']['series'];c=states['noop']['series']
 checks.update(multiple_ignitions=sum(e['ignition_count'] for e in a['consumed_events'])==2,delayed_ignition=any(e['time']==3600 and e['ignition_count']==1 for e in a['consumed_events']),polygon_native_cells=any(e['time']==3600 and e['vegetation_changed_cells']>0 and e['fuel_removal_geometries']==1 for e in b['consumed_events']),noop_probability_hashes=[f['sha256'] for f in a['frames']]==[f['sha256'] for f in c['frames']],area_reduces_spread=b['frames'][-1]['expected_area_ha']<a['frames'][-1]['expected_area_ha'],before_intervention_identical=a['frames'][0]['sha256']==b['frames'][0]['sha256'],line_fuel_consumed=any(e['fuel_removal_geometries']==1 and e['vegetation_changed_cells']>0 for e in states['line']['series']['consumed_events']))
 print('AREAS',a['frames'][-1]['expected_area_ha'],b['frames'][-1]['expected_area_ha'],flush=True)
(out/'native-verification.json').write_text(json.dumps(checks,indent=2));print(checks,flush=True)

if not all(checks.values()):raise SystemExit(1)
