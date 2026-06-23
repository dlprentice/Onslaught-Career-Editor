#!/usr/bin/env python3
"""
BEA.exe Patch: Display Mode Flow (Resolution + Windowed)
=======================================================

This utility applies reversible, byte-verified patches across two tracks:

- Stable track: primary display/windowed behavior patches.
- Experimental track: optional startup-flow tweak for edge-case setups.

Stable patches:

1) Resolution gate bypass in mode enumeration
   - Allows non-4:3 mode candidates even when `g_AllowWidescreenModes` is false.
   - Source location: BuildDeviceList path near VA 0x00529696.
   - File offset: 0x129696
   - Patch: 0xCC -> 0x00

2) Force windowed startup (without relying on CLI `-forcewindowed`)
   - Forces the startup windowed decision to TRUE (when device supports windowed).
   - Source location: Initialize3DEnvironment path near VA 0x0052A644.
   - File offset: 0x12A644
   - Patch: A1 F0 2D 66 00 -> B8 01 00 00 00

3) Unlock extra graphics features by default
   - Changes the GEFORCE_FX_POWER tweak registration default from 0 to 1.
   - Source location near VA 0x004CDD40.
   - File offset: 0x0CDD40
   - Patch: 6A 00 -> 6A 01

4) Ignore cardid.txt vendor/device tweak overrides
   - Bypasses startup call into cardid parser/override application path.
   - Source location near VA 0x0052AF3F.
   - File offset: 0x12AF3F
   - Patch: E8 9C D7 FF FF -> 90 90 90 90 90

5) Version overlay pointer redirect
   - Redirects bottom-left version overlay format pointer to patched-format cave string.
   - Source location near VA 0x0046316F.
   - File offset: 0x06416F
   - Patch: 54 94 62 00 -> 44 A4 5A 00

6) Version overlay cave string payload
   - Installs format string: `V%1d.%02d - PATCHED`.
   - Source location near VA 0x005AA444.
   - File offset: 0x1AA444
   - Patch: 20xCC bytes -> ASCII payload bytes

Experimental optional patch:
7) Skip auto fullscreen toggle in startup/device-flow helper
   - Source location near VA 0x0052BB97.
   - File offset: 0x12BB97
   - Patch: 75 20 -> EB 20
   - This is intentionally optional because behavior can vary by environment.

Usage:
  python3 patches/patch_display_mode_flow.py --path "C:\\safe-copy\\BEA.exe" --verify
  python3 patches/patch_display_mode_flow.py --path "C:\\safe-copy\\BEA.exe" --allowed-root "C:\\safe-copy" --apply
  python3 patches/patch_display_mode_flow.py --path "C:\\safe-copy\\BEA.exe" --allowed-root "C:\\safe-copy" --apply --resolution-only
  python3 patches/patch_display_mode_flow.py --path "C:\\safe-copy\\BEA.exe" --allowed-root "C:\\safe-copy" --apply --windowed-only
  python3 patches/patch_display_mode_flow.py --path "C:\\safe-copy\\BEA.exe" --allowed-root "C:\\safe-copy" --apply --version-overlay
  python3 patches/patch_display_mode_flow.py --path "C:\\safe-copy\\BEA.exe" --allowed-root "C:\\safe-copy" --apply --skip-auto-toggle
  python3 patches/patch_display_mode_flow.py --path "C:\\safe-copy\\BEA.exe" --allowed-root "C:\\safe-copy" --restore
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BACKUP_SUFFIX = ".original.backup"
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
PATCH_KEY_BY_OFFSET = {
    0x129696: "resolution_gate",
    0x12A644: "force_windowed",
    0x0CDD40: "extra_graphics_default_on",
    0x12AF3F: "ignore_cardid_tweak_overrides",
    0x6416F: "version_overlay_use_patched_format_pointer",
    0x1AA444: "version_overlay_patched_format_cave_string",
    0x12BB97: "skip_auto_toggle",
}


@dataclass(frozen=True)
class PatchSpec:
    name: str
    file_offset: int
    original: bytes
    patched: bytes
    optional: bool = False


BASE_PATCHES = [
    PatchSpec(
        name="BuildDeviceList non-4:3 rejection bypass",
        file_offset=0x129696,
        original=bytes([0xCC]),
        patched=bytes([0x00]),
    ),
    PatchSpec(
        name="Force windowed startup flag in Initialize3DEnvironment",
        file_offset=0x12A644,
        original=bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
        patched=bytes([0xB8, 0x01, 0x00, 0x00, 0x00]),
    ),
    PatchSpec(
        name="Unlock extra graphics features default gate (GEFORCE_FX_POWER=1)",
        file_offset=0x0CDD40,
        original=bytes([0x6A, 0x00]),
        patched=bytes([0x6A, 0x01]),
    ),
    PatchSpec(
        name="Ignore cardid.txt vendor/device tweak overrides",
        file_offset=0x12AF3F,
        original=bytes([0xE8, 0x9C, 0xD7, 0xFF, 0xFF]),
        patched=bytes([0x90, 0x90, 0x90, 0x90, 0x90]),
    ),
    PatchSpec(
        name="Version overlay pointer -> patched format cave",
        file_offset=0x6416F,
        original=bytes([0x54, 0x94, 0x62, 0x00]),
        patched=bytes([0x44, 0xA4, 0x5A, 0x00]),
    ),
    PatchSpec(
        name="Version overlay cave format payload (V%1d.%02d - PATCHED)",
        file_offset=0x1AA444,
        original=bytes([0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC]),
        patched=bytes([0x56, 0x25, 0x31, 0x64, 0x2E, 0x25, 0x30, 0x32, 0x64, 0x20, 0x2D, 0x20, 0x50, 0x41, 0x54, 0x43, 0x48, 0x45, 0x44, 0x00]),
    ),
]

OPTIONAL_PATCH = PatchSpec(
    name="Skip auto ToggleFullscreen call gate",
    file_offset=0x12BB97,
    original=bytes([0x75, 0x20]),
    patched=bytes([0xEB, 0x20]),
    optional=True,
)


def active_patches(
    include_optional: bool, resolution_only: bool, windowed_only: bool, version_overlay: bool
) -> list[PatchSpec]:
    if resolution_only and windowed_only:
        raise ValueError("Cannot combine --resolution-only and --windowed-only")

    # Core selectable display-flow patches.
    if resolution_only:
        patches = [BASE_PATCHES[0]]
    elif windowed_only:
        patches = [BASE_PATCHES[1]]
    else:
        patches = list(BASE_PATCHES[:4])

    # Version overlay is an explicit diagnostic marker, not a companion for every patch.
    if version_overlay:
        patches.extend(BASE_PATCHES[4:6])

    if include_optional:
        patches.append(OPTIONAL_PATCH)
    return patches


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


def required_patch_keys(specs: Iterable[PatchSpec]) -> set[str]:
    keys: set[str] = set()
    for spec in specs:
        key = PATCH_KEY_BY_OFFSET.get(spec.file_offset)
        if key:
            keys.add(key)
    return keys


def validate_generated_profile_manifest(
    root: Path, exe_path: Path, expected_patch_keys: set[str] | None = None
) -> None:
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
    if expected_patch_keys:
        missing_keys = sorted(expected_patch_keys - set(patch_keys))
        if missing_keys:
            raise ValueError(
                "generated playable copied game manifest does not list selected patch keys: "
                + ", ".join(missing_keys)
            )


def validate_backup_snapshot(backup_path: Path, specs: Iterable[PatchSpec]) -> None:
    hash_path = Path(str(backup_path) + BACKUP_HASH_SUFFIX)
    if not hash_path.is_file():
        raise ValueError("backup hash sidecar is missing; refusing to trust backup snapshot")

    backup_bytes = backup_path.read_bytes()
    expected_hash = hash_path.read_text(encoding="utf-8").strip()
    actual_hash = sha256_bytes(backup_bytes)
    if expected_hash.lower() != actual_hash.lower():
        raise ValueError("backup hash sidecar does not match backup snapshot")

    data = bytearray(backup_bytes)
    for spec in specs:
        cur = read_bytes(data, spec.file_offset, len(spec.original))
        if cur != spec.original:
            raise ValueError(f"backup snapshot does not contain original bytes for {spec.name}")


def ensure_safe_target(
    exe_path: Path,
    allowed_root: Path | None,
    mutating: bool,
    expected_patch_keys: set[str] | None = None,
) -> Path:
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
        backup_path = Path(str(resolved) + BACKUP_SUFFIX).resolve()
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
        validate_generated_profile_manifest(root, resolved, expected_patch_keys)

    return resolved


def read_bytes(data: bytearray, offset: int, length: int) -> bytes:
    return bytes(data[offset : offset + length])


def check_specs(data: bytearray, specs: Iterable[PatchSpec]) -> tuple[bool, bool]:
    """
    Returns:
      (all_known_state, all_already_patched)
    """
    all_known_state = True
    all_already_patched = True

    for spec in specs:
        cur = read_bytes(data, spec.file_offset, len(spec.original))
        if cur == spec.patched:
            print(f"[OK] {spec.name}: already patched")
        elif cur == spec.original:
            print(f"[OK] {spec.name}: ready to patch")
            all_already_patched = False
        else:
            print(f"[ERR] {spec.name}: unexpected bytes at 0x{spec.file_offset:X}")
            print(f"      expected original: {spec.original.hex(' ')}")
            print(f"      expected patched : {spec.patched.hex(' ')}")
            print(f"      found           : {cur.hex(' ')}")
            all_known_state = False
            all_already_patched = False

    return all_known_state, all_already_patched


def apply(exe_path: Path, specs: list[PatchSpec]) -> bool:
    data = bytearray(exe_path.read_bytes())
    all_known_state, all_already_patched = check_specs(data, specs)
    if not all_known_state:
        print("\nAborting due to unexpected bytes.")
        return False
    if all_already_patched:
        print("\nNo changes needed.")
        return True

    backup_path = Path(str(exe_path) + BACKUP_SUFFIX)
    if not backup_path.exists():
        shutil.copy2(exe_path, backup_path)
        write_backup_hash(backup_path)
        print(f"\nCreated backup: {backup_path}")
    else:
        validate_backup_snapshot(backup_path, specs)
        print(f"\nBackup exists: {backup_path}")

    for spec in specs:
        cur = read_bytes(data, spec.file_offset, len(spec.original))
        if cur == spec.original:
            data[spec.file_offset : spec.file_offset + len(spec.patched)] = spec.patched
            print(
                f"patched 0x{spec.file_offset:X}: "
                f"{spec.original.hex(' ')} -> {spec.patched.hex(' ')}  ({spec.name})"
            )

    exe_path.write_bytes(data)
    read_back = bytearray(exe_path.read_bytes())
    _, all_patched_after_write = check_specs(read_back, specs)
    if not all_patched_after_write:
        print("\n[ERR] On-disk patch verification did not match selected patched bytes.")
        return False
    print("\nPatch apply complete.")
    return True


def restore(exe_path: Path) -> bool:
    backup_path = Path(str(exe_path) + BACKUP_SUFFIX)
    if not backup_path.exists():
        print(f"[ERR] Backup not found: {backup_path}")
        return False
    all_specs = [*BASE_PATCHES, OPTIONAL_PATCH]
    try:
        validate_backup_snapshot(backup_path, all_specs)
    except ValueError as exc:
        print(f"[ERR] Restore aborted: {exc}")
        return False

    data = bytearray(exe_path.read_bytes())
    has_patched_bytes = False
    all_known_state = True
    for spec in all_specs:
        cur = read_bytes(data, spec.file_offset, len(spec.original))
        if cur == spec.patched:
            has_patched_bytes = True
        elif cur != spec.original:
            print(f"[ERR] {spec.name}: unexpected bytes at 0x{spec.file_offset:X}")
            all_known_state = False

    if not all_known_state:
        print("[ERR] Restore aborted: current target does not contain verified known patched bytes.")
        return False
    if not has_patched_bytes and exe_path.read_bytes() == backup_path.read_bytes():
        print("No changes needed. Target already matches the verified backup snapshot.")
        return True

    shutil.copy2(backup_path, exe_path)
    if exe_path.read_bytes() != backup_path.read_bytes():
        print("[ERR] Restore failed: on-disk verification did not match backup.")
        return False
    print(f"Restored from backup: {backup_path}")
    return True


def verify(exe_path: Path, specs: list[PatchSpec]) -> bool:
    data = bytearray(exe_path.read_bytes())
    all_known_state, all_already_patched = check_specs(data, specs)
    if not all_known_state:
        return False
    print(f"\nState: {'patched' if all_already_patched else 'mixed/original'}")
    return True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Patch BEA.exe display mode behavior")
    p.add_argument("--path", type=Path, required=True, help="Target copied BEA.exe path")
    p.add_argument("--allowed-root", type=Path, help="Required for apply/restore; app-owned root containing the copied target")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true", help="Apply selected patches")
    mode.add_argument("--restore", action="store_true", help="Restore backup")
    mode.add_argument("--verify", action="store_true", help="Verify patch state only")
    p.add_argument(
        "--skip-auto-toggle",
        action="store_true",
        help="Include optional patch to skip startup ToggleFullscreen gate",
    )
    p.add_argument(
        "--version-overlay",
        action="store_true",
        help="Include explicit diagnostic PATCHED marker in the bottom-left version overlay",
    )
    p.add_argument(
        "--resolution-only",
        action="store_true",
        help="Select only the non-4:3 resolution gate bypass patch",
    )
    p.add_argument(
        "--windowed-only",
        action="store_true",
        help="Select only the forced windowed startup patch",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        specs = active_patches(
            include_optional=args.skip_auto_toggle,
            resolution_only=args.resolution_only,
            windowed_only=args.windowed_only,
            version_overlay=args.version_overlay,
        )
    except ValueError as e:
        print(f"[ERR] {e}")
        return 1
    try:
        exe_path = ensure_safe_target(
            args.path,
            args.allowed_root,
            mutating=args.apply or args.restore,
            expected_patch_keys=required_patch_keys(specs) if args.apply else None,
        )
    except Exception as e:
        print(f"[ERR] {e}")
        return 1
    print(f"Target: {exe_path}")
    print(f"Patches selected: {len(specs)}")

    if args.verify:
        ok = verify(exe_path, specs)
    elif args.restore:
        ok = restore(exe_path)
    else:
        ok = apply(exe_path, specs)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
