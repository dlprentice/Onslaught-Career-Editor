#!/usr/bin/env python3
"""Validate Wave981 CFEPDebriefing boundary recovery artifacts."""

from __future__ import annotations

import argparse, csv, json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave981-cfepdebriefing-boundary-review"
QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfepdebriefing_boundary_recovery_wave981_2026-05-29.md"
DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPDebriefing.cpp" / "_index.md"

TARGETS = {
    "0x00456780": "CFEPDebriefing__Initialize",
    "0x00456850": "CFEPDebriefing__Shutdown",
    "0x00456930": "CFEPDebriefing__Process",
    "0x004568a0": "CFEPDebriefing__ButtonPressed",
    "0x00456d40": "CFEPDebriefing__RenderPreCommon",
    "0x00456dd0": "CFEPDebriefing__Render",
    "0x00457cf0": "CFEPDebriefing__TransitionNotification",
}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "") if path.is_file() else ""

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

def require_log_tokens(path: Path, failures: list[str], label: str, *tokens: str) -> None:
    text = read_text(path)
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing {token}")

def build_report() -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    index = read_tsv(BASE / "post-decompile" / "index.tsv")
    instructions = read_tsv(BASE / "post-instructions.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    vtables = read_tsv(BASE / "post-vtables.tsv")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")
    queue = json.loads(read_text(QUEUE_REPORT) or "{}")

    for addr, name in TARGETS.items():
        if (row_by_addr(metadata, addr) or {}).get("name") != name:
            failures.append(f"metadata mismatch for {addr}")
        if (row_by_addr(index, addr) or {}).get("name") != name:
            failures.append(f"decompile mismatch for {addr}")
        if (row_by_addr(tags, addr) or {}).get("status") != "OK":
            failures.append(f"tag row missing for {addr}")

    require_log_tokens(BASE / "apply-dry.log", failures, "dry log", "would_create=5", "bad=0")
    require_log_tokens(BASE / "apply.log", failures, "apply log", "updated=5", "created=5", "signature_updated=5", "bad=0")
    require_log_tokens(BASE / "apply-final-dry.log", failures, "final dry log", "updated=0", "skipped=5", "bad=0")

    if len(instructions) < 1500:
        failures.append(f"instruction export too small: {len(instructions)}")
    if len(xrefs) < 7:
        failures.append(f"xref export too small: {len(xrefs)}")
    if len(vtables) < 16:
        failures.append(f"vtable export too small: {len(vtables)}")
    if backup.get("fileCount") != 19 or backup.get("byteCount") != 173837191 or backup.get("hashDiffCount") != 0:
        failures.append("backup summary mismatch")
    quality = queue.get("qualitySignals") or {}
    if queue.get("totalFunctions") != 6222 or quality.get("commentlessFunctionCount") != 0:
        failures.append("queue summary mismatch")

    for label, text in {"note": read_text(NOTE), "doc": read_text(DOC)}.items():
        for token in ("Wave981", "CFEPDebriefing__Render", "CFEPDebriefing__TransitionNotification"):
            if token not in text:
                failures.append(f"{label} missing {token}")

    return {
        "schema": "ghidra-cfepdebriefing-boundary-recovery-wave981.v1",
        "status": "PASS" if not failures else "FAIL",
        "targets": TARGETS,
        "mutationStatus": "function-boundary recovery",
        "instructionRows": len(instructions),
        "xrefRows": len(xrefs),
        "vtableRows": len(vtables),
        "failures": failures,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave981-cfepdebriefing-boundary-recovery.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave981 CFEPDebriefing boundary recovery probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
