#!/usr/bin/env python3
"""Materialize a curated public-candidate tree from the manifest-derived allowlist."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "release" / "readiness" / "public_candidate_allowlist.tsv"
DEFAULT_DEST = ROOT.parent / ROOT.name.replace("-private", "-public-candidate")
PUBLIC_PACKAGE_SOURCE = "release/readiness/public_package.json"
PUBLIC_AGENTS_SOURCE = "release/readiness/public_AGENTS.md"
PUBLIC_GITIGNORE_SOURCE = "release/readiness/public_gitignore.txt"
MATERIALIZED_FILES = {
    "release/readiness/public_CURRENT_CAPABILITIES.txt": "CURRENT_CAPABILITIES.md",
    PUBLIC_PACKAGE_SOURCE: "package.json",
    PUBLIC_AGENTS_SOURCE: "AGENTS.md",
    PUBLIC_GITIGNORE_SOURCE: ".gitignore",
    "release/readiness/public_RE_INDEX.txt": "reverse-engineering/RE-INDEX.md",
    "release/readiness/public_quick_reference_index.txt": "reverse-engineering/quick-reference/_index.md",
    "release/readiness/public_ROADMAP_INDEX.txt": "roadmap/ROADMAP-INDEX.md",
    "release/readiness/public_winui_ui_ux_redesign_radar.txt": "roadmap/winui-ui-ux-redesign-radar.md",
    "release/readiness/public_mod_patch_runtime_rebuild_register.txt": "roadmap/mod-patch-runtime-rebuild-register.md",
    "release/readiness/public_lore_book_mod_patch_runtime_rebuild_register.txt": "lore-book/roadmap/mod-patch-runtime-rebuild-register.md",
    "release/readiness/public_lore_index.txt": "lore/_index.md",
    "release/readiness/public_lore_book_BOOK.txt": "lore-book/BOOK.md",
    "release/readiness/public_lore_book_Start-Here.txt": "lore-book/Start-Here.md",
    "release/readiness/public_lore_book_lore_index.txt": "lore-book/lore/_index.md",
    "release/readiness/public_msl_scripting.txt": "reverse-engineering/game-assets/msl-scripting.md",
}
EXPORT_MARKER = ".onslaught-public-candidate-export"
EXPORT_MARKER_TEXT = "onslaught-public-candidate-export.v1"
GENERATED_EXPORT_FILES = {"EXPORT_PROVENANCE.json", EXPORT_MARKER}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_clean_source_tree() -> None:
    dirty = source_tree_dirty_lines()
    if dirty:
        preview = "\n".join(f"  {line}" for line in dirty[:30])
        raise RuntimeError(
            "refusing to export public candidate from a dirty source tree.\n"
            "Commit, stash, or intentionally clear these changes first:\n"
            f"{preview}"
        )


def source_tree_dirty_lines() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def source_tree_status() -> str:
    return "dirty" if source_tree_dirty_lines() else "clean"


def run_allowlist_check() -> None:
    cmd = [sys.executable, str(ROOT / "tools" / "release_curated_manifest.py"), "--check"]
    subprocess.run(cmd, cwd=ROOT, check=True)
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "public_allowlist_safety_check.py"),
        "--self-test",
        "--require-private-text-guard",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "public_allowlist_safety_check.py"),
        "--require-private-text-guard",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def load_allowlist(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"missing allowlist: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)

    if not rows:
        raise ValueError("allowlist is empty")

    files: list[str] = []
    for row in rows:
        rel = (row.get("path") or "").strip()
        cls = (row.get("class") or "").strip()
        if not rel:
            raise ValueError("allowlist row missing path")
        if cls != "R0_ALLOW":
            raise ValueError(f"non-R0 path present in curated allowlist: {rel} => {cls}")
        files.append(rel)
    return files


def ensure_safe_dest(dest: Path, force_clean: bool) -> None:
    dest_resolved = dest.resolve()
    root_resolved = ROOT.resolve()
    if dest_resolved == root_resolved:
        raise ValueError("destination cannot be the repository root")
    if root_resolved in dest_resolved.parents:
        raise ValueError("destination cannot be inside the repository root; export to a sibling directory.")
    if not is_approved_export_dest(dest_resolved):
        raise ValueError(
            f"destination must be a sibling public-candidate directory named {DEFAULT_DEST.name} "
            f"or {DEFAULT_DEST.name}-<suffix>: {dest_resolved}"
        )
    if dest.exists():
        if not force_clean:
            raise FileExistsError(
                f"destination already exists: {dest}. Use --force-clean to replace it."
            )
        if not is_marked_previous_export(dest):
            raise ValueError(
                f"refusing --force-clean for unmarked destination: {dest}. "
                f"Only prior public-candidate exports with {EXPORT_MARKER} or EXPORT_PROVENANCE.json are replaced."
            )
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)


def is_approved_export_dest(dest: Path) -> bool:
    default_name = DEFAULT_DEST.name
    name = dest.name
    return dest.parent.resolve() == ROOT.parent.resolve() and (
        name == default_name or name.startswith(f"{default_name}-")
    )


def is_marked_previous_export(dest: Path) -> bool:
    marker = dest / EXPORT_MARKER
    if marker.is_file() and marker.read_text(encoding="utf-8", errors="replace").strip() == EXPORT_MARKER_TEXT:
        return True
    provenance = dest / "EXPORT_PROVENANCE.json"
    if not provenance.is_file():
        return False
    try:
        payload = json.loads(provenance.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return False
    return payload.get("schemaVersion") == "onslaught-public-export-provenance.v1"


def export_tree(files: list[str], dest: Path) -> None:
    copied = 0
    for rel in files:
        src = ROOT / rel
        if not src.is_file():
            raise FileNotFoundError(f"allowlist file missing from source tree: {rel}")
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        copied += 1

    for source_rel, materialized_rel in MATERIALIZED_FILES.items():
        src = ROOT / source_rel
        if not src.is_file():
            raise FileNotFoundError(f"materialized public source missing: {source_rel}")
        out = dest / materialized_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
    write_export_marker(dest)
    write_export_provenance(files, dest)
    print(f"Exported {copied} files to {dest}")


def write_export_marker(dest: Path) -> None:
    (dest / EXPORT_MARKER).write_text(EXPORT_MARKER_TEXT + "\n", encoding="utf-8", newline="\n")


def write_export_provenance(files: list[str], dest: Path) -> None:
    payload = {
        "schemaVersion": "onslaught-public-export-provenance.v1",
        "sourceCommit": git_output("rev-parse", "HEAD"),
        "exportedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exportCommandTemplate": "py -3 tools/export_curated_release_tree.py --dest <public-candidate-dir> --force-clean",
        "sourceTreeStatus": source_tree_status(),
        "allowlistFile": "release/readiness/public_candidate_allowlist.tsv",
        "allowlistSha256": sha256_file(ALLOWLIST),
        "exportScriptSha256": sha256_file(ROOT / "tools" / "export_curated_release_tree.py"),
        "publicPayloadFileCount": len(files),
        "materializedPublicFileCount": len(MATERIALIZED_FILES),
        "generatedFileCount": len(GENERATED_EXPORT_FILES),
        "finalInventoryRequirement": "Run npm run test:public-candidate-inventory on a fresh export before install/build/test output is created.",
    }
    out = dest / "EXPORT_PROVENANCE.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def refresh_exported_release_artifacts(dest: Path) -> None:
    print("Skipped exported-tree private release accounting refresh; source repo gates own it.")


def iter_exported_files(dest: Path) -> set[str]:
    return {
        path.relative_to(dest).as_posix()
        for path in dest.rglob("*")
        if path.is_file()
    }


def cleanup_transient_check_artifacts(dest: Path) -> None:
    removed = 0
    for path in sorted(dest.rglob("__pycache__"), reverse=True):
        if path.is_dir():
            shutil.rmtree(path)
            removed += 1
    if removed:
        print(f"Removed {removed} transient Python cache director{'y' if removed == 1 else 'ies'} from exported tree")


def validate_exported_inventory(files: list[str], dest: Path) -> None:
    expected = set(files) | set(MATERIALIZED_FILES.values()) | GENERATED_EXPORT_FILES
    actual = iter_exported_files(dest)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    errors: list[str] = []
    if missing:
        errors.append("missing exported files: " + ", ".join(missing[:25]))
    if extra:
        errors.append("unexpected exported files: " + ", ".join(extra[:25]))
    for source_rel, root_rel in MATERIALIZED_FILES.items():
        source = dest / source_rel
        if not source.is_file():
            source = ROOT / source_rel
        root_file = dest / root_rel
        if source.is_file() and root_file.is_file() and source.read_bytes() != root_file.read_bytes():
            errors.append(f"materialized root file differs from source: {root_rel} != {source_rel}")
    if errors:
        raise ValueError("; ".join(errors))
    print(f"Exported-tree inventory check: PASS ({len(actual)} files)")


def run_exported_tree_checks(files: list[str], dest: Path) -> None:
    validate_exported_inventory(files, dest)
    commands = [
        [
            sys.executable,
            str(ROOT / "tools" / "public_allowlist_safety_check.py"),
            "--payload-root",
            str(dest),
            "--require-private-text-guard",
        ],
        [
            sys.executable,
            str(ROOT / "tools" / "public_candidate_inventory_check.py"),
            "--candidate-root",
            str(dest),
        ],
        [sys.executable, str(dest / "tools" / "public_allowlist_safety_check.py"), "--self-test"],
        [sys.executable, str(dest / "tools" / "public_allowlist_safety_check.py")],
        [sys.executable, str(dest / "tools" / "md_link_check.py"), "--scope", "all", "--check-only"],
    ]
    for cmd in commands:
        subprocess.run(cmd, cwd=dest, check=True)
    cleanup_transient_check_artifacts(dest)
    validate_exported_inventory(files, dest)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export the curated public-candidate tree from the manifest-derived allowlist."
    )
    parser.add_argument(
        "--dest",
        default=str(DEFAULT_DEST),
        help="Destination directory for the exported public-candidate tree.",
    )
    parser.add_argument(
        "--force-clean",
        action="store_true",
        help="Remove the destination first if it already exists.",
    )
    args = parser.parse_args()

    dest = Path(args.dest).resolve()
    ensure_clean_source_tree()
    run_allowlist_check()
    files = load_allowlist(ALLOWLIST)
    ensure_safe_dest(dest, args.force_clean)
    export_tree(files, dest)
    refresh_exported_release_artifacts(dest)
    run_exported_tree_checks(files, dest)
    print("Validated exported-tree inventory and public safety checks.")
    print("Next step: run the sign-off commands from the exported tree to verify it stands on its own.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
