# STS Map

Python skeleton for Slay the Spire map generation.

## Conda Environment Setup (Windows PowerShell)

1. Create environment from file:

   ```powershell
   conda env create -f environment.yml
   ```

2. Activate environment:

   ```powershell
   conda activate sts-map
   ```

3. If dependencies changed, update environment:

   ```powershell
   conda env update -f environment.yml --prune
   ```

4. Quick sanity checks:

   ```powershell
   python -m pytest -q
   ruff check .
   mypy sts_map
   ```

## Package Layout

- `sts_map/domain`: enums, core models, runtime state
- `sts_map/config`: config schema
- `sts_map/generator`: topology and room generation pipeline
- `sts_map/rules`: act specific rules
- `sts_map/validators`: map validation
- `sts_map/io`: serialization helpers
- `sts_map/api`: public entrypoint

## Public API (Phase 6)

```python
from sts_map.api import generate_map, generate_map_payload, generate_map_json
from sts_map.domain.enums import ActId
from sts_map.domain.models import GenerationInput

input_data = GenerationInput(act_id=ActId.ACT1, ascension=10, seed=42, rule_version="0.6.0")

graph = generate_map(input_data)
payload = generate_map_payload(input_data)
payload_json = generate_map_json(input_data)
```

- JSON schema reference: [doc/JSON_SCHEMA.md](doc/JSON_SCHEMA.md)
- Versioning and migration: [doc/VERSIONING.md](doc/VERSIONING.md)
