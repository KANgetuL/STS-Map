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
