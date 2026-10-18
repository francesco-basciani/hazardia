"""VM-only point pilot: antecedent weather sensitivity, never a production fuel map."""
import argparse,datetime as dt,json,math,sys
from pathlib import Path

def assess(raw,start):
 from hazardia.fire_forcing import hourly_moisture
 if raw.get('timezone') not in ['GMT','UTC'] or raw.get('utc_offset_seconds')!=0:raise ValueError('UTC provider response required')
 units=raw.get('hourly_units',{});expected={'time':'iso8601','temperature_2m':'°C','relative_humidity_2m':'%','wind_speed_10m':'m/s','precipitation':'mm'}
 if units!=expected:raise ValueError('Unexpected provider units')
 h=raw['hourly'];times=[dt.datetime.fromisoformat(t).replace(tzinfo=dt.timezone.utc) for t in h['time']];begin=dt.datetime.fromisoformat(start.replace('Z','+00:00'))
 if begin.utcoffset()!=dt.timedelta(0) or begin.minute or begin.second or begin.microsecond:raise ValueError('Whole-hour UTC ignition required')
 if any((b-a).total_seconds()!=3600 for a,b in zip(times,times[1:])):raise ValueError('Hourly gap')
 for key in expected:
  if len(h[key])!=len(times):raise ValueError('Incomplete provider series')
  if key!='time' and any(type(v) not in [float,int] or not math.isfinite(v) for v in h[key]):raise ValueError('Missing weather')
 selected=[i for i,t in enumerate(times) if begin-dt.timedelta(hours=168)<=t<begin]
 if len(selected)!=168 or times[selected[0]]!=begin-dt.timedelta(hours=168):raise ValueError('Complete168h antecedent window required')
 histories=[]
 for code in [65,85,95]:
  moisture=147.2*(101-code)/(59.5+code);trace=[]
  for i in selected:
   # Provider precipitation is accumulated over the preceding hour: i+1 is
   # the completed rainfall for interval [times[i],times[i]+1h]. Never use i+2.
   if i+1>=len(times):raise ValueError('Missing rain interval end')
   moisture=float(hourly_moisture(moisture,h['temperature_2m'][i],h['relative_humidity_2m'][i],h['wind_speed_10m'][i]*3.6,h['precipitation'][i+1]));trace.append(moisture)
  histories.append(dict(initial_ffmc_assumption=code,initial_moisture_percent=147.2*(101-code)/(59.5+code),at_ignition_percent=moisture,trace_percent=trace))
 return dict(schema='fire-initialization-assessment/1',qualification='POINT_PILOT_NOT_SPATIAL_FUEL_MAP_NOT_CALIBRATED',start=start,antecedent_hours=168,provider_model_position=[raw['latitude'],raw['longitude']],provider_elevation_m=raw.get('elevation'),method='HFFMC_1977 existing estimator;168h antecedent weather; initial codes65/85/95 fixed before acquisition',legacy_reset_percent=147.2*(101-85)/(59.5+85),initialization_spread_at_ignition_pp=max(r['at_ignition_percent'] for r in histories)-min(r['at_ignition_percent'] for r in histories),histories=histories,limitations=['Recent archived forecast is not a weather-station observation','Single provider model point cannot initialize the whole spatial domain','Fuel type, seasonal curing, moisture and suppression efficacy uncalibrated','No native fire result or operational skill follows from this assessment'])

def main():
 if sys.platform!='linux':raise RuntimeError('Run inside the Linux VM')
 ap=argparse.ArgumentParser();ap.add_argument('--raw',required=True);ap.add_argument('--start',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();p=Path(a.output)
 if p.exists():raise FileExistsError('Evidence already exists; no overwrite')
 result=assess(json.loads(Path(a.raw).read_text()),a.start);p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='histories'},indent=2))
if __name__=='__main__':main()
