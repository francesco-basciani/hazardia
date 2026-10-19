"""Read-only native/PNG check of reported early visual freeze. Execute in the Linux VM."""
import argparse,json,sys
from pathlib import Path
from hazardia.io import load,sha256

def audit(root,case):
 import numpy as np
 from PIL import Image
 root=Path(root);definition=load(root/'web-assets/fire-cases'/(case+'.json'));rows=[];checks=[]
 def check(name,value):
  checks.append(dict(id=name,status='PASS' if value else 'FAIL'));assert value,name
 for scenario in definition['scenarios']:
  job=root/'jobs'/scenario['job_id'];series=load(job/'fire-series.json');request=load(job/'request.json');manifest=load(job/'manifest.json');frames=[]
  for h in [3,3.25,6,12]:
   f=next(x for x in series['frames'] if x['hour']==h);p=job/f['path'];png=job/'products'/('frame-%03d.png'%f['index'])
   check(scenario['id']+'-hashes-'+str(h),sha256(p)==f['sha256'] and sha256(png)==f['png_sha256'])
   with np.load(p,allow_pickle=False) as data:a=data['probability'];area=float(a.sum(dtype=np.float64)*request['grid']['transform'][0]**2/10000)
   check(scenario['id']+'-area-'+str(h),abs(area-f['expected_area_ha'])<1e-8)
   with Image.open(png) as im:box=im.getchannel('A').getbbox();size=im.size
   frames.append(dict(hour=h,area_ha=area,positive_cells=int((a>0).sum()),alpha_bounds=box,png_size=size,png_sha256=f['png_sha256']))
  check(scenario['id']+'-native-grows-after3h',all(b['area_ha']>a['area_ha'] for a,b in zip(frames,frames[1:])))
  check(scenario['id']+'-pngs-change',len({f['png_sha256'] for f in frames})==len(frames))
  rows.append(dict(job_id=scenario['job_id'],frames=frames))
 cfg=load(root/'runtime-v2.json');check('engine-pins-unchanged',all(sha256(Path(p))==h for p,h in cfg['engine_files'].items()))
 return dict(status='PASS',run_id='early-fire-playback-20261019',checks=checks,rows=rows,engine_pins=len(cfg['engine_files']),qualification='Display diagnosis only; no new physical model run or efficacy claim')
if __name__=='__main__':
 if sys.platform!='linux':raise RuntimeError('VM Linux only')
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--case',required=True);p.add_argument('--out',required=True);a=p.parse_args();r=audit(a.runtime,a.case);Path(a.out).write_text(json.dumps(r,indent=2));print('PASS',len(r['checks']),'native assertions')
