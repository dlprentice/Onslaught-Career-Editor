"""
Core binary patch logic for BEA.exe stable/experimental patch catalog entries.
GUI layers should import from here to keep logic testable without PyQt.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BACKUP_SUFFIX = ".original.backup"
CATALOG_RELATIVE_PATH = Path("patches") / "catalog" / "patches.v2.json"

PATCH_STATE_ORIGINAL = "ready (original)"
PATCH_STATE_PATCHED = "already patched"
PATCH_STATE_MISMATCH = "unexpected bytes"
PATCH_STATE_OUT_OF_RANGE = "offset out of range"


@dataclass(frozen=True)
class PatchSpec:
    key: str
    display_name: str
    file_offset: int
    original: bytes
    patched: bytes
    track: str = "Stable"
    optional: bool = False


@dataclass(frozen=True)
class CatalogLoadState:
    specs: tuple[PatchSpec, ...]
    using_fallback: bool
    status: str


_FALLBACK_PATCH_SPECS: tuple[PatchSpec, ...] = (
    PatchSpec(
        key="resolution_gate",
        display_name="Allow widescreen resolutions (remove 4:3-only rejection)",
        file_offset=0x129696,
        original=bytes([0xCC]),
        patched=bytes([0x00]),
        track="Stable",
    ),
    PatchSpec(
        key="force_windowed",
        display_name="Prefer windowed startup (when windowed-capable)",
        file_offset=0x12A644,
        original=bytes([0xA1, 0xF0, 0x2D, 0x66, 0x00]),
        patched=bytes([0xB8, 0x01, 0x00, 0x00, 0x00]),
        track="Stable",
    ),
    PatchSpec(
        key="extra_graphics_default_on",
        display_name="Unlock extra graphics features by default (disable cardid gate default)",
        file_offset=0x0CDD40,
        original=bytes([0x6A, 0x00]),
        patched=bytes([0x6A, 0x01]),
        track="Stable",
    ),
    PatchSpec(
        key="ignore_cardid_tweak_overrides",
        display_name="Ignore cardid.txt vendor/device tweak overrides",
        file_offset=0x12AF3F,
        original=bytes([0xE8, 0x9C, 0xD7, 0xFF, 0xFF]),
        patched=bytes([0x90, 0x90, 0x90, 0x90, 0x90]),
        track="Stable",
    ),
    PatchSpec(
        key="version_overlay_use_patched_format_pointer",
        display_name="Version overlay pointer -> patched format cave",
        file_offset=0x6416F,
        original=bytes([0x54, 0x94, 0x62, 0x00]),
        patched=bytes([0x44, 0xA4, 0x5A, 0x00]),
        track="Stable",
    ),
    PatchSpec(
        key="version_overlay_patched_format_cave_string",
        display_name="Version overlay cave format payload (V%1d.%02d - PATCHED)",
        file_offset=0x1AA444,
        original=bytes([0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC]),
        patched=bytes([0x56, 0x25, 0x31, 0x64, 0x2E, 0x25, 0x30, 0x32, 0x64, 0x20, 0x2D, 0x20, 0x50, 0x41, 0x54, 0x43, 0x48, 0x45, 0x44, 0x00]),
        track="Stable",
    ),
    PatchSpec(
        key="skip_auto_toggle",
        display_name="Optional: bypass one startup fullscreen toggle check",
        file_offset=0x12BB97,
        original=bytes([0x75, 0x20]),
        patched=bytes([0xEB, 0x20]),
        track="Experimental",
        optional=True,
    ),
)


def _resolve_catalog_path() -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[2] / CATALOG_RELATIVE_PATH,
        Path.cwd() / CATALOG_RELATIVE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _parse_hex_bytes(raw: str) -> bytes | None:
    if not raw or not raw.strip():
        return None

    tokens = raw.replace(",", " ").replace(";", " ").replace("-", " ").split()
    out: list[int] = []
    for token in tokens:
        t = token.strip()
        if t.lower().startswith("0x"):
            t = t[2:]
        if not t:
            continue
        try:
            out.append(int(t, 16))
        except ValueError:
            return None

    if not out:
        return None
    if any(v < 0 or v > 0xFF for v in out):
        return None
    return bytes(out)


def _parse_offset(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            if raw.lower().startswith("0x"):
                return int(raw[2:], 16)
            return int(raw, 10)
        except ValueError:
            return None
    return None


def _load_patch_specs_from_catalog() -> CatalogLoadState:
    catalog = _resolve_catalog_path()
    if catalog is None:
        return CatalogLoadState(
            specs=_FALLBACK_PATCH_SPECS,
            using_fallback=True,
            status="Catalog unavailable; using built-in fallback patch specs.",
        )

    try:
        payload = json.loads(catalog.read_text(encoding="utf-8"))
    except Exception as exc:
        return CatalogLoadState(
            specs=_FALLBACK_PATCH_SPECS,
            using_fallback=True,
            status=f"Catalog read failed ({exc}); using built-in fallback patch specs.",
        )

    patches = payload.get("patches")
    if not isinstance(patches, list):
        return CatalogLoadState(
            specs=_FALLBACK_PATCH_SPECS,
            using_fallback=True,
            status="Catalog payload missing patch list; using built-in fallback patch specs.",
        )

    loaded: list[PatchSpec] = []
    for row in patches:
        if not isinstance(row, dict):
            continue
        key = row.get("id")
        display_name = row.get("title")
        track = row.get("track")
        file_offset = _parse_offset(row.get("file_offset"))
        original = _parse_hex_bytes(str(row.get("expected_original_bytes", "")))
        patched = _parse_hex_bytes(str(row.get("patched_bytes", "")))
        optional = bool(row.get("optional", False))

        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(display_name, str) or not display_name.strip():
            continue
        if not isinstance(track, str) or not track.strip():
            continue
        if file_offset is None or file_offset < 0:
            continue
        if original is None or patched is None or len(original) != len(patched):
            continue

        normalized_track = "Stable" if track.lower() == "stable" else "Experimental" if track.lower() == "experimental" else track
        loaded.append(
            PatchSpec(
                key=key.strip(),
                display_name=display_name.strip(),
                file_offset=file_offset,
                original=original,
                patched=patched,
                track=normalized_track,
                optional=optional,
            )
        )

    if not loaded:
        return CatalogLoadState(
            specs=_FALLBACK_PATCH_SPECS,
            using_fallback=True,
            status="Catalog contained no valid patch rows; using built-in fallback patch specs.",
        )
    return CatalogLoadState(
        specs=tuple(loaded),
        using_fallback=False,
        status=f"Loaded patch catalog from {catalog}",
    )


_CATALOG_STATE = _load_patch_specs_from_catalog()
PATCH_SPECS: tuple[PatchSpec, ...] = _CATALOG_STATE.specs
USING_FALLBACK_PATCH_CATALOG = _CATALOG_STATE.using_fallback
PATCH_CATALOG_STATUS = _CATALOG_STATE.status


def get_patch_spec(key: str) -> PatchSpec | None:
    for spec in PATCH_SPECS:
        if spec.key == key:
            return spec
    return None


def build_backup_path(exe_path: Path) -> Path:
    return Path(str(exe_path) + BACKUP_SUFFIX)


def get_patch_state(data: bytes, spec: PatchSpec) -> str:
    if len(spec.original) != len(spec.patched):
        return PATCH_STATE_MISMATCH

    end = spec.file_offset + len(spec.original)
    if spec.file_offset < 0 or end > len(data):
        return PATCH_STATE_OUT_OF_RANGE

    current = data[spec.file_offset:end]
    if current == spec.patched:
        return PATCH_STATE_PATCHED
    if current == spec.original:
        return PATCH_STATE_ORIGINAL
    return PATCH_STATE_MISMATCH


def verify_patch_specs(data: bytes, specs: Iterable[PatchSpec]) -> tuple[bool, bool, list[tuple[PatchSpec, str]]]:
    rows: list[tuple[PatchSpec, str]] = []
    all_known_state = True
    all_already_patched = True

    for spec in specs:
        state = get_patch_state(data, spec)
        rows.append((spec, state))
        if state == PATCH_STATE_ORIGINAL:
            all_already_patched = False
        elif state in (PATCH_STATE_MISMATCH, PATCH_STATE_OUT_OF_RANGE):
            all_known_state = False
            all_already_patched = False

    return all_known_state, all_already_patched, rows


def render_state_report(exe_path: Path, rows: list[tuple[PatchSpec, str]], summary: str) -> str:
    lines = [f"Target: {exe_path}", ""]
    for spec, state in rows:
        lines.append(f"[{spec.track} | {spec.display_name}] @ 0x{spec.file_offset:X}: {state}")
    lines.extend(["", summary])
    return "\n".join(lines)


def apply_patches_to_file(exe_path: Path, specs: list[PatchSpec]) -> tuple[bool, str]:
    if not specs:
        return False, "Select at least one patch to apply."

    data = bytearray(exe_path.read_bytes())
    all_known, all_patched, rows = verify_patch_specs(data, specs)

    if not all_known:
        return False, render_state_report(
            exe_path,
            rows,
            "Apply aborted: at least one selected patch has unexpected bytes.",
        )

    if all_patched:
        return True, render_state_report(
            exe_path,
            rows,
            "No changes needed. All selected patches are already applied.",
        )

    backup_path = build_backup_path(exe_path)
    if not backup_path.exists():
        shutil.copy2(exe_path, backup_path)

    for spec, state in rows:
        if state == PATCH_STATE_ORIGINAL:
            start = spec.file_offset
            end = start + len(spec.patched)
            data[start:end] = spec.patched

    exe_path.write_bytes(data)
    _, _, after_rows = verify_patch_specs(data, specs)
    summary = (
        "Patch apply complete.\n"
        f"Backup: {backup_path}\n"
        "Restore uses the first full-file backup snapshot, not per-patch undo."
    )
    return True, render_state_report(exe_path, after_rows, summary)


def restore_from_backup(exe_path: Path) -> tuple[bool, str]:
    backup_path = build_backup_path(exe_path)
    if not backup_path.exists():
        return False, f"Backup file not found: {backup_path}"

    shutil.copy2(backup_path, exe_path)
    return True, (
        "Restore complete.\n"
        f"Target: {exe_path}\n"
        f"Backup source: {backup_path}\n"
        "Result: full executable restored from the original backup snapshot."
    )
