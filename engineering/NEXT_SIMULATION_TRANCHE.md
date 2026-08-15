# Cars4Mars — Next Simulation Tranche (Frozen Pending More Hardware Context)

**State:** `HOLD / NOT EXECUTED`  
**Baseline:** DFR-01  
**Reason:** Additional hardware/context information is expected before the next numerical stress run.

The purpose of this file is to pre-register what the next simulations must attack so that later results cannot be cherry-picked or retrofitted around a desired answer.

## Tranche A — Motor + drivetrain closure

Required inputs before execution:

- exact Rhino IG52 part/datasheet
- torque-speed curve
- rated/stall torque
- no-load/rated/stall current
- gearbox efficiency
- duty-cycle/thermal limits
- MDDS30 current-limit/protection configuration
- DC bus voltage under load

Planned outputs:

- wheel torque versus speed
- available ground force versus speed
- current demand versus slope/speed
- torque margin on 30 deg and 45 deg cases
- torque-limited versus traction-limited regions
- thermal/current-limit boundary hypotheses

## Tranche B — Rover geometry + rocker-bogie articulation

Required inputs:

- final wheelbase
- front/middle/rear axle spacing
- track width
- rocker length
- bogie length
- pivot coordinates
- joint range
- ground clearance
- CAD chassis reference frame

Planned outputs:

- wheel contact sequence over 30 cm / 30 deg bump profiles
- chassis pitch trajectory
- articulation-angle envelope
- approach/departure/clearance checks
- support polygon through contact transitions
- per-wheel normal-load approximation

## Tranche C — Centre of mass + static/dynamic stability

Required inputs:

- component mass ledger
- component coordinates
- CAD mass properties
- empty rover CG
- +1 kg payload CG

Planned outputs:

- pitch and roll static tip envelopes
- CG projection on 30 deg and 45 deg terrain
- support-polygon margin
- payload-induced CG shift
- stability sensitivity to battery/compute/payload placement

## Tranche D — Payload retention

Required inputs:

- final tray CAD
- wall heights/geometry
- tie-down locations and hardware
- fastener specification
- representative payload dimensions/shape
- friction assumptions or measured coefficient
- allowed displacement

Planned outputs:

- 1 kg inertial load under acceleration/deceleration
- longitudinal + slope combined load
- lateral turning load
- emergency-stop load envelope
- bump-induced retention demand
- friction contribution versus mechanical restraint contribution

## Tranche E — Power + current + runtime

Required inputs:

- verified motor current data
- Jetson power profile
- D455 current/power
- A2M12 current/power
- Teensy/radio/DC-DC branch budgets
- converter efficiencies
- BMS continuous/peak limits
- battery internal resistance or measured sag

Planned outputs:

- branch current budget
- idle/cruise/pivot/climb/near-stall current envelopes
- fuse/BMS margin
- battery voltage sag hypotheses
- 40-minute mission energy envelope
- thermal-energy duty cycle

## Tranche F — Safety stopping envelope

Required inputs:

- measured motor-disable latency
- MDDS30 disable/coast/brake behavior
- contactor opening time
- wheel speed decay
- payload configuration
- surface traction

Planned outputs:

- command-loss travel before disable
- physical braking/coast distance
- total stop distance versus initial speed
- 500 ms watchdog adequacy against measured stopping envelope
- payload retention coupling during fail-stop

## Tranche G — Perception + autonomy geometry

Required inputs:

- camera pose
- camera FOV and calibrated intrinsics
- LiDAR pose
- LiDAR range/noise model
- sensor-to-body transforms
- rover footprint
- target geometry assumptions

Planned outputs:

- bearing/range to rover-frame target coordinates
- rover-frame to world-frame transform
- nearest-point geometry for the 1.5 m balloon condition
- detection/localization uncertainty envelope
- stop-point safety margin under uncertainty
- target-loss and reacquisition state transitions

## PKA classification rule for every tranche

Each run must publish:

```text
KNOWN / source-backed parameters
MEASURED parameters
HYPOTHETICAL parameters
UNKNOWN parameters
model version
computed witness
scope
hard invariant
result
missing evidence
next gate
```

A simulation result may close only its declared model scope.

```text
MODEL PASS != PHYSICAL PASS
MODEL FAIL != PHYSICAL FAIL
```

A model failure may falsify an assumption or expose a design risk. A model pass may justify moving to the next evidence gate. Neither replaces the physical rover test.

## Current gate

```text
next_tests_enabled = false
```

Resume only when the additional hardware/context information has been incorporated into `engineering/hardware_parameter_registry.json` and the affected parameters have explicit provenance.
