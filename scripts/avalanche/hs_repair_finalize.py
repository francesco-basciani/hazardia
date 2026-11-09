"""Collect actual VM evidence; never rerun a solver or contact a source."""
from pathlib import Path
import datetime as dt,gzip,hashlib,json,shutil,tarfile
from hazardia_avalanche.hs_history_trial import profile_consistency
from hazardia_avalanche.hs_pilot import verified_product
from hazardia_avalanche.worker import iso

h=Path.home();r=h/'avalanche-runtime';w=Path('/dev/shm/hs-repair-20261101');result=json.loads((w/'latest-trial/result.json').read_text())
for key,entries in result['profiles'].items():
 for at,pr in entries.items():profile_consistency(pr,result['forecast'][key][0 if at=='at_observation' else -1])
for name in ['hs_restart_audit.py','hs_history_trial.py']:
 shutil.copyfile(r/'app/src/hazardia_avalanche'/name,w/('current-'+name))
for name in ['avalanche-hs-pilot.js','avalanche-entry.js','avalanche-layer.js']:
 shutil.copyfile(h/'hazardia-runtime/app/src/hazardia/web/static'/name,w/name)
raws=w/'raw-sources';raws.mkdir(exist_ok=True)
ledger=json.loads((w/'latest-inputs/source-ledger.json').read_text())
for source in ledger:
 lead=source['name'].split('f')[-1];p=r/'local-assessment/noaa-gfs/20261101T0000Z'/('f'+lead+'.grib2')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'];shutil.copyfile(p,raws/p.name)
station=result['provenance']['observations'];found=[]
restored=raws/'observed-campo-chart.gz'
if restored.exists() and hashlib.sha256(gzip.decompress(restored.read_bytes())).hexdigest()==station['source_sha256']:
 found=['Host verified archive experiments/automatic/20261101T102946Z; exact source restored for audit']
for p in (r/'runs').glob('20261101*/observed-campo-chart.gz'):
 raw=gzip.decompress(p.read_bytes())
 if hashlib.sha256(raw).hexdigest()==station['source_sha256']:
  shutil.copyfile(p,raws/'observed-campo-chart.gz');found.append(str(p));break
assert found,'OBSERVATION_RAW_NOT_FOUND'
assert hashlib.sha256(gzip.decompress((raws/'observed-station-locations.gz').read_bytes())).hexdigest()==station['location_source_sha256']
_,regional=verified_product(h/'hazardia-runtime/web-assets/avalanche-gran-sasso-full')
_,manifest=verified_product(h/'hazardia-runtime/web-assets/avalanche-hs-pilot')
audit=dict(checked_at=iso(dt.datetime.now(dt.timezone.utc)),regional_unchanged=regional['sha256']==result['provenance']['original_product']['sha256'],regional_sha256=regional['sha256'],published=manifest,observation_raw=found,native_solves=sum(len(json.loads((w/p).read_text())['runs']) for p in ['restart-protocol.json','history-trial/protocol.json','latest-trial/protocol.json']),free_disk=shutil.disk_usage(r).free,point_swe_change_kg_m2=result['mass_state_change_kg_m2'],table=[dict(lead=h,control_cm=result['forecast']['restart_control'][h]['hs_cm'],conditioned_cm=result['forecast']['hs_forced_trial'][h]['hs_cm'],original_cm=result['forecast']['original_archived'][h]['hs_cm']) for h in [0,6,12,24,48,72]])
(w/'final-audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit))
with tarfile.open('/dev/shm/hs-repair-evidence-20261101.tgz','w:gz') as t:
 for p in w.rglob('*'):
  if p.is_file() and 'preserved-assets' not in p.parts and p.suffix!='.tgz':t.add(p,arcname=str(p.relative_to(w)))
archive=Path('/dev/shm/hs-repair-evidence-20261101.tgz');print('ARCHIVE',hashlib.sha256(archive.read_bytes()).hexdigest(),archive.stat().st_size)
