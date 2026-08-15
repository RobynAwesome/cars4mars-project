# AI Orchestration & Engineering Provenance

## Why this file exists

Cars4Mars uses AI as an engineering accelerator. That increases the need for provenance, not the right to make stronger claims.

The registered student team retains responsibility for engineering decisions, rover design, system integration, testing, and competition operation.

## Required provenance chain

**PROMPT / HYPOTHESIS**
↓
**AI PROPOSAL**
↓
**HUMAN DECISION**
↓
**ENGINEERING ARTIFACT**
↓
**COMMIT**
↓
**TEST**
↓
**MEASUREMENT**
↓
**PASS / FAIL**

No arrow in that chain is implied merely because the previous stage exists.

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

1. **Engineering question / hypothesis** — what was being investigated.
2. **AI role** — what the AI actually contributed and, when useful, a prompt summary.
3. **Human decision** — accept / modify / reject / defer, with the reason.
4. **Human owner** — registered student accountable for the decision.
5. **Source basis** — requirement, datasheet, rule, calculation, measurement, or prior baseline.
6. **Engineering artifact** — file, drawing, calculation, code module, test, or decision.
7. **Commit** — immutable version-control reference.
8. **Test** — software/static/bench/integrated result where applicable.
9. **Measurement** — physical evidence required to close the claim.
10. **Pass / fail decision** — final state and test conditions.

A machine-readable starter exists at `evidence/provenance.template.json`.

## State boundary

`PROPOSED -> DESIGNED -> SOFTWARE-TESTED -> BENCH-TESTED -> INTEGRATED-TESTED -> VALIDATED`

No state may be skipped by rhetoric, document polish, diagram quality, code volume, or AI confidence.

## Engineering criticism versus provenance criticism

A useful engineering challenge identifies the assumption or artifact being disputed. Examples:

- "The 26 N.m figure excludes skid-steer scrub and therefore understates required torque."
- "The motor torque-speed curve does not provide sufficient margin at the required wheel speed."
- "The 500 ms watchdog is too slow for the measured stopping distance."
- "The centre of mass is too high for the measured track width and slope case."

"This looks AI-generated" is provenance feedback. It is a legitimate request to expose authorship and validation history, but it is not by itself an engineering falsification. The repository should expose provenance sufficiently that reviewers can move immediately to the technical claim.

## Current repository disclosure

The initial repository scaffold, DFR-01 transcription, deterministic safety reference model, unit-test scaffold, embedded protocol/safety scaffolding, engineering challenge matrix, evidence protocol, and CI configuration were produced with AI assistance on 15 August 2026 under Kholofelo Robyn Rababalela's direction.

**Human engineering review is still required before AI-assisted software artifacts are treated as accepted implementation decisions.**

Passing software tests proves only that the implemented logic behaves as asserted under those test conditions. It does not prove:

- Teensy 4.1 real-time timing on target hardware,
- Cytron MDDS30 behavior,
- Rhino IG52 torque/current/thermal performance,
- contactor opening time,
- E-stop wiring,
- radio range,
- physical rover braking distance,
- centre of mass,
- terrain performance,
- payload retention,
- perception accuracy,
- autonomous mission performance.

Those require corresponding physical integration and test evidence.

## Orchestration principle

**AI expands the hypothesis space. Humans own the decision. Engineering creates the artifact. Tests and measurements decide whether the claim survives reality.**
