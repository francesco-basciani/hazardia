# HAZARDIA — Completion & Acceptance Ledger (v1.4)

**CONTINUOUS EXECUTION AUTHORIZED (2026-10-15): user requests autonomous progress through M3–M7 to a testable dashboard.** M0–M4 technical-fixture gates PASS. M5/M6 software tests PASS within declared synthetic scope, full gates BLOCKED by forecast/effect/capability-optimization qualification. M7 technical verification/30minstability/local supplement executed; historical validation, incomplete P0s and large-load research release BLOCKED. Local dashboard available at http://127.0.0.1:8080/. Do not ask for routine milestone permission again. Stop only for substantial intervention outside existing scope/bounds: costs, privileged installs, large downloads/resource changes, unresolved rights/physical-model replacement, public deployment/push/real operations. All runtime one Linux VM, Abruzzo primary, two hazards. Earlier per-milestone authorization guards are superseded.

This is a tracked acceptance checklist, **not** an assertion that work exists. `SPEC.md` is normative for requirements, `PLAN.md` for ordered milestones, `CHECKLIST.md § Traceability` for mappings, and `research/EVIDENCE.md` for scientific claims. Use IDs and do not delete unresolved failures.

## Rules for changing status

- Lifecycle: `NOT STARTED` → `IN PROGRESS` → verification result `PASS` / `FAIL` / `BLOCKED` / `NOT RUN`. `PASS` requires observation and independent validation; a manually checked box without evidence is **not** PASS.
- Evidence template for each item: requirement/gate ID; scenario+fixture; procedure and command; expected outcome; observed outcome; PASS/FAIL/NOT RUN; evidence path; `run_id`; Git SHA; machine/OS and dependency versions; date/time; responsible agent and reviewer.
- A missing test must stay `NOT RUN` even when implementation is present. Real engine runs must be differentiated from mocks and synthetics. If a source is unavailable, mark `BLOCKED` and explain it.
- Do not modify evidence from past runs; issue a new immutable manifest. Review `git diff` and reconcile ledger at each milestone gate.
- `PASS` on every P0 requirement + every mandatory gate, with no unapproved BLOCKED items, is necessary but **not sufficient** for operational approval; research release and operational use are distinct.

## Current acceptance audit — 2026-10-16

[Full plan audit](reports/VERIFICA-PIANO.md), run `plan-audit-20261016T054141Z`: complete release **BLOCKED**. FR-03, FR-18 and FR-26 aggregate acceptance corrected to BLOCKED; historical scoped software PASS results remain unchanged. A PASS below is limited by its evidence column and is not model calibration, full usability or operational approval. Latest additions and user requirements are reconciled in the audit matrix and appendix; chronological checkpoints retain their original meaning.

## A. Functional requirements (all P0 unless indicated)

| Check | ID | Scope | Status | Test/evidence | Reviewer |
|---|---|---|---|---|---|
| [x] | FR-01 | Register AOI, CRS, units, time zone, source policies, administrative jurisdictions, calibration metadata,  | PASS | M2 profiles/negative contracts, §R; calibration UNKNOWN preserved | Codex self-check |
| [x] | FR-02 | Acquire/cache satellite observations and preprocessed products via replaceable connectors; record acquisit | PASS | M1 real Copernicus/ERA5 cache and hashes; M3 provider boundary, scoped local sources | Codex self-check |
| [ ] | FR-03 | Cluster and track events across time/sensors without merging unrelated incidents; ambiguous associations e | BLOCKED | M2 authored association/dedup/ambiguity tests PASS; required simple-baseline comparison NOT RUN; full acceptance BLOCKED, audit reports/VERIFICA-PIANO.md | Codex self-check |
| [x] | FR-04 | Fuse observations conservatively accounting for sensor dependence/uncertainty and conflicting evidence; no | PASS | M2 conservative correlated/conflicting fixture fusion; confidence not calibrated probability | Codex self-check |
| [ ] | FR-05 | Track sensor/feed health (staleness, outage, coverage, disagreement) and make health available to service- | BLOCKED | M1 QC + M6 controlled staleness pass; automatic real sensor/feed health chain incomplete | Codex self-check |
| [ ] | FR-06 | Acquire weather history, forecasts and ensembles (wind, precipitation and appropriate supporting variables | BLOCKED | Real ERA5 and current MET source audit PASS; complete matched forecast/ensemble forcing absent, M7 report | Codex self-check |
| [x] | FR-07 | Prepare/validate hazard-specific model inputs; run real wildfire and flood simulation jobs separately, reg | PASS | M1/M3 actual PROPAGATOR + HMC→REFlEx runs; disclosed patch/uncalibrated scenario | Codex self-check |
| [x] | FR-08 | Separate hazard evolution, physical suppression/mitigation where modeled, impact-only interventions, and e | PASS | M2/M3 immutable physical hashes; IMPACT_ONLY synthetic effects; unsupported physical action rejected | Codex self-check |
| [x] | FR-09 | Represent population/infrastructure exposure, vulnerability and access/road constraints with provenance an | PASS | M2 contracts/geo co-location and M3 synthetic exposure/access; real inventories/vulnerability unqualified | Codex self-check |
| [x] | FR-10 | Model resource type, skills, qualifications, equipment, position, home authority, schedule, fatigue, maint | PASS | M2 contracts + M3 independent verifier: schedule/rest/autonomy/qualification/road/consumables UNKNOWN negatives | Codex self-check |
| [x] | FR-11 | Support hierarchy of regional ownership plus suprarregional transfer proposals; no commitment without matc | PASS | M4 checked two-area reserve/authorization/no-overbook; M6 coordinator outage | Codex self-check |
| [x] | FR-12 | Implement versioned solver interface, initial constrained solver, hard-constraint validator external to so | PASS | M3 HiGHS/reference + independent checker; M5 robust objective/rolling continuity controlled tests | Codex self-check |
| [ ] | FR-13 | Return multiple candidate strategies or classified non-success (PROVEN_INFEASIBLE, TIMEOUT_UNPROVEN, INVAL | BLOCKED | Typed negative outcomes PASS M3/M5; current success publishes one optimum plus counterfactual, candidate portfolio incomplete | Codex self-check |
| [x] | FR-14 | Within 60 seconds of a **accepted decision request** provide safe validated proposal or classified status  | PASS | M5 two30-request campaigns incl queue/verification/publication; final p95 .820538s/max .828716s, experimental scope | Codex self-check |
| [x] | FR-15 | Define six capabilities (safety, situational awareness, allocation, regional coordination, forecast, expla | PASS | M6 six controlled capability states/rules/CAS/fresh synthetic recovery; no operational health certification | Codex self-check |
| [ ] | FR-16 | Under resource/data/infrastructure/environment degradation, minimize loss of prioritized capabilities, rec | BLOCKED | M6 rule-based fallback + measured diagnostic/loss PASS; general prioritized capability optimization not implemented | Codex self-check |
| [ ] | FR-17 | Monitor new forecast/data revisions and emit *impact-based* georeferenced alerts with uncertainty, evidenc | BLOCKED | M5/M6 authored alert lifecycle PASS; real georeferenced predictive impact watcher/review-window qualification incomplete | Codex self-check |
| [ ] | FR-18 | Local web UI: map/layers, scenario builder, resources, comparison 2+ synchronized maps, timeline playback, | BLOCKED | Small UI slice PASS; full territory/source/event/ensemble builder and candidate workflow incomplete; reports/VERIFICA-PIANO.md | Codex self-check |
| [x] | FR-19 | Preserve immutable experiment manifest (inputs, versions, seeds, data rights, execution environment), metr | PASS |3275file supplement/transport hashes and packaged source replay PASS, final checkpoint §V; complete physical replication unqualified | Codex self-check |
| [x] | FR-20 | Support independently evaluated preparedness/prepositioning strategies using the same admissibility rules  | PASS | M6 same independent admissibility checks for2/8min authored preparation; no empirical efficacy claim | Codex self-check |
| [x] | FR-21 | Simulator and connector worker jobs are isolated and bounded; failure in flood must not falsely invalidate | PASS | M1 supervisor and M6 actual owned flood-worker SIGKILL ERROR/unusable, FIRE remains validated | Codex self-check |
| [x] | FR-22 | Operate locally without paid/cloud services; support free reproducible Linux isolation on macOS; support f | PASS | OneVM runtime/models/preparation/server/solver, free/local/loopback; future-machine portability NOT RUN | Codex self-check |
| [ ] | FR-23 | Add user-submitted field reports, subscriptions/notifications, external interoperability, multi-user colla | NOT RUN | P1 deferred by original scope; no extra domains, application agents or external notifications | Codex self-check |

## B. Quality requirements

| Check | ID | Verification focus | Status | Test/evidence | Reviewer |
|---|---|---|---|---|---|
| [x] | QR-01 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M3/M4 verifier negatives + M6 critical UNKNOWN blocks new proposals; all research outputs nonoperational | Codex self-check |
| [x] | QR-02 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M5 fixed4resource2hazard benchmark,30/30 useful and terminal within60s; no hard-real-time proof | Codex self-check |
| [x] | QR-03 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M6 actual owned worker crash job5ed4fe3e..., typed ERROR, subsequent FIRE independently verified | Codex self-check |
| [ ] | QR-04 | See SPEC §4 and §8 + CHECKLIST § Traceability | BLOCKED | M0/M1 narrow seeded fire replay PASS; full physics/independent install replication unqualified | Codex self-check |
| [x] | QR-05 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M1/M2 independently read raster/array CRS/units/hash/time mismatches rejected, versioned products | Codex self-check |
| [x] | QR-06 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M3/M4 identical physical context across panes; mismatched joint windows rejected; impact-only effect labeled | Codex self-check |
| [x] | QR-07 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M3 loopback/Host/Origin/JSON/path/CSP checks; source push authorized and verified; no public service/dispatch. Deployment security review not performed | Codex self-check |
| [ ] | QR-08 | See SPEC §4 and §8 + CHECKLIST § Traceability | BLOCKED | M2 two-profile shared contracts/state PASS; end-to-end physical/decision portability outsideAbruzzo NOT RUN | Codex self-check |
| [x] | QR-09 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M1–M6 job/decision IDs/hash/queue/run metrics/classified failures; explicit retry only | Codex self-check |
| [x] | QR-10 | See SPEC §4 and §8 + CHECKLIST § Traceability | PASS | M5 controlled true-warning/false-alarm/stale/unknown-effect replay, raw lead/caveats; not real forecast skill | Codex self-check |

## C. Milestone and scientific closure gates

| Check | Gate | Technical evidence | Scientific evidence | Status |
|---|---|---|---|---|
| [x] | M0 | Original feasibility criteria reviewed; real engines/technical bridge, source/stack/benchmark assessment and contract examples evidenced; later physical qualification not passed | `reports/M0-gate-review.md`, existing E-M0 evidence/manifests; historical FAIL/BLOCKED unchanged | PASS (feasibility) |
| [x] | M1 | Real ingestion/two-hazard adapters, bounded jobs/manifest/CLI;33unit/6real integration checks; applicable extension phases | reports/M1-integration.md, §Q, E-M1-001…005; later-core phases NOT RUN | PASS (technical) |
| [x] | M2 | Shared territory/event/weather/consequence contracts, two profiles, negative/real-product tests | reports/M2-domain.md, §R, E-M2-001…003 | PASS (technical) |
| [x] | M3 | Genuine matched maps, bounded solver + independent verifier, responsive local UI | reports/M3-dashboard.md, m3-dashboard-20261015T192310Z | PASS (technical fixture) |
| [x] | M4 | Controlled two-region joint fire/flood resource allocation, checked baselines and browser | reports/M4-joint.md, m4-joint-20261015T194711Z | PASS (technical fixture) |
| [ ] | M5 | Timing/rolling/alert software PASS controlled; real forecast/impact and full baselines incomplete | reports/M5-adaptive.md, E-M5 | BLOCKED |
| [ ] | M6 |12integration groups + actual worker crash/UI PASS; full capability objective/qualification incomplete | reports/M6-degradation.md, E-M6 | BLOCKED |
| [ ] | M7 | Final technical pilot and reconstruction executed; historical/portability/large-load release blockers | reports/M7-validation.md, E-M7 | BLOCKED |

## D. Mandatory cross-cutting controls

| Check | Control | Required evidence | Status |
|---|---|---|---|
| [x] | G-01 Contract fixtures | All11SPEC7.1 boundaries, version0.1.0,124PASS incl78negatives; §M/ADR-0003/`m0-contracts-20261015T153248Z`. M1 adapter/product revalidation PASS §Q; later consumers NOT RUN | PASS (M0/M1 scope) |
| [x] | G-02 Research vs safety parameters | M2/M3/M6 synthetic threshold/effect profiles separated; no operational policy assertion | PASS |
| [x] | G-03 Run identity and provenance |3275file supplement/transport verification PASS, source998b934; final checkpoint below | PASS |
| [x] | G-04 Deadline per request | M5 fixed workload and corrected external short-watchdog tests; historical .800246s FAIL preserved | PASS |
| [x] | G-05 p95 benchmark | M5 two pinned n30 campaigns with raw timings/useful/terminal rates; CPU/RSS whole-suite log | PASS |
| [ ] | G-06 Research replication | Supplement/pinned local replay and independent-prefix native rebuild PASS; fresh OS boot/full historical replication NOT RUN | BLOCKED |
| [ ] | G-07 Release integrity | Not all P0 pass: real forecasts/history/candidate portfolio/capability objective/large-scale/per-machine validation | BLOCKED |

## E. Verification record template (copy once per executed check)

```text
Item ID:
Scenario / fixture:
Prerequisite versions / machine:
Command or reproducible manual procedure:
Expected:
Observed:
Verification: PASS | FAIL | NOT RUN | BLOCKED
Evidence files and immutable run_id:
Git SHA and dirty state:
Timestamp (UTC):
Agent / reviewer:
Open defects and next action:
```

## F. Historical initial status (superseded by current ledger)

All product P0 entries and M1–M7 remain NOT RUN. M0 was authorized on 15 October 2026; current gate BLOCKED. Standalone upstream fire smoke runs are not framework integration or operational validation. Later milestone gates still require approval; large downloads/privileged installations remain approval-bound.


---

## Traceability

Paths in the matrix remain planned unless linked to an executed run below. M0 evidence does not imply product-requirement completion. Every failed requirement blocks research-release claim unless explicitly descoped with user approval.

| Requirements | Scenario | Milestones | Test or acceptance ID | Evidence to capture |
|---|---|---|---|---|
| AR-EXT-01; FR-02, FR-07, FR-12, FR-19, FR-21, FR-22 | SC-01,SC-02,SC-08 | M1,M2,M3; repeat later gates | AT-EXT-01…05 (§N) | contract consumption, provider separation, core-unchanged replacement, dependency/run evidence; no interface-only claim |
| FR-01, FR-02, FR-05, FR-22 | SC-01, SC-08 | M0,M1,M2 | AT-DATA-01, AT-GEO-01, QR-08 | profiles, source provenance, freshness/error cases |
| FR-03, FR-04 | SC-01 | M1,M2 | AT-FUSE-01/02 | duplicate detections, disagreement baselines |
| FR-06, FR-17 | SC-05 | M1,M5,M6 | AT-WX-01, AT-ALERT-01, QR-10 | forecast revisions, alert histories, lead times |
| FR-07, FR-21 | SC-02,SC-06 | M0,M1,M6 | AT-SIM-01/02, AT-FAULT-01 | exact model versions, real outputs and failures |
| FR-08,FR-09 | SC-03 | M2,M3 | AT-IMPACT-01/02 | intervention evidence grade, exposure & roads |
| FR-10,FR-11 | SC-04 | M2,M4 | AT-RES-01/02, AT-AUTH-01 | synthetic inventory and transfer audit |
| FR-12,FR-13,FR-14 | SC-03,SC-04 | M3,M4,M5 | AT-SOLVER-01/02, AT-TIME-01 | independent constraint verifier, timeouts |
| FR-15,FR-16 | SC-06 | M5,M6 | AT-DEGRADE-01/02/03, QR-03 | six-capability vector and outcome delta |
| FR-18 | SC-03,SC-05 | M3,M4,M6 | AT-UI-01/02, QR-06 | synchronized maps & time/provenance |
| FR-19 | SC-07,SC-08 | all,M7 | AT-REPLAY-01, AT-HIST-01/02 | hashes, raw runs, sourced validation |
| FR-20 | SC-01 | M6 | AT-PREP-01 | prepositioning vs reference policy |
| FR-23 (P1) | future | post-V1 | pending separate specification | no first-release assertion |

**Fixed negative cases:** duplicate hotspot observations; conflicting satellite readings; missing forecast issue-time; resource overbooking; unauthorized transfer; unsafe road access; timed-out solver without proof; simulator crash; expired forecast; high-confidence false alarm; missing hazard-specific intervention model; mismatched weather between UI panes. Each should fail safely.

**Research link:** RQ1 architecture/capability, RQ2 decision effect, RQ3 reliability/performance (see research protocol); data-source tests inform validity rather than a claim of better satellite science.


## Completion ledger policy
Use `CHECKLIST.md` to report each P0 FR-01..FR-22 and QR-01..QR-10 separately, along with milestone acceptance gates. A multi-requirement row in the matrix above does **not** justify bulk PASS. Evidence must be specific to each requirement, including negative tests where applicable. Requirements FR-23 (P1) are explicitly deferred and not counted as first-release completeness. Contract schemas, safety parameter profiles and immutable manifests have cross-cutting gate rows in the completion ledger.

## G. Responsive UI and performance release blockers (v1.4)

| Check | ID | Verification needed for PASS | Status | run_id / test report |
|---|---|---|---|---|
| [x] | FR-24 | 375/768/1440 px browser and keyboard/accessibility walkthrough; controls usable without hidden essential actions | PASS | M3/M6/M7 375/768/1440px controls+keyboard+axe0violations; contrast incompletes remain, no WCAG certification |
| [x] | FR-25 | Genuine long simulation job while UI remains responsive; job states and cancellation verified | PASS | M3 genuine CIMA job with usable map/decision and cancellation/retry; M6 worker-crash isolation |
| [ ] | FR-26 | Real paired map outputs synchronized at same AOI/time, differences, export and mismatched-case rejection | BLOCKED | Small matched-pair/export tests PASS; complete physical workflows/large-layer acceptance incomplete, QR-14 FAIL; audit report |
| [x] | FR-27 | Cold/warm caching, paging/windowing, no redundant simulator restart | PASS | M2 indexed bounded window; M3 catalog/assets/cache/poll and no simulation POST from pan; M7 stress limits explicit |
| [x] | FR-28 | Route/job/render/memory observability, correct errors, no secret leakage | PASS | M3 browser/server metrics, M1 job RSS/CPU/queue, M5 timing/logs and typed UI error states; no credentials exported |
| [x] | QR-11 | P95 feedback <=200 ms and >=30 fps map interaction benchmark on pinned environment | PASS | M7 browser30actions/type and30map moves on supported case;100kdisplay stress separately FAIL |
| [x] | QR-12 | Cached read API p95 <=500 ms; dashboard useful <=3 s on 3 cold navigations | PASS | M3 API30reads p95~6.55ms, M7 threecold useful displays within3s; pinned local fixture |
| [x] | QR-13 | Long worker job, cancel/retry, nonblocking browser navigation, correct partial status | PASS | M3/M6 real isolated job/error/cancel/retry plus nonblocking client; partial outputs unusable |
| [ ] | QR-14 | Scaling and 30-minute session memory/latency metrics with trace and explicit limits | FAIL | M7 100kdisplay stress no valid mapFPS sample and1.316GBheap; 24/48slotfullM/L unsupported;historical30min smallfixture PASS; currentUI newsoak NOT RUN |
| [x] | M0-PERF | Host/browser inventoried; bounded fixture design and profiling protocol recorded; product UI metrics NOT RUN | PASS | `reports/M0-performance-baseline.md`; `m0-audit-20261015T122006Z` |
| [ ] | M7-PERF | All performance budgets measured and met or release blocked with owner approval | BLOCKED | M7 supported UI tests pass;100kdisplay stressFAIL,old30minstabilityPASS/newUIsoakNOTRUN; no target waived |

PASS requires real test execution, immutable run evidence, benchmark device/configuration, observed results, Git SHA and review, in accordance with the status policy at top of this ledger. P0 performance items block release and must be reconciled in SPEC and PLAN.


## H. Initial M0 executed verification ledger — 15 October 2026 (historical)

Common identity: `run_id=m0-audit-20261015T122006Z`, UTC start `2026-10-15T12:20:06Z`; precise later timestamps in prerecords/manifest. Git SHA/dirty null (not a repository), baseline document hashes in `baseline.json`; source commits in `sources/*/repository.json`; host/versions in `host-and-git.json` and `reports/m0-environment-freeze.txt`. Agent: Codex / Research Recorder; verification via separate artifact reader `verify-evidence.py`; human reviewer PENDING. Evidence root: `experiments/runs/m0-audit-20261015T122006Z/`. No PASS of a product FR/QR inferred from these subchecks.

| Item | Procedure / expected | Observed | Outcome | Evidence |
|---|---|---|---|---|
| M0.1 | Read eight baseline files; git status/remote/rev-parse; inventory host/tools | All documents read; git commands exit 128, no repository; M4 Pro/48 GiB/56 GiB free | PASS audit, Git prereq absent | `baseline.json`, `host-and-git.json` |
| M0.2 | GitHub API tree/commit; curl pinned raw files; recompute Git blob hashes; inspect licenses/deps | 110 files match; 3 EUPL-1.2 engines; legacy flood env identified | PASS source audit | `sources/`, `reports/m0-evidence-verification.json` |
| M0-ENV-01 | urllib HTTPS with system Python | CA verification failed; no TLS bypass, subsequent curl worked | FAIL original attempt | `initial-https-failure.txt` |
| M0-HARNESS-01 | First fire command should use venv | Resolved symlink invoked base Python: missing Numba | FAIL original attempt | `direct-cold-execution.json`, `child-warm-execution.json` |
| M0-FIRE-120 | Seeded 64²/2 realisations, 120 simulated s should spread >1 cell | Ignition=1, nonzero=1, t=120; execution assertion failed | FAIL | `*-retry-execution.json`, `diagnostic-execution.json` |
| M0.3 / M0-FIRE-600 | New prerecord 600 simulated s; genuine upstream core; output shape/bounds/ignition/spread and GeoTIFF roundtrip | Three successful executions, 9/6/6 nonzero cells; verified rasters | PASS standalone only | `fire-config-600s.json`, `pilot600-*/`, `*-execution.json` |
| M0-RNG-01 | Compare SHA-256 arrays with same seed/thread/fixture, exact repeatability expected | Three different hashes; no statistical stability claim | FAIL | `reports/m0-evidence-verification.json` |
| M0.4-HMC | Preflight Fortran/Linux/data availability before real compile/run | No gfortran/verified runner; no full static/forcing domain | BLOCKED | `hmc-preflight.json` |
| M0.4-REFLEX | `python reflex_step4_flood_mapping.py --help` import preflight; then full chain if possible | Exit 1 missing geopandas; GRASS/complete geospatial env and data unavailable | BLOCKED (real sim NOT RUN) | `reflex-dependency-probe.json` |
| M0.5 | Inspect units/grid/time and test real HMC→REFlEx bridge | Q m³/s vs CSV stream/Qrp/Q0/tconc and volume transform identified; no real coupled run | BLOCKED | `reports/M0-feasibility.md`, pinned source locations |
| M0.6 | Audit official sources/access/rights and design local cache | Source matrix delivered; credential/product-specific rights and historical data unresolved | PASS inventory; acquisition NOT RUN | `reports/M0-feasibility.md` |
| M0.7 | Direct Python vs new process, matched fixture | Both execute; stochastic outputs not equivalent; true Linux isolation absent | PASS execution; equality FAIL; Linux BLOCKED | `pilot600-cold-execution.json`, `pilot600-child-execution.json` |
| M0.8 | Compare solver/backend/UI/isolation, record conditional ADR | Candidates and alternatives documented; no framework built | PASS assessment | `reports/ADR-0001-M0-candidate-stack.md` |
| M0.9 | Record all results, limits and gate | Negative results retained; no-go M1; H1–H3 unsupported | PASS recorder/report; M0 BLOCKED | `research/EVIDENCE.md`, `manifest.json`, feasibility report |
| M0.10 | Freeze host/browser and proposed S/M/L fixtures/profiling | Inventory + design delivered; UI/API/60 s/stress absent | PASS deliverable; product tests NOT RUN | `reports/M0-performance-baseline.md` |
| G-01-M0 | Freeze valid/invalid schemas and execute every SPEC §7.1 boundary | Semantic inventory only; schemas/tests absent | NOT RUN | candidate ADR contract table |
| M0 gate | All mandatory prerequisite evidence for M1 | Flood runs/bridge, replay, full contracts and code identity unresolved | BLOCKED | report decisions/next increment |

The M0 manifest is a local append-only evidence artifact with SHA-256 inventory, not evidence that the complete framework run-identity implementation (G-03 / FR-19) passes. No GUI, alert, solver, intervention, safety, geographic-transfer or fault-isolation product test has run.


## I. Authorized M0 UTM continuation — current checkpoint 15 October 2026

Common identity: `run_id=m0-linux-rng-20261015T124458Z`, parent `m0-audit-20261015T122006Z`, UTC start2026-10-15T12:44:58Z. Git SHA/dirty null (no repository); baseline document hashes and source commits in prerecord/final manifest. Mac M4Pro48GiB; guest Ubuntu22.04.5ARM64/4vCPU/8192MiB/19GiB. Detailed commands, UTC and dependency versions: per-stage execution JSON, guest freeze/apt list and current report. Agent/reviewer: Codex / Research Recorder with separate artifact readers; external human review PENDING. Evidence root `experiments/runs/m0-linux-rng-20261015T124458Z/`; GUEST=`guest-final/artifact-final/`. §H outcomes stay historical; current superseding checks are explicit below. No product FR/QR bulk PASS.

| Item | Procedure / expected | Observed | Outcome | Evidence |
|---|---|---|---|---|
| M0-VM-01 | Official image digest, UTM bounded VM, boot/SSH, disk resize, shutdown | Image SHA matches;4vCPU/8192MiB/19GiB; ARM Linux runs; final stopped/no localhost listener | PASS | `image-verification.json`, `guest-inventory.json`, `vm-final-state.json` |
| M0-BUDGET-02 | Compare authorized5GiB/20GiB/8GiB4CPU with accounting and config | Conservative download<1.5GiB, FS~5.24GB used, main disk19GiB; guest-only installs | PASS | `image-download.json`, `guest-sources-and-budget.json`, `archive-final.json`, report accounting |
| M0-RNG-02 | Two seeds,3reps×3processes perOS/mode; compare complete probability/fire/arrival bytes | 108 recorded runs; worker-context1thread identical perseed/OS and acrossMac/Linux; seeds differ | PASS limited fixture | `rng-plan.json`, `rng-artifact-validation.json`, `.npz`, Linux raw records |
| M0-RNG-01-CONTROL | Old serial seed with/without priming should repeat | Mac9different outputs/9 perseed; Linux repeats; originalmethod FAIL retained | FAIL Mac controls | same RNG raw artifacts and verifier |
| M0-HMC-BUILD | Compile unmodified pinned source GNU/NetCDF and verify source/binary hashes | ELF aarch64; GFortran11.4;125 original guest source files match | PASS | `hmc-build.json`, `hmc-full-source-integrity-correction.json`, GUEST/source-integrity.json |
| M0-HMC-INPUT-V1 | Genuine model with incomplete nodata metadata | STOP/error but process exit0; no complete products | FAIL | `hmc-fixture-v1.json`, GUEST/hmc-run-v1.log |
| M0-HMC-POINT-NC | Genuine run with point NetCDF output | netCDF4 operation on classic file, STOP/exit0 and partial output | FAIL | `hmc-fixture-v2.json`, GUEST/hmc-run-v2.log |
| M0-HMC-RUN | Corrected synthetic9² input; six steps, finite/nonnegative gridded Q and positive response | Six NetCDF products; gridmax180.75862m³/s; sectionmax151.50m³/s | PASS standalone | `hmc-fixture-v3.json`, `flood-artifact-check.json`, GUEST/hmc-fixture-v3/ |
| M0-HMC-DRY | Matched zero-rain control | Six finite raster outputs; ASCII hydrographs0; raster residual<4e-7m³/s | PASS control | `hmc-dry-control.json`, GUEST/hmc-dry-control/ |
| M0-REFLEX-SERIAL | Actual step4 with prepared analytical HAND, serial branch | Four returned values assigned to three columns: ValueError | FAIL | `reflex-step4-v1.json`, GUEST/reflex-fixture/ |
| M0-REFLEX-PREPARED | Same engine, supported2process configuration, fresh fixture | Genuine step4 output;165positive cells/max0.42370656m; raster re-opened | PASS stage4 only | `reflex-step4-v2.json`, `host-raster-validation.json` |
| M0-REFLEX-SINGLE | Pipeline0–1 on one-stream DEM, thresholds100/1000 | r.stream.order rejects zero tributaries; threshold-complexity hypothesis falsified | FAIL preserved | `reflex-chain-step1.json`, `reflex-chain-v2-steps01.json`, source diagnosis |
| M0-REFLEX-MANUAL | Branched fixture step3 with inherited manual coastal flag | Requires manual_ce even with coastal disabled; original attempt fails | FAIL preserved | `reflex-chain-v3-step3.json`; explicit config retry record |
| M0-REFLEX-FULL | New preregistered branched65² DEM; real upstream0–4;3reach HAND and flood | Complete outputs;80positive cells/max0.01766856m, finite valid pixels; corrected NoData verifier | PASS synthetic standalone | `reflex-chain-v3-*`, GUEST/reflex-chain-v3/, `host-raster-validation.json` |
| M0-VERIFY-NAN | First HAND validator used inequality with NaN NoData | False invalid-pixel classification; new mask-aware check verifies3969/840/930 valid cells | FAIL original verifier; corrected PASS | GUEST/verification.json and hand-verification-v2.json, host raster checks |
| M0-HMC-DT0 | Shared65² grid with adaptive dt, source/coarse forcing trials,120s watchdog | Two exit124 timeouts; GDB SubFlow and unbuffered IntegrationStep0s | FAIL configurations / bounded timeout | `hmc-reflex-shared-grid.json`, `hmc-reflex-coarse-weather.json`, `hmc-profile-stack.json` |
| M0-HMC-DT1 | Supported static1s configuration on same derived land grid | Six complete finite/nonnegative spatial products; nonzero Q at3matched reaches | PASS configuration, no convergence claim | `static-dt-prerecord.json`, `hmc-reflex-static-step.json` |
| M0-COUPLE-IO | Actual gridded HMC Q0/peak perreach + derived tconc into upstream REFlEx | IDs2/4/6, coordinate delta0; final depth max0.03981196m,80positive cells, residuals small | PASS technical synthetic data path | `coupling-csv-build.json`, `coupling-final-validation.json`, GUEST/coupling manifest/raster |
| M0-COUPLE-PHYS | Qualify temporal volume, geodesic area, calibration, roughness and stable dt | Triangle and sampled hydrograph integrals differ; no physical/operational validation | BLOCKED | report volume table, GUEST/coupling-verification.json |
| M0-PERF-PILOT | Isolated child rusage/wall-clock for small real model runs | n=1 HMC0.1143s/20148KiB; REFlEx1.3982s/199744KiB; not aggregate VM/tree peak | PASS measurement; product budgets NOT RUN | `flood-memory-profile.json`, GUEST/*memory-probe.json |
| M0-DATA-RIGHTS | Audit official hmc-datasets/training catalog and explicit data rights | Git LFS domains found; license absent; no real payload downloaded/used | BLOCKED real-case rights | `dataset-discovery/`, report |
| M0-EVIDENCE-EXPORT | Hash archive and every exported file; read rasters on Mac; verify original sources | 501 guest files match,125 model files match; raw failures kept; humanreview pending | PASS local integrity | `final-transfer-validation.json`, `host-raster-validation.json`, final manifest |
| G-01-M0-CONT | Full boundary examples/schema/roundtrip/negative tests | Semantic inventory only; no framework contract implementation | NOT RUN | candidate ADR; no completion assertion |
| M0 gate | All gate prerequisites explicitly closed | Technical engine feasibility established; physical qualification/real-data rights/contract closure still open | BLOCKED | current report and PLAN checkpoint |

Retries changed only declared experiment inputs/configuration/environment; no CIMA source patched or substituted. UI/API/60s decision response, intervention efficacy, cross-region allocation, graceful degradation and historical skill remain NOT RUN.

## J. User viewing session — 15 October 2026
- **M0-VIEW-01 — PASS (display only):** Existing VM restarted, SSH reports Linux5.15.0-198-generic aarch64 and existing experiment directory; VM running for inspection. Existing raster preview checked visually and source hashes recorded in `reports/m0-preview/preview-provenance.json`: 80 positive cells, max0.0398119576m. No new simulation or M1; previous shutdown checks remain historical PASS. Reviewer: Codex self-check; not independent scientific validation.

## K. Real-terrain M0 increment — 15 October 2026
Run `m0-real-terrain-20261015T142405Z`; Git SHA/dirty null; source/document/data/patch hashes recorded. Reviewer Codex self-check, separate Mac/guest readers; external hydrologist pending. GUEST=`guest/m0-real-terrain-20261015T142405Z/` within run. Full report `reports/M0-real-terrain.md`.

| ID | Status | Observed evidence |
|---|---|---|
| REAL-RIGHTS | PASS | Primary DEM/Sentinel terms archived; public payloads, no credentials/cost. CIMA hydrological dataset rights remain separately BLOCKED. |
| REAL-GRID / AREA | PASS |433×325validDSM/Sentinel coverage; mean683.517m², ellipsoid andGeod comparison; geographic/UTM rasters, `terrain-verification.json`. |
| REAL-REFLEX-BASE | FAIL | Original0–4 returns0 but2/69HAND empty, optimisers nonfinite/100%residual; GUEST/real-output-validation.json. |
| REAL-HAND-DIAG | PASS | Cropped/fullgrid/pad1 probes, two1pixelstream targets retained but originalwindowHAND empty; workinghalo cures tested case; GUEST/*hand*probe.json. |
| REAL-HALO-MERGE | FAIL | Originalserialmerge halo434×327vs433×325; cropping-only434×326; rawlogs retained. |
| REAL-REFLEX-COMPAT | PASS | Explicit experimental2linecopy:69nonemptyfiniteHAND,69finiteoptimisers,433×325final; GUEST/halo-output-validation-v2.json. |
| REAL-HAND-REGRESSION | PASS | Macreader confirms0cmcommonpixeldelta,0lostvalid,7032newwithinoldextent; `host-verification.json`; not physicalvalidation. |
| REAL-MAP | PASS | Georeferenced hypotheticalmap3502positivecells/max0.7803145m; maxrelativeoptimiserresidual5.20e-7; staticpreview/sourcehashes, no dashboard. |
| HMC-DT | PASS | Threefreshsynthetic4/2/1sruns,6outputs each; L2changes.6611%/.3326%, `dt-validation.json`; no stabilitythreshold/p95claim. |
| M0-READER/HARNESS-NEGATIVES | FAIL | WrongNetCDF3reader,NaNemptypercentages,patchassert/pathchecks,missingmapreader,firstdisplayNoData check; originalrecords preserved, corrected records named separately. |
| BRIDGE-SEMANTICS | PASS | Source+primaryliterature audit; Q0bankfull/reference, triangle/transitvsintegral distinction, `interface-audit.json`; partialdraft only. |
| REAL-ARCHIVE / SOURCES | PASS |1126guesthashes,125originalsources,987parentartifacts unchanged; archive/hash/Macreader records. |
| REAL-BUDGET | PASS |1.66GiBconservative/5GiB;19GiBdisk/8GiBRAM/4CPUunchanged;VMrunning,loopbackSSH. |
| M0-COUPLE-PHYS / REAL-HYDRO-RIGHTS | BLOCKED | QualifiedQ0/completebasin/DTM/forcing/gauges/calibration/expertreview not resolved. |
| REAL-HMC / HISTORICAL-SKILL / FULL-G01 / M1–M7 | NOT RUN | No realhydrologicalforcing/modelcalibration or frameworkimplementation; M0gate remains BLOCKED. |

Standalone compatibility fix is a candidate patch with declared extra validcells, not upstream-certified behavior. The failed baseline cannot be relabeled PASS. Static satellite figure does not complete any productUI FR/QR.

## L. One Linux execution machine — 15 October 2026
Run `m0-unified-vm-20261015T150415Z`; Git SHA/dirty null, input/document/source/patch hashes explicit. Reviewer Codex self-check; external review pending. User-approved ADR-0002 governs placement; no product FR-22 completion is inferred from M0 checks.

| ID | Status | Actual evidence |
|---|---|---|
| VM-TOPOLOGY | PASS | User decision recorded in SPEC/ADR-0002; entry scripts and configs have no Mac paths or host scientific requirements. |
| VM-DATA | PASS | Guest HTTP200catalog/HTTP206prefixes match source cache; full assets reside inside VM; guest crop/area/reprojection completed; `vm-preflight.json`, `vm-source-access.json`. |
| VM-FIRE | PASS | Six fresh PROPAGATOR runs, two seeds/three repetitions, one thread; probability/fire/arrival exact by seed and equal to earlier Linux arrays; guest validator. |
| VM-HMC | PASS | New empty output/state/restart paths, six gridded65² products, finite/nonnegative m³/s and normal finish; guest validator. |
| VM-REFLEX | PASS | Actual0–4 replay in VM with declared two-line experimental copy;69nonemptyHAND/69finiteoptimisers,3502positivecells, max0.7803145m. |
| VM-RENDER | PASS | Guest Pillow9.0.1/Linux DejaVu font produces satellite PNG; no host scientific rendering. |
| VM-TRANSFER | PASS |646guestfiles checked by SHA256; three raw assets omitted only from transport duplicate, remain inside VM; original125sourcefiles unchanged. |
| VM-BUDGET | PASS |4vCPU/8GiB/19GiB unchanged, usedFS~5.64GB, conservative cumulative traffic<2GiB/5GiB; no installations or fees. |
| VM-FRAMEWORK / M1 | NOT RUN | Backend/jobs/solver/dashboard build and service required in VM, not implemented. No M1 authorization inferred. |
| M0-PHYSICS | BLOCKED | Hydrological qualification and real hydrological inputs remain unresolved. |
| FULL-CONTRACTS | NOT RUN | Complete G-01 contract freeze remains pending. |

## M. M0 contract fixture freeze — 15 October 2026
Run `m0-contracts-20261015T153248Z`, supersedes `m0-contracts-20261015T152857Z`. Git SHA/dirty null: directory is not Git. Ubuntu22.04/aarch64, Python3.10.12/jsonschema3.2.0 Draft7, existing VM4vCPU/8GiB/19GiB. Reviewer Codex self-check with separate fixture-isolation assertions and file-transfer readers; independent human review pending. Expected valid records/roundtrips accepted and invalid examples rejected with registered codes. Actual outputs under run `guest/<run_id>/`, commands/timestamps/stdout/stderr in `contract-*.json`; full report `reports/M0-contracts.md`.

| ID | Status | Observed evidence |
|---|---|---|
| CONTRACT-FIRST | FAIL | First run117PASS/2FAIL: two grid-negative fixtures mutated shared Python objects and did not contain intended mismatch; `validation-first.json`, unchanged. |
| G-01-M0-FREEZE | PASS |11schemas meta-valid,11valid canonical examples,11roundtrips,8positive bundles/variants,78negatives correctly rejected; all SPEC7.1 boundaries represented. `validation-frozen.json`:124PASS/0FAIL including JSON/exclusive-create/reference checks. |
| CONTRACT-ISOLATION | PASS | Separate assertions:78negative examples each alter only the declared record;113prerun input hashes unchanged; `fixture-isolation-audit.json`. |
| CONTRACT-OFFLINE | PASS | Replay with Python socket connections denied:124identical named outcomes/details, `validation-offline.json`; not an OS network sandbox or performance benchmark. |
| CONTRACT-IDENTITY | PASS | Actual previous guest validation artifact SHA matches predeclared reference;125original source files and672parent artifacts unchanged; guest audit and transfer verification. |
| CONTRACT-ARCHIVE | PASS |110first-run +117new-run guest file hashes checked on Mac; archive hashes in transfer-verification.json; exclusive-create negative preserves existing file. |
| CONTRACT-BUDGET | PASS | No installation/large download, cumulative conservative traffic<2GiB/5GiB; filesystem~5.64GB, configured19GiB/8GiB/4vCPU unchanged. |
| CONTRACT-PRODUCT / M1–M7 | NOT RUN | Experimental files only; real adapter conformance, safety verifier/solver/services/UI/60s and multi-region policies await their milestones. No FR/QR completion. |
| M0-HYDRO-QUALIFICATION | BLOCKED | Real forcing/discharge rights, complete basin, bankfull Q0/tconc, calibration/observational and expert review remain unresolved. |

G-01 completion denotes the finite M0 schema/example gate; it is not proof of complete application semantics or operational safety. Fields/units/CRS/time/UNKNOWN/provenance/error and version policy are specified in ADR-0003. Earlier G-01 NOT RUN rows remain historical evidence of their checkpoints.

## N. User-confirmed pre-M1 extensibility constraint — 15 October 2026
Source: user requirement, ADR-0004; document review record `reports/doc-extensibility-20261015T154021Z/`. No M1 authorization, no runtime experiment. Git SHA/dirty null (not Git); reviewer Codex self-review, independent review pending. Historical pre-M1 status: the following checks were NOT RUN; latest M1 phase results are recorded in §Q.

| ID / phase | Expected evidence and milestone | Status |
|---|---|---|
| EXT-DOC-01 | SPEC/PLAN review and alignment with all seven conceptual points, separated responsibilities, unchanged M1 sequence, safety/runtime/performance/scope guards; actual before/after files and review-result.json in document review record. Documentation check only. | PASS |
| AT-EXT-01 / core substitution | M3: execute same-hazard/product adapter replacement and show decision-core code unchanged, typed contracts, outputs and verifier outcomes. At M1 closure explicitly deferred to M3 because core absent. | NOT RUN |
| AT-EXT-02 / real adapter contracts | M1.2–M1.5: real CIMA products read via versioned contract/manifest, plus incompatible input/output rejection, without imports of engine internals in consumers. | NOT RUN |
| AT-EXT-02 / decision consumer | M3: core consumes those contracts without simulator-internal dependencies. | NOT RUN |
| AT-EXT-03 / source separation | M1.1/M1.5: change provider configuration/controlled fixture without editing simulation logic; inspect dependencies and verify normalized data/provenance. | NOT RUN |
| AT-EXT-03 / state and core | M2 temporal state/fusion; M3 source-independent decisions. Do not claim these components verified in M1. | NOT RUN |
| AT-EXT-04 / future model boundary review | M1: inspect concrete adapter contract/capabilities/provenance and extension path without rewriting CIMA engines; documentation/import review only. No new predictor required. | NOT RUN |
| AT-EXT-04 / executable model boundary | M3: controlled compatible adapter substitution and unsupported capability/UNKNOWN rejection. Real AI/Twin/agent integration outside M0–M7, requires future authorization. | NOT RUN |
| AT-EXT-05 / runtime independence | M1: actual locks/imports/process inventory plus both real integrations in existing VM without required Twin/agent runtime; recheck in later gates. | NOT RUN |

An abstract interface or architecture diagram cannot turn runtime checks PASS. All original FR/QR, M0 BLOCKED hydrological prerequisites, G-01 immutable pilot results and M1 authorization limits remain. New domains, learning, Twin and agents are not implementation deliverables. EXT-DOC-01 PASS refers solely to the recorded document review, not empirical extensibility.

### Scope clarification for §N — 15 October 2026
Confirmed focus: wildfire and flood only. The seven conceptual points are future architectural possibilities, not seven feature-completion obligations. Existing AT-EXT-01…05 verify only the original-plan component boundaries when their milestones are authorized; all executable statuses remain NOT RUN. No new functionality, runtime test or M1 authorization follows from this clarification.

## O. M0 real hydrological source and catchment audit — 15 October 2026
Run `m0-hydro-data-20261015T154619Z`; report `reports/M0-hydrological-case.md`. All acquisition/geospatial parsing/rendering in existing VM; Linux/aarch64 Python3.10.12/Fiona1.8.21/pyproj3.3.0, full environment freeze archived. Git SHA/dirty null because directory not Git. Reviewer Codex, separate published-total/copy readers; independent hydrological review pending. Logs `hydro-*.json`/`foca-*.json`, guest artifacts under `guest/<run_id>/`; commands/UTC/status detailed there. No scientific accuracy or product completion asserted.

| ID | Expected / observed evidence | Status |
|---|---|---|
| HYDRO-RIGHTS | Explicit public licenses and payload: FOCAv4CCBY4 metadata, SIRCCBYSA4 policy and actual data; preserve separate obligations and quality. | PASS |
| HYDRO-BOUNDED-ACQUISITION |11selectedZIPmembers CRC32/SHA; HTTP206exact ranges, total source payload13,104,470B vs32MiB cap. Full488MBZIP not downloaded or checksum-verified. | PASS |
| HYDRO-SOURCE-VALIDATION |18actual source/hash/count/CRS/geometry/annual-series/rain parsing checks;58prerun frozen inputs. `hydro-data-validation.json`. | PASS |
| HYDRO-AOI-D003 / D012 / D022 | Require full basin for rainfall-runoff use; observed originalAOI covers5.9288%/21.1411%/0%, `quality-and-map.json`. Does not invalidate old explicitly partial/hypothetical pilot. | FAIL |
| HYDRO-GAUGE-IDENTITY | FOCA/SIR name-matched sections offset940.45/577.88/3488.38m; D003finite annual1929–1970 vs modern15min2013onward, no temporal overlap. Do not join without section evidence. | BLOCKED |
| HYDRO-RAIN |366calendar labels,214zero days, no missing token;12totals match published, sum1922.2mm. PRE-VALIDATO/9→9 timezone anchoring retained, no hourly forcing generated. | PASS |
| HYDRO-RATING-PAYLOAD | Expected usable curve; public CSVHTTP200/931B/21metadata rows contains0numeric curve rows. `sources/sir-bagnone-rating-download`. | FAIL |
| HYDRO-SUBDAILY-ACCESS | Published15minavailability, unvalidated; actual request form needs email/CAPTCHA. No request submitted; manual export or explicit contact/request authorization needed. | BLOCKED |
| HYDRO-Q0 / TCONC / CALIBRATION | Qualified bankfull reference/method, full-basin attributes, matched observed event and expert review absent. | BLOCKED |
| HYDRO-MAP | Satellite background from prior verified cache plus real FOCA boundary and oldAOI; generated inside guest, source/hash/provenance and visual read recorded. Geographic diagnosis, not flood forecast. | PASS |
| HYDRO-INTEGRITY / BUDGET |58input hashes and125original source files unchanged;70guestfile hashes checked on copy; existing4vCPU/8GiB/19GiB, no install/fees. `integrity-and-budget.json`, transfer-verification.json. | PASS |
| HYDRO-REAL-HMC / REAL-SKILL / M1 | New qualified real-case HMC/REFlEx and historical scoring not executed; no framework code. Future protocol and unsent request are not their evidence. | NOT RUN |

Raw source/quality check aggregation20PASS/4FAIL/3BLOCKED/1NOTRUN combines differently scoped checks, not28independent scientific trials or a whole-case PASS. Existing M0 engine/contract evidence unchanged. Protocol complete as a documented next-test specification; physical execution remains NOT RUN. No external request, model substitution, resource increase or M1 authorization inferred.

## P. Confirmed Abruzzo example geography — 15 October 2026
Documentation/decision update only, no runtime experiment. Source: explicit user message; reviewer Codex; Git SHA unavailable because directory is not Git. SPEC territorial scope, PLAN and MEMORY aligned.

| ID | Expected / observed | Status |
|---|---|---|
| GEO-ABRUZZO-DECISION | Both primary real-territory fire/flood examples designated Abruzzo; configuration/portability requirements preserved; Tuscany candidate superseded without deleting evidence. | PASS (documentation) |
| GEO-ABRUZZO-SOURCES | Named AOI/basin/event, source rights/coverage/issue-valid timestamps and observations checked. None yet selected/acquired for Abruzzo. | NOT RUN |
| GEO-ABRUZZO-RUNS | Genuine Abruzzo PROPAGATOR/HMC+REFlEx runs and local accuracy/validation evidence. Existing Tuscany/synthetic outputs do not qualify. | NOT RUN |
| M0-GATE-REVIEW | Reassess original feasibility acceptance separately from later calibrated historical validation; no new full-Abruzzo-calibration prerequisite. Review not completed by this location decision. | NOT RUN |

Earlier source failures remain historical, not evidence that Abruzzo data are unavailable. No M1, new hazard, framework dependency, resource increase or external contact authorized by this geographic instruction.

## Q. M1 technical integration gate — 2026-10-15

Current authoritative result: **M1 PASS / COMPLETED**; later checkpoints above are historical. Run `m1-abruzzo-20261015T161041Z`, commands/logs `experiments/runs/<run_id>/m1-*.json`, transported artifacts `experiments/runs/<run_id>/evidence/`, report `reports/M1-integration.md`. Linux VM4vCPU/8GiB/19GiB; reviewer Codex self-check, not independent human/scientific review. Git: final fire86c96b3, flood03adad0, integration6efd8fe, rendering858a223; full SHAs/dirty/source hashes recorded. Every PASS below is technical and fixture-scoped, not a full FR/QR or operational qualification claim.

| ID | Status | Procedure and observed evidence |
|---|---|---|
| M1.1 / AT-DATA-M1 | PASS | `m1-ingest-source-v3`, `m1-prepare-abruzzo`: real public DSM/Sentinel2/ERA5, six immutable cache receipts+warm reuses, source units/coverage/time/hash checks; ingestion/preparation-result.json. Rights PDF copies and Open-Meteo primary HTML archived; ATTRIBUTION.md. |
| M1.2 / AT-SIM-FIRE-M1 | PASS | `m1-real-final-runs`: actual PROPAGATOR job7f7c35a549494a118219cd98bcf70093; two64²GeoTIFFs,4096valid probability/4burned cells; arrival compared with pinned upstream method in `m1-formal-integration`. |
| M1.3 / AT-SIM-FLOOD-M1 | PASS | `m1-shallow-flood-run`: actual HMC/REFlEx job78cd5d14b5234865b715bd8f090c0caf,6discharge grids/26reaches/HAND,145²depth1220positive cells; bridge units/times/coordinates/peak reread. Numerical residual2.12968e-6, unchanged diagnostic1%. |
| M1.4 / AT-JOB-M1 | PASS | `m1-formal-integration`, unit-final.log: FIFO/full queue/single running, queued/running cancellation, timeout kills descendant, explicit retry/recovery manifest, zeroexit without product→ERROR, log limit, frozen-input/config checks, failure leaves other queued job unaffected. CLI status/events/IDLE/recover executed in `m1-preview-cli`. No distributed queue or M6 capability manager claim. |
| M1.5 / AT-NEG-M1 | PASS |33unit tests in6.769s,6real-artifact checks; invalid version/field/units/grid/calendar/time gaps/duration/source availability/hash/path/missing/nonfinite rejected; cap before body and streaming cap/cache corruption/refresh guards verified. `integration-validation.json`6PASS/0FAIL. |
| M1-PROVENANCE / G-03-M1 | PASS | Immutable request/runtime snapshot, accepted checksum freeze, product0.2/run_manifest0.3, source/seed/env/Git/dirty/metrics/error/parent hashes; all real product manifests and listed bytes independently rechecked. Legacy M0 schema0.1 untouched; explicit migration retains unknowns and errors. Scientific evidence+transport manifest records commands and versions. Full future decision provenance NOT RUN. |
| M1-RESOURCES | PASS | `m1-rights-integrity-budget`:145pinned engine/binary/compatibility files unchanged; all runtime sameLinuxVM; conservative traffic2,434,488,075B/5GiB and disk6.20GBused at16:46:25Z. Core editable install and env freezes recorded. Mac only authoring/control/copy/display. |
| M1-PERFORMANCE | PASS (collection) | Cache cold/warm perasset, queue/execution/CPU/RSS samples/artifact size recorded separately; fire28.1862s/flood230.4269s. Resumed ingest not clean pipeline-cold; sampled RSS not exact peak. No p95/decision60s/UI performance inference. |
| AT-EXT-02-M1 | PASS | Real independently read products through strict versioned contracts; unsupported units/CRS/time/versions rejected. Downstream decision consumer NOT RUN untilM3. |
| AT-EXT-03-M1 | PASS (boundary) | Concrete public provider and controlled local normalized snapshot accepted without simulator changes; source provenance retained, AST audit8core/ingestfiles. Executable full alternate-source physical trial, fusionM2 and decision independenceM3 NOT RUN. |
| AT-EXT-04-M1 | PASS (review) | ADR-0005 and dependency review: concrete versioned input/product/engine metadata, no new AI/Twin/agent infrastructure. Alternate compatible predictor and capability/unknown-effect consumer tests NOT RUN untilM3. |
| AT-EXT-05-M1 | PASS | Actual fire/flood jobs,145file pin audit and environment freezes all in oneLinuxVM, no mandatory Twin/application-agent runtime. Repeat for later core/UI. |
| AT-EXT-01 / later M2/M3 phases | NOT RUN | Decision core and fusion not present; compatible-contract checks alone do not prove core-unchanged replacement. |
| M1-ORIGINAL-FAILURES | FAIL (preserved) | Original suite22PASS/2FAIL;4scientific job errors (axis, scratch race, float-rounding grid, optimizer residual), initial bundle/cap/pip/render errors retained with superseding fixes. `reports/M1-integration.md` failure table, immutable original logs/jobs. No failure erased by later PASS. |
| M1-PHYSICAL-QUALIFICATION | BLOCKED | PartialAOI/no complete calibrated basin, synthetic fuel/ignition/moisture/rain/Q0/soil, no matched observed validation. Not an actual observed fire/flood reconstruction. Source availability first-seen2026 prevents retrospective forecast claim. |
| M2–M7 / full FR-QR / H1–H3 | NOT RUN | No shared event/consequence/decision/UI/rolling horizon/predictive-alert/capability-retention implementation. No M2 authorization. Next M2.1–M2.6; dashboardM3. |

The original 60s decision target and all release gates remain unchanged. M1 simulation timeout is180sfire/600sflood and is not the decision deadline. Human approval remains mandatory for any real action. Full FR/QR rows stay NOT RUN where their broader behavior is not yet exercised; §Q records the actual partial requirement coverage without checking off future functionality.

- **M1-ARCHIVE — PASS:**1.163file inventariati guest,1.160trasportati+SHA verificati,3originali grandi conservati nella VM con hash/URL. Archivio16.198.427B, manifest SHA05ad03f4ee45460987cc2cf1a0a45604623eee9ce9c0e1c7f50d5796fd440ae8;23record comando/controllo congelati nel manifest host. `reports/m1-abruzzo/transfer-verification.json`; seed1730M1 NOT RUN. Budget finale2.435.051.901B/5GiB alle16:53:12Z. Nessun simulatore attivo, VM lasciata disponibile.


## R. M2 shared domain gate — 2026-10-15
Run `m2-domain-20261015T190836Z`; report `reports/M2-domain.md`, ADR-0006, commands m2-*.json / logs / immutable manifest in experiments/runs/<run_id>. Reviewer Codex self-check; no external physical reviewer. Existing LinuxVM4vCPU/8GiB/19GiB. Integration commitf165d7e; final guard/test commitdfe1b20; M1 regression9a4bef0 with unchanged M1code. Broad FR/QR rows are not bulk-completed by these fixture-scoped checks.

| ID | Status | Procedure / observed |
|---|---|---|
| M2.1 / AT-GEO-M2 | PASS | Same snapshot/event workflow for Abruzzo and syntheticSenegal, realPROJ verifies32633/32628metreCRS, Europe/Rome vsAfrica/Dakar. Invalid bbox/timezone/unsupported metricCRS/calibration assertions rejected. |
| M2.2 / AT-FUSE-M2 | PASS | Duplicate same-ID bytes collapse, changed-ID content conflict rejected, correlated duplicates no score inflation, disagreement retained, ambiguous bridge not transitive merged; future/stale/partial excluded. Deterministic reorder replay. |
| M2.3 / AT-WX-M2 | PASS (contract) | Nonemptyunique aligned hourlymembers, issue/availability/units/weights/coverage enforced; actualERA5M1 normalized asREANALYSIS; controlledforecast separately validates. Liveforecast acquisition NOT RUN. |
| M2.4 / AT-IMPACT-M2 | PASS (semantics) | ActualM1fire/flood depth/probability reread;3synthetic exposurepoints×10people→30;5synthetic evacuees→25, physicalrasterSHAidentical. Unknown/physicalunsupported effects rejected. No empirical efficacy inferred. |
| M2.5 / AT-ACCESS-M2 | PASS (inputs) | Unknowncriticalresource fields, closed/unknown roads, weightlimit, temporalexpiry, autonomy/shift, disconnected route reject; outside/NoData/unknownpopulation not safezero. No complete deployment verifier or authorization claim. |
| M2.6 / AT-REPLAY-M2 | PASS |19M2tests final,33M1regressions,5integration checks; CLIvalidate/events/window. Exclusive snapshots, cutoff/provenance/replay; M1run/job bytes and145enginefiles unchanged. |
| M2-PERF | PASS (measurement) |10000syntheticpoints, indexbuild24.7154s,100recordquery6.492ms/serialization1.798ms/payload51796B/index7090176B/processRSS103923712B. Fullscanresults equal; limit1..1000. Single sample; no p95/UI/60s claim. |
| AT-EXT-03-M2 | PASS (scoped) | Source-neutral snapshots/event state and normalized meteo; M1adapter/core code unchanged. AT-EXT-01/M3predictor replacement and decision consumers NOT RUN. |
| M2-NEGATIVE-ORIGINALS | FAIL (preserved) | First15PASS/1FAIL exactfloat oracle; firstintegration4PASS/1FAIL measurement-helper module collision. Later superseding records PASS, originalfiles unchanged. |
| M2-QUALIFICATION | BLOCKED | Missing actuallocal population/resourceinventory/validatedeffect/calibratedphysics/historicalobservations; controlledsynthetic fixtures not operational inventory. |
| M3–M7 / H1–H3 / G04–07 | NOT RUN | No solver/proposalverifier/dashboard/rolling horizon/alerts/servicecapability evaluation; nextM3 requires authorization. |


M2-ARCHIVE — PASS:122artefatti SHA verificati;8record comando/controllo congelati, manifest5f619a68ffdbba6efaf6933b91a340c4e47e7b54bad879cb8cbd82c504c16398; reports/m2-domain/transfer-verification.json. Budget2.438.028.097B/5GiB alle19:18:26Z, no nuovi download/installazioni. M3 NOT RUN.


## M3 checkpoint — 2026-10-15
Technical M3 PASS, reports/M3-dashboard.md / ADR-0007 / run m3-dashboard-20261015T192310Z.61unit tests,4integration groups,14browser checks, real long-model cancel/retry,0axe violations after fix; incompletes/negative harness/marker cases retained. Both new matched genuine CIMA products and actual Sentinel maps served in the oneVM. No physical/operational/WCAG certification or H1–H3 claim. User-authorized continuation now M4, no further routine approval.


## M4 checkpoint — 2026-10-15
M4technicalPASS controlledfixture, runm4-joint-20261015T194711Z, source dd501ce, reports/M4-joint.md. Genuine matchedAbruzzoCIMAcontexts +2syntheticregions/4sharedqualifiedevacuationunits, reserve/transfer/overbooking checks, jointreferenceobjective51.346 vscheckedhome-only66.546; browsernominal60→17joint /35local. Toycoefficients notempirical efficacy orH2proof. User-authorized continuation M5, no routine permission needed.


## M5 measurement checkpoint — 2026-10-15
Run m5-adaptive-20261015T195150Z, source8d8081a: PASS controlled rolling continuity, forecast advisory lifecycle and native bounded decision benchmark30/30 useful verified outcomes, p50 .738789s /p95 .870891s /worst .902334s. Independent verifier and outer timeout process-group tests executed. First verifier launch FAIL import-path only, preserved; corrected standalone harness. Expected-vs-worst endpoint choices coincide on this fixture: no observed robustness advantage. Live/attributable historical forecast skill BLOCKED; current implementation uses authored synthetic replay, not ERA5 as a forecast. CPU/RAM performance supplementation and UI alert evidence pending. Continue scoped M6 implementation/verification under broad user authorization; physical qualification unchanged.

## S. M3/M4 executed decision and dashboard scope

M3/M4 technical PASS within reports/M3-dashboard.md and reports/M4-joint.md; runs m3-dashboard-20261015T192310Z / m4-joint-20261015T194711Z. Actual CIMA products, genuine satellite pixels, independent verifier, small reference solver equality, joint reserve/authority/overbook checks, browser workload and accessibility corrections executed. AT-EXT-01/02/04 M3 PASS only for the exercised compatible controlled boundary with unchanged core hashes, not alternate-model accuracy. Same-author reviewer Codex; no external scientific review.

## T. M5 executed activity outcomes

| Activity | Outcome | Evidence / scope |
|---|---|---|
| M5.1 scenario objective and expected/worst endpoints | PASS | M5 results.json; both endpoints choose same plan on this fixture, no benefit claim |
| M5.2 rolling continuity | PASS | rolling-progress.json two-slot commitments/progress/consumables; M6 HTTP/browser |
| M5.3 bounded decision vs slower model | PASS | Outer process-group watchdog, native solver, queue separated; existing genuine models |
| M5.4 synthetic forecast advisory lifecycle | PASS | alert-replay.json; UI lifecycle M6 browser-third, immutable revisions/CAS |
| M5.4 matched real forecast/physical impact watcher | BLOCKED | M7 real MET source acquired, incomplete variables/time-mismatched; current UI synthetic only |
| M5.5 fixed benchmark | PASS | source8d8081a and e5ec104,30requests each; latest p50 .714691s/p95 .820538s/max .828716s,30/30 useful/terminal |
| M5.5 short-watchdog original | FAIL | .800246s on .8s test, decision-second.log; retained, corrected margin and10later trials PASS |
| M5.5 false-alarm observed field skill / full sensitivity/baselines | BLOCKED | Two authored truth cases not independent observed performance; no full main study |
| M5.6 full research gate | BLOCKED | Forecast/effect qualification and principal experiments incomplete, report M5 |

## U. M6 executed activity outcomes

| Activity | Outcome | Evidence / scope |
|---|---|---|
| M6.1 controlled faults and actual crash | PASS | integration-third/results.json12groups; owned job5ed4fe3ee3744ff689105e7c9cf0dc9b |
| M6.2 vector, rules and diagnostic retention | PASS | Six explicit states/causes/time/confidence,7injections; baseline .85 already degraded |
| M6.3 abstention/recovery/CAS/stale proposals | PASS | Critical UNKNOWN no proposal, old revision rejected, new authored positive evidence and audit |
| M6.4 FIRE under FLOOD outage, cached historical map | PASS | Actual worker ERROR/unusable and independently verified FIRE; controlledsource/solver cases |
| M6.5 preparedness and continuity software | PASS | Same admissibility checks, declared2/8min linear synthetic effects; HTTP/UI |
| M6.6 diagnostic loss comparison | PASS | Raw vectors, researchweights, per-scenario loss; fail-stop zero is analytic reference |
| M6.6 general optimized capability objective / actual external recovery / physical efficacy | BLOCKED | Rule-based current mechanism, no optimality or operational repair/efficacy claim |
| M6 full gate | BLOCKED | Technical slice tested, full normative deliverables not all satisfied |

## V. M7 verification outcomes (current)

| Activity | Outcome | Evidence / scope |
|---|---|---|
| M7.1 fire observation acquisition/read | PASS | EMSR4492020 vector619620B, source/CRS/schema read, historical-metadata/vectors |
| M7.1 matched historical fire hindcast/skill | BLOCKED | Current2024conditional products not2020hindcast; fuel/ignition/qualification incomplete |
| M7.2 flood observation acquisition/read | PASS | EMSR062Teramo2013 vector1016121B; no otherAOI counted asAbruzzo |
| M7.2 matched complete-basin flood hindcast/skill | BLOCKED | Forcing/boundary/Q0/tconc/calibration/cutoff unresolved; smallL'Aquila case different |
| M7 real current weather-source audit | PASS | MET Norway HTTP200/91times/40532B, issued-update semantics and license recorded |
| M7.3 two-profile contract portability | PASS | M2 tests and profiles; full native/decision geographic workflow beyondAbruzzo NOT RUN |
| M7.3 independent fresh-machine install/physics portability | NOT RUN | Existing singleVM and historicalM0portability do not count as final independent install |
| M7.4 final regressions | PASS |66tests +10forced-watchdog executions,145runtimeenginehashes unchanged |
| M7.4 scaling measurements | PASS | Geo100–100k,30queries/size; solver4/20/100resources at12slots,n1/size, all verified |
| M7.4 large UI100k budget | FAIL | No valid mapFPS samples;heap1.316GB.1k/10k PASS; limits explicit, no target relaxation |
| M7.4 original full physical M/L fixtures / principal ablations | NOT RUN |24/48slotdimensions unsupported; controlled alternatives not main-study evaluation |
| M7.5 responsive/performance/axe | PASS | Finalbrowser14checks, M6adaptationbrowser, axe0violations3widths, contrast incompletes unqualified |
| M7.5 30-minute stability | PASS |1800.030s/120samples; p95feedback17.1ms/p05map60FPS, peakheap5.16MB/GCgrowth.461MB; final checkpoint below |
| M7.4 local supplement integrity and isolated-checkout replay | PASS |3275files verified, archiveff69a31d..., packagedsource998b934replayed; fullinstall/nativequalification NOT RUN |
| M7.6 release integrity/H1–H3 | BLOCKED | Reports retain failures/qualification limits; no full research or operational release claim |

All outcomes above:2026-10-15, same4vCPU/8GiB/19GiBVM, Chrome155onMac display client, reviewer Codex self-check. Final paths/source IDs and hashes in reports/M5-adaptive.md, M6-degradation.md, M7-validation.md and their immutable run directories. No external review implied.


## Final30-minute stability checkpoint —2026-10-15
PASS runm7-verification-20261015T200759Z/stability/results.json: measured1800.030s after60sseparatewarmup,120samples,156feedbackpoints p9517.100ms,123map samples p0560FPS, peakclientheap5161124B, GC-normalizedgrowth461064B, DOMgrowth8nodes. NoJavaScript/UIerrors or simulator submissions fromnavigation. Chrome155/MacM4Proclient; allbackend/science staysVM. ExplicitGC only atbaseline/end; rawtrend retained; concurrentQAstress disclosed.44production-sourcefiles/145enginehashesunchanged atcheckpoint. This is bounded smallfixture evidence, not proof of allfutureloads;100kstressFAIL and fullresearchgates remainBLOCKED. Archive/transport classified separately afterexecution.


## Final supplement/health checkpoint —2026-10-15T20:41UTC
PASS local integrity and transport:3275files, expanded213996457B, archive68478162B; manifestSHA965e16421c2f2b099e0d310ccc28b2db160dd6dbd74871c2472a6c48c426e10a, archiveSHAff69a31d9bcdd9631ce35bfa7c3dea9d0746b101f1b8afcd01cc2f0d3a125a02. Frozen source998b934faf8b7519eb567ed6384cd591eac976f6; final documentation commits only append this subsequent verification. VM export/home/hazardia/hazardia-runtime/exports/research-supplement-20261015T203922Z.tar.gz; host experiments/runs/m7-verification-20261015T200759Z/exports/research-supplement-20261015T203922Z.tar.gz. Independently host-copied file sizes/hashes all match. Packagedsourcebundle defaultHEAD clone/replayPASS, same selected IDs/objective51.346, using existing guest environments; not a freshmachine/native-physics reproduction. Earlier main-onlybundle HEADfailure retained and corrected.
FinalhealthPASS: VMserviceRUNNING/loopback,44productionfiles+145enginefiles unchanged,4vCPU/8GiB/19GiB unchanged, conservative cumulative downloadbound2614785687B/5368709120B, freeguestdisk12712792064B. No paid/public/push/real action. Dashboard left available for user http://127.0.0.1:8080/; guide reports/DASHBOARD-GUIDA.md, plainstatus reports/STATO-IN-PAROLE-SEMPLICI.md. Scientificfullgates M5/M6/M7 remainBLOCKED; incomplete software/main-study items remain explicitly listed.


## Geographic-detail verification — FR-MAP-01 / FR-24/26/27/28 — 2026-10-15
Run `map-detail-20261015T204352Z`, source `a7d3eb6`, reviewer Codex self-check. Details/commands: reports/MAPPE-DETTAGLIO.md. No independent external review.

| Check | Outcome | Evidence |
|---|---|---|
| Official detailed imagery consultation / offline fallback | PASS | providers-probe, imagery-context-probe; actual JPEG / declared20cm WMS, dated2018–2019; browser-final checks |
| Geographic snapshot, search, coordinate/point/quarter/road/POI inspector, scale/labels | PASS | deploy-context-v2, service-data-proof; combinedSHA afcd5c7927eb65d04f47a72148d6ce48eb2d52ae8527bd44132e1038b0379e4e; 3834elements, source links/coverage |
| Bounded tile route/cache/budget and network failures | PASS | 5tests/unit/test_maps.py; fixedprovider/bbox/LRU/persistentbudget/errorrelease; browser-final injected503/offlinerecovery |
| Regressions and physical sources unchanged | PASS | regression-and-integrity.json;71tests,145enginehashes; no new model runs from map |
| Responsive/interaction/frame checks | PASS | browser-final/results.json:19checks,375/768/1440;30label p9516.2ms,31base p9514.2ms;30offlinepan p05≈59.99FPS |
| Automatedaccessibility | PASS | accessibility-final/axe-results.json:0violations3widths; contrast/link incompletes remain unresolved/manualreview, no fullWCAGclaim |
| Overpass extraction attempts | FAIL | imagery-context-probe, osm-retry/get-small/diagnose:HTTP500/502/406/timeouts; recovered by limited officialOSMAPIread |
| OSM API initial AOI too large | FAIL | osm-map-extract/osm-map-bounded:400limit50000nodes; reducedAOI successful osm-small-final |
| Initial static JSON delivery | FAIL | service-data-proof initialdiagnosis in worklog; fixed bytes serialization, finalHTTP200/SHAverified; old clientcache versioned |
| Official admin boundaries / cadastre / elevation / complete regional roads | NOT RUN | Not present or inferred; limited streets bbox visible in metadata |
| New30minsoak / online streaminglatency qualification | NOT RUN | Oldsoak not attributed to newcode; online highdetail functionallyverified only |
| Complete scientific qualification / 100kdisplayrelease | BLOCKED | PriorM5/M6/M7 blockers and100kFAIL retained |

Additional screenshot readiness check PASS: `browser-capture-verified/results.json`, all19checks repeated; screenshot waits for all visible256px tiles at full opacity after map expansion. p95label15.8ms/base15.6ms on this repeat; previous browser-final metrics above remain unchanged. Test-script revision archived with final Git commit. Actual screenshot: reports/dashboard-evidence/map-detail/orthophoto-detail.png.

Final context refinement `c190503`/`14457b5`: retain Chieti/Pescara/Teramo capitals at regional zoom, immutable content-addressed snapshot. Final context SHA afcd5c7927eb65d04f47a72148d6ce48eb2d52ae8527bd44132e1038b0379e4e (1,025,160B); earlier c24d snapshot remains in frozen first archive, not retroactively changed. Full cumulative download accounting carries historical upper bound: PASS2,691,375,540B/5,368,709,120B at final-resource-budget checkpoint (raw image+currentRX alone is incomplete); free disk12,676,374,528B. First archive transport PASS17files, SHA bd541f6b108f981b9b7b56d68566feeb32a0cc8eed40da7806a0dd2ee51558a5. Final release UI/transport outcomes below are separate subsequent checks.

Final UI verification PASS on source `c190503`: `browser-release/results.json` all19checks; labels30feedback p9515.6ms, base31feedback p9515.1ms, offline30pans p05≈60FPS. `accessibility-release/axe-results.json`:0violations375/768/1440, raw contrast/link incompletes retained. `final-release-proof.json` verifies final contextSHA and145unchangedenginefiles; current service/data operated solely in VM. Client display test-script hash and screenshot hashes: client-release-manifest.json. Prior measurements/snapshots stay historical; full scientific-release and100kload blockers unchanged.

Final local evidence transport PASS:21files rehashed on Mac (copy inspection only), archiveSHA90d58689998edb38e2667fb4d3c9c9664607f23e79ca992c04755a88e5f5d294; `final-transport-verification.json`. Final runtime budget proof2,708,877,321B/5,368,709,120B, free disk12,670,672,896B; resources unchanged. Native raster byte integrity and Sentinel background independently rehashed against catalog/product manifests: PASS7native rasters, `native-product-byte-integrity.json`; no physical-resolution upgrade claimed.


## Abruzzo two-example handoff — 2026-10-16 (Europe/Berlin)
Run `abruzzo-showcase-20261015T234538Z`, source `d88c78f`, reviewer Codex self-check. PASS: two browser views centered on native FIRE29cell/60min and FLOOD1220cell/maxdepth0.1786167m products over detailed ortho; existing raw raster hashes independently match manifests,145enginefiles unchanged. PASS: two genuine dashboard solver/verifier responses with2units, nominal30→17syntheticpeople and2assignments each, IDsdecision-488a8a1aae234c23bda016e4188ba693(FIRE)/decision-257f1670f32a4df4bfbba9861947c918(FLOOD). PASS manualtimeline0→60min forfire and explicitly disabled max-event timeline forflood. Evidence: experiments/runs/abruzzo-showcase-20261015T234538Z/showcase-proof.json; reports/dashboard-evidence/abruzzo-examples-20261016/ui-state.json + screenshots/manifest; instructions reports/DASHBOARD-GUIDA.md.
NOT RUN: newphysics simulations, newbroad regression/performance study (productioncode unchanged), suppression/barrier intervention physics. BLOCKED: prior scientific qualification/full-release gates unchanged. This is an interactive conditional demonstration, not historical/operational validation; evacuation changes synthetic exposure, not native hazard raster. Two tabs left open for user trials; page reload resets UI controls. No paid/public/push/dispatch/resource increase.


## Physical intervention / multi-day checkpoint — 2026-10-16
User requires distinct physical hazard maps under intervention and simulation horizons of days. Run `physical-days-20261016T040414Z`; report reports/INTERVENTI-FISICI-E-GIORNI.md, ADR-0009. PASS: native unmodified PROPAGATOR uses scheduled vegetation_changes; separate local `/physical-fire.html` displays matched control/trial hourly rasters over1/2/3days,72h actually completed in both,1024²×30m,2realizations,seed1729,1thread, ERA5hourly13–16July2024,syntheticuniformfuel/moisture. Published144native-derivedRGBAframes; matched no-op900s control used asA; no arbitrary raster shrinking. Main evacuation/solver/jobcontracts remain unchanged and do not claim generalized physical-action/duration support.
FAIL retained: first64²baseline exitsdomainafter5h, initial expanded-preparation missingPYTHONPATH (repaired); native no-op vs absentevent not bitwiseinvariant (114172probabilitycells differ), requiring matchedschedulerbaseline and limiting validity. No claim that this sensitivity is a universalbug or that idealizedring effectiveness generalizes. Old100kGeoJSONFAIL/M5–M7scientific blockers unchanged.
PASS finalbrowser-v2:18checks,24/48/72h controls,play/pause, identicalBcontrol,30nativeframeswitches p95fullautomation+delivery100.281ms,30keyboardpans RAFcadence60.002FPS,2imageDOMbound,responsive375/768/1440,axe0violations withrawcontrastincompletes,noJSerrors/noPOSTnativejobs. New30minsoak,validatedfuel/interventionlogistics,largeensemble and operationalqualification NOT RUN. Newfloodphysicaleffect/multi-dayhydraulicintegration NOT RUN: user asked to choose initialretentionbasin(HMCnativeaffordances) versuslocallevee/pumping(dedicatedhydraulicassessment). NativeHMCreservoircode exists but has not been tested here; additionalengine adoption not authorized/inferred. No costs,largeacquisition,privilegedinstall,public/push/operations; sameVMlimits.

Final integrity PASS:145enginehashes,144nativeframes and144PNG individually rehashed; manifestSHA69ddda1244015b7470ca6ed823ccf1aa7011157733c3a4e202bff0600b6fb684; final-integrity-budget.json. Conservative cumulative traffic3,087,176,564B/5,368,709,120B; freeguestdisk12,627,730,432B;4CPU/8GiB/19GiB unchanged. Evidence archive transport PASS257files, SHA524451d63e000953c69779040454b62ff7979d325a48f93d08df5b705a34f708, transport-verification.json. Mac only copy/hash inspection and browser display. New native experiments do not establish H1–H3 or physical field accuracy.


## UI reference / control-room verification — 2026-10-16
Run `ui-controlroom-20261016`; reviewer Codex self-check. Main source `7002398`, physical page `0edcd0a`; production backend notebook `c58a83f`. Report reports/UI-CONTROL-ROOM.md. This table supplements historical gates without overwriting them.

| Verification | Outcome | Evidence / limitation |
|---|---|---|
| Reference inspection and explicit feature gap matrix | PASS | Official Technosylva page + observed Geospace simulator DOM/screenshot; operational-map route errored, authenticated commercial parity not verified |
| Map-first sections, plain Italian/help, single/paired view and layers | PASS | browser-handoff/results.json; actual IAB screenshot in reports/dashboard-evidence/ui-controlroom-20261016 |
| Persistent cases and views; invalid/stale writes; bounded archive | PASS |6guest tests, browser reload/CAS/restore checks;20cases/20views/50annotations/200vertices/60kB/500snapshots; joint-case save explicitly unsupported |
| Distance, approximate area, notes, keyboard coordinates, GeoJSON export | PASS | Browser known111m line/0.91ha rectangle, self-cross rejection and lon/lat export; authored annotations, no physical intervention or census claims |
| Guest application regressions | PASS |77tests:6web+38unit+19domain+14decision; deploy-test.json/regression-integrity.json and guest logs |
| FIRE/FLOOD decision and native physical72h regressions | PASS |54main+18physical checks, genuine solver/verifier API responses and previous native frame manifest; no new scientific trials |
|375/768/1440layout + keyboard + automated access scan | PASS |12main+3physical axe scans0violations; raw incompletes retained; compact sidebar opens/closes at375/768 |
|>=30input feedback/action, offlinepan cadence,3coldloads,30APIreads | PASS | browser-handoff/results.json; metrics in PLAN/MEMORY/EVIDENCE; original <=200ms/30FPS/3s/500ms targets unchanged |
| Engine source / published physical manifest integrity | PASS |145files unchanged; regression-integrity.json; prior144framebyte proof remains historical |
| Initial QA execution | FAIL |browser-first/harness-failure.txt;browser-second.log/browser-third.log: test setup/oracle/selectors repaired; no scientific interpretation |
| Initial physical-page contrast | FAIL |physical-regression/results.json; dark text/dark buttons repaired, physical-final all18checksPASS |
| New30minsoak,100kloadqualification,externalusabilitystudy | NOT RUN | Older soak not transferred; historical100kFAIL remains unresolved |
| Full functional parity, livefeeds,censusedimpact,GPS/collaboration,PDFmapexport | NOT RUN | See gap matrix; no fake operational controls |
| Alluvial physical retention/lamination+levees+pumping+days | NOT RUN | User requests all; prior preference question resolved; verify existing HMC module and assess hydraulic requirements before substantial adoption |
| Original M5/M6/M7 scientific/release gates | BLOCKED | Qualification/effect/capability optimization/historicalvalidation and100kdisplay evidence unchanged |

Final evidence transport PASS: 241regularfiles in VM archive, SHA256`ec8c37cd00f5184754771e40c502785dda962dc3df8ebced05a7edc058841fec`; transport-verification.json. Runtime checkpoint2026-10-16T04:47:17.831825+00:00: cumulative conservative download3,301,968,232B/5,368,709,120B; freeguestdisk12,569,681,920B;4vCPU/8GiB/19GiB unchanged. Notebook cleanup guard independently checked against immutable VM snapshots: original content preserved, revision25→29→30. GUI evidence reports/dashboard-evidence/ui-controlroom-20261016/anteprima.png.


## GitHub / full reconstruction — 2026-10-16
Run `github-repro-20261016`; reviewer Codex self-check; FR-REPRO-GH-01. See reports/PUBBLICAZIONE-GITHUB.md for commands/source IDs/raw-evidence locations and limitations.

| Check | Outcome | Evidence / scope |
|---|---|---|
| UTM image checksum, SSH-key-only seed ISO + cloud-init schema | PASS | reports/reproducibility/utm-assets.json; cloud-init-schema.json, no new VM boot |
| Complete setup/source path, private GRASS prefix, new envs/HMC | PASS | installation-verification.json;260filehashes, paths independent of m0 |
| Genuine regenerated FIRE/FLOOD/72h and144frames | PASS | installation-verification.json; new job IDs/report; old145enginefiles untouched |
| Software regressions and publication protections | PASS |85tests:38unit+19domain+14decision+14web; backend-tests.json |
| Reconstructed dashboard/client | PASS |54main+18physicalchecks,15axe scans0violations375/768/1440; ui-checks.json/physical-ui-checks.json, raw incompletes retained |
| Exact FIRE arrays /72h NPZ+PNG replay | PASS | numerical-replay-audit.json;0changedFIREcells,144+144identicalhashes |
| Strict bitwise FLOOD replay | FAIL |197cells differ max1.4901161193847656e-08m; mask/positivecount/globalmax unchanged; valid-run PASS reported separately |
| First safe extraction / FIRE import / verifier attempts | FAIL | Original logs preserved; repaired and verified, no threshold/input tuning to hide failure |
| Public source export/secret-pattern scan/excluded-media policy | PASS | prepare_publication.py,5publicationtests,PUBLICATION.json; private history preserved |
| GitHub HTTPS authentication | BLOCKED | No configured HTTPS username/token; existing SSH auth dry-run PASS resolves delivery path |
| Actual public push + remote byte/tree verification | PASS | SSH push039df1c68cceb1b36c4fb58e1729b3faed7f194f; independent GitHub clone;191file hashes/lengths and exact tracked tree match, private history absent |
| New VM boot, privileged OS installation, complete fresh network acquisition | NOT RUN | ExistingVM OS and hash-verified archive/raster reuse; source-only install docs cover missing phases |
| Full scientific/operational qualification | BLOCKED | Existing M5/M6/M7 constraints not closed by installation/replay |

## Complete plan audit — plan-audit-20261016T054141Z

Reviewer Codex self-check; source d0f9f34. All28FR,14QR,9SC,8milestones, AR-EXT and6additional requirements mapped in reports/plan-audit/coverage.json and reports/VERIFICA-PIANO.md. No requirements removed or thresholds relaxed. FR-03/18/26 full acceptance BLOCKED; prior narrow PASS kept in executed records. QR-10 controlled software PASS does not establish real forecast skill. Full M5/M6/M7/G-07 remain BLOCKED.

| Check | Outcome | Evidence |
|---|---|---|
| Runtime/read-only original8080 inspection | PASS | runtime-inspection.json:7catalog scenarios,0active jobs, live589cb5f and reconstructed6c44c4b in sameVM |
| Current regression in reconstructed prefix | PASS | guest-regressions.json:38unit+19domain+14decision+14web=85, all exit0 |
| Live/source identity | PASS | Live differs only in jobs.py optional privateGRASSprefix support; reconstructed src matches audit checkout; no deployment inferred from push |
| New physics/browser/stress/soak/fault campaign during audit | NOT RUN | Audit only, existing user state untouched; old UI tests not recast as fresh runs |
| All requested flood physical interventions and days | NOT RUN | All3requested, not pending a single-choice answer |
| Complete current-user requirement acceptance | BLOCKED | Physical flood/day/editor/forecast/strategy/qualification gaps detailed in audit |

| Additional requirement | Outcome | Evidence / scope |
|---|---|---|
| AR-EXT-01 | PASS | Sette possibilità conservate nei confini/versioni; AT-EXT M1/M2/M3 controllati, non prova di sostituibilità fisica universale. |
| FR-MAP-01 | PASS | Ortofoto Abruzzo20cm nominali e Sentinel10m, coordinate/ricerca/scala; strade/POI locali, confini/quartieri ufficiali/catasto non coperti integralmente. |
| FR-MAP-02 | BLOCKED | Coppia nativa incendio con fascia ideale PASS; confronto fisico alluvione e azioni generali integrati nel decision engine NOT RUN. |
| FR-HORIZON-01 | BLOCKED | Laboratorio incendio72h reale PASS; jobUI10/30/60min, solver1–12slot e alluvione massima6h: durata generale di giorni NOT RUN. |
| FR-UI-REF-01 | BLOCKED | Restyling/strumenti cartografici salvati PASS; parità funzionale Tactical Analyst/Geospace NOT RUN, editor fisico libero e feeds mancanti. |
| FR-FLOOD-ACTIONS-01 | NOT RUN | Laminazione/invasi, argini e pompaggio richiesti tutti; nessuna delle tre integrazioni fisiche verificata. |
| FR-REPRO-GH-01 | PASS | Sorgenti/script/guide pubblicati, clone191hash PASS; nuovo prefisso nella stessa VM PASS, bootOS nuovo NOT RUN. |


## Monitoring-first UI — 1b7ccf9 / monitor-first-20261016T054705Z
User requests monitoring as main activity, large central map with FIRE/FLOOD/both filters, separate decisions/comparison. FR-MONITOR-01 added to SPEC. Implemented read-only monitoring map, per-hazard product selectors/dates/legends, context search/coordinates, online ortho and offline Sentinel, independent selection/opacity; dedicated decision section preserves existing proposal across navigation. No change to physical models, intervention semantics or source qualification.
PASS85guest regressions and44browser checks incl2real solver/verifier calls,12axe scans0violations (raw incompletes retained),3viewports375/768/1440,keyboard,35filter samples p95=17ms. No physicsPOST from map tools. SameVM runtime deployed1b7ccf9; existing persisted JSON files byte-preserved on guarded idle restart. Original8080 available. reports/MONITORAGGIO.md and reports/monitoring/verification.json; raw experiments/runs/monitor-first-20261016T054705Z. Current source85backend/44browser tests are engineering evidence only. New30minsoak,100kstress,live monitoring and expanded reference parity NOT RUN; prior scientific/release BLOCKED unchanged.

| Requirement/check | Outcome | Scope |
|---|---|---|
| FR-MONITOR-01 | PASS | Default central map, independent/both filters, distinct decision section, dates/legends, proposal preserved, no unwanted jobs;44browser checks |
| Responsive375/768/1440 + keyboard +12axe scans | PASS | Raw incompletes retained, no WCAG certification |
| Current guest regression | PASS |85tests in reconstructed-prefix runtime, deployed same source |
| New monitor30min/100k/historical/live feeds | NOT RUN | Existing QR-14FAIL and FR-05/06/17/M5–M7BLOCKED remain |


## Prerequisites / native HMC storage pilot — missing-prerequisites-20261016T055356Z
User asks to install missing requirements. Actual inventory PASS: 32Ubuntu packages,25pinned Python versions,4env imports,10commands,4GRASSaddons,145enginehashes. No declared runtime prerequisite missing; new package installation NOT RUN (unnecessary), no sudo/upgrade/new engine. Optional rg absent, Python fallback used. Functional/data/scientific gaps remain open, not solved by package installation.
E-HMC-STORAGE-001 PASS: unmodified pinned HMC spill/lake routines linked to synthetic native driver;7cases/21assertions and documented runner replay PASS, source/engine integrity PASS. Units verified: spill mm/step, lake mm/h; volume conversion explicit. Initial diagnostic substring counter22included final marker; corrected assertion count21, raw log retained. No full reservoir catchment/REFlEx mitigation/days/levees/pumping/historical accuracy result. FR-FLOOD-ACTIONS-01 remains NOT RUN for integrated actions; scientific gates remain BLOCKED. Report reports/PREREQUISITI-E-INVASI.md, reports/prerequisites/verification.json; source driver SHA and raw commands/logs under experiments/runs/missing-prerequisites-20261016T055356Z; sameVM, GNUFortran11.4.0, reviewer Codex self-check, no H1–H3 claim. Next executable work remains full matched HMC reservoir fixture/bridge and hydraulic assessment, not another dependency reinstall.

| Check | Outcome | Scope |
|---|---|---|
| Declared system/Python/native prerequisites | PASS | All present, actual versions/imports/file integrity audited |
| Additional dependency installation | NOT RUN | No declared prerequisite missing |
| Native HMC spill/tank component calls | PASS |7synthetic cases/21assertions, no upstream edits; documented replay PASS |
| Full reservoir mitigation HMC→REFlEx/UI | NOT RUN | Component checks do not imply integrated feature |
| All flood actions/day/historical/scientific release | BLOCKED | Prior unmet dependencies unchanged |


## Open-Meteo real map/native forecast increment — openmeteo-20261016T060251Z
User explicitly authorizes free-tier Open-Meteo on map and new native simulations, allsameVM. FR-WX-REAL-01/ADR-0010: fixed L’Aquila point,7variables4days,DWDICON-EU, shared30mincache/max48attemptsUTCday/256KiB/16MiB, no key/paid endpoint; unknown model issue stays null, first availability observed06:07:25Z, preceding-hour precip/radiation shifted explicitly. New research-forecast0.3 contracts preserve legacy0.2 retrospectivity.
PASS97guesttests,70browserchecks (26weather+44monitor,18axe0violations with rawincompletes),29independent native assertions. Actual8080 UI requests FIRE job-0ccb4d49371045b1af281486b40fa49e (31positivecells60min), FLOOD job-a91721608c7d49d6889190ec94ee4c77 (6h,HMC+REFlEx0–4,native21025validzero cells,0eligible runoff aboveunchanged1m3cutoff) bothSUCCEEDED. No added rainfall, fake water or real-safety claim. First flood FAIL job-cff1de0ab68e4a59bd14779579bccf60 retained: empty native optimizer case was wrongly rejected; pressure hPa→nativekPa mapping also corrected post-failure, actualnewforcing checked. Year-specific harnessFAIL and catalogsource-label defect retained/corrected beforehandoff.
Finalcatalogforecastmodes/hash/readers PASS, original145enginehashes unchanged,813priorstateJSON preserved duringguardedrestart;8080running,temporary8081closed. Oneactualproviderrequest atcheckpoint; conservative traffic3640858902/5368709120B, VMlimitsunchanged. Report reports/METEO-REALE.md and reports/weather/verification.json; raw run manifests/native products retained. Reviewer Codex self-check; noH1–H3/forecastskill/operational qualification. FR-06full/FR-17/M5–M7 remainBLOCKED forensembles,distributedforcing,effects,alertsqualification,history/scale; scoped FR-WX-REAL-01 PASS. Current next researchincrement remains all3floodphysicalactions/qualifiedinputs, not package reinstallation.

| Check | Outcome | Scope |
|---|---|---|
| FR-WX-REAL-01 | PASS | Real Open-Meteo point on map, hourly selection, fresh frozen forecast into actual native jobs, all VM/free |
| Shared forecast cache/quota/time/units/integrity | PASS | Actual1request,97software tests incl12forecast checks; no browser-provider requests |
| Native future FIRE60min / HMC→REFlEx6h | PASS | Both new8080jobs succeed,29content/forcing/provenance assertions; dry native map explicit |
| First flood / harnessyear / cataloglabel defects | FAIL | Historical negative attempts retained; corrected and verified in new runs |
| UI weather and monitoring regressions | PASS |70checks,18axe scans,375/768/1440, raw incompletes retained |
| Full FR-06/17 and M5–M7 | BLOCKED | No ensemble/distributed/calibrated/alert-quality/historical/fullscale qualification |
| New30min/100k/historical/mitigation/daystudy | NOT RUN | Earlier release blockers unchanged |


## Remaining integration clarification — remaining-integrations-20261016T063454Z

| Check | Outcome | Evidence / limitation |
|---|---|---|
| Native HMC reservoir input contract inspection | PASS | Guest source paths/SHA256/line extracts and executed command in experiments/runs/remaining-integrations-20261016T063454Z; source baseline cb012796c1633da474f068021b4265eb9391217e; reviewer Codex self-check |
| Full basin reservoir / HMC→REFlEx intervention maps | NOT RUN | Source inspection and prior component tests do not close integration |
| New hydraulic engine adoption/ARM64 build | NOT RUN | No engine installed or selected; architectural assessment required |
| Complete remaining integrations/research release | BLOCKED | Existing functional/data/scale/validation dependencies retained; user clarification is authorization, not evidence of completion |


## Weather overlay controls — weather-layers-20261016T063635Z

| Check | Outcome | Evidence / scope |
|---|---|---|
| FR-WX-LAYERS-01 point weather overlays | PASS |36browser checks, source b4dc8e5f139ee5dca4aff12ce8887758d1faa49c; raw experiments/runs/weather-layers-20261016T063635Z/browser/results.json; independent variable/master toggles, selected time, FROM/toward convention, hazard visibility preserved |
| Responsive/accessibility regression | PASS |375/768/1440 map/results,6axe scans0violations; incomplete axe checks retained |
| Shared quota / no provider browser call / no model submission | PASS |Existing shared VM cache, before/after attempt count unchanged; no model job created by map controls |
| SameVM live deployment | PASS |4static files SHA256 match; no backend restart or scientific execution; reports/weather/layers-verification.json; reviewer Codex self-check |
| Regional distributed weather field / new physics / new soak | NOT RUN |Current forecast covers one model point; no duplicated/interpolated field or new release claim |


## Professional responsive UI — professional-ui-20261016T064202Z

| Check | Outcome | Evidence / limits |
|---|---|---|
| FR-UI-DESIGN-01 responsive professional presentation | PASS |136automatedbrowserchecks; code 2bf6bd804e95dd36f2d188ff8e4946a7e165344f; reports/design/verification.json, report reports/INTERFACCIA-GRAFICA.md; reviewer Codex self-check |
| Layout/navigation320–1920 including tablet/landscape | PASS |8sizes,4sections+physicalpage, no overflow, navigation touch targets ≥44px, mobile planner reachable |
| Automated accessibility/keyboard/reduced motion | PASS |21axe scans0violations; raw incompletes retained, focus/navigation/reducedmotion assertions |
| Existing monitor/weather/decision regressions | PASS |44+36checks;2solver/verifier calls sameVM isolatedprefix; no physical job created |
| Local deployment/state preservation | PASS |3staticfilehashes;816priorstateJSONpreserved,backendkeptalive, sameVM bounds |
| Physical devices / crossbrowser / user study / new30min/100k | NOT RUN |Viewport emulation cannot establish perfect adaptation on all hardware/browsers; prior full-release blockers unchanged |


## Transparent weather map symbols — transparent-weather-20261016T065258Z

| Check | Outcome | Evidence / limits |
|---|---|---|
| FR-WX-LAYERS-01 transparent presentation | PASS |Transparent surface/no card, SVG wind, compact translucent values;38weatherchecks source 72f059d76c39d39cc479b43fe26bcad8d6c6b81e |
| Responsive/keyboard/weather regressions | PASS |56design+38weather=94checks,8viewport/orientations320–1920,9axe scans0violations; raw incomplete checks retained |
| VM deployment / state preservation | PASS |5staticSHA256, 816priorstateJSONunchanged, no backend restart; reports/weather/transparent-verification.json; reviewer Codex self-check |
| New physics / regional grid / soak100k / real devices | NOT RUN |Presentation-only; existing qualification blockers unchanged |


## Regional animated real wind — regional-wind-20261016T071443Z

| Check | Outcome | Evidence / limits |
|---|---|---|
| FR-WX-REGIONAL-01 real regional acquisition/representation | PASS |315nodes/96h/940016B, IDW actualcoords/bilinearU/V, immutable raw/receipt; reports/VENTO-REGIONALE.md |
| Cache/quota/negative contracts and regressions | PASS |110VMsoftware tests, max8/day/3h/315equivalents; scientific skill not implied |
| Wind UI/animation/responsive/accessibility | PASS |164browserchecks,24axe0violations,8viewport/orientations, pause/hide/reducedmotion/mobilefit; reports/weather/regional-verification.json |
| Frozen vector/engine integrity | PASS |1890comparisons with rounding tolerance0.000051m/s;145source/binarypinsunchanged; native-verification.json |
| First unit classification / provider requests | FAIL |Initial expected error mismatch; firstHTTPError lackingcode/body; diagnosticHTTP400elevationarity; allraw retained, corrected acquisitionPASS |
| Deployment / sameVM / state preservation | PASS |9file+contextdeploys/backups,823priorJSONpreserved excludingtrafficcounters, loopbackhealth, source74bd696867fa88cffd3f9ae498d57a71b19b568b; reviewer Codex self-check |
| Full forcing/CIMA reruns/forecastskill/soak100k/realdevices | NOT RUN |Display-only increment, prior complete-release gates BLOCKED |


| Regional wind closure check | Outcome | Evidence / limit |
|---|---|---|
| Guest wall-clock skew found | FAIL |Host12:44:25/guest07:48:55UTC; initial synced flag insufficient, original outputs retained |
| Existing NTP service resync on idle queue | PASS |sudo -n systemctl restart systemd-timesyncd, no install/config change; host/guest<3s final-runtime.json |
| UI clock/expiry downgrade and updated cache | PASS |2newclockchecks,166browserchecks total/24axe0violations; automatic second real dataset verified1890components;145enginepins unchanged |
| Direct API/CLI clock certification | NOT RUN |Correct OS time remains prerequisite; browser gate is conservative UI behavior, not independent operational clock authority |

## Geographic target reaffirmation — 2026-10-16
| Item | Status | Evidence / scope |
|---|---|---|
| GEO-TARGET-RECONFIRM | PASS (documentation) | Explicit user instruction: Abruzzo pilot; target all Italy and abroad, including Senegal. SPEC scope, PLAN and MEMORY aligned; reviewer Codex self-check. |
| GEO-TARGET-E2E | NOT RUN | No new geographic execution or provider qualification in this checkpoint. Existing synthetic two-profile checks remain limited to their recorded scope; QR-08 full gate remains BLOCKED. |

## Persistent event references — 2026-10-16
| Item | Status | Evidence / scope |
|---|---|---|
| FR-MAP-EVENT-01 current scenarios | PASS | event-markers-20261016T1304Z;30specific+56design browser checks,6axe scans0violations; monitor zoom8–20, filters/opacity/offscreen/keyboard/nearby icons, comparison+physical ignition;7VM SHA matches; reports/ICONE-EVENTI.md. Codex self-check. |
| Live geolocated alarm integration / large catalog | NOT RUN | Current replay alerts have no verified point geometry; not invented. No clustering/load or new geography qualification. |

## Weather across visible viewport — 2026-10-16
| Item | Status | Evidence / scope |
|---|---|---|
| FR-WX-VIEW-01 current monitoring map | PASS | viewport-weather-20261016T1320Z:117software/59browser,6axe scans0violations,13zoom coverage100%, temperature/precipitation transparent selection and point inspection. Codex self-check; reports/METEO-SULLA-MAPPA.md. |
| Actual global-model source and runtime | PASS |325228B raw+receipt/SHA;972transformation checks,145enginepins unchanged,9source/runtime hashes; bounded free shared cache, conservative daily6456location-equivalents including prior endpoints. |
| Cell-click inspection before correction | FAIL | browser-inspection/final/inspect-diagnostic/inspect-fix retain failed attempt; final verified suite PASS after feature click handler added. |
| Real Senegal/multi-country native workflow / distributed model forcing | NOT RUN | Global display adapter/synthetic bounds support does not qualify international physics or replace CIMA forcings. QR-08/fullM5–M7 unchanged BLOCKED. |
