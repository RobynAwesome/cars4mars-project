# Cars4Mars Hardware Evidence Receipt — 2026-08-16

**Baseline:** DFR-01  
**Branch:** `agent/hardware-math-staging`  
**State:** `STAGED_NOT_RETESTED`  
**Simulation gate:** **FROZEN**

This receipt records primary-source hardware facts that can be promoted into the parameter registry without promoting the rover to physical validation.

## Source-backed closures

### Cytron MDDS30

Primary source: Cytron product documentation.

Source-backed envelope:
- 7–35 V DC brushed-motor supply;
- 30 A continuous per channel;
- 80 A peak per channel for 1 second;
- 18 kHz switching;
- current-limit, thermal, under-voltage and over-voltage protection;
- no reverse-polarity protection on the motor-supply input.

Still unresolved for DFR-01 integration:
- actual DIP/control mode;
- effective current-limit/protection behavior with the selected wiring;
- cooling installation;
- channel/motor allocation under six-motor load.

### NVIDIA Jetson Orin Nano Super

Primary source: NVIDIA Jetson documentation.

Source-backed reference power envelope includes 7 W, 15 W and 25 W modes for the Orin Nano Super lineage. This is a module/reference-power statement, **not** the rover DC/DC branch budget.

Still unresolved:
- configured rover power mode;
- DC/DC efficiency;
- actual branch current;
- thermal margin under perception workload.

### SLAMTEC RPLIDAR A2M12

Primary source: SLAMTEC A2 specification.

Source-backed:
- 5 V;
- 450–600 mA;
- 2.25–3 W;
- 0.2–12 m measuring range;
- 16 kHz sampling;
- nominal 10 Hz rotation, 5–15 Hz range;
- 0.225° angular resolution;
- 360° angular range;
- UART 256000 baud.

Still unresolved:
- final pose/occlusion;
- converter efficiency;
- measured in-rover voltage/current.

### RealSense D455

Primary source: RealSense D455 product specification.

Source-backed:
- 87° × 58° depth FOV;
- 0.6–6 m ideal range;
- global shutter;
- manufacturer depth-error claim below 2% at 4 m under stated conditions.

Still unresolved:
- final mounting pose and post-mount occlusion;
- USB branch power/current;
- measured bandwidth/power in the rover.

### Teensy 4.1

Primary source: PJRC Teensy 4.1 documentation.

Source-backed:
- 5 V VIN when USB power is not used;
- 3.3 V logic/regulator rail;
- recommended maximum 250 mA for external loads on the 3.3 V pin.

Still unresolved:
- actual controller current with DFR-01 firmware/peripherals;
- VUSB/VIN isolation choice;
- peripheral loading on the 3.3 V rail.

## Deliberately not closed

The exact Rhino IG52 24 V / 60 rpm / 100 W motor purchase has not yet been matched to an authoritative manufacturer/supplier torque-speed/current/thermal document. Retailer candidate specifications are not promoted into the canonical registry.

The following also remain measurement/CAD integration gates:
- battery/BMS peak and continuous limits plus pack sag/internal resistance;
- wheelbase, track, rocker/bogie geometry and ground clearance;
- centre of mass with and without payload;
- tyre traction, rolling resistance and skid-turn scrub;
- payload retention geometry and displacement limit;
- contactor/motor disable latency and coast/braking profile;
- full branch power budget;
- final sensor poses/FOV after integration.

## Governance result

```text
PRIMARY SOURCE EVIDENCE -> REGISTRY UPDATE
                        -> UNKNOWN SET REDUCED
                        -> NO NEW STRESS TEST
                        -> NO PHYSICAL CLAIM PROMOTION
```

`next_tests_enabled` remains `false`.
