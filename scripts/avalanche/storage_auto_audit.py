"""Read-only verification of the recovered live forecast in the Linux VM."""
import datetime as dt,hashlib,json,math,shutil
from pathlib import Path
from hazardia_avalanche.hs_pilot import verified_product
from hazardia_avalanche.worker import parse,iso

h=Path.home();r=h/'avalanche-runtime';d=h/'hazardia-runtime/web-assets/avalanche-gran-sasso-full';w=Path('/dev/shm/storage-auto-20261101')
p,m=verified_product(d);meta=p['metadata'];start=parse(meta['reference_utc']);end=parse(meta['end_utc'])
assert end-start==dt.timedelta(hours=72)
assert meta['processed_sites']==meta['unique_sites']==4578
assert meta['weather_provider']=='noaa_gfs' and meta['preferred_weather_provider']=='icon2i_hybrid'
assert meta['weather_fallback_reason'].startswith('ICON2I_CYCLE_STALE')
assert dt.datetime.now(dt.timezone.utc)-parse(meta['weather_run_utc'])<dt.timedelta(hours=12)
history=[];parents=0;assets=0;states=0
for cid,desc in p['profile_assets'].items():
 raw=(d/desc['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==desc['sha256'];entries=json.loads(raw);assets+=1
 for key in ['NWP_INITIAL','ZERO_INITIAL']:
  e=entries[key];e=entries[e['alias']] if e.get('alias') else e
  assert parse(e['profile_at_reference']['valid_at']).replace(tzinfo=dt.timezone.utc)==start
  assert parse(e['profile_at72']['valid_at']).replace(tzinfo=dt.timezone.utc)==end
  for name,values in e['hourly']['quantities'].items():
   assert len(values)==73 and all(isinstance(v,(float,int)) and math.isfinite(v) and v>=0 for v in values),(cid,name)
  states+=73
 e=entries['NWP_INITIAL'];history.append(e['history_hours']);parents+=bool(e.get('parent_history_experiment'))
assert assets==meta['usable_sites']
ids=[f['properties']['profile_id'] for f in p['features']];assert len(ids)==len(set(ids))==4578
missing=sum(cid not in p['models'] for cid in ids)
assert missing==4578-assets
state=json.loads((h/'hazardia-runtime/avalanche/auto-state.json').read_text());attempt=json.loads((r/'local-assessment/automatic.json').read_text())
assert attempt['returncode']==0 and attempt['status']=='DEGRADED'
assert parse(state['last_checked_at'])>parse(attempt['completed_at'])
newer=[f.name for f in (r/'runs').glob('gs-full-*') if f.name>meta['experiment_id']]
assert not newer
audit=dict(checked_at=iso(dt.datetime.now(dt.timezone.utc)),manifest=m,status=json.loads((d/'status.json').read_text()),reference_utc=iso(start),end_utc=iso(end),weather_cycle_utc=meta['weather_run_utc'],weather_provider=meta['weather_provider'],preferred_weather_provider=meta['preferred_weather_provider'],fallback_reason=meta['weather_fallback_reason'],processed_units=len(ids),usable_units=assets,missing_units=missing,validated_hourly_values_including_aliases=states*3,history_hours=[min(history),max(history)],continued_columns=parents,unchanged_binary_sha256=hashlib.sha256((r/'prefix/bin/snowpack').read_bytes()).hexdigest(),automatic_attempt=attempt,subsequent_supervisor_poll_at=state['last_checked_at'],same_cycle_new_regional_runs=len(newer),free_disk_bytes=shutil.disk_usage(r).free,quota_bytes=json.loads((r/'network.json').read_text())['bytes'],reserve_bytes=2*1024**3+64*1024**2)
assert audit['free_disk_bytes']>audit['reserve_bytes']
(w/'live-audit.json').write_text(json.dumps(audit,indent=2));(w/'regional-manifest.json').write_text(json.dumps(m));(w/'automatic-state.json').write_text(json.dumps(state));(w/'regional-status.json').write_text(json.dumps(audit['status']));(w/'metadata.json').write_text(json.dumps(meta));print(json.dumps(audit))
