#!/usr/bin/env python3
"""Validate Wave975 CFEPBriefing boundary recovery artifacts."""

from __future__ import annotations

import argparse, csv, json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave975-frontend-briefing-state-review"
QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_LOG = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave975.log"
QUEUE_PROBE_LOG = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave975_queue_probe.log"
NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_briefing_state_review_wave975_2026-05-28.md"
DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
WAVE_TOTAL = 6217

TARGETS = {
    "0x00451b70": "CFEPBriefing__Init",
    "0x00451b80": "CFEPBriefing__Process",
    "0x00451c20": "CFEPBriefing__ButtonPressed",
    "0x00451c90": "CFEPBriefing__RenderPreCommon",
    "0x00451d50": "CFEPBriefing__Render",
    "0x00452430": "CFEPBriefing__TransitionNotification",
    "0x00452460": "CFEPBriefing__ActiveNotification",
}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace") if path.is_file() else ""

def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def read_json(path: Path) -> dict[str, object]:
    text = read_text(path)
    return json.loads(text) if text else {}

def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str] | None:
    want = addr.lower().replace("0x", "")
    for row in rows:
        got = (row.get("address") or row.get("target_addr") or "").lower().replace("0x", "")
        if got == want:
            return row
    return None

def require_log(pattern: str, path: Path, failures: list[str], label: str) -> None:
    if not re.search(pattern, read_text(path)):
        failures.append(f"{label} missing {pattern}")

def build_report() -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    index = read_tsv(BASE / "post-decompile" / "index.tsv")
    instructions = read_tsv(BASE / "post-instructions.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    vtables = read_tsv(BASE / "post-vtables.tsv")
    backup = read_json(BASE / "backup-summary.json")
    queue = read_json(QUEUE_REPORT)

    for addr, name in TARGETS.items():
        if (row_by_addr(metadata, addr) or {}).get("name") != name:
            failures.append(f"metadata mismatch for {addr}")
        if (row_by_addr(index, addr) or {}).get("name") != name:
            failures.append(f"decompile mismatch for {addr}")
        tag_text = (row_by_addr(tags, addr) or {}).get("tags", "")
        if "cfepbriefing-boundary-recovery-wave975" not in tag_text or "wave975-readback-verified" not in tag_text:
            failures.append(f"tag mismatch for {addr}")

    require_log(r"would_create=6 .*would_rename=1 .*bad=0", BASE / "apply-dry.log", failures, "dry log")
    require_log(r"updated=7 .*created=6 .*renamed=1 .*bad=0", BASE / "apply.log", failures, "apply log")
    require_log(r"updated=0 skipped=7 .*bad=0", BASE / "apply-final-dry.log", failures, "final dry log")

    if len(instructions) < 700:
        failures.append(f"instruction export too small: {len(instructions)}")
    if len(xrefs) < 7:
        failures.append(f"xref export too small: {len(xrefs)}")
    if len(vtables) < 32:
        failures.append(f"vtable export too small: {len(vtables)}")
    if backup.get("fileCount") != 19 or backup.get("byteCount") != 173804423 or backup.get("hashDiffCount") != 0:
        failures.append("backup summary mismatch")
    queue_log = read_text(QUEUE_LOG)
    queue_probe_log = read_text(QUEUE_PROBE_LOG)
    if "total_functions=6217 commented_functions=6217" not in queue_log:
        failures.append("wave queue export summary mismatch")
    for token in ("Total functions: 6217", "Commentless functions: 0", "Undefined signatures: 0", "Param signatures: 0"):
        if token not in queue_probe_log:
            failures.append(f"wave queue probe missing {token}")

    quality = queue.get("qualitySignals") or {}
    if (
        int(queue.get("totalFunctions") or 0) < WAVE_TOTAL
        or quality.get("commentlessFunctionCount") != 0
        or quality.get("undefinedSignatureCount") != 0
        or quality.get("paramSignatureCount") != 0
    ):
        failures.append("current queue summary mismatch")

    for label, text in {"note": read_text(NOTE), "doc": read_text(DOC)}.items():
        for token in ("Wave975", "CFEPBriefing__Render", "CFEPBriefing__ActiveNotification"):
            if token not in text:
                failures.append(f"{label} missing {token}")

    return {
        "schema": "ghidra-frontend-briefing-state-review-wave975.v1",
        "status": "PASS" if not failures else "FAIL",
        "targets": TARGETS,
        "mutationStatus": "function-boundary recovery",
        "instructionRows": len(instructions),
        "xrefRows": len(xrefs),
        "vtableRows": len(vtables),
        "waveQueueTotal": WAVE_TOTAL,
        "currentQueueTotal": queue.get("totalFunctions"),
        "failures": failures,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave975-frontend-briefing-state-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave975 frontend briefing state review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
