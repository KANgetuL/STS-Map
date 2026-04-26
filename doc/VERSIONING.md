# STS Map Versioning and Migration Notes

## Version dimensions

The project exposes three version dimensions in payload and runtime:

- `schema_version`: serialized export contract version.
- `api_version`: generator API surface version.
- `rule_version`: generation rule-set version for reproducibility.

## Recommended strategy

- `schema_version` follows semantic versioning:
  - MAJOR: breaking JSON contract changes.
  - MINOR: additive, backward-compatible fields.
  - PATCH: non-contract fixes/documentation.
- `api_version` follows semantic versioning for Python entrypoints.
- `rule_version` is mandatory per generation request and should be tracked in all downstream artifacts.

## Migration checklist

1. Before upgrading, compare current and target `schema_version`.
2. If MAJOR changed, update consumer parser and compatibility tests first.
3. Regenerate baseline snapshots after any `rule_version` behavior change.
4. Keep old snapshots for at least one release cycle for diff analysis.

## Consumer guidance

- Parse only required fields and ignore unknown keys.
- Fail fast when required top-level keys are missing.
- Store `schema_version` and `rule_version` with every persisted map for traceability.
