# Local domain descriptions and compatible execution — A2/A3

Implemented 24 October 2026, after review of the Stage 1 migration design. Discovery is **read-only metadata**. A3 now uses that metadata inside the existing isolated pipeline to select a reviewed worker; this is not a hot-plugin system.

From the application directory in the existing Linux VM:

```sh
PYTHONPATH=src ../core-env/bin/python -B -m hazardia.package_catalog
PYTHONPATH=src ../core-env/bin/python -B -m unittest tests.unit.test_package_catalog -v
```

The first command emits `hazardia.domain-catalog/0.1.0` with the two existing packages `hazardia.wildfire` and `hazardia.flood`. Python callers may use `discover().describe()` or `discover().get(package_id).describe()`. Returned dictionaries are independent copies. No web endpoint or UI control is added.

## What is described

Descriptors live in `src/hazardia/domain_packages/`; `schemas/domain_package.schema.json` defines their strict format. `index.json` pins their SHA-256 bytes. Descriptor version 0.1.0 is the HAZARDIA metadata version, **not** an upstream model release. Upstream source revisions come from the pins already used in `scripts/configure_runtime.py` and have been checked against the current VM configuration. Existing model hashes remain the runtime authority; discovery does not inspect or certify installation.

Each descriptor names its legacy hazard, bilingual labels, approved existing adapter/model revisions, existing input/output validator and schema versions, semantic limitations, decision policy references, verifier and replay-degradation reference. Maximum descriptor size is 16 KiB; the generic catalog collection is bounded to 16 entries, while bundled discovery deliberately admits only the two reviewed manifests. This is a pilot structural bound, not a new performance requirement.

The flood result remains a maximum over its hydrological window. The ideal fire policy uses priority points rather than people. The legacy request validator remains responsible for grids, units, freshness, seed, scientific assumptions, native actions and admissible combinations: descriptor metadata does not replace these checks or supply a new semantic composition engine.

## Qualification and safety

Presence in the catalog means a reviewed **description** is shipped. Runtime availability and data availability are explicitly `NOT_ASSESSED`; scientific qualification is `UNQUALIFIED_RESEARCH`; operational authorization is `NOT_GRANTED`. No descriptor grants an action, certifies resource effectiveness, changes aircraft safety, or bypasses `UNKNOWN` and the independent verifier.

Model, validator, policy and supervisor references are inert metadata. They are never passed to importlib, shell, subprocess or a network service. Discovery validates unknown fields, schema/core versions, digest drift, duplicate JSON fields, ID collisions and unknown model/adapter/contract/policy bindings. It returns no partial catalog on error. Packaged index hashes detect drift, not publisher authenticity: a malicious person who controls the source distribution can change both descriptors and index.

## Compatibility and rollback

The web service, JobStore, workspaces, existing CLI and scientific workers do not import discovery. The isolated pipeline now calls `adapters.dispatch.prepare`: only the fixed reviewed table supplies interpreter configuration keys and executable worker names. Descriptor strings are never imported or executed. FIRE keeps its exact PYTHONPATH extension; FLOOD retains its explicit experimental-patch guard. Unknown hazards retain the former error before discovery. Runtime engine revisions must match the selected reviewed description; existing source hash guards run before and after native execution. A corrupt/missing catalog or incompatible binding produces a classified failed job with no silent legacy fallback. API startup and archived products remain available. No legacy schema, run, workspace, solver policy, API or renderer was migrated.

Each new execution writes `adapter-binding.json` exclusively before starting a worker: descriptor body/identity/version/raw-byte digest, command lists and frozen request/runtime hashes. The existing JobStore includes this file in its immutable artifact manifest. This is an execution-time binding, not an acceptance-time descriptor freeze; request/runtime freezing remains unchanged. Retrying creates a new job and receipt, preserving the previous one. A source deployment is still controlled; queued jobs use the reviewed code/catalog present at their execution, as they already used current worker code.

The catalog JSON is a metadata view: `runtime_assessed`, `data_assessed` and `dispatch_changed:false` describe the discovery operation, not the deployment state of the pipeline. It never runs a model or changes a dispatch itself.

Rollback of A3 is a source revert/redeployment to A2, without deleting any run or modifying its archived receipt. The stable tag `stable-2026-10-24-pre-domain-evolution` remains unchanged. No runtime fallback flag bypasses integrity guards. A4 policy extraction and A5 schema/workspace migration remain separate increments, not implemented here.

## Reproduction and evidence

[A2 report](../reports/DOMAIN-PACKAGES-A2-20261024.md), [A3 report](../reports/DOMAIN-DISPATCH-A3-20261024.md), [test results](../reports/domain-packages/verification.json), [native diagnosis](../reports/domain-packages/native-diagnosis.json). Run native regressions only in the Linux geo environment, using explicit frozen jobs, a new run ID and no application DB submission:

```sh
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python -B \
 tests/integration/verify_package_catalog.py \
 --runtime /home/hazardia/hazardia-runtime --run-id YOUR_NEW_RUN_ID \
 --fire EXISTING_SUCCESSFUL_FIRE_JOB --flood EXISTING_SUCCESSFUL_FLOOD_JOB
```

The verifier deliberately retains an exact-replay failure. REFlEx uses random optimizer initialization; the observed tiny differences are documented rather than relabelled PASS. Technical execution and physical validation are separate outcomes. No new general repeatability tolerance or upstream RNG patch is introduced by A2.

## A3 regressions and selection overhead

```sh
PYTHONPATH=src ../core-env/bin/python -B -m unittest tests.unit.test_dispatch tests.unit.test_dispatch_jobs -v
PYTHONPATH=src:. ../core-env/bin/python -B tests/integration/benchmark_dispatch.py
```

The supervisor tests use a clearly synthetic sleeping interpreter to exercise the real pipeline, timeout/cancellation/descendant termination and explicit retry. They are not native simulator evidence; separate frozen CIMA replays provide that evidence. The microbenchmark compares only old/new selection, fresh-interpreter and in-process cases, not simulation runtime or the decision deadline.
