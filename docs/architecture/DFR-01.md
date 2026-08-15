# DFR-01 — Locked System Architecture

**Baseline date:** 02 August 2026  
**Repository transcription date:** 15 August 2026  
**Status:** DESIGN-LOCKED; physical validation incomplete

This file translates the submitted DFR-01 design baseline into a version-controlled engineering artifact. It does **not** claim that the hardware has been procured, assembled, integrated, or tested.

## System layers

| Layer | Selected design | Engineering role | Validation state |
|---|---|---|---|
| Mobility | Six wheels; skid-steer; passive rocker-bogie | Maintain contact and allow differential steering over uneven terrain | Designed |
| Actuation | 6 × Rhino IG52; 3 × Cytron MDDS30 | Bidirectional wheel actuation | Designed |
| Control | Teensy 4.1 | Deterministic command parsing, motor enable, watchdog and safety response | Designed |
| Perception | Jetson Orin Nano Super; RealSense D455; RPLIDAR A2M12 | Camera/range processing and planned autonomy | Designed |
| Power | 24 V 20 Ah LiFePO4; BMS; 60 A fuse; contactor; E-stop; logic rails | Independent power with protected shutdown | Designed |
| Communications | Local Wi-Fi; RFM95W LoRa heartbeat/fail-stop | Local command/video and narrow safety liveness path | Designed |
| Evidence/governance | Versioned repository + evidence ledger | Preserve claims, tests, failures and decisions | Repository implementation started |

## Authority boundary

```text
 RealSense D455 ----\
                     +--> Jetson Orin Nano Super --> bounded velocity request --+
 RPLIDAR A2M12 -----/                                                      |
                                                                            v
 Operator command ----------------------------------------------------> Teensy 4.1
                                                                            |
 LoRa heartbeat/fail-stop ----------------------------------------------->  |
                                                                            v
                                                          command validation / watchdog
                                                                            |
                                                              motor-enable authority
                                                                            |
                                                                            v
                                                                3 x Cytron MDDS30
                                                                            |
                                                                            v
                                                                 6 x Rhino IG52
```

### Non-negotiable rule

The Jetson, an LLM, a cloud service, or an evidence/governance service must **not** be able to bypass the Teensy/local power-stage safety boundary.

The perception layer may propose a bounded movement request. The deterministic control layer decides whether the request is admissible and whether the motor-enable path remains active.

## Safety behavior to implement and prove

1. **E-stop:** forces zero velocity and removes motor enable.
2. **Invalid command:** forces zero velocity and removes motor enable.
3. **Command lease:** a nonzero motion command may not remain active indefinitely without a fresh valid command.
4. **Loss of liveness:** more than 500 ms without valid command/heartbeat activity forces zero velocity and removes motor enable.
5. **Perception loss:** manual control and local stop must remain possible when the Jetson is unavailable.
6. **No cloud actuation:** no remote cloud/LLM path may directly command the motor drivers.

## Mechanical / mission anchors

- target envelope: **700 × 650 × 500 mm**
- BOM mass target: **28 kg**
- conservative engineering load case: **30 kg**
- competition rover mass ceiling: **40 kg**
- wheels: **6 × 250 mm**
- payload tray: **350 × 300 × 180 mm**, low central mount
- mission object: **up to 1 kg**
- 45° design check at 30 kg: approximately **208 N** downslope force and **26 N·m** ideal total wheel torque at 125 mm wheel radius, before losses

These are design inputs/calculations, not as-built measurements.

## Evidence gates

The baseline moves toward physical validation in this order:

1. final BOM + approved procurement evidence
2. received component/configuration records
3. protected power wiring + controlled shutdown
4. loaded forward/reverse
5. skid/pivot turning
6. E-stop and loss-of-link tests
7. command/video range tests
8. 1 kg payload retention
9. bumps/ramp/terrain
10. perception tests
11. autonomous sequence
12. integrated endurance run

Each gate must produce a dated artifact and pass/fail decision.
