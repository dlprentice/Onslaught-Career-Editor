#!/usr/bin/env python3
"""Check whether Goodies rows link to exported texture/model catalog rows.

This validates the same normalized matching shape used by the WinUI Asset
Library: Goodies primary texture refs should match texture catalog refs, and
Goodies primary mesh refs should match loose mesh catalog refs. Output strips
raw paths and asset names; only counts and failing Goodie indices are recorded.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = (
    ROOT
    / "subagents"
    / "goodie_catalog_probe_2026-05-07"
    / "asset_catalog"
    / "catalog.json"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-catalog-linkage"
    / "current"
    / "goodies-catalog-linkage.json"
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize(value: object) -> str:
    return str(value or "").replace("\\", "/").strip().lower()


def catalog_match(needle: str, haystack: set[str]) -> bool:
    if not needle:
        return False
    return any(candidate == needle or candidate.endswith(needle) for candidate in haystack)


def has_video_id(value: object) -> bool:
    text = str(value or "").strip()
    return bool(text) and text != "-1"


def build_report(catalog_path: Path) -> dict[str, object]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    goodies = catalog.get("goodies", [])
    texture_refs = {normalize(row.get("canonical_ref")) for row in catalog.get("textures", [])}
    mesh_refs = {normalize(row.get("canonical_ref")) for row in catalog.get("loose_meshes", [])}

    texture_rows = []
    mesh_rows = []
    video_rows = []
    video_rows_without_archive = []
    missing_texture_matches = []
    missing_mesh_matches = []
    kind_counts: Counter[str] = Counter()

    for row in goodies:
        index = int(row.get("index", -1))
        kind_counts[str(row.get("content_kind") or "Unknown")] += 1
        texture_ref = normalize(row.get("primary_texture_ref"))
        mesh_ref = normalize(row.get("primary_mesh_ref"))
        if texture_ref:
            texture_rows.append(index)
            if not catalog_match(texture_ref, texture_refs):
                missing_texture_matches.append(index)
        if mesh_ref:
            mesh_rows.append(index)
            if not catalog_match(mesh_ref, mesh_refs):
                missing_mesh_matches.append(index)
        if has_video_id(row.get("video_sequence_id")):
            video_rows.append(index)
            if not str(row.get("source_archive", "")).strip():
                video_rows_without_archive.append(index)

    status = "PASS" if not missing_texture_matches and not missing_mesh_matches else "FAIL"
    if video_rows_without_archive != [232]:
        status = "FAIL"
    return {
        "schema": "goodies-catalog-linkage.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceCatalog": relative(catalog_path),
        "status": status,
        "summary": {
            "goodieRows": len(goodies),
            "contentKindCounts": dict(sorted(kind_counts.items())),
            "primaryTextureRows": len(texture_rows),
            "primaryTextureRowsMatched": len(texture_rows) - len(missing_texture_matches),
            "primaryMeshRows": len(mesh_rows),
            "primaryMeshRowsMatched": len(mesh_rows) - len(missing_mesh_matches),
            "videoRows": len(video_rows),
            "videoRowsWithSourceArchive": len(video_rows) - len(video_rows_without_archive),
            "videoRowsWithoutSourceArchive": video_rows_without_archive,
            "missingTextureMatchIndices": missing_texture_matches,
            "missingMeshMatchIndices": missing_mesh_matches,
        },
        "safety": {
            "stripsAbsolutePaths": True,
            "stripsRawAssetNames": True,
            "extractsAssets": False,
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
        },
        "notes": [
            "This proves catalog-linkage readiness, not final textured/animated WinUI model rendering.",
            "WinUI currently shows an FBX-derived wireframe for matched model exports and delegates full material review to the local FBX viewer.",
            "Goodie 232 is intentionally represented as a catalog video handoff for cutscene 33 even though there is no matching goodie_232_res_PC.aya source archive in the checked PC install.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.catalog)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "Goodie linkage: "
        f"textures {summary['primaryTextureRowsMatched']}/{summary['primaryTextureRows']}, "
        f"models {summary['primaryMeshRowsMatched']}/{summary['primaryMeshRows']}, "
        f"videos {summary['videoRows']} "
        f"({summary['videoRowsWithSourceArchive']} archive-backed, "
        f"{len(summary['videoRowsWithoutSourceArchive'])} catalog-only)"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
