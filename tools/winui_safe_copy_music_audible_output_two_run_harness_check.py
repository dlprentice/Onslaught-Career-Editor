#!/usr/bin/env python3
"""Validate a two-run safe-copy music audible-output proof bundle.

This checker validates the shape of a future accepted proof. It does not
generate a BEA audible-output claim from the current repository state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "winui-safe-copy-music-audible-output-proof.v1"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
SELECTION_ID = 2
BASE_PATCH_KEYS = {"force_windowed", "resolution_gate"}
SOURCE_AUDIO_FINGERPRINT_VERSION = "source-audio-correlation-helper.v1"
MIN_SOURCE_AUDIO_MARGIN = 0.15


class ProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "Proof artifact must be a JSON object.")
    return value


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
    return child


def int_at(value: dict[str, Any], key: str) -> int:
    child = value.get(key)
    require(isinstance(child, int), f"Missing integer: {key}")
    return child


def number_at(value: dict[str, Any], key: str) -> float:
    child = value.get(key)
    require(isinstance(child, (int, float)), f"Missing number: {key}")
    return float(child)


def utc_at(value: dict[str, Any], key: str) -> dt.datetime:
    child = value.get(key)
    require(isinstance(child, str) and child.endswith("Z"), f"Missing UTC timestamp: {key}")
    try:
        parsed = dt.datetime.fromisoformat(child.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise ProofError(f"Invalid UTC timestamp {key}: {child}") from exc
    require(parsed.tzinfo is not None, f"UTC timestamp must be timezone-aware: {key}")
    return parsed.astimezone(dt.timezone.utc)


def string_set(value: list[Any], label: str) -> set[str]:
    require(all(isinstance(item, str) for item in value), f"{label} must contain only strings.")
    return {str(item) for item in value}


def validate_source_safety(run: dict[str, Any], role: str) -> dict[str, bool]:
    source_safety = object_at(run, "sourceSafety")
    required = {
        "installedHashUnchanged",
        "overrideHashUnchanged",
        "sourceTargetHashUnchanged",
        "sourceReplacementHashUnchanged",
        "noPreexistingBea",
        "noBeaAfterStop",
    }
    result = {key: bool_at(source_safety, key) for key in required}
    missing = sorted(key for key, value in result.items() if not value)
    require(not missing, f"{role} source-safety gate failed: {', '.join(missing)}")
    return result


def validate_runtime_evidence(run: dict[str, Any], role: str) -> dict[str, Any]:
    cdb = object_at(run, "cdbSelectionDecode")
    require(bool_at(cdb, "exactPidCdbObserver"), f"{role} must use exact-PID CDB evidence.")
    require(int_at(cdb, "levelId") == LEVEL_ID, f"{role} CDB level must be {LEVEL_ID}.")
    require(int_at(cdb, "selectionId") == SELECTION_ID, f"{role} CDB selection must be {SELECTION_ID}.")
    require(bool_at(cdb, "playMusicForCurrentLevelObserved"), f"{role} must observe CGame music selection.")
    require(bool_at(cdb, "playSelectionObserved"), f"{role} must observe CMusic selection.")
    require(bool_at(cdb, "asyncKickPathMatched"), f"{role} must observe async music kick path.")
    require(bool_at(cdb, "oggOpenPathMatched"), f"{role} must observe Ogg open path.")
    require(bool_at(cdb, "decodedPcmPositiveRequestObserved"), f"{role} must observe decoded PCM request.")
    decode_start = utc_at(cdb, "decodeWindowStartUtc")
    decode_end = utc_at(cdb, "decodeWindowEndUtc")
    require(decode_start <= decode_end, f"{role} CDB decode window is inverted.")
    return {
        "levelId": cdb["levelId"],
        "selectionId": cdb["selectionId"],
        "decodeWindowStartUtc": cdb["decodeWindowStartUtc"],
        "decodeWindowEndUtc": cdb["decodeWindowEndUtc"],
        "decodeWindowStartAt": decode_start,
        "decodeWindowEndAt": decode_end,
    }


def validate_audio_capture(run: dict[str, Any], role: str, *, require_non_silent: bool) -> dict[str, Any]:
    audio = object_at(run, "audioCapture")
    require(audio.get("schemaVersion") == "audio-loopback-capture.v1", f"{role} audio capture schema changed.")
    require(audio.get("status") == "captured", f"{role} audio capture did not complete.")
    require(audio.get("captureKind") in {"wasapi-loopback", "equivalent-output-capture"}, f"{role} capture kind is not accepted.")
    require(bool_at(audio, "boundedOutputArtifact"), f"{role} must be a bounded output artifact.")
    require(bool_at(audio, "startsBeforeExpectedMusicKick"), f"{role} capture must start before music kick.")
    require(bool_at(audio, "endsAfterDecodeBegins"), f"{role} capture must end after decode begins.")
    require("deviceStableId" not in audio, f"{role} must not publish raw deviceStableId.")
    require("device" not in audio, f"{role} must not publish raw device object.")
    capture_start = utc_at(audio, "captureStartedUtc")
    capture_end = utc_at(audio, "captureEndedUtc")
    require(capture_start < capture_end, f"{role} capture window must be positive.")
    duration_ms = int_at(audio, "observedDurationMs")
    require(duration_ms > 0, f"{role} capture duration must be positive.")
    wave_format = object_at(audio, "waveFormat")
    endpoint = object_at(audio, "sanitizedEndpoint")
    endpoint_alias = endpoint.get("endpointAlias")
    endpoint_fingerprint = endpoint.get("endpointFingerprint")
    require(isinstance(endpoint_alias, str) and endpoint_alias, f"{role} must include a sanitized endpoint alias.")
    require(
        isinstance(endpoint_fingerprint, str) and len(endpoint_fingerprint) == 64,
        f"{role} must include a sanitized endpoint fingerprint.",
    )
    stats = object_at(audio, "audioStats")
    require(int_at(wave_format, "sampleRate") > 0, f"{role} sample rate must be positive.")
    require(int_at(wave_format, "channels") > 0, f"{role} channel count must be positive.")
    non_silent = bool_at(stats, "nonSilent")
    if require_non_silent:
        require(non_silent, f"{role} must observe non-silent output.")
    return {
        "durationMs": duration_ms,
        "sampleRate": wave_format["sampleRate"],
        "channels": wave_format["channels"],
        "endpointAlias": endpoint_alias,
        "endpointFingerprint": endpoint_fingerprint,
        "captureStartedUtc": audio["captureStartedUtc"],
        "captureEndedUtc": audio["captureEndedUtc"],
        "captureStartedAt": capture_start,
        "captureEndedAt": capture_end,
        "nonSilent": non_silent,
        "peakAbs": number_at(stats, "peakAbs"),
        "rms": number_at(stats, "rms"),
    }


def validate_run(run: dict[str, Any], role: str, *, staged: bool) -> dict[str, Any]:
    require(run.get("role") == role, f"Unexpected run role for {role}.")
    require(int_at(run, "levelId") == LEVEL_ID, f"{role} level must be {LEVEL_ID}.")
    patch_keys = string_set(list_at(run, "patchKeys"), f"{role} patchKeys")
    require(BASE_PATCH_KEYS.issubset(patch_keys), f"{role} must include base safe-copy patch keys.")
    launch_args = list_at(run, "launchArguments")
    launch_arg_text = {str(item) for item in launch_args}
    require("-level" in launch_arg_text and str(LEVEL_ID) in launch_arg_text, f"{role} launch args must include level {LEVEL_ID}.")
    require("-nomusic" not in launch_arg_text, f"{role} must not use -nomusic.")
    require("-nosound" not in launch_arg_text, f"{role} must not use -nosound.")

    music = run.get("musicReplacement")
    if staged:
        require(isinstance(music, dict), "staged positive run must include musicReplacement.")
        require(music.get("presetId") == PRESET_ID, "staged positive preset id changed.")
        require(music.get("target") == TARGET, "staged positive target changed.")
        require(music.get("replacement") == REPLACEMENT, "staged positive replacement changed.")
        require(music.get("targetRelativePath") == r"data\Music\BEA_04(Master).ogg", "staged positive target path binding changed.")
        require(bool_at(music, "targetNowMatchesReplacement"), "staged positive target must match replacement.")
        require(bool_at(music, "backupMatchesOriginal"), "staged positive backup must match original.")
    else:
        require(music is None, "clean baseline must not include staged music replacement.")

    runtime = validate_runtime_evidence(run, role)
    audio = validate_audio_capture(run, role, require_non_silent=True)
    require(audio["captureStartedAt"] <= runtime["decodeWindowStartAt"], f"{role} capture must start before or at CDB decode window.")
    require(audio["captureEndedAt"] >= runtime["decodeWindowEndAt"], f"{role} capture must cover the CDB decode window.")

    return {
        "sourceSafety": validate_source_safety(run, role),
        "runtime": runtime,
        "audio": audio,
        "patchKeys": sorted(patch_keys),
        "launchArguments": [str(item) for item in launch_args],
    }


def validate_comparison(payload: dict[str, Any]) -> dict[str, Any]:
    comparison = object_at(payload, "comparison")
    require(bool_at(comparison, "sameLevelAndLaunchArgsExceptMutation"), "comparison must preserve same level/launch args except mutation.")
    require(bool_at(comparison, "samePatchSetExceptMutation"), "comparison must preserve same safe-copy patch set except mutation.")
    require(bool_at(comparison, "sameAudioEndpointAndFormat"), "comparison must preserve the same audio endpoint and format.")
    require(bool_at(comparison, "cleanAndPositiveHaveCdbEvidence"), "comparison must include CDB evidence for both runs.")
    require(bool_at(comparison, "positiveAudioTimeCorrelatedWithDecode"), "positive audio must be time-correlated with CDB decode.")
    require(bool_at(comparison, "positiveDiffersFromCleanBaseline"), "positive staged run must differ from clean same-level baseline.")
    require(bool_at(comparison, "muteControlNotAcceptedAsAudibleProof"), "mute-control non-acceptance must be recorded.")
    baseline_rms = number_at(comparison, "cleanBaselineRms")
    positive_rms = number_at(comparison, "stagedPositiveRms")
    require(positive_rms >= 0.0 and baseline_rms >= 0.0, "RMS values must be non-negative.")
    return {
        "cleanBaselineRms": baseline_rms,
        "stagedPositiveRms": positive_rms,
        "positiveDiffersFromCleanBaseline": True,
    }


def validate_same_endpoint_and_format(*audios: dict[str, Any]) -> None:
    first = audios[0]
    for audio in audios[1:]:
        require(audio["endpointAlias"] == first["endpointAlias"], "audio endpoint alias mismatch.")
        require(audio["endpointFingerprint"] == first["endpointFingerprint"], "audio endpoint fingerprint mismatch.")
        require(audio["sampleRate"] == first["sampleRate"], "audio sample-rate mismatch.")
        require(audio["channels"] == first["channels"], "audio channel-count mismatch.")


def validate_controls(payload: dict[str, Any]) -> dict[str, Any]:
    controls = object_at(payload, "negativeControls")
    ambient = object_at(controls, "ambientNoBea")
    require(ambient.get("role") == "ambientNoBea", "ambient control role changed.")
    require(bool_at(ambient, "noBeaProcessObserved"), "ambient control must observe no BEA process.")
    ambient_audio = validate_audio_capture(ambient, "ambientNoBea", require_non_silent=False)
    require(not ambient_audio["nonSilent"], "ambient no-BEA control must stay below non-silent threshold.")

    mute = object_at(controls, "muteControl")
    require(mute.get("role") == "muteControl", "mute control role changed.")
    mute_args = {str(item) for item in list_at(mute, "launchArguments")}
    require("-nomusic" in mute_args or "-nosound" in mute_args, "mute control must use -nomusic or -nosound.")
    require(bool_at(mute, "notAcceptedAsAudibleProof"), "mute control must be recorded as non-acceptance evidence.")
    mute_audio = validate_audio_capture(mute, "muteControl", require_non_silent=False)
    require(not mute_audio["nonSilent"], "mute control must stay below non-silent threshold.")
    return {
        "ambientNonSilent": ambient_audio["nonSilent"],
        "muteNonSilent": mute_audio["nonSilent"],
        "ambientAudio": ambient_audio,
        "muteAudio": mute_audio,
    }


def validate_source_audio_correlation(payload: dict[str, Any]) -> dict[str, Any]:
    correlation = object_at(payload, "sourceAudioCorrelation")
    require(correlation.get("method") in {"bounded-fingerprint", "windowed-spectral-fingerprint"}, "source audio correlation method is not accepted.")
    require(correlation.get("fingerprintVersion") == SOURCE_AUDIO_FINGERPRINT_VERSION, "source audio fingerprint version changed.")
    require(correlation.get("cleanBaselineBestMatch") == TARGET, "clean baseline must correlate to BEA_04.")
    require(correlation.get("stagedPositiveBestMatch") == REPLACEMENT, "staged positive must correlate to BEA_02.")
    require(bool_at(correlation, "cleanBaselineTargetCorrelationGtReplacement"), "clean baseline must prefer BEA_04 over BEA_02.")
    require(bool_at(correlation, "stagedPositiveReplacementCorrelationGtTarget"), "staged positive must prefer BEA_02 over BEA_04.")
    require(bool_at(correlation, "rawAudioPublished") is False, "raw audio must not be published.")
    require(bool_at(correlation, "sourceAudioPathsPublished") is False, "source audio paths must not be published.")
    require(bool_at(correlation, "privateCapturePathsPublished") is False, "private capture paths must not be published.")
    clean_margin = number_at(correlation, "cleanBaselineMargin")
    staged_margin = number_at(correlation, "stagedPositiveMargin")
    minimum_margin = number_at(correlation, "minimumAcceptedMargin")
    require(minimum_margin >= MIN_SOURCE_AUDIO_MARGIN, "source-audio minimum margin too weak.")
    require(clean_margin >= minimum_margin, "clean baseline source-audio margin too weak.")
    require(staged_margin >= minimum_margin, "staged positive source-audio margin too weak.")
    scores = object_at(correlation, "scoreMatrix")
    for key in {
        "cleanBaselineVsTarget",
        "cleanBaselineVsReplacement",
        "stagedPositiveVsTarget",
        "stagedPositiveVsReplacement",
    }:
        score = number_at(scores, key)
        require(-1.0 <= score <= 1.0, f"{key} must be normalized.")
    return {
        "method": correlation["method"],
        "cleanBaselineBestMatch": correlation["cleanBaselineBestMatch"],
        "stagedPositiveBestMatch": correlation["stagedPositiveBestMatch"],
        "cleanBaselineMargin": clean_margin,
        "stagedPositiveMargin": staged_margin,
    }


def validate_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "Unexpected proof artifact schema.")
    require(payload.get("presetId") == PRESET_ID, "Audible proof must use the level-100 BEA_04 preset.")
    require(payload.get("target") == TARGET, "Audible proof target changed.")
    require(payload.get("replacement") == REPLACEMENT, "Audible proof replacement changed.")
    require(int_at(payload, "levelId") == LEVEL_ID, "Audible proof level changed.")
    require(payload.get("runtimeAudibleOutputProof") is True, "Accepted proof artifact must explicitly claim audible output after all checks pass.")

    runs = object_at(payload, "runs")
    clean = validate_run(object_at(runs, "cleanBaseline"), "cleanBaseline", staged=False)
    staged = validate_run(object_at(runs, "stagedPositive"), "stagedPositive", staged=True)
    comparison = validate_comparison(payload)
    controls = validate_controls(payload)
    validate_same_endpoint_and_format(clean["audio"], staged["audio"], controls["ambientAudio"], controls["muteAudio"])
    correlation = validate_source_audio_correlation(payload)

    non_claims = string_set(list_at(payload, "nonClaims"), "nonClaims")
    for token in {
        "not arbitrary external OGG compatibility",
        "not all music cues",
        "not loop behavior proof",
        "not volume behavior proof",
        "not gameplay parity",
        "not rebuild parity",
        "not no-noticeable-difference parity",
    }:
        require(token in non_claims, f"Required non-claim missing: {token}")

    return {
        "schema": SCHEMA,
        "presetId": PRESET_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "levelId": LEVEL_ID,
        "runtimeAudibleOutputProof": True,
        "cleanBaselineNonSilent": clean["audio"]["nonSilent"],
        "stagedPositiveNonSilent": staged["audio"]["nonSilent"],
        "ambientControlNonSilent": controls["ambientNonSilent"],
        "muteControlNonSilent": controls["muteNonSilent"],
        "sourceAudioCorrelationMethod": correlation["method"],
        "positiveDiffersFromCleanBaseline": comparison["positiveDiffersFromCleanBaseline"],
        "claimBoundary": (
            "Two-run safe-copy proof plus negative controls only: clean same-level baseline versus "
            "staged BEA_02-over-BEA_04 positive with exact-PID CDB decode, bounded audio capture, "
            "ambient/mute controls, and source-track correlation."
        ),
    }


def _audio(non_silent: bool, *, rms: float, peak: float) -> dict[str, Any]:
    return {
        "schemaVersion": "audio-loopback-capture.v1",
        "status": "captured",
        "captureKind": "wasapi-loopback",
        "boundedOutputArtifact": True,
        "startsBeforeExpectedMusicKick": True,
        "endsAfterDecodeBegins": True,
        "captureStartedUtc": "2026-06-22T00:00:00Z",
        "captureEndedUtc": "2026-06-22T00:00:03Z",
        "observedDurationMs": 3000,
        "sanitizedEndpoint": {
            "endpointAlias": "default-render-endpoint",
            "endpointFingerprint": "a" * 64,
        },
        "waveFormat": {
            "sampleRate": 48000,
            "channels": 2,
        },
        "audioStats": {
            "peakAbs": peak,
            "rms": rms,
            "nonSilent": non_silent,
        },
    }


def _cdb(include_decode: bool) -> dict[str, Any]:
    return {
        "exactPidCdbObserver": True,
        "levelId": LEVEL_ID,
        "selectionId": SELECTION_ID,
        "playMusicForCurrentLevelObserved": include_decode,
        "playSelectionObserved": include_decode,
        "asyncKickPathMatched": include_decode,
        "oggOpenPathMatched": include_decode,
        "decodedPcmPositiveRequestObserved": include_decode,
        "decodeWindowStartUtc": "2026-06-22T00:00:01Z",
        "decodeWindowEndUtc": "2026-06-22T00:00:02Z",
    }


def _source_safety(ok: bool) -> dict[str, bool]:
    return {
        "installedHashUnchanged": ok,
        "overrideHashUnchanged": ok,
        "sourceTargetHashUnchanged": ok,
        "sourceReplacementHashUnchanged": ok,
        "noPreexistingBea": ok,
        "noBeaAfterStop": ok,
    }


def _run(role: str, *, staged: bool, include_decode: bool, source_ok: bool) -> dict[str, Any]:
    run: dict[str, Any] = {
        "role": role,
        "levelId": LEVEL_ID,
        "patchKeys": sorted(BASE_PATCH_KEYS),
        "launchArguments": ["-skipfmv", "-level", str(LEVEL_ID)],
        "sourceSafety": _source_safety(source_ok),
        "cdbSelectionDecode": _cdb(include_decode),
        "audioCapture": _audio(True, rms=0.010 if staged else 0.006, peak=0.03 if staged else 0.02),
    }
    if staged:
        run["musicReplacement"] = {
            "presetId": PRESET_ID,
            "target": TARGET,
            "replacement": REPLACEMENT,
            "targetRelativePath": r"data\Music\BEA_04(Master).ogg",
            "targetNowMatchesReplacement": True,
            "backupMatchesOriginal": True,
        }
    else:
        run["musicReplacement"] = None
    return run


def fixture(
    root: Path,
    *,
    clean_has_decode: bool = True,
    positive_has_decode: bool = True,
    source_hashes_unchanged: bool = True,
    positive_differs_from_baseline: bool = True,
    include_controls: bool = True,
    source_audio_correlation: bool = True,
) -> dict[str, Any]:
    _ = root
    payload: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "presetId": PRESET_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "levelId": LEVEL_ID,
        "runtimeAudibleOutputProof": True,
        "runs": {
            "cleanBaseline": _run(
                "cleanBaseline",
                staged=False,
                include_decode=clean_has_decode,
                source_ok=source_hashes_unchanged,
            ),
            "stagedPositive": _run(
                "stagedPositive",
                staged=True,
                include_decode=positive_has_decode,
                source_ok=source_hashes_unchanged,
            ),
        },
        "comparison": {
            "sameLevelAndLaunchArgsExceptMutation": True,
            "samePatchSetExceptMutation": True,
            "sameAudioEndpointAndFormat": True,
            "cleanAndPositiveHaveCdbEvidence": clean_has_decode and positive_has_decode,
            "positiveAudioTimeCorrelatedWithDecode": positive_has_decode,
            "positiveDiffersFromCleanBaseline": positive_differs_from_baseline,
            "muteControlNotAcceptedAsAudibleProof": True,
            "cleanBaselineRms": 0.006,
            "stagedPositiveRms": 0.010,
        },
        "nonClaims": [
            "not arbitrary external OGG compatibility",
            "not all music cues",
            "not loop behavior proof",
            "not volume behavior proof",
            "not gameplay parity",
            "not rebuild parity",
            "not no-noticeable-difference parity",
        ],
    }
    if include_controls:
        payload["negativeControls"] = {
            "ambientNoBea": {
                "role": "ambientNoBea",
                "noBeaProcessObserved": True,
                "audioCapture": _audio(False, rms=0.00001, peak=0.0001),
            },
            "muteControl": {
                "role": "muteControl",
                "launchArguments": ["-skipfmv", "-level", str(LEVEL_ID), "-nomusic"],
                "notAcceptedAsAudibleProof": True,
                "audioCapture": _audio(False, rms=0.00003, peak=0.0002),
            },
        }
    if source_audio_correlation:
        payload["sourceAudioCorrelation"] = {
            "method": "bounded-fingerprint",
            "fingerprintVersion": SOURCE_AUDIO_FINGERPRINT_VERSION,
            "cleanBaselineBestMatch": TARGET,
            "stagedPositiveBestMatch": REPLACEMENT,
            "cleanBaselineTargetCorrelationGtReplacement": True,
            "stagedPositiveReplacementCorrelationGtTarget": True,
            "cleanBaselineMargin": 0.78,
            "stagedPositiveMargin": 0.78,
            "minimumAcceptedMargin": MIN_SOURCE_AUDIO_MARGIN,
            "rawAudioPublished": False,
            "sourceAudioPathsPublished": False,
            "privateCapturePathsPublished": False,
            "scoreMatrix": {
                "cleanBaselineVsTarget": 1.0,
                "cleanBaselineVsReplacement": 0.22,
                "stagedPositiveVsTarget": 0.22,
                "stagedPositiveVsReplacement": 1.0,
            },
        }
    return payload


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        validate_artifact(fixture(root))
        for kwargs in (
            {"clean_has_decode": False},
            {"positive_has_decode": False},
            {"source_hashes_unchanged": False},
            {"positive_differs_from_baseline": False},
            {"include_controls": False},
            {"source_audio_correlation": False},
        ):
            try:
                validate_artifact(fixture(root, **kwargs))
            except ProofError:
                pass
            else:
                raise ProofError(f"Self-test expected fixture to fail: {kwargs}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Two-run audible-output proof JSON artifact")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music audible-output two-run harness checker self-test: PASS")
            return 0
        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        print(json.dumps(validate_artifact(read_json(Path(args.artifact))), indent=2, sort_keys=True))
        return 0
    except ProofError as exc:
        print(f"WinUI safe-copy music audible-output two-run harness check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
