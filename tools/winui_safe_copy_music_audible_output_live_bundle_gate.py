#!/usr/bin/env python3
"""Build a checked gate for a future music audible-output live raw bundle.

This helper does not launch BEA, attach CDB, capture audio, read private game
media, or materialize an audible-output proof. It records the exact raw inputs,
producer gaps, command ordering, and promotion path that must exist before a
single private live attempt should run.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "winui-safe-copy-music-audible-output-live-bundle-gate.v1"
GATE_STATUS = "producer-coverage-complete-prearm-readiness-required"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
LEVEL_ID = 100
PRIVATE_PROOF_ROOT_HINT = "<private-proof-root>"
READ_ONLY_SOURCE_ROOT_HINT = "<read-only-source-game-root>"
ARM_PHRASE = "RUN PRIVATE MUSIC AUDIBLE LIVE BUNDLE"
PRIVATE_PREARM_SCHEMA = "winui-safe-copy-music-audible-output-live-bundle-prearm-readiness.v1"
REQUIRED_RESOURCE_LEASES: tuple[str, ...] = (
    "bea-runtime",
    "cdb-debugger",
    "audio-loopback",
    "proof-root",
)
RUNTIME_PROOF_FALSE_KEYS = (
    "runtimeAudibleOutputProof",
    "allMusicCuesProof",
    "gameplayAudioParityProof",
    "rebuildParityProof",
    "hostJoinControlsMayBeEnabled",
    "baseOnlineMultiplayerReady",
)
REQUIRED_INPUTS: tuple[dict[str, str], ...] = (
    {
        "key": "cleanLive",
        "role": "cleanBaseline",
        "schema": "winui-safe-copy-live-runtime-smoke.v1",
        "materializerArg": "--clean-live",
        "producer": r"tools\winui_safe_copy_live_runtime_smoke.py",
    },
    {
        "key": "stagedLive",
        "role": "stagedPositive",
        "schema": "winui-safe-copy-live-runtime-smoke.v1",
        "materializerArg": "--staged-live",
        "producer": r"tools\winui_safe_copy_live_runtime_smoke.py",
    },
    {
        "key": "muteLive",
        "role": "muteControl",
        "schema": "winui-safe-copy-live-runtime-smoke.v1",
        "materializerArg": "--mute-live",
        "producer": r"tools\winui_safe_copy_live_runtime_smoke.py",
    },
    {
        "key": "cleanTimeline",
        "role": "cleanBaseline",
        "schema": "winui-safe-copy-music-cdb-decode-timeline.v1",
        "materializerArg": "--clean-timeline",
        "producer": r"tools\winui_safe_copy_music_cdb_timeline_sidecar.py",
    },
    {
        "key": "stagedTimeline",
        "role": "stagedPositive",
        "schema": "winui-safe-copy-music-cdb-decode-timeline.v1",
        "materializerArg": "--staged-timeline",
        "producer": r"tools\winui_safe_copy_music_cdb_timeline_sidecar.py",
    },
    {
        "key": "cleanSourceMusicSafety",
        "role": "cleanBaseline",
        "schema": "winui-safe-copy-source-music-safety.v1",
        "materializerArg": "--clean-source-music-safety",
        "producer": r"tools\winui_safe_copy_music_source_music_safety_sidecar.py",
    },
    {
        "key": "muteSourceMusicSafety",
        "role": "muteControl",
        "schema": "winui-safe-copy-source-music-safety.v1",
        "materializerArg": "--mute-source-music-safety",
        "producer": r"tools\winui_safe_copy_music_source_music_safety_sidecar.py",
    },
    {
        "key": "ambientCensus",
        "role": "ambientNoBea",
        "schema": "winui-safe-copy-no-bea-process-census.v1",
        "materializerArg": "--ambient-census",
        "producer": r"tools\winui_safe_copy_music_ambient_no_bea_census.py",
    },
    {
        "key": "ambientAudio",
        "role": "ambientNoBea",
        "schema": "audio-loopback-capture.v1",
        "materializerArg": "--ambient-audio",
        "producer": r"tools\capture_audio_loopback.py",
    },
    {
        "key": "cleanAudio",
        "role": "cleanBaseline",
        "schema": "audio-loopback-capture.v1",
        "materializerArg": "--clean-audio",
        "producer": r"tools\capture_audio_loopback.py",
    },
    {
        "key": "stagedAudio",
        "role": "stagedPositive",
        "schema": "audio-loopback-capture.v1",
        "materializerArg": "--staged-audio",
        "producer": r"tools\capture_audio_loopback.py",
    },
    {
        "key": "muteAudio",
        "role": "muteControl",
        "schema": "audio-loopback-capture.v1",
        "materializerArg": "--mute-audio",
        "producer": r"tools\capture_audio_loopback.py",
    },
    {
        "key": "captureSourceCorrelation",
        "role": "clean-staged-comparison",
        "schema": "winui-safe-copy-music-capture-source-correlation.v1",
        "materializerArg": "--capture-source-correlation",
        "producer": r"tools\winui_safe_copy_music_capture_source_correlation_builder.py",
    },
)
REQUIRED_GAP_IDS: tuple[str, ...] = ()


class MusicAudibleOutputLiveBundleGateError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MusicAudibleOutputLiveBundleGateError(message)


def require_exact_keys(value: dict[str, Any], expected: set[str], *, label: str) -> None:
    actual = set(value)
    require(actual == expected, f"{label} keys changed: expected {sorted(expected)}, got {sorted(actual)}")


def relative_hint(root: Path, *parts: str) -> str:
    return str(Path("<private-proof-root>", *parts))


def required_raw_inputs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in REQUIRED_INPUTS:
        rows.append(
            {
                **item,
                "pathHint": relative_hint(ROOT, "raw", f"{item['key']}.json"),
                "mustStayPrivate": True,
                "acceptedOnlyThroughMaterializer": True,
            }
        )
    return rows


def unresolved_producer_gaps() -> list[dict[str, Any]]:
    return []


def proof_booleans() -> dict[str, bool]:
    return {key: False for key in RUNTIME_PROOF_FALSE_KEYS}


def preflight_commands() -> list[str]:
    return [
        r"powershell -ExecutionPolicy Bypass -File .\tools\get_cdb_path.ps1 -AsLiteral",
        "npm run test:runtime-cdb-helper-safety",
        "npm run test:winui-safe-copy-live-runtime-smoke-helper",
        "npm run test:audio-loopback-capture-helper",
        "npm run test:winui-safe-copy-music-audible-output-contract",
        "npm run test:winui-safe-copy-music-audible-output-two-run-harness",
        "npm run test:winui-safe-copy-music-audible-output-live-bundle-executor",
        "npm run test:winui-safe-copy-music-timestamped-cdb-log-producer",
        "npm run test:winui-safe-copy-music-cdb-timeline-sidecar",
        "npm run test:winui-safe-copy-music-source-music-safety-sidecar",
        "npm run test:winui-safe-copy-music-audible-output-materializer",
        "npm run test:winui-safe-copy-music-source-audio-correlation",
        "npm run test:winui-safe-copy-music-capture-source-correlation",
        "npm run test:winui-safe-copy-music-capture-source-correlation-builder",
    ]


def promotion_command_template() -> list[str]:
    command = ["py -3 tools\\winui_safe_copy_music_audible_output_materializer.py"]
    for item in REQUIRED_INPUTS:
        command.append(f"{item['materializerArg']} {relative_hint(ROOT, 'raw', item['key'] + '.json')}")
    command.append(r"--output <private-proof-root>\audible-proof.json")
    command.append(r"then: py -3 tools\winui_safe_copy_music_audible_output_two_run_harness_check.py <private-proof-root>\audible-proof.json")
    return command


def pre_arm_readiness() -> dict[str, Any]:
    return {
        "status": "prearm-readiness-not-proven",
        "runtimeProofAuthority": {
            "explicitRuntimeProofAuthorityRequired": True,
            "requiredArmPhrase": ARM_PHRASE,
            "privatePrearmReadinessSchema": PRIVATE_PREARM_SCHEMA,
            "authorityMustBeRecordedBeforeLiveExecution": True,
            "noAuthorityFromThisGate": True,
        },
        "requiredResourceLeases": list(REQUIRED_RESOURCE_LEASES),
        "processPreflight": {
            "noPreexistingBeaOrCdbRequired": True,
            "passiveProcessCensusOnly": True,
            "unknownProcessOwnerBlocksLiveAttempt": True,
        },
        "proofRootPreflight": {
            "emptyIsolatedPrivateProofRootRequired": True,
            "mustNotOverlapReadOnlySourceRoot": True,
            "localIgnoredRawProofOnly": True,
        },
        "sourceMutationPolicy": {
            "copiedProfileAndAppOwnedArtifactRootsOnly": True,
            "installedGameAndOriginalBeaReadOnly": True,
        },
        "captureSpanDecodeWindowPreflight": {
            "captureStartedUtcStopwatchAlignmentRequired": True,
            "wavWallClockDurationMustCoverCdbDecodeWindow": True,
            "helperAuthoredWallClockPaddingMetadataRequired": True,
            "capturedBytesPlusSilencePaddingBytesMustEqualBytesRecorded": True,
            "canonicalWavHeaderAndDataFrameConsistencyRequired": True,
            "outOfRangeDecodeWindowRejectedByMaterializer": True,
        },
        "rawProofPolicy": {
            "rawProofArtifactsStayLocalIgnored": True,
            "privatePathsMustNotBePublished": True,
        },
        "readinessFailurePolicy": {
            "proofBooleanForcedFalse": "runtimeAudibleOutputProof",
            "forbiddenFailureClaimText": [
                "audible-output proof",
                "runtime audio proof",
                "player-ready online",
                "release ready",
            ],
            "readinessFailureCannotClaimAudibleOutput": True,
        },
    }


def build_gate(*, artifact_root: Path, source_root: Path) -> dict[str, Any]:
    gaps = unresolved_producer_gaps()
    return {
        "schemaVersion": SCHEMA,
        "status": GATE_STATUS,
        "presetId": PRESET_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "levelId": LEVEL_ID,
        "artifactRootHint": relative_hint(ROOT, "music-audible-live"),
        "sourceRootHint": READ_ONLY_SOURCE_ROOT_HINT,
        "privatePathPolicy": (
            "Gate output is path-redacted. Private roots, source game paths, raw CDB logs, "
            "WAV paths, and copied-game paths must stay in private raw artifacts only."
        ),
        "runtimeAudibleOutputProof": False,
        "producerCoverageComplete": True,
        "readyToRunLiveAttempt": False,
        "liveArmAllowed": False,
        "proofBooleans": proof_booleans(),
        "preArmReadiness": pre_arm_readiness(),
        "requiredRawInputs": required_raw_inputs(),
        "unresolvedProducerGaps": gaps,
        "producerGapBlocksLiveAttempt": bool(gaps),
        "preflightCommands": preflight_commands(),
        "promotionCommandTemplate": promotion_command_template(),
        "claimBoundary": (
            "Gate only. Producer coverage is complete, but this is not a BEA launch, CDB attach, audio capture, audible-output proof, "
            "all-cue proof, gameplay parity proof, online proof, or rebuild parity proof."
        ),
    }


def validate_gate(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "gate schema mismatch")
    require(payload.get("status") == GATE_STATUS, "gate status changed")
    require_exact_keys(
        payload,
        {
            "schemaVersion",
            "status",
            "presetId",
            "target",
            "replacement",
            "levelId",
            "artifactRootHint",
            "sourceRootHint",
            "privatePathPolicy",
            "runtimeAudibleOutputProof",
            "producerCoverageComplete",
            "readyToRunLiveAttempt",
            "liveArmAllowed",
            "proofBooleans",
            "preArmReadiness",
            "requiredRawInputs",
            "unresolvedProducerGaps",
            "producerGapBlocksLiveAttempt",
            "preflightCommands",
            "promotionCommandTemplate",
            "claimBoundary",
        },
        label="gate",
    )
    require(payload.get("presetId") == PRESET_ID, "preset id changed")
    require(payload.get("target") == TARGET, "target changed")
    require(payload.get("replacement") == REPLACEMENT, "replacement changed")
    require(payload.get("levelId") == LEVEL_ID, "level id changed")
    require(payload.get("runtimeAudibleOutputProof") is False, "gate must not claim runtime audible output proof")
    require(payload.get("producerCoverageComplete") is True, "producer coverage must remain complete")
    require(payload.get("readyToRunLiveAttempt") is False, "gate must not mark a live attempt ready before runtime pre-arm proof")
    require(payload.get("liveArmAllowed") is False, "gate output must not authorize a live arm")
    for forbidden in ("artifactRoot", "sourceRoot", "preferredPrivateRuntimeProofRoot"):
        require(forbidden not in payload, f"gate must not emit private path field: {forbidden}")
    require(payload.get("artifactRootHint") == relative_hint(ROOT, "music-audible-live"), "artifact root hint changed")
    require(payload.get("sourceRootHint") == READ_ONLY_SOURCE_ROOT_HINT, "source root hint changed")

    proof_flags = payload.get("proofBooleans")
    require(isinstance(proof_flags, dict), "proofBooleans missing")
    for key in RUNTIME_PROOF_FALSE_KEYS:
        require(proof_flags.get(key) is False, f"proof boolean must remain false: {key}")

    prearm = payload.get("preArmReadiness")
    require(isinstance(prearm, dict), "preArmReadiness missing")
    require(prearm.get("status") == "prearm-readiness-not-proven", "pre-arm readiness must remain unproven in the public gate")
    authority = prearm.get("runtimeProofAuthority")
    require(isinstance(authority, dict), "runtimeProofAuthority missing")
    require(authority.get("explicitRuntimeProofAuthorityRequired") is True, "runtime-proof authority requirement missing")
    require(authority.get("requiredArmPhrase") == ARM_PHRASE, "runtime-proof arm phrase changed")
    require(authority.get("privatePrearmReadinessSchema") == PRIVATE_PREARM_SCHEMA, "private pre-arm readiness schema changed")
    require(authority.get("noAuthorityFromThisGate") is True, "gate must not grant runtime-proof authority")
    require(prearm.get("requiredResourceLeases") == list(REQUIRED_RESOURCE_LEASES), "required resource leases changed")
    process = prearm.get("processPreflight")
    require(isinstance(process, dict), "processPreflight missing")
    require(process.get("noPreexistingBeaOrCdbRequired") is True, "BEA/CDB process preflight missing")
    require(process.get("passiveProcessCensusOnly") is True, "process preflight must remain passive")
    proof_root = prearm.get("proofRootPreflight")
    require(isinstance(proof_root, dict), "proofRootPreflight missing")
    require(proof_root.get("emptyIsolatedPrivateProofRootRequired") is True, "empty private proof-root preflight missing")
    require(proof_root.get("mustNotOverlapReadOnlySourceRoot") is True, "source/proof-root non-overlap preflight missing")
    require(proof_root.get("localIgnoredRawProofOnly") is True, "raw proof local/ignored policy missing")
    mutation = prearm.get("sourceMutationPolicy")
    require(isinstance(mutation, dict), "sourceMutationPolicy missing")
    require(mutation.get("copiedProfileAndAppOwnedArtifactRootsOnly") is True, "copied/app-owned roots policy missing")
    require(mutation.get("installedGameAndOriginalBeaReadOnly") is True, "installed game/original BEA read-only policy missing")
    capture_span = prearm.get("captureSpanDecodeWindowPreflight")
    require(isinstance(capture_span, dict), "captureSpanDecodeWindowPreflight missing")
    for key in (
        "captureStartedUtcStopwatchAlignmentRequired",
        "wavWallClockDurationMustCoverCdbDecodeWindow",
        "helperAuthoredWallClockPaddingMetadataRequired",
        "capturedBytesPlusSilencePaddingBytesMustEqualBytesRecorded",
        "canonicalWavHeaderAndDataFrameConsistencyRequired",
        "outOfRangeDecodeWindowRejectedByMaterializer",
    ):
        require(capture_span.get(key) is True, f"capture-span preflight missing: {key}")
    raw_policy = prearm.get("rawProofPolicy")
    require(isinstance(raw_policy, dict), "rawProofPolicy missing")
    require(raw_policy.get("rawProofArtifactsStayLocalIgnored") is True, "raw proof local/ignored policy missing")
    require(raw_policy.get("privatePathsMustNotBePublished") is True, "private path publication guard missing")
    failure_policy = prearm.get("readinessFailurePolicy")
    require(isinstance(failure_policy, dict), "readinessFailurePolicy missing")
    require(failure_policy.get("proofBooleanForcedFalse") == "runtimeAudibleOutputProof", "readiness failure must force runtimeAudibleOutputProof false")
    forbidden_failure_text = failure_policy.get("forbiddenFailureClaimText")
    require(isinstance(forbidden_failure_text, list), "forbiddenFailureClaimText missing")
    require("audible-output proof" in forbidden_failure_text, "readiness failure must forbid audible-output proof wording")
    require(failure_policy.get("readinessFailureCannotClaimAudibleOutput") is True, "readiness failure non-claim policy missing")

    raw_inputs = payload.get("requiredRawInputs")
    require(isinstance(raw_inputs, list), "requiredRawInputs missing")
    raw_keys = [item.get("key") for item in raw_inputs if isinstance(item, dict)]
    expected_keys = [item["key"] for item in REQUIRED_INPUTS]
    require(raw_keys == expected_keys, "required raw input keys changed")
    for item in raw_inputs:
        require(isinstance(item, dict), "raw input must be object")
        require(item.get("mustStayPrivate") is True, f"{item.get('key')} must stay private")
        require(item.get("acceptedOnlyThroughMaterializer") is True, f"{item.get('key')} must promote only through materializer")

    gaps = payload.get("unresolvedProducerGaps")
    require(isinstance(gaps, list), "unresolvedProducerGaps missing")
    gap_ids = [item.get("id") for item in gaps if isinstance(item, dict)]
    require(gap_ids == list(REQUIRED_GAP_IDS), "unresolved producer gaps changed")
    require(payload.get("producerGapBlocksLiveAttempt") is False, "producer gap block flag must be false after producer coverage is complete")

    commands = payload.get("preflightCommands")
    require(isinstance(commands, list) and commands, "preflight commands missing")
    require(
        "npm run test:winui-safe-copy-music-timestamped-cdb-log-producer" in commands,
        "timestamped CDB producer preflight command missing",
    )
    require(
        "npm run test:winui-safe-copy-music-audible-output-live-bundle-executor" in commands,
        "live bundle executor preflight command missing",
    )
    promotion = payload.get("promotionCommandTemplate")
    require(isinstance(promotion, list) and promotion, "promotion command template missing")
    joined = " ".join(str(part) for part in promotion)
    require("tools\\winui_safe_copy_music_audible_output_materializer.py" in joined, "materializer command missing")
    require("tools\\winui_safe_copy_music_audible_output_two_run_harness_check.py" in joined, "final checker command missing")

    return {
        "schema": SCHEMA,
        "requiredRawInputCount": len(raw_inputs),
        "unresolvedProducerGapCount": len(gaps),
        "producerCoverageComplete": True,
        "readyToRunLiveAttempt": False,
        "liveArmAllowed": False,
        "runtimeAudibleOutputProof": False,
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        payload = build_gate(artifact_root=root / "music-audible-live", source_root=root / "source")
        summary = validate_gate(payload)
        require(summary["requiredRawInputCount"] == len(REQUIRED_INPUTS), "self-test raw input count mismatch")
        require(summary["unresolvedProducerGapCount"] == len(REQUIRED_GAP_IDS), "self-test gap count mismatch")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--source-root", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("live-bundle-gate self-test passed")
            return 0
        require(args.artifact_root is not None, "Provide --artifact-root or --self-test.")
        require(args.source_root is not None, "Provide --source-root or --self-test.")
        payload = build_gate(artifact_root=args.artifact_root, source_root=args.source_root)
        summary = validate_gate(payload)
        if args.output_json is not None:
            write_json(args.output_json, payload)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except MusicAudibleOutputLiveBundleGateError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
