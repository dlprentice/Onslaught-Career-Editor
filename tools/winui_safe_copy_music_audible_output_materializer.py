#!/usr/bin/env python3
"""Materialize a sanitized music audible-output proof from private raw artifacts.

This tool does not launch BEA and does not infer proof from a hand-authored
final JSON blob. It translates explicit private raw files into the public-safe
`winui-safe-copy-music-audible-output-proof.v1` shape, then immediately runs the
final checker against the generated object.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import struct
import sys
from pathlib import Path
from typing import Any

import winui_safe_copy_music_audible_output_two_run_harness_check as final_check
import winui_safe_copy_music_capture_source_correlation_check as capture_correlation


SCHEMA = "winui-safe-copy-music-audible-output-proof.v1"
TIMELINE_SCHEMA = "winui-safe-copy-music-cdb-decode-timeline.v1"
SOURCE_MUSIC_SAFETY_SCHEMA = "winui-safe-copy-source-music-safety.v1"
NO_BEA_CENSUS_SCHEMA = "winui-safe-copy-no-bea-process-census.v1"
LIVE_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
AUDIO_SCHEMA = "audio-loopback-capture.v1"
TIMESTAMP_SOURCE = "timestamped-cdb-log"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
SELECTION_ID = 2
BASE_PATCH_KEYS = {"force_windowed", "resolution_gate"}
UTC_PREFIX_RE = re.compile(r"^\s*(?:\[)?(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)(?:\])?\s+")
FLOAT_EPSILON = 0.000001
MUSIC_PROVENANCE_WRAPPER = "cgame-wrapper"
MUSIC_PROVENANCE_RESTART_LOOP_DIRECT = "cgame-restart-loop-direct"
ACCEPTED_MUSIC_PROVENANCE = {MUSIC_PROVENANCE_WRAPPER, MUSIC_PROVENANCE_RESTART_LOOP_DIRECT}
C_GAME_RESTART_LOOP_DIRECT_MUSIC_RETURN = 0x0046E0BF

RAW_OUTPUT_KEYS = {
    "device",
    "devicestableid",
    "outputwav",
    "outputjson",
    "sourcepath",
    "sourcepaths",
    "cdbpath",
    "cdbLogPath".lower(),
    "logpath",
    "targetgameroot",
    "executablepath",
    "manifestpath",
    "workingdirectory",
}


class MaterializerError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MaterializerError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing JSON input: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON input must be an object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left.resolve())) == os.path.normcase(str(right.resolve()))


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def bool_at(value: dict[str, Any], key: str) -> bool:
    child = value.get(key)
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return bool(child)


def int_at(value: dict[str, Any], key: str) -> int:
    child = value.get(key)
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def string_at(value: dict[str, Any], key: str) -> str:
    child = value.get(key)
    require(isinstance(child, str) and child, f"Missing string: {key}")
    return str(child)


def utc_at(value: dict[str, Any], key: str) -> dt.datetime:
    child = string_at(value, key)
    require(child.endswith("Z") or child.endswith("+00:00"), f"{key} must be a UTC timestamp.")
    try:
        parsed = dt.datetime.fromisoformat(child.removesuffix("Z") + "+00:00" if child.endswith("Z") else child)
    except ValueError as exc:
        raise MaterializerError(f"Invalid UTC timestamp {key}: {child}") from exc
    return parsed.astimezone(dt.timezone.utc)


def format_utc(value: dt.datetime) -> str:
    value = value.astimezone(dt.timezone.utc)
    if value.microsecond:
        text = value.isoformat(timespec="milliseconds")
    else:
        text = value.isoformat(timespec="seconds")
    return text.replace("+00:00", "Z")


def normalized_key(value: str) -> str:
    return value.replace("_", "").replace("-", "").lower()


def has_forbidden_output_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if normalized_key(str(key)) in RAW_OUTPUT_KEYS:
                return True
            if has_forbidden_output_key(child):
                return True
    elif isinstance(value, list):
        return any(has_forbidden_output_key(item) for item in value)
    return False


def has_private_path_text(value: Any) -> bool:
    if isinstance(value, dict):
        return any(has_private_path_text(child) for child in value.values())
    if isinstance(value, list):
        return any(has_private_path_text(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return (
            ":\\" in value
            or ":/" in value
            or "program files" in lowered
            or "steamapps" in lowered
            or "onslaughtruntimeproofarchive" in lowered
            or str(Path(__file__).resolve().parents[1]).lower() in lowered
        )
    return False


def validate_no_symlink_or_reparse(path: Path) -> None:
    resolved = path.resolve()
    for candidate in (resolved, *resolved.parents):
        if candidate.is_symlink():
            raise MaterializerError(f"Refusing symlinked materializer path: {candidate}")
        attrs = getattr(candidate.stat(), "st_file_attributes", 0) if candidate.exists() else 0
        if attrs & 0x400:
            raise MaterializerError(f"Refusing reparse-point materializer path: {candidate}")


def validate_common_input_root(paths: list[Path]) -> Path:
    resolved = [path.resolve() for path in paths]
    for path in resolved:
        validate_no_symlink_or_reparse(path)
    common = Path(os.path.commonpath([str(path.parent) for path in resolved]))
    require(len(common.parts) >= 3, "Materializer inputs must share a non-root private proof directory.")
    return common


def load_inputs(paths: list[Path]) -> Path:
    common = validate_common_input_root(paths)
    for path in paths:
        require(path.is_file(), f"Missing materializer input: {path}")
    return common


def validate_output_path(output: Path, input_root: Path) -> None:
    validate_no_symlink_or_reparse(output.parent)
    require(is_relative_to(output, input_root), "Materialized output must stay inside the private raw input bundle.")
    require(output.suffix.lower() == ".json", "Materialized output must be a JSON file.")


def path_mentions_target(path_text: str) -> bool:
    return path_text.replace("/", "\\").lower().endswith(TARGET.lower())


def parse_timestamped_line(line: str) -> dt.datetime | None:
    match = UTC_PREFIX_RE.match(line)
    if not match:
        return None
    raw = match.group("ts")
    try:
        parsed = dt.datetime.fromisoformat(raw.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise MaterializerError(f"Invalid CDB row timestamp: {raw}") from exc
    return parsed.astimezone(dt.timezone.utc)


def append_timestamp(times: list[dt.datetime], line: str, label: str) -> None:
    parsed = parse_timestamped_line(line)
    require(parsed is not None, f"CDB {label} row is not timestamped.")
    times.append(parsed)


def parse_cdb_log(log_path: Path) -> dict[str, Any]:
    require(log_path.is_file(), f"CDB log not found: {log_path}")
    game_music: list[str] = []
    play_selection: list[str] = []
    restart_loop_direct_rows: list[dict[str, int]] = []
    kick_paths: list[str] = []
    open_paths: list[str] = []
    decode_requests: list[int] = []
    row_times: list[dt.datetime] = []
    decode_times: list[dt.datetime] = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if match := re.search(r"CGame__PlayMusicForCurrentLevel .*? level=(\d+) ", line, re.IGNORECASE):
            game_music.append(match.group(1))
            append_timestamp(row_times, line, "PlayMusicForCurrentLevel")
        if match := re.search(r"CMusic__PlaySelection entry .*? selection=(-?\d+) ", line, re.IGNORECASE):
            play_selection.append(match.group(1))
            append_timestamp(row_times, line, "PlaySelection")
        if match := re.search(
            r"CMusic__PlaySelection(?: entry|Caller).*? caller=([0-9a-fA-F]+).*? "
            r"globalLevel=(-?\d+) .*? selection=(-?\d+) ",
            line,
            re.IGNORECASE,
        ):
            caller = int(match.group(1), 16)
            global_level = int(match.group(2))
            selection = int(match.group(3))
            if (
                caller == C_GAME_RESTART_LOOP_DIRECT_MUSIC_RETURN
                and global_level == LEVEL_ID
                and selection == SELECTION_ID
            ):
                restart_loop_direct_rows.append(
                    {
                        "caller": caller,
                        "globalLevel": global_level,
                        "selection": selection,
                    }
                )
                append_timestamp(row_times, line, "RestartLoopDirectMusicSelection")
        if match := re.search(r"PCPlatform__KickAsyncMusicStreamRead path=(.*?\.ogg|<[^>]+>)", line, re.IGNORECASE):
            kick_paths.append(match.group(1))
            append_timestamp(row_times, line, "KickAsyncMusicStreamRead")
        if match := re.search(r"COggFileRead__OpenFileAndPrimeDecoder .*? path=(.*?\.ogg|<[^>]+>)", line, re.IGNORECASE):
            open_paths.append(match.group(1))
            append_timestamp(row_times, line, "OpenFileAndPrimeDecoder")
        if match := re.search(r"COggFileRead__ReadDecodedPcm .*? request=(\d+) ", line, re.IGNORECASE):
            decode_requests.append(int(match.group(1)))
            parsed = parse_timestamped_line(line)
            require(parsed is not None, "CDB decoded PCM row is not timestamped.")
            row_times.append(parsed)
            decode_times.append(parsed)
    wrapper_observed = any(int(value) == LEVEL_ID for value in game_music)
    restart_loop_direct_observed = bool(restart_loop_direct_rows)
    require(
        wrapper_observed or restart_loop_direct_observed,
        "CDB log missing accepted CGame music-selection provenance.",
    )
    require(any(int(value) == SELECTION_ID for value in play_selection), "CDB log missing expected CMusic selection row.")
    require(any(path_mentions_target(path) for path in kick_paths), "CDB log missing expected async kick target path.")
    require(any(path_mentions_target(path) for path in open_paths), "CDB log missing expected Ogg open target path.")
    require(any(value > 0 for value in decode_requests), "CDB log missing positive decoded PCM request.")
    require(row_times, "CDB log did not provide timestamped evidence rows.")
    require(decode_times, "CDB log did not provide timestamped decoded PCM rows.")
    return {
        "gameMusicRows": len(game_music),
        "playSelectionRows": len(play_selection),
        "restartLoopDirectRows": len(restart_loop_direct_rows),
        "musicSelectionProvenance": (
            MUSIC_PROVENANCE_WRAPPER if wrapper_observed else MUSIC_PROVENANCE_RESTART_LOOP_DIRECT
        ),
        "playMusicForCurrentLevelObserved": wrapper_observed,
        "restartLoopDirectMusicSelectionObserved": restart_loop_direct_observed,
        "restartLoopDirectMusicReturn": f"0x{C_GAME_RESTART_LOOP_DIRECT_MUSIC_RETURN:08x}",
        "asyncKickRows": len(kick_paths),
        "oggOpenRows": len(open_paths),
        "oggReadRows": len(decode_requests),
        "firstEvidenceAt": min(row_times),
        "lastEvidenceAt": max(row_times),
        "firstDecodedPcmAt": min(decode_times),
        "lastDecodedPcmAt": max(decode_times),
    }


def cdb_log_path_from_live(live: dict[str, Any]) -> Path:
    observer = object_at(live, "cdbObserver")
    result = object_at(observer, "result")
    candidate = result.get("logPath") or observer.get("logPath")
    require(isinstance(candidate, str) and candidate, "Live artifact missing CDB log path.")
    return Path(candidate)


def validate_timeline(timeline_path: Path, live_path: Path, live: dict[str, Any], role: str) -> dict[str, Any]:
    timeline = read_json(timeline_path)
    require(timeline.get("schemaVersion") == TIMELINE_SCHEMA, f"{role} timeline schema changed.")
    require(timeline.get("role") == role, f"{role} timeline role mismatch.")
    require(timeline.get("timestampSource") == TIMESTAMP_SOURCE, f"{role} timeline timestamp source must be {TIMESTAMP_SOURCE}.")
    require(bool_at(timeline, "cdbLogTimestamped"), f"{role} timeline must assert timestamped CDB log input.")
    require(timeline.get("liveArtifactSha256") == sha256_file(live_path), f"{role} timeline not bound to live artifact.")
    log_path = cdb_log_path_from_live(live)
    raw_log_hash = sha256_file(log_path)
    timestamped_log_path = timeline.get("timestampedCdbLogPath")
    timestamped_log_hash = timeline.get("timestampedCdbLogSha256")
    raw_log_bound_hash = timeline.get("rawCdbLogSha256")
    if timestamped_log_path or timestamped_log_hash or raw_log_bound_hash:
        require(raw_log_bound_hash == raw_log_hash, f"{role} timeline not bound to raw live CDB log.")
        require(isinstance(timestamped_log_path, str) and timestamped_log_path, f"{role} timeline missing timestamped CDB log path.")
        parsed_log_path = Path(timestamped_log_path)
        require(parsed_log_path.is_file(), f"{role} timestamped CDB log is missing.")
        validate_no_symlink_or_reparse(parsed_log_path)
        require(is_relative_to(parsed_log_path, timeline_path.parent), f"{role} timestamped CDB log must stay beside the timeline sidecar.")
        parsed_log_hash = sha256_file(parsed_log_path)
        require(timestamped_log_hash == parsed_log_hash, f"{role} timeline not bound to timestamped CDB log.")
        require(timeline.get("cdbLogSha256") == parsed_log_hash, f"{role} timeline cdbLogSha256 must bind the timestamped CDB evidence log.")
    else:
        parsed_log_path = log_path
        require(timeline.get("cdbLogSha256") == raw_log_hash, f"{role} timeline not bound to CDB log.")
    parsed = parse_cdb_log(parsed_log_path)
    for key in {
        "exactPidCdbObserver",
        "playSelectionObserved",
        "asyncKickPathMatched",
        "oggOpenPathMatched",
        "decodedPcmPositiveRequestObserved",
    }:
        require(bool_at(timeline, key), f"{role} timeline missing {key}.")
    provenance = str(timeline.get("musicSelectionProvenance") or "")
    if not provenance and bool_at(timeline, "playMusicForCurrentLevelObserved"):
        provenance = MUSIC_PROVENANCE_WRAPPER
    require(provenance in ACCEPTED_MUSIC_PROVENANCE, f"{role} timeline music-selection provenance is not accepted.")
    if provenance == MUSIC_PROVENANCE_WRAPPER:
        require(bool_at(timeline, "playMusicForCurrentLevelObserved"), f"{role} wrapper provenance requires CGame wrapper observation.")
    if provenance == MUSIC_PROVENANCE_RESTART_LOOP_DIRECT:
        require(
            bool_at(timeline, "restartLoopDirectMusicSelectionObserved"),
            f"{role} restart-loop direct provenance requires the direct-call observation.",
        )
    require(
        provenance == parsed["musicSelectionProvenance"],
        f"{role} timeline provenance does not match timestamped CDB log.",
    )
    require(int_at(timeline, "levelId") == LEVEL_ID, f"{role} timeline level mismatch.")
    require(int_at(timeline, "selectionId") == SELECTION_ID, f"{role} timeline selection mismatch.")
    decode_start = utc_at(timeline, "decodeWindowStartUtc")
    decode_end = utc_at(timeline, "decodeWindowEndUtc")
    require(decode_start <= decode_end, f"{role} decode timeline is inverted.")
    require(parsed["firstDecodedPcmAt"] >= decode_start, f"{role} first decoded PCM row is before timeline window.")
    require(parsed["lastDecodedPcmAt"] <= decode_end, f"{role} decoded PCM row is after timeline window.")
    require(parsed["firstEvidenceAt"] >= decode_start, f"{role} first CDB evidence row is before timeline window.")
    require(parsed["lastEvidenceAt"] <= decode_end, f"{role} last CDB evidence row is after timeline window.")
    return {
        "exactPidCdbObserver": True,
        "levelId": LEVEL_ID,
        "selectionId": SELECTION_ID,
        "musicSelectionProvenance": provenance,
        "playMusicForCurrentLevelObserved": bool(provenance == MUSIC_PROVENANCE_WRAPPER),
        "restartLoopDirectMusicSelectionObserved": bool(provenance == MUSIC_PROVENANCE_RESTART_LOOP_DIRECT),
        "playSelectionObserved": True,
        "asyncKickPathMatched": True,
        "oggOpenPathMatched": True,
        "decodedPcmPositiveRequestObserved": True,
        "decodeWindowStartUtc": format_utc(decode_start),
        "decodeWindowEndUtc": format_utc(decode_end),
        "cdbRowCounts": parsed,
        "_decodeWindowStartAt": decode_start,
        "_decodeWindowEndAt": decode_end,
    }


def parse_riff_wave(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    require(len(data) >= 44, "raw WAV artifact is too small.")
    require(data[0:4] == b"RIFF" and data[8:12] == b"WAVE", "raw WAV artifact is not RIFF/WAVE.")
    offset = 12
    fmt_chunk: bytes | None = None
    data_chunk: bytes | None = None
    while offset + 8 <= len(data):
        chunk_id = data[offset : offset + 4]
        chunk_size = struct.unpack_from("<I", data, offset + 4)[0]
        chunk_start = offset + 8
        chunk_end = chunk_start + chunk_size
        require(chunk_end <= len(data), "raw WAV chunk extends past file end.")
        chunk = data[chunk_start:chunk_end]
        if chunk_id == b"fmt ":
            fmt_chunk = chunk
        elif chunk_id == b"data":
            data_chunk = chunk
        offset = chunk_end + (chunk_size % 2)
    require(fmt_chunk is not None, "raw WAV artifact missing fmt chunk.")
    require(data_chunk is not None, "raw WAV artifact missing data chunk.")
    require(len(fmt_chunk) >= 16, "raw WAV fmt chunk is too small.")
    audio_format, channels, sample_rate, _byte_rate, block_align, bits_per_sample = struct.unpack_from("<HHIIHH", fmt_chunk, 0)
    if audio_format == 0xFFFE and len(fmt_chunk) >= 40:
        audio_format = struct.unpack_from("<H", fmt_chunk, 24)[0]
    require(channels > 0, "raw WAV channel count must be positive.")
    require(sample_rate > 0, "raw WAV sample rate must be positive.")
    require(bits_per_sample in {16, 32}, "raw WAV bits-per-sample must be 16 or 32 for materializer validation.")
    bytes_per_sample = bits_per_sample // 8
    require(block_align >= bytes_per_sample, "raw WAV block alignment is invalid.")
    sample_count = len(data_chunk) // bytes_per_sample
    require(sample_count > 0, "raw WAV has no samples.")
    peak_abs = 0.0
    sum_squares = 0.0
    non_zero = 0
    for sample_offset in range(0, sample_count * bytes_per_sample, bytes_per_sample):
        if audio_format == 3 and bits_per_sample == 32:
            sample = struct.unpack_from("<f", data_chunk, sample_offset)[0]
            if not (sample == sample and abs(sample) != float("inf")):
                sample = 0.0
            sample = max(-1.0, min(1.0, float(sample)))
        elif audio_format == 1 and bits_per_sample == 16:
            sample = struct.unpack_from("<h", data_chunk, sample_offset)[0] / 32768.0
        elif audio_format == 1 and bits_per_sample == 32:
            sample = struct.unpack_from("<i", data_chunk, sample_offset)[0] / 2147483648.0
        else:
            raise MaterializerError("raw WAV encoding is not supported for materializer validation.")
        abs_sample = abs(sample)
        peak_abs = max(peak_abs, abs_sample)
        if abs_sample > FLOAT_EPSILON:
            non_zero += 1
        sum_squares += sample * sample
    rms = (sum_squares / sample_count) ** 0.5
    return {
        "dataBytes": len(data_chunk),
        "sampleRate": sample_rate,
        "channels": channels,
        "bitsPerSample": bits_per_sample,
        "sampleCount": sample_count,
        "nonZeroSampleCount": non_zero,
        "peakAbs": peak_abs,
        "rms": rms,
        "nonSilent": sample_count > 0 and peak_abs >= 0.001 and rms >= 0.0001,
    }


def require_number_close(actual: float, expected: float, label: str, tolerance: float = 0.000001) -> None:
    require(abs(actual - expected) <= tolerance, f"{label} does not match raw WAV analysis.")


def validate_live_runtime(live_path: Path, *, role: str, staged: bool, mute: bool) -> dict[str, Any]:
    live = read_json(live_path)
    require(live.get("schemaVersion") == LIVE_SCHEMA, f"{role} live artifact schema changed.")
    source = object_at(live, "source")
    require(bool_at(source, "installedHashUnchanged"), f"{role} installed BEA hash changed.")
    require(bool_at(source, "overrideHashUnchanged"), f"{role} clean override hash changed.")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), f"{role} source save/options changed.")
    patch_keys = {str(item) for item in list_at(object_at(live, "safeCopy"), "patchKeys")}
    require(BASE_PATCH_KEYS.issubset(patch_keys), f"{role} missing base patch keys.")
    launch = object_at(live, "launch")
    require(bool_at(launch, "observedAlive"), f"{role} live artifact did not observe copied BEA alive.")
    launch_args = [str(item) for item in list_at(launch, "arguments")]
    require("-skipfmv" in launch_args, f"{role} launch args missing -skipfmv.")
    require("-level" in launch_args and str(LEVEL_ID) in launch_args, f"{role} launch args missing level {LEVEL_ID}.")
    if mute:
        require("-nomusic" in launch_args or "-nosound" in launch_args, "mute control must use -nomusic or -nosound.")
    else:
        require("-nomusic" not in launch_args and "-nosound" not in launch_args, f"{role} must not disable music/sound.")
    baseline = object_at(live, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), f"{role} had preexisting BEA process.")
    require(bool_at(baseline, "noBeaAfterStop"), f"{role} left BEA running.")
    require(bool_at(object_at(live, "stop"), "Success"), f"{role} stop did not succeed.")
    music = live.get("musicReplacement")
    if staged:
        require(isinstance(music, dict), "staged positive live artifact must include music replacement.")
        require(music.get("MusicSwapPresetId") == PRESET_ID, "staged positive preset id changed.")
        require(music.get("TargetMusicFileName") == TARGET, "staged target changed.")
        require(music.get("SourceReplacementFileName") == REPLACEMENT, "staged replacement changed.")
        require(bool_at(music, "targetNowMatchesReplacement"), "staged target must match replacement.")
        require(bool_at(music, "backupMatchesOriginal"), "staged backup must match original.")
        require(bool_at(music, "SourceTargetHashUnchanged"), "staged source target hash changed.")
        require(bool_at(music, "SourceReplacementHashUnchanged"), "staged source replacement hash changed.")
    else:
        require(music is None, f"{role} must not include staged music replacement.")
    return {
        "payload": live,
        "patchKeys": sorted(patch_keys),
        "launchArguments": launch_args,
        "sourceBaseSafety": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
    }


def validate_source_music_safety(path: Path, live_path: Path, role: str) -> dict[str, bool]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == SOURCE_MUSIC_SAFETY_SCHEMA, f"{role} source music safety schema changed.")
    require(payload.get("role") == role, f"{role} source music safety role mismatch.")
    require(payload.get("liveArtifactSha256") == sha256_file(live_path), f"{role} source music safety not bound to live artifact.")
    require(payload.get("target") == TARGET, f"{role} source music safety target changed.")
    require(payload.get("replacement") == REPLACEMENT, f"{role} source music safety replacement changed.")
    for key in {
        "sourceTargetHashBefore",
        "sourceTargetHashAfter",
        "sourceReplacementHashBefore",
        "sourceReplacementHashAfter",
    }:
        value = string_at(payload, key)
        require(bool(re.fullmatch(r"[0-9a-fA-F]{64}", value)), f"{role} {key} is not a SHA-256 hex string.")
    require(bool_at(payload, "sourceTargetHashUnchanged"), f"{role} source target hash changed.")
    require(bool_at(payload, "sourceReplacementHashUnchanged"), f"{role} source replacement hash changed.")
    require(payload["sourceTargetHashBefore"].lower() == payload["sourceTargetHashAfter"].lower(), f"{role} source target hashes differ.")
    require(
        payload["sourceReplacementHashBefore"].lower() == payload["sourceReplacementHashAfter"].lower(),
        f"{role} source replacement hashes differ.",
    )
    return {
        "sourceTargetHashUnchanged": True,
        "sourceReplacementHashUnchanged": True,
    }


def source_safety_from_staged_music(staged_live: dict[str, Any]) -> dict[str, bool]:
    music = object_at(staged_live, "musicReplacement")
    return {
        "sourceTargetHashUnchanged": bool_at(music, "SourceTargetHashUnchanged"),
        "sourceReplacementHashUnchanged": bool_at(music, "SourceReplacementHashUnchanged"),
    }


def validate_audio(path: Path, role: str, *, require_non_silent: bool, timeline: dict[str, Any] | None) -> dict[str, Any]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == AUDIO_SCHEMA, f"{role} audio schema changed.")
    require(payload.get("status") == "captured", f"{role} audio capture did not complete.")
    require(payload.get("captureKind") == "wasapi-loopback", f"{role} unexpected capture kind.")
    calibration = payload.get("calibration")
    require(not (isinstance(calibration, dict) and calibration.get("played") is True), f"{role} calibration-tone capture is not accepted.")
    device = object_at(payload, "device")
    endpoint_id = string_at(device, "id")
    output_json = Path(string_at(payload, "outputJson"))
    output_wav = Path(string_at(payload, "outputWav"))
    raw_wav_hash = string_at(payload, "rawWavSha256").lower()
    require(bool(re.fullmatch(r"[0-9a-f]{64}", raw_wav_hash)), f"{role} rawWavSha256 is not a SHA-256 hex string.")
    require(same_path(output_json, path), f"{role} outputJson does not point at the audio artifact being materialized.")
    require(output_wav.is_file(), f"{role} raw WAV artifact is missing.")
    validate_no_symlink_or_reparse(output_wav)
    require(is_relative_to(output_wav, path.parent), f"{role} raw WAV artifact must stay beside its audio JSON.")
    raw_wav_size = output_wav.stat().st_size
    require(raw_wav_hash == sha256_file(output_wav), f"{role} rawWavSha256 does not match raw WAV artifact.")
    wav_stats = parse_riff_wave(output_wav)
    capture_start = utc_at(payload, "captureStartedUtc")
    capture_end = utc_at(payload, "captureEndedUtc")
    require(capture_start < capture_end, f"{role} audio capture window is not positive.")
    wave_format = object_at(payload, "waveFormat")
    stats = object_at(payload, "audioStats")
    non_silent = bool_at(stats, "nonSilent")
    if require_non_silent:
        require(non_silent, f"{role} must be non-silent.")
    if role in {"ambientNoBea", "muteControl"}:
        require(not non_silent, f"{role} must stay below non-silent threshold.")
    starts_before = True
    ends_after = True
    if timeline is not None:
        starts_before = capture_start <= timeline["_decodeWindowStartAt"]
        ends_after = capture_end >= timeline["_decodeWindowEndAt"]
        require(starts_before, f"{role} capture starts after CDB decode window.")
        require(ends_after, f"{role} capture ends before CDB decode window closes.")
    require(int_at(wave_format, "sampleRate") > 0, f"{role} sample rate must be positive.")
    require(int_at(wave_format, "channels") > 0, f"{role} channel count must be positive.")
    require(int_at(stats, "wavFileBytes") > 0, f"{role} WAV file bytes must be positive.")
    require(int_at(stats, "wavFileBytes") == raw_wav_size, f"{role} WAV byte count does not match raw artifact.")
    require(int_at(stats, "bytesRecorded") >= 0, f"{role} bytesRecorded must be present.")
    require(int_at(stats, "bytesRecorded") == wav_stats["dataBytes"], f"{role} bytesRecorded does not match raw WAV data length.")
    require(int_at(stats, "sampleCount") == wav_stats["sampleCount"], f"{role} sampleCount does not match raw WAV analysis.")
    require(int_at(wave_format, "sampleRate") == wav_stats["sampleRate"], f"{role} sample rate does not match raw WAV.")
    require(int_at(wave_format, "channels") == wav_stats["channels"], f"{role} channel count does not match raw WAV.")
    if isinstance(wave_format.get("bitsPerSample"), int):
        require(int_at(wave_format, "bitsPerSample") == wav_stats["bitsPerSample"], f"{role} bitsPerSample does not match raw WAV.")
    require_number_close(float(stats.get("peakAbs", 0.0)), float(wav_stats["peakAbs"]), f"{role} peakAbs")
    require_number_close(float(stats.get("rms", 0.0)), float(wav_stats["rms"]), f"{role} rms")
    require(non_silent == wav_stats["nonSilent"], f"{role} nonSilent does not match raw WAV analysis.")
    return {
        "schemaVersion": AUDIO_SCHEMA,
        "status": "captured",
        "captureKind": "wasapi-loopback",
        "boundedOutputArtifact": True,
        "startsBeforeExpectedMusicKick": starts_before,
        "endsAfterDecodeBegins": ends_after,
        "captureStartedUtc": format_utc(capture_start),
        "captureEndedUtc": format_utc(capture_end),
        "observedDurationMs": int_at(payload, "observedDurationMs"),
        "sanitizedEndpoint": {
            "endpointAlias": "default-render-endpoint",
            "endpointFingerprint": sha256_text(f"wasapi-loopback:{endpoint_id}"),
        },
        "waveFormat": {
            "sampleRate": int_at(wave_format, "sampleRate"),
            "channels": int_at(wave_format, "channels"),
            "bitsPerSample": wave_format.get("bitsPerSample"),
        },
        "audioStats": {
            "bytesRecorded": int_at(stats, "bytesRecorded"),
            "wavFileBytes": int_at(stats, "wavFileBytes"),
            "sampleCount": int_at(stats, "sampleCount"),
            "peakAbs": float(stats.get("peakAbs", 0.0)),
            "rms": float(stats.get("rms", 0.0)),
            "nonSilent": non_silent,
        },
        "_audioArtifactSha256": sha256_file(path),
        "_rawWavSha256": sha256_file(output_wav),
        "_captureStartAt": capture_start,
        "_captureEndAt": capture_end,
    }


def ensure_same_endpoint_and_format(audios: list[dict[str, Any]]) -> None:
    first_endpoint = object_at(audios[0], "sanitizedEndpoint")
    first_format = object_at(audios[0], "waveFormat")
    for audio in audios[1:]:
        endpoint = object_at(audio, "sanitizedEndpoint")
        wave_format = object_at(audio, "waveFormat")
        require(endpoint == first_endpoint, "Audio endpoint mismatch across proof captures.")
        require(wave_format.get("sampleRate") == first_format.get("sampleRate"), "Audio sample-rate mismatch.")
        require(wave_format.get("channels") == first_format.get("channels"), "Audio channel-count mismatch.")


def validate_ambient_census(path: Path, ambient_audio: dict[str, Any]) -> None:
    payload = read_json(path)
    require(payload.get("schemaVersion") == NO_BEA_CENSUS_SCHEMA, "Ambient no-BEA census schema changed.")
    require(payload.get("role") == "ambientNoBea", "Ambient no-BEA census role mismatch.")
    require(bool_at(payload, "noBeaProcessObserved"), "Ambient no-BEA census did not prove no BEA process.")
    require(payload.get("audioArtifactSha256") == ambient_audio["_audioArtifactSha256"], "Ambient no-BEA census is not bound to the ambient audio JSON.")
    require(payload.get("audioWavSha256") == ambient_audio["_rawWavSha256"], "Ambient no-BEA census is not bound to the ambient raw WAV.")
    census_start = utc_at(payload, "censusStartUtc")
    census_end = utc_at(payload, "censusEndUtc")
    require(census_start <= ambient_audio["_captureStartAt"], "Ambient no-BEA census starts after audio capture begins.")
    require(census_end >= ambient_audio["_captureEndAt"], "Ambient no-BEA census ends before audio capture ends.")


def build_music_replacement_summary(staged_live: dict[str, Any]) -> dict[str, Any]:
    music = object_at(staged_live, "musicReplacement")
    return {
        "presetId": PRESET_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "targetRelativePath": r"data\Music\BEA_04(Master).ogg",
        "targetNowMatchesReplacement": bool_at(music, "targetNowMatchesReplacement"),
        "backupMatchesOriginal": bool_at(music, "backupMatchesOriginal"),
    }


def strip_private_timeline_fields(timeline: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in timeline.items()
        if not key.startswith("_") and key != "cdbRowCounts"
    }


def strip_private_audio_fields(audio: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in audio.items() if not key.startswith("_")}


def materialize_from_paths(
    *,
    clean_live: Path,
    staged_live: Path,
    mute_live: Path,
    clean_timeline: Path,
    staged_timeline: Path,
    clean_source_music_safety: Path,
    mute_source_music_safety: Path,
    ambient_census: Path,
    ambient_audio: Path,
    clean_audio: Path,
    staged_audio: Path,
    mute_audio: Path,
    capture_source_correlation: Path,
    output: Path,
) -> dict[str, Any]:
    input_paths = [
        clean_live,
        staged_live,
        mute_live,
        clean_timeline,
        staged_timeline,
        clean_source_music_safety,
        mute_source_music_safety,
        ambient_census,
        ambient_audio,
        clean_audio,
        staged_audio,
        mute_audio,
        capture_source_correlation,
    ]
    input_root = load_inputs(input_paths)
    validate_output_path(output, input_root)

    clean = validate_live_runtime(clean_live, role="cleanBaseline", staged=False, mute=False)
    staged = validate_live_runtime(staged_live, role="stagedPositive", staged=True, mute=False)
    mute = validate_live_runtime(mute_live, role="muteControl", staged=False, mute=True)
    clean_timeline_payload = validate_timeline(clean_timeline, clean_live, clean["payload"], "cleanBaseline")
    staged_timeline_payload = validate_timeline(staged_timeline, staged_live, staged["payload"], "stagedPositive")
    clean_music_safety = validate_source_music_safety(clean_source_music_safety, clean_live, "cleanBaseline")
    mute_music_safety = validate_source_music_safety(mute_source_music_safety, mute_live, "muteControl")
    staged_music_safety = source_safety_from_staged_music(staged["payload"])

    ambient_audio_summary = validate_audio(ambient_audio, "ambientNoBea", require_non_silent=False, timeline=None)
    clean_audio_summary = validate_audio(clean_audio, "cleanBaseline", require_non_silent=True, timeline=clean_timeline_payload)
    staged_audio_summary = validate_audio(staged_audio, "stagedPositive", require_non_silent=True, timeline=staged_timeline_payload)
    mute_audio_summary = validate_audio(mute_audio, "muteControl", require_non_silent=False, timeline=None)
    validate_ambient_census(ambient_census, ambient_audio_summary)
    ensure_same_endpoint_and_format([ambient_audio_summary, clean_audio_summary, staged_audio_summary, mute_audio_summary])

    correlation_summary = capture_correlation.validate_artifact(read_json(capture_source_correlation))
    source_audio_correlation = correlation_summary["sourceAudioCorrelation"]
    input_bindings = correlation_summary["inputBindings"]
    require(input_bindings["cleanAudioJsonSha256"] == clean_audio_summary["_audioArtifactSha256"], "Capture-source correlation is not bound to clean audio JSON.")
    require(input_bindings["cleanAudioWavSha256"] == clean_audio_summary["_rawWavSha256"], "Capture-source correlation is not bound to clean raw WAV.")
    require(input_bindings["stagedAudioJsonSha256"] == staged_audio_summary["_audioArtifactSha256"], "Capture-source correlation is not bound to staged audio JSON.")
    require(input_bindings["stagedAudioWavSha256"] == staged_audio_summary["_rawWavSha256"], "Capture-source correlation is not bound to staged raw WAV.")
    require(
        source_audio_correlation.get("cleanBaselineBestMatch") == TARGET
        and source_audio_correlation.get("stagedPositiveBestMatch") == REPLACEMENT,
        "Capture-source correlation does not prove the expected target/replacement split.",
    )

    clean_launch = clean["launchArguments"]
    staged_launch = staged["launchArguments"]
    clean_patch_keys = clean["patchKeys"]
    staged_patch_keys = staged["patchKeys"]
    proof = {
        "schemaVersion": SCHEMA,
        "presetId": PRESET_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "levelId": LEVEL_ID,
        "runtimeAudibleOutputProof": True,
        "runs": {
            "cleanBaseline": {
                "role": "cleanBaseline",
                "levelId": LEVEL_ID,
                "patchKeys": clean_patch_keys,
                "launchArguments": clean_launch,
                "sourceSafety": {
                    **clean["sourceBaseSafety"],
                    **clean_music_safety,
                },
                "cdbSelectionDecode": strip_private_timeline_fields(clean_timeline_payload),
                "audioCapture": strip_private_audio_fields(clean_audio_summary),
                "musicReplacement": None,
            },
            "stagedPositive": {
                "role": "stagedPositive",
                "levelId": LEVEL_ID,
                "patchKeys": staged_patch_keys,
                "launchArguments": staged_launch,
                "sourceSafety": {
                    **staged["sourceBaseSafety"],
                    **staged_music_safety,
                },
                "cdbSelectionDecode": strip_private_timeline_fields(staged_timeline_payload),
                "audioCapture": strip_private_audio_fields(staged_audio_summary),
                "musicReplacement": build_music_replacement_summary(staged["payload"]),
            },
        },
        "negativeControls": {
            "ambientNoBea": {
                "role": "ambientNoBea",
                "noBeaProcessObserved": True,
                "audioCapture": strip_private_audio_fields(ambient_audio_summary),
            },
            "muteControl": {
                "role": "muteControl",
                "launchArguments": mute["launchArguments"],
                "notAcceptedAsAudibleProof": True,
                "sourceSafety": {
                    **mute["sourceBaseSafety"],
                    **mute_music_safety,
                },
                "audioCapture": strip_private_audio_fields(mute_audio_summary),
            },
        },
        "comparison": {
            "sameLevelAndLaunchArgsExceptMutation": clean_launch == staged_launch,
            "samePatchSetExceptMutation": clean_patch_keys == staged_patch_keys,
            "sameAudioEndpointAndFormat": True,
            "cleanAndPositiveHaveCdbEvidence": True,
            "positiveAudioTimeCorrelatedWithDecode": True,
            "positiveDiffersFromCleanBaseline": True,
            "muteControlNotAcceptedAsAudibleProof": True,
            "cleanBaselineRms": clean_audio_summary["audioStats"]["rms"],
            "stagedPositiveRms": staged_audio_summary["audioStats"]["rms"],
        },
        "sourceAudioCorrelation": source_audio_correlation,
        "nonClaims": [
            "not arbitrary external OGG compatibility",
            "not all music cues",
            "not loop behavior proof",
            "not volume behavior proof",
            "not gameplay parity",
            "not rebuild parity",
            "not no-noticeable-difference parity",
        ],
        "materializer": {
            "schemaVersion": "winui-safe-copy-music-audible-output-materializer.v1",
            "inputMode": "explicit-files",
            "rawAudioPublished": False,
            "privatePathsPublished": False,
            "rawEndpointIdentifiersPublished": False,
            "claimBoundary": "Sanitized materialization from private raw artifacts; no raw paths, raw endpoint ids, WAVs, or CDB logs are published.",
        },
    }
    require(bool_at(proof["comparison"], "sameLevelAndLaunchArgsExceptMutation"), "Clean/staged launch arguments differ beyond mutation.")
    require(bool_at(proof["comparison"], "samePatchSetExceptMutation"), "Clean/staged patch keys differ beyond mutation.")
    require(not has_forbidden_output_key(proof), "Materialized proof contains a forbidden raw/private key.")
    require(not has_private_path_text(proof), "Materialized proof contains private path-like text.")
    final_check.validate_artifact(proof)
    write_json(output, proof)
    return proof


def sanitize_error_message(message: str) -> str:
    message = re.sub(r"[A-Za-z]:[\\/][^\r\n\"']+", "<path>", message)
    message = re.sub(r"\\\\[^\\/\s]+\\[^\r\n\"']+", "<unc-path>", message)
    return message


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-live", type=Path, required=True)
    parser.add_argument("--staged-live", type=Path, required=True)
    parser.add_argument("--mute-live", type=Path, required=True)
    parser.add_argument("--clean-timeline", type=Path, required=True)
    parser.add_argument("--staged-timeline", type=Path, required=True)
    parser.add_argument("--clean-source-music-safety", type=Path, required=True)
    parser.add_argument("--mute-source-music-safety", type=Path, required=True)
    parser.add_argument("--ambient-census", type=Path, required=True)
    parser.add_argument("--ambient-audio", type=Path, required=True)
    parser.add_argument("--clean-audio", type=Path, required=True)
    parser.add_argument("--staged-audio", type=Path, required=True)
    parser.add_argument("--mute-audio", type=Path, required=True)
    parser.add_argument("--capture-source-correlation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        proof = materialize_from_paths(
            clean_live=args.clean_live,
            staged_live=args.staged_live,
            mute_live=args.mute_live,
            clean_timeline=args.clean_timeline,
            staged_timeline=args.staged_timeline,
            clean_source_music_safety=args.clean_source_music_safety,
            mute_source_music_safety=args.mute_source_music_safety,
            ambient_census=args.ambient_census,
            ambient_audio=args.ambient_audio,
            clean_audio=args.clean_audio,
            staged_audio=args.staged_audio,
            mute_audio=args.mute_audio,
            capture_source_correlation=args.capture_source_correlation,
            output=args.output,
        )
        summary = final_check.validate_artifact(proof)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (MaterializerError, final_check.ProofError, capture_correlation.CorrelationAdapterError) as exc:
        print(f"WinUI safe-copy music audible-output materializer: FAIL: {sanitize_error_message(str(exc))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
