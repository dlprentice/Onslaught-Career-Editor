#!/usr/bin/env python3
"""Validate Wave655 CFastVB span/tree utility read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave655-cfastvb-span-tree"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_span_tree_wave655_2026-05-20.md"
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
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "cfastvb-span-tree-wave655",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00572f00": {
        "name": "CFastVB__InitDwordSpanBuilderState_00572f00",
        "signature": "void __thiscall CFastVB__InitDwordSpanBuilderState_00572f00(void * this, void * source_flag, void * unused_context)",
        "tags": {"cfastvb", "span-builder", "dword-span", "address-suffixed-helper"},
        "comment_tokens": ("source_flag", "+0x04/+0x08/+0x0c", "runtime strip quality"),
        "decompile": "00572f00_CFastVB__InitDwordSpanBuilderState_00572f00.c",
    },
    "0x00572f20": {
        "name": "CFastVB__AppendDwordRangeToSpanBuilder_00572f20",
        "signature": "void __thiscall CFastVB__AppendDwordRangeToSpanBuilder_00572f20(void * this, void * dest_cursor, void * range_cursor, void * unused_context)",
        "tags": {"cfastvb", "span-builder", "dword-copy", "triangle-adjacency"},
        "comment_tokens": ("copies dwords", "this+0x08", "triangle-adjacency"),
        "decompile": "00572f20_CFastVB__AppendDwordRangeToSpanBuilder_00572f20.c",
    },
    "0x00572f50": {
        "name": "CFastVB__CopyDwordRange",
        "signature": "void __stdcall CFastVB__CopyDwordRange(void * range_start, void * range_end, void * dest_or_null)",
        "tags": {"cfastvb", "span-copy", "dword-copy", "ret-0xc"},
        "comment_tokens": ("[range_start, range_end)", "dest_or_null", "triangle adjacency"),
        "decompile": "00572f50_CFastVB__CopyDwordRange.c",
    },
    "0x00572f80": {
        "name": "CFastVB__GetWordCapacity",
        "signature": "int __fastcall CFastVB__GetWordCapacity(void * span_state)",
        "tags": {"cfastvb", "word-span", "capacity", "strip-pipeline"},
        "comment_tokens": ("returns zero", "(end - begin) / 2", "BuildStripBatchesFromIndexBuffer"),
        "decompile": "00572f80_CFastVB__GetWordCapacity.c",
    },
    "0x00572fa0": {
        "name": "CFastVB__InsertWordAndGrow",
        "signature": "void * __thiscall CFastVB__InsertWordAndGrow(void * this, void * insert_at, void * value_ptr, void * unused_context)",
        "tags": {"cfastvb", "word-span", "insert-grow", "allocation"},
        "comment_tokens": ("word-span insert", "allocates a larger buffer", "returns the inserted element pointer"),
        "decompile": "00572fa0_CFastVB__InsertWordAndGrow.c",
    },
    "0x00573140": {
        "name": "CFastVB__CopyWordRange",
        "signature": "void __stdcall CFastVB__CopyWordRange(void * range_start, void * range_end, void * dest_or_null)",
        "tags": {"cfastvb", "word-copy", "word-span", "ret-0xc"},
        "comment_tokens": ("word range copy", "2-byte steps", "word-span grow-insert"),
        "decompile": "00573140_CFastVB__CopyWordRange.c",
    },
    "0x00573170": {
        "name": "CFastVB__InsertDwordAndGrow",
        "signature": "void * __thiscall CFastVB__InsertDwordAndGrow(void * this, void * insert_at, void * value_ptr, void * unused_context)",
        "tags": {"cfastvb", "dword-span", "insert-grow", "allocation"},
        "comment_tokens": ("dword-span insert", "copies prefix/value/suffix", "strip construction"),
        "decompile": "00573170_CFastVB__InsertDwordAndGrow.c",
    },
    "0x00573310": {
        "name": "CFastVB__CountDwordsFromPointerSpan",
        "signature": "int __fastcall CFastVB__CountDwordsFromPointerSpan(void * span_state)",
        "tags": {"cfastvb", "dword-span", "span-count", "strip-pipeline"},
        "comment_tokens": ("(current - begin) / 4", "dword grow-insert", "exact container type"),
        "decompile": "00573310_CFastVB__CountDwordsFromPointerSpan.c",
    },
    "0x00573330": {
        "name": "CFastVB__GetTreeRootNode_00573330",
        "signature": "void __thiscall CFastVB__GetTreeRootNode_00573330(void * this, void * out_node_slot, void * unused_context)",
        "tags": {"cfastvb", "red-black-tree", "tree-root", "shared-sentinel"},
        "comment_tokens": ("root node", "this+0x04", "owner/template identity"),
        "decompile": "00573330_CFastVB__GetTreeRootNode_00573330.c",
    },
    "0x00573340": {
        "name": "CFastVB__InsertNodeIntoRBTreeWithHint_00573340",
        "signature": "void __thiscall CFastVB__InsertNodeIntoRBTreeWithHint_00573340(void * this, void * out_insert_result, void * key_ptr, void * unused_context)",
        "tags": {"cfastvb", "red-black-tree", "insert-node", "uint-key", "shared-sentinel"},
        "comment_tokens": ("uint-key red-black-tree", "0x14-byte node", "rotations/recolors"),
        "decompile": "00573340_CFastVB__InsertNodeIntoRBTreeWithHint_00573340.c",
    },
    "0x00573560": {
        "name": "CFastVB__EraseNodeRangeFromRBTree_00573560",
        "signature": "void __thiscall CFastVB__EraseNodeRangeFromRBTree_00573560(void * this, void * out_next_slot, void * first_node, void * last_node, void * unused_context)",
        "tags": {"cfastvb", "red-black-tree", "erase-range", "shared-sentinel"},
        "comment_tokens": ("erase-range helper", "CTexture__EraseNodeFromTree", "node payload ownership"),
        "decompile": "00573560_CFastVB__EraseNodeRangeFromRBTree_00573560.c",
    },
    "0x00573630": {
        "name": "RBTree__FindLowerBoundByUIntKey",
        "signature": "void __thiscall RBTree__FindLowerBoundByUIntKey(void * this, void * out_node_slot, void * key_ptr, void * unused_context)",
        "tags": {"red-black-tree", "lower-bound", "uint-key", "strip-generation", "shared-sentinel"},
        "comment_tokens": ("lower-bound helper", "key is not less than key_ptr", "strip-candidate generation"),
        "decompile": "00573630_RBTree__FindLowerBoundByUIntKey.c",
    },
    "0x005736a0": {
        "name": "MemCopyU16Elements",
        "signature": "void __stdcall MemCopyU16Elements(void * dest_or_null, int element_count, void * value_ptr)",
        "tags": {"word-span", "fill-helper", "ret-0xc", "retained-name"},
        "comment_tokens": ("retained-name", "16-bit value", "destination is null"),
        "decompile": "005736a0_MemCopyU16Elements.c",
    },
    "0x005736d0": {
        "name": "CFastVB__InsertDwordSpanFilled",
        "signature": "void __thiscall CFastVB__InsertDwordSpanFilled(void * this, void * insert_at, int element_count, void * value_ptr, void * unused_context)",
        "tags": {"cfastvb", "dword-span", "fill-insert", "allocation"},
        "comment_tokens": ("element_count copies", "allocating a larger buffer", "candidate generation"),
        "decompile": "005736d0_CFastVB__InsertDwordSpanFilled.c",
    },
    "0x00573d00": {
        "name": "RBTree__InitUIntKeyTreeWithSharedSentinel",
        "signature": "void __fastcall RBTree__InitUIntKeyTreeWithSharedSentinel(void * tree_state)",
        "tags": {"red-black-tree", "init-tree", "uint-key", "shared-sentinel"},
        "comment_tokens": ("shared sentinel DAT_009d0c44", "0x14-byte header node", "header root/min/max links"),
        "decompile": "00573d00_RBTree__InitUIntKeyTreeWithSharedSentinel.c",
    },
    "0x00573ff0": {
        "name": "CFastVB__FillDwordSpanWithValue_00573ff0",
        "signature": "void __stdcall CFastVB__FillDwordSpanWithValue_00573ff0(void * dest_or_null, int element_count, void * value_ptr)",
        "tags": {"cfastvb", "dword-span", "fill-helper", "strip-pipeline"},
        "comment_tokens": ("dword referenced by value_ptr", "skipping writes", "strip emission"),
        "decompile": "00573ff0_CFastVB__FillDwordSpanWithValue_00573ff0.c",
    },
    "0x00574020": {
        "name": "CFastVB__RBTreeRotateLeft_00574020",
        "signature": "void __thiscall CFastVB__RBTreeRotateLeft_00574020(void * this, void * pivot_node, void * unused_context)",
        "tags": {"cfastvb", "red-black-tree", "left-rotate", "insert-fixup", "shared-sentinel"},
        "comment_tokens": ("left-rotation helper", "pivot_node", "insert-fixup"),
        "decompile": "00574020_CFastVB__RBTreeRotateLeft_00574020.c",
    },
    "0x005741d0": {
        "name": "CFastVB__CopyWordRange_Strict",
        "signature": "void __cdecl CFastVB__CopyWordRange_Strict(void * range_start, void * range_end, void * dest)",
        "tags": {"cfastvb", "word-span", "strict-copy", "strip-pipeline"},
        "comment_tokens": ("strict word copy", "unconditionally copies", "strip-batch building"),
        "decompile": "005741d0_CFastVB__CopyWordRange_Strict.c",
    },
    "0x00574200": {
        "name": "CFastVB__CopyDwordRange_Strict",
        "signature": "void __cdecl CFastVB__CopyDwordRange_Strict(void * range_start, void * range_end, void * dest)",
        "tags": {"cfastvb", "dword-span", "strict-copy", "strip-pipeline"},
        "comment_tokens": ("strict dword copy", "unconditionally copies", "MergeAndOrderStripBatches"),
        "decompile": "00574200_CFastVB__CopyDwordRange_Strict.c",
    },
    "0x00574230": {
        "name": "CFastVB__AssignDwordIfDestNotNull",
        "signature": "void __cdecl CFastVB__AssignDwordIfDestNotNull(void * dest_or_null, void * source_value)",
        "tags": {"cfastvb", "dword-copy", "assign-if-dest", "strip-pipeline"},
        "comment_tokens": ("copies one dword", "source_value", "CTexture tree insert"),
        "decompile": "00574230_CFastVB__AssignDwordIfDestNotNull.c",
    },
    "0x00574250": {
        "name": "CFastVB__AssignWordIfDestNotNull",
        "signature": "void __cdecl CFastVB__AssignWordIfDestNotNull(void * dest_or_null, void * source_value)",
        "tags": {"cfastvb", "word-copy", "assign-if-dest", "strip-pipeline"},
        "comment_tokens": ("copies one word", "source_value", "word-span grow-insert"),
        "decompile": "00574250_CFastVB__AssignWordIfDestNotNull.c",
    },
}

DOC_TOKENS = (
    "Wave655 CFastVB span/tree utility hardening",
    "3572",
    "2521",
    "736",
    "0x00574270 CDXTexture__FindFormatDescriptorById",
    "G:\\GhidraBackups\\BEA_20260520-202319_post_wave655_cfastvb_span_tree_verified",
)

OVERCLAIM_TOKENS = (
    "runtime strip quality proven",
    "runtime texture behavior proven",
    "concrete span layout proven",
    "concrete node layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
    "fully recovered",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "BAD:", "BADNAME:", "MISSING:", "Save blocked", "Read-back"):
        if bad_token in text:
            failures.append(f"{path.name} contains bad token: {bad_token}")


def check_metadata(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-metadata.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-metadata target set mismatch: {sorted(set(rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        require_tokens(f"{address} comment", row.get("comment", ""), ("Wave655 CFastVB span/tree utility hardening",) + spec["comment_tokens"], failures)


def check_tags(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-tags.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-tags target set mismatch: {sorted(set(rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        missing = sorted((COMMON_TAGS | spec["tags"]) - tags)
        if missing:
            failures.append(f"{address} missing tags: {missing}")


def check_decompiles(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "decompile-post" / "index.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"decompile index target set mismatch: {sorted(set(rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row and row.get("status") != "OK":
            failures.append(f"{address} decompile status mismatch: {row.get('status')}")
        decompile_path = BASE / "decompile-post" / spec["decompile"]
        if not decompile_path.is_file():
            failures.append(f"{address} missing decompile file: {spec['decompile']}")


def check_counts_and_logs(failures: list[str]) -> None:
    for path, expected in (
        (BASE / "apply-wave655-dry.log", {"updated": 0, "skipped": 21, "renamed": 0, "would_rename": 0, "signature_updated": 21, "missing": 0, "bad": 0}),
        (BASE / "apply-wave655-apply.log", {"updated": 21, "skipped": 0, "renamed": 0, "would_rename": 0, "signature_updated": 21, "missing": 0, "bad": 0}),
        (BASE / "apply-wave655-final-dry.log", {"updated": 0, "skipped": 21, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0}),
    ):
        require_log_summary(path, expected, failures)

    counts = {
        "post-metadata": len(read_tsv_rows(BASE / "post-metadata.tsv")),
        "post-tags": len(read_tsv_rows(BASE / "post-tags.tsv")),
        "post-xrefs": len(read_tsv_rows(BASE / "post-xrefs.tsv")),
        "post-instructions": len(read_tsv_rows(BASE / "post-instructions.tsv")),
        "post-decompile": len(read_tsv_rows(BASE / "decompile-post" / "index.tsv")),
    }
    expected_counts = {
        "post-metadata": 21,
        "post-tags": 21,
        "post-xrefs": 117,
        "post-instructions": 1869,
        "post-decompile": 21,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            failures.append(f"{key} count mismatch: {counts.get(key)} != {expected}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    expected_signals = {
        "commentlessFunctionCount": 2521,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 736,
    }
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    first = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if first.get("address") != "0x00574270" or first.get("name") != "CDXTexture__FindFormatDescriptorById":
        failures.append(f"queue head mismatch: {first}")

    backup = read_json(BACKUP_SUMMARY)
    destination = backup.get("BackupPath", backup.get("backupPath", ""))
    if "post_wave655_cfastvb_span_tree_verified" not in destination:
        failures.append(f"backup destination mismatch: {destination}")
    if backup.get("DiffCount", backup.get("diffCount")) != 0:
        failures.append(f"backup DiffCount mismatch: {backup.get('DiffCount', backup.get('diffCount'))}")
    if int(backup.get("FileCount", backup.get("fileCount", 0))) != 19:
        failures.append(f"backup FileCount mismatch: {backup.get('FileCount', backup.get('fileCount'))}")
    if int(backup.get("ByteCount", backup.get("byteCount", 0))) != 163154823:
        failures.append(f"backup byte count mismatch: {backup.get('ByteCount', backup.get('byteCount'))}")


def check_docs(failures: list[str]) -> None:
    docs = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "fastvb doc": read_text(FASTVB_DOC),
        "ghidra reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
        "tracking": read_text(TRACKING),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
    }
    for label, text in docs.items():
        require_tokens(label, text, DOC_TOKENS, failures)
        for bad in OVERCLAIM_TOKENS:
            if bad in text:
                failures.append(f"{label} contains overclaim token: {bad}")
    package_json = read_text(PACKAGE_JSON)
    if "test:ghidra-cfastvb-span-tree-wave655" not in package_json:
        failures.append("package.json missing Wave655 npm script")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Run validation checks.")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    failures: list[str] = []
    check_metadata(failures)
    check_tags(failures)
    check_decompiles(failures)
    check_counts_and_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave655 CFastVB span/tree probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave655 CFastVB span/tree probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
