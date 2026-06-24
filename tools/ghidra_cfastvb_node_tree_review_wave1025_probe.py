#!/usr/bin/env python3
"""Validate Wave1025 CFastVB node-tree read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1025-cfastvb-node-tree-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_node_tree_review_wave1025_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1025_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-004522_post_wave1025_cfastvb_node_tree_review_verified"

TARGETS = {
    "0x0056ff40": ("CFastVB__TriangleListContainsVertexTriplet_0056ff40", "uint __stdcall CFastVB__TriangleListContainsVertexTriplet_0056ff40(void * triangle_list_span, void * triangle)", ("Wave651", "triangle-record")),
    "0x00570be0": ("CFastVB__InitializeCandidateParentLinks_00570be0", "void __stdcall CFastVB__InitializeCandidateParentLinks_00570be0(void * out_candidate_span, void * selected_candidate_bucket)", ("Wave651", "parent")),
    "0x00598a81": ("CFastVB__NodeType9__ctor", "int CFastVB__NodeType9__ctor(void)", ("Wave704", "hidden-ECX", "locked storage")),
    "0x00598da4": ("CDXTexture__NodeType13__ctor", "int CDXTexture__NodeType13__ctor(void)", ("Wave704", "hidden-ECX", "locked storage")),
    "0x0059902a": ("CDXTexture__RegisterSerializedChunk", "int CDXTexture__RegisterSerializedChunk(void)", ("Wave705", "serialized-chunk", "locked storage")),
    "0x005997e1": ("CTexture__NodeType12_Ctor_DeleteOnFlag", "int CTexture__NodeType12_Ctor_DeleteOnFlag(void)", ("Wave706", "hidden-ECX", "descriptor")),
    "0x0059996f": ("CTexture__NodeType12_Ctor_ScalarDeletingDtor", "int CTexture__NodeType12_Ctor_ScalarDeletingDtor(void)", ("Wave706", "hidden-ECX", "scalar")),
    "0x00599b69": ("CFastVB__NodeTreeHasBitFlag0x200", "uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void * this, void * node_tree)", ("Wave708", "0x200", "phantom")),
    "0x00599bd7": ("CFastVB__NodeTreeHasOnlyLeafType0to2", "int __thiscall CFastVB__NodeTreeHasOnlyLeafType0to2(void * this, void * node_tree)", ("Wave708", "leaf kind 8", "phantom")),
    "0x00599c49": ("CFastVB__CountNodeTreeExpandedLeafCount", "int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void * this, void * node_tree)", ("Wave708", "expanded", "phantom")),
    "0x00599d80": ("CFastVB__FlattenNodeTreeLeafByLinearIndex", "int __thiscall CFastVB__FlattenNodeTreeLeafByLinearIndex(void * this, void * node_tree, uint linear_leaf_index, void * out_leaf_scratch)", ("Wave709", "RET 0xc", "output leaf scratch")),
    "0x0059a54d": ("CFastVB__ScoreNodeTreeMatch", "int __thiscall CFastVB__ScoreNodeTreeMatch(void * this, void * source_payload, void * candidate_payload, void * candidate_binding_chain, int match_flags)", ("Wave709", "RET 0x10", "match score")),
    "0x0059a71a": ("CFastVB__SelectBestNodeTreeMatch", "int CFastVB__SelectBestNodeTreeMatch(void)", ("Wave895", "hidden ECX/stack ABI", "0x00599349", "0x00599576")),
}

DOC_TOKENS = (
    "Wave1025",
    "cfastvb-node-tree-review-wave1025",
    "0x0056ff40 CFastVB__TriangleListContainsVertexTriplet_0056ff40",
    "0x00570be0 CFastVB__InitializeCandidateParentLinks_00570be0",
    "0x00598a81 CFastVB__NodeType9__ctor",
    "0x0059902a CDXTexture__RegisterSerializedChunk",
    "0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex",
    "0x0059a54d CFastVB__ScoreNodeTreeMatch",
    "0x0059a71a CFastVB__SelectBestNodeTreeMatch",
    "576/1408 = 40.91%",
    "805/1493 = 53.92%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    FASTVB_DOC: ("Wave1025", "cfastvb-node-tree-review-wave1025", "0x0056ff40 CFastVB__TriangleListContainsVertexTriplet_0056ff40", "0x0059a71a CFastVB__SelectBestNodeTreeMatch", BACKUP_PATH),
    DXTEXTURE_DOC: ("Wave1025", "cfastvb-node-tree-review-wave1025", "0x00598da4 CDXTexture__NodeType13__ctor", "0x0059902a CDXTexture__RegisterSerializedChunk", BACKUP_PATH),
    TEXTURE_DOC: ("Wave1025", "cfastvb-node-tree-review-wave1025", "0x005997e1 CTexture__NodeType12_Ctor_DeleteOnFlag", "0x0059996f CTexture__NodeType12_Ctor_ScalarDeletingDtor", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime shader/parser behavior proven",
    "runtime texture behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 13,
        "tags.tsv": 13,
        "xrefs.tsv": 53,
        "instructions.tsv": 1475,
        "decompile/index.tsv": 13,
        "comparison-metadata.tsv": 19,
        "comparison-tags.tsv": 19,
        "comparison-xrefs.tsv": 53,
        "comparison-instructions.tsv": 1928,
        "comparison-decompile/index.tsv": 19,
        "context-metadata.tsv": 9,
        "context-tags.tsv": 9,
        "context-xrefs.tsv": 14,
        "context-instructions.tsv": 2728,
        "context-decompile/index.tsv": 9,
        "instruction-windows.tsv": 159,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "decompile" / "index.tsv"), "address")
    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    evidence = "\n".join(
        read_text(BASE / path)
        for path in (
            "xrefs.tsv",
            "comparison-xrefs.tsv",
            "context-xrefs.tsv",
            "instructions.tsv",
            "instruction-windows.tsv",
            "comparison-metadata.tsv",
            "context-metadata.tsv",
        )
    )
    for token in (
        "0x00599349",
        "0x00599576",
        "CALL\t0x0059a71a",
        "RET\t0x20",
        "CFastVB__ScoreNodeTreePairMismatchBits",
        "CFastVB__AreNodeTreesCompatible",
        "CDXTexture__ProcessTextureChunkAndEmitBindings",
        "CTexture__ValidateConstantRegisterDeclarationType",
        "CFastVB__BuildTriangleStripFromSeedRecord",
        "CFastVB__GenerateStripCandidatesFromAdjacency",
    ):
        require(token in evidence, f"missing evidence token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=13 found=13 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "xrefs.log": "Wrote 53 rows",
        "instructions.log": "targets=13 missing=0",
        "decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "comparison-metadata.log": "targets=19 found=19 missing=0",
        "comparison-tags.log": "ExportFunctionTagsByAddress complete: rows=19 missing=0",
        "comparison-xrefs.log": "Wrote 53 rows",
        "comparison-instructions.log": "targets=19 missing=0",
        "comparison-decompile.log": "targets=19 dumped=19 missing=0 failed=0",
        "context-metadata.log": "targets=9 found=9 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "context-xrefs.log": "Wrote 14 rows",
        "context-instructions.log": "targets=9 missing=0",
        "context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "instruction-windows.log": "targets=3 missing=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cfastvb-node-tree-review-wave1025") == r"py -3 tools\ghidra_cfastvb_node_tree_review_wave1025_probe.py --check", "missing Wave1025 package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1025-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1025 --check", "missing aggregate package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1025 CFastVB node-tree review" for row in ledger_rows), "missing Wave1025 ledger row", failures)
    require(any(row.get("task") == "Wave1025 CFastVB node-tree review" and row.get("attempt_id") == 20607 for row in attempts), "missing Wave1025 attempt row", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)
    check_queue(failures)

    if failures:
        print("Wave1025 CFastVB node-tree review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1025 CFastVB node-tree review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
