"""Bounded live OSM context for an actually prepared fire domain, never population."""
import json,hashlib,urllib.request,time
from pathlib import Path
from hazardia.io import load,write_new,utcnow,HazardError,sha256
URL='https://overpass.private.coffee/api/interpreter'
def acquire(root,terrain_id,bounds):
 root=Path(root);key=hashlib.sha256(json.dumps(bounds).encode()).hexdigest()[:16];dest=root/'terrain-cache'/terrain_id/('priority-'+key+'.json')
 if dest.exists():return load(dest)
 count=root/'web-state/priority-requests';count.mkdir(exist_ok=True)
 if len(list(count.glob(time.strftime('%Y%m%d',time.gmtime())+'-*')))>=10:raise HazardError('SOURCE_QUOTA','Limite gratuito locale per nuove aree OSM raggiunto')
 import uuid
 write_new(count/(time.strftime('%Y%m%d',time.gmtime())+'-'+uuid.uuid4().hex+'.json'),dict(at=utcnow(),bounds=bounds))
 x0,y0,x1,y1=bounds;box=f'{y0},{x0},{y1},{x1}'
 query=f'[out:json][timeout:18];(nwr[amenity~"^(hospital|school|fire_station)$"]({box});way[landuse=residential]({box});node[place~"^(city|town|village|hamlet)$"]({box}););out center geom 1200;'
 from urllib.parse import urlencode
 request=urllib.request.Request(URL+'?'+urlencode({'data':query}),headers={'User-Agent':'HAZARDIA-research/0.1'})
 try:
  with urllib.request.urlopen(request,timeout=15) as r:data=r.read(2*1024**2+1)
 except Exception as error:
  result=builtup(root,terrain_id,bounds,str(error));write_new(dest,result);return result
 if len(data)>2*1024**2:raise HazardError('SOURCE_BUDGET','Mapped priority response over2MiB')
 raw=json.loads(data);elements=raw.get('elements',[])
 if raw.get('remark'):raise HazardError('SOURCE_MISSING','OSM query incomplete: '+raw['remark'])
 features=[]
 for element in elements:
  tags=element.get('tags',{});center=element.get('center',element);lat=center.get('lat');lon=center.get('lon')
  if lat is None or lon is None:continue
  category={'hospital':'hospital','school':'school','fire_station':'fire_station'}.get(tags.get('amenity'),'residential' if tags.get('landuse')=='residential' else 'settlement')
  geometry=dict(type='Point',coordinates=[lon,lat]);vertices=element.get('geometry',[])
  if tags.get('landuse')=='residential' and 4<=len(vertices)<=2000 and vertices[0]==vertices[-1]:geometry=dict(type='Polygon',coordinates=[[[p['lon'],p['lat']] for p in vertices]])
  features.append(dict(type='Feature',id=f'osm-{element["type"]}-{element["id"]}',geometry=geometry,properties=dict(name=tags.get('name',category+' OSM'),category=category)))
 result=dict(type='FeatureCollection',features=features,coverage_bbox_wgs84=bounds,source_url=URL,source_sha256=hashlib.sha256(data).hexdigest(),available_at=utcnow(),missing=['Population','Vulnerability','Incomplete OSM inventory','Points for assets without mapped polygon geometry'],qualification='MAPPED_POINTS_NOT_SATELLITE_DETECTION',truncated_possible=len(elements)>=1200)
 write_new(dest.with_name('priority-'+key+'-raw.json'),raw);write_new(dest,result);return result

def builtup(root,terrain_id,bounds,error):
 """Class50 polygons from actual WorldCover; unknown use/population, not OSM features."""
 import numpy as np
 from rasterio.features import shapes
 from rasterio.transform import Affine
 from rasterio.warp import transform_bounds
 from pyproj import Transformer
 from shapely.geometry import shape,mapping,box
 from shapely.ops import transform
 terrain=Path(root)/'terrain-cache'/terrain_id;g=load(terrain/'grid.json');tr=Affine(*g['transform']);back=Transformer.from_crs(g['crs'],4326,always_xy=True).transform;project=Transformer.from_crs(4326,g['crs'],always_xy=True).transform
 with np.load(terrain/'expanded-arrays.npz',allow_pickle=False) as a:cover=a['landcover'];mask=cover==50
 xmin,ymin,xmax,ymax=transform_bounds(4326,g['crs'],*bounds,densify_pts=12);c0,r1=(~tr)*(xmin,ymin);c1,r0=(~tr)*(xmax,ymax);roi=np.zeros(mask.shape,bool);roi[max(0,int(r0)):min(mask.shape[0],int(r1)+1),max(0,int(c0)):min(mask.shape[1],int(c1)+1)]=True;mask&=roi;features=[]
 for geom,value in shapes(mask.astype('uint8'),mask=mask,transform=tr,connectivity=8):
  poly=shape(geom)
  if not poly.is_valid:poly=poly.buffer(0)
  if poly.is_empty or poly.area<2700:continue
  features.append(dict(type='Feature',id='builtup-'+str(len(features)+1),geometry=mapping(transform(back,poly.simplify(15,preserve_topology=True))),properties=dict(name='Area edificata · WorldCover2021',category='settlement',source='ESA WorldCover2021 class50; use/occupancy unknown')))
 features=sorted(features,key=lambda f:shape(f['geometry']).area,reverse=True)[:200]
 return dict(type='FeatureCollection',features=features,coverage_bbox_wgs84=bounds,source_url='https://esa-worldcover.org/en/data-access',source_sha256=sha256(terrain/'expanded-arrays.npz'),available_at=load(terrain/'manifest.json')['available_at'],missing=['OSM unavailable: '+error,'Population','Building use, hospitals and schools unavailable','WorldCover2021 may omit changes after2021'],qualification='SATELLITE_CLASSIFIED_BUILTUP_UNCALIBRATED',truncated_possible=len(features)>=200)
