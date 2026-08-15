#!/usr/bin/env python3
"""Run deterministic DFR-01 simulations and emit website-ready JSON artifacts.

The output is model evidence only. Every artifact contains its own truth boundary
and assumptions so it cannot be mistaken for physical rover telemetry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cars4mars.simulation import (
    GradeCase,
    HeartbeatLossCase,
    grade_sensitivity,
    simulate_grade,
    simulate_heartbeat_loss,
)

IDEAL_45_TORQUE_NM = 26.012690712900116


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_artifacts() -> dict[str, object]:
    ideal = simulate_grade(
        "dfr01-grade45-ideal-lower-bound",
        GradeCase(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            total_drive_torque_nm=IDEAL_45_TORQUE_NM,
            drivetrain_efficiency=1.0,
            rolling_resistance_coeff=0.0,
            traction_mu=1.0,
        ),
        duration_s=3.0,
        dt_ms=100,
    )

    lossy = simulate_grade(
        "dfr01-grade45-lossy-hypothesis",
        GradeCase(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            total_drive_torque_nm=IDEAL_45_TORQUE_NM,
            drivetrain_efficiency=0.8,
            rolling_resistance_coeff=0.03,
            traction_mu=1.0,
        ),
        duration_s=3.0,
        dt_ms=100,
    )

    traction = simulate_grade(
        "dfr01-grade45-traction-limited-hypothesis",
        GradeCase(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            total_drive_torque_nm=45.0,
            drivetrain_efficiency=0.9,
            rolling_resistance_coeff=0.02,
            traction_mu=0.65,
        ),
        duration_s=3.0,
        dt_ms=100,
    )

    heartbeat = simulate_heartbeat_loss(
        "dfr01-heartbeat-loss-stop-envelope",
        HeartbeatLossCase(
            initial_speed_mps=0.5,
            command_timeout_ms=500,
            assumed_braking_deceleration_mps2=0.8,
        ),
        dt_ms=50,
    )

    sensitivity = {
        "schema": "cars4mars.sim.sweep.v1",
        "name": "dfr01-grade45-parameter-sensitivity",
        "truth_boundary": (
            "Hypothetical parameter sweep only. Torque/efficiency/traction grid values are not "
            "Rhino IG52 specifications and do not validate physical climb capability."
        ),
        "fixed_assumptions": {
            "mass_kg": 30.0,
            "slope_deg": 45.0,
            "wheel_radius_m": 0.125,
            "rolling_resistance_coeff": 0.02,
        },
        "sweep": grade_sensitivity(
            mass_kg=30.0,
            slope_deg=45.0,
            wheel_radius_m=0.125,
            torques_nm=[26.012690712900116, 32.5, 40.0, 50.0],
            efficiencies=[0.7, 0.8, 0.9],
            traction_coefficients=[0.6, 0.8, 1.0, 1.2],
            rolling_resistance_coeff=0.02,
        ),
    }

    return {
        "grade45_ideal_lower_bound.json": ideal.to_dict(),
        "grade45_lossy_hypothesis.json": lossy.to_dict(),
        "grade45_traction_limited.json": traction.to_dict(),
        "heartbeat_loss_stop_envelope.json": heartbeat.to_dict(),
        "grade45_sensitivity.json": sensitivity,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/simulations"),
        help="Output directory for deterministic JSON artifacts.",
    )
    args = parser.parse_args()

    artifacts = build_artifacts()
    for filename, payload in artifacts.items():
        write_json(args.out / filename, payload)
        print(f"wrote {args.out / filename}")

    print(f"simulation artifacts: {len(artifacts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
