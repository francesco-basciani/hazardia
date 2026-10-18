"""Bounded 168h antecedent ICON field, sharing the existing free API budget."""
import hashlib,json,urllib.request
from urllib.parse import parse_qs,urlsplit,urlencode
from hazardia.io import HazardError,load,write_new,utcnow,timestamp
from hazardia.ingest.map_weather import CAP,LIMIT,normalize

def history_rows(field,start):
 import datetime as dt
 begin=timestamp(start);by={r['at']:r for r in field['records']};rows=[]
 for h in range(168,0,-1):
  at=(begin-dt.timedelta(hours=h)).isoformat().replace('+00:00','Z')
  if at not in by:raise HazardError('SOURCE_MISSING','Complete168h antecedent weather required')
  rows.append(by[at])
 return rows

def acquire(store,field,start):
 q=parse_qs(urlsplit(field['source']['url']).query);params={k:v[0] for k,v in q.items()};params.update(hourly='wind_speed_10m,wind_direction_10m,temperature_2m,precipitation,relative_humidity_2m',past_days=7,forecast_days=2);address='https://api.open-meteo.com/v1/forecast?'+urlencode(params,safe=',')
 # Cache reuse is exact-grid and complete-window; never a single-point substitute.
 for path in sorted(store.root.glob('history-map-weather-*.json'),key=lambda p:p.stat().st_mtime,reverse=True):
  cached=store.read(path.name)
  if cached['lats']==field['lats'] and cached['lons']==field['lons'] and 0<=(timestamp(utcnow())-timestamp(cached['available_at'])).total_seconds()<10800:
   try:history_rows(cached,start);return cached
   except HazardError:pass
 if not store.busy.acquire(False):raise HazardError('WEATHER_THROTTLED','Weather source busy')
 try:
  now=store.clock()
  with store.connect() as db:
   db.execute('BEGIN IMMEDIATE');last=db.execute('SELECT max(at) FROM attempts').fetchone()[0];count=db.execute('SELECT count(*) FROM attempts WHERE at>=?',(now-now%86400,)).fetchone()[0]
   if last is not None and now-last<65:raise HazardError('WEATHER_THROTTLED','Shared65s request interval')
   if count>=LIMIT:raise HazardError('WEATHER_QUOTA','Shared free daily budget exhausted')
   if sum(p.stat().st_size for p in store.root.glob('*.json'))>64*1024**2-3*CAP:raise HazardError('WEATHER_CACHE_FULL','Weather archive budget reached')
   db.execute('INSERT INTO attempts VALUES(?)',(now,))
  with store.opener(urllib.request.Request(address,headers={'User-Agent':'HAZARDIA/0.1 Research','Accept-Encoding':'identity'}),timeout=30) as response:
   if getattr(response,'status',200)!=200 or not response.geturl().startswith('https://api.open-meteo.com/'):raise HazardError('SOURCE_URL','Unexpected antecedent provider')
   raw=response.read(CAP+1)
   if len(raw)>CAP:raise HazardError('DOWNLOAD_BUDGET','Antecedent response exceeds1MiB')
  digest=hashlib.sha256(raw).hexdigest();receipt=dict(normalization_version=2,provider='Open-Meteo',url=address,sha256=digest,bytes=len(raw),available_at=utcnow(),license_url='https://open-meteo.com/en/terms',model_initialization='NOT_SUPPLIED')
  for name,data in [('raw-'+digest+'.json',raw),('receipt-'+digest+'.json',json.dumps(receipt).encode())]:
   if not (store.root/name).exists():(store.root/name).write_bytes(data)
  receipt=load(store.root/('receipt-'+digest+'.json'));result=normalize(json.loads(raw),receipt);history_rows(result,start);name='history-'+result['id']+'.json'
  if not (store.root/name).exists():write_new(store.root/name,result)
  return result
 finally:store.busy.release()
