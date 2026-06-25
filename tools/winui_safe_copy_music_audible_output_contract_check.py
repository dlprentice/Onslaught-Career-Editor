#!/usr/bin/env python3
"""Validate the public-safe WinUI safe-copy music audible-output contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "roadmap" / "music-audible-proof-contract.v1.json"

EXPECTED_SCHEMA = "music-audible-proof-contract.v1"
EXPECTED_SCOPE = "public-audible-proof-contract-not-audio-capture-revalidation"

DOC_TOKENS = {
    "roadmap/music-audible-proof-contract.v1.json": [
        '"schemaVersion": "music-audible-proof-contract.v1"',
        '"audioLoopbackBackendPreflight": true',
        '"audioLoopbackCalibrationNonSilent": true',
        '"twoRunHarnessAcceptanceChecker": true',
        '"trustedRawArtifactMaterializer": true',
        '"liveRawBundleGate": true',
        '"liveBundleExecutor": true',
        '"ambientNoBeaCensusProducer": true',
        '"sourceMusicSafetySidecarProducer": true',
        '"sourceAudioReferenceFingerprint": true',
        '"captureSourceCorrelationAdapter": true',
        '"captureSourceCorrelationBuilder": true',
        '"timestampedCdbLogProducer": true',
        '"loopbackWallClockPaddingHelper": true',
        '"rawWavDataDurationMaterializerGuard": true',
        '"runtimeAudibleOutputProof": false',
        '"negativeControls"',
        '"sourceAudioCorrelation"',
        '"audioCapture"',
        "raw WAV data duration must cover the reported capture window",
        "raw WAV blockAlign must equal channels * bitsPerSample / 8",
        "WASAPI loopback quiet gaps must be represented as explicit zero-silence padding",
        "materializer independently derives raw WAV data duration from canonical RIFF sample-rate/block-align/data-frame math",
        "materializer requires enabled wallClockPadding metadata",
        '"positive staged run differs from a clean same-level baseline"',
        '"not current audible playback proof"',
    ],
    "release/readiness/winui_music_audible_output_materializer_2026-06-23.md": [
        "Status: trusted materializer gate only",
        "winui_safe_copy_music_audible_output_materializer.py",
        "winui_safe_copy_music_cdb_timeline_sidecar.py",
        "timestamped CDB decode timeline sidecars",
        "raw live CDB log SHA-256",
        "timestamped CDB evidence log SHA-256",
        "timestamped raw CDB rows",
        "helper-authored rawWavSha256",
        "independently rederived WAV sample statistics",
        "ambient no-BEA process census sidecar",
        "bound to clean/staged audio JSON and raw WAV SHA-256 values",
        "materialized output must stay inside the private raw input bundle",
        "runtimeAudibleOutputProof=false",
        "not current audible playback proof",
    ],
    "release/readiness/winui_music_audible_output_live_bundle_gate_2026-06-24.md": [
        "Status: complete proof-gate infrastructure",
        "winui_safe_copy_music_audible_output_live_bundle_gate.py",
        "winui_safe_copy_music_ambient_no_bea_census.py",
        "winui_safe_copy_music_source_music_safety_sidecar.py",
        "winui_safe_copy_music_capture_source_correlation_builder.py",
        "winui_safe_copy_music_timestamped_cdb_log_producer.py",
        "runtimeAudibleOutputProof=false",
        "producer coverage is complete",
        "no BEA launch",
        "no audio capture",
    ],
    "release/readiness/winui_music_audible_output_live_bundle_executor_2026-06-24.md": [
        "Status: private executor/checker infrastructure only",
        "run_winui_safe_copy_music_audible_output_live_bundle.py",
        "test:winui-safe-copy-music-audible-output-live-bundle-executor",
        "liveBundleExecutor=true",
        "RUN PRIVATE MUSIC AUDIBLE LIVE BUNDLE",
        "runtimeAudibleOutputProof=false",
        "no installed-game mutation",
        "no original executable mutation",
    ],
    "release/readiness/winui_music_ambient_no_bea_census_2026-06-24.md": [
        "Status: producer/checker infrastructure only",
        "winui_safe_copy_music_ambient_no_bea_census.py",
        "winui-safe-copy-no-bea-process-census.v1",
        "rejects the sidecar if any observed process",
        "runtimeAudibleOutputProof=false",
        "producer coverage is complete",
    ],
    "release/readiness/winui_music_source_music_safety_sidecar_2026-06-24.md": [
        "Status: producer/checker infrastructure only",
        "winui_safe_copy_music_source_music_safety_sidecar.py",
        "winui-safe-copy-source-music-safety.v1",
        "before-run source music hash snapshot",
        "sourceTargetHashUnchanged",
        "sourceReplacementHashUnchanged",
        "runtimeAudibleOutputProof=false",
        "producer coverage is complete",
    ],
    "release/readiness/winui_music_capture_source_correlation_builder_2026-06-24.md": [
        "Status: producer/checker infrastructure only",
        "winui_safe_copy_music_capture_source_correlation_builder.py",
        "winui-safe-copy-music-capture-source-correlation.v1",
        "winui-safe-copy-music-capture-source-correlation-rejection.v1",
        "not accepted by the adapter validator",
        "captureSourceCorrelationBuilder=true",
        "runtimeAudibleOutputProof=false",
        "producer coverage is complete",
        "no BEA launch",
        "no audio capture",
    ],
    "release/readiness/winui_music_capture_source_correlation_rejected_replay_2026-06-24.md": [
        "Status: rejected local replay diagnostic",
        "winui-safe-copy-music-capture-source-correlation-rejection.v1",
        "winui-safe-copy-music-rejected-replay-diagnostic.v1",
        "winui-safe-copy-music-decode-window-correlation-diagnostic.v1",
        "test:winui-safe-copy-music-decode-window-correlation-diagnostic",
        "stagedFileLayoutProven=true",
        "exactPidDecodeTimelineProven=true",
        "captureSourceCorrelationRejected=true",
        "decodeWindowInsideRawAudioCapture",
        "capture-window-out-of-range",
        "46208.935ms",
        "44148.22ms",
        "staged-positive-source-correlation-margin-too-weak",
        "stagedPositiveBestMatch=BEA_04(Master).ogg",
        "runtimeAudibleOutputProof=false",
        "not accepted capture-source correlation",
        "not materializer input",
    ],
    "release/readiness/winui_music_timestamped_cdb_log_producer_2026-06-24.md": [
        "Status: producer/checker infrastructure only",
        "winui_safe_copy_music_timestamped_cdb_log_producer.py",
        "winui-safe-copy-timestamped-cdb-log.v1",
        "trusted-tail-wrapper-observation-ledger",
        "runtimeAudibleOutputProof=false",
        "producer coverage is complete",
        "no BEA launch",
        "no CDB attach",
        "no audio capture",
    ],
    "release/readiness/winui_music_audible_proof_contract_2026-06-22.md": [
        "Status: contract guard only",
        "runtimeAudibleOutputProof=false",
        "bounded loopback or equivalent output-capture artifact",
        "positive staged run differs from a clean same-level baseline",
        "ambient/no-BEA and mute-control negative controls",
        "source-audio correlation",
        "not current audible playback proof",
    ],
    "CURRENT_CAPABILITIES.md": [
        "Music audible-proof contract:",
        "decodeWindowInsideRawAudioCapture=false",
        "runtimeAudibleOutputProof=false",
        "two-run harness checker",
        "negative controls",
        "positive staged run differs from a clean same-level baseline",
        "not accepted capture-source correlation",
        "not materializer input",
    ],
    "roadmap/mod-patch-runtime-rebuild-register.md": [
        "2026-06-24 music rejected replay addendum",
        "2026-06-24 music decode-window correlation diagnostic addendum",
        "test:winui-safe-copy-music-decode-window-correlation-diagnostic",
        "capture-window-out-of-range",
        "2026-06-22 music audible-proof contract addendum",
        "runtimeAudibleOutputProof=false",
        "not accepted capture-source correlation",
        "not materializer input",
        "audio-loopback backend preflight",
        "two-run harness checker",
        "source-audio correlation",
        "positive staged run differs from a clean same-level baseline",
    ],
    "release/readiness/winui_music_audio_loopback_preflight_2026-06-22.md": [
        "Status: private helper preflight",
        "audioLoopbackBackendPreflight=true",
        "audioLoopbackCalibrationNonSilent=true",
        "runtimeAudibleOutputProof=false",
    ],
    "release/readiness/winui_music_audible_output_two_run_harness_2026-06-22.md": [
        "Status: acceptance checker only",
        "ambient/no-BEA and mute-control negative controls",
        "source-audio correlation",
        "runtimeAudibleOutputProof=false",
        "not current audible playback proof",
    ],
    "release/readiness/winui_music_source_audio_correlation_2026-06-22.md": [
        "Status: private source-reference preflight",
        "sourceAudioReferenceFingerprint=true",
        "sourceDistinctMargin=0.7800401732295956",
        "runtimeAudibleOutputProof=false",
        "not runtime audible BEA playback",
    ],
    "release/readiness/winui_music_capture_source_correlation_adapter_2026-06-22.md": [
        "Status: adapter/checker only",
        "captureSourceCorrelationAdapter=true",
        "runtimeAudibleOutputProof=false",
        "not standalone audible-output proof",
        "not raw audio publication",
    ],
    "OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml": [
        "PatchBenchMusicAudibleProofContractStatus",
        "Audible proof still requires a bounded audio-output capture",
        "Staging and CDB decode are not audible playback proof.",
    ],
    "OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs": [
        "PatchBenchMusicAudibleProofContractStatus",
        "Audible proof still requires a bounded audio-output capture",
    ],
    "package.json": [
        "\"test:winui-safe-copy-music-audible-output-contract\"",
        "\"test:winui-safe-copy-music-audible-output-two-run-harness\"",
        "\"test:winui-safe-copy-music-timestamped-cdb-log-producer\"",
        "\"test:winui-safe-copy-music-cdb-timeline-sidecar\"",
        "\"test:winui-safe-copy-music-source-music-safety-sidecar\"",
        "\"test:winui-safe-copy-music-audible-output-live-bundle-gate\"",
        "\"test:winui-safe-copy-music-audible-output-live-bundle-executor\"",
        "\"test:winui-safe-copy-music-ambient-no-bea-census\"",
        "\"test:winui-safe-copy-music-source-audio-correlation\"",
        "\"test:winui-safe-copy-music-capture-source-correlation\"",
        "\"test:winui-safe-copy-music-capture-source-correlation-builder\"",
        "\"test:winui-safe-copy-music-rejected-replay-diagnostic\"",
        "\"test:winui-safe-copy-music-decode-window-correlation-diagnostic\"",
    ],
}


class ContractError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object.")
    return value


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def string_set(value: list[Any], label: str) -> set[str]:
    require(all(isinstance(item, str) for item in value), f"{label} must contain only strings.")
    return {str(item) for item in value}


def assert_contract() -> dict[str, Any]:
    payload = read_json(CONTRACT_PATH)
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "contract schema changed")
    require(payload.get("checkerScope") == EXPECTED_SCOPE, "contract checker scope changed")
    require(payload.get("scope") == "safe-copy-music-audible-output-acceptance-boundary", "contract scope changed")

    accepted = object_at(payload, "currentAcceptedEvidence")
    require(accepted.get("safeCopyStaging") is True, "contract must preserve staging proof")
    require(accepted.get("sourceMusicUnchanged") is True, "contract must preserve source-music safety")
    require(accepted.get("copiedTargetMatchesReplacement") is True, "contract must preserve copied target/replacement evidence")
    require(accepted.get("restoreManifest") is True, "contract must preserve restore-manifest evidence")
    require(accepted.get("level100SelectionDecodeProofs") == 2, "selection/decode proof count changed")
    require(accepted.get("namedPresetSelectionDecodeProof") == "use-bea02-for-bea04", "named preset anchor changed")
    require(accepted.get("audioLoopbackBackendPreflight") is True, "audio loopback backend preflight must remain recorded")
    require(accepted.get("audioLoopbackCalibrationNonSilent") is True, "audio loopback calibration preflight must remain recorded")
    require(accepted.get("twoRunHarnessAcceptanceChecker") is True, "two-run harness checker must remain recorded")
    require(accepted.get("trustedRawArtifactMaterializer") is True, "trusted materializer must remain recorded")
    require(accepted.get("liveRawBundleGate") is True, "live raw-bundle gate must remain recorded")
    require(accepted.get("liveBundleExecutor") is True, "live raw-bundle executor must remain recorded")
    require(accepted.get("ambientNoBeaCensusProducer") is True, "ambient no-BEA census producer must remain recorded")
    require(accepted.get("sourceMusicSafetySidecarProducer") is True, "source-music safety sidecar producer must remain recorded")
    require(accepted.get("sourceAudioReferenceFingerprint") is True, "source-audio reference fingerprint must remain recorded")
    require(accepted.get("captureSourceCorrelationAdapter") is True, "capture-to-source adapter must remain recorded")
    require(accepted.get("captureSourceCorrelationBuilder") is True, "capture-to-source builder must remain recorded")
    require(accepted.get("timestampedCdbLogProducer") is True, "timestamped CDB log producer must remain recorded")
    require(accepted.get("loopbackWallClockPaddingHelper") is True, "loopback wall-clock padding helper must remain recorded")
    require(accepted.get("rawWavDataDurationMaterializerGuard") is True, "raw WAV duration materializer guard must remain recorded")
    require(accepted.get("runtimeAudibleOutputProof") is False, "current contract must not claim audible output proof")

    minimum = object_at(payload, "minimumAudibleProof")
    require(minimum.get("artifactSchema") == "winui-safe-copy-music-audible-output-proof.v1", "audible artifact schema changed")
    source_safety = string_set(list_at(minimum, "sourceSafety"), "sourceSafety")
    safe_inputs = string_set(list_at(minimum, "safeCopyInputs"), "safeCopyInputs")
    runtime_decode = string_set(list_at(minimum, "runtimeSelectionDecode"), "runtimeSelectionDecode")
    audio_capture = string_set(list_at(minimum, "audioCapture"), "audioCapture")
    controls = string_set(list_at(minimum, "comparisonControls"), "comparisonControls")
    materialization = string_set(list_at(minimum, "materialization"), "materialization")
    negative_controls = string_set(list_at(minimum, "negativeControls"), "negativeControls")
    source_audio = string_set(list_at(minimum, "sourceAudioCorrelation"), "sourceAudioCorrelation")

    for token in {
        "installedHashUnchanged",
        "overrideHashUnchanged",
        "sourceTargetHashUnchanged",
        "sourceReplacementHashUnchanged",
        "noPreexistingBea",
        "noBeaAfterStop",
    }:
        require(token in source_safety, f"source-safety requirement missing: {token}")

    for token in {
        "resolution_gate",
        "force_windowed",
        "no -nomusic launch argument",
        "no -nosound launch argument",
        "targetNowMatchesReplacement",
        "backupMatchesOriginal",
    }:
        require(token in safe_inputs, f"safe-copy input requirement missing: {token}")

    for token in {
        "CGame music-selection provenance observed for the intended level via wrapper or restart-loop direct call",
        "CMusic__PlaySelection observed for the intended selection",
        "PCPlatform__KickAsyncMusicStreamRead path matches the staged target",
        "COggFileRead__OpenFileAndPrimeDecoder path matches the staged target",
        "COggFileRead__ReadDecodedPcm positive request observed",
    }:
        require(token in runtime_decode, f"runtime decode requirement missing: {token}")

    for token in {
        "bounded loopback or equivalent output-capture artifact",
        "capture starts before the expected music kick and ends after decode begins",
        "capture start/end UTC timestamps are reported and compared against the CDB decode window",
        "capture duration is positive and reported in milliseconds",
        "raw WAV data duration must cover the reported capture window and any CDB decode window being evaluated",
        "raw WAV blockAlign must equal channels * bitsPerSample / 8, byteRate must equal sampleRate * blockAlign, and data length must be block aligned",
        "WASAPI loopback quiet gaps must be represented as explicit zero-silence padding or equivalent wall-clock-preserving samples",
        "sample rate and channel count are reported",
        "sanitized audio endpoint alias/fingerprint is reported without raw device identifiers",
        "clean baseline and staged positive both observe non-silent signal in the expected window",
        "positive staged run differs from a clean same-level baseline",
        "mute-control run with -nomusic or -nosound is not accepted as audible output",
    }:
        require(token in audio_capture, f"audio-capture requirement missing: {token}")

    for token in {
        "same level and launch arguments except the tested music mutation",
        "same safe-copy patch set except the tested music mutation",
        "same sanitized audio endpoint and format between clean/staged/ambient/mute runs",
        "clean baseline and staged positive both have CDB selection/decode evidence",
        "clean baseline and staged positive audio windows are time-correlated with the CDB selection/decode windows",
    }:
        require(token in controls, f"comparison-control requirement missing: {token}")

    for token in {
        "final proof is generated from explicit private raw artifact paths, not accepted as a hand-authored summary",
        "clean/staged timestamped CDB decode timeline sidecars are bound to live artifact, raw live CDB log SHA-256, and timestamped CDB evidence log SHA-256 values",
        "ambient/clean/staged/mute audio JSON summaries are bound to existing raw WAV artifacts by outputJson path, outputWav path, helper-authored rawWavSha256, raw WAV byte count, and independently rederived WAV sample statistics before sanitized output is written",
        "materializer independently derives raw WAV data duration from canonical RIFF sample-rate/block-align/data-frame math and rejects summaries where timestamps outlast the actual data span",
        "materializer requires enabled wallClockPadding metadata and verifies capturedBytes plus silencePaddingBytes equals bytesRecorded",
        "clean/mute source music safety sidecars provide source target/replacement hash unchanged facts when non-staged live artifacts omit source music hash rows",
        "ambient no-BEA process census is required before accepting the ambient negative control and must cover the ambient capture window while binding to ambient audio JSON and raw WAV SHA-256 values",
        "clean/staged CDB-backed live-smoke stages must bind CDB target process id to launched safe-copy BEA process id, report attached positive CDB process ids, stopped/already-exited cleanup, and matching cleanup pid before timestamp/timeline generation",
        "executor must run a no-BEA/no-cdb process census after each CDB-backed stage and before final receipt acceptance or failure recording",
        "capture-to-source correlation adapter sidecar is bound to clean/staged audio JSON and raw WAV SHA-256 values",
        "raw loopback device identifiers, raw WAV paths, raw JSON paths, CDB paths, copied-game paths, source paths, and local proof roots are stripped from the sanitized proof",
        "materialized output must stay inside the private raw input bundle",
        "materialized output is immediately revalidated with the two-run harness checker",
    }:
        require(token in materialization, f"materialization requirement missing: {token}")

    for token in {
        "ambient no-BEA output-control stays below non-silent threshold",
        "mute-control run with -nomusic or -nosound stays below non-silent threshold",
        "negative controls are not accepted as audible-output proof",
    }:
        require(token in negative_controls, f"negative-control requirement missing: {token}")

    for token in {
        "deterministic decoded-source fingerprints exist for BEA_04 target and BEA_02 replacement",
        "source reference fingerprints differ by at least the accepted source margin",
        "capture-to-source adapter emits the harness-compatible sourceAudioCorrelation object without raw audio or private paths",
        "capture-to-source adapter binds to the clean/staged audio JSON and raw WAV hashes used by the materializer",
        "clean baseline correlates to original BEA_04 source audio more than replacement BEA_02",
        "staged positive correlates to replacement BEA_02 source audio more than original BEA_04",
        "RMS or peak-only difference is not sufficient",
    }:
        require(token in source_audio, f"source-audio requirement missing: {token}")

    non_claims = string_set(list_at(payload, "nonClaims"), "nonClaims")
    for token in {
        "not current audible playback proof",
        "not a new BEA launch",
        "not a new CDB attach",
        "not private audio artifact revalidation",
        "not arbitrary external OGG compatibility",
        "not all music cues",
        "not loop behavior proof",
        "not volume behavior proof",
        "not mixing or crossfade proof",
        "not gameplay parity",
        "not rebuild parity",
        "not no-noticeable-difference parity",
    }:
        require(token in non_claims, f"non-claim missing: {token}")

    next_proof = object_at(payload, "nextExecutableProof")
    require(next_proof.get("recommendedPreset") == "use-bea02-for-bea04", "recommended preset changed")
    require(next_proof.get("recommendedLevel") == 100, "recommended level changed")
    blocked_by = str(next_proof.get("blockedBy", ""))
    require("live two-run" in blocked_by, "next proof blocker must name live two-run evidence")
    require("timestamped CDB decode timeline sidecars" in blocked_by, "next proof blocker must name timestamped CDB timeline sidecars")
    require("source music safety sidecars" in blocked_by, "next proof blocker must name source music safety sidecars")
    require("ambient/mute controls" in blocked_by, "next proof blocker must name ambient/mute controls")
    require("accepted sanitized capture-to-source-audio correlation" in blocked_by, "next proof blocker must name accepted sanitized capture-to-source-audio correlation")
    require("materializer plus final checker" in blocked_by, "next proof blocker must name materializer plus final checker")
    require("Producer coverage is complete" in blocked_by, "next proof blocker must record completed producer coverage")
    require("actual ambient, clean, staged, mute, CDB timeline, source-safety, audio, and capture-correlation sidecars" in blocked_by, "next proof blocker must preserve remaining raw-bundle evidence boundary")

    return {
        "schema": EXPECTED_SCHEMA,
        "runtimeAudibleOutputProof": False,
        "level100SelectionDecodeProofs": accepted["level100SelectionDecodeProofs"],
        "namedPresetSelectionDecodeProof": accepted["namedPresetSelectionDecodeProof"],
        "audioLoopbackBackendPreflight": accepted["audioLoopbackBackendPreflight"],
        "audioLoopbackCalibrationNonSilent": accepted["audioLoopbackCalibrationNonSilent"],
        "twoRunHarnessAcceptanceChecker": accepted["twoRunHarnessAcceptanceChecker"],
        "trustedRawArtifactMaterializer": accepted["trustedRawArtifactMaterializer"],
        "liveRawBundleGate": accepted["liveRawBundleGate"],
        "liveBundleExecutor": accepted["liveBundleExecutor"],
        "ambientNoBeaCensusProducer": accepted["ambientNoBeaCensusProducer"],
        "sourceMusicSafetySidecarProducer": accepted["sourceMusicSafetySidecarProducer"],
        "sourceAudioReferenceFingerprint": accepted["sourceAudioReferenceFingerprint"],
        "captureSourceCorrelationAdapter": accepted["captureSourceCorrelationAdapter"],
        "captureSourceCorrelationBuilder": accepted["captureSourceCorrelationBuilder"],
        "timestampedCdbLogProducer": accepted["timestampedCdbLogProducer"],
        "loopbackWallClockPaddingHelper": accepted["loopbackWallClockPaddingHelper"],
        "rawWavDataDurationMaterializerGuard": accepted["rawWavDataDurationMaterializerGuard"],
        "audioCaptureRequirements": len(audio_capture),
        "comparisonControlRequirements": len(controls),
        "materializationRequirements": len(materialization),
        "negativeControlRequirements": len(negative_controls),
        "sourceAudioCorrelationRequirements": len(source_audio),
        "claimBoundary": "Contract only: staging and CDB selection/decode are accepted, but audible playback remains unproven until a bounded audio-output artifact passes this bar.",
    }


def assert_text_tokens() -> None:
    for relative, tokens in DOC_TOKENS.items():
        text = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            require(token in text, f"{relative} missing token: {token}")


def check() -> dict[str, Any]:
    summary = assert_contract()
    assert_text_tokens()
    return summary


def self_test() -> None:
    require(EXPECTED_SCHEMA.endswith(".v1"), "self-test expected versioned schema")
    require("audible" in EXPECTED_SCHEMA, "self-test expected audible schema")
    require("runtime" not in Path(__file__).name.lower(), "public-safe checker name should not imply runtime artifact validation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music audible-output contract checker self-test: PASS")
            return 0
        require(args.check, "use --check or --self-test")
        print(json.dumps(check(), indent=2, sort_keys=True))
        return 0
    except ContractError as exc:
        print(f"WinUI safe-copy music audible-output contract check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
