#!/usr/bin/env python3
"""Validate session-security provenance for an N-slot runtime bridge proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_host_authority_n_slot_session_security_smoke_bundle as security_builder
import winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check as runtime_bridge
import winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check as security


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROOF_ROOT = ROOT / "subagents"

EXPECTED_SCHEMA = "winui-original-binary-host-authority-secure-n-slot-runtime-bridge.v1"
EXPECTED_PROTOCOL = "host-authority-secure-n-slot-runtime-bridge.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-secure-n-slot-runtime-bridge"
EXPECTED_HELPER_VERSION = "host-authority-secure-n-slot-runtime-bridge.v1"
EXPECTED_SECURITY_SCOPE = security.EXPECTED_SECURITY_SCOPE
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]


class SecureNSlotRuntimeBridgeProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecureNSlotRuntimeBridgeProofError(message)


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
    root = PRIVATE_PROOF_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SecureNSlotRuntimeBridgeProofError(f"proof path must stay under ignored subagents root: {root}") from exc
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
        raise SecureNSlotRuntimeBridgeProofError(f"session-security proof rejected: {exc}") from exc

    scheduler = object_at(bundle, "hostAuthorityNSlotScheduler")
    authorization = object_at(bundle, "authorization")
    require(summary["securityProofScope"] == EXPECTED_SECURITY_SCOPE, "session-security scope mismatch")
    require(summary["sessionScopedMacCoverageProof"] is True, "session MAC coverage proof missing")
    require(summary["maxJsonLineBytesEnforced"] is True, "max JSON-line proof missing")
    require(summary["unknownFieldRejectionProof"] is True, "unknown-field proof missing")
    require(summary["strictMessageSchemaProof"] is True, "strict schema proof missing")
    require(summary["acceptedOriginalBinaryGameplayCommandCount"] == 2, "secure accepted command count mismatch")
    require(summary["metadataGameplayRejectionCount"] == 2, "secure metadata rejection count mismatch")
    require(summary["rejectedSecurityCaseCount"] == len(security.EXPECTED_SECURITY_REJECTION_CASES), "secure rejection count mismatch")
    require(summary["newBeaLaunchCount"] == 0, "session-security proof must not launch BEA")
    require(summary["cdbAttachCount"] == 0, "session-security proof must not attach CDB")
    require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "session-security N-player runtime proof must stay zero")
    require(summary["activeP3P4OriginalBinaryGameplayProof"] is False, "session-security P3/P4 gameplay proof must stay false")
    require(scheduler.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "secure active slot mismatch")
    require(scheduler.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "secure metadata slot mismatch")
    require(scheduler.get("runtimeCompatibleP1P2RelayHash") == security.EXPECTED_RUNTIME_P1P2_RELAY_HASH, "secure runtime-compatible relay hash mismatch")
    require(authorization.get("relayPlanHashMacBound") is True, "secure relay-plan hash must be MAC-bound")
    return summary, bundle


def validate_runtime_bridge(path: Path) -> dict[str, Any]:
    try:
        summary = runtime_bridge.validate_live_bridge_proof(path)
    except (runtime_bridge.HostAuthorityNSlotRuntimeBridgeError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        raise SecureNSlotRuntimeBridgeProofError(f"runtime bridge proof rejected: {exc}") from exc

    require(summary["acceptedOriginalBinaryGameplaySlots"] == EXPECTED_ACTIVE_SLOTS, "runtime bridge active slot mismatch")
    require(summary["metadataOnlySlots"] == EXPECTED_METADATA_SLOTS, "runtime bridge metadata slot mismatch")
    require(summary["rejectedGameplayRouteSlots"] == EXPECTED_METADATA_SLOTS, "runtime bridge rejected slot mismatch")
    require(summary["runtimeCompatibleP1P2RelayHash"] == security.EXPECTED_RUNTIME_P1P2_RELAY_HASH, "runtime bridge relay hash mismatch")
    require(summary["deliveredOriginalBinaryCommandCount"] == 2, "runtime bridge delivered command count mismatch")
    require(summary["hostHelperInputSent"] is True, "runtime bridge must prove host-helper input")
    require(summary["gameInputSentByNSlotScheduler"] is False, "runtime bridge must not claim scheduler direct input")
    require(summary["nPlayerOriginalBinaryRuntimeProof"] == 0, "runtime bridge N-player proof must stay zero")
    require(summary["activeP3P4OriginalBinaryGameplayProof"] is False, "runtime bridge P3/P4 gameplay proof must stay false")
    require(summary["visibleMovementDeltaClaim"] is False, "runtime bridge must not claim visible movement causality")
    return summary


def make_secure_bridge_proof(session_security_path: Path, runtime_bridge_path: Path, output_path: Path) -> dict[str, Any]:
    session_security_path = require_private_path(session_security_path, must_exist=True)
    runtime_bridge_path = require_private_path(runtime_bridge_path, must_exist=True)
    output_path = require_private_path(output_path, must_exist=False)

    security_summary, security_bundle = validate_session_security(session_security_path)
    bridge_summary = validate_runtime_bridge(runtime_bridge_path)
    secure_scheduler = object_at(security_bundle, "hostAuthorityNSlotScheduler")
    secure_relay_hash = secure_scheduler["runtimeCompatibleP1P2RelayHash"]
    runtime_relay_hash = bridge_summary["runtimeCompatibleP1P2RelayHash"]
    require(secure_relay_hash == runtime_relay_hash, "secure session relay hash does not match runtime bridge relay hash")

    proof = {
        "schemaVersion": EXPECTED_SCHEMA,
        "generatedBy": EXPECTED_HELPER,
        "helperVersion": EXPECTED_HELPER_VERSION,
        "protocolVersion": EXPECTED_PROTOCOL,
        "sessionSecurityProof": relative_path(output_path.parent, session_security_path),
        "sessionSecurityProofSha256": sha256_file(session_security_path),
        "nSlotRuntimeBridgeProof": relative_path(output_path.parent, runtime_bridge_path),
        "nSlotRuntimeBridgeProofSha256": sha256_file(runtime_bridge_path),
        "chain": {
            "secureSessionAcceptedRelayFeedsRuntimeBridge": True,
            "runtimeCompatibleP1P2RelayHashMatched": True,
            "sessionSecurityRelayPlanSha256": security_summary["relayPlanSha256"],
            "secureRuntimeCompatibleP1P2RelayHash": secure_relay_hash,
            "runtimeBridgeRuntimeCompatibleP1P2RelayHash": runtime_relay_hash,
            "acceptedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "secureSessionAcceptedCommandCount": security_summary["acceptedOriginalBinaryGameplayCommandCount"],
            "secureSessionMetadataRejectionCount": security_summary["metadataGameplayRejectionCount"],
            "secureSessionSecurityRejectionCount": security_summary["rejectedSecurityCaseCount"],
            "sourceRuntimeBridgeDeliveredOriginalBinaryCommandCount": bridge_summary["deliveredOriginalBinaryCommandCount"],
            "sourceRuntimeBridgeHostHelperInputSent": bridge_summary["hostHelperInputSent"],
            "sourceRuntimeBridgeVisualCaptureCount": bridge_summary["visualCaptureCount"],
            "wrapperNewBeaLaunchCount": 0,
            "wrapperCdbAttachCount": 0,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
        },
        "nonClaims": {
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "physicalGamepadProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "claimBoundary": (
            "Secure N-slot runtime bridge provenance proof. This links one accepted same-workstation N-slot "
            "session-security smoke to one accepted N-slot copied-runtime P1/P2 bridge by matching the "
            "runtime-compatible P1/P2 relay hash. It does not launch BEA, attach CDB, send new input, prove "
            "multi-host LAN, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, "
            "more than two original-binary runtime players, deterministic sync, rollback, anti-cheat, physical "
            "gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, proof)
    return validate_secure_bridge_proof(output_path)


def validate_secure_bridge_proof(path: Path) -> dict[str, Any]:
    path = require_private_path(path, must_exist=True)
    proof = read_json(path)
    require(proof.get("schemaVersion") == EXPECTED_SCHEMA, "secure bridge schema mismatch")
    require(proof.get("generatedBy") == EXPECTED_HELPER, "secure bridge helper mismatch")
    require(proof.get("helperVersion") == EXPECTED_HELPER_VERSION, "secure bridge helper version mismatch")
    require(proof.get("protocolVersion") == EXPECTED_PROTOCOL, "secure bridge protocol mismatch")

    session_path = resolve_path(path, str(proof.get("sessionSecurityProof", "")))
    bridge_path = resolve_path(path, str(proof.get("nSlotRuntimeBridgeProof", "")))
    require(proof.get("sessionSecurityProofSha256") == sha256_file(session_path), "session-security proof hash mismatch")
    require(proof.get("nSlotRuntimeBridgeProofSha256") == sha256_file(bridge_path), "runtime bridge proof hash mismatch")

    security_summary, security_bundle = validate_session_security(session_path)
    bridge_summary = validate_runtime_bridge(bridge_path)
    secure_scheduler = object_at(security_bundle, "hostAuthorityNSlotScheduler")
    chain = object_at(proof, "chain")
    require(chain.get("secureSessionAcceptedRelayFeedsRuntimeBridge") is True, "secure provenance flag missing")
    require(chain.get("runtimeCompatibleP1P2RelayHashMatched") is True, "relay hash match flag missing")
    require(chain.get("sessionSecurityRelayPlanSha256") == security_summary["relayPlanSha256"], "session relay plan hash drift")
    require(chain.get("secureRuntimeCompatibleP1P2RelayHash") == secure_scheduler["runtimeCompatibleP1P2RelayHash"], "secure relay hash drift")
    require(chain.get("runtimeBridgeRuntimeCompatibleP1P2RelayHash") == bridge_summary["runtimeCompatibleP1P2RelayHash"], "runtime bridge relay hash drift")
    require(chain.get("secureRuntimeCompatibleP1P2RelayHash") == chain.get("runtimeBridgeRuntimeCompatibleP1P2RelayHash"), "relay hash mismatch")
    require(chain.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "secure bridge active slot mismatch")
    require(chain.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "secure bridge metadata slot mismatch")
    require(chain.get("secureSessionAcceptedCommandCount") == 2, "secure bridge accepted count mismatch")
    require(chain.get("secureSessionMetadataRejectionCount") == 2, "secure bridge metadata count mismatch")
    require(chain.get("secureSessionSecurityRejectionCount") == len(security.EXPECTED_SECURITY_REJECTION_CASES), "secure bridge rejection count mismatch")
    require(chain.get("sourceRuntimeBridgeDeliveredOriginalBinaryCommandCount") == 2, "secure bridge delivered count mismatch")
    require(chain.get("sourceRuntimeBridgeHostHelperInputSent") is True, "secure bridge source host-helper flag missing")
    require(int(chain.get("sourceRuntimeBridgeVisualCaptureCount", 0)) >= 1, "secure bridge source visual captures missing")
    require(chain.get("wrapperNewBeaLaunchCount") == 0, "secure bridge wrapper must not launch BEA")
    require(chain.get("wrapperCdbAttachCount") == 0, "secure bridge wrapper must not attach CDB")
    require(chain.get("nPlayerOriginalBinaryRuntimeProof") == 0, "secure bridge N-player proof must stay zero")
    require(chain.get("activeP3P4OriginalBinaryGameplayProof") is False, "secure bridge P3/P4 proof must stay false")
    non_claims = object_at(proof, "nonClaims")
    for key, value in non_claims.items():
        require(value is False, f"non-claim must remain false: {key}")

    return {
        "schemaVersion": proof["schemaVersion"],
        "protocolVersion": proof["protocolVersion"],
        "artifact": str(path),
        "sessionSecurityProof": str(session_path),
        "nSlotRuntimeBridgeProof": str(bridge_path),
        "securityProofScope": security_summary["securityProofScope"],
        "secureSessionAcceptedRelayFeedsRuntimeBridge": chain["secureSessionAcceptedRelayFeedsRuntimeBridge"],
        "runtimeCompatibleP1P2RelayHashMatched": chain["runtimeCompatibleP1P2RelayHashMatched"],
        "runtimeCompatibleP1P2RelayHash": chain["secureRuntimeCompatibleP1P2RelayHash"],
        "acceptedOriginalBinaryGameplaySlots": chain["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": chain["metadataOnlySlots"],
        "rejectedGameplayRouteSlots": bridge_summary["rejectedGameplayRouteSlots"],
        "secureSessionAcceptedCommandCount": chain["secureSessionAcceptedCommandCount"],
        "secureSessionMetadataRejectionCount": chain["secureSessionMetadataRejectionCount"],
        "secureSessionSecurityRejectionCount": chain["secureSessionSecurityRejectionCount"],
        "sourceRuntimeBridgeDeliveredOriginalBinaryCommandCount": chain["sourceRuntimeBridgeDeliveredOriginalBinaryCommandCount"],
        "sourceRuntimeBridgeHostHelperInputSent": chain["sourceRuntimeBridgeHostHelperInputSent"],
        "sourceRuntimeBridgeVisualCaptureCount": chain["sourceRuntimeBridgeVisualCaptureCount"],
        "wrapperNewBeaLaunchCount": chain["wrapperNewBeaLaunchCount"],
        "wrapperCdbAttachCount": chain["wrapperCdbAttachCount"],
        "nPlayerOriginalBinaryRuntimeProof": chain["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": chain["activeP3P4OriginalBinaryGameplayProof"],
        "multiHostLanProof": non_claims["multiHostLanProof"],
        "publicMatchmakingProof": non_claims["publicMatchmakingProof"],
        "nativeBeaNetcodeProof": non_claims["nativeBeaNetcodeProof"],
        "deterministicSyncProof": non_claims["deterministicSyncProof"],
        "rollbackProof": non_claims["rollbackProof"],
        "antiCheatProof": non_claims["antiCheatProof"],
        "physicalGamepadProof": non_claims["physicalGamepadProof"],
        "claimBoundary": proof["claimBoundary"],
    }


def make_self_test_fixture(root: Path) -> Path:
    session_path = root / "session" / "host-authority-n-slot-session-security-smoke-proof.json"
    security_builder.build_bundle(session_path)
    bridge_path = runtime_bridge.make_live_bridge_fixture(root / "runtime-bridge")
    output_path = root / "secure-n-slot-runtime-bridge-proof.json"
    return Path(make_secure_bridge_proof(session_path, bridge_path, output_path)["artifact"])


def self_test() -> None:
    runtime_root = runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
    runtime_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=runtime_root) as tmp:
        summary = validate_secure_bridge_proof(make_self_test_fixture(Path(tmp)))
        require(summary["secureSessionAcceptedRelayFeedsRuntimeBridge"] is True, "self-test secure bridge flag missing")
        require(summary["runtimeCompatibleP1P2RelayHashMatched"] is True, "self-test relay hash match missing")

    with tempfile.TemporaryDirectory(dir=runtime_root) as tmp:
        root = Path(tmp)
        session_path = root / "session" / "host-authority-n-slot-session-security-smoke-proof.json"
        security_builder.build_bundle(session_path)
        bridge_path = runtime_bridge.make_live_bridge_fixture(root / "runtime-bridge")
        bridge = read_json(bridge_path)
        bridge["execution"]["runtimeCompatibleP1P2RelayHash"] = "0" * 64
        write_json(bridge_path, bridge)
        try:
            make_secure_bridge_proof(session_path, bridge_path, root / "secure-n-slot-runtime-bridge-proof.json")
        except SecureNSlotRuntimeBridgeProofError:
            pass
        else:
            raise SecureNSlotRuntimeBridgeProofError("relay mismatch should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path)
    parser.add_argument("runtime_bridge_proof", nargs="?", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI original-binary secure N-slot runtime bridge checker self-test: PASS")
        return 0
    if args.proof is not None and args.runtime_bridge_proof is not None:
        if args.output is None:
            raise SystemExit("--output is required when building from session-security and runtime-bridge proofs")
        print(json.dumps(make_secure_bridge_proof(args.proof, args.runtime_bridge_proof, args.output), indent=2, sort_keys=True))
        return 0
    if args.proof is None:
        raise SystemExit("proof is required unless --self-test is used")
    print(json.dumps(validate_secure_bridge_proof(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SecureNSlotRuntimeBridgeProofError as exc:
        print(f"WinUI original-binary secure N-slot runtime bridge check: FAIL: {exc}")
        raise SystemExit(2)
