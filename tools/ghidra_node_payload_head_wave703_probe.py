#!/usr/bin/env python3
"""Validate Wave703 node payload head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave703-node-payload-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_node_payload_head_wave703_2026-05-21.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

BASE_SIGNATURE_TAGS = {
    "static-reaudit",
    "ctexture-node-payload-head-wave703",
    "wave703-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}
BASE_COMMENT_TAGS = {
    "static-reaudit",
    "ctexture-node-payload-head-wave703",
    "wave703-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x00598702": (
        "CTexture__NodePayloadBaseCtor",
        "void __thiscall CTexture__NodePayloadBaseCtor(void * this, int format_class_id_or_kind)",
        ("node-payload header", "RET 0x4", "format class/kind"),
        BASE_SIGNATURE_TAGS | {"node-payload", "constructor", "format-class", "tranche-head", "phantom-param-removed"},
    ),
    "0x0059871c": (
        "CDXTexture__ReleaseNodePayloadChain",
        "void __fastcall CDXTexture__ReleaseNodePayloadChain(void * node_payload)",
        ("base release vtable", "delete flag 1", "sibling chain"),
        BASE_SIGNATURE_TAGS | {"node-payload", "release-chain", "vtable-dispatch", "destructor"},
    ),
    "0x00598749": (
        "CTexture__HasSameFormatClassId",
        "bool __thiscall CTexture__HasSameFormatClassId(void * this, void * candidate_node)",
        ("null candidate", "candidate_node+0x4", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-payload", "format-class", "compatibility", "phantom-param-removed"},
    ),
    "0x0059877e": (
        "CTexture__NodePayloadNoOp",
        "void CTexture__NodePayloadNoOp(void)",
        ("single RET", "locked storage", "no-op"),
        BASE_COMMENT_TAGS | {"node-payload", "no-op", "vtable-slot", "locked-storage"},
    ),
    "0x0059877f": (
        "CTexture__NodePayloadMatchesTypeOrNullIsZero",
        "uint __stdcall CTexture__NodePayloadMatchesTypeOrNullIsZero(void * node_or_null, int expected_type)",
        ("expected_type == 0", "vslot +0x4", "RET 0x8"),
        BASE_SIGNATURE_TAGS | {"node-payload", "vtable-dispatch", "type-match", "null-sentinel"},
    ),
    "0x0059879e": (
        "CDXTexture__InvokeNodeScoreOrZero",
        "int __stdcall CDXTexture__InvokeNodeScoreOrZero(void * node_or_null)",
        ("returns zero", "vslot +0x8", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-payload", "vtable-dispatch", "score", "null-sentinel"},
    ),
    "0x005987b2": (
        "CTexture__AppendNodeAtTail_Link0c",
        "void * __stdcall CTexture__AppendNodeAtTail_Link0c(void * chain_head, void * node_to_append)",
        ("+0xc link", "returns the resulting chain head", "parser reduction"),
        BASE_SIGNATURE_TAGS | {"node-payload", "linked-list", "append-tail", "parser-reduction"},
    ),
    "0x005987d9": (
        "CDXTexture__NodePayload__ctor",
        "void __fastcall CDXTexture__NodePayload__ctor(void * node_payload)",
        ("0x14-byte", "kind/class field 1", "zeroed +0x10"),
        BASE_SIGNATURE_TAGS | {"node-payload", "constructor", "derived-node", "vtable"},
    ),
    "0x005987f4": (
        "CTexture__NodePayloadRecordCtor",
        "int CTexture__NodePayloadRecordCtor(void)",
        ("hidden-ECX", "RET 0xc", "locked storage"),
        BASE_COMMENT_TAGS | {"node-payload", "constructor", "hidden-ecx", "locked-storage"},
    ),
    "0x0059881b": (
        "CTexture__IsFormatChainCompatible",
        "int __thiscall CTexture__IsFormatChainCompatible(void * this, void * candidate_chain)",
        ("CTexture__HasSameFormatClassId", "kind-1 child chains", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-payload", "compatibility", "linked-list", "child-chain", "phantom-param-removed"},
    ),
    "0x00598873": (
        "CFastVB__CloneNodeChainWithAddRef",
        "void * __fastcall CFastVB__CloneNodeChainWithAddRef(void * source_chain)",
        ("allocating 0x14-byte", "rolling back failed child clones", "vslot +0x8"),
        BASE_SIGNATURE_TAGS | {"node-payload", "clone-chain", "vtable-dispatch", "allocator", "fastcall-param-named"},
    ),
    "0x005988f5": (
        "CFastVB__CompareNodeValuesByTagAndPayload",
        "int __fastcall CFastVB__CompareNodeValuesByTagAndPayload(void * left_payload)",
        ("hidden EAX-held right payload", "tag", "boolean-style match result"),
        BASE_SIGNATURE_TAGS | {"node-payload", "comparator", "hidden-eax", "tag-dispatch", "fastcall-param-named"},
    ),
}

DOC_TOKENS = (
    "Wave703 node payload head",
    "ctexture-node-payload-head-wave703",
    "0x00598702 CTexture__NodePayloadBaseCtor",
    "0x005988f5 CFastVB__CompareNodeValuesByTagAndPayload",
    "0x005989c3 CTexture__NodeType8_InitDefaults",
)

OVERCLAIM_TOKENS = (
    "runtime texture behavior proven",
    "runtime vertex-buffer behavior proven",
    "payload layout proven",
    "exact addref semantics proven",
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
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 60,
        "pre-instructions.tsv": 444,
        "decompile-pre/index.tsv": 12,
        "post-metadata.tsv": 12,
        "post-tags.tsv": 12,
        "post-xrefs.tsv": 60,
        "post-instructions.tsv": 444,
        "decompile-post/index.tsv": 12,
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
        require("Wave703 static read-back" in comment, f"missing Wave703 comment at {address}", failures)
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
        "apply-wave703-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=2 missing=0 bad=0",
        "apply-wave703-apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=2 missing=0 bad=0",
        "apply-wave703-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "pre-xrefs.log": "Wrote 60 rows",
        "pre-instructions.log": "Wrote 444 instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-xrefs.log": "Wrote 60 rows",
        "post-instructions.log": "Wrote 444 instruction rows",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    queue_refresh = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave703.log")
    require("total_functions=6098 commented_functions=4068" in queue_refresh, "queue refresh count mismatch", failures)
    require("REPORT: Save succeeded" in queue_refresh, "queue refresh save report missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave703_queue_probe.log")
    require("Status: PASS" in queue_probe, "queue probe did not pass", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2030, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 260, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x005989c3", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__NodeType8_InitDefaults", f"next head name mismatch: {head}", failures)

    rows = read_tsv(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv")
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4014, f"strict clean proxy mismatch: {len(clean)}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-182413_post_wave703_node_payload_head_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup.get('file_count')}", failures)
    require(int(backup.get("byte_count", -1)) == 165317511, f"backup byte count mismatch: {backup.get('byte_count')}", failures)
    require(backup.get("diff_count") == 0, f"backup diff count mismatch: {backup.get('diff_count')}", failures)


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
        package.get("scripts", {}).get("test:ghidra-node-payload-head-wave703")
        == "py -3 tools\\ghidra_node_payload_head_wave703_probe.py --check",
        "package script missing",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave703 node payload head" for row in ledger_rows), "ledger row missing", failures)
    require(any(row.get("task") == "Wave703 node payload head" and row.get("readback") == "verified" for row in attempt_rows), "attempt row missing", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20359, f"next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)


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
        print("Wave703 node payload head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave703 node payload head probe: PASS")
    print("Targets: 12")
    print("Queue: 6098 total, 4068 commented, 2030 commentless, 1216 exact-undefined, 260 param_N")
    print("Strict clean-signature proxy: 4014/6098 = 65.82%")
    print("Next head: 0x005989c3 CTexture__NodeType8_InitDefaults")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
