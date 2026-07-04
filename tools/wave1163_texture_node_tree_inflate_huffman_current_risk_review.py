#!/usr/bin/env python3
"""Validate Wave1163 texture node-tree / inflate-Huffman current-risk evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1163-texture-node-tree-inflate-huffman-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1163-texture-node-tree-inflate-huffman-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1163-texture-node-tree-inflate-huffman-current-risk-review.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "wave1163_texture_node_tree_inflate_huffman_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x005987f4": ("CTexture__NodePayloadRecordCtor", "int CTexture__NodePayloadRecordCtor(void)", ("hidden-ECX constructor", "node-payload vtable")),
    "0x00598a81": ("CFastVB__NodeType9__ctor", "int CFastVB__NodeType9__ctor(void)", ("node-type 9", "vtable 0x005ef250")),
    "0x00598da4": ("CDXTexture__NodeType13__ctor", "int CDXTexture__NodeType13__ctor(void)", ("node-type 13", "vtable 0x005ef270")),
    "0x0059902a": ("CDXTexture__RegisterSerializedChunk", "int CDXTexture__RegisterSerializedChunk(void)", ("serialized-chunk registry helper", "0xffffffff string-length sentinel")),
    "0x00599b69": ("CFastVB__NodeTreeHasBitFlag0x200", "uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void * this, void * node_tree)", ("payload flag mask", "0x200")),
    "0x00599bd7": ("CFastVB__NodeTreeHasOnlyLeafType0to2", "int __thiscall CFastVB__NodeTreeHasOnlyLeafType0to2(void * this, void * node_tree)", ("leaf kind 8", "range 0..2")),
    "0x00599c49": ("CFastVB__CountNodeTreeExpandedLeafCount", "int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void * this, void * node_tree)", ("expanded CFastVB node-tree leaves", "phantom decompiler artifact")),
    "0x00599cd2": ("CFastVB__AreNodeTreesStructurallyEqual", "bool __stdcall CFastVB__AreNodeTreesStructurallyEqual(void * left_node_tree, void * right_node_tree)", ("structural equality", "leaf kind 8")),
    "0x0059a21f": ("CFastVB__AreNodeTreesCompatible", "int __thiscall CFastVB__AreNodeTreesCompatible(void * this, void * left_node_tree, void * right_node_tree, int relaxed_match)", ("RET 0xc", "relaxed leaf-type path")),
    "0x0059a54d": ("CFastVB__ScoreNodeTreeMatch", "int __thiscall CFastVB__ScoreNodeTreeMatch(void * this, void * source_payload, void * candidate_payload, void * candidate_binding_chain, int match_flags)", ("payload descriptor/name context", "accumulated match score")),
    "0x0059a71a": ("CFastVB__SelectBestNodeTreeMatch", "int CFastVB__SelectBestNodeTreeMatch(void)", ("CTexture__ValidateConstantRegisterDeclarationType", "CDXTexture__ProcessTextureChunkAndEmitBindings")),
    "0x005958e0": ("CTexture__LoadDefaultHuffmanTables", "void CTexture__LoadDefaultHuffmanTables(void)", ("built-in JPEG Huffman table definitions", "hidden ESI")),
    "0x0059c8c1": ("CDXTexture__InflateStream_ProcessZlibState", "int __stdcall CDXTexture__InflateStream_ProcessZlibState(void * inflate_stream, int flush_mode)", ("extraout_", "zlib CMF/FLG")),
    "0x005bcfd3": ("CDXTexture__InflateCodesState_Process", "int __stdcall CDXTexture__InflateCodesState_Process(void * inflate_state, void * inflate_stream, int status_code)", ("literal/length and distance code states", "invalid literal/length")),
    "0x005bd53b": ("CDXTexture__BuildInflateHuffmanTable", "int CDXTexture__BuildInflateHuffmanTable(void)", ("inflate Huffman table builder", "hidden EAX/stack-ABI")),
    "0x005bd933": ("CDXTexture__InflateDynamicTree_BuildLitDistTrees", "int __stdcall CDXTexture__InflateDynamicTree_BuildLitDistTrees(int literal_length_count, int distance_count, void * code_lengths, void * literal_bits_out, void * distance_bits_out, void * literal_table_out, void * distance_table_out, void * tree_workspace, void * inflate_stream)", ("dynamic inflate literal/length", "RET 0x24")),
    "0x005b3fd0": ("CDXTexture__FlushEntropyBitWriter", "void CDXTexture__FlushEntropyBitWriter(void)", ("entropy bits", "hidden EAX")),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "comment-hardened"}

DOCS = [
    NOTE,
    NOTE_MIRROR,
    CONTRACT,
    CONTRACT_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "AGENTS.md",
    ROOT / "README.MD",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

DOC_TOKENS = (
    "Wave1163",
    "wave1163-texture-node-tree-inflate-huffman-current-risk-review",
    "564/1179 = 47.84%",
    "17 CFastVB/CTexture/CDXTexture current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 615",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "68 xref rows",
    "2779 instruction rows",
    "CTexture__NodePayloadRecordCtor",
    "CFastVB__NodeType9__ctor",
    "CDXTexture__NodeType13__ctor",
    "CDXTexture__RegisterSerializedChunk",
    "CFastVB__AreNodeTreesCompatible",
    "CFastVB__SelectBestNodeTreeMatch",
    "CTexture__LoadDefaultHuffmanTables",
    "CDXTexture__InflateStream_ProcessZlibState",
    "CDXTexture__BuildInflateHuffmanTable",
    "CDXTexture__FlushEntropyBitWriter",
    "JPEG Huffman separate from inflate Huffman",
    BACKUP,
    "texture-resource-decode-static-contract.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime texture decode behavior proven",
    "runtime jpeg behavior proven",
    "runtime inflate behavior proven",
    "exact layout proven",
    "source identity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 17,
        "pre-tags.tsv": 17,
        "pre-xrefs.tsv": 68,
        "pre-instructions.tsv": 2779,
        "pre-decompile/index.tsv": 17,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    ref_types = [row.get("ref_type") for row in xrefs]
    require(ref_types.count("UNCONDITIONAL_CALL") == 68, "UNCONDITIONAL_CALL xref count mismatch", failures)
    require(set(ref_types) == {"UNCONDITIONAL_CALL"}, f"unexpected xref types: {set(ref_types)}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=17 found=17 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "pre-xrefs.log": "Wrote 68 rows",
        "pre-instructions.log": "Wrote 2779 function-body instruction rows",
        "pre-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("sourceRoot") == EXPECTED_SOURCE_ROOT, "backup source root mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175999879, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1163 texture node-tree / inflate-Huffman current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1163-texture-node-tree-inflate-huffman-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 564, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "47.84%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 615, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1163 texture node-tree / inflate-Huffman current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1163 note mirror mismatch", failures)
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "texture contract mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1163-texture-node-tree-inflate-huffman-current-risk-review")
        == r"py -3 tools\wave1163_texture_node_tree_inflate_huffman_current_risk_review.py --check",
        "missing Wave1163 package script",
        failures,
    )
    require(
        scripts.get("test:texture-resource-decode-static-contract")
        == r"py -3 tools\texture_resource_decode_static_contract_probe.py --check",
        "missing texture contract package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs_progress(failures)
    if failures:
        print("Wave1163 texture node-tree / inflate-Huffman current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1163 texture node-tree / inflate-Huffman current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
