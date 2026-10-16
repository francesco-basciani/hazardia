"""Bounded, revisioned VM-local research notes. No model/dispatch semantics."""
import json, math, os
from pathlib import Path
from hazardia.io import HazardError, load, utcnow


def validate(body):
    if set(body) != {'revision','cases','annotations','views'} or type(body['revision']) is not int or body['revision'] < 0:
        raise HazardError('INVALID_INPUT','Invalid notebook revision/fields')
    def text(v,n=80):
        if not isinstance(v,str) or not 1<=len(v)<=n or any(ord(c)<32 for c in v):
            raise HazardError('INVALID_INPUT','Invalid notebook text')
    def number(v,lo,hi):
        if type(v) not in (int,float) or not math.isfinite(v) or not lo<=v<=hi:
            raise HazardError('INVALID_INPUT','Invalid notebook coordinate/value')
    def point(p):
        if not isinstance(p,list) or len(p)!=2:raise HazardError('INVALID_INPUT','Invalid point')
        number(p[0],41.60,42.97);number(p[1],12.90,14.86)
    for name,limit in [('cases',20),('annotations',50),('views',20)]:
        if not isinstance(body[name],list) or len(body[name])>limit:raise HazardError('PAYLOAD_LIMIT','Notebook list limit')
    for c in body['cases']:
        if not isinstance(c,dict) or set(c)!={'name','hazard','scenario','resources','robust','road','transfer','disabled','preparedness'}:raise HazardError('INVALID_INPUT','Invalid case fields')
        text(c['name']);text(c['scenario'],128)
        if c['hazard'] not in ['FIRE','FLOOD','JOINT'] or type(c['resources']) is not int or not 1<=c['resources']<=8 or type(c['robust']) is not int or not 0<=c['robust']<=100:raise HazardError('INVALID_INPUT','Invalid case values')
        if any(type(c[k]) is not bool for k in ['road','transfer']) or c['disabled'] not in ['','unit-1','unit-2'] or c['preparedness'] not in ['','DELAYED','PREPOSITIONED']:raise HazardError('INVALID_INPUT','Invalid case options')
    for a in body['annotations']:
        if not isinstance(a,dict) or set(a)!={'name','kind','points'} or a['kind'] not in ['point','line','area']:raise HazardError('INVALID_INPUT','Invalid annotation')
        text(a['name'])
        pts=a['points'];minimum={'point':1,'line':2,'area':3}[a['kind']]
        if not isinstance(pts,list) or not minimum<=len(pts)<=200 or (a['kind']=='point' and len(pts)!=1):raise HazardError('INVALID_INPUT','Invalid vertex count')
        for p in pts:point(p)
    for v in body['views']:
        if not isinstance(v,dict) or set(v)!={'name','center','zoom','basemap','labels'}:raise HazardError('INVALID_INPUT','Invalid view')
        text(v['name']);point(v['center']);number(v['zoom'],8,20)
        if v['basemap'] not in ['ortho','sentinel'] or type(v['labels']) is not bool:raise HazardError('INVALID_INPUT','Invalid view layers')
    if len(json.dumps(body).encode())>60000:raise HazardError('PAYLOAD_LIMIT','Notebook byte limit')
    return body


class Notebook:
    def __init__(self,directory):
        self.directory=Path(directory);self.directory.mkdir(exist_ok=True)
    def read(self):
        paths=sorted(self.directory.glob('snapshot-*.json'))
        return load(paths[-1]) if paths else dict(revision=0,cases=[],annotations=[],views=[])
    def save(self,body):
        validate(body)
        current=self.read()
        if current['revision']!=body['revision']:raise HazardError('STALE_CONTEXT','Notebook changed; reload before saving')
        if current['revision']>=500:raise HazardError('PAYLOAD_LIMIT','500 notebook snapshots reached; archive before further edits')
        saved=dict(body,revision=current['revision']+1)
        dest=self.directory/('snapshot-%06d.json'%saved['revision'])
        # Append-only snapshots make clears recoverable; atomic rename avoids partial reads.
        tmp=dest.with_suffix('.pending')
        with tmp.open('x') as f:
            json.dump(saved,f,allow_nan=False);f.flush();os.fsync(f.fileno())
        tmp.replace(dest)
        return saved
