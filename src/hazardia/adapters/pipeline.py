"""Concrete process boundary: dispatch only supported CIMA jobs, then validate products."""
import os,subprocess,sys
from pathlib import Path
from hazardia.io import load,sha256,write_new,HazardError

def main(directory):
    root=Path(directory);request=load(root/'request.json');cfg=load(root/'runtime.json')
    try:
        for path,digest in cfg['engine_files'].items():
            if sha256(path)!=digest:raise HazardError('ENGINE_SOURCE_DRIFT',path)
        from hazardia.adapters.dispatch import prepare
        command,product,env,receipt=prepare(request,cfg,root,os.environ)
        receipt.update(request_sha256=sha256(root/'request.json'),runtime_sha256=sha256(root/'runtime.json'))
        write_new(root/'adapter-binding.json',receipt)
        subprocess.run(command,env=env,check=True)
        subprocess.run(product,env=env,check=True)
        for path,digest in cfg['engine_files'].items():
            if sha256(path)!=digest:raise HazardError('ENGINE_SOURCE_DRIFT',path)
    except Exception as exc:
        if not (root/'worker-error.json').exists():write_new(root/'worker-error.json',dict(code=exc.code if isinstance(exc,HazardError) else 'WORKER_EXIT',message=str(exc)))
        return 1
    return 0
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
