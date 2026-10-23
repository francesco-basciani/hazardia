"""Recent Sentinel discovery and bounded quicklooks, separate from map backgrounds."""
import datetime as dt,hashlib,json,re,threading,urllib.parse,urllib.request
from pathlib import Path
from hazardia.io import HazardError,utcnow
from hazardia.territorial_context import bounds_checked
STAC='https://stac.dataspace.copernicus.eu/v1/search'
def thumbnail_url(url):
 if not re.fullmatch(r'https://(?:datahub|zipper)\.creodias\.eu/odata/v1/Assets\([a-f0-9-]{36}\)/\$value',url):raise ValueError('Unsupported thumbnail endpoint')
 return url
class RecentImagery:
 def __init__(self,state):self.root=Path(state)/'recent-imagery';self.root.mkdir(exist_ok=True);self.lock=threading.Lock();self.value=dict(status='IDLE');self.busy=False
 def snapshot(self):
  with self.lock:return dict(self.value)
 def image(self,key):
  if not re.fullmatch('[a-f0-9]{24}',key):raise HazardError('NOT_FOUND','Invalid preview')
  path=self.root/(key+'.jpg')
  if not path.exists():raise HazardError('NOT_FOUND','Preview not available')
  return path.read_bytes()
 def prepare(self,body):
  if set(body)!={'bounds'}:raise HazardError('INVALID_INPUT','bounds required')
  bounds=bounds_checked(body['bounds']);key=hashlib.sha256(json.dumps([bounds,dt.date.today().isoformat()]).encode()).hexdigest()[:24];dest=self.root/(key+'.json')
  with self.lock:
   if self.busy:raise HazardError('QUEUE_FULL','Recent imagery query busy')
   if dest.exists():
    cached=json.loads(dest.read_text())
    if cached.get('items'):self.value=cached;return self.value
   quota=self.root/(dt.date.today().isoformat()+'.quota');n=int(quota.read_text()) if quota.exists() else 0
   if n>=6:raise HazardError('SOURCE_QUOTA','6 recent imagery queries per day')
   if sum(p.stat().st_size for p in self.root.iterdir())>24*1024**2:raise HazardError('CACHE_FULL','Recent preview cache24MiB reached')
   quota.write_text(str(n+1));self.busy=True;self.value=dict(status='LOADING')
  def get(url,cap):
   class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
     thumbnail_url(newurl)
     return super().redirect_request(req,fp,code,msg,headers,newurl)
   with urllib.request.build_opener(SafeRedirect()).open(urllib.request.Request(url,headers={'User-Agent':'HAZARDIA research/1'}),timeout=20) as response:
    if response.geturl()!=url:thumbnail_url(response.geturl())
    raw=response.read(cap+1)
   if len(raw)>cap:raise ValueError('Source response too large')
   return raw
  def admit(size):
   if sum(p.stat().st_size for p in self.root.iterdir())+size>24*1024**2:raise ValueError('Preview cache24MiB admission limit reached')
  def work():
   try:
    now=dt.datetime.now(dt.timezone.utc);query=dict(collections='sentinel-2-l2a',bbox=','.join(map(str,bounds)),limit=12,sortby='-datetime',datetime=(now-dt.timedelta(days=30)).isoformat()+'/'+now.isoformat());url=STAC+'?'+urllib.parse.urlencode(query);raw=get(url,2*1024**2);items=json.loads(raw)['features'];admit(len(raw));(self.root/(key+'.stac')).write_bytes(raw);selected=[];grid=None;days=set()
    for f in items:
     p=f['properties'];day=p['datetime'][:10]
     if len(selected)==2:break
     if grid and p.get('grid:code')!=grid or day in days:continue
     asset=f.get('assets',{}).get('thumbnail',{});href=asset.get('href')
     if not href:continue
     try:
      preview=get(thumbnail_url(href),2*1024**2)
      if not preview.startswith(b'\xff\xd8\xff'):raise ValueError('Not JPEG')
      ident=hashlib.sha256(preview).hexdigest()[:24];admit(len(preview));(self.root/(ident+'.jpg')).write_bytes(preview)
      selected.append(dict(id=f['id'],at=p['datetime'],cloud_percent=p.get('eo:cloud_cover'),grid=p.get('grid:code'),geometry=f['geometry'],thumbnail='/api/monitoring/recent-imagery/'+ident+'.jpg',preview_sha256=hashlib.sha256(preview).hexdigest(),source=href));grid=p.get('grid:code');days.add(day)
     except Exception as e:errors.append(str(e))
    value=dict(status='READY',items=selected,bounds=bounds,queried_at=utcnow(),source=url,raw_sha256=hashlib.sha256(raw).hexdigest(),errors=errors,license='Copernicus Sentinel data: free, full and open; credit European Union / Copernicus Sentinel',qualification='Observed optical quicklook, not a georectified analytical raster; cloud percentage is tile-wide; no interpolation to map or automatic fire confirmation',missing=[] if len(selected)==2 else ['Two different acquisition dates with accessible previews not found in latest12 intersecting products'])
    encoded=json.dumps(value);admit(len(encoded.encode()));dest.write_text(encoded)
   except Exception as e:value=dict(status='ERROR',detail=str(e))
   with self.lock:self.value=value;self.busy=False
  errors=[];threading.Thread(target=work,daemon=True).start();return dict(status='LOADING')
