# AI Orchestration & Engineering Provenance

## Why this file exists

Cars4Mars uses AI as an engineering accelerator. That increases the need for provenance, not the right to make stronger claims.

The registered student team retains responsibility for engineering decisions, rover design, system integration, testing, and competition operation.

## Authority rule

AI may:

- synthesize source material,
- propose architectures,
- draft code,
- generate test scaffolding,
- help review calculations,
- generate labelled design visualisations,
- organize evidence.

AI may **not**:

- turn a design into a physical test result,
- declare a component purchased without procurement evidence,
- declare hardware assembled without dated build evidence,
- promote a failed test to a pass,
- silently change the DFR-01 architecture,
- directly actuate rover motors,
- replace accountable student engineering ownership.

## Required provenance per accepted artifact

Every material AI-assisted engineering artifact should record:

1. **Artifact** — file, drawing, calculation, code module, test, or decision.
2. **AI role** — what the AI actually contributed.
3. **Human owner** — registered student accountable for accepting/rejecting it.
4. **Source basis** — requirement, datasheet, rule, calculation, or prior baseline.
5. **Review state** — pending / reviewed / rejected / superseded.
6. **Verification level** — design-only / software-tested / bench-tested / subsystem-tested / integrated-tested.
7. **Commit or evidence ID** — immutable reference.

## Current repository disclosure

The initial repository scaffold, DFR-01 transcription, deterministic safety reference model, unit-test scaffold, evidence protocol, and CI configuration were produced with AI assistance on 15 August 2026 under Kholofelo Robyn Rababalela's direction.

**Human engineering review is still required before these software artifacts are treated as accepted implementation decisions.**

Passing host-side software tests will prove only that the reference model behaves as asserted under those test conditions. It will not prove:

- Teensy 4.1 firmware timing,
- Cytron MDDS30 behavior,
- Rhino IG52 motor response,
- contactor opening time,
- E-stop wiring,
- radio range,
- physical rover braking distance,
- terrain performance,
- payload retention,
- perception accuracy,
- autonomous mission performance.

Those require the corresponding physical integration and test evidence.

## Orchestration principle

**AI expands the hypothesis space. Engineering constrains it. Evidence decides what becomes a validated claim.**
