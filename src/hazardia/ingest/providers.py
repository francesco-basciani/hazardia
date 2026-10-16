"""Concrete public STAC/history providers and an offline snapshot provider."""
from urllib.parse import urlencode
from hazardia.io import HazardError, load, write_new, timestamp

class StacProvider:
    def __init__(self, endpoint, cache):
        self.endpoint = endpoint.rstrip('/')
        self.cache = cache

    def search(self, collection, bbox, interval, label):
        query = dict(collections=collection, bbox=','.join(map(str,bbox)), limit=100)
        if interval is not None:
            query['datetime'] = interval
        receipt=self.cache.fetch(label, self.endpoint+'/search?'+urlencode(query))
        raw=load(self.cache.root/label)
        if raw.get('type')!='FeatureCollection' or not raw.get('features'):
            raise HazardError('SOURCE_EMPTY','No STAC features')
        return raw,receipt

    @staticmethod
    def choose_covering(items, bbox, cloud_limit=100):
        candidates=[]
        for item in items['features']:
            extent=item.get('bbox',[])
            if len(extent)!=4 or not (extent[0]<=bbox[0] and extent[1]<=bbox[1] and extent[2]>=bbox[2] and extent[3]>=bbox[3]):
                continue
            cloud=item.get('properties',{}).get('eo:cloud_cover',0)
            if cloud<=cloud_limit:
                candidates.append((cloud,item['id'],item))
        if not candidates:
            raise HazardError('SOURCE_COVERAGE','No full-bbox candidate')
        return min(candidates,key=lambda v:(v[0],v[1]))[2]

class OpenMeteoHistoryProvider:
    """Retrospective ERA5, never labeled an issued operational forecast."""
    def __init__(self, cache, endpoint='https://archive-api.open-meteo.com/v1/archive'):
        self.cache,self.endpoint=cache,endpoint

    def acquire(self, latitude, longitude, date, label='weather-history.json'):
        variables=['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m',
                   'wind_direction_10m','surface_pressure','shortwave_radiation']
        query=dict(latitude=latitude,longitude=longitude,start_date=date,end_date=date,
                   hourly=','.join(variables),timezone='UTC',wind_speed_unit='ms',models='era5')
        receipt=self.cache.fetch(label,self.endpoint+'?'+urlencode(query))
        raw=load(self.cache.root/label)
        if raw.get('utc_offset_seconds')!=0 or 'hourly' not in raw:
            raise HazardError('SOURCE_TIME','UTC hourly response required')
        expected=dict(temperature_2m='°C',relative_humidity_2m='%',precipitation='mm',
                      wind_speed_10m='m/s',wind_direction_10m='°',surface_pressure='hPa',shortwave_radiation='W/m²')
        units=raw.get('hourly_units',{})
        if any(units.get(k)!=v for k,v in expected.items()):
            raise HazardError('SOURCE_UNIT','Unexpected historical weather units')
        h=raw['hourly'];times=h.get('time',[])
        if len(times)!=24 or len(set(times))!=24 or any(len(h.get(k,[]))!=24 for k in variables):
            raise HazardError('SOURCE_TIME','Complete 24-hour snapshot required')
        records=[]
        for n,t in enumerate(times):
            at=t+':00Z'
            timestamp(at)
            values={k:h[k][n] for k in variables}
            if any(v is None for v in values.values()):
                raise HazardError('SOURCE_MISSING','Missing essential weather value')
            records.append(dict(at=at,values=values))
        return dict(schema_version='0.2.0',kind='weather',id='era5-'+date,
                    data_kind='REANALYSIS',issued_at=None,available_at=receipt['available_at'],
                    valid_from=records[0]['at'],valid_until=date+'T23:59:59Z',
                    original_timezone='UTC',member='era5',units=expected,accumulation_s=3600,
                    records=records,source=receipt,license='CC-BY-4.0',
                    caveats=['Retrospective reanalysis, not an issued forecast',
                             'First-seen availability recorded; no historical availability reconstructed',
                             'Grid-point weather is not a validated full-catchment forcing']),receipt

class LocalSnapshotProvider:
    def __init__(self, path):
        self.path=path
    def acquire(self):
        value=load(self.path)
        if not value.get('schema_version') or not value.get('kind'):
            raise HazardError('INVALID_INPUT','Versioned normalized snapshot required')
        return value
