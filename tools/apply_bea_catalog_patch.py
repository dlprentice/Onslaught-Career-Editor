#!/usr/bin/env python3
"""Verify or apply catalog byte patches to a generated copied-game BEA.exe.

This is a tooling/lab helper for runtime proof setup. Mutating modes require a
generated playable copied-game manifest and an app-owned allowed root so the
installed Steam executable cannot be patched through this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = REPO_ROOT / "patches" / "catalog" / "patches.v2.json"
EXPECTED_CATALOG_SHA256 = "9b42e35ba1f12f012300e569ea0be6e747c245d4c60403bee3e32c0b5857a582"
KNOWN_RETAIL_STEAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
KNOWN_RETAIL_STEAM_SIZE = 2_506_752
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

STATE_ORIGINAL = "ready (original)"
STATE_PATCHED = "already patched"
STATE_MISMATCH = "unexpected bytes"
STATE_OUT_OF_RANGE = "offset out of range"


@dataclass(frozen=True)
class PatchSpec:
    patch_id: str
    title: str
    track: str
    file_offset: int
    original: bytes
    patched: bytes
    optional: bool
    dependencies: tuple[str, ...]
    conflicts: tuple[str, ...]
    exclusive_group: str
    proof_level: str
    selectability: str
    preset_eligibility: tuple[str, ...]
    requires_windowed_pair: bool
    target_binary_size: int | None
    target_binary_hashes: tuple[str, ...]


def _parse_hex_bytes(raw: str) -> bytes:
    tokens = raw.replace(",", " ").replace(";", " ").replace("-", " ").split()
    out: list[int] = []
    for token in tokens:
        value = token[2:] if token.lower().startswith("0x") else token
        out.append(int(value, 16))
    return bytes(out)


def _parse_offset(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if raw.lower().startswith("0x"):
            return int(raw[2:], 16)
        return int(raw, 10)
    raise ValueError(f"unsupported offset value: {value!r}")


def _parse_string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    values: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        normalized = cleaned.casefold()
        if cleaned and normalized not in seen:
            seen.add(normalized)
            values.append(cleaned)
    return tuple(values)


def _parse_optional_string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _parse_optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip():
        return _parse_offset(value)
    return None


def load_catalog(catalog_path: Path) -> list[PatchSpec]:
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    patches = payload.get("patches")
    if not isinstance(patches, list):
        raise ValueError(f"catalog has no patches array: {catalog_path}")

    specs: list[PatchSpec] = []
    for row in patches:
        if not isinstance(row, dict):
            continue
        patch_id = str(row.get("id", "")).strip()
        title = str(row.get("title", "")).strip()
        track = str(row.get("track", "")).strip()
        original = _parse_hex_bytes(str(row.get("expected_original_bytes", "")))
        patched = _parse_hex_bytes(str(row.get("patched_bytes", "")))
        if not patch_id or not title or not track:
            continue
        if len(original) != len(patched) or original == patched:
            continue
        specs.append(
            PatchSpec(
                patch_id=patch_id,
                title=title,
                track=track,
                file_offset=_parse_offset(row.get("file_offset")),
                original=original,
                patched=patched,
                optional=bool(row.get("optional", False)),
                dependencies=_parse_string_tuple(row.get("dependencies")),
                conflicts=_parse_string_tuple(row.get("conflicts")),
                exclusive_group=_parse_optional_string(row.get("exclusive_group")),
                proof_level=_parse_optional_string(row.get("proof_level")),
                selectability=_parse_optional_string(row.get("selectability")),
                preset_eligibility=_parse_string_tuple(row.get("preset_eligibility")),
                requires_windowed_pair=bool(row.get("requires_windowed_pair", False)),
                target_binary_size=_parse_optional_int(row.get("target_binary_size")),
                target_binary_hashes=_parse_string_tuple(row.get("target_binary_hashes")),
            )
        )
    if not specs:
        raise ValueError(f"catalog produced no valid patch specs: {catalog_path}")
    return specs


def build_backup_path(exe_path: Path) -> Path:
    return Path(str(exe_path) + BACKUP_SUFFIX)


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


def validate_catalog_trust_for_mutation(catalog_path: Path) -> None:
    catalog_bytes = catalog_path.read_bytes()
    catalog_hash = sha256_bytes(catalog_bytes)
    if catalog_hash.lower() != EXPECTED_CATALOG_SHA256:
        raise ValueError(
            "mutating modes require the supported patch catalog hash; "
            "refusing arbitrary catalog bytes for copied-game proof mutation"
        )


def write_backup_hash(backup_path: Path) -> None:
    hash_path = Path(str(backup_path) + BACKUP_HASH_SUFFIX)
    with hash_path.open("x", encoding="utf-8") as stream:
        stream.write(sha256_bytes(backup_path.read_bytes()))


def validate_backup_hash_sidecar_path(backup_path: Path, root: Path) -> None:
    hash_path = Path(str(backup_path) + BACKUP_HASH_SUFFIX)
    reject_reparse_ancestors(hash_path, root)
    if not hash_path.exists():
        return
    if is_reparse_point(hash_path):
        raise ValueError(f"refusing to trust reparse-point backup hash sidecar: {hash_path}")
    if not hash_path.is_file():
        raise ValueError(f"backup hash sidecar is not a regular file: {hash_path}")
    if getattr(os.stat(hash_path), "st_nlink", 1) > 1:
        raise ValueError(f"refusing to write hardlinked backup hash sidecar: {hash_path}")
    if not backup_path.exists():
        raise ValueError(f"backup hash sidecar exists without its backup snapshot: {hash_path}")


def validate_generated_profile_manifest(root: Path, exe_path: Path, patch_ids: set[str]) -> None:
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
    manifest_patch_keys = patch_result.get("patchKeys")
    if not isinstance(manifest_patch_keys, list) or not all(isinstance(key, str) for key in manifest_patch_keys):
        raise ValueError("generated playable copied game manifest is missing patchResult.patchKeys")
    manifest_patch_ids = {key.casefold() for key in manifest_patch_keys}
    missing_patch_keys = sorted(key for key in patch_ids if key.casefold() not in manifest_patch_ids)
    if missing_patch_keys:
        raise ValueError(
            "generated playable copied game manifest does not list selected patch keys: "
            + ", ".join(missing_patch_keys)
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

    for spec in specs:
        current = bytes(backup_bytes[spec.file_offset : spec.file_offset + len(spec.original)])
        if current != spec.original:
            raise ValueError(f"backup snapshot does not contain original bytes for {spec.patch_id}")


def validate_current_against_backup_catalog_transitions(
    current_bytes: bytes,
    backup_bytes: bytes,
    catalog_specs: Iterable[PatchSpec],
) -> None:
    if len(current_bytes) != len(backup_bytes):
        raise ValueError("current BEA.exe size differs from the verified full-file backup")

    allowed_differences = bytearray(len(current_bytes))
    for spec in catalog_specs:
        start = spec.file_offset
        end = start + len(spec.original)
        if start < 0 or end > len(current_bytes):
            continue
        if backup_bytes[start:end] == spec.original and current_bytes[start:end] == spec.patched:
            allowed_differences[start:end] = b"\x01" * (end - start)

    for index, (current, original) in enumerate(zip(current_bytes, backup_bytes, strict=True)):
        if current != original and not allowed_differences[index]:
            raise ValueError(
                "current BEA.exe differs from the verified backup outside known catalog patch spans"
            )


def validate_supported_specimen_identity(
    exe_path: Path,
    selected_specs: Iterable[PatchSpec],
    catalog_specs: Iterable[PatchSpec],
    *,
    allow_byte_layout_only_target: bool,
) -> None:
    selected_list = list(selected_specs)
    catalog_list = list(catalog_specs)
    current_bytes = exe_path.read_bytes()
    backup_path = build_backup_path(exe_path)
    if backup_path.exists():
        validate_backup_snapshot(backup_path, selected_list)
        identity_bytes = backup_path.read_bytes()
        validate_current_against_backup_catalog_transitions(
            current_bytes,
            identity_bytes,
            catalog_list,
        )
    else:
        identity_bytes = current_bytes

    if allow_byte_layout_only_target:
        return

    digest = sha256_bytes(identity_bytes).lower()
    if digest != KNOWN_RETAIL_STEAM_SHA256 or len(identity_bytes) != KNOWN_RETAIL_STEAM_SIZE:
        raise ValueError(
            "mutating modes require the canonical clean specimen or its verified full-file backup; "
            "synthetic byte-layout fixtures require --allow-byte-layout-only-target"
        )


def ensure_safe_target(
    exe_path: Path,
    *,
    allowed_root: Path | None,
    mutating: bool,
    patch_ids: set[str] | None = None,
    specs: Iterable[PatchSpec] | None = None,
    catalog_specs: Iterable[PatchSpec] | None = None,
    allow_byte_layout_only_target: bool = False,
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
            "prepare a copied profile or app-owned artifact root first"
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
        backup_path = build_backup_path(resolved).resolve()
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
        validate_backup_hash_sidecar_path(backup_path, root)
        validate_generated_profile_manifest(root, resolved, patch_ids or set())
        known_sizes = {spec.target_binary_size for spec in specs or () if spec.target_binary_size}
        if known_sizes and resolved.stat().st_size not in known_sizes:
            raise ValueError("target BEA.exe size does not match the supported patch catalog specimen size")
        validate_supported_specimen_identity(
            resolved,
            specs or (),
            catalog_specs or specs or (),
            allow_byte_layout_only_target=allow_byte_layout_only_target,
        )
    return resolved


def patch_state(data: bytes | bytearray, spec: PatchSpec) -> str:
    end = spec.file_offset + len(spec.original)
    if spec.file_offset < 0 or end > len(data):
        return STATE_OUT_OF_RANGE
    current = bytes(data[spec.file_offset:end])
    if current == spec.patched:
        return STATE_PATCHED
    if current == spec.original:
        return STATE_ORIGINAL
    return STATE_MISMATCH


def verify(data: bytes | bytearray, specs: Iterable[PatchSpec]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec in specs:
        rows.append(
            {
                "id": spec.patch_id,
                "title": spec.title,
                "track": spec.track,
                "fileOffset": f"0x{spec.file_offset:X}",
                "state": patch_state(data, spec),
            }
        )
    return rows


def validate_patch_selection_policy(specs: list[PatchSpec]) -> None:
    by_id: dict[str, PatchSpec] = {}
    for spec in specs:
        normalized_id = spec.patch_id.casefold()
        if normalized_id in by_id:
            raise ValueError(f"patch selection contains duplicate row: {spec.patch_id}")
        by_id[normalized_id] = spec

    selected_ids = set(by_id)
    for spec in specs:
        if spec.original == spec.patched:
            raise ValueError(f"patch selection contains no-op row: {spec.patch_id}")
        for dependency in spec.dependencies:
            if dependency.casefold() not in selected_ids:
                raise ValueError(f"patch selection is missing dependency {dependency} required by {spec.patch_id}")
        for conflict in spec.conflicts:
            if conflict.casefold() in selected_ids:
                raise ValueError(f"patch selection contains conflicting rows: {spec.patch_id} and {conflict}")
        if spec.selectability.casefold() == "hidden_companion":
            has_visible_dependent = any(
                candidate.selectability.casefold() != "hidden_companion"
                and any(
                    dependency.casefold() == spec.patch_id.casefold()
                    for dependency in candidate.dependencies
                )
                for candidate in specs
            )
            if not has_visible_dependent:
                raise ValueError(f"patch selection contains hidden companion row without its visible dependent: {spec.patch_id}")

    exclusive_groups: dict[str, list[str]] = {}
    for spec in specs:
        if spec.exclusive_group:
            exclusive_groups.setdefault(spec.exclusive_group.casefold(), []).append(spec.patch_id)
    for group, members in exclusive_groups.items():
        if len(members) > 1:
            raise ValueError(f"patch selection contains multiple rows from exclusive group {group}: {', '.join(members)}")

    if any(spec.requires_windowed_pair for spec in specs) and not {"resolution_gate", "force_windowed"}.issubset(selected_ids):
        raise ValueError("patch selection includes a row that requires the baseline windowed compatibility pair")

    ranges = [
        (spec.file_offset, spec.file_offset + len(spec.patched), spec)
        for spec in specs
    ]
    for index, (left_start, left_end, left_spec) in enumerate(ranges):
        for right_start, right_end, right_spec in ranges[index + 1 :]:
            overlaps = left_start < right_end and right_start < left_end
            identical_mutation = (
                left_start == right_start
                and left_end == right_end
                and left_spec.original == right_spec.original
                and left_spec.patched == right_spec.patched
            )
            if overlaps and not identical_mutation:
                raise ValueError(f"patch selection contains overlapping rows: {left_spec.patch_id} and {right_spec.patch_id}")


def choose_specs(all_specs: list[PatchSpec], patch_ids: list[str]) -> list[PatchSpec]:
    by_id = {spec.patch_id.casefold(): spec for spec in all_specs}
    missing = [patch_id for patch_id in patch_ids if patch_id.casefold() not in by_id]
    if missing:
        raise ValueError(f"unknown patch id(s): {', '.join(missing)}")

    selected: list[PatchSpec] = []
    selected_ids: set[str] = set()

    def add_with_dependencies(patch_id: str) -> None:
        normalized_id = patch_id.casefold()
        spec = by_id[normalized_id]
        if normalized_id in selected_ids:
            return
        selected.append(spec)
        selected_ids.add(normalized_id)
        for dependency in spec.dependencies:
            if dependency.casefold() not in by_id:
                raise ValueError(f"patch selection references unknown dependency {dependency} required by {spec.patch_id}")
            add_with_dependencies(dependency)

    for patch_id in patch_ids:
        add_with_dependencies(patch_id)

    validate_patch_selection_policy(selected)
    return selected


def run_patch(
    exe_path: Path,
    specs: list[PatchSpec],
    *,
    apply: bool,
    dry_run: bool,
    catalog_specs: Iterable[PatchSpec] | None = None,
) -> dict[str, object]:
    data = bytearray(exe_path.read_bytes())
    before = verify(data, specs)
    bad_states = {STATE_MISMATCH, STATE_OUT_OF_RANGE}
    if any(row["state"] in bad_states for row in before):
        return {
            "success": False,
            "applied": False,
            "target": str(exe_path),
            "before": before,
            "after": before,
            "message": "aborted: at least one selected patch has unexpected bytes",
        }

    already_patched = all(row["state"] == STATE_PATCHED for row in before)
    if already_patched or dry_run or not apply:
        action = "verified" if already_patched else "dry-run" if dry_run else "verified"
        return {
            "success": True,
            "applied": False,
            "target": str(exe_path),
            "before": before,
            "after": before,
            "message": f"{action}: no bytes were written",
        }

    backup_path = build_backup_path(exe_path)
    if not backup_path.exists():
        shutil.copy2(exe_path, backup_path)
        write_backup_hash(backup_path)
    else:
        validate_backup_snapshot(backup_path, specs)
    backup_bytes = backup_path.read_bytes()
    validate_current_against_backup_catalog_transitions(
        bytes(data),
        backup_bytes,
        catalog_specs or specs,
    )

    for spec, row in zip(specs, before, strict=True):
        if row["state"] == STATE_ORIGINAL:
            start = spec.file_offset
            data[start : start + len(spec.patched)] = spec.patched

    exe_path.write_bytes(data)
    after = verify(bytearray(exe_path.read_bytes()), specs)
    success = all(row["state"] == STATE_PATCHED for row in after)
    return {
        "success": success,
        "applied": True,
        "target": str(exe_path),
        "backup": str(backup_path),
        "before": before,
        "after": after,
        "message": "patch apply complete" if success else "patch write completed but verification failed",
    }


def render_report(result: dict[str, object]) -> str:
    lines = [
        f"Target: {result['target']}",
        f"Result: {result['message']}",
    ]
    if "backup" in result:
        lines.append(f"Backup: {result['backup']}")
    lines.append("")
    for row in result["after"]:  # type: ignore[index]
        lines.append(f"{row['id']} @ {row['fileOffset']}: {row['state']}")
    return "\n".join(lines)


def self_test() -> int:
    if _parse_string_tuple(["custom", "CUSTOM"]) != ("custom",):
        print("self-test case-insensitive list normalization failed", file=sys.stderr)
        return 1

    catalog_specs = load_catalog(DEFAULT_CATALOG)
    selected = choose_specs(catalog_specs, ["FORCE_WINDOWED"])
    if [spec.patch_id for spec in selected] != ["force_windowed"]:
        print("self-test case-insensitive patch selection failed", file=sys.stderr)
        return 1
    selected = choose_specs(
        catalog_specs,
        ["resolution_gate", "force_windowed", "free_camera_keyboard_forward_q_hook"],
    )
    casefolded_selection = [
        replace(
            spec,
            patch_id=spec.patch_id.upper(),
            dependencies=tuple(dependency.upper() for dependency in spec.dependencies),
            conflicts=tuple(conflict.upper() for conflict in spec.conflicts),
        )
        for spec in selected
    ]
    try:
        validate_patch_selection_policy(casefolded_selection)
    except ValueError as exc:
        print(f"self-test case-insensitive selection policy failed: {exc}", file=sys.stderr)
        return 1
    try:
        choose_specs(catalog_specs, ["frontend_clear_screen_dark_red", "frontend_clear_screen_dark_green"])
        print("self-test conflict policy failed", file=sys.stderr)
        return 1
    except ValueError as exc:
        if "exclusive group" not in str(exc) and "conflicting rows" not in str(exc):
            print(f"self-test conflict policy wrong error: {exc}", file=sys.stderr)
            return 1

    try:
        choose_specs(catalog_specs, ["free_camera_aurore_gate_bypass"])
        print("self-test windowed-pair policy failed", file=sys.stderr)
        return 1
    except ValueError as exc:
        if "windowed compatibility pair" not in str(exc):
            print(f"self-test windowed-pair policy wrong error: {exc}", file=sys.stderr)
            return 1

    try:
        choose_specs(catalog_specs, ["version_overlay_patched_format_cave_string"])
        print("self-test hidden companion policy failed", file=sys.stderr)
        return 1
    except ValueError as exc:
        if "hidden companion" not in str(exc):
            print(f"self-test hidden companion policy wrong error: {exc}", file=sys.stderr)
            return 1

    overlay_specs = choose_specs(catalog_specs, ["version_overlay_use_patched_format_pointer"])
    if {spec.patch_id for spec in overlay_specs} != {
        "version_overlay_use_patched_format_pointer",
        "version_overlay_patched_format_cave_string",
    }:
        print("self-test dependency closure failed", file=sys.stderr)
        return 1

    overlap_first = choose_specs(catalog_specs, ["force_windowed"])[0]
    overlap_second = replace(
        overlap_first,
        patch_id="self_test_shifted_overlap",
        file_offset=overlap_first.file_offset + 1,
    )
    try:
        validate_patch_selection_policy([overlap_first, overlap_second])
        print("self-test shifted-overlap policy failed", file=sys.stderr)
        return 1
    except ValueError as exc:
        if "overlapping" not in str(exc):
            print(f"self-test shifted-overlap policy wrong error: {exc}", file=sys.stderr)
            return 1

    specs = choose_specs(catalog_specs, ["force_windowed"])
    spec = specs[0]
    with tempfile.TemporaryDirectory(prefix="bea-patch-self-test-") as temp:
        exe_path = Path(temp) / "BEA.exe"
        size = spec.file_offset + len(spec.original) + 32
        data = bytearray(b"\x00" * size)
        data[spec.file_offset : spec.file_offset + len(spec.original)] = spec.original
        exe_path.write_bytes(data)

        dry = run_patch(exe_path, specs, apply=False, dry_run=True)
        if dry["applied"] or dry["after"][0]["state"] != STATE_ORIGINAL:  # type: ignore[index]
            print("self-test dry-run failed", file=sys.stderr)
            return 1

        applied = run_patch(exe_path, specs, apply=True, dry_run=False, catalog_specs=catalog_specs)
        if not applied["success"] or applied["after"][0]["state"] != STATE_PATCHED:  # type: ignore[index]
            print("self-test apply failed", file=sys.stderr)
            return 1
        if not build_backup_path(exe_path).exists():
            print("self-test backup missing", file=sys.stderr)
            return 1
    print("self-test passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify or apply patch-catalog bytes to a copied BEA.exe."
    )
    parser.add_argument("--exe", type=Path, help="Copied BEA.exe target.")
    parser.add_argument("--allowed-root", type=Path, help="Required for --apply; app-owned copied-game root containing BEA.exe.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--patch-id", action="append", default=[])
    parser.add_argument("--list", action="store_true", help="List available patch IDs.")
    parser.add_argument("--apply", action="store_true", help="Write selected patch bytes.")
    parser.add_argument(
        "--allow-byte-layout-only-target",
        action="store_true",
        help="Test-only: permit a synthetic same-size fixture instead of the canonical specimen.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Verify without writing.")
    parser.add_argument("--json-out", type=Path, help="Optional JSON report path.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.apply:
        try:
            validate_catalog_trust_for_mutation(args.catalog)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2

    specs = load_catalog(args.catalog)
    if args.list:
        for spec in specs:
            marker = " optional" if spec.optional else ""
            print(f"{spec.patch_id}\t{spec.track}{marker}\t{spec.title}")
        return 0

    if args.exe is None:
        parser.error("--exe is required unless --list or --self-test is used")
    if not args.patch_id:
        parser.error("at least one --patch-id is required")
    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")
    if args.allow_byte_layout_only_target and not args.apply:
        parser.error("--allow-byte-layout-only-target is valid only with --apply")

    try:
        selected = choose_specs(specs, args.patch_id)
        exe_path = ensure_safe_target(
            args.exe,
            allowed_root=args.allowed_root,
            mutating=args.apply,
            patch_ids={spec.patch_id for spec in selected} if args.apply else None,
            specs=selected,
            catalog_specs=specs,
            allow_byte_layout_only_target=args.allow_byte_layout_only_target,
        )
        result = run_patch(
            exe_path,
            selected,
            apply=args.apply,
            dry_run=args.dry_run,
            catalog_specs=specs,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(render_report(result))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
