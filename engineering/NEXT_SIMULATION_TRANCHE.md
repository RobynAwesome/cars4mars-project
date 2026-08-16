# Cars4Mars — Next Simulation Tranche

**State:** `ENABLED / BOUNDED_UNCERTAINTY_ONLY`  
**Baseline:** DFR-01  
**Owner supersession:** 2026-08-16 — the former blanket hold is replaced by a sensitivity-first tranche so unresolved physical quantities no longer stop model work.

The purpose of this tranche is to attack uncertainty without turning guesses into hardware facts. Source-backed and measured inputs remain distinct from hypothesis envelopes. A model result may narrow design risk; it may not promote the rover to physical validation.

## Execution law

```text
SOURCE-BACKED FACTS
      +
EXPLICIT HYPOTHESIS ENVELOPES
      ↓
DETERMINISTIC SENSITIVITY SWEEP
      ↓
ROBUST_PASS | MIXED_HOLD | ROBUST_FAIL
      ↓
PHYSICAL MEASUREMENT GATE REMAINS SEPARATE
```

`MODEL PASS != PHYSICAL PASS`  
`MODEL FAIL != PHYSICAL FAIL`

## Tranche A — Motor + drivetrain envelope

Until the exact Rhino IG52 torque-speed/current/thermal document is positively matched, the rover is evaluated across an explicit total-wheel-torque × efficiency × traction × rolling-resistance envelope.

Outputs:
- uphill-force margin over the envelope;
- traction-limited versus torque-limited regions;
- robust/mixed/failing parameter regions;
- exact witness rows for later comparison with purchased-part data.

Exact motor current, stall behavior, thermal limits and duty cycle remain physical/source evidence gates.

## Tranche B — Rover geometry + rocker-bogie articulation

CAD/as-built geometry remains required before an exact articulation claim. The current tranche may only expose parameterized interfaces and conservative bounds. Final wheelbase, axle spacing, rocker/bogie lengths, pivots and ground clearance remain measurement gates.

## Tranche C — Centre of mass + static stability

CG height and payload shift are treated as hypothesis envelopes until CAD or measured mass properties exist. Any stability result is therefore a sensitivity witness, not an as-built statement.

## Tranche D — Payload retention

The 1 kg payload load can be symbolically/parametrically evaluated, but retention hardware, friction and allowable displacement remain physical-design evidence gates. No payload-retention PASS is permitted without those receipts.

## Tranche E — Power + runtime

Source-backed component envelopes may be combined with conditional assumptions, but no exact battery/BMS/current/runtime claim is permitted until the exact motor current data, pack limits, converter efficiencies and branch measurements exist.

## Tranche F — Safety stopping envelope

The existing 500 ms command timeout is evaluated across an explicit braking-deceleration hypothesis envelope. Actual disable latency, contactor opening and coast/braking behavior remain required before physical stop-distance validation.

## Tranche G — Perception + autonomy geometry

Manufacturer FOV/range data are source-backed; final mounting transforms are not. Sensor pose and yaw uncertainty may be swept, but autonomous stop-geometry validation remains gated on integrated calibration.

## PKA receipt for every run

Every run must publish:

```text
KNOWN / source-backed parameters
MEASURED parameters
HYPOTHESIS envelope
UNKNOWN / physical-gate parameters
model version
computed witness
scope
hard invariant
classification
missing physical evidence
next gate
```

Classification semantics:

- `ROBUST_PASS` — every sampled point in the declared hypothesis envelope passes the model criterion.
- `ROBUST_FAIL` — every sampled point fails the model criterion.
- `MIXED_HOLD` — the result changes across the envelope; a measurement/source receipt is needed to locate the real system.

## Current gate

```text
next_tests_enabled = true
mode = BOUNDED_UNCERTAINTY_ONLY
```

This unblocks model work. It does **not** waive the physical evidence required to claim the rover itself has passed a drivetrain, stability, retention, power, stopping or perception test.
