#!/usr/bin/env python3
"""Validate Wave521 BattleLine/Triangulate static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave521-battleline-triangulate-004f7170"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_battleline_triangulate_wave521_2026-05-18.md"

COMMON_TAGS = {
    "battleline-triangulate-wave521",
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

OVERCLAIM_TOKENS = (
    "runtime overlay mesh behavior proven",
    "runtime influence-map mesh behavior proven",
    "runtime triangulation result proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004f7170": target(
        "Triangulate__CreateQuadMesh",
        "void * __thiscall Triangulate__CreateQuadMesh(void * this, int max_vertices, float min_x, float min_y, float max_x, float max_y, int subdivision_mode)",
        ("RET 0x18", "max_vertices*8", "max_vertices*0x0c", "4 vertices/2 triangles", "remain unproven"),
        {"allocator", "battleline-mesh", "quad-mesh", "triangulate"},
        ("Triangulate__CreateQuadMesh", "max_vertices * 8", "max_vertices * 0xc", "subdivision_mode == 1"),
    ),
    "0x004f7460": target(
        "Triangulate__InsertPointOrAppendVertex",
        "void __thiscall Triangulate__InsertPointOrAppendVertex(void * this, void * point_xy)",
        ("RET 0x4", "Triangulate work object", "Triangulate__SplitTriangleAtPointAndLegalizeEdges", "appends the XY point", "remain unproven"),
        {"battleline-mesh", "owner-corrected", "point-insertion", "topology", "triangulate"},
        ("Triangulate__InsertPointOrAppendVertex", "point_xy", "Triangulate__SplitTriangleAtPointAndLegalizeEdges", "triangle_indices"),
    ),
    "0x004f74b0": target(
        "Triangulate__SplitTriangleAtPointAndLegalizeEdges",
        "int __thiscall Triangulate__SplitTriangleAtPointAndLegalizeEdges(void * this, void * triangle_indices, void * point_xy)",
        ("RET 0x8", "Triangulate work object", "epsilon 0x005d856c", "tries quality flips", "remain unproven"),
        {"battleline-mesh", "edge-flip", "owner-corrected", "triangle-split", "triangulate"},
        ("Triangulate__SplitTriangleAtPointAndLegalizeEdges", "triangle_indices", "point_xy", "Triangulate__TryFlipSharedEdgeForQuality"),
    ),
    "0x004f7660": target(
        "Triangulate__TryFlipSharedEdgeForQuality",
        "void __thiscall Triangulate__TryFlipSharedEdgeForQuality(void * this, int edge_start, int edge_end)",
        ("RET 0x8", "Triangulate work object", "ratio threshold 0x005d85f8", "dirty flag at this+0x14", "remain unproven"),
        {"battleline-mesh", "edge-flip", "owner-corrected", "quality-gate", "triangulate"},
        ("Triangulate__TryFlipSharedEdgeForQuality", "edge_start", "edge_end", "this + 0x14"),
    ),
    "0x004f78c0": target(
        "Triangulate__FindTriangleByDirectedEdge",
        "short * __thiscall Triangulate__FindTriangleByDirectedEdge(void * this, int edge_start, int edge_end)",
        ("RET 0x8", "Triangulate work object", "rotates a matching triangle", "absent edges return null", "remain unproven"),
        {"battleline-mesh", "directed-edge", "owner-corrected", "triangle-lookup", "triangulate"},
        ("Triangulate__FindTriangleByDirectedEdge", "edge_start", "edge_end", "return psVar2"),
    ),
    "0x004f7940": target(
        "Triangulate__RelaxMeshByEdgeFlips",
        "void __fastcall Triangulate__RelaxMeshByEdgeFlips(void * this)",
        ("ECX carries the Triangulate work object", "up to ten passes", "three directed edges", "remain unproven"),
        {"battleline-mesh", "edge-flip", "mesh-relaxation", "owner-corrected", "triangulate"},
        ("Triangulate__RelaxMeshByEdgeFlips", "local_c = 10", "Triangulate__TryFlipSharedEdgeForQuality", "this + 0x14"),
    ),
}

EXPECTED_XREFS = {
    ("0x004f7170", "0x0053a712", "CDXBattleLine__BuildMesh", "UNCONDITIONAL_CALL"),
    ("0x004f7460", "0x0053a7a4", "CDXBattleLine__BuildMesh", "UNCONDITIONAL_CALL"),
    ("0x004f74b0", "0x004f7478", "Triangulate__InsertPointOrAppendVertex", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f7622", "Triangulate__SplitTriangleAtPointAndLegalizeEdges", "UNCONDITIONAL_CALL"),
    ("0x004f7660", "0x004f798d", "Triangulate__RelaxMeshByEdgeFlips", "UNCONDITIONAL_CALL"),
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

PUBLIC_NOTE_TOKENS = (
    "Wave521",
    "Triangulate__CreateQuadMesh",
    "Triangulate__RelaxMeshByEdgeFlips",
    "12 target xref rows",
    "runtime overlay mesh behavior",
    "rebuild parity",
)


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    body = address[2:] if address.startswith("0x") else address
    return f"0x{int(body, 16):08x}"


def compact_text(value: str) -> str:
    return " ".join((value or "").replace("\t", " ").replace("\r", " ").replace("\n", " ").split())


def compact_token(value: str) -> str:
    return "".join(compact_text(value).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact_token(token) in compact_token(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "instruction_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


def find_decomp_file(decomp_dir: Path, address: str, expected_name: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    named = [path for path in candidates if expected_name in path.name]
    if named:
        return named[0]
    return candidates[0]


def validate_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        require(row["status"] == "OK", f"{address} status mismatch: {row['status']}")
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = compact_text(row["comment"])
        for token in expected["comment_tokens"]:
            require(token_present(comment, str(token)), f"{address} comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            require(not token_present(comment, token), f"{address} comment contains overclaim token {token!r}")


def validate_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        tags = {tag.strip() for tag in row["tags"].replace(",", ";").split(";") if tag.strip()}
        missing = expected["tags"] - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def validate_decompile(base: Path) -> None:
    decomp_dir = base / "post_decomp"
    require(decomp_dir.exists(), f"missing decompile dir: {decomp_dir}")
    for address, expected in TARGETS.items():
        text = find_decomp_file(decomp_dir, address, str(expected["name"])).read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, str(token)), f"{address} decompile missing token {token!r}")


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    got = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in rows
    }
    missing = EXPECTED_XREFS - got
    require(not missing, f"missing expected xrefs: {sorted(missing)}")

    context_rows = read_tsv(base / "post_context_xrefs.tsv")
    context_got = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in context_rows
    }
    context_missing = EXPECTED_CONTEXT_XREFS - context_got
    require(not context_missing, f"missing expected context xrefs: {sorted(context_missing)}")


def validate_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    for address, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        matches = [row for row in rows if row.get("instruction_addr") == normalize_addr(address)]
        require(matches, f"missing instruction row post_instructions.tsv:{address}")
        row = matches[0]
        require(row["mnemonic"] == mnemonic, f"{address} mnemonic mismatch: {row['mnemonic']}")
        require(function_name == row["function_name"], f"{address} function mismatch: {row['function_name']}")
        if operand_token:
            require(token_present(row["operands"], operand_token), f"{address} operands missing {operand_token!r}")


def validate_counts(base: Path) -> None:
    require(len(read_tsv(base / "post_metadata.tsv")) == 6, "post metadata row count mismatch")
    require(len(read_tsv(base / "post_tags.tsv")) == 6, "post tags row count mismatch")
    require(len(read_tsv(base / "post_xrefs.tsv")) == 12, "post xref row count mismatch")
    require(len(read_tsv(base / "post_context_metadata.tsv")) == 9, "post context metadata row count mismatch")
    require(len(read_tsv(base / "post_context_xrefs.tsv")) == 15, "post context xref row count mismatch")
    require(len(read_tsv(base / "post_instructions.tsv")) == 1398, "post instruction export row count mismatch")
    decomp_index = read_tsv(base / "post_decomp" / "index.tsv")
    require(len(decomp_index) == 6, "post decompile index row count mismatch")
    for row in decomp_index:
        require(row["status"] == "OK", f"decompile failed for {row.get('address')}")
    context_index = read_tsv(base / "post_context_decomp" / "index.tsv")
    require(len(context_index) == 9, "post context decompile index row count mismatch")
    for row in context_index:
        require(row["status"] == "OK", f"context decompile failed for {row.get('address')}")


def validate_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token in text, f"public note missing token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = args.base
    validate_metadata(base)
    validate_tags(base)
    validate_decompile(base)
    validate_xrefs(base)
    validate_instructions(base)
    validate_counts(base)
    if args.check:
        validate_public_note()
    print(f"PASS wave521 BattleLine/Triangulate evidence: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
