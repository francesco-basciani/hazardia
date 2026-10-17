"""Bounded solver-pluggable proposals with immutable accepted inputs and verification."""
import json,time,subprocess,os,signal,sys,itertools
from pathlib import Path
from hazardia.io import write_new,load,HazardError,utcnow
from hazardia.domain.state import identity
from hazardia.decision.problem import validate
from hazardia.decision.verifier import verify,losses

def decide(problem,directory,solver_python,*,accepted_monotonic=None):
    start=time.monotonic() if accepted_monotonic is None else accepted_monotonic;directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    write_new(directory/'problem.json',problem);status='ERROR';detail='';selection=[];raw={};validation={}
    try:
        validate(problem);remaining=problem['settings']['budget_s']-(time.monotonic()-start)-.1
        if remaining<=0:raise TimeoutError('Acceptance queue exhausted deadline')
        backend=problem['settings']['solver']
        if backend=='highs':
            env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]))
            try:
                with (directory/'solver.log').open('xb') as log:
                    proc=subprocess.Popen([solver_python,'-m','hazardia.decision.highs_worker',str(directory/'problem.json'),str(directory/'solver.json')],stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=os.environ.get('HAZARDIA_DECISION_SUPERVISED')!='1')
                    try:proc.wait(timeout=remaining)
                    except subprocess.TimeoutExpired:
                        if os.environ.get('HAZARDIA_DECISION_SUPERVISED')=='1':proc.kill()
                        else:os.killpg(proc.pid,signal.SIGKILL)
                        proc.wait();raise TimeoutError('Independent solver watchdog')
                if proc.returncode:raise HazardError('DEPENDENCY_UNAVAILABLE','Solver process failed; see solver.log')
            except FileNotFoundError as e:raise HazardError('DEPENDENCY_UNAVAILABLE','Solver environment unavailable') from e
            raw=load(directory/'solver.json')
        elif backend=='enumeration':
            if len(problem['options'])>18:raise HazardError('DEPENDENCY_UNAVAILABLE','Reference enumeration limited to18options')
            best=None
            for bits in itertools.product([0,1],repeat=len(problem['options'])):
                if time.monotonic()-start>problem['settings']['budget_s']-.1:raise TimeoutError('Reference solver deadline')
                chosen=[o['id'] for o,b in zip(problem['options'],bits) if b]
                if verify(problem,chosen)['status']!='VALIDATED_FOR_SIMULATION':continue
                score=losses(problem,chosen)['objective']
                if best is None or score<best[0]:best=(score,chosen)
            raw=dict(solver='enumeration-reference',has_incumbent=best is not None,selected=[] if best is None else best[1],optimal=True,infeasible=best is None,termination='Exhaustive enumeration')
        else:raise HazardError('DEPENDENCY_UNAVAILABLE','Unknown pluggable solver')
        selection=raw['selected'];validation=verify(problem,selection)
        if time.monotonic()-start>=problem['settings']['budget_s']:status='TIMEOUT_UNPROVEN';selection=[]
        elif raw['infeasible']:status='PROVEN_INFEASIBLE';selection=[]
        elif not raw['has_incumbent']:status='TIMEOUT_UNPROVEN';selection=[]
        elif validation['status']!='VALIDATED_FOR_SIMULATION':status='SAFETY_UNVERIFIED';selection=[]
        else:status='VALIDATED_FOR_SIMULATION'
    except TimeoutError as e:status,detail='TIMEOUT_UNPROVEN',str(e)
    except (HazardError,KeyError,TypeError,ValueError) as e:status,detail=(e.code if isinstance(e,HazardError) and e.code=='DEPENDENCY_UNAVAILABLE' else 'INVALID_INPUT'),str(e)
    result=dict(schema_version=problem.get('schema_version','0.5.0'),kind='decision_response',id=directory.name,problem_sha256=identity(problem),status=status,selected=selection,verifier=validation,solver=raw,loss=losses(problem,selection) if status=='VALIDATED_FOR_SIMULATION' else None,baseline=losses(problem,[]) if status=='VALIDATED_FOR_SIMULATION' else None,elapsed_s=time.monotonic()-start,ended_at=utcnow(),detail=detail,operationally_approvable=False,qualification='SYNTHETIC_RESEARCH')
    write_new(directory/'response.json',result);return result
