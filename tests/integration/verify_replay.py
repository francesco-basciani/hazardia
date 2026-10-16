"""Pinned decision replay from an isolated local source checkout; no field-skill claim."""
import argparse,sys,platform,subprocess
from pathlib import Path
import hazardia
from hazardia.io import load,write_new,sha256
from hazardia.domain.state import identity
from hazardia.domain.contracts import validate_record
from hazardia.decision.supervisor import bounded_decide
from hazardia.decision.verifier import verify

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--problem',required=True);ap.add_argument('--reference',required=True);ap.add_argument('--solver-python',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(__file__).resolve().parents[2];module=Path(hazardia.__file__).resolve();assert module.is_relative_to(root),module
    p=load(a.problem);expected=load(a.reference);assert identity(p)==expected['problem_sha256'];actual=bounded_decide(p,Path(a.out)/'decision',a.solver_python);assert actual['status']=='VALIDATED_FOR_SIMULATION';assert verify(p,actual['selected'])['status']=='VALIDATED_FOR_SIMULATION';assert abs(actual['loss']['objective']-expected['loss']['objective'])<1e-7
    for profile in ['abruzzo.json','senegal-synthetic.json']:validate_record(load(root/'profiles/research'/profile))
    result=dict(status='PASS',source_module=str(module),git_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),problem_sha256=sha256(a.problem),reference_sha256=sha256(a.reference),expected=expected['loss'],actual=actual['loss'],selected_equal=actual['selected']==expected['selected'],profile_contracts=['abruzzo','senegal-synthetic'],platform=platform.platform(),python=sys.version,scope='Isolated source checkout reuses same guest environments and pinned metadata. Not a fresh machine install, a native physics replay, or formal network namespace isolation.')
    write_new(Path(a.out)/'results.json',result);print(result)
if __name__=='__main__':main()
