"""Register native three-plan teaching case. No new simulations or data acquisition."""
import copy,json,pathlib,sys
if sys.platform!='linux':raise RuntimeError('VM only')
import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString
from hazardia.io import load,write_new,sha256
from hazardia.web.fire_cases import FireCases
from hazardia.web.fire_workspace import FireWorkspace
r=pathlib.Path('/home/hazardia/hazardia-runtime');o=r/'runs/three-plan-demonstration-20261105';p=load(o/'protocol.json');d=load(o/'results.json');native=load(o/'native-footprint-audit.json');assert all(v['admissible'] for v in native['rows'])
baseline=d['candidates'][0];manual=d['manual'];chosen=d['selected'];assert chosen and baseline['total_expected_ha']>manual['total_expected_ha']>chosen['total_expected_ha']
assert manual['interface_expected_ha']>=chosen['interface_expected_ha'];assert not baseline['resources']
mask=np.load(o/'interface-mask.npy',allow_pickle=False);reference=None;clock=None;events=None;checked=[];scenarios=[]
for v in d['candidates']:
 j=r/'jobs'/v['job_id'];q=load(j/'request.json');s=load(j/'fire-series.json');m=load(j/'manifest.json');static={a['role']:a['sha256'] for a in q['assets'] if a['role']!='fire_plan'};fixed=dict(assets=static,options=q['options'],grid=q['grid'],valid_from=q['valid_from'],valid_until=q['valid_until']);c=[f['elapsed_s'] for f in s['frames']];e=[x['time'] for x in s['consumed_events']]
 if reference is None:reference=fixed;clock=c;events=e
 assert fixed==reference and c==clock and e==events
 assert sha256(j/'fire-output.npz')==m['artifacts']['fire-output.npz'] and sha256(j/'fire-series.json')==m['artifacts']['fire-series.json']
 with np.load(j/'fire-output.npz',allow_pickle=False) as z:
  a=z['probability'];assert abs(float(a.sum())*.09-v['total_expected_ha'])<1e-6;assert abs(float(a[mask].sum())*.09-v['interface_expected_ha'])<1e-6
 if v['resources']:
  assert [(u['id'],u['category'],u['at_minutes'],u['effect']) for u in v['resources']]==[('ground-1','waterline_action',0,'native'),('heavy-1','heavy_action',10,'native')]
  to=Transformer.from_crs(4326,q['grid']['crs'],always_xy=True)
  for u,length in zip(v['resources'],[90,120]):assert abs(LineString([to.transform(x[1],x[0]) for x in u['line']]).length-length)<1e-5
  receipts=[u for event in s['consumed_events'] for u in event['resource_receipts']];assert len(receipts)==2 and all(u['affected_cells']>0 and u['initial_fuel_cells']>0 for u in receipts)
 checked.append(dict(plan=v['id'],job_id=v['job_id'],total_ha=v['total_expected_ha'],interface_ha=v['interface_expected_ha']))
for id,name,v in [('standard','1 · Senza interventi',baseline),('random','2 · Interventi casuali',manual),('optimized','3 · Interventi ottimizzati',chosen)]:
 s=load(r/'jobs'/v['job_id']/'fire-series.json');plan=s['plan'];inp=dict(ignitions=plan['ignitions_wgs84'],hours=12,seed=1729,moisture_percent=plan['moisture_percent'],resources=plan['resources'],weather_source=plan['weather_source'],weather_changes=plan['weather_changes'],start_at=s['valid_from'],moisture_model=plan['forcing']['moisture_model'],antecedent_hours=0,realizations=4,comparison_times=plan['comparison_times']);scenarios.append(dict(id=id,name=name,job_id=v['job_id'],input=inp,submitted_input=copy.deepcopy(inp)))
series=[load(r/'jobs'/v['job_id']/'fire-series.json')['frames'] for v in [baseline,manual,chosen]];crossings=[dict(hour=a['hour'],standard_ha=a['expected_area_ha'],random_ha=b['expected_area_ha'],optimized_ha=c['expected_area_ha']) for a,b,c in zip(*series) if not a['expected_area_ha']>=b['expected_area_ha']>=c['expected_area_ha']]
case='castelli-tre-piani-20261105';description='Tre scenari sullo stesso incendio: senza mezzi, interventi casuali e interventi ottimizzati. Replay dimostrativo con terreno reale e previsione ICON/Open-Meteo del21ottobre2026, non previsione odierna. Si apre sul risultato a12h: premi Riproduci per ripartire dall’innesco. Superficie media raggiunta:4,9275 / 1,08 / 0,18ha. Innesco ipotetico315m dall’edificato a nord di Castelli; vento iniziale circa6m/s da sud-ovest, variabile nelle12ore. Scenario1: zero interventi. Scenari2e3: identiche risorse, squadra a terra90m da0min e mezzo pesante120m da10min; cambiano soltanto posizione e orientamento. Piano casuale estratto con seed20261105, scelto fra3campioni per illustrare un esito intermedio; ottimizzato selezionato fra4fronti per ridurre prima l’esposizione dell’interfaccia100m attorno a8nuclei edificati, poi l’area totale. Selezione didattica sugli stessi risultati, non validazione indipendente o ottimo globale. Le prove peggiori sono conservate. Ordine4,93>1,08>0,18 valido a12h; prime ore con piccoli incroci stocastici tra scenari1e2. DSM/WorldCover2021 a30m; hFFMC da meteo con FFMC85iniziale ipotizzato, non umidità misurata. Azioni native di umidificazione/rimozione vegetazione, nessuna riduzione grafica del fuoco. Impronte dilatate di1cella; acqua, durata, accesso, sicurezza e capacità operative non qualificate. Edificato non significa uso residenziale verificato: popolazione e danni alle case non stimati. Tutti e tre modificabili e salvati separatamente.'
value=dict(id=case,title='Castelli · tre strategie a confronto',description=description,qualification='HYPOTHETICAL_ARCHIVED_REAL_FORECAST_DIDACTIC_SELECTION_UNQUALIFIED',source_url='https://open-meteo.com/en/docs',initial_hour=12,scenarios=scenarios)
FireWorkspace(o/'case-validation').save(dict(revision=0,scenarios=scenarios));write_new(r/'web-assets/fire-cases'/(case+'.json'),value);FireCases(r).definition(case)
assert sha256(r/'web-state/fire-workspace/workspace.json')==p['workspace_sha256'];cfg=load(r/'runtime-fire-studio.json');engines={path:sha256(pathlib.Path(path))==h for path,h in cfg['engine_files'].items() if '/fire-src/' in path};assert all(engines.values())
audit=dict(status='PASS',case=case,url='/?view=results&case='+case+'&section=compare&example=preview',results=checked,selected=[baseline['id'],manual['id'],chosen['id']],rank_at_12h=True,early_rank_crossings=crossings,all_native_frame_clocks_equal=True,all_native_event_clocks_equal=True,nonplan_assets_equal=True,shared_fleet_and_lengths_verified=True,main_workspace_preserved=True,upstream_fire_files_unchanged=len(engines),wall_seconds=sum(v['wall_seconds'] for v in d['candidates']))
write_new(o/'registration.json',audit);print(json.dumps(audit))
