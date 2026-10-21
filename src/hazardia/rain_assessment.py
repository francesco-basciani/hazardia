"""Zonal forecast rainfall evidence; no universal rainfall-to-flood alert rule.

Executed by the existing geospatial VM worker. Equal-area intersections weight
one bilinearly interpolated value at each clipped weather-cell centroid. This
is a bounded quadrature of a coarse display field, not rainfall observations.
"""
import datetime as dt
from hazardia.io import timestamp

WINDOWS = (1, 3, 6, 12, 24, 48)

def assess(field, zones, at, sampling=None):
    import numpy as np
    from shapely.geometry import shape, box
    from shapely.ops import transform
    from pyproj import Transformer
    start = timestamp(at)
    if start.minute or start.second or start.microsecond:
        raise ValueError('Whole UTC forecast hour required')
    ys, xs = field['lats'], field['lons']
    if len(ys) != 9 or len(xs) != 9 or any(b <= a for v in (ys, xs) for a, b in zip(v, v[1:])):
        raise ValueError('Ordered 9x9 weather grid required')
    records = {r['at']: r for r in field['records']}
    project = Transformer.from_crs(4326, 6933, always_xy=True).transform
    domain = box(xs[0], ys[0], xs[-1], ys[-1])
    cells = [(i, j, box(xs[j], ys[i], xs[j+1], ys[i+1])) for i in range(8) for j in range(8)]
    def hour(t):
        row = records.get(t.isoformat().replace('+00:00', 'Z'))
        values = row.get('precipitation') if row else None
        if not isinstance(values, list) or len(values) != 81:
            return None
        a = np.asarray(values, dtype=float)
        return a if np.isfinite(a).all() and (a >= 0).all() else None
    hourly = [hour(start + dt.timedelta(hours=h)) for h in range(48)]
    past = [hour(start - dt.timedelta(hours=h)) for h in range(24, 0, -1)]
    features = []; sampling_out={}
    for feature in zones['features']:
        geo = shape(feature['geometry']); src = feature['properties']
        cached=sampling.get(src['id']) if sampling else None
        valid = geo.is_valid and not geo.is_empty and src.get('source_geometry_valid', True)
        p = dict(id=src['id'], name=src['name'], risk_status='NOT_EVALUABLE',
                 bounds_wgs84=list(geo.bounds),
                 missing=['Soglie locali attuali qualificate', 'Suolo/saturazione qualificati',
                          'Radar, pluviometri e idrometri', 'Modello di impatto validato'], windows={})
        samples = []
        if cached:
            if cached['geometry_valid']!=valid:raise ValueError('Sampling plan geometry mismatch')
            samples=cached['samples'];p['coverage_fraction']=cached['coverage_fraction']
        elif valid:
            area = transform(project, geo).area
            covered = geo.intersection(domain)
            p['coverage_fraction'] = min(1., transform(project, covered).area / area) if area else 0
            for i, j, cell in cells:
                cut = geo.intersection(cell)
                if cut.is_empty or cut.area == 0:
                    continue
                centre = cut.centroid
                dx = (centre.x-xs[j])/(xs[j+1]-xs[j]); dy = (centre.y-ys[i])/(ys[i+1]-ys[i])
                samples.append((i*9+j, dx, dy, transform(project, cut).area))
        else:
            p['coverage_fraction'] = 0
        sampling_out[src['id']]=dict(geometry_valid=valid,coverage_fraction=p['coverage_fraction'],samples=samples)
        complete = valid and p['coverage_fraction'] >= .999999 and bool(samples)
        p.update(spatial_status='COMPLETE' if complete else 'PARTIAL' if samples else 'UNAVAILABLE',
                 weather_cells=len(samples), geometry_valid=valid)
        def summary(rows):
            if not complete or any(r is None for r in rows):
                return dict(status='UNAVAILABLE', reason='Geometria della fonte non qualificata' if not valid else 'Copertura spaziale o intervallo orario incompleto')
            a = np.sum(rows, axis=0)
            values=[]
            for b,x,y,w in samples:
                v=a[b]*(1-x)*(1-y)+a[b+1]*x*(1-y)+a[b+9]*(1-x)*y+a[b+10]*x*y
                values.append((float(v),w))
            return dict(status='AVAILABLE', mean_mm=round(sum(v*w for v,w in values)/sum(w for v,w in values),3),
                        sampled_min_mm=round(min(v for v,w in values),3),sampled_max_mm=round(max(v for v,w in values),3))
        for hours in WINDOWS:
            p['windows'][str(hours)] = summary(hourly[:hours])
        # Same frozen field and spatial quadrature as the window summaries.
        # Keep missing hours separate: a missing observation is never dry weather.
        p['hourly_forecast'] = [dict(
            at=(start + dt.timedelta(hours=h)).isoformat().replace('+00:00', 'Z'),
            until=(start + dt.timedelta(hours=h+1)).isoformat().replace('+00:00', 'Z'),
            **summary([row])) for h, row in enumerate(hourly)]
        p['previous_24h_forecast'] = summary(past)
        # Previous values are forecasts from this same archive, never observed soil wetness.
        features.append(dict(type='Feature', geometry=feature['geometry'], properties=p))
    return dict(type='FeatureCollection', features=features, at=at, windows=list(WINDOWS),
                forecast_id=field['id'], forecast_available_at=field['available_at'],
                model=field['model'], source=field['source'], bounds=field['bounds'],
                grid_spacing_degrees=[ys[1]-ys[0],xs[1]-xs[0]],
                qualification='FORECAST_RAIN_EVIDENCE_NOT_FLOOD_ALERT',
                method='Equal-area weighted clipped-cell centroid bilinear quadrature; sampled extrema, not true local maxima',
                rain_semantics='Each precipitation record is the amount in the hour beginning at at; probability is not used as rainfall',
                threshold_status='CURRENT_LOCAL_THRESHOLDS_NOT_QUALIFIED',sampling_plan=sampling_out)

def main(request, output):
    from hazardia.io import load, write_new
    import gzip,hashlib,json
    r=load(request)
    with gzip.open(r['geometry_path'],'rb') as f:raw=f.read(8*1024**2+1)
    if len(raw)>8*1024**2 or hashlib.sha256(raw).hexdigest()!=r['geometry_sha256']:raise ValueError('Frozen geometry checksum mismatch')
    result=assess(r['field'],json.loads(raw),r['at'],r.get('sampling_plan'))
    # The response reattaches verified immutable shared geometry; no duplicate archive per hour.
    for feature in result['features']:feature['geometry']=None
    result.update(attention_snapshot=r['attention_snapshot'], geometry_sha256=r['geometry_sha256'],
                  geometry_day=r['geometry_day'], assessment_id=r['assessment_id'], official=r['official'])
    write_new(output,result)

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
