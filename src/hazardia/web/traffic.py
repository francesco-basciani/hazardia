"""Independent bounded visual traffic. Never imported by model/decision workers."""
import datetime as dt, hashlib, json, math, threading, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from hazardia.io import HazardError, utcnow
CLASSES={'motorway':90,'trunk':70,'primary':50,'secondary':40,'tertiary':35,'residential':25,'unclassified':25,'service':15,'living_street':10}
DEFAULT=dict(seed=1729,density=8,max_vehicles=160,speeds=CLASSES,closures=[],bounds=[13.376,42.346,13.384,42.354],preset='ordinario')
def validate(c):
 if not isinstance(c,dict) or set(c)!=set(DEFAULT):raise HazardError('INVALID_INPUT','Traffic configuration fields required')
 b=c['bounds']
 if not isinstance(b,list) or len(b)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in b) or not -180<=b[0]<b[2]<=180 or not -80<=b[1]<b[3]<=80 or b[2]-b[0]>.061 or b[3]-b[1]>.061:raise HazardError('INVALID_INPUT','Traffic area must be at most0.06° per side')
 for k,lo,hi in [('seed',0,2147483647),('density',0,200),('max_vehicles',0,400)]:
  if type(c[k]) is not int or not lo<=c[k]<=hi:raise HazardError('INVALID_INPUT','Invalid '+k)
 if not isinstance(c['speeds'],dict) or set(c['speeds'])!=set(CLASSES) or any(type(v) not in (int,float) or not math.isfinite(v) or not 1<=v<=130 for v in c['speeds'].values()):raise HazardError('INVALID_INPUT','Invalid hypothetical road speeds')
 if c['preset'] not in ['scarso','ordinario','intenso','personalizzato'] or not isinstance(c['closures'],list) or len(c['closures'])>500 or any(not isinstance(v,str) or len(v)>60 for v in c['closures']):raise HazardError('INVALID_INPUT','Invalid closures or preset')
 return c

def graph_from_xml(raw,bounds):
 root=ET.fromstring(raw);nodes={n.get('id'):[float(n.get('lon')),float(n.get('lat'))] for n in root.findall('node')};blocked=set();counts=dict(missing_oneway=0,excluded_access=0,excluded_conditional=0,excluded_restriction=0,incomplete_ways=0)
 # Conservative safe subset: do not approximate turn restrictions. Omit all referenced ways.
 for rel in root.findall('relation'):
  tags={t.get('k'):t.get('v') for t in rel.findall('tag')}
  if tags.get('type')=='restriction':blocked.update(m.get('ref') for m in rel.findall('member') if m.get('type')=='way')
 barriers=set()
 for node in root.findall('node'):
  tags={t.get('k'):t.get('v') for t in node.findall('tag')}
  access=tags.get('motorcar',tags.get('motor_vehicle',tags.get('access')))
  if access in ('no','private') or tags.get('barrier') and access not in ('yes','permissive','designated'):barriers.add(node.get('id'))
 edges=[];west,south,east,north=bounds
 for w in root.findall('way'):
  t={x.get('k'):x.get('v') for x in w.findall('tag')};kind=t.get('highway','').removesuffix('_link');wid=w.get('id')
  if kind not in CLASSES or t.get('area')=='yes':continue
  if wid in blocked:counts['excluded_restriction']+=1;continue
  if any('conditional' in k or k.endswith((':forward',':backward')) and k.split(':')[0] in ('access','vehicle','motor_vehicle','motorcar') for k in t):counts['excluded_conditional']+=1;continue
  access=t.get('motorcar',t.get('motor_vehicle',t.get('vehicle',t.get('access','yes'))))
  if access not in ('yes','permissive','designated'):counts['excluded_access']+=1;continue
  one=t.get('oneway');one=one if one is not None else 'yes' if t.get('junction')=='roundabout' or kind=='motorway' else None
  if one not in (None,'yes','1','true','no','0','false','-1'):counts['excluded_conditional']+=1;continue
  if one is None:counts['missing_oneway']+=1
  ids=[n.get('ref') for n in w.findall('nd')]
  if any(i not in nodes for i in ids):counts['incomplete_ways']+=1;continue
  for i,(a,b) in enumerate(zip(ids,ids[1:])):
   if a in barriers or b in barriers:continue
   p,q=nodes[a],nodes[b]
   if not all(west<=v[0]<=east and south<=v[1]<=north for v in (p,q)):continue
   length=math.hypot((p[0]-q[0])*111320*math.cos(math.radians((p[1]+q[1])/2)),(p[1]-q[1])*111320)
   if length<.5:continue
   directions=[(b,a,q,p)] if one=='-1' else [(a,b,p,q)] if one in ('yes','1','true') else [(a,b,p,q),(b,a,q,p)]
   for u,v,P,Q in directions:edges.append(dict(id=f'{wid}:{i}:{u}',way=wid,u=u,v=v,a=P,b=Q,length=length,kind=kind,direction_assumed=one is None))
 if len(edges)>12000:raise HazardError('AREA_TOO_DENSE','More than12000 directed segments; choose smaller area')
 return dict(schema='visual-traffic-graph/2',edges=edges,bounds=bounds,counts=counts,at=utcnow(),source='https://api.openstreetmap.org/api/0.6/map',license='ODbL-1.0',raw_sha256=hashlib.sha256(raw).hexdigest(),missing=['OSM completeness','Live closures','Missing oneway assumed bidirectional','Unknown barriers and vehicle-specific dimensions','External restriction relations may be incomplete in map extract'],restriction_policy='Exclude all ways referenced by returned restriction relations and all conditional ways; no full turn-restriction solver',coupled_to_optimizer=False)
class Traffic:
 def __init__(self,state):
  self.root=Path(state)/'visual-traffic';self.root.mkdir(exist_ok=True);self.lock=threading.Lock();self.active=False;self.current=dict(status='IDLE')
 def config(self):return json.loads((self.root/'config.json').read_text()) if (self.root/'config.json').exists() else json.loads(json.dumps(DEFAULT))
 def save(self,c):
  validate(c)
  with self.lock:
   p=self.root/'config.tmp';p.write_text(json.dumps(c));p.replace(self.root/'config.json')
  return c
 def snapshot(self):
  with self.lock:return dict(self.current)
 def prepare(self,c):
  c=validate(c);key=hashlib.sha256(json.dumps(c['bounds']).encode()).hexdigest()[:20];dest=self.root/(key+'.json')
  with self.lock:
   if self.active:raise HazardError('QUEUE_FULL','Traffic acquisition already running')
   if dest.exists():
    graph=json.loads(dest.read_text())
    if graph.get('schema')!='visual-traffic-graph/2':
     graph=graph_from_xml(dest.with_suffix('.osm').read_bytes(),c['bounds']);dest.write_text(json.dumps(graph))
    self.current=dict(status='READY',graph=graph);return self.current
   today=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d');quota=self.root/(today+'.quota');attempts=int(quota.read_text()) if quota.exists() else 0
   if attempts>=8:raise HazardError('SOURCE_QUOTA','8 traffic area acquisitions per day; cached areas remain available')
   if sum(p.stat().st_size for p in self.root.iterdir() if p.is_file())>48*1024**2:raise HazardError('CACHE_FULL','Traffic cache48MiB reached')
   quota.write_text(str(attempts+1));self.active=True;self.current=dict(status='LOADING')
  def work():
   try:
    url='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,c['bounds']))
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HAZARDIA research visual traffic/1'}),timeout=25) as r:raw=r.read(4*1024**2+1)
    if len(raw)>4*1024**2:raise ValueError('OSM response exceeds4MiB; reduce area')
    graph=graph_from_xml(raw,c['bounds']);encoded=json.dumps(graph)
    if sum(p.stat().st_size for p in self.root.iterdir() if p.is_file())+len(raw)+len(encoded.encode())>48*1024**2:raise ValueError('Traffic cache48MiB admission limit reached')
    dest.with_suffix('.osm').write_bytes(raw);dest.write_text(encoded);value=dict(status='READY',graph=graph)
   except Exception as e:value=dict(status='ERROR',detail=str(e))
   with self.lock:self.current=value;self.active=False
  threading.Thread(target=work,daemon=True).start();return dict(status='LOADING')
