"""Actual prepared terrain interior, projected by the existing VM geo environment."""
import os,subprocess,threading
from pathlib import Path
from hazardia.io import load,loads,sha256,write_new,HazardError
from hazardia.firelab import dataset
_LOCK=threading.Lock()
def coverage(root):
    root=Path(root);source=dataset(root);grid=source/'grid.json'
    if not grid.is_file() or not (source/'expanded-arrays.npz').is_file():return dict(status='UNAVAILABLE',geometry=None,reason='Prepared terrain missing; bootstrap days required')
    digest=sha256(grid);cache=root/'web-state/fire-coverage'/('coverage-'+digest+'.json')
    with _LOCK:
        if not cache.exists():
            cfg=load(root/'runtime-v2.json');env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[2]),PROJ_LIB='/usr/share/proj')
            try:
                r=subprocess.run([cfg['geo_python'],'-m','hazardia.web.fire_coverage',str(grid)],capture_output=True,timeout=15,check=True,env=env)
                if len(r.stdout)>65536:raise ValueError('Coverage metadata too large')
                data=loads(r.stdout);cache.parent.mkdir(parents=True,exist_ok=True);write_new(cache,data)
            except (OSError,ValueError,subprocess.SubprocessError) as e:raise HazardError('DEPENDENCY_UNAVAILABLE','Prepared terrain coverage could not be projected') from e
        data=load(cache)
        if data.get('grid_sha256')!=digest:raise HazardError('CHECKSUM','Terrain coverage differs from grid')
        return data

def project(grid):
    from pyproj import Transformer
    from rasterio.transform import Affine
    g=load(grid);tr=Affine(*g['transform']);to=Transformer.from_crs(g['crs'],'EPSG:4326',always_xy=True);h,w=g['shape'];corners=[(2,2),(w-2,2),(w-2,h-2),(2,h-2)];ring=[]
    for i,(x,y) in enumerate(corners):
        nx,ny=corners[(i+1)%4]
        for j in range(32):
            px,py=tr*(x+(nx-x)*j/32,y+(ny-y)*j/32);lon,lat=to.transform(px,py);ring.append([lon,lat])
    ring.append(ring[0]);return dict(status='AVAILABLE',geometry=dict(type='Polygon',coordinates=[ring]),grid_sha256=sha256(grid),cell_m=g['native_cell_m'],margin_cells=2,qualification='PREPARED_TERRAIN_UNQUALIFIED_FUEL',shape=g['shape'],crs=g['crs'])
if __name__=='__main__':
    import sys,json
    print(json.dumps(project(Path(sys.argv[1])),allow_nan=False))
