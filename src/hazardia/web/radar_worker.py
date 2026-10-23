"""VM geospatial worker: dated Radar-DPC SRI observation to display-only PNG."""
import argparse,datetime as dt,hashlib,json,time,urllib.parse,urllib.request
from pathlib import Path
import numpy as np,rasterio
from rasterio.warp import calculate_default_transform,reproject,Resampling
from PIL import Image
API='https://radar-api.protezionecivile.it/'
HEADERS={'Origin':'https://radar.protezionecivile.it','Content-Type':'application/json','User-Agent':'HAZARDIA-local-research/0.1 (+https://github.com/francesco-basciani/hazardia)'}
def request(path,body=None):
    with urllib.request.urlopen(urllib.request.Request(API+path,data=json.dumps(body).encode() if body else None,headers=HEADERS),timeout=12) as r:return json.loads(r.read(65536))
def validate_product_url(address,at):
    url=urllib.parse.urlsplit(address);expected='/SRI/'+dt.datetime.fromtimestamp(at/1000,dt.timezone.utc).strftime('%d-%m-%Y-%H-%M')+'.tif'
    if url.scheme!='https' or url.hostname not in ['dpc-radar.s3.eu-south-1.amazonaws.com','s3-prod-dpc-radar.s3.eu-south-1.amazonaws.com'] or url.path!=expected:raise ValueError('Untrusted or wrong-time radar product URL')
    return url

def render(source,out):
    with rasterio.open(source) as src:
        if src.count!=1 or src.width>3000 or src.height>3000 or not src.crs:raise ValueError('Unexpected radar raster')
        transform,w,h=calculate_default_transform(src.crs,'EPSG:3857',src.width,src.height,*src.bounds,dst_width=600,dst_height=700)
        target=np.full((h,w),-9999,dtype='float32');raw=src.read(1)
        if not np.all(np.isfinite(raw)):raise ValueError('Nonfinite radar values')
        reproject(raw,target,src_transform=src.transform,src_crs=src.crs,src_nodata=-9999,dst_transform=transform,dst_crs='EPSG:3857',dst_nodata=-9999,resampling=Resampling.nearest)
        valid=(target>=0)&(target<=1000);rgba=np.zeros((h,w,4),dtype='uint8')
        for lo,hi,color in [(.1,1,(58,158,220,140)),(1,2.5,(37,111,218,170)),(2.5,5,(106,68,199,185)),(5,10,(191,55,137,200)),(10,1001,(220,56,53,220))]:rgba[valid&(target>=lo)&(target<hi)]=color
        Image.fromarray(rgba).save(out/'rain.png')
        yy,xx=np.indices((h,w));missing=np.zeros_like(rgba);missing[~valid&((xx+yy)%12<2)]=(75,83,92,65);Image.fromarray(missing).save(out/'missing.png')
        from rasterio.warp import transform as project
        west,north=transform*(0,0);east,south=transform*(w,h);xs,ys=project('EPSG:3857','EPSG:4326',[west,east],[south,north])
        return dict(bounds=[[ys[0],xs[0]],[ys[1],xs[1]]],native_resolution_m=[abs(src.transform.a),abs(src.transform.e)],display_shape=[h,w],valid_fraction=float(valid.mean()),wet_fraction=float((valid&(target>=.1)).mean()),max_mm_h=float(np.max(target[valid])) if valid.any() else None,nodata=-9999,rendering='Nearest-neighbour reprojection; transparent <0.1mm/h; hatch missing, not dry')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--at',type=int,required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    latest=request('findLastProductByType?type=SRI');last=latest['lastProducts'][0]['time'];at=a.at
    if not last-86400000<=at<=last:raise ValueError('Selected observation outside last24h/provider availability')
    product=request('downloadProduct',{'productType':'SRI','productDate':at});url=validate_product_url(product['url'],at)
    with urllib.request.urlopen(product['url'],timeout=20) as response:raw=response.read(4*1024**2+1)
    if len(raw)>4*1024**2:raise ValueError('Radar product exceeds4MiB')
    source=out/'source.tif';source.write_bytes(raw);result=render(source,out)
    result.update(source='Radar-DPC · Surface Rainfall Intensity (SRI)',kind='OBSERVATION',units='mm/h',at=dt.datetime.fromtimestamp(at/1000,dt.timezone.utc).isoformat().replace('+00:00','Z'),period_seconds=300,updated_at=dt.datetime.now(dt.timezone.utc).isoformat(),issued_at=None,source_url=API,product_path=url.path,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),license='CC BY-SA',license_url='https://mappe.protezionecivile.gov.it/it/mappe-e-dashboard-rischi/piattaforma-radar/',qualification='DISCLOSURE_ONLY_NOT_OPERATIONAL',coverage_note='National mosaic; maintenance and instrument gaps. Missing pixels do not establish absence of precipitation. Not a forecast or an alert.')
    (out/'result.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
