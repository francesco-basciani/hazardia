"""Reusable earthquake snapshots; bounded source updates, never a forecast.
Original snapshots are immutable. Recent revisions replace the same event ID in
new snapshots; older revisions are reconciled by a weekly full-window read.
"""
import copy
import datetime as dt
import hashlib
import gzip
import json
import shutil
import threading
import time
import urllib.parse
from pathlib import Path
from hazardia.io import HazardError

UTC=dt.timezone.utc
CAP=32*1024**2
SOURCES={'ingv':'https://webservices.ingv.it/fdsnws/event/1/query','usgs':'https://earthquake.usgs.gov/fdsnws/event/1/query'}
def stamp(t):return dt.datetime.fromtimestamp(t,UTC).isoformat().replace('+00:00','Z')
def epoch(v):return dt.datetime.fromisoformat(v.replace('Z','+00:00')).timestamp()
def read_snapshot(p):
    if p.exists():return json.loads(p.read_text())
    with gzip.open(str(p)+'.gz','rt') as stream:return json.load(stream)
def covers(a,b):return all(v>=a[i]-.00001 if i<2 else v<=a[i]+.00001 for i,v in enumerate(b))

class QuakeCache:
    def __init__(self,root,fetch,parse,clock=time.time):
        self.root=Path(root);self.fetch=fetch;self.parse=parse;self.clock=clock
        self.lock=threading.RLock();self.active=False;self.active_body=None;self.active_key=None;self.last=0;self.pending={};self.memo={}
    def snapshot(self,key):
        if not isinstance(key,str) or len(key)!=24 or any(c not in '0123456789abcdef' for c in key):raise HazardError('INVALID_INPUT','Acquisition request id required')
        with self.lock:
            if key in self.pending:return copy.deepcopy(self.pending[key])
            p=self.root/(key+'.json')
            if p.exists() or Path(str(p)+'.gz').exists():return read_snapshot(p)
        raise HazardError('NOT_FOUND','Acquisition not available')
    def candidates(self,provider,b,mag):
        found=[]
        for p in self.root.glob('*.json*'):
            if not p.name.endswith(('.json','.json.gz')):continue
            try:
                signature=(p.stat().st_mtime_ns,p.stat().st_size)
                if p.name not in self.memo or self.memo[p.name][0]!=signature:self.memo[p.name]=(signature,read_snapshot(Path(str(p).removesuffix('.gz'))))
                d=self.memo[p.name][1];q=d['quality']
                if d.get('status')=='READY' and q['provider']==provider and q['min_magnitude']<=mag and covers(d['bounds'],b):
                    found.append(d)
            except (ValueError,KeyError,TypeError,OSError):continue
        return sorted(found,key=lambda d:epoch(d['quality']['window_end']),reverse=True)
    def view(self,d,days,now,status,reason=None,next_at=None):
        result=copy.deepcopy(d);q=result['quality'];requested_start=now-days*86400
        result['features']=[f for f in result['features'] if epoch(f['properties']['at'])>=requested_start and epoch(f['properties']['at'])<=now]
        partial=epoch(q['window_start'])>requested_start+3600 or now-epoch(q['window_end'])>3600 or bool(q.get('limit_reached')) or bool(q.get('skipped'))
        q.update(archive_window_start=q['window_start'],window_start=stamp(max(epoch(q['window_start']),requested_start)),requested_days=days,requested_start=stamp(requested_start),cache_status=status,cache_reason=reason,partial_window=partial,
                 next_refresh_at=stamp(next_at if next_at is not None else epoch(d['acquired_at'])+3600),
                 cache_policy='persistent archive; hourly update; 48h revision overlap; weekly full reconciliation')
        return result
    def prepare(self,body,b,provider,days,mag):
        now=self.clock();end=int(now//3600)*3600;start=end-days*86400
        quota=self.root/(dt.datetime.fromtimestamp(now,UTC).date().isoformat()+'.quota')
        with self.lock:
            candidates=self.candidates(provider,b,mag)
            complete=[d for d in candidates if not d['quality'].get('limit_reached') and not d['quality'].get('skipped') and epoch(d['quality']['window_start'])<=start+1]
            base=complete[0] if complete else None
            if base and 0<=now-epoch(base['acquired_at'])<3600:return self.view(base,days,now,'CACHED')
            fallback=base or next(iter(candidates),None)
            n=int(quota.read_text()) if quota.exists() else 0
            if n>=24:
                if fallback:return self.view(fallback,days,now,'STALE','LOCAL_DAILY_QUOTA',now-now%86400+86400)
                raise HazardError('SOURCE_QUOTA','Local daily budget reached; no archive covering this area/magnitude')
            if self.active:
                if fallback:return self.view(fallback,days,now,'STALE','UPDATE_RUNNING',now+60)
                if self.active_body==body:return copy.deepcopy(self.pending[self.active_key])
                raise HazardError('QUEUE_FULL','Earthquake update running; retry this query after completion')
            if now-self.last<5:
                if fallback:return self.view(fallback,days,now,'STALE','RETRY_LATER',now+60)
                raise HazardError('SOURCE_QUOTA','Wait5seconds between source requests')
            if sum(p.stat().st_size for p in self.root.iterdir())>=CAP or shutil.disk_usage(self.root).free<2*1024**3+20*1024**2:
                if fallback:return self.view(fallback,days,now,'STALE','CACHE_ADMISSION_LIMIT',now+3600)
                raise HazardError('CACHE_FULL','Archive limit or2GiB reserve reached')
            area=[6,35,19,48] if provider=='ingv' else b
            minimum=-1 if provider=='ingv' else mag
            # Reuse only a complete spatial/magnitude base. No incremental merge
            # over a truncated response or an uncovered part of the requested area.
            delta=bool(base and covers(base['bounds'],area) and base['quality']['min_magnitude']<=minimum
                       and now-epoch(base['quality'].get('reconciled_at',base['acquired_at']))<7*86400)
            if not delta and base and provider=='ingv' and covers(base['bounds'],area):
                minimum=base['quality']['min_magnitude'];delta=now-epoch(base['quality'].get('reconciled_at',base['acquired_at']))<7*86400
            query_start=max(start,epoch(base['quality']['window_end'])-48*3600) if delta else start
            if delta:minimum=base['quality']['min_magnitude'];area=base['bounds']
            query_time=lambda t:dt.datetime.fromtimestamp(t,UTC).strftime('%Y-%m-%dT%H:%M:%S') if provider=='ingv' else stamp(t)
            query=dict(format='text',starttime=query_time(query_start),endtime=query_time(end),minlatitude=area[1],maxlatitude=area[3],minlongitude=area[0],maxlongitude=area[2],minmagnitude=minimum,limit=1000,orderby='time')
            url=SOURCES[provider]+'?'+urllib.parse.urlencode(query)
            key=hashlib.sha256(json.dumps(['quake-cache/1',provider,area,minimum,days,end,base['request_id'] if delta else None],sort_keys=True).encode()).hexdigest()[:24]
            if key in self.pending:return copy.deepcopy(self.pending[key])
            path=self.root/(key+'.json')
            if path.exists() or Path(str(path)+'.gz').exists():return self.view(read_snapshot(path),days,now,'CACHED')
            quota.write_text(str(n+1));self.active=True;self.active_body=copy.deepcopy(body);self.active_key=key;self.last=now;self.pending[key]=dict(status='LOADING',request_id=key)
        def work():
            try:
                raw=self.fetch(url)
                if len(raw)>8*1024**2:raise ValueError('Source response exceeds8MiB')
                features,q=self.parse(raw)
                if delta and q.get('limit_reached'):raise ValueError('Truncated incremental response: previous archive retained')
                if delta:
                    merged={f['id']:f for f in base['features']};merged.update({f['id']:f for f in features})
                    features=[f for f in merged.values() if start<=epoch(f['properties']['at'])<=end]
                features.sort(key=lambda f:f['properties']['at'],reverse=True)
                q.update(provider=provider,min_magnitude=minimum,window_start=stamp(start),window_end=stamp(end),
                         coverage='Italy regional catalogue' if provider=='ingv' else 'Mapped FDSN catalogue area; detection completeness unknown',
                         license='INGV CC BY4.0' if provider=='ingv' else 'USGS public-domain data; contributor attribution retained',
                         reconciled_at=base['quality'].get('reconciled_at',base['acquired_at']) if delta else stamp(now),
                         update_mode='INCREMENTAL_48H_REVISION_OVERLAP' if delta else 'FULL_WINDOW',
                         base_request_id=base['request_id'] if delta else None,
                         missing=['Detection completeness','Withdrawals and older revisions until full reconciliation','Felt intensity and damage'])
                value=dict(status='READY',request_id=key,type='FeatureCollection',features=features,bounds=area,source=url,acquired_at=stamp(self.clock()),raw_sha256=hashlib.sha256(raw).hexdigest(),stored_source_file=key+'.source.gz',stored_source_encoding='gzip',quality=q,kind='earthquakes',coupled_to_optimizer=False)
                encoded=gzip.compress(json.dumps(value,allow_nan=False).encode(),mtime=0);packed=gzip.compress(raw,mtime=0)
                with self.lock:
                    if sum(p.stat().st_size for p in self.root.iterdir())+len(packed)+len(encoded)>CAP:raise ValueError('32MiB archive admission limit')
                    (self.root/(key+'.source.gz')).write_bytes(packed);Path(str(path)+'.gz').write_bytes(encoded)
                value=self.view(value,days,self.clock(),'CACHED')
            except Exception as error:
                value=self.view(fallback,days,self.clock(),'STALE','UPDATE_FAILED: '+str(error),self.clock()+3600) if fallback else dict(status='ERROR',request_id=key,detail=str(error),kind='earthquakes')
                value['request_id']=key
            with self.lock:
                self.pending[key]=value;self.active=False
                for old in list(self.pending):
                    if len(self.pending)<=8:break
                    if self.pending[old]['status']!='LOADING':del self.pending[old]
        threading.Thread(target=work,daemon=True).start()
        return dict(status='LOADING',request_id=key)
