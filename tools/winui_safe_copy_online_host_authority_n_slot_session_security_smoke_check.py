#!/usr/bin/env python3
"""Validate an N-slot host-authority session-security smoke proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-original-binary-host-authority-n-slot-session-security-smoke.v1"
EXPECTED_SESSION_SCHEMA = "winui-original-binary-host-authority-n-slot-session.v1"
EXPECTED_PROTOCOL = "host-authority-n-slot-input.v1"
EXPECTED_HELPER = "winui-original-binary-host-authority-n-slot-session-security-smoke-helper"
EXPECTED_HELPER_VERSION = "host-authority-n-slot-session-security-smoke-helper.v1"
EXPECTED_SECURITY_SCOPE = "same-workstation-session-security-smoke-not-online-gameplay-proof"
EXPECTED_COMMAND = "forward"
EXPECTED_SLOTS = ["P1", "P2", "P3", "P4"]
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
EXPECTED_P1_COMMAND_ID = "host-authority-p1-forward-0001"
EXPECTED_P2_COMMAND_ID = "host-authority-p2-forward-0001"
EXPECTED_P3_COMMAND_ID = "host-authority-p3-forward-0001"
EXPECTED_P4_COMMAND_ID = "host-authority-p4-forward-0001"
EXPECTED_P1_SEQUENCE = "down:Q,wait:500,up:Q"
EXPECTED_P2_SEQUENCE = "down:E,wait:500,up:E"
EXPECTED_RUNTIME_P1P2_RELAY_HASH = "fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376"
EXPECTED_MAX_MESSAGE_BYTES = 4096
EXPECTED_SESSION_HELLO_MAC_FIELDS = [
    "sessionId",
    "type",
    "protocolVersion",
    "compatibilityKey",
    "clientSlot",
    "clientId",
    "clientIdentityFingerprint",
    "serverIdentityFingerprint",
    "nonce",
    "timestamp",
    "sequence",
]
EXPECTED_COMMAND_MAC_FIELDS = [
    "sessionId",
    "type",
    "protocolVersion",
    "compatibilityKey",
    "clientSlot",
    "clientId",
    "scheduledTick",
    "sequence",
    "nonce",
    "timestamp",
    "commandId",
    "command",
    "mappedInputSequence",
    "relayPlanSha256",
    "directGameInputClaim",
    "publicMatchmakingClaim",
    "teamAssignment",
]
EXPECTED_ACCEPTED_CASES = {"p1-forward-accepted", "p2-forward-accepted"}
EXPECTED_METADATA_REJECTION_CASES = {"p3-forward-rejected", "p4-forward-rejected"}
EXPECTED_SECURITY_REJECTION_REASONS = {
    "unknown-field",
    "oversized-message",
    "stale-tick",
    "future-tick",
    "replay-nonce",
    "missing-relayPlanHash",
    "relayPlanHash-mismatch",
    "bad-session-mac",
    "bad-slot-credential",
    "slot-identity-mismatch",
    "slot-changed-on-connection",
    "command-before-session",
    "duplicate-session-on-connection",
    "sequence-not-next",
    "slot-rate-limit",
    "tick-rate-limit",
    "missing-required-field",
    "wrong-field-type",
    "public-matchmaking-not-allowed",
    "direct-input-not-allowed",
    "server-identity-mismatch",
    "unknown-slot",
    "invalid-team-assignment",
    "duplicate-slot-identity",
    "duplicate-client-identity",
}
EXPECTED_SECURITY_REJECTION_CASES = {
    "slot-rate-limit-rejected": ("command_rejected", "slot-rate-limit"),
    "unknown-field-rejected": ("command_rejected", "unknown-field"),
    "oversized-message-rejected": ("command_rejected", "oversized-message"),
    "stale-tick-rejected": ("command_rejected", "stale-tick"),
    "future-tick-rejected": ("command_rejected", "future-tick"),
    "replay-nonce-rejected": ("command_rejected", "replay-nonce"),
    "missing-relayPlanHash-rejected": ("command_rejected", "missing-relayPlanHash"),
    "relayPlanHash-mismatch-rejected": ("command_rejected", "relayPlanHash-mismatch"),
    "bad-session-mac-rejected": ("command_rejected", "bad-session-mac"),
    "bad-slot-credential-rejected": ("command_rejected", "bad-slot-credential"),
    "slot-identity-mismatch-rejected": ("command_rejected", "slot-identity-mismatch"),
    "slot-changed-on-connection-rejected": ("command_rejected", "slot-changed-on-connection"),
    "command-before-session-rejected": ("command_rejected", "command-before-session"),
    "duplicate-session-on-connection-rejected": ("session_rejected", "duplicate-session-on-connection"),
    "sequence-not-next-rejected": ("command_rejected", "sequence-not-next"),
    "tick-rate-limit-rejected": ("command_rejected", "tick-rate-limit"),
    "missing-required-field-rejected": ("command_rejected", "missing-required-field"),
    "wrong-field-type-rejected": ("command_rejected", "wrong-field-type"),
    "public-matchmaking-rejected": ("command_rejected", "public-matchmaking-not-allowed"),
    "direct-input-rejected": ("command_rejected", "direct-input-not-allowed"),
    "server-identity-mismatch-rejected": ("session_rejected", "server-identity-mismatch"),
    "unknown-slot-rejected": ("session_rejected", "unknown-slot"),
    "invalid-team-assignment-rejected": ("command_rejected", "invalid-team-assignment"),
    "duplicate-slot-identity-rejected": ("session_rejected", "duplicate-slot-identity"),
    "duplicate-client-identity-rejected": ("session_rejected", "duplicate-client-identity"),
}
SAFE_CREDENTIAL_METADATA_KEYS = {
    "credentialstorage",
    "rawcredentialsserialized",
    "serializedcredentialpresent",
    "slotcredentialfingerprints",
}
DANGEROUS_KEY_FRAGMENTS = ("secret", "password", "token", "authkey", "credential", "apikey", "api_key")


class HostAuthorityNSlotSessionSecuritySmokeProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityNSlotSessionSecuritySmokeProofError(message)


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


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def require_no_serialized_credentials(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            require(
                not any(fragment in lowered for fragment in DANGEROUS_KEY_FRAGMENTS) or lowered in SAFE_CREDENTIAL_METADATA_KEYS,
                f"serialized credential-like field is not allowed at {path}.{key}",
            )
            require_no_serialized_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_serialized_credentials(child, f"{path}[{index}]")


def require_helper_contract(bundle: dict[str, Any]) -> None:
    require(bundle.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected session-security schema")
    require(bundle.get("generatedBy") == EXPECTED_HELPER, "unexpected session-security helper")
    require(bundle.get("helperVersion") == EXPECTED_HELPER_VERSION, "unexpected session-security helper version")
    require(bundle.get("protocolVersion") == EXPECTED_PROTOCOL, "unexpected protocol")


def require_transport(bundle: dict[str, Any]) -> dict[str, Any]:
    transport = object_at(bundle, "transport")
    require(transport.get("transport") == "host-authority-n-slot-message-security-harness", "transport mismatch")
    require(transport.get("networkScope") == "same-workstation-in-memory-session-security-smoke", "network scope mismatch")
    require(transport.get("sameWorkstationOnly") is True, "same-workstation boundary must be explicit")
    require(transport.get("publicNetworkSocketsOpened") is False, "public sockets must stay false")
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
        "gameInputSentByNSlotScheduler",
        "hostHelperInputSent",
    ):
        require(transport.get(key) is False, f"transport overclaim must be false: {key}")
    require(transport.get("newBeaLaunchCount") == 0, "session-security smoke must not launch BEA")
    require(transport.get("cdbAttachCount") == 0, "session-security smoke must not attach CDB")
    return transport


def require_session_descriptor(bundle: dict[str, Any]) -> dict[str, Any]:
    descriptor = object_at(bundle, "sessionDescriptor")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "session schema mismatch")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "session protocol mismatch")
    require(descriptor.get("slotCapacity") == 4, "slot capacity must be four")
    require(descriptor.get("acceptedSessionParticipantCount") == 4, "accepted participant count must be four")
    require(descriptor.get("originalBinaryActiveSlots") == EXPECTED_ACTIVE_SLOTS, "active original-binary slots mismatch")
    require(descriptor.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata slots mismatch")
    participants = list_at(descriptor, "participants")
    require([row.get("slotId") for row in participants if isinstance(row, dict)] == EXPECTED_SLOTS, "participant order mismatch")
    for row in participants:
        require(isinstance(row, dict), "participant row must be an object")
        slot = row.get("slotId")
        if slot in EXPECTED_ACTIVE_SLOTS:
            require(row.get("commandPermission") == "original-binary-command-allowed-when-authenticated", f"{slot} command permission mismatch")
            require(str(row.get("runtimeRoute", "")).startswith(str(slot) + "/inputDevice"), f"{slot} runtime route mismatch")
        else:
            require(row.get("runtimeRoute") == "unsupported-original-binary-active-slot", f"{slot} runtime route must stay unsupported")
            require(row.get("commandPermission") == "reject-gameplay-input-until-new-proof-class", f"{slot} gameplay permission must stay rejected")
    return descriptor


def require_authorization(bundle: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(bundle, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "ephemeral-not-serialized", "credential storage mismatch")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must not be present")
    require(authorization.get("rawCredentialsSerialized") is False, "raw credentials must not be serialized")
    fingerprints = object_at(authorization, "slotCredentialFingerprints")
    require(sorted(fingerprints) == EXPECTED_SLOTS, "slot credential fingerprints must cover P1-P4")
    for slot, value in fingerprints.items():
        require(isinstance(value, str) and len(value) == 64, f"{slot} fingerprint must be SHA-256")
    require(authorization.get("serverIdentityMode") == "pinned-fingerprint", "server identity mode mismatch")
    require(isinstance(authorization.get("serverIdentityFingerprint"), str) and len(authorization["serverIdentityFingerprint"]) == 64, "server identity fingerprint must be SHA-256")
    require(authorization.get("clientIdentityMode") == "pinned-slot-fingerprint", "client identity mode mismatch")
    require(authorization.get("securityProofScope") == EXPECTED_SECURITY_SCOPE, "session-security scope mismatch")
    require(authorization.get("sessionScopedMacCoverageProof") is True, "session-scoped MAC proof must be true")
    require(authorization.get("sessionScopedMacCoverageMode") == "canonical-json-message-excluding-mac", "session MAC coverage mode mismatch")
    require(authorization.get("sessionScopedMacExcludedFields") == ["mac"], "session MAC excluded fields mismatch")
    require(authorization.get("sessionHelloMacFields") == EXPECTED_SESSION_HELLO_MAC_FIELDS, "session hello MAC fields mismatch")
    require(authorization.get("commandMacFields") == EXPECTED_COMMAND_MAC_FIELDS, "command MAC fields mismatch")
    require(authorization.get("tickBoundMacFieldsProof") is True, "tick-bound MAC proof must be true")
    require(authorization.get("relayPlanHashMacBound") is True, "relay-plan hash MAC proof must be true")
    require(authorization.get("maxJsonLineBytesEnforced") is True, "max JSON line proof must be true")
    require(authorization.get("maxJsonLineBytes") == EXPECTED_MAX_MESSAGE_BYTES, "max JSON line byte limit mismatch")
    require(authorization.get("unknownFieldRejectionProof") is True, "unknown-field rejection proof must be true")
    require(authorization.get("strictMessageSchemaProof") is True, "strict schema proof must be true")
    require(authorization.get("nonceWindowSeconds") == 30, "nonce window mismatch")
    require(authorization.get("replayCacheEnabled") is True, "replay cache must be enabled")
    require(authorization.get("sequenceEnforced") is True, "sequence enforcement must be enabled")
    rate = object_at(authorization, "rateLimit")
    require(rate.get("maxAcceptedCommandsPerSlot") == 1, "per-slot rate limit mismatch")
    require(rate.get("maxAcceptedCommandsPerTick") == 2, "per-tick rate limit mismatch")
    return authorization


def require_scheduler(bundle: dict[str, Any]) -> dict[str, Any]:
    scheduler = object_at(bundle, "hostAuthorityNSlotScheduler")
    require(scheduler.get("schedulerSchema") == "host-authority-n-slot-scheduler.v1", "scheduler schema mismatch")
    require(scheduler.get("declaredSlotCount") == 4, "declared slot count mismatch")
    require(scheduler.get("slotCapacity") == 4, "slot capacity mismatch")
    require(scheduler.get("acceptedOriginalBinaryGameplaySlots") == EXPECTED_ACTIVE_SLOTS, "accepted slots mismatch")
    require(scheduler.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata slots mismatch")
    plan = list_at(scheduler, "relayPlan")
    require([row.get("clientSlot") for row in plan if isinstance(row, dict)] == EXPECTED_ACTIVE_SLOTS, "relay plan must be P1/P2 only")
    require(scheduler.get("relayPlanSha256") == sha256_payload(plan), "relay plan hash mismatch")
    expected_rows = {
        "P1": {
            "scheduledTick": 1,
            "commandId": EXPECTED_P1_COMMAND_ID,
            "mappedInputSequence": EXPECTED_P1_SEQUENCE,
            "route": "P1/inputDevice0/top-split-half",
            "hostHelperInputSent": False,
        },
        "P2": {
            "scheduledTick": 1,
            "commandId": EXPECTED_P2_COMMAND_ID,
            "mappedInputSequence": EXPECTED_P2_SEQUENCE,
            "route": "P2/inputDevice1/bottom-split-half",
            "hostHelperInputSent": False,
        },
    }
    for row in plan:
        require(isinstance(row, dict), "relay plan row must be an object")
        slot = str(row.get("clientSlot"))
        expected = expected_rows.get(slot)
        require(expected is not None, f"unexpected relay plan slot: {slot}")
        for key, expected_value in expected.items():
            require(row.get(key) == expected_value, f"{slot} relay plan {key} mismatch")
    require(scheduler.get("runtimeCompatibleP1P2RelayHash") == EXPECTED_RUNTIME_P1P2_RELAY_HASH, "runtime-compatible relay hash mismatch")
    for key in (
        "gameInputSentByNSlotScheduler",
        "hostHelperInputSent",
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "nativeBeaNetcodeClaim",
        "moreThanTwoRuntimePlayerClaim",
    ):
        require(scheduler.get(key) is False, f"scheduler overclaim must be false: {key}")
    return scheduler


def require_matrix(bundle: dict[str, Any]) -> dict[str, Any]:
    matrix = object_at(bundle, "sessionSecurityTestMatrix")
    require(matrix.get("maxJsonLineBytes") == EXPECTED_MAX_MESSAGE_BYTES, "matrix max bytes mismatch")
    accepted = list_at(matrix, "acceptedOriginalBinaryGameplay")
    metadata = list_at(matrix, "rejectedMetadataGameplay")
    security = list_at(matrix, "rejectedSecurityCases")
    require({row.get("caseId") for row in accepted if isinstance(row, dict)} == EXPECTED_ACCEPTED_CASES, "accepted case set mismatch")
    require({row.get("caseId") for row in metadata if isinstance(row, dict)} == EXPECTED_METADATA_REJECTION_CASES, "metadata rejection case set mismatch")
    require(len(security) == len(EXPECTED_SECURITY_REJECTION_CASES), "security rejection row count mismatch")
    require(
        {row.get("caseId") for row in security if isinstance(row, dict)} == set(EXPECTED_SECURITY_REJECTION_CASES),
        "security rejection case set mismatch",
    )
    reasons = {str(row.get("reason")) for row in security if isinstance(row, dict)}
    require(reasons == EXPECTED_SECURITY_REJECTION_REASONS, "security rejection reasons mismatch")
    require(matrix.get("acceptedOriginalBinaryGameplayCommandCount") == 2, "accepted command count mismatch")
    require(matrix.get("metadataGameplayRejectionCount") == 2, "metadata rejection count mismatch")
    require(matrix.get("securityRejectionCount") == len(EXPECTED_SECURITY_REJECTION_CASES), "security rejection count mismatch")
    for row in accepted:
        require(row.get("hostAccepted") is True, f"accepted case must be host accepted: {row}")
        require(row.get("responseType") == "command_accepted", f"accepted case response type mismatch: {row}")
        require(row.get("clientSlot") in EXPECTED_ACTIVE_SLOTS, f"accepted case must stay P1/P2: {row}")
        require(row.get("hostHelperInputSent") is False, "accepted security smoke must not send host-helper input")
    for row in metadata:
        require(row.get("hostAccepted") is False, f"rejected case must not be accepted: {row}")
        require(row.get("responseType") == "command_rejected", f"metadata rejection response type mismatch: {row}")
        require(row.get("hostHelperInputSent") is False, "rejected security smoke must not send host-helper input")
    for row in security:
        require(row.get("hostAccepted") is False, f"rejected case must not be accepted: {row}")
        require(row.get("hostHelperInputSent") is False, "rejected security smoke must not send host-helper input")
        case_id = str(row.get("caseId"))
        expected_response_type, expected_reason = EXPECTED_SECURITY_REJECTION_CASES[case_id]
        require(row.get("responseType") == expected_response_type, f"{case_id} response type mismatch")
        require(row.get("reason") == expected_reason, f"{case_id} reason mismatch")
    oversized = [row for row in security if isinstance(row, dict) and row.get("reason") == "oversized-message"]
    require(len(oversized) == 1, "exactly one oversized-message row is required")
    require(oversized[0].get("jsonLineByteMode") == "raw-line-before-json-parse", "oversized proof must be raw JSON-line checked")
    require(int(oversized[0].get("rawJsonLineBytes", 0)) > EXPECTED_MAX_MESSAGE_BYTES, "oversized raw JSON line must exceed the limit")
    proof_flags = object_at(matrix, "proofFlags")
    sensitivity = object_at(matrix, "macFieldSensitivityCases")
    hello_sensitivity = object_at(sensitivity, "session_hello")
    command_sensitivity = object_at(sensitivity, "command")
    require(set(hello_sensitivity) == set(EXPECTED_SESSION_HELLO_MAC_FIELDS), "session hello MAC sensitivity fields mismatch")
    require(set(command_sensitivity) == set(EXPECTED_COMMAND_MAC_FIELDS), "command MAC sensitivity fields mismatch")
    require(all(value is True for value in hello_sensitivity.values()), "session hello MAC field sensitivity must all be true")
    require(all(value is True for value in command_sensitivity.values()), "command MAC field sensitivity must all be true")
    for key in (
        "sessionScopedMacCoverageProof",
        "sessionScopedMacFieldSensitivityProof",
        "maxJsonLineBytesEnforced",
        "rawJsonLineByteLimitRejected",
        "unknownFieldRejectionProof",
        "strictMessageSchemaProof",
        "staleTickRejected",
        "missingRelayPlanHashRejected",
        "wrongRelayPlanHashRejected",
        "wrongSessionMacRejected",
        "replayNonceRejected",
        "serverIdentityMismatchRejected",
        "p3p4GameplayRejected",
        "publicMatchmakingRejected",
        "directInputClaimRejected",
    ):
        require(proof_flags.get(key) is True, f"missing proof flag: {key}")
    return matrix


def require_non_claims(bundle: dict[str, Any]) -> None:
    non_claims = object_at(bundle, "nonClaims")
    for key, value in non_claims.items():
        require(value is False, f"non-claim must remain false: {key}")
    require(bundle.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player original-binary runtime proof must remain zero")
    require(bundle.get("activeP3P4OriginalBinaryGameplayProof") is False, "active P3/P4 proof must remain false")


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = read_json(path)
    require_helper_contract(bundle)
    require_no_serialized_credentials(bundle)
    transport = require_transport(bundle)
    authorization = require_authorization(bundle)
    require_session_descriptor(bundle)
    scheduler = require_scheduler(bundle)
    matrix = require_matrix(bundle)
    require_non_claims(bundle)
    return {
        "artifact": str(path),
        "schemaVersion": bundle["schemaVersion"],
        "protocolVersion": bundle["protocolVersion"],
        "securityProofScope": authorization["securityProofScope"],
        "sessionScopedMacCoverageProof": authorization["sessionScopedMacCoverageProof"],
        "maxJsonLineBytesEnforced": authorization["maxJsonLineBytesEnforced"],
        "unknownFieldRejectionProof": authorization["unknownFieldRejectionProof"],
        "strictMessageSchemaProof": authorization["strictMessageSchemaProof"],
        "acceptedOriginalBinaryGameplayCommandCount": matrix["acceptedOriginalBinaryGameplayCommandCount"],
        "metadataGameplayRejectionCount": matrix["metadataGameplayRejectionCount"],
        "rejectedSecurityCaseCount": matrix["securityRejectionCount"],
        "relayPlanSha256": scheduler["relayPlanSha256"],
        "newBeaLaunchCount": transport["newBeaLaunchCount"],
        "cdbAttachCount": transport["cdbAttachCount"],
        "nPlayerOriginalBinaryRuntimeProof": bundle["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": bundle["activeP3P4OriginalBinaryGameplayProof"],
        "claimBoundary": (
            "This validates only a same-workstation in-memory N-slot session-security message harness. It proves "
            "strict message allowlists, session-scoped HMAC coverage, max JSON line size, nonce replay rejection, "
            "tick/relay-plan binding, P3/P4 gameplay rejection, and public-matchmaking/direct-input rejection for "
            "the host-authority protocol layer. It does not launch BEA, attach CDB, send game input, prove multi-host "
            "LAN, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, deterministic sync, "
            "rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity."
        ),
    }


def make_bundle_fixture(root: Path, *, overclaim: str | None = None) -> Path:
    from build_winui_original_binary_host_authority_n_slot_session_security_smoke_bundle import build_bundle

    path = root / "host-authority-n-slot-session-security-smoke-proof.json"
    build_bundle(path)
    if overclaim is not None:
        bundle = read_json(path)
        if overclaim == "runtime":
            bundle["nPlayerOriginalBinaryRuntimeProof"] = 4
        elif overclaim == "lan":
            bundle["transport"]["multiHostLanClaim"] = True
        elif overclaim == "missing-security-case":
            bundle["sessionSecurityTestMatrix"]["rejectedSecurityCases"].pop()
            bundle["sessionSecurityTestMatrix"]["securityRejectionCount"] -= 1
        elif overclaim == "relay-plan-tamper":
            plan = bundle["hostAuthorityNSlotScheduler"]["relayPlan"]
            plan[0]["mappedInputSequence"] = "down:X,wait:500,up:X"
            bundle["hostAuthorityNSlotScheduler"]["relayPlanSha256"] = sha256_payload(plan)
        elif overclaim == "missing-mac-sensitivity":
            bundle["sessionSecurityTestMatrix"]["macFieldSensitivityCases"]["command"].pop("clientSlot")
        write_json(path, bundle)
    return path


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        validate_bundle(make_bundle_fixture(Path(tmp)))
    for label, overclaim in (
        ("runtime overclaim should fail", "runtime"),
        ("LAN overclaim should fail", "lan"),
        ("missing security case should fail", "missing-security-case"),
        ("relay plan tamper should fail", "relay-plan-tamper"),
        ("missing MAC sensitivity field should fail", "missing-mac-sensitivity"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                validate_bundle(make_bundle_fixture(Path(tmp), overclaim=overclaim))
            except HostAuthorityNSlotSessionSecuritySmokeProofError:
                continue
            raise AssertionError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary host-authority N-slot session-security smoke checker self-test: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test is used")
    print(json.dumps(validate_bundle(args.bundle), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except HostAuthorityNSlotSessionSecuritySmokeProofError as exc:
        print(f"WinUI original-binary host-authority N-slot session-security smoke check: FAIL: {exc}")
        raise SystemExit(2)
