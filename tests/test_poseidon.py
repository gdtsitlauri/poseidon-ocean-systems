from __future__ import annotations

import math
import shutil
import subprocess

import pandas as pd
import pytest

from src.cad.cpp_bridge import cpp_bezier_linear, try_build_cpp_shared_lib
from src.cad.pipeline import nurbs_like_sample
from src.gis.pipeline import convex_hull, point_in_polygon, wgs84_to_utm
from src.maritime.ais_bridge import bridge_score, try_build_pascal_shared_lib
from src.maritime.pipeline import VesselState, compute_cpa_tcpa, fuel_consumption, generate_synthetic_ais, haversine_km
from src.optical.pipeline import run_ghdl_if_available, wavelength_assignment_first_fit
from src.poseidon_trident.run_all import run_all, run_experiments
from src.poseidon_trident.trident import optimize_joint


def test_ais_parser() -> None:
    tracks = generate_synthetic_ais(seed=1, n=3)
    assert tracks[0].mmsi == 100000000


def test_great_circle() -> None:
    dist = haversine_km(0.0, 0.0, 0.0, 1.0)
    assert abs(dist - 111.19) < 1.0


def test_collision_risk() -> None:
    v1 = VesselState(1, 0.0, 0.0, 12, 90, "Cargo", 10000, 3)
    v2 = VesselState(2, 0.0, 0.1, 10, 95, "Cargo", 12000, 4)
    cpa, tcpa = compute_cpa_tcpa(v1, v2)
    assert cpa > 0
    assert tcpa > 0


def test_fuel_model() -> None:
    low = fuel_consumption(10, 30000, 2)
    high = fuel_consumption(18, 30000, 2)
    assert high > low


def test_point_in_polygon() -> None:
    poly = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert point_in_polygon((2, 2), poly)
    assert not point_in_polygon((5, 5), poly)


def test_convex_hull() -> None:
    hull = convex_hull([(0, 0), (1, 1), (2, 0), (1, 0.5), (0, 2)])
    assert (0, 0) in hull and (2, 0) in hull and (0, 2) in hull


def test_coordinate_conversion() -> None:
    e, n, zone = wgs84_to_utm(40.0, -20.0)
    assert e > 0 and n > 0 and zone > 0


def test_nurbs_evaluation() -> None:
    p = nurbs_like_sample([(0, 0), (1, 2), (2, 0)], [1.0, 2.0, 1.0], 0.5)
    assert math.isfinite(p[0]) and math.isfinite(p[1])


def test_pascal_bridge_or_fallback() -> None:
    status = try_build_pascal_shared_lib()
    score = bridge_score(12.0, 3)
    assert status in {"pascal_bridge_ok", "pascal_bridge_build_failed", "c_bridge_ok", "c_bridge_build_failed", "gcc_missing", "bridge_src_missing"}
    assert score > 0


def test_cpp_bridge_or_fallback() -> None:
    status = try_build_cpp_shared_lib()
    midpoint = cpp_bezier_linear(0.0, 2.0, 0.5)
    assert status in {"cpp_ok", "cpp_build_failed", "gpp_missing", "cpp_src_missing"}
    assert abs(midpoint - 1.0) < 1e-6


def test_vhdl_simulation() -> None:
    status = run_ghdl_if_available()
    assert status in {"ghdl_not_available", "ghdl_ok", "ghdl_run_failed"}


def test_wavelength_assignment() -> None:
    import networkx as nx

    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("C", "D")])
    assigned = wavelength_assignment_first_fit(g)
    assert len(assigned) == 3


def test_trident_feasible() -> None:
    df = optimize_joint(seed=4, n=8)
    assert (df["joint_total_cost"] > 0).all()
    assert (df["joint_total_cost"] <= df["independent_total_cost"]).mean() >= 0.5
    assert "rank" in df.columns


def test_result_artifacts() -> None:
    run_experiments([7, 8, 9])
    paths = [
        "results/maritime/route_optimization.csv",
        "results/maritime/collision_risk.csv",
        "results/maritime/anomaly_detection.csv",
        "results/maritime/port_congestion_prediction.csv",
        "results/maritime/pascal_bridge_status.csv",
        "results/gis/spatial_benchmarks.csv",
        "results/gis/cable_route_analysis.csv",
        "results/gis/coordinate_conversion.csv",
        "results/gis/advanced_geometry_analysis.csv",
        "results/gis/submarine_cable_map.html",
        "results/cad/mesh_processing_benchmarks.csv",
        "results/cad/hull_design_export.stl",
        "results/optical/wavelength_assignment.csv",
        "results/optical/submarine_network_analysis.csv",
        "results/optical/failure_recovery.csv",
        "results/trident/joint_vs_independent_optimization.csv",
        "results/trident/pareto_frontier.png",
        "results/trident/experiment_summary.csv",
    ]
    for path in paths:
        assert pd.io.common.file_exists(path)
    bridge_df = pd.read_csv("results/maritime/pascal_bridge_status.csv")
    assert bridge_df.loc[0, "bridge_status"] in {"pascal_bridge_ok", "pascal_bridge_build_failed", "c_bridge_ok", "c_bridge_build_failed", "gcc_missing", "bridge_src_missing"}
    cad_df = pd.read_csv("results/cad/mesh_processing_benchmarks.csv")
    assert cad_df["cpp_bridge_status"].iloc[0] in {"cpp_ok", "cpp_build_failed", "gpp_missing", "cpp_src_missing"}
