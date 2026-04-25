# STS Map Roadmap

## Goal
Build a reproducible, rule-driven, and extensible STS map generator with testable topology, room allocation, and runtime random-room resolution.

## Timeline and Milestones

## Current Progress
- Phase 0: completed
- Phase 1: completed
- Phase 2: completed
- Phase 3: completed
- Phase 4: completed
- Phase 5: in progress (distribution thresholds configurable and snapshot baseline tests added)

### Phase 0 - Environment and Baseline (Week 1)
- Scope:
  - Standardize local setup with conda and dependency files.
  - Keep project skeleton importable and runnable.
- Deliverables:
  - `.gitignore`, `environment.yml`, `requirements.txt`, `requirements-dev.txt`.
  - CI-ready local commands (`pytest`, `ruff`, `mypy`).
- Acceptance:
  - New contributor can run setup in <= 10 minutes.
  - Lint/type/test commands execute without environment errors.

### Phase 1 - Topology Core (Week 2-3)
- Scope:
  - Implement layered graph generation and path constraints.
  - Enforce adjacency, load limits, and non-intersection.
- Deliverables:
  - `TopologyBuilder.build` and structural helper methods.
  - Deterministic generation by seed.
- Acceptance:
  - 500 generated maps contain 0 invalid edges.
  - All maps are connected from floor 0 to boss floor.

### Phase 2 - Room Allocation Rules (Week 4)
- Scope:
  - Implement weighted room assignment.
  - Apply blacklist floors, consecutive constraints, forced floors, and minimum guarantees.
- Deliverables:
  - `RoomAllocator.allocate` full flow.
  - Repair pass for minimum shop and elite count.
- Acceptance:
  - Floor 14 always Rest and floor 15 always Boss.
  - Per-act minimum shop/elite guarantees are always met.

### Phase 3 - Random Room Runtime Logic (Week 5)
- Scope:
  - Implement random-room internal resolution with pity accumulation and reset.
- Deliverables:
  - `RandomRoomResolver.resolve` and state transitions.
- Acceptance:
  - Weight evolution matches documented rules for consecutive event hits.
  - Reset behavior is correct after special-room hit.

### Phase 4 - Act Specific Rules (Week 6)
- Scope:
  - Implement Act1/Act2 special elite chain.
  - Implement fixed Act4 map template.
- Deliverables:
  - `RuleEngine` concrete act logic.
- Acceptance:
  - Act4 always outputs fixed 4-floor linear map.
  - Act1/Act2 special elite persistence behaves as specified.

### Phase 5 - Validator and Regression Suite (Week 7)
- Scope:
  - Complete structure/rule/distribution/reproducibility validators.
  - Add snapshot and property-style tests.
- Deliverables:
  - `MapValidator` full checks.
  - Test assets for multi-seed runs.
- Acceptance:
  - Invalid map ratio is 0 across baseline seeds.
  - Same seed + same rule version gives byte-identical output.

### Phase 6 - Public API and Serialization (Week 8)
- Scope:
  - Stabilize external API and JSON output schema.
  - Document versioning strategy and migration notes.
- Deliverables:
  - Production-ready `generate_map` API.
  - JSON schema examples in docs.
- Acceptance:
  - Simulator can consume exported maps without adapter changes.
  - Rule version changes are traceable and documented.

## Workstream Backlog

## A. Engineering Quality
- Add pre-commit hooks for lint/type/test.
- Add CI workflow for Windows/Linux matrix.

## B. Data and Balancing
- Add distribution dashboards for room frequency.
- Track ascension impact metrics over 1,000+ seeds.

## C. Extensibility
- Introduce plugin hook points for modded acts and room types.
- Add compatibility contract for future rule modules.

## Risks and Mitigations
- Risk: Rule interpretation drift across modules.
  - Mitigation: Keep `rule_version` mandatory and validate at entrypoint.
- Risk: Statistical behavior deviates after refactor.
  - Mitigation: Add fixed-seed regression snapshots in CI.
- Risk: Runtime state bugs in random-room pity logic.
  - Mitigation: Add scenario-based tests for multi-step transitions.

## Definition of Done (Project)
- All phase acceptance checks pass.
- API, data model, and validation reports are documented.
- New contributor can setup, run tests, and generate a map in one session.
