#!/usr/bin/env python3
"""Build a loopback remote-intent proof bundle from a copied-BEA live artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "winui-original-binary-loopback-p2-input.v1"
HELPER_NAME = "winui-original-binary-loopback-helper"
HELPER_VERSION = "loopback-helper.v1"
PROTOCOL_VERSION = "loopback-input.v1"
CLEAN_SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
MAPPED_SEQUENCE = "down:E,wait:500,up:E"


class BundleBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BundleBuildError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def relative_path(from_path: Path, to_path: Path) -> str:
    try:
        return to_path.resolve().relative_to(from_path.resolve()).as_posix()
    except ValueError:
        return str(to_path.resolve())


def find_sequence_window(live: dict[str, Any], sequence: str) -> dict[str, Any]:
    rows = list_at(live, "inputCdbWindows")
    matches = [row for row in rows if isinstance(row, dict) and row.get("sequence") == sequence]
    require(len(matches) == 1, f"expected exactly one input CDB window for {sequence!r}")
    return matches[0]


def build_bundle(live_artifact_path: Path, output_path: Path) -> dict[str, Any]:
    live_artifact_path = live_artifact_path.resolve()
    live = read_json(live_artifact_path)
    require(live.get("schemaVersion") == "winui-safe-copy-live-runtime-smoke.v1", "unexpected live artifact schema")

    source = object_at(live, "source")
    override_hash = str(source.get("overrideHashBefore", "")).lower()
    require(override_hash == CLEAN_SPECIMEN_SHA256, "live artifact did not use the canonical clean specimen override")

    safe_copy = object_at(live, "safeCopy")
    launch = object_at(live, "launch")
    control_options = object_at(safe_copy, "controlOptions")
    cdb_window = find_sequence_window(live, MAPPED_SEQUENCE)
    command_window_index = cdb_window.get("index")
    require(isinstance(command_window_index, int), "input CDB window index is missing")

    manifest_path = Path(str(safe_copy.get("ManifestPath") or ""))
    profile_root = Path(str(safe_copy.get("TargetGameRoot") or ""))
    require(profile_root.is_dir(), "safe-copy profile root is missing")
    require(manifest_path.is_file(), "safe-copy profile manifest is missing")

    patch_keys = safe_copy.get("patchKeys")
    require(isinstance(patch_keys, list), "safeCopy.patchKeys must be a list")
    launch_arguments = launch.get("arguments")
    require(launch_arguments == ["-skipfmv", "-level", "850", "-configuration", "1"], "unexpected launch arguments")

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_root = output_path.parent
    bundle = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER_NAME,
        "generatedAtSource": str(live.get("generatedAt", "")),
        "liveRuntimeArtifact": relative_path(bundle_root, live_artifact_path),
        "session": {
            "helperName": HELPER_NAME,
            "helperVersion": HELPER_VERSION,
            "protocolVersion": PROTOCOL_VERSION,
            "cleanSpecimenSha256": CLEAN_SPECIMEN_SHA256,
            "safeCopyProfileRoot": str(profile_root.resolve()),
            "profileManifestPath": str(manifest_path.resolve()),
            "profileManifestSha256": sha256_file(manifest_path),
            "patchKeys": patch_keys,
            "profilePresetId": safe_copy.get("ProfilePresetId"),
            "launchArguments": launch_arguments,
            "levelId": 850,
            "controllerConfiguration": 1,
            "remotePlayerSlot": "P2",
            "mappedInputSequence": MAPPED_SEQUENCE,
            "inputCdbWindowIndex": command_window_index,
            "controlOptionsProofLever": control_options.get("proofLever"),
        },
        "commands": {
            "accepted": [
                {
                    "commandId": "loopback-p2-forward-0001",
                    "order": 1,
                    "remoteSlot": "P2",
                    "command": "movement-forward",
                    "mappedInputSequence": MAPPED_SEQUENCE,
                    "cdbInputWindowIndex": command_window_index,
                    "inputSent": True,
                }
            ],
            "rejected": [
                {
                    "commandId": "loopback-reject-malformed-0001",
                    "reason": "malformed-command",
                    "inputSent": False,
                },
                {
                    "commandId": "loopback-reject-p1-0001",
                    "remoteSlot": "P1",
                    "reason": "remote-slot-not-allowed",
                    "inputSent": False,
                },
            ],
        },
        "loopback": {
            "transport": "local-loopback-mock",
            "protocolVersion": PROTOCOL_VERSION,
            "remoteSlot": "P2",
            "command": "movement-forward",
            "mappedInputSequence": MAPPED_SEQUENCE,
            "networkSocketsOpened": False,
            "matchmakingServerContacted": False,
            "publicServerClaim": False,
            "nativeBeaNetcodeClaim": False,
        },
        "claimBoundary": (
            "Local loopback command-envelope proof only. This is not online play, matchmaking, public relay/server "
            "behavior, native BEA netcode, deterministic sync, anti-cheat, physical gamepad proof, or rebuild parity."
        ),
    }
    output_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("live_artifact", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    live_artifact_path = args.live_artifact
    output_path = args.output or live_artifact_path.with_name("loopback-p2-input-proof.json")
    build_bundle(live_artifact_path, output_path)
    print(json.dumps({"bundle": str(output_path.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BundleBuildError as exc:
        print(f"WinUI original-binary loopback P2 bundle build: FAIL: {exc}")
        raise SystemExit(2)
