#!/usr/bin/env python3
"""Validate joined-session runtime-causality proof for the original-binary online ladder."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_joined_session_runtime_causality_bundle as builder
import winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check as executor_check
import winui_safe_copy_online_joined_session_same_host_runtime_authority_check as joined_check


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness" / "original_binary_joined_session_runtime_causality_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
FEASIBILITY_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
LOCAL_CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCRIPT = (
    r"py -3 tools\build_winui_original_binary_joined_session_runtime_causality_bundle.py && "
    r"py -3 tools\winui_safe_copy_online_joined_session_runtime_causality_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_joined_session_runtime_causality_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_joined_session_runtime_causality_check.py --check"
)


class JoinedSessionRuntimeCausalityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise JoinedSessionRuntimeCausalityError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def public_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def resolve_artifact_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    require(raw_path and not candidate.is_absolute(), f"source artifact reference must be relative: {raw_path}")
    resolved = (bundle_path.parent / candidate).resolve()
    require(resolved.is_file(), f"referenced source artifact is missing: {resolved}")
    return resolved


def require_source_artifacts(bundle: dict[str, Any], path: Path, *, allow_fixture: bool = False) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    artifacts = object_at(bundle, "sourceArtifacts")
    joined_path = resolve_artifact_path(path, str(artifacts.get("joinedSessionAuthorityProof", "")))
    executor_path = resolve_artifact_path(path, str(artifacts.get("secureRuntimeExecutorProof", "")))
    require(artifacts.get("joinedSessionAuthorityProofSha256") == builder.sha256_file(joined_path), "joined proof hash mismatch")
    require(artifacts.get("secureRuntimeExecutorProofSha256") == builder.sha256_file(executor_path), "secure executor proof hash mismatch")
    joined_summary = joined_check.validate_bundle(joined_path)
    executor_summary = executor_check.validate_secure_runtime_executor_proof(executor_path, allow_fixture=allow_fixture)
    executor_payload = executor_check.read_json(executor_path)
    runtime_path = builder.resolve_executor_runtime_path(executor_path, executor_payload)
    require(artifacts.get("sessionSecurityProofSha256") == executor_payload["sessionSecurityProofSha256"], "session-security hash mismatch")
    require(artifacts.get("liveRuntimeArtifactSha256") == executor_payload["liveRuntimeArtifactSha256"], "live runtime hash mismatch")
    require(artifacts.get("cdbLogSha256") == builder.cdb_log_sha256(runtime_path), "CDB log hash mismatch")
    require(isinstance(artifacts.get("runtimeStateSummarySha256"), str) and len(artifacts["runtimeStateSummarySha256"]) == 64, "runtime state digest missing")
    joined_payload = joined_check.read_json(joined_path)
    return joined_summary, executor_summary, joined_payload


def require_joined_causality(bundle: dict[str, Any], joined_summary: dict[str, Any], executor_summary: dict[str, Any], joined_payload: dict[str, Any]) -> dict[str, Any]:
    causality = object_at(bundle, "joinedSessionCausality")
    joined_session = object_at(joined_payload, "joinedSession")
    require(causality.get("joinedSessionRuntimeCausalityProven") is True, "causality flag missing")
    require(causality.get("joinedSessionAuthorityProofValidated") is True, "joined proof validation flag missing")
    require(causality.get("freshRuntimeExecutorProofValidated") is True, "fresh runtime validation flag missing")
    require(causality.get("joinTicketRuntimeRelayPathMatchCount") == 1, "join-ticket runtime relay-path match count mismatch")
    require(causality.get("acceptedJoinTicketSlot") == joined_summary["acceptedJoinTicketSlot"] == "P2", "accepted ticket slot mismatch")
    require(causality.get("acceptedJoinTicketFingerprint") == joined_session.get("acceptedJoinTicketFingerprint"), "accepted ticket fingerprint mismatch")
    require(isinstance(causality.get("acceptedJoinTicketFingerprint"), str) and len(causality["acceptedJoinTicketFingerprint"]) == 64, "accepted ticket fingerprint missing")
    require(causality.get("joinTicketRuntimeRelayHashMatched") is True, "relay hash link missing")
    require(causality.get("samePhysicalMachineWslPredecessor") is True, "same-machine WSL predecessor missing")
    require(causality.get("sameHostOnly") is True, "same-host flag missing")
    require(causality.get("secondPhysicalHostProof") is False, "second host must not be claimed")
    require(causality.get("runtimeCompatibleP1P2RelayHash") == executor_summary["runtimeCompatibleP1P2RelayHash"], "runtime relay hash mismatch")
    require(causality.get("derivedInputSequences") == executor_summary["derivedInputSequences"], "derived sequence mismatch")
    return causality


def require_runtime_evidence(bundle: dict[str, Any], executor_summary: dict[str, Any], *, allow_fixture: bool = False) -> dict[str, Any]:
    runtime = object_at(bundle, "runtimeEvidence")
    require(runtime.get("hostAuthorityScope") == builder.HOST_AUTHORITY_SCOPE, "host authority scope mismatch")
    require(runtime.get("receiptMode") == executor_summary["receiptMode"], "receipt mode mismatch")
    if allow_fixture:
        require(runtime.get("receiptMode") in {"live-secure-nslot-runtime-executor-subprocess", "self-test-fixture"}, "unexpected receipt mode")
    else:
        require(runtime.get("receiptMode") == "live-secure-nslot-runtime-executor-subprocess", "runtime causality proof must use a live receipt")
    require(runtime.get("securityProofScope") == executor_summary["securityProofScope"], "security scope mismatch")
    require(runtime.get("sessionSecurityRelayPlanSha256") == executor_summary["sessionSecurityRelayPlanSha256"], "session relay hash mismatch")
    require(runtime.get("acceptedOriginalBinaryGameplaySlots") == builder.ACTIVE_SLOTS, "active slots mismatch")
    require(runtime.get("metadataOnlySlots") == builder.METADATA_SLOTS, "metadata slots mismatch")
    require(runtime.get("rejectedGameplayRouteSlots") == builder.METADATA_SLOTS, "rejected slots mismatch")
    require(runtime.get("safeCopyLaunchLevel") == 850, "launch level mismatch")
    require(runtime.get("controllerConfiguration") == 1, "controller config mismatch")
    require(runtime.get("newBeaLaunchCount") == executor_summary["newBeaLaunchCount"] == 1, "BEA launch count mismatch")
    require(runtime.get("cdbAttachCount") == executor_summary["cdbAttachCount"] == 1, "CDB attach count mismatch")
    require(runtime.get("visualCaptureCount") == executor_summary["visualCaptureCount"], "visual capture count mismatch")
    if allow_fixture:
        require(isinstance(runtime.get("visualCaptureCount"), int) and runtime["visualCaptureCount"] > 0, "fixture visual capture count must be positive")
    else:
        require(runtime.get("visualCaptureCount") == 7, "live visual capture count mismatch")
    require(runtime.get("deliveredOriginalBinaryCommandCount") == executor_summary["deliveredOriginalBinaryCommandCount"] == 2, "delivered command count mismatch")
    require(runtime.get("hostHelperInputSent") is True, "host-helper input flag missing")
    for key in (
        "gameInputSentByJoinedSessionClient",
        "gameInputSentByDirectory",
        "gameInputSentByWslClient",
        "gameInputSentByNSlotScheduler",
        "visibleMovementDeltaClaim",
        "joinedSessionVisibleMovementCausalityProof",
        "activeP3P4OriginalBinaryGameplayProof",
    ):
        require(runtime.get(key) is False, f"{key} must stay false")
    require(runtime.get("stateAuthorityGraphProven") is True, "state-authority graph flag missing")
    require(runtime.get("exactPidCdbStateRowsProven") is True, "exact-PID CDB state flag missing")
    require(runtime.get("waitWindowsClean") is True, "wait windows must be clean")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player proof must stay zero")
    return runtime


def require_slot_boundary(bundle: dict[str, Any]) -> dict[str, Any]:
    slot = object_at(bundle, "slotBoundary")
    require(slot.get("slotCapacity") == 4, "slot capacity mismatch")
    require(slot.get("acceptedOriginalBinaryGameplaySlots") == builder.ACTIVE_SLOTS, "active slots mismatch")
    require(slot.get("metadataOnlySlots") == builder.METADATA_SLOTS, "metadata slots mismatch")
    require(slot.get("rejectedGameplayRouteSlots") == builder.METADATA_SLOTS, "rejected slots mismatch")
    require(slot.get("maxOriginalBinaryActiveSlotsProven") == 2, "max active slots must stay two")
    require(slot.get("beyondTwoPlayersRequiresNewProofClass") is True, "beyond-two proof-class flag missing")
    require(slot.get("permanentImpossibilityClaim") is False, "permanent impossibility must not be claimed")
    return slot


def require_nonclaims_and_release(bundle: dict[str, Any]) -> dict[str, Any]:
    nonclaims = object_at(bundle, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    boundary = object_at(bundle, "releaseBoundary")
    require(boundary.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    for key in (
        "rawPrivateProofPathPublished",
        "rawPrivateArtifactContentPublished",
        "absolutePrivatePathPublished",
        "rawRuntimePointerPublished",
        "rawRuntimePidPublished",
        "rawCdbLogPathPublished",
        "releaseIncludedPrivateArtifact",
    ):
        require(boundary.get(key) is False, f"release boundary must stay false: {key}")
    return nonclaims


def validate_bundle(path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    path = path.resolve()
    bundle = read_json(path)
    require(bundle.get("schemaVersion") == builder.SCHEMA, "schema mismatch")
    require(bundle.get("generatedBy") == builder.HELPER, "helper mismatch")
    require(bundle.get("helperVersion") == builder.HELPER_VERSION, "helper version mismatch")
    require(bundle.get("protocolVersion") == builder.PROTOCOL, "protocol mismatch")
    require(bundle.get("causalityScope") == builder.CAUSALITY_SCOPE, "causality scope mismatch")
    require(bundle.get("hostAuthorityModel") == builder.HOST_AUTHORITY_MODEL, "host model mismatch")
    require(bundle.get("runtimeProfile") == builder.RUNTIME_PROFILE, "runtime profile mismatch")
    joined_summary, executor_summary, joined_payload = require_source_artifacts(bundle, path, allow_fixture=allow_fixture)
    require_joined_causality(bundle, joined_summary, executor_summary, joined_payload)
    runtime = require_runtime_evidence(bundle, executor_summary, allow_fixture=allow_fixture)
    slot = require_slot_boundary(bundle)
    nonclaims = require_nonclaims_and_release(bundle)
    claim = str(bundle.get("claimBoundary", ""))
    for token in (
        "same-host joined-session runtime causality",
        "one fresh copied BEA level-850/config-1 secure N-slot runtime executor run",
        "does not prove base online multiplayer readiness",
        "second physical host",
        "public matchmaking",
        "native BEA netcode",
        "active P3/P4 original-binary gameplay",
        "joined-session visible movement causality",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": public_path(path),
        "schemaVersion": bundle["schemaVersion"],
        "causalityScope": bundle["causalityScope"],
        "joinedSessionRuntimeCausalityProven": True,
        "joinTicketRuntimeRelayPathMatchCount": 1,
        "acceptedJoinTicketSlot": "P2",
        "sameHostOnly": True,
        "newBeaLaunchCount": runtime["newBeaLaunchCount"],
        "cdbAttachCount": runtime["cdbAttachCount"],
        "visualCaptureCount": runtime["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": runtime["deliveredOriginalBinaryCommandCount"],
        "hostHelperInputSent": runtime["hostHelperInputSent"],
        "gameInputSentByJoinedSessionClient": runtime["gameInputSentByJoinedSessionClient"],
        "gameInputSentByNSlotScheduler": runtime["gameInputSentByNSlotScheduler"],
        "exactPidCdbStateRowsProven": runtime["exactPidCdbStateRowsProven"],
        "acceptedOriginalBinaryGameplaySlots": slot["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": slot["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": slot["rejectedGameplayRouteSlots"],
        "nPlayerOriginalBinaryRuntimeProof": runtime["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": runtime["activeP3P4OriginalBinaryGameplayProof"],
        "publicMatchmakingProof": nonclaims["publicMatchmakingProof"],
        "multiHostLanProof": nonclaims["multiHostLanProof"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
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
            builder.CAUSALITY_SCOPE,
            "joinedSessionRuntimeCausalityProven=true",
            "joinTicketRuntimeRelayPathMatchCount=1",
            "joinTicketRuntimeRelayHashMatched=true",
            "samePhysicalMachineWslPredecessor=true",
            "newBeaLaunchCount=1",
            "cdbAttachCount=1",
            "exactPidCdbStateRowsProven=true",
            "visibleMovementDeltaClaim=false",
            "acceptedOriginalBinaryGameplaySlots=P1,P2",
            "metadataOnlySlots=P3,P4",
            "rejectedGameplayRouteSlots=P3,P4",
            "baseOnlineMultiplayerReady=false",
            "publicMatchmakingProof=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "joinedSessionVisibleMovementCausalityProof=false",
            "privateProofReleaseExcludedByPolicy=true",
        ),
        FEASIBILITY: (
            "Joined-session runtime-causality proof",
            builder.CAUSALITY_SCOPE,
            "joinedSessionRuntimeCausalityProven=true",
            "joinTicketRuntimeRelayPathMatchCount=1",
            "joinTicketRuntimeRelayHashMatched=true",
            "samePhysicalMachineWslPredecessor=true",
            "newBeaLaunchCount=1",
            "cdbAttachCount=1",
            "baseOnlineMultiplayerReady=false",
            "publicMatchmakingProof=false",
        ),
        REGISTER: (
            "joined-session runtime-causality proof",
            builder.CAUSALITY_SCOPE,
            "newBeaLaunchCount=1",
            "cdbAttachCount=1",
            "exactPidCdbStateRowsProven=true",
            "joinedSessionVisibleMovementCausalityProof=false",
        ),
        CAPABILITIES: (
            "joined-session runtime-causality proof",
            builder.CAUSALITY_SCOPE,
            "joinedSessionRuntimeCausalityProven=true",
            "joinTicketRuntimeRelayPathMatchCount=1",
            "newBeaLaunchCount=1",
            "baseOnlineMultiplayerReady=false",
        ),
        LOCAL_CONTRACT: (
            "Latest joined-session runtime-causality proof",
            builder.CAUSALITY_SCOPE,
            "joinTicketRuntimeRelayPathMatchCount=1",
            "newBeaLaunchCount=1",
            "cdbAttachCount=1",
            "joinedSessionVisibleMovementCausalityProof=false",
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
    if read_text(LOCAL_CONTRACT) != read_text(LOCAL_CONTRACT_MIRROR):
        failures.append("local multiplayer contract lore mirror mismatch")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-joined-session-runtime-causality") != EXPECTED_SCRIPT:
        failures.append("package joined-session runtime-causality script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-joined-session-runtime-causality" not in aggregate:
        failures.append("aggregate runtime script missing joined-session runtime-causality proof")
    if not builder.DEFAULT_OUTPUT.is_file():
        failures.append(f"default joined-session runtime-causality proof is missing: {public_path(builder.DEFAULT_OUTPUT)}")
    if failures:
        raise JoinedSessionRuntimeCausalityError("\n".join(failures))


def make_fixture(root: Path) -> Path:
    joined_path = joined_check.make_fixture(root / "joined")
    executor_path = executor_check.make_fixture(root / "executor")
    output_path = root / "joined-session-runtime-causality-proof.json"
    builder.build_bundle_from_artifacts(joined_path, executor_path, output_path, allow_fixture_executor=True)
    return output_path


def run_self_test() -> None:
    private_root = builder.PRIVATE_ROOT
    private_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=private_root) as tmp:
        path = make_fixture(Path(tmp))
        validate_bundle(path, allow_fixture=True)

    for name, mutate in (
        ("online-ready claim should fail", lambda value: value["nonClaims"].__setitem__("baseOnlineMultiplayerReady", True)),
        ("P3 gameplay claim should fail", lambda value: value["runtimeEvidence"].__setitem__("activeP3P4OriginalBinaryGameplayProof", True)),
        ("visible causality overclaim should fail", lambda value: value["runtimeEvidence"].__setitem__("joinedSessionVisibleMovementCausalityProof", True)),
        ("visible movement delta claim should fail", lambda value: value["runtimeEvidence"].__setitem__("visibleMovementDeltaClaim", True)),
        ("multi-host LAN claim should fail", lambda value: value["nonClaims"].__setitem__("multiHostLanProof", True)),
        ("native netcode claim should fail", lambda value: value["nonClaims"].__setitem__("nativeBeaNetcodeProof", True)),
        ("public server claim should fail", lambda value: value["nonClaims"].__setitem__("publicServerProof", True)),
        ("second host claim should fail", lambda value: value["nonClaims"].__setitem__("secondPhysicalHostProof", True)),
        ("joined client direct input should fail", lambda value: value["runtimeEvidence"].__setitem__("gameInputSentByJoinedSessionClient", True)),
        ("missing fresh launch should fail", lambda value: value["runtimeEvidence"].__setitem__("newBeaLaunchCount", 0)),
        ("wrong accepted slot should fail", lambda value: value["joinedSessionCausality"].__setitem__("acceptedJoinTicketSlot", "P3")),
        ("fake ticket fingerprint should fail", lambda value: value["joinedSessionCausality"].__setitem__("acceptedJoinTicketFingerprint", "0" * 64)),
        ("absolute source reference should fail", lambda value: value["sourceArtifacts"].__setitem__("secureRuntimeExecutorProof", str((ROOT / "bad.json").resolve()))),
    ):
        with tempfile.TemporaryDirectory(dir=private_root) as tmp:
            path = make_fixture(Path(tmp))
            payload = read_json(path)
            mutate(payload)
            write_json(path, payload)
            try:
                validate_bundle(path, allow_fixture=True)
            except JoinedSessionRuntimeCausalityError:
                continue
            raise JoinedSessionRuntimeCausalityError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary joined-session runtime-causality checker self-test: PASS")
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
    except (
        JoinedSessionRuntimeCausalityError,
        builder.JoinedSessionRuntimeCausalityBuildError,
        joined_check.JoinedSessionRuntimeAuthorityError,
        executor_check.SecureNSlotRuntimeExecutorProofError,
    ) as exc:
        print(f"WinUI original-binary joined-session runtime-causality check: FAIL: {exc}")
        raise SystemExit(2)
