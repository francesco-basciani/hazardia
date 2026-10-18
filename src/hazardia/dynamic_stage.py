"""Build versioned native requests from immutable dynamic terrain and distributed weather."""
import copy,datetime as dt,json,shutil,sys
from pathlib import Path
from hazardia.io import load,write_new,sha256,HazardError,utcnow,timestamp
from hazardia.firelab import validate

def stage(root,folder):
 import numpy as np
 from pyproj import Transformer
 from rasterio.transform import Affine
 from shapely.geometry import Polygon,LineString
 root=Path(root);folder=Path(folder);body=validate(load(folder/'body.json'));ref=load(folder/'terrain.json');terrain=Path(ref['path'])
 if sha256(terrain/'manifest.json')!=ref['sha256']:raise HazardError('CHECKSUM','Dynamic terrain manifest differs')
 tm=load(terrain/'manifest.json');g=load(terrain/'grid.json');tr=Affine(*g['transform']);project=Transformer.from_crs(4326,g['crs'],always_xy=True)
 def cell(p):
  x,y=project.transform(p[1],p[0]);c,r=(~tr)*(x,y)
  if not 2<=r<g['shape'][0]-2 or not 2<=c<g['shape'][1]-2:raise HazardError('DOMAIN_SPAN','Event outside ignition-centred domain; nearby intervention or separate simulation required')
  return int(r),int(c)
 for i in body['ignitions']:cell(i['point'])
 for u in body['resources']:
  points=u.get('line',u.get('area'));coords=[project.transform(p[1],p[0]) for p in points]
  for p in points:cell(p)
  geom=LineString(coords) if 'line' in u else Polygon(coords)
  if not geom.is_valid or geom.is_empty or 'line' in u and not 1<=geom.length<=50000 or 'area' in u and not 1<=geom.area<=250000000:raise HazardError('INVALID_INPUT','Invalid or oversized intervention geometry')
 with np.load(terrain/'expanded-arrays.npz',allow_pickle=False) as a:
  dem=a['dem'];veg=a['veg']
  if any(veg[cell(i['point'])]==0 for i in body['ignitions']):raise HazardError('NO_BURNABLE_FUEL','Ignition on built-up, water, snow or bare surface in ESA WorldCover2021; move explicitly to vegetation')
  initial={}
  if body.get('antecedent_hours',0):
   from hazardia.fire_forcing import initialize_moisture
   history=load(folder/'antecedent.json');initial['initial_moisture']=initialize_moisture(g,history,body['start_at'])
  np.savez_compressed(folder/'arrays.npz',dem=dem,veg=veg,wind_speed_kmh=np.zeros_like(dem),wind_dir_deg=np.zeros_like(dem),**initial)
 shutil.copyfile(terrain/'dem.tif',folder/'dem.tif');field=load(folder/'field.json');start=timestamp(body['start_at']);rows=[]
 p=body['ignitions'][0]['point'];ys=field['lats'];xs=field['lons'];gx=(p[1]-xs[0])/(xs[1]-xs[0]);gy=(p[0]-ys[0])/(ys[1]-ys[0]);ix=min(7,int(gx));iy=min(7,int(gy));dx=gx-ix;dy=gy-iy;index=iy*9+ix
 if not 0<=gx<=8 or not 0<=gy<=8:raise HazardError('SOURCE_MISSING','Ignition outside distributed weather')
 def value(r,key):
  a=r[key];return a[index]*(1-dx)*(1-dy)+a[index+1]*dx*(1-dy)+a[index+9]*(1-dx)*dy+a[index+10]*dx*dy
 for h in range(body['hours']):
  at=(start+dt.timedelta(hours=h)).isoformat().replace('+00:00','Z');r=next(r for r in field['records'] if r['at']==at);u,v=value(r,'u'),value(r,'v')
  values=dict(wind_speed_10m=(u*u+v*v)**.5,wind_direction_10m=(__import__('math').degrees(__import__('math').atan2(-u,-v))+360)%360,temperature_2m=value(r,'temperature'),relative_humidity_2m=value(r,'humidity'),precipitation=value(r,'precipitation'),surface_pressure=value(r,'pressure'),shortwave_radiation=value(r,'radiation'));rows.append(dict(at=at,values=values))
 weather=dict(schema_version='0.3.0',kind='weather',data_kind='FORECAST',issued_at=None,issued_at_status='UNKNOWN_PROVIDER',available_at=field['available_at'],valid_from=rows[0]['at'],valid_until=(start+dt.timedelta(hours=body['hours'])).isoformat().replace('+00:00','Z'),units=dict(wind_speed_10m='m/s',wind_direction_10m='°',temperature_2m='°C',relative_humidity_2m='%',precipitation='mm',surface_pressure='hPa',shortwave_radiation='W/m²'),records=rows,source=field['source'],license='CC BY4.0 Open-Meteo',distributed_field=field)
 if body.get('antecedent_hours',0):weather['antecedent_field']=history
 write_new(folder/'weather.json',weather);raw=root/'web-state/map-weather'/('raw-'+field['source']['sha256']+'.json')
 if sha256(raw)!=field['source']['sha256']:raise HazardError('CHECKSUM','Provider response changed')
 shutil.copyfile(raw,folder/'raw.json');changes={c['hour']:c for c in body['weather_changes']};records=[]
 for h,row in enumerate(rows):
  values=copy.deepcopy(row['values'])
  if h in changes:values.update(wind_speed_10m=changes[h]['speed_ms'],wind_direction_10m=changes[h]['direction_deg'])
  records.append(dict(time=h*3600,at=row['at'],values=values))
 plan=dict(case='B',ignition_wgs84=body['ignitions'][0]['point'],ignitions_wgs84=body['ignitions'],weather_source='FORECAST',records=records,resources=body['resources'],action_times=sorted(set(int(u['at_minutes']*60) for u in body['resources'])),weather_changes=body['weather_changes'],qualification='UNQUALIFIED_RESEARCH',moisture_percent=body['moisture_percent'],comparison_times=body.get('comparison_times',[]),forcing=dict(version='distributed/1',terrain_id=tm['id'],field_id=field['id'],moisture_model=body.get('moisture_model','HFFMC_1977'),initial_ffmc=85,field_sha256=sha256(folder/'field.json'),landcover_crosswalk=g['crosswalk']))
 if body.get('antecedent_hours',0):plan['forcing'].update(version='distributed/2',initialization=dict(method='SPATIAL_HFFMC_168H',hours=168,field_id=history['id'],range_percent=[float(initial['initial_moisture'].min()),float(initial['initial_moisture'].max())],qualification='ESTIMATED_NOT_MEASURED'))
 write_new(folder/'plan.json',plan);req=dict(kind='simulation_request',hazard='FIRE',territory=dict(calibration='UNKNOWN',complete_catchment=False),grid=dict(vertical_datum='EGM2008_DSM_UNQUALIFIED',nodata=-9999),options=dict(fuel_legacy=5));req.update(schema_version='0.4.0',id=folder.name,valid_from=rows[0]['at'],valid_until=weather['valid_until'],snapshot_at=utcnow(),mode='RESEARCH_FORECAST',timeout_s=900,max_log_bytes=1048576)
 req['territory'].update(id='terrain-'+tm['id'][:24],region='User-selected territory',bbox_wgs84=tm['bbox_wgs84'],work_crs=g['crs'],timezone='UTC');req['grid'].update(shape=g['shape'],crs=g['crs'],transform=g['transform']);req['options'].update(duration_s=body['hours']*3600,seed=body['seed'],realizations=body.get('realizations',2),ignition=list(cell(body['ignitions'][0]['point'])),moisture_percent=body['moisture_percent'])
 req['assets']=[dict(role=role,path=name,sha256=sha256(folder/name)) for role,name in [('dem','dem.tif'),('fire_arrays','arrays.npz'),('weather','weather.json'),('weather_raw','raw.json'),('fire_plan','plan.json')]]
 req['assumptions']=['Real ignition-centred Copernicus DSM GLO30 and ESA WorldCover2021, versioned research fuel crosswalk; no uniform synthetic vegetation','Spatial hourly DWD ICON10m wind; bilinear u/v on native model grid, meridian convergence accounted for; no street-scale forecast skill','Fuel moisture HFFMC1977 estimated from temperature/RH/wind/rain, initial FFMC85 assumed unless explicit manual moisture selected; uncalibrated coupling, not RISICO','Hourly precipitation for following hour applied to moisture only at next hour; no future rain leakage','Research ideal fuel removal by authored resources; no certified category efficacy, dispatch, logistics or field validity','Domain prepared internally around ignitions, bounded30km; domain exit is a classified failure, not silent clipping']
 if body.get('antecedent_hours',0):req['assumptions']+=['Spatial168h antecedent ICON forecast initialization, not station measurements; residual initial-state/model/fuel uncertainty remains']
 from hazardia.contracts import validate_request
 validate_request(req,folder);write_new(folder/'request.json',req)
if __name__=='__main__':stage(Path(sys.argv[1]),Path(sys.argv[2]))
