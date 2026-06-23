#!/usr/bin/env python3
"""
BEA.exe Patch: Dev-Mode Goodies UI Logic Fix
===========================================
Fixes a dev-mode edge-case where `g_bAllCheatsEnabled` makes *all* cheat indices return TRUE,
including the goodies-only cheat at index 5 (`lat\xEAte`). When both `MALLOY` (index 0) and
`lat\xEAte` (index 5) are treated as active, the goodies UI gating logic can effectively hide
or block goodies actions.

This patch forces `g_Cheat_LATETE` to remain 0 in the goodies UI, so `g_bAllCheatsEnabled`
behaves like "MALLOY only" for the gallery.

NOTE: The MALLOY cheat works WITHOUT this patch when using a save name
containing "MALLOY". This patch is only needed for dev mode exploration.

This patch changes one instruction so the `g_Cheat_LATETE` flag is always written as 0.

Technical Details:
  Patch 1: VA 0x0045D819, File offset 0x5D819
    Before: F7 D8 (NEG EAX)
    After:  33 C0 (XOR EAX,EAX)

Effects (DEV MODE ONLY - normal save name cheats work without this patch):
  - Prevents `g_bAllCheatsEnabled` from activating the `lat\xEAte` goodies-only flag inside the gallery

Cheat Codes (enter as save game name):
  - MALLOY   : All goodies (index 0) - works WITHOUT patch
  - TURKEY   : All levels (index 1) - works WITHOUT patch
  - V3R5IOF  : Version display (index 2; no call sites found yet, needs in-game confirmation)
  - Maladim  : God mode menu toggle (index 3) - Steam build exposes God OFF/God ON
  - Aurore   : Free camera debug toggle (index 4)
  - lat\xEAte: Goodie UI override (index 5)

NOTE: MALLOY works WITHOUT this patch via save name. This patch is for dev mode
exploration of the g_bAllCheatsEnabled code path only.

Usage:
  python3 patch_devmode_goodies_logic_fix.py C:\\safe-copy\\BEA.exe --allowed-root C:\\safe-copy
  python3 patch_devmode_goodies_logic_fix.py C:\\safe-copy\\BEA.exe --allowed-root C:\\safe-copy --restore

Discovered via Ghidra RE analysis, December 2025
"""

import argparse
import hashlib
import json
import os
import sys
import shutil
from pathlib import Path

# Patch configuration
PATCHES = [
    {
        "name": "Disable g_Cheat_LATETE in goodies UI",
        "file_offset": 0x5D819,
        "original": bytes([0xF7, 0xD8]),  # NEG EAX
        "patched": bytes([0x33, 0xC0]),   # XOR EAX,EAX
    },
]
BACKUP_SUFFIX = ".exe.backup"
BACKUP_HASH_SUFFIX = ".sha256"
PROFILE_MANIFEST_NAME = "onslaught-profile-manifest.json"
PROFILE_SCHEMA_VERSION = "winui-copied-game-profile.v1"
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
REQUIRED_PROFILE_ENTRIES = {
    "BEA.exe",
    "data",
    "defaultoptions.bea",
    "binkw32.dll",
    "ogg.dll",
    "vorbis.dll",
    "zlib.dll",
}
SCRIPT_PATCH_KEY = "devmode_goodies_logic_fix"


def protected_roots() -> list[Path]:
    roots: list[Path] = []
    for key in ("ProgramFiles", "ProgramFiles(x86)"):
        raw = os.environ.get(key)
        if raw:
            roots.append(Path(raw).resolve())
    return roots


def has_known_installed_game_shape(path: Path) -> bool:
    parts = [part.lower() for part in path.resolve().parts]
    for index in range(0, len(parts) - 2):
        if (
            parts[index] == "steamapps"
            and parts[index + 1] == "common"
            and parts[index + 2] == "battle engine aquila"
        ):
            return True
    return False


def is_reparse_point(path: Path) -> bool:
    try:
        attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT) or path.is_symlink()


def reject_reparse_ancestors(path: Path, stop_root: Path) -> None:
    current = path if path.exists() else path.parent
    while True:
        if current.exists() and is_reparse_point(current):
            raise ValueError(f"refusing to mutate through a reparse point: {current}")
        if current == stop_root:
            return
        if current.parent == current:
            return
        current = current.parent


def reject_hardlinked_file(path: Path) -> None:
    link_count = getattr(os.stat(path), "st_nlink", 1)
    if link_count > 1:
        raise ValueError(f"refusing to mutate hardlinked target: {path}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_backup_hash(backup_path: Path) -> None:
    Path(str(backup_path) + BACKUP_HASH_SUFFIX).write_text(sha256_bytes(backup_path.read_bytes()), encoding="utf-8")


def validate_generated_profile_manifest(root: Path, exe_path: Path) -> None:
    manifest_path = root / PROFILE_MANIFEST_NAME
    if not manifest_path.is_file():
        raise ValueError(f"mutating modes require generated playable copied game manifest: {manifest_path}")

    reject_reparse_ancestors(manifest_path, root)
    if is_reparse_point(manifest_path):
        raise ValueError(f"refusing to trust reparse-point manifest: {manifest_path}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"generated playable copied game manifest is not valid JSON: {manifest_path}") from exc

    if manifest.get("schemaVersion") != PROFILE_SCHEMA_VERSION:
        raise ValueError("generated playable copied game manifest has an unsupported schema")
    if manifest.get("mutation") is not True:
        raise ValueError("generated playable copied game manifest must be a mutation=true profile")
    if not isinstance(manifest.get("generatedAt"), str) or not manifest["generatedAt"].strip():
        raise ValueError("generated playable copied game manifest is missing generatedAt")
    if manifest.get("targetGameRoot") != ".":
        raise ValueError("generated playable copied game manifest targetGameRoot must be '.'")

    manifest_exe = manifest.get("executablePath")
    if not isinstance(manifest_exe, str) or not manifest_exe.strip():
        raise ValueError("generated playable copied game manifest is missing executablePath")

    resolved_manifest_exe = (root / manifest_exe).resolve()
    if resolved_manifest_exe != exe_path:
        raise ValueError("generated playable copied game manifest executablePath does not match target BEA.exe")

    manifest_size = manifest.get("executableSize")
    if not isinstance(manifest_size, int) or manifest_size != exe_path.stat().st_size:
        raise ValueError("generated playable copied game manifest executableSize does not match target BEA.exe")

    manifest_hash = manifest.get("executableSha256")
    if not isinstance(manifest_hash, str) or manifest_hash.lower() != sha256_bytes(exe_path.read_bytes()).lower():
        raise ValueError("generated playable copied game manifest executableSha256 does not match target BEA.exe")

    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ValueError("generated playable copied game manifest is missing entries")
    entry_names = {entry.get("name") for entry in entries if isinstance(entry, dict)}
    missing_entries = sorted(REQUIRED_PROFILE_ENTRIES - entry_names)
    if missing_entries:
        raise ValueError(
            "generated playable copied game manifest is missing required copied entries: "
            + ", ".join(missing_entries)
        )

    patch_result = manifest.get("patchResult")
    if not isinstance(patch_result, dict) or patch_result.get("success") is not True:
        raise ValueError("generated playable copied game manifest does not record a successful patch state")
    patch_keys = patch_result.get("patchKeys")
    if not isinstance(patch_keys, list) or not all(isinstance(key, str) for key in patch_keys):
        raise ValueError("generated playable copied game manifest is missing patchResult.patchKeys")
    if SCRIPT_PATCH_KEY not in patch_keys:
        raise ValueError(f"generated playable copied game manifest does not list {SCRIPT_PATCH_KEY}")


def validate_backup_snapshot(backup_path: Path) -> None:
    hash_path = Path(str(backup_path) + BACKUP_HASH_SUFFIX)
    if not hash_path.is_file():
        raise ValueError("backup hash sidecar is missing; refusing to trust backup snapshot")

    backup_bytes = backup_path.read_bytes()
    expected_hash = hash_path.read_text(encoding="utf-8").strip()
    actual_hash = sha256_bytes(backup_bytes)
    if expected_hash.lower() != actual_hash.lower():
        raise ValueError("backup hash sidecar does not match backup snapshot")

    for patch in PATCHES:
        offset = patch["file_offset"]
        current = bytes(backup_bytes[offset:offset + len(patch["original"])])
        if current != patch["original"]:
            raise ValueError(f"backup snapshot does not contain original bytes for {patch['name']}")


def ensure_safe_target(exe_path: Path, allowed_root: Path | None, mutating: bool) -> Path:
    if mutating and allowed_root is None:
        raise ValueError("mutating modes require --allowed-root pointing at an app-owned copied-target workspace")

    resolved = exe_path.resolve(strict=True)
    if resolved.name.lower() != "bea.exe":
        raise ValueError(f"target must be BEA.exe, got: {resolved.name}")
    if not resolved.exists():
        raise FileNotFoundError(resolved)

    for root in protected_roots():
        try:
            resolved.relative_to(root)
        except ValueError:
            continue
        raise ValueError(
            "refusing to patch an executable under Program Files; "
            "prepare a safe copied game folder or app-owned artifact root first"
        )
    if has_known_installed_game_shape(resolved):
        raise ValueError(
            "refusing to patch an executable under a steamapps/common/Battle Engine Aquila install root; "
            "prepare a playable copied game folder or app-owned artifact root first"
        )

    if mutating:
        assert allowed_root is not None
        root = allowed_root.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError("mutating modes require target BEA.exe to be under --allowed-root") from exc
        for protected in protected_roots():
            try:
                root.relative_to(protected)
            except ValueError:
                continue
            raise ValueError("refusing to use a Program Files directory as --allowed-root")
        if has_known_installed_game_shape(root):
            raise ValueError("refusing to use a steamapps/common/Battle Engine Aquila install root as --allowed-root")
        backup_path = resolved.with_suffix(BACKUP_SUFFIX).resolve()
        try:
            backup_path.relative_to(root)
        except ValueError as exc:
            raise ValueError("backup path must stay under --allowed-root") from exc
        reject_reparse_ancestors(root, root)
        reject_reparse_ancestors(resolved, root)
        if is_reparse_point(resolved):
            raise ValueError(f"refusing to mutate reparse-point target: {resolved}")
        reject_hardlinked_file(resolved)
        if backup_path.exists():
            reject_reparse_ancestors(backup_path, root)
            if is_reparse_point(backup_path):
                raise ValueError(f"refusing to trust reparse-point backup: {backup_path}")
            reject_hardlinked_file(backup_path)
        validate_generated_profile_manifest(root, resolved)

    return resolved


def apply_patch(exe_path: Path) -> bool:
    """Apply the goodies logic fix patches to BEA.exe."""
    backup_path = exe_path.with_suffix('.exe.backup')

    print(f"Reading {exe_path}...")
    data = bytearray(exe_path.read_bytes())

    # Verify all patches first
    all_ok = True
    for patch in PATCHES:
        offset = patch["file_offset"]
        current = bytes(data[offset:offset + len(patch["original"])])

        if current == patch["patched"]:
            print(f"  [{patch['name']}] Already patched")
        elif current == patch["original"]:
            print(f"  [{patch['name']}] Ready to patch at 0x{offset:X}")
        else:
            print(f"  [{patch['name']}] ERROR: Unexpected bytes at 0x{offset:X}")
            print(f"    Expected: {patch['original'].hex(' ')}")
            print(f"    Found:    {current.hex(' ')}")
            all_ok = False

    if not all_ok:
        print("\nAborting - unexpected bytes found. Wrong BEA.exe version?")
        return False

    # Check if already fully patched
    already_patched = all(
        bytes(data[p["file_offset"]:p["file_offset"] + len(p["original"])]) == p["patched"]
        for p in PATCHES
    )
    if already_patched:
        print("\n[OK] All patches already applied!")
        return True

    # Create backup
    if not backup_path.exists():
        print(f"\nCreating backup: {backup_path}")
        shutil.copy2(exe_path, backup_path)
        write_backup_hash(backup_path)
    else:
        validate_backup_snapshot(backup_path)
        print(f"\nBackup exists: {backup_path}")

    # Apply patches
    print("\nApplying patches...")
    for patch in PATCHES:
        offset = patch["file_offset"]
        current = bytes(data[offset:offset + len(patch["original"])])
        if current == patch["original"]:
            data[offset:offset + len(patch["patched"])] = patch["patched"]
            print(f"  [{patch['name']}] {patch['original'].hex(' ')} -> {patch['patched'].hex(' ')}")

    exe_path.write_bytes(data)
    read_back = exe_path.read_bytes()
    for patch in PATCHES:
        offset = patch["file_offset"]
        current = bytes(read_back[offset:offset + len(patch["patched"])])
        if current != patch["patched"]:
            print("\n[ERROR] On-disk patch verification did not match selected patched bytes.")
            return False

    print("\n" + "=" * 60)
    print("PATCH APPLIED SUCCESSFULLY!")
    print("=" * 60)
    print("\nDev-mode LATETE suppression patch applied.")
    print("\nTo test: use a copied executable in a dev-mode/all-cheats scenario and verify LATETE no longer forces the Goodies wall override.")
    print("         Ordinary MALLOY all-goodies behavior works without this patch and is not the thing this patch proves.")
    print("\nCheat codes (include in save name - work WITHOUT this patch):")
    print("  MALLOY  - All goodies")
    print("  TURKEY  - All levels")
    print("  Maladim - God mode menu toggle")

    return True


def restore_backup(exe_path: Path) -> bool:
    """Restore the original BEA.exe from backup."""
    backup_path = exe_path.with_suffix(BACKUP_SUFFIX)

    if not backup_path.exists():
        print(f"[ERROR] No backup found at {backup_path}")
        return False

    try:
        validate_backup_snapshot(backup_path)
    except ValueError as exc:
        print(f"[ERROR] Restore aborted: {exc}")
        return False

    print(f"Restoring {exe_path} from backup...")
    current = exe_path.read_bytes()
    has_patched_bytes = False
    for patch in PATCHES:
        offset = patch["file_offset"]
        current_patch_bytes = bytes(current[offset:offset + len(patch["patched"])])
        if current_patch_bytes == patch["patched"]:
            has_patched_bytes = True
        elif current_patch_bytes != patch["original"]:
            print("[ERROR] Restore aborted: current target does not contain verified known patched bytes.")
            return False
    if not has_patched_bytes and current == backup_path.read_bytes():
        print("No changes needed. Target already matches the verified backup snapshot.")
        return True
    shutil.copy2(backup_path, exe_path)
    if exe_path.read_bytes() != backup_path.read_bytes():
        print("[ERROR] Restore failed: on-disk verification did not match backup.")
        return False
    print("Restore complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Patch dev-mode goodies logic on a copied BEA.exe")
    parser.add_argument("path", type=Path, help="Target copied BEA.exe path")
    parser.add_argument("--allowed-root", type=Path, help="Required for apply/restore; app-owned root containing the copied target")
    parser.add_argument("--restore", action="store_true", help="Restore from sidecar backup")
    args = parser.parse_args()

    try:
        exe_path = ensure_safe_target(args.path, args.allowed_root, mutating=True)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if args.restore:
        success = restore_backup(exe_path)
    else:
        success = apply_patch(exe_path)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
