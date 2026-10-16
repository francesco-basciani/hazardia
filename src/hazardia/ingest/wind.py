"""Bounded regional wind display, distinct from simulator forcing.
315 requested nodes; explicit IDW resampling from returned model coordinates,
then client bilinear vector interpolation. No bearing-angle interpolation.
"""
import math
from urllib.parse import urlencode
from hazardia.ingest.forecast import ForecastStore
from hazardia.io import HazardError,timestamp
LATS=[round(41.6+i*.1,1) for i in range(15)]
LONS=[round(12.9+i*.1,1) for i in range(21)]
POINTS=[(lat,lon) for lat in LATS for lon in LONS]
UNITS={'wind_speed_10m':'m/s','wind_direction_10m':'°'}
URL='https://api.open-meteo.com/v1/forecast?'+urlencode(dict(latitude=','.join(str(p[0]) for p in POINTS),longitude=','.join(str(p[1]) for p in POINTS),hourly=','.join(UNITS),timezone='UTC',wind_speed_unit='ms',forecast_days=4,models='icon_eu',cell_selection='nearest',elevation=','.join(['nan']*len(POINTS))),safe=',')

def vector(speed,direction):
    a=math.radians(direction)
    return -speed*math.sin(a),-speed*math.cos(a)

def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)

def normalize(raw,receipt):
    if not isinstance(raw,list) or len(raw)!=len(POINTS):raise HazardError('SOURCE_MISSING','All315 regional wind nodes required')
    times=None;nodes=[];series=[];seen={}
    for index,(location,(lat,lon)) in enumerate(zip(raw,POINTS)):
        if not isinstance(location,dict) or location.get('utc_offset_seconds')!=0 or location.get('timezone') not in ['GMT','UTC']:raise HazardError('SOURCE_TIME','UTC wind nodes required')
        if 'location_id' in location and location['location_id']!=index:raise HazardError('SOURCE_POSITION','Unexpected location ordering')
        y,x=location.get('latitude'),location.get('longitude')
        if not finite(y) or not finite(x) or abs(y-lat)>.08 or abs(x-lon)>.08:raise HazardError('SOURCE_POSITION','Returned model node outside nearest-cell tolerance')
        h=location.get('hourly',{});ts=h.get('time',[])
        if location.get('hourly_units')!={'time':'iso8601',**UNITS}:raise HazardError('SOURCE_UNIT','Regional wind unit mismatch')
        if not isinstance(ts,list) or not 24<=len(ts)<=100 or (times is not None and ts!=times):raise HazardError('SOURCE_TIME','Complete common wind horizon required')
        if times is None:
            parsed=[timestamp(t+':00Z') for t in ts]
            if any((b-a).total_seconds()!=3600 for a,b in zip(parsed,parsed[1:])):raise HazardError('SOURCE_TIME','Wind hourly gap/duplicate')
            times=ts
        speeds=h.get('wind_speed_10m',[]);directions=h.get('wind_direction_10m',[])
        if len(speeds)!=len(times) or len(directions)!=len(times):raise HazardError('SOURCE_MISSING','Wind series incomplete')
        if any(not finite(s) or not 0<=s<=150 or not finite(d) or not 0<=d<=360 for s,d in zip(speeds,directions)):raise HazardError('SOURCE_RANGE','Missing/nonfinite/invalid regional wind')
        uv=[vector(s,d) for s,d in zip(speeds,directions)];key=(y,x)
        if key in seen:
            if series[seen[key]]!=uv:raise HazardError('SOURCE_CONFLICT','Duplicate model coordinates have differing wind')
        else:seen[key]=len(nodes);nodes.append(key);series.append(uv)
    # Four nearest distinct actual grid points, inverse-distance-squared weights.
    # Coordinates approximate local planar distances; no extrapolation beyond requested bbox.
    weights=[]
    for lat,lon in POINTS:
        ranked=sorted((( (y-lat)**2+((x-lon)*math.cos(math.radians(lat)))**2,i) for i,(y,x) in enumerate(nodes)))[:4]
        if ranked[0][0]<1e-14:weights.append([(ranked[0][1],1.)]);continue
        total=sum(1/d for d,_ in ranked);weights.append([(i,(1/d)/total) for d,i in ranked])
    records=[]
    for hour,t in enumerate(times):
        u=[round(sum(series[i][hour][0]*w for i,w in ws),4) for ws in weights]
        v=[round(sum(series[i][hour][1]*w for i,w in ws),4) for ws in weights]
        records.append(dict(at=t+':00Z',u=u,v=v))
    return dict(schema_version='0.1.0',kind='regional_wind_display',id='openmeteo-wind-'+receipt['sha256'][:24],data_kind='FORECAST',issued_at=None,issued_at_status='UNKNOWN_PROVIDER',available_at=receipt['available_at'],model='DWD ICON-EU via Open-Meteo',height_m=10,units='m/s',bounds=[[LATS[0],LONS[0]],[LATS[-1],LONS[-1]]],lats=LATS,lons=LONS,requested_nodes=len(POINTS),model_nodes=[list(n) for n in nodes],records=records,source=receipt,license='CC-BY-4.0',interpolation='IDW4 inverse-distance-squared on actual returned model coordinates to0.1deg display grid; bilinear U/V on client, no temporal interpolation',caveats=['Forecast not observations; unknown model initialization','Display sampling0.1deg about8–11km; underlying ICON-EU grid0.0625deg about7km','Bounding rectangle includes neighboring regions and sea; not an administrative region mask','Visual advection speed amplified; particles are not real air-parcel trajectories','Display only, not distributed forcing for physical simulators'])

class WindStore(ForecastStore):
    url=URL;ttl=10800;limit=8;cap=2*1024**2;cache_cap=64*1024**2;timeout=30
    normalizer=staticmethod(normalize)
    scope='Abruzzo rectangle315nodes/2variables/4days; free noncommercial; up to2520 location-call equivalents/day plus separate point forecast≤48/day'
    def snapshot(self):
        s=super().snapshot();s['quota'].update(location_equivalents_per_refresh=len(POINTS),max_location_equivalents_daily=self.limit*len(POINTS));return s
