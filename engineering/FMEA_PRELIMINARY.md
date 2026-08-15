# DFR-01 Preliminary Failure Hypotheses

This is **not** a completed hardware FMEA. It is a queue of failure hypotheses that must be attacked with source-backed limits and physical measurements.

| Failure hypothesis | Why it matters | Current evidence state | Test that can falsify/confirm it |
|---|---|---|---|
| Traction loss on severe grade | A 45° static slope ideally requires μ ≈ 1 before adding dynamics or surface uncertainty. | Calculated only | Measure tyre/surface traction and loaded ramp behavior; log slip and wheel speed. |
| Insufficient motor torque margin | The 26 N·m figure is only the ideal total torque needed to balance gravity at 30 kg and 45°. | Lower-bound calculation only | Bind manufacturer torque-speed curve; calculate margin including losses; perform loaded climb. |
| Skid-steer current/thermal stress | Turning requires tyre scrub and can produce high current even on flat terrain. | Not measured | Instrument left/right drive current and motor/controller temperature during repeated zero-radius and loaded turns. |
| Battery sag / protection trip | Six drive motors plus compute/sensors may create transient demand that the energy rating alone does not describe. | Battery/fuse architecture selected; draw unknown | Log pack voltage/current and branch currents during idle, cruise, turns, ramp, and near-stall events. |
| Communications loss | Loss of control link is mission and safety critical. | Software fail-stop implemented and tested | Cut command path on bench and rover; measure command age, motor enable, contactor state, wheel stop time and distance. |
| Payload shift/ejection | A 1 kg payload changes dynamics and must remain in the onboard container. | Tray design intent only | Retain 1 kg through turns, bumps, ramp traversal, and emergency stop; inspect displacement and retention hardware. |
| Centre-of-mass instability | Stability on slopes/bumps depends on real mass distribution, not render placement. | COM coordinate unknown | Export CAD mass properties and verify with as-built corner scales/balance measurements. |
| Rocker-bogie structural/joint overload | Articulation introduces concentrated joint and frame loads during obstacles. | Not structurally validated | Perform CAD load cases, inspect fasteners/joints, then obstacle test under instrumented/defined load. |
| Thermal overload during sustained mission | 40-minute mission activity can expose thermal limits missed by short tests. | Not measured | 40-minute integrated endurance run with motor/controller/compute/battery temperatures recorded. |

## Rule

The phrase **"what fails first"** remains **UNKNOWN** until measurements rank actual limiting behavior. Engineering is allowed to have hypotheses; it is not allowed to promote them to facts without evidence.
