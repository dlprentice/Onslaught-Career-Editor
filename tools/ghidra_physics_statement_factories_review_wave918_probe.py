#!/usr/bin/env python3
"""Validate Wave918 PhysicsScript factory read-only review artifacts."""

from __future__ import annotations

import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave918-physics-statement-factories-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_statement_factories_review_wave918_2026-05-27.md"
DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"

TARGETS = {
    "0x00431bb0": "CPhysicsScriptStatements__CreateStatementType2",
    "0x00434300": "CPhysicsScriptStatements__CreateStatementType3",
    "0x00435010": "CPhysicsScriptStatements__CreateStatementType4",
    "0x00437490": "CPhysicsScriptStatements__CreateStatementType5",
    "0x00439b40": "CPhysicsScriptStatements__CreateStatementType6",
    "0x0043a860": "CPhysicsScriptStatements__CreateStatementType7",
    "0x0043b990": "CPhysicsScriptStatements__CreateStatementType8",
    "0x0043c0b0": "CPhysicsScriptStatements__CreateStatementType9",
    "0x0043c500": "CPhysicsScriptStatements__CreateStatementType10",
    "0x0043dcd0": "CPhysicsScriptStatements__CreateStatementType11",
    "0x0043ddc0": "CPhysicsScriptStatements__CreateStatementType12",
    "0x0043e310": "CPhysicsScriptStatements__CreateStatementType13",
    "0x0043e400": "CPhysicsScriptStatements__CreateStatementType14",
    "0x0043e540": "CPhysicsScriptStatements__CreateStatementType15",
}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""

def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str] | None:
    want = addr.lower().replace("0x", "")
    for row in rows:
        got = (row.get("address") or "").lower().replace("0x", "")
        if got == want:
            return row
    return None

def build_report() -> dict[str, object]:
    failures = []
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    index = read_tsv(BASE / "decompile" / "index.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    for addr, name in TARGETS.items():
        if (row_by_addr(metadata, addr) or {}).get("name") != name:
            failures.append(f"metadata mismatch for {addr}")
        if (row_by_addr(index, addr) or {}).get("name") != name:
            failures.append(f"decompile mismatch for {addr}")
        tag_text = (row_by_addr(tags, addr) or {}).get("tags", "")
        if "value-factory" not in tag_text or "static-reaudit" not in tag_text:
            failures.append(f"tag mismatch for {addr}")
    if len(instructions) < 3000:
        failures.append(f"instruction export too small: {len(instructions)}")
    for label, text in {"note": read_text(NOTE), "doc": read_text(DOC)}.items():
        for token in ("Wave918", "CPhysicsScriptStatements__CreateStatementType2", "CPhysicsScriptStatements__CreateStatementType15"):
            if token not in text:
                failures.append(f"{label} missing {token}")
    return {"schema": "ghidra-physics-statement-factories-review-wave918.v1", "status": "PASS" if not failures else "FAIL", "targets": TARGETS, "mutatedTargets": 0, "instructionRows": len(instructions), "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave918-physics-statement-factories-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave918 physics statement factories review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
