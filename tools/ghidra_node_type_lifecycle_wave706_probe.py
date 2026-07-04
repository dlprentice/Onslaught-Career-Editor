#!/usr/bin/env python3
"""Validate Wave706 node-type lifecycle read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave706-node-tree-match"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_node_type_lifecycle_wave706_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
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

BASE_SIGNATURE_TAGS = {
    "static-reaudit",
    "node-type-lifecycle-wave706",
    "wave706-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}
BASE_COMMENT_TAGS = {
    "static-reaudit",
    "node-type-lifecycle-wave706",
    "wave706-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x005997a5": (
        "CFastVB__InitNodeType17",
        "void * __fastcall CFastVB__InitNodeType17(void * node_type17)",
        ("node-type 0x11", "0x005ef374", "returns the initialized node pointer"),
        BASE_SIGNATURE_TAGS | {"node-type-0x11", "constructor", "vtable", "zero-init", "return-this", "tranche-head"},
    ),
    "0x005997e1": (
        "CTexture__NodeType12_Ctor_DeleteOnFlag",
        "int CTexture__NodeType12_Ctor_DeleteOnFlag(void)",
        ("hidden-ECX", "eight descriptor dwords", "locked storage"),
        BASE_COMMENT_TAGS | {"node-type-0x11", "constructor", "descriptor-copy", "hidden-ecx", "locked-storage"},
    ),
    "0x00599831": (
        "CTexture__NodeType12_Dtor_DeleteOnFlag_Body",
        "void __fastcall CTexture__NodeType12_Dtor_DeleteOnFlag_Body(void * node_type17)",
        ("0x005ef374", "+0x3c", "base node-payload chain"),
        BASE_SIGNATURE_TAGS | {"node-type-0x11", "destructor-body", "owned-resource-slots", "release-chain", "fastcall-param-named"},
    ),
    "0x00599878": (
        "CFastVB__CloneNodeTreeWithAddRef",
        "void * __fastcall CFastVB__CloneNodeTreeWithAddRef(void * source_node_type17)",
        ("0x60", "clone/add-ref hooks", "partial clone"),
        BASE_SIGNATURE_TAGS | {"node-type-0x11", "clone", "add-ref", "owned-resource-slots", "fastcall-param-named"},
    ),
    "0x0059993c": (
        "CTexture__NodeType12_Ctor",
        "void * __fastcall CTexture__NodeType12_Ctor(void * node_type12)",
        ("node-type 0x12", "0xf0000", "0xe40000"),
        BASE_SIGNATURE_TAGS | {"node-type-0x12", "constructor", "vtable", "default-scalars", "return-this"},
    ),
    "0x0059996f": (
        "CTexture__NodeType12_Ctor_ScalarDeletingDtor",
        "int CTexture__NodeType12_Ctor_ScalarDeletingDtor(void)",
        ("hidden-ECX", "five stack-provided scalars", "0x005ef384"),
        BASE_COMMENT_TAGS | {"node-type-0x12", "constructor", "stack-scalars", "hidden-ecx", "locked-storage"},
    ),
    "0x005999b5": (
        "CTexture__NodeType12_ScalarDeletingDtor_Body",
        "void __fastcall CTexture__NodeType12_ScalarDeletingDtor_Body(void * node_type12)",
        ("0x005ef384", "+0x28", "base node-payload chain"),
        BASE_SIGNATURE_TAGS | {"node-type-0x12", "destructor-body", "owned-resource-slot", "release-chain", "fastcall-param-named"},
    ),
    "0x00599a3c": (
        "CTexture__NodeType12_Dtor_DeleteOnFlag",
        "void * __thiscall CTexture__NodeType12_Dtor_DeleteOnFlag(void * this, uint delete_flags)",
        ("delete_flags bit 0", "RET 0x4", "OID__FreeObject_Callback"),
        BASE_SIGNATURE_TAGS | {"node-type-0x11", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed"},
    ),
    "0x00599a58": (
        "CTexture__NodeType12_ScalarDeletingDtor",
        "void * __thiscall CTexture__NodeType12_ScalarDeletingDtor(void * this, uint delete_flags)",
        ("delete_flags bit 0", "RET 0x4", "OID__FreeObject_Callback"),
        BASE_SIGNATURE_TAGS | {"node-type-0x12", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave706 node-type lifecycle",
    "node-type-lifecycle-wave706",
    "0x005997a5 CFastVB__InitNodeType17",
    "0x00599a58 CTexture__NodeType12_ScalarDeletingDtor",
    "0x0042f220 CSPtrSet__Clear",
    "0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag",
)

OVERCLAIM_TOKENS = (
    "runtime texture behavior proven",
    "runtime vertex-buffer behavior proven",
    "node-type enum proven",
    "field schema proven",
    "hidden abi proven",
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
        "pre-selected-metadata.tsv": 9,
        "pre-selected-tags.tsv": 9,
        "pre-selected-xrefs.tsv": 12,
        "pre-selected-instructions.tsv": 801,
        "decompile-selected-pre/index.tsv": 9,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 801,
        "decompile-post/index.tsv": 9,
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
        require("Wave706 static read-back" in comment, f"missing Wave706 comment at {address}", failures)
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
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave706-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=2 missing=0 bad=0",
        "apply-wave706-apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=2 missing=0 bad=0",
        "apply-wave706-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "export-pre-selected-metadata.log": "targets=9 found=9 missing=0",
        "export-pre-selected-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "export-pre-selected-xrefs.log": "Wrote 12 rows",
        "export-pre-selected-instructions.log": "Wrote 801 instruction rows",
        "export-pre-selected-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "export-post-metadata.log": "targets=9 found=9 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "export-post-xrefs.log": "Wrote 12 rows",
        "export-post-instructions.log": "Wrote 801 instruction rows",
        "export-post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    queue_refresh = read_text(BASE / "export-queue-refresh.log")
    require("total_functions=6098 commented_functions=4104" in queue_refresh, "queue refresh count mismatch", failures)
    require("REPORT: Save succeeded" in queue_refresh, "queue refresh save report missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave706_queue_probe.log")
    require("Status: PASS" in queue_probe, "queue probe did not pass", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 1994, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 231, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    high_signal_head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(high_signal_head.get("address") == "0x00599a74", f"high-signal head address mismatch: {high_signal_head}", failures)
    require(high_signal_head.get("name") == "CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag", f"high-signal head name mismatch: {high_signal_head}", failures)

    rows = read_tsv(QUALITY_TSV)
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4050, f"strict clean proxy mismatch: {len(clean)}", failures)

    commentless = [row for row in rows if not row.get("comment", "").strip()]
    require(bool(commentless), "no commentless rows found", failures)
    if commentless:
        require(normalize_address(commentless[0].get("address", "")) == "0x0042f220", f"raw commentless head mismatch: {commentless[0]}", failures)
        require(commentless[0].get("name") == "CSPtrSet__Clear", f"raw commentless head name mismatch: {commentless[0]}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-201902_post_wave706_node_type_lifecycle_verified", "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, f"backup file count mismatch: {backup.get('fileCount')}", failures)
    require(int(backup.get("totalBytes", -1)) == 165448583, f"backup byte count mismatch: {backup.get('totalBytes')}", failures)
    require(backup.get("diffCount") == 0, f"backup diff count mismatch: {backup.get('diffCount')}", failures)


def check_docs(failures: list[str]) -> None:
    doc_paths = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
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
        package.get("scripts", {}).get("test:ghidra-node-type-lifecycle-wave706")
        == "py -3 tools\\ghidra_node_type_lifecycle_wave706_probe.py --check",
        "package script missing",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave706 node-type lifecycle" for row in ledger_rows), "ledger row missing", failures)
    require(
        any(
            row.get("attempt_id") == 20361
            and row.get("task") == "Wave706 node-type lifecycle"
            and row.get("readback") == "verified"
            for row in attempt_rows
        ),
        "attempt row missing",
        failures,
    )
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20362, f"next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1102, f"ledger_rows mismatch: {counters.get('ledger_rows')}", failures)
    require(counters.get("attempt_rows") == 20362, f"attempt_rows mismatch: {counters.get('attempt_rows')}", failures)
    require(counters.get("completed") == 1093, f"completed mismatch: {counters.get('completed')}", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave706 node-type lifecycle probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave706 node-type lifecycle probe: PASS")
    print("Targets: 9")
    print("Queue: 6098 total, 4104 commented, 1994 commentless, 1216 exact-undefined, 231 param_N")
    print("Strict clean-signature proxy: 4050/6098 = 66.42%")
    print("Raw commentless head: 0x0042f220 CSPtrSet__Clear")
    print("High-signal head: 0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
