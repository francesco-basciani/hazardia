"""Read-only source fidelity and API audit, executed in the VM."""
import argparse,json,pathlib,hashlib,urllib.request,time,collections
from hazardia.osm_catalog import parse_osm,summary
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();r=pathlib.Path(a.root);out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=False)
def get(path,body=None):
 req=urllib.request.Request('http://127.0.0.1:8080'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json','X-Hazardia-Research':'1','Origin':'http://127.0.0.1:8080'})
 with urllib.request.urlopen(req,timeout=10) as response:return json.load(response)
before=[get('/api/fire-workspace'),get('/api/fire-workspace?case=forecast-fonte-vetica-20261018')];rawpath=r/'runs/map-detail-20261015T204352Z/osm-map-final-raw.json';raw=json.loads(rawpath.read_text());features,skipped=parse_osm(raw);tagged={f'osm-{e["type"]}-{e["id"]}':e for e in raw['elements'] if e.get('tags')};checks=[]
def check(name,ok):
 checks.append(dict(id=name,status='PASS' if ok else 'FAIL'));assert ok,name
check('all-represented-tags-preserved',all(f['properties']['osm_tags']==tagged[f['id']]['tags'] for f in features));check('no-silent-tagged-object-loss',len(features)+skipped==len(tagged));check('no-road-or-unknown-optimizer-priority',all(not f['properties']['optimization_eligible'] for f in features if f['properties']['catalog_group'] in ['transport','other','buildings']));check('real-healthcare-present',sum(f['properties']['catalog_group']=='healthcare' for f in features)>=14)
accepted=get('/api/territorial-context',dict(bounds=[13.375,42.345,13.405,42.36]));t=time.monotonic()
while True:
 result=get('/api/territorial-context/'+accepted['id'])
 if result['status']=='SUCCEEDED':break
 if result['status']=='ERROR' or time.monotonic()-t>100:raise RuntimeError(result)
 time.sleep(.25)
data=result['data'];check('versioned-real-catalogue-through-api',data['catalog']['version']=='osm-catalog/2');check('healthcare-through-api',data['catalog']['groups']['healthcare']>=14);check('raw-preserved',hashlib.sha256(rawpath.read_bytes()).hexdigest()=='4c3c76309a724f2fbdb95e4e793ede0eaa7f752c55c33ea5a54885eb73aa9cf7');check('user-workspaces-preserved',before==[get('/api/fire-workspace'),get('/api/fire-workspace?case=forecast-fonte-vetica-20261018')]);cfg=json.loads((r/'runtime-v2.json').read_text());check('all-engine-pins-unchanged',all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h for p,h in cfg['engine_files'].items()));value=dict(checks=checks,features=len(features),tagged=len(tagged),skipped_tagged=skipped,summary=summary(features),api_summary=data['catalog'],api_id=result['id'],source_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest(),elapsed_api_s=time.monotonic()-t,engine_pins=len(cfg['engine_files']),source_available_at=None,scope='Real cached local extract; no new physical run, health-capacity inference or national download');(out/'verification.json').write_text(json.dumps(value,indent=2));print(json.dumps(value,indent=2))
