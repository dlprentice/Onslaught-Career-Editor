#!/usr/bin/env python3
"""Validate Wave704 node-type constructor/destructor read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave704-node-type-constructors"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_node_type_constructors_wave704_2026-05-21.md"
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
    "node-type-constructors-wave704",
    "wave704-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}
BASE_COMMENT_TAGS = {
    "static-reaudit",
    "node-type-constructors-wave704",
    "wave704-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x005989c3": (
        "CTexture__NodeType8_InitDefaults",
        "void __fastcall CTexture__NodeType8_InitDefaults(void * node_type8)",
        ("node-type-8", "vtable 0x005ef240", "kind/class field +0x4 to 2"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-8", "constructor", "vtable", "fastcall-param-named", "tranche-head"},
    ),
    "0x005989db": (
        "CTexture__NodeType8_InitFromDescriptor",
        "void __thiscall CTexture__NodeType8_InitFromDescriptor(void * this, void * descriptor_words32)",
        ("node-type-8", "descriptor_words32", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-8", "descriptor-copy", "vtable", "phantom-param-removed"},
    ),
    "0x00598a56": (
        "CFastVB__InitNodeType9",
        "void __fastcall CFastVB__InitNodeType9(void * node_type9)",
        ("node-type-9", "vtable 0x005ef250", "+0x14 set to 9"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-9", "constructor", "vtable", "fastcall-param-named"},
    ),
    "0x00598a81": (
        "CFastVB__NodeType9__ctor",
        "int CFastVB__NodeType9__ctor(void)",
        ("hidden-ECX", "locked storage", "five stack values"),
        BASE_COMMENT_TAGS | {"node-type", "node-type-9", "constructor", "hidden-ecx", "locked-storage"},
    ),
    "0x00598abd": (
        "CFastVB__NodeType9__dtor",
        "void __fastcall CFastVB__NodeType9__dtor(void * node_type9)",
        ("node-type-9", "CDXTexture__ReleaseNodePayloadChain", "vtable 0x005ef250"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-9", "destructor", "release-chain", "fastcall-param-named"},
    ),
    "0x00598b48": (
        "CFastVB__InitNodeType10",
        "void __fastcall CFastVB__InitNodeType10(void * node_type10)",
        ("node-type-10", "vtable 0x005ef260", "+0x38"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-10", "constructor", "vtable", "owned-resource-slots", "fastcall-param-named"},
    ),
    "0x00598b81": (
        "CFastVB__NodeType10_dtor",
        "void __fastcall CFastVB__NodeType10_dtor(void * node_type10)",
        ("vtable 0x005ef260", "+0x20/+0x24/+0x28/+0x2c/+0x30", "+0x38"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-10", "destructor", "owned-resource-slots", "release-chain", "fastcall-param-named"},
    ),
    "0x00598d6b": (
        "CFastVB__InitNodeType13",
        "void * __fastcall CFastVB__InitNodeType13(void * node_type13)",
        ("node-type-13", "+0x10 set to 3", "returns the initialized node pointer"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-13", "constructor", "vtable", "fastcall-param-named", "return-this"},
    ),
    "0x00598da4": (
        "CDXTexture__NodeType13__ctor",
        "int CDXTexture__NodeType13__ctor(void)",
        ("hidden-ECX", "descriptor dwords", "locked storage"),
        BASE_COMMENT_TAGS | {"node-type", "node-type-13", "constructor", "descriptor-copy", "hidden-ecx", "locked-storage"},
    ),
    "0x00598ddc": (
        "CDXTexture__NodeType13__ctorWithRefBump",
        "int CDXTexture__NodeType13__ctorWithRefBump(void)",
        ("referenced object at +0x18", "vslot +4", "locked storage"),
        BASE_COMMENT_TAGS | {"node-type", "node-type-13", "constructor", "ref-bump", "hidden-ecx", "locked-storage"},
    ),
    "0x00598e22": (
        "CTexture__Dtor_ReleaseNodePayloadByKind",
        "void __fastcall CTexture__Dtor_ReleaseNodePayloadByKind(void * node_payload)",
        ("+0x10 == 5", "+0x10 == 4", "base node-payload chain"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-13", "destructor", "kind-dispatch", "release-chain", "fastcall-param-named"},
    ),
    "0x00598e5d": (
        "CDXTexture__CompareNodePayloadWithOptionalChild",
        "int __thiscall CDXTexture__CompareNodePayloadWithOptionalChild(void * this, void * candidate_payload)",
        ("CTexture__HasSameFormatClassId", "four dwords at +0x10", "optional child"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-13", "comparator", "optional-child", "phantom-param-removed"},
    ),
    "0x00598f22": (
        "CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag",
        "void * __thiscall CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, uint delete_flags)",
        ("delete_flags bit 0", "OID__FreeObject_Callback", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-type", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed"},
    ),
    "0x00598f3e": (
        "CDXTexture__Dtor_NodePayload_DeleteOnFlag",
        "void * __thiscall CDXTexture__Dtor_NodePayload_DeleteOnFlag(void * this, uint delete_flags)",
        ("vtable 0x005ef230", "delete_flags bit 0", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-type", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed"},
    ),
    "0x00598f60": (
        "CFastVB__NodeType8_scalar_deleting_dtor",
        "void * __thiscall CFastVB__NodeType8_scalar_deleting_dtor(void * this, uint delete_flags)",
        ("node-type-8", "delete_flags bit 0", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-8", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed"},
    ),
    "0x00598f82": (
        "CFastVB__NodeType9_scalar_deleting_dtor",
        "void * __thiscall CFastVB__NodeType9_scalar_deleting_dtor(void * this, uint delete_flags)",
        ("node-type-9", "delete_flags bit 0", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-9", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed"},
    ),
    "0x00598fa4": (
        "CFastVB__NodeType10_scalar_deleting_dtor",
        "void * __thiscall CFastVB__NodeType10_scalar_deleting_dtor(void * this, uint delete_flags)",
        ("CFastVB__NodeType10_dtor", "delete_flags bit 0", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-10", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed"},
    ),
    "0x00598fc0": (
        "CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag",
        "void * __thiscall CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, uint delete_flags)",
        ("CTexture__Dtor_ReleaseNodePayloadByKind", "delete_flags bit 0", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"node-type", "node-type-13", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed"},
    ),
    "0x00598fdc": (
        "CTexture__InitOwnedNodeList",
        "void __thiscall CTexture__InitOwnedNodeList(void * this, void * owner_context)",
        ("owner_context", "tail-link pointer", "RET 0x4"),
        BASE_SIGNATURE_TAGS | {"owned-node-list", "constructor", "tail-link", "phantom-param-removed"},
    ),
    "0x00598ff4": (
        "CTexture__FreeOwnedNodeListAndPayloads",
        "void __fastcall CTexture__FreeOwnedNodeListAndPayloads(void * owned_node_list)",
        ("owned-node list", "payloads", "node record"),
        BASE_SIGNATURE_TAGS | {"owned-node-list", "destructor", "payload-free", "fastcall-param-named"},
    ),
}

DOC_TOKENS = (
    "Wave704 node-type constructors/destructors",
    "node-type-constructors-wave704",
    "0x005989c3 CTexture__NodeType8_InitDefaults",
    "0x00598ff4 CTexture__FreeOwnedNodeListAndPayloads",
    "0x00599161 CTexture__ComputeDebugChunkDwordCount",
    "0x0042f220 CSPtrSet__Clear",
)

OVERCLAIM_TOKENS = (
    "runtime texture behavior proven",
    "runtime vertex-buffer behavior proven",
    "node-type enum proven",
    "exact node layout proven",
    "exact descriptor schema proven",
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
        "pre-metadata.tsv": 20,
        "pre-tags.tsv": 20,
        "pre-xrefs.tsv": 45,
        "pre-instructions.tsv": 2420,
        "decompile-pre/index.tsv": 20,
        "post-metadata.tsv": 20,
        "post-tags.tsv": 20,
        "post-xrefs.tsv": 45,
        "post-instructions.tsv": 2420,
        "decompile-post/index.tsv": 20,
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
        require("Wave704 static read-back" in comment, f"missing Wave704 comment at {address}", failures)
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
        "apply-wave704-dry.log": "SUMMARY: updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=17 comment_only_updated=3 missing=0 bad=0",
        "apply-wave704-apply.log": "SUMMARY: updated=20 skipped=0 renamed=0 would_rename=0 signature_updated=17 comment_only_updated=3 missing=0 bad=0",
        "apply-wave704-final-dry.log": "SUMMARY: updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply-wave704-comment-fix-dry.log": "SUMMARY: updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-wave704-comment-fix-apply.log": "SUMMARY: updated=1 skipped=19 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-wave704-final-dry-2.log": "SUMMARY: updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "export-pre-metadata.log": "targets=20 found=20 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "export-pre-xrefs.log": "Wrote 45 rows",
        "export-pre-instructions.log": "Wrote 2420 instruction rows",
        "export-pre-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
        "export-post-metadata-2.log": "targets=20 found=20 missing=0",
        "export-post-tags-2.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "export-post-xrefs-2.log": "Wrote 45 rows",
        "export-post-instructions-2.log": "Wrote 2420 instruction rows",
        "export-post-decompile-2.log": "targets=20 dumped=20 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    queue_refresh = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave704.log")
    require("total_functions=6098 commented_functions=4088" in queue_refresh, "queue refresh count mismatch", failures)
    require("REPORT: Save succeeded" in queue_refresh, "queue refresh save report missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave704_queue_probe.log")
    require("Status: PASS" in queue_probe, "queue probe did not pass", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2010, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 243, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    high_signal_head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(high_signal_head.get("address") == "0x00599161", f"high-signal head address mismatch: {high_signal_head}", failures)
    require(high_signal_head.get("name") == "CTexture__ComputeDebugChunkDwordCount", f"high-signal head name mismatch: {high_signal_head}", failures)

    rows = read_tsv(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv")
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4034, f"strict clean proxy mismatch: {len(clean)}", failures)

    commentless = [row for row in rows if not row.get("comment", "").strip()]
    require(bool(commentless), "no commentless rows found", failures)
    if commentless:
        require(normalize_address(commentless[0].get("address", "")) == "0x0042f220", f"raw commentless head mismatch: {commentless[0]}", failures)
        require(commentless[0].get("name") == "CSPtrSet__Clear", f"raw commentless head name mismatch: {commentless[0]}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup") == "[maintainer-local-ghidra-backup-root]\\BEA_20260521-185425_post_wave704_node_type_constructors_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup.get('file_count')}", failures)
    require(int(backup.get("byte_count", -1)) == 165415815, f"backup byte count mismatch: {backup.get('byte_count')}", failures)
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
        package.get("scripts", {}).get("test:ghidra-node-type-constructors-wave704")
        == "py -3 tools\\ghidra_node_type_constructors_wave704_probe.py --check",
        "package script missing",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave704 node-type constructors/destructors" for row in ledger_rows), "ledger row missing", failures)
    require(
        any(
            row.get("attempt_id") == 20359
            and row.get("task") == "Wave704 node-type constructors/destructors"
            and row.get("readback") == "verified"
            for row in attempt_rows
        ),
        "attempt row missing",
        failures,
    )
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20360, f"next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1100, f"ledger_rows mismatch: {counters.get('ledger_rows')}", failures)
    require(counters.get("attempt_rows") == 20360, f"attempt_rows mismatch: {counters.get('attempt_rows')}", failures)
    require(counters.get("completed") == 1091, f"completed mismatch: {counters.get('completed')}", failures)


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
        print("Wave704 node-type constructors/destructors probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave704 node-type constructors/destructors probe: PASS")
    print("Targets: 20")
    print("Queue: 6098 total, 4088 commented, 2010 commentless, 1216 exact-undefined, 243 param_N")
    print("Strict clean-signature proxy: 4034/6098 = 66.15%")
    print("Raw commentless head: 0x0042f220 CSPtrSet__Clear")
    print("High-signal head: 0x00599161 CTexture__ComputeDebugChunkDwordCount")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
