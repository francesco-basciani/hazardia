"""Public MeteoHub hourly rain observations; no forecast substitution or area inference.

Uses the same anonymous GET and CC-BY group as the provider's public map.
POST extraction, authenticated endpoints and non-CC-BY datasets are never used.
"""
import datetime as dt
import gzip
import hashlib
import json
import math
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = 'https://meteohub.agenziaitaliameteo.it'
MAX_BYTES = 2 * 1024**2
DOWNLOAD_BUDGET = 64 * 1024**2
REFRESH_SECONDS = 3600
FRESH_SECONDS = 5400
UTC = dt.timezone.utc


def iso(value):
    return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')


def parse_time(value):
    # Provider public map explicitly appends Z to its offset-free UTC ref values.
    if not isinstance(value, str):
        raise ValueError('Invalid observation time')
    t = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    return t.replace(tzinfo=UTC) if t.tzinfo is None else t.astimezone(UTC)


def normalize(payload, catalog, acquired):
    """Keep only documented, attributable CC BY 4.0 hourly water equivalents."""
    if payload.get('descr', {}).get('B13011', {}).get('unit') != 'KG/M**2':
        raise ValueError('Unexpected precipitation unit')
    if not isinstance(payload.get('data'), list) or len(payload['data']) > 10000:
        raise ValueError('Invalid station collection')
    networks = {x['id']: x for x in catalog if x.get('category') == 'OBS'
                and x.get('is_public') is True and x.get('license') == 'CCBY4.0'
                and x.get('group_license') == 'CCBY_COMPLIANT'
                and x.get('attribution') and x.get('license_url') == 'https://creativecommons.org/licenses/by/4.0/legalcode'}
    result = {}; rejected = 0
    for item in payload['data']:
        try:
            stat = item['stat']; network = networks[stat['net']]
            lat, lon = stat['lat'], stat['lon']
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in (lat, lon)) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError('Coordinates')
            name = next(x['val'] for x in stat['details'] if x['var'] == 'B01019')
            if not isinstance(name, str) or not name.strip() or len(name) > 250:
                raise ValueError('Station name')
            observations = []
            for product in item['prod']:
                if product['var'] != 'B13011' or product.get('trange', '1,0,3600') != '1,0,3600' or product.get('lev', '1,0,0,0') != '1,0,0,0':
                    continue
                for value in product['val']:
                    mm = value.get('val'); end = parse_time(value.get('ref'))
                    if type(mm) not in (int, float) or not math.isfinite(mm) or mm < 0 or type(value.get('rel')) is not int or value.get('rel') != 1:
                        continue
                    if end > acquired or end < acquired - dt.timedelta(hours=3):
                        continue
                    observations.append((end, mm))
            if not observations:
                raise ValueError('No reliable recent observation')
            end, mm = max(observations)
            key = hashlib.sha256(json.dumps([stat['net'], lat, lon, name]).encode()).hexdigest()[:20]
            feature = dict(type='Feature', geometry=dict(type='Point', coordinates=[lon, lat]), properties=dict(
                id=key, name=name, network=stat['net'], network_name=network['name'],
                network_description=network['description'], attribution=network['attribution'],
                attribution_description=network.get('attribution_description', network['attribution']),
                license='CC BY 4.0', license_url=network['license_url'],
                from_at=iso(end-dt.timedelta(hours=1)), until=iso(end), mm=mm,
                quantity='hourly_total_water_equivalent_mm', provider_reliability=1,
                qualification='UNVALIDATED_OBSERVATION'))
            if key not in result or result[key]['properties']['until'] < feature['properties']['until']:
                result[key] = feature
        except (KeyError, TypeError, ValueError, StopIteration):
            rejected += 1
    return dict(type='FeatureCollection', features=sorted(result.values(), key=lambda f: f['properties']['id']),
                rejected_rows=rejected, acquired_at=iso(acquired),
                provider='ItaliaMeteo / MeteoHub · reti indicate per stazione',
                source_url=BASE+'/app/maps/observations',
                method='B13011; timerange 1,0,3600; level 1,0,0,0; last=true; reliabilityCheck=true; CC BY compliant. 1 kg/m² di acqua = 1 mm. Accumulo nell’ora precedente il timestamp; può includere neve equivalente.',
                missing=['Copertura delle stazioni discontinua; nessuna stima areale',
                         'Dati provvisori non validati; assenza di sensori non significa assenza di pioggia',
                         'Rete regionale Abruzzo non presente nel catalogo pubblico verificato; presenti altre reti, anche amatoriali',
                         'Nessuna soglia di allerta o correzione automatica dei modelli derivata da queste misure'])


class ObservedRainStore:
    def __init__(self, root):
        self.root = Path(root); self.root.mkdir(exist_ok=True)
        self.lock = threading.Lock(); self.busy = False; self.cache = None

    def _read(self, name, default=None):
        path = self.root/name
        return json.loads(path.read_bytes()) if path.exists() else default

    def _write(self, name, value):
        path = self.root/name; tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(value, allow_nan=False)); tmp.replace(path)

    def _get(self, url, ledger):
        # Reserve maximum bytes before I/O, including failed/truncated requests.
        if ledger['reserved_bytes'] + MAX_BYTES > DOWNLOAD_BUDGET:
            raise ValueError('Budget di acquisizione osservazioni esaurito (64 MiB); nessun nuovo download')
        ledger['reserved_bytes'] += MAX_BYTES; self._write('ledger.json', ledger)
        req = urllib.request.Request(url, headers={'User-Agent': 'HAZARDIA-research/1 observed-rain (public-map GET)', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(MAX_BYTES+1)
            if len(raw) > MAX_BYTES:
                raise ValueError('Risposta oltre il limite di 2 MiB')
            if 'application/json' not in response.headers.get('Content-Type', ''):
                raise ValueError('Formato sorgente inatteso')
        ledger['reserved_bytes'] -= MAX_BYTES-len(raw); self._write('ledger.json', ledger)
        return raw

    def refresh(self):
        """Asynchronous, one shared request/hour at most, no download on map movement."""
        with self.lock:
            ledger = self._read('ledger.json', dict(reserved_bytes=0, last_attempt=0))
            if self.busy:
                return dict(status='RUNNING')
            if time.time() - ledger['last_attempt'] < REFRESH_SECONDS:
                return dict(status='CACHED', next_refresh_at=iso(dt.datetime.fromtimestamp(ledger['last_attempt']+REFRESH_SECONDS, UTC)))
            ledger['last_attempt'] = time.time(); self._write('ledger.json', ledger); self.busy = True
        def work():
            try:
                now = dt.datetime.now(UTC); catalog = self._read('catalog.json')
                if not catalog or (now-parse_time(catalog['acquired_at'])).total_seconds() >= 86400:
                    raw = self._get(BASE+'/api/datasets?licenceSpecs=true', ledger)
                    catalog = dict(data=json.loads(raw), acquired_at=iso(now), sha256=hashlib.sha256(raw).hexdigest())
                    self._write('catalog.json', catalog)
                    catalog_path=self.root/('catalog-'+catalog['sha256']+'.json.gz')
                    if not catalog_path.exists():catalog_path.write_bytes(gzip.compress(raw, mtime=0))
                end = now.replace(minute=0, second=0, microsecond=0); start = end-dt.timedelta(hours=2)
                q = f'reftime: >={start:%Y-%m-%d %H:%M},<={end:%Y-%m-%d %H:%M};product:B13011;license:CCBY_COMPLIANT;timerange:1,0,3600;level:1,0,0,0'
                url = BASE+'/api/observations?'+urllib.parse.urlencode(dict(q=q, last='true', reliabilityCheck='true'))
                raw = self._get(url, ledger); acquired = dt.datetime.now(UTC)
                data = normalize(json.loads(raw), catalog['data'], acquired)
                digest = hashlib.sha256(raw).hexdigest(); key = 'observed-'+digest[:24]
                data.update(id=key, raw_sha256=digest, catalog_sha256=catalog['sha256'], request_url=url)
                # Bounded immutable receipts; never silently delete old scientific snapshots.
                if len(list(self.root.glob('observed-*.json.gz'))) >= 64:
                    raise ValueError('Archivio osservazioni pieno (64 snapshot); aggiornamento sospeso')
                path = self.root/(key+'.json.gz')
                if not path.exists():
                    path.write_bytes(gzip.compress(raw, mtime=0))
                    self._write(key+'.receipt.json', data)
                self._write('latest.json', data)
                self._write('state.json', dict(error=None, last_success_at=iso(acquired)))
            except Exception as exc:
                self._write('state.json', dict(error=type(exc).__name__+': '+str(exc)[:220]))
            finally:
                with self.lock:
                    self.busy = False
        threading.Thread(target=work, name='observed-rain', daemon=True).start()
        return dict(status='ACCEPTED')

    def snapshot(self):
        now = dt.datetime.now(UTC); path=self.root/'latest.json'
        stamp=path.stat().st_mtime_ns if path.exists() else None
        if self.cache and self.cache[0]==stamp:data=self.cache[1]
        else:
            data=self._read('latest.json');self.cache=(stamp,data)
        state = self._read('state.json', {})
        if not data:
            return dict(status='MISSING', busy=self.busy, error=state.get('error'), data=None)
        features = []; networks = {}
        network_fields={'network_name','network_description','attribution','attribution_description','license','license_url'}
        for original in data['features']:
            p=original['properties'];networks[p['network']]={k:v for k,v in p.items() if k in network_fields}
            feature = dict(original, properties={k:v for k,v in p.items() if k not in network_fields})
            age = (now-parse_time(feature['properties']['until'])).total_seconds()
            feature['properties'].update(age_minutes=round(age/60, 1), freshness='FRESH' if 0<=age<=FRESH_SECONDS else 'STALE')
            features.append(feature)
        fresh = sum(f['properties']['freshness']=='FRESH' for f in features)
        age = (now-parse_time(data['acquired_at'])).total_seconds()
        return dict(status='FRESH' if 0<=age<=FRESH_SECONDS and fresh else 'STALE', busy=self.busy,
                    error=state.get('error'), data=dict(data, features=features, networks=networks), fresh_stations=fresh,
                    budget=self._read('ledger.json', {}))
