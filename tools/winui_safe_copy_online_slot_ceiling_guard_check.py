#!/usr/bin/env python3
"""Validate the original-binary online slot-ceiling guard."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_runtime_executor_check as executor
import winui_safe_copy_online_host_authority_state_authority_observer_check as state_authority
import winui_safe_copy_online_host_authority_state_authority_replayability_check as state_replayability


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-slot-ceiling-guard.v1.json"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
N_SLOT_SCHEMA = ROOT / "roadmap" / "original-binary-online-n-slot-session-schema.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_online_slot_ceiling_guard_2026-06-19.md"
EXECUTOR_READINESS = ROOT / "release" / "readiness" / "original_binary_host_authority_runtime_executor_2026-06-19.md"
STATE_AUTHORITY_READINESS = ROOT / "release" / "readiness" / "original_binary_host_authority_state_authority_observer_2026-06-19.md"
STATE_AUTHORITY_REPLAYABILITY_READINESS = ROOT / "release" / "readiness" / "original_binary_host_authority_state_authority_replayability_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
PACKAGE_JSON = ROOT / "package.json"
SOURCE_GAME_CPP = ROOT / "references" / "Onslaught" / "game.cpp"
SOURCE_ENGINE_H = ROOT / "references" / "Onslaught" / "engine.h"
SOURCE_GAME_H = ROOT / "references" / "Onslaught" / "game.h"
DEFAULT_PRIVATE_EXECUTOR_PROOF = (
    ROOT
    / "subagents"
    / "winui-safe-copy-live-runtime"
    / "online-host-authority-runtime-executor-20260619-focus2"
    / "host-authority-runtime-executor-proof.json"
)

EXPECTED_SCHEMA = "winui-original-binary-online-slot-ceiling-guard.v1"
EXPECTED_SCOPE = "original-binary-online-slot-ceiling-guard"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_slot_ceiling_guard_check.py --check"
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]


class SlotCeilingGuardError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SlotCeilingGuardError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def require_tokens(path: Path, tokens: tuple[str, ...]) -> None:
    text = read_text(path)
    for token in tokens:
        require(token in text, f"{path} missing token: {token}")


def require_source_anchors() -> None:
    require_tokens(
        SOURCE_GAME_CPP,
        (
            "WORLD.IsMultiplayer()",
            "mPlayers=2",
            "mPlayers=1",
            "CGame::IsMultiplayer()",
            ">849",
            "< 900",
            "(mPlayers==3) || (mPlayers==4)",
            "3/4 player quad split",
            "ENGINE.SetViewpoint(2",
            "ENGINE.SetViewpoint(3",
        ),
    )
    require_tokens(SOURCE_ENGINE_H, ("#define VIEWPOINTS", "mCamera[VIEWPOINTS]", "mViewport[VIEWPOINTS]", "mPlayer[VIEWPOINTS]"))
    require_tokens(SOURCE_GAME_H, ("#define MAX_PLAYERS 4", "mPlayer[ MAX_PLAYERS ]", "mController[ MAX_PLAYERS ]", "mCurrentCamera[ MAX_PLAYERS ]"))


def require_current_runtime_ceiling(contract: dict[str, Any]) -> dict[str, Any]:
    ceiling = object_at(contract, "currentOriginalBinaryRuntimeCeiling")
    require(ceiling.get("runtimeProfile") == "original-binary-copied-local-splitscreen", "runtime profile mismatch")
    require(ceiling.get("activeOriginalBinarySlotsProven") == EXPECTED_ACTIVE_SLOTS, "active slots must stay P1/P2")
    require(ceiling.get("maxOriginalBinaryActiveSlotsProven") == 2, "active original-binary slot proof must stay two")
    require(ceiling.get("maxRuntimePlayerSlotsProven") == 2, "runtime player proof must stay two")
    require(ceiling.get("retailViewpointsProven") == 2, "retail viewpoints proof must stay two")
    require(ceiling.get("observedViewpoints") == [0, 1], "observed viewpoints must stay 0,1")
    require(ceiling.get("moreThanTwoOriginalBinaryRuntimeProofSlices") == 0, "more-than-two proof must stay zero")
    require(ceiling.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(ceiling.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 active gameplay proof must stay false")
    require(ceiling.get("p3p4GameplayInputRejected") is True, "P3/P4 gameplay input rejection must stay true")
    require(ceiling.get("p3p4RuntimeRoute") == "metadata-only/rejected-original-binary-gameplay-route", "P3/P4 route boundary mismatch")
    require(ceiling.get("beyondTwoPlayersRequiresNewProofClass") is True, "beyond-two must require a new proof class")
    require(ceiling.get("absenceOfCurrentProofIsNotProofOfPermanentAbsence") is True, "guard must preserve future proof possibility")
    require(ceiling.get("permanentImpossibilityClaim") is False, "guard must not claim P3/P4 is impossible forever")
    return ceiling


def require_scalable_session_boundary(contract: dict[str, Any]) -> dict[str, Any]:
    boundary = object_at(contract, "scalableSessionBoundary")
    require(boundary.get("sessionArchitectureRemainsScalable") is True, "session architecture must remain scalable")
    require(boundary.get("mustNotHardcodeExactlyTwoPlayers") is True, "schema must not hardcode exactly two players")
    require(boundary.get("minimumArchitectureAcceptanceSlots") == 4, "minimum architecture slots must be four")
    require(boundary.get("slotCapacity") == 4, "slot capacity must be four")
    require(boundary.get("acceptedSessionParticipantCount") == 4, "accepted session participants must be four")
    require(boundary.get("activeOriginalBinarySlots") == EXPECTED_ACTIVE_SLOTS, "active slots mismatch")
    require(boundary.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata-only slots mismatch")
    require(boundary.get("unsupportedOriginalBinaryActiveSlotsRejected") == EXPECTED_METADATA_SLOTS, "unsupported slots mismatch")
    require(boundary.get("extraSlotRejectionPolicy") == "required-for-unproven-original-binary-slots", "extra-slot policy mismatch")
    require(boundary.get("rejectedOriginalBinaryGameplayCommandCount") == 2, "P3/P4 rejection count mismatch")
    require(boundary.get("modeScalableArchitecturePlanned") is True, "mode-scalable architecture should remain planned")
    require(boundary.get("coOpVersusModeRuntimeProofSlices") == 0, "co-op/versus runtime proof must stay zero")
    return boundary


def require_latest_runtime_boundary(contract: dict[str, Any]) -> dict[str, Any]:
    latest = object_at(contract, "latestRuntimeProofBoundary")
    require(latest.get("readinessNote") == "release/readiness/original_binary_host_authority_state_authority_replayability_2026-06-19.md", "state-authority replayability readiness pointer mismatch")
    require(latest.get("stateAuthorityReplayabilitySchema") == state_replayability.EXPECTED_SCHEMA, "state-authority replayability schema mismatch")
    require(latest.get("stateAuthoritySchema") == state_authority.EXPECTED_SCHEMA, "state-authority schema mismatch")
    require(latest.get("sourceBridgeSchema") == state_authority.EXPECTED_BRIDGE_SCHEMA, "state-authority source bridge schema mismatch")
    require(latest.get("hostAuthorityScope") == "single-copied-host-exact-pid-state-graph", "state-authority scope mismatch")
    require(latest.get("proofCount") == 2, "state-authority replayability proof count mismatch")
    require(latest.get("safeCopyLaunchLevel") == 850, "safe-copy launch level mismatch")
    require(latest.get("controllerConfiguration") == 1, "controller configuration mismatch")
    require(latest.get("deliveredOriginalBinaryCommandCount") == 2, "delivered command count must be two")
    require(latest.get("deliveredSlots") == EXPECTED_ACTIVE_SLOTS, "delivered slots must be P1/P2")
    require(latest.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "rejected slots must be P3/P4")
    require(latest.get("hostHelperInputSent") is True, "host-helper input proof should be true for P1/P2")
    require(latest.get("gameInputSentByScheduler") is False, "scheduler direct game input must stay false")
    require(latest.get("stateAuthorityGraphProven") is True, "state-authority graph proof missing")
    require(latest.get("stateAuthorityReplayabilityProven") is True, "state-authority replayability proof missing")
    require(latest.get("distinctLiveRuntimeArtifactHashes") is True, "state-authority distinct runtime hashes proof missing")
    require(latest.get("distinctSourceBridgeProofHashes") is True, "state-authority distinct source bridge proof missing")
    require(latest.get("distinctProcessIds") is True, "state-authority distinct process id proof missing")
    require(latest.get("distinctCdbLogs") is True, "state-authority distinct CDB log proof missing")
    require(latest.get("distinctRuntimePointerTuples") is True, "state-authority distinct pointer tuple proof missing")
    require(latest.get("distinctPlayers") is True, "state-authority distinct player proof missing")
    require(latest.get("distinctBattleEngines") is True, "state-authority distinct BattleEngine proof missing")
    require(latest.get("distinctWalkers") is True, "state-authority distinct Walker proof missing")
    require(latest.get("distinctControllers") is True, "state-authority distinct controller proof missing")
    require(latest.get("waitWindowsClean") is True, "state-authority wait-window proof missing")
    require(latest.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    return latest


def require_cross_contracts() -> None:
    scalability = read_json(SCALABILITY)
    runtime = object_at(scalability, "currentOriginalBinaryRuntime")
    require(runtime.get("maxRuntimePlayerSlotsProven") == 2, "scalability runtime cap drifted")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "scalability N-player proof drifted")
    require(runtime.get("beyondTwoPlayersRequiresNewProofClass") is True, "scalability proof-class boundary missing")
    architecture = object_at(scalability, "scalableArchitecture")
    require(architecture.get("mustNotHardcodeExactlyTwoPlayers") is True, "scalability architecture over-narrowed")
    require(architecture.get("minimumArchitectureAcceptanceSlots") == 4, "scalability architecture no longer accepts four slots")
    policy = object_at(architecture, "slotPolicy")
    require(policy.get("maxOriginalBinaryActiveSlots") == 2, "scalability slot policy cap drifted")
    require(policy.get("unsupportedSlotsRejected") is True, "unsupported slot rejection missing")

    nslot = read_json(N_SLOT_SCHEMA)
    runtime_boundary = object_at(nslot, "runtimeBoundary")
    require(runtime_boundary.get("maxOriginalBinaryActiveSlots") == 2, "N-slot runtime cap drifted")
    require(runtime_boundary.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-slot runtime proof drifted")
    descriptor = object_at(nslot, "sessionDescriptor")
    require(descriptor.get("slotCapacity") == 4, "N-slot capacity drifted")
    require(descriptor.get("acceptedSessionParticipantCount") == 4, "N-slot participant count drifted")
    require(descriptor.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "N-slot metadata slots drifted")
    scheduler = object_at(nslot, "hostAuthorityNSlotScheduler")
    require(scheduler.get("deterministicOriginalBinaryRelayOrder") == EXPECTED_ACTIVE_SLOTS, "N-slot relay order drifted")
    require(scheduler.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "N-slot rejected slots drifted")
    require(scheduler.get("rejectedOriginalBinaryGameplayCommandCount") == 2, "N-slot P3/P4 rejection count drifted")
    require([row.get("clientSlot") for row in list_at(scheduler, "relayPlan") if isinstance(row, dict)] == EXPECTED_ACTIVE_SLOTS, "N-slot relay plan must stay P1/P2 only")


def require_doc_tokens() -> None:
    require_tokens(
        READINESS,
        (
            "Original Binary Online Slot-Ceiling Guard Readiness Note",
            "original-binary-online-slot-ceiling-guard",
            "maxOriginalBinaryActiveSlotsProven=2",
            "activeOriginalBinarySlotsProven=P1,P2",
            "slotCapacity=4",
            "acceptedSessionParticipantCount=4",
            "P3/P4 metadata-only",
            "unsupported-original-binary-active-slot",
            "required-for-unproven-original-binary-slots",
            "p3p4GameplayInputRejected=true",
            "beyondTwoPlayersRequiresNewProofClass=true",
            "permanentImpossibilityClaim=false",
        ),
    )
    require_tokens(
        EXECUTOR_READINESS,
        (
            "deliveredOriginalBinaryCommandCount=2",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "does not prove active P3/P4 original-binary gameplay",
        ),
    )
    require_tokens(
        STATE_AUTHORITY_READINESS,
        (
            "winui-original-binary-host-authority-state-authority-observer.v1",
            "hostAuthorityModel=single-host-authoritative-copied-session",
            "runtimeProfile=original-binary-copied-local-splitscreen",
            "single-copied-host-exact-pid-state-graph",
            "acceptedOriginalBinaryGameplaySlots=P1,P2",
            "metadataOnlySlots=P3,P4",
            "maxOriginalBinaryActiveSlotsProven=2",
            "distinctPlayers=true",
            "distinctBattleEngines=true",
            "distinctWalkers=true",
            "distinctControllers=true",
            "waitWindowsClean=true",
            "hostHelperInputSent=true",
            "gameInputSentByNSlotScheduler=false",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
        ),
    )
    require_tokens(
        STATE_AUTHORITY_REPLAYABILITY_READINESS,
        (
            "winui-original-binary-host-authority-state-authority-replayability.v1",
            "host-authority-state-authority-replayability.v1",
            "single-copied-host-exact-pid-state-graph",
            "stateAuthorityGraphProven=true",
            "stateAuthorityReplayabilityProven=true",
            "Accepted original-binary gameplay slots",
            "P3",
            "P4",
            "distinctLiveRuntimeArtifactHashes=true",
            "distinctSourceBridgeProofHashes=true",
            "distinctProcessIds=true",
            "distinctCdbLogs=true",
            "distinctRuntimePointerTuples=true",
            "hostHelperInputSent=true",
            "gameInputSentByNSlotScheduler=false",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "beyondTwoPlayersRequiresNewProofClass=true",
            "permanentImpossibilityClaim=false",
        ),
    )
    for path in (FEASIBILITY, LOCAL_CONTRACT, REGISTER, CAPABILITIES, MAPPED_SYSTEMS):
        require_tokens(
            path,
            (
                "original-binary online slot-ceiling guard",
                "maxOriginalBinaryActiveSlotsProven=2",
                "P3/P4 metadata-only",
                "beyondTwoPlayersRequiresNewProofClass=true",
            ),
        )
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:winui-original-binary-online-slot-ceiling-guard") == EXPECTED_SCRIPT, "missing package slot-ceiling guard script")


def validate_contract(path: Path = CONTRACT) -> dict[str, Any]:
    contract = read_json(path)
    require(contract.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(contract.get("scope") == EXPECTED_SCOPE, "scope mismatch")
    require(contract.get("status") == "complete public-safe slot-ceiling guard; no new BEA launch or runtime proof", "status mismatch")
    anchors = object_at(contract, "sourceStaticAnchors")
    require("MAX_PLAYERS 4" in str(anchors.get("sourceCapacityTrap", "")), "MAX_PLAYERS capacity trap must be explicit")
    require("not proof" in str(anchors.get("sourceCapacityTrap", "")), "MAX_PLAYERS trap must not be treated as proof")
    require("3/4-player quad-split" in str(anchors.get("sourceLatentQuadSplitTrap", "")), "latent quad-split trap must be explicit")
    require("latent/source structural evidence" in str(anchors.get("sourceLatentQuadSplitTrap", "")), "quad-split source must not be treated as runtime proof")
    ceiling = require_current_runtime_ceiling(contract)
    boundary = require_scalable_session_boundary(contract)
    latest = require_latest_runtime_boundary(contract)
    required = list_at(contract, "requiredNewProofClassForP3P4")
    require(len(required) >= 5, "P3/P4 new-proof checklist is too narrow")
    non_claims = object_at(contract, "nonClaims")
    for key, value in non_claims.items():
        require(value is False, f"non-claim must remain false: {key}")
    require_source_anchors()
    require_cross_contracts()
    return {
        "schemaVersion": contract["schemaVersion"],
        "scope": contract["scope"],
        "activeOriginalBinarySlotsProven": ceiling["activeOriginalBinarySlotsProven"],
        "maxOriginalBinaryActiveSlotsProven": ceiling["maxOriginalBinaryActiveSlotsProven"],
        "slotCapacity": boundary["slotCapacity"],
        "acceptedSessionParticipantCount": boundary["acceptedSessionParticipantCount"],
        "metadataOnlySlots": boundary["metadataOnlySlots"],
        "p3p4GameplayInputRejected": ceiling["p3p4GameplayInputRejected"],
        "beyondTwoPlayersRequiresNewProofClass": ceiling["beyondTwoPlayersRequiresNewProofClass"],
        "absenceOfCurrentProofIsNotProofOfPermanentAbsence": ceiling["absenceOfCurrentProofIsNotProofOfPermanentAbsence"],
        "permanentImpossibilityClaim": ceiling["permanentImpossibilityClaim"],
        "deliveredOriginalBinaryCommandCount": latest["deliveredOriginalBinaryCommandCount"],
        "nPlayerOriginalBinaryRuntimeProof": latest["nPlayerOriginalBinaryRuntimeProof"],
        "claimBoundary": (
            "This validates that the current original-binary runtime proof is P1/P2 only while the session "
            "architecture remains four-slot-capable at the metadata/protocol layer only. It does not prove "
            "P3/P4 active gameplay, and it does not prove P3/P4 is impossible forever."
        ),
    }


def validate_private_executor_proof(path: Path) -> dict[str, Any]:
    summary = executor.validate_executor_proof(path)
    bundle = executor.read_json(path)
    delivery_path = executor.resolve_path(path, str(bundle.get("runtimeDeliveryProofBundle", "")))
    delivery_bundle = executor.delivery.read_json(delivery_path)
    delivery_object = object_at(delivery_bundle, "delivery")
    require(delivery_object.get("deliveredOriginalBinaryCommandCount") == 2, "private delivery count must be two")
    require(delivery_object.get("nPlayerOriginalBinaryRuntimeProof") == 0, "private N-player proof must stay zero")
    require(delivery_object.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "private metadata slots drifted")
    require(delivery_object.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "private rejected slots drifted")
    require(delivery_object.get("p3p4GameplayInputRejected") is True, "private P3/P4 rejection missing")
    rejected = list_at(delivery_object, "rejectedGameplayRows")
    rejected_slots = {
        str(row.get("clientSlot"))
        for row in rejected
        if isinstance(row, dict) and row.get("reason") == "required-for-unproven-original-binary-slots"
    }
    require(rejected_slots == set(EXPECTED_METADATA_SLOTS), "private proof must reject P3/P4 gameplay rows")
    for row in list_at(delivery_object, "deliveredCommands"):
        require(isinstance(row, dict), "delivered command row must be an object")
        require(row.get("clientSlot") in EXPECTED_ACTIVE_SLOTS, "private proof delivered a non-P1/P2 command")
    return {
        "privateExecutorProof": str(path),
        "runtimeDeliveryProof": str(delivery_path),
        "deliveredOriginalBinaryCommandCount": summary["deliveredOriginalBinaryCommandCount"],
        "nPlayerOriginalBinaryRuntimeProof": summary["nPlayerOriginalBinaryRuntimeProof"],
        "p3p4GameplayInputRejected": delivery_object["p3p4GameplayInputRejected"],
    }


def validate_repo_contract() -> dict[str, Any]:
    summary = validate_contract(CONTRACT)
    require_doc_tokens()
    return summary


def run_self_test() -> None:
    good = read_json(CONTRACT)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "contract.json"
        write_json(path, good)
        validate_contract(path)

        bad = json.loads(json.dumps(good))
        bad["currentOriginalBinaryRuntimeCeiling"]["maxOriginalBinaryActiveSlotsProven"] = 4
        write_json(path, bad)
        try:
            validate_contract(path)
        except SlotCeilingGuardError:
            pass
        else:
            raise AssertionError("active original-binary slot overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["currentOriginalBinaryRuntimeCeiling"]["permanentImpossibilityClaim"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except SlotCeilingGuardError:
            pass
        else:
            raise AssertionError("permanent impossibility overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["currentOriginalBinaryRuntimeCeiling"]["absenceOfCurrentProofIsNotProofOfPermanentAbsence"] = False
        write_json(path, bad)
        try:
            validate_contract(path)
        except SlotCeilingGuardError:
            pass
        else:
            raise AssertionError("absence-as-impossibility framing should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableSessionBoundary"]["slotCapacity"] = 2
        write_json(path, bad)
        try:
            validate_contract(path)
        except SlotCeilingGuardError:
            pass
        else:
            raise AssertionError("non-scalable slot capacity should fail")

        bad = json.loads(json.dumps(good))
        bad["latestRuntimeProofBoundary"]["deliveredSlots"] = ["P1", "P2", "P3"]
        write_json(path, bad)
        try:
            validate_contract(path)
        except SlotCeilingGuardError:
            pass
        else:
            raise AssertionError("P3 delivered runtime slot should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--private-proof", type=Path, default=None)
    parser.add_argument("--default-private-proof", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary online slot-ceiling guard checker self-test: PASS")
        return 0
    if args.default_private_proof:
        args.private_proof = DEFAULT_PRIVATE_EXECUTOR_PROOF
    if args.private_proof is not None:
        print(json.dumps(validate_private_executor_proof(args.private_proof), indent=2, sort_keys=True))
        return 0
    if not args.check:
        raise SystemExit("use --check, --self-test, --private-proof, or --default-private-proof")
    print(json.dumps(validate_repo_contract(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SlotCeilingGuardError,
        executor.HostAuthorityRuntimeExecutorError,
        executor.delivery.HostAuthorityRuntimeDeliveryError,
        executor.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor.delivery.nslot.NSlotSessionSchemaError,
        executor.delivery.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary online slot-ceiling guard check: FAIL: {exc}")
        raise SystemExit(2)
