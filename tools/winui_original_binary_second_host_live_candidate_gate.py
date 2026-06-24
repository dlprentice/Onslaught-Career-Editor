#!/usr/bin/env python3
"""Fail-closed private candidate gates for second-host online proof promotion."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping

import winui_safe_copy_online_second_host_command_source_check as command_source
import winui_safe_copy_online_second_host_runtime_causality_check as runtime_causality


COMMAND_SOURCE_ENV = "SECOND_HOST_COMMAND_SOURCE_BUNDLE"
RUNTIME_CAUSALITY_ENV = "SECOND_HOST_RUNTIME_CAUSALITY_CANDIDATE"
HEX64 = set("0123456789abcdef")
WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"(?i)\b[a-z]:[\\/][^\r\n]*")
UNC_ABSOLUTE_PATH_RE = re.compile(r"\\\\[^\r\n]+")
POSIX_PRIVATE_PATH_RE = re.compile(r"(?:(?:/home|/users|/tmp|/var/tmp)/[^\r\n]+)", re.IGNORECASE)
ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CLAIM_BOUNDARY_DOCS = (
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md",
    ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md",
    ROOT / "lore-book" / "CURRENT_CAPABILITIES.md",
    ROOT / "lore-book" / "roadmap" / "original-binary-online-multiplayer-feasibility.md",
    ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md",
    ROOT / "release" / "readiness" / "winui_original_binary_second_host_live_candidate_gate_2026-06-22.md",
    ROOT / "release" / "readiness" / "winui_original_binary_second_host_runtime_causality_raw_material_plan_2026-06-22.md",
)
PUBLIC_REQUIRED_BOUNDARY_TOKENS = (
    "Online play is not available in this release",
    "private-candidate-validation-not-host-join-enablement",
    "Host/Join remains disabled",
    "hostJoinControlsMayBeEnabled=false",
    "baseOnlineMultiplayerReady=false",
)
PUBLIC_TRUE_LIVE_STATUS_RE = re.compile(
    r"[`\"']?\b(?:acceptedLiveSecondHost(?:CommandSourceProof|RuntimeDeliveryProof|RuntimeCausalityProof)|hostJoinControlsMayBeEnabled|baseOnlineMultiplayerReady|multiHostLanPlayProof|multiHostLanProof|playerReadyOnlineMultiplayer|publicMatchmakingProof|nativeBeaNetcodeProof|secondPhysicalHostProof|activeP3P4OriginalBinaryGameplayProof)\b[`\"']?\s*(?::|=)\s*[`\"']?true[`\"']?",
    re.IGNORECASE,
)
PUBLIC_PROSE_ONLINE_READY_RE = re.compile(
    r"\b(?:host/join\s+(?:is\s+)?ready|ready\s+to\s+(?:host|join)|online multiplayer\s+(?:is\s+)?ready|(?:is|now|becomes|supports)\s+player-ready\s+online multiplayer)\b",
    re.IGNORECASE,
)
PUBLIC_CLAIM_BOUNDARY_EXACT_DOCS = {
    "current_capabilities.md",
    "readme.md",
    "readme.release.md",
    "release_scope_and_test_commands.md",
}
PUBLIC_CLAIM_BOUNDARY_PREFIXES = (
    "roadmap/",
    "release/readiness/",
    "lore-book/",
)


class LiveCandidateGateError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LiveCandidateGateError(message)


def redact_private_paths(message: str) -> str:
    redacted = WINDOWS_ABSOLUTE_PATH_RE.sub("<redacted-private-path>", message)
    redacted = UNC_ABSOLUTE_PATH_RE.sub("<redacted-private-path>", redacted)
    redacted = POSIX_PRIVATE_PATH_RE.sub("<redacted-private-path>", redacted)
    return redacted


def nested_rejection(prefix: str, exc: Exception) -> LiveCandidateGateError:
    return LiveCandidateGateError(f"{prefix}: {redact_private_paths(str(exc))}")


def require_hex64(value: Any, label: str) -> str:
    text = str(value or "")
    require(len(text) == 64 and all(char in HEX64 for char in text), f"{label} must be a lowercase sha256")
    return text


def path_from_env_or_arg(path: Path | str | None, env_name: str, env: Mapping[str, str] | None) -> Path:
    if path is not None:
        return Path(path)
    source = os.environ if env is None else env
    raw = str(source.get(env_name) or "").strip()
    require(raw, f"{env_name} is required for private live/candidate validation")
    return Path(raw)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path.name} must contain a JSON object")
    return value


def object_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    require(isinstance(value, dict), f"{key} object is required")
    return value


def accepted_command_source_binding(bundle_path: Path) -> dict[str, str]:
    payload = read_json(bundle_path)
    commands = object_at(payload, "commands")
    accepted = commands.get("accepted")
    require(isinstance(accepted, list) and len(accepted) == 1, "command-source candidate must carry exactly one accepted command")
    accepted_row = accepted[0]
    require(isinstance(accepted_row, dict), "accepted command row must be an object")
    invitation = object_at(payload, "invitationLifecycle")
    return {
        "acceptedSecondHostCommandRequestPayloadSha256": require_hex64(
            accepted_row.get("requestPayloadSha256"),
            "commands.accepted[0].requestPayloadSha256",
        ),
        "secondHostInvitationLifecycleSha256": require_hex64(
            invitation.get("sanitizedInvitationDescriptorSha256"),
            "invitationLifecycle.sanitizedInvitationDescriptorSha256",
        ),
    }


def validate_command_source_live_candidate(
    *,
    path: Path | str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    candidate_path = path_from_env_or_arg(path, COMMAND_SOURCE_ENV, env)
    try:
        summary = command_source.validate_bundle(candidate_path, require_live=True)
        binding = accepted_command_source_binding(candidate_path)
    except Exception as exc:  # noqa: BLE001 - normalize nested validator errors for a fail-closed CLI.
        raise nested_rejection("command-source live candidate rejected", exc) from exc

    require(summary.get("acceptedLiveSecondHostCommandSourceProof") is True, "command-source live proof was not accepted")
    require(summary.get("secondHostCommandSourceProof") is True, "second-host command-source proof flag missing")
    require(summary.get("liveValidationMode") is True, "command-source candidate must run in --live mode")
    require(summary.get("gameInputSentBySecondHostClient") is False, "second-host client must not send direct game input")
    require(summary.get("hostHelperInputSent") is False, "command-source proof must not send host-helper input")
    require(summary.get("baseOnlineMultiplayerReady") is False, "command-source proof cannot claim base online readiness")
    require(summary.get("publicMatchmakingProof") is False, "command-source proof cannot claim public matchmaking")
    require(summary.get("nativeBeaNetcodeProof") is False, "command-source proof cannot claim native BEA netcode")
    enriched = dict(summary)
    enriched.update(binding)
    return enriched


def validate_runtime_causality_candidate(
    *,
    path: Path | str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    candidate_path = path_from_env_or_arg(path, RUNTIME_CAUSALITY_ENV, env)
    try:
        summary = runtime_causality.validate_causality_candidate(
            runtime_causality.read_json(candidate_path),
            candidate_path=candidate_path,
            allow_fixture=False,
        )
    except Exception as exc:  # noqa: BLE001 - normalize nested validator errors for a fail-closed CLI.
        raise nested_rejection("runtime-causality candidate rejected", exc) from exc

    require(summary.get("selfTestFixtureCandidate") is False, "runtime-causality candidate must not be a self-test fixture")
    require(summary.get("runtimeInputDerivedFromSecondHostCommandSource") is True, "runtime input must derive from second-host command source")
    require(summary.get("runtimeDrivenBySecondHostCommandSource") is True, "runtime must be driven by second-host command source")
    require(summary.get("acceptedLiveSecondHostRuntimeDeliveryProof") is True, "runtime delivery proof was not accepted")
    require(summary.get("rawArtifactReceiptsRecomputed") is True, "raw artifact receipts must be recomputed")
    require(summary.get("hostJoinControlsMayBeEnabled") is False, "runtime candidate must not enable Host/Join directly")
    require(summary.get("baseOnlineMultiplayerReady") is False, "runtime candidate must not claim base online readiness")
    return summary


def validate_candidate_summary_pair(command_summary: dict[str, Any], runtime_summary: dict[str, Any]) -> dict[str, Any]:
    command_payload_hash = require_hex64(
        command_summary.get("acceptedSecondHostCommandRequestPayloadSha256"),
        "command-source accepted payload hash",
    )
    runtime_payload_hash = require_hex64(
        runtime_summary.get("acceptedSecondHostCommandRequestPayloadSha256"),
        "runtime-causality accepted payload hash",
    )
    command_invitation_hash = require_hex64(
        command_summary.get("secondHostInvitationLifecycleSha256"),
        "command-source invitation lifecycle hash",
    )
    runtime_invitation_hash = require_hex64(
        runtime_summary.get("secondHostInvitationLifecycleSha256"),
        "runtime-causality invitation lifecycle hash",
    )
    require(command_payload_hash == runtime_payload_hash, "command-source and runtime-causality payload hashes do not match")
    require(command_invitation_hash == runtime_invitation_hash, "command-source and runtime-causality invitation hashes do not match")
    require(command_summary.get("acceptedLiveSecondHostCommandSourceProof") is True, "command-source live proof is not accepted")
    require(runtime_summary.get("acceptedLiveSecondHostRuntimeDeliveryProof") is True, "runtime delivery proof is not accepted")
    require(runtime_summary.get("runtimeDrivenBySecondHostCommandSource") is True, "runtime is not driven by second-host command source")
    require(runtime_summary.get("rawArtifactReceiptsRecomputed") is True, "runtime raw artifact receipts are not recomputed")
    require(command_summary.get("baseOnlineMultiplayerReady") is False, "command-source candidate must not claim base online readiness")
    require(runtime_summary.get("baseOnlineMultiplayerReady") is False, "runtime candidate must not claim base online readiness")
    require(runtime_summary.get("hostJoinControlsMayBeEnabled") is False, "candidate input validation must not enable Host/Join")
    return {
        "schemaVersion": "winui-original-binary-second-host-live-candidate-gate.v1",
        "gateScope": "private-candidate-validation-not-host-join-enablement",
        "acceptedLiveSecondHostCommandSourceProof": True,
        "acceptedLiveSecondHostRuntimeDeliveryProof": True,
        "candidateAcceptedLiveSecondHostCommandSourceProof": True,
        "candidateAcceptedLiveSecondHostRuntimeDeliveryProof": True,
        "payloadHashMatched": True,
        "invitationLifecycleHashMatched": True,
        "runtimeDrivenBySecondHostCommandSource": True,
        "rawArtifactReceiptsRecomputed": True,
        "hostJoinPromotionGateRequired": True,
        "hostJoinControlsMayBeEnabled": False,
        "baseOnlineMultiplayerReady": False,
        "playerReadyOnlineMultiplayer": False,
        "publicMatchmakingProof": False,
        "nativeBeaNetcodeProof": False,
        "claimBoundary": "Candidate inputs validated; Host/Join remains disabled until a separate product/release promotion gate is intentionally added.",
    }


def discover_public_claim_boundary_docs() -> tuple[Path, ...]:
    discovered = set(PUBLIC_CLAIM_BOUNDARY_DOCS)
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return tuple(sorted(discovered, key=lambda path: path.as_posix().lower()))
    for row in result.stdout.splitlines():
        rel = row.strip().replace("\\", "/")
        lowered = rel.lower()
        if not lowered.endswith(".md"):
            continue
        if lowered in PUBLIC_CLAIM_BOUNDARY_EXACT_DOCS or lowered.startswith(PUBLIC_CLAIM_BOUNDARY_PREFIXES):
            discovered.add(ROOT / rel)
    return tuple(sorted(discovered, key=lambda path: path.as_posix().lower()))


def validate_public_claim_boundary(paths: list[Path] | tuple[Path, ...] | None = None) -> dict[str, Any]:
    checked_paths = list(discover_public_claim_boundary_docs() if paths is None else paths)
    combined: list[str] = []
    for path in checked_paths:
        require(path.is_file(), f"public claim-boundary doc is missing: {path.name}")
        text = path.read_text(encoding="utf-8-sig")
        match = PUBLIC_TRUE_LIVE_STATUS_RE.search(text)
        if match is not None:
            raise LiveCandidateGateError(f"{path.name} must not publish online proof/readiness as true: {match.group(0)}")
        prose_match = PUBLIC_PROSE_ONLINE_READY_RE.search(text)
        if prose_match is not None:
            raise LiveCandidateGateError(f"{path.name} must not publish Host/Join readiness prose: {prose_match.group(0)}")
        combined.append(text)
    combined_text = "\n".join(combined)
    missing = [token for token in PUBLIC_REQUIRED_BOUNDARY_TOKENS if token not in combined_text]
    require(not missing, f"public claim-boundary tokens missing: {', '.join(missing)}")
    return {
        "schemaVersion": "winui-original-binary-second-host-public-claim-boundary.v1",
        "gateScope": "public-doc-candidate-claim-boundary",
        "checkedFileCount": len(checked_paths),
        "requiredBoundaryTokenCount": len(PUBLIC_REQUIRED_BOUNDARY_TOKENS),
        "candidateReadyIsNotPlayerReady": True,
        "acceptedLiveProofPublishedAsReady": False,
        "hostJoinControlsMayBeEnabled": False,
        "baseOnlineMultiplayerReady": False,
    }


def validate_host_join_candidate(
    *,
    command_path: Path | str | None = None,
    runtime_path: Path | str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    command_summary = validate_command_source_live_candidate(path=command_path, env=env)
    runtime_summary = validate_runtime_causality_candidate(path=runtime_path, env=env)
    return validate_candidate_summary_pair(command_summary, runtime_summary)


def run_self_test() -> None:
    for validator, env_name in (
        (validate_command_source_live_candidate, COMMAND_SOURCE_ENV),
        (validate_runtime_causality_candidate, RUNTIME_CAUSALITY_ENV),
    ):
        try:
            validator(env={})
        except LiveCandidateGateError as exc:
            require(env_name in str(exc), f"{env_name} missing-env test did not mention the env var")
        else:
            raise AssertionError(f"{env_name} missing-env test should fail")

    runtime_causality.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=runtime_causality.PRIVATE_PROOF_ROOT) as tmp:
        fixture_path = runtime_causality.write_file_backed_self_test_candidate(Path(tmp))
        try:
            validate_runtime_causality_candidate(path=fixture_path)
        except LiveCandidateGateError:
            pass
        else:
            raise AssertionError("runtime self-test candidate should fail candidate gate")

    matching_hash = "a" * 64
    invitation_hash = "b" * 64
    validate_candidate_summary_pair(
        {
            "acceptedLiveSecondHostCommandSourceProof": True,
            "acceptedSecondHostCommandRequestPayloadSha256": matching_hash,
            "secondHostInvitationLifecycleSha256": invitation_hash,
            "baseOnlineMultiplayerReady": False,
        },
        {
            "acceptedLiveSecondHostRuntimeDeliveryProof": True,
            "runtimeDrivenBySecondHostCommandSource": True,
            "rawArtifactReceiptsRecomputed": True,
            "acceptedSecondHostCommandRequestPayloadSha256": matching_hash,
            "secondHostInvitationLifecycleSha256": invitation_hash,
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
        },
    )
    validate_public_claim_boundary()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", choices=("command-source-live", "runtime-causality-candidate", "host-join-candidate"))
    parser.add_argument("--command-source", type=Path)
    parser.add_argument("--runtime-causality", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary second-host live candidate gate self-test: PASS")
        return 0
    require(args.check is not None, "--check is required unless --self-test is used")
    if args.check == "command-source-live":
        summary = validate_command_source_live_candidate(path=args.command_source)
    elif args.check == "runtime-causality-candidate":
        summary = validate_runtime_causality_candidate(path=args.runtime_causality)
    else:
        summary = validate_host_join_candidate(command_path=args.command_source, runtime_path=args.runtime_causality)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LiveCandidateGateError, json.JSONDecodeError) as exc:
        print(f"WinUI original-binary second-host live candidate gate: FAIL: {exc}")
        raise SystemExit(2)
