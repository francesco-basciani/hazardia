"""Strict JSON and immutable byte identity; independent of scientific engines."""
import datetime as dt
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

class HazardError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')

def timestamp(value):
    if not isinstance(value, str) or not value.endswith('Z'):
        raise HazardError('INVALID_TIME', 'UTC timestamp with Z required')
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError as exc:
        raise HazardError('INVALID_TIME', str(exc)) from exc
    return parsed

def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise HazardError('INVALID_JSON', 'Duplicate key: ' + key)
        result[key] = value
    return result

def _constant(value):
    raise HazardError('INVALID_JSON', 'Nonfinite JSON value: ' + value)

def loads(raw):
    try:
        return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise HazardError('INVALID_JSON', str(exc)) from exc

def load(path):
    return loads(Path(path).read_text())

def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    # Readers never see partial JSON. Hard-link publication fails if target exists.
    fd, name = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        os.link(name, path)
    finally:
        os.unlink(name)

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def resolve_asset(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise HazardError('ASSET_PATH', 'Asset escapes snapshot root')
    return path

def verify_asset(root, asset):
    path = resolve_asset(root, asset['path'])
    if not path.is_file() or sha256(path) != asset['sha256']:
        raise HazardError('CHECKSUM', 'Missing or changed asset: ' + asset['path'])
    return path
