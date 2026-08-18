# P-001 — Wheel Interface

Status: **ACTIVE / GENERATED CONCEPT → DIMENSIONING**  
Timestamp: **2026-08-18 19:17 SAST**  
Baseline: **DFR-01**

## Purpose

Build one bounded wheel prototype before attempting the full six-wheel assembly.

The wheel is a subsystem. It must not be treated as a complete axle, rocker-bogie, or rover validation artifact.

## DFR-01 constants

The following values are not being redesigned in P-001:

- rover architecture: six-wheel skid-steer + passive rocker-bogie;
- wheel count: 6;
- wheel diameter baseline: **250 mm**;
- target rover envelope: 700 × 650 × 500 mm;
- engineering load case: 30 kg;
- physical validation remains incomplete.

## Interface model

The current concept separates three responsibilities:

```text
WHEEL BODY
   ↓ removable bolt/screw interface
WHEEL HUB
   ↓ precision shaft/bearing interface
AXLE SHAFT
```

The bare wheel shell is **not** the intended precision bearing surface for the axle shaft.

### Wheel body must provide

- 250 mm outer-diameter reference;
- open-spoke structure;
- a deliberate center mounting face for the wheel hub;
- central clearance/bore for the hub interface;
- removable fastener pattern around the hub mounting face;
- outer tread pockets that can receive replaceable traction inserts.

### Wheel hub — P-002 dependency

The wheel hub will carry the shaft-interface responsibility. P-001 therefore cannot freeze the center bore, hub-face diameter, bolt pitch circle or fastener size until P-002 interface dimensions are proposed together.

## Tread insert experiment

The brown pads in the generated concept are classified as **replaceable traction inserts**.

They are not decorative and they are not yet a final material selection.

### Experiment purpose

1. make contact with rough stones less purely rigid;
2. reduce hard-plastic slip relative to the wheel body alone;
3. test whether pocket spacing sheds or traps stones;
4. allow traction material/geometry changes without reprinting the entire wheel;
5. allow a damaged pad to be replaced independently.

### Initial material candidates

| Part | First prototype candidate | Evidence state |
|---|---|---|
| wheel body | PLA or PETG | candidate only |
| traction insert | TPU or another rubber-like material | candidate only |
| later stronger wheel body | nylon or reinforced filament | future candidate |

Printer/material availability, dimensional stability and actual traction testing decide promotion. No final wheel material is locked by this file.

## Unknowns that MUST stay TBD until measured/proposed

- wheel width;
- spoke count and exact spoke thickness;
- hub mounting-face diameter;
- center-bore diameter;
- bolt/screw count;
- bolt pitch-circle diameter;
- fastener diameter and thread;
- axle-shaft diameter;
- bearing ID/OD/width;
- tread-pocket count;
- tread-pocket width/length/depth;
- insert retention method;
- print tolerance/clearance.

A generated image may suggest geometry but may not supply a hidden dimension.

## Three-view packet

Before CAD release, capture:

1. **front view** — wheel diameter, spoke geometry, hub mounting face, center bore, bolt pattern;
2. **side view** — wheel width, tread-pocket depth, hub interface depth;
3. **top/section view** — center stack-up and how hub/fasteners/shaft pass through the wheel interface.

Also attach the rough hand sketch. Mark every unknown dimension `TBD`.

## Small-piece strategy

Do not start by printing a full 250 mm wheel if the hub interface is still uncertain.

Recommended progression:

```text
P-001A dimension interface
  -> P-001B print small hub/bolt-pattern coupon
  -> measure coupon
  -> revise fit/clearance
  -> P-001C print reduced or partial tread-pocket coupon
  -> compare rigid vs flexible insert retention
  -> P-001D release first full wheel prototype
```

This minimizes material waste and turns each change into a falsifiable experiment.

## Acceptance gates

### P-001A — dimensioned interface

PASS only when the design team has:

- rough sketch;
- front, side and top/section views;
- proposed wheel width;
- proposed hub-face diameter;
- proposed center bore;
- proposed bolt pattern;
- proposed tread-pocket dimensions;
- named prototype printer/process and available material.

### P-001B — interface coupon

PASS only when:

- printed/cut part has a revision ID;
- center bore and bolt spacing are measured;
- hub/fastener fit is recorded;
- failures remain visible in the evidence ledger.

### P-001C — tread coupon

PASS only when:

- rigid body pocket can retain the flexible insert;
- insert can be removed/replaced intentionally;
- obvious stone-trapping or pocket fracture is recorded as FAIL/REVISE, not hidden.

### P-001D — first full wheel

The full wheel remains a **prototype** until fit, rolling and load tests exist.

## KPGS progression

```text
APU = YELLOW
reason = critical dimensions are TBD
CRUD mutation = HOLD
SWFUS distribution = NOT_REACHED
```

The concept becomes GREEN only after bounded physical evidence supports the requested state transition.

## Generated artifacts admitted for design discussion

- Cars4Mars Axle Module Concept Board;
- Cars4Mars Axle Module Assembly Guide;
- Cars4Mars Part 1 — Wheel Concept Poster.

All three remain **generated design references**, not CAD or physical evidence.
