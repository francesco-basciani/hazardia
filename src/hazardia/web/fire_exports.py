"""Bounded immutable draft exports, independent of workspace revision and jobs."""
import hashlib,json,re
from pathlib import Path
from hazardia.io import HazardError,load,write_new
from hazardia.web.fire_workspace import FireWorkspace
class FireExports:
 def __init__(self,root):self.directory=Path(root)/'fire-exports'
 def create(self,body):
  if not isinstance(body,dict) or set(body)!={'scenarios'}:raise HazardError('INVALID_INPUT','Scenario snapshot required')
  FireWorkspace.validate_body(dict(revision=0,scenarios=body['scenarios']))
  raw=json.dumps(body,sort_keys=True,separators=(',',':'),allow_nan=False).encode();ident=hashlib.sha256(raw).hexdigest()[:32]
  self.directory.mkdir(parents=True,exist_ok=True);p=self.directory/(ident+'.json')
  if not p.exists():
   if len(list(self.directory.glob('*.json')))>=32:raise HazardError('PAYLOAD_LIMIT','Export archive full; JSON remains available in browser')
   write_new(p,body)
  return dict(id=ident,url='/api/fire-exports/'+ident+'.json',filename='hazardia-scenari-'+ident[:8]+'.json',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 def read(self,ident):
  if not isinstance(ident,str) or not re.fullmatch('[a-f0-9]{32}',ident):raise HazardError('INVALID_INPUT','Invalid export identifier')
  p=self.directory/(ident+'.json')
  if not p.is_file():raise HazardError('NOT_FOUND','Export unavailable')
  return load(p)
