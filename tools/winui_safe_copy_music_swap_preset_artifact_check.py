#!/usr/bin/env python3
"""Validate a safe-copy live runtime artifact for a named music swap preset."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_MUSIC_SCHEMA = "winui-safe-copy-music-replacement.v1"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
PRESETS = {
    "use-bea02-for-bea01": ("BEA_01(Master).ogg", "BEA_02(Master).ogg"),
    "use-bea01-for-bea02": ("BEA_02(Master).ogg", "BEA_01(Master).ogg"),
    "use-bea02-for-bea04": ("BEA_04(Master).ogg", "BEA_02(Master).ogg"),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
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


def validate_capture(payload: dict[str, Any], *, min_capture_count: int) -> None:
    captures = list_at(payload, "captures")
    require(len(captures) >= min_capture_count, f"Expected at least {min_capture_count} capture(s).")
    launch = object_at(payload, "launch")
    process_id = int_at(launch, "processId")
    hwnd = string_at(launch, "mainWindowHandle").lower()
    for item in captures:
        require(isinstance(item, dict), "Each capture must be an object.")
        require(item.get("status") == "captured", "Each capture must have captured status.")
        require(item.get("processId") == process_id, "Capture process id does not match launched process.")
        require(str(item.get("hwndHex", "")).lower() == hwnd, "Capture hwnd does not match launched window.")
        require(int_at(item, "fileSize") > 0, "Capture file size must be positive.")


def validate_artifact(
    payload: dict[str, Any],
    *,
    expected_preset_id: str,
    min_capture_count: int,
) -> dict[str, Any]:
    require(expected_preset_id in PRESETS, "Unknown expected preset id.")
    expected_target, expected_replacement = PRESETS[expected_preset_id]
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
    require(
        optional_string_at(music, "MusicSwapPresetId") == expected_preset_id,
        "Music swap preset id did not match the expected named preset.",
    )
    require(string_at(music, "TargetMusicFileName") == expected_target, "Music target file did not match preset.")
    require(string_at(music, "SourceTargetFileName") == expected_target, "Source target file did not match preset.")
    require(string_at(music, "SourceReplacementFileName") == expected_replacement, "Source replacement file did not match preset.")
    source_target_sha, _ = require_same_sha_pair(music, "SourceTargetHashBefore", "SourceTargetHashAfter", "Source target music")
    require(bool_at(music, "SourceTargetHashUnchanged"), "Source target music hash changed.")
    source_replacement_sha, _ = require_same_sha_pair(music, "SourceReplacementHashBefore", "SourceReplacementHashAfter", "Source replacement music")
    require(bool_at(music, "SourceReplacementHashUnchanged"), "Source replacement music hash changed.")
    require(bool_at(music, "targetNowMatchesReplacement"), "Copied target does not match replacement bytes.")
    require(bool_at(music, "backupMatchesOriginal"), "Copied backup does not match original target bytes.")

    original_sha = string_at(music, "OriginalSha256")
    replacement_sha = string_at(music, "ReplacementSha256")
    require_sha(original_sha, "OriginalSha256")
    require_sha(replacement_sha, "ReplacementSha256")
    require(source_target_sha.lower() == original_sha.lower(), "Source target hash does not match copied original backup hash.")
    require(source_replacement_sha.lower() == replacement_sha.lower(), "Source replacement hash does not match copied replacement hash.")
    require(original_sha.lower() != replacement_sha.lower(), "Original and replacement music hashes should differ.")
    require(int_at(music, "OriginalSize") > 0, "Original music size must be positive.")
    require(int_at(music, "ReplacementSize") > 0, "Replacement music size must be positive.")

    launch = object_at(payload, "launch")
    require(bool_at(launch, "observedAlive"), "Copied BEA process was not observed alive.")
    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")
    validate_capture(payload, min_capture_count=min_capture_count)

    boundary = string_at(payload, "claimBoundary")
    require("does not prove music selection" in boundary, "Claim boundary must reject music-selection proof.")
    require("audible playback" in boundary, "Claim boundary must reject audible playback proof.")

    return {
        "schema": EXPECTED_SCHEMA,
        "musicSchema": EXPECTED_MUSIC_SCHEMA,
        "presetId": expected_preset_id,
        "target": expected_target,
        "replacement": expected_replacement,
        "sourceMusicUnchanged": True,
        "targetNowMatchesReplacement": True,
        "backupMatchesOriginal": True,
        "captureCount": len(list_at(payload, "captures")),
        "noBeaAfterStop": True,
        "claim": "safe-copy named music swap file-layout plus launch/capture/stop only",
    }


def fixture(preset_id: str = "use-bea02-for-bea01") -> dict[str, Any]:
    target, replacement = PRESETS[preset_id]
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
            "MusicSwapPresetId": preset_id,
            "TargetMusicFileName": target,
            "TargetRelativePath": f"data/Music/{target}",
            "BackupRelativePath": f"data/Music/{target}.original.backup",
            "SourceTargetFileName": target,
            "SourceTargetHashBefore": "a" * 64,
            "SourceTargetHashAfter": "a" * 64,
            "SourceTargetHashUnchanged": True,
            "SourceReplacementFileName": replacement,
            "SourceReplacementHashBefore": "b" * 64,
            "SourceReplacementHashAfter": "b" * 64,
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
            }
        ],
        "stop": {
            "Success": True,
        },
        "claimBoundary": (
            "Optional music replacement proves staged copied-game file layout survives launch; "
            "it does not prove music selection, decode, audible playback, gameplay, or rebuild parity."
        ),
    }


def run_self_test() -> None:
    for preset_id in PRESETS:
        summary = validate_artifact(fixture(preset_id), expected_preset_id=preset_id, min_capture_count=1)
        require(summary["presetId"] == preset_id, "Self-test did not preserve preset id.")

    bad = fixture()
    bad["musicReplacement"]["MusicSwapPresetId"] = None
    try:
        validate_artifact(bad, expected_preset_id="use-bea02-for-bea01", min_capture_count=1)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected missing MusicSwapPresetId to fail.")

    bad = fixture()
    bad["musicReplacement"]["SourceTargetHashUnchanged"] = False
    try:
        validate_artifact(bad, expected_preset_id="use-bea02-for-bea01", min_capture_count=1)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected source hash mutation to fail.")

    bad = fixture()
    del bad["musicReplacement"]["SourceTargetHashBefore"]
    try:
        validate_artifact(bad, expected_preset_id="use-bea02-for-bea01", min_capture_count=1)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected missing source target hash evidence to fail.")

    bad = fixture()
    bad["musicReplacement"]["SourceReplacementHashAfter"] = "5" * 64
    try:
        validate_artifact(bad, expected_preset_id="use-bea02-for-bea01", min_capture_count=1)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected changed source replacement hash evidence to fail.")

    bad = fixture()
    bad["musicReplacement"]["SourceReplacementHashBefore"] = "c" * 64
    bad["musicReplacement"]["SourceReplacementHashAfter"] = "c" * 64
    try:
        validate_artifact(bad, expected_preset_id="use-bea02-for-bea01", min_capture_count=1)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected source replacement hash to match copied replacement hash.")

    bad = fixture()
    bad["musicReplacement"]["targetNowMatchesReplacement"] = False
    try:
        validate_artifact(bad, expected_preset_id="use-bea02-for-bea01", min_capture_count=1)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected copied target mismatch to fail.")

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "artifact.json"
        path.write_text(json.dumps(fixture()), encoding="utf-8")
        validate_artifact(read_json(path), expected_preset_id="use-bea02-for-bea01", min_capture_count=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Runtime smoke JSON artifact")
    parser.add_argument("--expected-preset-id", choices=sorted(PRESETS), default="use-bea02-for-bea01")
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive.")
        if args.self_test:
            run_self_test()
            print("WinUI safe-copy music swap preset artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(
            read_json(Path(args.artifact)),
            expected_preset_id=args.expected_preset_id,
            min_capture_count=args.min_capture_count,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy music swap preset artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
