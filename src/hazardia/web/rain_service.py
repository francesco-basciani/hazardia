"""One bounded asynchronous rainfall evidence worker; shared existing caches only."""
import gzip, hashlib, json, os, re, subprocess, threading, time
from pathlib import Path
from hazardia.io import HazardError, load, timestamp, write_new

class RainService:
    def __init__(self, app):
        self.app=app; self.root=app.state/'rain-assessments'; self.root.mkdir(exist_ok=True)
        self.lock=threading.Lock(); self.active=set();self.geometry_cache=None
    def geometry(self,digest):
        if not re.fullmatch('[a-f0-9]{64}',digest):raise HazardError('CACHE_CORRUPT','Invalid geometry reference')
        if self.geometry_cache and self.geometry_cache[0]==digest:return self.geometry_cache[1]
        with gzip.open(self.root/('geometry-'+digest+'.json.gz'),'rb') as f:raw=f.read(8*1024**2+1)
        if len(raw)>8*1024**2 or hashlib.sha256(raw).hexdigest()!=digest:raise HazardError('CACHE_CORRUPT','Rain geometry checksum differs')
        data=json.loads(raw);self.geometry_cache=(digest,data);return data
    def submit(self, body):
        if set(body)!={'at'} or not isinstance(body['at'],str):
            raise HazardError('INVALID_INPUT','Only a whole UTC forecast hour is accepted')
        t=timestamp(body['at'])
        if t.minute or t.second or t.microsecond: raise HazardError('INVALID_INPUT','Whole UTC forecast hour required')
        at=t.isoformat().replace('+00:00','Z')
        weather=self.app.map_weather.snapshot(); field=weather.get('forecast')
        if not field or weather['status']!='FRESH': raise HazardError('STALE_FORECAST','Previsione pioggia assente o scaduta: valutazione sospesa')
        if at not in {r['at'] for r in field['records']}: raise HazardError('SOURCE_MISSING','Ora non coperta dalla previsione')
        attention=self.app.attention.snapshot(); products=attention.get('sources',{}).get('dpc',{}).get('products',[])
        if not products: raise HazardError('SOURCE_MISSING','Geometrie ufficiali delle zone non disponibili')
        # Geometry vintage is independent of bulletin validity. Never extend a warning.
        from zoneinfo import ZoneInfo
        day=t.astimezone(ZoneInfo('Europe/Rome')).date().isoformat()
        p=next((v for v in products if v['day']==day),max(products,key=lambda p:p['day']))
        name=p['url'].split('/')[-1];zones=self.app.attention.layer(attention['id'],name)
        source=attention['sources']['dpc'];official=dict(status='UNAVAILABLE',reason='Bollettino non disponibile per questa ora')
        selected=next((v for v in products if v['day']==day),None)
        if selected and selected['freshness']=='FRESH' and source.get('issued_at') and timestamp(source['issued_at'])<=t<timestamp(selected['valid_until']):
            geo=self.app.attention.layer(attention['id'],selected['url'].split('/')[-1])
            official=dict(status='AVAILABLE',issued_at=source['issued_at'],valid_until=selected['valid_until'],day=day,
                          source_url=source['source_url'],revision=source.get('revision'),zones={v['properties']['id']:v['properties'] for v in geo['features']})
        geometry_raw=json.dumps(zones,sort_keys=True).encode();geometry_sha=hashlib.sha256(geometry_raw).hexdigest()
        plan_key=hashlib.sha256(json.dumps(['rain-sampling/1',field['lats'],field['lons'],geometry_sha],sort_keys=True).encode()).hexdigest()
        plan_path=self.root/('plan-'+plan_key+'.json');sampling=None
        if plan_path.exists():
            envelope=load(plan_path);raw=json.dumps(envelope['plan'],sort_keys=True).encode()
            if hashlib.sha256(raw).hexdigest()!=envelope['sha256']:raise HazardError('CACHE_CORRUPT','Rain sampling plan checksum differs')
            sampling=envelope['plan']
        # Warning text and municipalities already reside in the shared frozen geometry.
        if official['status']=='AVAILABLE':
            official['zones']={key:{k:v for k,v in value.items() if k in ['level','levels','reasons']} for key,value in official['zones'].items()}
        key='rain-'+hashlib.sha256(json.dumps(['rain/5',field['id'],geometry_sha,at,official],sort_keys=True).encode()).hexdigest()[:24]
        dest=self.root/key
        with self.lock:
            if (dest/'receipt.json').exists(): return dict(id=key,status='SUCCEEDED')
            if key in self.active: return dict(id=key,status='RUNNING')
            if (dest/'error.json').exists():return dict(id=key,status='ERROR',**load(dest/'error.json'))
            if self.active or not self.app.capacity.acquire(False): raise HazardError('QUEUE_FULL','Valutazione pioggia occupata: riprova tra poco')
            if sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file())>56*1024**2:
                self.app.capacity.release(); raise HazardError('CACHE_FULL','Archivio valutazioni pioggia pieno; nessuna nuova valutazione')
            self.active.add(key)
        try:
            geometry_path=self.root/('geometry-'+geometry_sha+'.json.gz')
            if not geometry_path.exists():
                tmp=Path(str(geometry_path)+'.tmp');tmp.write_bytes(gzip.compress(geometry_raw,compresslevel=1,mtime=0));tmp.replace(geometry_path)
            self.geometry(geometry_sha)
            dest.mkdir(exist_ok=True)
            if not (dest/'request.json').exists():
                write_new(dest/'request.json',dict(field=field,geometry_path=str(geometry_path),at=at,attention_snapshot=attention['id'],geometry_sha256=geometry_sha,geometry_day=p['day'],assessment_id=key,official=official,sampling_plan=sampling))
        except Exception:
            self.app.capacity.release()
            with self.lock:self.active.discard(key)
            raise
        def work():
            try:
                cfg=load(self.app.root/'runtime-v2.json'); begin=time.monotonic()
                with (dest/'worker.log').open('ab') as log:
                    subprocess.run([cfg['geo_python'],'-m','hazardia.rain_assessment',str(dest/'request.json'),str(dest/'result.json')],check=True,timeout=40,
                                   env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),PROJ_LIB='/usr/share/proj'),stdout=log,stderr=subprocess.STDOUT)
                computed=load(dest/'result.json')['sampling_plan']
                if not plan_path.exists():write_new(plan_path,dict(plan=computed,sha256=hashlib.sha256(json.dumps(computed,sort_keys=True).encode()).hexdigest()))
                hashes={}
                for name in ['request.json','result.json']:
                    raw=(dest/name).read_bytes();hashes[name]=hashlib.sha256(raw).hexdigest()
                    (dest/(name+'.gz')).write_bytes(gzip.compress(raw,compresslevel=1,mtime=0))
                    if gzip.decompress((dest/(name+'.gz')).read_bytes())!=raw:raise ValueError('Archive differs')
                    (dest/name).unlink()
                write_new(dest/'receipt.json',dict(raw_sha256=hashes))
                (dest/'elapsed.json').write_text(json.dumps(dict(seconds=time.monotonic()-begin)))
            except Exception as e:
                (dest/'error.json').write_text(json.dumps(dict(code='RAIN_ASSESSMENT_FAILED',detail='Valutazione pioggia non disponibile: '+type(e).__name__)))
            finally:
                self.app.capacity.release()
                with self.lock:self.active.discard(key)
        self.app.pool.submit(work)
        return dict(id=key,status='QUEUED')
    def read(self,key):
        if not re.fullmatch('rain-[a-f0-9]{24}',key): raise HazardError('INVALID_INPUT','Invalid rain evidence ID')
        dest=self.root/key
        if (dest/'receipt.json').exists():
            with gzip.open(dest/'result.json.gz','rb') as f:raw=f.read(8*1024**2+1)
            if len(raw)>8*1024**2 or hashlib.sha256(raw).hexdigest()!=load(dest/'receipt.json')['raw_sha256']['result.json']:
                raise HazardError('CACHE_CORRUPT','Rain evidence checksum differs')
            result=json.loads(raw);result.pop('sampling_plan',None)
            if any(f['geometry'] is None for f in result['features']):
                geometry={f['properties']['id']:f['geometry'] for f in self.geometry(result['geometry_sha256'])['features']}
                for f in result['features']:f['geometry']=geometry[f['properties']['id']]
            age=time.time()-timestamp(result['forecast_available_at']).timestamp()
            return dict(id=key,status='SUCCEEDED',freshness='FRESH' if 0<=age<10800 else 'STALE',data=result)
        with self.lock:
            if key in self.active:return dict(id=key,status='RUNNING')
        if (dest/'error.json').exists():return dict(id=key,status='ERROR',**load(dest/'error.json'))
        raise HazardError('NOT_FOUND','Valutazione non disponibile')
