"""Extend only the GSL22 forcing tail with the same public GFS cycle (VM only)."""
import datetime as dt,gzip,json,math,subprocess
from pathlib import Path
from hazardia_avalanche.worker import Refresh,atomic,parse,iso
from hazardia_avalanche.noaa_gfs import _fetch_frame,hourly_difference,bounded_percent

r=Path.home()/'avalanche-runtime';w=Path('/dev/shm/hs-repair-20261101/latest-inputs');w.mkdir(exist_ok=True)
old=json.loads(Path('/dev/shm/hs-pilot-20261101/protocol.json').read_text());point=old['point'];anchor=point['forcing_support']['source_point']
cycle=parse(old['weather_cycle_utc']);now=dt.datetime.now(dt.timezone.utc)
if not 0<=(now-cycle).total_seconds()<=12*3600:raise ValueError('ORIGINAL_CYCLE_NO_LONGER_FRESH')
service=Refresh(r,r/'local-assessment/control');cache=r/'local-assessment/noaa-gfs'/cycle.strftime('%Y%m%dT%H%MZ')
base=Path('/dev/shm/hs-pilot-20261101/original/local-native/NWP_INITIAL/forecast/input/GSL22.smet').read_text().splitlines();last=parse(base[-1].split()[0]).replace(tzinfo=dt.timezone.utc)
from hazardia_avalanche.hs_pilot import verified_product
observations,manifest=verified_product(Path.home()/'hazardia-runtime/web-assets/avalanche-snow-observations');station=next(s for s in observations['stations'] if s['id']=='campo-imperatore')
reference=parse(station['observed_at']);end=reference+dt.timedelta(hours=73)
count=int((end-last).total_seconds()/3600)
if not 0<count<=6:raise ValueError('TAIL_EXTENSION_LIMIT')
start_lead=int((last-cycle).total_seconds()/3600);frames={};sources={}
for lead in range(start_lead,start_lead+count+1):
 data,source=_fetch_frame(service,cache,cycle,lead,[anchor]);frames[lead]=data[anchor['id']];sources[source['sha256']]=source
rows=[]
for lead in range(start_lead+1,start_lead+count+1):
 c,prev=frames[lead],frames[lead-1]
 if c['missing_fields'] or prev['missing_fields']:raise ValueError('GFS_TAIL_MISSING')
 ta=c['temperature_2m'];rh=bounded_percent(c['relative_humidity_2m'])/100;sw=hourly_difference(c['radiation_mean'],prev['radiation_mean'],lead,'radiation');rain=hourly_difference(c['precip_accum'],prev['precip_accum'],lead,'precip');cloud=bounded_percent(c['cloud_cover'])/100
 if not -90<=ta<=60 or not 0<=rh<=1 or not 0<=sw<=1600 or not 0<=rain<=500:raise ValueError('TAIL_RANGE')
 lw=float(subprocess.check_output([str(r/'prefix/bin/current_ilwr')],input=f'{rh} {ta+273.15} {cloud}\n',text=True,timeout=5))
 at=cycle+dt.timedelta(hours=lead);u,v=c['u'],c['v'];values=[ta+273.15,rh,math.hypot(u,v),(math.degrees(math.atan2(-u,-v))+360)%360,sw,lw,rain,int(ta>=1.2),c['surface_temperature']+273.15]
 rows.append(at.strftime('%Y-%m-%dT%H:%M')+' '+' '.join(format(v,'.9g') for v in values))
(w/'future.smet').write_text('\n'.join(base+rows)+'\n')
atomic(w/'observations.json',station);atomic(w/'source-ledger.json',list(sources.values()));atomic(w/'receipt.json',dict(reference_utc=iso(reference),appended_hours=count,cycle_utc=iso(cycle),forecast_end_utc=iso(reference+dt.timedelta(hours=72)),observations_manifest=manifest,origin='FORECAST_GFS_TAIL_NOT_OBSERVED',no_altitude_adjustment=True))
print(json.dumps(json.loads((w/'receipt.json').read_text())))
