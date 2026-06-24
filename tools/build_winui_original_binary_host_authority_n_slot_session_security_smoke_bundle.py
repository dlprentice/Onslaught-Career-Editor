#!/usr/bin/env python3
"""Build an N-slot host-authority session-security smoke proof bundle."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check as check


SCHEMA = check.EXPECTED_SCHEMA
SESSION_SCHEMA = check.EXPECTED_SESSION_SCHEMA
PROTOCOL = check.EXPECTED_PROTOCOL
HELPER = check.EXPECTED_HELPER
HELPER_VERSION = check.EXPECTED_HELPER_VERSION
SLOTS = check.EXPECTED_SLOTS
ACTIVE_SLOTS = check.EXPECTED_ACTIVE_SLOTS
METADATA_SLOTS = check.EXPECTED_METADATA_SLOTS
MAX_MESSAGE_BYTES = check.EXPECTED_MAX_MESSAGE_BYTES
SESSION_ID = "n-slot-session-security-smoke-0001"
NOW_TICK = 50_000
COMMAND_IDS = {
    "P1": check.EXPECTED_P1_COMMAND_ID,
    "P2": check.EXPECTED_P2_COMMAND_ID,
    "P3": check.EXPECTED_P3_COMMAND_ID,
    "P4": check.EXPECTED_P4_COMMAND_ID,
}
SEQUENCES = {
    "P1": check.EXPECTED_P1_SEQUENCE,
    "P2": check.EXPECTED_P2_SEQUENCE,
    "P3": "down:R,wait:500,up:R",
    "P4": "down:T,wait:500,up:T",
}
SESSION_HELLO_ALLOWED_FIELDS = {
    "type",
    "sessionId",
    "protocolVersion",
    "compatibilityKey",
    "clientSlot",
    "clientId",
    "clientIdentityFingerprint",
    "serverIdentityFingerprint",
    "nonce",
    "timestamp",
    "sequence",
    "mac",
}
COMMAND_ALLOWED_FIELDS = {
    "type",
    "sessionId",
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
    "mac",
}
REQUIRED_FIELDS = {
    "session_hello": {
        "type",
        "sessionId",
        "protocolVersion",
        "compatibilityKey",
        "clientSlot",
        "clientId",
        "clientIdentityFingerprint",
        "serverIdentityFingerprint",
        "nonce",
        "timestamp",
        "sequence",
        "mac",
    },
    "command": {
        "type",
        "sessionId",
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
        "directGameInputClaim",
        "publicMatchmakingClaim",
        "teamAssignment",
        "mac",
    },
}


class HostAuthorityNSlotSessionSecuritySmokeBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityNSlotSessionSecuritySmokeBuildError(message)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "mac"}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")


def signed_payload(payload: dict[str, Any], credential: bytes) -> dict[str, Any]:
    signed = dict(payload)
    signed["mac"] = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    return signed


def payload_bytes(payload: dict[str, Any]) -> int:
    return len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1


def json_line_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def participant(slot: str) -> dict[str, Any]:
    active = slot in ACTIVE_SLOTS
    return {
        "slotId": slot,
        "clientId": f"client-{slot.lower()}",
        "sessionAdmission": "accepted-active-original-binary-slot" if active else "accepted-metadata-only-no-original-binary-gameplay-route",
        "runtimeRoute": (
            "P1/inputDevice0/top-split-half"
            if slot == "P1"
            else "P2/inputDevice1/bottom-split-half"
            if slot == "P2"
            else "unsupported-original-binary-active-slot"
        ),
        "commandPermission": "original-binary-command-allowed-when-authenticated" if active else "reject-gameplay-input-until-new-proof-class",
        "identityRequired": True,
    }


def make_session_descriptor() -> dict[str, Any]:
    return {
        "schemaVersion": SESSION_SCHEMA,
        "protocolVersion": PROTOCOL,
        "hostAuthorityModel": "single-host-authoritative-copied-session",
        "sessionId": SESSION_ID,
        "slotCapacity": 4,
        "acceptedSessionParticipantCount": 4,
        "originalBinaryActiveSlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "participants": [participant(slot) for slot in SLOTS],
        "sessionCompatibilityKey": sha256_text(f"{PROTOCOL}:{SESSION_ID}:n-slot-session-security-smoke"),
    }


def make_relay_plan() -> list[dict[str, Any]]:
    return [
        {
            "scheduledTick": 1,
            "clientSlot": "P1",
            "commandId": COMMAND_IDS["P1"],
            "mappedInputSequence": SEQUENCES["P1"],
            "route": "P1/inputDevice0/top-split-half",
            "hostHelperInputSent": False,
        },
        {
            "scheduledTick": 1,
            "clientSlot": "P2",
            "commandId": COMMAND_IDS["P2"],
            "mappedInputSequence": SEQUENCES["P2"],
            "route": "P2/inputDevice1/bottom-split-half",
            "hostHelperInputSent": False,
        },
    ]


class SecurityHarness:
    def __init__(self, descriptor: dict[str, Any], credentials: dict[str, bytes], authorization: dict[str, Any], relay_hash: str) -> None:
        self.descriptor = descriptor
        self.credentials = credentials
        self.authorization = authorization
        self.relay_hash = relay_hash
        self.established_connections: dict[str, str] = {}
        self.seen_nonces: set[tuple[str, str]] = set()
        self.expected_sequence = {slot: 1 for slot in SLOTS}
        self.accepted_per_slot = {slot: 0 for slot in SLOTS}
        self.accepted_per_tick = {1: 0}

    def verify_mac(self, payload: dict[str, Any], credential: bytes) -> bool:
        mac = payload.get("mac")
        if not isinstance(mac, str):
            return False
        expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
        return hmac.compare_digest(mac, expected)

    def evaluate_json_line(self, connection_id: str, raw_line: bytes, credential_slot: str | None = None) -> dict[str, Any]:
        if len(raw_line) > MAX_MESSAGE_BYTES:
            return self.reject("command_rejected", {}, "oversized-message")
        try:
            payload = json.loads(raw_line.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self.reject("command_rejected", {}, "malformed-json")
        if not isinstance(payload, dict):
            return self.reject("command_rejected", {}, "wrong-field-type")
        return self.evaluate(connection_id, payload, credential_slot=credential_slot)

    def evaluate(self, connection_id: str, payload: dict[str, Any], credential_slot: str | None = None) -> dict[str, Any]:
        message_type = payload.get("type")
        slot = payload.get("clientSlot")
        response_type = "session_rejected" if message_type == "session_hello" else "command_rejected"
        if payload_bytes(payload) > MAX_MESSAGE_BYTES:
            return self.reject(response_type, payload, "oversized-message")
        if message_type not in {"session_hello", "command"}:
            return self.reject(response_type, payload, "unknown-message-type")
        allowed = SESSION_HELLO_ALLOWED_FIELDS if message_type == "session_hello" else COMMAND_ALLOWED_FIELDS
        extra_fields = sorted(set(payload) - allowed)
        if extra_fields:
            return self.reject(response_type, payload, "unknown-field")
        missing = sorted(REQUIRED_FIELDS[message_type] - set(payload))
        if missing:
            return self.reject(response_type, payload, "missing-required-field")
        if slot not in SLOTS:
            return self.reject(response_type, payload, "unknown-slot")
        slot = str(slot)
        if credential_slot is not None and credential_slot != slot:
            return self.reject(response_type, payload, "bad-slot-credential")
        if not isinstance(payload.get("sequence"), int) or not isinstance(payload.get("timestamp"), int):
            return self.reject(response_type, payload, "wrong-field-type")
        if not isinstance(payload.get("nonce"), str) or not payload.get("nonce"):
            return self.reject(response_type, payload, "wrong-field-type")
        if self.established_connections.get(connection_id, slot) != slot:
            return self.reject(response_type, payload, "slot-changed-on-connection")
        if payload.get("sessionId") != self.descriptor["sessionId"]:
            return self.reject(response_type, payload, "session-mismatch")
        if payload.get("protocolVersion") != PROTOCOL:
            return self.reject(response_type, payload, "protocol-mismatch")
        if payload.get("compatibilityKey") != self.descriptor["sessionCompatibilityKey"]:
            return self.reject(response_type, payload, "session-compatibility-mismatch")
        if int(payload["timestamp"]) < NOW_TICK - int(self.authorization["nonceWindowSeconds"]):
            return self.reject(response_type, payload, "stale-tick")
        if int(payload["timestamp"]) > NOW_TICK + int(self.authorization["nonceWindowSeconds"]):
            return self.reject(response_type, payload, "future-tick")
        nonce_key = (slot, str(payload["nonce"]))
        if nonce_key in self.seen_nonces:
            return self.reject(response_type, payload, "replay-nonce")
        credential_name = credential_slot or slot
        credential = self.credentials.get(credential_name)
        if credential is None or not self.verify_mac(payload, credential):
            reason = "bad-slot-credential" if credential_name != slot else "bad-session-mac"
            return self.reject(response_type, payload, reason)
        self.seen_nonces.add(nonce_key)

        if message_type == "session_hello":
            if connection_id in self.established_connections:
                return self.reject(response_type, payload, "duplicate-session-on-connection")
            if payload.get("serverIdentityFingerprint") != self.authorization["serverIdentityFingerprint"]:
                return self.reject(response_type, payload, "server-identity-mismatch")
            if payload.get("clientId") in {f"client-{other.lower()}" for other in SLOTS if other != slot}:
                return self.reject(response_type, payload, "duplicate-slot-identity")
            if payload.get("clientIdentityFingerprint") in {
                fingerprint
                for other, fingerprint in self.authorization["clientIdentityFingerprints"].items()
                if other != slot
            }:
                return self.reject(response_type, payload, "duplicate-client-identity")
            if payload.get("clientId") != f"client-{slot.lower()}":
                return self.reject(response_type, payload, "slot-identity-mismatch")
            if payload.get("clientIdentityFingerprint") != self.authorization["clientIdentityFingerprints"][slot]:
                return self.reject(response_type, payload, "slot-identity-mismatch")
            self.established_connections[connection_id] = slot
            return {"type": "session_accepted", "clientSlot": slot, "hostAccepted": True}

        if connection_id not in self.established_connections:
            return self.reject(response_type, payload, "command-before-session")
        if payload.get("clientId") != f"client-{slot.lower()}":
            return self.reject(response_type, payload, "slot-identity-mismatch")
        if payload.get("scheduledTick") != 1:
            return self.reject(response_type, payload, "stale-tick")
        if payload.get("sequence") != self.expected_sequence[slot]:
            return self.reject(response_type, payload, "sequence-not-next")
        if payload.get("relayPlanSha256") is None:
            return self.reject(response_type, payload, "missing-relayPlanHash")
        if payload.get("relayPlanSha256") != self.relay_hash:
            return self.reject(response_type, payload, "relayPlanHash-mismatch")
        if payload.get("publicMatchmakingClaim") is True:
            return self.reject(response_type, payload, "public-matchmaking-not-allowed")
        if payload.get("directGameInputClaim") is True:
            return self.reject(response_type, payload, "direct-input-not-allowed")
        if payload.get("teamAssignment") not in {"alpha", "bravo"}:
            return self.reject(response_type, payload, "invalid-team-assignment")
        if slot in METADATA_SLOTS:
            return self.reject(response_type, payload, "required-for-unproven-original-binary-slots")
        if self.accepted_per_tick[1] >= int(self.authorization["rateLimit"]["maxAcceptedCommandsPerTick"]):
            return self.reject(response_type, payload, "tick-rate-limit")
        if self.accepted_per_slot[slot] >= int(self.authorization["rateLimit"]["maxAcceptedCommandsPerSlot"]):
            return self.reject(response_type, payload, "slot-rate-limit")
        if payload.get("command") != "forward":
            return self.reject(response_type, payload, "command-not-allowed")
        if payload.get("commandId") != COMMAND_IDS[slot]:
            return self.reject(response_type, payload, "command-id-not-allowed")
        if payload.get("mappedInputSequence") != SEQUENCES[slot]:
            return self.reject(response_type, payload, "mapped-input-sequence-mismatch")
        self.expected_sequence[slot] += 1
        self.accepted_per_slot[slot] += 1
        self.accepted_per_tick[1] += 1
        return {
            "type": "command_accepted",
            "clientSlot": slot,
            "commandId": payload["commandId"],
            "hostAccepted": True,
            "scheduledTick": 1,
            "hostHelperInputSent": False,
        }

    def reject(self, response_type: str, payload: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "type": response_type,
            "clientSlot": payload.get("clientSlot"),
            "commandId": payload.get("commandId"),
            "reason": reason,
            "hostAccepted": False,
            "hostHelperInputSent": False,
        }


def hello(slot: str, descriptor: dict[str, Any], authorization: dict[str, Any], *, nonce: str, sequence: int = 1) -> dict[str, Any]:
    return {
        "type": "session_hello",
        "sessionId": descriptor["sessionId"],
        "protocolVersion": PROTOCOL,
        "compatibilityKey": descriptor["sessionCompatibilityKey"],
        "clientSlot": slot,
        "clientId": f"client-{slot.lower()}",
        "clientIdentityFingerprint": authorization["clientIdentityFingerprints"][slot],
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "nonce": nonce,
        "timestamp": NOW_TICK,
        "sequence": sequence,
    }


def command(slot: str, descriptor: dict[str, Any], relay_hash: str, *, nonce: str, sequence: int = 1) -> dict[str, Any]:
    return {
        "type": "command",
        "sessionId": descriptor["sessionId"],
        "protocolVersion": PROTOCOL,
        "compatibilityKey": descriptor["sessionCompatibilityKey"],
        "clientSlot": slot,
        "clientId": f"client-{slot.lower()}",
        "scheduledTick": 1,
        "sequence": sequence,
        "nonce": nonce,
        "timestamp": NOW_TICK,
        "commandId": COMMAND_IDS[slot],
        "command": "forward",
        "mappedInputSequence": SEQUENCES[slot],
        "relayPlanSha256": relay_hash,
        "directGameInputClaim": False,
        "publicMatchmakingClaim": False,
        "teamAssignment": "alpha" if slot in {"P1", "P3"} else "bravo",
    }


def run_case(
    harness: SecurityHarness,
    *,
    case_id: str,
    connection_id: str,
    payload: dict[str, Any],
    credentials: dict[str, bytes],
    sign_slot: str,
    expected_type: str,
    expected_reason: str | None,
    credential_slot: str | None = None,
    sign_then_mutate: tuple[str, Any] | None = None,
) -> dict[str, Any]:
    signed = signed_payload(payload, credentials[sign_slot])
    if sign_then_mutate is not None:
        signed[sign_then_mutate[0]] = sign_then_mutate[1]
    response = harness.evaluate(connection_id, signed, credential_slot=credential_slot)
    require(response.get("type") == expected_type, f"{case_id} response type mismatch: {response}")
    require(response.get("reason") == expected_reason, f"{case_id} reason mismatch: {response}")
    return {
        "caseId": case_id,
        "clientSlot": payload.get("clientSlot"),
        "responseType": response.get("type"),
        "reason": response.get("reason"),
        "hostAccepted": response.get("hostAccepted") is True,
        "commandId": payload.get("commandId"),
        "payloadBytes": payload_bytes(signed),
        "hostHelperInputSent": False,
    }


def run_raw_json_line_case(
    harness: SecurityHarness,
    *,
    case_id: str,
    connection_id: str,
    payload: dict[str, Any],
    credentials: dict[str, bytes],
    sign_slot: str,
    expected_reason: str,
) -> dict[str, Any]:
    signed = signed_payload(payload, credentials[sign_slot])
    raw_line = json_line_bytes(signed)
    response = harness.evaluate_json_line(connection_id, raw_line)
    require(response.get("type") == "command_rejected", f"{case_id} response type mismatch: {response}")
    require(response.get("reason") == expected_reason, f"{case_id} reason mismatch: {response}")
    return {
        "caseId": case_id,
        "clientSlot": payload.get("clientSlot"),
        "responseType": response.get("type"),
        "reason": response.get("reason"),
        "hostAccepted": False,
        "commandId": payload.get("commandId"),
        "payloadBytes": len(raw_line),
        "rawJsonLineBytes": len(raw_line),
        "jsonLineByteMode": "raw-line-before-json-parse",
        "hostHelperInputSent": False,
    }


def mac_field_sensitivity(payload: dict[str, Any], fields: list[str], credential: bytes) -> dict[str, bool]:
    base_mac = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    result: dict[str, bool] = {}
    for field in fields:
        mutated = dict(payload)
        value = mutated[field]
        if isinstance(value, bool):
            mutated[field] = not value
        elif isinstance(value, int):
            mutated[field] = value + 1
        elif isinstance(value, str):
            mutated[field] = value + "-mutated"
        else:
            mutated[field] = "mutated"
        result[field] = hmac.new(credential, canonical_bytes(mutated), "sha256").hexdigest() != base_mac
    return result


def make_authorization(credentials: dict[str, bytes]) -> dict[str, Any]:
    return {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "rawCredentialsSerialized": False,
        "slotCredentialFingerprints": {slot: hashlib.sha256(value).hexdigest() for slot, value in credentials.items()},
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": sha256_text(f"{PROTOCOL}:{SESSION_ID}:server"),
        "clientIdentityMode": "pinned-slot-fingerprint",
        "clientIdentityFingerprints": {slot: sha256_text(f"{PROTOCOL}:{SESSION_ID}:client:{slot}") for slot in SLOTS},
        "securityProofScope": check.EXPECTED_SECURITY_SCOPE,
        "sessionScopedMacCoverageProof": True,
        "sessionScopedMacCoverageMode": "canonical-json-message-excluding-mac",
        "sessionScopedMacExcludedFields": ["mac"],
        "sessionHelloMacFields": check.EXPECTED_SESSION_HELLO_MAC_FIELDS,
        "commandMacFields": check.EXPECTED_COMMAND_MAC_FIELDS,
        "tickBoundMacFieldsProof": True,
        "relayPlanHashMacBound": True,
        "maxJsonLineBytesEnforced": True,
        "maxJsonLineBytes": MAX_MESSAGE_BYTES,
        "unknownFieldRejectionProof": True,
        "strictMessageSchemaProof": True,
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "replayCacheScope": "session-client-slot-nonce-smoke",
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSlot": 1,
            "maxAcceptedCommandsPerTick": 2,
        },
        "clockMode": "deterministic-smoke-clock",
    }


def build_matrix(descriptor: dict[str, Any], credentials: dict[str, bytes], authorization: dict[str, Any], relay_hash: str) -> dict[str, Any]:
    harness = SecurityHarness(descriptor, credentials, authorization, relay_hash)
    accepted: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    security: list[dict[str, Any]] = []

    for slot in ACTIVE_SLOTS:
        run_case(
            harness,
            case_id=f"{slot.lower()}-session-accepted",
            connection_id=f"{slot.lower()}-ok",
            payload=hello(slot, descriptor, authorization, nonce=f"{slot.lower()}-hello-ok"),
            credentials=credentials,
            sign_slot=slot,
            expected_type="session_accepted",
            expected_reason=None,
        )
        accepted.append(
            run_case(
                harness,
                case_id=f"{slot.lower()}-forward-accepted",
                connection_id=f"{slot.lower()}-ok",
                payload=command(slot, descriptor, relay_hash, nonce=f"{slot.lower()}-forward-ok"),
                credentials=credentials,
                sign_slot=slot,
                expected_type="command_accepted",
                expected_reason=None,
            )
        )
        if slot == "P1":
            security.append(
                run_case(
                    harness,
                    case_id="slot-rate-limit-rejected",
                    connection_id="p1-ok",
                    payload=command("P1", descriptor, relay_hash, nonce="p1-slot-rate", sequence=2),
                    credentials=credentials,
                    sign_slot="P1",
                    expected_type="command_rejected",
                    expected_reason="slot-rate-limit",
                )
            )

    for slot in METADATA_SLOTS:
        run_case(
            harness,
            case_id=f"{slot.lower()}-session-accepted",
            connection_id=f"{slot.lower()}-metadata",
            payload=hello(slot, descriptor, authorization, nonce=f"{slot.lower()}-hello-metadata"),
            credentials=credentials,
            sign_slot=slot,
            expected_type="session_accepted",
            expected_reason=None,
        )
        metadata.append(
            run_case(
                harness,
                case_id=f"{slot.lower()}-forward-rejected",
                connection_id=f"{slot.lower()}-metadata",
                payload=command(slot, descriptor, relay_hash, nonce=f"{slot.lower()}-forward-metadata"),
                credentials=credentials,
                sign_slot=slot,
                expected_type="command_rejected",
                expected_reason="required-for-unproven-original-binary-slots",
            )
        )

    def add_negative(case_id: str, payload: dict[str, Any], reason: str, *, connection_id: str, sign_slot: str = "P1", credential_slot: str | None = None, sign_then_mutate: tuple[str, Any] | None = None, expected_type: str = "command_rejected") -> None:
        security.append(
            run_case(
                harness,
                case_id=case_id,
                connection_id=connection_id,
                payload=payload,
                credentials=credentials,
                sign_slot=sign_slot,
                credential_slot=credential_slot,
                sign_then_mutate=sign_then_mutate,
                expected_type=expected_type,
                expected_reason=reason,
            )
        )

    base = lambda suffix: command("P1", descriptor, relay_hash, nonce=f"p1-negative-{suffix}", sequence=2)
    add_negative("unknown-field-rejected", {**base("unknown"), "unexpectedField": True}, "unknown-field", connection_id="p1-ok")
    security.append(
        run_raw_json_line_case(
            harness,
            case_id="oversized-message-rejected",
            connection_id="p1-ok",
            payload={**base("oversized"), "padding": "X" * (MAX_MESSAGE_BYTES + 1)},
            credentials=credentials,
            sign_slot="P1",
            expected_reason="oversized-message",
        )
    )
    stale = base("stale")
    stale["timestamp"] = NOW_TICK - 31
    add_negative("stale-tick-rejected", stale, "stale-tick", connection_id="p1-ok")
    future = base("future")
    future["timestamp"] = NOW_TICK + 31
    add_negative("future-tick-rejected", future, "future-tick", connection_id="p1-ok")
    replay = base("replay")
    replay["nonce"] = "p1-forward-ok"
    add_negative("replay-nonce-rejected", replay, "replay-nonce", connection_id="p1-ok")
    missing_hash = base("missing-relay")
    del missing_hash["relayPlanSha256"]
    add_negative("missing-relayPlanHash-rejected", missing_hash, "missing-relayPlanHash", connection_id="p1-ok")
    wrong_hash = base("wrong-relay")
    wrong_hash["relayPlanSha256"] = "0" * 64
    add_negative("relayPlanHash-mismatch-rejected", wrong_hash, "relayPlanHash-mismatch", connection_id="p1-ok")
    add_negative("bad-session-mac-rejected", base("bad-mac"), "bad-session-mac", connection_id="p1-ok", sign_then_mutate=("command", "backward"))
    add_negative("bad-slot-credential-rejected", base("wrong-credential"), "bad-slot-credential", connection_id="p1-ok", sign_slot="P2", credential_slot="P2")
    identity = base("identity")
    identity["clientId"] = "client-p2"
    add_negative("slot-identity-mismatch-rejected", identity, "slot-identity-mismatch", connection_id="p1-ok")
    changed = command("P2", descriptor, relay_hash, nonce="p2-on-p1-connection", sequence=1)
    add_negative("slot-changed-on-connection-rejected", changed, "slot-changed-on-connection", connection_id="p1-ok", sign_slot="P2")
    add_negative("command-before-session-rejected", command("P1", descriptor, relay_hash, nonce="p1-before-session"), "command-before-session", connection_id="p1-before-session")
    dup = hello("P1", descriptor, authorization, nonce="p1-duplicate-hello", sequence=2)
    add_negative("duplicate-session-on-connection-rejected", dup, "duplicate-session-on-connection", connection_id="p1-ok", expected_type="session_rejected")
    sequence = base("sequence")
    sequence["sequence"] = 99
    add_negative("sequence-not-next-rejected", sequence, "sequence-not-next", connection_id="p1-ok")
    add_negative("tick-rate-limit-rejected", command("P2", descriptor, relay_hash, nonce="p2-rate", sequence=2), "tick-rate-limit", connection_id="p2-ok", sign_slot="P2")
    missing = base("missing-required")
    del missing["commandId"]
    add_negative("missing-required-field-rejected", missing, "missing-required-field", connection_id="p1-ok")
    wrong_type = base("wrong-type")
    wrong_type["sequence"] = "2"
    add_negative("wrong-field-type-rejected", wrong_type, "wrong-field-type", connection_id="p1-ok")
    public = base("public")
    public["publicMatchmakingClaim"] = True
    add_negative("public-matchmaking-rejected", public, "public-matchmaking-not-allowed", connection_id="p1-ok")
    direct = base("direct")
    direct["directGameInputClaim"] = True
    add_negative("direct-input-rejected", direct, "direct-input-not-allowed", connection_id="p1-ok")
    bad_server = hello("P1", descriptor, authorization, nonce="p1-bad-server", sequence=1)
    bad_server["serverIdentityFingerprint"] = "0" * 64
    add_negative("server-identity-mismatch-rejected", bad_server, "server-identity-mismatch", connection_id="p1-bad-server", expected_type="session_rejected")
    unknown_slot = {
        **hello("P1", descriptor, authorization, nonce="p9-unknown-slot"),
        "clientSlot": "P9",
        "clientId": "client-p9",
    }
    add_negative("unknown-slot-rejected", unknown_slot, "unknown-slot", connection_id="p9-unknown", expected_type="session_rejected")
    bad_team = base("bad-team")
    bad_team["teamAssignment"] = "charlie"
    add_negative("invalid-team-assignment-rejected", bad_team, "invalid-team-assignment", connection_id="p1-ok")
    duplicate_slot = hello("P2", descriptor, authorization, nonce="p2-duplicate-slot")
    duplicate_slot["clientId"] = "client-p1"
    add_negative("duplicate-slot-identity-rejected", duplicate_slot, "duplicate-slot-identity", connection_id="duplicate-slot", expected_type="session_rejected", sign_slot="P2")
    duplicate_client = hello("P2", descriptor, authorization, nonce="p2-duplicate-client")
    duplicate_client["clientIdentityFingerprint"] = authorization["clientIdentityFingerprints"]["P1"]
    add_negative("duplicate-client-identity-rejected", duplicate_client, "duplicate-client-identity", connection_id="duplicate-client", expected_type="session_rejected", sign_slot="P2")

    return {
        "maxJsonLineBytes": MAX_MESSAGE_BYTES,
        "acceptedOriginalBinaryGameplay": accepted,
        "rejectedMetadataGameplay": metadata,
        "rejectedSecurityCases": security,
        "macFieldSensitivityCases": {
            "session_hello": mac_field_sensitivity(
                hello("P1", descriptor, authorization, nonce="p1-mac-sensitivity"),
                check.EXPECTED_SESSION_HELLO_MAC_FIELDS,
                credentials["P1"],
            ),
            "command": mac_field_sensitivity(
                command("P1", descriptor, relay_hash, nonce="p1-command-mac-sensitivity", sequence=2),
                check.EXPECTED_COMMAND_MAC_FIELDS,
                credentials["P1"],
            ),
        },
        "acceptedOriginalBinaryGameplayCommandCount": len(accepted),
        "metadataGameplayRejectionCount": len(metadata),
        "securityRejectionCount": len(security),
        "proofFlags": {
            "sessionScopedMacCoverageProof": True,
            "sessionScopedMacFieldSensitivityProof": True,
            "maxJsonLineBytesEnforced": True,
            "rawJsonLineByteLimitRejected": True,
            "unknownFieldRejectionProof": True,
            "strictMessageSchemaProof": True,
            "staleTickRejected": True,
            "missingRelayPlanHashRejected": True,
            "wrongRelayPlanHashRejected": True,
            "wrongSessionMacRejected": True,
            "replayNonceRejected": True,
            "serverIdentityMismatchRejected": True,
            "p3p4GameplayRejected": True,
            "publicMatchmakingRejected": True,
            "directInputClaimRejected": True,
        },
    }


def build_bundle(output_path: Path) -> dict[str, Any]:
    descriptor = make_session_descriptor()
    credentials = {slot: os.urandom(32) for slot in SLOTS}
    authorization = make_authorization(credentials)
    relay_plan = make_relay_plan()
    relay_hash = check.sha256_payload(relay_plan)
    matrix = build_matrix(descriptor, credentials, authorization, relay_hash)
    scheduler = {
        "schedulerSchema": "host-authority-n-slot-scheduler.v1",
        "declaredSlotCount": 4,
        "slotCapacity": 4,
        "acceptedSessionParticipantCount": 4,
        "originalBinaryRelaySlotCount": 2,
        "acceptedOriginalBinaryGameplayCommandCount": 2,
        "rejectedOriginalBinaryGameplayCommandCount": 2,
        "acceptedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "rejectedGameplayRouteSlots": METADATA_SLOTS,
        "extraSlotRejectionPolicy": "required-for-unproven-original-binary-slots",
        "deterministicParticipantOrder": SLOTS,
        "deterministicOriginalBinaryRelayOrder": ACTIVE_SLOTS,
        "relayPlan": relay_plan,
        "relayPlanSha256": relay_hash,
        "runtimeCompatibleP1P2RelayHash": check.EXPECTED_RUNTIME_P1P2_RELAY_HASH,
        "gameInputSentByNSlotScheduler": False,
        "hostHelperInputSent": False,
        "multiHostLanClaim": False,
        "publicMatchmakingClaim": False,
        "nativeBeaNetcodeClaim": False,
        "deterministicSyncClaim": False,
        "rollbackClaim": False,
        "antiCheatClaim": False,
        "moreThanTwoRuntimePlayerClaim": False,
    }
    bundle = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "sessionDescriptor": descriptor,
        "transport": {
            "transport": "host-authority-n-slot-message-security-harness",
            "networkScope": "same-workstation-in-memory-session-security-smoke",
            "sameWorkstationOnly": True,
            "publicNetworkSocketsOpened": False,
            "multiHostLanClaim": False,
            "publicMatchmakingClaim": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
            "deterministicSyncClaim": False,
            "rollbackClaim": False,
            "antiCheatClaim": False,
            "physicalGamepadClaim": False,
            "rebuildParityClaim": False,
            "gameInputSentByNSlotScheduler": False,
            "hostHelperInputSent": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
        },
        "authorization": authorization,
        "hostAuthorityNSlotScheduler": scheduler,
        "sessionSecurityTestMatrix": matrix,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "nonClaims": {
            "fourPlayerGameplayProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "coOpModeRuntimeProof": False,
            "versusModeRuntimeProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "physicalGamepadProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "claimBoundary": (
            "Same-workstation in-memory N-slot host-authority session-security message smoke only. It proves bounded "
            "message-level HMAC/schema/size/replay/tick/relay-plan/admission rejections for the host-authority "
            "protocol layer. It does not launch BEA, attach CDB, open public sockets, send host-helper input, prove "
            "multi-host LAN, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, "
            "deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    serialized = json.dumps(bundle, indent=2)
    for credential in credentials.values():
        require(credential.hex() not in serialized, "raw credential leaked into serialized proof")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized, encoding="utf-8")
    summary = check.validate_bundle(output_path)
    return {
        "bundle": str(output_path.resolve()),
        "bundleSha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_bundle(args.output.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HostAuthorityNSlotSessionSecuritySmokeBuildError, check.HostAuthorityNSlotSessionSecuritySmokeProofError) as exc:
        print(f"WinUI original-binary host-authority N-slot session-security smoke bundle build: FAIL: {exc}")
        raise SystemExit(2)
