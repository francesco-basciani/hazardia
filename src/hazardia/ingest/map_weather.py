"""Bounded global viewport display forecast. Never simulator forcing."""
import datetime as dt,hashlib,json,math,sqlite3,threading,time,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlencode,parse_qs,urlsplit
from hazardia.io import HazardError,load,write_new,utcnow,timestamp
from hazardia.ingest.wind import vector,finite
VARS={'wind_speed_10m':'m/s','wind_direction_10m':'°','temperature_2m':'°C','precipitation':'mm'}
EXTRA={'relative_humidity_2m':('%','humidity',0,100),'surface_pressure':('hPa','pressure',300,1200),'cloud_cover':('%','cloud',0,100),'wind_gusts_10m':('m/s','gusts',0,200),'shortwave_radiation':('W/m²','radiation',0,2000)}
CAP=1024**2;TTL=10800;LIMIT=48

def grid(bounds):
    if not isinstance(bounds,list) or len(bounds)!=2 or any(not isinstance(p,list) or len(p)!=2 for p in bounds):raise HazardError('INVALID_INPUT','Two WGS84 bounds required')
    a,b=bounds
    if not all(finite(v) for p in bounds for v in p) or not -85<=a[0]<b[0]<=85 or not -180<=a[1]<b[1]<=180:raise HazardError('INVALID_INPUT','Ordered WGS84 viewport required; no dateline wrapping')
    # Pad viewport and impose minimum span: never request pseudo street-scale weather.
    mid=[(a[i]+b[i])/2 for i in range(2)];span=[max(.8,(b[i]-a[i])*1.3) for i in range(2)]
    lo=[max([-85,-180][i],math.floor((mid[i]-span[i]/2)*10)/10) for i in range(2)];hi=[min([85,180][i],math.ceil((mid[i]+span[i]/2)*10)/10) for i in range(2)]
    ys=[round(lo[0]+(hi[0]-lo[0])*i/8,6) for i in range(9)];xs=[round(lo[1]+(hi[1]-lo[1])*i/8,6) for i in range(9)]
    return ys,xs

def url(bounds):
    ys,xs=grid(bounds);points=[(y,x) for y in ys for x in xs]
    return 'https://api.open-meteo.com/v1/forecast?'+urlencode(dict(latitude=','.join(str(y) for y,x in points),longitude=','.join(str(x) for y,x in points),hourly=','.join([*VARS,*EXTRA]),timezone='UTC',wind_speed_unit='ms',forecast_days=4,models='icon_global',cell_selection='nearest',elevation=','.join(['nan']*81)),safe=',')

def normalize(raw,receipt):
    q=parse_qs(urlsplit(receipt['url']).query);ys0=[float(x) for x in q['latitude'][0].split(',')];xs0=[float(x) for x in q['longitude'][0].split(',')]
    requested=q.get('hourly',[''])[0].split(',');extra={k:v for k,v in EXTRA.items() if k in requested}
    ys=ys0[::9];xs=xs0[:9];points=list(zip(ys0,xs0))
    if len(points)!=81 or q.get('models')!=['icon_global'] or not isinstance(raw,list) or len(raw)!=81:raise HazardError('SOURCE_MISSING','Complete 81-node ICON global field required')
    times=None;series=[];nodes=[]
    for i,(loc,(y,x)) in enumerate(zip(raw,points)):
        if loc.get('utc_offset_seconds')!=0 or loc.get('timezone') not in ['GMT','UTC']:raise HazardError('SOURCE_TIME','UTC required')
        if loc.get('location_id',i)!=i:raise HazardError('SOURCE_POSITION','Node ordering changed')
        py,px=loc.get('latitude'),loc.get('longitude')
        if not finite(py) or not finite(px) or abs(py-y)>.25 or abs(px-x)>.25:raise HazardError('SOURCE_POSITION','Unexpected nearest model coordinate')
        if loc.get('hourly_units')!={'time':'iso8601',**VARS,**{k:v[0] for k,v in extra.items()}}:raise HazardError('SOURCE_UNIT','Map weather units differ')
        h=loc.get('hourly',{});ts=h.get('time',[])
        if not 24<=len(ts)<=(216 if q.get('past_days')==['7'] and q.get('forecast_days')==['2'] else 100) or times is not None and ts!=times:raise HazardError('SOURCE_TIME','Common hourly horizon required')
        if times is None:
            parsed=[timestamp(t+':00Z') for t in ts]
            if any((b-a).total_seconds()!=3600 for a,b in zip(parsed,parsed[1:])):raise HazardError('SOURCE_TIME','Hourly gap')
            times=ts
        if any(len(h.get(k,[]))!=len(times) or any(not finite(v) for v in h[k]) for k in [*VARS,*extra]):raise HazardError('SOURCE_MISSING','Missing map weather values')
        if any(not 0<=s<=150 or not 0<=d<=360 or not -100<=t<=70 or not 0<=p<=2000 for s,d,t,p in zip(*(h[k] for k in VARS))):raise HazardError('SOURCE_RANGE','Invalid meteorological values')
        for k,(_,_,lo,hi) in extra.items():
            if any(not lo<=v<=hi for v in h[k]):raise HazardError('SOURCE_RANGE','Invalid supporting weather value')
        nodes.append([py,px]);series.append(h)
    # IDW on actual returned coordinates to the requested regular display grid.
    weights=[]
    for y,x in points:
        near=sorted((((py-y)**2+((px-x)*math.cos(math.radians(y)))**2,i) for i,(py,px) in enumerate(nodes)))[:4]
        if near[0][0]<1e-14:weights.append([(near[0][1],1.)]);continue
        total=sum(1/d for d,i in near);weights.append([(i,1/d/total) for d,i in near])
    records=[]
    for n,t in enumerate(times[:-1]):
        uv=[vector(h['wind_speed_10m'][n],h['wind_direction_10m'][n]) for h in series]
        mix=lambda values:[round(sum(values[i]*w for i,w in ws),4) for ws in weights]
        records.append(dict(at=t+':00Z',u=mix([v[0] for v in uv]),v=mix([v[1] for v in uv]),temperature=mix([h['temperature_2m'][n] for h in series]),precipitation=mix([h['precipitation'][n+1] for h in series]),**{v[1]:mix([h[k][n+1 if k=='shortwave_radiation' or k=='wind_gusts_10m' and receipt.get('normalization_version',1)>=2 else n] for h in series]) for k,v in extra.items()}))
    return dict(kind='viewport_weather_display',schema_version='0.1.0',id='map-weather-'+receipt['sha256'][:24],model='DWD ICON Global via Open-Meteo',issued_at=None,issued_at_status='UNKNOWN_PROVIDER',available_at=receipt['available_at'],requested_nodes=81,lats=ys,lons=xs,bounds=[[ys[0],xs[0]],[ys[-1],xs[-1]]],model_nodes=nodes,records=records,units=dict(wind='m/s',temperature='°C',precipitation='mm/h',**{v[1]:v[0] for v in extra.values()}),source=receipt,interval_semantics='temperature/wind instantaneous; precipitation from following provider end-hour, representing hour starting at at'+('; gusts maximum and radiation mean for following hour' if receipt.get('normalization_version',1)>=2 else ''),qualification='DISPLAY_ONLY_UNCALIBRATED')

class MapWeatherStore:
    def __init__(self,root,*,opener=urllib.request.urlopen,clock=time.time):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.opener=opener;self.clock=clock;self.busy=threading.Lock()
        with self.connect() as db:db.executescript('CREATE TABLE IF NOT EXISTS attempts(at REAL PRIMARY KEY); CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1),snapshot TEXT,error TEXT); INSERT OR IGNORE INTO state VALUES(1,NULL,NULL);')
    def connect(self):return sqlite3.connect(self.root/'quota.sqlite',timeout=10)
    def read(self,name):
        f=load(self.root/name);r=f['source'];raw=self.root/('raw-'+r['sha256']+'.json')
        if hashlib.sha256(raw.read_bytes()).hexdigest()!=r['sha256'] or load(self.root/('receipt-'+r['sha256']+'.json'))!=r or normalize(load(raw),r)!=f:raise HazardError('CACHE_CORRUPT','Map forecast integrity differs')
        return f
    def snapshot(self):
        now=self.clock()
        with self.connect() as db:
            name,error=db.execute('SELECT snapshot,error FROM state WHERE id=1').fetchone();count=db.execute('SELECT count(*) FROM attempts WHERE at>=?',(now-now%86400,)).fetchone()[0]
        f=self.read(name) if name else None;age=now-timestamp(f['available_at']).timestamp() if f else None
        return dict(status='EMPTY' if not f else 'FRESH' if 0<=age<TTL else 'STALE',forecast=f,error=error,age_s=age,fetching=self.busy.locked(),quota=dict(attempts_today=count,local_daily_limit=LIMIT,location_equivalents_per_refresh=81,max_location_equivalents_daily=3888,refresh_s=65))
    def acquire(self,bounds):
        address=url(bounds) # validate even if already busy
        requested_y,requested_x=grid(bounds)
        if not self.busy.acquire(False):return
        try:
            now=self.clock()
            # Reuse any fresh field containing the entire requested viewport.
            for path in sorted(self.root.glob('map-weather-*.json'),key=lambda p:p.stat().st_mtime,reverse=True):
                f=load(path);a,b=f['bounds'];age=now-timestamp(f['available_at']).timestamp()
                if f['source'].get('normalization_version',1)>=2 and set(EXTRA)<=set(parse_qs(urlsplit(f['source']['url']).query).get('hourly',[''])[0].split(',')) and (b[0]-a[0])<=4*(requested_y[-1]-requested_y[0]) and (b[1]-a[1])<=4*(requested_x[-1]-requested_x[0]) and 0<=age<TTL and all(a[i]<=bounds[0][i] and b[i]>=bounds[1][i] for i in range(2)):
                    self.read(path.name)
                    with self.connect() as db:db.execute('UPDATE state SET snapshot=?,error=NULL WHERE id=1',(path.name,))
                    return
            with self.connect() as db:
                db.execute('BEGIN IMMEDIATE');last=db.execute('SELECT max(at) FROM attempts').fetchone()[0];count=db.execute('SELECT count(*) FROM attempts WHERE at>=?',(now-now%86400,)).fetchone()[0]
                if last is not None and now-last<65:raise HazardError('WEATHER_THROTTLED','Attendi fino a65s per una nuova area; cache disponibile conservata')
                if count>=LIMIT:raise HazardError('WEATHER_QUOTA','Budget giornaliero gratuito esaurito per nuove aree')
                if sum(p.stat().st_size for p in self.root.glob('*.json'))>64*1024**2-3*CAP:raise HazardError('WEATHER_CACHE_FULL','Archivio meteo pieno; nessun download aggiuntivo')
                db.execute('INSERT INTO attempts VALUES(?)',(now,))
            request=urllib.request.Request(address,headers={'User-Agent':'HAZARDIA/0.1 https://github.com/francesco-basciani/hazardia','Accept-Encoding':'identity'})
            with self.opener(request,timeout=30) as response:
                if getattr(response,'status',200)!=200 or not response.geturl().startswith('https://api.open-meteo.com/'):raise HazardError('SOURCE_URL','Unexpected map forecast response')
                data=response.read(CAP+1)
                if len(data)>CAP:raise HazardError('DOWNLOAD_BUDGET','Map weather response exceeds1MiB')
            digest=hashlib.sha256(data).hexdigest();receipt=dict(normalization_version=2,provider='Open-Meteo',url=address,sha256=digest,bytes=len(data),available_at=utcnow(),license_url='https://open-meteo.com/en/terms',model_initialization='NOT_SUPPLIED')
            raw=self.root/('raw-'+digest+'.json');rec=self.root/('receipt-'+digest+'.json')
            if not raw.exists():raw.write_bytes(data)
            if not rec.exists():write_new(rec,receipt)
            receipt=load(rec);f=normalize(json.loads(data),receipt);name=f['id']+'.json'
            if not (self.root/name).exists():write_new(self.root/name,f)
            with self.connect() as db:db.execute('UPDATE state SET snapshot=?,error=NULL WHERE id=1',(name,))
        except urllib.error.HTTPError as e:
            body=e.read(4096).decode('utf-8','replace');write_new(self.root/('error-'+str(int(self.clock()*1000))+'.json'),dict(status=e.code,body=body,url=address,at=utcnow()))
            with self.connect() as db:db.execute('UPDATE state SET error=? WHERE id=1',('SOURCE_HTTP_'+str(e.code)+': '+body[:500],))
        except Exception as e:
            with self.connect() as db:db.execute('UPDATE state SET error=? WHERE id=1',((e.code+': '+str(e)) if isinstance(e,HazardError) else type(e).__name__+': map weather unavailable',))
        finally:self.busy.release()
