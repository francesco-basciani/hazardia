"""Outer deadline includes queue, solver, verifier and artifact serialization."""
import os,signal,subprocess,sys,time,math,platform
from pathlib import Path
from hazardia.io import load,write_new,utcnow,sha256
from hazardia.domain.state import identity
from hazardia.jobs import _code_identity

def _command(directory,solver_python,accepted):return [sys.executable,'-m','hazardia.decision.supervisor','worker',str(directory),str(solver_python),str(accepted)]

def bounded_decide(problem,directory,solver_python,*,accepted_monotonic=None):
    start=time.monotonic() if accepted_monotonic is None else accepted_monotonic;out=Path(directory);out.mkdir(parents=True,exist_ok=False);write_new(out/'problem.json',problem)
    budget=problem.get('settings',{}).get('budget_s',60)
    if not isinstance(budget,(int,float)) or isinstance(budget,bool) or not math.isfinite(budget) or not 0<budget<=60:budget=60
    identity_code=_code_identity(Path(__file__).resolve().parents[3]);write_new(out/'execution-plan.json',dict(accepted_at=utcnow(),accepted_monotonic=start,budget_s=budget,code=identity_code,solver_python=solver_python,core_python=sys.version,platform=platform.platform(),problem_sha256=identity(problem)))
    process=None;result=None;detail='';reserve=min(1.,budget*.5);remaining=start+budget-time.monotonic()-reserve
    try:
        if remaining<=0:raise subprocess.TimeoutExpired('acceptance-queue',budget)
        env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),HAZARDIA_DECISION_SUPERVISED='1')
        with (out/'supervisor.log').open('xb') as log:
            process=subprocess.Popen(_command(out,solver_python,start),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
            process.wait(timeout=max(.001,start+budget-time.monotonic()-reserve))
        path=out/'compute/response.json'
        if process.returncode or not path.exists():detail='Worker exited without a valid response'
        elif path.stat().st_size>2*1024**2:detail='Response exceeds serialization bound'
        else:result=load(path)
    except subprocess.TimeoutExpired:detail='Outer deadline exceeded, including queue/verifier/serialization'
    except OSError as e:detail='Decision dependency unavailable: '+type(e).__name__
    finally:
        if process is not None:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            process.wait()
    late=time.monotonic()-start>=budget-reserve*.25
    if result is None or late:
        result=dict(schema_version='0.5.0',kind='decision_response',id=out.name,problem_sha256=identity(problem),status='TIMEOUT_UNPROVEN' if late or 'deadline' in detail else 'ERROR',selected=[],verifier={},solver={},loss=None,baseline=None,detail=detail or 'Serialization reserve exhausted',operationally_approvable=False,qualification='SYNTHETIC_RESEARCH')
    result.update(id=out.name,elapsed_s=time.monotonic()-start,ended_at=utcnow(),outer_watchdog=True)
    write_new(out/'response.json',result);return result

if __name__=='__main__':
    from hazardia.decision.controller import decide
    out=Path(sys.argv[2]);decide(load(out/'problem.json'),out/'compute',sys.argv[3],accepted_monotonic=float(sys.argv[4]))
