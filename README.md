# POSEIDON

**Author:** George David Tsitlauri  
**Affiliation:** Dept. of Informatics & Telecommunications, University of Thessaly, Greece  
**Contact:** gdtsitlauri@gmail.com  
**Year:** 2026

Platform for Ocean Surveillance, Engineering Intelligence, and Digital Optical Networks.

POSEIDON is a multi-language research framework combining:
- Maritime informatics (Pascal + Python)
- GIS analytics (Python)
- CAD algorithms (C++ + Python)
- Optical networks (VHDL + Python)
- Unified optimization via POSEIDON-TRIDENT

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

## Citation

```bibtex
@misc{tsitlauri2026poseidon,
  author = {George David Tsitlauri},
  title  = {POSEIDON: A Multi-Language Research Framework for Maritime Analytics, GIS, CAD, and Optical Network Optimization},
  year   = {2026},
  institution = {University of Thessaly},
  email  = {gdtsitlauri@gmail.com}
}
```
