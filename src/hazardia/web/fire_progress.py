"""Bounded read of native progress, distinct from replay/forecast validity time."""
import re
from pathlib import Path
from hazardia.io import load

def progress(root,state):
 folder=Path(root)/'jobs'/state['id'];request=load(folder/'request.json');total=request['options']['duration_s']/3600;hours=0
 log=folder/'stdout.log'
 if log.exists():
  with log.open('rb') as f:f.seek(max(0,log.stat().st_size-16384));tail=f.read(16384).decode('utf8',errors='replace')
  values=re.findall(r'^HOUR\s+([0-9]+(?:\.[0-9]+)?)\s+CELLS\s+[0-9]+',tail,re.M)
  if values:hours=min(total,float(values[-1]))
 stage='QUEUED' if state['state']=='QUEUED' else 'PRODUCTS' if hours>=total else 'MODEL' if hours else 'STARTUP'
 return dict(stage=stage,native_hours=hours,total_hours=total,qualification='NATIVE_LOG_PROGRESS_NOT_REPLAY_TIME')
