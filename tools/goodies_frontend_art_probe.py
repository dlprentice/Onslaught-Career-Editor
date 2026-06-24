#!/usr/bin/env python3
"""Verify catalog coverage for FrontEnd Goodies artwork assets.

This probe consumes the asset catalog generated from a local Battle Engine
Aquila install and emits a public-safe summary. It proves that specific
FrontEnd Goodies textures are present and exported, without exposing absolute
source paths or bundling private game assets.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = (
    ROOT
    / "subagents"
    / "asset-full-install-2026-05-07"
    / "full-export"
    / "asset_catalog"
    / "catalog.json"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-frontend-art"
    / "current"
    / "goodies-frontend-art.json"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class RequiredTexture:
    key: str
    canonical_ref: str
    reason: str


REQUIRED_TEXTURES = (
    RequiredTexture(
        "goodies-icon-1",
        "frontend\\v2\\fe_goodies1.tga",
        "Goodies wall icon state seen in the FrontEnd texture set.",
    ),
    RequiredTexture(
        "goodies-icon-2",
        "frontend\\v2\\fe_goodies2.tga",
        "Goodies wall icon state seen in the FrontEnd texture set.",
    ),
    RequiredTexture(
        "goodies-icon-3",
        "frontend\\v2\\fe_goodies3.tga",
        "Goodies wall icon state seen in the FrontEnd texture set.",
    ),
    RequiredTexture(
        "goodies-icon-4",
        "frontend\\v2\\fe_goodies4.tga",
        "Larger Goodies wall icon/backing state.",
    ),
    RequiredTexture(
        "goodies-nav-symbol",
        "frontend\\v3\\fe_bea_title_nav_symbol_goodies01.tga",
        "Goodies navigation/title symbol.",
    ),
    RequiredTexture(
        "metal-ring-transition-1",
        "frontend\\v2\\fe_metal_ring_trans_from_levsel1.tga",
        "Goodies/level-select ring transition artwork.",
    ),
    RequiredTexture(
        "metal-ring-transition-2",
        "frontend\\v2\\fe_metal_ring_trans_from_levsel2.tga",
        "Goodies/level-select ring transition artwork.",
    ),
    RequiredTexture(
        "rock-background",
        "frontend\\v2\\fe_rock_background.tga",
        "FrontEnd background texture used near the Goodies/gallery shell.",
    ),
)

ADJACENT_TOKENS = (
    "goodies",
    "title_nav",
    "select_level",
    "metal_ring",
    "rock_background",
    "ranking_",
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_ref(value: object) -> str:
    return str(value).replace("\\", "/").lower()


def resolve_catalog_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


def load_texture_rows(catalog_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    if not catalog_path.is_file():
        return [], [f"missing catalog: {relative(catalog_path)}"]

    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"catalog JSON decode failed: {exc}"]

    if isinstance(data, dict):
        rows = data.get("textures", [])
    elif isinstance(data, list):
        rows = data
    else:
        rows = []

    if not isinstance(rows, list):
        failures.append("catalog textures field is not a list")
        return [], failures

    texture_rows = [row for row in rows if isinstance(row, dict)]
    if len(texture_rows) != len(rows):
        failures.append("catalog contains non-object texture rows")
    return texture_rows, failures


def png_dimensions(path: Path) -> tuple[int | None, int | None, str | None]:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError as exc:
        return None, None, f"cannot read PNG: {exc}"

    if len(header) < 24 or not header.startswith(PNG_SIGNATURE):
        return None, None, "not a PNG file"
    if header[12:16] != b"IHDR":
        return None, None, "missing PNG IHDR chunk"
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        return None, None, "invalid PNG dimensions"
    return width, height, None


def row_public_summary(
    row: dict[str, Any],
    *,
    required: RequiredTexture,
    check_exports: bool,
) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    export_paths = [Path(str(path)) for path in row.get("export_png_paths", []) or []]
    existing_exports = [path for path in export_paths if resolve_catalog_path(path).is_file()]

    width: int | None = None
    height: int | None = None
    if existing_exports:
        width, height, error = png_dimensions(resolve_catalog_path(existing_exports[0]))
        if error:
            failures.append(f"{required.canonical_ref}: {error}")
    elif check_exports:
        failures.append(f"{required.canonical_ref}: no readable exported PNG")

    return (
        {
            "key": required.key,
            "canonicalRef": required.canonical_ref,
            "reason": required.reason,
            "catalogRowPresent": True,
            "sourceAyaCount": int(row.get("source_aya_count", 0) or 0),
            "exportPngCount": int(row.get("export_png_count", 0) or 0),
            "readableExportPngCount": len(existing_exports),
            "exportedPngDimensions": {"width": width, "height": height},
            "packedTextRefCount": int(row.get("packed_text_ref_count", 0) or 0),
            "totalPackedRefCount": int(row.get("total_packed_ref_count", 0) or 0),
            "referencedInPacked": bool(row.get("referenced_in_packed", False)),
        },
        failures,
    )


def build_report(catalog_path: Path, *, check_exports: bool = False) -> dict[str, Any]:
    catalog_path = resolve_catalog_path(catalog_path)
    rows, failures = load_texture_rows(catalog_path)
    rows_by_ref = {normalize_ref(row.get("canonical_ref", "")): row for row in rows}

    present_required: list[dict[str, Any]] = []
    missing_required: list[str] = []
    for required in REQUIRED_TEXTURES:
        row = rows_by_ref.get(normalize_ref(required.canonical_ref))
        if row is None:
            missing_required.append(required.canonical_ref)
            failures.append(f"missing required texture: {required.canonical_ref}")
            continue
        summary, row_failures = row_public_summary(
            row, required=required, check_exports=check_exports
        )
        present_required.append(summary)
        failures.extend(row_failures)

    adjacent_rows = [
        row
        for row in rows
        if normalize_ref(row.get("canonical_ref", "")).startswith("frontend/")
        and any(token in normalize_ref(row.get("canonical_ref", "")) for token in ADJACENT_TOKENS)
    ]

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "goodies-frontend-art.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "catalog": relative(catalog_path),
        "textureRowCount": len(rows),
        "frontendGoodiesAdjacentTextureRowCount": len(adjacent_rows),
        "requiredTextureCount": len(REQUIRED_TEXTURES),
        "presentRequiredTextureCount": len(present_required),
        "missingRequiredTextures": missing_required,
        "requiredTextures": present_required,
        "publicSafety": {
            "stripsAbsoluteSourcePaths": True,
            "stripsExportFilePaths": True,
            "embedsPrivateAssets": False,
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
        },
        "currentClaims": [
            "These FrontEnd Goodies artwork rows are cataloged from a local PC game install.",
            "Readable PNG exports prove the extractor produced inspectable image artifacts for these rows.",
            "The report intentionally strips source and export file paths because they can reveal private local game material.",
        ],
        "notClaimed": [
            "This does not prove the retail Goodies wall layout, animation, or input hit testing.",
            "This does not prove the in-game model viewer loop.",
            "This does not make any redistribution claim for private game art.",
            "This does not mutate saves, Ghidra, or BEA.exe.",
        ],
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if required catalog rows or readable PNG exports are missing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.catalog, check_exports=args.check)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "Goodies FrontEnd art: "
        f"required={report['requiredTextureCount']} "
        f"present={report['presentRequiredTextureCount']} "
        f"adjacentRows={report['frontendGoodiesAdjacentTextureRowCount']}"
    )
    if report["missingRequiredTextures"]:
        print("missing: " + ", ".join(report["missingRequiredTextures"]))
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
