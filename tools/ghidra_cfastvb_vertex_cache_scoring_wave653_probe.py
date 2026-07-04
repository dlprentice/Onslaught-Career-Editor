#!/usr/bin/env python3
"""Validate Wave653 CFastVB vertex-cache/scoring read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave653-cfastvb-vertex-cache-scoring"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_vertex_cache_scoring_wave653_2026-05-20.md"
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
    "cfastvb-vertex-cache-scoring-wave653",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x005721f0": {
        "name": "CFastVB__SeedVertexCacheFromTriangleRefs",
        "signature": "void __stdcall CFastVB__SeedVertexCacheFromTriangleRefs(void * vertex_cache, void * strip_batch)",
        "tags": {"cfastvb", "vertex-cache", "strip-batch", "batch-ordering", "ret-0x8"},
        "comment_tokens": ("strip_batch", "vertex_cache", "overlap scoring"),
        "decompile": "005721f0_CFastVB__SeedVertexCacheFromTriangleRefs.c",
        "decompile_tokens": ("vertex_cache", "strip_batch", "+ 0x10"),
    },
    "0x00572310": {
        "name": "CFastVB__SeedVertexCacheFromTriangle",
        "signature": "void __stdcall CFastVB__SeedVertexCacheFromTriangle(void * vertex_cache, void * triangle)",
        "tags": {"cfastvb", "vertex-cache", "triangle-cache-seed", "stale-owner-corrected", "ret-0x8"},
        "comment_tokens": ("stale CDXTexture owner label", "triangle", "vertex_cache"),
        "decompile": "00572310_CFastVB__SeedVertexCacheFromTriangle.c",
        "decompile_tokens": ("CFastVB__SeedVertexCacheFromTriangle", "triangle", "vertex_cache"),
    },
    "0x005723c0": {
        "name": "CFastVB__ComputeAverageVertexOverlapScore_005723c0",
        "signature": "double __stdcall CFastVB__ComputeAverageVertexOverlapScore_005723c0(void * vertex_cache, void * strip_batch)",
        "tags": {"cfastvb", "vertex-cache", "overlap-score", "batch-ordering", "address-suffixed-helper"},
        "comment_tokens": ("average overlap score", "vertex_cache", "strip_batch"),
        "decompile": "005723c0_CFastVB__ComputeAverageVertexOverlapScore_005723c0.c",
        "decompile_tokens": ("double CFastVB__ComputeAverageVertexOverlapScore_005723c0", "vertex_cache", "strip_batch"),
    },
    "0x00572490": {
        "name": "CFastVB__CountTriangleVerticesInSet_00572490",
        "signature": "int __stdcall CFastVB__CountTriangleVerticesInSet_00572490(void * vertex_cache, void * triangle)",
        "tags": {"cfastvb", "vertex-cache", "triangle-score", "batch-ordering", "address-suffixed-helper"},
        "comment_tokens": ("triangle's three vertex ids", "vertex_cache", "temporary batch"),
        "decompile": "00572490_CFastVB__CountTriangleVerticesInSet_00572490.c",
        "decompile_tokens": ("int CFastVB__CountTriangleVerticesInSet_00572490", "vertex_cache", "triangle"),
    },
    "0x00572500": {
        "name": "CFastVB__CountResolvedOppositeEdges",
        "signature": "char __stdcall CFastVB__CountResolvedOppositeEdges(void * triangle, void * edge_buckets)",
        "tags": {"cfastvb", "triangle-adjacency", "edge-resolution-score", "batch-ordering", "ret-0x8"},
        "comment_tokens": ("CFastVB__ResolveOppositeAdjacencyRecord", "triangle edges", "ranking candidate"),
        "decompile": "00572500_CFastVB__CountResolvedOppositeEdges.c",
        "decompile_tokens": ("CFastVB__ResolveOppositeAdjacencyRecord", "edge_buckets", "triangle"),
    },
    "0x00572570": {
        "name": "CFastVB__ComputeAverageUnresolvedEdgesPerBatch",
        "signature": "double __stdcall CFastVB__ComputeAverageUnresolvedEdgesPerBatch(void * candidate_bucket)",
        "tags": {"cfastvb", "candidate-bucket", "unresolved-edge-score", "strip-generation", "ret-0x4"},
        "comment_tokens": ("candidate_bucket", "average unresolved-edge score", "primary candidate bucket"),
        "decompile": "00572570_CFastVB__ComputeAverageUnresolvedEdgesPerBatch.c",
        "decompile_tokens": ("candidate_bucket", "return (double)"),
    },
    "0x005725e0": {
        "name": "CFastVB__GenerateStripCandidatesFromAdjacency",
        "signature": "void __thiscall CFastVB__GenerateStripCandidatesFromAdjacency(void * this, void * out_candidate_span, void * triangle_record_span, void * edge_buckets, int seed_bucket_limit, void * edi_context)",
        "tags": {"cfastvb", "candidate-bucket", "strip-generation", "triangle-adjacency", "vertex-cache-scoring"},
        "comment_tokens": ("out_candidate_span", "seed candidate buckets", "CFastVB__ComputeAverageUnresolvedEdgesPerBatch"),
        "decompile": "005725e0_CFastVB__GenerateStripCandidatesFromAdjacency.c",
        "decompile_tokens": ("out_candidate_span", "seed_bucket_limit", "CFastVB__ComputeAverageUnresolvedEdgesPerBatch"),
    },
}

DOC_TOKENS = (
    "Wave653 CFastVB vertex-cache/scoring hardening",
    "3543",
    "2550",
    "765",
    "0x00572e40 CTexture__DestroyNodeTreeAndStorage",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260520-192250_post_wave653_cfastvb_vertex_cache_scoring_verified",
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
        (BASE / "apply-wave653-dry.log", {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 1, "signature_updated": 7, "missing": 0, "bad": 0}),
        (BASE / "apply-wave653-apply.log", {"updated": 7, "skipped": 0, "renamed": 1, "would_rename": 0, "signature_updated": 7, "missing": 0, "bad": 0}),
        (BASE / "apply-wave653-final-dry.log", {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0}),
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
        "post-metadata": 7,
        "post-tags": 7,
        "post-xrefs": 8,
        "post-instructions": 315,
        "post-decompile": 7,
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
        "commentlessFunctionCount": 2550,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 765,
    }
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    first = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if first.get("address") != "0x00572e40" or first.get("name") != "CTexture__DestroyNodeTreeAndStorage":
        failures.append(f"queue head mismatch: {first}")

    backup = read_json(BACKUP_SUMMARY)
    destination = backup.get("BackupPath", backup.get("Destination", ""))
    if "post_wave653_cfastvb_vertex_cache_scoring_verified" not in destination:
        failures.append(f"backup destination mismatch: {destination}")
    if backup.get("DiffCount") != 0:
        failures.append(f"backup DiffCount mismatch: {backup.get('DiffCount')}")
    if int(backup.get("FileCount", 0)) != 19:
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
    if "test:ghidra-cfastvb-vertex-cache-scoring-wave653" not in package.get("scripts", {}):
        failures.append("package.json missing Wave653 probe script")


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
        print("Wave653 CFastVB vertex-cache/scoring probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave653 CFastVB vertex-cache/scoring probe: PASS")
    print("Targets: 7")
    print("Queue: 6093 total, 3543 commented, 2550 commentless, 1217 exact-undefined, 765 param_N")
    print("Next head: 0x00572e40 CTexture__DestroyNodeTreeAndStorage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
