# DFR-01 Simulation Model

## Purpose

The Cars4Mars simulation layer exists to make engineering assumptions executable **before physical hardware exists** and to produce deterministic visual traces that can later be replayed in the Three.js rover scene on the Cars4Mars website.

Simulation is **model evidence**, not physical validation.

A simulation may falsify an internally inconsistent design assumption. It may not prove that the physical rover will behave the same way until the model parameters have been replaced or calibrated with measurements.

## Current models

### 1. Constant-force grade model

The first grade model resolves:

- gravity parallel to slope;
- total normal force;
- rolling-resistance hypothesis;
- wheel torque converted to ground force;
- drivetrain-efficiency hypothesis;
- traction force ceiling `mu * N`;
- net uphill force;
- resulting constant acceleration.

For the DFR-01 30 kg / 45 degree / 125 mm radius lower bound, the exact ideal gravity-balancing torque is approximately **26.0127 N.m total**.

That value is intentionally demonstrated as an **ideal hold condition**, not a successful climb margin.

The model currently omits:

- Rhino IG52 torque-speed curve;
- motor/controller current limiting;
- thermal derating;
- skid-steer tyre scrub;
- rocker-bogie unequal load distribution;
- tyre deformation;
- suspension/joint compliance;
- obstacle impacts;
- transient battery voltage sag.

Those omissions must not be hidden. They are the next engineering work.

### 2. Heartbeat-loss stopping envelope

The software timeout can be simulated directly. Physical stopping behaviour cannot yet be known.

The trace therefore separates:

1. command/heartbeat loss;
2. timeout interval;
3. motor-enable removal;
4. assumed braking/coast deceleration;
5. stop time and stop distance.

The current example uses an explicitly hypothetical braking deceleration. That number must later be replaced by measured wheel velocity and contactor/motor-driver timing.

### 3. Grade sensitivity sweep

The sensitivity model sweeps hypothetical:

- total wheel torque;
- drivetrain efficiency;
- traction coefficient.

The sweep is intended to answer questions such as:

- At what point does the rover become torque-limited?
- At what point does more motor torque stop helping because traction is the limiting factor?
- How sensitive is a 45 degree claim to efficiency and surface assumptions?

The sweep values are **not Rhino IG52 specifications** unless a future source-backed motor model explicitly says so.

## Website / Three.js replay contract

Every dynamic trace uses schema:

`cars4mars.sim.trace.v1`

Each frame exposes:

- `t_ms`
- `x_m`, `y_m`, `z_m`
- `yaw_rad`, `pitch_rad`
- `linear_mps`, `angular_rad_s`
- `motor_enable`
- `command_alive`
- `grade_deg`
- `net_force_n`
- `traction_limited`
- `state`

This allows a Three.js renderer to animate the rover from the simulation output instead of inventing motion in the UI.

The visual must also surface:

- simulation name;
- model version;
- truth boundary;
- assumptions;
- summary/result;
- whether the scenario is passing, failing, traction-limited, or unknown.

## Proposed visual modes

The website should eventually support at least:

1. **45 degree ideal hold** — shows why 26 N.m is only a lower bound.
2. **Lossy 45 degree case** — rover rolls back under the same nominal torque once efficiency and rolling resistance are introduced.
3. **Traction-limited case** — shows that adding torque cannot overcome inadequate tyre/surface friction.
4. **Heartbeat-loss replay** — command disappears, timeout counter advances, motor-enable drops, then the rover decelerates using a clearly labelled assumed/measured braking profile.
5. **Parameter sensitivity map** — torque vs efficiency vs traction with pass/fail regions.

## Calibration path

As hardware arrives, replace assumptions in this order:

1. exact motor torque-speed/current curve;
2. gearbox/drivetrain efficiency;
3. tyre/surface traction coefficient;
4. rolling and skid-turn resistance;
5. component masses and CAD centre of mass;
6. battery sag and branch current measurements;
7. contactor/motor-enable opening time;
8. wheel velocity and physical stopping distance;
9. thermal behaviour during sustained turns/climbs;
10. obstacle and rocker-bogie load-transfer behaviour.

At that point the simulation becomes a calibrated digital model rather than an uncalibrated design hypothesis.

## Provenance rule

Simulation follows the same project chain:

**PROMPT / HYPOTHESIS -> AI PROPOSAL -> HUMAN DECISION -> MODEL/ARTIFACT -> COMMIT -> SIMULATION TEST -> PHYSICAL MEASUREMENT -> PASS / FAIL**

A beautiful simulation does not advance a physical engineering state by itself.
