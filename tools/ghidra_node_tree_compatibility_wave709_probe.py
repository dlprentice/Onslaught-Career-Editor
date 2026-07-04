#!/usr/bin/env python3
"""Validate Wave709 node-tree compatibility read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave709-node-tree-compatibility"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_node_tree_compatibility_wave709_2026-05-21.md"
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
    "node-tree-compatibility-wave709",
    "wave709-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "node-tree-compatibility",
}

TARGETS = {
    "0x00599d80": (
        "CFastVB__FlattenNodeTreeLeafByLinearIndex",
        "int __thiscall CFastVB__FlattenNodeTreeLeafByLinearIndex(void * this, void * node_tree, uint linear_leaf_index, void * out_leaf_scratch)",
        ("RET 0xc", "linear leaf index", "output leaf scratch", "flag mask +0x20 & 0x200"),
        BASE_TAGS | {"flatten-leaf-by-index", "phantom-param-removed", "ret-0xc", "tranche-head"},
    ),
    "0x00599e48": (
        "CFastVB__ResolveCommonLeafFormat",
        "int __stdcall CFastVB__ResolveCommonLeafFormat(void * left_leaf_scratch, void * right_leaf_scratch, void * out_common_format)",
        ("RET 0xc", "two leaf scratch records", "compatibility tables", "common format ids 0..0xc"),
        BASE_TAGS | {"common-leaf-format", "format-compatibility-table", "ret-0xc"},
    ),
    "0x00599ffd": (
        "CFastVB__CompareNodePayloadBindingChain",
        "int __thiscall CFastVB__CompareNodePayloadBindingChain(void * this, void * left_payload, void * right_payload, void * right_binding_chain, int compare_flags)",
        ("RET 0x10", "fourth cleaned argument is not read", "payload +0x1c descriptor", "right binding chain"),
        BASE_TAGS | {"payload-binding-chain", "ret-0x10", "unused-cleaned-arg"},
    ),
    "0x0059a10a": (
        "CFastVB__ScoreNodeTreePairMismatchBits",
        "int __thiscall CFastVB__ScoreNodeTreePairMismatchBits(void * this, void * left_node_tree, void * right_node_tree)",
        ("RET 0x8", "phantom third stack argument", "flattens paired leaves", "accumulates mismatch bits"),
        BASE_TAGS | {"pair-mismatch-score", "phantom-param-removed", "ret-0x8"},
    ),
    "0x0059a21f": (
        "CFastVB__AreNodeTreesCompatible",
        "int __thiscall CFastVB__AreNodeTreesCompatible(void * this, void * left_node_tree, void * right_node_tree, int relaxed_match)",
        ("RET 0xc", "correct the prior stdcall signature", "relaxed leaf-type path", "structural equality"),
        BASE_TAGS | {"node-tree-compatible", "relaxed-match", "ret-0xc", "thiscall-correction"},
    ),
    "0x0059a54d": (
        "CFastVB__ScoreNodeTreeMatch",
        "int __thiscall CFastVB__ScoreNodeTreeMatch(void * this, void * source_payload, void * candidate_payload, void * candidate_binding_chain, int match_flags)",
        ("RET 0x10", "phantom fifth stack argument", "match flag 0x10 filtering", "accumulated match score"),
        BASE_TAGS | {"node-tree-match-score", "phantom-param-removed", "ret-0x10", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave709 node-tree compatibility",
    "node-tree-compatibility-wave709",
    "0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex",
    "0x0059a54d CFastVB__ScoreNodeTreeMatch",
    "0x0059a71a CFastVB__SelectBestNodeTreeMatch",
    "0x0042f220 CSPtrSet__Clear",
    "0x0059aec0 CTexture__CanUseCompactDecodePath",
)

OVERCLAIM_TOKENS = (
    "runtime parser behavior proven",
    "node layout proven",
    "compatibility rules proven",
    "score semantics proven",
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
        "pre-candidate-metadata.tsv": 7,
        "pre-candidate-tags.tsv": 7,
        "pre-candidate-xrefs.tsv": 17,
        "pre-candidate-instructions.tsv": 1855,
        "decompile-candidate-pre/index.tsv": 7,
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 15,
        "pre-instructions.tsv": 1590,
        "decompile-pre/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 15,
        "post-instructions.tsv": 1590,
        "decompile-post/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    selector = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")}
    require("0x0059a71a" in selector, "selector candidate export missing", failures)
    require("0x0059a71a" not in metadata, "selector unexpectedly appears in post metadata", failures)
    selector_decompile = BASE / "decompile-candidate-pre" / "0059a71a_CFastVB__SelectBestNodeTreeMatch.c"
    require(selector_decompile.is_file(), "selector candidate decompile missing", failures)
    if selector_decompile.is_file():
        text = read_text(selector_decompile)
        for token in ("in_ECX", "unaff_EDI", "in_stack_00000004", "in_stack_00000020"):
            require(token in text, f"selector candidate ABI token missing: {token}", failures)

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave709 static read-back" in comment, f"missing Wave709 comment at {address}", failures)
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
            for token in ("param_", "unaff_", "in_stack_", "in_ECX"):
                require(token not in text, f"{token} survived in post decompile for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave709-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0",
        "apply-wave709-apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0",
        "apply-wave709-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-pre-candidate-metadata.log": "targets=7 found=7 missing=0",
        "export-pre-candidate-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "export-pre-candidate-xrefs.log": "Wrote 17 rows",
        "export-pre-candidate-instructions.log": "Wrote 1855 instruction rows",
        "export-pre-candidate-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "export-pre-metadata.log": "targets=6 found=6 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "export-pre-xrefs.log": "Wrote 15 rows",
        "export-pre-instructions.log": "Wrote 1590 instruction rows",
        "export-pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "export-post-metadata.log": "targets=6 found=6 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "export-post-xrefs.log": "Wrote 15 rows",
        "export-post-instructions.log": "Wrote 1590 instruction rows",
        "export-post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
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
    require("total_functions=6098 commented_functions=4117" in queue_refresh, "queue refresh count mismatch", failures)
    require("REPORT: Save succeeded" in queue_refresh, "queue refresh save report missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave709_queue_probe.log")
    require('"status": "PASS"' in queue_probe or "Status: PASS" in queue_probe, "queue probe did not pass", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 1981, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 218, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    high_signal_head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(high_signal_head.get("address") == "0x0059aec0", f"high-signal head address mismatch: {high_signal_head}", failures)
    require(high_signal_head.get("name") == "CTexture__CanUseCompactDecodePath", f"high-signal head name mismatch: {high_signal_head}", failures)

    rows = read_tsv(QUALITY_TSV)
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4063, f"strict clean proxy mismatch: {len(clean)}", failures)

    commentless = [row for row in rows if not row.get("comment", "").strip()]
    require(bool(commentless), "no commentless rows found", failures)
    if commentless:
        require(normalize_address(commentless[0].get("address", "")) == "0x0042f220", f"raw commentless head mismatch: {commentless[0]}", failures)
        require(commentless[0].get("name") == "CSPtrSet__Clear", f"raw commentless head name mismatch: {commentless[0]}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-214637_post_wave709_node_tree_compatibility_verified", "backup path mismatch", failures)
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

    public_note = read_text(PUBLIC_NOTE)
    require("deferred read-only" in public_note, "public note missing selector deferral language", failures)
    require("0x0059a71a CFastVB__SelectBestNodeTreeMatch" in public_note, "public note missing selector anchor", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-node-tree-compatibility-wave709")
        == "py -3 tools\\ghidra_node_tree_compatibility_wave709_probe.py --check",
        "missing package script for Wave709 probe",
        failures,
    )


def check_logs_and_state(failures: list[str]) -> None:
    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(ledger_rows[-1].get("task") == "Wave709 node-tree compatibility", "latest ledger row is not Wave709", failures)
    require(attempt_rows[-1].get("attempt_id") == 20364, "latest attempt id mismatch", failures)
    require(attempt_rows[-1].get("task") == "Wave709 node-tree compatibility", "latest attempt row is not Wave709", failures)
    require(attempt_rows[-1].get("readback") == "verified", "latest attempt readback not verified", failures)
    require("subagents/ghidra-static-reaudit/wave709-node-tree-compatibility" in attempt_rows[-1].get("source", ""), "attempt source missing scratch path", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1105, f"ledger row counter mismatch: {counters.get('ledger_rows')}", failures)
    require(counters.get("attempt_rows") == 20365, f"attempt row counter mismatch: {counters.get('attempt_rows')}", failures)
    require(counters.get("completed") == 1096, f"completed counter mismatch: {counters.get('completed')}", failures)
    require(counters.get("pending") == 9, f"pending counter mismatch: {counters.get('pending')}", failures)
    require(tracking.get("next_attempt_id") == 20365, f"next attempt id mismatch: {tracking.get('next_attempt_id')}", failures)


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

    print("Wave709 node-tree compatibility probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Status: PASS")
    print("Verified 6 metadata rows, 6 tag rows, 15 xref rows, 1590 instruction rows, 6 decompile rows, candidate selector deferral, queue counts, docs, logs, and backup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
