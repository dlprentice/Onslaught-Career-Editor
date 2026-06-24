#!/usr/bin/env python3
"""Build and validate source-music safety sidecars for audible-output proof.

This producer is deliberately narrow. It snapshots the installed source target
and replacement music hashes before a live run, then builds a sidecar after the
run that proves those same source files are unchanged and binds that fact to a
specific clean or mute live artifact.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "winui-safe-copy-source-music-safety.v1"
SNAPSHOT_SCHEMA = "winui-safe-copy-source-music-snapshot.v1"
LIVE_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
TARGET_RELATIVE = Path("data") / "Music" / TARGET
REPLACEMENT_RELATIVE = Path("data") / "Music" / REPLACEMENT
ROLES = {"cleanBaseline", "muteControl"}
NON_CLAIMS = [
    "not audible-output proof",
    "not a BEA launch",
    "not a CDB attach",
    "not a loopback capture",
    "not source-audio correlation",
    "not gameplay parity",
    "not rebuild parity",
    "not no-noticeable-difference parity",
]


class SourceMusicSafetyError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SourceMusicSafetyError(message)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing JSON input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(payload, dict), f"JSON input must be an object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_no_symlink_or_reparse(path: Path) -> None:
    resolved = path.resolve()
    candidates = [resolved]
    candidates.extend(parent for parent in resolved.parents if parent.exists())
    for candidate in candidates:
        if candidate.is_symlink():
            raise SourceMusicSafetyError(f"Refusing symlinked source music safety path: {candidate}")
        attrs = getattr(candidate.stat(), "st_file_attributes", 0) if candidate.exists() else 0
        if attrs & 0x400:
            raise SourceMusicSafetyError(f"Refusing reparse-point source music safety path: {candidate}")


def validate_output_path(output: Path, source_root: Path) -> None:
    validate_no_symlink_or_reparse(source_root)
    validate_no_symlink_or_reparse(output.parent)
    require(not is_relative_to(output, source_root), "Source music safety sidecar output must not be written inside the source game root.")
    require(output.suffix.lower() == ".json", "Source music safety sidecar output must be a JSON file.")


def format_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def string_at(value: dict[str, Any], key: str) -> str:
    child = value.get(key)
    require(isinstance(child, str) and child, f"Missing string: {key}")
    return str(child)


def bool_at(value: dict[str, Any], key: str) -> bool:
    child = value.get(key)
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return bool(child)


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def validate_role(role: str) -> None:
    require(role in ROLES, f"Role must be one of: {', '.join(sorted(ROLES))}.")


def source_music_hashes(source_root: Path) -> dict[str, Any]:
    validate_no_symlink_or_reparse(source_root)
    target_path = source_root / TARGET_RELATIVE
    replacement_path = source_root / REPLACEMENT_RELATIVE
    require(target_path.is_file(), f"Missing source target music file: {TARGET_RELATIVE}")
    require(replacement_path.is_file(), f"Missing source replacement music file: {REPLACEMENT_RELATIVE}")
    validate_no_symlink_or_reparse(target_path)
    validate_no_symlink_or_reparse(replacement_path)
    return {
        "target": TARGET,
        "replacement": REPLACEMENT,
        "sourceTargetSha256": sha256_file(target_path),
        "sourceReplacementSha256": sha256_file(replacement_path),
        "sourceTargetByteCount": target_path.stat().st_size,
        "sourceReplacementByteCount": replacement_path.stat().st_size,
    }


def build_snapshot(*, source_root: Path) -> dict[str, Any]:
    hashes = source_music_hashes(source_root)
    require(hashes["sourceTargetByteCount"] > 0, "Source target music file is empty.")
    require(hashes["sourceReplacementByteCount"] > 0, "Source replacement music file is empty.")
    return {
        "schemaVersion": SNAPSHOT_SCHEMA,
        "generatedAtUtc": format_utc(dt.datetime.now(dt.timezone.utc)),
        "target": TARGET,
        "replacement": REPLACEMENT,
        "sourceTargetHash": hashes["sourceTargetSha256"],
        "sourceReplacementHash": hashes["sourceReplacementSha256"],
        "sourceTargetByteCount": hashes["sourceTargetByteCount"],
        "sourceReplacementByteCount": hashes["sourceReplacementByteCount"],
        "sourcePathsPublished": False,
        "claimBoundary": "Before-run source music hash snapshot only; no runtime or audible-output proof.",
    }


def validate_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SNAPSHOT_SCHEMA, "Source music snapshot schema changed.")
    require(payload.get("target") == TARGET, "Snapshot target changed.")
    require(payload.get("replacement") == REPLACEMENT, "Snapshot replacement changed.")
    require(payload.get("sourcePathsPublished") is False, "Snapshot must not publish source paths.")
    for key in ("sourceTargetHash", "sourceReplacementHash"):
        value = string_at(payload, key).lower()
        require(bool(re.fullmatch(r"[0-9a-f]{64}", value)), f"{key} must be a SHA-256 hex string.")
    for key in ("sourceTargetByteCount", "sourceReplacementByteCount"):
        value = payload.get(key)
        require(isinstance(value, int) and value > 0, f"{key} must be a positive integer.")
    return payload


def validate_live_artifact(live_path: Path, role: str) -> str:
    validate_role(role)
    live = read_json(live_path)
    require(live.get("schemaVersion") == LIVE_SCHEMA, "Live artifact schema changed.")
    source = object_at(live, "source")
    require(bool_at(source, "installedHashUnchanged"), "Live artifact does not prove installed BEA hash unchanged.")
    require(bool_at(source, "overrideHashUnchanged"), "Live artifact does not prove clean override hash unchanged.")
    save_options = object_at(source, "saveAndOptions")
    require(bool_at(save_options, "unchanged"), "Live artifact does not prove source save/options unchanged.")
    launch = object_at(live, "launch")
    launch_args = [str(item).lower() for item in launch.get("arguments", []) if isinstance(item, str)]
    require(launch_args, "Live artifact launch arguments are missing.")
    if role == "cleanBaseline":
        require("-nomusic" not in launch_args and "-nosound" not in launch_args, "Clean baseline must not disable music or sound.")
    if role == "muteControl":
        require("-nomusic" in launch_args or "-nosound" in launch_args, "Mute control must use -nomusic or -nosound.")
    baseline = object_at(live, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), "Live artifact had a preexisting BEA process.")
    require(bool_at(baseline, "noBeaAfterStop"), "Live artifact left BEA running after stop.")
    stop = object_at(live, "stop")
    require(bool_at(stop, "Success"), "Live artifact stop did not succeed.")
    require(live.get("musicReplacement") is None, "Clean/mute source safety sidecars must not be built from staged music-replacement artifacts.")
    return sha256_file(live_path)


def build_sidecar(*, live_path: Path, before_snapshot: dict[str, Any], source_root: Path, role: str) -> dict[str, Any]:
    before = validate_snapshot(before_snapshot)
    live_hash = validate_live_artifact(live_path, role)
    after = source_music_hashes(source_root)
    target_before = string_at(before, "sourceTargetHash").lower()
    replacement_before = string_at(before, "sourceReplacementHash").lower()
    target_after = str(after["sourceTargetSha256"]).lower()
    replacement_after = str(after["sourceReplacementSha256"]).lower()
    target_unchanged = target_before == target_after
    replacement_unchanged = replacement_before == replacement_after
    require(target_unchanged, "Source target music hash changed after live run.")
    require(replacement_unchanged, "Source replacement music hash changed after live run.")
    return {
        "schemaVersion": SCHEMA,
        "role": role,
        "generatedAtUtc": format_utc(dt.datetime.now(dt.timezone.utc)),
        "liveArtifactSha256": live_hash,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "sourceTargetHashBefore": target_before,
        "sourceTargetHashAfter": target_after,
        "sourceTargetHashUnchanged": True,
        "sourceReplacementHashBefore": replacement_before,
        "sourceReplacementHashAfter": replacement_after,
        "sourceReplacementHashUnchanged": True,
        "sourceTargetByteCount": after["sourceTargetByteCount"],
        "sourceReplacementByteCount": after["sourceReplacementByteCount"],
        "sourcePathsPublished": False,
        "claimBoundary": "Source music safety sidecar only; no BEA launch, CDB attach, audio capture, or audible-output proof.",
        "nonClaims": NON_CLAIMS,
    }


def build_sidecar_from_paths(
    *,
    live_path: Path,
    before_snapshot: Path,
    source_root: Path,
    output: Path,
    role: str,
) -> dict[str, Any]:
    validate_output_path(output, source_root)
    payload = build_sidecar(
        live_path=live_path,
        before_snapshot=read_json(before_snapshot),
        source_root=source_root,
        role=role,
    )
    write_json(output, payload)
    validate_artifact(payload, artifact_path=output, live_path=live_path)
    return payload


def validate_artifact(
    payload: dict[str, Any] | None = None,
    *,
    artifact_path: Path | None = None,
    live_path: Path | None = None,
) -> dict[str, Any]:
    if artifact_path is not None:
        payload = read_json(artifact_path)
    require(isinstance(payload, dict), "Source music safety artifact must be a JSON object.")
    require(payload.get("schemaVersion") == SCHEMA, "Source music safety schema changed.")
    role = string_at(payload, "role")
    validate_role(role)
    require(payload.get("target") == TARGET, "Source music safety target changed.")
    require(payload.get("replacement") == REPLACEMENT, "Source music safety replacement changed.")
    require(payload.get("sourcePathsPublished") is False, "Source music safety sidecar must not publish source paths.")
    if live_path is not None:
        require(payload.get("liveArtifactSha256") == sha256_file(live_path), "Source music safety sidecar is not bound to the live artifact.")
    else:
        value = string_at(payload, "liveArtifactSha256")
        require(bool(re.fullmatch(r"[0-9a-fA-F]{64}", value)), "liveArtifactSha256 must be a SHA-256 hex string.")
    for key in (
        "sourceTargetHashBefore",
        "sourceTargetHashAfter",
        "sourceReplacementHashBefore",
        "sourceReplacementHashAfter",
    ):
        value = string_at(payload, key)
        require(bool(re.fullmatch(r"[0-9a-fA-F]{64}", value)), f"{key} must be a SHA-256 hex string.")
    require(bool_at(payload, "sourceTargetHashUnchanged"), "Source target hash changed.")
    require(bool_at(payload, "sourceReplacementHashUnchanged"), "Source replacement hash changed.")
    require(
        payload["sourceTargetHashBefore"].lower() == payload["sourceTargetHashAfter"].lower(),
        "Source target before/after hashes differ.",
    )
    require(
        payload["sourceReplacementHashBefore"].lower() == payload["sourceReplacementHashAfter"].lower(),
        "Source replacement before/after hashes differ.",
    )
    return {
        "schemaVersion": SCHEMA,
        "role": role,
        "sourceTargetHashUnchanged": True,
        "sourceReplacementHashUnchanged": True,
        "target": TARGET,
        "replacement": REPLACEMENT,
    }


def run_self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="source-music-safety-sidecar-") as temp_dir:
        root = Path(temp_dir)
        source = root / "source"
        music = source / "data" / "Music"
        music.mkdir(parents=True, exist_ok=True)
        (music / TARGET).write_bytes(b"target-v1")
        (music / REPLACEMENT).write_bytes(b"replacement-v1")
        before = root / "before.json"
        write_json(before, build_snapshot(source_root=source))

        roles: list[str] = []
        for role, mute in (("cleanBaseline", False), ("muteControl", True)):
            live = {
                "schemaVersion": LIVE_SCHEMA,
                "source": {
                    "installedHashUnchanged": True,
                    "overrideHashUnchanged": True,
                    "saveAndOptions": {"unchanged": True},
                },
                "safeCopy": {"patchKeys": ["resolution_gate", "force_windowed"]},
                "musicReplacement": None,
                "launch": {"arguments": ["-skipfmv", "-level", "100"] + (["-nomusic"] if mute else [])},
                "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
                "stop": {"Success": True},
            }
            live_path = root / role / "live.json"
            output = root / role / "source-music-safety.json"
            write_json(live_path, live)
            payload = build_sidecar_from_paths(
                live_path=live_path,
                before_snapshot=before,
                source_root=source,
                output=output,
                role=role,
            )
            validate_artifact(payload, artifact_path=output, live_path=live_path)
            roles.append(role)

        return {
            "schemaVersion": SCHEMA,
            "rolesChecked": roles,
            "sourceTargetHashUnchanged": True,
            "sourceReplacementHashUnchanged": True,
        }


def sanitize_error_message(message: str) -> str:
    message = re.sub(r"[A-Za-z]:[\\/][^\r\n\"']+", "<path>", message)
    return message


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Battle Engine Aquila source game root.")
    parser.add_argument("--snapshot-output", type=Path, help="Write a before-run source music hash snapshot.")
    parser.add_argument("--before-snapshot", type=Path, help="Before-run source music hash snapshot JSON.")
    parser.add_argument("--live", type=Path, help="Clean or mute live runtime artifact to bind.")
    parser.add_argument("--output", type=Path, help="Output source music safety sidecar JSON.")
    parser.add_argument("--role", default="", help="cleanBaseline or muteControl.")
    parser.add_argument("--check", type=Path, help="Validate an existing source music safety sidecar.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            print(json.dumps(run_self_test(), indent=2, sort_keys=True))
            return 0
        if args.check:
            print(json.dumps(validate_artifact(artifact_path=args.check, live_path=args.live), indent=2, sort_keys=True))
            return 0
        if args.snapshot_output:
            require(args.source_root is not None, "--source-root is required with --snapshot-output.")
            payload = build_snapshot(source_root=args.source_root)
            write_json(args.snapshot_output, payload)
            print(json.dumps(validate_snapshot(payload), indent=2, sort_keys=True))
            return 0
        require(args.source_root is not None, "--source-root is required.")
        require(args.before_snapshot is not None, "--before-snapshot is required.")
        require(args.live is not None, "--live is required.")
        require(args.output is not None, "--output is required.")
        require(bool(args.role), "--role is required.")
        payload = build_sidecar_from_paths(
            live_path=args.live,
            before_snapshot=args.before_snapshot,
            source_root=args.source_root,
            output=args.output,
            role=args.role,
        )
        print(json.dumps(validate_artifact(payload, artifact_path=args.output, live_path=args.live), indent=2, sort_keys=True))
        return 0
    except SourceMusicSafetyError as exc:
        print(f"WinUI safe-copy music source safety sidecar: FAIL: {sanitize_error_message(str(exc))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
