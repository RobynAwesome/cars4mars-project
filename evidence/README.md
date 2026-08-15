# Evidence Ledger

This directory is the audit trail for Cars4Mars engineering state transitions.

## Rule

A claim does not advance because a report, render, AI answer, meeting, promise, or funding discussion sounds convincing. It advances only when the required artifact exists.

## States

`planned → designed → funded → ordered → received → assembled → tested → failed/redesigned → validated`

Not every record must pass through every state, but **tested** and **validated** require direct test evidence appropriate to the claim.

## Minimum record fields

- `ledger_id`
- `timestamp`
- `subsystem`
- `owner`
- `baseline`
- `claim`
- `state`
- `evidence`
- `conditions`
- `result`
- `decision`
- `next_gate`
- `ai_involvement`

## Procurement evidence

Real quotations, purchase orders, invoices, donor commitments, receipts, serial numbers, and delivery records belong under `evidence/procurement/` or are referenced from the ledger.

**Never fabricate a receipt or imply purchase when no purchase evidence exists.**

## Test evidence

A test record should capture, where applicable:

- date/time
- hardware configuration
- software commit SHA
- surface / slope / distance
- payload
- battery state
- duration
- measurement instrument
- raw footage / telemetry location
- observed values
- pass/fail
- anomaly
- decision and next action

Failures stay in the ledger. A correction references the failed record and creates a new versioned decision.
