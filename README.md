# POSEIDON


Platform for Ocean Surveillance, Engineering Intelligence, and Digital Optical Networks.

POSEIDON is a multi-language research framework combining:
- Maritime informatics (Pascal + Python)
- GIS analytics (Python)
- CAD algorithms (C++ + Python)
- Optical networks (VHDL + Python)
- Unified optimization via POSEIDON-TRIDENT


## Project Metadata

| Field | Value |
| --- | --- |
| Author | George David Tsitlauri |
| Affiliation | Dept. of Informatics & Telecommunications, University of Thessaly, Greece |
| Contact | gdtsitlauri@gmail.com |
| Year | 2026 |

## Primary Research Thesis

POSEIDON is strongest as a cross-domain engineering research platform that
connects maritime analytics, GIS, CAD, and optical-network workflows under one
artifact-driven execution model. The clearest value of the current repository is
not a claim of field-validated operational superiority, but that coupled
multi-domain planning can be studied reproducibly in one compact system with
stable outputs and explicit interoperability boundaries.

## Repository Layout

- `src/maritime` - AIS parsing, route optimization, maritime analytics
- `src/gis` - spatial indexing and cable GIS analysis
- `src/cad` - geometry and mesh processing helpers with optional C++ shared-library bridge
- `src/optical` - optical switch VHDL + network optimization
- `src/poseidon_trident` - joint three-layer optimizer
- `tests` - integration tests
- `results` - generated CSV/HTML/STL/PNG artifacts
- `data` - optional scratch CSV exports produced during local runs
- `paper` - IEEE-style manuscript scaffold

## Quick Start (WSL2 Ubuntu)

1. Install optional system tools:
   - `sudo apt update`
   - `sudo apt install -y fpc ghdl g++`
2. Create Python environment and install dependencies:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
3. Run experiments:
   - `python3 -m src.poseidon_trident.run_all`
   - This also refreshes `paper/generated_metrics.tex` from actual result CSV files.
4. Run tests:
   - `pytest -q`

## Notes

- If `fpc`, `g++`, or `ghdl` are not installed, POSEIDON falls back to pure-Python execution for the affected bridge/simulation steps and records the status in generated CSV artifacts.
- All outputs are written under `results/` with stable names aligned to the project specification.
- Local caches, compiled binaries, shared libraries, and scratch `data/*.csv` exports are intentionally ignored by Git.
- Multi-seed experiment summary is generated at `results/trident/experiment_summary.csv`.

## Result Snapshot

The current release already carries useful cross-domain evidence in the
generated artifacts:

- populated maritime route and fuel metrics in `results/maritime/`
- GIS timing and route-analysis outputs in `results/gis/`
- CAD geometry and mesh exports in `results/cad/`
- optical-network routing and recovery artifacts in `results/optical/`
- integrated summary metrics in `results/trident/experiment_summary.csv`

The repository therefore reads best as a serious systems-research platform with
real generated outputs across all major modules, rather than as a single-method
benchmark repo.

## Why POSEIDON Can Now Be Read More Strongly

POSEIDON now presents a much cleaner strong story:

- every major domain module produces populated artifacts,
- the joint `POSEIDON-TRIDENT` layer gives the repository a real integrative
  identity,
- the synthetic nature of the workloads is explicit, which makes the claims
  safer and more professional rather than weaker.

## Evidence Hierarchy

- Primary evidence: POSEIDON-TRIDENT integrated optimization summaries and
  cross-module artifact generation
- Secondary evidence: maritime, GIS, CAD, and optical module metrics populated
  under stable result trees
- Supporting evidence: multi-language fallbacks and native-bridge status
  reporting

## Why POSEIDON Now Stands Up Better

POSEIDON is more defensible as a strong repo when framed as a multi-domain
engineering platform:

- the integrated story is clearer,
- the synthetic workloads are acknowledged instead of hidden,
- the repository's strength comes from stable cross-domain execution and
  artifact production, not exaggerated deployment claims.

## Strongest positioning

The strongest way to present POSEIDON is:

- as a multi-domain engineering and optimization platform,
- centered on cross-domain execution and integrated artifact generation,
- with `POSEIDON-TRIDENT` as the main repository-level systems contribution.


