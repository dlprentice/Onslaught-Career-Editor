#!/usr/bin/env python3
"""Validate Wave979 Component factory/lifecycle read-only review artifacts."""

from __future__ import annotations

import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave979-component-factory-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_component_factory_lifecycle_review_wave979_2026-05-29.md"
REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"

TARGETS = {
    "0x00427b80": "CComponent__VFunc_09_00427b80",
    "0x00427cd0": "CComponent__CreateSubComponent1",
    "0x00427d50": "CComponent__CreateSubComponent2",
    "0x00427dd0": "CComponent__CreateWeaponComponent",
    "0x00427f90": "CComponentBomberAI__scalar_deleting_dtor",
    "0x00427fb0": "CComponentBomberAI__dtor_base",
    "0x00428050": "CFenrirMainGunAI__scalar_deleting_dtor",
    "0x00428070": "CFenrirMainGunAI__dtor_base",
    "0x00428e80": "CComponentAI__ClearReaderIfTargetDestroyedThenForward",
}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace") if path.is_file() else ""

def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str] | None:
    want = addr.lower().replace("0x", "")
    for row in rows:
        got = (row.get("address") or row.get("target_addr") or "").lower().replace("0x", "")
        if got == want:
            return row
    return None

def build_report() -> dict[str, object]:
    failures = []
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    index = read_tsv(BASE / "decompile" / "index.tsv")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")
    for addr, name in TARGETS.items():
        if (row_by_addr(metadata, addr) or {}).get("name") != name:
            failures.append(f"metadata mismatch for {addr}")
        if (row_by_addr(index, addr) or {}).get("name") != name:
            failures.append(f"decompile mismatch for {addr}")
        if (row_by_addr(tags, addr) or {}).get("status") != "OK":
            failures.append(f"tag row missing for {addr}")
    if len(xrefs) < 14:
        failures.append(f"xref export too small: {len(xrefs)}")
    if len(instructions) < 400:
        failures.append(f"instruction export too small: {len(instructions)}")
    if backup.get("fileCount") != 19 or backup.get("byteCount") != 173804423 or backup.get("hashDiffCount") != 0:
        failures.append("backup summary mismatch")
    for label, text in {"note": read_text(NOTE), "reference": read_text(REF)}.items():
        for token in ("Wave979", "CComponent__CreateWeaponComponent", "CFenrirMainGunAI__dtor_base"):
            if token not in text:
                failures.append(f"{label} missing {token}")
    return {
        "schema": "ghidra-component-factory-lifecycle-review-wave979.v1",
        "status": "PASS" if not failures else "FAIL",
        "targets": TARGETS,
        "mutatedTargets": 0,
        "instructionRows": len(instructions),
        "xrefRows": len(xrefs),
        "failures": failures,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave979-component-factory-lifecycle-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave979 Component factory/lifecycle review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
