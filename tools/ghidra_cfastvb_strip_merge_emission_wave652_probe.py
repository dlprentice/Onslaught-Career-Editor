#!/usr/bin/env python3
"""Validate Wave652 CFastVB strip merge/emission read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave652-cfastvb-strip-merge-emission"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_strip_merge_emission_wave652_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
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
    "cfastvb-strip-merge-emission-wave652",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00570cb0": {
        "name": "CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0",
        "signature": "bool __stdcall CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0(void * triangle_record_span, void * edge_buckets, void * candidate_root, void * out_edge_pick)",
        "tags": {"cfastvb", "strip-candidate-selection", "edge-chain-walk", "out-edge-pick", "address-suffixed-helper"},
        "comment_tokens": ("candidate_root", "out_edge_pick", "Static retail decompile/xref evidence only"),
        "decompile": "00570cb0_CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0.c",
        "decompile_tokens": ("candidate_root", "out_edge_pick", "CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90"),
    },
    "0x00570dd0": {
        "name": "CFastVB__MergeAndOrderStripBatches_Impl_00570dd0",
        "signature": "void __thiscall CFastVB__MergeAndOrderStripBatches_Impl_00570dd0(void * this, void * candidate_batch_span, void * overflow_batch_span, void * output_batch_span, void * edi_context)",
        "tags": {"cfastvb", "strip-merge-order", "internal-helper", "candidate-batches", "vertex-cache", "address-suffixed-helper"},
        "comment_tokens": ("internal thiscall helper", "output_batch_span", "CFastVB__CountTriangleVerticesInSet_00572490"),
        "decompile": "00570dd0_CFastVB__MergeAndOrderStripBatches_Impl_00570dd0.c",
        "decompile_tokens": ("candidate_batch_span", "output_batch_span", "CFastVB__CountTriangleVerticesInSet_00572490"),
    },
    "0x00571060": {
        "name": "CFastVB__IsEven",
        "signature": "bool __stdcall CFastVB__IsEven(uint value)",
        "tags": {"cfastvb", "parity-helper", "strip-emission-helper", "ret-0x4"},
        "comment_tokens": ("parity helper", "CFastVB__EmitTriangleStripIndexBuffer", "runtime strip quality"),
        "decompile": "00571060_CFastVB__IsEven.c",
        "decompile_tokens": ("uint value", "0x80000001", "uVar1 != 0", "return"),
    },
    "0x00571080": {
        "name": "CFastVB__IsDirectedEdgeInTriangle",
        "signature": "bool __stdcall CFastVB__IsDirectedEdgeInTriangle(void * triangle, int edge_start, int edge_end)",
        "tags": {"cfastvb", "directed-edge", "triangle-compare", "strip-emission-helper", "ret-0xc"},
        "comment_tokens": ("edge_start->edge_end", "wraparound edge", "strip emission"),
        "decompile": "00571080_CFastVB__IsDirectedEdgeInTriangle.c",
        "decompile_tokens": ("edge_start", "edge_end", "triangle"),
    },
    "0x005710d0": {
        "name": "CFastVB__EmitTriangleStripIndexBuffer",
        "signature": "void __stdcall CFastVB__EmitTriangleStripIndexBuffer(void * strip_batch_span, void * out_index_span, int emit_continuity_flag, void * out_separator_count)",
        "tags": {"cfastvb", "strip-emission", "index-buffer-emission", "separator-count", "triangle-compare"},
        "comment_tokens": ("0xffffffff restart separators", "out_separator_count", "runtime D3D index buffer behavior"),
        "decompile": "005710d0_CFastVB__EmitTriangleStripIndexBuffer.c",
        "decompile_tokens": ("strip_batch_span", "out_separator_count", "CFastVB__IsDirectedEdgeInTriangle"),
    },
    "0x00571870": {
        "name": "CFastVB__HasDuplicateTriangleIndices32",
        "signature": "bool __cdecl CFastVB__HasDuplicateTriangleIndices32(void * triangle)",
        "tags": {"cfastvb", "duplicate-indices", "triangle-compare", "dword-indices", "cdecl"},
        "comment_tokens": ("32-bit triangle triplet", "degenerate triangles", "merge/order paths"),
        "decompile": "00571870_CFastVB__HasDuplicateTriangleIndices32.c",
        "decompile_tokens": ("triangle", "return", "bool"),
    },
    "0x00571890": {
        "name": "CFastVB__HasDuplicateTriangleIndices16",
        "signature": "bool __stdcall CFastVB__HasDuplicateTriangleIndices16(int index_a, int index_b, int index_c)",
        "tags": {"cfastvb", "duplicate-indices", "triangle-compare", "word-indices", "ret-0xc"},
        "comment_tokens": ("low 16-bit", "BuildTriangleAdjacency", "degenerate-triangle"),
        "decompile": "00571890_CFastVB__HasDuplicateTriangleIndices16.c",
        "decompile_tokens": ("index_a", "index_b", "index_c"),
    },
    "0x005718c0": {
        "name": "CFastVB__MergeAndOrderStripBatches",
        "signature": "void __thiscall CFastVB__MergeAndOrderStripBatches(void * this, void * candidate_batch_span, void * ordered_batch_span, void * edge_buckets, void * output_batch_span, void * edi_context)",
        "tags": {"cfastvb", "strip-merge-order", "batch-splitting", "vertex-cache", "candidate-batches"},
        "comment_tokens": ("batch order", "edge-resolution", "vertex-cache scoring"),
        "decompile": "005718c0_CFastVB__MergeAndOrderStripBatches.c",
        "decompile_tokens": ("candidate_batch_span", "ordered_batch_span", "CFastVB__MergeAndOrderStripBatches_Impl_00570dd0"),
    },
}

DOC_TOKENS = (
    "Wave652 CFastVB strip merge/emission hardening",
    "3536",
    "2557",
    "772",
    "0x005721f0 CFastVB__SeedVertexCacheFromTriangleRefs",
    "G:\\GhidraBackups\\BEA_20260520-185249_post_wave652_cfastvb_strip_merge_emission_verified",
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
        text = read_text(BASE / "decompile-post" / spec["decompile"])
        require_tokens(f"{address} decompile", text, spec["decompile_tokens"], failures)


def check_counts_and_logs(failures: list[str]) -> None:
    for path, expected in (
        (BASE / "apply-wave652-dry.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "signature_updated": 8, "missing": 0, "bad": 0}),
        (BASE / "apply-wave652-apply.log", {"updated": 8, "skipped": 0, "renamed": 0, "would_rename": 0, "signature_updated": 8, "missing": 0, "bad": 0}),
        (BASE / "apply-wave652-final-dry.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0}),
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
        "post-metadata": 8,
        "post-tags": 8,
        "post-xrefs": 16,
        "post-instructions": 200,
        "post-decompile": 8,
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
        "commentlessFunctionCount": 2557,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 772,
    }
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    first = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if first.get("address") != "0x005721f0" or first.get("name") != "CFastVB__SeedVertexCacheFromTriangleRefs":
        failures.append(f"queue head mismatch: {first}")

    backup = read_json(BACKUP_SUMMARY)
    destination = backup.get("Destination", "")
    if "post_wave652_cfastvb_strip_merge_emission_verified" not in destination:
        failures.append(f"backup destination mismatch: {destination}")
    if backup.get("DiffCount") != 0:
        failures.append(f"backup DiffCount mismatch: {backup.get('DiffCount')}")
    if int(backup.get("FileCount", 0)) != 18:
        failures.append(f"backup FileCount mismatch: {backup.get('FileCount')}")


def check_docs(failures: list[str]) -> None:
    for path in (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXMESHVB_DOC,
        FASTVB_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        LEDGER,
        ATTEMPT_LOG,
        TRACKING,
    ):
        text = read_text(path)
        require_tokens(path.name, text, DOC_TOKENS, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path} contains overclaim token: {token}")
    package = read_json(PACKAGE_JSON)
    if "test:ghidra-cfastvb-strip-merge-emission-wave652" not in package.get("scripts", {}):
        failures.append("package.json missing Wave652 probe script")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_tags(failures)
    check_decompiles(failures)
    check_counts_and_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave652 CFastVB strip merge/emission probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave652 CFastVB strip merge/emission probe: PASS")
    print("Targets: 8")
    print("Queue: 6093 total, 3536 commented, 2557 commentless, 1217 exact-undefined, 772 param_N")
    print("Next head: 0x005721f0 CFastVB__SeedVertexCacheFromTriangleRefs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
