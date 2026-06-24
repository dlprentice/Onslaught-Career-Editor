#!/usr/bin/env python3
"""Validate Wave746 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave746-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave746_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
COMPONENT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Component.cpp" / "_index.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
CPHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScript.cpp.md"
WORLD_PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-173500_post_wave746_unwind_continuation_verified"

TARGETS = {
    "0x005d1aa3": {"scope": "0x0061a914", "tokens": ("CGenericActiveReader__dtor", "+0x24"), "tags": {"active-reader", "component-adjacent"}},
    "0x005d1ac0": {"scope": "0x0061a93c", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"monitor", "shutdown"}},
    "0x005d1ac8": {"scope": "0x0061a944", "tokens": ("CGenericActiveReader__dtor", "+0xc"), "tags": {"active-reader", "embedded-reader"}},
    "0x005d1ad3": {"scope": "0x0061a94c", "tokens": ("CGenericActiveReader__dtor", "+0x24"), "tags": {"active-reader", "embedded-reader"}},
    "0x005d1af0": {"scope": "0x0061a974", "tokens": ("CDXMemBuffer__dtor_base", "EBP-0x240"), "tags": {"dxmembuffer", "stack-local"}},
    "0x005d1b10": {"scope": "0x0061a99c", "tokens": ("CSPtrSet__Clear", "+0x4"), "tags": {"controller", "sptrset", "clear"}},
    "0x005d1b1b": {"scope": "0x0061a9a4", "tokens": ("CDXMemBuffer__dtor_base", "+0x2c"), "tags": {"controller", "dxmembuffer"}},
    "0x005d1b26": {"scope": "0x0061a9ac", "tokens": ("Controller.cpp", "line 0x27", "memtype 0x3c7"), "tags": {"controller", "controller-cpp", "free-object"}},
    "0x005d1b3f": {"scope": "0x0061a9b4", "tokens": ("CGenericActiveReader__dtor", "EBP-0x14"), "tags": {"controller", "active-reader"}},
    "0x005d1b47": {"scope": "0x0061a9bc", "tokens": ("monitor.h", "line 0x5e", "memtype 0x18"), "tags": {"monitor", "monitor-h", "free-object"}},
    "0x005d1b70": {"scope": "0x0061a9e4", "tokens": ("CSPtrSet__Clear", "+0x4"), "tags": {"sptrset", "clear"}},
    "0x005d1b7b": {"scope": "0x0061a9ec", "tokens": ("CDXMemBuffer__dtor_base", "+0x2c"), "tags": {"dxmembuffer"}},
    "0x005d1b90": {"scope": "0x0061aa14", "tokens": ("Controller.cpp", "line 0x27", "memtype 0x3c7"), "tags": {"controller", "controller-cpp", "free-object"}},
    "0x005d1ba9": {"scope": "0x0061aa1c", "tokens": ("CGenericActiveReader__dtor", "EBP-0x10"), "tags": {"active-reader"}},
    "0x005d1bb1": {"scope": "0x0061aa24", "tokens": ("monitor.h", "line 0x5e", "memtype 0x18"), "tags": {"monitor", "monitor-h", "free-object"}},
    "0x005d1be0": {"scope": "0x0061aa4c", "tokens": ("CPhysicsScript.cpp", "line 0x18", "memtype 0x10"), "tags": {"cphysicsscript", "cphysicsscript-cpp", "free-object"}},
    "0x005d1c00": {"scope": "0x0061aa74", "tokens": ("WorldPhysicsManager.h", "line 0xf", "memtype 0x971"), "tags": {"worldphysicsmanager", "worldphysicsmanager-h", "free-object"}},
    "0x005d1c19": {"scope": "0x0061aa7c", "tokens": ("CSPtrSet__Clear", "+0x3c"), "tags": {"worldphysicsmanager", "sptrset", "embedded-set"}},
    "0x005d1c24": {"scope": "0x0061aa84", "tokens": ("CSPtrSet__Clear", "+0x4c"), "tags": {"worldphysicsmanager", "sptrset", "embedded-set"}},
    "0x005d1c2f": {"scope": "0x0061aa8c", "tokens": ("CSPtrSet__Clear", "+0x5c"), "tags": {"worldphysicsmanager", "sptrset", "embedded-set"}},
    "0x005d1c3a": {"scope": "0x0061aa94", "tokens": ("CSPtrSet__Clear", "+0x6c"), "tags": {"worldphysicsmanager", "sptrset", "embedded-set"}},
    "0x005d1c50": {"scope": "0x0061aabc", "tokens": ("CPhysicsScriptStatement__dtor", "EBP-0x10"), "tags": {"cphysicsscript", "physics-script-statement", "destructor"}},
    "0x005d1c70": {"scope": "0x0061aae4", "tokens": ("WorldPhysicsManager.h", "line 0x3d", "memtype 0x95c"), "tags": {"worldphysicsmanager", "worldphysicsmanager-h", "free-object"}},
    "0x005d1ca0": {"scope": "0x0061ab0c", "tokens": ("CPhysicsScriptStatement__dtor", "EBP-0x10"), "tags": {"cphysicsscript", "physics-script-statement", "destructor"}},
    "0x005d1cc0": {"scope": "0x0061ab34", "tokens": ("WorldPhysicsManager.h", "line 0x3c", "memtype 0x955"), "tags": {"worldphysicsmanager", "worldphysicsmanager-h", "free-object"}},
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave746",
    "wave746-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

COMMON_DOC_TOKENS = (
    "Wave746 unwind continuation",
    "unwind-continuation-wave746",
    "0x005d1aa3 Unwind@005d1aa3",
    "0x005d1b26 Unwind@005d1b26",
    "0x005d1be0 Unwind@005d1be0",
    "0x005d1c00 Unwind@005d1c00",
    "0x005d1cc0 Unwind@005d1cc0",
    "0x005d1cd9 Unwind@005d1cd9",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime exception behavior proven",
    "runtime cleanup behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 25,
        "pre-tags.tsv": 25,
        "pre-xrefs.tsv": 25,
        "pre-instructions.tsv": 575,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 575,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for name in ("string-00625538.tsv", "string-0062551c.tsv", "string-0062568c.tsv", "string-00625850.tsv"):
        require(len(read_tsv(BASE / name)) == 1, f"{name} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        name = f"Unwind@{address[2:]}"
        signature = f"void __cdecl {name}(void)"
        comment = row.get("comment", "")
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        for token in ("Wave746 static read-back", "compiler-generated SEH unwind cleanup callback", expected["scope"], "Static retail Ghidra metadata/decompile/xref evidence only"):
            require(token in comment, f"missing comment token at {address}: {token}", failures)
        for token in expected["tokens"]:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required_tags = COMMON_TAGS | expected["tags"]
            require(required_tags.issubset(actual_tags), f"tags missing at {address}: {required_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    for address, expected in TARGETS.items():
        row = xrefs.get(address)
        require(row is not None, f"missing xref for {address}", failures)
        if row is not None:
            require(normalize_address(row.get("from_addr", "")) == expected["scope"], f"xref scope mismatch at {address}", failures)
            require(row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 575 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4512",
        "queue-probe.log": "Commentless functions: 1586",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave746.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave746_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1586, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1063, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d1cd9", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d1cd9", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4512, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4454, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 167578503 or backup.get("totalBytes") == 167578503.0, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    function_docs = {
        COMPONENT_DOC: ("Wave746", "unwind-continuation-wave746", "0x005d1aa3 Unwind@005d1aa3", "0x005d1cc0 Unwind@005d1cc0", BACKUP_PATH),
        CONTROLLER_DOC: ("Wave746", "unwind-continuation-wave746", "0x005d1b26 Unwind@005d1b26", "Controller.cpp", "0x005d1cd9 Unwind@005d1cd9", BACKUP_PATH),
        MONITOR_DOC: ("Wave746", "unwind-continuation-wave746", "0x005d1b47 Unwind@005d1b47", "monitor.h", "0x005d1cd9 Unwind@005d1cd9", BACKUP_PATH),
        CPHYSICS_DOC: ("Wave746", "unwind-continuation-wave746", "0x005d1be0 Unwind@005d1be0", "0x005d1c50 Unwind@005d1c50", "0x005d1cd9 Unwind@005d1cd9", BACKUP_PATH),
        WORLD_PHYSICS_DOC: ("Wave746", "unwind-continuation-wave746", "0x005d1c00 Unwind@005d1c00", "0x005d1cc0 Unwind@005d1cc0", "0x005d1cd9 Unwind@005d1cd9", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave746") == r"py -3 tools\ghidra_unwind_continuation_wave746_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave746 unwind continuation" for row in ledger_rows), "missing Wave746 ledger row", failures)
    require(any(row.get("task") == "Wave746 unwind continuation" and row.get("attempt_id") == 20401 for row in attempts), "missing Wave746 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave746 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave746 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
