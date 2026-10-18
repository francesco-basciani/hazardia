"""Spatial hourly atmosphere and explicitly uncalibrated fine-litter moisture model.
Independent implementation of Van Wagner1977 hourly moisture balance (PS-X-69),
including rain wetting equations Van Wagner/Pickett1985. Not RISICO or field moisture.
"""
import math

def hourly_moisture(previous,temp,rh,wind_kmh,rain_mm):
 import numpy as np
 m=np.asarray(previous,dtype=np.float64);t=np.asarray(temp);h=np.asarray(rh);w=np.asarray(wind_kmh);rain=np.asarray(rain_mm)
 if not all(np.isfinite(a).all() for a in [m,t,h,w,rain]) or ((h<0)|(h>100)).any() or (w<0).any() or (rain<0).any():raise ValueError('Invalid fuel moisture forcing')
 wet=m+42.5*rain*np.exp(-100/(251-m))*(-np.expm1(-6.93/np.maximum(rain,1e-12)))+np.where(m>150,.0015*(m-150)**2*np.sqrt(rain),0)
 m=np.where(rain>0,np.minimum(250,wet),m)
 common=.18*(21.1-t)*(1-np.exp(-.115*h));dry=.942*h**.679+11*np.exp((h-100)/10)+common;humid=.618*h**.753+10*np.exp((h-100)/10)+common
 rate=lambda fraction:(.424*(1-fraction**1.7)+.0694*np.sqrt(w)*(1-fraction**8))*.0579*np.exp(.0365*t)
 dried=dry+(m-dry)*10**(-rate(h/100));wetted=humid-(humid-m)*10**(-rate((100-h)/100))
 return np.clip(np.where(m>dry,dried,np.where(m<humid,wetted,m)),0,250).astype('float32')

class SpatialForcing:
 def __init__(self,grid,field):
  import numpy as np
  from pyproj import Transformer,Proj
  from affine import Affine
  from hazardia.io import HazardError
  self.field=field;n,m=grid['shape'];tr=Affine(*grid['transform']);cols,rows=np.meshgrid(np.arange(m)+.5,np.arange(n)+.5);x=tr.c+cols*tr.a;y=tr.f+rows*tr.e;lon,lat=Transformer.from_crs(grid['crs'],4326,always_xy=True).transform(x,y);ys=field['lats'];xs=field['lons']
  if lat.min()<ys[0] or lat.max()>ys[-1] or lon.min()<xs[0] or lon.max()>xs[-1]:raise HazardError('SOURCE_MISSING','Distributed forecast does not cover model domain')
  gx=(lon-xs[0])/(xs[1]-xs[0]);gy=(lat-ys[0])/(ys[1]-ys[0]);ix=np.minimum(len(xs)-2,np.floor(gx).astype(int));iy=np.minimum(len(ys)-2,np.floor(gy).astype(int));self.base=iy*len(xs)+ix;self.width=len(xs);self.dx=(gx-ix).astype('float32');self.dy=(gy-iy).astype('float32');self.convergence=Proj(grid['crs']).get_factors(lon,lat).meridian_convergence
 def sample(self,record,key):
  import numpy as np
  a=np.asarray(record[key],dtype=np.float32);b=self.base;dx=self.dx;dy=self.dy;n=self.width
  out=a[b]*(1-dx)*(1-dy)+a[b+1]*dx*(1-dy)+a[b+n]*(1-dx)*dy+a[b+n+1]*dx*dy
  if not np.isfinite(out).all():raise ValueError('Missing distributed atmosphere')
  return out
 def wind(self,record,change=None):
  import numpy as np
  u=self.sample(record,'u');v=self.sample(record,'v');speed=np.hypot(u,v)*3.6;direction=(np.degrees(np.arctan2(-u,-v))+360)%360
  if change:speed=np.full_like(speed,change['speed_ms']*3.6);direction=np.full_like(direction,change['direction_deg'])
  return speed.astype('float32'),((direction-self.convergence)%360).astype('float32')
