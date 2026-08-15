# Procurement Evidence

This directory is reserved for real procurement artifacts linked to DFR-01 BOM items.

Acceptable evidence includes:

- supplier quotation
- approved funding instrument / purchase authority
- purchase order
- invoice
- payment receipt
- verified donor commitment
- delivery note
- dated received-component photograph
- serial number / model / configuration record

## Current declaration

No procurement artifact is added here unless the team actually possesses it.

A funding discussion, verbal promise, render, AI answer, or planned budget is **not** purchase evidence.

When evidence is added, create a corresponding `evidence/ledger.ndjson` record linking:

- the BOM item,
- supplier,
- date,
- amount where appropriate,
- artifact path,
- owner,
- and next build gate.

Sensitive financial or personal information should be redacted before a public artifact is committed. Preserve the unredacted original privately if needed for audit.
