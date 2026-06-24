#!/usr/bin/env python3
"""Validate Wave934 BattleLine/Triangulate read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave934-battleline-triangulate-mesh-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleline_triangulate_mesh_review_wave934_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
TRI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "triangulate.cpp" / "_index.md"
DX_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXBattleLine.cpp.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"G:\GhidraBackups\BEA_20260528-005650_post_wave934_battleline_triangulate_mesh_review_verified"
SCRIPT_NAME = "test:ghidra-battleline-triangulate-mesh-review-wave934"
SCRIPT_VALUE = r"py -3 tools\ghidra_battleline_triangulate_mesh_review_wave934_probe.py --check"

TARGETS = {
    "0x004f7170": (
        "Triangulate__CreateQuadMesh",
        "void * __thiscall Triangulate__CreateQuadMesh(void * this, int max_vertices, float min_x, float min_y, float max_x, float max_y, int subdivision_mode)",
        ("RET 0x18", "max_vertices*8", "max_vertices*0x0c", "subdivision mode 1"),
        {"battleline-triangulate-wave521", "quad-mesh", "triangulate"},
    ),
    "0x004f7460": (
        "Triangulate__InsertPointOrAppendVertex",
        "void __thiscall Triangulate__InsertPointOrAppendVertex(void * this, void * point_xy)",
        ("RET 0x4", "Triangulate work object", "appends the XY point"),
        {"battleline-triangulate-wave521", "owner-corrected", "point-insertion", "triangulate"},
    ),
    "0x004f74b0": (
        "Triangulate__SplitTriangleAtPointAndLegalizeEdges",
        "int __thiscall Triangulate__SplitTriangleAtPointAndLegalizeEdges(void * this, void * triangle_indices, void * point_xy)",
        ("RET 0x8", "epsilon 0x005d856c", "tries quality flips"),
        {"battleline-triangulate-wave521", "edge-flip", "triangle-split", "triangulate"},
    ),
    "0x004f7660": (
        "Triangulate__TryFlipSharedEdgeForQuality",
        "void __thiscall Triangulate__TryFlipSharedEdgeForQuality(void * this, int edge_start, int edge_end)",
        ("RET 0x8", "ratio threshold 0x005d85f8", "dirty flag at this+0x14"),
        {"battleline-triangulate-wave521", "edge-flip", "quality-gate", "triangulate"},
    ),
    "0x004f78c0": (
        "Triangulate__FindTriangleByDirectedEdge",
        "short * __thiscall Triangulate__FindTriangleByDirectedEdge(void * this, int edge_start, int edge_end)",
        ("RET 0x8", "rotates a matching triangle", "absent edges return null"),
        {"battleline-triangulate-wave521", "directed-edge", "triangle-lookup", "triangulate"},
    ),
    "0x004f7940": (
        "Triangulate__RelaxMeshByEdgeFlips",
        "void __fastcall Triangulate__RelaxMeshByEdgeFlips(void * this)",
        ("ECX carries the Triangulate work object", "up to ten passes", "three directed edges"),
        {"battleline-triangulate-wave521", "edge-flip", "mesh-relaxation", "triangulate"},
    ),
}

CONTEXT = {
    "0x0053a5e0": (
        "CDXBattleLine__BuildMesh",
        "void __fastcall CDXBattleLine__BuildMesh(void * this)",
        {"battleline-core-wave589", "build-mesh", "triangulate-work-object"},
    ),
    "0x0053b470": (
        "CDXBattleLine__RenderTriOverlayPass",
        "void __fastcall CDXBattleLine__RenderTriOverlayPass(void * this)",
        {"battleline-core-wave589", "overlay-pass"},
    ),
    "0x00487d10": (
        "CHud__RenderBattleline",
        "void __thiscall CHud__RenderBattleline(void * this, void * viewport)",
        {"hud-battleline-tail-wave412", "battleline", "hud"},
    ),
}

EXPECTED_XREFS = {
    ("0x004f7170", "0x0053a712", "CDXBattleLine__BuildMesh", "UNCONDITIONAL_CALL"),
    ("0x004f7460", "0x0053a7a4", "CDXBattleLine__BuildMesh", "UNCONDITIONAL_CALL"),
    ("0x004f74b0", "0x004f7478", "Triangulate__InsertPointOrAppendVertex", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f7622", "Triangulate__SplitTriangleAtPointAndLegalizeEdges", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f762b", "Triangulate__SplitTriangleAtPointAndLegalizeEdges", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f7634", "Triangulate__SplitTriangleAtPointAndLegalizeEdges", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f798d", "Triangulate__RelaxMeshByEdgeFlips", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f799a", "Triangulate__RelaxMeshByEdgeFlips", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f79a7", "Triangulate__RelaxMeshByEdgeFlips", "UNCONDITIONAL_CALL"),
    ("0x004f78c0", "0x004f7673", "Triangulate__TryFlipSharedEdgeForQuality", "UNCONDITIONAL_CALL"),
    ("0x004f78c0", "0x004f767e", "Triangulate__TryFlipSharedEdgeForQuality", "UNCONDITIONAL_CALL"),
    ("0x004f7940", "0x0053a7c0", "CDXBattleLine__BuildMesh", "UNCONDITIONAL_CALL"),
}

EXPECTED_CONTEXT_XREFS = {
    ("0x0053a5e0", "0x0053a295", "CDXBattleLine__Setup", "UNCONDITIONAL_CALL"),
    ("0x0053b470", "0x0053b276", "CDXBattleLine__Render", "UNCONDITIONAL_CALL"),
    ("0x00487d10", "0x0053ed79", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("0x004f73aa", "RET", "0x18", "Triangulate__CreateQuadMesh"),
    ("0x004f7431", "RET", "0x18", "Triangulate__CreateQuadMesh"),
    ("0x004f74aa", "RET", "0x4", "Triangulate__InsertPointOrAppendVertex"),
    ("0x004f7645", "RET", "0x8", "Triangulate__SplitTriangleAtPointAndLegalizeEdges"),
    ("0x004f78bc", "RET", "0x8", "Triangulate__TryFlipSharedEdgeForQuality"),
    ("0x004f7905", "RET", "0x8", "Triangulate__FindTriangleByDirectedEdge"),
    ("0x004f79cc", "RET", "", "Triangulate__RelaxMeshByEdgeFlips"),
}

DECOMPILE_TOKENS = {
    "decompile/004f7170_Triangulate__CreateQuadMesh.c": ("max_vertices * 8", "max_vertices * 0xc", "subdivision_mode == 1"),
    "decompile/004f7460_Triangulate__InsertPointOrAppendVertex.c": ("point_xy", "Triangulate__SplitTriangleAtPointAndLegalizeEdges", "triangle_indices"),
    "decompile/004f74b0_Triangulate__SplitTriangleAtPointAndLegalizeEdges.c": ("triangle_indices", "point_xy", "Triangulate__TryFlipSharedEdgeForQuality"),
    "decompile/004f7660_Triangulate__TryFlipSharedEdgeForQuality.c": ("edge_start", "edge_end", "this + 0x14"),
    "decompile/004f78c0_Triangulate__FindTriangleByDirectedEdge.c": ("edge_start", "edge_end", "return psVar2"),
    "decompile/004f7940_Triangulate__RelaxMeshByEdgeFlips.c": ("local_c = 10", "Triangulate__TryFlipSharedEdgeForQuality", "this + 0x14"),
    "context-decompile/0053a5e0_CDXBattleLine__BuildMesh.c": ("Triangulate__CreateQuadMesh", "Triangulate__InsertPointOrAppendVertex", "Triangulate__RelaxMeshByEdgeFlips"),
    "context-decompile/0053b470_CDXBattleLine__RenderTriOverlayPass.c": ("CDXBattleLine__RenderTriOverlayPass", "this + 0x60", "this + 0x78"),
    "context-decompile/00487d10_CHud__RenderBattleline.c": ("CDXEngine__RenderBattleLinePulseSprites", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices", "CDXBattleLine__Render"),
}

CORE_TOKENS = (
    "Wave934",
    "battleline-triangulate-mesh-review-wave934",
    "146/1408 = 10.37%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x004f7170 Triangulate__CreateQuadMesh",
    "0x004f7460 Triangulate__InsertPointOrAppendVertex",
    "0x004f74b0 Triangulate__SplitTriangleAtPointAndLegalizeEdges",
    "0x004f7660 Triangulate__TryFlipSharedEdgeForQuality",
    "0x004f78c0 Triangulate__FindTriangleByDirectedEdge",
    "0x004f7940 Triangulate__RelaxMeshByEdgeFlips",
    "0x0053a5e0 CDXBattleLine__BuildMesh",
    "0x0053b470 CDXBattleLine__RenderTriOverlayPass",
    "0x00487d10 CHud__RenderBattleline",
    "no mutation",
)

OVERCLAIMS = (
    "runtime influence-map mesh behavior proven",
    "runtime overlay visual behavior proven",
    "complete triangulate structure layout",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 12,
        "instructions.tsv": 685,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 3,
        "context-tags.tsv": 3,
        "context-xrefs.tsv": 3,
        "context-instructions.tsv": 605,
        "context-decompile/index.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "rows=6 missing=0",
        "xrefs.log": "Wrote 12 rows",
        "instructions.log": "Wrote 685 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=3 found=3 missing=0",
        "context-tags.log": "rows=3 missing=0",
        "context-xrefs.log": "Wrote 3 rows",
        "context-instructions.log": "Wrote 605 function-body instruction rows",
        "context-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata_and_tags(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            missing = {"static-reaudit", "retail-binary-evidence", *expected_tags} - actual_tags
            require(not missing, f"missing tags {address}: {sorted(missing)}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

    context_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    context_tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-tags.tsv")}
    for address, (name, signature, expected_tags) in CONTEXT.items():
        row = context_metadata.get(address)
        require(row is not None, f"missing context metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"context metadata status mismatch {address}", failures)
            require(row.get("comment", "").strip(), f"missing context comment {address}", failures)
        tag_row = context_tags.get(address)
        require(tag_row is not None, f"missing context tags {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            missing = {"static-reaudit", "retail-binary-evidence", *expected_tags} - actual_tags
            require(not missing, f"missing context tags {address}: {sorted(missing)}", failures)
            require(tag_row.get("status") == "OK", f"context tag status mismatch {address}", failures)


def check_xrefs_and_instructions(failures: list[str]) -> None:
    actual = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["from_function"], row["ref_type"])
        for row in read_tsv(BASE / "xrefs.tsv")
    }
    missing = EXPECTED_XREFS - actual
    require(not missing, f"missing expected xrefs: {sorted(missing)}", failures)

    context_actual = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["from_function"], row["ref_type"])
        for row in read_tsv(BASE / "context-xrefs.tsv")
    }
    missing_context = EXPECTED_CONTEXT_XREFS - context_actual
    require(not missing_context, f"missing expected context xrefs: {sorted(missing_context)}", failures)

    instructions = {normalize_address(row["instruction_addr"]): row for row in read_tsv(BASE / "instructions.tsv")}
    for address, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        row = instructions.get(address)
        require(row is not None, f"missing instruction {address}", failures)
        if row is not None:
            require(row.get("mnemonic") == mnemonic, f"instruction mnemonic mismatch {address}", failures)
            require(row.get("function_name") == function_name, f"instruction function mismatch {address}", failures)
            if operand_token:
                require(operand_token in row.get("operands", ""), f"instruction operand mismatch {address}", failures)


def check_decompile_tokens(failures: list[str]) -> None:
    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        require(text, f"missing decompile file {relative}", failures)
        for token in tokens:
            require(token in text, f"missing decompile token {relative}: {token}", failures)


def check_docs_state_backup(failures: list[str]) -> None:
    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)
    for path in [NOTE, CAMPAIGN, TRI_DOC, DX_DOC, *STATE_FILES]:
        text = read_text(path)
        require(text, f"missing doc/state {path.relative_to(ROOT)}", failures)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata_and_tags(failures)
    check_xrefs_and_instructions(failures)
    check_decompile_tokens(failures)
    check_docs_state_backup(failures)

    if failures:
        print("Wave934 BattleLine/Triangulate mesh review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave934 BattleLine/Triangulate mesh review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
