"""Run only in the existing Linux geo environment. Import immutable evidence."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import box, shape, mapping
from shapely.ops import transform, unary_union
from hazardia.web.avalanche_layer import SCHEMA, validate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    source, output = Path(args.source), Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    def read(name):
        return json.loads((source / name).read_text())
    national = read('national-points.geojson')
    factors = read('factors.geojson')
    assessment = read('assessment.json')
    border = read('italy-boundary.geojson')
    country = unary_union([shape(f['geometry']) for f in border['features']])
    to_grid = Transformer.from_crs(4326, 3035, always_xy=True).transform
    to_wgs = Transformer.from_crs(3035, 4326, always_xy=True).transform
    country_grid = transform(to_grid, country)
    samples = {f['properties']['id']: f['properties'] for f in national['features']}
    if set(samples) != {f['properties']['id'] for f in factors['features']}:
        raise ValueError('Different national and factor sample IDs')
    features = []
    for f in factors['features']:
        p = dict(f['properties'])
        n = samples[p['id']]
        x = 4040000 + n['grid_col'] * 10000
        y = 2680000 - n['grid_row'] * 10000
        footprint = box(x, y - 10000, x + 10000, y).intersection(country_grid)
        if footprint.is_empty:
            raise ValueError('Empty national grid footprint')
        p.update(forecast_hs_cm=n['forecast_hs_cm'], aspect_deg=n['aspect_deg'],
                 initial_model_hs_m=n['initial_model_hs_m'],
                 grid_row=n['grid_row'], grid_col=n['grid_col'],
                 vegetation_status='NOT_INTEGRATED_NATIONALLY',
                 soil_substrate_status='NOT_INTEGRATED_NATIONALLY')
        features.append(dict(type='Feature', geometry=mapping(transform(to_wgs, footprint)), properties=p))
    data = dict(type='FeatureCollection', schema=SCHEMA, features=features, metadata=dict(
        product_id='avalanche-factors-20261029-01', reference_utc=assessment['reference_utc'],
        end_utc=assessment['end_utc'], weather_run_utc='2026-10-29T12:00:00Z',
        model='SNOWPACK 3.7.0 / MeteoIO 2.11.0', forecast='ICON-EU single run',
        grid_spacing_m=10000, geometry_meaning='10km sampling footprint clipped to Italy; not release area',
        initial_state='NWP snow depth; synthetic stratigraphy; no observed profiles assimilated',
        release_probability=None, hazard_grade=None, counts=assessment['counts'],
        factor_time_support='whole 72h; maxima may occur at different times',
        missing=['Observed weak layers and stability', 'Local wind transport and deposition',
                 'Basal water and snow-ground friction', 'National vegetation, soil and substrate integration',
                 'Validated release probability, runout, exposure and vulnerability'],
        terrain_selection='z>=600m OR z>=200m and 11km local relief>=300m; includes hills',
        sources=[dict(name='EAWS avalanche problems', href='https://www.avalanches.org/standards/avalanche-problems/'),
                 dict(name='National SNOWPACK run', id='italy-72h-20261029-01'),
                 dict(name='Factor assessment', id='avalanche-factors-20261029-01'),
                 dict(name='Italy boundary', credit='Eurostat GISCO 2024, 1:3M')]))
    validate(data)
    raw = json.dumps(data, allow_nan=False, separators=(',', ':')).encode()
    # Exclusive writes: imports never replace prior artifacts silently.
    with (output / 'layer.geojson').open('xb') as stream:
        stream.write(raw)
    manifest = dict(schema=SCHEMA, created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                    sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                    inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()})
    with (output / 'manifest.json').open('x') as stream:
        json.dump(manifest, stream, indent=2)
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
