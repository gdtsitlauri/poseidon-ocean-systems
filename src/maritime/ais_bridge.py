from __future__ import annotations

import ctypes
import shutil
import subprocess
from pathlib import Path


LIB_PATH = Path("src/maritime/libais_bridge.so")


def try_build_pascal_shared_lib() -> str:
    if LIB_PATH.exists():
        try:
            LIB_PATH.unlink()
        except OSError:
            pass
    fpc = shutil.which("fpc")
    pascal_src = Path("src/maritime/ais_bridge.pas")
    if fpc and pascal_src.exists():
        cmd = [fpc, "-B", "-Cg", "-XS", f"-FE{pascal_src.parent}", f"-FU{pascal_src.parent}", str(pascal_src)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if LIB_PATH.exists() and LIB_PATH.stat().st_size > 0:
                return "pascal_bridge_ok"
        except Exception:
            pass
    gcc = shutil.which("gcc")
    src = Path("src/maritime/bridge_stub.c")
    if not gcc:
        return "gcc_missing" if not fpc else "pascal_bridge_build_failed"
    if not src.exists():
        return "bridge_src_missing"
    cmd = [gcc, "-shared", "-fPIC", str(src), "-o", str(LIB_PATH)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except Exception:
        return "c_bridge_build_failed"
    if LIB_PATH.exists() and LIB_PATH.stat().st_size > 0:
        return "c_bridge_ok"
    return "c_bridge_build_failed"


def bridge_score(speed_kn: float, sea_state: int) -> float:
    if not LIB_PATH.exists():
        return speed_kn * (1.0 + 0.05 * sea_state)
    try:
        lib = ctypes.CDLL(str(LIB_PATH.resolve()))
    except OSError:
        return speed_kn * (1.0 + 0.05 * sea_state)
    lib.bridge_score.argtypes = [ctypes.c_double, ctypes.c_int]
    lib.bridge_score.restype = ctypes.c_double
    return float(lib.bridge_score(float(speed_kn), int(sea_state)))
