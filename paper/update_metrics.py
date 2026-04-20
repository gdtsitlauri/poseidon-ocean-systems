from __future__ import annotations

from pathlib import Path

import pandas as pd


def main() -> None:
    route = pd.read_csv("results/maritime/route_optimization.csv")
    gis = pd.read_csv("results/gis/spatial_benchmarks.csv")
    trident = pd.read_csv("results/trident/joint_vs_independent_optimization.csv")
    lines = [
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{POSEIDON Generated Metrics}",
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Metric & Value \\\\",
        "\\midrule",
        f"Mean fuel estimate & {route['fuel_estimate'].mean():.3f} \\\\",
        f"Best GIS query (ms) & {gis['query_time_ms'].min():.4f} \\\\",
        f"TRIDENT joint mean & {trident['joint_total_cost'].mean():.3f} \\\\",
        f"TRIDENT independent mean & {trident['independent_total_cost'].mean():.3f} \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    Path("paper/generated_metrics.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
