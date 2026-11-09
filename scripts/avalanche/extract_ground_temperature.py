"""Read the archived forcing of the delivered cycle; no new physical inference."""
import gzip,json,pathlib,datetime,hashlib
root=pathlib.Path('/dev/shm/avalanche-terrain-build');run=pathlib.Path('/home/hazardia/avalanche-runtime/runs/20261029T215928Z');protocol=json.loads((run/'protocol.json').read_text());seed=json.loads(pathlib.Path('/home/hazardia/avalanche-runtime/seed.geojson').read_text());points=[f['properties'] for f in seed['features']];out={};inputs={}
start=datetime.datetime.fromisoformat(protocol['reference_utc'].replace('Z','+00:00'));wanted=[(start+datetime.timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M') for i in range(73)]
for batch,offset in enumerate(range(0,len(points),80)):
 path=root/f'current-weather/weather-{batch:03d}.gz';raw=gzip.decompress(path.read_bytes());inputs[path.name]=hashlib.sha256(raw).hexdigest();weather=json.loads(raw)
 for p,d in zip(points[offset:offset+80],weather):
  assert d['hourly_units']['soil_temperature_0cm']=='°C';h=d['hourly'];values=[h['soil_temperature_0cm'][h['time'].index(t)] for t in wanted]
  out[p['id']]=dict(ground_temperature_min_c=min(values),ground_temperature_max_c=max(values),ground_temperature_source='NWP TSG surface forcing, not measured soil temperature')
result=dict(reference_utc=protocol['reference_utc'],weather_run_utc=protocol['weather_run_utc'],points=out,input_sha256=inputs)
(root/'output/thermal-context.json').write_text(json.dumps(result,separators=(',',':')));print('THERMAL CONTEXT',len(out))
