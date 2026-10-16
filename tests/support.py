"""Synthetic metadata/byte fixtures for supervisor tests; never real-engine evidence."""
from pathlib import Path
from hazardia.io import write_new,sha256

def fixture(root):
    root=Path(root);root.mkdir(exist_ok=True)
    (root/'dem.tif').write_bytes(b'SYNTHETIC UNIT TEST BYTES, NOT A RASTER')
    (root/'arrays.npz').write_bytes(b'SYNTHETIC UNIT TEST BYTES, NOT ARRAYS')
    units={'precipitation':'mm','wind_speed_10m':'m/s','wind_direction_10m':'°','temperature_2m':'°C','relative_humidity_2m':'%','surface_pressure':'hPa','shortwave_radiation':'W/m²'}
    values={'precipitation':0,'wind_speed_10m':2,'wind_direction_10m':90,'temperature_2m':20,'relative_humidity_2m':50,'surface_pressure':1000,'shortwave_radiation':100}
    weather=dict(schema_version='0.2.0',kind='weather',id='unit-weather',data_kind='REANALYSIS',issued_at=None,available_at='2024-07-13T00:00:00Z',valid_from='2024-07-13T00:00:00Z',valid_until='2024-07-13T23:59:59Z',units=units,records=[dict(at=f'2024-07-13T{hour:02}:00:00Z',values=values.copy()) for hour in range(24)],source={'source':'unit test'},license='SYNTHETIC')
    write_new(root/'weather.json',weather)
    assets=[dict(role=role,path=path,sha256=sha256(root/path)) for role,path in [('dem','dem.tif'),('weather','weather.json'),('fire_arrays','arrays.npz')]]
    request=dict(schema_version='0.2.0',kind='simulation_request',id='unit-fixture',hazard='FIRE',mode='RESEARCH_RETROSPECTIVE',territory=dict(id='synthetic',region='SYNTHETIC_TEST',bbox_wgs84=[13,42,14,43],work_crs='EPSG:32633',timezone='Europe/Rome',calibration='UNKNOWN',complete_catchment=False),grid=dict(shape=[2,3],crs='EPSG:32633',vertical_datum='SYNTHETIC',transform=[30,0,500000,0,-30,4700000],nodata=-9999),snapshot_at='2024-07-14T00:00:00Z',valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-13T13:10:00Z',assets=assets,assumptions=['UNIT TEST ONLY, NO PHYSICAL MODEL'],options=dict(duration_s=600,realizations=2,seed=1729,ignition=[1,1],moisture_percent=10,fuel_legacy=5),timeout_s=1,max_log_bytes=1024*1024)
    return request,weather
