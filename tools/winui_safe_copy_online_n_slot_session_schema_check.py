#!/usr/bin/env python3
"""Validate the original-binary online N-slot session schema proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-n-slot-session-schema.v1.json"
SOURCE_SCALABILITY_CONTRACT = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_online_n_slot_session_schema_2026-06-18.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCHEMA = "winui-original-binary-online-n-slot-session-schema.v1"
EXPECTED_SESSION_SCHEMA = "winui-original-binary-host-authority-n-slot-session.v1"
EXPECTED_PROTOCOL = "host-authority-n-slot-input.v1"
EXPECTED_SCOPE = "original-binary-online-n-slot-session-schema"
EXPECTED_SOURCE_SCHEMA = "winui-original-binary-online-session-scalability-contract.v1"
EXPECTED_RUNTIME_PROFILE = "original-binary-copied-local-splitscreen"
EXPECTED_SLOTS = ["P1", "P2", "P3", "P4"]
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]
EXPECTED_MODE_TYPES = {"cooperative", "versus-free-for-all", "team-versus", "spectator-admin"}
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_n_slot_session_schema_check.py --check"


class NSlotSessionSchemaError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise NSlotSessionSchemaError(message)


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


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


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


def require_runtime_boundary(contract: dict[str, Any]) -> dict[str, Any]:
    runtime = object_at(contract, "runtimeBoundary")
    require(runtime.get("runtimeProfile") == EXPECTED_RUNTIME_PROFILE, "runtime profile mismatch")
    require(runtime.get("originalBinaryPlayerSlotsProven") == EXPECTED_ACTIVE_SLOTS, "runtime proof must stay P1/P2")
    require(runtime.get("maxOriginalBinaryActiveSlots") == 2, "original-binary active slot cap must stay two")
    require(runtime.get("maxRuntimePlayerSlotsProven") == 2, "runtime player proof must stay two")
    require(runtime.get("maxRetailPlayersProven") == 2, "retail player proof must stay two")
    require(runtime.get("retailSlotsProven") == "P1,P2", "retail slot proof mismatch")
    require(runtime.get("retailViewpointsProven") == 2, "retail viewpoint proof must stay two")
    require(runtime.get("moreThanTwoOriginalBinaryRuntimeProofSlices") == 0, "more-than-two runtime proof must stay zero")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(runtime.get("coOpVersusModeRuntimeProofSlices") == 0, "co-op/versus runtime proof must stay zero")
    require(runtime.get("nativeBeaNetcodeProofSlices") == 0, "native BEA netcode proof must stay zero")
    require(runtime.get("beyondTwoPlayersRequiresNewProofClass") is True, "beyond-two proof must require a new proof class")
    return runtime


def require_source_contract(contract: dict[str, Any]) -> None:
    source = object_at(contract, "sourceContract")
    require(source.get("path") == "roadmap/original-binary-online-session-scalability-contract.v1.json", "source contract path mismatch")
    require(source.get("schemaVersion") == EXPECTED_SOURCE_SCHEMA, "source contract schema mismatch")
    require(source.get("requiredRuntimeCap") == "P1/P2 only", "source runtime cap mismatch")
    require(source.get("requiredMinimumArchitectureAcceptanceSlots") == 4, "source acceptance slot count mismatch")
    upstream = read_json(SOURCE_SCALABILITY_CONTRACT)
    require(upstream.get("schemaVersion") == EXPECTED_SOURCE_SCHEMA, "upstream scalability contract schema mismatch")
    upstream_runtime = object_at(upstream, "currentOriginalBinaryRuntime")
    require(upstream_runtime.get("maxRuntimePlayerSlotsProven") == 2, "upstream runtime cap drifted above two")
    upstream_arch = object_at(upstream, "scalableArchitecture")
    require(upstream_arch.get("minimumArchitectureAcceptanceSlots") == 4, "upstream minimum architecture acceptance mismatch")


def require_participants(descriptor: dict[str, Any]) -> dict[str, dict[str, Any]]:
    participants = list_at(descriptor, "participants")
    require(len(participants) == 4, "N-slot session must accept four participant rows")
    by_slot: dict[str, dict[str, Any]] = {}
    for row in participants:
        require(isinstance(row, dict), "participant row must be an object")
        slot = str(row.get("slotId"))
        require(slot in EXPECTED_SLOTS, f"unexpected participant slot: {slot}")
        require(slot not in by_slot, f"duplicate participant slot: {slot}")
        require(row.get("clientId") == f"client-{slot.lower()}", f"client id mismatch for {slot}")
        require(row.get("identityRequired") is True, f"identity must be required for {slot}")
        by_slot[slot] = row

    require(list(by_slot) == EXPECTED_SLOTS, "participant order must be P1,P2,P3,P4")
    for slot in EXPECTED_ACTIVE_SLOTS:
        row = by_slot[slot]
        require(row.get("sessionAdmission") == "accepted-active-original-binary-slot", f"{slot} admission mismatch")
        require(row.get("commandPermission") == "original-binary-command-allowed-when-authenticated", f"{slot} command permission mismatch")
        require(str(row.get("runtimeRoute", "")).startswith(slot + "/inputDevice"), f"{slot} runtime route mismatch")
        require(set(row.get("modeEligibility", [])) >= {"cooperative", "versus-free-for-all", "team-versus"}, f"{slot} mode eligibility too narrow")

    for slot in EXPECTED_METADATA_SLOTS:
        row = by_slot[slot]
        require(row.get("sessionAdmission") == "accepted-metadata-only-no-original-binary-gameplay-route", f"{slot} metadata admission mismatch")
        require(row.get("runtimeRoute") == "unsupported-original-binary-active-slot", f"{slot} must not have an original-binary runtime route")
        require(row.get("commandPermission") == "reject-gameplay-input-until-new-proof-class", f"{slot} must reject gameplay input")
        require("spectator-admin" in row.get("modeEligibility", []), f"{slot} must be eligible for spectator/admin metadata")

    return by_slot


def require_session_descriptor(contract: dict[str, Any]) -> dict[str, Any]:
    descriptor = object_at(contract, "sessionDescriptor")
    require(descriptor.get("schemaVersion") == EXPECTED_SESSION_SCHEMA, "session schema mismatch")
    require(descriptor.get("protocolVersion") == EXPECTED_PROTOCOL, "protocol version mismatch")
    require(descriptor.get("hostAuthorityModel") == "single-host-authoritative-copied-session", "host authority model mismatch")
    require(descriptor.get("sessionTypeModel") == "mode-family-scoped", "session type model mismatch")
    require(descriptor.get("participantField") == "participants[]", "participant field mismatch")
    require(descriptor.get("slotModel") == "profile-declared-indexed-player-slots", "slot model mismatch")
    require(descriptor.get("slotCapacity") == 4, "slot capacity must be four for this proof")
    require(descriptor.get("minimumArchitectureAcceptanceSlots") == 4, "minimum architecture acceptance must be four")
    require(descriptor.get("acceptedSessionParticipantCount") == 4, "accepted participant count must be four")
    require(descriptor.get("originalBinaryActiveSlots") == EXPECTED_ACTIVE_SLOTS, "active original-binary slots mismatch")
    require(descriptor.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata-only slots mismatch")
    require(descriptor.get("unsupportedOriginalBinaryActiveSlotsRejected") == EXPECTED_METADATA_SLOTS, "unsupported active slots mismatch")
    require_participants(descriptor)
    return descriptor


def require_mode_profiles(contract: dict[str, Any]) -> list[dict[str, Any]]:
    modes = list_at(contract, "modeProfiles")
    require(len(modes) == 4, "expected four mode profiles")
    ids = {str(row.get("sessionType")) for row in modes if isinstance(row, dict)}
    require(ids == EXPECTED_MODE_TYPES, "mode profiles must cover cooperative, FFA, team-versus, and spectator/admin")
    for row in modes:
        require(isinstance(row, dict), "mode row must be an object")
        require(row.get("sessionType") == row.get("modeFamily"), f"mode family mismatch: {row}")
        require(row.get("participantSlots") == EXPECTED_SLOTS, f"mode participants must be P1-P4: {row}")
        require(row.get("originalBinaryActiveSlots") == EXPECTED_ACTIVE_SLOTS, f"mode active slots must be P1/P2: {row}")
        require(row.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, f"mode metadata slots must be P3/P4: {row}")
        require(row.get("runtimeProofStatus") == "planned-not-runtime-proven", f"mode overclaim: {row}")
        require(row.get("modeRuntimeProofSlices") == 0, f"mode proof slices must stay zero: {row}")
        require(row.get("winConditionAuthority") == "unproven", f"win condition overclaim: {row}")
        require(row.get("respawnAuthority") == "unproven", f"respawn overclaim: {row}")
        require(row.get("teamAssignmentAuthority") == "schema-only", f"team assignment must be schema-only: {row}")
        require(row.get("friendlyFireStatus") == "unproven", f"friendly fire overclaim: {row}")
    team_versus = next(row for row in modes if row["sessionType"] == "team-versus")
    teams = object_at(team_versus, "teamAssignments")
    require(teams.get("alpha") == ["P1", "P3"], "team alpha assignment mismatch")
    require(teams.get("bravo") == ["P2", "P4"], "team bravo assignment mismatch")
    return modes


def require_scheduler(contract: dict[str, Any]) -> dict[str, Any]:
    scheduler = object_at(contract, "hostAuthorityNSlotScheduler")
    require(scheduler.get("schedulerSchema") == "host-authority-n-slot-scheduler.v1", "scheduler schema mismatch")
    require(scheduler.get("declaredSlotCount") == 4, "declared slot count must be four")
    require(scheduler.get("acceptedSessionParticipantCount") == 4, "scheduler must accept four session participants")
    require(scheduler.get("originalBinaryRelaySlotCount") == 2, "original-binary relay count must stay two")
    require(scheduler.get("acceptedOriginalBinaryGameplayCommandCount") == 2, "accepted gameplay commands must stay P1/P2")
    require(scheduler.get("rejectedOriginalBinaryGameplayCommandCount") == 2, "P3/P4 gameplay commands must be rejected")
    require(scheduler.get("activeOriginalBinarySlots") == EXPECTED_ACTIVE_SLOTS, "active scheduler slots mismatch")
    require(scheduler.get("metadataOnlySlots") == EXPECTED_METADATA_SLOTS, "metadata-only scheduler slots mismatch")
    require(scheduler.get("rejectedGameplayRouteSlots") == EXPECTED_METADATA_SLOTS, "rejected gameplay route slots mismatch")
    require(scheduler.get("extraSlotRejectionPolicy") == "required-for-unproven-original-binary-slots", "extra-slot rejection policy mismatch")
    require(scheduler.get("arrivalOrder") == ["P4", "P2", "P3", "P1"], "arrival order should prove stable sorting")
    require(scheduler.get("deterministicParticipantOrder") == EXPECTED_SLOTS, "deterministic participant order mismatch")
    require(scheduler.get("deterministicOriginalBinaryRelayOrder") == EXPECTED_ACTIVE_SLOTS, "deterministic relay order mismatch")

    plan = list_at(scheduler, "relayPlan")
    require(len(plan) == 2, "relay plan must contain only P1/P2")
    require([row.get("clientSlot") for row in plan if isinstance(row, dict)] == EXPECTED_ACTIVE_SLOTS, "relay plan order mismatch")
    require(scheduler.get("relayPlanSha256") == sha256_payload(plan), "relay plan hash mismatch")
    for row in plan:
        require(isinstance(row, dict), "relay plan row must be an object")
        require(row.get("scheduledTick") == 1, "relay plan tick mismatch")
        require(row.get("hostHelperInputSent") is False, "schema proof must not claim host-helper input")

    rejected = list_at(scheduler, "rejectedGameplayCommands")
    reasons = {(str(row.get("clientSlot")), str(row.get("reason"))) for row in rejected if isinstance(row, dict)}
    for expected in (
        ("P3", "required-for-unproven-original-binary-slots"),
        ("P4", "required-for-unproven-original-binary-slots"),
        ("P2", "public-matchmaking-not-allowed"),
        ("P1", "direct-input-not-allowed"),
        ("P9", "unknown-slot"),
        ("P3", "invalid-team-assignment"),
    ):
        require(expected in reasons, f"missing rejection case: {expected}")
    for row in rejected:
        require(isinstance(row, dict), "rejected command row must be an object")
        require(row.get("hostAccepted") is False, "rejected command must not be host accepted")
        require(row.get("gameInputSentByNSlotScheduler") is False, "rejected command must not send scheduler game input")
        require(row.get("hostHelperInputSent") is False, "rejected command must not send host-helper input")

    for key in (
        "gameInputSentByNSlotScheduler",
        "hostHelperInputSent",
        "multiHostLanClaim",
        "publicMatchmakingClaim",
        "nativeBeaNetcodeClaim",
        "deterministicSyncClaim",
        "moreThanTwoRuntimePlayerClaim",
    ):
        require(scheduler.get(key) is False, f"scheduler overclaim must be false: {key}")
    rejection_cases = set(str(item) for item in list_at(scheduler, "schemaRejectionCases"))
    for reason in (
        "slot-not-in-profile-enabledSlots",
        "duplicate-slot-identity",
        "duplicate-client-identity",
        "participant-slot-mismatch",
        "active-original-binary-slot-count-exceeds-two",
        "spectator-issued-game-input",
        "invalid-sessionType",
        "invalid-mode-family",
        "invalid-team-assignment",
        "unknown-field",
        "oversized-message",
        "stale-tick",
        "queue-overflow-backpressure-drop",
        "missing-relayPlanHash",
    ):
        require(reason in rejection_cases, f"missing schema rejection case: {reason}")
    return scheduler


def require_authorization(contract: dict[str, Any]) -> dict[str, Any]:
    authorization = object_at(contract, "authorization")
    require(authorization.get("scheme") == "HMAC-SHA256", "authorization scheme mismatch")
    require(authorization.get("credentialStorage") == "ephemeral-not-serialized", "credential storage mismatch")
    require(authorization.get("serializedCredentialPresent") is False, "serialized credential must not be present")
    require(authorization.get("slotIdentityMode") == "pinned-slot-fingerprint", "slot identity mode mismatch")
    fingerprints = object_at(authorization, "slotCredentialFingerprints")
    require(sorted(fingerprints) == EXPECTED_SLOTS, "fingerprints must cover P1-P4")
    for slot, value in fingerprints.items():
        require(isinstance(value, str) and len(value) == 64, f"{slot} fingerprint must be SHA-256-like")
    require(
        authorization.get("sessionScopedHmacFields")
        == ["sessionId", "protocolVersion", "slotId", "clientId", "tick", "sequence", "commandId", "payload"],
        "session-scoped HMAC fields mismatch",
    )
    require(authorization.get("nonceWindowSeconds") == 30, "nonce window mismatch")
    require(authorization.get("replayCacheEnabled") is True, "replay cache must be enabled")
    require(authorization.get("sequenceEnforced") is True, "sequence enforcement must be enabled")
    require(authorization.get("maxMessageBytes") == 4096, "max message size mismatch")
    require(authorization.get("schemaUnknownFieldsRejected") is True, "unknown fields must be rejected")
    require(authorization.get("publicBind") is False, "public bind must stay false")
    require(authorization.get("operatorSecretsOutsideGit") is True, "operator secrets must stay outside git")
    return authorization


def validate_contract(path: Path) -> dict[str, Any]:
    contract = read_json(path)
    require_no_serialized_credentials(contract)
    require(contract.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(contract.get("scope") == EXPECTED_SCOPE, "scope mismatch")
    require(contract.get("status") == "complete public-safe N-slot session schema proof; no BEA launch or runtime proof", "status mismatch")
    require_source_contract(contract)
    runtime = require_runtime_boundary(contract)
    descriptor = require_session_descriptor(contract)
    modes = require_mode_profiles(contract)
    scheduler = require_scheduler(contract)
    authorization = require_authorization(contract)
    non_claims = object_at(contract, "nonClaims")
    for key, value in non_claims.items():
        require(value is False, f"non-claim must remain false: {key}")
    return {
        "schemaVersion": contract["schemaVersion"],
        "sessionSchema": descriptor["schemaVersion"],
        "protocolVersion": descriptor["protocolVersion"],
        "slotCapacity": descriptor["slotCapacity"],
        "acceptedSessionParticipantCount": descriptor["acceptedSessionParticipantCount"],
        "originalBinaryPlayerSlotsProven": runtime["originalBinaryPlayerSlotsProven"],
        "maxOriginalBinaryActiveSlots": runtime["maxOriginalBinaryActiveSlots"],
        "nPlayerOriginalBinaryRuntimeProof": runtime["nPlayerOriginalBinaryRuntimeProof"],
        "coOpVersusModeRuntimeProofSlices": runtime["coOpVersusModeRuntimeProofSlices"],
        "modeProfiles": sorted(row["sessionType"] for row in modes),
        "acceptedOriginalBinaryGameplayCommandCount": scheduler["acceptedOriginalBinaryGameplayCommandCount"],
        "rejectedOriginalBinaryGameplayCommandCount": scheduler["rejectedOriginalBinaryGameplayCommandCount"],
        "deterministicParticipantOrder": scheduler["deterministicParticipantOrder"],
        "deterministicOriginalBinaryRelayOrder": scheduler["deterministicOriginalBinaryRelayOrder"],
        "relayPlanSha256": scheduler["relayPlanSha256"],
        "authorization": {
            "scheme": authorization["scheme"],
            "slotIdentityMode": authorization["slotIdentityMode"],
            "replayCacheEnabled": authorization["replayCacheEnabled"],
            "sequenceEnforced": authorization["sequenceEnforced"],
            "publicBind": authorization["publicBind"],
        },
        "claimBoundary": (
            "This validates a public-safe four-slot host-authority session/schema proof only. It accepts P1-P4 as "
            "session participants while preserving the original-binary gameplay route cap at P1/P2 and rejecting P3/P4 "
            "gameplay input. It does not prove more than two original-binary runtime players, co-op/versus runtime "
            "behavior, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rebuild parity, "
            "or no-noticeable-difference parity."
        ),
    }


def require_doc_tokens() -> None:
    token_sets = {
        READINESS: (
            "Original Binary Online N-Slot Session Schema Readiness Note",
            "original-binary-online-n-slot-session-schema",
            "winui-original-binary-online-n-slot-session-schema.v1",
            "slotCapacity=4",
            "acceptedSessionParticipantCount=4",
            "originalBinaryPlayerSlotsProven=P1,P2",
            "maxOriginalBinaryActiveSlots=2",
            "P3/P4 metadata-only",
            "unsupported-original-binary-active-slot",
            "required-for-unproven-original-binary-slots",
            "missing-relayPlanHash",
            "rejectedOriginalBinaryGameplayCommandCount=2",
            "cooperative",
            "versus-free-for-all",
            "team-versus",
            "spectator-admin",
            "not a BEA launch/capture/stop run",
        ),
        FEASIBILITY: (
            "N-slot session schema proof",
            "original-binary-online-n-slot-session-schema.v1.json",
            "slotCapacity=4",
            "acceptedSessionParticipantCount=4",
            "P3/P4 metadata-only",
            "unsupported-original-binary-active-slot",
            "co-op/versus runtime behavior remains unproven",
        ),
        LOCAL_CONTRACT: (
            "N-slot session schema proof",
            "1 public-safe four-slot session/schema proof",
            "slotCapacity=4",
            "acceptedSessionParticipantCount=4",
            "P3/P4 metadata-only",
            "nPlayerOriginalBinaryRuntimeProof=0",
        ),
        REGISTER: (
            "1 public-safe four-slot session/schema proof",
            "slotCapacity=4",
            "acceptedSessionParticipantCount=4",
            "P3/P4 metadata-only",
            "unsupported-original-binary-active-slot",
            "rejectedOriginalBinaryGameplayCommandCount=2",
        ),
        CAPABILITIES: (
            "online N-slot session schema",
            "slotCapacity=4",
            "acceptedSessionParticipantCount=4",
            "P3/P4 metadata-only",
            "rejectedOriginalBinaryGameplayCommandCount=2",
            "nPlayerOriginalBinaryRuntimeProof=0",
        ),
        MAPPED_SYSTEMS: (
            "Original-binary online N-slot session schema",
            "slotCapacity=4",
            "acceptedSessionParticipantCount=4",
            "P3/P4 metadata-only",
            "unsupported-original-binary-active-slot",
        ),
    }
    for path, tokens in token_sets.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"{path} missing token: {token}")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:winui-original-binary-online-n-slot-session-schema") == EXPECTED_SCRIPT,
        "missing package N-slot session schema checker script",
    )


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
        bad["runtimeBoundary"]["maxOriginalBinaryActiveSlots"] = 4
        write_json(path, bad)
        try:
            validate_contract(path)
        except NSlotSessionSchemaError:
            pass
        else:
            raise AssertionError("original-binary active-slot overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["sessionDescriptor"]["participants"][2]["commandPermission"] = "original-binary-command-allowed-when-authenticated"
        write_json(path, bad)
        try:
            validate_contract(path)
        except NSlotSessionSchemaError:
            pass
        else:
            raise AssertionError("P3 gameplay command permission should fail")

        bad = json.loads(json.dumps(good))
        bad["modeProfiles"][0]["runtimeProofStatus"] = "runtime-proven"
        write_json(path, bad)
        try:
            validate_contract(path)
        except NSlotSessionSchemaError:
            pass
        else:
            raise AssertionError("mode runtime overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["hostAuthorityNSlotScheduler"]["relayPlan"].append(
            {
                "scheduledTick": 1,
                "clientSlot": "P3",
                "commandId": "host-authority-p3-forward-0001",
                "mappedInputSequence": "down:R,wait:500,up:R",
                "route": "P3/unproven",
                "hostHelperInputSent": False,
            }
        )
        bad["hostAuthorityNSlotScheduler"]["relayPlanSha256"] = sha256_payload(bad["hostAuthorityNSlotScheduler"]["relayPlan"])
        write_json(path, bad)
        try:
            validate_contract(path)
        except NSlotSessionSchemaError:
            pass
        else:
            raise AssertionError("P3 relay plan should fail")

        bad = json.loads(json.dumps(good))
        bad["authorization"]["publicBind"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except NSlotSessionSchemaError:
            pass
        else:
            raise AssertionError("public bind should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary online N-slot session schema checker self-test: PASS")
        return 0
    if not args.check:
        raise SystemExit("use --check or --self-test")
    print(json.dumps(validate_repo_contract(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except NSlotSessionSchemaError as exc:
        print(f"WinUI original-binary online N-slot session schema check: FAIL: {exc}")
        raise SystemExit(2)
