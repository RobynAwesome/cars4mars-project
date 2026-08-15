"""Auditable mechanical calculations for the Cars4Mars DFR-01 baseline.

These functions intentionally separate arithmetic from physical validation.  A passing
unit test proves that the stated equations are implemented consistently; it does not prove
that the rover, motor, tyre, suspension, or terrain will achieve the calculated result.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

STANDARD_GRAVITY_MPS2 = 9.81


@dataclass(frozen=True)
class MassPoint:
    """A component mass located at a Cartesian point in rover coordinates."""

    mass_kg: float
    x_m: float
    y_m: float
    z_m: float


def downslope_force_n(
    mass_kg: float,
    slope_deg: float,
    *,
    gravity_mps2: float = STANDARD_GRAVITY_MPS2,
) -> float:
    """Return the gravitational force component parallel to a slope.

    F_parallel = m g sin(theta)
    """
    _require_positive(mass_kg, "mass_kg")
    _require_positive(gravity_mps2, "gravity_mps2")
    _require_angle(slope_deg)
    return mass_kg * gravity_mps2 * math.sin(math.radians(slope_deg))


def normal_force_n(
    mass_kg: float,
    slope_deg: float,
    *,
    gravity_mps2: float = STANDARD_GRAVITY_MPS2,
) -> float:
    """Return the ideal total normal force on a slope."""
    _require_positive(mass_kg, "mass_kg")
    _require_positive(gravity_mps2, "gravity_mps2")
    _require_angle(slope_deg)
    return mass_kg * gravity_mps2 * math.cos(math.radians(slope_deg))


def ideal_total_wheel_torque_nm(
    mass_kg: float,
    slope_deg: float,
    wheel_radius_m: float,
    *,
    gravity_mps2: float = STANDARD_GRAVITY_MPS2,
) -> float:
    """Ideal total wheel torque needed only to balance gravity on the slope.

    This excludes rolling resistance, tyre deformation, skid-steer scrub, drivetrain
    losses, acceleration, obstacle impact, and margin.  It is therefore a lower-bound
    sizing calculation, not a claim of sufficient available motor torque.
    """
    _require_positive(wheel_radius_m, "wheel_radius_m")
    return downslope_force_n(
        mass_kg, slope_deg, gravity_mps2=gravity_mps2
    ) * wheel_radius_m


def ideal_equal_share_torque_nm(total_torque_nm: float, driven_wheels: int) -> float:
    """Arithmetic equal-share torque per driven wheel.

    Real rocker-bogie contact loads are not guaranteed to be equal, so this value must
    never be used as a motor requirement without load-transfer and traction margin.
    """
    _require_nonnegative(total_torque_nm, "total_torque_nm")
    if not isinstance(driven_wheels, int) or driven_wheels <= 0:
        raise ValueError("driven_wheels must be a positive integer")
    return total_torque_nm / driven_wheels


def minimum_friction_coefficient_for_static_slope(slope_deg: float) -> float:
    """Ideal no-slip coefficient required on a uniform static slope: mu >= tan(theta)."""
    _require_angle(slope_deg)
    if abs(slope_deg) >= 90:
        raise ValueError("slope magnitude must be below 90 degrees")
    return abs(math.tan(math.radians(slope_deg)))


def no_load_surface_speed_mps(wheel_rpm: float, wheel_radius_m: float) -> float:
    """Geometric wheel-surface speed from RPM.

    This is a kinematic conversion only.  It does not include motor droop, tyre slip,
    drivetrain losses, or load.
    """
    _require_nonnegative(wheel_rpm, "wheel_rpm")
    _require_positive(wheel_radius_m, "wheel_radius_m")
    return (wheel_rpm / 60.0) * (2.0 * math.pi * wheel_radius_m)


def current_from_power_a(power_w: float, voltage_v: float) -> float:
    """Return I=P/V for a stated *electrical input* power.

    Do not use this function to infer Cars4Mars motor current until the Rhino IG52
    datasheet definition of the quoted 100 W rating is confirmed.  It is arithmetic,
    not a motor-current model and not a stall-current estimate.
    """
    _require_nonnegative(power_w, "power_w")
    _require_positive(voltage_v, "voltage_v")
    return power_w / voltage_v


def center_of_mass_m(points: Iterable[MassPoint]) -> tuple[float, float, float]:
    """Compute centre of mass from explicit component masses and positions.

    DFR-01 does not currently provide enough mass-property inputs to call this function
    with authoritative rover data.  It exists so CAD/as-built mass properties can later be
    inserted without changing the calculation method.
    """
    pts = tuple(points)
    if not pts:
        raise ValueError("at least one mass point is required")
    for point in pts:
        _require_positive(point.mass_kg, "mass_kg")
        for value in (point.x_m, point.y_m, point.z_m):
            if not math.isfinite(value):
                raise ValueError("mass-point coordinates must be finite")

    total_mass = sum(point.mass_kg for point in pts)
    return (
        sum(point.mass_kg * point.x_m for point in pts) / total_mass,
        sum(point.mass_kg * point.y_m for point in pts) / total_mass,
        sum(point.mass_kg * point.z_m for point in pts) / total_mass,
    )


def _require_positive(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def _require_nonnegative(value: float, name: str) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")


def _require_angle(value: float) -> None:
    if not math.isfinite(value):
        raise ValueError("slope_deg must be finite")
