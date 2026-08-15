# Cars4Mars Project — DFR-01 Engineering Evidence Repository

> **Current state:** DFR-01 is a locked design baseline. Procurement, fabrication, integration, and physical testing are incomplete.
>
> **Truth boundary:** code, calculations, diagrams, and simulations in this repository are engineering artifacts. They are **not** evidence that the physical rover has been built, integrated, tested, or validated.

## Purpose

This repository exists to make the Cars4Mars engineering chain auditable:

**requirement → engineering decision → human owner → code/CAD/calculation → version → test → evidence → decision**

The repository is the technical evidence spine for Kopano Labs' Cars4Mars rover programme. It is intentionally structured so that polished documentation or AI-generated material cannot silently advance an engineering claim.

## DFR-01 locked baseline

| Layer | Selected baseline | Current evidence state |
|---|---|---|
| Mobility | Six-wheel skid-steer + passive rocker-bogie | DESIGNED / LOCKED |
| Actuation | 6 × Rhino IG52 24 V / 60 rpm / 100 W motors; 3 × Cytron MDDS30 | DESIGNED / LOCKED |
| Deterministic control | Teensy 4.1 | DESIGNED / LOCKED |
| Perception | Jetson Orin Nano Super + Intel RealSense D455 + RPLIDAR A2M12 | DESIGNED / LOCKED |
| Power | 24 V 20 Ah LiFePO4; BMS; 60 A fuse; contactor; E-stop; separate logic rails | DESIGNED / LOCKED |
| Communications | Local Wi-Fi for command/video; RFM95W LoRa heartbeat/fail-stop only | DESIGNED / LOCKED |
| Payload | 350 × 300 × 180 mm low central tray; up to 1 kg mission object | DESIGNED / LOCKED |
| Mass | 28 kg BOM target; 30 kg engineering load case; 40 kg competition maximum | DESIGNED / LOCKED |

## Safety authority

The safety/control boundary is non-negotiable:

- The **Jetson may propose bounded movement requests**.
- The **Teensy owns deterministic command validation, motor enable, watchdog, and stop response**.
- **No LLM, cloud service, or governance service has direct motor authority**.
- Loss of valid command/heartbeat for more than **500 ms**, invalid input, or E-stop must force **zero velocity** and remove motor enable.

## Evidence ladder

`DESIGNED → FUNDED → ORDERED → RECEIVED → ASSEMBLED → TESTED → VALIDATED`

No state is advanced without a dated artifact. Examples:

- funding instrument / purchase authority
- quotation / purchase order / invoice
- component serial/configuration record
- CAD or drawing release
- source commit / software release
- continuous test footage
- telemetry / measurement sheet
- pass/fail decision

Failures remain part of the record. Corrections create a new versioned decision; they do not delete the earlier failure.

## Minimum reliable mission chain

`POWER → DRIVE → CONTROL → VIDEO → PAYLOAD → DETECTION → AUTONOMY`

Optional complexity is added only after the preceding capability has passed its evidence gate.

## Repository roadmap

The first engineering tranche is intentionally narrow:

1. deterministic safety/control reference model
2. protocol and authority boundaries
3. host-side tests for watchdog, E-stop, invalid input, and bounded commands
4. evidence-record schema and ledger
5. CI that proves the software tests run on every change
6. later: Teensy firmware, Jetson perception, CAD, wiring, BOM/procurement receipts, and physical test records

## AI orchestration disclosure

AI may assist with source synthesis, code proposals, documentation, simulation scaffolding, and review. Every accepted engineering artifact must still have:

- an accountable human owner,
- a version/commit,
- a stated validation level,
- and an appropriate test or physical evidence gate.

**AI output is never physical test evidence.**

## Competition basis

DFR-01 responds to the Cars4Mars African Rover Challenge 2026 requirements. The competition objective is to design, build, and operate a prototype Mars rover. Engineering decisions, rover design, system integration, testing, and competition operation remain the responsibility of registered student team members.

---

**Baseline:** DFR-01 — 02 August 2026  
**Repository initialized:** 15 August 2026  
**Team:** Kopano Labs / Cape Peninsula University of Technology
