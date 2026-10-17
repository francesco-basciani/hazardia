"""Independent frame reader/reprojection in VM geo environment."""
import numpy as np,rasterio
from PIL import Image
from rasterio.transform import Affine,from_bounds
from rasterio.warp import transform_bounds,reproject,Resampling
from hazardia.io import load,write_new,sha256,verify_asset,HazardError
def render(root,req):
    grid=req['grid'];tr=Affine(*grid['transform']);bounds=rasterio.transform.array_bounds(*grid['shape'],tr);geo=transform_bounds(grid['crs'],'EPSG:4326',*bounds);merc=transform_bounds(grid['crs'],'EPSG:3857',*bounds);native=load(root/'fire-native-result.json');rows=[]
    for frame in native['frames']:
        if sha256(root/frame['path'])!=frame['sha256']:raise HazardError('CHECKSUM','Native frame drift')
        with np.load(root/frame['path'],allow_pickle=False) as a:p=a['probability']
        if list(p.shape)!=grid['shape'] or not np.isfinite(p).all() or (p<0).any() or (p>1).any():raise HazardError('INVALID_OUTPUT','Native frame shape/range')
        projected=np.zeros((1024,1024),dtype='float32');reproject(p,projected,src_transform=tr,src_crs=grid['crs'],dst_transform=from_bounds(*merc,1024,1024),dst_crs='EPSG:3857',resampling=Resampling.nearest)
        rgba=np.zeros((1024,1024,4),dtype='uint8');rgba[:,:,:3]=[242,78,18];rgba[:,:,3]=np.where(projected>0,80+150*projected,0).astype('uint8');name='frame-%03d.png'%frame.get('index',frame['hour']);file=root/'products'/name;Image.fromarray(rgba,'RGBA').save(file)
        area=float(p.sum(dtype=np.float64)*tr.a**2/10000)
        if not np.isclose(area,frame['expected_area_ha']):raise HazardError('INVALID_OUTPUT','Independent frame area mismatch')
        rows.append(dict(frame,url='/api/firelab/'+root.name+'/'+name,png_sha256=sha256(file)))
    plan=load(verify_asset(root,next(a for a in req['assets'] if a['role']=='fire_plan')))
    cells=np.argwhere(p>0);affected=geo
    if len(cells):
        r0,c0=cells.min(axis=0);r1,c1=cells.max(axis=0)+1;west,north=tr*(int(c0),int(r0));east,south=tr*(int(c1),int(r1));affected=transform_bounds(grid['crs'],'EPSG:4326',west,south,east,north)
    write_new(root/'fire-series.json',dict(job_id=root.name,case=native['case'],bounds=[[geo[1],geo[0]],[geo[3],geo[2]]],affected_bounds=[[affected[1],affected[0]],[affected[3],affected[2]]],grid=grid,options=req['options'],frames=rows,plan=plan,request_id=req['id'],valid_from=req['valid_from'],valid_until=req['valid_until'],qualification='UNQUALIFIED_RESEARCH',engine=load(root/'product.json')['engine'],consumed_events=native['consumed_events']))
