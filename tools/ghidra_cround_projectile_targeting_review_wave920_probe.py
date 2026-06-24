#!/usr/bin/env python3
"""Validate Wave920 CRound projectile/targeting read-only review artifacts."""

from __future__ import annotations

import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave920-cround-projectile-targeting-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cround_projectile_targeting_review_wave920_2026-05-27.md"
DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md"

TARGETS = {
    "0x004d9ef0": "CRound__UpdateRoundAndTriggerLaunchEffect",
    "0x004daab0": "CRound__SetTargetReaderIfAllowed",
    "0x004daba0": "CRound__FindNearbyHostileWithinProjectileRadius",
    "0x004dac90": "CRound__SelectBestTargetReaderAndSyncAimState",
    "0x004db090": "CRound__GetPresetScalarByConfigName",
    "0x004db150": "CRound__SpawnConfiguredProjectile",
    "0x004db630": "CRound__ArmProjectileAndSpawnTrailEffect",
    "0x004d8410": "CRound__Init",
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
        if "round" not in tag_text or "static-reaudit" not in tag_text:
            failures.append(f"tag mismatch for {addr}")
    if len(instructions) < 1200:
        failures.append(f"instruction export too small: {len(instructions)}")
    for label, text in {"note": read_text(NOTE), "doc": read_text(DOC)}.items():
        for token in ("Wave920", "CRound__SpawnConfiguredProjectile", "CRound__FindNearbyHostileWithinProjectileRadius"):
            if token not in text:
                failures.append(f"{label} missing {token}")
    return {"schema": "ghidra-cround-projectile-targeting-review-wave920.v1", "status": "PASS" if not failures else "FAIL", "targets": TARGETS, "mutatedTargets": 0, "instructionRows": len(instructions), "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave920-cround-projectile-targeting-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave920 CRound projectile/targeting review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
