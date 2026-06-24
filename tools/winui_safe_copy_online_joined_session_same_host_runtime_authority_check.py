#!/usr/bin/env python3
"""Validate joined-session same-host runtime-authority proof for the original-binary online ladder."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_joined_session_same_host_runtime_authority_bundle as builder
import build_winui_original_binary_online_session_directory_smoke_bundle as directory_builder
import winui_safe_copy_online_session_directory_smoke_check as directory_check
import winui_safe_copy_online_wsl_remote_client_smoke_check as wsl_check


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness" / "original_binary_joined_session_same_host_runtime_authority_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
FEASIBILITY_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCRIPT = (
    r"npm run test:winui-original-binary-online-session-directory-smoke && "
    r"npm run test:winui-original-binary-wsl-remote-client-smoke && "
    r"py -3 tools\build_winui_original_binary_joined_session_same_host_runtime_authority_bundle.py && "
    r"py -3 tools\winui_safe_copy_online_joined_session_same_host_runtime_authority_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_joined_session_same_host_runtime_authority_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_joined_session_same_host_runtime_authority_check.py --check"
)


class JoinedSessionRuntimeAuthorityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise JoinedSessionRuntimeAuthorityError(message)


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


def public_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def resolve_artifact_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    require(raw_path and not candidate.is_absolute(), f"source artifact reference must be relative: {raw_path}")
    candidate = bundle_path.parent / candidate
    candidate = candidate.resolve()
    require(candidate.is_file(), f"referenced source artifact is missing: {candidate}")
    return candidate


def require_source_artifacts(bundle: dict[str, Any], path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    artifacts = object_at(bundle, "sourceArtifacts")
    directory_path = resolve_artifact_path(path, str(artifacts.get("sessionDirectoryProof", "")))
    wsl_path = resolve_artifact_path(path, str(artifacts.get("wslRemoteClientProof", "")))
    require(artifacts.get("sessionDirectoryProofSha256") == builder.sha256_file(directory_path), "session-directory proof hash mismatch")
    require(artifacts.get("wslRemoteClientProofSha256") == builder.sha256_file(wsl_path), "WSL proof hash mismatch")
    directory_summary = directory_check.validate_bundle(directory_path)
    wsl_summary = wsl_check.validate_bundle(wsl_path)
    return directory_summary, wsl_summary, read_json(directory_path), read_json(wsl_path)


def require_source_proofs(bundle: dict[str, Any]) -> dict[str, Any]:
    source = object_at(bundle, "sourceProofs")
    require(source.get("sessionDirectorySchema") == directory_builder.SCHEMA, "session-directory schema mismatch")
    require(source.get("directoryScope") == directory_builder.DIRECTORY_SCOPE, "directory scope mismatch")
    require(source.get("wslRemoteClientSchema") == wsl_check.EXPECTED_SCHEMA, "WSL schema mismatch")
    require(source.get("wslRemoteClientTransport") == wsl_check.EXPECTED_TRANSPORT, "WSL transport mismatch")
    require(source.get("sessionSecurityProofSha256") == builder.SESSION_SECURITY_PROOF_SHA256, "session-security hash mismatch")
    require(source.get("nSlotRelayPlanSha256") == builder.N_SLOT_RELAY_PLAN_SHA256, "N-slot relay hash mismatch")
    require(source.get("runtimeCompatibleP1P2RelayHash") == builder.RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256, "runtime relay hash mismatch")
    require(source.get("secureExecutorReplayabilityProofHashes") == builder.SECURE_EXECUTOR_REPLAYABILITY_PROOF_SHA256_VALUES, "secure executor proof hashes mismatch")
    require(source.get("stateAuthorityReplayabilitySummarySha256") == builder.STATE_AUTHORITY_REPLAYABILITY_SUMMARY_SHA256, "state-authority summary hash mismatch")
    require(source.get("stateAuthorityObserverProofHashes") == builder.STATE_AUTHORITY_OBSERVER_PROOF_SHA256_VALUES, "state-authority observer hashes mismatch")
    require(source.get("stateAuthorityLiveRuntimeArtifactHashes") == builder.STATE_AUTHORITY_LIVE_RUNTIME_SHA256_VALUES, "state-authority runtime hashes mismatch")
    return source


def directory_ticket_and_session(directory_bundle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    sessions = list_at(directory_bundle, "registeredSessions")
    require(len(sessions) == 1 and isinstance(sessions[0], dict), "directory proof must contain one registered session")
    tickets = object_at(directory_bundle, "joinTickets")
    accepted_tickets = list_at(tickets, "accepted")
    require(len(accepted_tickets) == 1 and isinstance(accepted_tickets[0], dict), "directory proof must contain one accepted ticket")
    accepted_queries = list_at(object_at(directory_bundle, "queries"), "accepted")
    require(len(accepted_queries) == 1 and isinstance(accepted_queries[0], dict), "directory proof must contain one accepted query")
    returned = list_at(accepted_queries[0], "returnedListings")
    require(len(returned) == 1 and isinstance(returned[0], dict), "directory proof must contain one returned listing")
    return accepted_tickets[0], sessions[0], returned[0]


def require_joined_session(
    bundle: dict[str, Any],
    directory_summary: dict[str, Any],
    wsl_summary: dict[str, Any],
    directory_bundle: dict[str, Any],
    wsl_bundle: dict[str, Any],
) -> dict[str, Any]:
    ticket, directory_session, returned_listing = directory_ticket_and_session(directory_bundle)
    wsl_descriptor = object_at(wsl_bundle, "sessionDescriptor")
    wsl_commands = object_at(wsl_bundle, "commands")
    accepted_wsl = list_at(wsl_commands, "accepted")
    require(len(accepted_wsl) == 1 and isinstance(accepted_wsl[0], dict), "WSL proof must contain one accepted command")
    accepted_command = accepted_wsl[0]
    joined = object_at(bundle, "joinedSession")
    require(joined.get("joinedSessionSameHostRuntimeAuthorityChainProven") is True, "joined-session chain flag missing")
    require(joined.get("acceptedJoinTicketSlot") == ticket.get("clientSlot") == "P2", "accepted join ticket must target source P2 ticket")
    require(joined.get("acceptedJoinTicketFingerprint") == ticket.get("ticketFingerprint"), "join-ticket fingerprint mismatch")
    require(isinstance(joined.get("acceptedJoinTicketFingerprint"), str) and len(joined["acceptedJoinTicketFingerprint"]) == 64, "join-ticket fingerprint missing")
    require(joined.get("joinTicketRuntimeRelayHashMatched") is True, "join-ticket relay hash link missing")
    require(joined.get("acceptedWslCommandId") == accepted_command.get("commandId") == wsl_check.EXPECTED_COMMAND_ID, "WSL accepted command mismatch")
    require(joined.get("wslTransport") == wsl_check.EXPECTED_TRANSPORT, "WSL transport mismatch")
    require(joined.get("wslNetworkScope") == wsl_summary["networkScope"], "WSL network scope mismatch")
    require(joined.get("samePhysicalMachineWslPredecessor") is True, "WSL same-physical-machine predecessor flag missing")
    require(joined.get("sameHostOnly") is True, "joined session must stay same-host only")
    require(joined.get("secondPhysicalHostProof") is False, "joined session must not claim second physical host")
    require(directory_summary["acceptedJoinTicketCount"] == 1, "directory proof must have one accepted join ticket")
    require(directory_session.get("sessionId") == ticket.get("sessionId"), "directory ticket session mismatch")
    require(returned_listing.get("sessionId") == ticket.get("sessionId"), "returned listing session mismatch")
    require(directory_session.get("cleanSpecimenSha256") == wsl_descriptor.get("cleanSpecimenSha256"), "clean specimen mismatch")
    require(directory_session.get("levelId") == wsl_descriptor.get("levelId") == 850, "level mismatch")
    require(directory_session.get("controllerConfiguration") == wsl_descriptor.get("controllerConfiguration") == 1, "controller configuration mismatch")
    require(directory_session.get("runtimeCompatibleP1P2RelayHash") == builder.RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256, "directory runtime relay hash mismatch")
    require(returned_listing.get("runtimeCompatibleP1P2RelayHash") == builder.RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256, "returned listing runtime relay hash mismatch")
    require(wsl_descriptor.get("allowedOriginalBinaryGameplaySlots") == builder.ACTIVE_SLOTS, "WSL active slot mismatch")
    require(wsl_descriptor.get("metadataOnlySlots") == builder.METADATA_SLOTS, "WSL metadata slot mismatch")
    require(wsl_descriptor.get("rejectedGameplayRouteSlots") == builder.METADATA_SLOTS, "WSL rejected route mismatch")
    require(accepted_command.get("remoteSlot") == ticket.get("clientSlot") == "P2", "WSL command/ticket slot mismatch")
    require(accepted_command.get("wouldForwardToPrivateLanCommandId") == wsl_check.EXPECTED_PRIVATE_LAN_COMMAND_ID, "WSL forward command mismatch")
    require(wsl_descriptor.get("mappedInputSequence") == wsl_check.EXPECTED_MAPPED_SEQUENCE, "WSL mapped input sequence mismatch")
    return joined


def require_runtime_authority(bundle: dict[str, Any]) -> dict[str, Any]:
    runtime = object_at(bundle, "runtimeAuthority")
    require(runtime.get("hostAuthorityScope") == builder.HOST_AUTHORITY_SCOPE, "host-authority scope mismatch")
    require(runtime.get("stateAuthorityGraphProven") is True, "state-authority graph flag missing")
    require(runtime.get("stateAuthorityReplayabilityProven") is True, "state-authority replayability flag missing")
    require(runtime.get("secureNSlotRuntimeExecutorReplayabilityProven") is True, "secure executor replayability flag missing")
    require(runtime.get("acceptedOriginalBinaryGameplaySlots") == builder.ACTIVE_SLOTS, "accepted gameplay slots mismatch")
    require(runtime.get("metadataOnlySlots") == builder.METADATA_SLOTS, "metadata-only slots mismatch")
    require(runtime.get("rejectedGameplayRouteSlots") == builder.METADATA_SLOTS, "rejected gameplay slots mismatch")
    require(runtime.get("maxOriginalBinaryActiveSlotsProven") == 2, "max active slots must stay two")
    require(runtime.get("derivedInputSequences") == builder.SEQUENCES, "derived sequence mismatch")
    require(runtime.get("waitWindowsClean") is True, "wait windows must be clean")
    require(runtime.get("visualCaptureCountPerRuntimeProof") == 7, "visual capture count mismatch")
    require(runtime.get("visibleMovementReferenceAccepted") is True, "visible movement reference flag missing")
    require(runtime.get("visibleMovementReferenceArtifacts") == builder.VISIBLE_MOVEMENT_REFERENCE_ARTIFACTS, "visible movement references mismatch")
    require(runtime.get("joinedSessionVisibleMovementCausalityProof") is False, "joined-session visible causality must remain unclaimed")
    for key in (
        "p1QButton31ReceiveRowsPerProof",
        "p1QForwardStateStoreRowsPerProof",
        "p2EButton31ReceiveRowsPerProof",
        "p2EForwardStateStoreRowsPerProof",
    ):
        require(isinstance(runtime.get(key), int) and runtime[key] > 0, f"missing runtime row count: {key}")
    return runtime


def require_counts_and_nonclaims(bundle: dict[str, Any], directory_summary: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    counts = object_at(bundle, "counts")
    require(counts.get("registeredSessionCount") == directory_summary["registeredSessionCount"] == 1, "registered session count mismatch")
    require(counts.get("compatibleListingCount") == directory_summary["compatibleListingCount"] == 1, "compatible listing count mismatch")
    require(counts.get("acceptedJoinTicketCount") == directory_summary["acceptedJoinTicketCount"] == 1, "join-ticket count mismatch")
    require(counts.get("rejectedDirectoryCaseCount") == directory_summary["rejectedDirectoryCaseCount"] == 14, "directory rejection count mismatch")
    require(counts.get("wslAcceptedCommandCount") == 1, "WSL accepted command count mismatch")
    require(counts.get("secureExecutorReplayabilityProofCount") == 2, "secure executor replayability proof count mismatch")
    require(counts.get("stateAuthorityReplayabilityProofCount") == 2, "state-authority proof count mismatch")
    require(counts.get("wrapperNewBeaLaunchCount") == 0, "wrapper must not launch BEA")
    require(counts.get("wrapperCdbAttachCount") == 0, "wrapper must not attach CDB")
    require(counts.get("upstreamNewBeaLaunchCountPerProof") == 1, "upstream BEA launch count mismatch")
    require(counts.get("upstreamCdbAttachCountPerProof") == 1, "upstream CDB attach count mismatch")
    require(counts.get("hostHelperInputSentByAcceptedRuntimeAuthority") is True, "accepted runtime authority must carry host-helper input")
    for key in ("gameInputSentByDirectory", "gameInputSentByWslClient", "gameInputSentByNSlotScheduler", "activeP3P4OriginalBinaryGameplayProof"):
        require(counts.get(key) is False, f"{key} must stay false")
    require(counts.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    nonclaims = object_at(bundle, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    return counts, nonclaims


def require_release_boundary(bundle: dict[str, Any]) -> None:
    boundary = object_at(bundle, "releaseBoundary")
    require(boundary.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    for key in ("rawPrivateProofPathPublished", "rawPrivateArtifactContentPublished", "absolutePrivatePathPublished", "releaseIncludedPrivateArtifact"):
        require(boundary.get(key) is False, f"release boundary must stay false: {key}")


def validate_bundle(path: Path) -> dict[str, Any]:
    path = path.resolve()
    bundle = read_json(path)
    require(bundle.get("schemaVersion") == builder.SCHEMA, "schema mismatch")
    require(bundle.get("generatedBy") == builder.HELPER, "helper mismatch")
    require(bundle.get("helperVersion") == builder.HELPER_VERSION, "helper version mismatch")
    require(bundle.get("protocolVersion") == builder.PROTOCOL, "protocol mismatch")
    require(bundle.get("joinedSessionScope") == builder.JOINED_SCOPE, "joined-session scope mismatch")
    require(bundle.get("hostAuthorityModel") == builder.HOST_AUTHORITY_MODEL, "host-authority model mismatch")
    require(bundle.get("runtimeProfile") == builder.RUNTIME_PROFILE, "runtime profile mismatch")
    directory_summary, wsl_summary, directory_bundle, wsl_bundle = require_source_artifacts(bundle, path)
    require_source_proofs(bundle)
    require_joined_session(bundle, directory_summary, wsl_summary, directory_bundle, wsl_bundle)
    runtime = require_runtime_authority(bundle)
    counts, nonclaims = require_counts_and_nonclaims(bundle, directory_summary)
    require_release_boundary(bundle)
    claim = str(bundle.get("claimBoundary", ""))
    for token in (
        "same-host joined-session runtime-authority chain",
        "does not prove a second physical host",
        "multi-host LAN play",
        "public matchmaking",
        "native BEA netcode",
        "active P3/P4 original-binary gameplay",
        "joined-session visible movement causality",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": public_path(path),
        "schemaVersion": bundle["schemaVersion"],
        "joinedSessionScope": bundle["joinedSessionScope"],
        "joinedSessionSameHostRuntimeAuthorityChainProven": True,
        "acceptedJoinTicketSlot": "P2",
        "joinTicketRuntimeRelayHashMatched": True,
        "hostAuthorityScope": runtime["hostAuthorityScope"],
        "stateAuthorityGraphProven": runtime["stateAuthorityGraphProven"],
        "stateAuthorityReplayabilityProven": runtime["stateAuthorityReplayabilityProven"],
        "secureNSlotRuntimeExecutorReplayabilityProven": runtime["secureNSlotRuntimeExecutorReplayabilityProven"],
        "acceptedOriginalBinaryGameplaySlots": runtime["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": runtime["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": runtime["rejectedGameplayRouteSlots"],
        "wrapperNewBeaLaunchCount": counts["wrapperNewBeaLaunchCount"],
        "wrapperCdbAttachCount": counts["wrapperCdbAttachCount"],
        "hostHelperInputSentByAcceptedRuntimeAuthority": counts["hostHelperInputSentByAcceptedRuntimeAuthority"],
        "gameInputSentByDirectory": counts["gameInputSentByDirectory"],
        "gameInputSentByWslClient": counts["gameInputSentByWslClient"],
        "gameInputSentByNSlotScheduler": counts["gameInputSentByNSlotScheduler"],
        "publicMatchmakingProof": nonclaims["publicMatchmakingProof"],
        "multiHostLanProof": nonclaims["multiHostLanProof"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "nPlayerOriginalBinaryRuntimeProof": counts["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": counts["activeP3P4OriginalBinaryGameplayProof"],
        "joinedSessionVisibleMovementCausalityProof": runtime["joinedSessionVisibleMovementCausalityProof"],
    }


def check_token(path: Path, token: str, failures: list[str]) -> None:
    if token not in read_text(path):
        failures.append(f"{path}: missing token {token!r}")


def validate_repo() -> None:
    failures: list[str] = []
    for path, tokens in {
        READINESS: (
            builder.SCHEMA,
            builder.JOINED_SCOPE,
            "joinedSessionSameHostRuntimeAuthorityChainProven=true",
            "acceptedJoinTicketSlot=P2",
            "joinTicketRuntimeRelayHashMatched=true",
            "samePhysicalMachineWslPredecessor=true",
            "sameHostOnly=true",
            "secondPhysicalHostProof=false",
            "hostAuthorityModel=single-host-authoritative-copied-session",
            "hostAuthorityScope=single-copied-host-exact-pid-state-graph",
            "acceptedOriginalBinaryGameplaySlots=P1,P2",
            "metadataOnlySlots=P3,P4",
            "rejectedGameplayRouteSlots=P3,P4",
            "hostHelperInputSentByAcceptedRuntimeAuthority=true",
            "wrapperNewBeaLaunchCount=0",
            "wrapperCdbAttachCount=0",
            "publicMatchmakingProof=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "joinedSessionVisibleMovementCausalityProof=false",
            "privateProofReleaseExcludedByPolicy=true",
        ),
        FEASIBILITY: (
            "Joined-session same-host runtime-authority proof",
            builder.JOINED_SCOPE,
            "joinedSessionSameHostRuntimeAuthorityChainProven=true",
            "samePhysicalMachineWslPredecessor=true",
            "sameHostOnly=true",
            "secondPhysicalHostProof=false",
            "hostAuthorityModel=single-host-authoritative-copied-session",
            "publicMatchmakingProof=false",
        ),
        REGISTER: (
            "joined-session same-host runtime-authority proof",
            builder.JOINED_SCOPE,
            "hostHelperInputSentByAcceptedRuntimeAuthority=true",
            "joinedSessionVisibleMovementCausalityProof=false",
            "sameHostOnly=true",
            "privateProofReleaseExcludedByPolicy=true",
        ),
        CAPABILITIES: (
            "joined-session same-host runtime-authority proof",
            builder.JOINED_SCOPE,
            "joinTicketRuntimeRelayHashMatched=true",
            "samePhysicalMachineWslPredecessor=true",
            "sameHostOnly=true",
            "publicMatchmakingProof=false",
        ),
    }.items():
        for token in tokens:
            check_token(path, token, failures)
    if read_text(REGISTER) != read_text(REGISTER_MIRROR):
        failures.append("register lore mirror mismatch")
    if read_text(FEASIBILITY) != read_text(FEASIBILITY_MIRROR):
        failures.append("online feasibility lore mirror mismatch")
    if read_text(CAPABILITIES) != read_text(CAPABILITIES_MIRROR):
        failures.append("current capabilities lore mirror mismatch")
    scalability = read_json(SCALABILITY)
    policy = object_at(object_at(scalability, "scalableArchitecture"), "joinedSessionSameHostRuntimeAuthorityPolicy")
    require(policy.get("proofSchema") == builder.SCHEMA, "scalability contract joined-session schema mismatch")
    require(policy.get("joinedSessionScope") == builder.JOINED_SCOPE, "scalability contract joined-session scope mismatch")
    require(policy.get("hostAuthorityModel") == builder.HOST_AUTHORITY_MODEL, "scalability contract host-authority model mismatch")
    require(policy.get("hostAuthorityScope") == builder.HOST_AUTHORITY_SCOPE, "scalability contract host-authority scope mismatch")
    require(policy.get("joinedSessionSameHostRuntimeAuthorityChainProven") is True, "scalability contract chain flag missing")
    require(policy.get("acceptedJoinTicketSlot") == "P2", "scalability contract ticket slot mismatch")
    require(policy.get("joinTicketRuntimeRelayHashMatched") is True, "scalability contract relay link mismatch")
    require(policy.get("samePhysicalMachineWslPredecessor") is True, "scalability contract same-machine WSL predecessor flag missing")
    require(policy.get("sameHostOnly") is True, "scalability contract same-host flag missing")
    require(policy.get("privateProofReleaseExcludedByPolicy") is True, "scalability contract release boundary missing")
    require(policy.get("acceptedOriginalBinaryGameplaySlots") == builder.ACTIVE_SLOTS, "scalability contract active slots mismatch")
    require(policy.get("metadataOnlySlots") == builder.METADATA_SLOTS, "scalability contract metadata slots mismatch")
    require(policy.get("rejectedGameplayRouteSlots") == builder.METADATA_SLOTS, "scalability contract rejected slots mismatch")
    for key in ("publicMatchmakingProof", "multiHostLanProof", "nativeBeaNetcodeProof", "activeP3P4OriginalBinaryGameplayProof", "joinedSessionVisibleMovementCausalityProof", "secondPhysicalHostProof"):
        require(policy.get(key) is False, f"scalability contract must keep false: {key}")
    require(policy.get("nPlayerOriginalBinaryRuntimeProof") == 0, "scalability contract N-player proof must stay zero")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-joined-session-same-host-runtime-authority") != EXPECTED_SCRIPT:
        failures.append("package joined-session script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-joined-session-same-host-runtime-authority" not in aggregate:
        failures.append("aggregate runtime script missing joined-session runtime-authority proof")
    if not builder.DEFAULT_OUTPUT.is_file():
        failures.append(f"default joined-session proof is missing: {public_path(builder.DEFAULT_OUTPUT)}")
    if failures:
        raise JoinedSessionRuntimeAuthorityError("\n".join(failures))


def make_fixture(root: Path) -> Path:
    session_path = root / "session" / "online-session-directory-smoke-proof.json"
    directory_builder.build_bundle(session_path)
    wsl_path = wsl_check.make_fixture(root / "wsl")
    output_path = root / "joined-session-same-host-runtime-authority-proof.json"
    builder.build_bundle(session_path, wsl_path, output_path)
    return output_path


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = make_fixture(Path(tmp))
        validate_bundle(path)

    for name, mutate in (
        ("public matchmaking overclaim should fail", lambda value: value["nonClaims"].__setitem__("publicMatchmakingProof", True)),
        ("P3 gameplay overclaim should fail", lambda value: value["counts"].__setitem__("activeP3P4OriginalBinaryGameplayProof", True)),
        ("joined visible movement overclaim should fail", lambda value: value["runtimeAuthority"].__setitem__("joinedSessionVisibleMovementCausalityProof", True)),
        ("wrong accepted ticket slot should fail", lambda value: value["joinedSession"].__setitem__("acceptedJoinTicketSlot", "P3")),
        ("wrapper BEA launch should fail", lambda value: value["counts"].__setitem__("wrapperNewBeaLaunchCount", 1)),
        ("direct WSL game input should fail", lambda value: value["counts"].__setitem__("gameInputSentByWslClient", True)),
        ("fake ticket fingerprint should fail", lambda value: value["joinedSession"].__setitem__("acceptedJoinTicketFingerprint", "0" * 64)),
        ("wrong WSL command should fail", lambda value: value["joinedSession"].__setitem__("acceptedWslCommandId", "wrong-command")),
        ("absolute source reference should fail", lambda value: value["sourceArtifacts"].__setitem__("sessionDirectoryProof", str((ROOT / "not-public.json").resolve()))),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_fixture(Path(tmp))
            payload = read_json(path)
            mutate(payload)
            write_json(path, payload)
            try:
                validate_bundle(path)
            except JoinedSessionRuntimeAuthorityError:
                continue
            raise JoinedSessionRuntimeAuthorityError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary joined-session same-host runtime-authority checker self-test: PASS")
        return 0
    if args.check:
        validate_repo()
        print(json.dumps(validate_bundle(builder.DEFAULT_OUTPUT), indent=2, sort_keys=True))
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test or --check is used")
    print(json.dumps(validate_bundle(args.bundle), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except JoinedSessionRuntimeAuthorityError as exc:
        print(f"WinUI original-binary joined-session same-host runtime-authority check: FAIL: {exc}")
        raise SystemExit(2)
