"""Opt-in prepared cases with independently revisioned VM workspaces."""
import re
from pathlib import Path
from hazardia.io import load,HazardError
from hazardia.web.fire_workspace import FireWorkspace
class FireCases:
 def __init__(self,runtime):
  self.root=Path(runtime);self.assets=self.root/'web-assets/fire-cases';self.state=self.root/'web-state/fire-case-workspaces'
 def definition(self,ident):
  if not isinstance(ident,str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',ident):raise HazardError('INVALID_INPUT','Invalid saved case identifier')
  path=self.assets/(ident+'.json')
  if not path.is_file():raise HazardError('NOT_FOUND','Saved case unavailable')
  if path.stat().st_size>60000:raise HazardError('PAYLOAD_LIMIT','Saved case too large')
  value=load(path)
  if value.get('id')!=ident or not isinstance(value.get('scenarios'),list) or not 1<=len(value['scenarios'])<=12:raise HazardError('INVALID_INPUT','Invalid saved case definition')
  for key in ['title','description','qualification','source_url']:
   if not isinstance(value.get(key),str) or len(value[key])>2000:raise HazardError('INVALID_INPUT','Invalid saved case metadata')
  if not value['source_url'].startswith('https://'):raise HazardError('INVALID_INPUT','Case source must use HTTPS')
  initial=value.get('initial_hour',0)
  if type(initial) not in [int,float] or not 0<=initial<=72:raise HazardError('INVALID_INPUT','Invalid initial playback hour')
  return value
 def catalog(self):
  return [dict(id=d['id'],title=d['title'],description=d['description']) for p in sorted(self.assets.glob('*.json'))[:20] for d in [self.definition(p.stem)]]
 def workspace(self,ident):
  definition=self.definition(ident);self.state.mkdir(parents=True,exist_ok=True);store=FireWorkspace(self.state/ident)
  if not (store.directory/'workspace.json').exists():store.save(dict(revision=0,scenarios=definition['scenarios']))
  return store
 def read(self,ident):
  definition=self.definition(ident);return dict(self.workspace(ident).read(),case={k:definition[k] for k in ['id','title','description','qualification','source_url']}|{'initial_hour':definition.get('initial_hour',0)})
