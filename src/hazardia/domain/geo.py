"""Geospatial leaf reader in the existing geo environment; no simulator imports."""
import math
import rasterio
from rasterio.warp import transform
from hazardia.io import timestamp,verify_asset,sha256
from hazardia.contracts import validate_product
from hazardia.domain.contracts import validate_record,require

def exposed_points(product,request,root,exposures,*,at,as_of):
    validate_product(product,request,root);p=product
    require(timestamp(p['valid_from'])<=timestamp(at)<timestamp(p['valid_until']) and timestamp(at)<=timestamp(as_of),'INVALID_TIME','Assessment outside physical product window/cutoff')
    name='FIRE_PROBABILITY' if p['hazard']=='FIRE' else 'MAXIMUM_DEPTH'
    layer=next(l for l in p['layers'] if l['name']==name);path=verify_asset(root,layer);before=sha256(path)
    total=0;affected=[];seen=set()
    with rasterio.open(path) as src:
        require(str(src.crs)==p['grid']['crs'] and list(src.shape)==p['grid']['shape'] and all(math.isclose(x,y,abs_tol=1e-12,rel_tol=0) for x,y in zip(list(src.transform)[:6],p['grid']['transform'])),'GRID_MISMATCH','Raster differs from contract')
        for record in exposures:
            validate_record(record);r=record['payload'];require(record['kind']=='exposure','INVALID_CONTRACT','Exposure point required')
            require(record['id'] not in seen,'DUPLICATE_EXPOSURE','Do not count people twice');seen.add(record['id'])
            require(r['territory_id']==request['territory']['id'],'TERRITORY_MISMATCH','Exposure belongs to another territory')
            require(timestamp(record['available_at'])<=timestamp(as_of) and timestamp(r['valid_from'])<=timestamp(at)<timestamp(r['valid_until']),'STALE_EXPOSURE','Unavailable/expired exposure')
            require(r['people'] is not None,'UNKNOWN_EXPOSURE','Missing population is not zero')
            x,y=transform('EPSG:4326',src.crs,[r['point_wgs84'][0]],[r['point_wgs84'][1]])
            row,col=src.index(x[0],y[0]);require(0<=row<src.height and 0<=col<src.width,'UNKNOWN_COVERAGE','Exposure outside hazard grid')
            sample=next(src.sample([(x[0],y[0])],masked=True));value=float(sample.data[0])
            require(not sample.mask[0] and math.isfinite(value) and value>=0,'UNKNOWN_COVERAGE','NoData or invalid hazard is not safe zero')
            if value>0:total+=r['people'];affected.append(dict(exposure_id=record['id'],people=r['people'],hazard_value=value,unit=layer['unit']))
    require(sha256(path)==before,'CHECKSUM','Assessment modified hazard raster')
    return dict(schema_version='0.4.0',kind='exposure_assessment',territory_id=request['territory']['id'],hazard=p['hazard'],hazard_sha256=before,at=at,as_of=as_of,exposed_people=total,affected=affected,qualification='UNQUALIFIED_RESEARCH',semantics='Point co-location with positive hazard cells; not damage, casualty estimate, or operational risk threshold')
