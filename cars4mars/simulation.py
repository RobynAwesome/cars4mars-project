"""Deterministic simulation models for Cars4Mars DFR-01.

Simulation is MODEL EVIDENCE, not physical validation.

The goal of this module is to make engineering assumptions executable and
visualisable before hardware exists. Every model is parameterised so unknown
hardware quantities remain explicit rather than being silently invented.

The JSON traces emitted by this module are intentionally suitable for later
Three.js replay on the Cars4Mars website.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable

from .mechanics import STANDARD_GRAVITY_MPS2


TRACE_SCHEMA = "cars4mars.sim.trace.v1"


@dataclass(frozen=True)
class GradeCase:
    mass_kg: float
    slope_deg: float
    wheel_radius_m: float
    total_drive_torque_nm: float
    drivetrain_efficiency: float
    rolling_resistance_coeff: float
    traction_mu: float
    initial_speed_mps: float = 0.0

    def __post_init__(self) -> None:
        if self.mass_kg <= 0:
            raise ValueError("mass_kg must be positive")
        if self.wheel_radius_m <= 0:
            raise ValueError("wheel_radius_m must be positive")
        if self.total_drive_torque_nm < 0:
            raise ValueError("total_drive_torque_nm must be non-negative")
        if not 0 < self.drivetrain_efficiency <= 1:
            raise ValueError("drivetrain_efficiency must be in (0, 1]")
        if self.rolling_resistance_coeff < 0:
            raise ValueError("rolling_resistance_coeff must be non-negative")
        if self.traction_mu < 0:
            raise ValueError("traction_mu must be non-negative")
        for value in (self.slope_deg, self.initial_speed_mps):
            if not math.isfinite(value):
                raise ValueError("grade case values must be finite")
        if abs(self.slope_deg) >= 90:
            raise ValueError("slope magnitude must be below 90 degrees")


@dataclass(frozen=True)
class GradeForces:
    gravity_downslope_n: float
    normal_force_n: float
    rolling_resistance_n: float
    drive_force_before_traction_n: float
    traction_limit_n: float
    usable_drive_force_n: float
    net_uphill_force_n: float
    acceleration_mps2: float
    traction_limited: bool
    status: str


@dataclass(frozen=True)
class HeartbeatLossCase:
    initial_speed_mps: float
    command_timeout_ms: int
    assumed_braking_deceleration_mps2: float

    def __post_init__(self) -> None:
        if self.initial_speed_mps < 0 or not math.isfinite(self.initial_speed_mps):
            raise ValueError("initial_speed_mps must be finite and non-negative")
        if self.command_timeout_ms <= 0:
            raise ValueError("command_timeout_ms must be positive")
        if self.assumed_braking_deceleration_mps2 <= 0 or not math.isfinite(
            self.assumed_braking_deceleration_mps2
        ):
            raise ValueError("assumed_braking_deceleration_mps2 must be positive")


@dataclass(frozen=True)
class TraceFrame:
    t_ms: int
    x_m: float
    y_m: float
    z_m: float
    yaw_rad: float
    pitch_rad: float
    linear_mps: float
    angular_rad_s: float
    motor_enable: bool
    command_alive: bool
    grade_deg: float
    net_force_n: float | None
    traction_limited: bool | None
    state: str


@dataclass(frozen=True)
class SimulationTrace:
    name: str
    model: str
    truth_boundary: str
    assumptions: dict[str, object]
    summary: dict[str, object]
    frames: tuple[TraceFrame, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": TRACE_SCHEMA,
            "name": self.name,
            "model": self.model,
            "truth_boundary": self.truth_boundary,
            "assumptions": self.assumptions,
            "summary": self.summary,
            "frames": [asdict(frame) for frame in self.frames],
        }


def grade_forces(case: GradeCase) -> GradeForces:
    """Evaluate a constant-parameter uphill force balance.

    This model deliberately does not include dynamic motor torque-speed behaviour,
    tyre compliance, rocker-bogie load transfer, obstacle impacts, or thermal limits.
    Those omissions are why this is a simulation hypothesis rather than validation.
    """
    theta = math.radians(case.slope_deg)
    gravity = case.mass_kg * STANDARD_GRAVITY_MPS2 * math.sin(theta)
    normal = case.mass_kg * STANDARD_GRAVITY_MPS2 * math.cos(theta)
    rolling = case.rolling_resistance_coeff * normal
    drive_before_traction = (
        case.total_drive_torque_nm * case.drivetrain_efficiency / case.wheel_radius_m
    )
    traction_limit = case.traction_mu * normal
    usable_drive = min(drive_before_traction, traction_limit)
    net = usable_drive - gravity - rolling
    accel = net / case.mass_kg
    traction_limited = traction_limit < drive_before_traction

    tolerance_n = 1e-6
    if net > tolerance_n:
        status = "accelerating_uphill"
    elif net < -tolerance_n:
        status = "insufficient_uphill_force"
    else:
        status = "ideal_grade_hold"

    return GradeForces(
        gravity_downslope_n=gravity,
        normal_force_n=normal,
        rolling_resistance_n=rolling,
        drive_force_before_traction_n=drive_before_traction,
        traction_limit_n=traction_limit,
        usable_drive_force_n=usable_drive,
        net_uphill_force_n=net,
        acceleration_mps2=accel,
        traction_limited=traction_limited,
        status=status,
    )


def simulate_grade(
    name: str,
    case: GradeCase,
    *,
    duration_s: float = 3.0,
    dt_ms: int = 100,
) -> SimulationTrace:
    """Generate an analytic constant-force grade trace for visual replay."""
    if duration_s <= 0 or not math.isfinite(duration_s):
        raise ValueError("duration_s must be finite and positive")
    if dt_ms <= 0:
        raise ValueError("dt_ms must be positive")

    forces = grade_forces(case)
    theta = math.radians(case.slope_deg)
    duration_ms = round(duration_s * 1000)
    times = list(range(0, duration_ms + 1, dt_ms))
    if times[-1] != duration_ms:
        times.append(duration_ms)

    frames: list[TraceFrame] = []
    for t_ms in times:
        t_s = t_ms / 1000.0
        s_m = case.initial_speed_mps * t_s + 0.5 * forces.acceleration_mps2 * t_s * t_s
        v_mps = case.initial_speed_mps + forces.acceleration_mps2 * t_s
        frames.append(
            TraceFrame(
                t_ms=t_ms,
                x_m=s_m * math.cos(theta),
                y_m=0.0,
                z_m=s_m * math.sin(theta),
                yaw_rad=0.0,
                pitch_rad=theta,
                linear_mps=v_mps,
                angular_rad_s=0.0,
                motor_enable=True,
                command_alive=True,
                grade_deg=case.slope_deg,
                net_force_n=forces.net_uphill_force_n,
                traction_limited=forces.traction_limited,
                state=forces.status,
            )
        )

    return SimulationTrace(
        name=name,
        model="constant_force_grade_v1",
        truth_boundary=(
            "Simulation only. Constant force balance with explicit assumptions; not a Rhino IG52 "
            "motor model and not evidence that the physical rover can climb the grade."
        ),
        assumptions={
            **asdict(case),
            "omitted": [
                "motor torque-speed curve",
                "stall-current limit",
                "thermal derating",
                "skid-steer scrub",
                "rocker-bogie load transfer",
                "tyre deformation",
                "obstacle impact",
                "controller current limiting",
            ],
        },
        summary={
            **asdict(forces),
            "end_speed_mps": frames[-1].linear_mps,
            "end_distance_along_slope_m": (
                case.initial_speed_mps * duration_s
                + 0.5 * forces.acceleration_mps2 * duration_s * duration_s
            ),
        },
        frames=tuple(frames),
    )


def simulate_heartbeat_loss(
    name: str,
    case: HeartbeatLossCase,
    *,
    dt_ms: int = 50,
) -> SimulationTrace:
    """Simulate command-loss latency followed by an assumed constant deceleration.

    The 500 ms software timeout can be represented exactly. Physical deceleration
    cannot: it depends on motor/controller/contactor/brake/coast behaviour, so this
    model requires the caller to state an assumed deceleration explicitly.
    """
    if dt_ms <= 0:
        raise ValueError("dt_ms must be positive")

    timeout_s = case.command_timeout_ms / 1000.0
    brake_time_s = case.initial_speed_mps / case.assumed_braking_deceleration_mps2
    stop_time_s = timeout_s + brake_time_s
    distance_during_timeout_m = case.initial_speed_mps * timeout_s
    braking_distance_m = (
        case.initial_speed_mps * case.initial_speed_mps
        / (2.0 * case.assumed_braking_deceleration_mps2)
    )
    stop_distance_m = distance_during_timeout_m + braking_distance_m
    duration_ms = math.ceil(stop_time_s * 1000.0)

    times = list(range(0, duration_ms + 1, dt_ms))
    if times[-1] != duration_ms:
        times.append(duration_ms)

    frames: list[TraceFrame] = []
    for t_ms in times:
        t_s = t_ms / 1000.0
        if t_s <= timeout_s:
            v = case.initial_speed_mps
            x = case.initial_speed_mps * t_s
            motor_enable = True
            state = "command_lost_waiting_for_timeout"
        else:
            tau = min(t_s - timeout_s, brake_time_s)
            v = max(
                0.0,
                case.initial_speed_mps
                - case.assumed_braking_deceleration_mps2 * tau,
            )
            x = (
                distance_during_timeout_m
                + case.initial_speed_mps * tau
                - 0.5 * case.assumed_braking_deceleration_mps2 * tau * tau
            )
            motor_enable = False
            state = "decelerating_after_motor_disable" if v > 0 else "stopped"

        frames.append(
            TraceFrame(
                t_ms=t_ms,
                x_m=x,
                y_m=0.0,
                z_m=0.0,
                yaw_rad=0.0,
                pitch_rad=0.0,
                linear_mps=v,
                angular_rad_s=0.0,
                motor_enable=motor_enable,
                command_alive=False,
                grade_deg=0.0,
                net_force_n=None,
                traction_limited=None,
                state=state,
            )
        )

    return SimulationTrace(
        name=name,
        model="heartbeat_loss_stop_envelope_v1",
        truth_boundary=(
            "The timeout is software design intent. Braking deceleration is an explicit hypothetical "
            "input until measured on the physical rover."
        ),
        assumptions={
            **asdict(case),
            "command_loss_time_ms": 0,
            "contactor_open_delay_ms": 0,
            "warning": "Measured contactor opening and wheel deceleration must replace these assumptions.",
        },
        summary={
            "timeout_distance_m": distance_during_timeout_m,
            "assumed_braking_distance_m": braking_distance_m,
            "assumed_total_stop_distance_m": stop_distance_m,
            "assumed_total_stop_time_s": stop_time_s,
        },
        frames=tuple(frames),
    )


def grade_sensitivity(
    *,
    mass_kg: float,
    slope_deg: float,
    wheel_radius_m: float,
    torques_nm: Iterable[float],
    efficiencies: Iterable[float],
    traction_coefficients: Iterable[float],
    rolling_resistance_coeff: float,
) -> list[dict[str, object]]:
    """Deterministic parameter sweep for visualising design sensitivity.

    Values in the sweep are hypotheses, not inferred Rhino IG52 specifications.
    """
    rows: list[dict[str, object]] = []
    for torque in torques_nm:
        for efficiency in efficiencies:
            for mu in traction_coefficients:
                case = GradeCase(
                    mass_kg=mass_kg,
                    slope_deg=slope_deg,
                    wheel_radius_m=wheel_radius_m,
                    total_drive_torque_nm=float(torque),
                    drivetrain_efficiency=float(efficiency),
                    rolling_resistance_coeff=rolling_resistance_coeff,
                    traction_mu=float(mu),
                )
                result = grade_forces(case)
                rows.append(
                    {
                        "torque_nm": torque,
                        "drivetrain_efficiency": efficiency,
                        "traction_mu": mu,
                        "net_uphill_force_n": result.net_uphill_force_n,
                        "acceleration_mps2": result.acceleration_mps2,
                        "traction_limited": result.traction_limited,
                        "status": result.status,
                    }
                )
    return rows
