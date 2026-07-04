#!/usr/bin/env python3
"""Validate Wave651 CFastVB strip-selection read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave651-cfastvb-strip-selection"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_strip_selection_wave651_2026-05-20.md"
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
    "cfastvb-strip-selection-wave651",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x0056fce0": {
        "name": "CFastVB__SelectTriangleWithMaxOpenEdges",
        "signature": "uint __stdcall CFastVB__SelectTriangleWithMaxOpenEdges(void * triangle_record_span, void * edge_buckets)",
        "tags": {"cfastvb", "strip-selection", "open-edge-count", "returns-index", "ret-0x8"},
        "comment_tokens": ("open-edge", "0xffffffff", "Static retail decompile/xref evidence only"),
        "decompile": "0056fce0_CFastVB__SelectTriangleWithMaxOpenEdges.c",
        "decompile_tokens": ("CFastVB__ResolveOppositeAdjacencyRecord", "return 0xffffffff", "triangle_record_span"),
    },
    "0x0056fdc0": {
        "name": "CFastVB__SelectNextStripTriangle",
        "signature": "void * __thiscall CFastVB__SelectNextStripTriangle(void * this, void * triangle_record_span, void * edge_buckets, void * edi_context)",
        "tags": {"cfastvb", "strip-selection", "next-triangle", "open-edge-seed", "returns-pointer"},
        "comment_tokens": ("this+0x1c", "this+0x18", "selected triangle pointer"),
        "decompile": "0056fdc0_CFastVB__SelectNextStripTriangle.c",
        "decompile_tokens": ("CFastVB__SelectTriangleWithMaxOpenEdges", "triangle_record_span", "pvVar5"),
    },
    "0x0056fe70": {
        "name": "CFastVB__AreTriangleVertexSetsEquivalent",
        "signature": "int __cdecl CFastVB__AreTriangleVertexSetsEquivalent(void * triangle_a, void * triangle_b)",
        "tags": {"cfastvb", "triangle-compare", "vertex-set-equivalence", "strip-emission-helper"},
        "comment_tokens": ("boolean exactness is not overclaimed", "match/rotation cue", "Static retail decompile/xref evidence only"),
        "decompile": "0056fe70_CFastVB__AreTriangleVertexSetsEquivalent.c",
        "decompile_tokens": ("triangle_a", "triangle_b", "regardless of order"),
    },
    "0x0056fec0": {
        "name": "CFastVB__GetSharedVerticesBetweenTriangles",
        "signature": "void __cdecl CFastVB__GetSharedVerticesBetweenTriangles(void * triangle_a, void * triangle_b, void * out_shared_a, void * out_shared_b)",
        "tags": {"cfastvb", "triangle-compare", "shared-vertices", "out-parameters"},
        "comment_tokens": ("out_shared_a", "out_shared_b", "0xffffffff"),
        "decompile": "0056fec0_CFastVB__GetSharedVerticesBetweenTriangles.c",
        "decompile_tokens": ("out_shared_a", "out_shared_b", "0xffffffff"),
    },
    "0x0056ff40": {
        "name": "CFastVB__TriangleListContainsVertexTriplet_0056ff40",
        "signature": "uint __stdcall CFastVB__TriangleListContainsVertexTriplet_0056ff40(void * triangle_list_span, void * triangle)",
        "tags": {"cfastvb", "triangle-compare", "triangle-list-membership", "ret-0x8", "address-suffixed-helper"},
        "comment_tokens": ("low-byte", "address-suffixed", "Static retail decompile/xref evidence only"),
        "decompile": "0056ff40_CFastVB__TriangleListContainsVertexTriplet_0056ff40.c",
        "decompile_tokens": ("triangle_list_span", "triangle", "CONCAT31"),
    },
    "0x00570000": {
        "name": "CFastVB__BuildTriangleStripFromSeedRecord",
        "signature": "void __thiscall CFastVB__BuildTriangleStripFromSeedRecord(void * this, void * edge_buckets, int generation_context)",
        "tags": {"cfastvb", "strip-builder", "seed-triangle", "adjacency-walk", "candidate-batches"},
        "comment_tokens": ("seed triangle/candidate", "CFastVB__InsertStripCandidatesIntoBuffer_005708a0", "generation_context"),
        "decompile": "00570000_CFastVB__BuildTriangleStripFromSeedRecord.c",
        "decompile_tokens": ("CFastVB__ResolveOppositeAdjacencyRecord", "CFastVB__InsertStripCandidatesIntoBuffer_005708a0", "generation_context"),
    },
    "0x00570870": {
        "name": "CFastVB__StampRecordOwnerFields",
        "signature": "void __thiscall CFastVB__StampRecordOwnerFields(void * this, void * triangle_record, void * edi_context)",
        "tags": {"cfastvb", "triangle-record", "owner-field-stamp", "candidate-batches"},
        "comment_tokens": ("this+0x1c", "this+0x20", "negative-owner"),
        "decompile": "00570870_CFastVB__StampRecordOwnerFields.c",
        "decompile_tokens": ("triangle_record", "edi_context", "0xffffffff"),
    },
    "0x005708a0": {
        "name": "CFastVB__InsertStripCandidatesIntoBuffer_005708a0",
        "signature": "void __thiscall CFastVB__InsertStripCandidatesIntoBuffer_005708a0(void * this, void * primary_candidate_span, void * secondary_candidate_span, void * edi_context)",
        "tags": {"cfastvb", "strip-candidate-buffer", "pointer-span-grow", "address-suffixed-helper"},
        "comment_tokens": ("secondary strip candidates", "primary candidates", "address-suffixed"),
        "decompile": "005708a0_CFastVB__InsertStripCandidatesIntoBuffer_005708a0.c",
        "decompile_tokens": ("primary_candidate_span", "secondary_candidate_span", "OID__AllocObject_DefaultTag_00662b2c"),
    },
    "0x00570a90": {
        "name": "CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90",
        "signature": "int __thiscall CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90(void * this, void * triangle_record, void * edge_buckets, void * edi_context)",
        "tags": {"cfastvb", "strip-candidate-selection", "adjacent-face-owner-check", "address-suffixed-helper"},
        "comment_tokens": ("all three edges", "current owner/group id", "low-byte true"),
        "decompile": "00570a90_CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90.c",
        "decompile_tokens": ("CFastVB__FindEdgeRecord", "edge_buckets", "triangle_record"),
    },
    "0x00570be0": {
        "name": "CFastVB__InitializeCandidateParentLinks_00570be0",
        "signature": "void __stdcall CFastVB__InitializeCandidateParentLinks_00570be0(void * out_candidate_span, void * selected_candidate_bucket)",
        "tags": {"cfastvb", "strip-candidate-links", "parent-link-initializer", "ret-0x8", "address-suffixed-helper"},
        "comment_tokens": ("out_candidate_span", "selected_candidate_bucket", "parent field"),
        "decompile": "00570be0_CFastVB__InitializeCandidateParentLinks_00570be0.c",
        "decompile_tokens": ("out_candidate_span", "selected_candidate_bucket", "0xffffffff"),
    },
}

DOC_TOKENS = (
    "Wave651 CFastVB strip-selection hardening",
    "3528",
    "2565",
    "780",
    "0x00570cb0 CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0",
    "[maintainer-local-ghidra-backup-root]\\BEA_20260520-182101_post_wave651_cfastvb_strip_selection_verified",
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
        (BASE / "apply-dry.log", {"updated": 0, "skipped": 10, "renamed": 0, "would_rename": 0, "signature_updated": 10, "missing": 0, "bad": 0}),
        (BASE / "apply.log", {"updated": 10, "skipped": 0, "renamed": 0, "would_rename": 0, "signature_updated": 10, "missing": 0, "bad": 0}),
        (BASE / "apply-final-dry.log", {"updated": 0, "skipped": 10, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0}),
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
        "post-metadata": 10,
        "post-tags": 10,
        "post-xrefs": 15,
        "post-instructions": 250,
        "post-decompile": 10,
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
        "commentlessFunctionCount": 2565,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 780,
    }
    for key, value in expected_signals.items():
        if signals.get(key) != value:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {value}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00570cb0" or head.get("name") != "CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("Destination") != r"[maintainer-local-ghidra-backup-root]\BEA_20260520-182101_post_wave651_cfastvb_strip_selection_verified":
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
            require_tokens(label, text, ("test:ghidra-cfastvb-strip-selection-wave651",), failures)
        else:
            require_tokens(label, text, DOC_TOKENS, failures)
        for bad in OVERCLAIM_TOKENS:
            if bad in text:
                failures.append(f"{label} contains overclaim token: {bad}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate artifacts and docs")
    parser.parse_args()

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
        print("Wave651 CFastVB strip-selection probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave651 CFastVB strip-selection probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
