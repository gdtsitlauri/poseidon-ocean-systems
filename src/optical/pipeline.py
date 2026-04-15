from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

import networkx as nx
import pandas as pd

from src.common import RESULT_FILES, ensure_dirs


def erlang_b(a: float, m: int) -> float:
    b = 1.0
    for i in range(1, m + 1):
        b = (a * b) / (i + a * b)
    return b


def wavelength_assignment_first_fit(graph: nx.Graph, max_wavelengths: int = 8) -> list[dict]:
    assignments = []
    used = {}
    for u, v in graph.edges():
        for w in range(max_wavelengths):
            if used.get((u, w), False) or used.get((v, w), False):
                continue
            used[(u, w)] = True
            used[(v, w)] = True
            assignments.append({"u": u, "v": v, "wavelength": w})
            break
    return assignments


def least_loaded_path(graph: nx.Graph, source: str, target: str, edge_load: dict[tuple[str, str], float]) -> list[str]:
    g = graph.copy()
    for u, v in g.edges():
        key = tuple(sorted((u, v)))
        g[u][v]["weight"] = 1.0 + edge_load.get(key, 0.0)
    return nx.shortest_path(g, source=source, target=target, weight="weight")


def rwa_assign_demands(graph: nx.Graph, demands: list[tuple[str, str]], max_wavelengths: int = 8) -> pd.DataFrame:
    rows = []
    edge_load: dict[tuple[str, str], float] = defaultdict(float)
    edge_wavelength_use: dict[tuple[str, str], set[int]] = defaultdict(set)
    for src, dst in demands:
        path = least_loaded_path(graph, src, dst, edge_load)
        assigned = None
        for w in range(max_wavelengths):
            feasible = True
            for a, b in zip(path[:-1], path[1:]):
                edge = tuple(sorted((a, b)))
                if w in edge_wavelength_use[edge]:
                    feasible = False
                    break
            if feasible:
                assigned = w
                for a, b in zip(path[:-1], path[1:]):
                    edge = tuple(sorted((a, b)))
                    edge_wavelength_use[edge].add(w)
                    edge_load[edge] += 1.0
                break
        rows.append({"src": src, "dst": dst, "path": "->".join(path), "wavelength": -1 if assigned is None else assigned, "blocked": assigned is None})
    return pd.DataFrame(rows)


def run_ghdl_if_available() -> str:
    if not shutil.which("ghdl"):
        return "ghdl_not_available"
    switch_vhd = Path("src/optical/optical_switch.vhd").resolve()
    tb_vhd = Path("src/optical/optical_switch_tb.vhd").resolve()
    cmds = [
        ["ghdl", "-a", str(switch_vhd)],
        ["ghdl", "-a", str(tb_vhd)],
        ["ghdl", "-e", "optical_switch_tb"],
        ["ghdl", "-r", "optical_switch_tb", "--stop-time=50ns"],
    ]
    try:
        with tempfile.TemporaryDirectory(prefix="poseidon_ghdl_") as tmp_dir:
            workdir = Path(tmp_dir)
            for cmd in cmds:
                subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=workdir)
    except Exception:
        return "ghdl_run_failed"
    return "ghdl_ok"


def rwa_ilp_maximization(graph: nx.Graph, demands: list[tuple[str, str]], channels: int) -> tuple[float, str]:
    try:
        import cvxpy as cp

        if not demands:
            return 0.0, "ilp_ok"
        paths = [nx.shortest_path(graph, s, t) for s, t in demands]
        edges = [tuple(sorted(e)) for e in graph.edges()]
        edge_to_idx = {e: i for i, e in enumerate(edges)}
        x = cp.Variable((len(demands), channels), boolean=True)
        y = cp.Variable(len(demands), boolean=True)
        constraints = []
        for d in range(len(demands)):
            constraints.append(cp.sum(x[d, :]) == y[d])
        for e_idx, edge in enumerate(edges):
            for w in range(channels):
                usage_terms = []
                for d_idx, path in enumerate(paths):
                    for a, b in zip(path[:-1], path[1:]):
                        if tuple(sorted((a, b))) == edge:
                            usage_terms.append(x[d_idx, w])
                            break
                if usage_terms:
                    constraints.append(cp.sum(cp.hstack(usage_terms)) <= 1)
        constraints.append(cp.sum(y) <= channels)
        objective = cp.Maximize(cp.sum(y))
        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.ECOS_BB, verbose=False)
        return float(prob.value or 0.0), "ilp_rwa_ok"
    except Exception:
        return float(min(len(demands), channels)), "ilp_rwa_fallback"


def run() -> None:
    ensure_dirs(
        [
            RESULT_FILES["optical_wavelength"],
            RESULT_FILES["optical_network"],
            RESULT_FILES["optical_failure"],
        ]
    )
    g = nx.Graph()
    g.add_edges_from(
        [("NYC", "Lisbon"), ("Lisbon", "Dakar"), ("Dakar", "Rio"), ("NYC", "London"), ("London", "Lisbon"), ("Rio", "Dakar")]
    )
    demands = [("NYC", "Dakar"), ("NYC", "Rio"), ("London", "Dakar"), ("Lisbon", "Rio"), ("NYC", "Lisbon")]
    rwa = rwa_assign_demands(g, demands, max_wavelengths=8)
    rwa.to_csv(RESULT_FILES["optical_wavelength"], index=False)

    offered = 12.0
    channels = 16
    blocking = erlang_b(offered, channels)
    ilp_served, ilp_status = rwa_ilp_maximization(g, demands=demands, channels=channels)
    analysis = pd.DataFrame(
        [
            {"offered_traffic_erlang": offered, "channels": channels, "blocking_probability": blocking, "scheme": "ErlangB"},
            {"offered_traffic_erlang": offered, "channels": channels, "blocking_probability": float(rwa["blocked"].mean()), "scheme": "RWA_simulated"},
            {"offered_traffic_erlang": offered, "channels": channels, "blocking_probability": 1.0 - (ilp_served / max(1, len(demands))), "scheme": ilp_status},
        ]
    )
    analysis.to_csv(RESULT_FILES["optical_network"], index=False)

    g2 = g.copy()
    g2.remove_edge("NYC", "Lisbon")
    recoverable = nx.has_path(g2, "NYC", "Dakar")
    hops = len(nx.shortest_path(g2, "NYC", "Dakar")) - 1 if recoverable else -1
    pd.DataFrame(
        [
            {"failure_edge": "NYC-Lisbon", "recoverable": recoverable, "reroute_hops": hops},
            {"vhdl_status": run_ghdl_if_available(), "recoverable": True, "reroute_hops": 0},
        ]
    ).to_csv(RESULT_FILES["optical_failure"], index=False)

    _ = math.log(10)
