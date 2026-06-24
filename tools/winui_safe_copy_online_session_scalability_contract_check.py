#!/usr/bin/env python3
"""Validate the original-binary online session scalability/mode contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_joined_session_same_host_runtime_authority_bundle as joined_builder
import build_winui_original_binary_joined_session_runtime_causality_bundle as causality_builder


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_online_session_scalability_contract_2026-06-18.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCHEMA = "winui-original-binary-online-session-scalability-contract.v1"
EXPECTED_SCOPE = "original-binary-online-session-scalability-contract"
EXPECTED_STATUS = "complete public-safe design/process/security/session-directory/WSL-client/joined-session-control/mode-classifier contract that aggregates one same-host P1/P2 copied-runtime causality proof; no true online multiplayer, second-host LAN, public matchmaking, native BEA netcode, more-than-two runtime players, runtime co-op/versus/team mode, or active P3/P4 gameplay proof"
EXPECTED_RUNTIME_PROFILE = "original-binary-copied-local-splitscreen"
EXPECTED_SLOT_MODEL = "profile-declared-indexed-player-slots"
EXPECTED_MODE_IDS = {"cooperative", "versus-free-for-all", "team-versus", "spectator-admin"}
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_session_scalability_contract_check.py --check"
EXPECTED_SESSION_SECURITY_SCHEMA = "winui-original-binary-host-authority-n-slot-session-security-smoke.v1"
EXPECTED_SESSION_SECURITY_SCOPE = "same-workstation-session-security-smoke-not-online-gameplay-proof"
EXPECTED_CONTROL_LIFECYCLE_SCHEMA = "winui-original-binary-joined-session-control-lifecycle.v1"
EXPECTED_SAME_HOST_SESSION_CONTROL_SCHEMA = "winui-original-binary-joined-session-same-host-session-control.v1"
EXPECTED_CONTROL_LIFECYCLE_SCOPE = "joined-session-control-lifecycle-same-host-not-online-play"
EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE = "joined-session-same-host-session-control-not-online-play"
EXPECTED_MODE_CLASSIFIER_SCHEMA = "winui-original-binary-online-mode-classifier.v1"
EXPECTED_MODE_CLASSIFIER_PROOF_CLASS = "static-source-session-taxonomy-not-runtime-mode-proof"
EXPECTED_MODE_CLASSIFIER_SCOPE = "original-binary-online-mode-classifier-not-runtime-mode-proof"
FALSE_NON_CLAIM_KEYS = (
    "baseOnlineMultiplayerReady",
    "moreThanTwoOriginalBinaryRuntimeProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "coOpModeRuntimeProof",
    "versusModeRuntimeProof",
    "teamVersusRuntimeProof",
    "multiHostLanProof",
    "secondPhysicalHostProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "physicalGamepadProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
)


class ScalabilityContractError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ScalabilityContractError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
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


def validate_contract(path: Path) -> dict[str, Any]:
    contract = read_json(path)
    require(contract.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(contract.get("scope") == EXPECTED_SCOPE, "scope mismatch")
    require(contract.get("status") == EXPECTED_STATUS, "status boundary drifted")

    runtime = object_at(contract, "currentOriginalBinaryRuntime")
    require(runtime.get("runtimeProfile") == EXPECTED_RUNTIME_PROFILE, "runtime profile mismatch")
    require(runtime.get("playerSlotsProven") == ["P1", "P2"], "original-binary runtime proof must stay P1/P2")
    require(runtime.get("maxRuntimePlayerSlotsProven") == 2, "original-binary runtime proof must not exceed two players")
    require(runtime.get("maxRetailPlayersProven") == 2, "retail players proven must stay two")
    require(runtime.get("retailSlotsProven") == "P1,P2", "retail slots proven must stay P1,P2")
    require(runtime.get("retailViewpointsProven") == 2, "retail viewpoints proven must stay two")
    require("mPlayers=2" in str(runtime.get("sourcePlayerCountAnchor")), "missing mPlayers=2 source anchor")
    require("VIEWPOINTS 2" in str(runtime.get("sourceViewpointAnchor")), "missing VIEWPOINTS 2 source anchor")
    require(runtime.get("moreThanTwoOriginalBinaryRuntimeProofSlices") == 0, "more-than-two original-binary proof must remain zero")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player original-binary runtime proof must remain zero")
    require(runtime.get("beyondTwoPlayersRequiresNewProofClass") is True, "beyond-two-player runtime work must require a new proof class")
    require(runtime.get("coOpVersusModeRuntimeProofSlices") == 0, "co-op/versus mode proof must remain zero")
    require(runtime.get("nativeBeaNetcodeProofSlices") == 0, "native BEA netcode proof must remain zero")
    require(runtime.get("modeScalableContractStatus") == "design-only-unproven", "mode-scalable contract status must be design-only")
    require(runtime.get("modeRuntimeClassification") == "unclassified-local-multiplayer", "runtime mode classification must stay unclassified local multiplayer")

    architecture = object_at(contract, "scalableArchitecture")
    require(architecture.get("modeScalableArchitecturePlanned") is True, "mode-scalable architecture flag must be true")
    session_type = object_at(architecture, "sessionTypeModel")
    require(session_type.get("schema") == "host-authority-session-schema.v2-planned", "session type schema mismatch")
    require(session_type.get("participantsField") == "participants[]", "session type must use participants[]")
    require(session_type.get("maxOriginalBinaryActiveSlots") == 2, "session type must preserve original-binary active-slot cap")
    require(session_type.get("unsupportedSlotsRejected") is True, "session type must reject unsupported slots")
    require(architecture.get("slotModel") == EXPECTED_SLOT_MODEL, "slot model must be profile-declared/indexed")
    slot_policy = object_at(architecture, "slotPolicy")
    require(slot_policy.get("slotSet") == "profile-declared", "slot policy slot set mismatch")
    require(slot_policy.get("maxOriginalBinaryActiveSlots") == 2, "slot policy must cap original-binary active slots at two")
    require(slot_policy.get("unsupportedSlotsRejected") is True, "slot policy must reject unsupported slots")
    require(architecture.get("mustNotHardcodeExactlyTwoPlayers") is True, "architecture must reject hardcoded two-player design")
    require(architecture.get("minimumArchitectureAcceptanceSlots") == 4, "architecture acceptance must cover at least four design slots")
    require(architecture.get("slotIdsInDesignExamples") == ["P1", "P2", "P3", "P4"], "design examples must cover P1-P4")
    scheduler = object_at(architecture, "schedulerPolicy")
    require(scheduler.get("schedulerCardinalityProven") == 4, "scheduler cardinality proof must be four process slots")
    require(scheduler.get("maxClientProcessesProven") == 4, "max client-process proof must be four")
    require(scheduler.get("sequentialProcessConcurrencyModel") == "sequential-distinct-client-processes", "sequential process concurrency model mismatch")
    require(scheduler.get("sequentialSimultaneousClientProcessesProven") == 1, "sequential simultaneous client-process proof must remain one")
    require(scheduler.get("processConcurrencyModel") == "barrier-concurrent-client-processes", "process concurrency model must be barrier concurrent")
    require(scheduler.get("simultaneousClientProcessesProven") == 4, "simultaneous client-process proof must be four")
    require(scheduler.get("maxSimultaneousSocketConnectionsProven") == 4, "simultaneous socket proof must be four")
    require(scheduler.get("clientReadyBeforeBarrierReleaseCount") == 4, "barrier readiness count must be four")
    require(scheduler.get("barrierReleaseAfterAllClientsReady") is True, "barrier release must follow all client readiness")
    require(scheduler.get("concurrentProofSchema") == "winui-original-binary-host-authority-n-slot-concurrent-process-smoke.v1", "concurrent proof schema mismatch")
    require(scheduler.get("privateInterfaceListenerScope") == "private-lan-reachable-during-smoke-foreign-peers-rejected-after-accept", "private-interface listener scope mismatch")
    require(scheduler.get("concurrentProcessSmokeSecurityScope") == "minimal-smoke-hmac-envelope-not-full-session-security-proof", "concurrent smoke security scope mismatch")
    for key in (
        "sessionScopedMacCoverageProof",
        "maxJsonLineBytesEnforced",
        "unknownFieldRejectionProof",
        "strictMessageSchemaProof",
    ):
        require(scheduler.get(key) is False, f"unproven concurrent-smoke security claim must remain false: {key}")
    require(scheduler.get("schedulePolicy") == "stable-slot-order", "schedule policy mismatch")
    require(scheduler.get("arrivalOrderCanDiffer") is True, "scheduler must record arrival-order independence")
    require(scheduler.get("slotSet") == "profile-declared", "scheduler slot set mismatch")
    require(scheduler.get("rejectedExtraSlot") == "required-for-unproven-original-binary-slots", "scheduler must require rejected extra-slot handling")
    require(scheduler.get("gameInputSentByScheduler") is False, "scheduler design contract must not claim game input")
    security_smoke = object_at(architecture, "sessionSecuritySmokePolicy")
    require(security_smoke.get("proofSchema") == EXPECTED_SESSION_SECURITY_SCHEMA, "session-security proof schema mismatch")
    require(security_smoke.get("securityProofScope") == EXPECTED_SESSION_SECURITY_SCOPE, "session-security proof scope mismatch")
    require(security_smoke.get("sessionScopedMacCoverageProof") is True, "session-security smoke must prove session-scoped MAC coverage")
    require(security_smoke.get("tickBoundMacFieldsProof") is True, "session-security smoke must prove tick-bound MAC fields")
    require(security_smoke.get("relayPlanHashMacBound") is True, "session-security smoke must bind relay-plan hash")
    require(security_smoke.get("maxJsonLineBytesEnforced") is True, "session-security smoke must enforce max JSON line bytes")
    require(security_smoke.get("maxJsonLineBytes") == 4096, "session-security smoke max JSON line bytes mismatch")
    require(security_smoke.get("unknownFieldRejectionProof") is True, "session-security smoke must reject unknown fields")
    require(security_smoke.get("strictMessageSchemaProof") is True, "session-security smoke must prove strict schema")
    require(security_smoke.get("acceptedOriginalBinaryGameplayCommandCount") == 2, "session-security smoke accepted command count mismatch")
    require(security_smoke.get("metadataGameplayRejectionCount") == 2, "session-security smoke metadata rejection count mismatch")
    require(security_smoke.get("rejectedSecurityCaseCount") == 25, "session-security smoke rejection count mismatch")
    for key in (
        "newBeaLaunchCount",
        "cdbAttachCount",
        "nPlayerOriginalBinaryRuntimeProof",
    ):
        require(security_smoke.get(key) == 0, f"session-security smoke must keep {key}=0")
    for key in (
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
    ):
        require(security_smoke.get(key) is False, f"session-security overclaim must remain false: {key}")
    require(architecture.get("modeTaxonomyVersion") == "online-mode-taxonomy.v1", "mode taxonomy version mismatch")
    joined_policy = object_at(architecture, "joinedSessionSameHostRuntimeAuthorityPolicy")
    require(joined_policy.get("proofSchema") == joined_builder.SCHEMA, "joined-session policy schema mismatch")
    require(joined_policy.get("protocolVersion") == joined_builder.PROTOCOL, "joined-session policy protocol mismatch")
    require(joined_policy.get("joinedSessionScope") == joined_builder.JOINED_SCOPE, "joined-session policy scope mismatch")
    require(joined_policy.get("hostAuthorityModel") == joined_builder.HOST_AUTHORITY_MODEL, "joined-session host model mismatch")
    require(joined_policy.get("hostAuthorityScope") == joined_builder.HOST_AUTHORITY_SCOPE, "joined-session host scope mismatch")
    require(joined_policy.get("runtimeProfile") == EXPECTED_RUNTIME_PROFILE, "joined-session runtime profile mismatch")
    require(joined_policy.get("joinedSessionSameHostRuntimeAuthorityChainProven") is True, "joined-session chain flag missing")
    require(joined_policy.get("acceptedJoinTicketSlot") == "P2", "joined-session ticket slot mismatch")
    require(joined_policy.get("joinTicketRuntimeRelayHashMatched") is True, "joined-session relay link missing")
    require(joined_policy.get("samePhysicalMachineWslPredecessor") is True, "joined-session WSL predecessor flag missing")
    require(joined_policy.get("sameHostOnly") is True, "joined-session same-host flag missing")
    require(joined_policy.get("privateProofReleaseExcludedByPolicy") is True, "joined-session release boundary missing")
    require(joined_policy.get("secureNSlotRuntimeExecutorReplayabilityProven") is True, "joined-session secure executor flag missing")
    require(joined_policy.get("stateAuthorityGraphProven") is True, "joined-session state graph flag missing")
    require(joined_policy.get("stateAuthorityReplayabilityProven") is True, "joined-session state replayability flag missing")
    require(joined_policy.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "joined-session active slot mismatch")
    require(joined_policy.get("metadataOnlySlots") == ["P3", "P4"], "joined-session metadata slot mismatch")
    require(joined_policy.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "joined-session rejected slot mismatch")
    require(joined_policy.get("maxOriginalBinaryActiveSlotsProven") == 2, "joined-session max active slots must stay two")
    require(joined_policy.get("wrapperNewBeaLaunchCount") == 0, "joined-session wrapper must not launch BEA")
    require(joined_policy.get("wrapperCdbAttachCount") == 0, "joined-session wrapper must not attach CDB")
    require(joined_policy.get("upstreamNewBeaLaunchCountPerProof") == 1, "joined-session upstream launch count mismatch")
    require(joined_policy.get("upstreamCdbAttachCountPerProof") == 1, "joined-session upstream CDB count mismatch")
    require(joined_policy.get("hostHelperInputSentByAcceptedRuntimeAuthority") is True, "joined-session runtime-authority host-helper flag missing")
    for key in (
        "gameInputSentByDirectory",
        "gameInputSentByWslClient",
        "gameInputSentByNSlotScheduler",
        "joinedSessionVisibleMovementCausalityProof",
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "permanentImpossibilityClaim",
    ):
        require(joined_policy.get(key) is False, f"joined-session overclaim must remain false: {key}")
    require(joined_policy.get("nPlayerOriginalBinaryRuntimeProof") == 0, "joined-session N-player proof must stay zero")
    require(joined_policy.get("beyondTwoPlayersRequiresNewProofClass") is True, "joined-session beyond-two proof class flag missing")
    causality_policy = object_at(architecture, "joinedSessionRuntimeCausalityPolicy")
    require(causality_policy.get("proofSchema") == causality_builder.SCHEMA, "joined-session causality schema mismatch")
    require(causality_policy.get("protocolVersion") == causality_builder.PROTOCOL, "joined-session causality protocol mismatch")
    require(causality_policy.get("causalityScope") == causality_builder.CAUSALITY_SCOPE, "joined-session causality scope mismatch")
    require(causality_policy.get("hostAuthorityModel") == causality_builder.HOST_AUTHORITY_MODEL, "joined-session causality host model mismatch")
    require(causality_policy.get("hostAuthorityScope") == causality_builder.HOST_AUTHORITY_SCOPE, "joined-session causality host scope mismatch")
    require(causality_policy.get("runtimeProfile") == EXPECTED_RUNTIME_PROFILE, "joined-session causality runtime profile mismatch")
    require(causality_policy.get("joinedSessionRuntimeCausalityProven") is True, "joined-session causality flag missing")
    require(causality_policy.get("joinedSessionAuthorityProofValidated") is True, "joined-session causality source flag missing")
    require(causality_policy.get("freshRuntimeExecutorProofValidated") is True, "joined-session causality executor flag missing")
    require(causality_policy.get("joinTicketRuntimeRelayPathMatchCount") == 1, "joined-session causality relay-path match count mismatch")
    require(causality_policy.get("acceptedJoinTicketSlot") == "P2", "joined-session causality ticket slot mismatch")
    require(causality_policy.get("joinTicketRuntimeRelayHashMatched") is True, "joined-session causality relay link missing")
    require(causality_policy.get("samePhysicalMachineWslPredecessor") is True, "joined-session causality WSL predecessor missing")
    require(causality_policy.get("sameHostOnly") is True, "joined-session causality same-host flag missing")
    require(causality_policy.get("newBeaLaunchCount") == 1, "joined-session causality launch count mismatch")
    require(causality_policy.get("cdbAttachCount") == 1, "joined-session causality CDB count mismatch")
    require(causality_policy.get("visualCaptureCount") == 7, "joined-session causality visual count mismatch")
    require(causality_policy.get("deliveredOriginalBinaryCommandCount") == 2, "joined-session causality delivered command count mismatch")
    require(causality_policy.get("hostHelperInputSent") is True, "joined-session causality host-helper flag missing")
    require(causality_policy.get("stateAuthorityGraphProven") is True, "joined-session causality state graph flag missing")
    require(causality_policy.get("exactPidCdbStateRowsProven") is True, "joined-session causality CDB state flag missing")
    require(causality_policy.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "joined-session causality active slot mismatch")
    require(causality_policy.get("metadataOnlySlots") == ["P3", "P4"], "joined-session causality metadata slot mismatch")
    require(causality_policy.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "joined-session causality rejected slot mismatch")
    require(causality_policy.get("maxOriginalBinaryActiveSlotsProven") == 2, "joined-session causality max active slot mismatch")
    require(causality_policy.get("slotCapacity") == 4, "joined-session causality slot capacity mismatch")
    for key in (
        "gameInputSentByJoinedSessionClient",
        "gameInputSentByDirectory",
        "gameInputSentByWslClient",
        "gameInputSentByNSlotScheduler",
        "baseOnlineMultiplayerReady",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "secondPhysicalHostProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "visibleMovementDeltaClaim",
        "joinedSessionVisibleMovementCausalityProof",
        "permanentImpossibilityClaim",
    ):
        require(causality_policy.get(key) is False, f"joined-session causality overclaim must remain false: {key}")
    require(causality_policy.get("nPlayerOriginalBinaryRuntimeProof") == 0, "joined-session causality N-player proof must stay zero")
    require(causality_policy.get("beyondTwoPlayersRequiresNewProofClass") is True, "joined-session causality beyond-two flag missing")
    require(causality_policy.get("privateProofReleaseExcludedByPolicy") is True, "joined-session causality release boundary missing")
    control_policy = object_at(architecture, "joinedSessionControlLifecyclePolicy")
    require(control_policy.get("proofSchema") == EXPECTED_CONTROL_LIFECYCLE_SCHEMA, "joined-session control lifecycle schema mismatch")
    require(control_policy.get("sameHostSessionControlSchema") == EXPECTED_SAME_HOST_SESSION_CONTROL_SCHEMA, "same-host session-control schema mismatch")
    require(control_policy.get("protocolVersion") == "joined-session-same-host-session-control.v1", "same-host session-control protocol mismatch")
    require(control_policy.get("sessionControlScope") == EXPECTED_CONTROL_LIFECYCLE_SCOPE, "joined-session control lifecycle scope mismatch")
    require(control_policy.get("sameHostSessionControlScope") == EXPECTED_SAME_HOST_SESSION_CONTROL_SCOPE, "same-host session-control scope mismatch")
    require(control_policy.get("proofClass") == "control-plane-lifecycle-harness-not-runtime-gameplay-proof", "joined-session control proof class mismatch")
    require(control_policy.get("sourceJoinedAuthoritySchema") == joined_builder.SCHEMA, "joined-session control authority source mismatch")
    require(control_policy.get("sourceJoinedCausalitySchema") == causality_builder.SCHEMA, "joined-session control causality source mismatch")
    require(control_policy.get("sessionControlLifecycleProven") is True, "joined-session control lifecycle flag missing")
    require(control_policy.get("sessionControlBoundToRuntimeRelayHash") is True, "joined-session control relay binding missing")
    require(control_policy.get("upstreamJoinedSessionRuntimeCausalityProven") is True, "joined-session control upstream causality flag missing")
    require(control_policy.get("acceptedJoinTicketSlot") == "P2", "joined-session control ticket slot mismatch")
    require(control_policy.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "joined-session control active slot mismatch")
    require(control_policy.get("metadataOnlySlots") == ["P3", "P4"], "joined-session control metadata slots mismatch")
    require(control_policy.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "joined-session control rejected slots mismatch")
    require(control_policy.get("acceptedControlActionCount") == 11, "joined-session control accepted action count mismatch")
    require(control_policy.get("rejectedControlCaseCount") == 22, "joined-session control rejected case count mismatch")
    require(control_policy.get("reconnectProofScope") == "metadata-reconnect-only-not-runtime-reconnect", "joined-session control reconnect scope mismatch")
    require(control_policy.get("spectatorAdminMetadataOnly") is True, "joined-session control spectator/admin boundary missing")
    require(control_policy.get("securityScope") == "same-host-session-control-message-smoke-not-production-security-proof", "joined-session control security scope mismatch")
    require(control_policy.get("sameHostOnly") is True, "joined-session control same-host flag missing")
    require(control_policy.get("samePhysicalMachineOnly") is True, "joined-session control same-physical-machine flag missing")
    require(control_policy.get("privateProofReleaseExcludedByPolicy") is True, "joined-session control release boundary missing")
    for key in ("newBeaLaunchCount", "cdbAttachCount", "nPlayerOriginalBinaryRuntimeProof"):
        require(control_policy.get(key) == 0, f"joined-session control must keep {key}=0")
    for key in (
        "hostHelperInputSentBySessionControl",
        "gameInputSentBySessionControl",
        "baseOnlineMultiplayerReady",
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "publicBind",
        "publicNetworkSocketsOpened",
        "rawCredentialSerialized",
        "operatorSecretsRequired",
    ):
        require(control_policy.get(key) is False, f"joined-session control overclaim must remain false: {key}")
    p3p4_policy = object_at(architecture, "p3p4RuntimeFeasibilityMapPolicy")
    require(p3p4_policy.get("proofSchema") == "winui-original-binary-online-p3p4-runtime-feasibility-map.v1", "P3/P4 feasibility map schema mismatch")
    require(p3p4_policy.get("mapProofClass") == "static-blast-radius-map-not-runtime-proof", "P3/P4 feasibility map proof class mismatch")
    require(p3p4_policy.get("p3p4FeasibilityScope") == "static-blast-radius-not-runtime-proof", "P3/P4 feasibility scope mismatch")
    require(p3p4_policy.get("newBeaLaunchCount") == 0, "P3/P4 map must not launch BEA")
    require(p3p4_policy.get("cdbAttachCount") == 0, "P3/P4 map must not attach CDB")
    require(p3p4_policy.get("ghidraMutationCount") == 0, "P3/P4 map must not mutate Ghidra")
    for key in (
        "maxOriginalBinaryActiveSlotsProven",
        "maxRuntimePlayerSlotsProven",
        "maxRetailPlayersProven",
        "retailViewpointsProven",
    ):
        require(p3p4_policy.get(key) == 2, f"P3/P4 map must preserve {key}=2")
    for key in (
        "nPlayerOriginalBinaryRuntimeProof",
        "moreThanTwoOriginalBinaryRuntimeProofSlices",
    ):
        require(p3p4_policy.get(key) == 0, f"P3/P4 map must keep {key}=0")
    require(p3p4_policy.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "P3/P4 map active slots must stay P1/P2")
    require(p3p4_policy.get("metadataOnlySlots") == ["P3", "P4"], "P3/P4 map metadata slots mismatch")
    require(p3p4_policy.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "P3/P4 map rejected slots mismatch")
    require(p3p4_policy.get("p3p4GameplayInputRejected") is True, "P3/P4 gameplay input must remain rejected")
    for key in (
        "sourceOnlyMaxPlayersIsRuntimeProof",
        "quadSplitBranchIsRuntimeProof",
        "mapCompleteForRuntimeAttempt",
        "safeToPatchMPlayersAbove2",
        "permanentImpossibilityClaim",
        "publicMatchmakingProof",
        "multiHostLanProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
    ):
        require(p3p4_policy.get(key) is False, f"P3/P4 feasibility overclaim must remain false: {key}")
    require(p3p4_policy.get("beyondTwoPlayersRequiresNewProofClass") is True, "P3/P4 map beyond-two proof-class flag missing")
    require(p3p4_policy.get("absenceOfCurrentProofIsNotProofOfPermanentAbsence") is True, "P3/P4 map permanent-absence boundary missing")
    mode_policy = object_at(architecture, "modeClassifierPolicy")
    require(mode_policy.get("proofSchema") == EXPECTED_MODE_CLASSIFIER_SCHEMA, "mode classifier schema mismatch")
    require(mode_policy.get("proofClass") == EXPECTED_MODE_CLASSIFIER_PROOF_CLASS, "mode classifier proof class mismatch")
    require(mode_policy.get("modeClassifierScope") == EXPECTED_MODE_CLASSIFIER_SCOPE, "mode classifier scope mismatch")
    require(mode_policy.get("modeClassifierProven") is True, "mode classifier proven flag missing")
    require(mode_policy.get("currentRuntimeModeClassification") == "unclassified-local-multiplayer", "mode classifier runtime classification mismatch")
    require(mode_policy.get("classificationStatus") == "runtime-observed-local-splitscreen-not-co-op-or-versus-proof", "mode classifier status mismatch")
    require(mode_policy.get("modeFamiliesClassified") == ["cooperative", "versus-free-for-all", "team-versus", "spectator-admin"], "mode classifier family list mismatch")
    require(mode_policy.get("modeRuntimeProofSlices") == 0, "mode classifier runtime proof count must remain zero")
    require(mode_policy.get("coOpVersusModeRuntimeProofSlices") == 0, "mode classifier co-op/versus proof count must remain zero")
    require(mode_policy.get("teamAssignmentAuthority") == "schema-only-not-runtime-proof", "mode classifier team boundary mismatch")
    for key in (
        "coOpModeRuntimeProof",
        "versusModeRuntimeProof",
        "teamVersusRuntimeProof",
        "spectatorAdminRuntimeProof",
        "gameInputSentByModeClassifier",
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "safeToPatchMPlayersAbove2",
    ):
        require(mode_policy.get(key) is False, f"mode classifier overclaim must remain false: {key}")
    for key in ("newBeaLaunchCount", "cdbAttachCount", "ghidraMutationCount", "nPlayerOriginalBinaryRuntimeProof"):
        require(mode_policy.get(key) == 0, f"mode classifier must keep {key}=0")
    mode_ids = {str(row.get("id")) for row in list_at(architecture, "modeFamiliesPlanned") if isinstance(row, dict)}
    require(mode_ids == EXPECTED_MODE_IDS, "mode families must cover co-op, FFA versus, team versus, and spectator/admin")
    for row in list_at(architecture, "modeFamiliesPlanned"):
        require(isinstance(row, dict), "mode family row must be an object")
        require(row.get("proofStatus") == "planned-not-runtime-proven", f"mode family overclaim: {row}")
        require(row.get("modeProofStatus") == "planned-not-runtime-proven", f"mode proof overclaim: {row}")
        require(row.get("winConditionAuthority") == "unproven", f"win-condition overclaim: {row}")
        require(row.get("respawnAuthority") == "unproven", f"respawn overclaim: {row}")
        require(row.get("teamAssignmentAuthority") == "unproven", f"team-assignment overclaim: {row}")
        require(row.get("friendlyFireStatus") == "unproven", f"friendly-fire overclaim: {row}")

    requirements = set(str(item) for item in list_at(contract, "securityAndProtocolRequirements"))
    for item in (
        "per-slot identity",
        "server identity pinning",
        "nonce freshness and replay rejection",
        "session-scoped HMAC coverage over sessionId protocolVersion slotId clientId tick sequence commandId payload",
        "replay cache keyed by session/client/slot/nonce",
        "sequence enforcement",
        "per-slot and per-session rate limits",
        "max message size",
        "schema allowlists and unknown-field rejection",
        "per-slot and global queue limits",
        "tick budget and backpressure/drop policy",
        "mode/team admission validation",
        "compatibility checks before command acceptance",
        "deterministic host schedule independent of arrival order",
        "current concurrent process smoke is not full session-security proof",
        "publicBind=false until public server design exists",
        "operator secrets outside git",
    ):
        require(item in requirements, f"missing security/protocol requirement: {item}")

    non_claims = object_at(contract, "nonClaims")
    require(set(non_claims) == set(FALSE_NON_CLAIM_KEYS), "non-claim key set drifted")
    for key in FALSE_NON_CLAIM_KEYS:
        require(non_claims.get(key) is False, f"non-claim must remain false: {key}")

    ladder = [str(item) for item in list_at(contract, "nextProofLadder")]
    require(any("real multi-host private LAN command source" in item for item in ladder), "missing multi-host command-source next rung")
    require(any("same-host session-control proof" in item for item in ladder), "missing same-host session-control next rung")
    require(any("P3/P4 proof-class deep dive" in item for item in ladder), "missing P3/P4 proof-class deep-dive next rung")
    require(any("objective/win/death/respawn" in item for item in ladder), "missing co-op/versus runtime observer next rung")
    require(any("team/friendly-fire" in item for item in ladder), "missing team/friendly-fire next rung")

    return {
        "schemaVersion": contract["schemaVersion"],
        "runtimeProfile": runtime["runtimeProfile"],
        "originalBinaryPlayerSlotsProven": runtime["playerSlotsProven"],
        "maxRuntimePlayerSlotsProven": runtime["maxRuntimePlayerSlotsProven"],
        "maxRetailPlayersProven": runtime["maxRetailPlayersProven"],
        "retailSlotsProven": runtime["retailSlotsProven"],
        "retailViewpointsProven": runtime["retailViewpointsProven"],
        "moreThanTwoOriginalBinaryRuntimeProofSlices": runtime["moreThanTwoOriginalBinaryRuntimeProofSlices"],
        "nPlayerOriginalBinaryRuntimeProof": runtime["nPlayerOriginalBinaryRuntimeProof"],
        "coOpVersusModeRuntimeProofSlices": runtime["coOpVersusModeRuntimeProofSlices"],
        "modeScalableContractStatus": runtime["modeScalableContractStatus"],
        "modeScalableArchitecturePlanned": architecture["modeScalableArchitecturePlanned"],
        "slotModel": architecture["slotModel"],
        "minimumArchitectureAcceptanceSlots": architecture["minimumArchitectureAcceptanceSlots"],
        "schedulerCardinalityProven": scheduler["schedulerCardinalityProven"],
        "maxClientProcessesProven": scheduler["maxClientProcessesProven"],
        "sequentialProcessConcurrencyModel": scheduler["sequentialProcessConcurrencyModel"],
        "sequentialSimultaneousClientProcessesProven": scheduler["sequentialSimultaneousClientProcessesProven"],
        "processConcurrencyModel": scheduler["processConcurrencyModel"],
        "simultaneousClientProcessesProven": scheduler["simultaneousClientProcessesProven"],
        "maxSimultaneousSocketConnectionsProven": scheduler["maxSimultaneousSocketConnectionsProven"],
        "clientReadyBeforeBarrierReleaseCount": scheduler["clientReadyBeforeBarrierReleaseCount"],
        "privateInterfaceListenerScope": scheduler["privateInterfaceListenerScope"],
        "concurrentProcessSmokeSecurityScope": scheduler["concurrentProcessSmokeSecurityScope"],
        "sessionSecuritySmokePolicy": {
            "proofSchema": security_smoke["proofSchema"],
            "securityProofScope": security_smoke["securityProofScope"],
            "sessionScopedMacCoverageProof": security_smoke["sessionScopedMacCoverageProof"],
            "rejectedSecurityCaseCount": security_smoke["rejectedSecurityCaseCount"],
        },
        "joinedSessionSameHostRuntimeAuthorityPolicy": {
            "proofSchema": joined_policy["proofSchema"],
            "joinedSessionScope": joined_policy["joinedSessionScope"],
            "joinedSessionSameHostRuntimeAuthorityChainProven": joined_policy["joinedSessionSameHostRuntimeAuthorityChainProven"],
            "acceptedJoinTicketSlot": joined_policy["acceptedJoinTicketSlot"],
            "joinTicketRuntimeRelayHashMatched": joined_policy["joinTicketRuntimeRelayHashMatched"],
            "samePhysicalMachineWslPredecessor": joined_policy["samePhysicalMachineWslPredecessor"],
            "sameHostOnly": joined_policy["sameHostOnly"],
        },
        "joinedSessionRuntimeCausalityPolicy": {
            "proofSchema": causality_policy["proofSchema"],
            "causalityScope": causality_policy["causalityScope"],
            "joinedSessionRuntimeCausalityProven": causality_policy["joinedSessionRuntimeCausalityProven"],
            "joinTicketRuntimeRelayPathMatchCount": causality_policy["joinTicketRuntimeRelayPathMatchCount"],
            "newBeaLaunchCount": causality_policy["newBeaLaunchCount"],
            "cdbAttachCount": causality_policy["cdbAttachCount"],
        },
        "joinedSessionControlLifecyclePolicy": {
            "proofSchema": control_policy["proofSchema"],
            "sessionControlScope": control_policy["sessionControlScope"],
            "sameHostSessionControlScope": control_policy["sameHostSessionControlScope"],
            "sessionControlLifecycleProven": control_policy["sessionControlLifecycleProven"],
            "acceptedControlActionCount": control_policy["acceptedControlActionCount"],
            "rejectedControlCaseCount": control_policy["rejectedControlCaseCount"],
            "newBeaLaunchCount": control_policy["newBeaLaunchCount"],
            "cdbAttachCount": control_policy["cdbAttachCount"],
            "gameInputSentBySessionControl": control_policy["gameInputSentBySessionControl"],
        },
        "p3p4RuntimeFeasibilityMapPolicy": {
            "proofSchema": p3p4_policy["proofSchema"],
            "mapProofClass": p3p4_policy["mapProofClass"],
            "p3p4FeasibilityScope": p3p4_policy["p3p4FeasibilityScope"],
            "nPlayerOriginalBinaryRuntimeProof": p3p4_policy["nPlayerOriginalBinaryRuntimeProof"],
            "safeToPatchMPlayersAbove2": p3p4_policy["safeToPatchMPlayersAbove2"],
        },
        "modeClassifierPolicy": {
            "proofSchema": mode_policy["proofSchema"],
            "proofClass": mode_policy["proofClass"],
            "currentRuntimeModeClassification": mode_policy["currentRuntimeModeClassification"],
            "modeRuntimeProofSlices": mode_policy["modeRuntimeProofSlices"],
            "coOpVersusModeRuntimeProofSlices": mode_policy["coOpVersusModeRuntimeProofSlices"],
        },
        "modeFamiliesPlanned": sorted(mode_ids),
        "claimBoundary": (
            "This validates a public-safe online session scalability and mode-design contract only. It does not prove "
            "more than two original-binary runtime players, co-op/versus mode behavior, multi-host LAN play, public "
            "matchmaking, native BEA netcode, deterministic sync, rebuild parity, or no-noticeable-difference parity."
        ),
    }


def require_doc_tokens() -> None:
    token_sets = {
        READINESS: (
            "Original Binary Online Session Scalability Contract Readiness Note",
            "original-binary-online-session-scalability-contract",
            "originalBinaryPlayerSlotsProven=2",
            "maxRetailPlayersProven=2",
            "retailSlotsProven=P1,P2",
            "retailViewpointsProven=2",
            "moreThanTwoOriginalBinaryRuntimeProofSlices=0",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "beyondTwoPlayersRequiresNewProofClass",
            "modeScalableContractStatus=design-only-unproven",
            "modeScalableArchitecturePlanned=true",
            "coOpVersusModeRuntimeProofSlices=0",
            "minimumArchitectureAcceptanceSlots=4",
            "schedulerCardinalityProven=4",
            "maxClientProcessesProven=4",
            "sequentialProcessConcurrencyModel=sequential-distinct-client-processes",
            "sequentialSimultaneousClientProcessesProven=1",
            "processConcurrencyModel=barrier-concurrent-client-processes",
            "simultaneousClientProcessesProven=4",
            "maxSimultaneousSocketConnectionsProven=4",
            "clientReadyBeforeBarrierReleaseCount=4",
            "barrierReleaseAfterAllClientsReady=true",
            "private-lan-reachable-during-smoke-foreign-peers-rejected-after-accept",
            "minimal-smoke-hmac-envelope-not-full-session-security-proof",
            "same-workstation-session-security-smoke-not-online-gameplay-proof",
            "securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof",
            "sessionScopedMacCoverageProof=true",
            "maxJsonLineBytesEnforced=true",
            "unknownFieldRejectionProof=true",
            "strictMessageSchemaProof=true",
            "rejectedSecurityCaseCount=25",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "joined-session control-lifecycle proof",
            "joined-session-control-lifecycle-same-host-not-online-play",
            "joined-session-same-host-session-control-not-online-play",
            "sessionControlLifecycleProven=true",
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "gameInputSentBySessionControl=false",
            "online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "runtime-observed-local-splitscreen-not-co-op-or-versus-proof",
            "modeRuntimeProofSlices=0",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
            "rejectedExtraSlot",
            "cooperative",
            "versus-free-for-all",
            "team-versus",
            "spectator-admin",
            "not a BEA launch/capture/stop run",
        ),
        FEASIBILITY: (
            "Original Binary Online Session Scalability Contract",
            "original-binary-online-session-scalability-contract.v1.json",
            "originalBinaryPlayerSlotsProven=2",
            "maxRetailPlayersProven=2",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "modeScalableArchitecturePlanned=true",
            "coOpVersusModeRuntimeProofSlices=0",
            "must not hardcode exactly two players",
            "sessionType",
            "participants[]",
            "same-workstation N-slot session-security message smoke",
            "same-workstation-session-security-smoke-not-online-gameplay-proof",
            "securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof",
            "sessionScopedMacCoverageProof=true",
            "rejectedSecurityCaseCount=25",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "joined-session same-host runtime-authority proof",
            "joined-session-same-host-runtime-authority-not-online-play",
            "joinedSessionSameHostRuntimeAuthorityChainProven=true",
            "joinTicketRuntimeRelayHashMatched=true",
            "samePhysicalMachineWslPredecessor=true",
            "sameHostOnly=true",
            "Joined-session control-lifecycle proof",
            "joined-session-control-lifecycle-same-host-not-online-play",
            "joined-session-same-host-session-control-not-online-play",
            "sessionControlLifecycleProven=true",
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "gameInputSentBySessionControl=false",
            "Original Binary Online P3/P4 Runtime Feasibility Map",
            "mapProofClass=static-blast-radius-map-not-runtime-proof",
            "safeToPatchMPlayersAbove2=false",
            "Original Binary Online Mode Classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "modeRuntimeProofSlices=0",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
        ),
        LOCAL_CONTRACT: (
            "Online session scalability/mode contract",
            "1 public-safe N-player/mode-scalable session contract",
            "originalBinaryPlayerSlotsProven=2",
            "maxRetailPlayersProven=2",
            "retailSlotsProven=P1,P2",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "modeScalableArchitecturePlanned=true",
            "coOpVersusModeRuntimeProofSlices=0",
            "1 same-workstation N-slot session-security message smoke",
            "securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof",
            "sessionScopedMacCoverageProof=true",
            "rejectedSecurityCaseCount=25",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "Joined-session control-lifecycle proof",
            "sessionControlLifecycleProven=true",
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "gameInputSentBySessionControl=false",
            "P3/P4 runtime feasibility map",
            "mapProofClass=static-blast-radius-map-not-runtime-proof",
            "safeToPatchMPlayersAbove2=false",
            "Online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "modeRuntimeProofSlices=0",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
        ),
        REGISTER: (
            "1 N-player/mode-scalable session contract",
            "minimumArchitectureAcceptanceSlots=4",
            "profile-declared indexed slots",
            "maxRetailPlayersProven=2",
            "minimal-smoke-hmac-envelope-not-full-session-security-proof",
            "1 same-workstation N-slot session-security message smoke",
            "same-workstation-session-security-smoke-not-online-gameplay-proof",
            "securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof",
            "sessionScopedMacCoverageProof=true",
            "rejectedSecurityCaseCount=25",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "joined-session same-host runtime-authority proof",
            "joined-session-same-host-runtime-authority-not-online-play",
            "joinedSessionSameHostRuntimeAuthorityChainProven=true",
            "joinTicketRuntimeRelayHashMatched=true",
            "sameHostOnly=true",
            "privateProofReleaseExcludedByPolicy=true",
            "joined-session control-lifecycle proof",
            "joined-session-same-host-session-control-not-online-play",
            "sessionControlLifecycleProven=true",
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "gameInputSentBySessionControl=false",
            "P3/P4 runtime feasibility map",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "safeToPatchMPlayersAbove2=false",
            "online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "modeRuntimeProofSlices=0",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
            "same-host session-control",
            "co-op/versus mode behavior remains unproven",
        ),
        CAPABILITIES: (
            "original-binary online session scalability contract",
            "originalBinaryPlayerSlotsProven=2",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "modeScalableArchitecturePlanned=true",
            "coOpVersusModeRuntimeProofSlices=0",
            "same-workstation N-slot session-security message smoke",
            "same-workstation-session-security-smoke-not-online-gameplay-proof",
            "securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof",
            "sessionScopedMacCoverageProof=true",
            "rejectedSecurityCaseCount=25",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "joined-session same-host runtime-authority proof",
            "joined-session-same-host-runtime-authority-not-online-play",
            "joinedSessionSameHostRuntimeAuthorityChainProven=true",
            "joinTicketRuntimeRelayHashMatched=true",
            "samePhysicalMachineWslPredecessor=true",
            "sameHostOnly=true",
            "joined-session control-lifecycle proof",
            "joined-session-same-host-session-control-not-online-play",
            "sessionControlLifecycleProven=true",
            "acceptedControlActionCount=11",
            "rejectedControlCaseCount=22",
            "gameInputSentBySessionControl=false",
            "P3/P4 runtime feasibility map",
            "mapProofClass=static-blast-radius-map-not-runtime-proof",
            "safeToPatchMPlayersAbove2=false",
            "online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "modeRuntimeProofSlices=0",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
        ),
        MAPPED_SYSTEMS: (
            "Original-binary online session scalability contract",
            "profile-declared indexed slots",
            "originalBinaryPlayerSlotsProven=2",
            "minimumArchitectureAcceptanceSlots=4",
            "modeScalableContractStatus=design-only-unproven",
            "same-workstation N-slot session-security message smoke",
            "securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof",
            "sessionScopedMacCoverageProof=true",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "joined-session control-lifecycle proof",
            "sessionControlLifecycleProven=true",
            "gameInputSentBySessionControl=false",
            "P3/P4 runtime feasibility map",
            "engine-viewpoints-two",
            "runtimeProofStatus=unproven",
            "supportsOriginalBinaryRuntimeProof=false",
            "online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "sessionType-is-not-runtime-mode-proof",
        ),
    }
    for path, tokens in token_sets.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path} missing token: {token}")

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:winui-original-binary-online-session-scalability-contract") == EXPECTED_SCRIPT, "missing package scalability contract script")


def validate_repo_contract() -> dict[str, Any]:
    summary = validate_contract(CONTRACT)
    require_doc_tokens()
    return summary


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def run_self_test() -> None:
    good = read_json(CONTRACT)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "contract.json"
        write_json(path, good)
        validate_contract(path)

        bad = json.loads(json.dumps(good))
        bad["currentOriginalBinaryRuntime"]["maxRuntimePlayerSlotsProven"] = 4
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("original-binary >2 runtime overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["status"] = "online multiplayer proof accepted"
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("top-level online status overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["mustNotHardcodeExactlyTwoPlayers"] = False
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("hardcoded two-player architecture should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["schedulerPolicy"]["schedulerCardinalityProven"] = 2
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("stale two-client process cardinality should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["schedulerPolicy"]["simultaneousClientProcessesProven"] = 1
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("concurrent four-client downgrade should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["modeFamiliesPlanned"] = bad["scalableArchitecture"]["modeFamiliesPlanned"][:1]
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("missing mode families should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"].pop("sessionSecuritySmokePolicy", None)
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("missing session-security smoke policy should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["joinedSessionSameHostRuntimeAuthorityPolicy"]["publicMatchmakingProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("joined-session public matchmaking overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["joinedSessionControlLifecyclePolicy"]["gameInputSentBySessionControl"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("joined-session control game-input overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["p3p4RuntimeFeasibilityMapPolicy"]["safeToPatchMPlayersAbove2"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("P3/P4 safe-to-patch overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["p3p4RuntimeFeasibilityMapPolicy"]["acceptedOriginalBinaryGameplaySlots"] = ["P1", "P2", "P3"]
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("P3 gameplay overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["modeClassifierPolicy"]["coOpModeRuntimeProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("mode-classifier co-op overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"]["modeClassifierPolicy"]["modeRuntimeProofSlices"] = 1
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("mode-classifier runtime proof count overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["scalableArchitecture"].pop("modeClassifierPolicy", None)
        write_json(path, bad)
        try:
            validate_contract(path)
        except ScalabilityContractError:
            pass
        else:
            raise AssertionError("missing mode-classifier policy should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary online session scalability contract checker self-test: PASS")
        return 0
    if not args.check:
        raise SystemExit("use --check or --self-test")
    print(json.dumps(validate_repo_contract(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScalabilityContractError as exc:
        print(f"WinUI original-binary online session scalability contract check: FAIL: {exc}")
        raise SystemExit(2)
