#!/usr/bin/env python3
"""Validate private remote-client to copied-runtime causality proof bundles."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_private_remote_client_runtime_causality_bundle as builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness" / "original_binary_private_remote_client_runtime_causality_2026-06-20.md"
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
    r"py -3 tools\build_winui_original_binary_private_remote_client_runtime_causality_bundle.py "
    r"subagents\winui-safe-copy-live-runtime\online-host-authority-runtime-executor-20260619-focus2\host-authority-runtime-executor-proof.json "
    r"--output subagents\winui-safe-copy-live-runtime\private-remote-client-runtime-causality-20260620\private-remote-client-runtime-causality-proof.json && "
    r"py -3 tools\winui_safe_copy_online_private_remote_client_runtime_causality_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_private_remote_client_runtime_causality_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_private_remote_client_runtime_causality_check.py --check"
)


class PrivateRemoteClientRuntimeCausalityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrivateRemoteClientRuntimeCausalityError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"missing object: {key}")
    return value


def resolve_artifact_path(bundle_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    require(not candidate.is_absolute(), f"referenced artifact must be private-root-relative: {raw_path}")
    candidate = builder.PRIVATE_PROOF_ROOT / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(builder.PRIVATE_PROOF_ROOT.resolve())
    except ValueError as exc:
        raise PrivateRemoteClientRuntimeCausalityError(f"referenced artifact escapes private proof root: {raw_path}") from exc
    require(candidate.is_file(), f"referenced artifact is missing: {candidate}")
    return candidate


def public_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(builder.PRIVATE_PROOF_ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == builder.SCHEMA, "schema mismatch")
    require(bundle.get("generatedBy") == builder.HELPER, "helper mismatch")
    require(bundle.get("helperVersion") == builder.HELPER_VERSION, "helper version mismatch")
    require(bundle.get("protocolVersion") == builder.PROTOCOL, "protocol mismatch")
    require(bundle.get("causalityScope") == builder.CAUSALITY_SCOPE, "causality scope mismatch")


def require_source_artifacts(bundle: dict[str, Any], bundle_path: Path) -> tuple[Path, dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]:
    artifacts = object_at(bundle, "sourceArtifacts")
    remote_path = resolve_artifact_path(bundle_path, str(artifacts.get("privateRemoteClientProof") or ""))
    host_path = resolve_artifact_path(bundle_path, str(artifacts.get("hostAuthorityTwoClientProof") or ""))
    executor_path = resolve_artifact_path(bundle_path, str(artifacts.get("runtimeExecutorProof") or ""))
    delivery_path = resolve_artifact_path(bundle_path, str(artifacts.get("runtimeDeliveryProof") or ""))
    runtime_path = resolve_artifact_path(bundle_path, str(artifacts.get("liveRuntimeArtifact") or ""))

    require(artifacts.get("privateRemoteClientProofSha256") == executor_check.delivery.host.remote.sha256_file(remote_path), "private remote-client proof hash mismatch")
    require(artifacts.get("hostAuthorityTwoClientProofSha256") == executor_check.sha256_file(host_path), "host-authority proof hash mismatch")
    require(artifacts.get("runtimeExecutorProofSha256") == executor_check.sha256_file(executor_path), "runtime executor proof hash mismatch")
    require(artifacts.get("runtimeDeliveryProofSha256") == executor_check.sha256_file(delivery_path), "runtime delivery proof hash mismatch")
    require(artifacts.get("liveRuntimeArtifactSha256") == executor_check.sha256_file(runtime_path), "live runtime artifact hash mismatch")

    remote_summary = executor_check.delivery.host.remote.validate_bundle(remote_path, expected_controller_configuration=1)
    host_summary = executor_check.delivery.host.validate_bundle(host_path, expected_controller_configuration=1)
    executor_summary = executor_check.validate_executor_proof(executor_path)
    executor_payload = executor_check.read_json(executor_path)
    resolved_host = executor_check.resolve_path(executor_path, str(executor_payload.get("hostAuthorityTwoClientProofBundle") or ""))
    resolved_delivery = executor_check.resolve_path(executor_path, str(executor_payload.get("runtimeDeliveryProofBundle") or ""))
    resolved_runtime = executor_check.resolve_path(executor_path, str(executor_payload.get("liveRuntimeArtifact") or ""))
    require(resolved_host.resolve() == host_path.resolve(), "executor host-authority reference mismatch")
    require(resolved_delivery.resolve() == delivery_path.resolve(), "executor runtime-delivery reference mismatch")
    require(resolved_runtime.resolve() == runtime_path.resolve(), "executor live-runtime reference mismatch")
    require(Path(host_summary["privateRemoteClientProofBundle"]).resolve() == remote_path.resolve(), "host remote-client reference mismatch")
    return remote_path, remote_summary, host_path, host_summary, executor_path, executor_summary


def require_causality(
    bundle: dict[str, Any],
    *,
    remote_summary: dict[str, Any],
    host_summary: dict[str, Any],
    executor_summary: dict[str, Any],
) -> dict[str, Any]:
    causality = object_at(bundle, "privateRemoteClientRuntimeCausality")
    require(causality.get("privateRemoteClientRuntimeCausalityProven") is True, "causality flag missing")
    require(causality.get("remoteClientAcceptedCommandId") == remote_summary["acceptedCommandId"], "remote command id mismatch")
    require(causality.get("remoteClientTransport") == remote_summary["transport"], "remote transport mismatch")
    require(causality.get("remoteClientProcessModel") == remote_summary["processBoundary"]["processModel"], "remote process model mismatch")
    require(causality.get("remoteClientProcessSeparated") is True, "remote client process separation missing")
    require(causality.get("remoteClientSameWorkstationOnly") is True, "same-workstation boundary missing")
    require(causality.get("remoteClientWouldForwardToPrivateLanCommandId") == remote_summary["wouldForwardToPrivateLanCommandId"], "private LAN forward id mismatch")
    require(causality.get("hostAuthorityAcceptedCommandIds") == host_summary["acceptedCommandIds"], "host accepted command list mismatch")
    require(causality.get("hostAuthorityRelayPlanSha256") == host_summary["relayPlanSha256"], "host relay hash mismatch")
    require(causality.get("hostAuthorityUpstreamPrivateRemoteClientCommandId") == remote_summary["acceptedCommandId"], "host upstream remote command mismatch")
    require(causality.get("runtimeExecutorDerivedInputSequences") == executor_summary["derivedInputSequences"], "executor derived sequences mismatch")
    require(causality.get("runtimeExecutorHostAuthorityRelayPlanSha256") == executor_summary["hostAuthorityRelayPlanSha256"], "executor relay hash mismatch")
    require(causality.get("runtimeDeliveryHostAuthorityRelayPlanSha256") == host_summary["relayPlanSha256"], "delivery relay hash mismatch")
    require(causality.get("remoteClientToHostRelayPathMatchCount") == 1, "remote-to-host path match count mismatch")
    require(causality.get("hostRelayToRuntimeExecutorPathMatchCount") == 1, "host-to-runtime path match count mismatch")
    return causality


def require_runtime(bundle: dict[str, Any], executor_summary: dict[str, Any], *, allow_fixture: bool) -> dict[str, Any]:
    runtime = object_at(bundle, "runtimeEvidence")
    receipt_mode = runtime.get("runtimeExecutorReceiptMode")
    if allow_fixture:
        require(receipt_mode in {"live-executor-subprocess", "self-test-fixture"}, "unexpected receipt mode")
    else:
        require(receipt_mode == "live-executor-subprocess", "runtime executor must be live")
    require(runtime.get("safeCopyLaunchLevel") == 850, "safe-copy launch level mismatch")
    require(runtime.get("controllerConfiguration") == 1, "controller configuration mismatch")
    require(runtime.get("newBeaLaunchCount") == 1, "new copied BEA launch count mismatch")
    require(runtime.get("cdbAttachCount") == 1, "CDB attach count mismatch")
    require(runtime.get("visualCaptureCount") == executor_summary["visualCaptureCount"], "visual capture count mismatch")
    require(runtime.get("deliveredOriginalBinaryCommandCount") == executor_summary["deliveredOriginalBinaryCommandCount"] == 2, "delivered command count mismatch")
    require(runtime.get("hostHelperInputSent") is True, "host helper input flag missing")
    require(runtime.get("gameInputSentByRemoteClient") is False, "remote client must not claim direct game input")
    require(runtime.get("gameInputSentByHostAuthorityScheduler") is False, "scheduler must not claim direct game input")
    require(runtime.get("bridgeSendsNewNetworkInput") is False, "bridge must not claim new network input")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player proof must stay zero")
    require(runtime.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted slots mismatch")
    require(runtime.get("metadataOnlySlots") == ["P3", "P4"], "metadata slots mismatch")
    require(runtime.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected route slots mismatch")
    require(runtime.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 proof must stay false")
    return runtime


def require_nonclaims_and_release(bundle: dict[str, Any]) -> dict[str, Any]:
    nonclaims = object_at(bundle, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    release = object_at(bundle, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    for key in (
        "rawPrivateProofPathPublished",
        "rawPrivateArtifactContentPublished",
        "absolutePrivatePathPublished",
        "rawRuntimePointerPublished",
        "rawRuntimePidPublished",
        "rawCdbLogPathPublished",
        "releaseIncludedPrivateArtifact",
    ):
        require(release.get(key) is False, f"release boundary must remain false: {key}")
    return nonclaims


def validate_bundle(path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    path = path.resolve()
    bundle = read_json(path)
    require_helper_contract(bundle)
    remote_path, remote_summary, host_path, host_summary, executor_path, executor_summary = require_source_artifacts(bundle, path)
    require_causality(bundle, remote_summary=remote_summary, host_summary=host_summary, executor_summary=executor_summary)
    runtime = require_runtime(bundle, executor_summary, allow_fixture=allow_fixture)
    nonclaims = require_nonclaims_and_release(bundle)
    claim = str(bundle.get("claimBoundary") or "")
    for token in (
        "process-separated private remote-client command source",
        "copied original-BEA level-850/config-1 host-authority runtime executor proof",
        "does not prove player-ready online multiplayer",
        "second physical host",
        "multi-host LAN play",
        "native BEA netcode",
        "active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": public_path(path),
        "schemaVersion": bundle["schemaVersion"],
        "causalityScope": bundle["causalityScope"],
        "privateRemoteClientRuntimeCausalityProven": True,
        "privateRemoteClientProof": public_path(remote_path),
        "hostAuthorityTwoClientProof": public_path(host_path),
        "runtimeExecutorProof": public_path(executor_path),
        "remoteClientAcceptedCommandId": remote_summary["acceptedCommandId"],
        "remoteClientProcessSeparated": True,
        "sameWorkstationOnly": True,
        "newBeaLaunchCount": runtime["newBeaLaunchCount"],
        "cdbAttachCount": runtime["cdbAttachCount"],
        "visualCaptureCount": runtime["visualCaptureCount"],
        "deliveredOriginalBinaryCommandCount": runtime["deliveredOriginalBinaryCommandCount"],
        "hostHelperInputSent": runtime["hostHelperInputSent"],
        "acceptedOriginalBinaryGameplaySlots": runtime["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": runtime["metadataOnlySlots"],
        "nPlayerOriginalBinaryRuntimeProof": runtime["nPlayerOriginalBinaryRuntimeProof"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "multiHostLanProof": nonclaims["multiHostLanProof"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
        tmp = Path(raw_tmp)
        executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
        output_path = tmp / "wrapper" / "private-remote-client-runtime-causality-proof.json"
        summary = builder.build_bundle_from_executor(executor_path, output_path, allow_fixture_executor=True)
        require(summary["privateRemoteClientRuntimeCausalityProven"] is True, "self-test fixture was not accepted")

    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as raw_tmp:
        tmp = Path(raw_tmp)
        executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
        output_path = tmp / "wrapper" / "private-remote-client-runtime-causality-proof.json"
        builder.build_bundle_from_executor(executor_path, output_path, allow_fixture_executor=True)
        payload = read_json(output_path)
        payload["nonClaims"]["nativeBeaNetcodeProof"] = True
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        try:
            validate_bundle(output_path, allow_fixture=True)
        except PrivateRemoteClientRuntimeCausalityError:
            pass
        else:
            raise AssertionError("native netcode overclaim should fail validation")


def check_token(path: Path, token: str, failures: list[str]) -> None:
    text = read_text(path)
    if token not in text:
        failures.append(f"{path}: missing token {token!r}")


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def validate_repo() -> dict[str, Any]:
    failures: list[str] = []
    for path, tokens in {
        READINESS: (
            builder.SCHEMA,
            builder.CAUSALITY_SCOPE,
            "privateRemoteClientRuntimeCausalityProven=true",
            "private-remote-client-p2-forward-0001",
            "remoteClientProcessSeparated=true",
            "sameWorkstationOnly=true",
            "newBeaLaunchCount=1",
            "cdbAttachCount=1",
            "visualCaptureCount=7",
            "deliveredOriginalBinaryCommandCount=2",
            "hostHelperInputSent=true",
            "gameInputSentByRemoteClient=false",
            "gameInputSentByHostAuthorityScheduler=false",
            "bridgeSendsNewNetworkInput=false",
            "acceptedOriginalBinaryGameplaySlots=P1,P2",
            "metadataOnlySlots=P3,P4",
            "baseOnlineMultiplayerReady=false",
            "publicMatchmakingProof=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "privateProofReleaseExcludedByPolicy=true",
            "privateProofRootRelative=true",
            "absoluteSourceArtifactPathRejected=true",
            "sourceArtifactEscapesPrivateProofRootRejected=true",
        ),
        FEASIBILITY: (
            "Private remote-client runtime-causality wrapper",
            builder.CAUSALITY_SCOPE,
            "privateRemoteClientRuntimeCausalityProven=true",
            "remoteClientProcessSeparated=true",
            "sameWorkstationOnly=true",
            "baseOnlineMultiplayerReady=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
        ),
        REGISTER: (
            "private remote-client runtime-causality wrapper",
            builder.CAUSALITY_SCOPE,
            "privateRemoteClientRuntimeCausalityProven=true",
            "private-remote-client-p2-forward-0001",
            "newBeaLaunchCount=1",
            "cdbAttachCount=1",
            "baseOnlineMultiplayerReady=false",
        ),
        CAPABILITIES: (
            "private remote-client runtime-causality wrapper",
            builder.CAUSALITY_SCOPE,
            "privateRemoteClientRuntimeCausalityProven=true",
            "remoteClientProcessSeparated=true",
            "baseOnlineMultiplayerReady=false",
        ),
        LOCAL_CONTRACT: (
            "Private remote-client runtime-causality wrapper",
            builder.CAUSALITY_SCOPE,
            "privateRemoteClientRuntimeCausalityProven=true",
            "remoteClientProcessSeparated=true",
            "gameInputSentByRemoteClient=false",
            "bridgeSendsNewNetworkInput=false",
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
    if scripts.get("test:winui-original-binary-private-remote-client-runtime-causality") != EXPECTED_SCRIPT:
        failures.append("package private remote-client runtime-causality script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-private-remote-client-runtime-causality" not in aggregate:
        failures.append("aggregate runtime script missing private remote-client runtime-causality proof")
    if not builder.DEFAULT_OUTPUT.is_file():
        failures.append(f"default private remote-client runtime-causality proof is missing: {public_path(builder.DEFAULT_OUTPUT)}")
    if failures:
        raise PrivateRemoteClientRuntimeCausalityError("\n".join(failures))
    return validate_bundle(builder.DEFAULT_OUTPUT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--allow-fixture", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        print("WinUI original-binary private remote-client runtime-causality checker self-test: PASS")
        return 0
    if args.check:
        print(json.dumps(validate_repo(), indent=2, sort_keys=True))
        return 0
    if args.proof is None:
        raise SystemExit("proof is required unless --self-test or --check is used")
    print(json.dumps(validate_bundle(args.proof, allow_fixture=args.allow_fixture), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        PrivateRemoteClientRuntimeCausalityError,
        builder.PrivateRemoteClientRuntimeCausalityBuildError,
        executor_check.HostAuthorityRuntimeExecutorError,
        executor_check.delivery.HostAuthorityRuntimeDeliveryError,
        executor_check.delivery.host.HostAuthorityTwoClientSmokeProofError,
        executor_check.delivery.host.remote.PrivateRemoteClientSmokeProofError,
    ) as exc:
        print(f"WinUI original-binary private remote-client runtime-causality check: FAIL: {exc}")
        raise SystemExit(2)
