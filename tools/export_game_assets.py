#!/usr/bin/env python3
"""
Run the full local Battle Engine Aquila asset-extraction backend.

This orchestrates the existing private extraction lanes:
- packed AYA inventory + embedded-body preparation
- headless texture/mesh export harness, one lane per process
- language DAT export
- loose video manifest
- cross-surface asset catalog

Example:
    py -3 tools/export_game_assets.py --game-root game
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path


def default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def pick_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def render_cmd(cmd: list[str]) -> str:
    return subprocess.list2cmdline([str(part) for part in cmd])


def require_existing(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f"{description} does not exist: {path}")


def run_step(cmd: list[str], *, cwd: Path, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"$ {render_cmd(cmd)}")
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        process = subprocess.run(
            [str(part) for part in cmd],
            cwd=str(cwd),
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    if process.returncode != 0:
        tail = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
        print("\n".join(tail), file=sys.stderr)
        raise SystemExit(f"step failed with exit code {process.returncode}: {log_path}")
    print(f"[OK] {log_path}")


def build_harness_cmd(args: argparse.Namespace, repo_root: Path, resources_root: Path, embedded_root: Path, asset_export_root: Path, command: str) -> list[str]:
    cmd = [
        args.dotnet_exe,
        "run",
        "--project",
        str(repo_root / "tools" / "BeaAssetExportHarness" / "BeaAssetExportHarness.csproj"),
        "--",
        command,
        "--repo-root",
        str(repo_root),
        "--resources-root",
        str(resources_root),
        "--extractor-runtime-dir",
        str(args.extractor_runtime_dir),
        "--extractor-root",
        str(args.extractor_root),
        "--embedded-root",
        str(embedded_root),
        "--out-dir",
        str(asset_export_root),
        "--progress-every",
        str(args.progress_every),
    ]
    if command == "export-textures" and args.limit_loose_textures is not None:
        cmd.extend(["--limit-loose-textures", str(args.limit_loose_textures)])
    if command == "export-loose-meshes" and args.limit_loose_meshes is not None:
        cmd.extend(["--limit-loose-meshes", str(args.limit_loose_meshes)])
    if command == "export-embedded-meshes" and args.limit_embedded_bodies is not None:
        cmd.extend(["--limit-embedded-bodies", str(args.limit_embedded_bodies)])
    if args.skip_existing:
        cmd.append("--skip-existing")
    return cmd


def lane_result_from_manifest(asset_export_root: Path, lane: str) -> dict[str, object]:
    manifest_path = asset_export_root / lane / "manifest.json"
    rows = read_json(manifest_path)
    if not isinstance(rows, list):
        raise SystemExit(f"unexpected manifest shape: {manifest_path}")
    succeeded = sum(1 for row in rows if isinstance(row, dict) and row.get("status") in ("ok", "skipped_existing"))
    failed = sum(1 for row in rows if isinstance(row, dict) and row.get("status") == "error")
    return {
        "Lane": lane,
        "Attempted": len(rows),
        "Succeeded": succeeded,
        "Failed": failed,
        "ManifestPath": str(manifest_path),
    }


def write_asset_export_summary(asset_export_root: Path) -> dict[str, object]:
    summary = {
        "command": "export-all",
        "out_dir": str(asset_export_root),
        "process_model": "separate_process_per_lane",
        "results": [
            lane_result_from_manifest(asset_export_root, "loose_textures"),
            lane_result_from_manifest(asset_export_root, "loose_meshes"),
            lane_result_from_manifest(asset_export_root, "embedded_meshes"),
        ],
    }
    write_json(asset_export_root / "summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    repo_root = default_repo_root()
    game_root = repo_root / "game"
    default_out = repo_root / "subagents" / f"asset_backend_wave1_{date.today().isoformat()}"

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=repo_root)
    ap.add_argument("--game-root", type=Path, default=game_root)
    ap.add_argument("--out-root", type=Path, default=default_out)
    ap.add_argument("--python-exe", default=sys.executable)
    ap.add_argument("--dotnet-exe", default=os.environ.get("DOTNET_EXE", "dotnet"))
    ap.add_argument(
        "--extractor-runtime-dir",
        type=Path,
        default=repo_root / "references" / "AYAResourceExtractor" / "Code" / "AyaResourceExtractor" / "bin" / "Debug" / "net6.0-windows",
    )
    ap.add_argument(
        "--extractor-root",
        type=Path,
        default=repo_root / "references" / "AYAResourceExtractor",
    )
    ap.add_argument("--archive-glob", default="*_res_PC.aya")
    ap.add_argument("--limit-archives", type=int, default=0)
    ap.add_argument("--limit-loose-textures", type=int)
    ap.add_argument("--limit-loose-meshes", type=int)
    ap.add_argument("--limit-embedded-bodies", type=int)
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--progress-every", type=int, default=25)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    game_root = args.game_root.resolve()
    out_root = args.out_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    data_root = game_root / "data"
    resources_root = pick_existing(data_root / "resources")
    language_dir = pick_existing(data_root / "LANGUAGE", data_root / "language")
    video_root = pick_existing(data_root / "video")
    stf_path = pick_existing(data_root / "MissionScripts" / "text" / "text.stf")

    require_existing(repo_root / "tools" / "aya_archive_inventory.py", "aya archive inventory tool")
    require_existing(repo_root / "tools" / "export_language_corpus.py", "language export tool")
    require_existing(repo_root / "tools" / "export_video_manifest.py", "video manifest tool")
    require_existing(repo_root / "tools" / "export_asset_catalog.py", "asset catalog tool")
    require_existing(repo_root / "tools" / "BeaAssetExportHarness" / "BeaAssetExportHarness.csproj", "asset export harness project")
    require_existing(game_root, "game root")
    require_existing(resources_root, "resources root")
    require_existing(language_dir, "language dir")
    require_existing(video_root, "video root")
    require_existing(stf_path, "text.stf")
    require_existing(args.extractor_root, "AYAResourceExtractor root")
    require_existing(args.extractor_runtime_dir / "AYAResourceExtractor.dll", "AYAResourceExtractor runtime dll")
    require_existing(args.extractor_runtime_dir / "DDSTextureUncompress.dll", "DDSTextureUncompress runtime dll")

    logs_dir = out_root / "logs"
    embedded_root = out_root / "aya_embedded_meshes"
    asset_manifest_path = out_root / "aya_asset_manifest.json"
    asset_export_root = out_root / "asset_export"
    language_out = out_root / "language_export"
    video_out = out_root / "video_manifest"
    catalog_out = out_root / "asset_catalog"

    inventory_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "aya_archive_inventory.py"),
        str(resources_root),
        "--glob",
        args.archive_glob,
        "--resolve-assets",
        "--resource-root",
        str(resources_root),
        "--dump-dir",
        str(embedded_root),
        "--dump-tag",
        "MESH",
        "--extract-embedded-mesh-bodies",
        "--asset-manifest-out",
        str(asset_manifest_path),
    ]
    if args.limit_archives > 0:
        inventory_cmd.extend(["--limit", str(args.limit_archives)])

    harness_steps = [
        ("02a_asset_export_textures.log", build_harness_cmd(args, repo_root, resources_root, embedded_root, asset_export_root, "export-textures")),
        ("02b_asset_export_loose_meshes.log", build_harness_cmd(args, repo_root, resources_root, embedded_root, asset_export_root, "export-loose-meshes")),
        ("02c_asset_export_embedded_meshes.log", build_harness_cmd(args, repo_root, resources_root, embedded_root, asset_export_root, "export-embedded-meshes")),
    ]

    language_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "export_language_corpus.py"),
        "--language-dir",
        str(language_dir),
        "--stf",
        str(stf_path),
        "--out-dir",
        str(language_out),
    ]

    video_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "export_video_manifest.py"),
        "--video-root",
        str(video_root),
        "--out-dir",
        str(video_out),
    ]

    catalog_cmd = [
        args.python_exe,
        str(repo_root / "tools" / "export_asset_catalog.py"),
        "--repo-root",
        str(repo_root),
        "--packed-manifest",
        str(asset_manifest_path),
        "--texture-manifest",
        str(asset_export_root / "loose_textures" / "manifest.json"),
        "--loose-mesh-manifest",
        str(asset_export_root / "loose_meshes" / "manifest.json"),
        "--embedded-mesh-manifest",
        str(asset_export_root / "embedded_meshes" / "manifest.json"),
        "--video-manifest",
        str(video_out / "manifest.json"),
        "--language-matrix",
        str(language_out / "merged_matrix.json"),
        "--out-dir",
        str(catalog_out),
    ]

    run_step(inventory_cmd, cwd=repo_root, log_path=logs_dir / "01_aya_inventory.log")
    for log_name, harness_cmd in harness_steps:
        run_step(harness_cmd, cwd=repo_root, log_path=logs_dir / log_name)
    run_step(language_cmd, cwd=repo_root, log_path=logs_dir / "03_language_export.log")
    run_step(video_cmd, cwd=repo_root, log_path=logs_dir / "04_video_manifest.log")
    run_step(catalog_cmd, cwd=repo_root, log_path=logs_dir / "05_asset_catalog.log")

    asset_manifest = read_json(asset_manifest_path)
    asset_export_summary = write_asset_export_summary(asset_export_root)
    language_summary = read_json(language_out / "summary.json")
    video_summary = read_json(video_out / "summary.json")
    catalog_summary = read_json(catalog_out / "summary.json")

    summary = {
        "status": "ok",
        "repo_root": str(repo_root),
        "game_root": str(game_root),
        "out_root": str(out_root),
        "notes": [
            "Backend-only extraction workflow intended for WinUI/tooling integration or public BYO-assets packaging.",
            "This pipeline does not ship any copyrighted assets; it operates against a local game install.",
        ],
        "paths": {
            "asset_manifest": str(asset_manifest_path),
            "embedded_root": str(embedded_root),
            "asset_export_root": str(asset_export_root),
            "language_out": str(language_out),
            "video_out": str(video_out),
            "catalog_out": str(catalog_out),
            "logs_dir": str(logs_dir),
        },
        "summaries": {
            "aya_asset_manifest": asset_manifest["summary"],
            "asset_export": asset_export_summary,
            "language_export": language_summary,
            "video_manifest": video_summary,
            "asset_catalog": catalog_summary,
        },
    }
    summary_path = out_root / "extraction_summary.json"
    write_json(summary_path, summary)
    print(json.dumps(summary, indent=2))
    print(f"[OK] wrote backend summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
