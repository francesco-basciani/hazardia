"""Bounded persistent FIFO and isolated process supervisor for M1 simulation jobs."""
import contextlib
import json
import os
import platform
import resource
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path
from hazardia.io import HazardError,load,loads,sha256,utcnow,write_new,verify_asset
from hazardia.contracts import validate,validate_request,validate_product

TERMINAL={'SUCCEEDED','ERROR','TIMEOUT','CANCELLED'}

class JobStore:
    def __init__(self, root, config, queue_capacity=4):
        self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
        self.config=Path(config).resolve()
        self.capacity=queue_capacity
        self.db=self.root/'jobs.sqlite'
        with self.connect() as db:
            db.executescript('''PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,state TEXT NOT NULL,
            created TEXT NOT NULL,started TEXT,ended TEXT,parent TEXT,cancel INTEGER NOT NULL DEFAULT0,
            runner_pid INTEGER,worker_pid INTEGER,error_code TEXT);
            CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,at TEXT,state TEXT,detail TEXT);'''.replace('DEFAULT0','DEFAULT 0'))

    def connect(self):
        db=sqlite3.connect(self.db,timeout=10)
        db.row_factory=sqlite3.Row
        return db

    @staticmethod
    def event(db,job,state,detail=''):
        db.execute('INSERT INTO events(job_id,at,state,detail) VALUES(?,?,?,?)',(job,utcnow(),state,detail))

    def submit(self,request,snapshot_root,*,parent=None):
        if platform.system()!='Linux':
            raise HazardError('UNSUPPORTED_RUNTIME','Scientific jobs must run in Linux')
        request=loads(json.dumps(request,allow_nan=False))
        validate_request(request,snapshot_root)
        job='job-'+uuid.uuid4().hex
        dest=self.root/job
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("SELECT count(*) FROM jobs WHERE state='QUEUED'").fetchone()[0]>=self.capacity:
                raise HazardError('QUEUE_FULL','Bounded queue is full')
            dest.mkdir()
            try:
                write_new(dest/'submitted-request.json',request)
                for asset in request['assets']:
                    src=verify_asset(snapshot_root,asset)
                    if src.stat().st_size>16*1024**2:
                        raise HazardError('INPUT_SIZE','Stage prepared/windowed inputs below16MiB each')
                    relative='input/'+asset['role']+src.suffix
                    path=dest/relative;path.parent.mkdir(exist_ok=True)
                    shutil.copyfile(src,path)
                    if sha256(path)!=asset['sha256']:
                        raise HazardError('CHECKSUM','Input changed while being staged')
                    asset['path']=relative
                validate_request(request,dest)
                write_new(dest/'request.json',request)
                # Freeze runtime config per job; later changes cannot silently affect queued jobs.
                write_new(dest/'runtime.json',load(self.config))
                write_new(dest/'submission-checksums.json',dict(request_sha256=sha256(dest/'request.json'),runtime_sha256=sha256(dest/'runtime.json')))
                db.execute('INSERT INTO jobs(id,state,created,parent) VALUES(?,?,?,?)',(job,'QUEUED',utcnow(),parent))
                self.event(db,job,'QUEUED','Inputs staged and verified')
            except Exception:
                # Unaccepted staging is not an experiment result; retain failure evidence.
                write_new(dest/'submission-error.json',dict(at=utcnow(),state='ERROR',reason='Submission rejected before acceptance'))
                raise
        return job

    def get(self,job):
        with self.connect() as db:
            row=db.execute('SELECT * FROM jobs WHERE id=?',(job,)).fetchone()
            if row is None:raise HazardError('JOB_NOT_FOUND',job)
            result=dict(row);result['usable_product']=row['state']=='SUCCEEDED'
            return result

    def events(self,job):
        with self.connect() as db:return [dict(v) for v in db.execute('SELECT * FROM events WHERE job_id=? ORDER BY seq',(job,))]

    def cancel(self,job):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT state FROM jobs WHERE id=?',(job,)).fetchone()
            if row is None:raise HazardError('JOB_NOT_FOUND',job)
            if row['state'] in TERMINAL:return False
            if row['state']=='QUEUED':
                db.execute("UPDATE jobs SET state='CANCELLED',cancel=1,ended=? WHERE id=?",(utcnow(),job))
                self.event(db,job,'CANCELLED','Cancelled before execution')
                directory=self.root/job
                _publish_manifest(directory,dict(schema_version='0.3.0',kind='run_manifest',run_id=job,status='CANCELLED',error_code='CANCELLED_BEFORE_START',parent_job=self.get(job)['parent'],request_id=load(directory/'request.json')['id'],metrics=None,detail='Cancelled before execution',seed=load(directory/'request.json')['options'].get('seed'),environment=load(directory/'runtime.json').get('environment',{}),started_at=None,ended_at=utcnow(),code=_code_identity(Path(__file__).resolve().parents[2]),artifacts={str(p.relative_to(directory)):sha256(p) for p in directory.rglob('*') if p.is_file()},qualification='UNQUALIFIED_RESEARCH'))
            else:
                db.execute('UPDATE jobs SET cancel=1 WHERE id=?',(job,))
                self.event(db,job,'CANCEL_REQUESTED','Worker tree termination requested')
        return True

    def retry(self,job):
        old=self.get(job)
        if old['state'] not in TERMINAL:raise HazardError('JOB_ACTIVE','Only terminal jobs may be retried')
        return self.submit(load(self.root/job/'request.json'),self.root/job,parent=job)

    def claim(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("SELECT count(*) FROM jobs WHERE state='RUNNING'").fetchone()[0]:return None
            row=db.execute("SELECT id FROM jobs WHERE state='QUEUED' ORDER BY rowid LIMIT1".replace('LIMIT1','LIMIT 1')).fetchone()
            if row is None:return None
            job=row['id'];db.execute("UPDATE jobs SET state='RUNNING',started=?,runner_pid=? WHERE id=?",(utcnow(),os.getpid(),job));self.event(db,job,'RUNNING')
            return job

    def recover(self):
        """Explicit recovery only; never assume an interrupted job is valid or silently retry."""
        recovered=[]
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            for row in db.execute("SELECT * FROM jobs WHERE state='RUNNING'").fetchall():
                try:os.kill(row['runner_pid'],0);alive=True
                except (ProcessLookupError,TypeError):alive=False
                if alive:continue
                if row['worker_pid']:
                    _terminate_group(row['worker_pid'])
                directory=self.root/row['id']
                request=load(directory/'request.json');cfg=load(directory/'runtime.json')
                # Preserve a manifest already written before a controller crash.
                # Recovery never reclassifies unverified output as usable.
                filename='recovery.json' if (directory/'manifest.json').exists() else 'manifest.json'
                _publish_manifest(directory,dict(schema_version='0.3.0',kind='run_manifest',run_id=row['id'],parent_job=row['parent'],request_id=request['id'],status='ERROR',error_code='INTERRUPTED',detail='Explicit controller recovery; output unverified; no automatic retry',started_at=row['started'],ended_at=utcnow(),metrics=None,artifacts={str(p.relative_to(directory)):sha256(p) for p in directory.rglob('*') if p.is_file()},seed=request['options'].get('seed'),environment=cfg.get('environment',{}),qualification='UNQUALIFIED_RESEARCH',code=_code_identity(Path(__file__).resolve().parents[2])),filename)
                db.execute("UPDATE jobs SET state='ERROR',ended=?,error_code='INTERRUPTED' WHERE id=?",(utcnow(),row['id']))
                self.event(db,row['id'],'ERROR','INTERRUPTED: explicit recovery, outputs unverified')
                recovered.append(row['id'])
        return recovered

    def work_once(self):
        job=self.claim()
        if job is None:return None
        directory=self.root/job;request=dict(id='UNKNOWN_CORRUPT_REQUEST',options={});cfg={}
        start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
        peak_rss=0;samples=0;state='ERROR';error='INTERNAL_ERROR';process=None
        detail='';queue_s=None
        try:
            frozen=load(directory/'submission-checksums.json')
            if sha256(directory/'request.json')!=frozen['request_sha256'] or sha256(directory/'runtime.json')!=frozen['runtime_sha256']:
                raise HazardError('CHECKSUM','Accepted request/runtime configuration changed')
            request=load(directory/'request.json');cfg=load(directory/'runtime.json')
            validate_request(request,directory)
            if shutil.disk_usage(directory).free<cfg.get('minimum_free_bytes',1024**3):
                raise HazardError('DISK_BUDGET','Insufficient free filesystem reserve')
            identity=_code_identity(Path(__file__).resolve().parents[2])
            write_new(directory/'execution-plan.json',dict(job_id=job,started_at=utcnow(),request_sha256=sha256(directory/'request.json'),runtime_config_sha256=sha256(directory/'runtime.json'),code=identity,python=sys.version,platform=platform.platform(),seed=request['options'].get('seed'),assumptions=request['assumptions'],limits=dict(timeout_s=request['timeout_s'],max_log_bytes=request['max_log_bytes'],max_job_bytes=cfg.get('max_job_bytes',512*1024**2))))
            command=build_command(directory,cfg)
            env=dict(os.environ,NUMBA_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj',PYTHONPATH=str(Path(__file__).resolve().parents[1]))
            if cfg.get('grass_addon_base'):env['GRASS_ADDON_BASE']=cfg['grass_addon_base']
            with (directory/'stdout.log').open('xb') as out,(directory/'stderr.log').open('xb') as err:
                process=subprocess.Popen(command,stdout=out,stderr=err,cwd=directory,env=env,start_new_session=True)
                with self.connect() as db:db.execute('UPDATE jobs SET worker_pid=? WHERE id=?',(process.pid,job))
                while process.poll() is None:
                    rss=_group_rss(process.pid);peak_rss=max(peak_rss,rss);samples+=1
                    status=self.get(job)
                    if status['cancel']:state,error='CANCELLED','CANCELLED';break
                    if time.monotonic()-start>request['timeout_s']:state,error='TIMEOUT','JOB_TIMEOUT';break
                    disk_bytes,log_bytes=_disk_usage(directory)
                    if log_bytes>request['max_log_bytes']:state,error='ERROR','LOG_LIMIT';break
                    if disk_bytes>cfg.get('max_job_bytes',512*1024**2):state,error='ERROR','DISK_LIMIT';break
                    time.sleep(.1)
                else:
                    if process.returncode:
                        worker_error=directory/'worker-error.json'
                        error=load(worker_error).get('code','WORKER_EXIT') if worker_error.exists() else 'WORKER_EXIT'
                        raise HazardError(error,'Worker exit '+str(process.returncode))
                    if not (directory/'product.json').is_file():
                        raise HazardError('INVALID_OUTPUT','Worker exited without a product contract')
                    validate_product(load(directory/'product.json'),request,directory)
                    product=load(directory/'product.json')
                    if product['job_id']!=job or product['request_id']!=request['id'] or product['hazard']!=request['hazard'] or product['grid']!=request['grid'] or (product['valid_from'],product['valid_until'])!=(request['valid_from'],request['valid_until']):
                        raise HazardError('PRODUCT_MISMATCH','Product does not match accepted request')
                    for layer in product['layers']:verify_asset(directory,layer)
                    state,error='SUCCEEDED',None
                if process.poll() is None:_terminate_group(process.pid)
                process.wait()
            validate_request(request,directory)
        except HazardError as exc:
            state,error,detail='ERROR',exc.code,str(exc)
        except Exception as exc:
            state,error,detail='ERROR','INTERNAL_ERROR',type(exc).__name__+': '+str(exc)
        finally:
            if process is not None:
                # Kill leftover descendants even when their direct parent already exited.
                _terminate_group(process.pid)
                process.wait()
            end=time.monotonic();after=resource.getrusage(resource.RUSAGE_CHILDREN)
            with self.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                current=db.execute('SELECT * FROM jobs WHERE id=?',(job,)).fetchone()
                if current['cancel']:state,error='CANCELLED','CANCELLED'
                # Manifest publication precedes terminal state exposure.
                metrics=dict(execution_s=end-start,queue_s=(__import__('datetime').datetime.fromisoformat(current['started'].replace('Z','+00:00'))-__import__('datetime').datetime.fromisoformat(current['created'].replace('Z','+00:00'))).total_seconds(),sampled_peak_process_group_rss_bytes=peak_rss,rss_samples=samples,rss_sampling_interval_s=.1,child_cpu_user_s=after.ru_utime-before.ru_utime,child_cpu_system_s=after.ru_stime-before.ru_stime,artifact_bytes=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file()))
                artifacts={str(p.relative_to(directory)):sha256(p) for p in directory.rglob('*') if p.is_file()}
                _publish_manifest(directory,dict(schema_version='0.3.0',kind='run_manifest',run_id=job,parent_job=current['parent'],request_id=request['id'],status=state,error_code=error,detail=detail,started_at=current['started'],ended_at=utcnow(),metrics=metrics,artifacts=artifacts,seed=request['options'].get('seed'),environment=cfg.get('environment',{}),qualification='UNQUALIFIED_RESEARCH',code=_code_identity(Path(__file__).resolve().parents[2])))
                db.execute('UPDATE jobs SET state=?,ended=?,error_code=? WHERE id=?',(state,utcnow(),error,job));self.event(db,job,state,error or 'Technical products verified')
        return self.get(job)

def build_command(directory,config):
    return [config['core_python'],'-m','hazardia.adapters.pipeline',str(directory)]

def _code_identity(root):
    try:
        sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
        # Only tracked source dirtiness is relevant; local runtime paths are separate/ignored.
        dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root,text=True))
        return dict(git_sha=sha,dirty=dirty,source_sha256={str(p.relative_to(root)):sha256(p) for p in (root/'src/hazardia').rglob('*.py')})
    except (OSError,subprocess.CalledProcessError):
        return dict(git_sha=None,dirty=None,reason='Git identity unavailable',source_sha256={})

def _group_rss(pgid):
    total=0
    for p in Path('/proc').glob('[0-9]*'):
        try:
            fields=(p/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[2])!=pgid:continue
            for line in (p/'status').read_text().splitlines():
                if line.startswith('VmRSS:'):total+=int(line.split()[1])*1024
        except (OSError,ValueError,IndexError):continue
    return total

def _terminate_group(pid):
    try:os.killpg(pid,signal.SIGTERM)
    except ProcessLookupError:return
    deadline=time.monotonic()+1
    while time.monotonic()<deadline:
        try:os.killpg(pid,0)
        except ProcessLookupError:return
        time.sleep(.05)
    try:os.killpg(pid,signal.SIGKILL)
    except ProcessLookupError:pass


def _disk_usage(directory):
    """Files in simulator scratch trees may disappear between traversal and stat."""
    total=logs=0
    for p in directory.rglob('*'):
        try:
            if not p.is_file():continue
            size=p.stat().st_size
        except FileNotFoundError:
            continue
        total+=size
        if p.suffix=='.log':logs+=size
    return total,logs


def _publish_manifest(directory,manifest,filename='manifest.json'):
    validate('run_manifest',manifest)
    write_new(directory/filename,manifest)
