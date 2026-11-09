"""Lossless packing of verified closed host evidence; never scientific processing.

Original bytes and per-path metadata are retained. restore_file reads both direct
files and immutable content packs without expanding the whole archive.
"""
import hashlib,json,os,re,tarfile,tempfile,io,fcntl
from pathlib import Path
MAX_BATCH=64*1024**2
MAX_PACK=16*1024**2

def sha(data):return hashlib.sha256(data).hexdigest()
def candidates(root):
 for receipt in sorted(root.glob('*/host-receipt.json')):
  ack=json.loads(receipt.read_text())
  if ack.get('archive_protocol_version')!=2 or not ack.get('complete',True):continue
  for name,digest in ack.get('files',{}).items():
   if not re.fullmatch(r'[A-Za-z0-9_.-]+',name) or not name.endswith(('.py','.json')):continue
   path=receipt.parent/name
   if path.is_file() and not path.is_symlink() and sha(path.read_bytes())==digest:yield path,digest

def pack_closed(root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True)
 # Serialize manual maintenance with the archiver's own packing step.
 with (root/'.pack.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  return _pack_closed(root)

def _pack_closed(root):
 root=Path(root);folder=root/'evidence-packs';folder.mkdir(exist_ok=True);batch=[];size=0;reports=[]
 def flush(batch):
  if not batch:return
  aliases={};objects={}
  for path,digest in batch:
   st=path.stat();body=path.read_bytes()
   if sha(body)!=digest:raise ValueError('EVIDENCE_CHANGED')
   objects.setdefault(digest,body);aliases[str(path.relative_to(root))]=dict(sha256=digest,bytes=len(body),mode=st.st_mode,uid=st.st_uid,gid=st.st_gid,mtime_ns=st.st_mtime_ns,atime_ns=st.st_atime_ns)
  fd,temp=tempfile.mkstemp(prefix='hazardia-pack-',suffix='.tgz');os.close(fd);tmp=Path(temp)
  try:
   with tarfile.open(tmp,'w:gz') as tar:
    for digest,body in sorted(objects.items()):
     info=tarfile.TarInfo('objects/'+digest);info.size=len(body);info.mode=0o444;tar.addfile(info,io.BytesIO(body))
   if tmp.stat().st_size>MAX_PACK:raise RuntimeError('HOST_PACK_WORKSPACE_LIMIT_16MIB')
   with tarfile.open(tmp) as tar:
    for digest,body in objects.items():
     if sha(tar.extractfile('objects/'+digest).read())!=digest:raise ValueError('HOST_PACK_VERIFY')
   digest=sha(tmp.read_bytes());target=folder/(digest+'.tgz')
   if not target.exists():os.replace(tmp,target)
   if sha(target.read_bytes())!=digest:raise ValueError('HOST_PACK_TARGET_VERIFY')
   index=folder/(digest+'.index.json')
   if index.exists():
    previous=json.loads(index.read_text())['files']
    for name,value in aliases.items():
     if name in previous and previous[name]!=value:raise ValueError('HOST_PACK_ALIAS_CONFLICT')
    aliases={**previous,**aliases}
   body=dict(schema='hazardia.evidence-content-pack/1.0',archive=target.name,sha256=digest,files=aliases)
   temp_index=index.with_suffix('.tmp');temp_index.write_text(json.dumps(body,separators=(',',':')));os.replace(temp_index,index)
   # Original byte hashes were checked against completed host receipts and pack.
   # Recheck every source before removing any redundant direct copy.
   for path,expected in batch:
    if sha(path.read_bytes())!=expected:raise ValueError('HOST_EVIDENCE_CHANGED_BEFORE_COMPACT')
   for path,_ in batch:path.unlink()
   reports.append(dict(pack=target.name,files=len(batch),original_bytes=sum(v['bytes'] for v in aliases.values()),stored_bytes=target.stat().st_size+index.stat().st_size))
  finally:
   if tmp.exists():tmp.unlink()
 for path,digest in candidates(root):
  n=path.stat().st_size
  if n>MAX_BATCH:continue
  if batch and size+n>MAX_BATCH:flush(batch);batch=[];size=0
  batch.append((path,digest));size+=n
 flush(batch);return reports

def read_file(root,relative):
 root=Path(root)
 if Path(relative).is_absolute() or '..' in Path(relative).parts:raise ValueError('UNSAFE_EVIDENCE_PATH')
 direct=root/relative
 if direct.is_file():return direct.read_bytes()
 for index in sorted((root/'evidence-packs').glob('*.index.json'),key=lambda p:p.stat().st_mtime,reverse=True):
  meta=json.loads(index.read_text());entry=meta['files'].get(relative)
  if not entry:continue
  archive=index.parent/meta['archive']
  if sha(archive.read_bytes())!=meta['sha256']:raise ValueError('PACK_DIGEST')
  with tarfile.open(archive) as tar:body=tar.extractfile('objects/'+entry['sha256']).read()
  if len(body)!=entry['bytes'] or sha(body)!=entry['sha256']:raise ValueError('PACK_MEMBER_DIGEST')
  return body
 raise FileNotFoundError(relative)

def restore_file(root,relative,destination):
 body=read_file(root,relative);Path(destination).write_bytes(body);return dict(bytes=len(body),sha256=sha(body))
