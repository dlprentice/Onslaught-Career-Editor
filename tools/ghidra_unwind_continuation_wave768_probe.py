#!/usr/bin/env python3
"""Validate Wave768 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave768-unwind-continuation"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave768_2026-05-23.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
TENTACLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Tentacle.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
THUNDERHEAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ThunderHead.cpp" / "_index.md"
TREE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "tree.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260523-171555_post_wave768_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d5050": "0x0061d8cc",
    "0x005d5070": "0x0061d8f4",
    "0x005d5090": "0x0061d91c",
    "0x005d50b0": "0x0061d944",
    "0x005d50b8": "0x0061d94c",
    "0x005d50c3": "0x0061d954",
    "0x005d50e0": "0x0061d97c",
    "0x005d5100": "0x0061d9a4",
    "0x005d5150": "0x0061d9f4",
    "0x005d5170": "0x0061da1c",
    "0x005d5190": "0x0061da44",
    "0x005d5198": "0x0061da4c",
    "0x005d51b0": "0x0061da74",
    "0x005d51d0": "0x0061da9c",
    "0x005d51f0": "0x0061dac4",
    "0x005d51f8": "0x0061dacc",
    "0x005d5200": "0x0061dad4",
    "0x005d5220": "0x0061dafc",
    "0x005d5250": "0x0061db24",
    "0x005d5280": "0x0061db4c",
    "0x005d52a0": "0x0061db74",
    "0x005d52c0": "0x0061db9c",
    "0x005d52e0": "0x0061dbc4",
    "0x005d5300": "0x0061dbec",
    "0x005d5320": "0x0061dc14",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave768",
    "wave768-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

HELPER_NAMES = (
    "OID__FreeObject_Callback",
    "CMonitor__Shutdown",
    "CGenericActiveReader__dtor",
    "CParticleManager__RemoveFromGlobalList_Thunk",
    "CDXMemBuffer__dtor_base",
    "CMonitor__Shutdown_Thunk",
    "CMapWhoEntry__RemoveFromMap",
    "CCollisionSeekingRound__Destructor",
    "CThing__dtor_base",
    "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
)

STRING_EXPECTATIONS = {
    "string-00632ccc.tsv": r"[maintainer-local-source-export-root]\Tentacle.cpp",
    "string-00632ef0.tsv": r"[maintainer-local-source-export-root]\texture.cpp",
    "string-006331c0.tsv": r"[maintainer-local-source-export-root]\thing.cpp",
    "string-00633240.tsv": r"[maintainer-local-source-export-root]\ThunderHead.cpp",
    "string-00633a84.tsv": r"[maintainer-local-source-export-root]\tree.cpp",
}

COMMENT_TOKENS = {
    "0x005d5050": ("Wave768 static read-back", "Tentacle.cpp", "0x00632ccc", "0x2f", "0x1b"),
    "0x005d50b0": ("Wave768 static read-back", "CMonitor__Shutdown", "0x0061d944"),
    "0x005d50e0": ("Wave768 static read-back", "CParticleManager__RemoveFromGlobalList_Thunk", "EBP-0x44"),
    "0x005d5100": ("Wave768 static read-back", "CDXMemBuffer__dtor_base", "EBP-0x240"),
    "0x005d5198": ("Wave768 static read-back", "CMapWhoEntry__RemoveFromMap", "0x0061da4c"),
    "0x005d51b0": ("Wave768 static read-back", "CCollisionSeekingRound__Destructor", "0x0061da74"),
    "0x005d5220": ("Wave768 static read-back", "thing.cpp", "0x006331c0", "0x299", "0x18"),
    "0x005d5280": ("Wave768 static read-back", "ThunderHead.cpp", "0x00633240", "0x20", "0x1b"),
    "0x005d52e0": ("Wave768 static read-back", "CDXLandscape__DestroyResourceDescriptorArray_Thunk", "EBP-0x534"),
    "0x005d5320": ("Wave768 static read-back", "tree.cpp", "0x00633a84", "0x8f", "0x5c"),
}

CORE_ANCHORS = (
    "Wave768 unwind continuation",
    "unwind-continuation-wave768",
    "0x005d5050 Unwind@005d5050",
    "0x005d50b0 Unwind@005d50b0",
    "0x005d5100 Unwind@005d5100",
    "0x005d5198 Unwind@005d5198",
    "0x005d5220 Unwind@005d5220",
    "0x005d5280 Unwind@005d5280",
    "0x005d52e0 Unwind@005d52e0",
    "0x005d5320 Unwind@005d5320",
    "0x005d5350 Unwind@005d5350",
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


def expected_name(address: str) -> str:
    return f"Unwind@{address[2:]}"


def expected_signature(address: str) -> str:
    return f"void __cdecl {expected_name(address)}(void)"


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
        "pre-instructions.tsv": 2025,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 2025,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 10,
        "post-helper-metadata.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in HELPER_NAMES:
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, expected_scope in TARGET_XREFS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected_name(address), f"name mismatch at {address}", failures)
            require(row.get("signature") == expected_signature(address), f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            default_tokens = ("Wave768 static read-back", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only")
            for token in COMMENT_TOKENS.get(address, default_tokens):
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
            require(dec.get("signature") == expected_signature(address), f"decompile signature mismatch at {address}", failures)
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
        "post-instructions.log": "Wrote 2025 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-helper-metadata.log": "targets=10 found=10 missing=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5062",
        "queue-probe.log": "Commentless functions: 1036",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave768.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave768_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1036, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 513, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d5350", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d5350", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5062, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5004, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 169610119 or backup.get("totalBytes") == 169610119.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        TENTACLE_DOC: ("Wave768", "unwind-continuation-wave768", "0x005d5050 Unwind@005d5050", "0x005d50b0 Unwind@005d50b0", BACKUP_PATH),
        TEXTURE_DOC: ("Wave768", "unwind-continuation-wave768", "0x005d5100 Unwind@005d5100", "0x005d5198 Unwind@005d5198", "0x005d5200 Unwind@005d5200", BACKUP_PATH),
        THING_DOC: ("Wave768", "unwind-continuation-wave768", "0x005d5220 Unwind@005d5220", "0x005d5250 Unwind@005d5250", BACKUP_PATH),
        THUNDERHEAD_DOC: ("Wave768", "unwind-continuation-wave768", "0x005d5280 Unwind@005d5280", "0x005d52e0 Unwind@005d52e0", "0x005d5300 Unwind@005d5300", BACKUP_PATH),
        TREE_DOC: ("Wave768", "unwind-continuation-wave768", "0x005d5320 Unwind@005d5320", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave768") == r"py -3 tools\ghidra_unwind_continuation_wave768_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave768 unwind continuation" for row in ledger_rows), "missing Wave768 ledger row", failures)
    require(any(row.get("task") == "Wave768 unwind continuation" and row.get("attempt_id") == 20423 for row in attempts), "missing Wave768 attempt row", failures)


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
        print("Wave768 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave768 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
