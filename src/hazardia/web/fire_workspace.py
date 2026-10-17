"""VM-local versioned fire scenarios; saved drafts do not qualify simulation results."""
import json,os,re
from pathlib import Path
from hazardia.io import HazardError,load
from hazardia.firelab import validate
class FireWorkspace:
    def __init__(self,directory):
        self.directory=Path(directory);self.directory.mkdir(exist_ok=True)
    def read(self):
        p=self.directory/'workspace.json'
        return load(p) if p.exists() else dict(revision=0,scenarios=[])
    def save(self,body):
        if set(body)!={'revision','scenarios'} or type(body['revision']) is not int or not isinstance(body['scenarios'],list):raise HazardError('INVALID_INPUT','Invalid workspace')
        ids=[]
        for s in body['scenarios']:
            if not isinstance(s,dict) or not {'id','name','input','job_id','submitted_input'}<=set(s) or set(s)-{'id','name','input','job_id','submitted_input','previous_job_id'}:raise HazardError('INVALID_INPUT','Invalid scenario fields')
            if not isinstance(s['id'],str) or not re.fullmatch('[a-zA-Z0-9_-]{1,60}',s['id']) or not isinstance(s['name'],str) or not 1<=len(s['name'])<=80 or any(ord(c)<32 for c in s['name']):raise HazardError('INVALID_INPUT','Invalid scenario identity')
            validate(s['input'])
            if s['submitted_input'] is not None:validate(s['submitted_input'])
            if s['job_id'] is not None and (not isinstance(s['job_id'],str) or not re.fullmatch('job-[a-f0-9]{32}',s['job_id'])):raise HazardError('INVALID_INPUT','Invalid stored job')
            if s.get('previous_job_id') is not None and (not isinstance(s['previous_job_id'],str) or not re.fullmatch('job-[a-f0-9]{32}',s['previous_job_id'])):raise HazardError('INVALID_INPUT','Invalid previous job')
            ids.append(s['id'])
        if len(ids)!=len(set(ids)):raise HazardError('INVALID_INPUT','Duplicate scenarios')
        current=self.read()
        if current['revision']!=body['revision']:raise HazardError('STALE_CONTEXT','Workspace changed in another client; reload before saving')
        value=dict(body,revision=current['revision']+1);raw=json.dumps(value,allow_nan=False)
        if len(raw.encode())>60000:raise HazardError('PAYLOAD_LIMIT','Workspace byte budget reached; export scenarios before removing drafts')
        dest=self.directory/'workspace.json';temp=self.directory/'workspace.pending'
        with temp.open('w') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        temp.replace(dest);return value
