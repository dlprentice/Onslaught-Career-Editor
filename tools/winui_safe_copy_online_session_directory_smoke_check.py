#!/usr/bin/env python3
"""Validate local session-directory smoke proof for original-binary online groundwork."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_online_session_directory_smoke_bundle as builder


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness" / "original_binary_online_session_directory_smoke_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCRIPT = (
    r"py -3 tools\winui_safe_copy_online_session_directory_smoke_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_session_directory_smoke_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_session_directory_smoke_check.py --check"
)
EXPECTED_REJECTION_REASONS = {
    "public-matchmaking-not-allowed",
    "public-bind-not-allowed",
    "native-bea-netcode-not-proven",
    "multi-host-lan-not-proven",
    "required-for-unproven-original-binary-slots",
    "co-op-versus-mode-runtime-not-proven",
    "clean-specimen-mismatch",
    "protocol-version-mismatch",
    "unknown-field",
    "max-json-line-bytes-exceeded",
    "secret-bearing-listing-rejected",
    "raw-private-path-listing-rejected",
    "duplicate-session-id",
}
DANGEROUS_VALUE_TOKENS = ("password", "api_key", "apikey", "auth_token", "secret_value")


class SessionDirectorySmokeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SessionDirectorySmokeError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def require_no_secret_values(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require_no_secret_values(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_no_secret_values(child, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        require(not any(token in lowered for token in DANGEROUS_VALUE_TOKENS), f"secret-like value at {path}")


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = read_json(path)
    require_no_secret_values(bundle)
    require(bundle.get("schemaVersion") == builder.SCHEMA, "schema mismatch")
    require(bundle.get("generatedBy") == builder.HELPER, "helper mismatch")
    require(bundle.get("helperVersion") == builder.HELPER_VERSION, "helper version mismatch")
    require(bundle.get("protocolVersion") == builder.PROTOCOL, "protocol mismatch")
    require(bundle.get("directoryScope") == builder.DIRECTORY_SCOPE, "directory scope mismatch")

    source = object_at(bundle, "sourceProofs")
    require(source.get("sessionSecurityProofSha256") == builder.SESSION_SECURITY_PROOF_SHA256, "session-security proof hash mismatch")
    require(source.get("sessionRelayPlanSha256") == builder.SESSION_RELAY_PLAN_SHA256, "session relay hash mismatch")
    require(source.get("runtimeCompatibleP1P2RelayHash") == builder.RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256, "runtime relay hash mismatch")
    require(source.get("secureExecutorReplayabilityProofHashes") == builder.SECURE_EXECUTOR_PROOF_SHA256_VALUES, "executor replayability hashes mismatch")

    directory = object_at(bundle, "directory")
    require(directory.get("transport") == "same-workstation-in-memory-session-directory", "directory transport mismatch")
    require(directory.get("networkScope") == builder.DIRECTORY_SCOPE, "directory network scope mismatch")
    require(directory.get("publicNetworkSocketsOpened") is False, "directory must not open public sockets")
    require(directory.get("publicBind") is False, "directory must not bind public sockets")
    require(directory.get("publicMatchmakingClaim") is False, "directory must not claim public matchmaking")
    require(directory.get("matchmakingServerContacted") is False, "directory must not contact matchmaking")
    require(directory.get("operatorSecretsRequired") is False, "directory must not require operator secrets")
    require(directory.get("credentialStorage") == "ephemeral-not-serialized", "credential storage mismatch")
    require(directory.get("serializedCredentialPresent") is False, "serialized credentials must be absent")
    require(directory.get("maxJsonLineBytes") == 4096, "max JSON line bytes mismatch")
    require(directory.get("unknownFieldRejectionProof") is True, "unknown-field proof missing")
    require(directory.get("strictMessageSchemaProof") is True, "strict schema proof missing")
    require(isinstance(directory.get("serverIdentityFingerprint"), str) and len(directory["serverIdentityFingerprint"]) == 64, "server identity fingerprint missing")

    sessions = list_at(bundle, "registeredSessions")
    require(len(sessions) == 1, "exactly one local directory session should be registered")
    session = sessions[0]
    require(isinstance(session, dict), "registered session must be object")
    require(session.get("cleanSpecimenSha256") == builder.CLEAN_SPECIMEN_SHA256, "session clean specimen mismatch")
    require(session.get("slotCapacity") == 4, "session slot capacity mismatch")
    require(session.get("acceptedOriginalBinaryGameplaySlots") == builder.ACTIVE_SLOTS, "accepted slots mismatch")
    require(session.get("metadataOnlySlots") == builder.METADATA_SLOTS, "metadata slots mismatch")
    require(session.get("rejectedGameplayRouteSlots") == builder.METADATA_SLOTS, "rejected route slots mismatch")
    require(session.get("maxOriginalBinaryActiveSlotsProven") == 2, "max original-binary active slots must stay two")
    require(session.get("runtimeCompatibleP1P2RelayHash") == builder.RUNTIME_COMPATIBLE_P1P2_RELAY_SHA256, "session relay hash mismatch")
    for key in ("publicAddressPublished", "rawPrivateRuntimePathPublished", "operatorSecretPublished", "directConnectionAddressPublished"):
        require(session.get(key) is False, f"session leak/overclaim must be false: {key}")

    queries = object_at(bundle, "queries")
    accepted = list_at(queries, "accepted")
    rejected = list_at(queries, "rejected")
    require(len(accepted) == 1, "expected one accepted directory query")
    accepted_query = accepted[0]
    require(isinstance(accepted_query, dict), "accepted query must be object")
    require(accepted_query.get("directoryAccepted") is True, "accepted query not accepted")
    require(accepted_query.get("listingReturned") is True, "accepted query did not return listing")
    require(accepted_query.get("returnedListingCount") == 1, "accepted query listing count mismatch")
    for key in ("publicAddressPublished", "rawPrivateRuntimePathPublished", "operatorSecretPublished"):
        require(accepted_query.get(key) is False, f"accepted query leak/overclaim must be false: {key}")
    returned = list_at(accepted_query, "returnedListings")
    require(len(returned) == 1, "expected one redacted listing")
    require("sessionSecurityProofSha256" not in returned[0], "returned public listing should be redacted from proof internals")

    reasons = {str(row.get("reason")) for row in rejected if isinstance(row, dict)}
    require(EXPECTED_REJECTION_REASONS.issubset(reasons), "directory rejection matrix missing required reasons")
    for row in rejected:
        require(isinstance(row, dict), "rejected query must be object")
        require(row.get("directoryAccepted") is False, "rejected query accepted")
        require(row.get("listingReturned") is False, "rejected query returned listing")
        require(row.get("joinTicketIssued") is False, "rejected query issued ticket")

    tickets = object_at(bundle, "joinTickets")
    accepted_tickets = list_at(tickets, "accepted")
    rejected_tickets = list_at(tickets, "rejected")
    require(len(accepted_tickets) == 1, "expected one accepted join ticket")
    ticket = accepted_tickets[0]
    require(isinstance(ticket, dict), "accepted ticket must be object")
    require(ticket.get("clientSlot") == "P2", "accepted join ticket should target P2")
    require(isinstance(ticket.get("ticketFingerprint"), str) and len(ticket["ticketFingerprint"]) == 64, "ticket fingerprint missing")
    require(ticket.get("credentialStorage") == "ephemeral-not-serialized", "ticket credential storage mismatch")
    require(ticket.get("rawCredentialSerialized") is False, "raw ticket credential must not serialize")
    for key in ("publicServerClaim", "publicMatchmakingClaim", "multiHostLanClaim"):
        require(ticket.get(key) is False, f"ticket overclaim must be false: {key}")
    rejected_slots = {row.get("clientSlot") for row in rejected_tickets if isinstance(row, dict)}
    require(rejected_slots == set(builder.METADATA_SLOTS), "P3/P4 join-ticket rejections missing")

    counts = object_at(bundle, "counts")
    require(counts.get("registeredSessionCount") == 1, "registered session count mismatch")
    require(counts.get("compatibleListingCount") == 1, "compatible listing count mismatch")
    require(counts.get("acceptedJoinTicketCount") == 1, "accepted join-ticket count mismatch")
    require(counts.get("rejectedDirectoryCaseCount") == len(rejected), "rejected directory case count mismatch")
    for key in ("newBeaLaunchCount", "cdbAttachCount", "nPlayerOriginalBinaryRuntimeProof"):
        require(counts.get(key) == 0, f"{key} must stay zero")
    for key in ("hostHelperInputSent", "gameInputSentByDirectory", "activeP3P4OriginalBinaryGameplayProof"):
        require(counts.get(key) is False, f"{key} must stay false")

    non_claims = object_at(bundle, "nonClaims")
    for key, value in non_claims.items():
        require(value is False, f"non-claim must remain false: {key}")

    boundary = str(bundle.get("claimBoundary", "")).lower()
    for token in ("same-workstation local session-directory smoke", "does not contact a public matchmaking server", "does not prove multi-host lan play", "does not prove native bea netcode"):
        require(token in boundary, f"claim boundary missing: {token}")

    return {
        "artifact": str(path),
        "schemaVersion": bundle["schemaVersion"],
        "protocolVersion": bundle["protocolVersion"],
        "directoryScope": bundle["directoryScope"],
        "registeredSessionCount": counts["registeredSessionCount"],
        "compatibleListingCount": counts["compatibleListingCount"],
        "acceptedJoinTicketCount": counts["acceptedJoinTicketCount"],
        "rejectedDirectoryCaseCount": counts["rejectedDirectoryCaseCount"],
        "publicMatchmakingProof": non_claims["publicMatchmakingProof"],
        "multiHostLanProof": non_claims["multiHostLanProof"],
        "nativeBeaNetcodeProof": non_claims["nativeBeaNetcodeProof"],
        "nPlayerOriginalBinaryRuntimeProof": counts["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": counts["activeP3P4OriginalBinaryGameplayProof"],
    }


def check_token(path: Path, token: str, failures: list[str]) -> None:
    if token not in read_text(path):
        failures.append(f"{path} missing token: {token}")


def validate_repo() -> None:
    failures: list[str] = []
    token_sets = {
        READINESS: (
            "Original Binary Online Session Directory Smoke Readiness Note",
            "same-workstation-local-directory-smoke-not-public-matchmaking",
            "registeredSessionCount=1",
            "compatibleListingCount=1",
            "acceptedJoinTicketCount=1",
            "rejectedDirectoryCaseCount=14",
            "publicMatchmakingProof=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
        ),
        FEASIBILITY: (
            "Local session-directory smoke",
            "same-workstation-local-directory-smoke-not-public-matchmaking",
            "registeredSessionCount=1",
            "acceptedJoinTicketCount=1",
            "rejectedDirectoryCaseCount=14",
            "publicMatchmakingProof=false",
        ),
        REGISTER: (
            "1 local session-directory smoke",
            "same-workstation-local-directory-smoke-not-public-matchmaking",
            "publicMatchmakingProof=false",
            "acceptedJoinTicketCount=1",
        ),
        CAPABILITIES: (
            "local session-directory smoke",
            "same-workstation-local-directory-smoke-not-public-matchmaking",
            "registeredSessionCount=1",
            "acceptedJoinTicketCount=1",
            "publicMatchmakingProof=false",
        ),
    }
    for path, tokens in token_sets.items():
        for token in tokens:
            check_token(path, token, failures)
    if read_text(REGISTER) != read_text(REGISTER_MIRROR):
        failures.append("register lore mirror mismatch")
    if read_text(CAPABILITIES) != read_text(CAPABILITIES_MIRROR):
        failures.append("current capabilities lore mirror mismatch")
    scalability = read_json(SCALABILITY)
    directory_policy = object_at(object_at(scalability, "scalableArchitecture"), "sessionDirectorySmokePolicy")
    require(directory_policy.get("proofSchema") == builder.SCHEMA, "scalability contract session-directory schema mismatch")
    require(directory_policy.get("directoryScope") == builder.DIRECTORY_SCOPE, "scalability contract directory scope mismatch")
    require(directory_policy.get("publicMatchmakingProof") is False, "scalability contract must not claim public matchmaking")
    require(directory_policy.get("registeredSessionCount") == 1, "scalability contract registered session count mismatch")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-online-session-directory-smoke") != EXPECTED_SCRIPT:
        failures.append("package session-directory script mismatch")
    aggregate = str(scripts.get("test:winui-copied-profile-runtime", ""))
    if "test:winui-original-binary-online-session-directory-smoke" not in aggregate:
        failures.append("aggregate runtime script missing session-directory smoke")
    if failures:
        raise SessionDirectorySmokeError("\n".join(failures))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "proof.json"
        builder.build_bundle(path)
        validate_bundle(path)

        value = read_json(path)
        value["nonClaims"]["publicMatchmakingProof"] = True
        path.write_text(json.dumps(value), encoding="utf-8")
        try:
            validate_bundle(path)
        except SessionDirectorySmokeError:
            pass
        else:
            raise SessionDirectorySmokeError("public matchmaking overclaim should fail")

    for label, mutate in (
        ("public bind should fail", lambda value: value["directory"].__setitem__("publicBind", True)),
        ("native netcode claim should fail", lambda value: value["nonClaims"].__setitem__("nativeBeaNetcodeProof", True)),
        ("P3 ticket should fail", lambda value: value["joinTickets"]["accepted"][0].__setitem__("clientSlot", "P3")),
        ("serialized credential should fail", lambda value: value["joinTickets"]["accepted"][0].__setitem__("rawCredentialSerialized", True)),
        ("secret-like value should fail", lambda value: value.__setitem__("bad", "secret_value")),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proof.json"
            builder.build_bundle(path)
            value = read_json(path)
            mutate(value)
            path.write_text(json.dumps(value), encoding="utf-8")
            try:
                validate_bundle(path)
            except SessionDirectorySmokeError:
                continue
            raise SessionDirectorySmokeError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary online session-directory smoke checker self-test: PASS")
        return 0
    if args.check:
        validate_repo()
        if builder.DEFAULT_OUTPUT.is_file():
            print(json.dumps(validate_bundle(builder.DEFAULT_OUTPUT), indent=2, sort_keys=True))
        else:
            print("WinUI original-binary online session-directory smoke repo check: PASS")
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test or --check is used")
    print(json.dumps(validate_bundle(args.bundle), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SessionDirectorySmokeError as exc:
        print(f"WinUI original-binary online session-directory smoke check: FAIL: {exc}")
        raise SystemExit(2)
