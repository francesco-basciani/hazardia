"""Read-only, checksummed SNOWPACK snapshot. No model execution or acquisition."""
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

SCHEMA = 'hazardia.avalanche-screening/1.0'
MAX_BYTES = 16 * 1024 * 1024


def freshness(meta, now):
    end = dt.datetime.fromisoformat(meta['end_utc'].replace('Z', '+00:00'))
    reference = dt.datetime.fromisoformat(meta['reference_utc'].replace('Z', '+00:00'))
    cycle = dt.datetime.fromisoformat(meta.get('weather_run_utc', meta['reference_utc']).replace('Z', '+00:00'))
    if now > end:
        return 'EXPIRED'
    if reference > now + dt.timedelta(minutes=5):
        return 'FUTURE_REFERENCE_INVALID'
    if now-reference > dt.timedelta(hours=9) or now-cycle > dt.timedelta(hours=12):
        return 'STALE'
    return 'CURRENT_MODEL_ESTIMATE'


def record_supervisor_failure(runtime, code):
    path = Path(runtime) / 'avalanche/supervisor-error.json'
    path.write_text(json.dumps(dict(code=code, at=dt.datetime.now(dt.timezone.utc).isoformat())))


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Invalid avalanche snapshot object')
    if data.get('type') != 'FeatureCollection' or data.get('schema') != SCHEMA:
        raise ValueError('Invalid avalanche snapshot schema')
    meta = data['metadata']
    start = dt.datetime.fromisoformat(meta['reference_utc'].replace('Z', '+00:00'))
    end = dt.datetime.fromisoformat(meta['end_utc'].replace('Z', '+00:00'))
    if end - start != dt.timedelta(hours=72) or start.tzinfo is None:
        raise ValueError('Invalid snapshot horizon')
    if meta['release_probability'] is not None or meta['hazard_grade'] is not None:
        raise ValueError('Unqualified probability or danger grade')
    features = data['features']
    if not 1 <= len(features) <= 10000:
        raise ValueError('Invalid bounded feature count')
    ids = set()
    for f in features:
        p = f['properties']
        if p['id'] in ids or f['geometry']['type'] not in ('Polygon', 'MultiPolygon'):
            raise ValueError('Duplicate sample or invalid footprint')
        ids.add(p['id'])
        if p['release_probability'] is not None or p['hazard_grade'] is not None:
            raise ValueError('Unqualified sample probability')
        c = p['factor_class']
        if type(c) is not int or c not in range(5):
            raise ValueError('Unknown factor category')
        if c == 0:
            if p['forecast_hs_cm'] is not None or p['status'] != 'UNKNOWN_MODEL_OUTPUT':
                raise ValueError('Missing model output replaced by a value')
        else:
            hs = p['forecast_hs_cm']
            if not isinstance(hs, list) or len(hs) != 4 or any(type(v) not in (int, float) or not 0 <= v <= 10000 for v in hs):
                raise ValueError('Invalid modeled snow depth')
            steep = p['slope_deg'] >= 30
            load = p['max_net_swe_increase_kg_m2'] > .001
            wet = p['liquid_water_max_kg_m2'] > .001
            expected = 4 if steep and load and wet else 3 if steep and load else 2 if steep and wet else 1
            if c != expected:
                raise ValueError('Factor category inconsistent with physical indicators')
    if meta['counts']['total_points'] != len(features) or meta['counts']['missing_physical_output'] != sum(f['properties']['factor_class'] == 0 for f in features):
        raise ValueError('Inconsistent snapshot counts')
    return data


class Snapshot:
    def __init__(self, runtime):
        self.directory = Path(runtime) / 'avalanche'

    def read(self):
        manifest = json.loads((self.directory / 'manifest.json').read_text())
        # Fixed filenames: no path or URL from the manifest or HTTP request is executed.
        digest = manifest['sha256']
        if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest):
            raise ValueError('Invalid snapshot digest')
        # New delivery: one atomic manifest references an immutable content object.
        path = self.directory / 'objects' / (digest + '.geojson')
        if not path.exists():
            path = self.directory / 'layer.geojson'  # legacy frozen snapshot
        if path.stat().st_size > MAX_BYTES:
            raise ValueError('Snapshot exceeds bounded size')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest['sha256']:
            raise ValueError('Snapshot checksum mismatch')
        self.digest = digest
        return validate(json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON'))))

    def response(self, now=None):
        data = self.read()
        now = now or dt.datetime.now(dt.timezone.utc)
        meta = data['metadata']
        end = dt.datetime.fromisoformat(meta['end_utc'].replace('Z', '+00:00'))
        meta['delivery_status'] = 'EXPIRED_SNAPSHOT' if now > end else 'FROZEN_FORECAST_SNAPSHOT'
        meta['served_at'] = now.isoformat()
        meta['automatic_refresh'] = False
        for observation in meta.get('observations', []):
            if observation.get('id') == 'T0169':
                observation['quality_note'] = 'Grostè: discordanza sensore/EO del 29 ottobre non risolta; nessuna nuova verifica satellitare in questo ciclo'
        meta['freshness_status'] = freshness(meta, now)
        meta['forecast_age_hours'] = round((now-dt.datetime.fromisoformat(meta['reference_utc'].replace('Z', '+00:00'))).total_seconds()/3600, 2)
        config = self.directory.parent / 'avalanche-auto-config.json'
        if config.exists():
            meta['automatic_refresh'] = json.loads(config.read_text()) == {'enabled': True}
        state = self.directory / 'auto-state.json'
        data['pipeline'] = json.loads(state.read_text()) if state.exists() and state.stat().st_size < 65536 else dict(status='NOT_CONFIGURED')
        if meta['automatic_refresh']:
            meta['delivery_status'] = meta['freshness_status']
            heartbeat = data['pipeline'].get('heartbeat_at')
            if heartbeat and now-dt.datetime.fromisoformat(heartbeat.replace('Z', '+00:00')) > dt.timedelta(minutes=45):
                data['pipeline']['status'] = 'WORKER_HEARTBEAT_STALE'
            error = self.directory / 'supervisor-error.json'
            if error.exists():
                record = json.loads(error.read_text())
                if not heartbeat or record['at'] > heartbeat:
                    data['pipeline']['status'] = record['code']
        data['version'] = self.digest
        from hazardia.web.avalanche_potential import enrich
        return enrich(data,self.directory)
