# ADR-0005 — Concrete M1 boundaries and compatibility

Date: 2026-10-15. Status: accepted within authorized M1 scope. Reviewer: Codex self-review; external physical qualification pending.

M1 implements two actual adapters: PROPAGATOR and HMC→REFlEx. Acquisition/cache/normalization, request validation, persistent bounded job control, simulator processes, and independent raster-content publication have separate responsibilities. No decision core, UI service, Digital Twin, AI model, model registry or application-agent runtime is added. Seven architectural possibilities remain conceptual (ADR-0004).

## Contracts and versions

Frozen M0 examples/schemas 0.1.0 remain immutable. Their eleven-kind envelope is a feasibility contract, not silently repurposed as the M1 application. Concrete observation, simulation request and hazard product use strict 0.2.0 schemas, UTC timestamps, explicit grid/units, content hashes and unqualified-research assumptions. Unsupported versions/fields are rejected. Observation 0.1.0 metadata can migrate explicitly, preserving source time/rights/asset identity, with no asset qualification. Other M0 kinds are not implicitly migrated; shared state/event/consequence design belongs to M2.

Run manifest is 0.3.0 because early M1 0.2.0 manifests did not require seed and environment fields. The explicit legacy migration preserves original status/hash and marks environment UNKNOWN_LEGACY_ENVIRONMENT; it does not rerun or rehabilitate failures. Requests/products remain 0.2.0; package version 0.1.0 is independently versioned. No public release is made.

## Runtime and numerical policy

All acquisition, geospatial preparation, engine execution, tests and rendering run in the existing ARM64 Linux VM. Core Python3.10/jsonschema3.2.0, fire Python3.12/Numba, and flood Python3.10/GRASS/GDAL remain separate environments/processes. Core has no simulator/scientific-array imports. Dependencies are pinned in each executed manifest, engine source files checked before and after work. A local editable install permits development; every execution records Git SHA, tracked dirty state and source hashes.

SQLite WAL provides a FIFO with four waiting entries and one active job per runtime store. Separate runtime stores must not be created as a concurrency bypass. A controller runs one job per CLI `work-once` invocation. Queued/running cancellation, process-group timeout, disk/log limits, explicit retry and controller recovery have typed outcomes. Recovery does not accept unverified output. This is a single-VM M1 supervisor, not a distributed scheduler or an M6 capability manager. Queue delay and model execution are recorded separately; no 60-second decision claim.

The flood adapter uses the declared two-line REFlEx compatibility copy from M0, never describes it as unmodified upstream. The source example's 0.1m optimization floor failed the unchanged 1% residual diagnostic on small real-terrain/synthetic-forcing reaches. A subsequent experiment permits 1e-6m minimum depth using the native configuration; this changes a numerical search bound, not the physical model or accuracy threshold. Preserve both outcomes and disclose post-failure tuning. Derived geotransforms use absolute tolerance1e-12 degrees to accommodate GDAL rounding; no raster resampling or cell shift is hidden.

## Alternatives and consequences

Directly importing all simulators in one environment risks incompatible Python/NumPy/geospatial dependencies; separate workers within the same VM meet the user's placement rule. A service bus/distributed queue is premature for this resource budget. Keeping the frozen M0 envelope unchanged for every application field would require misleading defaults/unknown values; explicit narrow contracts and migrations make changes visible. Broad generalized interfaces for seven concepts would add untested behavior, so only concrete current responsibilities are implemented.

AT-EXT-02: verify actual versioned products and incompatible units/grid/time cases in M1; downstream decision consumer NOT RUN until M3. AT-EXT-03: normalized public/local snapshot sources and core import review in M1; fusion M2 and decision independence M3 NOT RUN. AT-EXT-04: concrete input/product/engine-metadata review only; compatible alternate predictor/unsupported capability checks at M3 NOT RUN. AT-EXT-05: both real engines and dependency/process evidence in the same VM; repeat for later components. AT-EXT-01 unchanged decision-core replacement NOT RUN because the core does not yet exist. Contract compatibility never implies physical qualification or human approval.
