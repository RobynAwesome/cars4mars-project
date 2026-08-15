#!/usr/bin/env python3
"""Validate that engineering challenge answers expose evidence gaps explicitly."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "engineering" / "challenge_matrix.json"

REQUIRED_FIELDS = {
    "id",
    "question",
    "status",
    "answer",
    "artifact",
    "test",
    "missing_evidence",
    "next_gate",
}

ALLOWED_STATUS = {
    "calculated_lower_bound",
    "selection_rationale_incomplete",
    "design_rationale",
    "software_tested_not_hardware_validated",
    "unknown",
    "design_intent_not_physical_validation",
    "unknown_measured_value",
    "unknown_requires_fmea_and_test",
}


def main() -> int:
    try:
        payload = json.loads(MATRIX.read_text(encoding="utf-8"))
        questions = payload.get("questions")
        if not isinstance(questions, list) or not questions:
            raise ValueError("challenge matrix must contain a non-empty questions list")

        seen: set[str] = set()
        for item in questions:
            missing = REQUIRED_FIELDS - item.keys()
            if missing:
                raise ValueError(f"challenge item missing {sorted(missing)}: {item}")
            if item["id"] in seen:
                raise ValueError(f"duplicate challenge id: {item['id']}")
            seen.add(item["id"])
            if item["status"] not in ALLOWED_STATUS:
                raise ValueError(f"{item['id']}: unsupported status {item['status']!r}")
            if not str(item["missing_evidence"]).strip():
                raise ValueError(f"{item['id']}: missing_evidence must be explicit")
            if not str(item["next_gate"]).strip():
                raise ValueError(f"{item['id']}: next_gate must be explicit")

        print(f"Engineering challenge matrix OK: {len(questions)} questions")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"CHALLENGE MATRIX VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
