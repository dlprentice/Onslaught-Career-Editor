#!/usr/bin/env python3
"""Validate sanitized live capture-to-source music correlation adapter artifacts.

This checker is an adapter gate for future live capture summaries. It produces
the sourceAudioCorrelation object expected by the two-run audible-output checker,
but it does not claim runtime audible output.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "winui-safe-copy-music-capture-source-correlation.v1"
ADAPTER_VERSION = "capture-source-correlation-helper.v1"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
SOURCE_AUDIO_FINGERPRINT_VERSION = "source-audio-correlation-helper.v1"
WINDOW_COUNT = 128
MIN_ACTIVE_WINDOW_COUNT = 16
MIN_ACCEPTED_MARGIN = 0.15
ACCEPTED_METHODS = {"windowed-spectral-fingerprint", "bounded-fingerprint"}
REQUIRED_NON_CLAIMS = {
    "not runtime audible BEA playback",
    "not standalone audible-output proof",
    "not raw audio publication",
    "not private path publication",
    "not RMS or peak-only proof",
    "not all music cues",
    "not gameplay parity",
    "not rebuild parity",
}
FORBIDDEN_PAYLOAD_KEYS = {
    "capturepath",
    "deviceid",
    "devicestableid",
    "endpointid",
    "envelopebuckets",
    "oggbase64",
    "oggbytes",
    "outputjson",
    "outputwav",
    "pcmbase64",
    "rawaudio",
    "rawaudiobase64",
    "rawpcm",
    "rawpcmbase64",
    "rawsamples",
    "samples",
    "sourcepath",
    "spectrogram",
    "spectrogrambins",
    "wavbase64",
    "wavbytes",
}


class CorrelationAdapterError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CorrelationAdapterError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "Adapter artifact must be a JSON object.")
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
    require(isinstance(child, int) and not isinstance(child, bool), f"Missing integer: {key}")
    return child


def number_at(value: dict[str, Any], key: str) -> float:
    child = value.get(key)
    require(isinstance(child, (int, float)) and not isinstance(child, bool), f"Missing number: {key}")
    numeric = float(child)
    require(math.isfinite(numeric), f"{key} must be finite.")
    return numeric


def normalized_key(key: object) -> str:
    return str(key).replace("_", "").replace("-", "").lower()


def has_forbidden_payload_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if normalized_key(key) in FORBIDDEN_PAYLOAD_KEYS:
                return True
            if has_forbidden_payload_key(child):
                return True
    elif isinstance(value, list):
        return any(has_forbidden_payload_key(child) for child in value)
    return False


def has_private_path_text(value: Any) -> bool:
    if isinstance(value, dict):
        return any(has_private_path_text(child) for child in value.values())
    if isinstance(value, list):
        return any(has_private_path_text(child) for child in value)
    if isinstance(value, str):
        lowered = value.lower()
        return (
            ":\\" in value
            or ":/" in value
            or "\\users\\" in lowered
            or "program files" in lowered
            or "steamapps" in lowered
            or str(ROOT).lower() in lowered
        )
    return False


def validate_capture_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    capture = object_at(payload, "captureAnalysis")
    method = capture.get("method")
    require(method in ACCEPTED_METHODS, "capture analysis method is not accepted.")
    require(method != "rms-peak-delta", "RMS/peak-only capture analysis is not accepted.")
    window_count = int_at(capture, "windowCount")
    minimum_active = int_at(capture, "minimumActiveWindowCount")
    clean_active = int_at(capture, "cleanBaselineActiveWindowCount")
    staged_active = int_at(capture, "stagedPositiveActiveWindowCount")
    require(window_count == WINDOW_COUNT, "capture window count changed.")
    require(minimum_active >= MIN_ACTIVE_WINDOW_COUNT, "minimum active window count is too weak.")
    require(clean_active >= minimum_active, "clean baseline has too few active analysis windows.")
    require(staged_active >= minimum_active, "staged positive has too few active analysis windows.")
    require(capture.get("rmsPeakOnly") is not True, "RMS/peak-only evidence is not accepted.")
    return {
        "method": method,
        "windowCount": window_count,
        "minimumActiveWindowCount": minimum_active,
        "cleanBaselineActiveWindowCount": clean_active,
        "stagedPositiveActiveWindowCount": staged_active,
    }


def validate_source_audio_correlation(payload: dict[str, Any], method: str) -> dict[str, Any]:
    correlation = object_at(payload, "sourceAudioCorrelation")
    require(correlation.get("method") == method, "capture and source-correlation methods must match.")
    require(correlation.get("method") in ACCEPTED_METHODS, "source correlation method is not accepted.")
    require(correlation.get("fingerprintVersion") == SOURCE_AUDIO_FINGERPRINT_VERSION, "source audio fingerprint version changed.")
    require(correlation.get("cleanBaselineBestMatch") == TARGET, "clean baseline must correlate to BEA_04.")
    require(correlation.get("stagedPositiveBestMatch") == REPLACEMENT, "staged positive must correlate to BEA_02.")
    require(bool_at(correlation, "rawAudioPublished") is False, "raw audio must not be published.")
    require(bool_at(correlation, "sourceAudioPathsPublished") is False, "source audio paths must not be published.")
    require(bool_at(correlation, "privateCapturePathsPublished") is False, "private capture paths must not be published.")

    clean_margin = number_at(correlation, "cleanBaselineMargin")
    staged_margin = number_at(correlation, "stagedPositiveMargin")
    minimum_margin = number_at(correlation, "minimumAcceptedMargin")
    require(minimum_margin >= MIN_ACCEPTED_MARGIN, "source-audio minimum margin too weak.")
    require(clean_margin >= minimum_margin, "clean baseline source-audio margin too weak.")
    require(staged_margin >= minimum_margin, "staged positive source-audio margin too weak.")

    scores = object_at(correlation, "scoreMatrix")
    clean_target = number_at(scores, "cleanBaselineVsTarget")
    clean_replacement = number_at(scores, "cleanBaselineVsReplacement")
    staged_target = number_at(scores, "stagedPositiveVsTarget")
    staged_replacement = number_at(scores, "stagedPositiveVsReplacement")
    for label, score in {
        "cleanBaselineVsTarget": clean_target,
        "cleanBaselineVsReplacement": clean_replacement,
        "stagedPositiveVsTarget": staged_target,
        "stagedPositiveVsReplacement": staged_replacement,
    }.items():
        require(-1.0 <= score <= 1.0, f"{label} must be normalized.")

    require(clean_target > clean_replacement, "clean baseline scores must prefer BEA_04 over BEA_02.")
    require(staged_replacement > staged_target, "staged positive scores must prefer BEA_02 over BEA_04.")
    require(abs((clean_target - clean_replacement) - clean_margin) <= 0.000001, "clean baseline margin drifted from score matrix.")
    require(abs((staged_replacement - staged_target) - staged_margin) <= 0.000001, "staged positive margin drifted from score matrix.")
    require(bool_at(correlation, "cleanBaselineTargetCorrelationGtReplacement") is True, "clean preference boolean must be true.")
    require(bool_at(correlation, "stagedPositiveReplacementCorrelationGtTarget") is True, "staged preference boolean must be true.")

    return correlation


def validate_input_bindings(payload: dict[str, Any]) -> dict[str, str]:
    bindings = object_at(payload, "inputBindings")
    result: dict[str, str] = {}
    for key in {
        "cleanAudioJsonSha256",
        "cleanAudioWavSha256",
        "stagedAudioJsonSha256",
        "stagedAudioWavSha256",
    }:
        value = bindings.get(key)
        require(isinstance(value, str) and bool(value), f"Missing input binding: {key}")
        normalized = value.lower()
        require(bool(re.fullmatch(r"[0-9a-f]{64}", normalized)), f"{key} must be SHA-256 hex.")
        result[key] = normalized
    return result


def validate_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "Unexpected capture-source correlation schema.")
    require(payload.get("adapterVersion") == ADAPTER_VERSION, "Unexpected adapter version.")
    require(payload.get("presetId") == PRESET_ID, "Preset id changed.")
    require(payload.get("target") == TARGET, "Target track changed.")
    require(payload.get("replacement") == REPLACEMENT, "Replacement track changed.")
    require(int_at(payload, "levelId") == LEVEL_ID, "Level id changed.")
    require("runtimeAudibleOutputProof" not in payload, "Adapter artifact must not carry runtimeAudibleOutputProof.")
    require(not has_private_path_text(payload), "Artifact contains private path-like text.")
    require(not has_forbidden_payload_key(payload), "Artifact contains raw/private audio payload keys.")

    bindings = validate_input_bindings(payload)
    capture = validate_capture_analysis(payload)
    correlation = validate_source_audio_correlation(payload, str(capture["method"]))

    non_claims = {str(item) for item in list_at(payload, "nonClaims")}
    for token in REQUIRED_NON_CLAIMS:
        require(token in non_claims, f"Missing non-claim: {token}")

    return {
        "schema": SCHEMA,
        "adapterVersion": ADAPTER_VERSION,
        "presetId": PRESET_ID,
        "levelId": LEVEL_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "runtimeAudibleOutputProof": False,
        "cleanBaselineBestMatch": correlation["cleanBaselineBestMatch"],
        "stagedPositiveBestMatch": correlation["stagedPositiveBestMatch"],
        "cleanBaselineMargin": correlation["cleanBaselineMargin"],
        "stagedPositiveMargin": correlation["stagedPositiveMargin"],
        "sourceAudioCorrelation": correlation,
        "inputBindings": bindings,
        "claimBoundary": "Adapter only: source-bound capture correlation for a future two-run proof, not current audible output proof.",
    }


def fixture() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA,
        "adapterVersion": ADAPTER_VERSION,
        "generatedAt": "2026-06-22T00:00:00Z",
        "presetId": PRESET_ID,
        "levelId": LEVEL_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "inputBindings": {
            "cleanAudioJsonSha256": "1" * 64,
            "cleanAudioWavSha256": "2" * 64,
            "stagedAudioJsonSha256": "3" * 64,
            "stagedAudioWavSha256": "4" * 64,
        },
        "captureAnalysis": {
            "method": "windowed-spectral-fingerprint",
            "windowCount": WINDOW_COUNT,
            "minimumActiveWindowCount": MIN_ACTIVE_WINDOW_COUNT,
            "cleanBaselineActiveWindowCount": 92,
            "stagedPositiveActiveWindowCount": 96,
            "rmsPeakOnly": False,
        },
        "sourceAudioCorrelation": {
            "method": "windowed-spectral-fingerprint",
            "fingerprintVersion": SOURCE_AUDIO_FINGERPRINT_VERSION,
            "cleanBaselineBestMatch": TARGET,
            "stagedPositiveBestMatch": REPLACEMENT,
            "cleanBaselineTargetCorrelationGtReplacement": True,
            "stagedPositiveReplacementCorrelationGtTarget": True,
            "cleanBaselineMargin": 0.72,
            "stagedPositiveMargin": 0.73,
            "minimumAcceptedMargin": MIN_ACCEPTED_MARGIN,
            "rawAudioPublished": False,
            "sourceAudioPathsPublished": False,
            "privateCapturePathsPublished": False,
            "scoreMatrix": {
                "cleanBaselineVsTarget": 0.91,
                "cleanBaselineVsReplacement": 0.19,
                "stagedPositiveVsTarget": 0.18,
                "stagedPositiveVsReplacement": 0.91,
            },
        },
        "claimBoundary": "Capture-to-source correlation adapter only. Not runtime audible-output proof.",
        "nonClaims": sorted(REQUIRED_NON_CLAIMS),
    }


def self_test() -> None:
    validate_artifact(fixture())
    for mutator in (
        lambda payload: payload.__setitem__("runtimeAudibleOutputProof", True),
        lambda payload: payload["captureAnalysis"].__setitem__("outputWav", r"C:\temp\capture.wav"),
        lambda payload: payload["captureAnalysis"].__setitem__("spectrogramBins", [0.1]),
        lambda payload: payload["sourceAudioCorrelation"].__setitem__("cleanBaselineMargin", 0.01),
        lambda payload: payload["sourceAudioCorrelation"]["scoreMatrix"].__setitem__("cleanBaselineVsTarget", 0.1),
        lambda payload: payload["captureAnalysis"].__setitem__("cleanBaselineActiveWindowCount", 2),
        lambda payload: payload["sourceAudioCorrelation"].__setitem__("stagedPositiveReplacementCorrelationGtTarget", False),
    ):
        payload = fixture()
        mutator(payload)
        try:
            validate_artifact(payload)
        except CorrelationAdapterError:
            pass
        else:
            raise CorrelationAdapterError("Self-test expected invalid fixture to fail.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Sanitized capture-to-source correlation JSON artifact")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music capture-source correlation checker self-test: PASS")
            return 0
        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        print(json.dumps(validate_artifact(read_json(Path(args.artifact))), indent=2, sort_keys=True))
        return 0
    except CorrelationAdapterError as exc:
        print(f"WinUI safe-copy music capture-source correlation check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
