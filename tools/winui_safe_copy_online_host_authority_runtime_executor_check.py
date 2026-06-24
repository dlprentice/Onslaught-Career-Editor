#!/usr/bin/env python3
"""Validate a relay-plan-driven host-authority copied-runtime execution proof."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_runtime_delivery_check as delivery


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROOF_ROOT = ROOT / "subagents" / "winui-safe-copy-live-runtime"
LIVE_SMOKE = ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"
DEFAULT_EXE_OVERRIDE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe.original.backup")
EXPECTED_SCHEMA = "winui-original-binary-host-authority-runtime-executor.v1"
EXPECTED_PROTOCOL = "host-authority-runtime-executor.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-runtime-executor"
EXPECTED_HELPER_VERSION = "host-authority-runtime-executor.v1"
EXPECTED_EXECUTION_MODE = "host-authority-relay-plan-derived-safe-copy-runtime-execution"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_runtime_executor_check.py --self-test"
LIVE_EXECUTOR_TIMEOUT_SECONDS = 240
SENSITIVE_ENV_FRAGMENTS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASS", "COOKIE", "SESSION", "AUTH", "CREDENTIAL")
ALLOWED_CHILD_ENV_KEYS = {
    "APPDATA",
    "COMSPEC",
    "HOME",
    "HOMEDRIVE",
    "HOMEPATH",
    "LOCALAPPDATA",
    "NUMBER_OF_PROCESSORS",
    "OS",
    "PATH",
    "PATHEXT",
    "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_IDENTIFIER",
    "PROCESSOR_LEVEL",
    "PROCESSOR_REVISION",
    "PROGRAMDATA",
    "PROGRAMFILES",
    "PROGRAMFILES(X86)",
    "PROGRAMW6432",
    "PSMODULEPATH",
    "PUBLIC",
    "SYSTEMDRIVE",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "USERDOMAIN",
    "USERNAME",
    "USERPROFILE",
    "WINDIR",
}


class HostAuthorityRuntimeExecutorError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityRuntimeExecutorError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = bundle_path.parent / candidate
    candidate = candidate.resolve()
    require(candidate.is_file(), f"referenced file is missing: {candidate}")
    return candidate


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def require_private_proof_path(path: Path) -> Path:
    resolved = path.resolve()
    root = PRIVATE_PROOF_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise HostAuthorityRuntimeExecutorError(
            f"artifact root/output must stay under ignored private proof root: {root}"
        ) from exc
    return resolved


def minimal_child_env() -> dict[str, str]:
    allowed = {key.upper() for key in ALLOWED_CHILD_ENV_KEYS}
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    sensitive = sensitive_env_keys(env)
    require(not sensitive, f"minimal child env unexpectedly retained sensitive-looking keys: {', '.join(sensitive)}")
    return env


def sensitive_env_keys(env: dict[str, str]) -> list[str]:
    return sorted(key for key in env if any(fragment in key.upper() for fragment in SENSITIVE_ENV_FRAGMENTS))


def process_names_running(names: tuple[str, ...] = ("BEA", "cdb")) -> list[dict[str, str | int]]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "$names=@(" + ",".join(f"'{name}'" for name in names) + "); "
        "Get-Process -Name $names -ErrorAction SilentlyContinue | "
        "Select-Object ProcessName,Id,Path | ConvertTo-Json -Compress",
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=minimal_child_env())
    if completed.returncode not in (0, 1) or not completed.stdout.strip():
        return []
    value = json.loads(completed.stdout)
    rows = value if isinstance(value, list) else [value]
    return [row for row in rows if isinstance(row, dict)]


def require_no_bea_or_cdb_processes(context: str) -> None:
    rows = process_names_running()
    require(not rows, f"{context}: BEA/CDB processes are still running: {rows}")


def require_no_serialized_credentials(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            require(
                lowered not in {"secret", "sharedsecret", "rawsecret", "authkey", "credential", "password", "token"},
                f"serialized credential-like field is not allowed at {path}.{key}",
            )
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def relay_plan_sequences(host_bundle: dict[str, Any]) -> list[str]:
    scheduler = object_at(host_bundle, "hostAuthorityScheduler")
    require(scheduler.get("deterministicScheduleOrder") == ["P1", "P2"], "deterministic order must stay P1/P2")
    plan = list_at(scheduler, "relayPlan")
    require([row.get("clientSlot") for row in plan if isinstance(row, dict)] == ["P1", "P2"], "relay plan order mismatch")
    sequences = [str(row.get("mappedInputSequence") or "") for row in plan if isinstance(row, dict)]
    require(sequences == [delivery.host.EXPECTED_P1_SEQUENCE, delivery.host.EXPECTED_P2_SEQUENCE], "relay plan sequences mismatch")
    return sequences


def derived_runtime_input_sequences(host_bundle: dict[str, Any]) -> list[str]:
    p1, p2 = relay_plan_sequences(host_bundle)
    return ["wait:300", p1, "wait:300", p2]


def runtime_input_window_sequences(runtime_path: Path) -> list[str]:
    runtime = delivery.state_delta.read_json(runtime_path)
    windows = runtime.get("inputCdbWindows")
    require(isinstance(windows, list), f"{runtime_path} missing inputCdbWindows")
    return [str(row.get("sequence") or "") for row in windows if isinstance(row, dict)]


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected executor schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected executor helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected executor helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected executor protocol")


def validate_executor_proof(path: Path) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)

    host_path = resolve_path(path, str(bundle.get("hostAuthorityTwoClientProofBundle", "")))
    require(bundle.get("hostAuthorityTwoClientProofSha256") == sha256_file(host_path), "host-authority proof hash mismatch")
    host_summary = delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    host_bundle = delivery.host.read_json(host_path)
    expected_sequences = derived_runtime_input_sequences(host_bundle)
    host_descriptor = object_at(host_bundle, "sessionDescriptor")

    runtime_path = resolve_path(path, str(bundle.get("liveRuntimeArtifact", "")))
    require(bundle.get("liveRuntimeArtifactSha256") == sha256_file(runtime_path), "live runtime artifact hash mismatch")
    runtime_bundle = delivery.state_delta.read_json(runtime_path)
    runtime_source = object_at(runtime_bundle, "source")
    require(runtime_source.get("overrideHashBefore") == host_descriptor.get("cleanSpecimenSha256"), "runtime override hash does not match scheduler clean specimen")
    runtime_summary = delivery.state_delta.validate_artifact(
        runtime_path,
        min_capture_count=1,
        expected_controller_configuration=1,
        expected_qe_proof_lever="input-isolation-forward-qe",
    )
    require(runtime_input_window_sequences(runtime_path) == expected_sequences, "runtime input windows were not derived relay-plan sequence")

    delivery_path = resolve_path(path, str(bundle.get("runtimeDeliveryProofBundle", "")))
    require(bundle.get("runtimeDeliveryProofSha256") == sha256_file(delivery_path), "runtime delivery proof hash mismatch")
    require(runtime_path.parent.resolve() == path.parent.resolve(), "live runtime artifact must share executor proof root")
    require(delivery_path.parent.resolve() == path.parent.resolve(), "runtime delivery proof must share executor proof root")
    delivery_summary = delivery.validate_bundle(delivery_path)
    require(Path(delivery_summary["hostAuthorityTwoClientProofBundle"]).resolve() == host_path.resolve(), "delivery proof host reference mismatch")
    require(Path(delivery_summary["liveRuntimeArtifact"]).resolve() == runtime_path.resolve(), "delivery proof runtime reference mismatch")

    execution = object_at(bundle, "execution")
    require(execution.get("executionMode") == EXPECTED_EXECUTION_MODE, "execution mode mismatch")
    require(execution.get("hostAuthorityRelayPlanSha256") == host_summary["relayPlanSha256"], "host relay plan hash mismatch")
    require(execution.get("derivedInputSequences") == expected_sequences, "derived input sequence mismatch")
    require(execution.get("runtimeInputWindowSequences") == expected_sequences, "runtime input sequence mismatch")
    require(execution.get("runtimeDeliveryProofBuilt") is True, "runtime delivery bundle build must be recorded")
    require(execution.get("generatedByLiveSmokeHarness") is True, "live smoke harness generation must be recorded")
    receipt = object_at(execution, "executionReceipt")
    require(receipt.get("mode") in {"live-executor-subprocess", "self-test-fixture"}, "execution receipt mode mismatch")
    require(Path(str(receipt.get("artifactRoot") or "")).resolve() == path.parent.resolve(), "execution receipt artifact root mismatch")
    require(receipt.get("liveSmokeReturnCode") == 0, "live smoke return code must be zero")
    require(receipt.get("runtimeDeliveryBuildReturnCode") == 0, "runtime delivery build return code must be zero")
    require(receipt.get("executorRecordsFreshSameRootArtifacts") is True, "fresh same-root artifact receipt missing")
    command_sha = str(receipt.get("liveSmokeCommandSha256") or "")
    require(len(command_sha) == 64, "live smoke command hash must be SHA-256")
    require(receipt.get("childEnvSensitiveKeyCount") == 0, "executor child env retained sensitive-looking keys")
    require(receipt.get("childEnvSensitiveKeys") == [], "executor child env sensitive key list must be empty")
    created = object_at(receipt, "createdFiles")
    for key, expected_path in (
        ("liveRuntimeArtifact", runtime_path),
        ("runtimeDeliveryProofBundle", delivery_path),
    ):
        row = object_at(created, key)
        require(Path(str(row.get("path") or "")).resolve() == expected_path.resolve(), f"created file path mismatch: {key}")
        require(isinstance(row.get("mtimeUtc"), str) and row["mtimeUtc"], f"created file mtime missing: {key}")
    require(execution.get("safeCopyLaunchLevel") == 850, "executor must stay on level 850")
    require(execution.get("controllerConfiguration") == 1, "executor must stay on controller config 1")
    require(execution.get("deliveredOriginalBinaryCommandCount") == 2, "expected two delivered original-binary commands")
    require(execution.get("hostHelperInputSent") is True, "host-helper input must be true")
    require(execution.get("gameInputSentByScheduler") is False, "scheduler must not claim direct game input")
    require(execution.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player original-binary runtime proof must stay zero")
    require(execution.get("visualCaptureCount") == delivery_summary["visualCaptureCount"], "visual capture count mismatch")
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
        require(execution.get(key) is False, f"execution overclaim must be false: {key}")

    return {
        "artifact": str(path),
        "claim": "scheduler relay plan drove one copied BEA runtime-delivery proof through the safe-copy live harness",
        "hostAuthorityTwoClientProofBundle": str(host_path),
        "liveRuntimeArtifact": str(runtime_path),
        "runtimeDeliveryProofBundle": str(delivery_path),
        "derivedInputSequences": execution["derivedInputSequences"],
        "hostAuthorityRelayPlanSha256": execution["hostAuthorityRelayPlanSha256"],
        "visualCaptureCount": execution["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": execution["deliveredOriginalBinaryCommandCount"],
        "nPlayerOriginalBinaryRuntimeProof": execution["nPlayerOriginalBinaryRuntimeProof"],
        "claimBoundary": (
            "This proves the accepted host-authority P1/P2 relay plan was used as the source of a safe-copy live "
            "runtime execution that produced and validated one copied original-BEA level-850/config-1 runtime-delivery "
            "bundle. It does not prove multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 "
            "gameplay, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or "
            "no-noticeable-difference online parity."
        ),
    }


def make_executor_proof(
    host_path: Path,
    runtime_path: Path,
    delivery_path: Path,
    output_path: Path,
    *,
    host_summary: dict[str, Any] | None = None,
    runtime_summary: dict[str, Any] | None = None,
    delivery_summary: dict[str, Any] | None = None,
    execution_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    host_path = host_path.resolve()
    runtime_path = runtime_path.resolve()
    delivery_path = delivery_path.resolve()
    output_path = output_path.resolve()
    require_private_proof_path(output_path)
    host_summary = host_summary or delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    host_bundle = delivery.host.read_json(host_path)
    expected_sequences = derived_runtime_input_sequences(host_bundle)
    runtime_summary = runtime_summary or delivery.state_delta.validate_artifact(
        runtime_path,
        min_capture_count=1,
        expected_controller_configuration=1,
        expected_qe_proof_lever="input-isolation-forward-qe",
    )
    delivery_summary = delivery_summary or delivery.validate_bundle(delivery_path)
    execution_receipt = execution_receipt or {
        "mode": "self-test-fixture",
        "artifactRoot": str(output_path.parent),
        "liveSmokeReturnCode": 0,
        "runtimeDeliveryBuildReturnCode": 0,
        "liveSmokeCommandSha256": "0" * 64,
        "childEnvKeyCount": 0,
        "childEnvSensitiveKeyCount": 0,
        "childEnvSensitiveKeys": [],
        "executorRecordsFreshSameRootArtifacts": True,
        "createdFiles": {
            "liveRuntimeArtifact": {
                "path": str(runtime_path),
                "mtimeUtc": dt.datetime.fromtimestamp(runtime_path.stat().st_mtime, dt.timezone.utc).isoformat(),
            },
            "runtimeDeliveryProofBundle": {
                "path": str(delivery_path),
                "mtimeUtc": dt.datetime.fromtimestamp(delivery_path.stat().st_mtime, dt.timezone.utc).isoformat(),
            },
        },
    }
    execution = {
        "executionMode": EXPECTED_EXECUTION_MODE,
        "sourceHostAuthorityProtocolVersion": delivery.host.EXPECTED_PROTOCOL,
        "runtimeDeliveryProtocolVersion": delivery.EXPECTED_PROTOCOL,
        "hostAuthorityRelayPlanSha256": host_summary["relayPlanSha256"],
        "derivedInputSequences": expected_sequences,
        "runtimeInputWindowSequences": runtime_input_window_sequences(runtime_path),
        "executionReceipt": execution_receipt,
        "generatedByLiveSmokeHarness": True,
        "runtimeDeliveryProofBuilt": True,
        "safeCopyLaunchLevel": 850,
        "controllerConfiguration": 1,
        "visualCaptureCount": delivery_summary["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": delivery_summary["deliveredOriginalBinaryCommandCount"],
        "hostHelperInputSent": True,
        "gameInputSentByScheduler": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
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
    }
    bundle = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "hostAuthorityTwoClientProofBundle": relative_path(output_path.parent, host_path),
        "hostAuthorityTwoClientProofSha256": sha256_file(host_path),
        "liveRuntimeArtifact": relative_path(output_path.parent, runtime_path),
        "liveRuntimeArtifactSha256": sha256_file(runtime_path),
        "runtimeDeliveryProofBundle": relative_path(output_path.parent, delivery_path),
        "runtimeDeliveryProofSha256": sha256_file(delivery_path),
        "execution": execution,
        "claimBoundary": (
            "Relay-plan-driven host-authority runtime execution proof for P1/P2 only. This records that the accepted "
            "scheduler relay plan supplied the safe-copy live harness input sequence before the runtime-delivery bundle "
            "was built. It does not prove multi-host LAN, public matchmaking, native BEA netcode, P3/P4 active gameplay, "
            "deterministic sync, rollback, anti-cheat, gamepad behavior, rebuild parity, or no-noticeable-difference parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return validate_executor_proof(output_path)


def live_smoke_command(host_bundle: dict[str, Any], *, artifact_root: Path, exe_override: Path) -> list[str]:
    sequences = derived_runtime_input_sequences(host_bundle)
    command = [
        sys.executable,
        str(LIVE_SMOKE),
        "--exe-override",
        str(exe_override),
        "--artifact-root",
        str(artifact_root),
        "--timeout-seconds",
        "25",
        "--pre-input-capture-count",
        "1",
        "--focus-before-pre-input-capture",
        "--capture-count",
        "2",
        "--capture-after-each-input-sequence",
        "--after-input-capture-delay-ms",
        "500",
        "--capture-interval-seconds",
        "1",
        "--post-window-delay-seconds",
        "2",
    ]
    for sequence in sequences:
        command.extend(["--input-sequence", sequence])
    command.extend(
        [
            "--level-id",
            "850",
            "--controller-configuration",
            "1",
            "--persist-controller-config-in-options",
            "--bind-forward-qe-for-input-isolation",
            "--enable-cdb-observer",
            "--arm-cdb-observer",
            delivery.state_delta.CDB_OBSERVER_ARM_PHRASE if hasattr(delivery.state_delta, "CDB_OBSERVER_ARM_PHRASE") else "ATTACH CDB TO SAFE COPY BEA",
            "--cdb-command-file",
            r"tools\runtime-probes\local-multiplayer-level850-input-state-delta-observer.cdb.txt",
            "--cdb-log-ready-timeout-ms",
            "30000",
            "--cdb-post-attach-wait-seconds",
            "2",
            "--arm-live-bea",
            "LAUNCH SAFE COPY BEA",
        ]
    )
    return command


def command_hash(command: list[str]) -> str:
    return hashlib.sha256(json.dumps(command, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def run_live_smoke_process(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = minimal_child_env()
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        stdout, stderr = process.communicate(timeout=LIVE_EXECUTOR_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], cwd=ROOT, text=True, capture_output=True, check=False, env=env)
        process.kill()
        stdout, stderr = process.communicate()
        raise HostAuthorityRuntimeExecutorError(
            f"live smoke timed out after {LIVE_EXECUTOR_TIMEOUT_SECONDS}s and process tree was killed: {stdout}\n{stderr}"
        ) from exc
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def created_file_receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "mtimeUtc": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(),
        "sha256": sha256_file(path),
    }


def build_live_executor_proof(host_path: Path, artifact_root: Path, *, exe_override: Path) -> dict[str, Any]:
    artifact_root = require_private_proof_path(artifact_root)
    host_path = host_path.resolve()
    exe_override = exe_override.resolve()
    require(exe_override.is_file(), f"executable override not found: {exe_override}")
    require_no_bea_or_cdb_processes("before live executor")
    host_summary = delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    host_bundle = delivery.host.read_json(host_path)
    command = live_smoke_command(host_bundle, artifact_root=artifact_root, exe_override=exe_override)
    child_env = minimal_child_env()
    started_at = dt.datetime.now(dt.timezone.utc)
    completed = run_live_smoke_process(command)
    ended_at = dt.datetime.now(dt.timezone.utc)
    require(completed.returncode == 0, f"live smoke failed with {completed.returncode}: {completed.stdout}\n{completed.stderr}")
    runtime_path = artifact_root / ("live-safe-copy-runtime-" + "smoke.json")
    require(runtime_path.is_file(), f"live runtime artifact was not created: {runtime_path}")
    delivery_path = artifact_root / "host-authority-runtime-delivery-proof.json"
    delivery.build_bundle(host_path, runtime_path, delivery_path, enforce_private_output=True)
    output_path = artifact_root / "host-authority-runtime-executor-proof.json"
    require_no_bea_or_cdb_processes("after live executor")
    receipt = {
        "mode": "live-executor-subprocess",
        "artifactRoot": str(artifact_root),
        "startedAtUtc": started_at.isoformat(),
        "endedAtUtc": ended_at.isoformat(),
        "liveSmokeCommandSha256": command_hash(command),
        "liveSmokeReturnCode": completed.returncode,
        "runtimeDeliveryBuildReturnCode": 0,
        "childEnvKeyCount": len(child_env),
        "childEnvSensitiveKeyCount": len(sensitive_env_keys(child_env)),
        "childEnvSensitiveKeys": sensitive_env_keys(child_env),
        "executorRecordsFreshSameRootArtifacts": runtime_path.parent.resolve() == artifact_root.resolve() and delivery_path.parent.resolve() == artifact_root.resolve(),
        "createdFiles": {
            "liveRuntimeArtifact": created_file_receipt(runtime_path),
            "runtimeDeliveryProofBundle": created_file_receipt(delivery_path),
        },
        "stdoutSha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stderrSha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
    }
    return make_executor_proof(host_path, runtime_path, delivery_path, output_path, host_summary=host_summary, execution_receipt=receipt)


def make_executor_fixture(root: Path, *, wrong_runtime_sequence: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    host_path = delivery.host.make_bundle_fixture(root / "host-authority")
    artifact_root = root / "executor-root"
    artifact_root.mkdir(parents=True, exist_ok=True)
    runtime_path = delivery.state_delta.make_artifact(
        artifact_root,
        controller_configuration=1,
        qe_proof_lever="input-isolation-forward-qe",
    )
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    host_bundle = delivery.host.read_json(host_path)
    runtime["source"]["overrideHashBefore"] = host_bundle["sessionDescriptor"]["cleanSpecimenSha256"]
    if wrong_runtime_sequence:
        runtime["inputCdbWindows"][1]["sequence"] = "down:O,wait:500,up:O"
    runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
    delivery_path = artifact_root / "host-authority-runtime-delivery-proof.json"
    delivery.build_bundle(host_path, runtime_path, delivery_path)
    output_path = artifact_root / "host-authority-runtime-executor-proof.json"
    make_executor_proof(host_path, runtime_path, delivery_path, output_path)
    return output_path


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(dir=PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_executor_proof(make_executor_fixture(Path(tmp)))
        require(summary["deliveredOriginalBinaryCommandCount"] == 2, "fixture must deliver two commands")

    with tempfile.TemporaryDirectory(dir=PRIVATE_PROOF_ROOT) as tmp:
        try:
            make_executor_fixture(Path(tmp), wrong_runtime_sequence=True)
        except (HostAuthorityRuntimeExecutorError, delivery.HostAuthorityRuntimeDeliveryError, delivery.state_delta.ArtifactError):
            pass
        else:
            raise AssertionError("wrong runtime sequence should fail executor proof")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--build-live-from-host-authority", type=Path, default=None)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--exe-override", type=Path, default=DEFAULT_EXE_OVERRIDE)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary host-authority runtime executor checker self-test: PASS")
        return 0
    if args.build_live_from_host_authority is not None:
        if args.artifact_root is None:
            raise SystemExit("--artifact-root is required with --build-live-from-host-authority")
        print(json.dumps(build_live_executor_proof(args.build_live_from_host_authority, args.artifact_root, exe_override=args.exe_override), indent=2, sort_keys=True))
        return 0
    if args.proof is None:
        raise SystemExit("proof is required unless --self-test or --build-live-from-host-authority is used")
    print(json.dumps(validate_executor_proof(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityRuntimeExecutorError,
        delivery.HostAuthorityRuntimeDeliveryError,
        delivery.host.HostAuthorityTwoClientSmokeProofError,
        delivery.host.remote.PrivateRemoteClientSmokeProofError,
        delivery.host.remote.lan.PrivateTransportSmokeProofError,
        delivery.host.remote.lan.delivery.PrivateRelayDeliveryProofError,
        delivery.host.remote.lan.delivery.relay.RelayProofError,
        delivery.host.remote.lan.delivery.loopback.LoopbackProofError,
        delivery.state_delta.ArtifactError,
        delivery.nslot.NSlotSessionSchemaError,
    ) as exc:
        print(f"WinUI original-binary host-authority runtime executor check: FAIL: {exc}")
        raise SystemExit(2)
