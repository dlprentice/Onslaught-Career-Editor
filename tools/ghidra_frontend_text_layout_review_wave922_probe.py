#!/usr/bin/env python3
"""Validate Wave922 frontend text/layout read-only review artifacts."""

from __future__ import annotations

import argparse, csv, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave922-frontend-text-layout-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_text_layout_review_wave922_2026-05-27.md"
DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
LANG_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPLanguageTest.cpp" / "_index.md"

TARGETS = {
    "0x00465a20": "TextLayout__WrapWideTextToFixedLines",
    "0x00469c20": "CFrontEnd__ResolveEpisodeNameTextByIndex",
    "0x00469cf0": "CFrontEnd__ResolveLevelNameTextIdByCode",
    "0x0046a1f0": "FrontEndText__GetLevelNameTextAfterCode",
    "0x0046a210": "FrontEnd__GetBriefingLevelListTextColor",
    "0x0046a220": "FrontEndText__GetMultiplayerLevelDescriptionByType",
    "0x0046a2a0": "FrontEndText__GetLocalizedOrFallbackTextByToken",
    "0x0046b1e0": "FrontEndText__GetAsciiFallbackTextByToken",
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
        if "static-reaudit" not in tag_text:
            failures.append(f"tag mismatch for {addr}")
    if len(instructions) < 1400:
        failures.append(f"instruction export too small: {len(instructions)}")
    if len(xrefs) < 100:
        failures.append(f"xref export too small: {len(xrefs)}")
    if backup.get("files") != 19 or backup.get("bytes") != 173247367:
        failures.append("backup summary mismatch")
    required = {
        "note": (read_text(NOTE), ("Wave922", "TextLayout__WrapWideTextToFixedLines", "FrontEndText__GetLocalizedOrFallbackTextByToken")),
        "front_end_doc": (read_text(DOC), ("Wave922", "TextLayout__WrapWideTextToFixedLines", "FrontEndText__GetLocalizedOrFallbackTextByToken")),
        "language_doc": (read_text(LANG_DOC), ("Wave922", "TextLayout__WrapWideTextToFixedLines")),
    }
    for label, (text, tokens) in required.items():
        for token in tokens:
            if token not in text:
                failures.append(f"{label} missing {token}")
    return {"schema": "ghidra-frontend-text-layout-review-wave922.v1", "status": "PASS" if not failures else "FAIL", "targets": TARGETS, "mutatedTargets": 0, "instructionRows": len(instructions), "xrefRows": len(xrefs), "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave922-frontend-text-layout-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave922 frontend text/layout review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    for failure in report["failures"]:
        print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
