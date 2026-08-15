"""Six-wheel skid-steer kinematic reference for DFR-01.

The model converts a body-frame linear/angular velocity request into left/right
wheel speeds for the three motors on each side. It is a design and software
artifact, not a traction or terrain-performance claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class DriveGeometry:
    track_width_m: float = 0.56
    wheel_radius_m: float = 0.125
    nominal_motor_rpm: float = 60.0

    def __post_init__(self) -> None:
        if self.track_width_m <= 0 or self.wheel_radius_m <= 0 or self.nominal_motor_rpm <= 0:
            raise ValueError("drive geometry values must be positive")


@dataclass(frozen=True)
class SixWheelCommand:
    left_front: float
    left_middle: float
    left_rear: float
    right_front: float
    right_middle: float
    right_rear: float

    def as_tuple(self) -> tuple[float, float, float, float, float, float]:
        return (
            self.left_front,
            self.left_middle,
            self.left_rear,
            self.right_front,
            self.right_middle,
            self.right_rear,
        )


@dataclass(frozen=True)
class DriveMix:
    left_mps: float
    right_mps: float
    left_rpm: float
    right_rpm: float
    duty: SixWheelCommand
    saturated: bool


def _wheel_rpm(linear_mps: float, radius_m: float) -> float:
    return linear_mps * 60.0 / (2.0 * math.pi * radius_m)


def mix_skid_steer(
    linear_mps: float,
    angular_rad_s: float,
    geometry: DriveGeometry = DriveGeometry(),
) -> DriveMix:
    """Map a body twist to six normalized motor duty commands.

    Positive angular velocity turns left: the right side moves faster than the
    left side. If either requested side exceeds nominal motor speed, both sides
    are scaled by the same factor to preserve curvature.
    """
    if not math.isfinite(linear_mps) or not math.isfinite(angular_rad_s):
        raise ValueError("velocity request must be finite")

    half_track = geometry.track_width_m / 2.0
    left_mps = linear_mps - angular_rad_s * half_track
    right_mps = linear_mps + angular_rad_s * half_track

    left_rpm = _wheel_rpm(left_mps, geometry.wheel_radius_m)
    right_rpm = _wheel_rpm(right_mps, geometry.wheel_radius_m)

    peak = max(abs(left_rpm), abs(right_rpm))
    scale = 1.0
    saturated = peak > geometry.nominal_motor_rpm
    if saturated:
        scale = geometry.nominal_motor_rpm / peak
        left_rpm *= scale
        right_rpm *= scale
        left_mps *= scale
        right_mps *= scale

    left_duty = left_rpm / geometry.nominal_motor_rpm
    right_duty = right_rpm / geometry.nominal_motor_rpm

    return DriveMix(
        left_mps=left_mps,
        right_mps=right_mps,
        left_rpm=left_rpm,
        right_rpm=right_rpm,
        duty=SixWheelCommand(
            left_front=left_duty,
            left_middle=left_duty,
            left_rear=left_duty,
            right_front=right_duty,
            right_middle=right_duty,
            right_rear=right_duty,
        ),
        saturated=saturated,
    )
