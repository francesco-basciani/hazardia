"""Loopback-only COG range gateway: bounded bytes, immutable cached chunks and receipts."""
import hashlib,json,re,threading,time,urllib.request,urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from hazardia.io import load,write_new,HazardError,utcnow
HOSTS=('https://copernicus-dem-30m.s3.amazonaws.com/','https://esa-worldcover.s3.eu-central-1.amazonaws.com/')
class RangeCache:
 def __init__(self,root,cap=96*1024**2):
  self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.cap=cap;self.bytes=0;self.urls={};self.error=None;self.lock=threading.Lock()
 def metadata(self,url):
  if not url.startswith(HOSTS) or not url.endswith('.tif'):raise HazardError('SOURCE_URL','Unapproved COG source')
  key=hashlib.sha256(url.encode()).hexdigest();meta=self.root/(key+'.json')
  if meta.exists():return key,load(meta)
  with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=20) as r:
   if r.geturl()!=url:raise HazardError('SOURCE_URL','COG redirect rejected')
   m=dict(url=url,bytes=int(r.headers['Content-Length']),etag=r.headers.get('ETag'),available_at=utcnow())
  write_new(meta,m);return key,m
 def start(self):
  owner=self
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*a):pass
   def do_HEAD(self):self.reply(False)
   def do_GET(self):self.reply(True)
   def reply(self,body):
    try:
     key=self.path.split('/')[-1].split('?')[0].removesuffix('.tif');url,meta=owner.urls[key];total=meta['bytes'];data=b''
     if body:
      match=re.fullmatch(r'bytes=(\d+)-(\d+)',self.headers.get('Range',''))
      if not match:raise HazardError('DOWNLOAD_BUDGET','Only explicit bounded HTTP ranges allowed')
      a,b=map(int,match.groups());b=min(b,total-1)
      if a<0 or b<a or b-a+1>32*1024**2:raise HazardError('DOWNLOAD_BUDGET','Range larger than32MiB')
      chunk=owner.root/(key+'-'+str(a)+'-'+str(b));receipt=chunk.with_suffix('.receipt.json')
      with owner.lock:
       if chunk.exists():
        data=chunk.read_bytes()
        if hashlib.sha256(data).hexdigest()!=load(receipt)['sha256']:raise HazardError('CHECKSUM','COG cache changed')
       else:
        size=b-a+1
        if owner.bytes+size>owner.cap or sum(p.stat().st_size for p in owner.root.iterdir())+size>256*1024**2:raise HazardError('DOWNLOAD_BUDGET','Bounded COG download/cache exhausted')
        owner.bytes+=size
        headers={'Range':f'bytes={a}-{b}','If-Match':meta['etag']} if meta['etag'] else {'Range':f'bytes={a}-{b}'}
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r:
         if r.status!=206 or r.geturl()!=url or r.headers.get('Content-Range')!=f'bytes {a}-{b}/{total}':raise HazardError('SOURCE_RANGE','Server must honor exact HTTP byte range')
         data=r.read(size+1)
        if len(data)!=size:raise HazardError('SOURCE_MISSING','Incomplete COG range')
        chunk.write_bytes(data);write_new(receipt,dict(url=url,range=[a,b],sha256=hashlib.sha256(data).hexdigest(),etag=meta['etag'],available_at=utcnow()))
     self.send_response(206 if body else 200);self.send_header('Content-Length',str(len(data) if body else total));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Type','image/tiff')
     if body:self.send_header('Content-Range',f'bytes {a}-{b}/{total}')
     self.end_headers()
     if body:self.wfile.write(data)
    except Exception as e:owner.error=str(e);self.send_error(503,'Bounded raster source unavailable')
  self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.daemon_threads=True;threading.Thread(target=self.server.serve_forever,daemon=True).start();return self
 def local(self,url):
  key,m=self.metadata(url);self.urls[key]=(url,m);return f'/vsicurl/http://127.0.0.1:{self.server.server_port}/{key}.tif'
 def close(self):self.server.shutdown();self.server.server_close()
