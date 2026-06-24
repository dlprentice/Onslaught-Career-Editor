#!/usr/bin/env python3
"""Build a private level-854 input-assisted outcome-transition proof bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import build_winui_original_binary_level854_outcome_semantics_observer_bundle as observer


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROOF_ROOT = observer.PRIVATE_PROOF_ROOT
DEFAULT_ARTIFACT_ROOT = PRIVATE_PROOF_ROOT / "level854-input-assisted-outcome-20260619"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "level854-input-assisted-outcome-proof.json"
DEFAULT_GAME_ROOT = observer.DEFAULT_GAME_ROOT
DEFAULT_EXE_OVERRIDE = observer.DEFAULT_EXE_OVERRIDE
COMMAND_FILE = ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-input-assisted-outcome-observer.cdb.txt"

SCHEMA = "winui-original-binary-level854-input-assisted-outcome.v1"
PROTOCOL = "level854-input-assisted-outcome.v1"
HELPER = "winui-original-binary-level854-input-assisted-outcome"
HELPER_VERSION = "level854-input-assisted-outcome.v1"
SCOPE = "level854-input-assisted-outcome-transition-attempt-not-online-proof"
RUNTIME_PROFILE = observer.RUNTIME_PROFILE
INPUT_SEQUENCES = [
    "wait:1000",
    "down:Q,wait:1500,up:Q",
    "wait:500",
    "down:E,wait:1500,up:E",
    "wait:500",
    "click:320x240,wait:500",
    "click:320x360,wait:500",
    "wait:1000",
]


class Level854InputAssistedOutcomeBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level854InputAssistedOutcomeBuildError(message)


def require_private_path(path: Path, *, must_exist: bool = False) -> Path:
    return observer.require_private_path(path, must_exist=must_exist)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def fresh_artifact_root() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return PRIVATE_PROOF_ROOT / f"level854-input-assisted-outcome-live-{stamp}"


def relative_path(base: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), base.resolve()).replace("\\", "/")


def require_path_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise Level854InputAssistedOutcomeBuildError(f"{label} must stay under {root_resolved}: {resolved}") from exc
    return resolved


def require_recorded_path(raw: Any, expected: Path, label: str) -> Path:
    require(isinstance(raw, str) and raw.strip(), f"{label} path missing")
    resolved = Path(raw).resolve()
    require(resolved == expected.resolve(), f"{label} path mismatch: {resolved} != {expected.resolve()}")
    return resolved


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def validate_command_file(path: Path = COMMAND_FILE) -> None:
    path = path.resolve()
    require(path.is_file(), f"input-assisted CDB command file missing: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    for pattern in (
        r"^\s*\.shell\b",
        r"^\s*\.dump\b",
        r"^\s*\.writemem\b",
        r"^\s*ed\s+",
        r"^\s*eb\s+",
        r"^\s*ew\s+",
        r"^\s*eq\s+",
        r"^\s*r\s+",
    ):
        require(
            re.search(pattern, text, re.IGNORECASE | re.MULTILINE) is None,
            f"CDB command file contains mutating command pattern: {pattern}",
        )
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(".echo") or stripped.startswith("bp ") or stripped == "g" or stripped in {"vertarget", "lm m BEA"}:
            continue
        raise Level854InputAssistedOutcomeBuildError(f"CDB command file contains unsupported command: {stripped}")


def is_wait_only_sequence(sequence: str) -> bool:
    parts = [part.strip().lower() for part in sequence.split(",") if part.strip()]
    return bool(parts) and all(part.startswith("wait:") for part in parts)


def transition_hit_count(text: str) -> int:
    total = 0
    for name in observer.UNFORCED_TRANSITION_TARGETS:
        total += len(re.findall(rf"OUTCOME_SEM_HIT name={re.escape(name)}\b", text))
    return total


def outcome_hit_counts(text: str) -> dict[str, int]:
    return {
        name: len(re.findall(rf"OUTCOME_SEM_HIT name={re.escape(name)}\b", text))
        for name in observer.UNFORCED_TRANSITION_TARGETS
    }


def input_assist_hit_count(text: str) -> int:
    return len(re.findall(r"INPUT_ASSIST_HIT name=", text))


def input_windows_from_runtime(runtime: dict[str, Any], log_path: Path) -> list[dict[str, Any]]:
    rows = list_at(runtime, "inputCdbWindows")
    log_path = log_path.resolve()
    data = log_path.read_bytes()
    windows: list[dict[str, Any]] = []
    for row in rows:
        require(isinstance(row, dict), "inputCdbWindows row is not an object")
        index = row.get("index")
        sequence = row.get("sequence")
        start = row.get("logStartByte")
        end = row.get("logEndByte")
        require(isinstance(index, int) and index > 0, "inputCdbWindows row has invalid index")
        require(isinstance(sequence, str) and sequence, f"inputCdbWindows row {index} has invalid sequence")
        require(isinstance(start, int) and isinstance(end, int), f"inputCdbWindows row {index} is missing byte offsets")
        require(0 <= start <= end <= len(data), f"inputCdbWindows row {index} byte offsets are out of range")
        require_recorded_path(row.get("logPath"), log_path, f"inputCdbWindows row {index} log")
        text = data[start:end].decode("utf-8", errors="replace")
        stimulus = not is_wait_only_sequence(sequence)
        transitions = transition_hit_count(text)
        windows.append(
            {
                "index": index,
                "sequence": sequence,
                "stimulusWindow": stimulus,
                "byteCount": end - start,
                "inputAssistHitCount": input_assist_hit_count(text),
                "outcomeTransitionHitCount": transitions,
                "transitionHitCounts": outcome_hit_counts(text),
            }
        )
    windows.sort(key=lambda item: int(item["index"]))
    require(any(row["stimulusWindow"] for row in windows), "input-assisted proof needs at least one stimulus input window")
    require(any(not row["stimulusWindow"] for row in windows), "input-assisted proof needs at least one wait/no-input control window")
    return windows


def cdb_log_from_runtime(runtime_artifact: dict[str, Any]) -> Path:
    return observer.cdb_log_from_runtime(runtime_artifact)


def validate_runtime_artifact(runtime_path: Path) -> tuple[dict[str, Any], Path, dict[str, Any], list[dict[str, Any]]]:
    runtime_path = require_private_path(runtime_path, must_exist=True)
    runtime_root = runtime_path.parent.resolve()
    expected_cdb_root = runtime_root / "cdb"
    runtime = read_json(runtime_path)
    require(runtime.get("schemaVersion") == "winui-safe-copy-live-runtime-smoke.v1", "unexpected runtime artifact schema")
    require(object_at(runtime, "launch").get("arguments") == ["-skipfmv", "-level", "854", "-configuration", "1"], "runtime launch arguments must be -skipfmv -level 854 -configuration 1")
    source = object_at(runtime, "source")
    require(source.get("installedHashUnchanged") is True, "installed BEA.exe hash changed")
    require(source.get("overrideHashUnchanged") is True, "clean override BEA.exe hash changed")
    require(object_at(source, "saveAndOptions").get("unchanged") is True, "source save/options changed")
    baseline = object_at(runtime, "processBaseline")
    require(baseline.get("noPreexistingBea") is True, "pre-existing BEA process was present")
    require(baseline.get("noBeaAfterStop") is True, "BEA process remained after stop")
    require(object_at(runtime, "stop").get("Success") is True, "managed stop did not succeed")
    captures = runtime.get("captures")
    require(isinstance(captures, list) and captures, "runtime artifact has no bounded captures")
    require(all(isinstance(row, dict) and row.get("status") == "captured" for row in captures), "bounded captures must all be captured")
    require(all(isinstance(row, dict) and row.get("visualProof") is True for row in captures), "bounded captures must all carry visualProof=true")
    observer_state = object_at(runtime, "cdbObserver")
    require(observer_state.get("enabled") is True, "CDB observer was not enabled")
    expected_command = COMMAND_FILE.resolve()
    require_recorded_path(observer_state.get("commandFile"), expected_command, "CDB observer command")
    result = object_at(observer_state, "result")
    require(result.get("status") == "attached", "CDB observer did not attach")
    require(result.get("logExists") is True, "CDB log was not created")
    require_recorded_path(result.get("commandFile"), expected_command, "CDB observer result command")
    require(object_at(observer_state, "cleanup").get("status") in {"stopped", "already-exited"}, "CDB observer cleanup did not complete")
    input_plan = object_at(runtime, "inputPlan")
    input_summary = object_at(runtime, "inputSummary")
    require(input_plan.get("inputSequenceCount", 0) >= 2, "input-assisted proof needs multiple input windows")
    require(input_plan.get("allowBackgroundWindowMessages") is False, "background window messages are not allowed for outcome proof")
    require(input_summary.get("inputSequencesSent", 0) == input_plan.get("inputSequenceCount"), "not every planned input sequence was sent")
    require(input_summary.get("focusedInputSequences", 0) == input_plan.get("inputSequenceCount"), "not every input sequence was focused")
    require(input_summary.get("inputWindowMessageEventsSent", 0) == 0, "background/window-message input is not allowed")
    require(input_summary.get("inputKeyEventsSent", 0) + input_summary.get("inputMouseEventsSent", 0) > 0, "no real key or mouse input was sent")
    input_rows = runtime.get("input")
    require(isinstance(input_rows, list) and input_rows, "input result rows are missing")
    require(all(isinstance(row, dict) and row.get("status") == "sent" for row in input_rows), "all input result rows must have status=sent")
    log_path = require_path_under(cdb_log_from_runtime(runtime), expected_cdb_root, "CDB log")
    require_recorded_path(observer_state.get("logPath"), log_path, "CDB observer log")
    require_recorded_path(result.get("logPath"), log_path, "CDB observer result log")
    helper_payload = result.get("helperPayload")
    if isinstance(helper_payload, dict):
        require_recorded_path(helper_payload.get("logPath"), log_path, "CDB helper payload log")
    validate_command_file(COMMAND_FILE)
    parsed = observer.parse_cdb_log(log_path)
    windows = input_windows_from_runtime(runtime, log_path)
    return runtime, log_path, parsed, windows


def build_bundle_from_runtime(runtime_path: Path, output_path: Path, *, fresh_live_execution: bool = False) -> dict[str, Any]:
    output_path = require_private_path(output_path)
    runtime, log_path, parsed, windows = validate_runtime_artifact(runtime_path)
    captures = runtime.get("captures") if isinstance(runtime.get("captures"), list) else []
    visual_count = len([row for row in captures if isinstance(row, dict) and row.get("visualProof") is True])
    render = parsed["render"]
    stimulus_transition_count = sum(int(row["outcomeTransitionHitCount"]) for row in windows if row["stimulusWindow"])
    wait_transition_count = sum(int(row["outcomeTransitionHitCount"]) for row in windows if not row["stimulusWindow"])
    input_assist_hits = sum(int(row["inputAssistHitCount"]) for row in windows)
    positive_stimulus_windows = [
        row
        for row in windows
        if row["stimulusWindow"] and int(row["outcomeTransitionHitCount"]) > 0 and int(row["inputAssistHitCount"]) > 0
    ]
    require(wait_transition_count == 0, "wait/no-input window outcome transition cannot be causal proof")
    require(
        stimulus_transition_count == 0 or bool(positive_stimulus_windows),
        "stimulus-window outcome transition requires input-assist hits in the same window",
    )
    runtime_outcome = bool(positive_stimulus_windows) and wait_transition_count == 0
    bundle: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "proofScope": SCOPE,
        "runtimeProfile": RUNTIME_PROFILE,
        "executionReceipt": {
            "freshLiveExecution": fresh_live_execution,
            "runtimeGeneratedAt": runtime.get("generatedAt"),
            "runtimeArtifactRootName": runtime_path.parent.name,
            "runtimeArtifactSha256": sha256_file(runtime_path),
            "outputRootName": output_path.parent.name,
            "replayArtifactAcceptedForPromotion": False,
        },
        "sourceArtifacts": {
            "liveRuntimeArtifact": relative_path(output_path.parent, runtime_path),
            "liveRuntimeArtifactSha256": sha256_file(runtime_path),
            "cdbLogSha256": sha256_file(log_path),
            "observerCommandFile": relative_path(output_path.parent, COMMAND_FILE),
            "observerCommandFileSha256": sha256_file(COMMAND_FILE),
        },
        "runtimeEvidence": {
            "safeCopyLaunchLevel": 854,
            "controllerConfiguration": 1,
            "newBeaLaunchCount": 1,
            "cdbAttachCount": 1,
            "boundedCaptureCount": len(captures),
            "visualCaptureCount": visual_count,
            "exactPidCdbObserverProven": True,
            "renderPlayers": render["players"],
            "renderLevel": render["level"],
            "horizontalSplit": render["horizSplit"] == 1,
            "p1Pointer": render["p0"],
            "p2Pointer": render["p1"],
            "p1p2PointersDistinct": True,
            "sourceHashesUnchanged": True,
            "managedStopClean": True,
        },
        "inputAssistedOutcome": {
            "inputAssistedOutcomeAttempted": True,
            "inputSequences": [row["sequence"] for row in windows],
            "inputWindowCount": len(windows),
            "stimulusWindowCount": len([row for row in windows if row["stimulusWindow"]]),
            "waitControlWindowCount": len([row for row in windows if not row["stimulusWindow"]]),
            "inputAssistHitCount": input_assist_hits,
            "inputWindowSummaries": windows,
            "inputWindowOutcomeTransitionHitCount": stimulus_transition_count,
            "waitWindowOutcomeTransitionHitCount": wait_transition_count,
            "positiveStimulusWindowCount": len(positive_stimulus_windows),
            "stimulusAttemptOnly": not runtime_outcome,
            "runtimeOutcomeProof": runtime_outcome,
            "minimalDeathOrRespawnProof": runtime_outcome and any(
                row["transitionHitCounts"].get("CGame__DeclarePlayerDead", 0) + row["transitionHitCounts"].get("CGame__RespawnPlayer", 0) > 0
                for row in windows
                if row["stimulusWindow"]
            ),
            "strongWinOrDrawProof": runtime_outcome and any(
                row["transitionHitCounts"].get("CGame__MPDeclarePlayerWon", 0) + row["transitionHitCounts"].get("CGame__MPDeclareGameDrawn", 0) > 0
                for row in windows
                if row["stimulusWindow"]
            ),
            "forcedOutcomeTransition": False,
            "forcedWinDeathRespawn": False,
            "backgroundWindowMessagesAllowed": False,
        },
        "outcomeSemanticsSurface": {
            "outcomeHookSurfaceObserved": True,
            "selectedRuntimeCandidate": 854,
            "outcomeHookTargets": observer.OUTCOME_TARGETS,
            "outcomeHookTargetCount": len(observer.OUTCOME_TARGETS),
            "hookTargetCount": parsed["hookTargetCount"],
            "expectedHookTargetCount": len(observer.TARGETS),
            "hitCounts": parsed["hitCounts"],
            "unforcedTransitionTargets": observer.UNFORCED_TRANSITION_TARGETS,
            "totalUnforcedTransitionHitCount": parsed["unforcedTransitionHitCount"],
            "objectiveSurfaceTargets": observer.OBJECTIVE_TARGETS,
            "objectiveSurfaceHitCount": parsed["objectiveSurfaceHitCount"],
            "modeRuntimeProofSlicesAdded": 0,
            "coOpVersusModeRuntimeProofSlicesAdded": 0,
            "currentRuntimeModeClassification": "unclassified-local-multiplayer",
        },
        "slotBoundary": {
            "acceptedOriginalBinaryGameplaySlots": observer.EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": observer.EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": observer.EXPECTED_METADATA_SLOTS,
            "maxOriginalBinaryActiveSlotsProven": 2,
            "slotCapacity": 4,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "beyondTwoPlayersRequiresNewProofClass": True,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "secondPhysicalHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "coOpModeRuntimeProof": False,
            "versusModeRuntimeProof": False,
            "teamVersusRuntimeProof": False,
            "spectatorAdminRuntimeProof": False,
            "moreThanTwoOriginalBinaryRuntimeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "safeToPatchMPlayersAbove2": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "rawPrivateProofPathPublished": False,
            "rawPrivateArtifactContentPublished": False,
            "absolutePrivatePathPublished": False,
            "rawRuntimePointerPublishedInPublicDocs": False,
            "rawRuntimePidPublishedInPublicDocs": False,
            "rawCdbLogPathPublishedInPublicDocs": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This is a copied original-binary level-854/config-1 P1/P2 input-assisted outcome transition attempt. "
            "It uses focused scoped input, exact-PID CDB observation, no-input wait controls, and copied-game safety. "
            "Only outcome-transition hits inside stimulus input windows with same-window input-assist hits can promote "
            "runtimeOutcomeProof; wait-window or ambient hits are rejected as causal proof. This is not real online "
            "multiplayer, not LAN, not public "
            "matchmaking, not native BEA netcode, not co-op/versus classification, not active P3/P4 gameplay, not "
            "more-than-two-player original-binary runtime proof, and not rebuild/no-noticeable-difference parity."
        ),
    }
    write_json(output_path, bundle)
    return bundle


def build_live_bundle(artifact_root: Path, output_path: Path, *, exe_override: Path) -> dict[str, Any]:
    artifact_root = require_private_path(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"),
        "--artifact-root",
        str(artifact_root),
        "--arm-live-bea",
        "LAUNCH SAFE COPY BEA",
        "--timeout-seconds",
        "36",
        "--capture-count",
        "1",
        "--pre-input-capture-count",
        "1",
        "--capture-after-each-input-sequence",
        "--after-input-capture-delay-ms",
        "350",
        "--capture-interval-seconds",
        "1",
        "--post-window-delay-seconds",
        "1",
        "--level-id",
        "854",
        "--controller-configuration",
        "1",
        "--bind-forward-qe-for-input-isolation",
        "--enable-cdb-observer",
        "--arm-cdb-observer",
        "ATTACH CDB TO SAFE COPY BEA",
        "--cdb-command-file",
        str(COMMAND_FILE.relative_to(ROOT)),
        "--cdb-post-attach-wait-seconds",
        "2",
        "--exe-override",
        str(exe_override),
    ]
    for sequence in INPUT_SEQUENCES:
        command.extend(["--input-sequence", sequence])
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (artifact_root / "input-assisted-outcome-builder-stdout.log").write_text(result.stdout, encoding="utf-8")
    (artifact_root / "input-assisted-outcome-builder-stderr.log").write_text(result.stderr, encoding="utf-8")
    runtime_artifact = artifact_root / "live-safe-copy-runtime-smoke.json"
    if result.returncode != 0:
        raise Level854InputAssistedOutcomeBuildError(
            "live level854 input-assisted outcome smoke failed with exit "
            f"{result.returncode}; see {artifact_root / 'input-assisted-outcome-builder-stderr.log'}"
        )
    bundle = build_bundle_from_runtime(runtime_artifact, output_path, fresh_live_execution=True)
    bundle["runtimeEvidence"]["liveSmokeExitCode"] = result.returncode
    bundle["runtimeEvidence"]["liveSmokeAcceptedDespiteNonzeroExit"] = False
    write_json(output_path, bundle)
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--runtime-artifact", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--exe-override", type=Path, default=DEFAULT_EXE_OVERRIDE)
    args = parser.parse_args()
    if args.runtime_artifact is not None:
        bundle = build_bundle_from_runtime(args.runtime_artifact, args.output)
    else:
        bundle = build_live_bundle(args.artifact_root or fresh_artifact_root(), args.output, exe_override=args.exe_override)
    print(
        json.dumps(
            {
                "artifact": str(args.output),
                "schemaVersion": bundle["schemaVersion"],
                "proofScope": bundle["proofScope"],
                "inputWindowOutcomeTransitionHitCount": bundle["inputAssistedOutcome"]["inputWindowOutcomeTransitionHitCount"],
                "waitWindowOutcomeTransitionHitCount": bundle["inputAssistedOutcome"]["waitWindowOutcomeTransitionHitCount"],
                "runtimeOutcomeProof": bundle["inputAssistedOutcome"]["runtimeOutcomeProof"],
                "stimulusAttemptOnly": bundle["inputAssistedOutcome"]["stimulusAttemptOnly"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Level854InputAssistedOutcomeBuildError as exc:
        print(f"WinUI original-binary level854 input-assisted outcome build: FAIL: {exc}")
        raise SystemExit(2)
