#!/usr/bin/env python3
"""
Hash the canonical BEA retail specimen set used for runtime/provenance work.

This does not mutate any game data. It exists to pin the exact files that
future runtime probes and validation runs should target.

Example:
    py -3 tools/hash_retail_specimens.py
    py -3 tools/hash_retail_specimens.py --out reverse-engineering/binary-analysis/retail-specimen-manifest-2026-03-14.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_default_targets(repo_root: Path, steam_root: Path) -> list[dict[str, object]]:
    return [
        {
            "key": "installed_live_bea_exe",
            "kind": "executable",
            "label": "Installed live executable used by runtime sessions",
            "path": steam_root / "BEA.exe",
        },
        {
            "key": "clean_repo_bea_exe",
            "kind": "executable",
            "label": "Clean repo mirror of the retail Steam executable",
            "path": repo_root / "game" / "BEA.exe",
        },
        {
            "key": "repo_defaultoptions_bea",
            "kind": "options_snapshot",
            "label": "Repo mirror boot/global options snapshot",
            "path": repo_root / "game" / "defaultoptions.bea",
        },
        {
            "key": "gold_save_haha_cannon",
            "kind": "career_save",
            "label": "Gold save baseline used by app/manual regression work",
            "path": repo_root / "save-attempts" / "haha-cannon-goes-brrrrr.bes",
        },
        {
            "key": "base_res_pc_aya",
            "kind": "resource_archive",
            "label": "Core base packed resource archive",
            "path": repo_root / "game" / "data" / "resources" / "base_res_PC.aya",
        },
        {
            "key": "level_852_res_pc_aya",
            "kind": "resource_archive",
            "label": "Representative hidden/multiplayer-family packed resource archive",
            "path": repo_root / "game" / "data" / "resources" / "852_res_PC.aya",
        },
        {
            "key": "mesh_m_be_trans_aya",
            "kind": "loose_mesh_payload",
            "label": "Representative loose mesh payload",
            "path": repo_root / "game" / "data" / "resources" / "meshes" / "m_be_trans.msh.aya",
        },
        {
            "key": "english_dat",
            "kind": "language_dat",
            "label": "Representative localization table",
            "path": repo_root / "game" / "data" / "LANGUAGE" / "english.dat",
        },
        {
            "key": "video_01_vid",
            "kind": "video",
            "label": "Representative Bink cutscene payload",
            "path": repo_root / "game" / "data" / "video" / "cutscenes" / "01.vid",
        },
    ]


def materialize_targets(targets: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in targets:
        path = Path(target["path"])
        exists = path.exists()
        row = {
            "key": target["key"],
            "kind": target["kind"],
            "label": target["label"],
            "path": str(path),
            "exists": exists,
        }
        if exists:
            row["size"] = path.stat().st_size
            row["sha256"] = sha256_path(path)
        rows.append(row)
    return rows


def build_summary(rows: list[dict[str, object]], repo_root: Path, steam_root: Path) -> dict[str, object]:
    by_key = {row["key"]: row for row in rows}
    steam = by_key.get("installed_live_bea_exe")
    repo = by_key.get("clean_repo_bea_exe")
    hashes_match = (
        bool(steam and repo)
        and steam.get("exists")
        and repo.get("exists")
        and steam.get("sha256") == repo.get("sha256")
    )
    return {
        "repo_root": str(repo_root),
        "steam_root": str(steam_root),
        "target_count": len(rows),
        "existing_target_count": sum(1 for row in rows if row["exists"]),
        "missing_targets": [row["key"] for row in rows if not row["exists"]],
        "installed_live_exe_matches_clean_repo": hashes_match,
    }


def parse_args() -> argparse.Namespace:
    repo_root = default_repo_root()
    steam_root = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=repo_root)
    ap.add_argument("--steam-root", type=Path, default=steam_root)
    ap.add_argument(
        "--out",
        type=Path,
        default=repo_root / "reverse-engineering" / "binary-analysis" / "retail-specimen-manifest-2026-03-14.json",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    rows = materialize_targets(build_default_targets(args.repo_root, args.steam_root))
    payload = {
        "summary": build_summary(rows, args.repo_root, args.steam_root),
        "targets": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
