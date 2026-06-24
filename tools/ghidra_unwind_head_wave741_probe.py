#!/usr/bin/env python3
"""Validate Wave741 unwind-head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave741-unwind-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_head_wave741_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md"
ATMOSPHERICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Atmospherics.cpp" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-150238_post_wave741_unwind_head_verified"

TARGETS = {
    "0x005d0f10": {"scope": "0x00619e04", "tokens": ("Monitor.h", "OID__FreeObject_Callback", "memtype 0x5e"), "tags": {"monitor", "monitor-h", "free-object"}},
    "0x005d0f30": {"scope": "0x00619e2c", "tokens": ("CMonitor__Shutdown_Thunk", "EBP-0x10"), "tags": {"monitor", "shutdown-thunk"}},
    "0x005d0f38": {"scope": "0x00619e34", "tokens": ("CGenericActiveReader__dtor", "0x2c"), "tags": {"active-reader", "embedded-reader"}},
    "0x005d0f50": {"scope": "0x00619e5c", "tokens": ("CMonitor__Shutdown_Thunk", "EBP-0x10"), "tags": {"monitor", "shutdown-thunk"}},
    "0x005d0f70": {"scope": "0x00619e84", "tokens": ("AirUnit.cpp", "line 0x2a", "memtype 0x10"), "tags": {"airunit", "airunit-cpp", "free-object"}},
    "0x005d0f86": {"scope": "0x00619e8c", "tokens": ("AirUnit.cpp", "line 0x36", "memtype 0x10"), "tags": {"airunit", "airunit-cpp", "free-object"}},
    "0x005d0fb0": {"scope": "0x00619eb4", "tokens": ("CDXLandscape__DestroyResourceDescriptorArray_Thunk", "EBP-0x434"), "tags": {"dxlandscape-cleanup", "resource-descriptor"}},
    "0x005d0fd0": {"scope": "0x00619edc", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"monitor", "shutdown"}},
    "0x005d0ff0": {"scope": "0x00619f04", "tokens": ("Atmospherics.cpp", "line 0x70", "memtype 0x65"), "tags": {"atmospherics", "atmospherics-cpp", "free-object"}},
    "0x005d1006": {"scope": "0x00619f0c", "tokens": ("Atmospherics.cpp", "line 0x73", "memtype 0x65"), "tags": {"atmospherics", "atmospherics-cpp", "free-object"}},
    "0x005d1030": {"scope": "0x00619f34", "tokens": ("BattleEngine.cpp", "line 0x63", "memtype 0x15"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d1049": {"scope": "0x00619f3c", "tokens": ("BattleEngine.cpp", "line 0x64", "memtype 0x15"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d1062": {"scope": "0x00619f44", "tokens": ("CDXLandscape__DestroyResourceDescriptorArray_Thunk", "EBP-0x434"), "tags": {"dxlandscape-cleanup", "resource-descriptor"}},
    "0x005d106d": {"scope": "0x00619f4c", "tokens": ("BattleEngine.cpp", "line 0xb1", "memtype 0x10"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d1089": {"scope": "0x00619f54", "tokens": ("BattleEngine.cpp", "line 0xbd", "memtype 0x10"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d10a5": {"scope": "0x00619f5c", "tokens": ("BattleEngine.cpp", "line 0xc8", "memtype 0x15"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d10c1": {"scope": "0x00619f64", "tokens": ("BattleEngine.cpp", "line 0x1f5", "EBP-0x47c"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d10dd": {"scope": "0x00619f6c", "tokens": ("BattleEngine.cpp", "line 0x108", "EBP-0x47c"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d10f9": {"scope": "0x00619f74", "tokens": ("BattleEngine.cpp", "line 0x124", "EBP-0x47c"), "tags": {"battleengine", "battleengine-cpp", "free-object"}},
    "0x005d1115": {"scope": "0x00619f7c", "tokens": ("BattleEngine.cpp", "CMonitor__Shutdown_Thunk", "EBP-0x47c"), "tags": {"battleengine", "monitor", "shutdown-thunk"}},
    "0x005d1130": {"scope": "0x00619fa4", "tokens": ("CUnit__dtor_base", "EBP-0x10"), "tags": {"unit", "destructor"}},
    "0x005d1138": {"scope": "0x00619fac", "tokens": ("CSPtrSet__Clear", "0x250"), "tags": {"unit", "sptrset-clear"}},
    "0x005d1146": {"scope": "0x00619fb4", "tokens": ("CGenericActiveReader__dtor", "0x264"), "tags": {"unit", "active-reader"}},
    "0x005d1154": {"scope": "0x00619fbc", "tokens": ("CSPtrSet__Clear", "0x284"), "tags": {"unit", "sptrset-clear"}},
    "0x005d1162": {"scope": "0x00619fc4", "tokens": ("CSPtrSet__Clear", "0x294"), "tags": {"unit", "sptrset-clear"}},
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-head-wave741",
    "wave741-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

COMMON_DOC_TOKENS = (
    "Wave741 unwind head",
    "unwind-head-wave741",
    "0x005d0f10 Unwind@005d0f10",
    "0x005d0f70 Unwind@005d0f70",
    "0x005d0ff0 Unwind@005d0ff0",
    "0x005d1030 Unwind@005d1030",
    "0x005d1162 Unwind@005d1162",
    "0x005d1170 Unwind@005d1170",
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
        "pre-instructions.tsv": 525,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 525,
        "post-decompile/index.tsv": 25,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

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
        for token in ("Wave741 static read-back", "compiler-generated SEH unwind cleanup callback", expected["scope"], "Static retail Ghidra metadata/decompile/xref evidence only"):
            require(token in comment, f"missing common comment token at {address}: {token}", failures)
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
        "post-instructions.log": "Wrote 525 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4386",
        "queue-probe.log": "Commentless functions: 1712",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1712, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1189, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d1170", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d1170", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4386, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4328, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 167086983, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for doc in docs:
        text = read_text(doc)
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {doc.relative_to(ROOT)}: {token}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token.lower() not in text.lower(), f"overclaim token in {doc.relative_to(ROOT)}: {token}", failures)

    specialized = {
        MONITOR_DOC: ("Wave741 unwind head", "0x005d0f10", "0x005d0fd0", "CMonitor__Shutdown"),
        AIRUNIT_DOC: ("Wave741 unwind head", "0x005d0f70", "0x005d0f86", "AirUnit.cpp"),
        ATMOSPHERICS_DOC: ("Wave741 unwind head", "0x005d0ff0", "0x005d1006", "Atmospherics.cpp"),
        BATTLEENGINE_DOC: ("Wave741 unwind head", "0x005d1030", "0x005d1115", "BattleEngine.cpp"),
        UNIT_DOC: ("Wave741 unwind head", "0x005d1130", "0x005d1162", "CSPtrSet__Clear"),
    }
    for doc, tokens in specialized.items():
        text = read_text(doc)
        for token in tokens:
            require(token in text, f"missing specialized doc token in {doc.relative_to(ROOT)}: {token}", failures)

    package_text = read_text(PACKAGE_JSON)
    require("test:ghidra-unwind-head-wave741" in package_text, "missing npm probe script", failures)

    ledger_entries = read_jsonl(LEDGER)
    attempt_entries = read_jsonl(ATTEMPT_LOG)
    require(any(e.get("task") == "Wave741 unwind head" for e in ledger_entries), "ledger missing Wave741", failures)
    require(any(e.get("task") == "Wave741 unwind head" for e in attempt_entries), "attempt log missing Wave741", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero on validation failure.")
    args = parser.parse_args()

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs):
        try:
            check(failures)
        except Exception as exc:  # noqa: BLE001 - probe should report all available context.
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave741 unwind head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave741 unwind head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
