"""Run synthetic native storage component checks against an already built HMC.
Linux guest only; never installs, edits upstream files, or changes the live catalog.
This is not an intervention integration or calibrated basin validation.
"""
import argparse,datetime,hashlib,json,platform,re,shlex,subprocess
from pathlib import Path

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--engine-source',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    if platform.system()!='Linux':raise SystemExit('Run in the Linux VM; Mac is only development/display client')
    src=Path(a.engine_source).resolve();out=Path(a.output).resolve();harness=Path(__file__).resolve().parents[1]/'tests/native/hmc_storage_probe.f90'
    if out.exists():raise SystemExit('Use a new output directory; previous evidence is immutable')
    objects=sorted(p for p in src.glob('*.o') if p.name!='HMC_Main.o')
    if not objects or not (src/'hmc_module_phys_hydraulicstructure.mod').exists():raise SystemExit('First build the pinned HMC via the documented bootstrap')
    out.mkdir(parents=True);source_hashes={str(p):digest(p) for p in src.glob('*.f90')}
    manifest=dict(started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),platform=platform.platform(),harness_sha256=digest(harness),upstream_source_sha256=source_hashes,linked_objects={p.name:digest(p) for p in objects},compiler=subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0],scope='Synthetic native component checks, not calibrated basin or coupled mitigation',reviewer='Automated oracle; Codex self-check, no external domain review')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    command=['gfortran','-O0','-fcheck=all','-fbacktrace','-ffree-line-length-none','-I'+str(src),str(harness),*[str(p) for p in objects],*shlex.split(subprocess.check_output(['nf-config','--flibs'],text=True)),'-o',str(out/'storage-probe')]
    build=subprocess.run(command,cwd=out,text=True,capture_output=True);(out/'compile.stdout').write_text(build.stdout);(out/'compile.stderr').write_text(build.stderr)
    result=dict(compile_exit=build.returncode,compile_command=command,status='FAIL')
    if build.returncode==0:
        run=subprocess.run([str(out/'storage-probe')],cwd=out,text=True,capture_output=True,timeout=20)
        (out/'native.stdout').write_text(run.stdout);(out/'native.stderr').write_text(run.stderr)
        checks=len(re.findall(r'^\s*PASS',run.stdout,re.M));result.update(native_exit=run.returncode,assertions_passed=checks,synthetic_cases=7)
        if run.returncode==0 and checks==21 and 'ALL_COMPONENT_CHECKS_PASS' in run.stdout:result['status']='PASS'
    result['upstream_sources_unchanged']=all(digest(p)==h for p,h in source_hashes.items())
    if not result['upstream_sources_unchanged']:result['status']='FAIL'
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
