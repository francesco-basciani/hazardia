"""VM-only post-run audit and opt-in two-scenario registration; no new solves."""
import copy,json,pathlib,sys
if sys.platform!='linux':raise RuntimeError('VM only')
from hazardia.io import load,sha256,write_new
def record(path,value):
 if path.exists():assert load(path)==value
 else:write_new(path,value)
from hazardia.web.fire_cases import FireCases
from hazardia.web.fire_workspace import FireWorkspace
r=pathlib.Path('/home/hazardia/hazardia-runtime');out=r/'runs/same-fleet-settlement-20261105';p=load(out/'protocol.json');result=load(out/'results.json');footprints=load(out/'native-footprint-audit.json');admissible={v['id'] for v in footprints['rows'] if v['admissible']};assert 'manual' in admissible
rank=lambda v:(v['interface_expected_ha'],v['interface_max_probability'],v['total_expected_ha'],v['id'])
selected=min([v for v in result['candidates'] if v['id'] in admissible],key=rank);manual=result['manual'];assert selected['id']!='manual'
selection=dict(selected=selected,manual=manual,excluded=[v for v in result['candidates'] if v['id']!='baseline' and v['id'] not in admissible],rule='Apply preregistered no-initial-cell-treatment rule to full native dilated footprints; retain earlier geometric-only selection as rejected evidence',native_physics_unchanged=True)
record(out/'verified-selection.json',selection)
scenarios=[];reference_request=None;reference_clock=None
for id,name,v in [('manual','Scenario 1 · linee sui fianchi',manual),('optimized','Ottimizzato · fronte verso l’abitato',selected)]:
 job=r/'jobs'/v['job_id'];s=load(job/'fire-series.json');q=load(job/'request.json');m=load(job/'manifest.json');plan=s['plan']
 for f in ['fire-series.json','fire-output.npz']:assert sha256(job/f)==m['artifacts'][f]
 inp=dict(ignitions=plan['ignitions_wgs84'],hours=s['options']['duration_s']//3600,seed=s['options']['seed'],moisture_percent=plan['moisture_percent'],resources=plan['resources'],weather_source=plan['weather_source'],weather_changes=plan['weather_changes'],start_at=s['valid_from'],moisture_model=plan['forcing']['moisture_model'],antecedent_hours=0,realizations=s['options']['realizations'],comparison_times=plan['comparison_times'])
 assert [(u['id'],u['category'],u['at_minutes'],u['effect']) for u in inp['resources']]==[(u['id'],u['category'],u['at_minutes'],u['effect']) for u in p['plans'][0]['resources']]
 static=lambda q:{a['role']:a['sha256'] for a in q['assets'] if a['role']!='fire_plan'}
 if reference_request is None:reference_request=q;reference_clock=[f['elapsed_s'] for f in s['frames']]
 assert static(q)==static(reference_request) and all(q[k]==reference_request[k] for k in ['options','grid','valid_from','valid_until'])
 assert [f['elapsed_s'] for f in s['frames']]==reference_clock
 events=s['consumed_events'];receipts=[u for e in events for u in e['resource_receipts']];assert {v['resource_id'] for v in receipts}=={'ground-1','heavy-1'} and all(v['affected_cells']>0 and v['initial_fuel_cells']>0 for v in receipts)
 assert len([e for e in events if e['spatial_forcing']])==12
 scenarios.append(dict(id=id,name=name,job_id=v['job_id'],input=inp,submitted_input=copy.deepcopy(inp)))
case='castelli-stessa-flotta-20261105';definition=dict(id=case,title='Castelli · stessa flotta, protezione dell’abitato',description='Due piani modificabili con lo stesso innesco, terreno, meteo, seed e risorse. Innesco ipotetico a165,7m dall’edificato classificato a nord di Castelli; non incendio osservato. Squadra a terra: linea90m, attiva subito. Mezzo pesante: linea120m, arrivo+10min. Scenario1 sui fianchi; ottimizzato davanti all’abitato, migliore posizione ammissibile fra quelle provate. Priorità: minimizzare la vegetazione raggiunta entro100m dagli8nuclei edificati entro1km; poi area totale. Entrambi i piani evitano questa fascia nel campione: non dimostrato un maggior numero di abitazioni salvate. Area media totale a12h:0,3825ha contro0,2475ha(−35,3%). Riferimento senza interventi1,0125ha, conservato nelle evidenze. Esclusa la candidata30m: l’impronta nativa dilatata toccava l’innesco. Meteo reale ICON/Open-Meteo acquisito5novembre15:02UTC, valido5nov16UTC→6nov04UTC;12h/4realizzazioni. Vento variabile e pioggia influiscono nel motore, non solo sulla grafica. Umidità combustibile hFFMC, inizialeFFMC85 ipotizzato, non misurato. DSM30m/WorldCover2021; uso residenziale, persone e danni alle case non conosciuti. Azioni native: umidificazione e rimozione vegetazione, con impronta a celle30m; linee/arrivi ipotetici, non capacità certificate. Nessun modello autonomo di durata, rifornimenti, accesso o sicurezza operatori. Ricerca finita, non ottimo globale o piano operativo.',qualification='HYPOTHETICAL_REAL_FORECAST_UNQUALIFIED_RESEARCH',source_url='https://esa-worldcover.org/en/data-access',initial_hour=0,scenarios=scenarios)

if not (out/'case-validation/workspace.json').exists():FireWorkspace(out/'case-validation').save(dict(revision=0,scenarios=scenarios))
dest=r/'web-assets/fire-cases'/(case+'.json');record(dest,definition);FireCases(r).definition(case)
assert sha256(r/'web-state/fire-workspace/workspace.json')==p['workspace_sha256']
audit=dict(case=case,url='/?view=results&case='+case+'&section=compare&example=start',manual_job=manual['job_id'],optimized_job=selected['job_id'],manual_ha=manual['total_expected_ha'],optimized_ha=selected['total_expected_ha'],reduction_percent=100*(1-selected['total_expected_ha']/manual['total_expected_ha']),residential_interface_equal_zero=True,main_workspace_preserved=True,native_receipts_verified=True,shared_fleet_verified=True,shared_inputs_verified=result['shared_inputs_verified'],runs=len(result['candidates']),wall_seconds=sum(v['wall_seconds'] for v in result['candidates']))
record(out/'registration.json',audit);print(json.dumps(audit))
