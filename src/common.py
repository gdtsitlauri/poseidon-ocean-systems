from __future__ import annotations

from pathlib import Path
from typing import Iterable


RESULT_FILES = {
    "maritime_route": "results/maritime/route_optimization.csv",
    "maritime_collision": "results/maritime/collision_risk.csv",
    "maritime_anomaly": "results/maritime/anomaly_detection.csv",
    "gis_benchmarks": "results/gis/spatial_benchmarks.csv",
    "gis_cable": "results/gis/cable_route_analysis.csv",
    "gis_map": "results/gis/submarine_cable_map.html",
    "cad_benchmarks": "results/cad/mesh_processing_benchmarks.csv",
    "cad_stl": "results/cad/hull_design_export.stl",
    "optical_wavelength": "results/optical/wavelength_assignment.csv",
    "optical_network": "results/optical/submarine_network_analysis.csv",
    "optical_failure": "results/optical/failure_recovery.csv",
    "trident_joint": "results/trident/joint_vs_independent_optimization.csv",
    "trident_pareto": "results/trident/pareto_frontier.png",
}


def ensure_dirs(paths: Iterable[str]) -> None:
    for rel in paths:
        Path(rel).parent.mkdir(parents=True, exist_ok=True)
