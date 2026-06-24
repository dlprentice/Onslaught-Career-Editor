#!/usr/bin/env python3
"""Validate host-authority N-slot runtime bridge state-authority graph evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_input_state_delta_check as state_delta
import winui_safe_copy_local_multiplayer_movement_state_delta_check as movement
import winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check as nslot_bridge


EXPECTED_SCHEMA = "winui-original-binary-host-authority-state-authority-observer.v1"
EXPECTED_PROTOCOL = "host-authority-state-authority-observer.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-state-authority-observer"
EXPECTED_HELPER_VERSION = "host-authority-state-authority-observer.v1"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_host_authority_state_authority_observer_check.py --self-test"
EXPECTED_BRIDGE_SCHEMA = "winui-original-binary-host-authority-n-slot-runtime-bridge.v1"
EXPECTED_QE_PROOF_LEVER = "input-isolation-forward-qe"
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
PRIVATE_PROOF_ROOT = nslot_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT


class HostAuthorityStateAuthorityObserverError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityStateAuthorityObserverError(message)


def require_private_proof_path(path: Path) -> Path:
    resolved = path.resolve()
    root = PRIVATE_PROOF_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise HostAuthorityStateAuthorityObserverError(
            f"state-authority proof/source must stay under ignored private proof root: {root}"
        ) from exc
    return resolved


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def nonzero_hex(value: Any) -> bool:
    return isinstance(value, str) and state_delta.nonzero_hex(value)


def require_distinct_nonzero(label: str, values: list[str]) -> None:
    require(all(nonzero_hex(value) for value in values), f"{label} contains a null/invalid pointer")
    require(len(set(values)) == len(values), f"{label} pointers are not distinct")


def resolve_bridge_paths(bridge_path: Path) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    bridge_summary = nslot_bridge.validate_live_bridge_proof(bridge_path)
    bridge_proof = nslot_bridge.read_json(bridge_path)
    runtime_path = nslot_bridge.resolve_path(bridge_path, str(bridge_proof.get("liveRuntimeArtifact", "")))
    nslot_path = nslot_bridge.resolve_path(bridge_path, str(bridge_proof.get("nSlotConcurrentProcessProof", "")))
    return bridge_summary, bridge_proof, runtime_path, nslot_path


def strict_window_by_sequence(state_summary: dict[str, Any], sequence: str) -> dict[str, Any]:
    strict = object_at(state_summary, "strictStateProof")
    windows = strict.get("windows")
    require(isinstance(windows, list), "strict state proof windows missing")
    matches = [row for row in windows if isinstance(row, dict) and row.get("sequence") == sequence]
    require(len(matches) == 1, f"expected one strict state window for {sequence}")
    return matches[0]


def public_window_by_index(state_summary: dict[str, Any], index: int) -> dict[str, Any]:
    windows = state_summary.get("windows")
    require(isinstance(windows, list), "window summaries missing")
    matches = [row for row in windows if isinstance(row, dict) and row.get("index") == index]
    require(len(matches) == 1, f"expected one window summary for index {index}")
    return matches[0]


def require_wait_window_clean(row: dict[str, Any]) -> None:
    require(str(row.get("sequence", "")).startswith("wait:"), f"window {row.get('index')} is not a wait window")
    for key in (
        "sendRows",
        "receiveRows",
        "forwardEntryRows",
        "forwardStateStoreRows",
        "jetThrustEntryRows",
        "jetThrustStateStoreRows",
    ):
        require(row.get(key) == 0, f"wait window {row.get('index')} has nonzero {key}")


def route_summary(
    *,
    route: str,
    strict_window: dict[str, Any],
    public_window: dict[str, Any],
    movement_row: dict[str, Any],
    expected_player: str,
    expected_controller_input_device: int,
    expected_battle_engine: str,
    expected_walker: str,
) -> dict[str, Any]:
    require(strict_window.get("player") == expected_player, f"{route} player mismatch")
    require(strict_window.get("inputDevice") == expected_controller_input_device, f"{route} input device mismatch")
    require(strict_window.get("battleEngine") == expected_battle_engine, f"{route} BattleEngine mismatch")
    require(strict_window.get("walker") == expected_walker, f"{route} WalkerPart mismatch")
    require(strict_window.get("routeType") == "walker-forward", f"{route} route is not walker-forward")
    require(strict_window.get("state260") == "00000002", f"{route} state260 was not walker-forward state")
    require(strict_window.get("observedVectorDelta") is True, f"{route} did not observe vector delta")
    require(strict_window.get("button31ReceiveRows", 0) > 0, f"{route} had no button-31 receive rows")
    require(strict_window.get("forwardEntryRows", 0) > 0, f"{route} had no Forward entry rows")
    require(strict_window.get("forwardStateStoreRows", 0) > 0, f"{route} had no Forward state-store rows")
    require(strict_window.get("jetThrustEntryRows") == 0, f"{route} unexpectedly used jet thrust entry")
    require(strict_window.get("jetThrustStateStoreRows") == 0, f"{route} unexpectedly used jet thrust store")
    require(strict_window.get("nonzeroStoredLastMoveYValues") == ["bf800000"], f"{route} stored last-move values mismatch")

    require(public_window.get("sendRows") == strict_window.get("button31ReceiveRows"), f"{route} send row count mismatch")
    require(public_window.get("receiveRows") == strict_window.get("button31ReceiveRows"), f"{route} receive row count mismatch")
    require(public_window.get("forwardEntryRows") == strict_window.get("forwardEntryRows"), f"{route} Forward entry count mismatch")
    require(public_window.get("forwardStateStoreRows") == strict_window.get("forwardStateStoreRows"), f"{route} Forward store count mismatch")
    require(public_window.get("sendControllerConfigurations") == [1], f"{route} controller config mismatch")
    require(public_window.get("sendButton31InputDeviceCounts") == {str(expected_controller_input_device): strict_window["button31ReceiveRows"]}, f"{route} input device count mismatch")
    require(public_window.get("receiveButton31PlayerCounts") == {expected_player: strict_window["button31ReceiveRows"]}, f"{route} receive player count mismatch")
    require(public_window.get("receiveBattleEngines") == [expected_battle_engine], f"{route} receive BattleEngine mismatch")
    require(public_window.get("receiveWalkers") == [expected_walker], f"{route} receive WalkerPart mismatch")

    require(movement_row.get("player") == expected_player, f"{route} movement player mismatch")
    require(movement_row.get("inputDevice") == expected_controller_input_device, f"{route} movement input device mismatch")
    require(movement_row.get("button31ReceiveRows") == strict_window.get("button31ReceiveRows"), f"{route} movement receive count mismatch")
    require(movement_row.get("forwardStateStoreRows") == strict_window.get("forwardStateStoreRows"), f"{route} movement store count mismatch")
    require(movement_row.get("targetPositionChanged") is True, f"{route} target position did not change")
    require(movement_row.get("targetVelocityChanged") is True, f"{route} target velocity did not change")
    require(movement_row.get("targetDiffersFromAdjacentBaseline") is True, f"{route} target did not differ from baseline")

    return {
        "route": route,
        "player": expected_player,
        "controller": strict_window["controller"],
        "inputDevice": expected_controller_input_device,
        "battleEngine": expected_battle_engine,
        "walker": expected_walker,
        "jet": strict_window["jet"],
        "state260": strict_window["state260"],
        "button31ReceiveRows": strict_window["button31ReceiveRows"],
        "forwardEntryRows": strict_window["forwardEntryRows"],
        "forwardStateStoreRows": strict_window["forwardStateStoreRows"],
        "nonzeroStoredLastMoveYValues": strict_window["nonzeroStoredLastMoveYValues"],
        "observedVectorDelta": strict_window["observedVectorDelta"],
        "targetPositionChanged": movement_row["targetPositionChanged"],
        "targetVelocityChanged": movement_row["targetVelocityChanged"],
        "targetDiffersFromAdjacentBaseline": movement_row["targetDiffersFromAdjacentBaseline"],
    }


def validate_state_authority(bridge_path: Path) -> dict[str, Any]:
    bridge_summary, bridge_proof, runtime_path, nslot_path = resolve_bridge_paths(bridge_path)
    state_summary = state_delta.validate_artifact(
        runtime_path,
        min_capture_count=5,
        expected_controller_configuration=1,
        expected_qe_proof_lever=EXPECTED_QE_PROOF_LEVER,
    )
    movement_summary = movement.validate_artifact(
        runtime_path,
        min_capture_count=5,
        min_render_samples=2,
        expected_controller_configuration=1,
        expected_qe_proof_lever=EXPECTED_QE_PROOF_LEVER,
    )

    require(bridge_summary["schemaVersion"] == EXPECTED_BRIDGE_SCHEMA, "source bridge schema mismatch")
    require(bridge_summary["acceptedOriginalBinaryGameplaySlots"] == EXPECTED_ACTIVE_SLOTS, "active slot list mismatch")
    require(bridge_summary["metadataOnlySlots"] == EXPECTED_METADATA_SLOTS, "metadata-only slot list mismatch")
    require(bridge_summary["hostHelperInputSent"] is True, "bridge did not send host-helper input")
    require(bridge_summary["gameInputSentByNSlotScheduler"] is False, "N-slot scheduler direct input must stay false")
    require(bridge_summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "N-player runtime proof must stay zero")
    require(bridge_summary["activeP3P4OriginalBinaryGameplayProof"] is False, "P3/P4 runtime gameplay proof must stay false")
    require(bridge_summary["visualCaptureCount"] == state_summary["visualCaptureCount"] == movement_summary["visualCaptureCount"], "visual capture count mismatch")

    render = object_at(state_summary, "render")
    require(render.get("players") == 2, "host render player count must be 2")
    require(render.get("level") == 850, "host render level must be 850")
    require(render.get("horizSplit") == 1, "host render must report horizontal split")
    require(render.get("p0") == state_summary["p0"], "render P0 pointer mismatch")
    require(render.get("p1") == state_summary["p1"], "render P1 pointer mismatch")
    require(bridge_summary["runtimePlayers"] == {"P1": state_summary["p0"], "P2": state_summary["p1"]}, "bridge runtime players mismatch")
    require_distinct_nonzero("players", [render["p0"], render["p1"]])
    require_distinct_nonzero("BattleEngine parts", [render["p0be"], render["p1be"]])
    require_distinct_nonzero("Walker parts", [render["p0walker"], render["p1walker"]])

    require_wait_window_clean(public_window_by_index(state_summary, 1))
    require_wait_window_clean(public_window_by_index(state_summary, 3))

    q_route = route_summary(
        route="P1/Q",
        strict_window=strict_window_by_sequence(state_summary, "down:Q,wait:500,up:Q"),
        public_window=public_window_by_index(state_summary, 2),
        movement_row=object_at(movement_summary, "q"),
        expected_player=render["p0"],
        expected_controller_input_device=0,
        expected_battle_engine=render["p0be"],
        expected_walker=render["p0walker"],
    )
    e_route = route_summary(
        route="P2/E",
        strict_window=strict_window_by_sequence(state_summary, "down:E,wait:500,up:E"),
        public_window=public_window_by_index(state_summary, 4),
        movement_row=object_at(movement_summary, "e"),
        expected_player=render["p1"],
        expected_controller_input_device=1,
        expected_battle_engine=render["p1be"],
        expected_walker=render["p1walker"],
    )
    require_distinct_nonzero("controllers", [q_route["controller"], e_route["controller"]])
    require(q_route["controller"] != q_route["player"], "P1 controller pointer equals player pointer")
    require(e_route["controller"] != e_route["player"], "P2 controller pointer equals player pointer")

    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "protocolVersion": EXPECTED_PROTOCOL,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "sourceBridgeProofSha256": sha256_file(bridge_path),
        "liveRuntimeArtifactSha256": sha256_file(runtime_path),
        "nSlotConcurrentProcessProofSha256": sha256_file(nslot_path),
        "claim": "N-slot-derived P1/P2 copied-host state-authority graph proof",
        "hostAuthorityScope": "single-copied-host-exact-pid-state-graph",
        "slotCapacity": bridge_summary["slotCapacity"],
        "acceptedSessionParticipantCount": bridge_summary["acceptedSessionParticipantCount"],
        "acceptedOriginalBinaryGameplaySlots": bridge_summary["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": bridge_summary["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": bridge_summary["rejectedGameplayRouteSlots"],
        "processConcurrencyModel": bridge_summary["processConcurrencyModel"],
        "simultaneousClientProcessesProven": bridge_summary["simultaneousClientProcessesProven"],
        "maxSimultaneousSocketConnectionsProven": bridge_summary["maxSimultaneousSocketConnectionsProven"],
        "derivedInputSequences": bridge_summary["derivedInputSequences"],
        "visualCaptureCount": bridge_summary["visualCaptureCount"],
        "hostGraph": {
            "players": render["players"],
            "level": render["level"],
            "horizSplit": render["horizSplit"],
            "p1Player": render["p0"],
            "p2Player": render["p1"],
            "p1BattleEngine": render["p0be"],
            "p2BattleEngine": render["p1be"],
            "p1Walker": render["p0walker"],
            "p2Walker": render["p1walker"],
            "distinctPlayers": True,
            "distinctBattleEngines": True,
            "distinctWalkers": True,
            "distinctControllers": True,
        },
        "routeAuthority": {
            "P1/Q": q_route,
            "P2/E": e_route,
        },
        "waitWindowsClean": True,
        "hostHelperInputSent": True,
        "gameInputSentByNSlotScheduler": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "multiHostLanProof": False,
        "publicMatchmakingProof": False,
        "nativeBeaNetcodeProof": False,
        "fullSessionSecurityProof": False,
        "deterministicSyncProof": False,
        "rollbackProof": False,
        "antiCheatProof": False,
        "physicalGamepadProof": False,
        "rebuildParityProof": False,
        "noNoticeableDifferenceProof": False,
        "privateProofContainsRawPrivatePath": True,
        "privateProofReleaseExcludedByPolicy": True,
        "publicPublicationSafetyValidatedBy": (
            "tools/local_multiplayer_static_runtime_contract_probe.py plus release profile, curated manifest, and public allowlist gates"
        ),
        "claimBoundary": (
            "This proves the accepted N-slot concurrent relay plan drove one copied host where exact-PID CDB rows form a "
            "consistent P1/P2 host-owned state graph from render state through controller dispatch, player receive, "
            "BattleEngine part, WalkerPart, and movement-state store. It does not prove active P3/P4 original-binary "
            "gameplay, more-than-two original-binary runtime players, multi-host LAN play, public matchmaking, native BEA "
            "netcode, full session-security proof, deterministic sync, rollback, anti-cheat, physical gamepad proof, "
            "rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_state_authority_proof(bridge_path: Path, output_path: Path) -> dict[str, Any]:
    require_private_proof_path(output_path)
    bridge_path = require_private_proof_path(bridge_path)
    summary = validate_state_authority(bridge_path)
    proof = {
        **summary,
        "sourceBridgeProof": str(bridge_path),
    }
    write_json(output_path, proof)
    return validate_state_authority_proof(output_path)


def validate_state_authority_proof(path: Path) -> dict[str, Any]:
    require_private_proof_path(path)
    proof = read_json(path)
    require(proof.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected state-authority schema")
    require(proof.get("generatedBy") == EXPECTED_HELPER, "unexpected state-authority helper")
    require(proof.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected state-authority helper version")
    require(proof.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected state-authority protocol")
    source_bridge = Path(str(proof.get("sourceBridgeProof", "")))
    require_private_proof_path(source_bridge)
    require(source_bridge.is_file(), "source bridge proof is missing")
    expected = validate_state_authority(source_bridge)
    for key, value in expected.items():
        require(proof.get(key) == value, f"state-authority proof mismatch: {key}")
    return expected


def make_fixture(root: Path, *, render_mismatch: bool = False) -> Path:
    bridge_path = nslot_bridge.make_live_bridge_fixture(root / "bridge")
    if render_mismatch:
        bridge_proof = nslot_bridge.read_json(bridge_path)
        runtime_path = nslot_bridge.resolve_path(bridge_path, str(bridge_proof.get("liveRuntimeArtifact", "")))
        artifact = state_delta.read_json(runtime_path)
        log_path = Path(str(object_at(object_at(artifact, "cdbObserver"), "result").get("logPath", "")))
        text = log_path.read_text(encoding="utf-8")
        require("p0be=03867570" in text, "fixture CDB render p0be marker missing")
        log_path.write_text(text.replace("p0be=03867570", "p0be=03867571", 1), encoding="utf-8")
    return bridge_path


def self_test() -> None:
    private_root = nslot_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
    private_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=private_root) as tmp:
        root = Path(tmp)
        bridge_path = make_fixture(root)
        output_path = root / "host-authority-state-authority-observer-proof.json"
        summary = make_state_authority_proof(bridge_path, output_path)
        require(summary["hostGraph"]["distinctPlayers"] is True, "fixture must prove distinct players")
        require(summary["routeAuthority"]["P1/Q"]["inputDevice"] == 0, "fixture P1 route mismatch")
        require(summary["routeAuthority"]["P2/E"]["inputDevice"] == 1, "fixture P2 route mismatch")

        with tempfile.TemporaryDirectory() as public_tmp:
            try:
                make_state_authority_proof(bridge_path, Path(public_tmp) / "should-fail-private-boundary.json")
            except HostAuthorityStateAuthorityObserverError:
                pass
            else:
                raise HostAuthorityStateAuthorityObserverError("public output path should fail private boundary")

            try:
                make_state_authority_proof(Path(public_tmp) / "bridge-outside-private-root.json", root / "bad-source-proof.json")
            except HostAuthorityStateAuthorityObserverError:
                pass
            else:
                raise HostAuthorityStateAuthorityObserverError("source bridge outside private root should fail")

        bad_privacy = read_json(output_path)
        bad_privacy["privateProofReleaseExcludedByPolicy"] = False
        bad_privacy_path = root / "bad-private-boundary-field.json"
        write_json(bad_privacy_path, bad_privacy)
        try:
            validate_state_authority_proof(bad_privacy_path)
        except HostAuthorityStateAuthorityObserverError:
            pass
        else:
            raise HostAuthorityStateAuthorityObserverError("tampered private boundary field should fail")

        bad_hash = read_json(output_path)
        bad_hash["sourceBridgeProofSha256"] = "0" * 64
        bad_hash_path = root / "bad-source-hash.json"
        write_json(bad_hash_path, bad_hash)
        try:
            validate_state_authority_proof(bad_hash_path)
        except HostAuthorityStateAuthorityObserverError:
            pass
        else:
            raise HostAuthorityStateAuthorityObserverError("tampered source bridge hash should fail")

    with tempfile.TemporaryDirectory(dir=private_root) as tmp:
        try:
            validate_state_authority(make_fixture(Path(tmp), render_mismatch=True))
        except HostAuthorityStateAuthorityObserverError:
            pass
        else:
            raise HostAuthorityStateAuthorityObserverError("render/receive BattleEngine mismatch should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--build-from-nslot-runtime-bridge", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary host-authority state-authority observer checker self-test: PASS")
        return 0
    if args.build_from_nslot_runtime_bridge is not None:
        if args.output is None:
            raise SystemExit("--output is required with --build-from-nslot-runtime-bridge")
        print(json.dumps(make_state_authority_proof(args.build_from_nslot_runtime_bridge, args.output), indent=2, sort_keys=True))
        return 0
    if args.proof is None:
        raise SystemExit("proof is required unless --self-test or --build-from-nslot-runtime-bridge is used")
    print(json.dumps(validate_state_authority_proof(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        HostAuthorityStateAuthorityObserverError,
        nslot_bridge.HostAuthorityNSlotRuntimeBridgeError,
        nslot_bridge.nslot.HostAuthorityNSlotProcessSmokeProofError,
        nslot_bridge.movement_bridge.HostAuthorityRuntimeMovementBridgeError,
        nslot_bridge.movement_bridge.executor.HostAuthorityRuntimeExecutorError,
        nslot_bridge.movement_bridge.executor.delivery.HostAuthorityRuntimeDeliveryError,
        state_delta.ArtifactError,
        movement.MovementStateDeltaError,
    ) as exc:
        print(f"WinUI original-binary host-authority state-authority observer check: FAIL: {exc}")
        raise SystemExit(2)
