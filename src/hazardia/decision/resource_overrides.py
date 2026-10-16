"""User-authored evacuation research inputs; never physical suppression."""
import math
from hazardia.io import HazardError

def apply(problem,rows):
    if not isinstance(rows,list) or len(rows)!=len(problem['resources']):raise HazardError('INVALID_INPUT','One bounded resource row per selected unit required')
    ids={r['id'] for r in problem['resources']}
    if any(not isinstance(r,dict) or set(r)!={'id','lat','lon','arrival_minutes','available'} for r in rows):raise HazardError('INVALID_INPUT','Strict evacuation resource row required')
    if len({r['id'] for r in rows})!=len(rows) or {r['id'] for r in rows}!=ids:raise HazardError('INVALID_INPUT','Resource IDs do not match pool')
    for row in rows:
        for k in ['lat','lon','arrival_minutes']:
            v=row[k]
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise HazardError('INVALID_INPUT','Finite resource position/time required')
        if not -90<=row['lat']<=90 or not -180<=row['lon']<=180 or not 0<=row['arrival_minutes']<=480 or type(row['available']) is not bool:raise HazardError('INVALID_INPUT','Resource bounds/availability invalid')
        r=next(r for r in problem['resources'] if r['id']==row['id']);p=r['record']['payload'];p['point_wgs84']=[row['lon'],row['lat']];r['record']['available_at']=problem['data_cutoff']
        if not row['available']:p['maintenance']='UNAVAILABLE'
        r['record']['provenance']['source']='User-authored evacuation research unit; manual arrival, no routing or physical suppression'
        for o in problem['options']:
            if o['resource_id']!=row['id']:continue
            o['arrival_s']=row['arrival_minutes']*60
            factor=max(0,1-o['arrival_s']/600)/.8
            o['benefit']={k:v*factor for k,v in o['benefit'].items()}
    return problem
