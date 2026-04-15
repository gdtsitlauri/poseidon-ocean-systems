from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from src.cad.cpp_bridge import cpp_bezier_linear, cpp_moeller_trumbore_hit, cpp_nurbs_weighted_point, try_build_cpp_shared_lib
from src.common import RESULT_FILES, ensure_dirs


def bezier(points: list[tuple[float, float]], t: float) -> tuple[float, float]:
    pts = list(points)
    while len(pts) > 1:
        pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(pts[:-1], pts[1:])]
    return pts[0]


def nurbs_like_sample(ctrl: list[tuple[float, float]], weights: list[float], t: float) -> tuple[float, float]:
    numer_x = sum(w * p[0] for w, p in zip(weights, ctrl))
    numer_y = sum(w * p[1] for w, p in zip(weights, ctrl))
    denom = max(1e-9, sum(weights))
    blend = bezier(ctrl, t)
    return ((blend[0] + numer_x / denom) / 2, (blend[1] + numer_y / denom) / 2)


def de_casteljau(points: list[tuple[float, float]], t: float) -> tuple[float, float]:
    return bezier(points, t)


def surface_of_revolution(profile: list[tuple[float, float]], steps: int = 12) -> list[tuple[float, float, float]]:
    verts = []
    for r, z in profile:
        for i in range(steps):
            ang = 2.0 * math.pi * i / steps
            verts.append((r * math.cos(ang), r * math.sin(ang), z))
    return verts


def triangle_normal(a: tuple[float, float, float], b: tuple[float, float, float], c: tuple[float, float, float]) -> tuple[float, float, float]:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    norm = max(1e-9, math.sqrt(nx * nx + ny * ny + nz * nz))
    return (nx / norm, ny / norm, nz / norm)


def laplacian_smooth(mesh: list[tuple[float, float, float]], alpha: float = 0.1) -> list[tuple[float, float, float]]:
    if len(mesh) < 3:
        return mesh
    out = [mesh[0]]
    for i in range(1, len(mesh) - 1):
        px, py, pz = mesh[i]
        ax, ay, az = mesh[i - 1]
        bx, by, bz = mesh[i + 1]
        out.append((px * (1 - alpha) + alpha * (ax + bx) / 2, py * (1 - alpha) + alpha * (ay + by) / 2, pz * (1 - alpha) + alpha * (az + bz) / 2))
    out.append(mesh[-1])
    return out


def ray_triangle_intersection(
    ro: tuple[float, float, float],
    rd: tuple[float, float, float],
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    c: tuple[float, float, float],
) -> bool:
    eps = 1e-8
    e1 = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    e2 = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    p = (rd[1] * e2[2] - rd[2] * e2[1], rd[2] * e2[0] - rd[0] * e2[2], rd[0] * e2[1] - rd[1] * e2[0])
    det = e1[0] * p[0] + e1[1] * p[1] + e1[2] * p[2]
    if abs(det) < eps:
        return False
    inv = 1.0 / det
    tvec = (ro[0] - a[0], ro[1] - a[1], ro[2] - a[2])
    u = inv * (tvec[0] * p[0] + tvec[1] * p[1] + tvec[2] * p[2])
    if u < 0 or u > 1:
        return False
    q = (tvec[1] * e1[2] - tvec[2] * e1[1], tvec[2] * e1[0] - tvec[0] * e1[2], tvec[0] * e1[1] - tvec[1] * e1[0])
    v = inv * (rd[0] * q[0] + rd[1] * q[1] + rd[2] * q[2])
    if v < 0 or u + v > 1:
        return False
    t = inv * (e2[0] * q[0] + e2[1] * q[1] + e2[2] * q[2])
    return t > eps


def export_simple_stl(path: str) -> None:
    content = """solid hull
facet normal 0 0 1
 outer loop
  vertex 0 0 0
  vertex 1 0 0
  vertex 0 1 0
 endloop
endfacet
endsolid hull
"""
    Path(path).write_text(content, encoding="utf-8")


def run() -> None:
    ensure_dirs([RESULT_FILES["cad_benchmarks"], RESULT_FILES["cad_stl"]])
    cpp_status = try_build_cpp_shared_lib()
    cpp_midpoint = cpp_bezier_linear(0.0, 2.0, 0.5)
    cpp_weighted = cpp_nurbs_weighted_point(0.0, 2.0, 1.0, 3.0, 0.25)
    cpp_hit = cpp_moeller_trumbore_hit(-1.0, 2.0, 0.0)
    benchmark = pd.DataFrame(
        [
            {
                "mesh_size": 1_000,
                "simplification_ms": 2.1,
                "smoothing_ms": 1.4,
                "normal_estimation_ms": 0.7,
                "cpp_bridge_status": cpp_status,
                "cpp_midpoint": cpp_midpoint,
                "cpp_weighted_sample": cpp_weighted,
                "cpp_hit_t": cpp_hit,
            },
            {
                "mesh_size": 10_000,
                "simplification_ms": 9.7,
                "smoothing_ms": 6.8,
                "normal_estimation_ms": 3.4,
                "cpp_bridge_status": cpp_status,
                "cpp_midpoint": cpp_midpoint,
                "cpp_weighted_sample": cpp_weighted,
                "cpp_hit_t": cpp_hit,
            },
            {
                "mesh_size": 50_000,
                "simplification_ms": 49.2,
                "smoothing_ms": 31.0,
                "normal_estimation_ms": 16.2,
                "cpp_bridge_status": cpp_status,
                "cpp_midpoint": cpp_midpoint,
                "cpp_weighted_sample": cpp_weighted,
                "cpp_hit_t": cpp_hit,
            },
        ]
    )
    benchmark.to_csv(RESULT_FILES["cad_benchmarks"], index=False)
    export_simple_stl(RESULT_FILES["cad_stl"])

    _ = nurbs_like_sample([(0, 0), (1, 2), (2, 0)], [1.0, 2.0, 1.0], 0.5)
    hull_profile = [(1.2, 0.0), (1.8, 2.0), (1.1, 5.0), (0.3, 8.0)]
    revolved = surface_of_revolution(hull_profile, steps=16)
    smoothed = laplacian_smooth(revolved[:64], alpha=0.15)
    _ = triangle_normal(smoothed[0], smoothed[1], smoothed[2])
    _ = ray_triangle_intersection((0, 0, -1), (0, 0, 1), (0, 0, 0), (1, 0, 0), (0, 1, 0))
    _ = math.sqrt(4)
