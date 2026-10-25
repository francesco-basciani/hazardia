# HAZARDIA — Consolidated Requirements Specification v1.4

**State:** normative requirements baseline. M0–M4 technical fixture gates and M5/M6 controlled software slices have executed evidence; the local dashboard is available. Full P0/research-release completion remains BLOCKED and is tracked exclusively in CHECKLIST.md. Controlled replay and observed software performance do not qualify physical effects, historical skill or operational use. Priorities: P0 required for research release, P1 post-research additions. The reference to real engines means *actual execution* rather than placeholder screenshots. A capability unavailable due to input access must be reported BLOCKED; never silently replaced by a mock.

## 1. Scope and actors

- Platform identity: HAZARDIA means **Hazard-Aware Adaptive Resource and Decision Intelligence Architecture**. Platform branding and general descriptions remain hazard-neutral; specific hazard names belong to the corresponding modules. User reconfirmation 2026-10-17 preserves the original extensible architecture and does not expand current implementation scope.
- Hazards: wildfire and flood in V1, validated separately before joint cross-region allocation. Other hazards may be added via adapters but are not release acceptance targets.
- Actors: researcher (configures runs and evaluates), decision analyst (builds and compares plans), regional coordinator (controls own resources), suprarregional coordinator (proposes transfers), human authorizer (authorizes modeled real-world operations). No dispatch or evacuation automation.
- Time horizons: real-time-ish response with rolling-horizon recomputation and 60 s **decision response budget**; preventive prepositioning is also required. Physical model simulation latencies are separately tracked.
- Territory: configurable geographies worldwide, including cross-border basin and independently scoped administrative authorities. User-confirmed primary Italian wildfire and flood examples: **Abruzzo** (2026-10-15); specific AOIs/basins/events selected after source/rights/coverage audit, not assumed calibrated. Previous Tuscany examples remain historical feasibility evidence. User reconfirmation (2026-10-16): Abruzzo is the current pilot, not the geographic boundary of the product; the target includes all Italy and international territories, explicitly Senegal. Geographic portability and cross-territory tests remain required. Real Senegal deployment/physics qualification requires its own source, rights, coverage and calibration assessment; synthetic transfer tests do not establish readiness there. Territory-specific map, weather, resource and authority settings must remain explicit replaceable configuration; Italian/European provider coverage must not be assumed abroad.
- Single Linux execution machine: initially UTM VM HAZARDIA-M0-ARM64 on the MacBook. All HAZARDIA data processing, fire/flood engines and future backend/jobs/solver/dashboard build and service run inside that VM. Mac is the hypervisor/development/display client, with no required native scientific runtime. Preserve portability to a future Linux server and hardware independence. No mandatory paid technology.

## 2. User scenarios (SC)

| ID | Observable goal / expected response |
|---|---|
| SC-01 | Analyst configures a geographic profile, imports satellite plus weather data and receives a versioned georeferenced hazard scenario or typed error. |
| SC-02 | Analyst independently executes PROPAGATOR for wildfire and HMC + REFlEx for flood (if feasible), with provenance and real output files. |
| SC-03 | Analyst compares no-action, ground, aerial, and mixed interventions for the same wildfire or admissible flood strategies; maps synced by AOI/time and matched weather, with impact and uncertainty deltas. |
| SC-04 | Two regions, simultaneous wildfire and flood, share at least one appropriately qualified/authorized resource; competing allocations cannot double book. |
| SC-05 | Wind/precipitation forecast revisions increase predicted exposure; system creates an alert, reevaluates, and compares early intervention with status quo. |
| SC-06 | Lose a resource, model job, sensor/feed, or environmental assumption; preserve safe functions, recompute or abstain, show six capability service states and decision loss. |
| SC-07 | Replay Italian historic fire and flood observations separately, check model skill and limitations, avoiding future-information leakage. |
| SC-08 | Switch Italy to synthetic Senegal River profile with no decision-core changes, including alternate CRS/time zone/source and cross-border governance. No claim of local model calibration. |
| SC-09 | Human approves/rejects a proposal in a *modeled* workflow with immutable record; no external dispatch. |

## 3. Functional requirements (FR)

| ID | P | Contractual behavior |
|---|---|---|
| FR-01 | 0 | Register AOI, CRS, units, time zone, source policies, administrative jurisdictions, calibration metadata, missing-data policy as validated TerritoryProfile. |
| FR-02 | 0 | Acquire/cache satellite observations and preprocessed products via replaceable connectors; record acquisition timestamp, sensing timestamp, coverage, native resolution, license and checksum. |
| FR-03 | 0 | Cluster and track events across time/sensors without merging unrelated incidents; ambiguous associations explicitly marked; compare clustering/fusion against simple baselines. |
| FR-04 | 0 | Fuse observations conservatively accounting for sensor dependence/uncertainty and conflicting evidence; no naive confidence inflation. |
| FR-05 | 0 | Track sensor/feed health (staleness, outage, coverage, disagreement) and make health available to service-state logic/UI. |
| FR-06 | 0 | Acquire weather history, forecasts and ensembles (wind, precipitation and appropriate supporting variables); version issue-time, valid-time, units, source and spatial resolution. |
| FR-07 | 0 | Prepare/validate hazard-specific model inputs; run real wildfire and flood simulation jobs separately, register run IDs, versions and output validity. |
| FR-08 | 0 | Separate hazard evolution, physical suppression/mitigation where modeled, impact-only interventions, and exposure/vulnerability effects. Never claim flood rescue changes water flow. |
| FR-09 | 0 | Represent population/infrastructure exposure, vulnerability and access/road constraints with provenance and uncertainty. |
| FR-10 | 0 | Model resource type, skills, qualifications, equipment, position, home authority, schedule, fatigue, maintenance, autonomy, consumables, cost, reliability and capabilities per hazard. Unknown fields are not unconstrained. |
| FR-11 | 0 | Support hierarchy of regional ownership plus suprarregional transfer proposals; no commitment without matching authorization state and donor capacity. |
| FR-12 | 0 | Implement versioned solver interface, initial constrained solver, hard-constraint validator external to solver, robust multi-scenario comparison and rolling horizon. |
| FR-13 | 0 | Return multiple candidate strategies or classified non-success (PROVEN_INFEASIBLE, TIMEOUT_UNPROVEN, INVALID_INPUT, SAFETY_UNVERIFIED, DEPENDENCY_UNAVAILABLE) with explanations. |
| FR-14 | 0 | Within 60 seconds of a **accepted decision request** provide safe validated proposal or classified status on declared benchmark workload; separately time queue, retrieval, simulation, verification and UI. |
| FR-15 | 0 | Define six capabilities (safety, situational awareness, allocation, regional coordination, forecast, explanation), per-capability NOMINAL/DEGRADED/UNAVAILABLE with rule-driven transitions and recovery. |
| FR-16 | 0 | Under resource/data/infrastructure/environment degradation, minimize loss of prioritized capabilities, recompute safely or abstain; report both service quality and outcome impact. |
| FR-17 | 0 | Monitor new forecast/data revisions and emit *impact-based* georeferenced alerts with uncertainty, evidence, priority, recommended review window, acknowledgment and resolution; suggestions require human review. |
| FR-18 | 0 | Local web UI: map/layers, scenario builder, resources, comparison 2+ synchronized maps, timeline playback, differences, charts, provenance, alerts, service states and proposal authorization. |
| FR-19 | 0 | Preserve immutable experiment manifest (inputs, versions, seeds, data rights, execution environment), metrics and decision trail; export reproducible evidence without secrets. |
| FR-20 | 0 | Support independently evaluated preparedness/prepositioning strategies using the same admissibility rules and territorial constraints. |
| FR-21 | 0 | Simulator and connector worker jobs are isolated and bounded; failure in flood must not falsely invalidate unaffected wildfire results; preserve last valid output only within validity window. |
| FR-22 | 0 | Operate locally without paid/cloud services on one Linux machine, initially the existing UTM VM: data pipeline, both hazard simulators and future backend/jobs/solver/dashboard build and service co-located. No native macOS scientific dependency. Preserve process isolation and portability to a future lab Linux server. |
| FR-23 | 1 | Add user-submitted field reports, subscriptions/notifications, external interoperability, multi-user collaboration and eventual safe synchronization in separate extensions. |

## 4. Nonfunctional / quality scenarios (QR)

| ID | Stimulus / measurable acceptance (pre-operational research) |
|---|---|
| QR-01 Safety | Invalid capability, overlapping assignment, unauthorized transfer or unknown essential safety field => no 'operationally approvable' strategy; every published candidate independently checked. |
| QR-02 Decision timeliness | **Per-request deadline:** every accepted decision request must transition within 60 seconds (monotonic wall clock, including verification and response serialization) to an admissible independently verified strategy **or** typed terminal response (`INFEASIBLE_PROVEN`, `UNVERIFIED`, `TIMEOUT`, `ERROR`, `BLOCKED`). A candidate solution after timeout cannot be labeled validated. **Statistical performance target:** on a pinned benchmark workload, p95 for verified useful strategies or typed terminal responses <=60 seconds across >=30 repetitions, with success/failure/timeout rates reported separately. A timeout response counts as deadline-compliant for termination but **not** as success in producing a useful strategy. Record individual latency, p50, p95, worst case and host spec; target unverified until measured. Queueing from request acceptance is included; fresh physical simulator computations not required in this budget unless explicitly requested. |
| QR-03 Fault containment | Terminating flood simulator worker leaves fire runs retrievable; flood marked DEGRADED/UNAVAILABLE according to validity; status change recorded. |
| QR-04 Reproducibility | Given fixed artifacts, pinned version, seed and config: deterministic outputs where engine supports it, otherwise stable statistics with declared tolerance; replay does not require paid service. |
| QR-05 Interoperability | Common outputs preserve CRS, timestamps, native units, uncertainty and provenance; reject nonconvertible time/space/units. |
| QR-06 Comparison integrity | Side-by-side compared strategies use identical initial condition/weather/seed policy, AOI and temporal scale, or UI flags mismatch and forbids causal comparison. |
| QR-07 Security | Localhost by default; no open inbound remote access, secrets in repo, public dispatch or unapproved exports; before lab deployment require review of identity, TLS, authz, logs, backups and institution policies. |
| QR-08 Geographic transfer | Two synthetic geography profiles execute same core workflow unchanged; unsupported local data/calibration triggers explicit BLOCKED status, not Italian defaults. |
| QR-09 Observability | All runs have correlation IDs, state transitions, elapsed time, input hashes and typed errors; no silent retries. |
| QR-10 Alert quality | Replay includes true-warning, forecast false-alarm, obsolete forecast and unsupported-impact examples; record lead time, false-positive rate and evidence validity without unjustified accuracy promises. |

## 5. Acceptance / definition of complete research release

- All P0 requirements have executable evidence with PASS, or explicitly documented FAIL/BLOCKED which prevents claiming completion. P1 deliberately out of research-release scope.
- Real simulator for each of wildfire and flood; if HMC+REFlEx chain proves impossible, **STOP and request user decision**; do not silently switch to LISFLOOD-FP/HEC-RAS.
- Single-domain fire/flood and joint multi-region scenario; at least one correctly qualified shared resource, interventions, proactive weather event, graceful-degradation case, full UI comparison, recorded authorizations; historical Italian case for each domain.
- Replication bundle, benchmark results and limitation statements; research release is not operational certification. User must explicitly authorize any GitHub push, deployment, real data upload or external incident action.

## 6. Known open, evidence-dependent decisions

Exact Mac hardware; simulator installation constraints/licenses; HMC↔REFlEx coupling; source access and licenses; weather/impact source quality; risk weights, safety thresholds, operational authority policy, benchmark sizing and simulator timing. Codex may choose implementation details inside agreed contract, but cannot independently redefine safety thresholds, fabricate calibration or substitute core components without approval. See `SPEC.md § Data and simulators` and `SPEC.md § Decision model`.

## 7. Evidence-linked completion control (normative)
`CHECKLIST.md` is the authoritative **status ledger** for each requirement and milestone. The checklist cannot replace this specification, tests or raw evidence. Each acceptance item MUST have a stable ID, expected outcome, observed result, test command or manual procedure, evidence link(s), execution timestamp, code commit, environment, and reviewer status. Status values: `NOT STARTED`, `IN PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, `NOT RUN` (verification not executed); only `PASS` with recorded evidence is eligible for completion. No completion by assertion or checkbox alone. Distinguish P0 first release and P1 later work. Every P0 entry must link to the acceptance tests in `CHECKLIST.md § Traceability`. No empirical status is PASS at document initialization.

### 7.1 Concrete contract examples gate
At M0/M1 freeze versioned, valid and deliberately invalid examples for territory profile, satellite observation, weather issue-time and validity, hazard simulation input/output, resource capability, intervention effect, decision request/response, authorization and experiment manifest. For each record fields, units, CRS/time conventions, missing/unknown semantics, error codes, schema version and provenance; test round-trip compatibility and negative cases. Framework-language or serialization choice is deferred to feasibility ADR, not the semantics. Schema incompatible changes require ADR, migration strategy and relevant tests.

### 7.2 Decision parameters and safety profiles gate
Keep **hard safety invariants** separate from configurable objective preferences, robustness balance, risk attitudes and alert thresholds. Define `profiles/research/` with explicitly **synthetic, non-operational** parameter fixtures: weights, robust scenario budget, planning horizon/step, resource bounds, warning sensitivity and provenance. Require deterministic validity checks and scenario sensitivity experiments before using any values. Do not invent jurisdictional safety thresholds or reuse a research weight as an operational policy. Operational profiles are BLOCKED pending domain-expert approval and calibration.

### 7.3 Experiment identity and immutable provenance gate
Every scientific or performance run MUST have a stable `run_id`, parent scenario ID, Git SHA, working-tree dirty flag, dependency/simulator versions, configuration+dataset hashes, random seeds, machine/OS/architecture, start time, commands, actual artifacts and test outcome. Record in immutable `experiments/runs/<run_id>/manifest.*` and refer to it from `research/EVIDENCE.md`; large inputs may remain external with immutable checksum and access restrictions. Correct mistaken records by superseding them with a linked new run, not editing history. No fabricated or recycled run IDs.


---

## Architecture

## Principles
Modular core and isolated simulator workers; one first-party local backend/UI; hazard-neutral decision primitives; domain-specific simulation physics; satellite-first but not satellite-only; no dependency on commercial hosted services. Prefer Python for core/adapters if feasibility supports it; UI technology remains a bounded M0 choice; do not hard-code frameworks before license/platform audit.

### AR-EXT-01 — Architectural extensibility (user-confirmed, before M1)
**Scope clarification confirmed by the user (2026-10-15): current development and validation focus exclusively on wildfire and flood. The seven conceptual extension points remain architectural possibilities only; they do not create seven implementation workstreams. Apply compatibility checks only to the concrete original-plan components, without adding Twin, agent, AI-model, registry or extra-domain deliverables.**
HAZARDIA must preserve compatibility with a future temporal territorial Digital Twin, additional satellite/IoT/ground/drone sources, physical and AI predictive models, controlled model evaluation/evolution, specialized agents and additional domains. These are extension opportunities, not current functionality or new M1 deliverables. Keep acquisition/normalization, territorial state, hazard prediction, impact assessment, decision/resource allocation, adaptation and visualization separate through explicit versionable contracts; consumers must not depend on simulator internals, fixed providers, territories or incidental hazard-specific formats.

| Conceptual extension point | Responsibility / existing boundary |
|---|---|
| ObservationProvider | Replaceable acquisition and normalization, with sensing/availability time, quality and rights; current connectors. |
| TerritorialStateProvider | Access/update temporal territorial snapshots with provenance and observation cutoff; later Digital Twin compatibility, without rewriting past snapshots. |
| PredictionModel | Execute a declared physical or future AI predictor via adapter; identify supported variables/hazards, units, validity, uncertainty and qualification, without implying physical interchangeability. |
| ModelEvaluation | Compare predictions against subsequent attributable observations, keeping prediction cutoff separate from later scoring; existing research validation responsibilities. |
| ModelRegistry | Future model identity/version, validation, approval and rollback; use current manifest identity now, no registry service required. |
| AgentOrchestrator | Potential future specialized agent coordination through the same contracts; no dependency on an agentic runtime. |
| DomainDecisionPolicy | Domain-specific objectives, hard constraints, intervention capabilities/evidence and decision criteria; preserve hazard-neutral solver boundary and independent verification. |

These are conceptual responsibilities, not mandatory interface/class names. Create no empty abstractions, extra services or premature microservices; implement only boundaries justified by concrete authorized milestone requirements. A Digital Twin must not replace the decision engine; agents/models must not bypass hard safety, qualification, temporal validity or human authorization. Maintain all approved V1 requirements, the CIMA engines, robust solver-pluggable rolling horizon, graceful degradation, alerts/comparison, scientific traceability, responsive UI/performance, geographic/platform portability and single-VM local-first execution. No full Twin, AI agents/framework, continuous training or new domains are authorized by this requirement.

The frozen M0 examples are a versioned starting point, not universal model/source/domain enumerations. Extend via declared capabilities and explicit version/migration/test policy (§7.1, ADR-0003), never by silently accepting unknown safety semantics or modifying old run evidence. Verification `AT-EXT-01…05` is staged in PLAN and CHECKLIST: assess real adapter contracts/source separation/dependencies in M1; defer the executable unchanged-decision-core replacement to M3, where that core exists. An interface alone proves no extensibility. ADR-0004 records rationale and limits.

## Logical flow
`Satellite/Weather/Territory connectors → ingestion & QC / event tracking → hazard-specific input builders → simulation job orchestrator → PROPAGATOR or HMC→REFlEx worker → geo-temporal hazard products → impact/exposure assessment ↔ scenario manager → robust constrained solver ↔ independent verifier ↔ capability-aware adaptation → alert/authorization API → local geospatial dashboard`. Simulator outputs and forecasts are versioned, and decision engine may use valid cached forecasts when new simulation too slow. Simulators are advisory to decisions, not intrinsically real-time.

## Major components and contracts

| Component | Accepts | Emits | Error / isolation |
|---|---|---|---|
| Territory registry | validated TerritoryProfile | versioned AOI/CRS/time zone/source/jurisdiction config | INVALID_PROFILE |
| Observation connectors | source query, credentials outside repo, time bounds | ObservationBundle, coverage, freshness, rights | SOURCE_UNAVAILABLE/STALE/PARTIAL |
| Event tracker/fusion | ObservationBundle | EventHypothesis + confidence provenance | AMBIGUOUS_ASSOCIATION |
| Weather manager | AOI, issue/valid windows, scenario member | WeatherEnsemble | STALE_FORECAST/UNAVAILABLE |
| SimulationJobAdapter | SimJobRequest (type, AOI, grid, weather, input URIs/hashes, intervention config) | JobReceipt/status and HazardProductBundle | job deadline, failed worker, invalid inputs |
| Impact assessor | hazard + exposure/accessibility + interventions | ImpactDistribution + caveats | UNSUPPORTED_EFFECT |
| Resource registry | resource/update/authority | audited ResourceSnapshot | CONFLICT/STALE/UNQUALIFIED |
| Solver interface | DecisionProblem + budget and seed | candidate strategies + termination reason | TIMEOUT_UNPROVEN/INFEASIBLE |
| Safety verifier | candidate + authoritative constraint snapshot | VALID/INVALID/UNKNOWN with rule IDs | UNKNOWN is never VALID |
| Adaptation manager | service health, events, candidates | capability vector, recovery plan and classifications | DEGRADED/UNAVAILABLE |
| Alerts | forecast revision, impact deltas, verification | versioned Alert (OPEN/ACK/UPDATED/RESOLVED/EXPIRED) | unverified advisory status |
| UI/API | scenario ID, user role, filters | map layers, comparisons, decisions, evidence links | safe refusal, not silent success |

## Minimum versioned entities
`TerritoryProfile(id, polygon, crs, tz, jurisdictions, sources, datum, calibrationRefs)`; `Observation(id, variable, geometry, sensedAt, ingestedAt, coverage, resolution, license, uncertainty, checksum)`; `WeatherForecast(issueAt, validAt, ensembleId, grid, uncertainty)`; `HazardScenario(type, territory, initialState, forecastRefs, runRefs)`; `HazardProduct(type, fieldNames, units, grid, timestamp, uncertainty, provenance)`; `Resource(id, abilities, qualifications, region, shift, maintenance, consumables, movement, reliability)`; `Intervention(type, intent, resourceRef, startsAt, duration, physicalEffectModel?, impactEffectModel?, evidenceGrade)`; `DecisionProposal(assignments, objectives, constraints, robustness, qualityByScenario, verifierStatus, authorizations, rationale)`; `CapabilityProfile(states, reasons, updatedAt)`; `Alert(...)`; `RunManifest(versions, hashes, environment, seeds, outputRefs)`.

All timestamps ISO-8601 UTC internally with original time zone metadata; spatial CRS carried explicitly and transformed with logged accuracy/units. Never treat cells from different raster grids or different valid times as directly comparable. Missing mandatory fields fail validation.

## Execution boundaries
- One Linux runtime host: all project processes, data/cache, scientific preparation, simulator workers and future core/API/solver/dashboard build/service execute inside HAZARDIA-M0-ARM64. Use isolated processes and separate dependency environments within this same VM. Mac is the VM host and development/display client; a browser may display the VM-served UI, but no native Mac scientific component is required. No shared host source/data directory is a runtime prerequisite. Upstream source/config/data remain separately versioned/licensed.
- Long model jobs are asynchronous and idempotent by stable run-key; worker state QUEUED/RUNNING/SUCCEEDED/FAILED/TIMED_OUT/CANCELLED. Retries capped and logged. Output filenames unique and atomically committed; restart reconciles abandoned jobs.
- Decision-time 60s budget starts when API accepts an *already-prepared* decision request; warn when cached simulations are stale, and mark missing hard constraints UNKNOWN. Track end-to-end ingestion/model times separately.
- Dataset inventory and experiment manifests persisted to local files (e.g. JSON metadata + GeoTIFF/GeoJSON/Parquet as appropriate). Production database choice deferred until measured need. Never make proprietary source mandatory.

## Security and future deployment
Default binds to loopback only. Authentication required for any shared instance, authority-separated roles/permissions, no real dispatch API in research release; lab server requires reviewed institution networking, TLS, auth, backups, risk assessment. GitHub release and lab publication are separately authorized.

## Decisions at M0
Runtime placement now confirmed by user: one Linux VM for the full stack (ADR-0002). Keep separate worker processes/environments inside it. JSON schema serialization, UI framework, licensing and basemap options remain subject to M0 evidence. Limits unchanged; architectural replacements require explicit approval.


---

## Decision model

This is a **specification for implementation**, not a claim of an operationally safe optimizer. Use the simplest correct solver; preserve a pluggable interface.

## Problem sets and timeline
Regions `R`, hazards/events `H`, resources `U`, intervention types `A`, protection objectives/assets `P`, forecast scenarios `Ω`, decision slots `T` of declared duration. Each resource has qualified tasks, schedules, location, maintenance, autonomy/consumables, availability, transfer authority; each scenario provides forecasts and provenance. Rolling horizon: plan over `t..t+K`, commit *nothing operationally* automatically; replan when state/forecast changes, enforce continuity and account for previous commitments.

## Decision variables (initial discrete model)
Binary `x[u,a,h,t]` assignment/activation; `z[u,r,s,t]` region transfer where appropriate; optional binary `y[p,t]` protection/coverage; continuous or discrete `q[h,p,ω,t]` predicted residual consequence if supported by evaluator. Time and effort/consumption variables may be added while maintaining contract. Resource may be assigned at most once per overlapping interval. Decision candidates include a no-action baseline and distinct feasible alternatives when available.

## Hard constraints (independent verifier must repeat)
Qualification and equipment compatibility; availability and maintenance/shift/rest; travel/road access and arrival; fuel/water and service autonomy; safe deployment conditions if verifiable; resource non-overlap; transfer authorization and minimum donor capacity; hazard-specific mission contracts; committed actions and temporal continuity. An absent value needed for a hard constraint => UNKNOWN safety, not implicitly satisfied. Physical model feasibility and operational authority validation are separate gates. A 'suggestion for review' can contain known limitations, but only verified candidates may be marked admissible, and none directly dispatch.

## Preference and robustness
Stakeholder policy defines ordered hard safety invariants, then configurable weights or Pareto priorities on population exposure, critical assets, environmental damage, response delay, cost, service-capability retention and uncertainty. Normalize dimensions with declared units/reference values; never directly equate fire intensity to flood depth. Evaluate each candidate under a matched scenario set. Initial robust objective candidate `J(x)=λ·E_ω[L(x,ω)] +(1−λ)·RiskTail_ω(L(x,ω))` with λ configurable by research protocol (choose risk functional CVaR or max after pilot); additional tie-breaker resource usage. If scenario probabilities untrustworthy, evaluate worst-case set with caveat. All weights/risk parameters are CONFIGURATION awaiting evidence and stakeholder review, not safety defaults. Report frontier and scenario-wise losses to avoid hiding tradeoffs.

## Intervention semantics
Declare `PHYSICAL_EFFECT` only if corresponding simulator and parameterization have justified support. Declare `IMPACT_ONLY` for evacuation, shelter, logistics, accessibility etc; require explicit effect model provenance; `UNKNOWN_EFFECT` cannot score as confirmed improvement. Fire suppression may change simulated fire state where engine supports it. Flood emergency resource allocation normally changes consequence/exposure, not flooding physics, unless explicit hydraulic mitigation is modeled and validated.

## Independent result validation
`ProposalStatus ∈ {VALIDATED_FOR_SIMULATION, UNVERIFIED, INVALID, TIMEOUT_UNPROVEN, PROVEN_INFEASIBLE, DEPENDENCY_UNAVAILABLE}`. A solver FEASIBLE flag is insufficient without separate verifier. Independent validator reports tested rule IDs, data snapshot, unresolved conditions; no assumption of real-world safety or permission from a simulation validity flag.

## Service capability vector and degradation
Capabilities = SAFETY_CHECK, SITUATIONAL_AWARENESS, RESOURCE_ALLOCATION, REGIONAL_COORDINATION, FORECASTING, EXPLAINABILITY. Each in {NOMINAL, DEGRADED, UNAVAILABLE}, with cause, confidence, source age, timestamp. Rules: missing mandatory input to safety => SAFETY_CHECK UNAVAILABLE and proposals nonapprovable; stale forecasts => FORECASTING DEGRADED or UNAVAILABLE depending declared validity window; failed hydraulic worker does not collapse valid fire forecast; outage coordinator => no new cross-region transfer authorization; missing solver => historical results displayed but no newly validated plan. Transitions and recovery require *fresh positive evidence* (no assumed self-healing).

Example fault injections: helicopter breakdown, delayed VIIRS data, REFlEx timeout, new strong-wind ensemble, road closure, regional authority feed disconnection. Measure weighted retained capability vector and resulting decision impact independently; weights justified in experimental protocol, show raw vector too. Do not label merely re-solving as graceful degradation.

## Predictive alerts
On weather-issue revision or significant hazard/impact delta, compute candidate trigger from policy-configured confidence, severity, lead time and exposure. Prevent duplicate alerts by event/area/time/source key; revision rather than uncontrolled repetition. `OPEN→ACKNOWLEDGED→UPDATED/RESOLVED/EXPIRED`; log evidence, triggers, superseding forecasts and human acknowledgments. Alerts may show data quality warnings without suggesting deployment. High-risk operational actions always human reviewed.

## Benchmarks and termination
Decision budget of 60 s on fixed synthetic workload after input acceptance; return independently validated candidate or classified status by deadline. Record p50/p95 across >=30 repetitions, CPU/RAM, scenario count, hazard count, resource count, time slots and solver config. Separate new-simulation latency. A timeout is not an infeasibility proof. Compare static/no-replanning, reactive/no-robust, robust/nonadaptive, independent per-hazard and ablation without capability model.


---

## Data and simulators

## Engines (framework adapters planned; standalone feasibility checkpoints in reports)
- **Wildfire:** `https://github.com/CIMAFoundation/propagator_sim` PROPAGATOR. Evaluate native Python integration vs separate subprocess/service, license, intervention affordances, ensemble seed controls, GeoTIFF and model runtime.
- **Flood:** candidates `https://github.com/c-hydro/hmc-dev` (HMC/Continuum) + `https://github.com/c-hydro/reflex` (REFlEx). **Hypothesis, not proven integration:** inspect exact official input schema, release versions, license and environmental dependencies; run HMC and REFlEx standalone; check whether HMC's runoff/discharge and timing/grid/boundary representations can provide REFlEx-required flood inputs; document conversions and uncertainty. If infeasible stop and request approval before substituting or claiming flood capability.
- Distinguish model *hazard outputs*, *impact evaluation* and *response effectiveness*. Do not invent a temporal flood arrival map from a maximum inundation extent product.

## Satellite-first sources to evaluate, not guaranteed ready
Wildfire: FIRMS VIIRS/MODIS hotspots/FRP, Sentinel-2 optical/burn scars, Copernicus EFFIS where licensed. Flood: Sentinel-1 SAR extent, Sentinel-2 optical/land cover, Copernicus Global Flood Monitoring/GloFAS where appropriate; GPM precipitation, terrain DEM, population/exposure layers, roads. Meteo: publicly accessible weather forecast and historical providers with forecast issue-time and ensemble support; require attribution, coverage, update cadence, quotas, file formats, rights. Sources not required to be satellite-only; models and gauge/rainfall information can supplement. Do not infer a hotspot equals full burn perimeter or satellite flood extent equals future inundation prediction.

## Data contract/quality indicators
Observation footprint, sensing and ingestion timestamps, source, CRS, native spatial/temporal resolution, coverage/no-data, confidence/quality and epistemic caveats, duplication key, license and local checksum. Compare disagreement across sensors without blindly multiplying confidence as if independent. Source catalog reports availability, failures, staleness, update latency, corroboration status. Satellite source is considered inadequate if update gap or resolution means a particular decision claim cannot be supported; mark degraded.

## Territorial configuration
Profiles define AOI, hydro catchment, admin authorities and transfer rules, CRS transformations, UTC local time display, optional sensor/gauge feeds, accepted data licenses, calibrated model parameter references and gaps. Minimum transferability test: two synthetic Italy/Senegal-like profiles with different CRS/timezones/jurisdictions, no change to core; real Senegal basin case deferred until dataset/calibration feasibility verified. Synthetic resources may not be labeled operational inventory.

## What M0 must actually inspect
For each upstream project: repository URL and commit/tag, platform/compiler/lib requirements, source license and redistribution constraints, cost, test geometry, setup commands, input/output units and CRS, run duration and memory on actual local host; make PASS/FAIL/NOT RUN truthful. Compare reproducible free isolation for Mac; do not download massive datasets or install system-wide without user permission. Dataset candidates for Italian wildfire/flood and optional Senegal require provenance and explicit training/test split.


---

## UI workflows

Web dashboard on localhost; future remote lab requires security review. Research release must contain working UI, not only API/CLI.

| View | Inputs and required observable outputs | Failure / safety behavior |
|---|---|---|
| Territory & sources | Configure territory/AOI, CRS/time zone, satellite products, weather feeds, freshness indicators and dataset catalog | Invalid sources/coverage visibly flagged, not silently dropped |
| Event monitor | Clustered detections, event identity, observations by sensor and timestamps, disagreements/confidence | Ambiguous event assignments shown as ambiguous |
| Scenario builder | Select historical/synthetic case, hazard, observation cutoff, forecast issue/ensemble, intervention plan and resource snapshot | Warn on incomparable inputs, unknown effectiveness, invalid assumptions |
| Simulation jobs | Select/run real engine, view job status/log/provenance, cancel/retry within limits | Failed/stale jobs explicit; never show mock as real forecast |
| Resource map | Regions, bases, skills, shifts, routes/closures, consumables, ownership/transfer authority | Disqualified resource cannot appear as admissible choice |
| Strategy compare | 2+ synchronized geospatial panels same extent/time/legend, layer controls, timeline playback, scenario-wise impact/uncertainty charts, delta raster where meaningful, no-action baseline | Different source weather/issue-time highlighted; causal attribution disabled unless matched |
| Decision center | Feasible candidate alternatives, scenario robustness, constraint-verification evidence, capability vector and reasoned tradeoffs | Cannot approve unavailable/unverified hard-safety constraints |
| Alert center | Time/location/severity/lead time/confidence/reasons, source revision, acknowledge/update/resolve; compare proactive vs reactive action | Weather alert not automatically treated as operational dispatch recommendation |
| Experiment/research | Run manifest, dataset/model versions, fixed seed, metrics, export and comparison to baselines | Never claim performance without measurements |

## Geographic detail — user requirement 2026-10-15 (FR-MAP-01)
The dashboard must support a genuinely detailed licensed geographic background, legible place/neighbourhood/road context, metric scale, WGS84 coordinates, local place/coordinate search and point inspection with provenance/coverage. Prefer official regional orthophoto consultation where available; retain local satellite fallback. Declare imagery acquisition date, native pixel size and network dependency. Never imply basemap pixel size is simulator grid size, model accuracy or an observation of the simulated event. Named points/nearest streets are contextual; administrative containment, access safety, cadastral and elevation claims need their own qualified source. Bound tile download/cache and visible features; map exploration must not run simulators. Initial validated scope is Abruzzo place gazetteer plus central L’Aquila OSM context; Istat2026 regional overview boundaries are available; province/municipality detail and jurisdictional containment remain NOT RUN. See reports/MAPPE-DETTAGLIO.md and CHECKLIST map-detail checkpoint.

## Physical comparisons and multi-day horizons — user requirement 2026-10-16
FR-MAP-02: when a physical intervention is claimed, compare separately executed model products with matched terrain, ignition/boundaries, weather/time, seed/ensemble and intervention timestamps; preserve provenance and a null-action control. Impact-only evacuation must remain distinguishable and must not visually change hazard physics. FR-HORIZON-01: support simulation horizons measured in days where actual forcing coverage, model/domain behavior and performance have been verified; do not repeat short products or extrapolate beyond coverage. First verified increment is a separate idealized native PROPAGATOR72h lab, not general job/solver support. Multi-day flood mitigation remains NOT RUN pending specific hydraulic case and integration. Scientific calibration and empirical effectiveness remain independent gates. See ADR-0009 and CHECKLIST checkpoint.

## Mandatory early end-to-end UI acceptance
User opens localhost UI, chooses a small recorded fire scenario, runs or loads a *genuine* PROPAGATOR output, selects two matched intervention strategies, sees side-by-side synchronized maps with time control, comparison table and provenance; user can switch to a real flood output when M1 completed. Scenario comparison is a V1 requirement, not deferred. Static demo imagery is not evidence of passing.

## Usability & accessibility
Clear label: OBSERVED / FORECAST / SIMULATED / ASSUMED / STALE / UNVERIFIED, source time and timezone, meaningful legend units, keyboard navigation/basic contrast, offline cached-replay warnings. No fabricated operational status like 'open now' or 'safe intervention'.

## 8. Mandatory performance, responsiveness and user experience (P0, v1.4)

**Performance is an acceptance gate, not cosmetic polish.** HAZARDIA must remain interactive while CIMA simulator jobs execute. Separate metrics for: (i) ingestion/fusion, (ii) simulator queue+execution, (iii) solver/verifier, (iv) HTTP/API, (v) browser rendering and interaction. Never conflate these budgets or claim end-to-end forecast generation in 60 seconds solely because a decision request terminates within that budget.

| ID | Requirement and measurable research-release target | Verification |
|---|---|---|
| FR-24 | Responsive web UI works at viewport widths 375, 768 and 1440 CSS px; no horizontally clipped primary controls or inaccessible actions, with accessible table/map alternatives; keyboard-accessible controls and readable focus states. | Browser tests/screenshots at all breakpoints, keyboard workflow and automated accessibility scan; browser and OS recorded. |
| FR-25 | UI stays responsive to user inputs while satellite downloads, simulations, scenario ensemble evaluation and optimization jobs run asynchronously/cancellably; status, progress when measurable, queued/running/failed/cancelled/completed displayed. | Launch a long-running representative job, pan map, switch panels, cancel job; UI must not freeze, no incorrect completion indicators. |
| FR-26 | Scenario comparison supports synchronized map pan/zoom, common AOI/time/legend, timeline playback, scenario selection, difference visualization and export; large layer rendering is bounded by scale and viewport (tiling, generalization or equivalent as measured). | Match two genuine geospatial outputs; compare equal timestamps and different ones; test mismatch warnings, large fixture and slow device. |
| FR-27 | Data fetching and visualization use bounded concurrency, paging/windowing and caching with source freshness/ETag or equivalent validation; avoid re-running simulator on map interaction. | Cold vs warm browsing traces, request counts, memory-growth and stale-cache invalidation tests. |
| FR-28 | Observability records job queue/execution, per-route latency, map rendering and memory footprint with no secrets or personal information; show useful loading/error/empty states. | Local profiling report with p50/p95, client/server timings, resource consumption and status reconciliation. |

| ID | Quality acceptance scenario / provisional benchmark | Evidence gate |
|---|---|---|
| QR-11 UI interactivity | On declared reference Mac/browser and fixture, local UI non-simulation interactions: p95 <= 200 ms for *input acknowledgement / visual feedback*, excluding network result delivery; map pan/zoom should target >= 30 rendered frames/s during representative interaction. | Browser performance capture >=30 interactions per action, device spec, dataset size; report failed percentile and worst cases. |
| QR-12 API and initial page | On pinned warm local fixture: p95 <= 500 ms for cached/read-only API responses; initial useful dashboard display <= 3 s in 3 repeated cold browser navigations after local backend is already running. These targets are provisional research baselines to recalibrate at M0 (never silently loosen). | Profile cold/warm cases separately, network/cache state, p50/p95 and failures. |
| QR-13 Long-job resilience | User can run, inspect, cancel and retry an isolated model job without blocking navigation; no browser reload required; cancellation accurately marks result unusable if partial. | Browser+backend integrated test with genuinely long job and failure injection. |
| QR-14 Scalability/memory | With increasing geospatial features, event count, scenario count and resources, report load latency, UI frame rate, solver termination, memory peak and limiting factor; no unbounded accumulation in a 30-minute representative UI session. | Reproducible stress profile with resource usage time series, thresholds stated before test; absence of a proven bound is reported NOT VERIFIED. |

These numeric UI targets are **initial engineering budgets, not validated operational SLAs**. M0 must establish benchmark host (CPU, RAM, architecture), representative dataset sizes, browser and feasible baselines; proposed changes require a recorded decision and user approval, not silent target redefinition. No production-safety conclusions from a fast prototype. A failing QR-11–QR-14 blocks the research release until remediated or transparently rescoped with user approval.

### Performance architecture guardrails
- Keep browser rendering independent of simulation workers; run physical solvers outside interactive request threads.
- Lazy-load maps/layers, stream/paginate large datasets, perform heavy preprocessing off main UI thread where practical, profile before adding caches.
- Restrict concurrency and memory per worker; implement job state, timeout, cancellation and backpressure; conserve MacBook resources.
- Use appropriate geospatial formats and render levels of detail while preserving original output, CRS, provenance and uncertainty.
- No mandatory paid telemetry/CDN/services; local profiling with portable open tooling and future laboratory-server compatibility.

## User-confirmed UI reference requirement — 2026-10-16

**FR-UI-REF-01 (P0):** use Tactical Analyst and Geospace Wildfire as functional/UI reference targets, preserve FIRE/FLOOD scope and detailed real maps. Provide coherent map-first workflows, readable Italian terminology and contextual help, distinct navigation for map/results/sources, controllable layers, scenario comparison/time, map annotations/measurements, saved configurations/views, provenance and exports. Do not declare full reference parity from an initial UI increment. Explicit coverage/gaps and observed-versus-marketed evidence: reports/UI-CONTROL-ROOM.md. Existing FR-24–28/QR-11–14, safety and scientific qualification remain binding. Live satellite/meteo, censused impact, operational resources/collaboration and arbitrary physical editing require real supported integrations; no decorative or fabricated operational features.

**FR-FLOOD-ACTIONS-01:** user answered «Voglio tutto»: investigate and implement verified physical comparisons for retention/lamination, local levees and pumping, with multi-day evolution as previously requested. The prior choice between a single intervention is resolved; all three are requested. Native HMC reservoir affordances are not evidence of integrated success. Assess hydraulic needs and present any substantial engine adoption/replacement before applying it; don't infer permission for privileged installs, costs, public deployment or larger VM resources. This is requested scope, not an executed/qualified feature.

## User-confirmed complete GitHub reconstruction requirement — 2026-10-16

**FR-REPRO-GH-01:** publish all current HAZARDIA application, UI, adapter, decision/queue, schema/test and provisioning source with complete installation/recreation instructions, including UTM VM configuration, SSH-key-only cloud-init, reference OS/system prerequisites, pinned upstream engines/dependencies/inputs, genuine native runs and local UI startup. Target repository is `francesco-basciani/hazardia`; source pushes are now explicitly authorized within this scope, public service deployment and costs are not. Do not publish secrets, virtual disks, personal runtime state or imagery with unresolved redistribution rights. A curated complete source snapshot may exclude private historical media while retaining the original local research history. Distinguish passed new-prefix reconstruction from NOT RUN fresh-OS/second-machine boot and from unqualified physics; no fabricated install/bitwise/scientific result. Guide docs/INSTALLAZIONE.md and report reports/PUBBLICAZIONE-GITHUB.md provide the executable path and evidence.

## User-confirmed monitoring-first UI — 2026-10-16

**FR-MONITOR-01 (P0):** make monitoring the default workspace, with a large central map, independently selectable FIRE/FLOOD overlays and both visible together. Show explicit product dates, native variable/unit legends, provenance and simulated/observed qualification. Separate decision construction, strategy comparison and results into a dedicated navigation section; switching sections must preserve an existing current proposal unless its inputs/context change. Hazard filtering, map pan/search and view navigation must not launch simulators or decisions. Overlapping dated scenario outputs is consultation, not a fused/live/joint forecast. Current scope is the existing Abruzzo research catalog; this user request does not waive FR-05/06/17, historical validation, general multi-day flood support or operational safety gates.

## User-authorized real Open-Meteo integration — 2026-10-16

**FR-WX-REAL-01 (P0, scoped increment of FR-06/07/18/22):** display attributable real hourly Open-Meteo point forecasts on the monitoring map and allow explicitly requested new native FIRE/FLOOD conditional research jobs using a fresh immutable forecast in the same VM. Free noncommercial endpoint only, shared bounded cache/traffic, no API keys/costs or automatic operational action. Explicitly distinguish real forecast weather from hypothetical ignition/fuel/moisture/soil/Q0 and retrospective examples. Preserve unknown provider model initialization, actual first-seen time, correct preceding-hour precipitation/radiation alignment and native wind/pressure conversion. New0.3.0 research-forecast contract, legacy0.2.0 research-replay behavior retained; ADR-0010 defines compatibility and failure semantics. Ensemble/distributed basin forcing, calibration, predictive alert quality and fullM5–M7 gates remain separate acceptance items.


**FR-WX-LAYERS-01 (scoped UI increment):** monitoring offers independently selectable wind, temperature and hourly precipitation forecast overlays, retaining a master weather switch and selected forecast hour. At current point-data coverage display one anchored marker at the provider model grid point, with date/model/units and an explicit non-interpolated coverage legend. Weather symbols must use a transparent map surface with small translucent value labels rather than an opaque enclosing card, preserving the visible terrain beneath. Wind arrow denotes direction toward (meteorological FROM +180°), while the text denotes FROM; overlays must not submit simulation jobs, alter hazard visibility or bypass shared free-tier cache. A regional wind/precipitation field requires separately acquired distributed data; repeating a single point is not regional coverage.


**FR-UI-DESIGN-01 (user-confirmed presentation requirement):** provide a consistent professional visual system across monitoring, decisions, sources/help and physical comparison, retaining all existing workflows and responsive layouts. Adapt navigation, map/panel arrangement and touch controls to desktop/tablet/phone; preserve readable contrast, keyboard focus, reduced-motion preference and no page-level horizontal overflow. Visual redesign cannot alter data qualification or imply operational/scientific readiness. Acceptance includes representative viewport and automated accessibility evidence, with real-device/cross-browser limitations explicit.


**FR-WX-REGIONAL-01 (user-confirmed scoped increment):** provide switchable transparent animated wind across the Abruzzo coverage rectangle from attributable real multi-point10m forecast vectors, with selectable valid hour and direction/intensity legend. Preserve effective model coordinates, timestamps/unknown initialization, vector interpolation and explicit display resolution; do not duplicate a single point or imply observational/air-parcel accuracy. Keep acquisition/cache/preprocessing/service in the sameVM and rendering in the browser; only bounded free noncommercial endpoints with shared quota, no paid fallback. Stop/pause animation for hidden/layerOFF views, respect reduced-motion and retain responsive/accessible controls. Regional imagery may use an attributed bounded free noncommercial mosaic; physical simulator forcing remains a separately qualified contract. ADR-0011 records scope and alternatives.

## Persistent map event references — user requirement 2026-10-16
**FR-MAP-EVENT-01 (P0):** visible selected hazard scenarios and future geolocated alarm points must remain identifiable at every supported zoom through high-contrast screen-sized symbols independent of raster opacity and polygon size. Respect hazard filters, distinguish nearby symbols, provide keyboard access and a recenter control for references outside the viewport. Preserve actual geographic anchors; explicitly distinguish configured ignition, representative simulated cell/domain and observed alarm. Do not invent coordinates for unlocated alerts or imply a zero-depth scenario is a positive flood detection. No territory-specific styling dependency.

## Viewport-wide weather — user requirement 2026-10-16
**FR-WX-VIEW-01 (P0):** wind, temperature and precipitation must cover the visible monitoring map at all supported zooms using real distributed data, preserving the transparent background. Adapt rendering and bounded acquisition/cache to the viewport and territorial profile; no single-point replication or extrapolation beyond acquired coverage. Expose selected valid time, units, sampling/model resolution, provenance and partial/stale/unavailable state. Point inspection returns attributable interpolated values. Keep the finer existing regional wind where fresh/compatible and identify the broader global forecast separately. Zoom does not improve native forecast skill/resolution. Free noncommercial quotas, singleVM and separately qualified CIMA forcing remain mandatory. See ADR-0012; real international transfer still needs its own evaluation.

## Physical wildfire inputs — user reconfirmation 2026-10-16
**FR-FIRE-FORCING-01 (P0, clarification of FR-06/08 and FR-WX-REAL-01):** weather shown in the UI is not sufficient evidence of simulator coupling. Every new wildfire run must identify the actually consumed terrain, vegetation/fuel, georeferenced wind vectors and fuel-moisture inputs, including their temporal schedule, units, provenance and uncertainty. Real distributed/time-varying forcing must be projected and aligned to the simulator grid, with coverage/time validation and explicit missing-data policy. Air relative humidity is not fuel moisture; temperature, atmospheric humidity, precipitation and radiation require an explicitly sourced and separately verified fuel-moisture estimation model where used, rather than direct substitution into the native moisture percentage. Keep synthetic/research parameters visibly qualified until replaced and tested. Current point-wind <=1h slice is partial support, not completed distributed forcing; existing historical scenarios must not be silently re-forced with current weather.

## Regional overview context — user requirement 2026-10-16
FR-MAP-REGION-01: show sourced administrative region boundaries and region names over distant satellite views, with an independent accessible toggle. Prefer high-contrast unfilled lines, emphasize the configured pilot region and reduce visual clutter at local zoom. Geography/year/license/generalization must be explicit; display boundaries must not silently determine operational jurisdiction or historical membership. Current Italian context: Istat2026 generalized20regions; foreign territory assets require separate qualification.


## Control placement and editable resources — user requirement 2026-10-16
**FR-UI-WORKSPACE-01 (P0):** keep map settings, including regional boundaries, in a coherent configuration section; place comparison mode controls beside their maps; keep weather hour, layer and actual visible-area values discoverable. Minimize repeated prose without removing qualification/provenance. Resource editing must send actual position, availability and arrival inputs to the solver. Explicitly distinguish research evacuation from physical hazard suppression: manual coordinates alone must never imply computed road travel, firefighting capability or altered propagation. Existing scenarios retain their forcing; selected-run weather must be explicit. Full typed firefighting intervention coupling remains required by existing physical-action requirements and is not satisfied by an evacuation editor.


## Interactive physical fire workflow — user reconfirmation 2026-10-16
**FR-FIRE-STUDIO-01 (P0):** allow map-authored ignition and categorized firefighting action geometry/time, compare native outputs under relocated resources or time-varying weather, and show hourly meteorology including temperature/RH/precipitation with explicit consumed-input provenance. Resource actions must affect native simulator inputs, never merely exposure or drawn perimeters. The current native line-action slice is unqualified research, not full calibrated fleet capability/logistics. Multi-day support must distinguish executed horizons/pairs. FR-FIRE-FORCING-01 remains required: merely showing atmospheric values does not satisfy fuel-moisture coupling.
**FR-DEGRAD-UI-01 (P0 clarification):** make retained functions, unavailable functions, stale sources and failure reasons visible/testable. Distinguish actual health/freshness from controlled fault replay. Preserve already verified results, reject critical unknown/stale proposals, retain independent hazard functions where admissible. Full M6 still requires capability-driven adaptation/decision-quality evaluation, not only injected-state badges.


## FR-FIRE-WORKSPACE-01 — flusso confermato e precisato 2026-10-17
Dentro **Simulazioni e risorse** una mappa consente drag/drop di uno o più inneschi e unità, geometrie di intervento a linea/area e relativi tempi. Timeline comune con avanzamento, pausa, ritorno indietro e confronto di scenari aggiungibili oltre A/B. Le categorie non implicano efficacia non verificata: l'ipotesi richiesta di sottrazione del combustibile deve alterare input fisici temporizzati, conservando la traccia delle celle coinvolte. Distinguere riproduzione dei frame calcolati, bozza modificata e ricalcolo fisico. Conservare separazione dal laboratorio evacuazione, meteo e qualificazioni scientifiche; nessuna azione reale. La semplificazione interattiva non autorizza perimetri disegnati come risultati o una dichiarazione di streaming/checkpoint del solver non implementati.


## FR-UI-LAYERS-01 — confronto cartografico, 2026-10-17
La UI deve rendere centrale la mappa e consentire di leggere risultati come livelli sovrapposti con opacità, oppure confrontare due scenari con un separatore trascinabile sincronizzato alla stessa ora simulata. Conservare la georeferenziazione e i valori originali; distinguere selezione per modifica, risultati calcolati, frame mancanti e bozze. Controlli contestuali compatti, accessibili via mouse/touch/tastiera e responsive. Il riferimento visuale commerciale non qualifica nuovi prodotti fisici o metriche di rischio e non cambia AR-EXT-01 né l'ambito M0–M7.


## Territorial monitoring and evidence fusion — FR-MONITOR-FUSION-01 (P0)

User clarification 2026-10-17, refining FR-05/06/17, FR-MONITOR-01 and M2/M5/M6 without replacing the decision core. Monitoring must combine attributable available weather, satellite observations, territorial susceptibility and exposure to identify areas needing review before a user-configured ignition or decision job. Existing simulated examples alone do not satisfy this requirement. Platform remains generic; fire and flood are the initial modules. Geographic profiles supply local sources, units, catchments/administrative areas and qualified thresholds; do not hardcode Abruzzo as the platform boundary.

- Fire evidence: forecast wind/gusts, temperature, relative humidity, antecedent rainfall and drying, fuel/vegetation and terrain, sourced fire-weather/drought indices (e.g. EFFIS FWI/DC), satellite thermal observations when available. Distinguish fire-weather danger, observed hotspot and conditional propagation; a dry area is not an observed ignition, and relative air humidity is not measured fuel moisture.
- Flood evidence: spatial rainfall intensity and accumulations over declared complete intervals, antecedent rain/soil wetness, catchment/drainage/terrain, available radar/gauges/river observations and qualified hydrological/hydraulic outputs, local susceptibility and exposed people/assets. Separate pluvial flooding from fluvial flooding; rainfall alone does not establish flood extent/depth or impact. Never apply an invented universal mm threshold or transfer a jurisdiction's thresholds without qualification.
- Prefer official regional/civil-protection warning polygons and bulletins where licensing and machine access permit. Keep their issuer, issue/valid times, jurisdiction and revision. Display these independently from HAZARDIA research attention areas; internal evaluations cannot impersonate an official alert or imply equivalent certification. No inference about a commercial site's private algorithm.
- Map UI: selectable transparent attention layers by hazard, time horizon and official/internal/observed origin; click an area for reasons, contributing values, source timestamps, native resolution, uncertainty/coverage, missing or conflicting inputs, affected places and available exposure. Open a prefilled simulation from the inspected area through an explicit user action. Explain per-hazard signals rather than hiding incompatible quantities in one score.
- Evidence fusion must reconcile spatial support, units and issue/valid/available times, deduplicate revisions and preserve reproducible snapshots. Prevent future-data leakage in replay. Assess contradictions and correlated sources; source count is not confidence. Only available/legally usable/quality-checked relevant sources participate; disclose omissions. Bound polling, viewport/time processing and caches within free quotas and the existing single VM.
- Degradation: stale/missing rainfall, radar, fuel, drought or other required inputs must lower the corresponding assessment capability, withhold unsupported classification and display unknown/partial coverage distinctly from low danger. Retain dated qualified cached products when allowed, mark expiry and recovery; lack of data must never produce an all-clear. Separate high weather danger from qualified impact risk, which also needs exposure/vulnerability.

Acceptance: (1) documented source/rights/coverage and immutable real snapshot; (2) map-reproducible local fire and flood attention examples with reason/time/source inspection; (3) independently dated official warning overlay if obtainable, with explicit unavailable status otherwise; (4) missing/stale/contradictory source tests, no false all-clear and capability recovery; (5) equal-rainfall/different-catchment case using qualified territorial evidence, not invented thresholds; (6) geographic profile separation and bounded quota/resource verification; (7) historical cutoff replay and separate precision/false-alarm/lead-time validation. Until those tests execute, implementation/accuracy remain NOT RUN or BLOCKED, not PASS from documentation.


### FR-MONITOR-FUSION-01 — primo incremento reale, 2026-10-17
Implementazione di consultazione integrata: EFFIS FWI/DC e zone DPC con evidenze contestuali meteo, fonti/tempi distinti, livelli filtrabili, cache e degradazione per fonte. Profilo geografico concreto Italia e sfondo d'insieme4–11, preservando limiti di risorse; i prodotti fisici restano sui domini già preparati. Scenari di ricerca attivabili separatamente. Non introduce un nuovo indice composito o una previsione locale d'impatto: questa rimane non disponibile finché non sono qualificati suolo, fuel, esposizione, sensori e modello. Geometrie non valide e zeri WMS ambigui devono restare unknown. Criteri di validazione/portabilità storica e scientifica di FR-MONITOR-FUSION-01 rimangono aperti; il PASS di integrazione non li chiude.


### FR-FIRE-WORKSPACE-01 — chiarezza del percorso e campioni suborari
Mostrare scenari, stato e durata dei risultati senza obbligare ad aprire il pannello livelli. Duplicazione esplicita in alternativa con selezione del confronto; durata comune richiesta distinta dai risultati precedenti. I nuovi prodotti hanno output fisici a15minuti; mantenere compatibilità con le serie orarie e lookup per tempo, senza trattare l’indice come ore. Nessuna crescita interpolata spacciata per soluzione fisica, nessun ricalcolo implicito durante playback. Segnalare confronti con cadenze/durate diverse e risultati mancanti; rivalutare prestazioni per orizzonti lunghi senza dedurre validazione dalle sole opzioni UI.

### Meteo completo e zone ufficiali — precisazione 2026-10-17
FR-WX-VIEW-01 include selezione di umidità relativa, raffiche, nubi, pressione al suolo e radiazione, oltre a vento/T/pioggia, con unità, intervalli temporali e missing espliciti. Questi campi di consultazione non attestano un coupling fisico. FR-MONITOR-FUSION-01 usa le geometrie ufficiali del territorio per le sintesi visibili: in Italia zone del bollettino DPC, mantenendo livelli ufficiali meteo-idro distinti dagli indici EFFIS aggregati per consultazione. Mostrare massimo/media/minimo e campioni validi; nessun allarme incendio ufficiale o impatto idraulico dedotto dall'aggregazione. Geometrie invalide o copertura assente restano unknown. Il numero di zone segue la versione pubblicata dalla fonte. Nessuna suddivisione italiana deve essere imposta ai profili esteri.
FR-FIRE-WORKSPACE-01 espone l'esaurimento dei fronti nativi nei nuovi output e distingue tale stato da un limite di durata o un'estinzione osservata. Il requisito di scenario realistico completo non è soddisfatto da un pilot72h con fuel/moisture ipotetici: FR-FIRE-FORCING-01 e qualificazione delle capacità rimangono obbligatori.

### Scenario comparison clarification — 2026-10-17
The fire authoring workspace uses simultaneous scenario map windows rather than a swipe divider. Pan/zoom and elapsed time are synchronized. Authored ignition additions, moves, times and removals are common to all scenario drafts; resources and their geometries/times remain scenario-specific. Preserve prior immutable results and identify drafts requiring recalculation. Legacy workspaces with different ignitions must warn before the next explicit ignition edit aligns their drafts. Always-visible meteorological context distinguishes the result's consumed snapshot from newly available forecasts, timestamps, missing values and atmospheric variables not yet physically coupled. This refines FR-26 and the fire scenario requirements without qualifying the experimental intervention/fuel model.

### Empty authoring and explicit map weather layers — 2026-10-17
A new fire workspace starts with one empty no-intervention reference: zero ignitions, zero resources and no preloaded results. Empty ignition lists may be persisted as drafts, never submitted for physical execution. New scenarios inherit common ignitions and explicitly displayed calculation parameters, but never inherit resources implicitly. Every intervention must be authored by the user; its initial visible100m line and editable geometry/time must be disclosed. Weather display offers independent checkboxes for wind, temperature, precipitation, relative humidity, gusts, cloud, pressure and radiation on all simultaneous scenario maps, with transparent rendering, animated wind, explicit absolute valid time, freshness and coverage. A display time may follow the simulation timeline or be chosen for consultation; checking a weather layer does not mutate simulation forcing. Preserve existing source quota/cache and physics-qualification gates.

### Ideal mapped-priority assignment — 2026-10-17
User-requested ideal case uses available resource inventory and explicit priority weights on mapped residential areas/facilities. Distinguish cartographic identification from satellite detection, unknown population and incomplete coverage from low risk, coverage-proxy optimization from native suppression and calibrated efficacy. Versioned decision policy0.6.0 declares weighted_priority_points, IDEAL_ASSET_COVERAGE and RESEARCH_IDEAL;0.5.0 evacuation semantics remain unchanged. Maintain independent verification, bounded decision deadline, resource availability and no double-booking/duplicate target. New physical comparison uses paired frozen forcing/clock. No operational approval or automatic dispatch; ideal examples are opt-in and never silently replace authored work. ADR-0013 defines limits and deferred rolling/qualification gates.

### Leggibilità del meteo e contesto — chiarimento utente2026-10-17
FR-WX-VIEW-01 prevede indicatori numerici distribuiti e combinati (temperatura/umidità e variabili selezionate), vento animato visibile e precipitazione con palette d'intensità trasparente, leggenda/unità/ora/fonte. Densità grafica e amplificazione del vento non aumentano la risoluzione dei modelli. Confini e nomi geografici disponibili nelle mappe, impostazioni cartografiche raccolte; copertura parziale/missing espliciti. Mantenere drag/drop, confronto sincronizzato, quote gratuite e runtime unicaVM. La pioggia visualizzata non è una previsione d'allagamento e le classi cromatiche non sono livelli di allerta. Non modifica i requisiti di coupling/qualificazione fisica già aperti. Esito dell'incremento: reports/METEO-LEGGIBILE-E-CONTESTO.md.

Richiesta UI2026-10-17: indicatori meteo numerici come testo sovrapposto senza riquadri, sfondi o bordi; il territorio deve rimanere visibile. Ammesso solo contorno/ombra sui caratteri per la leggibilità.

### Replay meteo e priorità alle mappe — richiesta utente2026-10-17
FR-WX-VIEW-01 comprende colore numerico della temperatura e campi pioggia/nuvolosità con sfumature continue, trasparenti e legende con unità, dati mancanti espliciti. Una barra meteo play/pausa/cursore/velocità esplora gli istanti realmente disponibili, con arresto a fine orizzonte o assenza dati e sospensione in background. Non cambia le forzanti di un job né costituisce una nuova previsione fisica. FR-24/26: mappa prima dei pannelli secondari in tutti i percorsi cartografici, mantenendo controlli e layout responsive. Distinguere il tempo meteorologico dal tempo dei risultati dei simulatori. Esiti e limiti in reports/PREVISIONI-METEO-E-MAPPE-IN-ALTO.md.

## Distinzione cartografica e continuità meteo — precisazione utente2026-10-17
FR-WX-VIEW-01: nomi di località/regioni visivamente distinti dai valori meteorologici; replay continuo fra record orari adiacenti con interpolazione dichiarata, pausa sul punto intermedio e ripresa, senza estrapolare o colmare dati mancanti. Vento interpolato nelle componenti, non negli angoli; precipitazione/raffiche/radiazione restano campi riferiti alle finestre orarie, le transizioni non producono nuove previsioni al minuto. Origine, validità/freschezza e copertura della previsione reale verificabili; i record grafici non modificano le forzanti native. Verifica: reports/NOMI-E-METEO-CONTINUO.md.

## Copertura e destinazione del drag/drop — precisazione2026-10-17
FR-FIRE-WORKSPACE-01: ogni finestra di scenario deve accettare l'inserimento e lo spostamento delle proprie squadre; gli inneschi inseriti su qualsiasi finestra restano comuni. Prima del calcolo rendere distinguibile la copertura del terreno fisico da quella dell'immagine satellitare, con confine reale, inquadratura dedicata e controlli di copertura/limiti geometrici. Configurazioni fuori dominio restano bozze recuperabili, con motivo italiano e blocco dell'invio; nessuno spostamento o ritaglio automatico. La validazione backend rimane indipendente. Un territorio non preparato richiede dati/forzanti verificati, senza dichiarare una copertura fisica globale dall'accesso allo sfondo cartografico.


## Riallineamento monitoraggio e simulazione — decisione utente 2026-10-18

FR-FIRE-WORKSPACE-01 / FR-FIRE-FORCING-01: i nuovi scenari non devono dipendere dal riquadro del caso dimostrativo. Preparare automaticamente un dominio numerico interno comune attorno agli inneschi condivisi, da fonti attribuibili per elevazione/copertura e meteo locale. Il requisito del 2026-10-17 di mostrare obbligatoriamente il confine fisso è superato per questo percorso; il replay storico mantiene gli input originari. Nessuno spostamento automatico degli inneschi o sostituzione con terreno sintetico. Dichiarare mancanza dei dati, combustibile assente, estensione non supportata e uscita del fronte dal dominio, senza presentare una simulazione troncata come completa.

Vento spazio-temporale e stima dell’umidità del combustibile devono essere effettivamente consumati dal motore, distinguendo RH atmosferica da moisture. Il modello di stima, inizializzazione, riclassificazione della vegetazione e risoluzioni restano espliciti e non calibrati finché privi di validazione. Comparazioni con identico terreno, meteo congelato, tempi e politica stocastica; unità/linee/aree restano proprie di ogni scenario. L’ottimizzazione propone solo interventi sperimentali sui mezzi disponibili e sulle priorità con evidenza; assenza OSM non equivale ad assenza di centri abitati.

FR-MONITOR-FUSION-01 / FR-WX-VIEW-01: Monitoraggio e Simulazioni sono i due percorsi principali, fonti/guida strumenti di supporto. Monitoraggio esplora criticità e condizioni attuali/previste per la validità selezionata; oltre l’orizzonte dei bollettini mostra missing, non prolunga implicitamente le zone colorate. Distinguere meteo aggiornato di consultazione da quello congelato dei risultati. QR-11: scrollWheelZoom disabilitato su tutte le mappe, inclusi confronti e viste storiche. Queste correzioni non chiudono i gate di qualificazione M5–M7. ADR-0014 e report DOMINI-DINAMICI-E-FORZANTI descrivono il percorso verificato.


## Tempo unico degli scenari — decisione utente 2026-10-18
FR-26 / FR-WX-VIEW-01: nello studio di simulazione deve esserci un solo comando Riproduci/Pausa e una sola timeline. Ogni finestra risolve il meteo all’istante assoluto inizio dello scenario + tempo trascorso. Nessun selettore o player meteo indipendente nello studio. La scelta della fonte (snapshot consumato dal risultato o previsione aggiornata) non cambia il tempo: una nuova fonte non riscrive automaticamente risultati fisici precedenti. Dati orari esatti alle ore intere; transizioni visuali solo fra campioni orari adiacenti, con mancanze e fine copertura dichiarate. Il Monitoraggio conserva il proprio unico player previsionale. Questa decisione supera il precedente doppio clock di consultazione nello studio; nessuna estensione dei gate scientifici.


## Modifica, calcolo e riproduzione fisica — chiarimento2026-10-18
FR-FIRE-WORKSPACE-01 / FR-FIRE-FORCING-01 / FR-28: squadre, geometrie, tempi e meteo modificati non possono essere presentati come già applicati a un risultato precedente. L’unico comando temporale diventa Calcola e riproduci quando il gruppo confrontato contiene modifiche: esegue prima il calcolo fisico con gli input attuali e il contesto comune, poi riproduce i risultati aggiornati. Durante preparazione/calcolo mostra progressi e conserva i risultati precedenti esplicitamente etichettati; errori/cancellazioni impediscono l’avvio automatico, mantenendo gli esiti indipendenti degli altri scenari. Il controllo di coerenza deve confrontare anche il piano effettivamente consumato dal risultato, non soltanto l’ultima richiesta salvata, incluso dopo reload. Le categorie risorse restano ipotesi ideali non qualificate finché mancano efficacia/logistica validate; nessuna riduzione del fuoco garantita dal semplice inserimento di un’icona.


## Flusso simulazione confermato dall’utente — 2026-10-18
La richiesta corrente sostituisce il precedente vincolo degli inneschi comuni: ogni scenario può avere inneschi e risorse propri, inclusi il primo scenario e un unico scenario con squadre. Copiare un caso è esplicito; le copie diventano indipendenti. Conservare0risorse, più inneschi, categorie, geometria ed attivazione modificabili, timeline unica congruente al meteo, pausa/seek/edit/ricalcolo e ripartenza dall’ora scelta. Il ricalcolo completo è distinto da checkpoint/streaming del solver non implementati. Scenario ottimizzato integrato, con mezzi/priorità dichiarati, proposta del solver verificata e confronto fisico su input congelati; “migliore” significa migliore fra gli scenari effettivamente valutati secondo l’obiettivo esplicito, non ottimo fisico globale o efficacia certificata. AR-EXT-01 e architettura multi-hazard invariati, focus esecutivo FIRE. Le categorie restano ipotesi ideali finché prive di dati di efficacia e logistica; nessun nuovo modello o deployment autorizzato implicitamente.


## Replay di interventi e azioni native —2026-10-18
Le modifiche alle sole risorse di un risultato esistente conservano gli input congelati e l’inizio del proprio scenario; non convertirle implicitamente in una nuova previsione futura. Finestre stabili e pausa al pointerdown della palette. Nessuna attivazione retrodatata silenziosamente quando il cursore è a fine orizzonte. Canadair/elicotteri nuovi usano azione nativa upstream lungo linea, distinta dalla barriera fuel_removal selezionabile; vecchie configurazioni immutate, aree richiedono effetto ideale esplicito. Area cumulativamente raggiunta distinta da fiamme attive: non cancellare il passato per simulare spegnimento. Parametri upstream non certificano efficacia/logistica e non sostituiscono ensemble o validazione. AR-EXT-01 e M0–M7 invariati; nessun nuovo modello o operazione reale. Report reports/MODIFICHE-DURANTE-LA-SIMULAZIONE.md.


## Transizioni visuali e stato del ricalcolo — chiarimento2026-10-18
FR-26/28: la riproduzione può dissolvere i PNG fra campioni nativi adiacenti per evitare scatti, identificando l’interpolazione esclusivamente grafica. Valori numerici/artefatti originali restano campionati; nessuna estrapolazione attraverso gap o oltre copertura. Pausa conserva il tempo visibile, meteo risolto allo stesso istante, reduced-motion rispettato. Distinguere progressi fisici del job dall’ora del replay e fronti esauriti da job bloccato. Il recupero della coda dopo reload è condizionato a configurazione persistita e compatibile, non equivale a checkpoint del solver o recupero crash transazionale. Qualifiche scientifiche e architettura originali invariate.


## Previsione condizionale con dati reali —2026-10-18
Scelta utente: scenario futuro con innesco ipotetico e dati reali, distinto dalla ricostruzione dell’evento. FR-FIRE-FORCING-01: profilo168h antecedenti può inizializzare spazialmente lo stesso estimatore hFFMC già usato;FFMC85 rimane prior assunto all’inizio del warm-up, non osservazione. Nuovo forcingdistributed/2 conserva compatibilità con1 e asset originali. Storia necessaria incompleta/scaduta o quota impediscono il nuovo calcolo senza fallback secco; risultati precedenti conservati. FR-FIRE-WORKSPACE-01:2/4/8realizzazioni selezionabili entro risorse, input salvati e consumati verificati; modifiche del profilo richiedono nuova preparazione, replay risorse conserva il profilo del genitore. Otto realizzazioni di un solo forecast non sono otto previsioni indipendenti né validazione. Nessuna efficacia certificata, skill locale o durata minima dell’incendio dedotta; AR-EXT-01 e gate M5–M7 invariati. Report PREVISIONE-CON-DATI-REALI.


## FR-FIRE-WORKSPACE-01 — disposizione nominale, richiesta2026-10-18
Nuovo workspace con un solo scenario nominale vuoto. Il primo scenario rimane riferimento in evidenza, con alternative sotto nell’ordine di creazione; selezione/modifica non scambia le mappe. Alternative eliminabili dalla workspace, con annullamento singolo nella sessione e mantenimento degli artefatti calcolati. Nominale protetto dalla cancellazione, inneschi e risorse sempre modificabili; non imporre assenza di squadre al lavoro esistente. Nessun reset automatico di configurazioni o casi già salvati. Risorse/geometrie indirizzate alla mappa scelta, sincronizzazione temporale/meteo e zoom esistente invariati.


## FR-FIRE-WORKSPACE-01 — ricalcolo e bozze vuote
Le alternative senza inneschi restano bozze visibili e non impediscono calcolo/ripresa degli scenari eseguibili. Lo stato modificato dipende dai valori, non dall’ordine delle proprietà JSON. Un risultato invariato può essere riutilizzato soltanto se compatibile anche con il calendario di eventi numerici comune; altrimenti viene ricalcolato. Mostrare calcolo/errore accanto al cursore, fermare la coda al primo errore ed evitare falsa ripresa; risultati precedenti conservati. La ripresa richiede risultati coerenti con gli input correnti ed esclude le sole bozze senza inneschi.


## FR-TERR-CONTEXT-01 / FR-AIR-CONTEXT-01 — richiesta19ottobre2026
Integrare abitati, edificato e strutture prioritarie come livelli geografici nel Monitoraggio e nelle simulazioni, con provenienza, epoca, geometria reale, copertura parziale e dati mancanti espliciti. Derivare contatto e probabilità dagli array nativi dello scenario, alla stessa ora della timeline, distinguendo frequenze stocastiche condizionali da rischio umano e da allerte ufficiali. Una bozza non ricalcolata conserva la qualificazione del risultato precedente; inventari diversi non sono un confronto perfettamente allineato. Centri puntuali non sono confini amministrativi. Popolazione/vulnerabilità non si deducono da copertura edificata.
Linee elettriche aeree e sostegni selezionabili, includendo distribuzione e tensioni ignote; escludere cavi interrati/sottomarini e non inferire quote o tensione assente. Intersezione con una geometria d’intervento è un avviso cartografico, non verifica di rotta o distanza di sicurezza. Sole/notte stimati al tempo dello scenario non determinano idoneità al volo. In assenza di qualificazione ostacoli/quote/corridoi/mezzo/equipaggio, il pianificatore automatico esclude le categorie aeree; applicare il controllo anche a replay di vecchie proposte. Simulazioni manuali restano ipotetiche, senza autorizzazioni operative. Fonti libere, cache e lavorazioni nella VM, acquisizioni e job limitati. AR-EXT-01 e gate scientificiM5–M7 invariati.


**FR-OSM-CATALOG-01 —19ottobre2026:** la fonte OSM alimenta un catalogo territoriale generico riusabile da futuri scenari, inclusa sanità. Conservare raw e tutti i tag degli oggetti rappresentabili, anche chiavi non note; gruppi e layer selezionabili, ricerca/ispezione, geometrie/proxy/omissioni espliciti, provenienza/versione/diritti/copertura. Non confondere un estratto con copertura territoriale completa. Tag sanitari non certificano capacità o disponibilità attuale. Nuove categorie non diventano automaticamente priorità o risorse del decision engine; nessun nuovo simulatore sanitario in questo incremento. Acquisizioni/cache e normalizzazione nella stessaVM, con budget e fallimenti espliciti.


**FR-UI-ROOM-01 —19ottobre2026:** Monitoraggio orientato alla mappa, navigazione chiara, comandi uniformi e pannelli ordinati; ispirazione gerarchica dal riferimentoGeospace, senza copiarne asset o dichiarazioni operative. Conservare controlli/funzioni, meteo e confronti, provenienza/missing espliciti e responsività; limitare altezza mappe anche negli iframe. SfondoOSM opzionale di consultazione con attribuzione/cache/budget conformi alla fonte, oltre al satellite; nessuna pretesa di navigabilità o accuratezza del modello. Piano originario e genericità multi-hazard invariati.


### FR-INTERVENTION-PLAN-01 — richiesta utente19ottobre2026
In Simulazioni separare Piano d’intervento (una mappa con proposte sui mezzi dichiarati disponibili) e Confronto scenari (mappe multiple e ordine preservato). Il pulsante Calcola posizionamento usa prodotti fisici e fonti territoriali congelati, priorità esplicite modificabili e ora selezionata; nessuna attivazione retrodatata. Estensione esplicitamente autorizzata rispetto a FR-OSM-CATALOG-01: tag qualificanti di sanità, abitati, ferrovie, linee elettriche, impianti e ponti possono alimentare la politica dichiarata, non tutti gli oggetti del catalogo. Riportare incompletezza e tensione ignota, escludere proxy non qualificati. Non dedurre persone salvate o sicurezza aerea. Conservare compatibilità dei pesi legacy, verifica indipendente e termine60s; fallback verificato con ottimalità non provata soltanto per indisponibilità/timeout del solver, mai bypassare vincoli ignoti. Confronto fisico distinto dal proxy di copertura, nessun dispatch o efficacia certificata. I pesi iniziali sono ipotesi di ricerca, non graduatorie ufficiali; la richiesta non qualifica logistica o abilita gli aerei. Architettura generica, M0–M7 e AR-EXT-01 invariati.


## Priorità cartografica e comandi a richiesta — 2026-10-20
FR-24/26: la mappa è il contenuto principale di Monitoraggio e Simulazioni. Evitare colonne di navigazione o palette permanenti che ne sottraggano larghezza; gestione scenari, inserimento risorse e inquadrature restano accessibili da comandi compatti. Pannelli di contesto a richiesta, timeline vicina alla mappa e note estese sotto. Preservare accessibilità, responsive, distinzione ricerca/operatività, stato dei dati e configurazioni esistenti; nessuna modifica implicita alle simulazioni.


## Controlli cartografici sovrapposti — precisazione2026-10-20
FR-24/26: i comandi secondari possono sovrapporsi alla mappa in pannelli a scomparsa, contenuti nei bordi anche su touch. Mantenere nome/stato, indicazione di ricerca, accessibilità e timeline unica; evitare righe permanenti di configurazione sopra la mappa. Pausa/ripresa deve funzionare anche su campioni già in cache, senza ricalcolare o alterare prodotti fisici.


### FR-WX-VIEW-01 — chiarimento copertura e densità (2026-10-20)
La consultazione meteo segue l’intera inquadratura, comprese viste nazionali e internazionali, con acquisizione/retry limitati e avviso visibile di copertura parziale, attesa, dati scaduti o indisponibili anche a pannelli chiusi. Cache lossless e provenienza preservate. Copertura spaziale completa non equivale a densità/risoluzione locale costante: dichiarare passo campionato e interpolazione alle scale ampie. Le mappe dei risultati fisici conservano le forzanti congelate del run e il proprio dominio; il meteo consultativo non può sostituirle o fingere di avere influenzato un risultato già calcolato. Antimeridiano/poli richiedono verifica specifica prima di dichiararne il supporto.


### FR-WX-VIEW-01 — probabilità e nuvole (2026-10-20)
Mostrare probabilità di precipitazione acquisita come tale dalla fonte, separata dai mm previsti, con soglia/evento e finestra oraria dichiarati. Non stimarla da pioggia deterministica o copertura nuvolosa. Copertura nuvolosa con scala0–100%, colori/opacità leggibili e continui, territorio visibile, livello indipendente e legenda distinta dalla pioggia. I dati mancanti, inclusa la probabilità nei risultati già congelati, restano mancanti e segnalati; nessuna sostituzione o retrodatazione dei dati del run per migliorare la grafica. Le transizioni interpolate restano soltanto visuali.


### FR-UI-ROOM-01 — riquadro iniziale (2026-10-20)
Su richiesta utente rimuovere la sezione «Ambiente di ricerca» sopra la mappa, evitando spazio verticale dedicato. Qualificazione e provenienza continuano nelle informazioni pertinenti ai dati, ai risultati e alla guida; nessuna nuova qualificazione operativa implicita.


### FR-WX-VIEW-01 — leggibilità della precipitazione (2026-10-21)
Nel Monitoraggio privilegiare una vista meteo interpretabile: modalità Pioggia con quantità e scala inmm per la finestra oraria dichiarata, legenda sempre raggiungibile sulla mappa e opzioni separate per nuvole,vento,temperatura,umidità e probabilità. Evitare la fusione automatica dei colori di nuvole/pioggia e la sovrapposizione predefinita di tutti i valori. Una copertura meteo incompleta non deve sembrare il confine di una perturbazione: nascondere la grafica incompleta della vista e dichiarare il caricamento/missing, senza estrapolare o suggerire assenza di pioggia. Le previsioni di precipitazione non sono osservazioni radar. Questo chiarimento supera i default grafici precedenti, preservando livelli selezionabili e forzanti scientifiche.


### FR-MONITOR-FUSION-01 — accumuli per zona e validità distinta, 2026-10-21

La vista Pioggia e allerte associa accumuli previsionali completi1/3/6/12/24/48h alle geometrie ufficiali, all’ora scelta dalla barra meteo. Classi cartografiche quantitative, bollettino ufficiale e rischio idraulico autonomo restano tre significati distinti. Quantità basse del modello non annullano un bollettino; confini datati non prolungano la sua validità. Copertura parziale, geometria invalida e ore mancanti non diventano zero/basso rischio. Estremi dei campioni non sono massimi locali garantiti; precipitazione totale può includere neve equivalente. La nuova consultazione non chiude i requisiti di soglie/antecedenti/impatti qualificati di FR-MONITOR-FUSION-01. Report: reports/PIOGGIA-ZONE-E-ALLERTE.md.

## FR-EWS-BASELINE-01 — Riferimento architetturale MyDewetra, rettifica 2026-10-22

L’utente chiarisce che dal paper MyDewetra si riprende l’architettura di
integrazione di applicazioni, servizi e dati. Questa decisione sostituisce la
precedente interpretazione del 21 ottobre come obbligo di parità funzionale.
L’ID resta stabile per la tracciabilità; i registri MB-01…08 sono storici e
non introducono ulteriori criteri di accettazione per la replica del prodotto.

Il riferimento riguarda la separazione tra UI/API applicative, acquisizione
delle fonti, pubblicazione cartografica temporale, elaborazioni e aggiornamenti
dei client. In HAZARDIA l’avvio dei simulatori passa dai contratti versionati,
dai job e dagli adapter/worker isolati; la lettura dei risultati è distinta
dall’esecuzione del motore. Il paper non specifica un connettore PROPAGATOR:
non dedurre un protocollo eseguibile dalla sola architettura di alto livello,
né l’assenza di integrazioni nel prodotto completo dall’assenza nel paper.

Restano tutti i requisiti HAZARDIA originari e le richieste autonome successive:
Monitoraggio e Simulazioni, meteo/territorio reali, inneschi e risorse configurabili,
confronti, ottimizzazione robusta e priorità, rolling horizon, deadline e graceful
degradation. Restano AR-EXT-01, piattaforma generica, primi moduli incendi/alluvioni,
portabilità geografica, UI responsive con mappa centrale, stessa VM e fonti gratuite.
Nessuna nuova funzione, dipendenza da MyDewetra, copia del suo stack cloud o
installazione è implicita nel riferimento. Non viene modificato il manoscritto.
Analisi e mappatura: reports/MYDEWETRA-RIFERIMENTO-ARCHITETTURALE.md.
Il requisito di prodotto non attribuisce autorità per emettere allerte ufficiali,
non qualifica automaticamente soglie/effetti e non autorizza spese, accessi
ristretti, installazioni privilegiate o cambiamenti architetturali sostanziali.

La matrice di copertura è registrata in CHECKLIST.md, ID MB-01…MB-08.
Le priorità precedenti delle singole funzioni, incluso FR-23, non vengono
silenziosamente riclassificate: la baseline è un obiettivo complessivo, la
sequenza incrementale resta nel piano M0–M7. Nessuna equivalenza completata
può essere dichiarata senza verifiche eseguibili per ciascuna capacità.


## FR-MAP-WORKBENCH-01 — requisiti confermati23ottobre2026
L'esperienza cartografica di God's Eye View è un riferimento d'interazione, non una sostituzione dell'architettura HAZARDIA. Conservare simulatori, decision engine, snapshot e scenari. Acquisizione/backend nella VM e rendering nel browser; nessun passaggio diretto ai fornitori introdotto senza decisione esplicita. Mappa centrale, pannelli compatti/richiudibili, OSM sempre selezionabile, fallback dichiarato e conservazione della vista/ora/livelli. Ricerca geografica configurabile globalmente, dettaglio/copertura effettivi e rotella disabilitata. Fonti meteorologiche italiane verificate, osservazioni/previsioni/simulazioni distinte; timestamp, unità, emissione sconosciuta, copertura/risoluzione e missing espliciti. Timeline condivisa fra prodotti compatibili: nessuna sostituzione silenziosa con un'altra ora; livelli visuali non alterano le forzanti scientifiche. Cache e richieste limitate, deduplicate e protette dalle risposte superate; quote temporali e disco non significano dati/traffico illimitati. Valutare Cesium/terreno solo tramite prova reale prima di migrare, senza due mappe complete. Esri non attivato: utente senza licenza sceglie alternative gratuite. Nessuna nuova chiave commerciale obbligatoria, spesa, risorsa VM o deployment è autorizzata da questo requisito. Esiti nella CHECKLIST e report MAPPA-E-MONITORAGGIO-20261023; M0–M7 invariati.


## FR-MONITOR-LAYERS-02 / FR-TRAFFIC-VISUAL-01 — richiesta23ottobre2026
Integrare selettivamente i livelli utili di God's Eye View con copertura geografica verificata: meteo/osservazioni, territorio/esposizione, risorse/accessibilità, scenari/simulazioni. Riutilizzare i servizi esistenti; distinguere previsto, osservato, anomalia termica, incendio confermato, perimetro osservato e propagazione simulata con tempi/provenienza/legende. Immagini recenti separate dallo sfondo, data e nuvolosità, confronto temporale; mancanza locale o accesso non qualificato dichiarati senza controlli vuoti. Opzionali solo con dati/diritti utili verificati; esclusioni dell’utente preservate.
Traffico visuale su strade reali, indipendente e spento inizialmente: area selezionabile, densità/massimo, velocità per strada/preset ipotetici, pausa/ripresa/reset/velocità, seed e configurazione persistita. Rispettare i vincoli interpretati e dichiarare dati mancanti/limiti; chiusure ipotetiche distinte dalle osservate. Dicitura visibile obbligatoria “Traffico simulato — scenario ipotetico”. Limiti di carico e verifiche di riproducibilità/restrizioni/missing/performance. La sola animazione non è congestione o evacuazione: nessuna influenza automatica su tempi di intervento, ottimizzatore o risultati scientifici. Futuro collegamento solo esplicito, documentato e verificato. Runtime/acquisizioni nella VM, browser come client grafico, nessun nuovo servizio commerciale o installazione privilegiata. Stato effettivo e mancanze nel report LIVELLI-E-TRAFFICO-20261023; il requisito non dichiara tutti i livelli già disponibili.


## FR-MAP-CONSOLE-01 — decisione utente23ottobre2026
Monitoraggio e studio delle simulazioni occupano lo spazio sotto la sola barra superiore; nessuna pagina cartografica lunga. Navigazione livelli/scenari e palette a sinistra, parametri/proprietà dell’elemento selezionato a destra; pannelli richiudibili, scorrimento interno, ricerca e timeline sovrapposte, layout desktop/tablet/telefono. La rotella è ora abilitata per zoom nelle mappe convertite a viewport fisso: questa decisione esplicita supera i precedenti divieti applicabili a tali viste. Sopra pannelli/controlli lo scroll non modifica la mappa. Preservare controlli e stati reali, dati/provenienza/missing, accesso tastiera, scene stabili e tutti i contratti/limiti scientifici. Nessun nuovo motore, feed, risorsaVM o dispatch implicito. Pagine storiche non convertite conservano le impostazioni precedenti. Verifiche nel report MAPPA-A-SCHERMO-INTERO-20261023.


## FR-MONITOR-MODULES-03 — richiesta utente23 ottobre 2026
Il traffico visuale è un modulo opzionale indipendente, affiancabile ai livelli FIRE/FLOOD senza accoppiamento implicito a fisica, ottimizzatore o evacuazione. Aggiungere nel Monitoraggio terremoti osservati, inclusi eventi piccoli con magnitudo minima esplicita, fonte/periodo/copertura/missing; magnitudo distinta dall’intensità e nessuna previsione sismica o simulatore sismico implicito. Questa autorizzazione supera l’esclusione precedente dei terremoti limitatamente al catalogo osservato. Prevedere livello dedicato alla rete elettrica AT: tensioni dichiarate e sconosciute distinte, linee aeree/cavi/sostegni/sottostazioni, provenienza/data/copertura e limiti cartografici. Assenza cartografica non garantisce assenza di cavi; nessuna certificazione al volo, stato operativo o rischio inferiti. Moduli attivabili insieme con controlli laterali e carico limitato, niente duplicazione dei servizi esistenti; runtime/acquisizioni nella VM. Mantiene AR-EXT-01 e confini del decision engine. Il report MODULI-TRAFFICO-SISMI-RETE-ELETTRICA-20261023 distingue i PASS tecnici dalle coperture ancora BLOCKED.


## FR-MONITOR-SECTIONS-04 — rettifica utente23ottobre2026
Scenari e simulazioni e traffico ipotetico appartengono a Simulazioni e risorse, non ai livelli del Monitoraggio. Supera la collocazione visuale del traffico descritta in FR-MONITOR-MODULES-03, preservandone indipendenza e qualifiche. A sinistra selezione dei livelli, a destra parametri, incluse tutte le variabili meteo. Pioggia/nuvole combinabili con unità/legende distinte. Sismi osservati: attivazione e acquisizione coerenti; dati presenti, catalogo vuoto, errore, loading e fuori copertura distinti; scelta INGV/USGS secondo copertura, senza attribuire completezza mondiale ai piccoli eventi. Nessuna modifica implicita a fisica, ottimizzazione o classificazione delle allerte. Verifica e limiti in reports/MONITORAGGIO-AUDIT-E-SEZIONI-20261023.md.


## FR-MONITOR-CLOCK-05 —23ottobre2026
Il Monitoraggio usa un unico orologio di consultazione per tutte le fonti con dati previsionali, indipendente dall’attivazione del livello meteo. Orizzonte dall’unione delle validità disponibili; ogni prodotto conserva passo, copertura e scadenza, senza interpolare bollettini/classi o sostituire orari mancanti. Osservazioni datate e cataloghi statici non diventano previsioni. Nessun avvio implicito dei simulatori. Report TIMELINE-COMUNE-MONITORAGGIO-20261023.


## FR-MAP-DATA-SEMANTICS-06 —24ottobre2026
Sismi osservati: raggio schermo crescente con M e colori per classe, legenda coerente; nessuna equivalenza con danno/intensità. Meteo: quantità prevista e probabilità di pioggia sono scelte alternative con superfici/unità distinte; copertura nuvolosa indipendente come velo neutro bianco/grigio, non satellite. Nessuna conversione fra probabilità/nuvole/mm e nessun cambiamento implicito alle forzanti fisiche. Rendere espliciti mancanti, validità e copertura; audit dati non equivale a qualificazione scientifica. Report MAPPA-DATI-MAGNITUDO-E-METEO-20261024.


## FR-POWER-AERIAL-07 —24ottobre2026
Comando semplificato Cavi aerei e tralicci per consultazione degli ostacoli mappati relativi agli interventi dall’alto. Preset include linee aeree di qualunque tensione e sostegni; mantiene distinguibili tensione sconosciuta e classi dichiarate. Parametri completi in Filtri avanzati; copertura, origine OSM, timestamp e assenza di quote espliciti. La posa può essere dedotta dal tipo di oggetto OSM e non certifica cavi scoperti, isolamento, corrente presente o sicurezza del volo. Nessun vincolo operativo o modifica automatica a ottimizzazione/propagazione.


## FR-MONITOR-LAYERS-08 —24ottobre2026
Sfondo è un parametro cartografico separato dalle sovrapposizioni. Pericoli/risultati simulati, meteo e criticità territoriali hanno controlli distinti; i filtri FIRE/FLOOD dei risultati non abilitano implicitamente DPC/EFFIS. Le criticità hanno interruttore master, DPC ed EFFIS selezionabili separatamente e legenda visibile sulla mappa con fonte, validità, classi, mancante/scaduto. DPC è allerta ufficiale meteo-idro per zona; EFFIS è pericolosità prevista FWI/DC, non allerta ufficiale o incendio osservato. La legenda segnala l’ambiguità quando si sovrappongono entrambe le fonti; default solo DPC. Nessuna variazione delle soglie native, né rischio d’impatto locale qualificato dedotto dal colore.


## FR-ZONE-COVERAGE-09 —24ottobre2026
Distinguere livelli testuali del bollettino disponibili, geometria della zona qualificata e copertura degli indici previsionali. Rendere consultabili tutte le zone del bollettino anche con confine non qualificato, mostrando nomi/conteggi dei mancanti. Un fallback geometrico automatico è ammesso solo versoSHP ufficiale dello stesso bollettino e revisione, con nomi univoci/livelli concordanti/CRS e bounds controllati/geometria valida; tracciare la provenienza e non inventare il confine con riparazioni. Conservare raw, snapshot precedenti e validità/freschezza originali nelle derivazioni. Fonte disponibile non significa copertura zonale completa. Nessuna estrapolazione di allerte per date non coperte.


## FR-UI-ACTIONS-10 —24ottobre2026
Pioggia e allerte è un accesso sulla mappa allo stesso livello di Livelli, non una voce interna ai livelli. Centra è accanto allozoom+/−. Configura è vicino allo stato connessioneVM nella barra superiore. Date e copertura, Stato delle fonti e Posizione e riferimenti vicini risiedono in Dati e fonti; preservare contenuti e aggiornamenti esistenti, senza pulsanti duplicati nel menu mappa. Responsività e indipendenza dei pannelli conservate.


## FR-LAYER-CATALOG-11 —24ottobre2026
Ultima richiesta utente prevale sulla precedente collocazione a destra: selezione e opzioni dei livelli sono sulla sinistra, con ritorno all’elenco. Rimuovere Risorse e accessibilità, rendere riconoscibile il meteo mediante icona. Centri abitati è un livello indipendente sui dati esistenti, con stato/copertura/conteggio eON/OFF. Elencare esplicitamente i livelli effettivamente integrati con interruttori sincronizzati, e le categorie territorialiOSM disponibili; non introdurre checkbox di feed non acquisiti. Aprire le opzioni non attiva automaticamente un livello. Previsioni e osservazioni meteorologiche indipendenti; immagini recenti distinguono impronte/anteprime dai raster analitici. Dataset/forzanti/solver invariati, nessun censimento o completezza mondiale dedotti dalla cartografia.


## FR-I18N-01 — italiano e inglese
Italiano predefinito senza preferenza salvata; selettore Italiano/English nella barra comune, preferenza del browser persistita e condivisa con gli studi incorporati. Tradurre navigazione, controlli, legende, messaggi e guida; preservare valori/ID/payload scientifici, nomi assegnati dagli utenti, toponimi e testo ufficiale originale chiaramente identificato. Cambiare lingua non ricarica gli scenari o esegue modelli. Modelli CIMA/solver e VM unica invariati. Report reports/ITALIANO-E-INGLESE-20261024.md; futuri testi UI devono mantenere il catalogo.


## FR-MAP-CLOCK-AND-LAYERS-20261024
L’elenco dei livelli è uniforme a sinistra; ogni selezione apre le opzioni in un pannello separato a destra, mai annidate nella lista. Su schermi piccoli i pannelli si alternano. Mostrare sempre il tempo monitorato (data, secondi, offset UTC), distinguendo futuro e ora reale. Un timestamp mancante non va sostituito silenziosamente con l’ora attuale. La progettazione domain-agnostic preserva AR-EXT-01, contratti e compatibilità correnti; Stage 1 documentario non autorizza migrazioni implicite dei dati.


## AR-EXT-A2 — descrittori locali informativi
Il catalogo domain-package/0.1.0 descrive soltanto FIRE/FLOOD esistenti: metadati rigidi/digest, versioni e riferimenti approvati, senza import/esecuzione dinamica. Discovery opt-in; i validator, runtime hash, worker, JobStore e verifier attuali restano autorità. Presenza del descriptor distinta da installazione/dati/qualifica/autorizzazione. Nessuna migrazione di contratti o scenari. Schema `schemas/domain_package.schema.json`, guida `docs/DOMAIN-PACKAGES.md`.


## AR-EXT-A3 — binding compatibile dei worker esistenti
Il catalogo è consumato nel processo pipeline isolato da una tabella locale recensita: nessuna esecuzione di riferimenti arbitrari. Conservare comandi, ambienti, hash engine pre/post, guard FLOOD, validator, JobStore e qualifica. Errori dei metadati o revisioni incompatibili causano fallimento classificato. Ogni nuova esecuzione conserva una ricevuta esclusiva con identità/versione/digest del descriptor e hash degli input/runtime; nessuna migrazione dei run o contratti legacy. Freeze descriptor a execution-time distinto dal freeze request/runtime alla submit.


## AR-EXT-A4 — semantica delle policy decisionali esistenti
Le policy versionate 0.5/0.6 sono definite localmente e immutabili; unità/effetto/semantica non sono intercambiabili. Unknown policy/versione/unità sono rifiutati. L’estrazione conserva le formule, i vincoli, solver/backends, watchdog e verifier indipendente; non introduce predicate/righe condivise col checker, modelli d’efficacia o migrazioni dei contratti. Il modulo policy non richiede dipendenze numeriche/geospaziali/JSON Schema nell’ambiente solver.


## AR-EXT-01 — A5a exchange boundary (2026-10-24)
Il nucleo di scambio per prodotti grigliati usa identificativi opachi di dominio e quantità, contratti versionati e verifica esplicita di unità, griglia, tempo, provenienza e incertezza. I consumatori dichiarano requisiti; incompatibilità e dati critici ignoti non diventano compatibilità implicita. Nessuna conversione, composizione o esecuzione è dedotta dal metadata match. Semantica FIRE/FLOOD e validator storici restano negli adapter legacy con facciata compatibile. Il sidecar non riscrive prodotti/archivi. Questo confine non sostituisce ancora gli ingressi legacy dei job o il verificatore indipendente. Guida: docs/EXCHANGE-CONTRACTS.md; verifiche: reports/EXCHANGE-CONTRACTS-A5A-20261024.md.


## FR-MONITOR-CONTROLS-20261024 — rettifica UI confermata
Orario dei dati compatto accanto alla ricerca in alto, con istante/fuso completi accessibili nel dettaglio e indicazione futura coerente con la timeline. Sfondo e nomi delle località sono configurazione cartografica, non voci autonome del catalogo livelli. Lingua/configurazione restano nell'header senza sovrapporsi ai controlli della mappa. Il clic sul nome Terremoti attiva le osservazioni e apre parametri nel pannello destro; la casella conserva il controllo di disattivazione. Acquisizione, assenza di eventi e dati mancanti devono restare distinguibili. Report MONITOR-CONTROLS-20261024.


## FR-ADMIN-LEVELS-20261024 — Confini
La voce Confini apre a destra tre opzioni indipendenti: nazioni, regioni, province. Confini amministrativi distinti da zone di allerta/criticità e da input dei simulatori. Copertura e fonte esplicite: nazioni globali NaturalEarth50m, regioni/province Italia Istat2026 nell'attuale incremento; fuori copertura non inventare geometrie. Preserve default regionale e caricamento differito per opzioni aggiuntive. Guida docs/ADMINISTRATIVE-BOUNDARIES.md.


## FR-MAP-LAYER-GROUPS-20261025 — livelli, scala e legende
Richiesta confermata: Monitoraggio con voci uniformi raggruppate per previsioni/criticità, osservazioni, territorio/infrastrutture, cartografia/catalogo; visibilità separata dai parametri nel pannello destro unico. Legende/stati raccolti in un accesso compatto, mantenendo scale, tempi e missing. Indicatore di zoom solo per restrizioni realmente applicate; edifici da zoom15 nel solo Monitoraggio, senza alterare acquisizione, esposizione o simulatori. Favicon coerente con marchio HAZARDIA. Report [LAYER-CONSOLE-20261025](reports/LAYER-CONSOLE-20261025.md).


## FR-MAP-DUAL-CLOCK-20261025
Rettifica utente: VM connessa ultimo controllo a destra della barra. Orologio reale del client HH:mm:ss visibile accanto alla validità dei dati sulla mappa, distinta e marcata Previsione quando futura. Non chiamare la validità selezionata ultima acquisizione/osservazione. Tempi/offset dettagliati e missing conservati. Rapporto `reports/DUAL-CLOCK-20261025.md`; nessun cambio timeline/motori.


## FR-MAP-PIN-ZOOM-20261025
Richiesta utente: zoom corrente e selettore di scale accanto a +/−/Centra. Nel Monitoraggio un pin di navigazione unico, distinto dagli inneschi, è riferimento per Centra (zoom conservato) e scelta zoom (centro sul pin); senza pin rimangono centro/fit precedenti. Pin posizionabile, trascinabile e rimovibile, nessun cambiamento agli input scientifici. Report `reports/MAP-PIN-ZOOM-20261025.md`.
