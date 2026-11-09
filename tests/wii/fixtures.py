import copy
from wii.datasets import scientific_source


def source():
    return scientific_source('manual-test','Synthetic test source','manual://test',regions=['IT-65'],
        bounds=[12,41,15,44],license_uri='SYNTHETIC_TEST',attribution='SYNTHETIC TEST',method='MANUAL',category='manual')


def event(doc,ident='e1',geometry=None):
    return dict(id=ident,type='WILDFIRE',start='2024-07-13T00:00:00Z',end='2024-07-14T00:00:00Z',
        time_precision='DAY',status='REPORTED',source_id=doc['source_id'],document_id=doc['id'],
        available_at=doc['available_at'],location=dict(kind='REPORTED_LOCATION',
        geometry=geometry or dict(type='Point',coordinates=[13.4,42.3]),precision='POINT_REPORTED',
        uncertainty='Synthetic report only',verification=None),attributes={})


def product(lam=.7):
    return dict(schema='hazardia.wii.probability/0.1.0',id='synthetic-probability',model_id='synthetic-model',
        issue_at='2026-10-24T00:00:00Z',available_at='2026-10-24T00:00:01Z',valid_from='2026-10-25T00:00:00Z',
        valid_until='2026-10-26T00:00:00Z',crs='EPSG:3035',cell_size_m=1000,
        cells=[dict(id='c',x=4400000,y=2200000,area_km2=1,mu=lam,p=-__import__('math').expm1(-lam),features=[])],
        calibration=dict(status='EXPERIMENTAL_UNCALIBRATED',evidence=None,limitations='SYNTHETIC SOFTWARE TEST ONLY'),
        provenance=dict(mask_geometry=dict(type='Polygon',coordinates=[[[4400000,2200000],[4401000,2200000],
            [4401000,2201000],[4400000,2201000],[4400000,2200000]]])),
        definition='P_AT_LEAST_ONE_WILDFIRE_IGNITION_PER_CELL_INTERVAL',process='CONDITIONAL_INDEPENDENT_POISSON')
