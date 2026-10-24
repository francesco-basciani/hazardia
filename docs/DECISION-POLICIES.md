# Reviewed decision policies — A4

`hazardia.decision.policies` isolates immutable semantics for the **two existing** decision contracts. It is a local reviewed table, not a plugin installer or a universal optimization model. No request, response, workspace or product schema is migrated.

| Existing contract | Internal policy | Units and effect | Existing behavior retained |
|---|---|---|---|
| decision_problem 0.5.0 | RESEARCH_EXPOSURE | Synthetic exposed people; IMPACT_ONLY | EVACUATION / VEHICLE; several resources per event subject to exposure bounds; empty verified selection remains accepted; no ideal-policy fallback |
| decision_problem 0.6.0 | FIRE_IDEAL_ASSIGNMENT | Authored weighted priority points; exclusive area coverage proxy | FIRE_SUPPRESSION / category equipment; at most one resource per target; NO_ADMISSIBLE_ACTION for empty assignment; bounded independently verified greedy fallback |

The 0.6.0 declaration remains exactly `domain=FIRE_IDEAL_ASSIGNMENT`, `loss_unit=weighted_priority_points`, `benefit_model=EXCLUSIVE_AREA_COVERAGE_PROXY`. The 0.5.0 payload still has no policy field. Unknown schemas/declarations/units are rejected, never defaulted to a different policy. Public `fire_ideal.POLICY` and `CATEGORIES` keep their old values and types.

## Responsibility boundary

- `problem.validate` keeps its signature, strict shared checks, error codes/messages and data validation; policy headers/resource shape come from the reviewed definitions.
- The HiGHS worker still constructs the same mathematical model and eligibility predicates itself, using the policy's fixed skill/equipment/effect/target semantics. No dynamic imports, arbitrary policy strings or new solver dependencies.
- The controller keeps its solver backends, deadlines and fallback algorithm. Existing policy-specific verification reserves remain 0.1 s / 2 s. The outer 60 s watchdog and queue semantics are unchanged.
- `verifier.py` is **byte-for-byte unchanged**. It does not import the policy module or reuse solver eligibility predicates/rows. Common input validation remains shared as before; operational safety checks and loss arithmetic remain independent. A controlled skill-metadata fault is rejected by the verifier despite the altered solver policy.
- Spatial priority preparation, aircraft exclusion, intervention assumptions, units and missing-data handling are unchanged. Declared categories do not certify operational aircraft availability or resource efficacy.

Policy metadata and table are immutable; returned declaration dictionaries are copies. Policy selection makes no network requests and imports neither JSON Schema nor NumPy, geospatial libraries or solver libraries. This matters because the clean decision environment deliberately lacks the core validator's JSON Schema dependency.

## Tests and reproduction

Run in the application directory of the existing Linux VM:

```sh
PYTHONPATH=src ../core-env/bin/python -B -m unittest tests.decision.test_policies -v
```

For differential tests, extract the **trusted pre-A4 source** from the public baseline commit `41ca275` into a new reference directory as `legacy_problem.py`, `legacy_highs.py` and `legacy_controller.py`. Never use untrusted downloaded Python as an oracle. The verifier accepts explicit frozen problem paths and never modifies them:

```sh
PYTHONPATH=src:. ../core-env/bin/python -B tests/integration/verify_decision_policies.py \
 --solver-python /home/hazardia/hazardia-runtime/decision-env/bin/python \
 --reference-dir /path/to/reviewed-reference --output /path/to/new-output \
 --saved-exposure /path/to/frozen-exposure-problem.json \
 --saved-ideal /path/to/frozen-ideal-problem.json
```

The core driver validates input; clean solver subprocesses run the old/new HiGHS workers. It compares 122 acceptance/error cases, six serialized LP models and solver outputs/losses, and eight controller flows, ignoring only response IDs/timestamps/timing. The archived problems and model files are copied into the new output with a protocol before execution; no dashboard workspace, application job DB or live provider is used.

A separate pilot is available with `benchmark_decision_policies.py --differential <output> --solver-python <python> --output <new-output>`. It sets an explicit 60 s budget and repeats each of the two small archived workloads 30 times through the unchanged outer watchdog, including final response serialization. It does not include HTTP transport/service queue load or qualify arbitrary workloads. No new physics runs are needed to establish a metadata refactor's equivalence; native CIMA source/archives are checked unchanged.

[Report](../reports/DECISION-POLICIES-A4-20261024.md), [differential evidence](../reports/decision-policies/differential.json), [deadline pilot](../reports/decision-policies/deadline-pilot.json).

Rollback is a source revert/redeploy to A3, preserving every archived input/output and scenario. The stable tag remains unchanged. A5 schema/workspace migration remains NOT RUN: it needs a concrete demonstrated use case and explicit compatibility evidence, not merely a desire to rename existing fields. Future policies/domains still require reviewed semantics, solver/verifier constraints and domain qualification.
