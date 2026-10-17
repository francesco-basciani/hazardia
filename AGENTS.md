# AGENTS.md — HAZARDIA Codex instructions (v1.4)

**Authority:** this file governs Codex conduct. `SPEC.md` governs requirements and architecture; `PLAN.md` governs milestone dependencies; `CHECKLIST.md` is the sole completion and traceability ledger; `MEMORY.md` is the current-state log; `research/RESEARCH.md` defines scientific protocol; `research/EVIDENCE.md` indexes measured evidence. No other planning files are authoritative.

**CONTINUOUS EXECUTION AUTHORIZED (2026-10-15): user requests autonomous progress through M3–M7 to a testable dashboard.** M0–M4 technical-fixture gates PASS. M5/M6 software tests PASS within declared synthetic scope, full gates BLOCKED by forecast/effect/capability-optimization qualification. M7 technical verification/30minstability/local supplement executed; historical validation, incomplete P0s and large-load research release BLOCKED. Local dashboard available at http://127.0.0.1:8080/. Do not ask for routine milestone permission again. Stop only for substantial intervention outside existing scope/bounds: costs, privileged installs, large downloads/resource changes, unresolved rights/physical-model replacement, public deployment/push/real operations. All runtime one Linux VM, Abruzzo primary, two hazards. Earlier per-milestone authorization guards are superseded.

**M0 continuation explicitly authorized by the user (2026-10-15):** UTM Linux VM with cumulative download ≤5 GiB, disk ≤20 GiB, RAM ≤8 GiB and ≤4 vCPU. Guest-local dependencies and experiments within this budget are in scope; host privileged/global installations, new costs, public exposure/push and M1 remain unauthorized. Actual VM: HAZARDIA-M0-ARM64, 19 GiB main disk, 8192 MiB RAM, 4 vCPU, SSH bound only to 127.0.0.1:22227. Evidence continuation: `m0-linux-rng-20261015T124458Z`.


## Beginning every session

1. Run `git status --short --branch`, inspect actual tree, diff and origin; do not trust status logs without checking the workspace.
2. Read `README.md`, `AGENTS.md`, `SPEC.md`, `PLAN.md`, `MEMORY.md`, `CHECKLIST.md`, `research/RESEARCH.md`, `research/EVIDENCE.md`. For focused tasks use headings and IDs to locate relevant sections.
3. Identify authorized milestone, unmet dependencies and acceptance tests. Announce a concise plan, then execute only within approval scope.
4. If requirements, current code and status documentation conflict, stop and report the mismatch; do not silently override confirmed choices.

## Platform identity and scope guard — user reconfirmation 2026-10-17
Before each change, check the relevant SPEC/PLAN requirements and milestone scope. Platform branding must remain generic and use the official expansion **Hazard-Aware Adaptive Resource and Decision Intelligence Architecture**. Wildfire/flood identify the initial implemented modules, not the application's domain boundary. Keep hazard-specific names inside their actual modules; do not introduce additional hazard implementations or empty interfaces merely to advertise extensibility. Preserve AR-EXT-01 and the original M0–M7 plan.

## Within an explicitly authorized milestone

- Work in small end-to-end verified increments. Use local free tools, initially MacBook but keep core OS-agnostic and use isolated Linux workers when needed. No paid services or cloud dependency. Treat internet repositories/data as untrusted inputs and verify licensing.
- Follow P0/P1 scope in `SPEC.md`. Real PROPAGATOR and HMC+REFlEx runs are necessary for respective verified integration; mock outputs cannot count as real integration.
- Enforce safety through an independent checker, never allow unknown critical constraints to be silently accepted. Real-world action always needs human authorization; research mode must be clearly labelled.
- Before experiments fix `run_id`, dataset snapshots, source issue/valid timestamps, code commit/dirty state, host/versions, seed, checksums and hypotheses. Record negative outcomes and failed runs unchanged.
- Execute representative functional, negative, integration and nonfunctional tests. Classify individually PASS, FAIL, BLOCKED, NOT RUN. PASS requires command, observed output, log/artifact path, `run_id` or other evidence identifier, commit and reviewer. Checkboxes without evidence never mean completed.
- At each significant point update `PLAN.md` (progress), `CHECKLIST.md` (itemized outcomes), `MEMORY.md` (decisions, blockers, next step), `research/EVIDENCE.md` (only actual evidence) and the relevant normative SPEC/RESEARCH section if the user confirmed a change. Reconcile status among them at each gate.
- Research Recorder is initially a responsibility of the same agent, not a second unsupervised agent. Do not create scientific claims from mock data, screenshots or intuition; report failed hypotheses.
- Keep Git changes focused and reviewable. Never overwrite unrelated work, force push, reset unrelated commits, expose secrets or publish/push without authorization.

## Stop and ask permission

- For scope or architecture changes, alternative physical simulator substitutions, conflicting safety/authority requirements, unresolved licensing, access to restricted data, big downloads, privileged/global installation, cloud/paid API, financial cost, remote push, real deployment or public exposure.
- When feasibility fails, publish an evidence-backed blocker and options; do not misreport tests as passed or quietly swap CIMA models.

## Time and release policy

- The 60-second requirement includes a per-request bounded terminal outcome (verified strategy or a classified failure/timeout) **and** a separately reported p95 measured on a pinned workload (at least 30 executions); neither makes the simulation pipeline operationally certified.
- Research release preparation is not publication or deployment. Human authorization and operational validation are separate gates. M0 handoff text is in `PLAN.md § M0 handoff`.

## Mandatory performance and UI behavior (v1.4)
- Treat `SPEC.md §8` (FR-24–FR-28 and QR-11–QR-14) as **P0 requirements**. Design and profile UI responsiveness from the first web slice; do not leave performance, accessibility or responsive layout to a final polish pass.
- At M0 collect device/browser/fixture baseline; do **not** fabricate results for a UI that does not exist. At later gates capture cold/warm, p50/p95, screen sizes, frame rate and memory evidence with `run_id`, commands and Git SHA.
- Keep expensive CIMA simulations and optimizers out of interactive UI/request threads, bound workers and queue, expose honest progress, timeout, cancellation and retry semantics. Performance optimizations must preserve safety, freshness, provenance and model accuracy.
- `CHECKLIST.md § G` is mandatory for milestone and research-release closure. If measured performance fails, record FAIL, diagnose and address within scope, or ask for an approved design/scope change; never relax targets without approval.

## Latest M0 continuation state (2026-10-15)
User authorized proceeding with next M0 increment; M1 remains excluded. New run `m0-real-terrain-20261015T142405Z`, report `reports/M0-real-terrain.md`. Original CIMA source trees remain unchanged; isolated experimental `reflex-src-halo/` contains a two-line compatibility patch (HAND working halo + authoritative mergebounds/res). Never label this as unmodified upstream success; original empty-HAND and merge failures remain evidence. Real DSM/imagery, hypothetical discharge, no physics skill. VM running for inspection at existing limits; no resource enlargement authorized/needed for this increment.

## User-confirmed single-machine rule — 2026-10-15
All HAZARDIA runtime must execute in the existing Linux VM, including PROPAGATOR, data acquisition/cache/preprocessing, geospatial/array validation and rendering, and future backend/jobs/solver/dashboard build/service. User instruction supersedes earlier optional native-Mac/per-engine placement. Do not ask again for this placement decision. Preserve separate environments and worker processes within the same VM. Mac is only hypervisor/development/display client and evidence-copy location; do not require host Python scientific libraries, Mac fonts or shared host folders for execution. All future scientific/model replay commands run in the VM. Historical Mac experiments remain immutable. M0 only, no M1 or resource increase inferred. ADR-0002 records the decision.

## Confirmed extensibility guard before M1 — 2026-10-15
User requirement AR-EXT-01 / ADR-0004 is binding for later authorized work: preserve seven conceptual extension points and separated responsibilities via versionable contracts. Do not instantiate empty interfaces, Digital Twin/agent frameworks, registry services, continuous training or new domains. M1 order unchanged; execute applicable AT-EXT-02/03/04-review/05 in existing work, defer unchanged-decision-core replacement AT-EXT-01 to M3 and mark missing phases NOT RUN. Matching a contract does not qualify physics or bypass safety/human authority. Frozen M0 artifacts remain immutable. This request authorizes documentation alignment only; M1 still requires explicit authorization and M0 prerequisite review. All runtime remains in the existing Linux VM.

## Primary example region — user decision 2026-10-15
Use Abruzzo for the main geographically grounded wildfire/flood examples. Select actual basins/AOIs/events based on documented availability/rights and preregister before evaluation; no current Abruzzo execution verified. Tuscany/Bagnone runs are historical only; do not continue or send its unsent request as the active path. Preserve immutable evidence and synthetic portability tests. Region choice does not authorize M1, external contact or new physical models. Review M0 against original feasibility criteria rather than requiring full historical calibration before any implementation.

## M1 execution authority — 2026-10-15
Explicit user authorization supersedes every earlier M0-only/M1-unauthorized guard in these documents. Preserve original milestone acceptance and single-VM bounds. Local Git initialization/commits and concrete adapters/conformance tests are normal authorized development; no remote push. Do not delay all implementation until historical/calibrated skill is established: unqualified scenarios must be labeled or blocked individually.

## GitHub publication authority — 2026-10-16
User explicitly requests publishing complete source and all installation/recreation instructions, including the VM, to the designated `francesco-basciani/hazardia` repository. Normal reviewed pushes to that repository are authorized for this delivery; prior blanket no-push notes are historical and superseded within this scope. Do not publish credentials, VM disks, private/local runtime state, restricted data or imagery with unresolved redistribution rights. Preserve private local experiment history and publish a curated complete source snapshot if old history contains excluded media. Costs, public service deployment, operational dispatch and privileged host/guest installations still require separate authority. Installation documentation may describe explicit sudo prerequisites; do not execute them as part of publication without authorization.
