#!/usr/bin/env python3
"""Build and validate curated public-candidate allowlist from manifest patterns."""

from __future__ import annotations

import argparse
import difflib
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True

from release_profile_snapshot import ALLOW_EXACT, Classification, classify_path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "release" / "readiness" / "curated_release_manifest.json"
OUT_ALLOWLIST = ROOT / "release" / "readiness" / "public_candidate_allowlist.tsv"
MATERIALIZED_PUBLIC_SOURCES = {
    "CURRENT_CAPABILITIES.md": "release/readiness/public_CURRENT_CAPABILITIES.txt",
    "lore-book/BOOK.md": "release/readiness/public_lore_book_BOOK.txt",
    "lore-book/Start-Here.md": "release/readiness/public_lore_book_Start-Here.txt",
    "lore-book/lore/_index.md": "release/readiness/public_lore_book_lore_index.txt",
    "lore/_index.md": "release/readiness/public_lore_index.txt",
    "reverse-engineering/RE-INDEX.md": "release/readiness/public_RE_INDEX.txt",
    "reverse-engineering/game-assets/msl-scripting.md": "release/readiness/public_msl_scripting.txt",
    "reverse-engineering/quick-reference/_index.md": "release/readiness/public_quick_reference_index.txt",
    "roadmap/ROADMAP-INDEX.md": "release/readiness/public_ROADMAP_INDEX.txt",
    "roadmap/winui-ui-ux-redesign-radar.md": "release/readiness/public_winui_ui_ux_redesign_radar.txt",
    "roadmap/mod-patch-runtime-rebuild-register.md": "release/readiness/public_mod_patch_runtime_rebuild_register.txt",
    "lore-book/roadmap/mod-patch-runtime-rebuild-register.md": "release/readiness/public_lore_book_mod_patch_runtime_rebuild_register.txt",
}
IGNORED_PARTS = {
    ".git",
    ".vs",
    "__pycache__",
    "bin",
    "obj",
    "TestResults",
    "AppPackages",
    "BundleArtifacts",
    "MsixPackages",
    "publish",
}


def root_has_own_git_index(root: Path) -> bool:
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return False
    return Path(top).resolve() == root.resolve()


def get_tracked_files(root: Path) -> list[str]:
    if not root_has_own_git_index(root):
        raise RuntimeError(
            "curated manifest generation requires a source tree with its own git index; "
            "refusing filesystem fallback for tracked-only release accounting"
        )
    out = subprocess.check_output(["git", "ls-files"], cwd=root, text=True, stderr=subprocess.DEVNULL)
    files = [line.strip() for line in out.splitlines() if line.strip()]
    return sorted(set(files))


def path_matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def select_manifest_files(files: list[str], include_patterns: Iterable[str], exclude_patterns: Iterable[str]) -> list[str]:
    return [
        p
        for p in files
        if (path_matches(p, include_patterns) or p in ALLOW_EXACT)
        and (p in ALLOW_EXACT or not path_matches(p, exclude_patterns))
    ]


def load_manifest(path: Path) -> tuple[list[str], list[str], bool]:
    data = json.loads(path.read_text(encoding="utf-8"))
    include = [str(x) for x in data.get("include", [])]
    exclude = [str(x) for x in data.get("exclude", [])]
    tracked_only = bool(data.get("tracked_only", True))
    if not include:
        raise ValueError("Manifest include list is empty")
    return include, exclude, tracked_only


def render_allowlist(rows: list[tuple[str, Classification]]) -> str:
    lines = ["path\tclass\treason\trelease_posture\n"]
    for file_path, cls in rows:
        posture = "allow_with_normal_review" if cls.cls == "R0_ALLOW" else "exclude_or_review"
        lines.append(f"{file_path}\t{cls.cls}\t{cls.reason}\t{posture}\n")
    return "".join(lines)


def filter_public_rows(
    rows: list[tuple[str, Classification]],
) -> tuple[list[tuple[str, Classification]], list[tuple[str, Classification]]]:
    public_rows = [(path, cls) for path, cls in rows if cls.cls == "R0_ALLOW"]
    excluded_rows = [(path, cls) for path, cls in rows if cls.cls != "R0_ALLOW"]
    return public_rows, excluded_rows


def with_materialized_public_rows(
    public_rows: list[tuple[str, Classification]],
) -> tuple[list[tuple[str, Classification]], int]:
    row_paths = {path for path, _cls in public_rows}
    added = 0
    for target_path, source_path in MATERIALIZED_PUBLIC_SOURCES.items():
        if target_path in row_paths:
            continue
        if source_path not in row_paths:
            continue
        public_rows.append(
            (
                target_path,
                Classification(
                    target_path,
                    "R0_ALLOW",
                    f"materialized-public-template:{source_path}",
                ),
            )
        )
        row_paths.add(target_path)
        added += 1
    public_rows.sort(key=lambda row: row[0])
    return public_rows, added


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n")


def print_preview_diff(expected: str, actual: str) -> None:
    diff = difflib.unified_diff(
        actual.splitlines(),
        expected.splitlines(),
        fromfile="current/public_candidate_allowlist.tsv",
        tofile="expected/from-curated-manifest",
        lineterm="",
    )
    for idx, line in enumerate(diff):
        if idx >= 80:
            print("... diff truncated ...")
            break
        print(line)


def write_allowlist(path: Path, rows: list[tuple[str, Classification]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_allowlist(rows), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate curated allowlist without changing files")
    args = parser.parse_args()

    include_patterns, exclude_patterns, tracked_only = load_manifest(MANIFEST_PATH)

    files = get_tracked_files(ROOT)
    if not tracked_only:
        try:
            if not root_has_own_git_index(ROOT):
                raise RuntimeError("nested tree or no local git index")
            extra = subprocess.check_output(
                ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
            )
            files = sorted(set(files + [line.strip() for line in extra.splitlines() if line.strip()]))
        except Exception:
            pass

    selected = select_manifest_files(files, include_patterns, exclude_patterns)

    selected_rows: list[tuple[str, Classification]] = []
    for p in selected:
        cls = classify_path(p)
        selected_rows.append((p, cls))
    public_rows, excluded_rows = filter_public_rows(selected_rows)
    public_rows, materialized_public_rows = with_materialized_public_rows(public_rows)
    payload_safety_excluded = [
        (p, cls) for p, cls in excluded_rows if cls.reason.startswith("public-payload-safety:")
    ]
    non_payload_non_r0 = [
        (p, cls) for p, cls in excluded_rows if not cls.reason.startswith("public-payload-safety:")
    ]

    print(f"Curated manifest: {MANIFEST_PATH}")
    print(f"Selected files: {len(selected_rows)}")
    if materialized_public_rows:
        print(f"Materialized public rows: {materialized_public_rows}")
    if payload_safety_excluded:
        print(f"Payload-safety exclusions: {len(payload_safety_excluded)}")
    print(f"Output: {OUT_ALLOWLIST}")

    if non_payload_non_r0:
        print("ERROR: Curated allowlist contains non-R0 paths:")
        for path, cls in non_payload_non_r0[:50]:
            print(f"  - {path} => {cls.cls}:{cls.reason}")
        if len(non_payload_non_r0) > 50:
            print(f"  ... and {len(non_payload_non_r0)-50} more")
        return 1

    if not public_rows:
        print("ERROR: Curated allowlist selected zero files")
        return 1

    expected = render_allowlist(public_rows)
    if args.check:
        if not OUT_ALLOWLIST.is_file():
            print(f"ERROR: Missing allowlist file for --check: {OUT_ALLOWLIST}")
            print("Run: python3 tools/release_curated_manifest.py")
            return 1
        current = OUT_ALLOWLIST.read_text(encoding="utf-8")
        if normalize_newlines(current) != normalize_newlines(expected):
            print("ERROR: public_candidate_allowlist.tsv is stale/out-of-sync with curated manifest.")
            print("Run: python3 tools/release_curated_manifest.py")
            print_preview_diff(expected, current)
            return 1
    else:
        write_allowlist(OUT_ALLOWLIST, public_rows)

    print("Curated allowlist check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
