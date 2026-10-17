"""First-party bounded local HTTP service, models isolated via existing JobStore."""
import concurrent.futures,copy,datetime as dt,hashlib,json,mimetypes,os,re,sqlite3,subprocess,sys,threading,time,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from hazardia.io import load,loads,write_new,utcnow,HazardError,sha256
from hazardia.jobs import JobStore
from hazardia.web.maps import Orthophotos,RegionalSatellite
from hazardia.web.notebook import Notebook
from hazardia.decision.research_fixture import problem
from hazardia.decision.supervisor import bounded_decide
from hazardia.adaptation.control import ResearchControl
from hazardia.decision.rolling import advance
from hazardia.decision.resource_overrides import apply as apply_resource_overrides
from hazardia.ingest.forecast import ForecastStore
from hazardia.ingest.wind import WindStore
from hazardia.ingest.map_weather import MapWeatherStore,grid as map_weather_grid
from hazardia.adapters.forecast import stage as stage_forecast
from hazardia.firelab import stage as stage_firelab,validate as validate_firelab

class App:
    def __init__(self,root):
        self.root=Path(root).resolve();self.store=JobStore(self.root/'jobs',(self.root/'runtime-fire-studio.json') if (self.root/'runtime-fire-studio.json').exists() else (self.root/'runtime-v2.json'));self.state=self.root/'web-state';self.state.mkdir(exist_ok=True);self.results={};self.lock=threading.Lock();self.pool=concurrent.futures.ThreadPoolExecutor(max_workers=2);self.capacity=threading.BoundedSemaphore(4);self.metrics=[];self.stop=threading.Event();self.replay=ResearchControl(self.state/"research-replay");self.orthophotos=Orthophotos(self.state);self.regional_satellite=RegionalSatellite(self.state);self.notebook=Notebook(self.state/"notebook");self.weather=ForecastStore(self.state/"weather");self.weather_lock=threading.Lock();self.wind=WindStore(self.state/"regional-wind");self.wind_lock=threading.Lock();self.map_weather=MapWeatherStore(self.state/"map-weather");self.map_weather_lock=threading.Lock()
        threading.Thread(target=self.models,daemon=True).start()
    def catalog(self):return load(self.root/'web-assets/catalog.json')
    def models(self):
        while not self.stop.is_set():
            try:
                res=self.store.work_once()
                if res and res['state']=='SUCCEEDED':
                    if (self.root/'jobs'/res['id']/'fire-series.json').exists():continue
                    cfg=load(self.root/'runtime-v2.json');env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),PROJ_LIB='/usr/share/proj');subprocess.run([cfg['geo_python'],str(Path(__file__).resolve().parents[3]/'scripts/build_dashboard_data.py'),'--runtime',str(self.root)],env=env,timeout=60,check=True)
                if res:continue
            except Exception as e:
                write_new(self.state/('model-error-'+uuid.uuid4().hex+'.json'),dict(at=utcnow(),type=type(e).__name__,detail=str(e)))
            self.stop.wait(.5)
    def jobs(self):
        with self.store.connect() as db:rows=db.execute('SELECT * FROM jobs ORDER BY rowid DESC LIMIT 25').fetchall()
        return [dict(dict(r),usable_product=r['state']=='SUCCEEDED') for r in rows]
    def submit_firelab(self,body):
        validate_firelab(body)
        if body['weather_source']=='FORECAST' and 'source_stale' in self.replay.state['faults']:raise HazardError('STALE_FORECAST','Controlled source loss: new forecast blocked; historical replay remains available')
        forecast=self.weather.fresh(body.get('forecast_id')) if body['weather_source']=='FORECAST' else None
        # Reserve both places before staging; no partial pair accepted on a full queue.
        with self.lock:
            with self.store.connect() as db:
                if db.execute("SELECT count(*) FROM jobs WHERE state='QUEUED'").fetchone()[0]>self.store.capacity-2:raise HazardError('QUEUE_FULL','Two queue places required for a matched native comparison')
            folder,requests=stage_firelab(self.root,body,forecast);jobs={}
            try:
                for case,req in requests.items():jobs[case]=self.store.submit(req,folder)
            except Exception:
                for job in jobs.values():self.store.cancel(job)
                raise
        write_new(folder/'jobs.json',jobs);return dict(jobs=jobs,qualification='UNQUALIFIED_RESEARCH',configuration_id=folder.name)
    def submit_model(self,body):
        allowed={'hazard','seed','minutes','row','col','weather_source','forecast_id','start_at'}
        if set(body)-allowed:raise HazardError('INVALID_INPUT','Unknown simulation fields')
        hazard=body.get('hazard');
        if hazard not in ['FIRE','FLOOD']:raise HazardError('INVALID_INPUT','Select FIRE/FLOOD')
        if body.get('weather_source')=='FORECAST':
            forecast=self.weather.fresh(body.get('forecast_id'));req,folder=stage_forecast(self.root,forecast,body,self.weather.root);return self.store.get(self.store.submit(req,folder))
        if body.get('weather_source') not in [None,'HISTORICAL']:raise HazardError('INVALID_INPUT','Unsupported weather source')
        old=self.root/'runs/m1-abruzzo-20261015T161041Z';req=load(old/(hazard.lower()+'-request.json'));req['id']='ui-'+uuid.uuid4().hex;req['snapshot_at']=utcnow()
        if hazard=='FIRE':
            seed=body.get('seed',1729);minutes=body.get('minutes',30);row=body.get('row',32);col=body.get('col',32)
            if not all(type(v) is int for v in [seed,minutes,row,col]) or not 0<=seed<2**31 or minutes not in [10,30,60] or not 0<=row<64 or not 0<=col<64:raise HazardError('INVALID_INPUT','Invalid seed/duration/ignition')
            req['options'].update(seed=seed,duration_s=minutes*60,ignition=[row,col]);req['valid_until']=(dt.datetime.fromisoformat(req['valid_from'].replace('Z','+00:00'))+dt.timedelta(minutes=minutes)).isoformat().replace('+00:00','Z')
        else:req['valid_from']='2024-07-13T13:00:00Z';req['valid_until']='2024-07-13T19:00:00Z'
        return self.store.get(self.store.submit(req,old))
    def refresh_weather(self):
        if self.weather_lock.acquire(False):
            def fetch():
                try:self.weather.refresh()
                except HazardError as e:
                    with self.weather.connect() as db:db.execute('UPDATE state SET error=? WHERE id=1',(e.code+': '+str(e),))
                finally:self.weather_lock.release()
            threading.Thread(target=fetch,daemon=True).start()
        return dict(status='ACCEPTED',scope='Shared bounded VM cache; existing forecast remains readable')
    def refresh_wind(self):
        if self.wind_lock.acquire(False):
            def fetch():
                try:self.wind.refresh()
                except HazardError as e:
                    with self.wind.connect() as db:db.execute('UPDATE state SET error=? WHERE id=1',(e.code+': '+str(e),))
                finally:self.wind_lock.release()
            threading.Thread(target=fetch,daemon=True).start()
        return dict(status='ACCEPTED',scope='Fixed regional grid; shared three-hour VM cache')
    def refresh_map_weather(self,bounds):
        map_weather_grid(bounds)
        if self.map_weather_lock.acquire(False):
            def fetch():
                try:self.map_weather.acquire(bounds)
                finally:self.map_weather_lock.release()
            threading.Thread(target=fetch,daemon=True).start()
        return dict(status='ACCEPTED',scope='Bounded viewport display only;81nodes; shared VM cache')
    def submit_decision(self,body):
        if set(body)-{'hazard','resources','robust','road_open','transfer','disabled','scenario_ids','rolling_from','preparedness','resource_overrides'}:raise HazardError('INVALID_INPUT','Unknown decision fields')
        hazard=body.get('hazard','FIRE');count=body.get('resources',3);risk=body.get('robust',.5)
        if hazard not in ['FIRE','FLOOD','JOINT'] or type(count) is not int or not 1<=count<=8 or not isinstance(risk,(int,float)) or isinstance(risk,bool) or not 0<=risk<=1:raise HazardError('INVALID_INPUT','Invalid decision controls')
        for key in ['road_open','transfer']:
            if key in body and type(body[key]) is not bool:raise HazardError('INVALID_INPUT','Explicit boolean controls required')
        if not self.capacity.acquire(False):raise HazardError('QUEUE_FULL','Decision queue full')
        accepted=time.monotonic();ident='decision-'+uuid.uuid4().hex
        try:
            scenarios=self.catalog()['scenarios'];refs={};totals={}
            for h in ['FIRE','FLOOD']:
                candidate=next((s for s in scenarios if s['hazard']==h and (h not in body.get('scenario_ids',{}) or s['id']==body['scenario_ids'][h])),None)
                if candidate:
                    refs[h]=candidate['reference'];totals[h]=sum(v['people'] for v in candidate['exposure_points'])
            if hazard!='JOINT' and hazard not in refs or hazard=='JOINT' and len(refs)!=2:raise HazardError('DEPENDENCY_UNAVAILABLE','No genuine spatial product for requested hazard')
            p=problem(refs,hazard,count,robust=risk,road_open=body.get('road_open',True),transfer=body.get('transfer',True),disabled=body.get('disabled'));p['id']=ident
            for event in p['events']:
                total=totals[event['hazard']];event['exposure']={'nominal':total,'stress':total*1.5}
            if body.get('preparedness') is not None:
                if body['preparedness'] not in ['PREPOSITIONED','DELAYED']:raise HazardError('INVALID_INPUT','Unknown preparedness fixture')
                arrival=120 if body['preparedness']=='PREPOSITIONED' else 480
                for option in p['options']:
                    option['arrival_s']=arrival;option['benefit']={w:v*(1-arrival/600) for w,v in option['benefit'].items()}
            if body.get('resource_overrides') is not None:
                if body.get('rolling_from') or body.get('preparedness'):raise HazardError('INVALID_INPUT','Custom unit arrivals cannot be combined with rolling or preset arrival profiles')
                apply_resource_overrides(p,body['resource_overrides'])
            progress=None
            if body.get('rolling_from'):
                previous=self.decision(body['rolling_from']);old=load(self.state/body['rolling_from']/'problem.json');p,progress=advance(old,previous,1);p['id']=ident
            with self.lock:
                p=self.replay.apply(p);health=self.replay.snapshot();self.results[ident]=dict(id=ident,status='QUEUED')
            def work():
                try:
                    with self.lock:self.results[ident]=dict(id=ident,status='RUNNING')
                    r=bounded_decide(p,self.state/ident,str(self.root/'decision-env/bin/python'),accepted_monotonic=accepted)
                    r.update(replay_health_revision=health['revision'],rolling_progress=progress,preparedness=body.get('preparedness'))
                    write_new(self.state/ident/'context.json',dict(health=health,rolling_progress=progress,preparedness=body.get('preparedness')))
                except Exception as e:r=dict(id=ident,status='ERROR',detail=str(e),operationally_approvable=False)
                finally:self.capacity.release()
                with self.lock:
                    self.results[ident]=r
                    # Bounded in-memory status cache; historical results remain on disk.
                    while len(self.results)>100:self.results.pop(next(iter(self.results)))
            self.pool.submit(work);return dict(id=ident,status='QUEUED')
        except Exception:self.capacity.release();raise
    def decision(self,ident):
        if not re.fullmatch('decision-[a-f0-9]{32}',ident):raise HazardError('INVALID_INPUT','Invalid decision ID')
        with self.lock:
            if ident in self.results:return self.current_result(self.results[ident])
        path=self.state/ident/'response.json'
        if path.exists():
            r=load(path);context=self.state/ident/'context.json'
            if context.exists():r['replay_health_revision']=load(context)['health']['revision']
            return self.current_result(r)
        raise HazardError('NOT_FOUND','Decision not found')

    def current_result(self,r):
        if r.get('status')=='VALIDATED_FOR_SIMULATION' and r.get('replay_health_revision')!=self.replay.state['revision']:
            return dict(r,status='STALE_CONTEXT',selected=[],detail='Research availability/forecast changed since acceptance; replan before review',operationally_approvable=False)
        return r

class Handler(BaseHTTPRequestHandler):
    server_version='HAZARDIA-Research/0.1'
    def log_message(self,*args):pass
    def send(self,status,value,content_type='application/json',etag=None):
        raw=json.dumps(value,allow_nan=False).encode() if content_type=='application/json' and not isinstance(value,bytes) else value
        self.send_response(status);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-cache' if content_type=='application/json' else ('no-store' if self.path.startswith('/api/maps/ortho/') else 'no-cache' if not self.path.startswith('/assets/') else 'public, max-age=3600'));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data: blob:; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; frame-ancestors "+("'self'" if urlsplit(self.path).path=='/fire-studio.html' else "'none'"))
        if etag:self.send_header('ETag',etag)
        self.end_headers()
        if self.command!='HEAD':self.wfile.write(raw)
    def check_host(self):
        expected={'localhost:'+str(self.server.server_port),'127.0.0.1:'+str(self.server.server_port)}
        if self.headers.get('Host') not in expected:raise HazardError('FORBIDDEN','Loopback Host required')
    def do_GET(self):self.route(False)
    def do_HEAD(self):self.route(False)
    def do_POST(self):self.route(True)
    def route(self,post):
        tic=time.monotonic();path=urlsplit(self.path).path;app=self.server.app
        try:
            self.check_host()
            if post:
                if self.headers.get('X-Hazardia-Research')!='1' or self.headers.get('Origin') not in [None,'http://'+self.headers.get('Host')]:raise HazardError('FORBIDDEN','Same-origin research request required')
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=65536:raise HazardError('PAYLOAD_LIMIT','Body must be1..65536bytes')
                body=loads(self.rfile.read(size).decode())
                if not isinstance(body,dict):raise HazardError('INVALID_INPUT','JSON object required')
                if path=='/api/notebook':
                    with app.lock:result=app.notebook.save(body)
                    return self.send(200,result)
                if path=='/api/research':
                    with app.lock:result=app.replay.action(body)
                    return self.send(200,result)
                if path=='/api/weather/map/refresh':
                    if set(body)!={'bounds'}:raise HazardError('INVALID_INPUT','Only viewport bounds allowed')
                    return self.send(202,app.refresh_map_weather(body['bounds']))
                if path=='/api/weather/wind/refresh':
                    if body:raise HazardError('INVALID_INPUT','Fixed regional wind grid; arbitrary queries not allowed')
                    return self.send(202,app.refresh_wind())
                if path=='/api/weather/refresh':
                    if body:raise HazardError('INVALID_INPUT','Fixed research forecast point; no arbitrary provider queries')
                    return self.send(202,app.refresh_weather())
                if path=='/api/jobs':return self.send(202,app.submit_model(body))
                if path=='/api/firelab':return self.send(202,app.submit_firelab(body))
                if path=='/api/decisions':return self.send(202,app.submit_decision(body))
                match=re.fullmatch('/api/jobs/(job-[a-f0-9]{32})/(cancel|retry)',path)
                if match:
                    job,action=match.groups();result=dict(cancel_accepted=app.store.cancel(job)) if action=='cancel' else dict(job_id=app.store.retry(job));return self.send(200,result)
                if path=='/api/reviews':
                    result=app.decision(body.get('id',''));choice=body.get('choice')
                    if choice not in ['ACKNOWLEDGE_RESEARCH','REJECT'] or result.get('status')!='VALIDATED_FOR_SIMULATION':raise HazardError('INVALID_INPUT','Review only a verified research proposal')
                    record=dict(id='review-'+uuid.uuid4().hex,decision_id=result['id'],choice=choice,at=utcnow(),operational_authority=False,meaning='Modeled research review only; no dispatch');write_new(app.state/(record['id']+'.json'),record);return self.send(201,record)
                raise HazardError('NOT_FOUND','Unknown endpoint')
            if path=='/api/notebook':
                with app.lock:result=app.notebook.read()
                return self.send(200,result)
            if path=='/api/research':
                with app.lock:result=app.replay.snapshot()
                return self.send(200,result)
            if path=='/api/maps/regional/status':return self.send(200,app.regional_satellite.status())
            regional=re.fullmatch(r'/api/maps/regional/(\d{1,2})/(\d{1,6})/(\d{1,6})',path)
            if regional:return self.send(200,app.regional_satellite.tile(*map(int,regional.groups())),'image/jpeg')
            if path=='/api/maps/status':return self.send(200,app.orthophotos.status())
            tile=re.fullmatch(r'/api/maps/ortho/(\d{1,2})/(\d{1,6})/(\d{1,6})',path)
            if tile:return self.send(200,app.orthophotos.tile(*map(int,tile.groups())),'image/jpeg')
            if path=='/api/weather/map':return self.send(200,app.map_weather.snapshot())
            if path=='/api/weather/wind':return self.send(200,app.wind.snapshot())
            if path=='/api/weather':return self.send(200,app.weather.snapshot())
            if path=='/api/catalog':return self.send(200,app.catalog())
            if path=='/api/jobs':return self.send(200,app.jobs())
            studio=re.fullmatch('/api/firelab/(job-[a-f0-9]{32})(?:/(frame-[0-9]{3}\\.png))?',path)
            if studio:
                job,frame=studio.groups();state=app.store.get(job)
                if state['state']!='SUCCEEDED':return self.send(200,state)
                folder=app.root/'jobs'/job
                if frame:
                    series=load(folder/'fire-series.json');entry=next((f for f in series['frames'] if f['url'].endswith('/'+frame)),None)
                    if entry is None or sha256(folder/'products'/frame)!=entry['png_sha256']:raise HazardError('CHECKSUM','Frame not verified')
                    return self.send(200,(folder/'products'/frame).read_bytes(),'image/png')
                return self.send(200,dict(state,series=load(folder/'fire-series.json')))
            match=re.fullmatch('/api/decisions/(decision-[a-f0-9]{32})/problem',path)
            if match:
                app.decision(match.group(1));return self.send(200,load(app.state/match.group(1)/'problem.json'))
            if path.startswith('/api/decisions/'):return self.send(200,app.decision(path.split('/')[-1]))
            if path=='/api/health':return self.send(200,dict(status='RUNNING',runtime='one Linux VM',research_only=True,metrics=app.metrics[-30:]))
            if path.startswith('/assets/'):base=app.root/'web-assets';relative=path[len('/assets/'):]
            else:base=Path(__file__).with_name('static');relative='index.html' if path=='/' else path.lstrip('/')
            target=(base/relative).resolve()
            if not target.is_relative_to(base.resolve()) or not target.is_file():raise HazardError('NOT_FOUND','Asset not found')
            data=target.read_bytes();return self.send(200,data,mimetypes.guess_type(target.name)[0] or 'application/octet-stream',etag='"'+hashlib.sha256(data).hexdigest()+'"')
        except (HazardError,ValueError,KeyError,TypeError) as e:self.send(403 if isinstance(e,HazardError) and e.code=='FORBIDDEN' else 400,dict(status='ERROR',code=e.code if isinstance(e,HazardError) else 'INVALID_INPUT',detail=str(e)))
        except (OSError,sqlite3.Error) as e:self.send(503,dict(status='ERROR',code='DEPENDENCY_UNAVAILABLE',detail=type(e).__name__))
        finally:
            with app.lock:
                app.metrics.append(dict(path=path.split('/')[1:3],elapsed_ms=(time.monotonic()-tic)*1000,at=utcnow()));app.metrics[:]=app.metrics[-500:]

def serve(root,port=8080):
    app=App(root);server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.app=app;server.daemon_threads=True
    print('HAZARDIA local research dashboard http://127.0.0.1:'+str(port),flush=True)
    try:server.serve_forever()
    finally:app.stop.set();server.server_close();app.pool.shutdown(wait=False,cancel_futures=True)
