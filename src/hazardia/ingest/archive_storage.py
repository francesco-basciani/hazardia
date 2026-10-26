"""Lossless bounded archive storage. Preserve decoded bytes and every logical name."""
import gzip
import hashlib
import os
from pathlib import Path
from hazardia.io import HazardError


def read_bytes(path,limit=32*1024**2):
    path=Path(path)
    try:
        with path.open('rb') as stream:data=stream.read(limit+1)
    except FileNotFoundError:
        try:
            with gzip.open(str(path)+'.gz','rb') as stream:data=stream.read(limit+1)
        except (OSError,EOFError) as exc:
            raise HazardError('CACHE_CORRUPT','Archive unavailable or invalid') from exc
    if len(data)>limit:raise HazardError('CACHE_CORRUPT','Archive expansion limit exceeded')
    return data


def stored_bytes(root):
    """Count shared immutable inodes once; aliases still resolve to identical bytes."""
    seen=set();size=0
    for path in Path(root).rglob('*'):
        if not path.is_file():continue
        stat=path.stat();key=(stat.st_dev,stat.st_ino)
        if key not in seen:seen.add(key);size+=stat.st_size
    return size


def compact(paths):
    """Compress only JSON; verify any existing representation before removing raw."""
    for path in paths:
        path=Path(path)
        raw=read_bytes(path);packed=gzip.compress(raw,mtime=0);target=Path(str(path)+'.gz')
        if len(packed)>=len(raw):continue
        if target.exists():
            if read_bytes(target.with_suffix(''))!=raw or gzip.decompress(target.read_bytes())!=raw:
                raise HazardError('CACHE_CORRUPT','Conflicting archive representation')
        else:
            temp=Path(str(target)+'.tmp');temp.write_bytes(packed);temp.replace(target)
        with gzip.open(target,'rb') as stream:decoded=stream.read(len(raw)+1)
        if decoded!=raw:raise HazardError('CACHE_CORRUPT','Archive compaction differs')
        path.unlink()


def deduplicate(paths):
    """Share bytes of immutable files, preserving paths and checking hash + bytes."""
    seen={};count=0
    for path in paths:
        path=Path(path)
        if not path.is_file():continue
        stat=path.stat();raw=path.read_bytes();key=(stat.st_size,hashlib.sha256(raw).digest())
        other=seen.get(key)
        if other is None:seen[key]=path;continue
        if other.stat().st_ino==stat.st_ino:continue
        if other.read_bytes()!=raw:raise HazardError('CACHE_CORRUPT','Archive hash collision')
        temp=Path(str(path)+'.dedup-tmp')
        os.link(other,temp)
        try:os.replace(temp,path)
        finally:
            if temp.exists():temp.unlink()
        count+=1
    return count
