#!/usr/bin/env python3
"""Validate Wave650 CDXMeshVB/CFastVB strip read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave650-cdxmeshvb-cfastvb-strip"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxmeshvb_cfastvb_strip_wave650_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "cdxmeshvb-cfastvb-strip-wave650",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x0056eb50": {
        "name": "CDXMeshVB__SetTriangleStripDebugFlag",
        "signature": "void __cdecl CDXMeshVB__SetTriangleStripDebugFlag(int enabled)",
        "tags": {"cdxmeshvb", "strip-state-setter", "debug-strip-flag", "global-009d0c40"},
        "comment_tokens": ("DAT_009d0c40", "CLandscapeIB__CreateIndexBuffer", "Static retail decompile/xref evidence only"),
        "decompile": "0056eb50_CDXMeshVB__SetTriangleStripDebugFlag.c",
        "decompile_tokens": ("DAT_009d0c40 = (undefined1)enabled;",),
    },
    "0x0056eb60": {
        "name": "CDXMeshVB__SetEmitDegenerateFlag",
        "signature": "void __cdecl CDXMeshVB__SetEmitDegenerateFlag(int enabled)",
        "tags": {"cdxmeshvb", "strip-state-setter", "degenerate-strip-flag", "global-00656e5c"},
        "comment_tokens": ("DAT_00656e5c", "strip-batch setup", "Static retail decompile/xref evidence only"),
        "decompile": "0056eb60_CDXMeshVB__SetEmitDegenerateFlag.c",
        "decompile_tokens": ("DAT_00656e5c = enabled;",),
    },
    "0x0056eb70": {
        "name": "CDXMeshVB__SetWordIndexModeFlag",
        "signature": "void __cdecl CDXMeshVB__SetWordIndexModeFlag(int enabled)",
        "tags": {"cdxmeshvb", "strip-state-setter", "word-index-mode", "global-00656e60"},
        "comment_tokens": ("DAT_00656e60", "packed word-index stream", "Static retail decompile/xref evidence only"),
        "decompile": "0056eb70_CDXMeshVB__SetWordIndexModeFlag.c",
        "decompile_tokens": ("DAT_00656e60 = (undefined1)enabled;",),
    },
    "0x0056eb80": {
        "name": "CDXMeshVB__SetBatchSplitThreshold",
        "signature": "void __cdecl CDXMeshVB__SetBatchSplitThreshold(int threshold)",
        "tags": {"cdxmeshvb", "strip-state-setter", "batch-split-threshold", "global-009d0c3c"},
        "comment_tokens": ("DAT_009d0c3c", "triangle-strip batches", "Static retail decompile/xref evidence only"),
        "decompile": "0056eb80_CDXMeshVB__SetBatchSplitThreshold.c",
        "decompile_tokens": ("DAT_009d0c3c = threshold;",),
    },
    "0x0056eb90": {
        "name": "CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer",
        "signature": "void __cdecl CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer(void * index_words, uint index_word_count, void * out_batch_records, void * out_batch_count)",
        "tags": {"cdxmeshvb", "strip-batch-build", "index-buffer-emission", "cfastvb-pipeline", "out-batch-records"},
        "comment_tokens": ("CFastVB pipeline", "0x0c-byte batch records", "Static retail decompile/xref evidence only"),
        "decompile": "0056eb90_CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer.c",
        "decompile_tokens": ("CFastVB__BuildStripBatchesFromIndexBuffer", "out_batch_records", "out_batch_count"),
    },
    "0x0056f260": {
        "name": "CFastVB__ReleaseBufferAndResetTriplet_0056f260",
        "signature": "void __fastcall CFastVB__ReleaseBufferAndResetTriplet_0056f260(void * span)",
        "tags": {"cfastvb", "span-release-reset", "strip-cleanup", "duplicate-helper-0056f260"},
        "comment_tokens": ("span+0x4", "BuildTriangleStripFromSeedRecord cleanup", "Static retail decompile/xref evidence only"),
        "decompile": "0056f260_CFastVB__ReleaseBufferAndResetTriplet_0056f260.c",
        "decompile_tokens": ("OID__FreeObject_Callback(*(void **)((int)span + 4));",),
    },
    "0x0056f280": {
        "name": "CFastVB__CountWordElements",
        "signature": "int __fastcall CFastVB__CountWordElements(void * span)",
        "tags": {"cfastvb", "word-span", "count-elements", "index-word-count"},
        "comment_tokens": ("(end - begin) >> 1", "16-bit index spans", "Static retail decompile/xref evidence only"),
        "decompile": "0056f280_CFastVB__CountWordElements.c",
        "decompile_tokens": ("return *(int *)((int)span + 8) - *(int *)((int)span + 4) >> 1;",),
    },
    "0x0056f2a0": {
        "name": "CFastVB__InsertWordSpanFilled",
        "signature": "void __thiscall CFastVB__InsertWordSpanFilled(void * this, void * insert_word_ptr, uint word_count, void * fill_word_ptr, void * edi_context)",
        "tags": {"cfastvb", "word-span", "insert-filled", "span-grow"},
        "comment_tokens": ("16-bit span", "fill_word_ptr", "reallocates through OID helpers"),
        "decompile": "0056f2a0_CFastVB__InsertWordSpanFilled.c",
        "decompile_tokens": ("word_count", "fill_word_ptr", "OID__AllocObject_DefaultTag_00662b2c"),
    },
    "0x0056f4b0": {
        "name": "CFastVB__CopyWordRangeToBufferAndAdvanceEnd",
        "signature": "void __thiscall CFastVB__CopyWordRangeToBufferAndAdvanceEnd(void * this, void * write_ptr, void * src_begin, void * edi_context)",
        "tags": {"cfastvb", "word-span", "copy-range", "advance-end"},
        "comment_tokens": ("src_begin", "advances this+0x8", "Static retail decompile/callsite evidence only"),
        "decompile": "0056f4b0_CFastVB__CopyWordRangeToBufferAndAdvanceEnd.c",
        "decompile_tokens": ("src_begin", "write_ptr", "*(void **)((int)this + 8) = write_ptr;"),
    },
    "0x0056f500": {
        "name": "CFastVB__InitWordSpanHeader",
        "signature": "void __fastcall CFastVB__InitWordSpanHeader(void * span)",
        "tags": {"cfastvb", "word-span", "initializer", "triplet-clear"},
        "comment_tokens": ("first byte", "+0x4/+0x8/+0x0c", "Static retail decompile evidence only"),
        "decompile": "0056f500_CFastVB__InitWordSpanHeader.c",
        "decompile_tokens": ("*(undefined4 *)((int)span + 4) = 0;",),
    },
    "0x0056f520": {
        "name": "CFastVB__ReleaseBufferAndResetTriplet_0056f520",
        "signature": "void __fastcall CFastVB__ReleaseBufferAndResetTriplet_0056f520(void * span)",
        "tags": {"cfastvb", "span-release-reset", "duplicate-helper-0056f520", "strip-cleanup"},
        "comment_tokens": ("duplicate fastcall release/reset body", "distinct address-suffixed helper", "Static retail decompile/xref evidence only"),
        "decompile": "0056f520_CFastVB__ReleaseBufferAndResetTriplet_0056f520.c",
        "decompile_tokens": ("OID__FreeObject_Callback(*(void **)((int)span + 4));",),
    },
    "0x0056f540": {
        "name": "CFastVB__FindEdgeRecord",
        "signature": "void * __cdecl CFastVB__FindEdgeRecord(void * edge_buckets, int vertex_a, int vertex_b)",
        "tags": {"cfastvb", "triangle-adjacency", "edge-record-lookup", "returns-pointer"},
        "comment_tokens": ("edge-record bucket chain", "+0x14 and +0x18", "Static retail decompile/xref evidence only"),
        "decompile": "0056f540_CFastVB__FindEdgeRecord.c",
        "decompile_tokens": ("edge_buckets", "vertex_a", "vertex_b"),
    },
    "0x0056f580": {
        "name": "CFastVB__ResolveOppositeAdjacencyRecord",
        "signature": "void * __cdecl CFastVB__ResolveOppositeAdjacencyRecord(void * edge_buckets, int vertex_a, int vertex_b, void * current_triangle)",
        "tags": {"cfastvb", "triangle-adjacency", "opposite-record", "returns-pointer"},
        "comment_tokens": ("opposite triangle pointer", "+0x4/+0x8 pair", "Static retail decompile/xref evidence only"),
        "decompile": "0056f580_CFastVB__ResolveOppositeAdjacencyRecord.c",
        "decompile_tokens": ("CFastVB__FindEdgeRecord(edge_buckets,vertex_a,vertex_b)", "current_triangle"),
    },
    "0x0056f5c0": {
        "name": "CFastVB__ContainsTriangleTriplet",
        "signature": "uint __stdcall CFastVB__ContainsTriangleTriplet(void * triangle, void * triangle_span)",
        "tags": {"cfastvb", "triangle-adjacency", "triangle-triplet-predicate", "ret-0x8"},
        "comment_tokens": ("low-byte true value", "first three dwords", "Static retail decompile/xref evidence only"),
        "decompile": "0056f5c0_CFastVB__ContainsTriangleTriplet.c",
        "decompile_tokens": ("triangle_span", "triangle", "CONCAT31"),
    },
    "0x0056f620": {
        "name": "CFastVB__BuildTriangleAdjacency",
        "signature": "void __thiscall CFastVB__BuildTriangleAdjacency(void * this, void * triangle_record_span, void * edge_buckets, int max_vertex_index, uint mode_flags)",
        "tags": {"cfastvb", "triangle-adjacency", "edge-record-build", "stripify"},
        "comment_tokens": ("0x18-byte triangle records", "0x1c-byte edge records", "duplicate/non-manifold diagnostics"),
        "decompile": "0056f620_CFastVB__BuildTriangleAdjacency.c",
        "decompile_tokens": ("triangle_record_span", "edge_buckets", "BuildStripifyInfo__>_2_triangles"),
    },
}

DOC_TOKENS = (
    "Wave650 CDXMeshVB/CFastVB strip hardening",
    "3518",
    "2575",
    "790",
    "0x0056fce0 CFastVB__SelectTriangleWithMaxOpenEdges",
    "G:\\GhidraBackups\\BEA_20260520-215037_post_wave650_cdxmeshvb_cfastvb_strip_verified",
)

OVERCLAIM_TOKENS = (
    "runtime strip quality proven",
    "concrete D3D output proven",
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
        require_tokens(f"{address} comment", row.get("comment", ""), spec["comment_tokens"], failures)


def check_tags(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-tags.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-tags target set mismatch: {sorted(set(rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        required = COMMON_TAGS | spec["tags"]
        missing = sorted(required - tags)
        if missing:
            failures.append(f"{address} missing tags: {missing}")


def check_decompiles(failures: list[str]) -> None:
    index_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "decompile-post" / "index.tsv")}
    if set(index_rows) != set(TARGETS):
        failures.append(f"decompile index target set mismatch: {sorted(set(index_rows) ^ set(TARGETS))}")
    for address, spec in TARGETS.items():
        row = index_rows.get(address)
        if row and row.get("status") != "OK":
            failures.append(f"{address} decompile status mismatch: {row.get('status')}")
        text = read_text(BASE / "decompile-post" / spec["decompile"])
        require_tokens(f"{address} decompile", text, spec["decompile_tokens"], failures)


def check_counts_and_logs(failures: list[str]) -> None:
    for path, expected in (
        (BASE / "apply-dry.log", {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 0, "signature_updated": 15, "missing": 0, "bad": 0}),
        (BASE / "apply.log", {"updated": 15, "skipped": 0, "renamed": 0, "would_rename": 0, "signature_updated": 15, "missing": 0, "bad": 0}),
        (BASE / "apply-final-dry.log", {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0}),
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
        "post-metadata": 15,
        "post-tags": 15,
        "post-xrefs": 86,
        "post-instructions": 1335,
        "post-decompile": 15,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            failures.append(f"{key} count mismatch: {counts.get(key)} != {expected}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    expected = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 2575,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 790,
    }
    if queue.get("totalFunctions") != expected["totalFunctions"]:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key, value in expected.items():
        if key == "totalFunctions":
            continue
        if signals.get(key) != value:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {value}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0056fce0" or head.get("name") != "CFastVB__SelectTriangleWithMaxOpenEdges":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("Destination") != r"G:\GhidraBackups\BEA_20260520-215037_post_wave650_cdxmeshvb_cfastvb_strip_verified":
        failures.append(f"backup destination mismatch: {backup.get('Destination')}")
    if backup.get("FileCount") != 19:
        failures.append(f"backup file count mismatch: {backup.get('FileCount')}")
    if int(backup.get("TotalBytes", 0)) != 162990983:
        failures.append(f"backup byte count mismatch: {backup.get('TotalBytes')}")
    if backup.get("DiffCount") != 0:
        failures.append(f"backup diff count mismatch: {backup.get('DiffCount')}")


def check_docs(failures: list[str]) -> None:
    docs = {
        "public note": PUBLIC_NOTE,
        "package": PACKAGE_JSON,
        "function index": FUNCTION_INDEX,
        "DXMeshVB doc": DXMESHVB_DOC,
        "GHIDRA reference": GHIDRA_REFERENCE,
        "campaign": CAMPAIGN,
        "backlog": BACKLOG,
        "ledger": LEDGER,
        "attempt log": ATTEMPT_LOG,
        "tracking": TRACKING,
    }
    for label, path in docs.items():
        text = read_text(path)
        if label == "package":
            require_tokens(label, text, ("test:ghidra-cdxmeshvb-cfastvb-strip-wave650",), failures)
        else:
            require_tokens(label, text, DOC_TOKENS, failures)
        for bad in OVERCLAIM_TOKENS:
            if bad in text:
                failures.append(f"{label} contains overclaim token: {bad}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate artifacts and docs")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_tags(failures)
        check_decompiles(failures)
        check_counts_and_logs(failures)
        check_queue_and_backup(failures)
        check_docs(failures)
    except Exception as exc:  # pragma: no cover - command-line guard
        failures.append(f"{type(exc).__name__}: {exc}")

    if failures:
        print("Wave650 CDXMeshVB/CFastVB strip probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave650 CDXMeshVB/CFastVB strip probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
