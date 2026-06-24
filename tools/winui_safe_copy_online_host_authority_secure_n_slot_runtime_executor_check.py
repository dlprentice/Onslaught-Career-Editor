#!/usr/bin/env python3
"""Validate a secure N-slot session proof that directly drives copied-runtime P1/P2 input."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_host_authority_n_slot_session_security_smoke_bundle as security_builder
import winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check as runtime_bridge
import winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check as security


EXPECTED_SCHEMA = "winui-original-binary-host-authority-secure-n-slot-runtime-executor.v1"
EXPECTED_PROTOCOL = "host-authority-secure-n-slot-runtime-executor.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-secure-n-slot-runtime-executor"
EXPECTED_HELPER_VERSION = "host-authority-secure-n-slot-runtime-executor.v1"
EXPECTED_EXECUTION_MODE = "secure-n-slot-session-derived-safe-copy-runtime-state-observer"
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
EXPECTED_SEQUENCES = [
    "wait:300",
    security.EXPECTED_P1_SEQUENCE,
    "wait:300",
    security.EXPECTED_P2_SEQUENCE,
]
MAX_LIVE_EXECUTOR_ATTEMPTS = 2
FIRST_WAIT_RENDER_WARMUP_TOKEN = "wait window 1 had no render movement samples"


class SecureNSlotRuntimeExecutorProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecureNSlotRuntimeExecutorProofError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_private_path(path: Path, *, must_exist: bool) -> Path:
    resolved = path.resolve()
    root = runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SecureNSlotRuntimeExecutorProofError(
            f"proof path must stay under ignored private proof root: {root}"
        ) from exc
    if must_exist:
        require(resolved.is_file(), f"proof artifact is missing: {resolved}")
    return resolved


def resolve_path(anchor: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = anchor.parent / candidate
    return require_private_path(candidate, must_exist=True)


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def validate_session_security(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        summary = security.validate_bundle(path)
        bundle = security.read_json(path)
    except (security.HostAuthorityNSlotSessionSecuritySmokeProofError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        raise SecureNSlotRuntimeExecutorProofError(f"session-security proof rejected: {exc}") from exc

    scheduler = object_at(bundle, "hostAuthorityNSlotScheduler")
    authorization = object_at(bundle, "authorization")
    require(summary["securityProofScope"] == security.EXPECTED_SECURITY_SCOPE, "session-security scope mismatch")
    require(summary["sessionScopedMacCoverageProof"] is True, "session MAC proof missing")
    require(summary["maxJsonLineBytesEnforced"] is True, "JSON-line proof missing")
    require(summary["unknownFieldRejectionProof"] is True, "unknown-field proof missing")
    require(summary["strictMessageSchemaProof"] is True, "strict schema proof missing")
    require(summary["acceptedOriginalBinaryGameplayCommandCount"] == 2, "accepted secure command count mismatch")
    require(summary["metadataGameplayRejectionCount"] == 2, "metadata rejection count mismatch")
    require(summary["rejectedSecurityCaseCount"] == len(security.EXPECTED_SECURITY_REJECTION_CASES), "security rejection count mismatch")
    require(summary["newBeaLaunchCount"] == 0, "session-security proof must not launch BEA")
    require(summary["cdbAttachCount"] == 0, "session-security proof must not attach CDB")
    require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "N-player runtime proof must stay zero")
    require(summary["activeP3P4OriginalBinaryGameplayProof"] is False, "P3/P4 proof must stay false")
    require(scheduler.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "accepted slots mismatch")
    require(scheduler.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata slots mismatch")
    require(scheduler.get("runtimeCompatibleP1P2RelayHash") == security.EXPECTED_RUNTIME_P1P2_RELAY_HASH, "runtime-compatible relay hash mismatch")
    require(authorization.get("tickBoundMacFieldsProof") is True, "tick-bound MAC proof missing")
    require(authorization.get("relayPlanHashMacBound") is True, "relay-plan MAC binding missing")
    return summary, bundle


def derived_input_sequences(session_bundle: dict[str, Any]) -> list[str]:
    scheduler = object_at(session_bundle, "hostAuthorityNSlotScheduler")
    relay_plan = scheduler.get("relayPlan")
    require(isinstance(relay_plan, list), "session relay plan must be a list")
    require([row.get("clientSlot") for row in relay_plan if isinstance(row, dict)] == EXPECTED_ACTIVE_SLOTS, "session relay plan order must be P1/P2")
    sequences = [str(row.get("mappedInputSequence") or "") for row in relay_plan if isinstance(row, dict)]
    require(sequences == [security.EXPECTED_P1_SEQUENCE, security.EXPECTED_P2_SEQUENCE], "session relay sequences mismatch")
    return EXPECTED_SEQUENCES


def runtime_input_window_sequences(runtime_path: Path) -> list[str]:
    return runtime_bridge.runtime_input_window_sequences(runtime_path)


def validate_movement_runtime(runtime_path: Path) -> dict[str, Any]:
    return runtime_bridge.validate_movement_runtime(runtime_path)


def runtime_artifact_has_first_wait_render_warmup_miss(runtime_path: Path) -> bool:
    if not runtime_path.is_file():
        return False
    try:
        raw = read_json(runtime_path)
        observer = raw.get("cdbObserver") if isinstance(raw.get("cdbObserver"), dict) else {}
        result = observer.get("result") if isinstance(observer.get("result"), dict) else {}
        log_path = Path(str(result.get("logPath") or observer.get("logPath") or ""))
        if not log_path.is_file():
            return False
        windows = runtime_bridge.movement_bridge.movement.state_delta.sequence_windows_from_artifact(raw, log_path)
        if set(windows) != {1, 2, 3, 4}:
            return False
        render_rows = {
            index: len(runtime_bridge.movement_bridge.movement.render_movement_rows(windows[index][2]))
            for index in (1, 2, 3, 4)
        }
        return (
            render_rows[1] == 0
            and render_rows[2] > 0
            and render_rows[3] > 0
            and render_rows[4] > 0
        )
    except Exception:
        return False


def movement_state_summary(movement_summary: dict[str, Any]) -> dict[str, Any]:
    return runtime_bridge.require_movement_summary(movement_summary)


def require_helper_contract(proof: dict[str, Any]) -> None:
    require(proof.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(proof.get("generatedBy") == EXPECTED_HELPER, "helper mismatch")
    require(proof.get("helperVersion") == EXPECTED_HELPER_VERSION, "helper version mismatch")
    require(proof.get("protocolVersion") == EXPECTED_PROTOCOL, "protocol mismatch")


def make_secure_runtime_executor_proof(
    session_path: Path,
    runtime_path: Path,
    output_path: Path,
    *,
    execution_receipt: dict[str, Any],
    allow_fixture_receipt: bool = False,
) -> dict[str, Any]:
    session_path = require_private_path(session_path, must_exist=True)
    runtime_path = require_private_path(runtime_path, must_exist=True)
    output_path = require_private_path(output_path, must_exist=False)
    security_summary, session_bundle = validate_session_security(session_path)
    expected_sequences = derived_input_sequences(session_bundle)
    require(runtime_input_window_sequences(runtime_path) == expected_sequences, "runtime input windows were not derived from secure session relay plan")
    movement_summary = validate_movement_runtime(runtime_path)
    movement_state = movement_state_summary(movement_summary)
    scheduler = object_at(session_bundle, "hostAuthorityNSlotScheduler")

    proof = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "sessionSecurityProof": relative_path(output_path.parent, session_path),
        "sessionSecurityProofSha256": sha256_file(session_path),
        "liveRuntimeArtifact": relative_path(output_path.parent, runtime_path),
        "liveRuntimeArtifactSha256": sha256_file(runtime_path),
        "execution": {
            "executionMode": EXPECTED_EXECUTION_MODE,
            "securityProofScope": security_summary["securityProofScope"],
            "sessionSecurityRelayPlanSha256": security_summary["relayPlanSha256"],
            "runtimeCompatibleP1P2RelayHash": scheduler["runtimeCompatibleP1P2RelayHash"],
            "derivedInputSequences": expected_sequences,
            "runtimeInputWindowSequences": runtime_input_window_sequences(runtime_path),
            "executionReceipt": execution_receipt,
            "generatedByLiveSmokeHarness": True,
            "safeCopyLaunchLevel": 850,
            "controllerConfiguration": 1,
            "visualCaptureCount": movement_summary["visualCaptureCount"],
            "runtimePlayers": {"P1": movement_summary["p0"], "P2": movement_summary["p1"]},
            "movementState": movement_state,
            "acceptedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": EXPECTED_METADATA_SLOTS,
            "secureSessionAcceptedCommandCount": security_summary["acceptedOriginalBinaryGameplayCommandCount"],
            "secureSessionMetadataRejectionCount": security_summary["metadataGameplayRejectionCount"],
            "secureSessionSecurityRejectionCount": security_summary["rejectedSecurityCaseCount"],
            "deliveredOriginalBinaryCommandCount": 2,
            "hostHelperInputSent": True,
            "gameInputSentByNSlotScheduler": False,
            "newBeaLaunchCount": 1,
            "cdbAttachCount": 1,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "visibleMovementDeltaClaim": False,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "noNoticeableDifferenceClaim": False,
        },
        "claimBoundary": (
            "Secure N-slot session-derived runtime executor proof for P1/P2 only. This records that an accepted "
            "same-workstation N-slot session-security proof supplied the P1/P2 relay input sequence for one fresh "
            "safe-copy level-850/config-1 BEA host-helper run, and exact-PID CDB movement-state windows showed Q/P1 "
            "and E/P2 state deltas. P3/P4 remain metadata-only and gameplay-rejected. This does not prove multi-host "
            "LAN, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more than two "
            "original-binary runtime players, deterministic sync, rollback, anti-cheat, physical gamepad behavior, "
            "production server identity, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, proof)
    return validate_secure_runtime_executor_proof(output_path, allow_fixture=allow_fixture_receipt)


def validate_secure_runtime_executor_proof(path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    path = require_private_path(path, must_exist=True)
    proof = read_json(path)
    require_helper_contract(proof)
    session_path = resolve_path(path, str(proof.get("sessionSecurityProof", "")))
    runtime_path = resolve_path(path, str(proof.get("liveRuntimeArtifact", "")))
    require(proof.get("sessionSecurityProofSha256") == sha256_file(session_path), "session proof hash mismatch")
    require(proof.get("liveRuntimeArtifactSha256") == sha256_file(runtime_path), "runtime artifact hash mismatch")
    security_summary, session_bundle = validate_session_security(session_path)
    expected_sequences = derived_input_sequences(session_bundle)
    movement_summary = validate_movement_runtime(runtime_path)
    movement_state = movement_state_summary(movement_summary)
    scheduler = object_at(session_bundle, "hostAuthorityNSlotScheduler")
    execution = object_at(proof, "execution")

    require(execution.get("executionMode") == EXPECTED_EXECUTION_MODE, "execution mode mismatch")
    require(execution.get("securityProofScope") == security_summary["securityProofScope"], "security scope mismatch")
    require(execution.get("sessionSecurityRelayPlanSha256") == security_summary["relayPlanSha256"], "session relay hash mismatch")
    require(execution.get("runtimeCompatibleP1P2RelayHash") == scheduler["runtimeCompatibleP1P2RelayHash"], "runtime relay hash mismatch")
    require(execution.get("derivedInputSequences") == expected_sequences, "derived input sequence mismatch")
    require(execution.get("runtimeInputWindowSequences") == runtime_input_window_sequences(runtime_path), "runtime sequence mismatch")
    require(execution.get("runtimeInputWindowSequences") == expected_sequences, "runtime windows not derived from secure session")
    receipt = object_at(execution, "executionReceipt")
    receipt_mode = receipt.get("mode")
    if allow_fixture:
        require(receipt_mode in {"live-secure-nslot-runtime-executor-subprocess", "self-test-fixture"}, "receipt mode mismatch")
    else:
        require(receipt_mode == "live-secure-nslot-runtime-executor-subprocess", "receipt mode must be live executor subprocess")
    require(receipt.get("liveSmokeReturnCode") == 0, "live smoke return code must be zero")
    require(receipt.get("childEnvSensitiveKeyCount") == 0, "child env retained sensitive-looking keys")
    require(receipt.get("executorRecordsFreshSameRootArtifacts") is True, "fresh same-root artifact receipt missing")
    if receipt_mode == "live-secure-nslot-runtime-executor-subprocess":
        receipt_root = Path(str(receipt.get("artifactRoot", ""))).resolve()
        require(receipt_root == path.parent.resolve(), "receipt artifact root must match proof root")
        created_files = object_at(receipt, "createdFiles")
        created_runtime = object_at(created_files, "liveRuntimeArtifact")
        require(Path(str(created_runtime.get("path", ""))).resolve() == runtime_path.resolve(), "created runtime receipt path mismatch")
        require(created_runtime.get("sha256") == sha256_file(runtime_path), "created runtime receipt hash mismatch")
    require(execution.get("generatedByLiveSmokeHarness") is True, "live smoke harness generation must be recorded")
    require(execution.get("safeCopyLaunchLevel") == 850, "level must stay 850")
    require(execution.get("controllerConfiguration") == 1, "controller config must stay 1")
    require(execution.get("visualCaptureCount") == movement_summary["visualCaptureCount"], "visual capture count mismatch")
    require(execution.get("runtimePlayers") == {"P1": movement_summary["p0"], "P2": movement_summary["p1"]}, "runtime players mismatch")
    require(execution.get("movementState") == movement_state, "movement-state summary mismatch")
    require(execution.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "accepted slot mismatch")
    require(execution.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata slot mismatch")
    require(execution.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "rejected route mismatch")
    require(execution.get("secureSessionAcceptedCommandCount") == 2, "accepted secure command count mismatch")
    require(execution.get("secureSessionMetadataRejectionCount") == 2, "metadata rejection count mismatch")
    require(execution.get("secureSessionSecurityRejectionCount") == len(security.EXPECTED_SECURITY_REJECTION_CASES), "security rejection count mismatch")
    require(execution.get("deliveredOriginalBinaryCommandCount") == 2, "expected two delivered commands")
    require(execution.get("hostHelperInputSent") is True, "host-helper input must be true")
    require(execution.get("gameInputSentByNSlotScheduler") is False, "scheduler direct game input must be false")
    require(execution.get("newBeaLaunchCount") == 1, "this proof must account for one copied BEA launch")
    require(execution.get("cdbAttachCount") == 1, "this proof must account for one CDB attach")
    require(execution.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(execution.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 proof must stay false")
    require(execution.get("visibleMovementDeltaClaim") is False, "visible movement causality must remain unclaimed")
    for key in (
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "publicServerClaim",
        "nativeBeaNetcodeClaim",
        "deterministicSyncClaim",
        "rollbackClaim",
        "antiCheatClaim",
        "physicalGamepadClaim",
        "rebuildParityClaim",
        "noNoticeableDifferenceClaim",
    ):
        require(execution.get(key) is False, f"overclaim must be false: {key}")

    return {
        "schemaVersion": proof["schemaVersion"],
        "protocolVersion": proof["protocolVersion"],
        "artifact": str(path),
        "sessionSecurityProof": str(session_path),
        "liveRuntimeArtifact": str(runtime_path),
        "claim": (
            "secure N-slot session proof directly drove one copied-runtime P1/P2 movement-state proof"
            if receipt_mode == "live-secure-nslot-runtime-executor-subprocess"
            else "self-test fixture exercises secure N-slot runtime executor checker only"
        ),
        "receiptMode": receipt_mode,
        "securityProofScope": execution["securityProofScope"],
        "sessionSecurityRelayPlanSha256": execution["sessionSecurityRelayPlanSha256"],
        "runtimeCompatibleP1P2RelayHash": execution["runtimeCompatibleP1P2RelayHash"],
        "derivedInputSequences": expected_sequences,
        "acceptedOriginalBinaryGameplaySlots": execution["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": execution["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": execution["rejectedGameplayRouteSlots"],
        "secureSessionAcceptedCommandCount": execution["secureSessionAcceptedCommandCount"],
        "secureSessionMetadataRejectionCount": execution["secureSessionMetadataRejectionCount"],
        "secureSessionSecurityRejectionCount": execution["secureSessionSecurityRejectionCount"],
        "visualCaptureCount": execution["visualCaptureCount"],
        "runtimePlayers": execution["runtimePlayers"],
        "movementState": execution["movementState"],
        "deliveredOriginalBinaryCommandCount": execution["deliveredOriginalBinaryCommandCount"],
        "hostHelperInputSent": execution["hostHelperInputSent"],
        "gameInputSentByNSlotScheduler": execution["gameInputSentByNSlotScheduler"],
        "newBeaLaunchCount": execution["newBeaLaunchCount"],
        "cdbAttachCount": execution["cdbAttachCount"],
        "nPlayerOriginalBinaryRuntimeProof": execution["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": execution["activeP3P4OriginalBinaryGameplayProof"],
        "visibleMovementDeltaClaim": execution["visibleMovementDeltaClaim"],
        "claimBoundary": proof["claimBoundary"],
    }


def build_live_secure_runtime_executor(session_path: Path, artifact_root: Path, *, exe_override: Path) -> dict[str, Any]:
    artifact_root = runtime_bridge.movement_bridge.executor.require_private_proof_path(artifact_root)
    session_path = session_path.resolve()
    exe_override = exe_override.resolve()
    require(exe_override.is_file(), f"executable override not found: {exe_override}")
    _, session_bundle = validate_session_security(session_path)
    sequences = derived_input_sequences(session_bundle)
    retried_after_first_wait_render_warmup_miss = False
    last_warmup_error: Exception | None = None
    for attempt in range(1, MAX_LIVE_EXECUTOR_ATTEMPTS + 1):
        current_root = artifact_root if attempt == 1 else artifact_root / f"retry-{attempt}"
        command = runtime_bridge.live_smoke_command(sequences, artifact_root=current_root, exe_override=exe_override)
        child_env = runtime_bridge.movement_bridge.executor.minimal_child_env()
        runtime_bridge.movement_bridge.executor.require_no_bea_or_cdb_processes("before secure N-slot runtime executor")
        started_at = dt.datetime.now(dt.timezone.utc)
        completed = runtime_bridge.movement_bridge.executor.run_live_smoke_process(command)
        ended_at = dt.datetime.now(dt.timezone.utc)
        require(completed.returncode == 0, f"live smoke failed with {completed.returncode}: {completed.stdout}\n{completed.stderr}")
        runtime_path = current_root / ("live-safe-copy-runtime-" + "smoke.json")
        require(runtime_path.is_file(), f"live runtime artifact was not created: {runtime_path}")
        output_path = current_root / "secure-n-slot-runtime-executor-proof.json"
        runtime_bridge.movement_bridge.executor.require_no_bea_or_cdb_processes("after secure N-slot runtime executor")
        receipt = {
            "mode": "live-secure-nslot-runtime-executor-subprocess",
            "artifactRoot": str(current_root.resolve()),
            "startedAtUtc": started_at.isoformat(),
            "endedAtUtc": ended_at.isoformat(),
            "liveSmokeCommandSha256": runtime_bridge.movement_bridge.executor.command_hash(command),
            "liveSmokeReturnCode": completed.returncode,
            "liveExecutorAttemptCount": attempt,
            "liveExecutorRetriedAfterFirstWaitRenderWarmupMiss": retried_after_first_wait_render_warmup_miss,
            "childEnvKeyCount": len(child_env),
            "childEnvSensitiveKeyCount": len(runtime_bridge.movement_bridge.executor.sensitive_env_keys(child_env)),
            "childEnvSensitiveKeys": runtime_bridge.movement_bridge.executor.sensitive_env_keys(child_env),
            "executorRecordsFreshSameRootArtifacts": runtime_path.parent.resolve() == current_root.resolve(),
            "createdFiles": {
                "liveRuntimeArtifact": runtime_bridge.movement_bridge.executor.created_file_receipt(runtime_path),
            },
            "stdoutSha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
            "stderrSha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
        }
        try:
            return make_secure_runtime_executor_proof(session_path, runtime_path, output_path, execution_receipt=receipt)
        except runtime_bridge.movement_bridge.movement.MovementStateDeltaError as exc:
            first_wait_warmup_miss = (
                FIRST_WAIT_RENDER_WARMUP_TOKEN in str(exc)
                and runtime_artifact_has_first_wait_render_warmup_miss(runtime_path)
            )
            if first_wait_warmup_miss and attempt < MAX_LIVE_EXECUTOR_ATTEMPTS:
                last_warmup_error = exc
                retried_after_first_wait_render_warmup_miss = True
                continue
            raise
    if last_warmup_error is not None:
        raise SecureNSlotRuntimeExecutorProofError(
            f"live secure N-slot runtime executor failed after retryable first-wait render warmup miss: {last_warmup_error}"
        ) from last_warmup_error
    raise SecureNSlotRuntimeExecutorProofError("live secure N-slot runtime executor did not produce a proof")


def make_fixture(root: Path) -> Path:
    session_path = root / "session" / "host-authority-n-slot-session-security-smoke-proof.json"
    security_builder.build_bundle(session_path)
    runtime_bridge_proof = runtime_bridge.movement_bridge.make_bridge_fixture(root / "runtime")
    _, runtime_path, _ = runtime_bridge.movement_bridge.resolve_executor_paths(runtime_bridge_proof)
    output_path = root / "secure-n-slot-runtime-executor-proof.json"
    receipt = {
        "mode": "self-test-fixture",
        "artifactRoot": str(root.resolve()),
        "liveSmokeCommandSha256": "0" * 64,
        "liveSmokeReturnCode": 0,
        "childEnvKeyCount": 0,
        "childEnvSensitiveKeyCount": 0,
        "childEnvSensitiveKeys": [],
        "executorRecordsFreshSameRootArtifacts": True,
        "createdFiles": {
            "liveRuntimeArtifact": runtime_bridge.movement_bridge.executor.created_file_receipt(runtime_path),
        },
    }
    return Path(
        make_secure_runtime_executor_proof(
            session_path,
            runtime_path,
            output_path,
            execution_receipt=receipt,
            allow_fixture_receipt=True,
        )["artifact"]
    )


def self_test() -> None:
    runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_secure_runtime_executor_proof(make_fixture(Path(tmp)), allow_fixture=True)
        require(summary["hostHelperInputSent"] is True, "self-test host-helper flag missing")
        require(summary["acceptedOriginalBinaryGameplaySlots"] == EXPECTED_ACTIVE_SLOTS, "self-test slot mismatch")

    with tempfile.TemporaryDirectory(dir=runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT) as tmp:
        root = Path(tmp)
        proof_path = make_fixture(root)
        proof = read_json(proof_path)
        runtime_path = resolve_path(proof_path, str(proof["liveRuntimeArtifact"]))
        runtime = read_json(runtime_path)
        runtime["inputCdbWindows"][1]["sequence"] = "down:O,wait:500,up:O"
        write_json(runtime_path, runtime)
        try:
            validate_secure_runtime_executor_proof(proof_path, allow_fixture=True)
        except SecureNSlotRuntimeExecutorProofError:
            pass
        else:
            raise SecureNSlotRuntimeExecutorProofError("runtime sequence tamper should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("runtime_artifact", nargs="?", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--build-live-from-session-security", type=Path, default=None)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--exe-override", type=Path, default=runtime_bridge.movement_bridge.executor.DEFAULT_EXE_OVERRIDE)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary secure N-slot runtime executor checker self-test: PASS")
        return 0
    if args.build_live_from_session_security is not None:
        if args.artifact_root is None:
            raise SystemExit("--artifact-root is required with --build-live-from-session-security")
        print(json.dumps(build_live_secure_runtime_executor(args.build_live_from_session_security, args.artifact_root, exe_override=args.exe_override), indent=2, sort_keys=True))
        return 0
    if args.proof is not None and args.runtime_artifact is not None:
        if args.output is None:
            raise SystemExit("--output is required when building from session-security and runtime artifact")
        receipt = {
            "mode": "self-test-fixture",
            "artifactRoot": str(args.output.parent.resolve()),
            "liveSmokeCommandSha256": "0" * 64,
            "liveSmokeReturnCode": 0,
            "childEnvKeyCount": 0,
            "childEnvSensitiveKeyCount": 0,
            "childEnvSensitiveKeys": [],
            "executorRecordsFreshSameRootArtifacts": args.runtime_artifact.resolve().parent == args.output.resolve().parent,
            "createdFiles": {
                "liveRuntimeArtifact": runtime_bridge.movement_bridge.executor.created_file_receipt(args.runtime_artifact.resolve()),
            },
        }
        print(
            json.dumps(
                make_secure_runtime_executor_proof(
                    args.proof,
                    args.runtime_artifact,
                    args.output,
                    execution_receipt=receipt,
                    allow_fixture_receipt=True,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.proof is None:
        raise SystemExit("proof is required unless --self-test or --build-live-from-session-security is used")
    print(json.dumps(validate_secure_runtime_executor_proof(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SecureNSlotRuntimeExecutorProofError,
        security.HostAuthorityNSlotSessionSecuritySmokeProofError,
        runtime_bridge.HostAuthorityNSlotRuntimeBridgeError,
        runtime_bridge.nslot.HostAuthorityNSlotProcessSmokeProofError,
        runtime_bridge.movement_bridge.HostAuthorityRuntimeMovementBridgeError,
        runtime_bridge.movement_bridge.executor.HostAuthorityRuntimeExecutorError,
        runtime_bridge.movement_bridge.executor.delivery.HostAuthorityRuntimeDeliveryError,
        runtime_bridge.movement_bridge.movement.MovementStateDeltaError,
        runtime_bridge.movement_bridge.movement.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary secure N-slot runtime executor check: FAIL: {exc}")
        raise SystemExit(2)
