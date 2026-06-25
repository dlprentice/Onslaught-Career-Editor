#!/usr/bin/env python3
"""Validate a replay-only diagnostic for rejected music audible-output bundles.

This checker ties together existing sanitized sidecars:
- staged music file layout is proven in the live-smoke JSON,
- clean/staged timestamped CDB timeline sidecars prove the decode window,
- capture-to-source correlation remains explicitly rejected.

It deliberately does not read raw WAV bytes, raw CDB logs, source OGG bytes, or
private proof payloads. It also does not emit a materializer-compatible proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import winui_safe_copy_music_capture_source_correlation_check as correlation_check
import winui_safe_copy_music_swap_preset_artifact_check as preset_check


SCHEMA = "winui-safe-copy-music-rejected-replay-diagnostic.v1"
TIMELINE_SCHEMA = "winui-safe-copy-music-cdb-decode-timeline.v1"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
SELECTION_ID = 2
SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
REQUIRED_NON_CLAIMS = [
    "not accepted capture-source correlation",
    "not materializer input",
    "not runtime audible-output proof",
    "not raw audio publication",
    "not raw CDB publication",
    "not private path publication",
    "not source path publication",
    "not arbitrary external OGG compatibility",
    "not all-cue proof",
    "not loop volume or mix proof",
    "not gameplay parity",
    "not online proof",
    "not rebuild parity",
    "no installed-game or original BEA.exe mutation",
]


class RejectedReplayDiagnosticError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RejectedReplayDiagnosticError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object.")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def int_at(value: dict[str, Any], key: str) -> int:
    child = value.get(key)
    require(isinstance(child, int) and not isinstance(child, bool), f"Missing integer: {key}")
    return int(child)


def bool_at(value: dict[str, Any], key: str) -> bool:
    child = value.get(key)
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return bool(child)


def number_at(value: dict[str, Any], key: str) -> float:
    child = value.get(key)
    require(isinstance(child, (int, float)) and not isinstance(child, bool), f"Missing number: {key}")
    return float(child)


def validate_sha(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(SHA256_RE.fullmatch(value)), f"{label} must be a SHA-256 hex string.")
    return value.lower()


def validate_timeline(path: Path, *, live_path: Path, role: str) -> dict[str, Any]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == TIMELINE_SCHEMA, f"{role} timeline schema changed.")
    require(payload.get("role") == role, f"{role} timeline role mismatch.")
    require(payload.get("timestampSource") == "timestamped-cdb-log", f"{role} timeline timestamp source changed.")
    require(bool_at(payload, "cdbLogTimestamped"), f"{role} timeline must be timestamped.")
    require(payload.get("liveArtifactSha256") == sha256_file(live_path), f"{role} timeline is not bound to the live artifact.")
    require(bool_at(payload, "exactPidCdbObserver"), f"{role} timeline must be exact-PID CDB evidence.")
    require(int_at(payload, "levelId") == LEVEL_ID, f"{role} timeline level mismatch.")
    require(int_at(payload, "selectionId") == SELECTION_ID, f"{role} timeline selection mismatch.")
    require(bool_at(payload, "playSelectionObserved"), f"{role} timeline missing play-selection observation.")
    require(bool_at(payload, "asyncKickPathMatched"), f"{role} timeline missing async music kick.")
    require(bool_at(payload, "oggOpenPathMatched"), f"{role} timeline missing Ogg open.")
    require(bool_at(payload, "decodedPcmPositiveRequestObserved"), f"{role} timeline missing decoded PCM read.")
    provenance = payload.get("musicSelectionProvenance")
    require(provenance in {"cgame-wrapper", "cgame-restart-loop-direct"}, f"{role} timeline provenance is not accepted.")
    if provenance == "cgame-restart-loop-direct":
        require(bool_at(payload, "restartLoopDirectMusicSelectionObserved"), f"{role} timeline missing restart-loop direct observation.")
    if provenance == "cgame-wrapper":
        require(bool_at(payload, "playMusicForCurrentLevelObserved"), f"{role} timeline missing CGame wrapper observation.")
    row_counts = object_at(payload, "cdbEvidenceRowCounts")
    require(int_at(row_counts, "playSelectionRows") > 0, f"{role} timeline missing play-selection rows.")
    require(int_at(row_counts, "asyncKickRows") > 0, f"{role} timeline missing async-kick rows.")
    require(int_at(row_counts, "oggOpenRows") > 0, f"{role} timeline missing Ogg-open rows.")
    require(int_at(row_counts, "oggReadRows") > 0, f"{role} timeline missing Ogg-read rows.")
    return {
        "role": role,
        "musicSelectionProvenance": provenance,
        "rowCounts": {
            "playSelectionRows": int_at(row_counts, "playSelectionRows"),
            "asyncKickRows": int_at(row_counts, "asyncKickRows"),
            "oggOpenRows": int_at(row_counts, "oggOpenRows"),
            "oggReadRows": int_at(row_counts, "oggReadRows"),
        },
    }


def validate_clean_live(path: Path) -> None:
    payload = read_json(path)
    require(payload.get("schemaVersion") == "winui-safe-copy-live-runtime-smoke.v1", "Clean live artifact schema changed.")
    require(payload.get("musicReplacement") is None, "Clean live artifact must not include staged music replacement.")
    source = object_at(payload, "source")
    require(bool_at(source, "installedHashUnchanged"), "Clean live artifact installed hash changed.")
    require(bool_at(source, "overrideHashUnchanged"), "Clean live artifact override hash changed.")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "Clean live artifact source save/options changed.")
    launch = object_at(payload, "launch")
    args = [str(item).lower() for item in launch.get("arguments", []) if isinstance(item, str)]
    require("-nomusic" not in args and "-nosound" not in args, "Clean live artifact disables music or sound.")
    require("-level" in args and str(LEVEL_ID) in args, "Clean live artifact is not bound to level 100.")
    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "Clean live artifact had preexisting BEA.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "Clean live artifact left BEA running.")
    require(bool_at(object_at(payload, "stop"), "Success"), "Clean live artifact stop failed.")


def validate_from_paths(
    *,
    clean_live: Path,
    staged_live: Path,
    clean_timeline: Path,
    staged_timeline: Path,
    rejection_diagnostic: Path,
) -> dict[str, Any]:
    validate_clean_live(clean_live)
    try:
        staged_summary = preset_check.validate_artifact(
            preset_check.read_json(staged_live),
            expected_preset_id=PRESET_ID,
            min_capture_count=2,
        )
    except preset_check.ArtifactError as exc:
        raise RejectedReplayDiagnosticError(f"staged preset artifact: {exc}") from exc

    clean_timeline_summary = validate_timeline(clean_timeline, live_path=clean_live, role="cleanBaseline")
    staged_timeline_summary = validate_timeline(staged_timeline, live_path=staged_live, role="stagedPositive")

    try:
        rejection_summary = correlation_check.validate_rejection_diagnostic(
            correlation_check.read_json(rejection_diagnostic)
        )
    except correlation_check.CorrelationAdapterError as exc:
        raise RejectedReplayDiagnosticError(f"capture-source rejection diagnostic: {exc}") from exc

    require(rejection_summary["status"] == "rejected", "Capture-source diagnostic must be rejected.")
    require(rejection_summary["runtimeAudibleOutputProof"] is False, "Rejected diagnostic must not claim audible output.")
    require(rejection_summary["target"] == TARGET, "Rejected diagnostic target changed.")
    require(rejection_summary["replacement"] == REPLACEMENT, "Rejected diagnostic replacement changed.")

    bindings = rejection_summary["inputBindings"]
    clean_audio_json_sha = validate_sha(bindings.get("cleanAudioJsonSha256"), "cleanAudioJsonSha256")
    clean_audio_wav_sha = validate_sha(bindings.get("cleanAudioWavSha256"), "cleanAudioWavSha256")
    staged_audio_json_sha = validate_sha(bindings.get("stagedAudioJsonSha256"), "stagedAudioJsonSha256")
    staged_audio_wav_sha = validate_sha(bindings.get("stagedAudioWavSha256"), "stagedAudioWavSha256")

    return {
        "schema": SCHEMA,
        "presetId": PRESET_ID,
        "levelId": LEVEL_ID,
        "selectionId": SELECTION_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "runtimeAudibleOutputProof": False,
        "stagedFileLayoutProven": True,
        "exactPidDecodeTimelineProven": True,
        "captureSourceCorrelationRejected": True,
        "rejectionReason": rejection_summary["rejectionReason"],
        "cleanBaselineBestMatch": rejection_summary["cleanBaselineBestMatch"],
        "stagedPositiveBestMatch": rejection_summary["stagedPositiveBestMatch"],
        "cleanBaselineMargin": number_at(rejection_summary, "cleanBaselineMargin"),
        "stagedPositiveMargin": number_at(rejection_summary, "stagedPositiveMargin"),
        "stagedTargetNowMatchesReplacement": staged_summary["targetNowMatchesReplacement"],
        "stagedBackupMatchesOriginal": staged_summary["backupMatchesOriginal"],
        "stagedSourceMusicUnchanged": staged_summary["sourceMusicUnchanged"],
        "cleanTimeline": clean_timeline_summary,
        "stagedTimeline": staged_timeline_summary,
        "inputBindings": {
            "cleanAudioJsonSha256": clean_audio_json_sha,
            "cleanAudioWavSha256": clean_audio_wav_sha,
            "stagedAudioJsonSha256": staged_audio_json_sha,
            "stagedAudioWavSha256": staged_audio_wav_sha,
        },
        "claimBoundary": (
            "Replay-only diagnostic: staged copied music file layout and exact-PID decode timeline are present, "
            "but capture-source correlation is rejected. Not materializer input and not runtime audible-output proof."
        ),
        "nonClaims": REQUIRED_NON_CLAIMS,
    }


def run_self_test() -> dict[str, Any]:
    from winui_safe_copy_music_rejected_replay_diagnostic_check_test import (  # type: ignore
        clean_live_fixture,
        staged_live_fixture,
        timeline_fixture,
        write_json,
    )

    import tempfile

    with tempfile.TemporaryDirectory(prefix="music-rejected-replay-self-test-") as temp_dir:
        root = Path(temp_dir)
        clean_live = write_json(root / "clean" / "live.json", clean_live_fixture())
        staged_live = write_json(root / "staged" / "live.json", staged_live_fixture())
        clean_timeline = write_json(root / "clean" / "timeline.json", timeline_fixture(clean_live, role="cleanBaseline"))
        staged_timeline = write_json(root / "staged" / "timeline.json", timeline_fixture(staged_live, role="stagedPositive"))
        rejection = write_json(root / "capture-source-correlation-rejection.json", correlation_check.rejection_fixture())
        return validate_from_paths(
            clean_live=clean_live,
            staged_live=staged_live,
            clean_timeline=clean_timeline,
            staged_timeline=staged_timeline,
            rejection_diagnostic=rejection,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-live", type=Path)
    parser.add_argument("--staged-live", type=Path)
    parser.add_argument("--clean-timeline", type=Path)
    parser.add_argument("--staged-timeline", type=Path)
    parser.add_argument("--rejection-diagnostic", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            summary = run_self_test()
        else:
            require(args.clean_live is not None, "Provide --clean-live or --self-test.")
            require(args.staged_live is not None, "Provide --staged-live.")
            require(args.clean_timeline is not None, "Provide --clean-timeline.")
            require(args.staged_timeline is not None, "Provide --staged-timeline.")
            require(args.rejection_diagnostic is not None, "Provide --rejection-diagnostic.")
            summary = validate_from_paths(
                clean_live=args.clean_live,
                staged_live=args.staged_live,
                clean_timeline=args.clean_timeline,
                staged_timeline=args.staged_timeline,
                rejection_diagnostic=args.rejection_diagnostic,
            )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except RejectedReplayDiagnosticError as exc:
        print(f"WinUI safe-copy music rejected-replay diagnostic check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
