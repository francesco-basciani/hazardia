# CODEX TASK — HAZARDIA Domain-Agnostic Architecture Evolution

## ROLE

Act as a Principal Software Architect, Model-Driven Engineering Researcher, Geospatial Systems Engineer, and Performance Engineer.

You are working on the existing HAZARDIA repository.

Your task is to evolve HAZARDIA into a modular, domain-agnostic platform for spatial intelligence, simulation, and robust decision support.

**This is an architectural evolution of an existing research software system, not a greenfield project.**

Preserve existing functionality, scientific assumptions, performance requirements, and completed work.

## 1. MANDATORY INITIAL AUDIT

Before modifying any source code:

1. Read `AGENTS.md`, `README.md`, `SPEC.md`, `MEMORY.md`, and the existing checklist.
2. Inspect the repository structure, dependencies, tests, domain implementations, APIs, simulators, and decision-support components.
3. Reconstruct the actual implementation status and milestones.
4. Identify existing architectural abstractions that can be reused.
5. Identify domain-specific coupling, architectural limitations, duplication, and migration risks.
6. Distinguish existing functionality, partially implemented functionality, planned functionality, and functionality introduced by this task.

Do not assume that a feature exists merely because it is mentioned in documentation.

Do not delete, rewrite, or replace existing components without a documented technical justification.

## 2. ARCHITECTURAL OBJECTIVE

Evolve HAZARDIA into a platform that can support heterogeneous domains, including:

- Wildfires
- Floods
- Landslides
- Environmental pollution
- Critical infrastructure monitoring and degradation
- Other spatial, environmental, and infrastructure-related phenomena

Crime analysis is explicitly OUT OF SCOPE for the current development.

The architecture must not contain assumptions or hardcoded abstractions specific to crime analysis.

Existing wildfire and flood capabilities must remain supported.

## 3. TARGET ARCHITECTURE

Organize the logical architecture around the following capabilities.

### A. Spatio-Temporal Data and Knowledge Layer

Responsibilities:

- Heterogeneous data acquisition
- Earth observation and satellite data
- Sensor networks and telemetry
- Weather and environmental data
- Historical and open datasets
- Geospatial data normalization
- Temporal alignment
- Data quality assessment
- Provenance and traceability
- Missing and unreliable data handling
- Geospatial storage and retrieval

Define common interfaces without forcing every provider to expose identical native data structures.

Reuse existing connectors where possible.

### B. Domain Modeling and Intelligence Layer

Introduce explicit abstractions for:

- Domain
- Phenomenon
- Observation
- Event
- SpatialEntity
- InfrastructureAsset
- Indicator
- Hazard
- Exposure
- Vulnerability
- RiskEstimate
- Uncertainty
- Model
- Prediction
- Scenario
- Impact
- Resource
- Intervention
- Decision

Keep these concepts semantically distinct.

In particular:

- An observation is not necessarily an event.
- Hazard is not equivalent to risk.
- A susceptibility map is not necessarily a probability map.
- A prediction is not necessarily a physical simulation.
- An intervention is not necessarily an available or authorized action.
- Different domains may require different spatial and temporal semantics.

Provide extensible models, schemas, and validation constraints.

Every relevant data product should support explicit spatial reference, time reference, units, provenance, quality, and uncertainty metadata.

### C. Modeling, Forecasting, and Simulation Layer

Introduce or refine a pluggable model execution architecture supporting:

- Statistical models
- Spatial risk and susceptibility models
- Machine learning models
- Physics-based models
- Hybrid models
- Domain-specific simulators
- Scenario-based simulation
- Multi-scenario comparison
- Model composition

Preserve integration paths for existing CIMA-related wildfire and flood components.

Do not reimplement scientific simulators unnecessarily.

Clearly distinguish model configuration, model execution, simulator orchestration, and model validation.

Introduce explicit input/output contracts that describe:

- Semantic meaning
- Data types
- Physical units
- Spatial and temporal resolution
- Coordinate reference system
- Validity interval
- Required inputs
- Model assumptions
- Expected outputs
- Uncertainty representation
- Execution cost and resource requirements

Do not assume that models are compatible merely because their input/output types match.

### D. Decision Intelligence Layer

Preserve and generalize HAZARDIA's existing decision-support objectives:

- Resource allocation
- Preventive and reactive decisions
- Intervention-effect modeling
- Multi-region coordination
- Multi-scenario robustness
- Rolling-horizon optimization
- Solver-pluggable optimization
- Degradation-aware decision making
- Graceful degradation
- Explainability and decision traceability

Keep MILP/CP and other solver alternatives replaceable.

Ensure that domain-specific decision variables, constraints, objectives, and intervention effects can be introduced without changing the core optimization infrastructure.

Do not impose a universal optimization formulation on all domains.

### E. Operational Application Layer

Provide reusable capabilities for:

- Web-GIS visualization
- Domain-specific dashboards
- Event tracking
- Spatial and temporal analytics
- Alerts
- Scenario comparison
- Decision explanations
- Simulation monitoring
- External APIs

Maintain responsive interactions.

Avoid loading heavy datasets or executing expensive scientific computations synchronously in the UI request path.

## 4. DOMAIN PACKAGE ARCHITECTURE

Introduce a well-defined Domain Package concept.

A Domain Package should be able to declare:

- Domain identity and version
- Domain vocabulary and semantic definitions
- Supported phenomena
- Relevant spatial entities
- Data requirements
- Available data providers
- Indicators and risk factors
- Available analytical models
- Available simulators
- Model compatibility requirements
- Intervention types
- Resource types
- Optimization problem definitions
- Visualization capabilities
- Validation requirements

Design a registration and discovery mechanism.

Domain packages must be independently maintainable, testable, and replaceable.

A domain package must not require modifications to unrelated domain packages.

Existing wildfire and flood functionality should be migrated incrementally, without breaking compatibility.

## 5. INTEROPERABILITY

Design explicit integration contracts for externally developed domain systems.

A domain system may be:

1. An external service consumed through an API.
2. A simulator executed through an adapter.
3. A locally installed analytical component.
4. A complete subsystem providing multiple capabilities.
5. A domain package generated by an external Model-Driven Engineering framework.

Evaluate established standards where technically appropriate, including OGC SensorThings API, OGC API - Processes, and OpenMI.

Do not implement standards without demonstrated requirements.

The interface contracts must permit future externally generated domain systems to integrate without coupling them to HAZARDIA internals.

## 6. PERFORMANCE AND ROBUSTNESS

Preserve the established HAZARDIA non-functional requirements.

In particular:

- Efficient local execution
- Responsive user interface
- Modular execution
- Bounded resource consumption
- Asynchronous processing of expensive operations
- Incremental and cached computations where appropriate
- Explicit failure handling
- Rapid decision recomputation
- Rolling horizon
- Graceful degradation of data, models, simulators, infrastructure, and operational resources

The existing 60-second decision recomputation target remains a key requirement for its defined operational scenarios.

Do not claim this bound is guaranteed for arbitrary models or scenarios.

Introduce measurable performance budgets, benchmarks, and regression tests.

Prefer architectural simplicity over unnecessary microservices.

## 7. MIGRATION STRATEGY

Do not rewrite the system.

Develop an incremental architecture migration plan.

Classify components as:

- KEEP
- REFACTOR
- EXTEND
- REPLACE, only with justification
- DEFER

Reconstruct and protect the actual milestone state from PLAN.md and CHECKLIST.md. M0–M4 technical fixtures have evidence; later software slices exist, while scientific and research-release gates remain partially BLOCKED. Do not treat HAZARDIA as an ongoing M1-only project, reset milestones, or promote technical tests into physical or operational validation.

Use compatibility adapters and incremental refactoring where necessary.

Any change that affects existing functionality must include meaningful regression evidence. At minimum protect:
- Reading existing workspace versions and saved scenario configuration.
- Reading frozen historical requests/results without rewriting or reinterpreting them.
- Producing semantically identical CIMA inputs/forcing/actions for identical accepted inputs; exercise native equivalence when execution changes.
- Maintaining independent validation, UNKNOWN safety, timeout/degradation and human-authority checks.
- Maintaining monitoring/layer switches, IT/EN, map authoring, independent scenarios, shared scenario/weather time, pause/seek/recompute and comparison.
- Maintaining the bounded declared decision workload and its timing evidence separately from simulation latency.

Schema changes require new versions, declared compatibility and explicit opt-in migration; never migrate archived scientific evidence in place. Pin package/model/policy identity to historical executions. Matching a schema does not establish scientific interchangeability.

## 8. REQUIRED DOCUMENTATION

Update the existing project documentation rather than creating unnecessary duplicate files.

Update:

- `README.md`: architecture and development workflow
- `SPEC.md`: architectural requirements; preserve PLAN.md as the milestone authority
- `AGENTS.md`: engineering rules and agent responsibilities
- `PLAN.md`: migration dependencies and progress without rewriting historical gates
- `MEMORY.md`: architectural decisions and progress; use existing ADR practice for versioned decisions
- `research/EVIDENCE.md`: actual evidence and limits, following research/RESEARCH.md
- Existing checklist: traceable implementation and validation tasks

Create additional architecture documentation only where necessary.

Include:

- Architecture diagrams
- Component responsibilities
- Domain package contracts
- Data model and schema definitions
- Interface specifications
- Migration plan
- Design decisions and trade-offs
- Performance and validation strategy

Document assumptions and unresolved technical questions.

## 8A. BINDING CURRENT REQUIREMENTS AND SCOPE

Preserve the existing single Linux UTM VM for runtime, acquisition, preprocessing, API, jobs and scientific engines; the Mac remains development/display only. Free sources and local-first execution remain binding. No new privileged installation, large download, expense, public deployment or operational dispatch is authorised by this architectural task. Normal reviewed source updates to the already authorised GitHub repository remain subject to its curated publication procedure.

Preserve PROPAGATOR, HMC/Continuum and REFlEx, frozen inputs, scenario workspaces, API behaviour, independent scenario ignitions/resources/intervention geometry and activation times, weather-forcing provenance, timeline/pause/seek/recompute behaviour, optimised-plan comparison, independent verification, and capability-aware degradation. Preserve map-first responsive UI and Italian default / English switch. Latest UI clarification: all genuine map layers use uniform entries on the left; a selected layer opens its own settings pane on the RIGHT. The selected monitoring validity time, including future forecasts, must be explicit and distinct from current wall-clock time. Observed, forecast, simulated, missing and stale products remain distinguishable.

Landslides, pollution and other future domains are ARCHITECTURAL extension examples only. Do not implement new engines, risk calculations, datasets, dashboards or empty domain controls for them. Observed earthquakes, the power-network layer and hypothetical traffic retain their current separate roles; observed seismic events do not imply a seismic simulator, and traffic animation does not imply congestion/evacuation or automatic optimiser coupling.

Do not create twenty empty classes to mirror the vocabulary. Define semantics at the contract boundary and implement only concepts exercised by the agreed concrete increment. Domain registration must initially be a lightweight local description/lookup, not hot-loading arbitrary code, installing plugins from the network, or adding microservices.

## 9. IMPLEMENTATION STRATEGY

Proceed in two distinct stages.

### Stage 1 — Architecture and migration design

Perform the audit, specify the target architecture, define contracts, and document the migration strategy.

Update project documentation and checklists. Stage 1 delivers an audit and concrete reviewable migration design ONLY: implemented/proposed/deferred must be explicit. UI corrections expressly requested alongside this task may be completed separately, without claiming that the architecture migration is implemented.

Do not alter application schemas, dispatch, workspaces, solver policies, engine environments or scientific archives in Stage 1. Do not automatically proceed to Stage 2 merely because Stage 1 documentation is written. First expose its contracts, migration risks and the precisely bounded next executable increment for review.

### Stage 2 — Controlled implementation

Implement only compatible, independently testable architectural foundations that do not disrupt ongoing milestones.

Stage 2 proceeds as explicitly delimited increments. The first candidate increment is read-only local package descriptions for the EXISTING wildfire/flood capabilities plus discovery tests; it must not replace current dispatch or expose unqualified capabilities. Routing, contract migrations, domain-policy extraction and UI generalisation are later separate increments, each with regression evidence and rollback to the stable checkpoint.

For larger or potentially breaking modifications, document the dependency and defer them to the appropriate milestone.

Never mark a milestone complete unless its acceptance criteria have been tested.

## 10. SCIENTIFIC ENGINEERING REQUIREMENTS

The architecture must remain suitable for research on:

- Model-Driven Engineering
- Domain-specific system engineering
- Model and simulator composition
- Spatial intelligence
- Robust decision support
- Uncertainty propagation
- Graceful degradation
- Multi-domain validation

Keep research hypotheses separate from demonstrated results.

Preserve experiment reproducibility and traceability.

## 11. COMPLETION CRITERIA

At the end of the task provide:

1. Summary of existing architecture.
2. Identified architectural limitations.
3. Proposed target architecture.
4. Domain package specification.
5. Interoperability contracts.
6. Migration plan with milestone dependencies.
7. Documentation changes.
8. Implemented changes, if any.
9. Tests and benchmark results.
10. Remaining risks and pending work.

Clearly distinguish implemented, documented, proposed, and deferred functionality.

Never report unexecuted tests as passed.

**Primary objective: make HAZARDIA domain-agnostic without sacrificing the correctness, stability, performance, and scientific integrity of the existing system.**
