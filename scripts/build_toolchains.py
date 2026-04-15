from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class ToolchainStatus:
    name: str
    available: bool
    details: str


def check_fpc() -> ToolchainStatus:
    if not shutil.which("fpc"):
        return ToolchainStatus("fpc", False, "fpc not installed")
    proc = subprocess.run(["fpc", "-h"], capture_output=True, text=True)
    return ToolchainStatus("fpc", proc.returncode == 0, "fpc help command")


def check_ghdl() -> ToolchainStatus:
    if not shutil.which("ghdl"):
        return ToolchainStatus("ghdl", False, "ghdl not installed")
    proc = subprocess.run(["ghdl", "--version"], capture_output=True, text=True)
    return ToolchainStatus("ghdl", proc.returncode == 0, "ghdl version command")


def check_gpp() -> ToolchainStatus:
    if not shutil.which("g++"):
        return ToolchainStatus("g++", False, "g++ not installed")
    proc = subprocess.run(["g++", "--version"], capture_output=True, text=True)
    return ToolchainStatus("g++", proc.returncode == 0, "g++ version command")


def main() -> None:
    statuses = [check_fpc(), check_ghdl(), check_gpp()]
    for st in statuses:
        state = "OK" if st.available else "MISSING"
        print(f"{st.name}: {state} ({st.details})")


if __name__ == "__main__":
    main()
