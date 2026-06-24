#!/usr/bin/env python3
"""Validate repeated host-authority delivery into copied BEA runtime artifacts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_runtime_delivery_check as delivery


EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_runtime_delivery_replayability_check.py --self-test"


class HostAuthorityRuntimeDeliveryReplayabilityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityRuntimeDeliveryReplayabilityError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def live_runtime_path(bundle_path: Path, bundle: dict[str, Any]) -> Path:
    return delivery.resolve_path(bundle_path, str(bundle.get("liveRuntimeArtifact", "")))


def runtime_identity(runtime_summary: dict[str, Any]) -> tuple[Any, ...]:
    strict = runtime_summary.get("strictStateProof")
    require(isinstance(strict, dict), "runtime summary missing strictStateProof")
    windows = strict.get("windows")
    require(isinstance(windows, list) and len(windows) == 2, "runtime summary must include two strict windows")
    by_sequence = {str(row.get("sequence")): row for row in windows if isinstance(row, dict)}
    q = by_sequence.get(delivery.host.EXPECTED_P1_SEQUENCE)
    e = by_sequence.get(delivery.host.EXPECTED_P2_SEQUENCE)
    require(isinstance(q, dict), "runtime summary missing P1/Q strict window")
    require(isinstance(e, dict), "runtime summary missing P2/E strict window")
    return (
        runtime_summary.get("p0"),
        runtime_summary.get("p1"),
        q.get("controller"),
        e.get("controller"),
        q.get("battleEngine"),
        e.get("battleEngine"),
        q.get("walker"),
        e.get("walker"),
    )


def runtime_process_and_log(runtime_path: Path) -> tuple[Any, str]:
    artifact = delivery.state_delta.read_json(runtime_path)
    launch = artifact.get("launch") if isinstance(artifact.get("launch"), dict) else {}
    observer = artifact.get("cdbObserver") if isinstance(artifact.get("cdbObserver"), dict) else {}
    result = observer.get("result") if isinstance(observer.get("result"), dict) else {}
    process_id = launch.get("processId")
    log_path = str(result.get("logPath") or observer.get("logPath") or "")
    require(isinstance(process_id, int) and process_id > 0, f"{runtime_path} missing launch process id")
    require(log_path, f"{runtime_path} missing CDB log path")
    return process_id, log_path


def require_delivery_row_invariants(bundle_path: Path, bundle: dict[str, Any], runtime_summary: dict[str, Any]) -> None:
    delivery_body = bundle.get("delivery")
    require(isinstance(delivery_body, dict), f"{bundle_path} missing delivery object")
    rows = delivery_body.get("deliveredCommands")
    require(isinstance(rows, list) and len(rows) == 2, f"{bundle_path} must contain P1/P2 delivered rows")
    by_slot = {str(row.get("clientSlot")): row for row in rows if isinstance(row, dict)}
    require(set(by_slot) == {"P1", "P2"}, f"{bundle_path} delivered rows must cover P1/P2")
    expected = {
        "P1": (delivery.host.EXPECTED_P1_COMMAND_ID, delivery.host.EXPECTED_P1_SEQUENCE, 0, runtime_summary["p0"]),
        "P2": (delivery.host.EXPECTED_P2_COMMAND_ID, delivery.host.EXPECTED_P2_SEQUENCE, 1, runtime_summary["p1"]),
    }
    for slot, (command_id, sequence, input_device, player) in expected.items():
        row = by_slot[slot]
        require(row.get("commandId") == command_id, f"{bundle_path} {slot} command id mismatch")
        require(row.get("mappedInputSequence") == sequence, f"{bundle_path} {slot} sequence mismatch")
        require(row.get("inputDevice") == input_device, f"{bundle_path} {slot} input device mismatch")
        require(row.get("runtimePlayer") == player, f"{bundle_path} {slot} runtime player mismatch")
        require(row.get("hostAcceptedByScheduler") is True, f"{bundle_path} {slot} scheduler acceptance missing")
        require(row.get("hostHelperInputSent") is True, f"{bundle_path} {slot} host helper delivery missing")
        require(int(row.get("button31ReceiveRows", 0)) > 0, f"{bundle_path} {slot} lacks button receive rows")
        require(int(row.get("forwardStateStoreRows", 0)) > 0, f"{bundle_path} {slot} lacks forward state-store rows")


def validate_bundles(paths: list[Path]) -> dict[str, Any]:
    require(len(paths) >= 2, "at least two runtime-delivery bundles are required for replayability")
    resolved_paths = [path.resolve() for path in paths]
    require(len(set(resolved_paths)) == len(resolved_paths), "bundle paths must be distinct")

    relay_hashes: set[str] = set()
    n_slot_hashes: set[str] = set()
    runtime_paths: set[Path] = set()
    runtime_hashes: set[str] = set()
    runtime_identities: set[tuple[Any, ...]] = set()
    process_ids: set[Any] = set()
    cdb_logs: set[str] = set()
    artifacts: list[dict[str, Any]] = []

    for path in resolved_paths:
        summary = delivery.validate_bundle(path)
        bundle = read_json(path)
        runtime_path = live_runtime_path(path, bundle)
        runtime_summary = delivery.state_delta.validate_artifact(
            runtime_path,
            min_capture_count=1,
            expected_controller_configuration=1,
            expected_qe_proof_lever="input-isolation-forward-qe",
        )
        require_delivery_row_invariants(path, bundle, runtime_summary)
        identity = runtime_identity(runtime_summary)
        process_id, log_path = runtime_process_and_log(runtime_path)
        runtime_hash = str(bundle.get("liveRuntimeArtifactSha256") or "")

        require(runtime_path not in runtime_paths, f"{path} repeats a live runtime artifact path")
        runtime_paths.add(runtime_path)
        require(runtime_hash and runtime_hash not in runtime_hashes, f"{path} repeats a live runtime artifact hash")
        runtime_hashes.add(runtime_hash)
        require(identity not in runtime_identities, f"{path} repeats a runtime player/controller/BattleEngine/Walker tuple")
        runtime_identities.add(identity)
        require(process_id not in process_ids, f"{path} repeats a launch process id")
        process_ids.add(process_id)
        require(log_path not in cdb_logs, f"{path} repeats a CDB log path")
        cdb_logs.add(log_path)

        relay_hashes.add(summary["hostAuthorityRelayPlanSha256"])
        n_slot_hashes.add(summary["nSlotRelayPlanSha256"])
        require(summary["deliveredOriginalBinaryCommandCount"] == 2, f"{path} must deliver two P1/P2 commands")
        require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, f"{path} must not claim N-player original-binary runtime proof")
        artifacts.append(
            {
                "artifact": str(path),
                "liveRuntimeArtifact": str(runtime_path),
                "liveRuntimeArtifactSha256": runtime_hash,
                "processId": process_id,
                "cdbLogPath": log_path,
                "visualCaptureCount": summary["visualCaptureCount"],
                "runtimePlayers": summary["runtimePlayers"],
                "deliveredCommandIds": summary["deliveredCommandIds"],
            }
        )

    require(len(relay_hashes) == 1, "all runs must use the same deterministic host-authority relay plan hash")
    require(len(n_slot_hashes) == 1, "all runs must use the same N-slot design relay hash")
    return {
        "claim": "repeated same-workstation host-authority P1/P2 scheduler-to-host-helper delivery into copied original-BEA runtime artifacts",
        "bundleCount": len(artifacts),
        "controllerConfiguration": 1,
        "deliveredOriginalBinaryCommandCountPerBundle": 2,
        "hostAuthorityRelayPlanSha256": next(iter(relay_hashes)),
        "nSlotRelayPlanSha256": next(iter(n_slot_hashes)),
        "roleInvariant": "P1 -> Q -> inputDevice0/top split half; P2 -> E -> inputDevice1/bottom split half",
        "artifacts": artifacts,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "claimBoundary": (
            "This proves the accepted host-authority P1/P2 scheduler relay plan can be delivered through the safe-copy "
            "host-helper input path across distinct copied original-BEA level-850/config-1 runtime artifacts with distinct "
            "process IDs, CDB logs, runtime player/controller/BattleEngine/Walker tuples, and live artifact hashes. It does "
            "not prove more than two original-binary runtime players, active P3/P4 gameplay, co-op/versus online semantics, "
            "multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, "
            "physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def replace_fixture_pointers(path: Path, replacements: dict[str, str]) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    observer = artifact["cdbObserver"]
    result = observer["result"]
    log_path = Path(result["logPath"])
    log_text = log_path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        log_text = log_text.replace(old, new)
    log_path.write_text(log_text, encoding="utf-8")


def set_fixture_process_id(path: Path, process_id: int) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["launch"]["processId"] = process_id
    artifact["cdbObserver"]["result"]["targetProcessId"] = process_id
    path.write_text(json.dumps(artifact), encoding="utf-8")


def make_runtime_fixture(root: Path, *, distinct: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    runtime_path = delivery.state_delta.make_artifact(
        root,
        controller_configuration=1,
        qe_proof_lever="input-isolation-forward-qe",
    )
    if distinct:
        replace_fixture_pointers(
            runtime_path,
            {
                "04646090": "04aa0090",
                "0465d890": "04bb8890",
                "046460f0": "04aa00f0",
                "0465d8f0": "04bb88f0",
                "03867570": "07aa7570",
                "0386d570": "07bbd570",
                "04700010": "04cc0010",
                "04710010": "04dd0010",
            },
        )
        set_fixture_process_id(runtime_path, 5678)
    return runtime_path


def make_bundle_fixture(root: Path, *, duplicate_runtime: bool = False) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    host_path = delivery.host.make_bundle_fixture(root / "host-authority")
    first_runtime = make_runtime_fixture(root / "first-runtime")
    second_runtime = first_runtime if duplicate_runtime else make_runtime_fixture(root / "second-runtime", distinct=True)
    first_bundle = root / "first" / "host-authority-runtime-delivery-proof.json"
    second_bundle = root / "second" / "host-authority-runtime-delivery-proof.json"
    delivery.build_bundle(host_path, first_runtime, first_bundle)
    delivery.build_bundle(host_path, second_runtime, second_bundle)
    return [first_bundle, second_bundle]


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_bundles(make_bundle_fixture(Path(tmp)))
        require(summary["bundleCount"] == 2, "expected two replayability bundles")
        require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "self-test must keep N-player proof at zero")

    with tempfile.TemporaryDirectory() as tmp:
        paths = make_bundle_fixture(Path(tmp))
        try:
            validate_bundles([paths[0], paths[0]])
        except HostAuthorityRuntimeDeliveryReplayabilityError:
            pass
        else:
            raise AssertionError("duplicate bundle path should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            validate_bundles(make_bundle_fixture(Path(tmp), duplicate_runtime=True))
        except HostAuthorityRuntimeDeliveryReplayabilityError:
            pass
        else:
            raise AssertionError("duplicate live runtime artifact should fail replayability")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundles", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary host-authority runtime-delivery replayability checker self-test: PASS")
        return 0
    print(json.dumps(validate_bundles(args.bundles), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityRuntimeDeliveryReplayabilityError,
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
        print(f"WinUI original-binary host-authority runtime-delivery replayability check: FAIL: {exc}")
        raise SystemExit(2)
