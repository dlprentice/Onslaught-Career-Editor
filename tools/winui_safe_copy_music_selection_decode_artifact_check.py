#!/usr/bin/env python3
"""Validate a CDB-backed safe-copy music selection/decode artifact."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_MUSIC_SCHEMA = "winui-safe-copy-music-replacement.v1"
EXPECTED_COMMAND_FILE = "safe-copy-music-selection-decode-observer.cdb.txt"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "Artifact root must be a JSON object.")
    return value


def object_at(value: Any, key: str) -> dict[str, Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: Any, key: str) -> list[Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def bool_at(value: Any, key: str) -> bool:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return child


def int_at(value: Any, key: str) -> int:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def optional_string_at(value: Any, key: str) -> str | None:
    child = value.get(key) if isinstance(value, dict) else None
    require(child is None or isinstance(child, str), f"{key} must be a string or null.")
    return child


def string_list_at(value: Any, key: str) -> list[str]:
    child = list_at(value, key)
    require(all(isinstance(item, str) for item in child), f"{key} must contain only strings.")
    return [str(item) for item in child]


def require_sha(value: str, label: str) -> None:
    require(bool(SHA256_RE.fullmatch(value)), f"{label} must be a SHA-256 hex string.")


def require_same_sha_pair(value: dict[str, Any], before_key: str, after_key: str, label: str) -> tuple[str, str]:
    before = string_at(value, before_key)
    after = string_at(value, after_key)
    require_sha(before, before_key)
    require_sha(after, after_key)
    require(before.lower() == after.lower(), f"{label} before/after SHA-256 values differ.")
    return before, after


def normalize_path_token(value: str) -> str:
    value = value.strip().strip('"').strip("'").replace("/", "\\")
    return re.sub(r"\s+$", "", value).lower()


def basename_token(value: str) -> str:
    normalized = normalize_path_token(value)
    return normalized.rsplit("\\", 1)[-1]


def path_mentions_file(path_value: str, expected_file: str) -> bool:
    return basename_token(path_value) == expected_file.lower()


def visual_capture_count(captures: list[Any]) -> int:
    total = 0
    for item in captures:
        if not isinstance(item, dict):
            continue
        occlusion = item.get("occlusion")
        if item.get("visualProof") is True or item.get("foregroundMatchesTarget") is True:
            total += 1
        elif (
            isinstance(occlusion, dict)
            and occlusion.get("checked") is True
            and occlusion.get("targetFound") is True
            and occlusion.get("occlusionFree") is True
            and occlusion.get("occludingWindowCount") == 0
        ):
            total += 1
    return total


def extract_log_path(observer: dict[str, Any]) -> Path:
    result = object_at(observer, "result")
    candidate = result.get("logPath") or observer.get("logPath")
    require(isinstance(candidate, str) and candidate, "CDB log path is missing.")
    path = Path(candidate)
    require(path.is_file(), f"CDB log path is missing: {path}")
    return path


def all_regex(pattern: str, text: str) -> list[re.Match[str]]:
    return list(re.finditer(pattern, text, flags=re.IGNORECASE))


def validate_artifact(
    payload: dict[str, Any],
    *,
    min_capture_count: int,
    expected_target: str | None,
    expected_replacement: str | None,
    expected_level: int | None,
    expected_selection: int | None,
    require_ogg_decode: bool,
) -> dict[str, Any]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")

    source = object_at(payload, "source")
    require_same_sha_pair(source, "installedHashBefore", "installedHashAfter", "Installed BEA.exe")
    require(bool_at(source, "installedHashUnchanged"), "Installed BEA.exe hash changed.")
    require_same_sha_pair(source, "overrideHashBefore", "overrideHashAfter", "Clean executable override")
    require(bool_at(source, "overrideHashUnchanged"), "Clean executable override hash changed.")
    source_save_options = object_at(source, "saveAndOptions")
    require(bool_at(source_save_options, "unchanged"), "Source defaultoptions/savegames hashes changed.")

    safe_copy = object_at(payload, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "Safe copy did not apply required windowed compatibility patch keys.")

    music = object_at(payload, "musicReplacement")
    require(string_at(music, "SchemaVersion") == EXPECTED_MUSIC_SCHEMA, "Unexpected music replacement schema.")
    target = string_at(music, "TargetMusicFileName")
    replacement = string_at(music, "SourceReplacementFileName")
    if expected_target:
        require(target.lower() == expected_target.lower(), "Music target file did not match expected target.")
    if expected_replacement:
        require(replacement.lower() == expected_replacement.lower(), "Music replacement file did not match expected replacement.")
    require_same_sha_pair(music, "SourceTargetHashBefore", "SourceTargetHashAfter", "Source target music")
    require(bool_at(music, "SourceTargetHashUnchanged"), "Source target music hash changed.")
    require_same_sha_pair(music, "SourceReplacementHashBefore", "SourceReplacementHashAfter", "Source replacement music")
    require(bool_at(music, "SourceReplacementHashUnchanged"), "Source replacement music hash changed.")
    require(bool_at(music, "targetNowMatchesReplacement"), "Copied target does not match replacement bytes.")
    require(bool_at(music, "backupMatchesOriginal"), "Copied backup does not match original target bytes.")
    require_sha(string_at(music, "OriginalSha256"), "OriginalSha256")
    require_sha(string_at(music, "ReplacementSha256"), "ReplacementSha256")
    require(string_at(music, "OriginalSha256").lower() != string_at(music, "ReplacementSha256").lower(), "Original and replacement music hashes should differ.")

    launch = object_at(payload, "launch")
    require(bool_at(launch, "observedAlive"), "Copied BEA process was not observed alive.")
    launch_args = list_at(launch, "arguments")
    require(all(isinstance(item, str) for item in launch_args), "Launch arguments must be strings.")
    lower_args = [str(item).lower() for item in launch_args]
    require("-nomusic" not in lower_args, "Launch arguments disable music.")
    require("-nosound" not in lower_args, "Launch arguments disable sound.")
    require("-skipfmv" in lower_args, "Launch arguments are missing -skipfmv.")
    if expected_level is not None:
        require("-level" in lower_args, "Expected-level proof requires a -level launch argument.")
        level_index = lower_args.index("-level")
        require(level_index + 1 < len(lower_args), "-level is missing its value.")
        require(str(launch_args[level_index + 1]) == str(expected_level), "Launch level did not match expected level.")

    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")

    captures = list_at(payload, "captures")
    require(len(captures) >= min_capture_count, f"Expected at least {min_capture_count} capture(s).")
    for item in captures:
        require(isinstance(item, dict), "Each capture must be an object.")
        require(item.get("status") == "captured", "Each capture must have captured status.")
        require(int_at(item, "fileSize") > 0, "Capture file size must be positive.")

    observer = object_at(payload, "cdbObserver")
    require(bool_at(observer, "enabled"), "CDB observer not enabled.")
    command_file = optional_string_at(observer, "commandFile") or ""
    require(command_file.replace("/", "\\").lower().endswith(EXPECTED_COMMAND_FILE), "Unexpected CDB observer command file.")
    result = object_at(observer, "result")
    cleanup = object_at(observer, "cleanup")
    require(result.get("status") == "attached", "CDB observer did not attach.")
    require(bool_at(result, "logExists"), "CDB log was not created.")
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB cleanup did not finish.")

    log_path = extract_log_path(observer)
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    target_lower = target.lower()

    play_selection_entries = all_regex(
        r"CMusic__PlaySelection entry this=([0-9a-fA-F]+) selection=(-?\d+) fade=(-?\d+) "
        r"playing=(\d+) head=([0-9a-fA-F]+) current=([0-9a-fA-F]+)",
        log_text,
    )
    play_selection_resolved = all_regex(
        r"CMusic__PlaySelectionResolved this=([0-9a-fA-F]+) selection=(-?\d+) selected=([0-9a-fA-F]+) "
        r"path=(.*?) playing=(\d+) fadeArg=(-?\d+) current=([0-9a-fA-F]+) pending=([0-9a-fA-F]+) mode=(-?\d+)",
        log_text,
    )
    cdb_path_stop = r"(?:\s+[A-Z][A-Za-z0-9_]+__|\s+eax=|\r?\n|$)"
    kick_rows = all_regex(r"PCPlatform__KickAsyncMusicStreamRead path=(.*?\.ogg|<[^>]+>)" + cdb_path_stop, log_text)
    open_rows = all_regex(r"COggFileRead__OpenFileAndPrimeDecoder this=([0-9a-fA-F]+) path=(.*?\.ogg|<[^>]+>)" + cdb_path_stop, log_text)
    read_rows = all_regex(
        r"COggFileRead__ReadDecodedPcm this=([0-9a-fA-F]+) request=(\d+) out=([0-9a-fA-F]+) outBytes=([0-9a-fA-F]+)",
        log_text,
    )
    update_rows = all_regex(
        r"CMusic__UpdateStatus this=([0-9a-fA-F]+) playing=(\d+) mode=(-?\d+) head=([0-9a-fA-F]+) "
        r"current=([0-9a-fA-F]+) currentPath=(.*?\.ogg|<[^>]+>) pending=([0-9a-fA-F]+) pendingPath=(.*?)" + cdb_path_stop,
        log_text,
    )
    game_music_rows = all_regex(
        r"CGame__PlayMusicForCurrentLevel this=([0-9a-fA-F]+) level=(\d+) raw=([0-9a-fA-F]+)",
        log_text,
    )

    require(play_selection_entries, "Missing CMusic__PlaySelection entry observation.")
    require(kick_rows, "Missing PCPlatform__KickAsyncMusicStreamRead observation.")
    if expected_selection is not None:
        require(
            any(int(row.group(2)) == expected_selection for row in play_selection_entries),
            "CMusic selection observation did not match expected selection.",
        )
    if expected_level is not None:
        if game_music_rows:
            require(any(int(row.group(2)) == expected_level for row in game_music_rows), "CGame music-level observation did not match expected level.")

    resolved_paths = [match.group(4).strip() for match in play_selection_resolved]
    current_paths = [match.group(6).strip() for match in update_rows]
    kick_paths = [match.group(1).strip() for match in kick_rows]
    open_paths = [match.group(2).strip() for match in open_rows]
    decode_requests = [int(match.group(2)) for match in read_rows]

    require(any(path_mentions_file(path, target_lower) for path in kick_paths), "Async music kick path did not match staged target.")

    decode_proven = bool(open_rows) and any(path_mentions_file(path, target_lower) for path in open_paths) and any(value > 0 for value in decode_requests)
    if require_ogg_decode:
        require(open_rows, "Missing COggFileRead__OpenFileAndPrimeDecoder observation.")
        require(any(path_mentions_file(path, target_lower) for path in open_paths), "Ogg open path did not match staged target.")
        require(read_rows, "Missing COggFileRead__ReadDecodedPcm observation.")
        require(any(value > 0 for value in decode_requests), "Ogg read request was not positive.")

    boundary = string_at(payload, "claimBoundary")
    require("audible playback" in boundary, "Claim boundary must still reject audible playback proof.")

    return {
        "schema": EXPECTED_SCHEMA,
        "musicSchema": EXPECTED_MUSIC_SCHEMA,
        "target": target,
        "replacement": replacement,
        "captureCount": len(captures),
        "visualCaptureCount": visual_capture_count(captures),
        "launchArguments": launch_args,
        "cdbStatus": result.get("status"),
        "cdbCleanup": cleanup.get("status"),
        "gameMusicLevelObservations": [int(row.group(2)) for row in game_music_rows],
        "playSelectionEntryCount": len(play_selection_entries),
        "playSelectionResolvedCount": len(play_selection_resolved),
        "updateStatusCount": len(update_rows),
        "asyncKickCount": len(kick_rows),
        "oggOpenCount": len(open_rows),
        "oggReadCount": len(read_rows),
        "decodeProven": decode_proven,
        "audibleOutputProven": False,
        "audiblePlaybackProven": False,
        "observedSelectedPaths": sorted({normalize_path_token(path) for path in resolved_paths}),
        "observedCurrentPaths": sorted({normalize_path_token(path) for path in current_paths}),
        "observedKickPaths": sorted({normalize_path_token(path) for path in kick_paths}),
        "observedOpenPaths": sorted({normalize_path_token(path) for path in open_paths}),
        "maxDecodeRequest": max(decode_requests) if decode_requests else 0,
        "claim": "safe-copy CMusic selection reached the staged target through the async music stream"
        + (" with Ogg open/read evidence" if decode_proven else " without Ogg decode evidence"),
        "claimBoundary": boundary,
        "nonClaims": [
            "audible playback",
            "audible output",
            "loop behavior",
            "volume behavior",
            "mixing or crossfade behavior",
            "all music cues",
            "arbitrary external OGG compatibility",
            "gameplay parity",
            "rebuild parity",
        ],
    }


def fixture(log_path: Path, *, include_decode: bool = True) -> dict[str, Any]:
    target = "BEA_04(Master).ogg"
    replacement = "BEA_02(Master).ogg"
    lines = [
        "CGame__PlayMusicForCurrentLevel this=008a9a98 level=100 raw=00000064",
        "CMusic__PlaySelection entry this=00889a48 selection=2 fade=0 playing=0 head=04400000 current=00000000",
        "CMusic__UpdateStatus this=00889a48 playing=1 mode=3 head=04400000 current=04400300 currentPath=data\\music\\BEA_04(Master).ogg pending=00000000 pendingPath=<Memory access error>",
        "CMusic__PlaySelectionResolved this=00889a48 selection=2 selected=04400300 path=data\\music\\BEA_04(Master).ogg playing=0 fadeArg=0 current=00000000 pending=00000000 mode=0",
        "PCPlatform__KickAsyncMusicStreamRead path=data\\music\\BEA_04(Master).ogg",
    ]
    if include_decode:
        lines.extend(
            [
                "COggFileRead__OpenFileAndPrimeDecoder this=0440a000 path=data\\music\\BEA_04(Master).ogg",
                "COggFileRead__ReadDecodedPcm this=0440a000 request=4096 out=04500000 outBytes=0019f4b0",
            ]
        )
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return {
            "schemaVersion": EXPECTED_SCHEMA,
            "source": {
                "installedHashBefore": "1" * 64,
                "installedHashAfter": "1" * 64,
                "installedHashUnchanged": True,
                "overrideHashBefore": "2" * 64,
                "overrideHashAfter": "2" * 64,
                "overrideHashUnchanged": True,
                "saveAndOptions": {
                    "unchanged": True,
                },
            },
            "safeCopy": {
                "patchKeys": ["resolution_gate", "force_windowed"],
            },
            "musicReplacement": {
                "SchemaVersion": EXPECTED_MUSIC_SCHEMA,
                "MusicSwapPresetId": None,
                "TargetMusicFileName": target,
                "TargetRelativePath": f"data/Music/{target}",
                "BackupRelativePath": f"data/Music/{target}.original.backup",
                "SourceTargetFileName": target,
                "SourceTargetHashBefore": "3" * 64,
                "SourceTargetHashAfter": "3" * 64,
                "SourceTargetHashUnchanged": True,
                "SourceReplacementFileName": replacement,
                "SourceReplacementHashBefore": "4" * 64,
                "SourceReplacementHashAfter": "4" * 64,
                "SourceReplacementHashUnchanged": True,
                "OriginalSize": 100,
                "OriginalSha256": "a" * 64,
                "ReplacementSize": 200,
                "ReplacementSha256": "b" * 64,
                "targetNowMatchesReplacement": True,
                "backupMatchesOriginal": True,
            },
            "launch": {
                "processId": 42464,
                "observedAlive": True,
                "mainWindowHandle": "0x1600d2a",
                "arguments": ["-skipfmv", "-level", "100"],
            },
            "processBaseline": {
                "noPreexistingBea": True,
                "noBeaAfterStop": True,
            },
            "captures": [
                {
                    "status": "captured",
                    "processId": 42464,
                    "hwndHex": "0x1600d2a",
                    "fileSize": 503209,
                    "visualProof": True,
                }
            ],
            "stop": {
                "Success": True,
            },
            "cdbObserver": {
                "enabled": True,
                "commandFile": f"tools/runtime-probes/{EXPECTED_COMMAND_FILE}",
                "logPath": str(log_path),
                "result": {
                    "status": "attached",
                    "logExists": True,
                    "logPath": str(log_path),
                },
                "cleanup": {
                    "status": "stopped",
                },
            },
            "claimBoundary": (
                "Optional music replacement proves staged copied-game file layout survives launch; "
                "it does not prove music selection, decode, audible playback, gameplay, menu reach, "
                "rendering correctness, visual parity, unoccluded pixels, or rebuild parity unless "
                "the focused proof explicitly captures that narrower outcome."
            ),
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "artifact.json"
        log_path = Path(temp_dir) / "windbg.log"
        payload = fixture(log_path, include_decode=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        summary = validate_artifact(
            read_json(path),
            min_capture_count=1,
            expected_target="BEA_04(Master).ogg",
            expected_replacement="BEA_02(Master).ogg",
            expected_level=100,
            expected_selection=2,
            require_ogg_decode=True,
        )
        require(summary["decodeProven"] is True, "Self-test expected decode proof.")
        require(summary["audibleOutputProven"] is False, "Self-test expected audible output to remain false.")
        require(summary["audiblePlaybackProven"] is False, "Self-test expected audible playback to remain false.")
        require("audible playback" in summary["nonClaims"], "Self-test expected audible playback non-claim.")

        no_decode = fixture(log_path, include_decode=False)
        path.write_text(json.dumps(no_decode), encoding="utf-8")
        summary = validate_artifact(
            read_json(path),
            min_capture_count=1,
            expected_target="BEA_04(Master).ogg",
            expected_replacement="BEA_02(Master).ogg",
            expected_level=100,
            expected_selection=2,
            require_ogg_decode=False,
        )
        require(summary["decodeProven"] is False, "Self-test expected no decode proof.")

        bad = fixture(log_path, include_decode=True)
        log_path.write_text(log_path.read_text(encoding="utf-8").replace("BEA_04(Master).ogg", "BEA_01(Master).ogg"), encoding="utf-8")
        path.write_text(json.dumps(bad), encoding="utf-8")
        try:
            validate_artifact(
                read_json(path),
                min_capture_count=1,
                expected_target="BEA_04(Master).ogg",
                expected_replacement="BEA_02(Master).ogg",
                expected_level=100,
                expected_selection=2,
                require_ogg_decode=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected mismatched selected path to fail.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Runtime smoke JSON artifact")
    parser.add_argument("--expected-target", default="", help="Expected staged target music file name")
    parser.add_argument("--expected-replacement", default="", help="Expected source replacement music file name")
    parser.add_argument("--expected-level", type=int, default=0, help="Expected -level argument and CGame music-level observation")
    parser.add_argument("--expected-selection", type=int, default=-1, help="Expected CMusic selection argument")
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--require-ogg-decode", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive.")
        if args.self_test:
            run_self_test()
            print("WinUI safe-copy music selection/decode artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(
            read_json(Path(args.artifact)),
            min_capture_count=args.min_capture_count,
            expected_target=args.expected_target.strip() or None,
            expected_replacement=args.expected_replacement.strip() or None,
            expected_level=args.expected_level or None,
            expected_selection=args.expected_selection if args.expected_selection >= 0 else None,
            require_ogg_decode=args.require_ogg_decode,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy music selection/decode artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
