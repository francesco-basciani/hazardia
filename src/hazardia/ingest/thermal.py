"""Bounded public NASA FIRMS regional CSV observations; no MAP_KEY or model coupling."""
import csv,datetime as dt,gzip,hashlib,io,json,math,shutil,threading,time,urllib.request
from pathlib import Path
from hazardia.io import HazardError

UTC=dt.timezone.utc
SOURCES={region:'https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_'+region+'_7d.csv' for region in ('Europe',)}
CAP=2*1024**2

def stamp(t):return t.astimezone(UTC).isoformat().replace('+00:00','Z')

def normalize(raw,acquired):
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    fields={'latitude','longitude','acq_date','acq_time','satellite','confidence','frp','scan','track','version'}
    if not fields<=set(reader.fieldnames or []):raise ValueError('Unexpected FIRMS CSV schema')
    features=[];rejected=0;seen=set();rows=0
    for row in reader:
        rows+=1
        if rows>20000:raise ValueError('FIRMS row limit20000 exceeded')
        try:
            lon,lat,frp,scan,track=[float(row[k]) for k in ('longitude','latitude','frp','scan','track')]
            if not all(math.isfinite(x) for x in (lon,lat,frp,scan,track)) or not -180<=lon<=180 or not -90<=lat<=90 or frp<0 or scan<=0 or track<=0:raise ValueError('Invalid numeric measurement')
            hhmm=row['acq_time'].zfill(4)
            if len(hhmm)!=4 or not hhmm.isdigit():raise ValueError('Invalid acquisition time')
            at=dt.datetime.strptime(row['acq_date']+' '+hhmm,'%Y-%m-%d %H%M').replace(tzinfo=UTC)
            if at>acquired+dt.timedelta(minutes=5) or at<acquired-dt.timedelta(days=8):raise ValueError('Observation outside recent window')
            if row['confidence'] not in ('low','nominal','high','l','n','h'):raise ValueError('Unknown VIIRS confidence')
            ident=hashlib.sha256(json.dumps([row['satellite'],stamp(at),lon,lat],separators=(',',':')).encode()).hexdigest()[:24]
            if ident in seen:continue
            seen.add(ident)
            features.append(dict(type='Feature',id=ident,geometry=dict(type='Point',coordinates=[lon,lat]),properties=dict(id=ident,at=stamp(at),frp_mw=frp,confidence=row['confidence'],satellite=row['satellite'],scan_km=scan,track_km=track,version=row['version'],qualification='THERMAL_ANOMALY_NOT_CONFIRMED_WILDFIRE',native_resolution_m=375)))
        except (KeyError,TypeError,ValueError):rejected+=1
    if rows and not features:raise ValueError('All FIRMS rows rejected; not an empty valid observation')
    return dict(type='FeatureCollection',features=features,rejected_rows=rejected,source_rows=rows,observation_from=min((f['properties']['at'] for f in features),default=None),observation_until=max((f['properties']['at'] for f in features),default=None))

class ThermalStore:
    def __init__(self,root,fetch=None):
        self.root=Path(root);self.root.mkdir(exist_ok=True);self.lock=threading.Lock();self.busy=None;self.fetch=fetch or self._fetch;self.pending={}
    @staticmethod
    def _fetch(url):
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HAZARDIA research consultation/1','Accept':'text/csv'}),timeout=20) as r:
            if r.geturl()!=url:raise ValueError('Unexpected source redirect')
            raw=r.read(CAP+1)
        if len(raw)>CAP:raise ValueError('FIRMS response exceeds2MiB')
        return raw
    def snapshot(self,region):
        if region not in SOURCES:raise HazardError('INVALID_INPUT','Choose Europe')
        with self.lock:
            path=self.root/(region+'.latest.json');data=json.loads(path.read_text()) if path.exists() else None
            return dict(status='AVAILABLE' if data else 'MISSING',busy=self.busy==region,error=self.pending.get(region),data=data)
    def refresh(self,body):
        if set(body)!={'region'} or not isinstance(body['region'],str) or body['region'] not in SOURCES:raise HazardError('INVALID_INPUT','Known FIRMS region required')
        region=body['region'];now=time.time();ledger=self.root/'attempts.json'
        with self.lock:
            attempts=json.loads(ledger.read_text()) if ledger.exists() else []
            attempts=[a for a in attempts if a['at']>now-86400]
            if self.busy is not None:return dict(status='BUSY')
            if any(a['region']==region and a['at']>now-3600 for a in attempts):return dict(status='CACHED')
            if len(attempts)>=16:raise HazardError('SOURCE_QUOTA','FIRMS16requests/day;32MiB maximum source budget')
            if sum(p.stat().st_size for p in self.root.iterdir())>32*1024**2 or shutil.disk_usage(self.root).free<2*1024**3+12*1024**2:raise HazardError('CACHE_FULL','FIRMS cache32MiB/free reserve2GiB; originals retained')
            attempts.append(dict(at=now,region=region));ledger.write_text(json.dumps(attempts));self.busy=region;self.pending[region]=None
        def work():
            try:
                raw=self.fetch(SOURCES[region])
                if len(raw)>CAP:raise ValueError('FIRMS response exceeds2MiB')
                data=normalize(raw,dt.datetime.now(UTC));digest=hashlib.sha256(raw).hexdigest()
                data.update(region=region,source=SOURCES[region],raw_sha256=digest,acquired_at=stamp(dt.datetime.now(UTC)),attribution='NASA FIRMS / NOAA-20 VIIRS',license='NASA Earth science data: free and open; acknowledge NASA FIRMS',coverage='Regional satellite observations; cloud, overpass and detection gaps; not a complete fire inventory',coupled_to_models=False)
                encoded=json.dumps(data,allow_nan=False).encode();packed=gzip.compress(raw,mtime=0);receipt_bytes=gzip.compress(encoded,mtime=0)
                if len(encoded)>8*1024**2 or sum(p.stat().st_size for p in self.root.iterdir())+len(encoded)+len(receipt_bytes)+len(packed)>32*1024**2:raise ValueError('FIRMS cache admission limit')
                source=self.root/(digest+'.csv.gz')
                if not source.exists():source.write_bytes(packed)
                receipt=self.root/(digest+'.receipt.json.gz')
                if not receipt.exists():receipt.write_bytes(receipt_bytes)
                temp=self.root/(region+'.tmp');temp.write_bytes(encoded);temp.replace(self.root/(region+'.latest.json'))
            except Exception as exc:self.pending[region]=str(exc)
            finally:
                with self.lock:self.busy=None
        threading.Thread(target=work,name='thermal-observations',daemon=True).start();return dict(status='ACCEPTED')
