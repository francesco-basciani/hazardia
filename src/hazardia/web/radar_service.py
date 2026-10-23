"""Bounded separate observation worker; never touches simulator forcing."""
import datetime as dt,json,os,re,subprocess,threading,time
from pathlib import Path
from hazardia.io import HazardError,load
class RadarService:
    def __init__(self,app):self.app=app;self.root=app.state/'radar-dpc';self.root.mkdir(exist_ok=True);self.lock=threading.Lock();self.active=None;self.error=None;self.latest_request=None
    @staticmethod
    def time_key(at):
        try:value=dt.datetime.fromisoformat(at.replace('Z','+00:00')).timestamp()
        except (ValueError,AttributeError):raise HazardError('INVALID_INPUT','Explicit UTC radar observation required')
        if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z',at):raise HazardError('INVALID_INPUT','UTC radar observation required')
        return int(value//300*300)
    def snapshot(self,at):
        key=self.time_key(at);folder=self.root/str(key);p=folder/'result.json';now=time.time()
        if p.exists():
            data=load(p);return dict(status='AVAILABLE',data=dict(data,image=f'/api/monitoring/radar/{key}/rain.png',missing_image=f'/api/monitoring/radar/{key}/missing.png'),busy=self.active==key,selected_at=at)
        return dict(status='OUTSIDE_VALIDITY' if key>now or key<now-86400 else 'LOADING' if self.active==key else 'UNAVAILABLE',data=None,busy=self.active is not None,selected_at=at,error=self.error if self.latest_request==key else None,detail='Solo osservazioni radar nelle ultime24h. Nessuna sostituzione con un altro orario.')
    def refresh(self,at):
        key=self.time_key(at);current=self.snapshot(at)
        if current['status'] in ['AVAILABLE','OUTSIDE_VALIDITY'] or self.active is not None:return current
        with self.lock:
            if self.active is not None:return self.snapshot(at)
            usage=self.root/'attempts.json';entries=load(usage) if usage.exists() else [];now=time.time();entries=[x for x in entries if x>now-86400]
            if len(entries)>=12 or entries and now-entries[-1]<60:return dict(current,error='Consultazione radar limitata: riprova più tardi; cache disponibile agli orari già acquisiti.')
            if sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file())>32*1024**2:return dict(current,error='Cache radar32MiB piena; dati precedenti conservati.')
            entries.append(now);usage.write_text(json.dumps(entries));self.active=key;self.latest_request=key;self.error=None
            threading.Thread(target=self.run,args=(key,),daemon=True).start();return self.snapshot(at)
    def run(self,key):
        folder=self.root/str(key);folder.mkdir(exist_ok=True)
        try:
            cfg=load(self.app.root/'runtime-v2.json');env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),PROJ_LIB='/usr/share/proj')
            with (folder/'worker.log').open('ab') as log:subprocess.run([cfg['geo_python'],'-m','hazardia.web.radar_worker','--out',str(folder),'--at',str(key*1000)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60,check=True)
        except Exception as e:self.error='Acquisizione radar non riuscita: '+type(e).__name__
        finally:self.active=None
    def image(self,key,name):
        if name not in ['rain.png','missing.png'] or not str(key).isdigit():raise HazardError('INVALID_INPUT','Invalid radar image')
        p=self.root/str(key)/name
        if not p.exists():raise HazardError('NOT_FOUND','Radar image unavailable')
        return p.read_bytes()
