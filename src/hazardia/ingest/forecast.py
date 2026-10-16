"""Bounded Open-Meteo free-tier point forecast; VM-shared immutable snapshots.
No API key, arbitrary URL/coordinates, billing endpoint, or dispatch.
"""
import datetime as dt,hashlib,json,math,sqlite3,threading,time,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlencode
from hazardia.io import HazardError,load,utcnow,write_new,timestamp
VARIABLES={'temperature_2m':'°C','relative_humidity_2m':'%','precipitation':'mm','wind_speed_10m':'m/s','wind_direction_10m':'°','surface_pressure':'hPa','shortwave_radiation':'W/m²'}
URL='https://api.open-meteo.com/v1/forecast?'+urlencode(dict(latitude=42.35,longitude=13.38,hourly=','.join(VARIABLES),timezone='UTC',wind_speed_unit='ms',forecast_days=4,models='icon_eu'))
TTL=1800;DAILY_LIMIT=48;CAP=256*1024;CACHE_CAP=16*1024**2

def normalize(raw,receipt):
    if raw.get('utc_offset_seconds')!=0 or raw.get('timezone') not in ['GMT','UTC']:raise HazardError('SOURCE_TIME','UTC forecast required')
    units=raw.get('hourly_units',{});h=raw.get('hourly',{});times=h.get('time',[])
    if any(units.get(k)!=v for k,v in VARIABLES.items()):raise HazardError('SOURCE_UNIT','Forecast variables/units missing or incompatible')
    if not 8<=len(times)<=100 or any(len(h.get(k,[]))!=len(times) for k in VARIABLES):raise HazardError('SOURCE_MISSING','Complete bounded hourly series required')
    parsed=[timestamp(t+':00Z') for t in times]
    if any((b-a).total_seconds()!=3600 for a,b in zip(parsed,parsed[1:])):raise HazardError('SOURCE_TIME','Forecast hourly gap/duplicate')
    for k in VARIABLES:
        if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) for v in h[k]):raise HazardError('SOURCE_MISSING','Null/nonfinite forecast variable: '+k)
    records=[]
    for i,t in enumerate(times[:-1]):
        values={k:h[k][i+1 if k in ['precipitation','shortwave_radiation'] else i] for k in VARIABLES}
        if not (values['precipitation']>=0 and values['wind_speed_10m']>=0 and 0<=values['wind_direction_10m']<=360 and 0<=values['relative_humidity_2m']<=100 and values['surface_pressure']>0 and values['shortwave_radiation']>=0):raise HazardError('SOURCE_RANGE','Invalid forecast range')
        records.append(dict(at=t+':00Z',values=values))
    return dict(schema_version='0.3.0',kind='weather',id='openmeteo-'+receipt['sha256'][:24],data_kind='FORECAST',issued_at=None,issued_at_status='UNKNOWN_PROVIDER',available_at=receipt['available_at'],valid_from=records[0]['at'],valid_until=times[-1]+':00Z',units=VARIABLES,records=records,source=receipt,license='CC-BY-4.0',model='DWD ICON-EU via Open-Meteo',requested_point=dict(latitude=42.35,longitude=13.38),model_point={k:raw.get(k) for k in ['latitude','longitude','elevation']},interval_semantics='START_OF_HOUR: precipitation and shortwave mean shifted from next provider end-of-hour row; other variables instantaneous at start',caveats=['Real point forecast, not a sensor observation or spatially resolved basin forcing','Provider model initialization not supplied; issued_at stays unknown, first-seen availability is separate','No ensemble or calibration; fuel/moisture/soil/Q0 remain hypothetical'])

class ForecastStore:
    def __init__(self,root,*,opener=urllib.request.urlopen,clock=time.time):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.opener=opener;self.clock=clock;self.busy=threading.Lock()
        with self.connect() as db:db.executescript('CREATE TABLE IF NOT EXISTS attempts(at REAL PRIMARY KEY); CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1),snapshot TEXT,error TEXT); INSERT OR IGNORE INTO state VALUES(1,NULL,NULL);')
    def connect(self):return sqlite3.connect(self.root/'quota.sqlite',timeout=10)
    def snapshot(self):
        with self.connect() as db:
            row=db.execute('SELECT snapshot,error FROM state WHERE id=1').fetchone();now=self.clock();count=db.execute('SELECT count(*) FROM attempts WHERE at>=?',(now-now%86400,)).fetchone()[0]
        data=load(self.root/row[0]) if row[0] else None
        if data:
            digest=data['source']['sha256'];raw=self.root/('raw-'+digest+'.json');receipt=self.root/('receipt-'+digest+'.json')
            if not raw.is_file() or not receipt.is_file() or hashlib.sha256(raw.read_bytes()).hexdigest()!=digest or load(receipt)!=data['source'] or normalize(load(raw),load(receipt))!=data:
                raise HazardError('CACHE_CORRUPT','Weather raw/receipt/normalized snapshot integrity differs; new simulations blocked')
        age=now-timestamp(data['available_at']).timestamp() if data else None
        return dict(status='EMPTY' if data is None else 'FRESH' if 0<=age<TTL else 'STALE',forecast=data,error=row[1],age_s=age,quota=dict(attempts_today=count,local_daily_limit=DAILY_LIMIT,refresh_s=TTL,scope='single fixed point;7variables4days; free noncommercial endpoint'),fetching=self.busy.locked())
    def fresh(self,ident=None):
        s=self.snapshot()
        if s['status']!='FRESH':raise HazardError('STALE_FORECAST','Acquire a fresh forecast before starting a new simulation')
        f=s['forecast']
        if ident!=f['id']:raise HazardError('STALE_CONTEXT','Forecast changed; refresh the selected snapshot')
        return f
    def refresh(self):
        if not self.busy.acquire(False):return self.snapshot()
        try:self.acquire()
        finally:self.busy.release()
        return self.snapshot()
    def acquire(self):
        now=self.clock()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');last=db.execute('SELECT max(at) FROM attempts').fetchone()[0]
            if last is not None and now-last<TTL:return
            count=db.execute('SELECT count(*) FROM attempts WHERE at>=?',(now-now%86400,)).fetchone()[0]
            if count>=DAILY_LIMIT:raise HazardError('WEATHER_QUOTA','Local daily free-tier safety budget exhausted')
            if sum(p.stat().st_size for p in self.root.glob('*.json'))>=CACHE_CAP-CAP*2:raise HazardError('WEATHER_CACHE_FULL','Archive weather evidence before further downloads')
            db.execute('INSERT INTO attempts VALUES(?)',(now,));db.commit()
        try:
            request=urllib.request.Request(URL,headers={'User-Agent':'HAZARDIA/0.1 https://github.com/francesco-basciani/hazardia','Accept-Encoding':'identity'})
            with self.opener(request,timeout=20) as response:
                if getattr(response,'status',200)!=200:raise HazardError('SOURCE_UNAVAILABLE','Forecast HTTP non-success')
                if int(response.headers.get('Content-Length',0))>CAP:raise HazardError('DOWNLOAD_BUDGET','Weather response too large')
                data=response.read(CAP+1)
                if len(data)>CAP:raise HazardError('DOWNLOAD_BUDGET','Weather response cap exceeded')
                final=response.geturl()
                if not final.startswith('https://api.open-meteo.com/'):raise HazardError('SOURCE_URL','Unexpected forecast redirect')
            digest=hashlib.sha256(data).hexdigest();receipt=dict(provider='Open-Meteo',url=URL,sha256=digest,bytes=len(data),available_at=utcnow(),model_initialization='NOT_SUPPLIED',license_url='https://open-meteo.com/en/terms')
            rawname='raw-'+digest+'.json'
            if not (self.root/rawname).exists():(self.root/rawname).write_bytes(data)
            if not (self.root/('receipt-'+digest+'.json')).exists():write_new(self.root/('receipt-'+digest+'.json'),receipt)
            forecast=normalize(json.loads(data),receipt)
            name=forecast['id']+'-'+str(int(now))+'.json';write_new(self.root/name,forecast)
            with self.connect() as db:db.execute('UPDATE state SET snapshot=?,error=NULL WHERE id=1',(name,))
        except Exception as e:
            with self.connect() as db:db.execute('UPDATE state SET error=? WHERE id=1',((e.code+': '+str(e)) if isinstance(e,HazardError) else type(e).__name__+': forecast unavailable',))
