# DFR-01 Algebra + Trigonometry Model — Staged, Not Retested

**Status:** `STAGED_NOT_RETESTED`  
**Baseline:** DFR-01  
**Purpose:** Turn the rover architecture into explicit symbolic relationships before the next simulation/test tranche is allowed to execute.

This document does **not** claim that the physical rover satisfies any of these relationships under real load. It separates source-locked geometry/hardware from conditional algebra and unresolved physical parameters.

## 1. Source-locked anchors

- Rover target envelope: `0.700 x 0.650 x 0.500 m`
- Engineering mass case: `m = 30 kg`
- Six wheels; skid-steer; passive rocker-bogie
- Wheel diameter: `D = 0.250 m`; radius `r = 0.125 m`
- Six Rhino IG52 motors: `24 V / 60 rpm / 100 W label`
- Three Cytron MDDS30 motor drivers
- 24 V, 20 Ah LiFePO4 battery: `E_nom = 480 Wh`
- Payload: `m_p <= 1 kg`; tray `0.350 x 0.300 x 0.180 m`
- Bumps: height up to `0.30 m`, slope up to `30 deg`
- Hill/ramp: height up to `1.0 m`, slope up to `45 deg`
- Balloon stop radius: `1.5 m`; dwell: `5 s`

The existing software default `track_width = 0.56 m` is **not source-locked**. It remains a model hypothesis until CAD/as-built geometry replaces it.

---

## 2. Wheel rotation and ideal kinematics

Wheel circumference:

```text
C = 2*pi*r
```

For `r = 0.125 m`:

```text
C = 0.785398 m
```

At `60 rpm = 1 revolution/s`, the purely geometric no-load surface speed is:

```text
v_surface = C*(rpm/60)
          = 0.785398 m/s
```

This is **not** the loaded rover speed. Real speed depends on motor torque-speed droop, voltage, controller limits, tyre deformation and slip.

For skid-steer body command `(v, omega)` and track width `W_t`:

```text
v_left  = v - omega*W_t/2
v_right = v + omega*W_t/2
```

Wheel angular velocity:

```text
omega_wheel = v_side/r
```

Wheel RPM:

```text
rpm_side = (v_side/(2*pi*r))*60
```

Because `W_t` is unresolved, all turn-radius and differential-speed results that depend on it remain `MAYBE` at hardware scope.

---

## 3. Slope trigonometry

For slope angle `theta`:

```text
rise/run = tan(theta)
```

At `theta = 45 deg`:

```text
tan(45 deg) = 1
```

Therefore a **conditional** ramp with exactly `1.0 m` vertical rise at exactly `45 deg` would have:

```text
horizontal_run = rise/tan(theta) = 1.0 m
path_length    = rise/sin(theta)  = sqrt(2) ~= 1.4142 m
```

The Rulebook gives maximum expected height and maximum expected slope. It does not state that both maxima must occur simultaneously, so this geometry is a conditional witness, not the canonical Marsyard geometry.

For the bump maximum slope of `30 deg`:

```text
tan(30 deg) ~= 0.57735
```

A conditional `0.30 m` rise at exactly `30 deg` would require:

```text
horizontal_run ~= 0.5196 m
path_length    = 0.30/sin(30 deg) = 0.60 m
```

Again: conditional geometry only.

---

## 4. Gravity decomposition on a slope

For rover mass `m`, gravity `g`, slope `theta`:

```text
F_parallel = m*g*sin(theta)
F_normal   = m*g*cos(theta)
```

At `m = 30 kg`, `theta = 45 deg`, `g = 9.81 m/s^2`:

```text
F_parallel ~= 208.1015 N
F_normal   ~= 208.1015 N
```

The ideal total wheel torque required only to balance the downslope gravity component is:

```text
tau_gravity = F_parallel*r
```

At `r = 0.125 m`:

```text
tau_gravity ~= 26.0127 N.m total
```

Arithmetic equal share across six driven wheels:

```text
tau_equal ~= 4.33545 N.m/wheel
```

This equal-share result is **not** a rocker-bogie load-transfer model.

---

## 5. Expanded uphill force balance

Let:

- `tau_total` = total wheel torque available at the ground-side shafts
- `eta_d` = drivetrain efficiency
- `C_rr` = rolling-resistance coefficient
- `mu` = tyre/surface traction coefficient

Requested drive force before traction saturation:

```text
F_drive_raw = tau_total*eta_d/r
```

Traction ceiling:

```text
F_traction_max = mu*F_normal
```

Usable drive force:

```text
F_drive = min(F_drive_raw, F_traction_max)
```

Rolling resistance approximation:

```text
F_rr = C_rr*F_normal
```

Net uphill force:

```text
F_net = F_drive - F_parallel - F_rr
```

Acceleration:

```text
a = F_net/m
```

Positive-margin climb requires:

```text
F_net > 0
```

A necessary traction condition under this simplified model is:

```text
mu > tan(theta) + C_rr
```

At `45 deg`:

```text
mu > 1 + C_rr
```

Because `mu` and `C_rr` are unresolved, the physical 45-degree capability must remain `MAYBE`.

---

## 6. Torque threshold before traction saturation

Ignoring dynamic motor-speed variation for the moment, torque required for positive margin is:

```text
tau_required > r*(F_parallel + F_rr)/eta_d
```

Substituting the slope equations:

```text
tau_required > r*m*g*(sin(theta) + C_rr*cos(theta))/eta_d
```

This equation becomes procurement-useful only after `eta_d`, tyre/surface behavior and the Rhino IG52 torque-speed curve are source-backed or measured.

The exact motor must be evaluated at the **required wheel speed**, not only by stall torque or a single catalogue number.

---

## 7. Payload dynamics and retention

For mission payload mass `m_p` on a slope:

```text
F_payload_slope = m_p*g*sin(theta)
N_payload       = m_p*g*cos(theta)
```

At `m_p = 1 kg`, `theta = 45 deg`:

```text
F_payload_slope ~= 6.9367 N
N_payload       ~= 6.9367 N
```

During longitudinal acceleration/deceleration `a_x`, a simple worst-aligned retention demand is:

```text
F_retention_x >= m_p*|a_x + g*sin(theta)|
```

For lateral acceleration `a_y`:

```text
F_retention_y >= m_p*|a_y|
```

If retention relies partly on friction:

```text
F_friction_max = mu_payload*N_payload
```

Mechanical walls/tie-downs must carry any residual demand:

```text
F_mechanical >= F_demand - F_friction_max
```

No pass/fail retention result is allowed until the final tray geometry, tie-down hardware, friction assumptions, acceleration envelope and permitted displacement are defined.

---

## 8. Centre of mass and tipping envelope

The exact DFR-01 centre of mass is unresolved.

For component mass points `m_i` at coordinates `(x_i,y_i,z_i)`:

```text
x_cg = sum(m_i*x_i)/sum(m_i)
y_cg = sum(m_i*y_i)/sum(m_i)
z_cg = sum(m_i*z_i)/sum(m_i)
```

A first-order rigid-body slope check projects the CG onto the support plane.

For a centered CG with support half-length `L_s/2` in the pitch direction:

```text
z_cg*tan(theta) < L_s/2
```

Equivalent static tip angle:

```text
theta_tip_pitch = atan((L_s/2)/z_cg)
```

For lateral half-width `W_s/2`:

```text
theta_tip_roll = atan((W_s/2)/z_cg)
```

These are only bounding equations. A rocker-bogie rover has a changing support polygon and unequal wheel loads, so actual stability requires suspension geometry and contact-state modelling.

Payload must be evaluated in at least two configurations:

```text
CG_empty
CG_with_1kg_payload
```

---

## 9. Bump / rocker-bogie geometry

The competition expects bumps up to `0.30 m` height and `30 deg` slope. The 250 mm wheel diameter means:

```text
D_wheel = 0.25 m
h_bump,max = 0.30 m
```

Because the obstacle height can exceed one wheel diameter, the design must **not** rely on a single-wheel vertical-step model. However, the Rulebook defines bumps/uneven terrain with a maximum expected slope, not a guaranteed vertical 0.30 m wall.

The correct next model needs:

```text
front/middle/rear axle spacing
rocker arm length
bogie arm length
pivot positions
joint limits
chassis ground clearance
wheel load distribution
approach/departure geometry
```

Once those values exist, the next trigonometric layer can solve articulation angles and body pitch as each wheel contacts the bump profile.

---

## 10. Power algebra — without pretending energy is current

Nominal battery energy:

```text
E_nom = V*Ah = 24*20 = 480 Wh
```

This does **not** determine operating current or runtime.

Conditional branch-current algebra:

```text
I_branch = P_electrical/V_bus
I_total  = sum(I_branch)
```

If — and only if — the Rhino `100 W` label were verified as electrical input power at the operating point, six motors at that exact condition would imply:

```text
P_6motors = 600 W
I_6motors = 600/24 = 25 A
```

That is a conditional arithmetic witness only. It is **not** rated current, climb current, stall current or complete rover current.

Idealized runtime relation:

```text
t_hours = E_usable_Wh/P_average_W
```

Real runtime additionally requires:

```text
usable battery fraction
BMS limits
voltage sag
motor load profile
Jetson + sensors + radios + DC/DC losses
thermal limits
mission duty cycle
```

The DFR-01 release gate remains the planned 40-minute integrated run with voltage/current/temperature logging.

---

## 11. Braking and watchdog geometry

If command authority is removed after timeout `t_timeout` while the rover is moving at speed `v0`, then pre-disable travel is:

```text
d_timeout = v0*t_timeout
```

If physical deceleration magnitude after disable is `a_b`:

```text
t_brake = v0/a_b

d_brake = v0^2/(2*a_b)

d_stop = d_timeout + d_brake
```

The software timeout may be known. The physical `a_b`, controller disable latency and contactor behavior are not yet known.

Therefore stopping distance remains `MAYBE` until measured.

---

## 12. Sensor/navigation trigonometry contract

For a detected target with camera/LiDAR-relative bearing `beta` and range `rho`:

```text
x_target = rho*cos(beta)
y_target = rho*sin(beta)
```

If rover pose is `(x_r,y_r,psi)`:

```text
x_world = x_r + rho*cos(psi + beta)
y_world = y_r + rho*sin(psi + beta)
```

The autonomous 1.5 m stopping condition can be represented geometrically as:

```text
sqrt((x_rover-x_balloon)^2 + (y_rover-y_balloon)^2) <= 1.5 m
```

but the competition condition is based on the rover's **nearest point** to the balloon reference point, not merely rover-center distance. Final simulation therefore needs rover footprint geometry and target/reference geometry.

---

## 13. PKA binding

Each engineering equation shall emit a domain witness with:

```text
input parameters
parameter provenance
source-locked / measured / hypothetical classification
equation/model version
computed output
closure predicate
scope
missing hard parameters
```

Candidate closure law:

```text
verified witness + all hard inputs source-backed/measured + invariant satisfied
    -> bounded POC_CANDIDATE

verified witness + invariant violated
    -> bounded FOC_CANDIDATE

hard input unresolved OR witness outcome changes across admissible unresolved space
    -> MAYBE
```

The equation does not own the verdict. The domain model computes the witness; PKA governs closure.

---

## 14. Freeze condition

**Do not execute the next simulation/stress tranche yet.**

The next tranche is intentionally waiting for additional user-provided hardware/context information. Until then:

```text
symbolic derivation = allowed
parameter classification = allowed
model-contract design = allowed
new numerical pass/fail promotion = HOLD
```
