# HAZARDIA — Consolidated Requirements Specification v1.4

**State:** normative requirements baseline. M0–M4 technical fixture gates and M5/M6 controlled software slices have executed evidence; the local dashboard is available. Full P0/research-release completion remains BLOCKED and is tracked exclusively in CHECKLIST.md. Controlled replay and observed software performance do not qualify physical effects, historical skill or operational use. Priorities: P0 required for research release, P1 post-research additions. The reference to real engines means *actual execution* rather than placeholder screenshots. A capability unavailable due to input access must be reported BLOCKED; never silently replaced by a mock.

## 1. Scope and actors

- Hazards: wildfire and flood in V1, validated separately before joint cross-region allocation. Other hazards may be added via adapters but are not release acceptance targets.
- Actors: researcher (configures runs and evaluates), decision analyst (builds and compares plans), regional coordinator (controls own resources), suprarregional coordinator (proposes transfers), human authorizer (authorizes modeled real-world operations). No dispatch or evacuation automation.
- Time horizons: real-time-ish response with rolling-horizon recomputation and 60 s **decision response budget**; preventive prepositioning is also required. Physical model simulation latencies are separately tracked.
- Territory: configurable geographies worldwide, including cross-border basin and independently scoped administrative authorities. User-confirmed primary Italian wildfire and flood examples: **Abruzzo** (2026-10-15); specific AOIs/basins/events selected after source/rights/coverage audit, not assumed calibrated. Previous Tuscany examples remain historical feasibility evidence. Geographic portability and planned synthetic cross-territory tests remain required; Senegal is a candidate transferability study.
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
The dashboard must support a genuinely detailed licensed geographic background, legible place/neighbourhood/road context, metric scale, WGS84 coordinates, local place/coordinate search and point inspection with provenance/coverage. Prefer official regional orthophoto consultation where available; retain local satellite fallback. Declare imagery acquisition date, native pixel size and network dependency. Never imply basemap pixel size is simulator grid size, model accuracy or an observation of the simulated event. Named points/nearest streets are contextual; administrative containment, access safety, cadastral and elevation claims need their own qualified source. Bound tile download/cache and visible features; map exploration must not run simulators. Initial validated scope is Abruzzo place gazetteer plus central L’Aquila OSM context; detailed official administrative polygons remain NOT RUN. See reports/MAPPE-DETTAGLIO.md and CHECKLIST map-detail checkpoint.

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
