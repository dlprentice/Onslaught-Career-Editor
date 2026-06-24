#!/usr/bin/env python3
"""Validate Wave511 static-shadows static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave511-static-shadows-004eba30"
)
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_static_shadows_wave511_2026-05-17.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "static-shadows-wave511",
}


def target(
    name: str,
    signature: str,
    comment_tokens: tuple[str, ...],
    tags: set[str],
    decompile_tokens: tuple[str, ...],
    instruction_tokens: tuple[tuple[str, str], ...],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "comment_tokens": comment_tokens,
        "tags": COMMON_TAGS | tags,
        "decompile_tokens": decompile_tokens,
        "instruction_tokens": instruction_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004eba30": target(
        "CEngine__SetVertexShaderPathEnabled",
        "void __stdcall CEngine__SetVertexShaderPathEnabled(int enable_vertex_shader_path)",
        ("render-state helper", "RET 0x4", "global shader support", "render-state dword 0x98"),
        {"engine", "render-state", "vertex-shader"},
        ("void __stdcall CEngine__SetVertexShaderPathEnabled", "enable_vertex_shader_path", "RenderState_Set"),
        (("RET", "0x4"), ("CALL", "0x00513bc0"), ("CALL", "0x00513c20")),
    ),
    "0x004ebbc0": target(
        "CStaticShadows__Initialise",
        "void __fastcall CStaticShadows__Initialise(void * this)",
        ("CStaticShadows initialise body", "ECX=0x009c8010", "BuildStaticShadows", "64x64"),
        {"build-command", "initialise", "stale-owner-corrected", "static-shadows"},
        ("void __fastcall CStaticShadows__Initialise", "CConsole__RegisterCommand", "BuildStaticShadows"),
        (("PUSH", "0x4ebbb0"), ("MOV", "[ESI + 0x4018]"), ("RET", "")),
    ),
    "0x004ebd10": target(
        "CStaticShadows__ClearAllShadowEntries",
        "void __fastcall CStaticShadows__ClearAllShadowEntries(void * this)",
        ("list/grid cleanup body", "linked shadow-entry list", "visibility removal", "64x64"),
        {"cleanup", "linked-list", "shadow-grid", "static-shadows"},
        ("void __fastcall CStaticShadows__ClearAllShadowEntries", "CStaticShadows__UpdateVisibility", "CStaticShadows__ShadowMapEntryDeletingDestructor"),
        (("CALL", "0x004ebfb0"), ("CALL", "0x004ec250"), ("RET", "")),
    ),
    "0x004ebdf0": target(
        "CStaticShadows__ShadowMapEntryDestructor",
        "void __fastcall CStaticShadows__ShadowMapEntryDestructor(void * this)",
        ("per-shadow-map-entry destructor callback", "0x200-byte bitmap", "0x1c-byte entries"),
        {"destructor", "shadow-map-entry", "stale-purpose-corrected", "static-shadows"},
        ("void __fastcall CStaticShadows__ShadowMapEntryDestructor", "CDXMemoryManager__Free"),
        (("CALL", "0x00549220"), ("RET", "")),
    ),
    "0x004ebe40": target(
        "CStaticShadows__UpdateLightVectorAndRebuild",
        "void __fastcall CStaticShadows__UpdateLightVectorAndRebuild(void * this)",
        ("BuildStaticShadows command target", "normalizes light-vector", "0x24-byte linked shadow entries"),
        {"build-command", "light-vector", "rebuild", "static-shadows"},
        ("void __fastcall CStaticShadows__UpdateLightVectorAndRebuild", "CStaticShadows__BuildShadowMaps", "OID__AllocObject"),
        (("CALL", "0x004ec2f0"), ("CALL", "0x005490e0"), ("RET", "")),
    ),
    "0x004ebfb0": target(
        "CStaticShadows__UpdateVisibility",
        "void __stdcall CStaticShadows__UpdateVisibility(void * thing, int force_update)",
        ("RET 0x8", "thing static-shadow payload", "clears overlapped grid cells", "landscape tiles"),
        {"shadow-grid", "static-shadows", "thing", "visibility"},
        ("void __stdcall CStaticShadows__UpdateVisibility", "force_update", "CStaticShadows__ApplyShadowsToGrid", "CDXEngine__InvalidateLandscapeTilesAndPatchSlots"),
        (("CALL", "dword ptr [EAX + 0x2c]"), ("CALL", "dword ptr [EDX + 0x70]"), ("RET", "0x8")),
    ),
    "0x004ec250": target(
        "CStaticShadows__ShadowMapEntryDeletingDestructor",
        "void * __thiscall CStaticShadows__ShadowMapEntryDeletingDestructor(void * this, byte flags)",
        ("scalar/vector deleting destructor", "RET 0x4", "flags&2", "0x1c-byte entries"),
        {"deleting-destructor", "shadow-map-entry", "stale-purpose-corrected", "static-shadows"},
        ("void * __thiscall CStaticShadows__ShadowMapEntryDeletingDestructor", "CStaticShadows__ShadowMapEntryDestructor", "CDXMemoryManager__Free"),
        (("PUSH", "0x4ebdf0"), ("CALL", "0x0055db0a"), ("RET", "0x4")),
    ),
    "0x004ec2f0": target(
        "CStaticShadows__BuildShadowMaps",
        "void __fastcall CStaticShadows__BuildShadowMaps(void * shadow_entry)",
        ("main static-shadow map builder", "0x1c-byte entry array", "heightfield", "ray-triangle"),
        {"build", "heightfield", "ray-triangle", "shadow-grid", "static-shadows"},
        ("void __fastcall CStaticShadows__BuildShadowMaps", "shadow_entry", "CStaticShadows__RayTriangleIntersect", "CStaticShadows__ApplyShadowsToGrid"),
        (("CALL", "dword ptr [EAX + 0x24]"), ("CALL", "0x005490e0"), ("CALL", "0x0055dc20")),
    ),
    "0x004ee0d0": target(
        "CPolyBucket__ScalarDeletingDestructor",
        "void * __thiscall CPolyBucket__ScalarDeletingDestructor(void * this, byte flags)",
        ("CPolyBucket scalar-deleting destructor", "RET 0x4", "CPolyBucket__FreeBuffers", "flags&1"),
        {"destructor", "polybucket", "scalar-deleting", "stale-owner-corrected"},
        ("void * __thiscall CPolyBucket__ScalarDeletingDestructor", "CPolyBucket__FreeBuffers", "CDXMemoryManager__Free"),
        (("CALL", "0x004d3a00"), ("CALL", "0x00549220"), ("RET", "0x4")),
    ),
    "0x004ee0f0": target(
        "CStaticShadows__ApplyShadowsToGrid",
        "void __thiscall CStaticShadows__ApplyShadowsToGrid(void * this, int start_x, int start_y, int width, int height)",
        ("RET 0x10", "global 64x64", "0x200-byte bitmaps", "OR-composited"),
        {"apply-grid", "bitmap", "shadow-grid", "static-shadows"},
        ("void __thiscall CStaticShadows__ApplyShadowsToGrid", "start_x", "Thing_at_0x_x_has_no_RTMesh"),
        (("CALL", "dword ptr [EAX + 0x24]"), ("CALL", "0x0055de9b"), ("RET", "0x10")),
    ),
    "0x004ee410": target(
        "CStaticShadows__RayTriangleIntersect",
        "bool __cdecl CStaticShadows__RayTriangleIntersect(float * triangle_a, float * triangle_b, float * triangle_c, float segment_start_x, float segment_start_y, float segment_start_z, int segment_padding_or_w, float segment_end_x, float segment_end_y, float segment_end_z)",
        ("ray/segment versus triangle predicate", "unused seventh stack slot", "acos-based edge angles", "returns 1"),
        {"geometry", "predicate", "ray-triangle", "static-shadows"},
        ("bool __cdecl CStaticShadows__RayTriangleIntersect", "segment_padding_or_w", "CRT__AcosClassifyAndDispatch"),
        (("JNZ", "0x004ee4c7"), ("FSQRT", ""), ("RET", "")),
    ),
    "0x004ee8a0": target(
        "CStaticShadows__LoadAll",
        "void __stdcall CStaticShadows__LoadAll(void * chunk_reader)",
        ("bulk deserializer", "RET 0x4", "reads a count", "CStaticShadows__Load"),
        {"chunk-reader", "load", "resource", "static-shadows"},
        ("void __stdcall CStaticShadows__LoadAll", "chunk_reader", "CStaticShadows__Load"),
        (("CALL", "0x004ee8f0"), ("RET", "0x4")),
    ),
    "0x004ee8f0": target(
        "CStaticShadows__Load",
        "void __cdecl CStaticShadows__Load(void * chunk_reader)",
        ("single-entry deserializer", "cdecl caller cleans one argument", "0x24-byte linked shadow entry", "0x200-byte bitmap"),
        {"chunk-reader", "load", "resource", "shadow-map-entry", "static-shadows"},
        ("void __cdecl CStaticShadows__Load", "chunk_reader", "OID__AllocObject", "CChunkReader__Read"),
        (("CALL", "0x005490e0"), ("CALL", "0x00423960")),
    ),
}

EXPECTED_XREFS = {
    ("0x004ebbc0", "0x0046c3c4", "CGame__Init", "UNCONDITIONAL_CALL"),
    ("0x004ebe40", "0x004ebbb5", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004ebfb0", "0x00417567", "CThing__RenderAndUpdateStaticShadow", "UNCONDITIONAL_CALL"),
    ("0x004ec250", "0x004ebd70", "CStaticShadows__ClearAllShadowEntries", "UNCONDITIONAL_CALL"),
    ("0x004ee0d0", "0x004ee008", "CStaticShadows__BuildShadowMaps", "UNCONDITIONAL_CALL"),
    ("0x004ee0f0", "0x004ec1e2", "CStaticShadows__UpdateVisibility", "UNCONDITIONAL_CALL"),
    ("0x004ee410", "0x004edee4", "CStaticShadows__BuildShadowMaps", "UNCONDITIONAL_CALL"),
    ("0x004ee8a0", "0x004d7836", "CResourceAccumulator__ReadResourceFile", "UNCONDITIONAL_CALL"),
    ("0x004ee8f0", "0x004ee8d6", "CStaticShadows__LoadAll", "UNCONDITIONAL_CALL"),
}

EXPECTED_LOG_SUMMARIES = {
    "apply_wave511_dry.log": "SUMMARY updated=0 skipped=13 renamed=0 would_rename=4 missing=0 bad=0",
    "apply_wave511_apply.log": "SUMMARY updated=13 skipped=0 renamed=4 would_rename=0 missing=0 bad=0",
    "apply_wave511_receiver_fix_apply.log": "SUMMARY updated=1 skipped=12 renamed=0 would_rename=0 missing=0 bad=0",
    "apply_wave511_verify_dry.log": "SUMMARY updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0",
}

PUBLIC_NOTE_TOKENS = (
    "13",
    "4 renames",
    "CStaticShadows__Initialise",
    "CStaticShadows__ShadowMapEntryDeletingDestructor",
    "CPolyBucket__ScalarDeletingDestructor",
    "runtime shadow behavior",
    "rebuild parity",
)

CALLSITE_TOKENS = {
    "callsite_0046c3c4.tsv": ("MOV\tECX, 0x9c8010", "CALL\t0x004ebbc0"),
    "build_static_shadows_callback_004ebbb0.tsv": ("MOV\tECX, 0x9c8010", "JMP\t0x004ebe40"),
}


def normalize_addr(address: str) -> str:
    address = (address or "").strip().lower()
    if not address or address.startswith("<"):
        return address
    body = address[2:] if address.startswith("0x") else address
    return f"0x{int(body, 16):08x}"


def compact_text(value: str) -> str:
    return " ".join((value or "").replace("\t", " ").replace("\r", " ").replace("\n", " ").split())


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def find_decomp_file(decomp_dir: Path, address: str, expected_name: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    if not candidates:
        candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:].lstrip('0')}_*.c"))
    require(bool(candidates), f"missing decompile export for {address} {expected_name}")
    return candidates[0]


def validate_metadata(base: Path) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    by_addr = {normalize_addr(row["address"]): row for row in rows}
    require(set(TARGETS).issubset(by_addr), "post metadata missing one or more Wave511 targets")
    for address, expected in TARGETS.items():
        row = by_addr[address]
        require(row["name"] == expected["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        comment = compact_text(row["comment"])
        for token in expected["comment_tokens"]:
            require(token in comment, f"{address} comment missing token {token!r}")


def validate_tags(base: Path) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    by_addr = {normalize_addr(row["address"]): row for row in rows}
    require(set(TARGETS).issubset(by_addr), "post tags missing one or more Wave511 targets")
    for address, expected in TARGETS.items():
        raw_tags = by_addr[address]["tags"].replace(",", ";")
        tags = {tag.strip() for tag in raw_tags.split(";") if tag.strip()}
        missing = expected["tags"] - tags
        require(not missing, f"{address} missing tags: {sorted(missing)}")


def validate_decompile(base: Path) -> None:
    decomp_dir = base / "post-decomp"
    require(decomp_dir.exists(), f"missing decompile dir: {decomp_dir}")
    for address, expected in TARGETS.items():
        path = find_decomp_file(decomp_dir, address, str(expected["name"]))
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token in text, f"{address} decompile missing token {token!r}")


def validate_instructions(base: Path) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_addr.setdefault(normalize_addr(row["target_addr"]), []).append(row)
    for address, expected in TARGETS.items():
        rows_for_target = by_addr.get(address, [])
        require(rows_for_target, f"{address} missing instruction rows")
        for mnemonic, operand_token in expected["instruction_tokens"]:
            found = any(
                row["mnemonic"] == mnemonic and operand_token in compact_text(row.get("operands", ""))
                for row in rows_for_target
            )
            require(found, f"{address} missing instruction token {mnemonic} {operand_token!r}")


def validate_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {
        (
            normalize_addr(row["target_addr"]),
            normalize_addr(row["from_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    missing = EXPECTED_XREFS - actual
    require(not missing, f"missing xrefs: {sorted(missing)}")


def validate_logs(base: Path) -> None:
    for filename, expected in EXPECTED_LOG_SUMMARIES.items():
        path = base / filename
        require(path.exists(), f"missing log: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        require(expected in text, f"{filename} missing summary {expected!r}")
        require("REPORT: Save succeeded" in text, f"{filename} missing save success")
        for token in ("MISSING:", "BADNAME:", "Exception", "LockException"):
            require(token not in text, f"{filename} contains {token}")


def validate_public_note() -> None:
    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    text = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token in text, f"public note missing token {token!r}")


def validate_queue(base: Path) -> None:
    path = base / "queue_after_wave511.txt"
    require(path.exists(), f"missing queue snapshot: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in ("Total functions:", "Commentless functions:", "Undefined signatures:", "Param signatures:"):
        require(token in text, f"queue snapshot missing {token}")


def validate_callsites(base: Path) -> None:
    for filename, tokens in CALLSITE_TOKENS.items():
        path = base / filename
        require(path.exists(), f"missing callsite proof: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            require(token in text, f"{filename} missing token {token!r}")


def run_check(base: Path) -> None:
    validate_metadata(base)
    validate_tags(base)
    validate_decompile(base)
    validate_instructions(base)
    validate_xrefs(base)
    validate_logs(base)
    validate_public_note()
    validate_queue(base)
    validate_callsites(base)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    try:
        run_check(args.base)
    except AssertionError as exc:
        if args.check:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        raise

    print(f"PASS: Wave511 static-shadows evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
