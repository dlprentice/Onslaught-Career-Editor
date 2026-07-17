#!/usr/bin/env python3
"""
Build a deduplicated cross-surface private asset catalog.

This ties together:
- packed AYA reference manifests
- loose texture exports
- loose mesh exports
- embedded packed-mesh exports
- merged language corpus
- loose video manifest

Examples:
    py -3 tools/export_asset_catalog.py --self-test
    py -3 tools/export_asset_catalog.py --bundle-root <generated-root> --out-dir <generated-root>/asset_catalog ...
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections import Counter
from pathlib import Path

import aya_archive_inventory as aai
from safe_generated_output import SecuredOutputRoot


CATALOG_SCHEMA_VERSION = 2
CATALOG_PATH_CONTRACT = "bundle-root-relative"


def repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("/", "\\")
    except Exception:
        return str(path).replace("/", "\\")


def bundle_rel(path: Path, bundle_root: Path, label: str) -> str:
    try:
        relative = path.resolve().relative_to(bundle_root.resolve())
    except ValueError as exc:
        raise SystemExit(f"{label} is outside --bundle-root: {path}") from exc
    if not relative.parts:
        raise SystemExit(f"{label} must be a file below --bundle-root: {path}")
    return str(relative).replace("/", "\\")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def choose_texture_ref(refs: set[str], fallback_name: str) -> str:
    if not refs:
        return fallback_name.lower()
    return sorted(refs, key=lambda value: (value.startswith("mustbe_"), len(value), value))[0]


def texture_aliases_for_catalog(file_name: str) -> set[str]:
    lower = file_name.lower()
    stem = lower[:-4] if lower.endswith(".aya") else lower
    if "(0)" in stem:
        stem = stem.split("(0)", 1)[0]

    if ".tga" in stem:
        base = stem[: stem.index(".tga") + 4]
    elif ".t" in stem:
        base = f"{stem[: stem.index('.t') + 2]}ga"
    else:
        base = stem

    aliases = {base.replace("%", "\\")}
    for alias in list(aliases):
        if alias.startswith("mustbe_"):
            aliases.add(alias[len("mustbe_") :])
    return aliases


def mesh_aliases_from_loose_name(file_name: str) -> list[str]:
    lower = file_name.lower()
    if not lower.endswith(".aya"):
        return [lower]
    stem = lower[:-4]
    aliases = {stem}
    if stem.startswith("m_"):
        aliases.add(stem[2:])
    return sorted(aliases)


def choose_mesh_ref(aliases: list[str]) -> str:
    return sorted(aliases, key=lambda value: (value.startswith("m_"), len(value), value))[0]


def packed_ref_maps(packed_manifest: dict[str, object], key: str) -> dict[str, dict[str, object]]:
    rows = packed_manifest[key]
    return {
        row["ref"]: {
            "count": row["count"],
            "match_count": row["match_count"],
            "matches": row["matches"],
        }
        for row in rows
    }


def build_texture_catalog(
    texture_manifest: list[dict[str, object]],
    packed_manifest: dict[str, object],
    repo_root: Path,
    bundle_root: Path,
) -> list[dict[str, object]]:
    text_map = packed_ref_maps(packed_manifest, "text_texture_refs")
    gdie_map = packed_ref_maps(packed_manifest, "gdie_texture_refs")
    catalog: dict[str, dict[str, object]] = {}

    for row in texture_manifest:
        input_path = Path(row["input"])
        output_path = Path(row["output"])
        refs = texture_aliases_for_catalog(input_path.name)
        canonical_ref = choose_texture_ref(refs, input_path.stem)
        entry = catalog.setdefault(
            canonical_ref,
            {
                "catalog_id": f"texture:{canonical_ref}",
                "kind": "texture",
                "canonical_ref": canonical_ref,
                "aliases": sorted(refs) if refs else [canonical_ref],
                "source_aya_paths": [],
                "source_roots": set(),
                "loose_export_pngs": [],
                "packed_text_ref_count": text_map.get(canonical_ref, {}).get("count", 0),
                "gdie_ref_count": gdie_map.get(canonical_ref, {}).get("count", 0),
            },
        )
        entry["source_aya_paths"].append(repo_rel(input_path, repo_root))
        entry["source_roots"].add(input_path.parent.name.lower())
        entry["loose_export_pngs"].append(bundle_rel(output_path, bundle_root, "texture export"))

    out: list[dict[str, object]] = []
    for key in sorted(catalog):
        entry = catalog[key]
        source_paths = sorted(set(entry["source_aya_paths"]))
        export_paths = sorted(set(entry["loose_export_pngs"]))
        packed_text = entry["packed_text_ref_count"]
        gdie = entry["gdie_ref_count"]
        out.append(
            {
                "catalog_id": entry["catalog_id"],
                "kind": entry["kind"],
                "canonical_ref": entry["canonical_ref"],
                "aliases": entry["aliases"],
                "source_aya_count": len(source_paths),
                "source_aya_paths": source_paths,
                "source_roots": sorted(entry["source_roots"]),
                "export_png_count": len(export_paths),
                "export_png_paths": export_paths,
                "packed_text_ref_count": packed_text,
                "gdie_ref_count": gdie,
                "total_packed_ref_count": packed_text + gdie,
                "referenced_in_packed": (packed_text + gdie) > 0,
            }
        )
    return out


def build_loose_mesh_catalog(
    mesh_manifest: list[dict[str, object]],
    packed_manifest: dict[str, object],
    repo_root: Path,
    bundle_root: Path,
) -> list[dict[str, object]]:
    reference_map = packed_ref_maps(packed_manifest, "reference_mesh_refs")
    gdie_map = packed_ref_maps(packed_manifest, "gdie_mesh_refs")
    catalog: dict[str, dict[str, object]] = {}

    for row in mesh_manifest:
        input_path = Path(row["input"])
        output_path = Path(row["output"])
        aliases = mesh_aliases_from_loose_name(input_path.name)
        canonical_ref = choose_mesh_ref(aliases)
        entry = catalog.setdefault(
            canonical_ref,
            {
                "catalog_id": f"mesh:{canonical_ref}",
                "kind": "loose_mesh",
                "canonical_ref": canonical_ref,
                "aliases": aliases,
                "source_aya_paths": [],
                "export_fbx_paths": [],
                "packed_reference_count": reference_map.get(canonical_ref, {}).get("count", 0),
                "gdie_ref_count": gdie_map.get(canonical_ref, {}).get("count", 0),
            },
        )
        entry["source_aya_paths"].append(repo_rel(input_path, repo_root))
        entry["export_fbx_paths"].append(bundle_rel(output_path, bundle_root, "loose-mesh export"))

    out: list[dict[str, object]] = []
    for key in sorted(catalog):
        entry = catalog[key]
        source_paths = sorted(set(entry["source_aya_paths"]))
        export_paths = sorted(set(entry["export_fbx_paths"]))
        packed_ref = entry["packed_reference_count"]
        gdie = entry["gdie_ref_count"]
        out.append(
            {
                "catalog_id": entry["catalog_id"],
                "kind": entry["kind"],
                "canonical_ref": entry["canonical_ref"],
                "aliases": entry["aliases"],
                "source_aya_count": len(source_paths),
                "source_aya_paths": source_paths,
                "export_fbx_count": len(export_paths),
                "export_fbx_paths": export_paths,
                "packed_reference_count": packed_ref,
                "gdie_ref_count": gdie,
                "total_packed_ref_count": packed_ref + gdie,
                "referenced_in_packed": (packed_ref + gdie) > 0,
            }
        )
    return out


def build_embedded_mesh_catalog(
    embedded_manifest: list[dict[str, object]],
    repo_root: Path,
    bundle_root: Path,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in embedded_manifest:
        input_path = Path(row["input"])
        output_path = Path(row["output"])
        source_archive = input_path.parent.name
        body_name = input_path.stem
        out.append(
            {
                "catalog_id": f"embedded_mesh:{source_archive}/{body_name}",
                "kind": "embedded_mesh",
                "source_archive": source_archive,
                "body_name": body_name,
                "source_body_path": repo_rel(input_path, repo_root),
                "export_fbx_path": bundle_rel(output_path, bundle_root, "embedded-mesh export"),
            }
        )
    return sorted(out, key=lambda item: item["catalog_id"])


def build_video_catalog(video_manifest: dict[str, object]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in video_manifest["files"]:
        relative_path = row["relative_path"].replace("/", "\\")
        out.append(
            {
                "catalog_id": f"video:{relative_path.lower()}",
                "kind": "video",
                "relative_path": relative_path,
                "family": row["family"],
                "sequence_id": row["sequence_id"],
                "size": row["size"],
                "sha256": row["sha256"],
                "magic": row["magic"],
            }
        )
    return out


def build_language_catalog(language_matrix: dict[str, object]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in language_matrix["rows"]:
        named_text_count = sum(1 for item in row["languages"].values() if item["text"])
        named_audio_count = sum(1 for item in row["languages"].values() if item["audio"])
        out.append(
            {
                "catalog_id": f"language:{row['id']}",
                "kind": "language_row",
                "id": row["id"],
                "hex": row["hex"],
                "name": row["name"],
                "language_count": len(row["languages"]),
                "text_present_count": named_text_count,
                "audio_present_count": named_audio_count,
                "languages": row["languages"],
            }
        )
    return out


def _goodie_index_from_archive(archive_path: str) -> int | None:
    archive_name = Path(archive_path).name.lower()
    prefix = "goodie_"
    suffix = "_res_pc.aya"
    if not archive_name.startswith(prefix) or not archive_name.endswith(suffix):
        return None

    try:
        return int(archive_name[len(prefix) : -len(suffix)])
    except ValueError:
        return None


def _language_text(row: dict[str, object]) -> str:
    languages = row.get("languages", {})
    if not isinstance(languages, dict):
        return ""

    for key in ("english", "american"):
        item = languages.get(key)
        if isinstance(item, dict) and item.get("text"):
            return str(item["text"])

    for item in languages.values():
        if isinstance(item, dict) and item.get("text"):
            return str(item["text"])
    return ""


def _goodie_title_map(language_rows: list[dict[str, object]]) -> dict[int, str]:
    titles: dict[int, str] = {}
    for row in language_rows:
        name = str(row.get("name", ""))
        match = re.fullmatch(r"GOODIE_TEXT_(\d+)_TITLE", name)
        if not match:
            continue

        title = _language_text(row).strip()
        if not title:
            continue

        titles[int(match.group(1)) - 1] = title
    return titles


def _goodie_title_from_ref(index: int, texture_refs: list[str], mesh_refs: list[str], video_sequence_id: str) -> str:
    if video_sequence_id:
        return f"Goodie {index:03d} - Cutscene {video_sequence_id}"

    ref = mesh_refs[0] if mesh_refs else texture_refs[0] if texture_refs else ""
    if not ref:
        return f"Goodie {index:03d}"

    stem = Path(ref.replace("\\", "/")).stem
    for prefix in ("ca_fc_", "ca_fu_", "ca_mu_", "ca_ma_", "ca_fa_", "ca_be_", "ca_boss_", "ca_cl_"):
        if stem.lower().startswith(prefix):
            stem = stem[len(prefix) :]
            break

    label = " ".join(part for part in stem.replace("-", "_").split("_") if part)
    return f"Goodie {index:03d} - {label.title()}" if label else f"Goodie {index:03d}"


def _goodie_source_type(index: int) -> str:
    if index <= 7:
        return "Artwork"
    if index in (12, 13, 24, 33, 34, 35):
        return "Artwork"
    if index <= 57:
        return "Model"
    if index <= 65:
        return "Artwork"
    if index <= 70:
        return "Level"
    if index <= 74:
        return "Artwork"
    if index == 75:
        return "Video"
    if index == 76:
        return "Model"
    if index == 77:
        return "Video"
    if index > 200:
        return "Video"
    return "Artwork"


def _goodie_video(
    index: int,
    video_by_sequence: dict[str, dict[str, object]],
    video_by_relative: dict[str, dict[str, object]],
) -> tuple[str, dict[str, object] | None]:
    if 201 <= index <= 231:
        sequence_id = f"{index - 200:02d}"
        return sequence_id, video_by_sequence.get(sequence_id)
    if index == 232:
        return "33", video_by_sequence.get("33")
    if index == 75:
        return "gill_m_on_a_fork", video_by_relative.get("gill_m_on_a_fork.vid")
    if index == 77:
        return "UsTheMovie", video_by_relative.get("usthemovie.vid")
    return "", None


def build_goodie_catalog(
    packed_manifest: dict[str, object],
    videos: list[dict[str, object]],
    language_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    goodie_titles = _goodie_title_map(language_rows)
    video_by_sequence = {
        item["sequence_id"]: item
        for item in videos
        if item.get("family") == "cutscene_numeric" and item.get("sequence_id")
    }
    video_by_relative = {
        str(item["relative_path"]).replace("\\", "/").lower(): item
        for item in videos
        if item.get("relative_path")
    }
    rows: list[dict[str, object]] = []

    for item in packed_manifest.get("gdie_families", []):
        index = _goodie_index_from_archive(str(item.get("archive", "")))
        if index is None:
            continue

        texture_refs = [str(ref) for ref in item.get("texture_refs", [])]
        mesh_refs = [str(ref) for ref in item.get("mesh_refs", [])]
        video_sequence_id, video = _goodie_video(index, video_by_sequence, video_by_relative)
        source_title = goodie_titles.get(index, "")
        content_kind = _goodie_source_type(index)

        rows.append(
            {
                "catalog_id": f"goodie:{index:03d}",
                "kind": "goodie",
                "index": index,
                "display_name": (
                    f"Goodie {index:03d} - {source_title}"
                    if source_title
                    else _goodie_title_from_ref(index, texture_refs, mesh_refs, video_sequence_id)
                ),
                "content_kind": content_kind,
                "source_title": source_title,
                "source_archive": Path(str(item.get("archive", ""))).name,
                "gdie_family": item.get("family", ""),
                "texture_refs": texture_refs,
                "mesh_refs": mesh_refs,
                "primary_texture_ref": texture_refs[0] if texture_refs else "",
                "primary_mesh_ref": mesh_refs[0] if mesh_refs else "",
                "video_sequence_id": video_sequence_id,
                "video_catalog_id": video.get("catalog_id", "") if video else "",
                "video_relative_path": video.get("relative_path", "") if video else "",
            }
        )

    if "33" in video_by_sequence:
        video = video_by_sequence["33"]
        rows.append(
            {
                "catalog_id": "goodie:232",
                "kind": "goodie",
                "index": 232,
                "display_name": "Goodie 232 - Cutscene 33",
                "content_kind": "Video",
                "source_title": "",
                "source_archive": "",
                "gdie_family": "video_only",
                "texture_refs": [],
                "mesh_refs": [],
                "primary_texture_ref": "",
                "primary_mesh_ref": "",
                "video_sequence_id": "33",
                "video_catalog_id": video.get("catalog_id", ""),
                "video_relative_path": video.get("relative_path", ""),
            }
        )

    return sorted(rows, key=lambda item: item["index"])


def build_summary(
    textures: list[dict[str, object]],
    loose_meshes: list[dict[str, object]],
    embedded_meshes: list[dict[str, object]],
    videos: list[dict[str, object]],
    language_rows: list[dict[str, object]],
    goodies: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "texture_catalog_entries": len(textures),
        "texture_entries_referenced_in_packed": sum(1 for item in textures if item["referenced_in_packed"]),
        "texture_entries_loose_only": sum(1 for item in textures if not item["referenced_in_packed"]),
        "texture_entries_with_multiple_source_variants": sum(1 for item in textures if item["source_aya_count"] > 1),
        "loose_mesh_catalog_entries": len(loose_meshes),
        "loose_mesh_entries_referenced_in_packed": sum(1 for item in loose_meshes if item["referenced_in_packed"]),
        "loose_mesh_entries_loose_only": sum(1 for item in loose_meshes if not item["referenced_in_packed"]),
        "embedded_mesh_catalog_entries": len(embedded_meshes),
        "video_catalog_entries": len(videos),
        "language_catalog_entries": len(language_rows),
        "goodie_catalog_entries": len(goodies),
        "total_catalog_entries": len(textures)
        + len(loose_meshes)
        + len(embedded_meshes)
        + len(videos)
        + len(language_rows)
        + len(goodies),
        "video_family_counts": dict(sorted(Counter(item["family"] for item in videos).items())),
        "goodie_family_counts": dict(sorted(Counter(item["content_kind"] for item in goodies).items())),
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument(
        "--bundle-root",
        type=Path,
        help="Single generated export root that contains every catalog export path",
    )
    ap.add_argument("--packed-manifest", type=Path, default=Path(".artifacts/aya-assets/packed-manifest.json"))
    ap.add_argument("--texture-manifest", type=Path, default=Path(".artifacts/asset-export/loose-textures/manifest.json"))
    ap.add_argument("--loose-mesh-manifest", type=Path, default=Path(".artifacts/asset-export/loose-meshes/manifest.json"))
    ap.add_argument("--embedded-mesh-manifest", type=Path, default=Path(".artifacts/asset-export/embedded-meshes/manifest.json"))
    ap.add_argument("--video-manifest", type=Path, default=Path(".artifacts/video-manifest/manifest.json"))
    ap.add_argument("--language-matrix", type=Path, default=Path(".artifacts/language-export/merged_matrix.json"))
    ap.add_argument("--out-dir", type=Path, default=Path(".artifacts/asset-catalog"))
    ap.add_argument("--self-test", action="store_true", help="Run built-in catalog assembly checks without private game assets")
    ap.add_argument(
        "--emit-consumer-contract-fixture",
        type=Path,
        help=argparse.SUPPRESS,
    )
    return ap.parse_args()


def validate_catalog_output_layout(bundle_root: Path, out_dir: Path) -> None:
    expected_catalog_dir = bundle_root / "asset_catalog"
    if out_dir != expected_catalog_dir:
        raise SystemExit("--out-dir must be the asset_catalog child directory of --bundle-root")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp)
        packed_manifest = {
            "text_texture_refs": [
                {"ref": "meshtex\\cloud.tga", "count": 2, "match_count": 1, "matches": ["001_res_PC.aya"]},
            ],
            "gdie_texture_refs": [
                {"ref": "goodie\\icon.tga", "count": 1, "match_count": 1, "matches": ["goodie_08_res_PC.aya"]},
            ],
            "reference_mesh_refs": [
                {"ref": "fighter", "count": 3, "match_count": 1, "matches": ["base_res_PC.aya"]},
            ],
            "gdie_mesh_refs": [
                {"ref": "reward", "count": 1, "match_count": 1, "matches": ["goodie_08_res_PC.aya"]},
            ],
            "gdie_families": [
                {
                    "archive": str(repo_root / "game" / "data" / "resources" / "goodie_08_res_PC.aya"),
                    "family": "texture_mesh",
                    "texture_refs": ["goodie\\icon.tga"],
                    "mesh_refs": ["reward"],
                }
            ],
        }
        texture_manifest = [
            {
                "input": str(repo_root / "textures" / "meshtex%cloud.tga.aya"),
                "output": str(repo_root / "exports" / "cloud.png"),
            },
        ]
        loose_mesh_manifest = [
            {
                "input": str(repo_root / "meshes" / "m_fighter.aya"),
                "output": str(repo_root / "exports" / "fighter.fbx"),
            },
        ]
        embedded_mesh_manifest = [
            {
                "input": str(repo_root / "embedded" / "001_res_PC.aya" / "body00.cmsbody"),
                "output": str(repo_root / "exports" / "body00.fbx"),
            },
        ]
        video_manifest = {
            "files": [
                {
                    "relative_path": "briefings/PC_100_exact.vid",
                    "family": "briefing",
                    "sequence_id": "100",
                    "size": 16,
                    "sha256": "0" * 64,
                    "magic": "BIKi",
                },
                {
                    "relative_path": "cutscenes/33.vid",
                    "family": "cutscene_numeric",
                    "sequence_id": "33",
                    "size": 32,
                    "sha256": "1" * 64,
                    "magic": "BIKi",
                },
            ]
        }
        language_matrix = {
            "rows": [
                {
                    "id": 1,
                    "hex": "0x0001",
                    "name": "Sample",
                    "languages": {
                        "en": {"text": "Hello", "audio": "sample.ogg"},
                        "fr": {"text": "", "audio": ""},
                    },
                },
                {
                    "id": 2,
                    "hex": "0x0002",
                    "name": "GOODIE_TEXT_9_TITLE",
                    "languages": {
                        "english": {"text": "Test Reward", "audio": ""},
                        "american": {"text": "Test Reward", "audio": ""},
                    },
                }
            ]
        }

        textures = build_texture_catalog(texture_manifest, packed_manifest, repo_root, repo_root)
        loose_meshes = build_loose_mesh_catalog(loose_mesh_manifest, packed_manifest, repo_root, repo_root)
        embedded_meshes = build_embedded_mesh_catalog(embedded_mesh_manifest, repo_root, repo_root)
        videos = build_video_catalog(video_manifest)
        language_rows = build_language_catalog(language_matrix)
        goodies = build_goodie_catalog(packed_manifest, videos, language_rows)
        summary = build_summary(textures, loose_meshes, embedded_meshes, videos, language_rows, goodies)

        assert summary["texture_catalog_entries"] == 1
        assert summary["texture_entries_referenced_in_packed"] == 1
        assert summary["loose_mesh_catalog_entries"] == 1
        assert summary["loose_mesh_entries_referenced_in_packed"] == 1
        assert summary["embedded_mesh_catalog_entries"] == 1
        assert summary["video_catalog_entries"] == 2
        assert summary["language_catalog_entries"] == 2
        assert summary["goodie_catalog_entries"] == 2
        assert summary["total_catalog_entries"] == 9
        assert summary["video_family_counts"] == {"briefing": 1, "cutscene_numeric": 1}
        assert summary["goodie_family_counts"] == {"Model": 1, "Video": 1}
        assert textures[0]["canonical_ref"] == "meshtex\\cloud.tga"
        assert textures[0]["export_png_paths"] == ["exports\\cloud.png"]
        assert loose_meshes[0]["canonical_ref"] == "fighter"
        assert loose_meshes[0]["export_fbx_paths"] == ["exports\\fighter.fbx"]
        assert embedded_meshes[0]["source_archive"] == "001_res_PC.aya"
        assert embedded_meshes[0]["export_fbx_path"] == "exports\\body00.fbx"
        assert language_rows[0]["text_present_count"] == 1
        assert language_rows[0]["audio_present_count"] == 1
        assert goodies[0]["index"] == 8
        assert goodies[0]["content_kind"] == "Model"
        assert goodies[0]["source_title"] == "Test Reward"
        assert goodies[0]["display_name"] == "Goodie 008 - Test Reward"
        assert goodies[1]["index"] == 232
        assert goodies[1]["video_sequence_id"] == "33"

        validate_catalog_output_layout(repo_root, repo_root / "asset_catalog")
        try:
            validate_catalog_output_layout(repo_root, repo_root)
            raise AssertionError("direct catalog output layout should be rejected")
        except SystemExit as exc:
            assert "asset_catalog child" in str(exc)

    print("export_asset_catalog self-test: PASS")
    return 0


def emit_consumer_contract_fixture(bundle_root: Path) -> int:
    """Emit a tiny producer-owned bundle for the AppCore contract regression."""

    bundle_root = bundle_root.resolve()
    export_path = bundle_root / "exports" / "producer_texture.png"
    catalog_path = bundle_root / "asset_catalog" / "catalog.json"
    png = bytes(
        [
            137, 80, 78, 71, 13, 10, 26, 10,
            0, 0, 0, 13, 73, 72, 68, 82,
            0, 0, 0, 1, 0, 0, 0, 1,
            8, 6, 0, 0, 0, 31, 21, 196,
            137, 0, 0, 0, 13, 73, 68, 65,
            84, 120, 156, 99, 248, 207, 192,
            240, 31, 0, 5, 0, 1, 255, 137,
            153, 61, 29, 0, 0, 0, 0, 73,
            69, 78, 68, 174, 66, 96, 130,
        ]
    )
    catalog = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "path_contract": CATALOG_PATH_CONTRACT,
        "summary": {
            "texture_catalog_entries": 1,
            "total_catalog_entries": 1,
        },
        "textures": [
            {
                "catalog_id": "texture:producer-contract",
                "canonical_ref": "textures\\producer_contract.tga",
                "export_png_paths": ["exports\\producer_texture.png"],
            }
        ],
        "loose_meshes": [],
        "embedded_meshes": [],
        "videos": [],
        "language_rows": [],
        "goodies": [],
    }
    with SecuredOutputRoot(bundle_root) as output:
        output.atomic_write_bytes(export_path, png)
        output.atomic_write_json(catalog_path, catalog)
    print(json.dumps({"catalog": str(catalog_path)}, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    if args.emit_consumer_contract_fixture is not None:
        return emit_consumer_contract_fixture(args.emit_consumer_contract_fixture)
    if args.self_test:
        return run_self_test()

    args.repo_root = args.repo_root.resolve()
    args.out_dir = args.out_dir.resolve()
    bundle_root = (
        args.bundle_root.resolve()
        if args.bundle_root is not None
        else (args.out_dir.parent if args.out_dir.name.lower() == "asset_catalog" else args.out_dir)
    )
    validate_catalog_output_layout(bundle_root, args.out_dir)

    input_paths = (
        args.packed_manifest.resolve(),
        args.texture_manifest.resolve(),
        args.loose_mesh_manifest.resolve(),
        args.embedded_mesh_manifest.resolve(),
        args.video_manifest.resolve(),
        args.language_matrix.resolve(),
    )
    missing_inputs = [path for path in input_paths if not path.is_file()]
    if missing_inputs:
        raise SystemExit(f"catalog input does not exist: {missing_inputs[0]}")

    with SecuredOutputRoot(args.out_dir, protected_sources=input_paths) as output:
        packed_manifest = read_json(input_paths[0])
        texture_manifest = read_json(input_paths[1])
        loose_mesh_manifest = read_json(input_paths[2])
        embedded_mesh_manifest = read_json(input_paths[3])
        video_manifest = read_json(input_paths[4])
        language_matrix = read_json(input_paths[5])

        textures = build_texture_catalog(texture_manifest, packed_manifest, args.repo_root, bundle_root)
        loose_meshes = build_loose_mesh_catalog(loose_mesh_manifest, packed_manifest, args.repo_root, bundle_root)
        embedded_meshes = build_embedded_mesh_catalog(embedded_mesh_manifest, args.repo_root, bundle_root)
        videos = build_video_catalog(video_manifest)
        language_rows = build_language_catalog(language_matrix)
        goodies = build_goodie_catalog(packed_manifest, videos, language_rows)
        summary = build_summary(textures, loose_meshes, embedded_meshes, videos, language_rows, goodies)

        catalog = {
            "schema_version": CATALOG_SCHEMA_VERSION,
            "path_contract": CATALOG_PATH_CONTRACT,
            "summary": summary,
            "textures": textures,
            "loose_meshes": loose_meshes,
            "embedded_meshes": embedded_meshes,
            "videos": videos,
            "language_rows": language_rows,
            "goodies": goodies,
        }

        output.atomic_write_json(args.out_dir / "summary.json", summary)
        output.atomic_write_json(args.out_dir / "catalog.json", catalog)
        output.atomic_write_json(args.out_dir / "textures.json", textures)
        output.atomic_write_json(args.out_dir / "loose_meshes.json", loose_meshes)
        output.atomic_write_json(args.out_dir / "embedded_meshes.json", embedded_meshes)
        output.atomic_write_json(args.out_dir / "videos.json", videos)
        output.atomic_write_json(args.out_dir / "language_rows.json", language_rows)
        output.atomic_write_json(args.out_dir / "goodies.json", goodies)

    print(json.dumps({"out_dir": str(args.out_dir), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
