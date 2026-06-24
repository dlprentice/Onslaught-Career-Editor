#!/usr/bin/env python3
"""Validate Wave462 particle sprite/render static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave462-particle-sprite-render-current"
COMMON_TAGS = {"static-reaudit", "particle-sprite-render-wave462", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 14,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 14,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 14,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004c0940": target(
        "CPDSimpleSprite__SetUVFromTileIndex",
        "void __thiscall CPDSimpleSprite__SetUVFromTileIndex(void * this, int tile_index, uint tile_grid_selector, int unused_context)",
        ["Wave462 correction", "atlas UV rectangle", "+0xb8", "+0xc4", "falls back to full 0..1 UVs"],
        ["uv-atlas", "sprite", "signature-corrected", "comment-hardened"],
        ["+ 0xb8", "+ 0xc4", "_DAT_005d8568"],
    ),
    "0x004c14f0": target(
        "CPDSimpleSprite__VFunc_10_004c14f0",
        "int __thiscall CPDSimpleSprite__VFunc_10_004c14f0(void * this, void * particle, int unused_context)",
        ["Wave462 correction", "vtable slot 10", "particle +0x74", "frame accumulator"],
        ["vtable-slot-10", "sprite-update", "signature-corrected", "comment-hardened"],
        ["CPDSimpleSprite__EvaluateExpressionRecursive", "+ 0x74", "+ 0x78"],
    ),
    "0x004c35d0": target(
        "CEngine__ConfigureParticleBurstForDistance",
        "void __thiscall CEngine__ConfigureParticleBurstForDistance(void * this, void * particle, int unused_context)",
        ["Wave462 correction", "particle +0x80", "CParticleManager__SetParticleResource", "resource-slot records"],
        ["particle-resource", "distance-lod", "signature-corrected", "comment-hardened"],
        ["CParticleManager__SetParticleResource", "0x3e4ccccd", "+ 0x88"],
    ),
    "0x004c5280": target(
        "CPDSimpleSprite__CopyTransformMatrix",
        "void __thiscall CPDSimpleSprite__CopyTransformMatrix(void * this, void * out_matrix, void * unused_context)",
        ["Wave462 correction", "Copies observed CPDSimpleSprite matrix/basis fields", "caller-provided output block", "local decompiler artifacts"],
        ["transform-copy", "sprite", "signature-corrected", "comment-hardened"],
        ["+ 0x28", "+ 0x2c", "return;"],
    ),
    "0x004c5c50": target(
        "CPDSimpleSprite__BuildUvAtlasBuckets",
        "void __fastcall CPDSimpleSprite__BuildUvAtlasBuckets(float unused_seed)",
        ["Wave462 correction", "DAT_00829e58", "five tile-grid buckets", "DAT_0082b39c"],
        ["uv-atlas", "table-init", "signature-corrected", "comment-hardened"],
        ["DAT_00829e58", "DAT_0082b39c", "0x10"],
    ),
    "0x004c5d50": target(
        "CPDSimpleSprite__ProcessAndRenderSpriteList",
        "void __fastcall CPDSimpleSprite__ProcessAndRenderSpriteList(void * descriptor)",
        ["Wave462 correction", "active particle list", "emits quad vertices plus six indices", "visibility/distance bits"],
        ["sprite-render", "vertex-emission", "signature-corrected", "comment-hardened"],
        ["CPDSimpleSprite__BuildUvAtlasBuckets", "CVBufTexture__GetVertexPtrAt", "DXParticleTexture__GetIndexBuffer"],
    ),
    "0x004c78b0": target(
        "CPDSimpleSprite__ScaleVec3InPlace",
        "void __thiscall CPDSimpleSprite__ScaleVec3InPlace(void * this, float scale, float unused_context)",
        ["Wave462 correction", "scales three consecutive float components", "in place", "sprite render path"],
        ["vec3", "scale", "signature-corrected", "comment-hardened"],
        ["* *(float *)this", "+ 8", "return;"],
    ),
    "0x004c78d0": target(
        "CPDSimpleSprite__ReciprocalVec3Magnitude",
        "double __fastcall CPDSimpleSprite__ReciprocalVec3Magnitude(void * vec3)",
        ["Wave462 correction", "1.0 / sqrt", "three float components", "no zero-length guard"],
        ["vec3", "reciprocal-magnitude", "signature-corrected", "comment-hardened"],
        ["SQRT", "_DAT_005d8568 /", "+ 8"],
    ),
    "0x004c7950": target(
        "CPDSimpleSprite__EvaluateCurveDrivenScale",
        "double __thiscall CPDSimpleSprite__EvaluateCurveDrivenScale(void * this, void * x_value, float lifetime, float particle_context, float eval_flags)",
        ["Wave462 correction", "expression-driven scalar", "pow/exp/sin/cos/inv/log/rand", "clamp/wrap-style output modes"],
        ["curve-scale", "expression-eval", "signature-corrected", "comment-hardened"],
        ["CPDSimpleSprite__EvaluateExpressionRecursive", "_rand()", "fsin"],
    ),
    "0x004c8040": target(
        "CPDSimpleSprite__VFunc_23_004c8040",
        "void __fastcall CPDSimpleSprite__VFunc_23_004c8040(void * descriptor)",
        ["Wave462 correction", "vtable slot 23", "initializes the noise table", "only when descriptor +0x6c is nonzero"],
        ["vtable-slot-23", "render-dispatch", "signature-corrected", "comment-hardened"],
        ["CPDSimpleSprite__InitNoiseTableOnce", "CPDSimpleSprite__ProcessAndRenderSpriteList", "+ 0x6c"],
    ),
    "0x004c8060": target(
        "CEngine__ComputeSpriteTintByDistance",
        "int __thiscall CEngine__ComputeSpriteTintByDistance(void * this, int particle_index, int alpha_scale, float descriptor_context, float distance_context)",
        ["Wave462 correction", "Computes a packed sprite tint/alpha value", "expression colour curves", "distance or age fade"],
        ["tint", "distance-fade", "signature-corrected", "comment-hardened"],
        ["CPDSimpleSprite__EvaluateExpressionRecursive", "return -1", "0xff"],
    ),
    "0x004cab30": target(
        "Color32__LerpArgb",
        "int __cdecl Color32__LerpArgb(uint from_argb, uint to_argb, float t)",
        ["Wave462 correction", "Linearly interpolates each ARGB byte", "packed 32-bit colours", "no clamp is applied inside"],
        ["color", "lerp", "signature-corrected", "comment-hardened"],
        ["ROUND", "0x100", "& 0xff"],
    ),
    "0x004cac40": target(
        "Math__InvLerpClamp01",
        "double __cdecl Math__InvLerpClamp01(float value, float min_value, float max_value)",
        ["Wave462 correction", "inverse lerp", "clamps the result to 0..1", "no visible divide-by-zero guard"],
        ["math", "clamp", "signature-corrected", "comment-hardened"],
        ["_DAT_005d856c", "_DAT_005d8568", "return (double)"],
    ),
    "0x004cac80": target(
        "CPDSelector__ConvertNormalizedToScreenCoords",
        "void __cdecl CPDSelector__ConvertNormalizedToScreenCoords(float normalized_x, float normalized_y)",
        ["Wave462 correction", "Scales a normalized pair", "rounds through CRT__RoundDoubleWithFpuChecks", "does not expose a stable return/output contract"],
        ["selector", "screen-coords", "signature-corrected", "comment-hardened"],
        ["CRT__RoundDoubleWithFpuChecks", "_DAT_005db2b8"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004c0940", "0x004c0770", "<no_function>"),
    ("0x004c14f0", "0x005ddf88", "<no_function>"),
    ("0x004c35d0", "0x004c36d5", "<no_function>"),
    ("0x004c5280", "0x004c5157", "<no_function>"),
    ("0x004c5c50", "0x004c5d6f", "CPDSimpleSprite__ProcessAndRenderSpriteList"),
    ("0x004c5d50", "0x004c8056", "CPDSimpleSprite__VFunc_23_004c8040"),
    ("0x004c78b0", "0x004c7689", "CPDSimpleSprite__ProcessAndRenderSpriteList"),
    ("0x004c78d0", "0x004c73ef", "CPDSimpleSprite__ProcessAndRenderSpriteList"),
    ("0x004c7950", "0x004c74f0", "CPDSimpleSprite__ProcessAndRenderSpriteList"),
    ("0x004c8040", "0x005ddfbc", "<no_function>"),
    ("0x004c8060", "0x004c8a21", "<no_function>"),
    ("0x004cab30", "0x004ca15d", "<no_function>"),
    ("0x004cac40", "0x004ca14c", "<no_function>"),
    ("0x004cac80", "0x004c9f2a", "<no_function>"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime rendering proven",
    "exact layout proven",
    "source identity proven",
    "fully re'ed",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"SUMMARY\s+(.+)", text)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(1))}


def check_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    actual = parse_summary(read_text(path))
    if not actual:
        failures.append(f"{path.name}: missing SUMMARY")
        return
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{path.name}: expected {key}={value}, got {actual.get(key)}")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_metadata.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"post_metadata.tsv: missing {address}")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    seen: dict[str, set[str]] = {}
    for row in rows:
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        seen.setdefault(row.get("address", ""), set()).update(tags)
    for address, expected in TARGETS.items():
        actual = seen.get(normalize_address(address), set())
        for tag in expected["tags"]:
            if tag not in actual:
                failures.append(f"{address}: missing tag {tag}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {(row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post decompile export")
            continue
        for token in expected["decompileTokens"]:
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    return ("FAIL" if failures else "PASS", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Accepted for npm-script consistency")
    parser.add_argument("--base", type=Path, default=BASE, help="Wave462 artifact directory")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
