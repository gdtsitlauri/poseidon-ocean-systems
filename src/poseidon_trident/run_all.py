from __future__ import annotations

import pandas as pd
import subprocess

from src.cad.pipeline import run as run_cad
from src.gis.pipeline import run as run_gis
from src.maritime.pipeline import run as run_maritime
from src.optical.pipeline import run as run_optical
from src.poseidon_trident.trident import optimize_joint, run as run_trident


def run_all(seed: int = 42) -> None:
    run_maritime(seed=seed)
    run_gis(seed=seed)
    run_cad()
    run_optical()
    run_trident(seed=seed)


def run_experiments(seeds: list[int] | None = None) -> None:
    seeds = seeds or [11, 17, 23]
    all_rows = []
    for seed in seeds:
        run_all(seed=seed)
        df = optimize_joint(seed=seed)
        summary = {
            "seed": seed,
            "n_candidates": int(df.shape[0]),
            "joint_mean": float(df["joint_total_cost"].mean()),
            "independent_mean": float(df["independent_total_cost"].mean()),
            "joint_win_rate": float((df["joint_total_cost"] < df["independent_total_cost"]).mean()),
        }
        all_rows.append(summary)
    pd.DataFrame(all_rows).to_csv("results/trident/experiment_summary.csv", index=False)
    try:
        subprocess.run(["python3", "paper/update_metrics.py"], check=True, capture_output=True, text=True)
    except Exception:
        pass


if __name__ == "__main__":
    run_experiments()
