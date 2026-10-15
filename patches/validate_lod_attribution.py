#!/usr/bin/env python3
"""Compare two proxy-v2 captures at one transform-pinned LOD checkpoint.

The comparator deliberately ignores process-local matrix ids, COM pointers,
wrapper generations, texture serials, and frame numbers. It admits a draw only
when direct view/projection/world matrix values, texture content identities, and
complete non-provisional VB/IB geometry digests make the comparison reproducible.
Every omission is a named failure or an explicit exclusion in the receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Sequence

RECEIPT_SCHEMA = "bea-lod-attribution-receipt.v1"
RUN_SCHEMA = "bea-lod-attribution-run.v1"
PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
HEX16_RE = re.compile(r"^[0-9A-Fa-f]{16}$")
FIELD_RE = re.compile(r"(?:^|\s)([A-Za-z0-9_.]+)=([^\s]+)")
MATRIX_RE = re.compile(r"^M (\d+) (\S+)( mul)? m=(.+)$")
DRAW_RE = re.compile(r"^D (\d+) (\d+) (\S+) (.+)$")
GEOM_RE = re.compile(r"^G (\d+) (\d+) (vb|ib) (.+)$")
PRESENT_RE = re.compile(r"^P (\d+) draws=(\d+)$")
PID_RE = re.compile(r"^# time=.* pid=(\d+)$")
PROXY_RE = re.compile(r"^# bea-d3d9-proxy v(\d+)$")


class AttributionFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class MatrixValue:
    slot: str
    values: tuple[str, ...]
    derived: bool


@dataclass(frozen=True)
class DrawObservation:
    frame: int
    draw: int
    camera_identity: str
    camera_values: dict[str, list[str]]
    draw_identity: str
    draw_key: dict[str, Any]
    mesh_identity: str
    mesh_key: dict[str, Any]
    detail_vector: tuple[int, ...]


@dataclass
class ParsedLog:
    observations: list[DrawObservation]
    presented_frames: set[int]
    excluded: dict[str, int]
    ambiguous_draws: list[tuple[int, str]]


@dataclass(frozen=True)
class StableWindow:
    frames: tuple[int, ...]
    draws: dict[str, DrawObservation]
    camera_values: dict[str, list[str]]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _identity(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _sha256_bytes(body.encode("ascii"))


def _fields(text: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in FIELD_RE.finditer(text)}


def _positive_int(value: Any, code: str, label: str) -> int:
    if isinstance(value, bool):
        raise AttributionFailure(code, f"{label} must be a positive integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AttributionFailure(code, f"{label} must be a positive integer") from exc
    if parsed <= 0:
        raise AttributionFailure(code, f"{label} must be a positive integer")
    return parsed


def _exact_int(value: Any, expected: int, code: str, label: str) -> None:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AttributionFailure(code, f"{label} must be {expected}") from exc
    if parsed != expected:
        raise AttributionFailure(code, f"{label} must be {expected}, got {parsed}")


def _require_bool(value: Any, expected: bool, code: str, label: str) -> None:
    if value is not expected:
        raise AttributionFailure(code, f"{label} must be {str(expected).lower()}")


def _require_sha(value: Any, code: str, label: str) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value.lower()):
        raise AttributionFailure(code, f"{label} must be a 64-digit SHA-256")
    return value.lower()


def _require_mapping(value: Any, code: str, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AttributionFailure(code, f"{label} must be an object")
    return value


def _require_list(value: Any, code: str, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise AttributionFailure(code, f"{label} must be an array")
    return value


def _canonical_matrix(raw: str, label: str) -> tuple[str, ...]:
    parts = raw.split(",")
    if len(parts) != 16:
        raise AttributionFailure("malformed_matrix", f"{label} has {len(parts)} values; expected 16")
    result: list[str] = []
    for part in parts:
        try:
            value = Decimal(part)
        except InvalidOperation as exc:
            raise AttributionFailure("malformed_matrix", f"{label} contains non-decimal {part!r}") from exc
        if not value.is_finite():
            raise AttributionFailure("malformed_matrix", f"{label} contains non-finite {part!r}")
        if value == 0:
            value = Decimal(0)
        result.append(f"{value:.6f}")
    return tuple(result)


def _normalize_va(value: str) -> str:
    try:
        number = int(value, 16)
    except (TypeError, ValueError) as exc:
        raise AttributionFailure("invalid_row_va", f"invalid row VA {value!r}") from exc
    return f"0x{number:08X}"


def _normalize_bytes(value: Any, code: str, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) % 2 or not re.fullmatch(r"[0-9A-Fa-f]+", value):
        raise AttributionFailure(code, f"{label} must be an even-length hex byte string")
    return value.lower()


def _load_sidecar(path: Path, log_path: Path, role: str, row_va: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AttributionFailure(f"{role}_run_unreadable", f"{role} run sidecar is unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise AttributionFailure(f"{role}_run_not_object", f"{role} run sidecar must be an object")
    if data.get("schema") != RUN_SCHEMA:
        raise AttributionFailure(f"{role}_run_schema", f"{role} run schema must be {RUN_SCHEMA}")
    if data.get("role") != role:
        raise AttributionFailure(f"{role}_role_mismatch", f"{role} sidecar role is {data.get('role')!r}")
    if not isinstance(data.get("label"), str) or not data["label"]:
        raise AttributionFailure(f"{role}_label_missing", f"{role} label is required")
    _exact_int(data.get("level"), 100, f"{role}_level_not_100", f"{role} level")
    if data.get("quality") != "high":
        raise AttributionFailure(f"{role}_quality_not_high", f"{role} quality must be high")
    if data.get("game_args") != ["-skipfmv", "-level", "100"]:
        raise AttributionFailure(
            f"{role}_game_args_mismatch",
            f"{role} game_args must be exactly ['-skipfmv', '-level', '100']",
        )
    if not isinstance(data.get("checkpoint"), str) or not data["checkpoint"]:
        raise AttributionFailure(f"{role}_checkpoint_missing", f"{role} checkpoint is required")
    _positive_int(data.get("pid"), f"{role}_pid_invalid", f"{role} pid")

    row = _require_mapping(data.get("row"), f"{role}_row_missing", f"{role} row")
    actual_va = _normalize_va(str(row.get("va")))
    if actual_va != row_va:
        raise AttributionFailure(f"{role}_row_va_mismatch", f"{role} row VA {actual_va} != {row_va}")
    original = _normalize_bytes(row.get("original_bytes"), f"{role}_original_bytes", f"{role} original_bytes")
    patched = _normalize_bytes(row.get("patched_bytes"), f"{role}_patched_bytes", f"{role} patched_bytes")
    applied = _normalize_bytes(row.get("applied_bytes"), f"{role}_applied_bytes", f"{role} applied_bytes")
    if original == patched:
        raise AttributionFailure(f"{role}_row_no_delta", f"{role} original and patched bytes are identical")
    expected_applied = original if role == "stock" else patched
    if applied != expected_applied:
        raise AttributionFailure(
            f"{role}_applied_bytes_mismatch",
            f"{role} applied_bytes {applied} != expected {expected_applied}",
        )
    row.update({"va": actual_va, "original_bytes": original, "patched_bytes": patched, "applied_bytes": applied})

    hashes = _require_mapping(data.get("hashes"), f"{role}_hashes_missing", f"{role} hashes")
    for key in ("pristine", "product", "exe", "options", "log"):
        hashes[key] = _require_sha(hashes.get(key), f"{role}_{key}_hash_invalid", f"{role} hashes.{key}")
    if hashes["pristine"] != PRISTINE_SHA256:
        raise AttributionFailure(f"{role}_pristine_hash_mismatch", f"{role} pristine hash is not the named specimen")
    saves = _require_mapping(hashes.get("saves"), f"{role}_save_hashes_missing", f"{role} hashes.saves")
    if set(saves) != {"BEA 1.bes", "BEA 2.bes"}:
        raise AttributionFailure(f"{role}_save_set_mismatch", f"{role} must hash exactly BEA 1.bes and BEA 2.bes")
    for name, value in saves.items():
        saves[name] = _require_sha(value, f"{role}_save_hash_invalid", f"{role} {name}")
    actual_log_sha = _sha256_file(log_path)
    if hashes["log"] != actual_log_sha:
        raise AttributionFailure(
            f"{role}_log_hash_mismatch",
            f"{role} sidecar log hash {hashes['log']} != actual {actual_log_sha}",
        )
    if role == "stock" and hashes["exe"] != hashes["product"]:
        raise AttributionFailure("stock_exe_not_product", "stock executable hash must equal product baseline")
    if role == "staged" and hashes["exe"] == hashes["product"]:
        raise AttributionFailure("staged_exe_not_changed", "staged executable hash must differ from product baseline")

    stage_rows = _require_list(data.get("stage_rows"), f"{role}_stage_rows_missing", f"{role} stage_rows")
    if role == "stock":
        if stage_rows:
            raise AttributionFailure("stock_stage_rows_not_empty", "stock run must have no staged rows")
    else:
        if len(stage_rows) != 1 or not isinstance(stage_rows[0], dict):
            raise AttributionFailure("staged_row_count_not_one", "staged run must contain exactly one staged row")
        staged_row = stage_rows[0]
        staged_va = _normalize_va(str(staged_row.get("va")))
        staged_original = _normalize_bytes(
            staged_row.get("original_bytes"), "staged_stage_original_bytes", "staged stage row original_bytes"
        )
        staged_patched = _normalize_bytes(
            staged_row.get("patched_bytes"), "staged_stage_patched_bytes", "staged stage row patched_bytes"
        )
        staged_applied = _normalize_bytes(
            staged_row.get("applied_bytes"), "staged_stage_applied_bytes", "staged stage row applied_bytes"
        )
        if (staged_va, staged_original, staged_patched, staged_applied) != (
            row_va,
            original,
            patched,
            patched,
        ):
            raise AttributionFailure("staged_stage_row_mismatch", "staged row does not exactly match the named comparison row")

    capture = _require_mapping(data.get("capture"), f"{role}_capture_missing", f"{role} capture")
    _exact_int(capture.get("proxy_version"), 2, f"{role}_proxy_version_not_2", f"{role} proxy version")
    capture["firstframe"] = int(capture.get("firstframe"))
    if capture["firstframe"] < 0:
        raise AttributionFailure(f"{role}_capture_firstframe_negative", f"{role} firstframe must be non-negative")
    capture["maxframes"] = _positive_int(
        capture.get("maxframes"), f"{role}_capture_maxframes_not_positive", f"{role} capture maxframes"
    )
    _require_bool(capture.get("digest"), True, f"{role}_digest_disabled", f"{role} capture digest")
    _require_bool(capture.get("texhash"), True, f"{role}_texhash_disabled", f"{role} capture texhash")
    _require_bool(capture.get("strictcov"), True, f"{role}_strictcov_disabled", f"{role} capture strictcov")

    guard = _require_mapping(data.get("guard"), f"{role}_guard_missing", f"{role} guard")
    _require_bool(guard.get("copied_profile"), True, f"{role}_not_copied_profile", f"{role} copied_profile")
    _require_bool(guard.get("collision"), False, f"{role}_process_collision", f"{role} collision")
    _exact_int(
        guard.get("process_count_peak"), 1, f"{role}_process_count_not_one", f"{role} process_count_peak"
    )
    if guard.get("terminal_processes") != []:
        raise AttributionFailure(f"{role}_terminal_processes_nonzero", f"{role} terminal process list is not empty")
    _require_bool(guard.get("proxy_removed"), True, f"{role}_proxy_not_removed", f"{role} proxy_removed")

    data["_run_sha256"] = _sha256_bytes(raw)
    return data


def _parse_texture_identities(fields: dict[str, str]) -> tuple[list[dict[str, str]], str | None]:
    identities: list[dict[str, str]] = []
    texture_fields = sorted(
        (name for name in fields if re.fullmatch(r"tex\d+", name)),
        key=lambda name: int(name[3:]),
    )
    for name in texture_fields:
        value = fields[name]
        pointer = value.split(":", 1)[0].lower()
        if pointer in {"0x0", "0x00000000", "null"}:
            identities.append({"slot": name, "value": "null"})
            continue
        hash_match = re.search(r":h=([0-9A-Fa-f]{16})(?:$|:)", value)
        descriptor_match = re.search(r":([0-9]+x[0-9]+):fmt([0-9]+):lv([0-9]+):", value)
        if not hash_match or not descriptor_match:
            return [], "bound_texture_without_content_hash"
        identities.append(
            {
                "slot": name,
                "size": descriptor_match.group(1),
                "format": descriptor_match.group(2),
                "levels": descriptor_match.group(3),
                "content_hash": hash_match.group(1).upper(),
            }
        )
    if not identities:
        return [], "texture_state_missing"
    return identities, None


def _stream_stride(fields: dict[str, str]) -> int | None:
    value = fields.get("s0")
    if value is None:
        return None
    match = re.search(r"stride=(\d+)", value)
    return int(match.group(1)) if match else None


def _object_space_fvf(raw: str | None) -> bool:
    if raw is None or raw == "?":
        return False
    try:
        value = int(raw, 16)
    except ValueError:
        return False
    position = value & 0xE
    return position != 0x4 and position in {0x2, 0x6, 0x8, 0xA, 0xC, 0xE}


def _canonical_tfactor(fields: dict[str, str], role: str, frame: int, draw: int) -> str:
    raw = fields.get("tfactor")
    if raw is None:
        raise AttributionFailure(
            f"{role}_tfactor_missing",
            f"{role} draw {frame}:{draw} has no texture factor",
        )
    match = re.fullmatch(r"0x([0-9A-Fa-f]{8})~?", raw)
    if not match:
        raise AttributionFailure(
            f"{role}_tfactor_invalid",
            f"{role} draw {frame}:{draw} has invalid texture factor {raw!r}",
        )
    return f"0x{match.group(1).upper()}"


def _reject_untracked_matrices(fields: dict[str, str], role: str, frame: int, draw: int) -> None:
    raw = fields.get("mtxuntracked")
    if raw is None:
        return
    if not re.fullmatch(r"[0-9]+", raw):
        raise AttributionFailure(
            f"{role}_mtxuntracked_invalid",
            f"{role} draw {frame}:{draw} has invalid untracked-matrix count {raw!r}",
        )
    if int(raw) != 0:
        raise AttributionFailure(
            f"{role}_mtxuntracked_nonzero",
            f"{role} draw {frame}:{draw} has {raw} untracked matrices",
        )


def _matrix_for_draw(
    matrices: dict[int, MatrixValue], raw_id: str | None, role: str, kind: str
) -> MatrixValue:
    if raw_id is None or raw_id == "?":
        raise AttributionFailure(f"{role}_unknown_matrix", f"{role} draw has unknown {kind} matrix")
    try:
        matrix_id = int(raw_id)
    except ValueError as exc:
        raise AttributionFailure(f"{role}_unknown_matrix", f"{role} draw has invalid {kind} id {raw_id!r}") from exc
    if matrix_id == 0:
        raise AttributionFailure(f"{role}_default_matrix", f"{role} draw uses default identity for {kind}")
    if matrix_id not in matrices:
        raise AttributionFailure(f"{role}_missing_matrix", f"{role} draw references missing matrix id {matrix_id}")
    matrix = matrices[matrix_id]
    if matrix.derived:
        raise AttributionFailure(f"{role}_derived_matrix", f"{role} {kind} matrix id {matrix_id} is multiply-derived")
    return matrix


def _texture_transform_for_draw(
    matrices: dict[int, MatrixValue],
    fields: dict[str, str],
    role: str,
    frame: int,
    draw: int,
) -> dict[str, Any] | None:
    raw_matrix = fields.get("tm0")
    raw_flags = fields.get("tmflags")
    if raw_matrix is None and raw_flags is None:
        return None
    if raw_matrix is None:
        raise AttributionFailure(
            f"{role}_texture_matrix_missing",
            f"{role} draw {frame}:{draw} has texture flags without tm0",
        )
    if raw_flags is None:
        raise AttributionFailure(
            f"{role}_texture_flags_missing",
            f"{role} draw {frame}:{draw} has tm0 without texture flags",
        )
    if not re.fullmatch(r"[0-9]+", raw_flags):
        raise AttributionFailure(
            f"{role}_texture_flags_invalid",
            f"{role} draw {frame}:{draw} has invalid texture flags {raw_flags!r}",
        )
    flags = int(raw_flags)
    if flags not in {1, 2, 3, 4, 257, 258, 259, 260}:
        raise AttributionFailure(
            f"{role}_texture_flags_invalid",
            f"{role} draw {frame}:{draw} has unsupported texture flags {flags}",
        )
    matrix = _matrix_for_draw(matrices, raw_matrix, role, "texture")
    if matrix.slot != "tex0":
        raise AttributionFailure(
            f"{role}_texture_matrix_slot_mismatch",
            f"{role} draw {frame}:{draw} tm0 references {matrix.slot!r}, not 'tex0'",
        )
    return {"matrix": list(matrix.values), "flags": flags}


def _parse_log(path: Path, sidecar: dict[str, Any], role: str) -> ParsedLog:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise AttributionFailure(f"{role}_log_unreadable", f"{role} log is unreadable: {exc}") from exc
    lines = text.splitlines()
    proxy_version: int | None = None
    header_pid: int | None = None
    config: dict[str, str] | None = None
    gating: dict[str, str] | None = None
    matrices: dict[int, MatrixValue] = {}
    draws: dict[tuple[int, int], tuple[str, dict[str, str]]] = {}
    geometry: dict[tuple[int, int], dict[str, tuple[dict[str, str], str]]] = {}
    presented: set[int] = set()
    refusal_summary = False

    if any("FAULT-INJECTION" in line for line in lines):
        raise AttributionFailure(f"{role}_fault_injection_log", f"{role} log is stamped FAULT-INJECTION")
    if "# detach" not in lines:
        raise AttributionFailure(f"{role}_log_not_detached", f"{role} log has no # detach")
    nonempty_lines = [line for line in lines if line.strip()]
    if not nonempty_lines or nonempty_lines[-1] != "# detach":
        raise AttributionFailure(
            f"{role}_log_not_terminal_detach",
            f"{role} log has content after # detach",
        )

    for line in lines:
        match = PROXY_RE.match(line)
        if match:
            proxy_version = int(match.group(1))
            continue
        match = PID_RE.match(line)
        if match:
            header_pid = int(match.group(1))
            continue
        if line.startswith("# cfg "):
            config = _fields(line[6:])
            continue
        if line.startswith("# gating "):
            gating = _fields(line[9:])
            continue
        if line.startswith("# refusals total="):
            refusal_summary = True
            continue
        match = MATRIX_RE.match(line)
        if match:
            matrix_id = int(match.group(1))
            if matrix_id in matrices:
                raise AttributionFailure(f"{role}_duplicate_matrix_id", f"{role} repeats matrix id {matrix_id}")
            matrices[matrix_id] = MatrixValue(
                slot=match.group(2),
                values=_canonical_matrix(match.group(4), f"{role} matrix {matrix_id}"),
                derived=bool(match.group(3)),
            )
            continue
        match = DRAW_RE.match(line)
        if match:
            key = (int(match.group(1)), int(match.group(2)))
            if key in draws:
                raise AttributionFailure(f"{role}_duplicate_draw_record", f"{role} repeats draw {key}")
            draws[key] = (match.group(3), _fields(match.group(4)))
            continue
        match = GEOM_RE.match(line)
        if match:
            key = (int(match.group(1)), int(match.group(2)))
            kind = match.group(3)
            draw_geometry = geometry.setdefault(key, {})
            if kind in draw_geometry:
                raise AttributionFailure(
                    f"{role}_duplicate_geometry_record",
                    f"{role} repeats {kind} digest for draw {key}",
                )
            draw_geometry[kind] = (_fields(match.group(4)), match.group(4))
            continue
        match = PRESENT_RE.match(line)
        if match:
            presented.add(int(match.group(1)))

    if proxy_version != 2:
        raise AttributionFailure(f"{role}_log_proxy_version_not_2", f"{role} log proxy version is {proxy_version!r}")
    if header_pid != int(sidecar["pid"]):
        raise AttributionFailure(f"{role}_pid_mismatch", f"{role} log pid {header_pid!r} != sidecar pid {sidecar['pid']}")
    if config is None:
        raise AttributionFailure(f"{role}_config_header_missing", f"{role} log has no # cfg header")
    if gating is None:
        raise AttributionFailure(f"{role}_gating_header_missing", f"{role} log has no # gating header")
    if not refusal_summary:
        raise AttributionFailure(
            f"{role}_refusal_summary_missing", f"{role} log has no # refusals summary"
        )
    expected_capture = sidecar["capture"]
    expected_config = {
        "firstframe": str(expected_capture["firstframe"]),
        "maxframes": str(expected_capture["maxframes"]),
        "strictcov": "1",
    }
    for key, expected in expected_config.items():
        if config.get(key) != expected:
            raise AttributionFailure(
                f"{role}_log_{key}_mismatch",
                f"{role} log {key}={config.get(key)!r}; expected {expected}",
            )
    for key in ("digest", "texhash"):
        if gating.get(key) != "1":
            raise AttributionFailure(f"{role}_log_{key}_disabled", f"{role} log gating {key} must be 1")

    excluded: dict[str, int] = {}
    observations: list[DrawObservation] = []

    def exclude(reason: str) -> None:
        excluded[reason] = excluded.get(reason, 0) + 1

    for (frame, draw), (kind, fields) in sorted(draws.items()):
        if frame not in presented:
            exclude("draw_without_present")
            continue
        if kind not in {"DP", "DIP"}:
            exclude("non_buffer_draw")
            continue
        if not _object_space_fvf(fields.get("fvf")):
            exclude("non_object_space_or_unknown_fvf")
            continue
        if any(fields.get(name, "").lower() not in {"0x0", "0x00000000"} for name in ("decl", "vs", "ps")):
            exclude("unidentified_shader_or_declaration")
            continue

        texture_factor = _canonical_tfactor(fields, role, frame, draw)
        _reject_untracked_matrices(fields, role, frame, draw)

        view = _matrix_for_draw(matrices, fields.get("v"), role, "view")
        projection = _matrix_for_draw(matrices, fields.get("p"), role, "projection")
        world = _matrix_for_draw(matrices, fields.get("w"), role, "world")
        if view.slot != "view" or projection.slot != "proj" or world.slot != "world0":
            raise AttributionFailure(
                f"{role}_matrix_slot_mismatch",
                f"{role} draw {frame}:{draw} references wrong transform slots",
            )
        texture_transform = _texture_transform_for_draw(matrices, fields, role, frame, draw)
        camera_values = {"view": list(view.values), "projection": list(projection.values)}
        camera_identity = _identity(camera_values)

        textures, texture_error = _parse_texture_identities(fields)
        if texture_error:
            exclude(texture_error)
            continue
        stride = _stream_stride(fields)
        if stride is None:
            exclude("stream0_stride_missing")
            continue
        geoms = geometry.get((frame, draw), {})
        required_geoms = ("vb", "ib") if kind == "DIP" else ("vb",)
        if any(required not in geoms for required in required_geoms):
            exclude("geometry_digest_missing")
            continue
        if any(" PROVISIONAL" in geoms[required][1] for required in required_geoms):
            exclude("provisional_geometry_digest")
            continue

        try:
            primc = int(fields["primc"])
            verts = int(fields["verts"])
        except (KeyError, ValueError) as exc:
            raise AttributionFailure(
                f"{role}_draw_counts_invalid", f"{role} draw {frame}:{draw} has invalid primc/verts"
            ) from exc
        vb = geoms["vb"][0]
        ib = geoms.get("ib", ({}, ""))[0]
        for geom_kind, geom_fields in (("vb", vb), *(([("ib", ib)]) if kind == "DIP" else [])):
            required = ("n", "bytes", "h", "stride") if geom_kind == "vb" else ("n", "bytes", "h", "esz")
            if any(name not in geom_fields for name in required):
                raise AttributionFailure(
                    f"{role}_{geom_kind}_digest_incomplete",
                    f"{role} draw {frame}:{draw} {geom_kind} digest lacks {required}",
                )
            if not HEX16_RE.fullmatch(geom_fields["h"]):
                raise AttributionFailure(
                    f"{role}_{geom_kind}_hash_invalid",
                    f"{role} draw {frame}:{draw} has invalid {geom_kind} hash",
                )
        if int(vb["stride"]) != stride:
            raise AttributionFailure(
                f"{role}_stride_mismatch", f"{role} draw {frame}:{draw} D/G stride mismatch"
            )

        material_names = (
            "ab", "sb", "db", "bop", "at", "aref", "afunc", "z", "zw", "zf",
            "cull", "lit", "fog", "s0.cop", "s0.aop", "s1.cop", "s1.aop",
            "s0.addr", "s0.filt", "vp",
        )
        if any(name not in fields or "?" in fields[name] for name in material_names):
            exclude("unknown_material_state")
            continue
        draw_key = {
            "world": list(world.values),
            "textures": textures,
            "kind": kind,
            "primitive": fields.get("prim"),
            "fvf": fields.get("fvf", "").upper(),
            "stride": stride,
            "texture_factor": texture_factor,
            "texture_transform": texture_transform,
            "material": {name: fields[name] for name in material_names},
        }
        draw_identity = _identity(draw_key)
        vb_key = {
            "count": int(vb["n"]),
            "bytes": int(vb["bytes"]),
            "hash": vb["h"].upper(),
            "stride": int(vb["stride"]),
        }
        ib_key: dict[str, Any] | None = None
        if kind == "DIP":
            ib_key = {
                "count": int(ib["n"]),
                "bytes": int(ib["bytes"]),
                "hash": ib["h"].upper(),
                "element_size": int(ib["esz"]),
            }
        mesh_key = {
            "kind": kind,
            "primitive": fields.get("prim"),
            "primitive_count": primc,
            "vertex_count": verts,
            "vb": vb_key,
            "ib": ib_key,
        }
        mesh_identity = _identity(mesh_key)
        detail_vector = (
            primc,
            verts,
            ib_key["count"] if ib_key else 0,
            vb_key["count"],
            ib_key["bytes"] if ib_key else 0,
            vb_key["bytes"],
        )
        observations.append(
            DrawObservation(
                frame=frame,
                draw=draw,
                camera_identity=camera_identity,
                camera_values=camera_values,
                draw_identity=draw_identity,
                draw_key=draw_key,
                mesh_identity=mesh_identity,
                mesh_key=mesh_key,
                detail_vector=detail_vector,
            )
        )

    by_frame_identity: dict[tuple[int, str], int] = {}
    ambiguous: list[tuple[int, str]] = []
    for observation in observations:
        key = (observation.frame, observation.draw_identity)
        by_frame_identity[key] = by_frame_identity.get(key, 0) + 1
    for (frame, draw_identity), count in sorted(by_frame_identity.items()):
        if count > 1:
            ambiguous.append((frame, draw_identity))
    return ParsedLog(observations, presented, excluded, ambiguous)


def _stable_windows(parsed: ParsedLog, minimum: int) -> dict[str, StableWindow]:
    by_camera_frame: dict[str, dict[int, dict[str, DrawObservation]]] = {}
    camera_values: dict[str, dict[str, list[str]]] = {}
    for observation in parsed.observations:
        by_camera_frame.setdefault(observation.camera_identity, {}).setdefault(observation.frame, {})[
            observation.draw_identity
        ] = observation
        camera_values[observation.camera_identity] = observation.camera_values

    result: dict[str, StableWindow] = {}
    for camera, frames_map in sorted(by_camera_frame.items()):
        frame_numbers = sorted(frames_map)
        sequences: list[list[int]] = []
        for frame in frame_numbers:
            if not sequences or frame != sequences[-1][-1] + 1:
                sequences.append([frame])
            else:
                sequences[-1].append(frame)
        candidates: list[StableWindow] = []
        for sequence in sequences:
            if len(sequence) < minimum:
                continue
            for start in range(0, len(sequence) - minimum + 1):
                selected = sequence[start : start + minimum]
                common = set(frames_map[selected[0]])
                for frame in selected[1:]:
                    common &= set(frames_map[frame])
                stable: dict[str, DrawObservation] = {}
                for draw_identity in sorted(common):
                    items = [frames_map[frame][draw_identity] for frame in selected]
                    if len({item.mesh_identity for item in items}) == 1:
                        stable[draw_identity] = items[0]
                if stable:
                    candidates.append(
                        StableWindow(tuple(selected), stable, camera_values[camera])
                    )
        if candidates:
            candidates.sort(key=lambda item: (-len(item.draws), item.frames))
            result[camera] = candidates[0]
    return result


def _detail_order(stock: tuple[int, ...], staged: tuple[int, ...]) -> str:
    if stock == staged:
        return "equal_counts"
    if all(right >= left for left, right in zip(stock, staged)) and any(
        right > left for left, right in zip(stock, staged)
    ):
        return "staged_higher"
    if all(left >= right for left, right in zip(stock, staged)) and any(
        left > right for left, right in zip(stock, staged)
    ):
        return "stock_higher"
    return "ambiguous"


def _failed_receipt(row_va: str, failure: AttributionFailure) -> dict[str, Any]:
    return {
        "schema": RECEIPT_SCHEMA,
        "ok": False,
        "row_va": row_va,
        "error_codes": [failure.code],
        "errors": [failure.message],
    }


def analyze_pair(
    stock_log: Path | str,
    stock_run: Path | str,
    staged_log: Path | str,
    staged_run: Path | str,
    *,
    row_va: str,
    min_stable_frames: int = 3,
    min_matched_draws: int = 1,
    camera_identity: str | None = None,
) -> dict[str, Any]:
    """Return a deterministic success or fail-closed receipt."""

    try:
        normalized_va = _normalize_va(row_va)
    except AttributionFailure as failure:
        return _failed_receipt(str(row_va), failure)
    try:
        minimum_frames = _positive_int(
            min_stable_frames, "min_stable_frames_not_positive", "min_stable_frames"
        )
        minimum_draws = _positive_int(
            min_matched_draws, "min_matched_draws_not_positive", "min_matched_draws"
        )
        stock_log_path = Path(stock_log)
        stock_run_path = Path(stock_run)
        staged_log_path = Path(staged_log)
        staged_run_path = Path(staged_run)
        stock_meta = _load_sidecar(stock_run_path, stock_log_path, "stock", normalized_va)
        staged_meta = _load_sidecar(staged_run_path, staged_log_path, "staged", normalized_va)

        if stock_meta["checkpoint"] != staged_meta["checkpoint"]:
            raise AttributionFailure("checkpoint_name_mismatch", "stock and staged checkpoint names differ")
        stock_row = stock_meta["row"]
        staged_row = staged_meta["row"]
        for name in ("va", "original_bytes", "patched_bytes"):
            if stock_row[name] != staged_row[name]:
                raise AttributionFailure("row_contract_mismatch", f"stock and staged row {name} differs")
        for name in ("pristine", "product", "options", "saves"):
            if stock_meta["hashes"][name] != staged_meta["hashes"][name]:
                raise AttributionFailure(f"shared_{name}_hash_mismatch", f"stock and staged {name} hashes differ")

        parsed_stock = _parse_log(stock_log_path, stock_meta, "stock")
        parsed_staged = _parse_log(staged_log_path, staged_meta, "staged")
        if parsed_stock.ambiguous_draws:
            raise AttributionFailure(
                "stock_ambiguous_draw_identity",
                f"stock has duplicate draw anchor in frame {parsed_stock.ambiguous_draws[0][0]}",
            )
        if parsed_staged.ambiguous_draws:
            raise AttributionFailure(
                "staged_ambiguous_draw_identity",
                f"staged has duplicate draw anchor in frame {parsed_staged.ambiguous_draws[0][0]}",
            )
        if not parsed_stock.observations:
            raise AttributionFailure(
                "no_attributable_stock_draws",
                f"stock has no attributable world draws; exclusions={parsed_stock.excluded}",
            )
        if not parsed_staged.observations:
            raise AttributionFailure(
                "no_attributable_staged_draws",
                f"staged has no attributable world draws; exclusions={parsed_staged.excluded}",
            )

        stock_windows = _stable_windows(parsed_stock, minimum_frames)
        staged_windows = _stable_windows(parsed_staged, minimum_frames)
        common = sorted(set(stock_windows) & set(staged_windows))
        if camera_identity is not None:
            requested = camera_identity.lower()
            common = [candidate for candidate in common if candidate.lower() == requested]
            if not common:
                raise AttributionFailure(
                    "requested_camera_not_stable",
                    f"requested camera identity {camera_identity} is not stable in both runs",
                )
        if not common:
            raise AttributionFailure(
                "no_common_stable_camera",
                f"no common camera holds for {minimum_frames} consecutive frames",
            )

        ranked: list[tuple[int, str, list[str]]] = []
        for candidate in common:
            matched = sorted(set(stock_windows[candidate].draws) & set(staged_windows[candidate].draws))
            ranked.append((len(matched), candidate, matched))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        best_count = ranked[0][0]
        if best_count < minimum_draws:
            raise AttributionFailure(
                "no_matched_draws",
                f"best common camera has {best_count} matched draws; need {minimum_draws}",
            )
        tied = [item for item in ranked if item[0] == best_count]
        if len(tied) > 1 and camera_identity is None:
            raise AttributionFailure(
                "ambiguous_common_camera",
                f"{len(tied)} stable cameras tie at {best_count} matched draws; select one explicitly",
            )
        _, selected_camera, matched_ids = ranked[0]
        stock_window = stock_windows[selected_camera]
        staged_window = staged_windows[selected_camera]

        matches: list[dict[str, Any]] = []
        changed = 0
        detail_orders: list[str] = []
        for draw_identity in matched_ids:
            stock_observation = stock_window.draws[draw_identity]
            staged_observation = staged_window.draws[draw_identity]
            geometry_changed = stock_observation.mesh_identity != staged_observation.mesh_identity
            if geometry_changed:
                changed += 1
            order = _detail_order(stock_observation.detail_vector, staged_observation.detail_vector)
            if geometry_changed:
                detail_orders.append(order)
            matches.append(
                {
                    "draw_identity": draw_identity,
                    "draw_key": stock_observation.draw_key,
                    "geometry_changed": geometry_changed,
                    "detail_order": order,
                    "stock": {
                        "mesh_identity": stock_observation.mesh_identity,
                        "mesh_key": stock_observation.mesh_key,
                    },
                    "staged": {
                        "mesh_identity": staged_observation.mesh_identity,
                        "mesh_key": staged_observation.mesh_key,
                    },
                }
            )

        if changed == 0:
            verdict = "no_geometry_delta_at_matched_camera"
        elif detail_orders and all(order == "staged_higher" for order in detail_orders):
            verdict = "staged_finer_geometry_at_matched_camera"
        elif detail_orders and all(order == "stock_higher" for order in detail_orders):
            verdict = "stock_finer_geometry_at_matched_camera"
        else:
            verdict = "geometry_delta_detail_order_ambiguous"

        return {
            "schema": RECEIPT_SCHEMA,
            "ok": True,
            "row": {
                "va": normalized_va,
                "original_bytes": stock_row["original_bytes"],
                "patched_bytes": stock_row["patched_bytes"],
            },
            "checkpoint": {
                "name": stock_meta["checkpoint"],
                "level": 100,
                "camera_identity": selected_camera,
                "camera_values": stock_window.camera_values,
                "minimum_consecutive_frames": minimum_frames,
                "stock_frames": list(stock_window.frames),
                "staged_frames": list(staged_window.frames),
            },
            "inputs": {
                "stock": {
                    "label": stock_meta["label"],
                    "pid": stock_meta["pid"],
                    "exe_sha256": stock_meta["hashes"]["exe"],
                    "log_sha256": stock_meta["hashes"]["log"],
                    "run_sha256": stock_meta["_run_sha256"],
                },
                "staged": {
                    "label": staged_meta["label"],
                    "pid": staged_meta["pid"],
                    "exe_sha256": staged_meta["hashes"]["exe"],
                    "log_sha256": staged_meta["hashes"]["log"],
                    "run_sha256": staged_meta["_run_sha256"],
                },
                "shared": {
                    "pristine_sha256": stock_meta["hashes"]["pristine"],
                    "product_sha256": stock_meta["hashes"]["product"],
                    "options_sha256": stock_meta["hashes"]["options"],
                    "save_sha256": stock_meta["hashes"]["saves"],
                },
            },
            "excluded_draws": {
                "stock": dict(sorted(parsed_stock.excluded.items())),
                "staged": dict(sorted(parsed_staged.excluded.items())),
            },
            "summary": {
                "matched_draws": len(matches),
                "changed_meshes": changed,
                "unchanged_meshes": len(matches) - changed,
            },
            "matched_draws": matches,
            "verdict": verdict,
        }
    except AttributionFailure as failure:
        return _failed_receipt(normalized_va, failure)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        failure = AttributionFailure("unexpected_input_shape", f"input rejected: {type(exc).__name__}: {exc}")
        return _failed_receipt(normalized_va, failure)


def _write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(body, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-log", required=True, type=Path)
    parser.add_argument("--stock-run", required=True, type=Path)
    parser.add_argument("--staged-log", required=True, type=Path)
    parser.add_argument("--staged-run", required=True, type=Path)
    parser.add_argument("--row-va", required=True)
    parser.add_argument("--min-stable-frames", type=int, default=3)
    parser.add_argument("--min-matched-draws", type=int, default=1)
    parser.add_argument("--camera-identity")
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    receipt = analyze_pair(
        args.stock_log,
        args.stock_run,
        args.staged_log,
        args.staged_run,
        row_va=args.row_va,
        min_stable_frames=args.min_stable_frames,
        min_matched_draws=args.min_matched_draws,
        camera_identity=args.camera_identity,
    )
    _write_receipt(args.output, receipt)
    if receipt["ok"]:
        print(
            f"PASS {receipt['row']['va']}: {receipt['verdict']}; "
            f"camera={receipt['checkpoint']['camera_identity']} "
            f"matched={receipt['summary']['matched_draws']}"
        )
        return 0
    print(f"FAIL {receipt['row_va']}: {receipt['error_codes'][0]}: {receipt['errors'][0]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
