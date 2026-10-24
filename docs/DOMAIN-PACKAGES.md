# Local domain descriptions — A2

Implemented 24 October 2026, after review of the Stage 1 migration design. This is opt-in **read-only discovery**, not a replacement for the existing runtime or a hot-plugin system.

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

The web service, JobStore, pipeline, workspaces, existing CLI and workers do **not** call this catalog. Missing/broken descriptors therefore fail opt-in discovery without stopping the existing simulators. No legacy schema, run, workspace, solver policy, API or renderer was migrated. Package data are included in the wheel; offline wheel construction and discovery from the unpacked wheel have been tested.

A2 can be removed by reverting its additive commit; existing dispatch needs no rollback switch. The stable tag `stable-2026-10-24-pre-domain-evolution` remains unchanged. A3, a compatible execution lookup, is a separate future increment. It must preserve dispatch errors, process isolation, runtime hash checks, timeouts/cancellation and exact request/native forcing/action behavior; it must not execute arbitrary descriptor strings.

## Reproduction and evidence

[Report](../reports/DOMAIN-PACKAGES-A2-20261024.md), [test results](../reports/domain-packages/verification.json), [native diagnosis](../reports/domain-packages/native-diagnosis.json). Run native regressions only in the Linux geo environment, using explicit frozen jobs, a new run ID and no application DB submission:

```sh
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python -B \
 tests/integration/verify_package_catalog.py \
 --runtime /home/hazardia/hazardia-runtime --run-id YOUR_NEW_RUN_ID \
 --fire EXISTING_SUCCESSFUL_FIRE_JOB --flood EXISTING_SUCCESSFUL_FLOOD_JOB
```

The verifier deliberately retains an exact-replay failure. REFlEx uses random optimizer initialization; the observed tiny differences are documented rather than relabelled PASS. Technical execution and physical validation are separate outcomes. No new general repeatability tolerance or upstream RNG patch is introduced by A2.
