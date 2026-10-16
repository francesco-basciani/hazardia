"""Small real forecast wind input transformation, run only in VM geo environment."""
import argparse,platform
import numpy as np
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True);p.add_argument('--speed-kmh',type=float,required=True);p.add_argument('--direction',type=float,required=True);a=p.parse_args()
if platform.system()!='Linux':raise SystemExit('Run only in the Linux VM')
if not np.isfinite(a.speed_kmh) or a.speed_kmh<0 or not np.isfinite(a.direction) or not 0<=a.direction<=360:raise SystemExit('Invalid forecast wind')
if Path(a.output).exists():raise SystemExit('Refusing overwrite')
with np.load(a.source,allow_pickle=False) as s:
    dem=s['dem'];veg=s['veg'];np.savez(a.output,dem=dem,veg=veg,wind_speed_kmh=np.full_like(dem,a.speed_kmh),wind_dir_deg=np.full_like(dem,a.direction))
print('Forecast wind staged from m/s to km/h; terrain/fuel unchanged; no humidity-to-fuel-moisture conversion')
