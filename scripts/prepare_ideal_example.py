"""VM-only opt-in reproducible ideal example using completed baseline and cached OSM."""
import argparse,json,time,urllib.request
from pathlib import Path
from hazardia.io import HazardError

def api(base,path,body=None):
 req=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Hazardia-Research':'1'});return json.load(urllib.request.urlopen(req,timeout=15))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--request',required=True,help='Explicit job_id/fleet/weights/robust/assumptions JSON');ap.add_argument('--base',default='http://127.0.0.1:8080');ap.add_argument('--replace',action='store_true');a=ap.parse_args();root=Path(a.runtime);out=root/'web-assets/ideal-example.json'
 if out.exists() and not a.replace:raise SystemExit('Example exists; use --replace explicitly')
 accepted=api(a.base,'/api/fire-ideal',json.loads(Path(a.request).read_text()));start=time.monotonic()
 while True:
  r=api(a.base,'/api/decisions/'+accepted['id'])
  if r['status'] not in ['RUNNING','QUEUED']:break
  if time.monotonic()-start>65:raise SystemExit('Decision deadline outcome unavailable; inspect ID '+accepted['id'])
  time.sleep(1)
 if r['status']!='VALIDATED_FOR_SIMULATION':raise SystemExit(json.dumps(r))
 pair=api(a.base,'/api/fire-ideal/replay',{'decision_id':r['id']});start=time.monotonic();series={}
 while len(series)<2:
  for k,j in pair['jobs'].items():
   if k in series:continue
   v=api(a.base,'/api/firelab/'+j)
   if v['state']=='SUCCEEDED':series[k]=v['series']
   elif v['state'] in ['ERROR','TIMEOUT','CANCELLED']:raise SystemExit(json.dumps(v))
  if time.monotonic()-start>1900:raise SystemExit('Native pair still incomplete; retain job IDs '+str(pair))
  if len(series)<2:time.sleep(3)
 cases=[]
 for k in ['A','B']:
  inp=dict(r['ideal']['baseline_input'],resources=series[k]['plan']['resources'],comparison_times=series[k]['plan']['comparison_times']);cases.append(dict(name='Ideale · Replay senza interventi' if k=='A' else 'Ideale · Replay piano ottimizzato',input=inp,job_id=pair['jobs'][k]))
 value=dict(qualification='IDEAL_FROZEN_REPLAY_NOT_OPERATIONAL',decision_id=r['id'],scenarios=cases,fleet=r['ideal']['fleet'],assumptions=r['ideal']['assumptions']);out.write_text(json.dumps(value,ensure_ascii=False));print(json.dumps({'decision_id':r['id'],'jobs':pair['jobs'],'example':str(out)}))
if __name__=='__main__':main()
