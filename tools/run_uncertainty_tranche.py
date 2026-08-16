#!/usr/bin/env python3
"""Execute the Cars4Mars bounded-uncertainty tranche.

This runner deliberately consumes only source-backed facts and explicitly labelled
hypothesis envelopes. It does not infer missing Rhino, CAD or physical-test values.
"""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cars4mars.simulation import GradeCase, HeartbeatLossCase, grade_forces, simulate_heartbeat_loss

REGISTRY = ROOT / "engineering" / "hardware_parameter_registry.json"


def classify(values: list[bool]) -> str:
    if values and all(values):
        return "ROBUST_PASS"
    if values and not any(values):
        return "ROBUST_FAIL"
    return "MIXED_HOLD"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("artifacts/uncertainty-tranche.json"))
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    governance = registry["governance"]
    if governance.get("next_tests_enabled") is not True:
        raise SystemExit("bounded uncertainty tranche is not enabled")
    if governance.get("enabled_mode") != "BOUNDED_UNCERTAINTY_ONLY":
        raise SystemExit("refusing to run outside BOUNDED_UNCERTAINTY_ONLY mode")

    locked = registry["source_locked"]
    envelope = registry["hypothesis_envelopes"]
    mass = float(locked["engineering_load_case_kg"])
    radius = float(locked["wheel_radius_m"])
    slope = float(locked["terrain"]["hill_or_ramp_max_expected_slope_deg"])

    grade_rows: list[dict[str, object]] = []
    grade_passes: list[bool] = []
    for torque, efficiency, mu, crr in product(
        envelope["total_drive_torque_nm"],
        envelope["drivetrain_efficiency"],
        envelope["traction_mu"],
        envelope["rolling_resistance_coeff"],
    ):
        case = GradeCase(
            mass_kg=mass,
            slope_deg=slope,
            wheel_radius_m=radius,
            total_drive_torque_nm=float(torque),
            drivetrain_efficiency=float(efficiency),
            rolling_resistance_coeff=float(crr),
            traction_mu=float(mu),
        )
        result = grade_forces(case)
        passed = result.net_uphill_force_n >= 0.0
        grade_passes.append(passed)
        grade_rows.append({
            "torque_nm": torque,
            "efficiency": efficiency,
            "traction_mu": mu,
            "rolling_resistance_coeff": crr,
            "net_uphill_force_n": result.net_uphill_force_n,
            "acceleration_mps2": result.acceleration_mps2,
            "traction_limited": result.traction_limited,
            "passes_model_criterion": passed,
        })

    nominal_speed_mps = float(registry["derived_but_not_physical_validation"]["ideal_surface_speed_at_60rpm_mps"])
    stop_rows: list[dict[str, object]] = []
    stop_passes: list[bool] = []
    # Model criterion: stop inside the 1.5 m autonomous stop radius after the 500 ms watchdog timeout.
    stop_radius_m = float(locked["autonomy"]["stop_radius_m"])
    for decel in envelope["physical_braking_deceleration_mps2"]:
        trace = simulate_heartbeat_loss(
            f"heartbeat-{decel}",
            HeartbeatLossCase(
                initial_speed_mps=nominal_speed_mps,
                command_timeout_ms=500,
                assumed_braking_deceleration_mps2=float(decel),
            ),
        )
        total = float(trace.summary["assumed_total_stop_distance_m"])
        passed = total <= stop_radius_m
        stop_passes.append(passed)
        stop_rows.append({
            "assumed_braking_deceleration_mps2": decel,
            "initial_speed_mps": nominal_speed_mps,
            "watchdog_timeout_ms": 500,
            "assumed_total_stop_distance_m": total,
            "model_limit_m": stop_radius_m,
            "passes_model_criterion": passed,
        })

    # Static cross-slope tipping sensitivity using a rectangular support approximation.
    # This is not rocker-bogie dynamics and intentionally ignores transient load transfer.
    stability_rows: list[dict[str, object]] = []
    stability_passes: list[bool] = []
    for track, cg_h in product(envelope["track_width_m"], envelope["cg_height_m"]):
        import math
        tip_angle_deg = math.degrees(math.atan((float(track) / 2.0) / float(cg_h)))
        passed = tip_angle_deg >= slope
        stability_passes.append(passed)
        stability_rows.append({
            "track_width_m": track,
            "cg_height_m": cg_h,
            "rectangular_static_tip_angle_deg": tip_angle_deg,
            "reference_slope_deg": slope,
            "passes_model_criterion": passed,
        })

    payload_rows = []
    payload_passes: list[bool] = []
    payload_mass = float(locked["payload"]["mission_object_max_kg"])
    g = 9.80665
    for decel in envelope["physical_braking_deceleration_mps2"]:
        inertial = payload_mass * float(decel)
        downslope = payload_mass * g * (2 ** -0.5)
        combined = inertial + downslope
        # No pass/fail retention claim is possible without restraint capacity.
        payload_rows.append({
            "assumed_deceleration_mps2": decel,
            "inertial_force_n": inertial,
            "gravity_downslope_45deg_n": downslope,
            "combined_longitudinal_demand_n": combined,
            "passes_model_criterion": None,
            "classification": "MIXED_HOLD",
            "missing": "measured/source-backed restraint capacity and friction",
        })
    payload_passes = [True, False]  # Force governed HOLD until physical restraint evidence exists.

    sections = {
        "drivetrain_grade_45deg": {
            "classification": classify(grade_passes),
            "criterion": "net uphill force >= 0 N",
            "rows": grade_rows,
        },
        "watchdog_stop_envelope": {
            "classification": classify(stop_passes),
            "criterion": f"assumed total stop distance <= {stop_radius_m} m",
            "rows": stop_rows,
        },
        "static_cross_slope_stability": {
            "classification": classify(stability_passes),
            "criterion": f"rectangular static tip angle >= {slope} deg",
            "rows": stability_rows,
            "omitted": ["rocker-bogie articulation", "dynamic load transfer", "wheel lift sequence"],
        },
        "payload_retention_demand": {
            "classification": classify(payload_passes),
            "criterion": "demand computed; physical capacity intentionally unknown",
            "rows": payload_rows,
        },
    }

    payload = {
        "schema": "cars4mars.uncertainty.tranche.v1",
        "baseline": registry["baseline"],
        "mode": governance["enabled_mode"],
        "truth_boundary": registry["truth_boundary"],
        "provenance": {
            "source_locked": "engineering/hardware_parameter_registry.json#source_locked",
            "primary_source_evidence": "engineering/hardware_parameter_registry.json#primary_source_evidence",
            "hypothesis_envelopes": "engineering/hardware_parameter_registry.json#hypothesis_envelopes",
        },
        "sections": sections,
        "physical_validation_measurements_remaining": registry["physical_validation_measurements"],
        "hard_invariant": "MODEL PASS != PHYSICAL PASS",
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({name: section["classification"] for name, section in sections.items()}, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
