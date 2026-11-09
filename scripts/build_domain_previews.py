"""Build UI thumbnails from reviewed archived HAZARDIA screenshots (Linux VM)."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageOps
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
source=Path(a.input);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
boxes={'fire':(.52,.27,.97,.49),'water':(.28,.12,.64,.68),'snow':(.02,.21,.59,.73),'seismic':(.21,.18,.70,.72),'infrastructure':(.25,.26,.70,.79),'mobility':(.15,.2,.70,.8),'security':(.04,.25,.58,.85)}
manifest={'purpose':'Archived UI illustrations, never current observations or forecasts','attribution':'HAZARDIA UI; map sources © OpenStreetMap contributors / ODbL; EOX Sentinel-2 cloudless / modified Copernicus Sentinel data, CC BY-NC-SA4.0; other original credits remain in the source screenshots','previews':[]}
for key,box in boxes.items():
 raw=(source/(key+'.png')).read_bytes();im=Image.open(source/(key+'.png')).convert('RGB');w,h=im.size
 crop=im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box)))
 preview=ImageOps.fit(crop,(640,300),method=getattr(Image,'Resampling',Image).LANCZOS);target=out/(key+'.webp');preview.save(target,'WEBP',quality=84,method=6)
 manifest['previews'].append(dict(id=key,source_sha256=hashlib.sha256(raw).hexdigest(),crop_fraction=box,output_bytes=target.stat().st_size,output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),size=[640,300]))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(sum(x['output_bytes'] for x in manifest['previews']),'bytes in 7 previews')
