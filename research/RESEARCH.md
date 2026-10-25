# HAZARDIA — JSS-oriented research protocol v1.4

**Status: preregistration candidate; initial M0 feasibility pilot recorded on 2026-10-15 (see checkpoint below). No claims established for H1–H3; main experiments NOT RUN.** Primary focus Software Engineering (architecture, adaptive decision-making, resilience). Satellite/flood/fire modelling is infrastructure and external validity, not automatically original physics contribution.

## Research questions and falsifiable hypotheses
- **RQ1 Architecture / graceful degradation:** Does capability-aware fault isolation and reconfiguration preserve more essential functionalities than naive fail-stop or reactive-only orchestration? H1: higher retained-capability profile with no additional hard constraint violation, under identical injected faults.
- **RQ2 Decision quality / joint multi-hazard:** Under shared scarce resources, does robust rolling-horizon cross-hazard allocation reduce adverse-scenario decision loss versus static, reactive-only, non-adaptive robust, and hazard-separated allocation? H2: improved chosen risk-tail metric under matched scenarios and declared cost, not assumed always.
- **RQ3 Timeliness / sustainability of adaptation:** Can independently verified candidate-or-status responses satisfy a declared 60 s p95 local workload and how does performance/quality scale with size and uncertainty? H3: meet deadline for bounded reference fixture; characterize break-even/failure cases.
- **Secondary exploratory:** sensor health/data quality, predictive warning lead-time and false alarms, geographic portability, UI explainability. Do not elevate all to independent primary RQs in same paper without evidence and venue constraints.

## Experimental factors
Independent: hazards (fire/flood/joint); two-region resource constraints and eligibility; event count; resources {small, medium, large} defined after M0; horizon length; forecast ensemble size; variation in weather issue-time and reliability; resource/data/model/network/environment faults; severity and occurrence; replan frequency; algorithm/baseline; host platform. Dependent: weighted and component-wise service retention, scenario-wise exposure/risk/impact and worst-tail, validated feasibility rate, undetected/flagged safety violations, regret vs bounded reference optimum where computable, adaptation time, time to response (p50/p95), CPU/RAM/disk, false-alarm rate and useful lead-time.

## Methods and baselines
B0 static unaltered plan, B1 reactive constrained reallocation without robust term, B2 robust but not adaptive, B3 independently allocating per hazard, B4 fail-stop service without capability degradation, HAZARDIA full, plus ablations minus capability manager / minus data quality / minus forecast updates / minus independent verifier (the last only in an offline controlled safety test and never as authorized mode). Use same snapshots, uncertainty set, resource pool, intervention effects and evaluation conditions. Avoid future observation leakage in replay: use only data available by event decision timestamp; later observations reserved for scoring. Keep weather, seed and exposure constant across compared interventions unless explicitly testing variation.

## Protocol and sample plan
Before collecting main results, prerecord parameter ranges, effect measures and fixed random seeds; use a pilot for runtime sizing and effect-model feasibility; separate pilot tuning from held-out evaluation. Target >=30 independent repeated trials per timing configuration for distributional descriptions; scenario/repetition counts and sample sizes for effect estimation determined by power/precision analysis after pilot, without retroactive cherry-picking. For each setting: record machine hardware, OS, model commit, source licenses, input and output hashes, sensor issue-time, forecast valid-time, random seed and solver termination. Report all runs incl. failed and timed out. Summarize central tendency, dispersion, uncertainty interval and effect sizes, with multiple-comparison caution. For nondeterministic simulators use paired/common random numbers when supported; otherwise document alternative.

## Validation layers
1. **Physics/observation:** wildfire predicted footprint vs held-out satellite-derived perimeter; flood inferred extent vs observed SAR/UNOSAT/Copernicus product where available. Use IoU/precision/recall and timing/calibration metrics as appropriate, with satellite-observation uncertainty caveats. Do not claim true operational skill merely from one case.
2. **Allocation constraints:** independently validate safety and jurisdiction invariants; synthetic resources are synthetic.
3. **Adaptive system:** inject resource/data/infrastructure/environment failures and report capability vector as well as decision-quality deltas.
4. **UI/traceability:** inspect synchrony/matched scenario conditions, action rationale, warning lifecycle and evidence export.

## Research gates / milestone alignment
- M0: related work + feasibility assumptions + initial RQ/benchmark design, explicit negative viability results.
- M1/M2: genuine simulator outputs, provenance and conceptual contracts; data quality/missingness characterization.
- M3/M4: per-hazard baselines, constrained reference problem and shared-resources comparison.
- M5: controlled robust vs reactive/static comparisons, forecast lead times/falses and 60 s benchmark.
- M6: degradation-vs-impact comparisons and system fault isolation ablations.
- M7: held-out Italian fire/flood, generality synthetic territory tests, reproducibility package, threats, article-ready tables/figures.

## Threats to validity / honesty gates
Model uncertainty, unavailable field resource inventories, calibrated vs synthetic intervention effects, physical-model and geospatial resolution error, opportunistic historical event selection, algorithm parameter tuning, host-specific 60s performance, correlated satellite data and forecast uncertainty, ethical operational deployment concerns. Negative results are publishable evidence. No declarations of significant improvement until measurements and appropriate analyses exist. A future JSS submission requires current author guidelines checked at submission time, independent editorial judgment and a user-approved release.


## Evidence traceability enforcement (v1.4)
Every result used in any RQ must refer to a real, immutable `run_id` manifest identifying Git commit+dirty state, dataset/config checksums, model/solver versions, hardware/OS, seed and executed commands. Report verification status independently of hypothesis outcomes (negative results retained). No RQ marked supported solely by UI screenshots, mock integration or manuscript narrative. Preserve all repetitions, including timeouts, errors, non-convergence and failed hard-safety checks. Study parameter sensitivity separately from operational safety policy.


---

## Related work

**Not an exhaustive systematic literature review.** Links are starting points; functionality, API, licenses and research claims must be checked against primary sources and dated. 'Not verified' is not 'absent'.

| System | Initial relevance | Contrast / verification needed |
|---|---|---|
| Envair360 / `https://wildfire.geospace.es/` | Wildfire satellite multisensor detection, apparent sensor/data health and fire evolution dashboards | Check empirical evidence for clustering/fusion; do not reuse unsubstantiated metrics or assume API availability |
| Technosylva / `https://technosylva.com/` | Operational wildfire forecasting, planning and resource context; some multi-hazard products | Do not claim we invented multi-hazard simulation, scenario comparison or resource management; verify any robust graceful-degradation formalism |
| WIFIRE Firemap / `https://firemap.sdsc.edu/` | Fire simulation, data integration, interactive maps | Compare openness, replication workflows, scenario tools |
| Delft-FEWS / `https://delft-fews.nl/` | Flood forecasting workflows and data orchestration | Compare integration patterns, not necessarily resource allocation |
| Google Flood Hub / `https://sites.research.google/floods/` | River forecasting, flood mapping | Data availability, use terms, global transfer |
| Sahana Eden | Disaster information coordination/resources | Compare information management and coordination concepts |
| CIMA PROPAGATOR, HMC, REFlEx | Physical simulators to integrate, not competitors for our own solver | Confirm API, model validity, licenses, time behavior |

Research search topics: self-adaptive systems, MAPE-K, architectural degradation patterns, multi-hazard disaster DSS, robust stochastic scheduling, resource allocation with uncertainty, explainable human-in-the-loop decision support, satellite fusion uncertainty, empirical SE architecture evaluation. For each accepted paper store BibTeX, DOI, method, evaluated capabilities, datasets, empirical limitations and direct comparison. No citations or novelty claims should be invented. The distinctive research hypothesis is capability-aware constrained robust adaptation with measured retained function, not 'first satellite+simulator dashboard'.


---

## Paper outline

Working title: *Capability-Aware Robust Adaptation in Satellite-Driven Multi-Hazard Decision Support Systems: Architecture and Empirical Evaluation*.

1. Introduction, motivating wildfire/flood and scarce shared response resources; clearly separate observed versus hypothetical shortcomings.
2. Problem and context: weather ensembles, physical models, hard resource/jurisdiction constraints, capability preservation, bounded decision time.
3. Related work: architecture and self-adaptation, multi-hazard and satellite-informed DSS, resource optimizers and empirical resilience; sourced evidence from `RELATED_WORK.md`.
4. HAZARDIA reference architecture: hazard adapters, weather/event quality, impact models, solver-pluggable core, independently verified policies, capability manager and decision UI.
5. Formal model and algorithms: action/impact semantics, robust rolling-horizon objective, timed termination, six-capability lattice/fault transitions, human authorization.
6. Study design: RQ1–RQ3, baselines, scenarios and held-out cases, hardware, fault injection, metrics/statistics, transparency and preregistration.
7. Results: only after real measurements; comparison/ablation and scenarios; no invented numbers.
8. Discussion: novelty bounded by evidence, generalizability, lessons about external simulators and sensor uncertainty.
9. Threats to validity, operational caveats and safety/ethical considerations.
10. Conclusion, data availability, replication artifact and future multi-territory research.

**Evidence mapping:** each eventual strong claim must link to `research/EVIDENCE.md` experiment IDs, raw manifests, source bibliography and counterexamples. Keep simulation physics credibility separate from software engineering claims. Editorial fit and author instructions to be verified at submission time.

## UI responsiveness and system performance evidence plan (v1.4)
Performance is a first-class engineering result, but is not automatically a separate primary RQ. Include per-scenario decision response rates (useful strategy versus timeout), p50/p95/worst end-to-end, simulator queue+runtime separately, hardware budget, RAM/CPU/disk, frontend interaction latency, frame rate, accessibility and scenario comparison consistency. Use pinned Mac/browser and fixture versions, cold/warm definitions, >=30 actions per benchmarked interaction and >=30 decision requests per fixed configuration. Collect objective traces with run IDs and negative cases; do not infer user satisfaction from performance counters alone. For JSS, relate resilience/performance trade-offs to RQ1/RQ3; only claim usability effectiveness if independently evaluated through an appropriate user study. Record performance regressions caused by richer satellite layers, uncertainty visualization and complex map comparisons.


## M0 source review and protocol checkpoint — 2026-10-15

Initial run `m0-audit-20261015T122006Z`; M0 gate BLOCKED. See E-M0-001…006; no H1–H3 results. Standalone PROPAGATOR 600 s synthetic pilot executes natively but exact repetition with attempted seed/thread control fails. Before main comparisons: isolate upstream RNG controls (including parallel state) or preregister distributional tolerance/paired design with sufficient repetitions; do not treat a Python NumPy seed alone as complete simulator control. The current three exploratory runs cannot establish stability, speedup or p95.

Related-work review (primary sources, not a systematic review):

| Source checked | What is established for this assessment | What remains unverified |
|---|---|---|
| [CIMA PROPAGATOR repository](https://github.com/CIMAFoundation/propagator_sim), pinned in report | Python/Numba engine and documented I/O/intervention affordances exist; real core locally executed | Empirical suppression validity, seeded replay, historic skill and Linux comparison |
| [HMC repository](https://github.com/c-hydro/hmc-dev) and [REFlEx repository](https://github.com/c-hydro/reflex) | Fortran discharge outputs and geomorphologic HAND flood chain are distinct interfaces; licenses/dates pinned | Runtime/coupling/calibration and quantitative skill on our data |
| [Arcorace et al., 2024, DOI 10.1111/jfr3.13034](https://doi.org/10.1111/jfr3.13034) | Primary model publication identified and accessed; supports treating REFlEx as geomorphologic extent/depth model | No published accuracy/runtime values adopted as local HAZARDIA results; no superiority claim |
| [Delft-FEWS](https://delft-fews.nl/) | Existing environmental forecast orchestration and broader water-domain applications; website also links FloodHub import | Capability-aware robust resource-allocation comparison requires deeper technical/empirical study; no absence claim |
| [Sahana Eden](https://sahanafoundation.org/products/eden/) | Existing humanitarian resources/assets/scenarios/mapping modules | Not a benchmarked robust-adaptation baseline yet; legacy page is not proof of current API behavior |
| [WIFIRE](https://wifire.ucsd.edu/) | Address redirected to SCIL during lookup | Firemap algorithms/API/license/metrics not confirmed in this lookup |
| [Flood Hub](https://sites.research.google/floods/) | Accessible public portal with informational-use caveat | Data API, rights, reproducibility and underlying model comparison not audited |
| [Envair360](https://wildfire.geospace.es/), [Technosylva](https://www.technosylva.com/) | Direct tool access failed in this session | Product/algorithm/availability metrics remain NOT RUN; access failure does not imply system absence |

No claim that HAZARDIA first combines satellites, hazards, maps or resource coordination. Future literature work must inspect self-adaptive/MAPE-K and robust scheduling primary research, record DOI/BibTeX/method/limitations and bound novelty by empirical comparisons. Full systematic search and current JSS submission requirements remain NOT RUN. Dataset inventory, explicit research-only weights, historical availability cutoff and held-out sampling remain mandatory; no real case selected based on successful outcome.


## Linux/RNG continuation and pilot amendments — 2026-10-15

See E-M0-007…015 and `reports/M0-continuation.md`, run `m0-linux-rng-20261015T124458Z`. This is feasibility/pilot evidence, not main RQ1–RQ3 evaluation. Engine execution and a synthetic technical common-grid flood interface pass; physical semantics/calibration remain BLOCKED. Research-release/operational targets unchanged; no M1 authorized.

Reproducibility pilot: two seeds, three repetitions across three processes perOS/method, one thread, flat64²/2realizations/spottingoff. Worker-context seeding after priming produces identical probability/fire/arrival bytes within and across Mac/Linux. Serial Mac controls fail; Linux serial controls repeat. Keep seed helper, consumed worker RNG draw, runtime/thread/backend versions and original negative cases in future manifests. This establishes a narrow executable method, not a universal seed guarantee or statistical physics-validation result. Future main trials must preregister concurrency, paired stochastic policy and independent seeds rather than count identical replays as independent scenario samples.

Flood pilot: actual HMC/REFlEx0–4 run on synthetic inputs. Preserve failures of point-NetCDF output with exit0/STOP, serial REFlEx tuple assignment, single-stream GRASS vector hierarchy, manual coast flag and adaptive HMC zero-dt hangs. Record underlying failure source independently from terminal response compliance. The attempted65²forcing→3²coarse change did not resolve nonprogress; debugger points to physics with integration step0. Static1s supported config works, but convergence/stability/calibration remain a new explicit validation obligation. Watchdog experiment is not evidence HAZARDIA retains capabilities under fault.

Coupling protocol amendment before using flood consequences in decisions: freeze meaning of gridded versus section/averaged Q, temporal sampling/window/Q0, reach mapping/drainage area/CRS/datum, actual cell areas, tconc method and loss of hydrograph information in triangular-volume surrogate. Quantify discrepancies and uncertainty; do not label syntheticQ100 as a calibrated recurrence or infer arrival times. Domain-expert review and licensed real case required before claims of physics skill. Keep scenario-only numerical feasibility separate from an approved risk/effect model.

Pilot tuning remains separate from held-out evaluation: V-valley toY-valley, extraction thresholds, manual flag and small-volume profile changes are declared responses to known failures. Original inputs/results are retained. No causal benefit or significant improvement estimated. Post-hoc1%volume-residual artifact check is diagnostic, not a preregistered physical-accuracy criterion. NaN NoData handling uses explicit GDAL masks; previous checker defect retained with superseding record. Dataset discovery found official GitLFS examples without explicit license; rights and payload remain BLOCKED, not assumed covered by model EUPL.

## Real-terrain pilot amendment — 2026-10-15
Run `m0-real-terrain-20261015T142405Z`, E-M0-017…022, report `reports/M0-real-terrain.md`. This remains M0 pilot, no H1–H3 evaluation. Actual DSM and dated Sentinelbackground replace synthetic terrain in a REFlEx execution test; discharges remain explicitlyhypothetical. AOI is not a certifiedcompletecatchment and backgroundimagery is not observedfloodtruth. Dataset selection preregistered independently of successfulmodelappearance; later halo/merge remedy is explicitlypost-failure tuning, not held-out validation.

Keep primarypaper/source-based Q0bankfull semantics separate from arbitrary initialHMCsample; native triangle/transitvolume is not an estimate guaranteed equal to full-event hydrographintegral. Main-study qualification still needs realinputs/calibration/expertreview. Geographiccellarea measured and approximated with disclosedmeanerror, DSMcanopy/buildingbias retained. Do not infer sub-meter accuracy from fractional outputdepth.

Original REFlEx completequalityFAIL despite exit0 and existing69files: twoemptyHANDs. Two-line isolatedcompatibilitypatch tested with all69HAND readers and commonpixelregression; extra validpixels could affect hazardextent and need independentvalidation. Baseline, halo-only mergefailure, failedcroppingremedy and recorderfailures retained. Future regression: singlepixelreach at workingwindowedge, wholeAOIedge, branching/topology, multiplegeographies, empty products, nodata reprojection and boundedmerge. FuturecontrolledREFlExreplay must also address randomoptimiserstart; no exactreplayclaim here. SyntheticHMCdt4/2/1 is sensitivity only, no convergence/stability/calibrationskill declaration and no producttimingdistribution.

## Runtime placement protocol amendment — 2026-10-15
User requires one Linux execution machine, initially HAZARDIA-M0-ARM64 (ADR-0002). Native Mac runs remain historical portability controls, not production topology. Future main experiments run acquisition/preparation, both hazards, solver and numerical verification in the same declared VM/server; distinguish optional display-client performance. Separate environments and bounded processes remain inside the same machine. Placement decision is user preference, not an empirically proven performance superiority claim.

M0 run `m0-unified-vm-20261015T150415Z` repeats real preprocessing/REFlEx with the disclosed compatibility copy, synthetic fire/HMC and rendering inside VM. Cached source assets reused with full hashes; guest HTTP range responses match source prefixes, no fictitious new full download. Same scenario limitations and post-hoc patch status as prior pilot. No H1–H3, physical qualification, UI performance, multi-thread guarantee or M1 claim.

## M0 contract conformance pilot — 2026-10-15
Original plan retained; exploratory Control Room extensions deferred by user. Runs `m0-contracts-20261015T152857Z` and superseding `m0-contracts-20261015T153248Z`, E-M0-026…028. Eleven versioned schemas/examples satisfy the M0 fixture gate;124checks incl78negatives pass and repeat offline after correcting two improperly generated grid-negative examples.113inputs hashed before formal validation. Same author designs schemas/oracles; separate isolation assertions detect aliasing but are not independent scientific review. Finite authored fixtures, closed one-record-per-kind context, fictional permissions/effects and metadata time assertions do not support real safety, model skill, deadline, generalization or RQ1–RQ3 claims. Original117PASS/2FAIL retained with diagnosis; do not count repeated deterministic checks as independent samples. Real previous artifact reference checks identity only. Future adapters must validate actual array/raster/time/rights contents and broader adversarial cases.

## Architectural extensibility decision — 2026-10-15 (no empirical result)
The user confirmed AR-EXT-01/ADR-0004 before M1: keep explicit versioned boundaries for observation acquisition, temporal territorial state, physical/future AI prediction, evaluation, model identity/approval/rollback, optional specialized-agent coordination and domain decision policies. Motivation is to preserve future evaluation opportunities without adding functionality, infrastructure, empty abstractions or current dependencies. Current RQ1–RQ3, M1 order, approved CIMA engines, safety/authorization and performance targets remain unchanged.

Future evidence must distinguish design review from exercised extensibility. PLAN/CHECKLIST AT-EXT-01…05 stage actual adapter/source/dependency checks in M1, state/fusion in M2, and replacement without decision-core modification in M3. Record code/config diffs, immutable contract/version IDs, real vs test-adapter identity, rejected incompatible capabilities, run environment and workload. No substitute model's accuracy follows from matching a contract. Historical model scoring remains M7 with subsequent observations excluded from the prediction cutoff. Real AI/Twin/agent evolution is separately authorized future work, not an added main-study treatment, RQ or M7 deliverable. Same-author review and finite substitutes limit any later generalization; no claim of demonstrated extensibility from interfaces alone. Decision record D-ARCH-001 in EVIDENCE is explicitly nonexperimental.

## Scope clarification — 2026-10-15
User confirms wildfire/flood as the only current application domains. The seven conceptual extension points preserve future options, not additional implemented features or experimental treatments. Maintain the existing research questions and wildfire/flood study plan; do not add an extensibility/AI/Twin/agent efficacy claim or new study scope from this clarification.

## Real hydrological source feasibility pilot — 2026-10-15
Run `m0-hydro-data-20261015T154619Z`, E-M0-029…032. Selection preregistered by region/public rights/data identity before model score, with bounded32MiBremote payload and a declared decompression-only ceiling amendment. FOCAv4/SIR rights and actual small payloads checked; three named nearby historical basins, modern station offsets, incomplete formerAOI and non-overlapping annual/subdaily periods measured. This diagnoses suitability threats, not improved prediction. Public daily prevalidated rain is parsed with explicit zero/missing symbols and matched to monthly published sums; no arbitrary disaggregation. Empty public ratingCSV and email/CAPTCHA subdaily procedure remain negative/blocked evidence.

The next-test protocol in `reports/M0-hydrological-validation-protocol.md` distinguishes matched gauge/terrain/forcing, bankfull-referenceQ0/tconc, calibration/sensitivity and held-out hydrograph/inundation comparison. Main thresholds, event/split and source timing must be fixed after availability audit but before scoring; no current skill or main-study result. Proposed2013–2025data request is an acquisition window only, not a preregistered main-study split. FOCAhistorical annual maxima and modern source data cannot be merged by name or assumed stationary. Dataset reference boundaries are not surveyed truth; provider metadata/geolocation/validation uncertainty remains. No actual data request was sent. H1–H3 and real-case trials NOT RUN; no architecture extension implemented.

## Geographic study scope update — 2026-10-15
User selects Abruzzo for the primary wildfire/flood examples. This is an externally specified study-region choice, not selection on measured model performance. Particular events/basins/AOIs and the historical evaluation split remain to be fixed after availability/rights review and before main scoring. Tuscany/Bagnone and synthetic runs remain declared feasibility pilots; their maps, failures and post-hoc tuning must not be relabeled as Abruzzo results or held-out validation. Original RQs, geographic portability and synthetic cross-territory tests remain unchanged. Do not require completed historical skill validation to retrospectively redefine the M0 feasibility gate.


## M1 pilot checkpoint — 2026-10-15

E-M1-001…005 records real adapters/normalized inputs/products, bounded supervisor and content verification on preregistered small Abruzzo geography in the single Linux VM. This supports an executable software integration account, not H1–H3 outcomes. Historical ERA5 available-at2026 is expressly retrospective; no anticipatory forecast claim. Keep failed trials, explicit syntheticfuel/ignition/moisture/rain/Q0/soil and unqualifiedcatchment/DSM biases. The REFlExminimumdepth search-bound change is post-failure tuning with an unchanged numerical diagnostic, not a calibrated physics intervention or held-out validation. Same-seed equality on a narrow fire fixture is a replay result, not extra statistical trials. Main baselines/ablations, ensembleforecast decisions, independenthistoricalskill, secondmachine, p95/60s, UI and six-capability evaluation remain NOT RUN under original milestone plan. No paper agent, new RQ, Twin/AI/agent framework or manuscript conclusions added.


## M2 checkpoint — 2026-10-15
E-M2-001…003 tests shared territorial/event/weather/effect/accessibility boundaries, not mainRQ hypotheses. Syntheticdetections/exposure/resources/effects explicitlyauthored; positivecellselection deliberatelycontrolled, not observedpopulation/event sampling. ActualM1rasters/ERA5 reused read-only. Scoreminimum is not calibratedprobability; oneRTreeworkload is not scaling/p95evidence. Preserve firstoracle/harnessfailures and post-failurecorrections. Operational/empiricalmodels unqualified; M3decision/UI not started.

## M3–M7 pilot amendment — 2026-10-15

See E-M3, E-M5, E-M6, E-M7 and reports/M3-dashboard.md through M7-validation.md. Concrete software exists and has executed tests; main RQ hypotheses remain unconfirmed. Timing trials reuse a small frozen physical context and authored effects: not independent event samples. M5 expected/worst choices coincide; report this negative distinction. The short-watchdog failure and UI/mobile failures precede corrections and remain immutable evidence. The rule-based capability vector has a baseline ordinal loss of information (further forecast loss can retain DEGRADED); report causes and decision loss, not only a scalar. General capability optimization/candidate portfolios are incomplete.

CEMS observation acquisition2020/2013 and actual current2026MET forecast are source availability results. They must not be scored againstJuly2024conditional products. Pressure at sea level is not surface pressure; missing radiation is unknown, not zero. Publication/update time is not automatically a model cycle or evidence our system had the data then. Physical/historical/operational qualification remains blocked.

Final UI/stability and bounded scaling are engineering pilot evidence;100kdisplay failure and unsupported24/48slot cases constrain claims. Additional QA stress may overlap the soak: record that co-load as a validity limitation. Working editorial scaffold research/PAPER-NOTES.md and results/README.md do not establish novelty, usability effectiveness or publication readiness. Same-author recorder remains the explicit role; no autonomous paper agent or external communication.

## Open-Meteo conditional forecast pilot amendment — 2026-10-16
Run openmeteo-20261016T060251Z: user-authorized real point forecast on map and future native conditional simulations in sameVM. Choose the first full futureUTC hour independently of rainfall/success; fixed ignition/fuel/moisture/soil/Q0 remain synthetic. Record unknown model initialization separately from first-seen availability; do not fabricate issue time from HTTP/generation timing. Align previous-hour accumulation/mean to simulation interval. The first dry native result exposes an empty-optimizer validation defect and legacy pressure-unit mapping; preserve that run, declare post-failure corrections, rerun without rain/threshold tuning. Native zero-map acceptance requires upstream runoff eligibility and independent zero/finite raster checks; it is not evidence of no real flood. Source availability/native execution do not establish H1–H3, forecast skill, false-alarm performance or operational warnings. ADR-0010 and final report/ledger carry measured outcomes only.


## Pilot input geografici distribuiti — 2026-10-18
Run dynamic-fire-domain-20261018 separa esecuzione nativa/input reali dalla loro qualificazione. Sono tuning successivi ai fallimenti: margine lettura COG, range budget, istante di disponibilità dell’inventario e fallback fonte OSM. Senegal scelto per richiesta geografica dell’utente, poi punto non-fuel rifiutato e punto vegetato scelto esplicitamente per probe: non è selezione held-out né evidenza di generalizzazione. Le quattro esecuzioni72h formano due confronti con seme/meteo/terreno congelati; replay uguali non sono repliche indipendenti. FFMC iniziale85, crosswalk WorldCover e fuel_removal introducono incertezza e trasferimento ecologico da qualificare. Edificato satellitare non identifica servizi/popolazione; priorità/beneficio restano proxy di ricerca. Nessuna H1–H3 confermata, nessuna efficacia reale o superiorità scientifica dedotta. Definire casi, inizializzazione/stagionalità, sensibilità/ensemble e criteri prima della valutazione storica.


## Fonte Vetica — pilot prospettico, 2026-10-18
La notizia proposta dall’utente seleziona il luogo, non offre ground truth. Il punto cartografico dell’EnteParco è un innesco rappresentativo fissato prima dei run, non una localizzazione osservata. Prove72h future con meteo congelato e stesso seme: assenza, fuel removal100m immediato e dopo1h; nessuna ottimizzazione post-hoc dei parametri per produrre più incendio. L’intervento immediato è volutamente favorevole e non è una policy operativa praticabile dimostrata.2realizzazioni non sostituiscono ensemble/repliche indipendenti. Fotografia d’archivio e dati2017 non possono validare2026. Ricostruzione/scoring richiedono veri perimetri e cronologie con date, fuel/moisture e cutoff; nessun claim H1–H3 o skill dalla differenza fra i tre controfattuali. Report FONTE-VETICA-20261018 e preregistrazione nel raw.


## Workflow e confronto fisico ottimizzato —2026-10-18
E-WORKFLOW-001…004 registra un incremento tecnico preregistrato, non un nuovo trattamento principale o RQ. Scenari ora indipendenti per richiesta utente, copia esplicita, replay e ricalcolo distinti da checkpoint. Il solver ottimizza un proxy; il vincitore della coppia viene deciso dopo il replay PROPAGATOR sulle stesse priorità/input congelati. Riportare anche un riferimento vincente e qualsiasi divergenza proxy/fisica; non etichettare automaticamente la proposta come migliore globale. Le due coppie con stesso seme/input sono ripetibilità e non repliche indipendenti. Fuel removal, piena disponibilità72h, buffer e pesi espliciti restano ipotesi. Dataset OSM mancante e WorldCover parziale non autorizzano stime di popolazione/usi. RQs/qualificazione/held-out del piano originale invariati.


## Ruolo del riferimento MyDewetra — chiarimento 22 ottobre 2026
Il paper è una fonte per l’architettura d’integrazione di applicazioni, dati e servizi, non un obbligo di parità funzionale. Non confondere richiami algoritmici, esecuzione di simulatori e pubblicazione dei risultati. Il paper non specifica un adapter PROPAGATOR; tale mancanza di dettaglio non dimostra assenza nel prodotto completo. Manteniamo RQ, baseline e qualificazioni del piano HAZARDIA: nessun claim di originalità o superiorità nasce da questa mappatura. Report reports/MYDEWETRA-RIFERIMENTO-ARCHITETTURALE.md, revisione documentale/statica mydewetra-architecture-20261022. Nessuna modifica del manoscritto né nuova evidenza sperimentale.


## Verifica presentazione25ottobre2026
UI-LAYER-CONSOLE-20261025 distingue gate di rappresentazione da qualificazione scientifica: soglia cartografica edifici15 nel Monitoraggio non filtra input/esposizione del modello. Riordino usa nodi originali e dati acquisiti; categorie/legenda non attestano copertura completa. Protocollo finale dichiara precedenti controlli esplorativi e tentativo Node VM fallito. PASS client/UI e backend osservazioni; NOT RUN benchmark/replay fisici. Conservare FAIL REFlEx e gate M0–M7. Report `reports/LAYER-CONSOLE-20261025.md`.
