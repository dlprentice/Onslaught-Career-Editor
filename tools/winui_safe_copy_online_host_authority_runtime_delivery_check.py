#!/usr/bin/env python3
"""Validate host-authority scheduler delivery into a copied BEA runtime artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_input_state_delta_check as state_delta
import winui_safe_copy_online_host_authority_two_client_smoke_check as host
import winui_safe_copy_online_n_slot_session_schema_check as nslot


ROOT = Path(__file__).resolve().parents[1]
N_SLOT_CONTRACT = ROOT / "roadmap" / "original-binary-online-n-slot-session-schema.v1.json"
PRIVATE_PROOF_ROOT = ROOT / "subagents" / "winui-safe-copy-live-runtime"

EXPECTED_SCHEMA = "winui-original-binary-host-authority-runtime-delivery.v1"
EXPECTED_PROTOCOL = "host-authority-runtime-delivery.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-runtime-delivery-helper"
EXPECTED_HELPER_VERSION = "host-authority-runtime-delivery-helper.v1"
EXPECTED_DELIVERY_MODE = "host-authority-deterministic-p1-p2-relay-plan-to-safe-copy-host-helper"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_runtime_delivery_check.py --self-test"


class HostAuthorityRuntimeDeliveryError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityRuntimeDeliveryError(message)


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


def resolve_path(bundle_path: Path, raw_path: str, *, repo_relative: bool = False) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = (ROOT if repo_relative else bundle_path.parent) / candidate
    candidate = candidate.resolve()
    require(candidate.is_file(), f"referenced file is missing: {candidate}")
    return candidate


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def require_private_proof_output(path: Path) -> None:
    output = path.resolve()
    root = PRIVATE_PROOF_ROOT.resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise HostAuthorityRuntimeDeliveryError(
            f"output path must stay under ignored private proof root: {root}"
        ) from exc


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


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected runtime delivery schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected runtime delivery helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected runtime delivery helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected runtime delivery protocol")


def require_references(bundle: dict[str, Any], bundle_path: Path) -> tuple[Path, dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]:
    host_path = resolve_path(bundle_path, str(bundle.get("hostAuthorityTwoClientProofBundle", "")))
    require(bundle.get("hostAuthorityTwoClientProofSha256") == sha256_file(host_path), "host-authority proof hash mismatch")
    host_summary = host.validate_bundle(host_path, expected_controller_configuration=1)

    runtime_path = resolve_path(bundle_path, str(bundle.get("liveRuntimeArtifact", "")))
    require(bundle.get("liveRuntimeArtifactSha256") == sha256_file(runtime_path), "live runtime artifact hash mismatch")
    runtime_summary = state_delta.validate_artifact(
        runtime_path,
        min_capture_count=1,
        expected_controller_configuration=1,
        expected_qe_proof_lever="input-isolation-forward-qe",
    )

    n_slot_path = resolve_path(bundle_path, str(bundle.get("nSlotSessionSchemaPath", "")), repo_relative=True)
    require(n_slot_path == N_SLOT_CONTRACT.resolve(), "N-slot schema path must be the canonical repo contract")
    require(bundle.get("nSlotSessionSchemaSha256") == sha256_file(n_slot_path), "N-slot schema hash mismatch")
    n_slot_summary = nslot.validate_contract(n_slot_path)
    return host_path, host_summary, runtime_path, runtime_summary, n_slot_path, n_slot_summary


def require_delivery(bundle: dict[str, Any], *, host_summary: dict[str, Any], runtime_summary: dict[str, Any], n_slot_summary: dict[str, Any]) -> dict[str, Any]:
    delivery = object_at(bundle, "delivery")
    require(delivery.get("deliveryMode") == EXPECTED_DELIVERY_MODE, "delivery mode mismatch")
    require(delivery.get("sourceHostAuthorityProtocolVersion") == host.EXPECTED_PROTOCOL, "host-authority protocol mismatch")
    require(delivery.get("runtimeArtifactSchema") == state_delta.EXPECTED_SCHEMA, "runtime artifact schema mismatch")
    require(delivery.get("hostAuthorityAcceptedCommandCount") == 2, "host-authority accepted count must stay two")
    require(set(delivery.get("hostAuthorityAcceptedCommandIds", [])) == {host.EXPECTED_P1_COMMAND_ID, host.EXPECTED_P2_COMMAND_ID}, "accepted command ids mismatch")
    require(delivery.get("deterministicScheduleOrder") == ["P1", "P2"], "deterministic schedule order mismatch")
    require(delivery.get("hostAuthorityRelayPlanSha256") == host_summary["relayPlanSha256"], "host relay plan hash mismatch")
    require(delivery.get("runtimeInputWindowCount") == 4, "runtime input window count mismatch")
    require(delivery.get("visualCaptureCount") == runtime_summary["visualCaptureCount"], "visual capture count mismatch")
    require(delivery.get("deliveredOriginalBinaryCommandCount") == 2, "expected two delivered original-binary commands")
    require(delivery.get("gameInputSentByScheduler") is False, "scheduler must not claim direct game input")
    require(delivery.get("hostHelperInputSent") is True, "host-helper delivery must be true for this proof")
    require(delivery.get("bridgeSendsNewNetworkInput") is False, "bridge must not claim new network input")
    require(delivery.get("newBeaLaunchCount") == 1, "this proof must account for one copied BEA launch")
    require(delivery.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(delivery.get("moreThanTwoOriginalBinaryRuntimeProof") is False, "more-than-two runtime proof must stay false")
    require(delivery.get("coOpVersusModeRuntimeProofSlices") == 0, "co-op/versus runtime proof must stay zero")
    require(delivery.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slot list mismatch")
    require(delivery.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected gameplay route slots mismatch")
    require(delivery.get("p3p4GameplayInputRejected") is True, "P3/P4 gameplay rejection must remain explicit")
    require(delivery.get("nSlotRelayPlanSha256") == n_slot_summary["relayPlanSha256"], "N-slot relay plan hash mismatch")

    proof = object_at(runtime_summary, "strictStateProof")
    windows = list_at(proof, "windows")
    require(len(windows) == 2, "runtime strict proof must contain P1 and P2 windows")
    by_sequence = {str(row.get("sequence")): row for row in windows if isinstance(row, dict)}
    require(host.EXPECTED_P1_SEQUENCE in by_sequence, "missing P1 Q runtime window")
    require(host.EXPECTED_P2_SEQUENCE in by_sequence, "missing P2 E runtime window")

    delivered = list_at(delivery, "deliveredCommands")
    require(len(delivered) == 2, "expected two delivered command rows")
    by_slot = {str(row.get("clientSlot")): row for row in delivered if isinstance(row, dict)}
    require(set(by_slot) == {"P1", "P2"}, "delivered rows must cover P1/P2")
    expected = {
        "P1": (host.EXPECTED_P1_COMMAND_ID, host.EXPECTED_P1_SEQUENCE, 0, runtime_summary["p0"], by_sequence[host.EXPECTED_P1_SEQUENCE]),
        "P2": (host.EXPECTED_P2_COMMAND_ID, host.EXPECTED_P2_SEQUENCE, 1, runtime_summary["p1"], by_sequence[host.EXPECTED_P2_SEQUENCE]),
    }
    for slot, (command_id, sequence, input_device, player, window) in expected.items():
        row = by_slot[slot]
        require(row.get("commandId") == command_id, f"{slot} command id mismatch")
        require(row.get("mappedInputSequence") == sequence, f"{slot} sequence mismatch")
        require(row.get("inputDevice") == input_device, f"{slot} input device mismatch")
        require(row.get("runtimePlayer") == player, f"{slot} runtime player mismatch")
        require(row.get("runtimeRouteType") == window["routeType"], f"{slot} route type mismatch")
        require(row.get("button31ReceiveRows") == window["button31ReceiveRows"], f"{slot} button receive count mismatch")
        require(row.get("forwardStateStoreRows") == window["forwardStateStoreRows"], f"{slot} forward store count mismatch")
        require(row.get("hostAcceptedByScheduler") is True, f"{slot} scheduler acceptance must be true")
        require(row.get("hostHelperInputSent") is True, f"{slot} host-helper delivery must be true")

    rejected = list_at(delivery, "rejectedGameplayRows")
    reasons = {(str(row.get("clientSlot")), str(row.get("reason"))) for row in rejected if isinstance(row, dict)}
    for expected_reason in (
        ("P3", "required-for-unproven-original-binary-slots"),
        ("P4", "required-for-unproven-original-binary-slots"),
        ("P2", "public-matchmaking-not-allowed"),
        ("P1", "direct-input-not-allowed"),
    ):
        require(expected_reason in reasons, f"missing rejected gameplay row: {expected_reason}")
    for row in rejected:
        require(isinstance(row, dict), "rejected row must be an object")
        require(row.get("hostAcceptedByScheduler") is False, "rejected row must not be scheduler-accepted")
        require(row.get("hostHelperInputSent") is False, "rejected row must not send host-helper input")

    for key in (
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "publicServerClaim",
        "nativeBeaNetcodeClaim",
        "natTraversalClaim",
        "deterministicSyncClaim",
        "rollbackClaim",
        "antiCheatClaim",
        "physicalGamepadClaim",
        "rebuildParityClaim",
        "noNoticeableDifferenceClaim",
    ):
        require(delivery.get(key) is False, f"delivery overclaim must be false: {key}")
    return delivery


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    host_path, host_summary, runtime_path, runtime_summary, n_slot_path, n_slot_summary = require_references(bundle, path)
    delivery = require_delivery(bundle, host_summary=host_summary, runtime_summary=runtime_summary, n_slot_summary=n_slot_summary)
    return {
        "artifact": str(path),
        "hostAuthorityTwoClientProofBundle": str(host_path),
        "liveRuntimeArtifact": str(runtime_path),
        "nSlotSessionSchemaPath": str(n_slot_path),
        "claim": "same-workstation host-authority P1/P2 scheduler plan delivered into one copied BEA host-helper runtime artifact",
        "protocolVersion": bundle["protocolVersion"],
        "helperVersion": bundle["helperVersion"],
        "controllerConfiguration": runtime_summary["controllerConfiguration"],
        "launchArguments": runtime_summary["launchArguments"],
        "visualCaptureCount": delivery["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": delivery["deliveredOriginalBinaryCommandCount"],
        "deliveredCommandIds": [row["commandId"] for row in delivery["deliveredCommands"]],
        "runtimePlayers": {
            "P1": delivery["deliveredCommands"][0]["runtimePlayer"],
            "P2": delivery["deliveredCommands"][1]["runtimePlayer"],
        },
        "hostAuthorityRelayPlanSha256": delivery["hostAuthorityRelayPlanSha256"],
        "nSlotRelayPlanSha256": delivery["nSlotRelayPlanSha256"],
        "nPlayerOriginalBinaryRuntimeProof": delivery["nPlayerOriginalBinaryRuntimeProof"],
        "claimBoundary": (
            "This proves one same-workstation host-authority P1/P2 relay plan was executed through the safe-copy "
            "host-helper input path into a copied original-BEA level-850 split-screen session with exact-PID CDB state "
            "evidence. It does not prove more than two original-binary runtime players, co-op/versus online modes, "
            "multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, "
            "physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def build_bundle(
    host_authority_proof_path: Path,
    live_runtime_artifact_path: Path,
    output_path: Path,
    *,
    enforce_private_output: bool = False,
) -> dict[str, Any]:
    host_authority_proof_path = host_authority_proof_path.resolve()
    live_runtime_artifact_path = live_runtime_artifact_path.resolve()
    output_path = output_path.resolve()
    if enforce_private_output:
        require_private_proof_output(output_path)
    host_summary = host.validate_bundle(host_authority_proof_path, expected_controller_configuration=1)
    runtime_summary = state_delta.validate_artifact(
        live_runtime_artifact_path,
        min_capture_count=1,
        expected_controller_configuration=1,
        expected_qe_proof_lever="input-isolation-forward-qe",
    )
    n_slot_summary = nslot.validate_contract(N_SLOT_CONTRACT)
    strict_windows = {row["sequence"]: row for row in runtime_summary["strictStateProof"]["windows"]}
    delivered = [
        {
            "commandId": host.EXPECTED_P1_COMMAND_ID,
            "clientSlot": "P1",
            "mappedInputSequence": host.EXPECTED_P1_SEQUENCE,
            "runtimeRoute": "P1/inputDevice0/top-split-half",
            "inputDevice": 0,
            "runtimePlayer": runtime_summary["p0"],
            "runtimeRouteType": strict_windows[host.EXPECTED_P1_SEQUENCE]["routeType"],
            "button31ReceiveRows": strict_windows[host.EXPECTED_P1_SEQUENCE]["button31ReceiveRows"],
            "forwardStateStoreRows": strict_windows[host.EXPECTED_P1_SEQUENCE]["forwardStateStoreRows"],
            "hostAcceptedByScheduler": True,
            "hostHelperInputSent": True,
        },
        {
            "commandId": host.EXPECTED_P2_COMMAND_ID,
            "clientSlot": "P2",
            "mappedInputSequence": host.EXPECTED_P2_SEQUENCE,
            "runtimeRoute": "P2/inputDevice1/bottom-split-half",
            "inputDevice": 1,
            "runtimePlayer": runtime_summary["p1"],
            "runtimeRouteType": strict_windows[host.EXPECTED_P2_SEQUENCE]["routeType"],
            "button31ReceiveRows": strict_windows[host.EXPECTED_P2_SEQUENCE]["button31ReceiveRows"],
            "forwardStateStoreRows": strict_windows[host.EXPECTED_P2_SEQUENCE]["forwardStateStoreRows"],
            "hostAcceptedByScheduler": True,
            "hostHelperInputSent": True,
        },
    ]
    delivery = {
        "deliveryMode": EXPECTED_DELIVERY_MODE,
        "sourceHostAuthorityProtocolVersion": host.EXPECTED_PROTOCOL,
        "runtimeArtifactSchema": state_delta.EXPECTED_SCHEMA,
        "hostAuthorityAcceptedCommandCount": 2,
        "hostAuthorityAcceptedCommandIds": host_summary["acceptedCommandIds"],
        "deterministicScheduleOrder": host_summary["deterministicScheduleOrder"],
        "hostAuthorityRelayPlanSha256": host_summary["relayPlanSha256"],
        "runtimeInputWindowCount": 4,
        "visualCaptureCount": runtime_summary["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": 2,
        "deliveredCommands": delivered,
        "rejectedGameplayRows": [
            {
                "commandId": "host-authority-p3-forward-0001",
                "clientSlot": "P3",
                "reason": "required-for-unproven-original-binary-slots",
                "hostAcceptedByScheduler": False,
                "hostHelperInputSent": False,
            },
            {
                "commandId": "host-authority-p4-forward-0001",
                "clientSlot": "P4",
                "reason": "required-for-unproven-original-binary-slots",
                "hostAcceptedByScheduler": False,
                "hostHelperInputSent": False,
            },
            {
                "commandId": "host-authority-public-matchmaking-claim-0001",
                "clientSlot": "P2",
                "reason": "public-matchmaking-not-allowed",
                "hostAcceptedByScheduler": False,
                "hostHelperInputSent": False,
            },
            {
                "commandId": "host-authority-direct-input-claim-0001",
                "clientSlot": "P1",
                "reason": "direct-input-not-allowed",
                "hostAcceptedByScheduler": False,
                "hostHelperInputSent": False,
            },
        ],
        "gameInputSentByScheduler": False,
        "hostHelperInputSent": True,
        "bridgeSendsNewNetworkInput": False,
        "newBeaLaunchCount": 1,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "moreThanTwoOriginalBinaryRuntimeProof": False,
        "coOpVersusModeRuntimeProofSlices": 0,
        "metadataOnlySlots": ["P3", "P4"],
        "rejectedGameplayRouteSlots": ["P3", "P4"],
        "p3p4GameplayInputRejected": True,
        "nSlotRelayPlanSha256": n_slot_summary["relayPlanSha256"],
        "multiHostLanClaim": False,
        "publicMatchmakingClaim": False,
        "publicServerClaim": False,
        "nativeBeaNetcodeClaim": False,
        "natTraversalClaim": False,
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
        "hostAuthorityTwoClientProofBundle": relative_path(output_path.parent, host_authority_proof_path),
        "hostAuthorityTwoClientProofSha256": sha256_file(host_authority_proof_path),
        "liveRuntimeArtifact": relative_path(output_path.parent, live_runtime_artifact_path),
        "liveRuntimeArtifactSha256": sha256_file(live_runtime_artifact_path),
        "nSlotSessionSchemaPath": "roadmap/original-binary-online-n-slot-session-schema.v1.json",
        "nSlotSessionSchemaSha256": sha256_file(N_SLOT_CONTRACT),
        "delivery": delivery,
        "claimBoundary": (
            "Host-authority runtime delivery proof for P1/P2 only. This uses one copied original-BEA level-850/config-1 "
            "runtime artifact with exact-PID CDB state evidence. P3/P4 remain metadata-only/rejected original-binary "
            "gameplay slots, and no multi-host LAN/public/native-netcode/deterministic-sync claim is made."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    summary = validate_bundle(output_path)
    return {"bundle": str(output_path), "summary": summary}


def make_bundle_fixture(root: Path, *, p3_runtime_claim: bool = False, scheduler_input_claim: bool = False, missing_delivery: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    host_path = host.make_bundle_fixture(root / "host-authority")
    (root / "runtime").mkdir(parents=True, exist_ok=True)
    runtime_path = state_delta.make_artifact(
        root / "runtime",
        controller_configuration=1,
        qe_proof_lever="input-isolation-forward-qe",
    )
    output = root / "host-authority-runtime-delivery-proof.json"
    build_bundle(host_path, runtime_path, output)
    bundle = read_json(output)
    if p3_runtime_claim:
        bundle["delivery"]["moreThanTwoOriginalBinaryRuntimeProof"] = True
        bundle["delivery"]["nPlayerOriginalBinaryRuntimeProof"] = 1
    if scheduler_input_claim:
        bundle["delivery"]["gameInputSentByScheduler"] = True
    if missing_delivery:
        bundle["delivery"]["deliveredCommands"] = bundle["delivery"]["deliveredCommands"][:1]
        bundle["delivery"]["deliveredOriginalBinaryCommandCount"] = 1
    output.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return output


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        summary = validate_bundle(make_bundle_fixture(Path(tmp)))
        require(summary["deliveredOriginalBinaryCommandCount"] == 2, "fixture should deliver P1/P2")
    for label, kwargs in (
        ("P3 runtime overclaim should fail", {"p3_runtime_claim": True}),
        ("scheduler game-input claim should fail", {"scheduler_input_claim": True}),
        ("missing P2 delivery should fail", {"missing_delivery": True}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), **kwargs))
            except HostAuthorityRuntimeDeliveryError:
                continue
            raise AssertionError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--build-from-host-authority", type=Path, default=None)
    parser.add_argument("--live-runtime-artifact", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary host-authority runtime delivery checker self-test: PASS")
        return 0
    if args.build_from_host_authority is not None:
        if args.live_runtime_artifact is None:
            raise SystemExit("--live-runtime-artifact is required with --build-from-host-authority")
        output = args.output or args.build_from_host_authority.with_name("host-authority-runtime-delivery-proof.json")
        print(json.dumps(build_bundle(args.build_from_host_authority, args.live_runtime_artifact, output, enforce_private_output=True), indent=2, sort_keys=True))
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test or --build-from-host-authority is used")
    print(json.dumps(validate_bundle(args.bundle), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityRuntimeDeliveryError,
        host.HostAuthorityTwoClientSmokeProofError,
        host.remote.PrivateRemoteClientSmokeProofError,
        host.remote.lan.PrivateTransportSmokeProofError,
        host.remote.lan.delivery.PrivateRelayDeliveryProofError,
        host.remote.lan.delivery.relay.RelayProofError,
        host.remote.lan.delivery.loopback.LoopbackProofError,
        state_delta.ArtifactError,
        nslot.NSlotSessionSchemaError,
    ) as exc:
        print(f"WinUI original-binary host-authority runtime delivery check: FAIL: {exc}")
        raise SystemExit(2)
