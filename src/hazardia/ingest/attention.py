"""Shared bounded VM attention cache. Acquisition is isolated from HTTP threads."""
import datetime as dt
import hashlib
import gzip
import json
import os
import re
import subprocess
import threading
import time
import uuid
from zoneinfo import ZoneInfo
from pathlib import Path
from hazardia.io import HazardError,load

class AttentionStore:
    def __init__(self,root,runtime,*,clock=time.time):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.runtime=Path(runtime);self.clock=clock;self.busy=threading.Lock();self.lock=threading.Lock();self.cached=None
        self.profile=Path(__file__).resolve().parents[3]/'profiles/monitoring/italy.json'
    def raw(self,path):
        try:return path.read_bytes()
        except FileNotFoundError:
            with gzip.open(str(path)+'.gz','rb') as f:data=f.read(32*1024**2+1)
            if len(data)>32*1024**2:raise HazardError('CACHE_CORRUPT','Attention expanded file too large')
            return data
    def compact(self):
        # Lossless storage representation; source names and raw SHA manifests unchanged.
        for path in self.root.glob('snapshot-*/*'):
            if path.suffix not in ['.json','.geojson']:continue
            raw=path.read_bytes();packed=gzip.compress(raw,mtime=0);target=Path(str(path)+'.gz')
            if len(packed)>=len(raw):continue
            if target.exists():
                if gzip.decompress(target.read_bytes())!=raw:raise HazardError('CACHE_CORRUPT','Conflicting attention archive')
            else:
                temp=Path(str(target)+'.tmp');temp.write_bytes(packed);temp.replace(target)
            if gzip.decompress(target.read_bytes())!=raw:raise HazardError('CACHE_CORRUPT','Attention compaction differs')
            path.unlink()
    def state(self):
        path=self.root/'state.json'
        return load(path) if path.exists() else {}
    def write_state(self,value):
        temp=self.root/'state.tmp';temp.write_text(json.dumps(value));temp.replace(self.root/'state.json')
    def bundle(self):
        state=self.state();ident=state.get('snapshot')
        if not ident:return None,None
        if not re.fullmatch('snapshot-[a-f0-9]{32}',ident):raise HazardError('CACHE_CORRUPT','Invalid attention snapshot')
        path=self.root/ident/'result.json';raw=self.raw(path);digest=hashlib.sha256(raw).hexdigest()
        if digest!=state.get('sha256'):raise HazardError('CACHE_CORRUPT','Attention manifest checksum differs')
        if not self.cached or self.cached[0]!=digest:self.cached=(digest,json.loads(raw))
        return ident,self.cached[1]
    def snapshot(self):
        with self.lock:
            state=self.state();ident,data=self.bundle();now=self.clock()
            if not data:return dict(status='UNAVAILABLE',sources={},fetching=self.busy.locked(),error=state.get('error'),missing=['No real-source snapshot yet'],refresh_s=10800,retry_after_s=max(0,10800-(now-state.get('attempt_at',0))))
            reference=data.get('reference_epoch');effective=max(now,(reference or now)+max(0,now-data['local_epoch']))
            age=effective-(reference or data['local_epoch']);fresh=reference is not None and now>=data['local_epoch']-300 and 0<=age<10800
            out=json.loads(json.dumps(data));out.pop('files',None);out.pop('receipts',None)
            for key,source in out['sources'].items():
                for p in source.get('products',[]):
                    if 'valid_from' not in p:
                        zone=dt.timezone.utc if key!='dpc' else ZoneInfo('Europe/Rome')
                        p['valid_from']=dt.datetime.fromisoformat(p['day']).replace(tzinfo=zone).astimezone(dt.timezone.utc).isoformat().replace('+00:00','Z')
                    p['url']='/api/monitoring/layers/'+ident+'/'+p.pop('file')
                    p['freshness']='FRESH' if fresh and effective<dt.datetime.fromisoformat(p['valid_until'].replace('Z','+00:00')).timestamp() else 'STALE'
                source['freshness']='FRESH' if fresh else 'STALE'
            has_data=any(source.get('products') for source in out['sources'].values())
            out['capabilities']=dict(territorial_awareness='DEGRADED' if has_data else 'UNAVAILABLE',local_impact='UNAVAILABLE',sources={key:('UNAVAILABLE' if not source.get('products') else 'DEGRADED' if not fresh or source['status']!='AVAILABLE' else 'NOMINAL') for key,source in out['sources'].items()})
            out.update(retry_after_s=max(0,10800-(now-state.get('attempt_at',0))),id=ident,status='UNAVAILABLE' if not has_data else 'PARTIAL' if fresh else 'STALE',age_s=age,fetching=self.busy.locked(),error=state.get('error'),refresh_s=10800,effective_at=dt.datetime.fromtimestamp(effective,dt.timezone.utc).isoformat().replace('+00:00','Z'),clock_status='CLOCK_DISCONTINUITY' if now<data['local_epoch']-300 else 'HTTPS_REFERENCE_VM_SKEW' if abs(data.get('clock_offset_s') or 0)>300 else 'CONSISTENT' if reference else 'UNVERIFIED')
            return out
    def layer(self,ident,name):
        if not re.fullmatch('snapshot-[a-f0-9]{32}',ident) or not re.fullmatch('(dpc|effis)-\d{4}-\d{2}-\d{2}\.geojson',name):raise HazardError('INVALID_INPUT','Invalid attention layer')
        # Only files named in a validated immutable manifest may be served.
        with self.lock:
            current,data=self.bundle()
            if current!=ident:raise HazardError('STALE_CONTEXT','Attention snapshot changed; reload the layer list')
            path=self.root/ident/name
            if not data or name not in data['files']:raise HazardError('NOT_FOUND','Attention layer unavailable')
            raw=self.raw(path)
            if hashlib.sha256(raw).hexdigest()!=data['files'][name]:raise HazardError('CACHE_CORRUPT','Attention layer checksum differs')
        return json.loads(raw)
    def refresh(self):
        if not self.busy.acquire(False):return dict(status='ACCEPTED',fetching=True)
        def acquire():
            try:
                now=self.clock()
                if sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file())>240*1024**2:
                    self.compact()
                with self.lock:
                    state=self.state();last=state.get('attempt_at')
                    if last is not None and -300<now-last<10800:return
                    if sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file())>256*1024**2:raise HazardError('CACHE_FULL','Attention archive cap256MiB reached')
                    self.write_state(dict(state,attempt_at=now,error=None))
                folder=self.root/('snapshot-'+uuid.uuid4().hex);folder.mkdir()
                config=load(self.runtime/'runtime-v2.json')
                completed=subprocess.run([config['geo_python'],'-m','hazardia.ingest.attention_worker',str(folder),str(self.profile)],check=True,env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2])),timeout=180,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
                (folder/'worker-stderr.txt').write_bytes(completed.stderr[:16384])
                raw=(folder/'result.json').read_bytes()
                with self.lock:self.write_state(dict(attempt_at=now,snapshot=folder.name,sha256=hashlib.sha256(raw).hexdigest(),error=None))
            except Exception as e:
                if isinstance(e,subprocess.CalledProcessError):
                    (folder/'worker-stderr.txt').write_bytes((e.stderr or b'')[:16384])
                with self.lock:self.write_state(dict(self.state(),error=(e.code+': '+str(e)) if isinstance(e,HazardError) else type(e).__name__+': attention acquisition failed; cached dated snapshot retained'))
            finally:self.busy.release()
        threading.Thread(target=acquire,daemon=True).start()
        return dict(status='ACCEPTED',scope='Shared3h VM cache; free EFFIS/DPC; no simulator job')
