# HAZARDIA

**Hazard-Aware Adaptive Resource and Decision Intelligence Architecture**  
**Documentation baseline v1.4 | Local multi-hazard dashboard available for research trials; current demo: Abruzzo**

Satellite-first, weather-aware, geographically configurable multi-hazard decision support, with wildfires and floods as the first implemented domains. HAZARDIA is a generic extensible platform; these initial modules do not define its future domain boundary. HAZARDIA is a research framework comprising replaceable satellite/data connectors, CIMA physical simulators (PROPAGATOR and HMC + REFlEx, executed on declared unqualified research fixtures), impact/exposure models, a solver-pluggable robust rolling-horizon decision engine, capability-aware graceful degradation, predictive alerts, and a local web UI for side-by-side scenario comparisons. All real dispatch decisions require human authorization.

## Monitoraggio territoriale reale

In **Monitoraggio → Attenzione territoriale** trovi pericolosità incendio FWI e secchezza DC da EFFIS, zone di criticità/allerta DPC e contesto meteo disponibile, con giorno, fonti, evidenze e copertura mancante espliciti. Tutto viene acquisito e conservato nella VM con cache3ore. **Inquadra copertura delle fonti** apre la vista Italia; gli esempi dei simulatori sono attivabili a parte in Configurazione. È un monitoraggio di ricerca con fonti reali: rischio d'impatto locale e sensori non collegati sono dichiarati non disponibili. [Fonti, comandi e verifiche](reports/MONITORAGGIO-FONTI-REALI.md).

## Innesco e squadre antincendio

Apri **Simulazioni e risorse → Incendio · innesco e squadre** (`/?view=results`). Trascina inneschi e unità sulla mappa, disegna linee o aree d'intervento e imposta l'istante di attivazione. Aggiungi scenari con **＋ Nuovo**, calcolali e confrontali con una timeline comune dotata di play, pausa e rewind. Le configurazioni sono salvate nella VM. La nuova ipotesi di intervento rimuove il combustibile nelle celle disegnate dal momento indicato; non è un'efficacia operativa calibrata delle categorie. Vento orario consumato, fuel uniforme e moisture manuale; T/RH/pioggia visibili ma non ancora accoppiati. Vedi [workflow ed evidenze](reports/SCENARI-INCENDIO.md). Il [confronto cartografico](reports/MAPPA-E-CONFRONTO.md) aggiunge livelli con opacità e separatore trascinabile, sincronizzato con la timeline, in una UI centrata sulla mappa.

Per iniziare, usa i due esempi **24 h** già calcolati nella VM: **Riproduci** avanza su risultati ogni15minuti. Per un confronto tuo seleziona un caso, premi **Crea alternativa**, sposta/aggiungi le squadre e disegna la loro linea/area; poi **Calcola tutti da confrontare**. La **Durata del confronto** modifica tutti i casi e richiede nuovi calcoli; i risultati precedenti conservano la propria durata. [Percorso e verifiche](reports/SIMULATORE-USABILITA.md).

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
