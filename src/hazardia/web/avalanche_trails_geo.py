"""Linux geospatial worker for mapped trails: intersection is not a safety judgement."""
import json,hashlib,gzip,pathlib,datetime,argparse,collections,math,os,re

def parse_trails(data):
 if data.get('remark'):raise ValueError('INCOMPLETE_OVERPASS_RESPONSE')
 elements=data.get('elements');assert isinstance(elements,list) and len(elements)<=25000
 routes=collections.defaultdict(list)
 for item in elements:
  tags=item.get('tags',{})
  if item.get('type')=='relation' and tags.get('type')=='route' and tags.get('route') in ('hiking','foot'):
   route={k:tags.get(k) for k in ('ref','name','operator','network','cai_scale','osmc:symbol')};route['osm_relation_id']=item['id']
   for member in item.get('members',[]):
    if member.get('type')=='way':routes[member['ref']].append(route)
 features=[];missing=0
 for item in elements:
  if item.get('type')!='way':continue
  tags=item.get('tags',{});ident=item['id']
  if type(ident) is not int or ident<=0:missing+=1;continue
  if tags.get('highway') not in ('path','footway','steps','bridleway') and ident not in routes:continue
  if tags.get('area')=='yes' and ident not in routes:continue
  parts=[];part=[]
  for point in item.get('geometry',[]):
   if isinstance(point,dict) and all(type(point.get(k)) in (int,float) and math.isfinite(point[k]) for k in ('lon','lat')) and -180<=point['lon']<=180 and -90<=point['lat']<=90:
    q=[point['lon'],point['lat']]
    if not part or part[-1]!=q:part.append(q)
   else:
    if len(part)>1:parts.append(part)
    part=[];missing+=1
  if len(part)>1:parts.append(part)
  if not parts:missing+=1;continue
  attrs={k:str(tags[k])[:500] if k in tags else None for k in ('name','ref','highway','sac_scale','cai_scale','trail_visibility','surface','access','foot','access:conditional','foot:conditional','check_date','survey:date','operator')}
  attrs.update(osm_way_id=ident,osm_url='https://www.openstreetmap.org/way/'+str(ident),routes=routes[ident],cai_label_declared=bool(tags.get('cai_scale') or re.search(r'\bCAI\b|Club Alpino Italiano',str(tags.get('operator','')),re.I) or any(re.search(r'\bCAI\b|Club Alpino Italiano',str(p.get('operator','')),re.I) for p in routes[ident])),cai_certification_verified=False,passability_verified=False)
  features.append(dict(type='Feature',geometry=dict(type='MultiLineString',coordinates=parts),properties=attrs))
 if len(features)>12000:raise ValueError('TOO_MANY_TRAILS_REDUCE_AREA')
 return features,dict(missing_geometry_parts=missing,ways=len(features),route_relations=sum(e.get('type')=='relation' for e in elements))

def line_parts(g):
 if g.is_empty:return []
 if g.geom_type=='LineString':return [g] if g.length>.01 else []
 return [line for part in getattr(g,'geoms',[]) for line in line_parts(part)]

def partition_line(line,potential,near,unknown,coverage):
 """Disjoint positive-length pieces; a point contact does not fabricate a segment."""
 result=[];remaining=line
 for label,mask in [('POTENTIAL_INTERSECTION',potential),('PROXIMITY_ONLY',near),('DATA_UNCERTAIN',unknown),('NO_SELECTED_INTERSECTION',coverage)]:
  hit=remaining.intersection(mask)
  result.extend((label,part) for part in line_parts(hit));remaining=remaining.difference(mask)
 result.extend(('OUTSIDE_ASSESSMENT',part) for part in line_parts(remaining));return result

def analyze(runtime,source,receipt,output):
 os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj')
 import resource
 resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
 from shapely.geometry import shape,box,mapping,GeometryCollection
 from shapely.ops import transform,unary_union,clip_by_rect
 from shapely.strtree import STRtree
 from pyproj import Transformer
 from hazardia.web.avalanche_layer import Snapshot
 runtime=pathlib.Path(runtime);rec=json.loads(pathlib.Path(receipt).read_text());raw=gzip.decompress(pathlib.Path(source).read_bytes());assert hashlib.sha256(raw).hexdigest()==rec['sha256'];trails,quality=parse_trails(json.loads(raw));data=Snapshot(runtime).response();forward=Transformer.from_crs(4326,3035,always_xy=True).transform;back=Transformer.from_crs(3035,4326,always_xy=True).transform;area=box(*rec['bounds']);aoi=transform(forward,area);region=aoi.buffer(250);coarse_region=transform(back,region);groups=collections.defaultdict(list);missing_reasons=set()
 for f in data['potential_areas']:
  g=shape(f['geometry'])
  if not g.intersects(coarse_region):continue
  g=transform(forward,g)
  if not g.is_valid:g=g.buffer(0)
  g=g.intersection(region)
  if g.is_empty:continue
  p=f['properties'];code=p['potential_class'];groups['coverage'].append(g)
  if code>=3:groups['potential'].append(g)
  elif code in (0,2):groups['unknown'].append(g)
  if code>=3:missing_reasons.update(p.get('potential_missing',[]))
 indexes={k:STRtree(groups[k]) if groups[k] else None for k in ('coverage','potential','unknown')};segments=[];ways={};counts=collections.Counter();lengths=collections.Counter();contact_count=0
 def local_mask(kind,line,margin):
  tree=indexes[kind]
  if tree is None:return GeometryCollection()
  w,s,e,n=line.bounds;bounds=(w-margin,s-margin,e+margin,n+margin);pieces=[]
  for polygon in tree.query(box(*bounds)):
   clipped=clip_by_rect(polygon,*bounds)
   if not clipped.is_valid:clipped=clipped.buffer(0)
   if not clipped.is_empty:pieces.append(clipped)
  return unary_union(pieces) if pieces else GeometryCollection()
 for f in trails:
  g=transform(forward,shape(f['geometry'])).intersection(aoi)
  if g.is_empty:continue
  p=f['properties'];way_id=p['osm_way_id'];totals=collections.Counter();masks=dict(potential=local_mask('potential',g,251),unknown=local_mask('unknown',g,1),coverage=local_mask('coverage',g,1));near=masks['potential'].buffer(250);pieces=partition_line(g,masks['potential'],near,masks['unknown'],masks['coverage']);contact=g.intersection(masks['potential']);touch=not line_parts(contact) and not contact.is_empty;contact_count+=touch
  by_kind=collections.defaultdict(list)
  for kind,line in pieces:by_kind[kind].append(line)
  for n,(kind,parts) in enumerate(by_kind.items()):
   from shapely.geometry import MultiLineString
   line=MultiLineString(parts) if len(parts)>1 else parts[0]
   props=dict(p,segment_id=str(way_id)+'-'+str(n),classification=kind,parts_count=len(parts),length_m=float(line.length),proximity_distance_m=250 if kind=='PROXIMITY_ONLY' else None,has_uncertain_snow_or_model=line.intersects(masks['unknown']),boundary_only_contact=touch,qualification='CARTOGRAPHIC_SCREENING_NOT_PASSABILITY_OR_AVALANCHE_RUNOUT',release_probability=None,safe_route=None)
   segments.append(dict(type='Feature',geometry=mapping(transform(back,line)),properties=props));totals[kind]+=line.length;counts[kind]+=1;lengths[kind]+=line.length
  ways[way_id]=dict(osm_way_id=way_id,name=p.get('name'),ref=p.get('ref'),routes=p['routes'],lengths_m={k:round(v,1) for k,v in totals.items()})
  if len(segments)>40000:raise ValueError('TOO_MANY_SEGMENTS_REDUCE_AREA')
 metadata=dict(bounds=rec['bounds'],source='© OpenStreetMap contributors · ODbL-1.0',source_url=rec['url'],license_url='https://www.openstreetmap.org/copyright',source_sha256=rec['sha256'],source_acquired_at=rec['at'],osm_base=rec.get('osm_base'),source_quality=quality,source_complete_not_guaranteed=True,cai_source_status='OSM route labels only, no independent INFOMONT validation',cai_reference_url='https://infomont.cai.it',forecast_version=data['version'],native_version=data['native_version'],reference_utc=data['metadata']['reference_utc'],end_utc=data['metadata']['end_utc'],weather_run_utc=data['metadata']['weather_run_utc'],proximity_search_m=250,proximity_is_runout=False,runout_assessed=False,passability_assessed=False,critical_missing=sorted(missing_reasons),counts=dict(counts),lengths_m={k:round(v,1) for k,v in lengths.items()},ways=len(ways),segments=len(segments),boundary_contact_ways=contact_count,created_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 product=dict(type='FeatureCollection',schema='hazardia.avalanche-trails/1.0',features=segments,metadata=metadata,ways=list(ways.values()));out=json.dumps(product,separators=(',',':'),allow_nan=False).encode();assert len(out)<=32*1024**2
 path=pathlib.Path(output);temporary=path.with_suffix('.tmp')
 with gzip.open(temporary,'wb') as stream:stream.write(out)
 temporary.replace(path);print(json.dumps(dict(ways=len(ways),segments=len(segments),counts=dict(counts),bytes=len(out))))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--runtime',required=True);parser.add_argument('--source',required=True);parser.add_argument('--receipt',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();analyze(args.runtime,args.source,args.receipt,args.output)
