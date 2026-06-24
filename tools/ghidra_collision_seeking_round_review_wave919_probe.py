#!/usr/bin/env python3
"""Validate Wave919 collision-seeking round read-only review artifacts."""

from __future__ import annotations

import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave919-collision-seeking-round-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_collision_seeking_round_review_wave919_2026-05-27.md"
DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CollisionSeekingRound.cpp" / "_index.md"

TARGETS = {
    "0x00425a10": "CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags",
    "0x00425c60": "CCollisionSeekingRound__FilterCollisionCandidateByTrajectory",
    "0x00426900": "CCollisionSeekingRound__CheckCollisionFlags",
    "0x00426920": "CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance",
    "0x00426a00": "CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
    "0x00426a20": "CCollisionSeekingRound__MarkDelayedCollisionReady",
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
        if (row_by_addr(tags, addr) or {}).get("status") != "OK":
            failures.append(f"tag row missing for {addr}")
    if len(instructions) < 240:
        failures.append(f"instruction export too small: {len(instructions)}")
    for label, text in {"note": read_text(NOTE), "doc": read_text(DOC)}.items():
        for token in ("Wave919", "CCollisionSeekingRound__FilterCollisionCandidateByTrajectory", "CCollisionSeekingRound__MarkDelayedCollisionReady"):
            if token not in text:
                failures.append(f"{label} missing {token}")
    return {"schema": "ghidra-collision-seeking-round-review-wave919.v1", "status": "PASS" if not failures else "FAIL", "targets": TARGETS, "mutatedTargets": 0, "instructionRows": len(instructions), "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave919-collision-seeking-round-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave919 collision-seeking round review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
