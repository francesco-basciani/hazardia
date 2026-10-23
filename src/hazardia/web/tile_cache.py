"""On-demand consultation only: bounded cache, rolling traffic and single-flight.

No prefetch, export, scientific ingestion or lifetime-counter reset. Network runs
outside the index lock; four upstream requests may make progress independently.
"""
import collections,concurrent.futures,hashlib,json,re,threading,time,urllib.request,urllib.error
from pathlib import Path
from hazardia.io import HazardError
UA='HAZARDIA-local-research/0.1 (+https://github.com/francesco-basciani/hazardia)'

class ConsultationCache:
    tile_limit=1024**2
    def __init__(self,root,*,disk_limit=32*1024**2,memory_limit=4*1024**2,ttl=7*86400,tile_limit=1024**2,opener=None,clock=time.time):
        self.tile_limit=tile_limit;self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.disk_limit=disk_limit;self.memory_limit=memory_limit;self.ttl=ttl;self.clock=clock;self.opener=opener or urllib.request.urlopen
        self.lock=threading.RLock();self.reservations=threading.Condition(self.lock);self.slots=threading.BoundedSemaphore(4);self.admission=threading.BoundedSemaphore(16);self.pending={};self.memory=collections.OrderedDict();self.memory_bytes=0;self.hits=0;self.requests=0;self.errors=0;self.reserved=0;self.cooldown={}
        self.hour_limit=16*1024**2;self.day_limit=32*1024**2
        self.traffic_path=self.root/'consultation-traffic.json'
        self.traffic=json.loads(self.traffic_path.read_text()) if self.traffic_path.exists() else {'total_bytes':0,'events':[]}
        self.disk={p.name:(p.stat().st_size,p.stat().st_mtime) for p in self.root.glob('*.tile')};self.disk_bytes=sum(x[0] for x in self.disk.values())
    def _save(self,path,value):
        temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value));temp.replace(path)
    def _used(self,seconds):return sum(size for at,size in self.traffic['events'] if at>self.clock()-seconds)
    def _remember(self,key,raw,expires):
        if key in self.memory:self.memory_bytes-=len(self.memory.pop(key)[0])
        self.memory[key]=(raw,expires);self.memory_bytes+=len(raw)
        while self.memory_bytes>self.memory_limit:self.memory_bytes-=len(self.memory.popitem(last=False)[1][0])
    def _ttl(self,headers):
        cache=headers.get('Cache-Control','');m=re.search(r'(?:^|,)\s*max-age=(\d+)',cache)
        return 0 if 'no-store' in cache or 'no-cache' in cache else int(m.group(1)) if m else self.ttl
    def get(self,key,url,signature,content_type,referer='http://127.0.0.1:8080/'):
        if not re.fullmatch(r'[a-z0-9-]+',key):raise HazardError('INVALID_INPUT','Invalid cache key')
        now=self.clock();path=self.root/(key+'.tile');meta=path.with_suffix('.json')
        with self.lock:
            entry=self.memory.get(key)
            if entry and entry[1]>now:self.hits+=1;self.memory.move_to_end(key);return entry[0]
            m=json.loads(meta.read_text()) if meta.exists() else {}
            if path.exists() and m.get('expires',0)>now:
                raw=path.read_bytes()
                if raw.startswith(signature) and hashlib.sha256(raw).hexdigest()==m.get('sha256'):
                    self._remember(key,raw,m['expires']);self.hits+=1;return raw
            if self.cooldown.get(key,0)>now:raise HazardError('SOURCE_BUSY','Map tile retry delayed after provider failure')
            if key in self.pending:future=self.pending[key];owner=False
            else:future=concurrent.futures.Future();self.pending[key]=future;owner=True
        if not owner:return future.result(timeout=22)
        admitted=False;reserved=False
        try:
            admitted=self.admission.acquire(False)
            if not admitted:raise HazardError('QUEUE_FULL','Map consultation busy; retry')
            with self.slots:
                with self.lock:
                    deadline=time.monotonic()+10
                    while self.reserved and ((self._used(3600)+self.reserved+self.tile_limit>self.hour_limit and self._used(3600)+self.tile_limit<=self.hour_limit) or (self.disk_bytes+self.reserved+self.tile_limit>self.disk_limit and self.disk_bytes+self.tile_limit<=self.disk_limit)):
                        remaining=deadline-time.monotonic()
                        if remaining<=0:raise HazardError('SOURCE_BUSY','Map requests pending; retry after completion')
                        self.reservations.wait(remaining)
                    if self._used(3600)+self.reserved+self.tile_limit>self.hour_limit or self._used(86400)+self.reserved+self.tile_limit>self.day_limit:raise HazardError('DOWNLOAD_LIMIT','Rolling map traffic limit; cached tiles remain available, retry after the window')
                    # Retain fresh cached objects; evict only expired entries, never prefetch replacements.
                    for name,info in sorted(list(self.disk.items()),key=lambda x:x[1][1]):
                        if self.disk_bytes+self.reserved+self.tile_limit<=self.disk_limit:break
                        p=self.root/name;mp=p.with_suffix('.json');old=json.loads(mp.read_text()) if mp.exists() else {}
                        if old.get('expires',0)>now or p==path:continue
                        self.disk_bytes-=info[0];self.disk.pop(name,None);p.unlink(missing_ok=True);mp.unlink(missing_ok=True);self.memory.pop(name.removesuffix('.tile'),None)
                    self.memory_bytes=sum(len(v[0]) for v in self.memory.values())
                    if self.disk_bytes+self.reserved+self.tile_limit>self.disk_limit:raise HazardError('CACHE_FULL','Consultation cache full; unexpired tiles retained')
                    self.reserved+=self.tile_limit;reserved=True
                headers={'User-Agent':UA,'Referer':referer,'Accept':content_type}
                if path.exists() and m.get('etag'):headers['If-None-Match']=m['etag']
                if path.exists() and m.get('last_modified'):headers['If-Modified-Since']=m['last_modified']
                downloaded=0
                try:
                    with self.opener(urllib.request.Request(url,headers=headers),timeout=10) as response:
                        raw=response.read(self.tile_limit+1);rh=response.headers
                        if not raw.startswith(signature) or len(raw)>self.tile_limit or rh.get_content_type() not in ([content_type,'application/octet-stream'] if content_type=='application/vnd.quantized-mesh' else [content_type]):raise OSError('Invalid map payload')
                        downloaded=len(raw)
                        if rh.get('Content-Encoding')=='gzip':
                            import gzip
                            raw=gzip.decompress(raw)
                            if len(raw)>self.tile_limit:raise OSError('Expanded tile too large')
                        m={'etag':rh.get('ETag'),'last_modified':rh.get('Last-Modified'),'expires':now+self._ttl(rh),'sha256':hashlib.sha256(raw).hexdigest()}
                except urllib.error.HTTPError as e:
                    if e.code!=304 or not path.exists():raise
                    raw=path.read_bytes()
                    if not raw.startswith(signature) or hashlib.sha256(raw).hexdigest()!=m.get('sha256'):raise OSError('Corrupt revalidated tile')
                    m['expires']=now+self._ttl(e.headers)
                with self.lock:
                    self.requests+=1;self.traffic['total_bytes']+=downloaded;self.traffic['events']=[x for x in self.traffic['events'] if x[0]>now-86400]
                    if downloaded:self.traffic['events'].append([now,downloaded])
                    self._save(self.traffic_path,self.traffic)
                    if m['expires']>now:
                        previous=self.disk.get(path.name,(0,0))[0];tmp=path.with_suffix('.tmp');tmp.write_bytes(raw);tmp.replace(path);self._save(meta,m);self.disk[path.name]=(len(raw),now);self.disk_bytes+=len(raw)-previous;self._remember(key,raw,m['expires'])
                future.set_result(raw);return raw
        except Exception as e:
            with self.lock:self.errors+=1;self.cooldown[key]=now+15
            future.set_exception(e);raise
        finally:
            with self.lock:
                if reserved:self.reserved-=self.tile_limit;self.reservations.notify_all()
                self.pending.pop(key,None)
                if len(self.cooldown)>256:self.cooldown={k:v for k,v in self.cooldown.items() if v>self.clock()}
            if admitted:self.admission.release()
    def remaining(self,key):
        with self.lock:
            p=self.root/(key+'.json');m=json.loads(p.read_text()) if p.exists() else {}
            return max(0,int(m.get('expires',0)-self.clock()))
    def status(self):
        with self.lock:return dict(mode='On-demand consultation; no prefetch/export',tiles=len(self.disk),cache_bytes=self.disk_bytes,cache_limit_bytes=self.disk_limit,memory_bytes=self.memory_bytes,memory_limit_bytes=self.memory_limit,upstream_requests=self.requests,cache_hits=self.hits,errors=self.errors,downloaded_bytes=self.traffic['total_bytes'],last_hour_bytes=self._used(3600),last_day_bytes=self._used(86400),hour_limit_bytes=self.hour_limit,day_limit_bytes=self.day_limit,can_download_tiles=self._used(3600)+self.tile_limit<=self.hour_limit and self._used(86400)+self.tile_limit<=self.day_limit)
