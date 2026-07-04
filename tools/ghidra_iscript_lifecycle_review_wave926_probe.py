#!/usr/bin/env python3
"""Validate Wave926 IScript lifecycle read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave926-iscript-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_lifecycle_review_wave926_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260527-224500_post_wave926_iscript_lifecycle_review_verified"
SCRIPT_NAME = "test:ghidra-iscript-lifecycle-review-wave926"
SCRIPT_VALUE = r"py -3 tools\ghidra_iscript_lifecycle_review_wave926_probe.py --check"

TARGETS = {
    "0x005333b0": (
        "IScript__Constructor",
        "void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)",
    ),
    "0x00533450": (
        "IScript__Destructor",
        "void __thiscall IScript__Destructor(void * this)",
    ),
}

EXPECTED_XREFS = {
    "0x005333b0": {("0x004f42a8", "CComplexThing__SetScript", "UNCONDITIONAL_CALL")},
    "0x00533450": {("0x00533433", "IScript__ScalarDeletingDestructor", "UNCONDITIONAL_CALL")},
}

CORE_TOKENS = (
    "Wave926",
    "iscript-lifecycle-review-wave926",
    "98/1408 = 6.96%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x005333b0",
    "0x00533450",
    "CComplexThing__SetScript",
    "IScript__ScalarDeletingDestructor",
)

OVERCLAIMS = (
    "runtime mission-script startup behavior proven",
    "runtime mission-script teardown behavior proven",
    "runtime mission-script behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalized(addr: str) -> str:
    value = (addr or "").lower().strip()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str]:
    want = normalized(addr)
    for row in rows:
        got = row.get("address") or row.get("target_addr") or row.get("function_entry") or ""
        if normalized(got) == want:
            return row
    return {}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def build_report() -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    decomp = read_tsv(BASE / "decompile" / "index.tsv")
    summary = json.loads(read_text(BASE / "wave926-iscript-lifecycle-review.json") or "{}")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")

    require(len(metadata) == 2, "metadata row count mismatch", failures)
    require(len(tags) == 2, "tag row count mismatch", failures)
    require(len(xrefs) == 2, "xref row count mismatch", failures)
    require(len(instructions) == 95, "instruction row count mismatch", failures)
    require(len(decomp) == 2, "decompile row count mismatch", failures)

    for addr, (name, signature) in TARGETS.items():
        mrow = row_by_addr(metadata, addr)
        require(mrow.get("name") == name, f"metadata name mismatch for {addr}", failures)
        require(mrow.get("signature") == signature, f"metadata signature mismatch for {addr}", failures)
        require(mrow.get("status") == "OK", f"metadata status mismatch for {addr}", failures)
        drow = row_by_addr(decomp, addr)
        require(drow.get("name") == name, f"decompile name mismatch for {addr}", failures)
        require(drow.get("signature") == signature, f"decompile signature mismatch for {addr}", failures)
        require(drow.get("status") == "OK", f"decompile status mismatch for {addr}", failures)
        require(row_by_addr(tags, addr).get("status") == "OK", f"tag status mismatch for {addr}", failures)

    actual_xrefs: dict[str, set[tuple[str, str, str]]] = {}
    for row in xrefs:
        target = normalized(row.get("target_addr", ""))
        actual_xrefs.setdefault(target, set()).add(
            (normalized(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", ""))
        )
    for addr, expected in EXPECTED_XREFS.items():
        actual = actual_xrefs.get(normalized(addr), set())
        normalized_expected = {(normalized(from_addr), from_func, ref_type) for from_addr, from_func, ref_type in expected}
        require(normalized_expected.issubset(actual), f"xref mismatch for {addr}: {normalized_expected - actual}", failures)

    for log_name, token in {
        "metadata.log": "targets=2 found=2 missing=0",
        "tags.log": "rows=2 missing=0",
        "xrefs.log": "Wrote 2 rows",
        "instructions.log": "Wrote 95 function-body instruction rows",
        "decompile.log": "targets=2 dumped=2 missing=0 failed=0",
    }.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {log_name}: {bad}", failures)

    require(summary.get("status") == "read-only static review; no mutation warranted", "summary status mismatch", failures)
    require(summary.get("focusedProgress") == "98/1408 = 6.96%", "summary progress mismatch", failures)
    require(summary.get("staticClosure") == "6113/6113 = 100.00%", "summary closure mismatch", failures)
    counts = summary.get("counts", {})
    require(counts.get("instructions") == 95, "summary instruction count mismatch", failures)

    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    docs = [NOTE, CAMPAIGN, ISCRIPT_DOC, *STATE_FILES]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON) or "{}")
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "package script mismatch", failures)

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "counts": {
            "metadata": len(metadata),
            "tags": len(tags),
            "xrefs": len(xrefs),
            "instructions": len(instructions),
            "decompile": len(decomp),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    report = build_report()
    report_path = BASE / "wave926-probe-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Ghidra Wave926 IScript lifecycle review probe")
    print(f"Status: {report['status']}")
    print(f"Output: {report_path.relative_to(ROOT)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
