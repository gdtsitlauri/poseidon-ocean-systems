from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev
import shutil
import subprocess

import pandas as pd

from src.common import RESULT_FILES, ensure_dirs
from src.maritime.ais_bridge import bridge_score, try_build_pascal_shared_lib


@dataclass
class VesselState:
    mmsi: int
    lat: float
    lon: float
    speed_kn: float
    course_deg: float
    vessel_type: str
    displacement_tons: float
    sea_state: int


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def generate_synthetic_ais(seed: int = 42, n: int = 100) -> list[VesselState]:
    rng = random.Random(seed)
    vessel_types = ["Cargo", "Tanker", "Passenger", "Fishing", "Service"]
    tracks = []
    for i in range(n):
        tracks.append(
            VesselState(
                mmsi=100_000_000 + i,
                lat=rng.uniform(-40, 60),
                lon=rng.uniform(-70, 30),
                speed_kn=rng.uniform(8, 22),
                course_deg=rng.uniform(0, 359),
                vessel_type=rng.choice(vessel_types),
                displacement_tons=rng.uniform(2_000, 90_000),
                sea_state=rng.randint(1, 7),
            )
        )
    return tracks


def fuel_consumption(speed_kn: float, displacement_tons: float, sea_state: int) -> float:
    speed_factor = 0.0008 * speed_kn**3
    displacement_factor = 0.00002 * displacement_tons
    sea_factor = 1.0 + 0.08 * sea_state
    return (speed_factor + displacement_factor + 0.6) * sea_factor


def compute_cpa_tcpa(v1: VesselState, v2: VesselState) -> tuple[float, float]:
    distance = haversine_km(v1.lat, v1.lon, v2.lat, v2.lon)
    relative_speed = max(0.1, abs(v1.speed_kn - v2.speed_kn))
    tcpa_h = distance / (relative_speed * 1.852)
    return distance, tcpa_h


def great_circle_candidates(vessel: VesselState) -> list[tuple[float, float]]:
    return [
        (vessel.lat + 1.0, vessel.lon + 1.0),
        (vessel.lat + 1.5, vessel.lon + 0.8),
        (vessel.lat + 0.8, vessel.lon + 1.4),
    ]


def weather_penalty(lat: float, lon: float) -> float:
    return abs(math.sin(math.radians(lat)) * math.cos(math.radians(lon))) * 12.0


def optimize_route_dp(vessel: VesselState, stops: int = 3) -> tuple[float, float]:
    candidates = great_circle_candidates(vessel)
    dp = [(0.0, vessel.lat, vessel.lon, vessel.speed_kn)]
    for _ in range(stops):
        next_dp = []
        for cost, cur_lat, cur_lon, speed in dp:
            for nlat, nlon in candidates:
                segment = haversine_km(cur_lat, cur_lon, nlat, nlon)
                penalty = weather_penalty(nlat, nlon)
                fuel = fuel_consumption(speed, vessel.displacement_tons, vessel.sea_state) * (segment / 100.0)
                next_dp.append((cost + segment + fuel + penalty, nlat, nlon, max(8.0, speed - 0.5)))
        dp = sorted(next_dp, key=lambda x: x[0])[:6]
    best = min(dp, key=lambda x: x[0])
    return best[0], best[3]


def congestion_prediction(tracks: list[VesselState]) -> pd.DataFrame:
    ports = {
        "Lisbon": (38.72, -9.14),
        "Rotterdam": (51.92, 4.48),
        "Piraeus": (37.94, 23.64),
    }
    rows = []
    for port_name, (plat, plon) in ports.items():
        nearby = sum(1 for v in tracks if haversine_km(v.lat, v.lon, plat, plon) < 350)
        waiting_time_h = 1.2 + 0.3 * nearby
        rows.append({"port": port_name, "nearby_vessels": nearby, "predicted_waiting_h": waiting_time_h})
    return pd.DataFrame(rows)


def run(seed: int = 42) -> None:
    ensure_dirs(
        [
            RESULT_FILES["maritime_route"],
            RESULT_FILES["maritime_collision"],
            RESULT_FILES["maritime_anomaly"],
        ]
    )
    tracks = generate_synthetic_ais(seed=seed)
    bridge_status = try_build_pascal_shared_lib()
    pascal_status = "fpc_missing"
    if shutil.which("fpc"):
        try:
            subprocess.run(["fpc", "src/maritime/ais_parser.pas"], check=True, capture_output=True, text=True)
            sample_line = "!AIVDM,1,1,,A,123456789,0,37.8,-9.1,12.3,90.0,Cargo"
            subprocess.run(["./src/maritime/ais_parser"], input=sample_line + "\n", check=True, capture_output=True, text=True)
            pascal_status = "pascal_ok"
        except Exception:
            pascal_status = "pascal_compile_or_run_failed"
    route_rows = []
    for vessel in tracks:
        best_cost, optimal_speed = optimize_route_dp(vessel, stops=3)
        dist = haversine_km(vessel.lat, vessel.lon, vessel.lat + 1.0, vessel.lon + 1.0)
        fuel = fuel_consumption(vessel.speed_kn, vessel.displacement_tons, vessel.sea_state)
        route_rows.append(
            {
                "mmsi": vessel.mmsi,
                "distance_km": dist,
                "speed_kn": vessel.speed_kn,
                "fuel_estimate": fuel,
                "optimal_speed_kn": optimal_speed,
                "dp_route_cost": best_cost,
                "bridge_score": bridge_score(vessel.speed_kn, vessel.sea_state),
                "vessel_type": vessel.vessel_type,
            }
        )
    pd.DataFrame(route_rows).to_csv(RESULT_FILES["maritime_route"], index=False)

    collision_rows = []
    for i in range(0, min(len(tracks) - 1, 30), 2):
        cpa, tcpa = compute_cpa_tcpa(tracks[i], tracks[i + 1])
        collision_rows.append({"mmsi_a": tracks[i].mmsi, "mmsi_b": tracks[i + 1].mmsi, "cpa_km": cpa, "tcpa_h": tcpa})
    pd.DataFrame(collision_rows).to_csv(RESULT_FILES["maritime_collision"], index=False)

    speeds = [v.speed_kn for v in tracks]
    speed_mu, speed_sigma = mean(speeds), max(1e-9, pstdev(speeds))
    anomaly_rows = []
    for vessel in tracks:
        z = abs((vessel.speed_kn - speed_mu) / speed_sigma)
        route_dev = weather_penalty(vessel.lat, vessel.lon) / 12.0
        score = 0.6 * z + 0.4 * route_dev
        anomaly_rows.append({"mmsi": vessel.mmsi, "anomaly_score": score, "is_anomaly": score > 1.6})
    pd.DataFrame(anomaly_rows).to_csv(RESULT_FILES["maritime_anomaly"], index=False)
    congestion_prediction(tracks).to_csv("results/maritime/port_congestion_prediction.csv", index=False)

    # Provide a simple CSV export equivalent to Pascal parser output.
    Path("data").mkdir(exist_ok=True)
    pd.DataFrame([v.__dict__ for v in tracks]).to_csv("data/synthetic_ais.csv", index=False)
    pd.DataFrame([{"pascal_status": pascal_status, "bridge_status": bridge_status}]).to_csv(
        "results/maritime/pascal_bridge_status.csv", index=False
    )
