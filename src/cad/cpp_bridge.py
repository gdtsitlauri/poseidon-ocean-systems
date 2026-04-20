from __future__ import annotations

import ctypes
import shutil
import subprocess
from pathlib import Path


LIB_PATH = Path("src/cad/libposeidon_cad.so")


def try_build_cpp_shared_lib() -> str:
    gpp = shutil.which("g++")
    if not gpp:
        return "gpp_missing"
    src = Path("src/cad/geometry.cpp")
    if not src.exists():
        return "cpp_src_missing"
    cmd = [gpp, "-std=c++17", "-shared", "-fPIC", str(src), "-o", str(LIB_PATH)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except Exception:
        return "cpp_build_failed"
    return "cpp_ok"


def _load_lib() -> ctypes.CDLL | None:
    if not LIB_PATH.exists():
        return None
    return ctypes.CDLL(str(LIB_PATH.resolve()))


def cpp_bezier_linear(p0: float, p1: float, t: float) -> float:
    lib = _load_lib()
    if lib is None:
        return (1.0 - t) * p0 + t * p1
    lib.bezier_linear.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.bezier_linear.restype = ctypes.c_double
    return float(lib.bezier_linear(float(p0), float(p1), float(t)))


def cpp_nurbs_weighted_point(p0: float, p1: float, w0: float, w1: float, t: float) -> float:
    lib = _load_lib()
    if lib is None:
        b0 = 1.0 - t
        b1 = t
        denom = max(1e-12, b0 * w0 + b1 * w1)
        return (b0 * w0 * p0 + b1 * w1 * p1) / denom
    lib.nurbs_weighted_point.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.nurbs_weighted_point.restype = ctypes.c_double
    return float(lib.nurbs_weighted_point(float(p0), float(p1), float(w0), float(w1), float(t)))


def cpp_moeller_trumbore_hit(oz: float, dz: float, tri_z: float) -> float:
    lib = _load_lib()
    if lib is None:
        if abs(dz) < 1e-12:
            return -1.0
        return (tri_z - oz) / dz
    lib.moeller_trumbore_hit.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
    lib.moeller_trumbore_hit.restype = ctypes.c_double
    return float(lib.moeller_trumbore_hit(float(oz), float(dz), float(tri_z)))
