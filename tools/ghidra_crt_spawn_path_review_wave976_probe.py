#!/usr/bin/env python3
"""Validate Wave976 CRT spawn/path read-only review artifacts."""

from __future__ import annotations

import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave976-crt-spawn-path-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_crt_spawn_path_review_wave976_2026-05-29.md"
REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"

TARGETS = {
    "0x0055e412": "CRT__SpawnPathVarargsNoEnv_Thunk",
    "0x00564a0b": "CRT__SpawnSearchPathWithFallbackExtensions",
    "0x00564b54": "CRT__SpawnResolvedPathWithBuiltCommandEnv",
    "0x0056a7e7": "CRT__ValidatePathAttributesForOpen",
    "0x0056a936": "CRT__SpawnVe",
    "0x0056ab1f": "CRT__BuildSpawnCommandAndEnv",
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
        tag_text = (row_by_addr(tags, addr) or {}).get("tags", "")
        if "static-reaudit" not in tag_text or "crt-runtime" not in tag_text:
            failures.append(f"tag mismatch for {addr}")
    if len(xrefs) < 8:
        failures.append(f"xref export too small: {len(xrefs)}")
    if len(instructions) < 500:
        failures.append(f"instruction export too small: {len(instructions)}")
    if backup.get("fileCount") != 19 or backup.get("byteCount") != 173804423 or backup.get("hashDiffCount") != 0:
        failures.append("backup summary mismatch")
    for label, text in {"note": read_text(NOTE), "reference": read_text(REF)}.items():
        for token in ("Wave976", "CRT__SpawnSearchPathWithFallbackExtensions", "CRT__SpawnVe"):
            if token not in text:
                failures.append(f"{label} missing {token}")
    return {
        "schema": "ghidra-crt-spawn-path-review-wave976.v1",
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
    parser.add_argument("--out", type=Path, default=BASE / "wave976-crt-spawn-path-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave976 CRT spawn/path review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
