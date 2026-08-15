# Cars4Mars AI Provenance Protocol

AI use is not hidden and AI output is not self-validating.

The required provenance chain is:

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

## Governance rule

A generated statement, diagram, calculation, code fragment, CAD suggestion, component recommendation, or test plan may enter the repository as a proposal or designed artifact. It may not become a validated engineering claim merely because it is coherent, polished, or passes a language-model review.

## Required provenance fields

For any material AI-assisted engineering contribution, preserve:

- hypothesis or engineering question;
- AI role and, where useful, the prompt or prompt summary;
- human decision: accept, modify, reject, or defer;
- accountable human/team owner;
- resulting repository artifact and commit;
- software/static-analysis test where applicable;
- physical measurement or inspection required to close the claim;
- final pass/fail decision and conditions.

## State boundary

The following are deliberately different states:

`PROPOSED -> DESIGNED -> SOFTWARE-TESTED -> BENCH-TESTED -> INTEGRATED-TESTED -> VALIDATED`

No state may be skipped by rhetoric.

## Criticism protocol

A useful engineering challenge identifies the assumption or artifact being disputed. Examples:

- "The 26 N.m figure excludes skid-steer scrub and therefore understates required torque."
- "The selected motor has insufficient rated torque at the required speed according to the manufacturer curve."
- "The 500 ms watchdog is too slow for the measured stopping distance."
- "The centre of mass is too high for the measured track width and slope case."

"This looks AI-generated" is provenance feedback, not an engineering falsification. The repository should make provenance visible enough that reviewers can move directly to the technical question.

## Cars4Mars truth rule

**AI expands the hypothesis space. Humans own the decision. Engineering creates the artifact. Tests and measurements decide whether the claim survives reality.**
