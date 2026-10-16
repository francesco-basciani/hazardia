"""Bounded HTTPS acquisition and hash-verified offline reuse."""
import json
import os
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit
from hazardia.io import HazardError, load, sha256, utcnow, write_new

class Cache:
    def __init__(self, root, budget_bytes=384*1024**2):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.budget = budget_bytes

    def fetch(self, label, url, *, cap=4*1024**2, refresh=False):
        if not label or Path(label).name != label or label.startswith('.'):
            raise HazardError('INVALID_INPUT', 'Safe cache label required')
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise HazardError('SOURCE_URL', 'Credential-free HTTPS source required')
        data = self.root/label
        record = self.root/(label+'.source.json')
        tic = time.monotonic()
        if record.exists():
            meta = load(record)
            if meta['url'] != url or not data.is_file() or sha256(data) != meta['sha256']:
                raise HazardError('CACHE_CORRUPT', 'Cached URL or bytes differ')
            if refresh:
                raise HazardError('IMMUTABLE_CACHE', 'Use a new label/snapshot for a revision')
            return dict(meta, cache_hit=True, elapsed_s=time.monotonic()-tic)
        if data.exists():
            raise HazardError('INCOMPLETE_CACHE', 'Unregistered source bytes; use another snapshot')
        used = sum(load(p).get('bytes', 0) for p in self.root.glob('*.source.json'))
        allowance = min(cap, self.budget-used)
        if allowance <= 0:
            raise HazardError('DOWNLOAD_BUDGET', 'Source budget exhausted')
        start = utcnow()
        request = urllib.request.Request(url, headers={'User-Agent':'HAZARDIA-M1/0.1 public research', 'Accept-Encoding':'identity'})
        pending = self.root/(label+'.partial')
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                if int(response.headers.get('Content-Length', '0')) > allowance:
                    raise HazardError('DOWNLOAD_BUDGET', 'Declared source payload exceeds allowance')
                size=0
                with pending.open('xb') as out:
                    while True:
                        block = response.read(min(1024*1024, allowance-size+1))
                        if not block:
                            break
                        size += len(block)
                        if size > allowance:
                            raise HazardError('DOWNLOAD_BUDGET', 'Streaming source cap exceeded')
                        out.write(block)
                    out.flush();os.fsync(out.fileno())
                meta=dict(url=url, final_url=response.url, status=response.status,
                          fetched_at=start, available_at=utcnow(), bytes=size,
                          sha256=sha256(pending), headers={k:v for k,v in response.headers.items()
                          if k.lower() in ('content-type','content-length','etag','last-modified')})
            os.link(pending,data)
            write_new(record,meta)
            return dict(meta, cache_hit=False, elapsed_s=time.monotonic()-tic)
        except HazardError:
            raise
        except Exception as exc:
            raise HazardError('SOURCE_UNAVAILABLE', str(exc)) from exc
        finally:
            pending.unlink(missing_ok=True)
