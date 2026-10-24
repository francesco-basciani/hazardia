# Domain-independent exchange contracts — A5a

The shared product boundary now accepts opaque domain IDs and variable quantities without FIRE/FLOOD enums. The existing public `hazardia.contracts` module is a compatibility facade: old validator names/signatures delegate to `adapters.legacy_contracts`; new callers use `validate_exchange_product`, `validate_exchange_requirement` and `check_exchange_compatibility`. All seven old validator/migration function bodies are unchanged (AST comparison); their legacy schemas remain unchanged.

## Implemented scope

The new contracts describe **regular north-up gridded products**, not every possible spatial data type or an executable model. JSON schemas are `schemas/exchange_product.schema.json` and `exchange_requirement.schema.json`, version 0.1.0. Code is in `hazardia.exchange`. Metadata is bounded to 256 KiB, 32 variables and bounded provenance lists; no scientific library, network, conversion, reprojection, interpolation or model execution is invoked by this kernel. Existing core JSON Schema dependency is reused.

A product states:

- Arbitrary domain ID, product ID, OBSERVED/FORECAST/SIMULATED origin and explicit qualification.
- Grid shape, CRS, X/Y axis convention, affine transform, NoData, horizontal unit and vertical reference.
- Exact validity window, producer source cutoff and explicit availability (or UNKNOWN).
- Variable IDs, quantity identifiers, exact units, temporal support, uncertainty kind/member count/calibration, artifact references and statistics.
- Hashed provenance records, explicit engine identity/status, license status, assumptions.

`KNOWN` means the value is declared, **not** scientifically verified. `UNKNOWN` and `NOT_APPLICABLE` are distinct and carry reasons; neither can contain an invented value. In particular an unqualified DSM datum remains labelled unqualified even when its declared name is known. Original data rights and scientific assumptions are not inferred from software installation.

A consumer declares its expected domain, accepted origins/qualifications, exact grid and window, cutoff and maximum age, quantities/units/support, accepted uncertainty, minimum member count, and whether calibration/license must be known. If it explicitly does not need an absolute vertical reference it may mark that requirement NOT_APPLICABLE with a reason; this waiver is never inferred by the checker.

## Compatibility results

- `COMPATIBLE`: metadata satisfies the explicit consumer requirements.
- `INCOMPATIBLE`: a known mismatch, wrong unit/grid/window/semantics, future source or stale product. Window maxima and cumulative values are not reused for a different sub-window.
- `UNKNOWN`: required datum/unit, availability, license, calibration or member count is unknown.

Malformed contracts raise a classified error. A known mismatch takes precedence over UNKNOWN, with individual issues retained. Metadata agreement does not qualify physics, verify an ontology, authorize dispatch or prove operational suitability. The return always has `operationally_approvable:false`; compatibility never executes anything. Quantities/units are compared literally; there is no automatic unit or vocabulary normalization.

With `root` supplied the checker verifies SHA-256 and path containment for payload/provenance assets. Without it the result explicitly says `asset_hashes_verified:false`. Hash verification is not raster interpretation, source authenticity or numerical model validation; the existing native validators remain authoritative.

## Existing CIMA path

`adapters.legacy_exchange` validates the old request/product using unchanged legacy checks, then creates a **non-destructive view**. FIRE/FLOOD interpretation is isolated here:

| Legacy field | Units | Support / uncertainty retained |
|---|---|---|
| FIRE_PROBABILITY | 1 | Cumulative reached probability at horizon; simulator realization frequency, not a calibrated weather/event probability |
| ARRIVAL_TIME | s | Earliest realization offset from window start, masked where not reached; not expected arrival |
| MAXIMUM_DEPTH | m | Window maximum derived from per-reach peak discharge; not instantaneous/observed water depth; uncertainty not quantified |

New pipeline executions exclusively write `exchange-product.json` **after** unchanged native commands/product generation and both engine-hash guards. JobStore includes its hash in the existing artifact manifest. The legacy request, product, arrays, time series and workspace remain authoritative and unchanged; time-series/frames are not converted by this final-product adapter. Sidecar validation/write failure yields a classified failed job, without silent fallback. The new metadata is not added to old job directories.

For archived products `export_legacy_product(root)` leaves original publication time UNKNOWN. It never invents it from mtime or the present time. Only a new producer execution supplies the explicit current availability. Aggregate license and calibration remain UNKNOWN; original input metadata is retained through hashed raw references. Native samples do not establish calibration or turn research into operational authorization.

## Read-only CLI

From the existing Linux VM application directory:

```sh
PYTHONPATH=src ../core-env/bin/python -B -m hazardia.exchange \
 --product /path/to/new-job/exchange-product.json --root /path/to/new-job

PYTHONPATH=src ../core-env/bin/python -B -m hazardia.exchange \
 --product /path/to/product.json --requirement /path/to/consumer.json --root /path/to/assets
```

Inspection lists unknown fields. Check exit codes: 0 COMPATIBLE, 3 UNKNOWN, 2 INCOMPATIBLE/error. No files/models/providers are created by these commands. Schema references are resolved locally only: the supported VM's JSON Schema 3.2 has a URN/fragment issue, so the kernel explicitly expands local definitions and refuses external/missing/cyclic references.

## What remains separate

Generic job admission for arbitrary models, automatic model composition, vector/point/time-series adapters, full provider conversion, new simulator/domain registration and UI generation are **not implemented by this increment**. The existing execution API is still the reviewed legacy route for the two current models, behind compatible adapters. New domain execution needs a qualified adapter/binding; a valid exchange document alone never makes it executable. No new hazard/layer controls are added.

There is no workspace or historical data migration. Rollback is source revert/redeploy to A4, retaining already-written artifacts; old consumers continue reading the same legacy product files. Standards such as OGC are not claimed as implemented/conformant. [Report](../reports/EXCHANGE-CONTRACTS-A5A-20261024.md) documents tests, native replay failures, performance and remaining scope.
