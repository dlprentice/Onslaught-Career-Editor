#!/usr/bin/env python3
"""Validate the named BEA_04 music-swap preset plus level-100 CDB decode proof."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_music_selection_decode_artifact_check as selection_decode
import winui_safe_copy_music_swap_preset_artifact_check as preset_check


PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
SELECTION_ID = 2
MIN_CAPTURE_COUNT = 2


class ProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "Proof artifact must be a JSON object.")
    return value


def _with_wrapped_error(label: str, func: Any) -> dict[str, Any]:
    try:
        summary = func()
    except (preset_check.ArtifactError, selection_decode.ArtifactError) as exc:
        raise ProofError(f"{label}: {exc}") from exc
    require(isinstance(summary, dict), f"{label} did not return a summary object.")
    return summary


def validate_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    preset_summary = _with_wrapped_error(
        "named preset artifact",
        lambda: preset_check.validate_artifact(
            payload,
            expected_preset_id=PRESET_ID,
            min_capture_count=MIN_CAPTURE_COUNT,
        ),
    )
    decode_summary = _with_wrapped_error(
        "music selection/decode artifact",
        lambda: selection_decode.validate_artifact(
            payload,
            min_capture_count=MIN_CAPTURE_COUNT,
            expected_target=TARGET,
            expected_replacement=REPLACEMENT,
            expected_level=LEVEL_ID,
            expected_selection=SELECTION_ID,
            require_ogg_decode=True,
        ),
    )

    require(preset_summary.get("target") == TARGET, "Preset target summary drifted.")
    require(preset_summary.get("replacement") == REPLACEMENT, "Preset replacement summary drifted.")
    require(decode_summary.get("target") == TARGET, "Decode target summary drifted.")
    require(decode_summary.get("replacement") == REPLACEMENT, "Decode replacement summary drifted.")
    require(decode_summary.get("decodeProven") is True, "Decode proof did not report true.")
    require(int(decode_summary.get("oggReadCount", 0)) > 0, "Decode proof did not include Ogg read rows.")
    require(int(decode_summary.get("asyncKickCount", 0)) > 0, "Decode proof did not include async music kick rows.")
    require(
        int(decode_summary.get("visualCaptureCount", 0)) >= MIN_CAPTURE_COUNT,
        "Proof needs at least two bounded visual captures for this accepted slice.",
    )

    return {
        "schema": "winui-safe-copy-music-swap-level100-decode-proof.v1",
        "presetId": PRESET_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "levelId": LEVEL_ID,
        "selectionId": SELECTION_ID,
        "captureCount": preset_summary["captureCount"],
        "visualCaptureCount": decode_summary["visualCaptureCount"],
        "asyncKickCount": decode_summary["asyncKickCount"],
        "oggOpenCount": decode_summary["oggOpenCount"],
        "oggReadCount": decode_summary["oggReadCount"],
        "maxDecodeRequest": decode_summary["maxDecodeRequest"],
        "sourceMusicUnchanged": preset_summary["sourceMusicUnchanged"],
        "targetNowMatchesReplacement": preset_summary["targetNowMatchesReplacement"],
        "backupMatchesOriginal": preset_summary["backupMatchesOriginal"],
        "claim": (
            "named safe-copy shipped-track preset staged BEA_02 over BEA_04 and level-100 CDB "
            "evidence reached the staged BEA_04 path through async music kick and Ogg decode"
        ),
        "nonClaims": [
            "audible playback",
            "loop behavior",
            "all music cues",
            "arbitrary user OGG compatibility",
            "gameplay parity",
            "rebuild parity",
        ],
    }


def fixture(log_path: Path, *, include_decode: bool = True) -> dict[str, Any]:
    payload = selection_decode.fixture(log_path, include_decode=include_decode)
    payload["musicReplacement"]["MusicSwapPresetId"] = PRESET_ID
    payload["musicReplacement"]["SourceTargetHashBefore"] = payload["musicReplacement"]["OriginalSha256"]
    payload["musicReplacement"]["SourceTargetHashAfter"] = payload["musicReplacement"]["OriginalSha256"]
    payload["musicReplacement"]["SourceReplacementHashBefore"] = payload["musicReplacement"]["ReplacementSha256"]
    payload["musicReplacement"]["SourceReplacementHashAfter"] = payload["musicReplacement"]["ReplacementSha256"]
    capture = dict(payload["captures"][0])
    capture["fileSize"] = int(capture["fileSize"]) + 1
    payload["captures"].append(capture)
    return payload


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        artifact_path = root / "artifact.json"
        log_path = root / "windbg.log"

        payload = fixture(log_path, include_decode=True)
        artifact_path.write_text(json.dumps(payload), encoding="utf-8")
        summary = validate_artifact(read_json(artifact_path))
        require(summary["presetId"] == PRESET_ID, "Self-test did not preserve preset id.")
        require(summary["oggReadCount"] > 0, "Self-test expected Ogg read proof.")

        missing_preset = fixture(log_path, include_decode=True)
        missing_preset["musicReplacement"]["MusicSwapPresetId"] = None
        try:
            validate_artifact(missing_preset)
        except ProofError:
            pass
        else:
            raise ProofError("Self-test expected missing preset id to fail.")

        no_decode = fixture(log_path, include_decode=False)
        try:
            validate_artifact(no_decode)
        except ProofError:
            pass
        else:
            raise ProofError("Self-test expected missing Ogg decode evidence to fail.")

        weak_capture = fixture(log_path, include_decode=True)
        weak_capture["captures"] = weak_capture["captures"][:1]
        try:
            validate_artifact(weak_capture)
        except ProofError:
            pass
        else:
            raise ProofError("Self-test expected single-capture proof to fail.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Runtime smoke JSON artifact")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print("WinUI safe-copy music swap level-100 decode proof checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(read_json(Path(args.artifact)))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ProofError as exc:
        print(f"WinUI safe-copy music swap level-100 decode proof check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
