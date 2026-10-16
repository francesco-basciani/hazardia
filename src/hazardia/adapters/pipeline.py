"""Concrete process boundary: dispatch only supported CIMA jobs, then validate products."""
import os,subprocess,sys
from pathlib import Path
from hazardia.io import load,sha256,write_new,HazardError

def main(directory):
    root=Path(directory);request=load(root/'request.json');cfg=load(root/'runtime.json')
    try:
        for path,digest in cfg['engine_files'].items():
            if sha256(path)!=digest:raise HazardError('ENGINE_SOURCE_DRIFT',path)
        env=dict(os.environ)
        if request['hazard']=='FIRE':
            env['PYTHONPATH']=env['PYTHONPATH']+os.pathsep+cfg['fire_source']
            command=[cfg['fire_python'],'-m','hazardia.adapters.workers.fire',str(root)]
        elif request['hazard']=='FLOOD':
            if not request['options']['allow_experimental_patch']:
                raise HazardError('UNSUPPORTED_CONFIGURATION','Current terrain adapter requires declared experimental HAND/merge compatibility patch')
            command=[cfg['geo_python'],'-m','hazardia.adapters.workers.flood',str(root)]
        else:raise HazardError('UNSUPPORTED_HAZARD','No adapter for '+request['hazard'])
        subprocess.run(command,env=env,check=True)
        subprocess.run([cfg['geo_python'],'-m','hazardia.adapters.workers.product',str(root)],env=env,check=True)
        for path,digest in cfg['engine_files'].items():
            if sha256(path)!=digest:raise HazardError('ENGINE_SOURCE_DRIFT',path)
    except Exception as exc:
        if not (root/'worker-error.json').exists():write_new(root/'worker-error.json',dict(code=exc.code if isinstance(exc,HazardError) else 'WORKER_EXIT',message=str(exc)))
        return 1
    return 0
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
