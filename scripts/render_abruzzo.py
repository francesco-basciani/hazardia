"""Render actual M1 satellite/product overlays inside the VM, not a dashboard."""
import argparse
from pathlib import Path
import numpy as np,rasterio
from rasterio.warp import reproject,Resampling
from PIL import Image,ImageDraw,ImageFont
from PIL.PngImagePlugin import PngInfo
from hazardia.io import load,write_new,sha256

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--jobs',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    run=Path(a.run);jobs=Path(a.jobs);output=Path(a.output)
    if output.exists():raise FileExistsError(output)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';regular=ImageFont.truetype(font,16);title=ImageFont.truetype(font,24)
    canvas=Image.new('RGB',(1240,905),'#f5f7fa');draw=ImageDraw.Draw(canvas)
    draw.text((25,18),'HAZARDIA M1 | Abruzzo - area di L’Aquila',fill='#10273c',font=title)
    draw.text((25,55),'PROVE TECNICHE NON CALIBRATE - scenari ipotetici, non eventi osservati o previsioni operative',fill='#a22b18',font=regular)
    controls=[('final-fire-integration.json','products/fire-probability.tif','INCENDIO | PROPAGATOR',25),('shallow-flood-integration.json','products/maximum-depth.tif','ALLUVIONE | HMC + REFlEx',645)]
    rendered=[]
    for record,layer,label,left in controls:
        job=jobs/load(run/record)['id'];path=job/layer
        with rasterio.open(path) as hazard:
            values=hazard.read(1,masked=True);rgb=np.zeros((3,hazard.height,hazard.width),dtype='uint8')
            with rasterio.open(run/'prepared/satellite.tif') as sat:
                for b in range(3):reproject(rasterio.band(sat,b+1),rgb[b],src_transform=sat.transform,src_crs=sat.crs,dst_transform=hazard.transform,dst_crs=hazard.crs,resampling=Resampling.bilinear)
            base=np.transpose(rgb,(1,2,0)).astype(float);mask=(~np.ma.getmaskarray(values))&(values.data>0)
            maxval=float(values.compressed().max());colors=np.zeros_like(base)
            if 'fire' in layer:colors[:]=[255,55,0];caption=f'Probabilità simulata: rosso > 0; {int(mask.sum())} celle coinvolte';assumptions='Innesco, combustibile e umidità sintetici; vento ERA5.'
            else:
                fraction=np.clip(values.filled(0)/max(maxval,1e-12),0,1);colors[:,:,0]=20;colors[:,:,1]=170-100*fraction;colors[:,:,2]=255
                caption=f'Profondità massima: blu chiaro 0+ / blu scuro {maxval:.3f} m';assumptions='Pioggia e Q0 sintetici; AOI parziale, suolo non calibrato.'
            base[mask]=.3*base[mask]+.7*colors[mask]
            image=Image.fromarray(base.astype('uint8')).resize((570,570),Image.NEAREST)
            canvas.paste(image,(left,118));draw.text((left,87),label,fill='#10273c',font=title)
            draw.text((left,699),caption,fill='#10273c',font=regular);draw.text((left,726),assumptions,fill='#4c5862',font=regular)
            rendered.append(dict(job_id=job.name,product_sha256=sha256(path),positive_cells=int(mask.sum()),maximum=maxval))
    draw.text((25,770),'Base reale: Copernicus Sentinel-2 L2A, 13/07/2024, S2A_33TUG_20240713_0_L2A.',fill='#4c5862',font=regular)
    draw.text((25,797),'© European Union / Copernicus. Terreno: Copernicus DEM. Meteo: ERA5 via Open-Meteo (CC BY 4.0).',fill='#4c5862',font=regular)
    draw.text((25,826),'Ritagli e scale differenti: incendio 1.92 km di lato; alluvione ~4.4 km N-S. Nessuna mappa di danno osservato.',fill='#4c5862',font=regular)
    draw.text((25,851),'Contains modified Copernicus Sentinel data 2024. Weather data by https://open-meteo.com/ (CC BY 4.0).',fill='#4c5862',font=regular)
    draw.text((25,876),'Attribuzioni complete e modifiche: ATTRIBUTION.md, incluso anche nei metadati di questa immagine.',fill='#4c5862',font=regular)
    metadata=PngInfo();metadata.add_text('Attribution',(run/'ATTRIBUTION.md').read_text())
    canvas.save(output,pnginfo=metadata);write_new(str(output)+'.json',dict(status='PASS',scope='Static scientific-artifact preview; not implemented interactive dashboard',satellite_sha256=sha256(run/'prepared/satellite.tif'),layers=rendered,png_sha256=sha256(output)))
if __name__=='__main__':main()
