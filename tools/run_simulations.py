#!/usr/bin/env python3
"""Run deterministic DFR-01 simulations from the shared scenario contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cars4mars.simulation import GradeCase, HeartbeatLossCase, grade_sensitivity, simulate_grade, simulate_heartbeat_loss

SCENARIOS = ROOT / "engineering" / "simulation_scenarios.json"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_contract() -> dict[str, object]:
    payload = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    if payload.get("schema") != "cars4mars.sim.scenarios.v1" or payload.get("baseline") != "DFR-01":
        raise ValueError("invalid Cars4Mars simulation scenario contract")
    return payload


def build_artifacts() -> dict[str, object]:
    contract = load_contract()
    artifacts: dict[str, object] = {"scenario_contract.json": contract}

    for scenario in contract["scenarios"]:
        scenario_id = scenario["id"]
        kind = scenario["kind"]
        p = scenario["parameters"]

        if kind == "grade":
            trace = simulate_grade(
                scenario_id,
                GradeCase(
                    mass_kg=p["mass_kg"], slope_deg=p["slope_deg"], wheel_radius_m=p["wheel_radius_m"],
                    total_drive_torque_nm=p["total_drive_torque_nm"], drivetrain_efficiency=p["drivetrain_efficiency"],
                    rolling_resistance_coeff=p["rolling_resistance_coeff"], traction_mu=p["traction_mu"],
                    initial_speed_mps=p.get("initial_speed_mps", 0.0),
                ),
                duration_s=p["duration_s"], dt_ms=p["dt_ms"],
            )
            artifacts[f"{scenario_id}.json"] = trace.to_dict()
        elif kind == "heartbeat_loss":
            trace = simulate_heartbeat_loss(
                scenario_id,
                HeartbeatLossCase(
                    initial_speed_mps=p["initial_speed_mps"], command_timeout_ms=p["command_timeout_ms"],
                    assumed_braking_deceleration_mps2=p["assumed_braking_deceleration_mps2"],
                ),
                dt_ms=p["dt_ms"],
            )
            artifacts[f"{scenario_id}.json"] = trace.to_dict()
        elif kind == "grade_sensitivity":
            artifacts[f"{scenario_id}.json"] = {
                "schema": "cars4mars.sim.sweep.v1",
                "name": scenario_id,
                "truth_boundary": contract["truth_boundary"],
                "fixed_assumptions": {k: p[k] for k in ("mass_kg", "slope_deg", "wheel_radius_m", "rolling_resistance_coeff")},
                "sweep": grade_sensitivity(
                    mass_kg=p["mass_kg"], slope_deg=p["slope_deg"], wheel_radius_m=p["wheel_radius_m"],
                    torques_nm=p["torques_nm"], efficiencies=p["efficiencies"], traction_coefficients=p["traction_coefficients"],
                    rolling_resistance_coeff=p["rolling_resistance_coeff"],
                ),
            }
        else:
            raise ValueError(f"unsupported scenario kind: {kind}")
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("artifacts/simulations"))
    args = parser.parse_args()
    artifacts = build_artifacts()
    for filename, payload in artifacts.items():
        write_json(args.out / filename, payload)
        print(f"wrote {args.out / filename}")
    print(f"simulation artifacts: {len(artifacts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
