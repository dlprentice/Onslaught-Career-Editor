#!/usr/bin/env python3
"""Validate Wave748 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave748-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave748_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
CUTSCENE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Cutscene.cpp" / "_index.md"
DESTRUCTABLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DestructableSegmentsController.cpp" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-183258_post_wave748_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d1fc8": "0x0061ae64",
    "0x005d1fd6": "0x0061ae6c",
    "0x005d1ff0": "0x0061ae94",
    "0x005d2020": "0x0061aebc",
    "0x005d2050": "0x0061aee4",
    "0x005d2070": "0x0061af0c",
    "0x005d2090": "0x0061af34",
    "0x005d2098": "0x0061af3c",
    "0x005d20b0": "0x0061af64",
    "0x005d20b8": "0x0061af6c",
    "0x005d20d0": "0x0061af94",
    "0x005d20f0": "0x0061afbc",
    "0x005d2110": "0x0061afe4",
    "0x005d2118": "0x0061afec",
    "0x005d2130": "0x0061b014",
    "0x005d2150": "0x0061b03c",
    "0x005d2170": "0x0061b064",
    "0x005d2189": "0x0061b06c",
    "0x005d2191": "0x0061b074",
    "0x005d2199": "0x0061b07c",
    "0x005d21c0": "0x0061b0a4",
    "0x005d21e0": "0x0061b0cc",
    "0x005d21f9": "0x0061b0d4",
    "0x005d2212": "0x0061b0dc",
    "0x005d222b": "0x0061b0e4",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave748",
    "wave748-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

CORE_ANCHORS = (
    "Wave748 unwind continuation",
    "unwind-continuation-wave748",
    "0x005d1fc8 Unwind@005d1fc8",
    "0x005d1ff0 Unwind@005d1ff0",
    "0x005d2070 Unwind@005d2070",
    "0x005d2170 Unwind@005d2170",
    "0x005d222b Unwind@005d222b",
    "0x005d2250 Unwind@005d2250",
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
        "pre-helper-metadata.tsv": 10,
        "string-0062811c.tsv": 1,
        "string-006287b4.tsv": 1,
        "string-0062551c.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "pre-helper-metadata.tsv")}
    for name in (
        "CGenericActiveReader__dtor",
        "CResourceDescriptor__dtor",
        "OID__FreeObject_Callback",
        "CTGALoader__Destructor",
        "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
        "CMonitor__Shutdown",
        "CSPtrSet__Clear",
        "CParticleManager__RemoveFromGlobalList_Thunk",
        "CDestroyableSegment__dtor_base",
        "CRT__SehDispatchWithScopeTable_Thunk_0055d731",
    ):
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    expected_strings = {
        "string-0062811c.tsv": r"C:\dev\ONSLAUGHT2\Cutscene.cpp",
        "string-006287b4.tsv": r"C:\dev\ONSLAUGHT2\DestructableSegmentsController.cpp",
        "string-0062551c.tsv": r"C:\dev\ONSLAUGHT2\monitor.h",
    }
    for relative, expected in expected_strings.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, expected_scope in TARGET_XREFS.items():
        name = f"Unwind@{address[2:]}"
        signature = f"void __cdecl {name}(void)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave748 static read-back", "compiler-generated SEH unwind", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref_row = xrefs.get(address)
        require(xref_row is not None, f"missing xref for {address}", failures)
        if xref_row is not None:
            require(normalize_address(xref_row.get("from_addr", "")) == expected_scope, f"xref scope mismatch at {address}", failures)
            require(xref_row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


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
        "quality-refresh.log": "total_functions=6098 commented_functions=4562",
        "queue-probe.log": "Commentless functions: 1536",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave748.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave748_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1536, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1013, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d2250", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d2250", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4562, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4504, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 167742343 or backup.get("totalBytes") == 167742343.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
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
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    function_docs = {
        CUTSCENE_DOC: ("Wave748", "unwind-continuation-wave748", "0x005d1fc8 Unwind@005d1fc8", "0x005d1ff0 Unwind@005d1ff0", "0x005d2020 Unwind@005d2020", BACKUP_PATH),
        DESTRUCTABLE_DOC: ("Wave748", "unwind-continuation-wave748", "0x005d2170 Unwind@005d2170", "0x005d21e0 Unwind@005d21e0", "0x005d222b Unwind@005d222b", BACKUP_PATH),
        MONITOR_DOC: ("Wave748", "unwind-continuation-wave748", "0x005d2199 Unwind@005d2199", "0x0042f220 CSPtrSet__Clear", BACKUP_PATH),
        DXLANDSCAPE_DOC: ("Wave748", "unwind-continuation-wave748", "0x005d2070 Unwind@005d2070", BACKUP_PATH),
        PARTICLE_DOC: ("Wave748", "unwind-continuation-wave748", "0x005d20f0 Unwind@005d20f0", "0x005d2130 Unwind@005d2130", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave748") == r"py -3 tools\ghidra_unwind_continuation_wave748_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave748 unwind continuation" for row in ledger_rows), "missing Wave748 ledger row", failures)
    require(any(row.get("task") == "Wave748 unwind continuation" and row.get("attempt_id") == 20403 for row in attempts), "missing Wave748 attempt row", failures)


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
        print("Wave748 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave748 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
