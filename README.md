# HAZARDIA

**Hazard-Aware Adaptive Resource and Decision Intelligence Architecture**  
**Documentation baseline v1.4 | Local multi-hazard dashboard available for research trials; current demo: Abruzzo**

Satellite-first, weather-aware, geographically configurable multi-hazard decision support, with wildfires and floods as the first implemented domains. HAZARDIA is a generic extensible platform; these initial modules do not define its future domain boundary. HAZARDIA is a research framework comprising replaceable satellite/data connectors, CIMA physical simulators (PROPAGATOR and HMC + REFlEx, executed on declared unqualified research fixtures), impact/exposure models, a solver-pluggable robust rolling-horizon decision engine, capability-aware graceful degradation, predictive alerts, and a local web UI for side-by-side scenario comparisons. All real dispatch decisions require human authorization.

## Monitoraggio territoriale reale

In **Monitoraggio → Attenzione territoriale** trovi pericolosità incendio FWI e secchezza DC da EFFIS, zone di criticità/allerta DPC e contesto meteo disponibile, con giorno, fonti, evidenze e copertura mancante espliciti. Tutto viene acquisito e conservato nella VM con cache3ore. **Inquadra copertura delle fonti** apre la vista Italia; gli esempi dei simulatori sono attivabili a parte in Configurazione. È un monitoraggio di ricerca con fonti reali: rischio d'impatto locale e sensori non collegati sono dichiarati non disponibili. [Fonti, comandi e verifiche](reports/MONITORAGGIO-FONTI-REALI.md).

## Innesco e squadre antincendio

Apri **Simulazioni e risorse → Incendio · innesco e squadre** (`/?view=results`). Un nuovo workspace parte senza esempi precaricati. Ogni scenario ha inneschi e squadre indipendenti. Trascina gli elementi anche nel primo scenario; usa **Crea scenario** per un caso vuoto o **Duplica** per copiarne uno, poi modifica solo la copia. Trascina le squadre nella mappa dello scenario destinatario e disegna le loro linee o aree d'intervento. Premi **Avvia simulazione**; quando il calcolo è disponibile la timeline riproduce incendio e meteo insieme. Puoi mettere in pausa, tornare indietro, modificare gli elementi nell’elenco **Elementi dello scenario** e usare **Aggiorna e riprendi**: ricalcola la configurazione modificata e ritorna all’ora scelta. Le alternative vuote non bloccano il gruppo. I risultati invariati vengono riutilizzati quando compatibili anche con il calendario numerico comune; altrimenti sono ricalcolati. Durante il calcolo fisico nella VM il tempo resta in pausa e il pulsante indica **Calcolo in corso**; la ripresa è automatica dopo risultati coerenti. Per modifiche alle sole squadre conserva data iniziale, terreno e meteo congelati del risultato precedente; il trascinamento mette subito in pausa e le finestre mantengono il proprio ordine. A fine orizzonte torna prima indietro. Non è un checkpoint interno del motore. Dimensione, categoria, area/linea e minuto di attivazione sono nell’ispettore; **Attiva all’ora selezionata** copia il tempo della timeline. Per i nuovi calcoli con **Previsioni reali** la VM prepara automaticamente il territorio attorno agli inneschi: nessun riquadro dimostrativo da rispettare. Usa DEM Copernicus GLO30 e copertura ESA WorldCover2021, con riclassificazione sperimentale dei combustibili; vento distribuito e umidità del combustibile stimata da temperatura, umidità dell’aria, vento e pioggia orari. L’umidità manuale rimane una scelta avanzata esplicita. Durata fino a72ore, meteo congelato comune al confronto e visualizzabile su ciascuna mappa come **METEO USATO**. Il dominio numerico interno misura circa30km: fonti mancanti, superficie non combustibile, inneschi troppo distanti o incendio che raggiunge il bordo producono un motivo esplicito. Non è una garanzia di copertura o accuratezza universale. Il selettore **Effetto nel modello** distingue barriera ideale con rimozione del combustibile e azione nativa PROPAGATOR lungo una linea; i nuovi Canadair/elicotteri usano l’azione nativa sull’umidità. Le configurazioni precedenti mantengono il proprio effetto. Nessuna efficacia di categoria certificata. Il pulsante **Scenario ottimizzato** apre mezzi disponibili e priorità; puoi importare le squadre dello scenario. Il sistema prepara se necessario un riferimento senza interventi, ottimizza e calcola una coppia nativa su input congelati. Il verdetto usa la probabilità del fuoco sulle priorità cartografate e sceglie il migliore dei due risultati, anche quando è il riferimento; non promette un ottimo fisico globale. Coperture e qualifiche mancanti restano esplicite. Configurazioni dell’utente conservate nella VM, nessun esempio o intervento nascosto. Lo scroll della pagina non ingrandisce le mappe; usare i pulsanti di zoom. [Flusso, prove reali e limiti](reports/FLUSSO-SIMULAZIONE-E-OTTIMIZZAZIONE.md).

## Prove salvate senza cambiare i propri scenari

La prova **Fonte Vetica ·18ottobre2026** comprende tre scenari nativi72h con innesco rappresentativo, nessun intervento, intervento ideale immediato o dopo1h. È ispirata alla notizia, non una ricostruzione o previsione del rogo reale. Nella VM in uso è disponibile in **Simulazioni → Come creare e confrontare gli scenari → Prove salvate**, oppure `/?view=results&case=fonte-vetica-20261018`. Si apre a+24h; modifiche e nuovi scenari rimangono nella copia separata. [Ipotesi, risultati e rigenerazione](reports/FONTE-VETICA-20261018.md). Su una nuova installazione la prova va prima preparata con la spec/script documentati; nessun esempio viene inserito automaticamente nel workspace principale.

## Esplorare le previsioni meteo

In Monitoraggio la barra **Previsioni meteo** permette di riprodurre, mettere in pausa e scorrere le ore del campo disponibile, con velocità regolabile e data/ora esplicita. Il passaggio fra ore è continuo, con interpolazione visuale dichiarata e pausa anche sugli istanti intermedi; i nomi geografici hanno una gerarchia distinta dai numeri meteo. Nei controlli sotto la mappa seleziona vento, temperatura, pioggia, umidità, nuvole e altre variabili. Valori senza riquadri, temperature colorate, precipitazione e nuvolosità trasparenti con sfumature continue. Mappe prima dei pannelli di configurazione. Nelle simulazioni esiste una sola timeline per incendio e meteo. Il replay consulta la cache reale Open-Meteo nella VM: non avvia simulazioni né modifica un risultato già calcolato; quote, risoluzione e dati mancanti sono dichiarati. [Verifiche e limiti](reports/NOMI-E-METEO-CONTINUO.md).

## Installazione completa e ricostruzione della VM

Repository: **[francesco-basciani/hazardia](https://github.com/francesco-basciani/hazardia)**. Parti dalla **[guida completa in italiano](docs/INSTALLAZIONE.md)**: creazione UTM/Ubuntu, chiavi proprie, dipendenze, tutti e tre i simulatori, dati Abruzzo, dashboard e test. Il [documento di riproducibilità](docs/RIPRODUCIBILITA.md) distingue sorgenti pubblicati, dati rigenerabili e verifiche effettivamente eseguite.

I comandi scientifici seguenti si eseguono **nella VM Ubuntu 22.04 ARM64**, dopo i prerequisiti della guida e con il repository in `~/hazardia-runtime/app`:

```sh
python3 scripts/bootstrap.py install --runtime "$HOME/hazardia-runtime"
python3 scripts/bootstrap.py demo --runtime "$HOME/hazardia-runtime"
python3 scripts/bootstrap.py regions --runtime "$HOME/hazardia-runtime"
python3 scripts/bootstrap.py days --runtime "$HOME/hazardia-runtime"
python3 scripts/bootstrap.py verify --runtime "$HOME/hazardia-runtime"
../core-env/bin/python scripts/web_service.py start --runtime "$HOME/hazardia-runtime"
```

Il server resta locale; la guida spiega il tunnel SSH e l’accesso dal browser. VM, ambienti, raster pesanti e stato personale non si copiano in Git: vengono creati dalle procedure. Non occorrono servizi commerciali obbligatori. [Esiti della ricostruzione/pubblicazione](reports/PUBBLICAZIONE-GITHUB.md).

## Eight authoritative Markdown documents

| File | Responsibility |
|---|---|
| `README.md` | Human overview and getting started |
| `AGENTS.md` | Codex operating contract and autonomy limits |
| `SPEC.md` | Requirements, architecture, UI, data/simulators, decision model, acceptance |
| `PLAN.md` | Milestones M0–M7, deliverables, dependencies, verification, M0 handoff |
| `MEMORY.md` | Confirmed decisions, progress, blockers, next action and decision rationale |
| `CHECKLIST.md` | Requirement-by-requirement statuses, traceability, tests and evidence pointers |
| `research/RESEARCH.md` | JSS research questions, experiment plan, baselines, related work and paper outline |
| `research/EVIDENCE.md` | Scientific evidence ledger; initial M0 real runs and negative outcomes recorded |

## Scope and execution constraints

- Initial execution machine: **one Linux UTM VM on the MacBook**, containing both fire and flood pipelines and all future HAZARDIA services. Mac hosts UTM and acts as a development/display client. Preserve portability to a future Linux server.
- No required paid service or commercial cloud. Separate processes/dependency environments inside the same Linux VM; no native Mac scientific runtime dependency.
- Start with separate wildfire and flood examples, progress to two-region multi-hazard joint resource allocation, strategy comparison, forecast-driven proactive alerts, and measured graceful degradation.
- Satellite-first does not mean satellite-only: weather, hydrology, elevation, river measurements, exposure and resource inventories are necessary where appropriate. Source provenance, uncertainty and data rights are mandatory.
- Research-only V1; no claim of certified emergency operations. Synthetic resources must be declared synthetic.
- GitHub publication explicitly requested by the user on 2026-10-16; designated repository: `https://github.com/francesco-basciani/hazardia.git`.

## Complete plan audit

[Verifica completa del piano](reports/VERIFICA-PIANO.md): tutti i requisiti restano previsti, ma la piattaforma non è completa. La matrice distingue software verificato, fixture sintetici, funzionalità mancanti e gate bloccati; non dedurre il completamento dai soli test PASS.

## Previsioni reali e nuovi scenari

[Open-Meteo è collegato](reports/METEO-REALE.md): livello Meteo sul punto L’Aquila, selezione oraria e avvio esplicito di nuove simulazioni native con previsione reale. Cache condivisa nella VM, piano gratuito non commerciale, massimo48tentativi/giorno e intervallo30min. Incendio60min e HMC→REFlEx6h eseguiti: il caso alluvionale asciutto produce un raster nativo zero, senza pioggia inventata. Condizioni iniziali e parametri fisici restano di ricerca; nessuna allerta operativa o calibrazione implicita.

## Current repository status

**Open [the local dashboard](http://127.0.0.1:8080/).** The default workspace is [Monitoraggio](reports/MONITORAGGIO.md): a large central map with independent fire/flood filters and both overlays. Planning and comparisons have their own “Decisioni e confronto” section. Read the [Italian quick-start guide](reports/DASHBOARD-GUIDA.md) for practical trials, model jobs and restart commands.

The backend, data, HiGHS, PROPAGATOR and HMC→REFlEx execute together in the existing Linux VM (4vCPU/8GiB RAM/19GiB disk); the Mac is the display/development client. Real Sentinel-2 pixels and genuine model outputs cover a small L'Aquila AOI. Two synchronized maps, authored resources/exposure, verified allocation, joint fire/flood comparison, physical-job queue/cancel/retry, controlled rolling progress, fault laboratory and advisory replay are available. No paid service, public service deployment or dispatch; source publication is separate from running an operational service.

**Reconstruction checkpoint (2026-10-16):** new environments, HMC compilation, genuine FIRE/FLOOD and native paired72h rebuilt in a separate prefix in the same VM;85softwaretests +72browserchecks PASS. VM assets/schema PASS; newly booted independent OS NOT RUN. FIRE/72h replay exact; FLOOD has197one-float-level cell differences, documented rather than hidden. [Delivery evidence](reports/PUBBLICAZIONE-GITHUB.md).

**Historical technical evidence:** M0–M4 fixture gates passed; M5/M6 software tests passed on controlled inputs. Final regression66tests and two30-request decision timing campaigns pass; latest p95 .821s, maximum .829s on the pinned small workload. [M3](reports/M3-dashboard.md), [M4](reports/M4-joint.md), [M5](reports/M5-adaptive.md), [M6](reports/M6-degradation.md), [M7 assessment](reports/M7-validation.md).

**The full research release remains BLOCKED.** The2024scenarios use synthetic ignition/fuel/rain/Q0, populations/resources and intervention effects; hydrology is uncalibrated and REFlEx uses a disclosed compatibility copy. Alert emissions in the dashboard are explicitly synthetic. Real current weather and historical CEMS observations were acquired separately and cannot validate unmatched2024scenarios. Large display stress100kpolygons failed; original full M/L cases, complete physical portability/fresh-machine install and principal scientific ablations remain unverified. H1–H3 and operational skill are not established. Current truth is in [CHECKLIST](CHECKLIST.md), not inferred from screenshots.

User authorized autonomous continuation through the original plan; no further routine milestone approval is required. Substantial out-of-scope intervention still requires the user. Earlier authorization/status notes in chronological records are historical, superseded by the latest checkpoint. Historical failure artifacts are retained unchanged.

## Available research workflow

Select FIRE, FLOOD or JOINT; inspect source dates and model provenance; compare authored interventions on identical physical products; start/cancel/retry genuine CIMA jobs in the VM; inspect independent constraints and JSON export. FIRE playback uses actual model arrival times; FLOOD shows maximum depth only. Controlled synthetic fault, preparedness, rolling and alert tools are labeled as such. Human research acknowledgment never authorizes real action. The UI currently uses the L'Aquila example; the second geography is a contract/replay test, not a second live calibrated study region.

## Performance and responsive interface

Desktop/tablet/phone375/768/1440px, keyboard controls, cold display,30feedback actions, map movements, long-job handling and automatic accessibility checks have executed evidence. The30-minute stability session passed on the pinned small fixture (p95feedback17.1ms, p05map60FPS, GC-normalizedgrowth.461MB); raw evidence is in M7. Automatic contrast incompletes and the100kdisplay failure remain explicit limits; no WCAG or universal performance certification. See [the ledger](CHECKLIST.md) and [reference protocol](reports/M0-performance-baseline.md).

## Runtime, geography and extensibility

The complete stack executes in HAZARDIA-M0-ARM64, including both hazards; see [ADR-0002](reports/ADR-0002-single-linux-runtime.md). Abruzzo examples currently use a compact L'Aquila AOI. Earlier Tuscany experiments remain historical feasibility evidence; local calibration and historical skill remain unqualified.

SPEC AR-EXT-01 / [ADR-0004](reports/ADR-0004-architectural-extensibility.md) preserve seven conceptual extension possibilities, without implementing additional domains, Digital Twins, AI models or application agents. Concrete M1 boundaries and versions are in [ADR-0005](reports/ADR-0005-M1-concrete-boundaries.md); staged checks in CHECKLIST distinguish M1/M2/M3 boundary executions from unqualified alternate physics.

Historical M0 reports: [single VM](reports/M0-unified-vm.md), [contract examples](reports/M0-contracts.md), [real terrain](reports/M0-real-terrain.md), [hydrological source dossier](reports/M0-hydrological-case.md), [original-gate review](reports/M0-gate-review.md). Original FAIL/BLOCKED outcomes are retained; earlier M0-only authorization notes are superseded by the current continuous-execution checkpoint above.


Final local supplement:3,275files verified inVM and after host transport; source998b934, integrity record [transport verification](reports/dashboard-evidence/transport-verification.json). The packaged-source replay agrees exactly on the pinned decision. This is a research supplement relying on retained M1parent assets/environments, not a completed independent full installation. The dashboard remains running for user trials; full research gates remain blocked.


[Vento regionale animato](reports/VENTO-REGIONALE.md):315punti ICON-EU reali su tutto il rettangolo Abruzzo,96ore, particelle trasparenti/ora/pausa, piano gratuito non commerciale con cacheVM3h/max8acquisizioni al giorno. Sfondo satellitare regionale e ortofoto al dettaglio; il campo è di visualizzazione, non nuove forzanti distribuite nei simulatori.

Il [meteo sull’intera inquadratura](reports/METEO-SULLA-MAPPA.md) aggiunge vento, temperatura e precipitazione reali nel Monitoraggio ai13zoom8–20, con livelli trasparenti, lettura per punto e cache VM gratuita entro quote. Conserva il vento Abruzzo più fitto; il contesto globale usa un campionamento dichiarato più rado. La portabilità reale all’estero e le forzanti distribuite CIMA restano da qualificare.

Monitoraggio: nel selettore **Livello meteo** sono disponibili temperatura, pioggia, umidità, raffiche, nubi, pressione e radiazione, con vento animato indipendente. Le aree di attenzione seguono le zone ufficiali DPC; l'incendio usa una sintesi EFFIS esplicitamente distinta dalle allerte meteo-idro. In **Simulazioni e risorse** l’avvio è vuoto: inserisci gli inneschi di ciascuno scenario, crea o duplica esplicitamente gli scenari e aggiungi solo le unità scelte. I precedenti esempi72h rimangono evidenze storiche, non configurazioni precaricate. Dettagli e limiti in [Meteo, zone e tre giorni](reports/METEO-ZONE-E-TRE-GIORNI.md).

Nello studio, **Strumenti e confronto** raccoglie inserimento di inneschi/squadre; il confronto usa finestre cartografiche contemporanee. Su telefono/tablet il pannello e le impostazioni sono richiudibili; le proprietà dell'elemento selezionato hanno uno spazio dedicato. [Riordino grafico e verifiche](reports/RIORDINO-GRAFICO-SIMULATORE.md).

**Meteo nelle mappe degli scenari:** spunta vento, temperatura, pioggia, umidità, raffiche, nubi, pressione e radiazione. Le sovrapposizioni sono trasparenti, il vento è animato; l’ora segue sempre la timeline unica dello scenario. La cache e le richieste Open-Meteo restano nella VM entro le quote gratuite. Copertura assente, ora mancante e cache scaduta sono esplicite. Attivare un livello non cambia gli input fisici del calcolo. [Avvio pulito e livelli meteo](reports/AVVIO-PULITO-E-LIVELLI-METEO.md).

**Caso ideale con ottimizzazione e priorità:** in Simulazioni e risorse aprire **Priorità territoriali e piano ideale**. Il caso verificato si carica esplicitamente solo in un workspace vuoto; offre4mezzi ipotetici, pesi modificabili, cartografia OSM parziale e ricalcolo con unità indisponibili. HiGHS ottimizza punti di priorità, non persone salvate; il confronto nativo è distinto e usa forzanti congelate. [Risultati e riproduzione](reports/CASO-IDEALE-E-PRIORITA.md), [contratto0.6](reports/ADR-0013-ideal-spatial-policy.md).

La superficie colorata negli scenari è l’**area cumulativamente raggiunta**, non le fiamme attive: un Canadair non cancella il bruciato precedente. [Correzioni del replay e prove Canadair/barriera](reports/MODIFICHE-DURANTE-LA-SIMULAZIONE.md).
