#!/usr/bin/env python3
"""Second-host client runner for the original-binary command-source harness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_winui_original_binary_second_host_command_source_bundle as builder


def build_identity_preflight_summary(
    *,
    client_machine_fingerprint: str | None = None,
    client_copied_profile_sha256: str | None = None,
    client_installed_game_sha256: str | None = None,
    client_copied_profile_root: Path | None = None,
    client_installed_game_root: Path | None = None,
    client_runtime_host_kind: str | None = None,
) -> dict[str, object]:
    machine_identity = builder.make_machine_identity_preflight(
        client_machine_fingerprint,
        runtime_host_kind=client_runtime_host_kind,
    )
    source_safety = builder.make_source_safety_side_evidence(
        role="client",
        copied_profile_sha256=client_copied_profile_sha256,
        installed_game_sha256=client_installed_game_sha256,
        copied_profile_root=client_copied_profile_root,
        installed_game_root=client_installed_game_root,
    )
    fingerprint = str(machine_identity["machineFingerprint"])
    return {
        "schemaVersion": "winui-original-binary-second-host-client-preflight.v1",
        "scope": "second-host-client-identity-source-safety-preflight-not-command-source-proof",
        "clientIdentityFingerprint": fingerprint,
        "machineIdentity": machine_identity,
        "clientSourceSafety": source_safety,
        "copyForServerArgument": f"--client-identity-fingerprint {fingerprint}",
        "copyForClientRuntimeHostKindArgument": (
            "omit manual runtime-kind overrides for live proof; manual overrides are attempt-only diagnostics"
        ),
        "privateProofCreated": False,
        "gameInputSent": False,
        "baseOnlineMultiplayerReady": False,
        "acceptedLiveSecondHostCommandSourceProof": False,
        "acceptedLiveSecondHostRuntimeDeliveryProof": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("invitation", type=Path, nargs="?")
    parser.add_argument("--identity-preflight", action="store_true")
    parser.add_argument("--client-machine-fingerprint")
    parser.add_argument("--client-copied-profile-sha256")
    parser.add_argument("--client-installed-game-sha256")
    parser.add_argument("--client-copied-profile-root", type=Path)
    parser.add_argument("--client-installed-game-root", type=Path)
    parser.add_argument("--client-runtime-host-kind", choices=sorted(builder.KNOWN_RUNTIME_HOST_KINDS))
    args = parser.parse_args()

    if args.identity_preflight:
        summary = build_identity_preflight_summary(
            client_machine_fingerprint=args.client_machine_fingerprint,
            client_copied_profile_sha256=args.client_copied_profile_sha256,
            client_installed_game_sha256=args.client_installed_game_sha256,
            client_copied_profile_root=args.client_copied_profile_root,
            client_installed_game_root=args.client_installed_game_root,
            client_runtime_host_kind=args.client_runtime_host_kind,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    if args.invitation is None:
        parser.error("invitation is required unless --identity-preflight is used")

    summary = builder.run_client(
        args.invitation,
        client_machine_fingerprint=args.client_machine_fingerprint,
        client_copied_profile_sha256=args.client_copied_profile_sha256,
        client_installed_game_sha256=args.client_installed_game_sha256,
        client_copied_profile_root=args.client_copied_profile_root,
        client_installed_game_root=args.client_installed_game_root,
        client_runtime_host_kind=args.client_runtime_host_kind,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
