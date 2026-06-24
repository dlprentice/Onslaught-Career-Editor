#!/usr/bin/env python3
"""Validate Wave708 node-tree predicate read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave708-node-tree-predicates"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_node_tree_predicates_wave708_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BASE_TAGS = {
    "static-reaudit",
    "node-tree-predicates-wave708",
    "wave708-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "node-tree-predicate",
    "recursive-node-walk",
}

TARGETS = {
    "0x00599b69": (
        "CFastVB__NodeTreeHasBitFlag0x200",
        "uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void * this, void * node_tree)",
        ("kind 8 returns", "node +0x20 & 0x200", "phantom decompiler artifact"),
        BASE_TAGS | {"phantom-param-removed", "internal-error-diagnostic", "bit-flag-0x200", "tranche-head"},
    ),
    "0x00599bd7": (
        "CFastVB__NodeTreeHasOnlyLeafType0to2",
        "int __thiscall CFastVB__NodeTreeHasOnlyLeafType0to2(void * this, void * node_tree)",
        ("null trees pass", "inclusive range 0..2", "phantom decompiler artifact"),
        BASE_TAGS | {"phantom-param-removed", "internal-error-diagnostic", "leaf-type-range-0-to-2"},
    ),
    "0x00599c49": (
        "CFastVB__CountNodeTreeExpandedLeafCount",
        "int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void * this, void * node_tree)",
        ("recursively counts", "node +0x1c * node +0x18", "phantom decompiler artifact"),
        BASE_TAGS | {"phantom-param-removed", "internal-error-diagnostic", "expanded-leaf-count"},
    ),
    "0x00599cd2": (
        "CFastVB__AreNodeTreesStructurallyEqual",
        "bool __stdcall CFastVB__AreNodeTreesStructurallyEqual(void * left_node_tree, void * right_node_tree)",
        ("structural equality", "leaf kind 8 compares", "+0x10, +0x14, +0x18, and +0x1c"),
        BASE_TAGS | {"structural-equality", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave708 node-tree predicates",
    "node-tree-predicates-wave708",
    "0x00599b69 CFastVB__NodeTreeHasBitFlag0x200",
    "0x00599cd2 CFastVB__AreNodeTreesStructurallyEqual",
    "0x0042f220 CSPtrSet__Clear",
    "0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex",
)

OVERCLAIM_TOKENS = (
    "runtime parser behavior proven",
    "node layout proven",
    "field semantics proven",
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


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    expected_counts = {
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 19,
        "pre-instructions.tsv": 356,
        "decompile-pre/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 19,
        "post-instructions.tsv": 356,
        "decompile-post/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave708 static read-back" in comment, f"missing Wave708 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        decompile_file = BASE / "decompile-post" / f"{address[2:]}_{name}.c"
        require(decompile_file.is_file(), f"missing decompile file for {address}", failures)
        if decompile_file.is_file():
            text = read_text(decompile_file)
            require("unaff_" not in text, f"unaff_ survived in post decompile for {address}", failures)
            require("param_" not in text, f"param_ survived in post decompile for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave708-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0",
        "apply-wave708-apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0",
        "apply-wave708-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-pre-metadata.log": "targets=4 found=4 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "export-pre-xrefs.log": "Wrote 19 rows",
        "export-pre-instructions.log": "Wrote 356 instruction rows",
        "export-pre-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "export-post-metadata.log": "targets=4 found=4 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "export-post-xrefs.log": "Wrote 19 rows",
        "export-post-instructions.log": "Wrote 356 instruction rows",
        "export-post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BADNAME:" not in text and "MISSING:" not in text and "FAIL:" not in text, f"bad/missing marker found in {filename}", failures)

    queue_refresh = read_text(BASE / "export-queue-refresh.log")
    require("total_functions=6098 commented_functions=4111" in queue_refresh, "queue refresh count mismatch", failures)
    require("REPORT: Save succeeded" in queue_refresh, "queue refresh save report missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave708_queue_probe.log")
    require("Status: PASS" in queue_probe, "queue probe did not pass", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 1987, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 224, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    high_signal_head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(high_signal_head.get("address") == "0x00599d80", f"high-signal head address mismatch: {high_signal_head}", failures)
    require(high_signal_head.get("name") == "CFastVB__FlattenNodeTreeLeafByLinearIndex", f"high-signal head name mismatch: {high_signal_head}", failures)

    rows = read_tsv(QUALITY_TSV)
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4057, f"strict clean proxy mismatch: {len(clean)}", failures)

    commentless = [row for row in rows if not row.get("comment", "").strip()]
    require(bool(commentless), "no commentless rows found", failures)
    if commentless:
        require(normalize_address(commentless[0].get("address", "")) == "0x0042f220", f"raw commentless head mismatch: {commentless[0]}", failures)
        require(commentless[0].get("name") == "CSPtrSet__Clear", f"raw commentless head name mismatch: {commentless[0]}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == "G:\\GhidraBackups\\BEA_20260521-211737_post_wave708_node_tree_predicates_verified", "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, f"backup file count mismatch: {backup.get('fileCount')}", failures)
    require(int(backup.get("totalBytes", -1)) == 165481351, f"backup byte count mismatch: {backup.get('totalBytes')}", failures)
    require(backup.get("diffCount") == 0, f"backup diff count mismatch: {backup.get('diffCount')}", failures)


def check_docs(failures: list[str]) -> None:
    doc_paths = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        FASTVB_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in doc_paths:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token found in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-node-tree-predicates-wave708")
        == "py -3 tools\\ghidra_node_tree_predicates_wave708_probe.py --check",
        "missing package script for Wave708 probe",
        failures,
    )


def check_logs_and_state(failures: list[str]) -> None:
    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(ledger_rows[-1].get("task") == "Wave708 node-tree predicates", "latest ledger row is not Wave708", failures)
    require(attempt_rows[-1].get("attempt_id") == 20363, "latest attempt id mismatch", failures)
    require(attempt_rows[-1].get("task") == "Wave708 node-tree predicates", "latest attempt row is not Wave708", failures)
    require(attempt_rows[-1].get("readback") == "verified", "latest attempt readback not verified", failures)
    require("subagents/ghidra-static-reaudit/wave708-node-tree-predicates" in attempt_rows[-1].get("source", ""), "attempt source missing scratch path", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1104, f"ledger row counter mismatch: {counters.get('ledger_rows')}", failures)
    require(counters.get("attempt_rows") == 20364, f"attempt row counter mismatch: {counters.get('attempt_rows')}", failures)
    require(counters.get("completed") == 1095, f"completed counter mismatch: {counters.get('completed')}", failures)
    require(tracking.get("next_attempt_id") == 20364, f"next attempt id mismatch: {tracking.get('next_attempt_id')}", failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_logs(failures)
        check_queue_and_backup(failures)
        check_docs(failures)
        check_logs_and_state(failures)
    except Exception as exc:  # pragma: no cover - command-line diagnostics
        failures.append(f"unexpected exception: {exc}")

    print("Wave708 node-tree predicates probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Status: PASS")
    print("Verified 4 metadata rows, 4 tag rows, 19 xref rows, 356 instruction rows, 4 decompile rows, queue counts, docs, logs, and backup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
