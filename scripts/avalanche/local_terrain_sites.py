"""Preregistered <=24 stratified local columns; terrain is not a snow observation."""
import pathlib,json,gzip,hashlib,datetime,collections
import numpy as np,rasterio
from rasterio.features import shapes
from shapely.geometry import shape,mapping,box
from shapely.ops import unary_union,transform
from pyproj import Transformer,Geod
root=pathlib.Path('/dev/shm/avalanche-terrain-build');out=root/'output';base=root/'experiments';gs=base/'combined-terrain-20261029-01/results';terrain=base/'terrain-20261029-01'
with rasterio.open(gs/'land_cover.tif') as ds:cover=ds.read(1);aff=ds.transform;crs=ds.crs
with rasterio.open(gs/'combined_zone.tif') as ds:zones=ds.read(1)
with rasterio.open(terrain/'slope.tif') as ds:slope=ds.read(1)
with rasterio.open(terrain/'elevation.tif') as ds:elevation=ds.read(1)
with rasterio.open(terrain/'aspect.tif') as ds:aspect=ds.read(1)
valid=(zones>0)&(slope>=30)&(aspect>=0)&np.isin(cover,[30,60]);altband=np.digitize(elevation,[2200,2600]);direction=((aspect+45)%360//90).astype(np.int32);group=np.where(valid,cover.astype(np.int32)*100+altband*4+direction,-1)
towgs=Transformer.from_crs(crs,4326,always_xy=True).transform;to3035=Transformer.from_crs(crs,3035,always_xy=True);back=Transformer.from_crs(3035,4326,always_xy=True).transform;sites=[];bygroup={}
for n,g in enumerate(sorted(np.unique(group[valid])),1):
 rr,cc=np.where(group==g);order=np.argsort(elevation[rr,cc],kind='stable');k=order[len(order)//2];r,c=int(rr[k]),int(cc[k]);x,y=aff*(c+.5,r+.5);lon,lat=towgs(x,y);site=dict(id='GSL'+str(n).zfill(2),lat=lat,lon=lon,elevation_m=float(elevation[r,c]),slope_deg=float(slope[r,c]),aspect_deg=float(aspect[r,c]),cover_code=int(cover[r,c]),altitude_band=int(altband[r,c]),aspect_quadrant=int(direction[r,c]),support='One synthetic snow column representative of cover/elevation/aspect stratum; not forecast30m',local_profile=True);sites.append(site);bygroup[int(g)]=site
assert len(sites)<=24
protocol=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),selection='Median-altitude eligible pixel per cover(30grass/60bare)×altitude(<2200/2200–2600/>=2600)×aspect90deg quadrant; slope>=30; no profile selected by model outcome',max_sites=24,sites=sites,snow_initialization='NWP HS, synthetic uniform -1C rho300; no observed profile or soil friction inferred',mapping='Same stratum and distance<=5km; otherwise retain explicit national-column fallback',physics='NativeSNOWPACK; no friction coefficient or risk weights from soil/grass')
(out/'local-sites.json').write_text(json.dumps(sites,indent=2));(out/'local-protocol.json').write_text(json.dumps(protocol,indent=2))
context=json.loads(gzip.decompress((out/'terrain-context.json.gz').read_bytes()));parents=json.loads(pathlib.Path('/home/hazardia/avalanche-runtime/seed.geojson').read_text())['features'];pindex={p['properties']['id']:i+1 for i,p in enumerate(parents)};yy,xx=np.indices(zones.shape);px,py=to3035.transform(aff.c+(xx+.5)*aff.a,aff.f+(yy+.5)*aff.e);gr=((2680000-py)//10000).astype(int);gc=((px-4040000)//10000).astype(int);par=np.zeros(zones.shape,np.int32)
for i,f in enumerate(parents,1):
 p=f['properties']
 if gr.min()<=p['grid_row']<=gr.max() and gc.min()<=p['grid_col']<=gc.max():par[(gr==p['grid_row'])&(gc==p['grid_col'])]=i
oldlabels=zones.astype(np.int32)*4096+par;labels=oldlabels*12+altband*4+direction;lookup={int(f['properties']['id'][3:]):f for f in context['features'] if f['properties']['id'].startswith('GS-')};groups=collections.defaultdict(list)
for geometry,code in shapes(labels.astype(np.int32),mask=valid&(par>0),transform=aff):groups[int(code)].append(shape(geometry))
new=[];geod=Geod(ellps='WGS84');bbox=box(13.49,42.4,13.64,42.52)
for code,geoms in groups.items():
 original=lookup.get(code//12)
 if not original:continue
 p=dict(original['properties']);mask=(labels==code)&valid;g=int(np.unique(group[mask])[0]);site=bygroup[g];r,c=np.argwhere(mask)[len(np.argwhere(mask))//2];x,y=aff*(float(c)+.5,float(r)+.5);lon,lat=towgs(x,y);distance=geod.inv(lon,lat,site['lon'],site['lat'])[2];geometry=transform(towgs,unary_union(geoms).simplify(5,preserve_topology=True)).intersection(bbox)
 if geometry.is_empty:continue
 p.update(id='GSX-'+str(code),slope_min_deg=float(slope[mask].min()),slope_max_deg=float(slope[mask].max()),elevation_min_m=float(elevation[mask].min()),elevation_max_m=float(elevation[mask].max()),local_sample_id=site['id'] if distance<=5000 else None,local_profile_distance_m=distance,local_profile_support='Synthetic representative, same cover/elevation/aspect stratum; not a local measured snow profile')
 new.append(dict(type='Feature',geometry=mapping(geometry),properties=p))
remove={int(code//12) for code in groups};context['features']=[f for f in context['features'] if not(f['properties']['id'].startswith('GS-') and int(f['properties']['id'][3:]) in remove)]+new
context['metadata'].update(local_sites_count=len(sites),local_sites_rule=protocol['selection'],local_profiles_are_observed=False,local_representative_max_distance_m=5000)
raw=json.dumps(context,separators=(',',':'),allow_nan=False).encode();digest=hashlib.sha256(raw).hexdigest()
with gzip.open(out/'terrain-context-local.json.gz','wb') as stream:stream.write(raw)
manifest=json.loads((out/'terrain-manifest.json').read_text());manifest.update(sha256=digest,bytes=len(raw),compressed_bytes=(out/'terrain-context-local.json.gz').stat().st_size,features=len(context['features']),metadata=context['metadata'],local_sites_builder_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest());(out/'terrain-manifest-local.json').write_text(json.dumps(manifest,indent=2));print('LOCAL SITES',len(sites),'AREAS',len(context['features']),'BYTES',len(raw),flush=True)
