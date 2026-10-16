"""Deterministic bounded geographic read index and immutable temporal snapshots."""
import json,hashlib,sqlite3
from hazardia.io import timestamp,write_new,HazardError
from hazardia.domain.contracts import validate_record,require,bounds,within

def identity(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def snapshot(profile,records,as_of,path):
    validate_record(profile);require(profile['kind']=='territory','INVALID_PROFILE','Territory required');cutoff=timestamp(as_of)
    require(timestamp(profile['available_at'])<=cutoff,'FUTURE_SOURCE','Profile unavailable at cutoff')
    selected={};excluded=[];bbox=profile['payload']['bbox_wgs84']
    for record in records:
        validate_record(record);p=record['payload'];require(p.get('territory_id')==profile['id'],'TERRITORY_MISMATCH','Record belongs to another territory')
        if 'point_wgs84' in p:require(within(p['point_wgs84'],bbox),'INVALID_GEOMETRY','Record outside profile')
        if timestamp(record['available_at'])>cutoff:excluded.append(record['id']);continue
        if record['id'] in selected:require(identity(selected[record['id']])==identity(record),'CONFLICTING_REVISION','Same ID different bytes')
        selected[record['id']]=record
    result=dict(schema_version='0.4.0',kind='territorial_snapshot',profile=profile,as_of=as_of,records=[selected[k] for k in sorted(selected)],excluded_future_ids=sorted(excluded),qualification='UNQUALIFIED_RESEARCH')
    result['content_sha256']=identity(result);write_new(path,result);return result

class GeoIndex:
    """Immutable DB build with SQLite RTree candidate filtering; point coverage in WGS84."""
    def __init__(self,path):self.path=path
    def build(self,records):
        from pathlib import Path
        # Exclusive create; never silently rebuild an earlier snapshot index.
        with Path(self.path).open('xb'):pass
        with sqlite3.connect(self.path) as db:
            db.executescript('CREATE TABLE records(n INTEGER PRIMARY KEY,id TEXT UNIQUE,available TEXT,data TEXT);CREATE INDEX available_idx ON records(available);CREATE VIRTUAL TABLE geo USING rtree(n,x0,x1,y0,y1);')
            for n,record in enumerate(records,1):
                validate_record(record);p=record['payload'];point=p.get('point_wgs84');require(point is not None,'INVALID_GEOMETRY','Point DTO required')
                db.execute('INSERT INTO records VALUES(?,?,?,?)',(n,record['id'],record['available_at'],json.dumps(record,allow_nan=False)))
                x,y=point;db.execute('INSERT INTO geo VALUES(?,?,?,?,?)',(n,x,x,y,y))
    def window(self,bbox,as_of,limit=100):
        bounds(bbox);cutoff=timestamp(as_of);require(isinstance(limit,int) and not isinstance(limit,bool) and 1<=limit<=1000,'PAYLOAD_LIMIT','Window limit1..1000')
        # RTree float32 bounds are conservative: exact filter must precede limit.
        with sqlite3.connect('file:'+str(self.path)+'?mode=ro',uri=True) as db:
            rows=db.execute('SELECT r.data FROM records r JOIN geo g ON g.n=r.n WHERE g.x1>=? AND g.x0<=? AND g.y1>=? AND g.y0<=? ORDER BY r.id',(bbox[0],bbox[2],bbox[1],bbox[3]))
            result=[]
            for (data,) in rows:
                v=json.loads(data)
                if timestamp(v['available_at'])<=cutoff and within(v['payload']['point_wgs84'],bbox):result.append(v)
                if len(result)==limit:break
        return result
