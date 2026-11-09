"""Public ARPA Piemonte gauges; preserve gauge datum, negative heights and source dates."""
import datetime as dt,gzip,hashlib,json,math,shutil,threading,time,urllib.parse,urllib.request
from pathlib import Path
from hazardia.io import HazardError
from hazardia.ingest.thermal import stamp
UTC=dt.timezone.utc
BASE='https://utility.arpa.piemonte.it/api_realtime/'
CAP=2*1024**2

def moment(value):
    at=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    if at.tzinfo is None:raise ValueError('Source observation needs explicit timezone')
    return at.astimezone(UTC)

def normalize(registry,payload,acquired):
    if not isinstance(registry,list) or len(registry)>1000:raise ValueError('Bounded station registry required')
    if not isinstance(payload,dict) or payload.get('total_pages')!=1 or not isinstance(payload.get('data'),list) or len(payload['data'])>2000 or payload.get('total_items')!=len(payload['data']):raise ValueError('Complete single-page observation window required')
    latest={};rejected=0
    for row in payload['data']:
        try:
            value=row.get('hydrometric_level')
            if value is None:continue
            if type(value) not in (int,float) or not math.isfinite(value):raise ValueError('Finite gauge height required')
            at=moment(row['date'])
            if at>acquired+dt.timedelta(minutes=5) or at<acquired-dt.timedelta(days=7):raise ValueError('Source date outside retained window')
            key=(row['id_network'],row['station_code'])
            if key not in latest or at>latest[key][0]:latest[key]=(at,value)
        except (ValueError,TypeError,KeyError):rejected+=1
    result=[]
    for station in registry:
        try:
            key=(station['id_network'],station['station_code'])
            if key not in latest:continue
            lat,lon=station['lat'],station['lng']
            if not all(type(x) in (int,float) and math.isfinite(x) for x in (lat,lon)) or not -90<=lat<=90 or not -180<=lon<=180:raise ValueError('Invalid station coordinate')
            at,value=latest[key];age=(acquired-at).total_seconds()/60
            result.append(dict(type='Feature',id='-'.join(key),geometry=dict(type='Point',coordinates=[lon,lat]),properties=dict(id='-'.join(key),name=station['name'],river=station.get('river_name'),level_m=value,at=stamp(at),age_minutes=round(age,1),freshness='FRESH' if 0<=age<=120 else 'STALE',gauge_zero=station.get('hydrometric_zero') or None,qualification='AUTOMATIC_OBSERVATION_NOT_FLOOD_WARNING',source='Arpa Piemonte',license='CC BY4.0')))
        except (ValueError,TypeError,KeyError):rejected+=1
    return dict(type='FeatureCollection',features=result,rejected_rows=rejected,acquired_at=stamp(acquired),observation_until=max((f['properties']['at'] for f in result),default=None),attribution='Fonte: Arpa Piemonte - www.arpa.piemonte.it',license='CC BY4.0',license_url='https://www.arpa.piemonte.it/note-legali',source=BASE+'docs',coverage='Available Arpa Piemonte stations only; no current Abruzzo telemetry',semantics='Gauge height in metres relative to the station datum; negative levels are valid. Not water depth or inundation extent. No threshold or model coupling.',coupled_to_models=False)

class HydrometerStore:
    def __init__(self,root,fetch=None):
        self.root=Path(root);self.root.mkdir(exist_ok=True);self.lock=threading.Lock();self.busy=False;self.fetch=fetch or self._fetch;self.error=None
    @staticmethod
    def _fetch(url):
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HAZARDIA research consultation/1'}),timeout=15) as r:
            if r.geturl()!=url:raise ValueError('Unexpected source redirect')
            raw=r.read(CAP+1)
        if len(raw)>CAP:raise ValueError('Hydrometer source exceeds2MiB')
        return raw
    def snapshot(self):
        p=self.root/'latest.json';data=json.loads(p.read_text()) if p.exists() else None
        return dict(status='AVAILABLE' if data else 'MISSING',busy=self.busy,error=self.error,data=data)
    def refresh(self):
        path=self.root/'attempts.json';now=time.time()
        with self.lock:
            entries=json.loads(path.read_text()) if path.exists() else []
            entries=[x for x in entries if x>now-86400]
            if self.busy:return dict(status='BUSY')
            if entries and now-entries[-1]<3600:return dict(status='CACHED')
            # At most3 requests x2MiB per build, total at most24MiB/day.
            if len(entries)>=4:raise HazardError('SOURCE_QUOTA','Hydrometers4builds/day maximum; existing observations retained')
            if sum(p.stat().st_size for p in self.root.iterdir())+8*1024**2>24*1024**2 or shutil.disk_usage(self.root).free<2*1024**3+12*1024**2:raise HazardError('CACHE_FULL','Hydrometer cache24MiB/free reserve2GiB')
            entries.append(now);path.write_text(json.dumps(entries));self.busy=True;self.error=None
        def work():
            try:
                sources=[]
                def get(path):
                    url=BASE+path;raw=self.fetch(url)
                    if len(raw)>CAP:raise ValueError('Hydrometer source exceeds2MiB')
                    digest=hashlib.sha256(raw).hexdigest();source=self.root/(digest+'.json.gz')
                    if not source.exists():source.write_bytes(gzip.compress(raw,mtime=0))
                    sources.append(dict(url=url,sha256=digest));return json.loads(raw)
                registry=get('pie_anag')
                # The first published hydrometric station supplies an actual data timestamp;
                # never invent a time or silently label this historical fallback as current.
                stations=[s for s in registry if s.get('river_name') not in ('','-',None)]
                if not stations:raise ValueError('Hydrometric station registry unavailable')
                probe=get('data_pie?'+urllib.parse.urlencode(dict(station_code=stations[0]['station_code'],page_size=200)))
                if probe.get('total_pages')!=1:raise ValueError('Station date probe is truncated')
                dates=[moment(r['date']) for r in probe.get('data') or [] if type(r.get('hydrometric_level')) in (int,float)]
                if not dates:raise ValueError('No published hydrometer measurements')
                end=max(dates);start=end-dt.timedelta(hours=3)
                # The API documents naive query timestamps, with source responses carrying
                # explicit offsets. Express bounds in Europe/Rome, matching the published API.
                from zoneinfo import ZoneInfo
                zone=ZoneInfo('Europe/Rome')
                query=dict(date_from=start.astimezone(zone).strftime('%Y-%m-%dT%H:%M'),date_to=end.astimezone(zone).strftime('%Y-%m-%dT%H:%M'),page_size=2000)
                payload=get('data_pie?'+urllib.parse.urlencode(query));data=normalize(registry,payload,dt.datetime.now(UTC));data['sources']=sources;encoded=json.dumps(data,allow_nan=False).encode()
                if not data['features']:raise ValueError('No mapped source measurements; not zero water levels')
                if sum(p.stat().st_size for p in self.root.iterdir())+len(encoded)*2>24*1024**2:raise ValueError('Hydrometer archive admission limit')
                key=hashlib.sha256(encoded).hexdigest();(self.root/(key+'.receipt.json')).write_bytes(encoded)
                tmp=self.root/'latest.tmp';tmp.write_bytes(encoded);tmp.replace(self.root/'latest.json')
            except Exception as exc:self.error=str(exc)
            finally:
                with self.lock:self.busy=False
        threading.Thread(target=work,name='hydrometer-observations',daemon=True).start();return dict(status='ACCEPTED')
