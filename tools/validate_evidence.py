#!/usr/bin/env python3
"""Validate Cars4Mars repository evidence metadata using only stdlib."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "evidence" / "ledger.ndjson"
REQUIREMENTS = ROOT / "engineering" / "requirements.json"

REQUIRED_LEDGER_FIELDS = {
    "ledger_id",
    "timestamp",
    "subsystem",
    "owner",
    "baseline",
    "claim",
    "state",
    "evidence",
    "conditions",
    "result",
    "decision",
    "next_gate",
    "ai_involvement",
}

ALLOWED_STATES = {
    "planned",
    "designed",
    "funded",
    "ordered",
    "received",
    "assembled",
    "tested",
    "failed",
    "redesigned",
    "validated",
}

REQUIRED_REQUIREMENT_FIELDS = {
    "id",
    "name",
    "requirement",
    "owner_layer",
    "design_state",
    "physical_gate",
    "validation_state",
}


def fail(message: str) -> None:
    raise ValueError(message)


def validate_ledger() -> int:
    if not LEDGER.exists():
        fail(f"missing ledger: {LEDGER}")

    ids: set[str] = set()
    count = 0
    for line_no, raw in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        count += 1
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"ledger line {line_no}: invalid JSON: {exc}")

        missing = REQUIRED_LEDGER_FIELDS - record.keys()
        if missing:
            fail(f"ledger line {line_no}: missing fields: {sorted(missing)}")

        ledger_id = record["ledger_id"]
        if ledger_id in ids:
            fail(f"duplicate ledger_id: {ledger_id}")
        ids.add(ledger_id)

        state = record["state"]
        if state not in ALLOWED_STATES:
            fail(f"{ledger_id}: unsupported state {state!r}")

        evidence = record["evidence"]
        if not isinstance(evidence, list):
            fail(f"{ledger_id}: evidence must be a list")

        if state in {"tested", "validated"} and not evidence:
            fail(f"{ledger_id}: state {state!r} requires direct evidence")

        ai = record["ai_involvement"]
        if not isinstance(ai, dict) or "used" not in ai or "human_review" not in ai:
            fail(f"{ledger_id}: ai_involvement must disclose used and human_review")

    if count == 0:
        fail("ledger contains no records")
    return count


def validate_requirements() -> int:
    if not REQUIREMENTS.exists():
        fail(f"missing requirements file: {REQUIREMENTS}")

    payload = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    if payload.get("baseline") != "DFR-01":
        fail("requirements baseline must be DFR-01")

    requirements = payload.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        fail("requirements must be a non-empty list")

    ids: set[str] = set()
    for item in requirements:
        missing = REQUIRED_REQUIREMENT_FIELDS - item.keys()
        if missing:
            fail(f"requirement missing fields {sorted(missing)}: {item}")
        req_id = item["id"]
        if req_id in ids:
            fail(f"duplicate requirement id: {req_id}")
        ids.add(req_id)

        state = item["validation_state"]
        if state not in {"design_only", "software_model_only", "bench_tested", "integrated_tested", "validated"}:
            fail(f"{req_id}: unknown validation_state {state!r}")

    return len(requirements)


def main() -> int:
    try:
        ledger_count = validate_ledger()
        requirement_count = validate_requirements()
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"EVIDENCE VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"Evidence ledger OK: {ledger_count} records")
    print(f"Requirements trace OK: {requirement_count} requirements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
