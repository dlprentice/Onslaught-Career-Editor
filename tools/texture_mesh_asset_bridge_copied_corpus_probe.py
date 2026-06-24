#!/usr/bin/env python3
"""Validate the texture/mesh copied-corpus inventory/export proof."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "texture_mesh_asset_bridge_proof_2026-06-08"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
PLAN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_asset_bridge_copied_corpus_proof_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

SUMMARY = BASE / "extraction_summary.json"
ARCHIVE_INVENTORY = BASE / "aya_archive_inventory.json"
PACKED_MANIFEST = BASE / "aya_asset_manifest.json"

RESULT_LINK = "texture-mesh-asset-bridge-copied-corpus-proof.md"
ABSOLUTE_USER_SENTINEL = "C:" + "\\Users" + "\\david"

FORBIDDEN_DOC_PHRASES = (
    "runtime texture pixels proven",
    "gpu upload parity proven",
    "visual qa complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "exact layouts proven",
    "asset bridge counts prove runtime render correctness",
    "godot is the active product lane",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path):
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def count_files_and_bytes(root: Path) -> tuple[int, int]:
    files = [path for path in root.rglob("*") if path.is_file()]
    return len(files), sum(path.stat().st_size for path in files)


def aggregate_tags(rows: list[dict]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for row in rows:
        for tag, count in row.get("tag_counts", {}).items():
            totals[tag] = totals.get(tag, 0) + int(count)
    return totals


def file_name(path_text: str) -> str:
    return path_text.replace("\\", "/").rsplit("/", 1)[-1]


def lane_rows(lane: str) -> list[dict]:
    return read_json(BASE / "asset_export" / lane / "manifest.json")


def lane_summary(summary: dict, lane: str) -> dict:
    for row in summary["summaries"]["asset_export"]["results"]:
        if row.get("Lane") == lane:
            return row
    raise KeyError(lane)


def check_artifacts(failures: list[str]) -> None:
    require(BASE.is_dir(), "missing ignored proof artifact root", failures)
    for path in (SUMMARY, ARCHIVE_INVENTORY, PACKED_MANIFEST):
        require(path.is_file(), f"missing artifact: {path.relative_to(ROOT)}", failures)

    summary = read_json(SUMMARY)
    archive_rows = read_json(ARCHIVE_INVENTORY)
    packed = read_json(PACKED_MANIFEST)
    file_count, total_bytes = count_files_and_bytes(BASE)
    tags = aggregate_tags(archive_rows)

    require(summary.get("status") == "ok", "extraction summary status mismatch", failures)
    require("Program Files" not in summary.get("game_root", ""), "proof used Program Files game root", failures)
    require(summary.get("out_root", "").endswith(r"subagents\texture_mesh_asset_bridge_proof_2026-06-08"), "out_root mismatch", failures)
    require(file_count == 8574, f"artifact file count mismatch: {file_count}", failures)
    require(total_bytes == 250335133, f"artifact byte count mismatch: {total_bytes}", failures)

    require(len(archive_rows) == 301, "archive inventory row count mismatch", failures)
    require(sum(1 for row in archive_rows if file_name(row["path"]).lower().startswith("goodie_")) == 232, "goodie archive count mismatch", failures)
    for key, expected in {
        "TEXT": 18857,
        "MESH": 3492,
        "GDIE": 232,
        "LVLR": 301,
        "TARG": 301,
        "AYAD": 301,
    }.items():
        require(tags.get(key) == expected, f"top-level tag count mismatch {key}: {tags.get(key)}", failures)
    require(all(len(row.get("compressed_sha256", "")) == 64 for row in archive_rows), "missing compressed hashes", failures)
    require(all(len(row.get("raw_sha256", "")) == 64 for row in archive_rows), "missing raw hashes", failures)

    packed_summary = packed["summary"]
    for key, expected in {
        "text_texture_refs": 601,
        "text_texture_refs_resolved": 601,
        "reference_mesh_refs": 209,
        "reference_mesh_refs_resolved": 209,
        "gdie_texture_refs": 206,
        "gdie_texture_refs_resolved": 206,
        "gdie_mesh_refs": 42,
        "gdie_mesh_refs_resolved": 42,
    }.items():
        require(packed_summary.get(key) == expected, f"packed summary mismatch {key}", failures)
    require(packed_summary.get("gdie_family_counts") == {"metadata_only": 38, "texture_mesh": 45, "texture_only": 149}, "GDIE family counts mismatch", failures)

    for lane, expected in {
        "loose_textures": 847,
        "loose_meshes": 213,
        "embedded_meshes": 139,
    }.items():
        lane_result = lane_summary(summary, lane)
        rows = lane_rows(lane)
        statuses = [row.get("status") for row in rows]
        require(lane_result.get("Attempted") == expected, f"{lane} attempted mismatch", failures)
        require(lane_result.get("Succeeded") == expected, f"{lane} succeeded mismatch", failures)
        require(lane_result.get("Failed") == 0, f"{lane} failed rows", failures)
        require(len(rows) == expected, f"{lane} manifest row count mismatch", failures)
        require(statuses.count("ok") == expected, f"{lane} non-ok statuses", failures)
        require(statuses.count("skipped_existing") == 0, f"{lane} skipped_existing rows", failures)
        require(statuses.count("error") == 0, f"{lane} error rows", failures)

    language = summary["summaries"]["language_export"]
    video = summary["summaries"]["video_manifest"]
    catalog = summary["summaries"]["asset_catalog"]
    require(language.get("language_count") == 6, "language count mismatch", failures)
    require(language.get("merged_row_count") == 2571, "language row mismatch", failures)
    require(video.get("file_count") == 66, "video file count mismatch", failures)
    require(video.get("total_bytes") == 353110648, "video byte count mismatch", failures)
    for key, expected in {
        "texture_catalog_entries": 828,
        "texture_entries_referenced_in_packed": 759,
        "texture_entries_loose_only": 69,
        "loose_mesh_catalog_entries": 213,
        "loose_mesh_entries_referenced_in_packed": 213,
        "loose_mesh_entries_loose_only": 0,
        "embedded_mesh_catalog_entries": 139,
        "video_catalog_entries": 66,
        "language_catalog_entries": 2571,
        "goodie_catalog_entries": 233,
        "total_catalog_entries": 4050,
    }.items():
        require(catalog.get(key) == expected, f"catalog mismatch {key}", failures)
    require(catalog.get("goodie_family_counts") == {"Artwork": 149, "Level": 5, "Model": 45, "Video": 34}, "goodie family counts mismatch", failures)


def check_docs(failures: list[str]) -> None:
    result = read_text(RESULT)
    require(read_text(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore plan mirror mismatch", failures)

    required_result_tokens = (
        "Status: copied-corpus inventory/export proof complete, not runtime proof",
        "not a new static re-audit wave",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        "Remaining active focused work remains `0`",
        "subagents/texture_mesh_asset_bridge_proof_2026-06-08/",
        "8574",
        "250335133",
        "TEXT 18857",
        "MESH 3492",
        "GDIE 232",
        "601/601",
        "209/209",
        "206/206",
        "42/42",
        "847",
        "213",
        "139",
        "4050",
        "copied-corpus inventory/export proof only",
        "texture-mesh-material-sidecar-ledger-proof.md",
        "Follow-up generated material/sidecar ledger proof",
        "0` catalog-missing refs",
    )
    for path in (RESULT, READINESS):
        text = read_text(path)
        for token in required_result_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        require(ABSOLUTE_USER_SENTINEL not in text, f"{path.relative_to(ROOT)} leaks absolute user path", failures)
        require("Program Files" not in text, f"{path.relative_to(ROOT)} leaks Program Files path", failures)
        for bad in FORBIDDEN_DOC_PHRASES:
            require(bad not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {bad}", failures)

    for path in (PLAN, BACKLOG, MAPPED, GAME_ASSETS_INDEX, RE_INDEX):
        text = read_text(path)
        require(RESULT_LINK in text, f"{path.relative_to(ROOT)} missing result link", failures)
        for bad in FORBIDDEN_DOC_PHRASES:
            require(bad not in text.lower(), f"{path.relative_to(ROOT)} overclaims: {bad}", failures)


def check_progress_unchanged(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk focused mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "current focused candidates mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1210, "legacy additive mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)


def check_package_and_git(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    expected = r"py -3 tools\texture_mesh_asset_bridge_copied_corpus_probe.py --check"
    actual = package["scripts"].get("test:texture-mesh-asset-bridge-copied-corpus")
    require(actual == expected, "missing package copied-corpus proof script", failures)

    gitignore = read_text(ROOT / ".gitignore")
    require("subagents/" in gitignore, "subagents root is not ignored", failures)
    require("game/" in gitignore, "game root is not ignored", failures)
    tracked = subprocess.run(
        ["git", "ls-files", "subagents/texture_mesh_asset_bridge_proof_2026-06-08"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(tracked.returncode == 0, "git ls-files check failed", failures)
    require(not tracked.stdout.strip(), "ignored proof artifacts are tracked", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_docs(failures)
    check_progress_unchanged(failures)
    check_package_and_git(failures)

    if failures:
        print("Texture/mesh asset bridge copied-corpus probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh asset bridge copied-corpus probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
