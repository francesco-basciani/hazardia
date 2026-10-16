"""Guest installation proof without trusting historical M0 parent paths."""
import argparse,json,platform,subprocess
from pathlib import Path
from hazardia.io import load,sha256,utcnow,write_new
from hazardia.contracts import validate_product
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);a=p.parse_args();root=Path(a.runtime).resolve();cfg=load(root/'runtime-v2.json');checks=[]
for path,h in cfg['engine_files'].items():
    assert Path(path).is_relative_to(root),('External engine path',path)
    assert sha256(path)==h,path
checks.append(dict(id='independent-engine-files',status='PASS',count=len(cfg['engine_files'])))
versions=json.loads(subprocess.check_output([cfg['geo_python'],'-c','import json,numpy,rasterio,pyproj; from osgeo import gdal; print(json.dumps(dict(numpy=numpy.__version__,rasterio=rasterio.__version__,pyproj=pyproj.__version__,gdal=gdal.__version__)))'],text=True))
expected=dict(numpy='1.21.5',rasterio='1.2.10',pyproj='3.3.0',gdal='3.4.1')
assert versions==expected,('Reference geospatial version drift',versions,expected)
checks.append(dict(id='reference-geospatial-versions',status='PASS',versions=versions))
for key in ['core_python','fire_python','geo_python','fire_source','hmc_binary','reflex_source','grass_addon_base']:
    assert Path(cfg[key]).is_relative_to(root),(key,cfg[key])
for record in load(root/'installation/demo-jobs.json'):
    directory=root/'jobs'/record['id'];product=load(directory/'product.json');validate_product(product,load(directory/'request.json'),directory);checks.append(dict(id=record['hazard'],status='PASS',product=record['id'],qualification=product['qualification']))
cat=load(root/'web-assets/catalog.json');assert {s['hazard'] for s in cat['scenarios']}=={'FIRE','FLOOD'}
physical=root/'web-assets/physical-days-20261016T040414Z/comparison.json'
if physical.exists():
    data=load(physical);assert data['status']=='PASS' and data['completed_hours']==[72,72]
    for row in data['frames']:
        for key in ['baseline','fuelbreak']:
            path=root/'web-assets'/row[key]['url'].split('/assets/',1)[1];assert sha256(path)==row[key]['png_sha256']
    checks.append(dict(id='native-72h-pair-and144png',status='PASS'))
else:checks.append(dict(id='native-72h-pair',status='NOT RUN'))
result=dict(at=utcnow(),status='PASS',platform=platform.platform(),checks=checks,limitations=['Same VM OS prerequisites, not independent newly booted VM','Unqualified conditional physics, no H1-H3 evidence'])
output=root/'installation'/('verification-'+utcnow().replace(':','').replace('.','')+'.json');write_new(output,result);print(json.dumps(result,indent=2))
