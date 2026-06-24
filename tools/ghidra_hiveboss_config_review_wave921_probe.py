#!/usr/bin/env python3
"""Validate Wave921 HiveBoss config read-only review artifacts."""

from __future__ import annotations

import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave921-hiveboss-config-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_hiveboss_config_review_wave921_2026-05-27.md"
DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HiveBoss.cpp" / "_index.md"

TARGETS = {
    "0x0047fe30": "CHiveBoss__Init",
    "0x004804c0": "CHiveBoss__SetVar",
    "0x00497090": "CMCHiveBoss__Constructor",
    "0x00497110": "CMCHiveBoss__ScalarDeletingDestructor",
    "0x004976d0": "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0",
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
    index = read_tsv(BASE / "decompile" / "index.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")
    for addr, name in TARGETS.items():
        if (row_by_addr(metadata, addr) or {}).get("name") != name:
            failures.append(f"metadata mismatch for {addr}")
        if (row_by_addr(index, addr) or {}).get("name") != name:
            failures.append(f"decompile mismatch for {addr}")
        tag_text = (row_by_addr(tags, addr) or {}).get("tags", "")
        if "hiveboss" not in tag_text and "cmchiveboss" not in tag_text:
            failures.append(f"tag mismatch for {addr}")
    if len(instructions) < 900:
        failures.append(f"instruction export too small: {len(instructions)}")
    if len(xrefs) < 5:
        failures.append(f"xref export too small: {len(xrefs)}")
    if backup.get("files") != 19 or backup.get("bytes") != 173247367:
        failures.append("backup summary mismatch")
    for label, text in {"note": read_text(NOTE), "doc": read_text(DOC)}.items():
        for token in ("Wave921", "CHiveBoss__SetVar", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0"):
            if token not in text:
                failures.append(f"{label} missing {token}")
    return {"schema": "ghidra-hiveboss-config-review-wave921.v1", "status": "PASS" if not failures else "FAIL", "targets": TARGETS, "mutatedTargets": 0, "instructionRows": len(instructions), "xrefRows": len(xrefs), "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave921-hiveboss-config-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave921 HiveBoss config review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
