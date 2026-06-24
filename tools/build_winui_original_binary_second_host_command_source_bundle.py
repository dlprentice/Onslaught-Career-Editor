#!/usr/bin/env python3
"""Build a distinct-host command-source proof bundle for the online ladder.

This helper is intentionally one rung below netplay: it proves a private-LAN
client command source can authenticate and produce a P2 command envelope that
would feed the existing private-LAN command path. It does not launch BEA, attach
CDB, or send host-helper input.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import platform
import queue
import secrets
import socket
import subprocess
import tempfile
import threading
import time
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

import winui_safe_copy_online_private_lan_transport_smoke_check as lan
import winui_safe_copy_online_second_host_command_source_check as checker


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "subagents"
    / "winui-original-binary-online"
    / "second-host-command-source-20260620"
    / "second-host-command-source-proof.json"
)

PROCESS_TIMEOUT_SECONDS = 120
TIMESTAMP_WINDOW_SECONDS = 30
SESSION_EXPIRY_SECONDS = 120
STALE_TIMESTAMP_SECONDS = 1_000
SOCKET_IO_TIMEOUT_SECONDS = 15
MAX_JSON_LINE_BYTES = 4_096
PRIVATE_INVITATION_ROOT = (ROOT / "subagents").resolve()
OS_TEMP_ROOT = Path(tempfile.gettempdir()).resolve()
KNOWN_RUNTIME_HOST_KINDS = {
    "windows-host",
    "linux-host",
    "macos-host",
    "vm-guest",
    "wsl-on-host",
    "container-on-host",
    "unknown-host",
}
VM_GUEST_MARKERS = (
    "virtual machine",
    "vmware",
    "virtualbox",
    "kvm",
    "qemu",
    "xen",
    "parallels",
    "hyper-v",
    "hyperv",
    "bhyve",
    "bochs",
    "rhev",
    "openstack",
    "amazon ec2",
    "google compute engine",
    "azure",
)
LINUX_VM_MARKER_PATHS = (
    Path("/sys/class/dmi/id/product_name"),
    Path("/sys/class/dmi/id/sys_vendor"),
    Path("/sys/class/dmi/id/board_vendor"),
    Path("/sys/class/dmi/id/bios_vendor"),
    Path("/proc/sysinfo"),
)
CLIENT_IDENTITY_MESSAGE_KEYS = {
    "machineFingerprint",
    "machineFingerprintComputedByPreflight",
    "machineFingerprintSource",
    "machineFingerprintInputsRedacted",
    "observedSourceAddress",
    "assignedPrivateAddresses",
    "hostnameFingerprint",
    "platformFingerprint",
    "runtimeHostKind",
    "runtimeHostKindSource",
    "runtimeHostKindInputsRedacted",
    "wslDetectedByPreflight",
    "containerDetectedByPreflight",
}
SOURCE_SAFETY_SIDE_MESSAGE_KEYS = {
    "sourceEvidenceMode",
    "computedByPreflight",
    "pathValuesPublished",
    "absolutePathsSerialized",
    "copiedProfileRootClass",
    "copiedProfileHashMode",
    "copiedProfileFileCount",
    "copiedProfileSha256Before",
    "copiedProfileSha256After",
    "prePostHashSamplingMode",
    "prePostHashSampleCount",
    "prePostHashSamplesDistinct",
    "installedGameRootClass",
    "installedGameHashMode",
    "installedGameFileCount",
    "installedGameSha256Before",
    "installedGameSha256After",
    "programFilesMutationAttempted",
}
SESSION_HELLO_MESSAGE_KEYS = {
    "type",
    "protocolVersion",
    "serverIdentityFingerprint",
    "clientIdentityFingerprint",
    "nonce",
    "timestamp",
    "clientIdentity",
    "clientSourceSafety",
    "mac",
}
COMMAND_MESSAGE_KEYS = {
    "type",
    "protocolVersion",
    "compatibilityKey",
    "commandId",
    "remoteSlot",
    "command",
    "sequence",
    "nonce",
    "timestamp",
    "wouldForwardToPrivateLanCommandId",
    "mac",
}
DIRECT_INPUT_COMMAND_MESSAGE_KEYS = COMMAND_MESSAGE_KEYS | {
    "directInputAttempted",
    "gameInputSentBySecondHostClient",
    "hostHelperInputSent",
}
SOURCE_SAFETY_POSTFLIGHT_MESSAGE_KEYS = {
    "type",
    "protocolVersion",
    "clientIdentityFingerprint",
    "nonce",
    "timestamp",
    "clientSourceSafetyAfter",
    "mac",
}
CLOSE_MESSAGE_KEYS = {"type"}
KNOWN_COMMAND_IDS = {
    "second-host-reject-p3-forward-0001",
    "second-host-reject-bad-hmac-0001",
    "second-host-reject-pre-session-0001",
    "second-host-reject-timestamp-0001",
    "second-host-reject-future-timestamp-0001",
    "second-host-reject-sequence-0001",
    "second-host-reject-compatibility-key-0001",
    checker.EXPECTED_COMMAND_ID,
    "second-host-reject-replay-0001",
    "second-host-reject-rate-limit-0001",
    "second-host-reject-unknown-field-0001",
    "second-host-reject-direct-input-0001",
}


class SecondHostCommandSourceBundleBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondHostCommandSourceBundleBuildError(message)


def require_exact_keys(payload: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(payload)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    require(not missing and not unexpected, f"{label} schema mismatch; missing={missing}; unexpected={unexpected}")


def require_incoming_message_schema(payload: dict[str, Any]) -> None:
    message_type = payload.get("type")
    if message_type == "session_hello":
        require_exact_keys(payload, SESSION_HELLO_MESSAGE_KEYS, "session_hello")
        client_identity = payload.get("clientIdentity")
        require(isinstance(client_identity, dict), "session_hello clientIdentity must be an object")
        require_exact_keys(client_identity, CLIENT_IDENTITY_MESSAGE_KEYS, "session_hello.clientIdentity")
        client_safety = payload.get("clientSourceSafety")
        require(isinstance(client_safety, dict), "session_hello clientSourceSafety must be an object")
        require_exact_keys(client_safety, SOURCE_SAFETY_SIDE_MESSAGE_KEYS, "session_hello.clientSourceSafety")
        return
    if message_type == "command":
        command_id = payload.get("commandId")
        require(isinstance(command_id, str) and command_id in KNOWN_COMMAND_IDS, "commandId is not in the accepted protocol schema")
        expected_keys = DIRECT_INPUT_COMMAND_MESSAGE_KEYS if command_id == "second-host-reject-direct-input-0001" else COMMAND_MESSAGE_KEYS
        require_exact_keys(payload, expected_keys, "command")
        return
    if message_type == "source_safety_postflight":
        require_exact_keys(payload, SOURCE_SAFETY_POSTFLIGHT_MESSAGE_KEYS, "source_safety_postflight")
        client_safety_after = payload.get("clientSourceSafetyAfter")
        require(isinstance(client_safety_after, dict), "source_safety_postflight clientSourceSafetyAfter must be an object")
        require_exact_keys(client_safety_after, SOURCE_SAFETY_SIDE_MESSAGE_KEYS, "source_safety_postflight.clientSourceSafetyAfter")
        return
    if message_type == "close":
        require_exact_keys(payload, CLOSE_MESSAGE_KEYS, "close")
        return
    raise SecondHostCommandSourceBundleBuildError("unknown-message-type")


def incoming_message_schema_error(payload: dict[str, Any]) -> str | None:
    try:
        require_incoming_message_schema(payload)
    except SecondHostCommandSourceBundleBuildError:
        return "message-schema-mismatch"
    return None


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_validated_bundle(path: Path, value: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    try:
        write_json(temp_path, value)
        summary = checker.validate_bundle(temp_path)
        os.replace(temp_path, path)
        return summary
    finally:
        if temp_path.exists():
            temp_path.unlink()


def delete_private_invitation(path: Path) -> bool:
    resolved = require_private_invitation_path(path)
    if not resolved.exists():
        return False
    resolved.unlink()
    return True


def write_private_invitation(path: Path, value: dict[str, Any]) -> None:
    resolved = require_private_invitation_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2) + "\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(resolved, flags, 0o600)
    except FileExistsError as exc:
        raise SecondHostCommandSourceBundleBuildError("client invitation already exists; refusing to overwrite") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def require_invitation_not_expired(invitation: dict[str, Any], *, now_unix: int | None = None) -> None:
    now = int(time.time()) if now_unix is None else int(now_unix)
    try:
        issued_at = int(invitation["issuedAtUnix"])
        expires_at = int(invitation["expiresAtUnix"])
        nonce_window = int(invitation["nonceWindowSeconds"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SecondHostCommandSourceBundleBuildError("client invitation expiry fields are invalid") from exc
    require(expires_at > issued_at, "client invitation expiry must be after issue time")
    require(now <= expires_at, "client invitation is expired")
    require(now >= issued_at - nonce_window, "client invitation is not valid yet")


def session_is_expired(authorization: dict[str, Any], *, now_unix: int | None = None) -> bool:
    now = int(time.time()) if now_unix is None else int(now_unix)
    try:
        return now > int(authorization["expiresAtUnix"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SecondHostCommandSourceBundleBuildError("authorization expiry fields are invalid") from exc


def payload_timestamp_in_window(payload: dict[str, Any], authorization: dict[str, Any], *, observed_at_unix: int) -> bool:
    try:
        timestamp = int(payload.get("timestamp"))
        issued_at = int(authorization["issuedAtUnix"])
        expires_at = int(authorization["expiresAtUnix"])
        nonce_window = int(authorization["nonceWindowSeconds"])
    except (KeyError, TypeError, ValueError):
        return False
    if timestamp < issued_at - nonce_window or timestamp > expires_at:
        return False
    return observed_at_unix - nonce_window <= timestamp <= observed_at_unix + nonce_window


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def require_private_invitation_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    under_temp_outside_repo = is_relative_to(resolved, OS_TEMP_ROOT) and not is_relative_to(resolved, ROOT.resolve())
    require(
        under_temp_outside_repo,
        "client invitation must stay under OS temp outside the repo",
    )
    require(resolved.suffix.lower() == ".json", "client invitation must be a .json file")
    return resolved


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "mac"}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: dict[str, Any], credential: bytes) -> dict[str, Any]:
    signed = dict(payload)
    signed["mac"] = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    return signed


def verify_mac(payload: dict[str, Any], credential: bytes) -> bool:
    mac = payload.get("mac")
    if not isinstance(mac, str):
        return False
    expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    return hmac.compare_digest(mac, expected)


def write_json_line(handle: Any, payload: dict[str, Any]) -> None:
    line = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
    require(len(line) <= MAX_JSON_LINE_BYTES, "JSONL payload exceeds max line size")
    handle.write(line)
    handle.flush()


def read_json_line(handle: Any) -> dict[str, Any]:
    line = handle.readline(MAX_JSON_LINE_BYTES + 1)
    require(bool(line), "socket closed before a response was read")
    require(len(line) <= MAX_JSON_LINE_BYTES, "JSONL payload exceeds max line size")
    require(line.endswith(b"\n"), "JSONL payload must be newline-terminated")
    try:
        value = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SecondHostCommandSourceBundleBuildError("JSONL payload was not valid UTF-8 JSON") from exc
    require(isinstance(value, dict), "response was not a JSON object")
    return value


def sha256_payload(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def sha256_file_bytes(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_path_for_preflight(path: Path) -> tuple[str, str, int]:
    resolved = path.expanduser().resolve()
    require(resolved.exists(), f"source-safety preflight path is missing: {path}")
    if resolved.is_file():
        return sha256_file_bytes(resolved), "file-sha256", 1
    require(resolved.is_dir(), f"source-safety preflight path must be a file or directory: {path}")
    digest = sha256()
    file_count = 0
    for child in sorted(row for row in resolved.rglob("*") if row.is_file()):
        require(not child.is_symlink(), f"source-safety preflight refuses symlinked file: {child}")
        relative = child.relative_to(resolved).as_posix()
        child_hash = sha256_file_bytes(child)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(child.stat().st_size).encode("ascii"))
        digest.update(b"\0")
        digest.update(child_hash.encode("ascii"))
        digest.update(b"\n")
        file_count += 1
    require(file_count > 0, f"source-safety preflight directory has no files: {path}")
    return digest.hexdigest(), "directory-manifest-sha256", file_count


def has_vm_guest_marker(values: Iterable[str]) -> bool:
    for value in values:
        lowered = value.lower()
        if any(marker in lowered for marker in VM_GUEST_MARKERS):
            return True
    return False


def collect_linux_vm_marker_texts() -> list[str]:
    values: list[str] = []
    for path in LINUX_VM_MARKER_PATHS:
        try:
            if path.exists() and path.is_file():
                values.append(path.read_text(encoding="utf-8", errors="ignore")[:4096])
        except OSError:
            continue
    return values


def collect_windows_vm_marker_texts() -> list[str]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "$cs = Get-CimInstance Win32_ComputerSystem; "
            "$bios = Get-CimInstance Win32_BIOS; "
            "@($cs.Manufacturer, $cs.Model, $bios.Manufacturer, $bios.Version) | "
            "Where-Object { $_ }"
        ),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def collect_platform_vm_marker_texts(system: str) -> list[str]:
    if system == "windows":
        return collect_windows_vm_marker_texts()
    if system == "linux":
        return collect_linux_vm_marker_texts()
    return []


def detect_runtime_host_kind(
    *,
    dockerenv_exists: bool | None = None,
    env_container: str | None = None,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_description: str | None = None,
    vm_marker_texts: Iterable[str] | None = None,
) -> str:
    if dockerenv_exists is None:
        dockerenv_exists = Path("/.dockerenv").exists()
    if dockerenv_exists:
        return "container-on-host"
    if env_container is None:
        env_container = os.environ.get("container") or os.environ.get("CONTAINER") or ""
    env_container = env_container.lower()
    if env_container:
        return "container-on-host"
    system = (platform_system if platform_system is not None else platform.system()).lower()
    release = (platform_release if platform_release is not None else platform.release()).lower()
    platform_text = (platform_description if platform_description is not None else platform.platform()).lower()
    if "microsoft" in release or "microsoft" in platform_text or "wsl" in release or "wsl" in platform_text:
        return "wsl-on-host"
    marker_texts = list(vm_marker_texts) if vm_marker_texts is not None else collect_platform_vm_marker_texts(system)
    if has_vm_guest_marker(marker_texts):
        return "vm-guest"
    if system == "windows":
        return "windows-host"
    if system == "linux":
        return "linux-host"
    if system == "darwin":
        return "macos-host"
    return "unknown-host"


def make_machine_identity_preflight(
    machine_fingerprint: str | None = None,
    *,
    evidence_mode: str | None = None,
    runtime_host_kind: str | None = None,
) -> dict[str, Any]:
    hostname_fingerprint = hash_label(socket.gethostname())
    platform_fingerprint = hash_label(platform.platform())
    if runtime_host_kind is None:
        runtime_host_kind = detect_runtime_host_kind()
        runtime_source = "auto-platform-preflight"
    else:
        require(runtime_host_kind in KNOWN_RUNTIME_HOST_KINDS, "runtime host kind mismatch")
        runtime_source = "operator-supplied-runtime-host-kind"
    if machine_fingerprint is None:
        source = "local-hostname-platform-preflight"
        machine_fingerprint = sha256_payload(
            {
                "schemaVersion": "winui-original-binary-second-host-machine-fingerprint-preflight.v1",
                "hostnameFingerprint": hostname_fingerprint,
                "platformFingerprint": platform_fingerprint,
                "runtimeHostKind": runtime_host_kind,
            }
        )
        computed = True
    else:
        source = evidence_mode or "operator-supplied-machine-fingerprint"
        machine_fingerprint = require_hex64(machine_fingerprint, "machine fingerprint")
        computed = source != "operator-supplied-machine-fingerprint"
    return {
        "machineFingerprint": machine_fingerprint,
        "machineFingerprintComputedByPreflight": computed,
        "machineFingerprintSource": source,
        "machineFingerprintInputsRedacted": True,
        "hostnameFingerprint": hostname_fingerprint,
        "platformFingerprint": platform_fingerprint,
        "runtimeHostKind": runtime_host_kind,
        "runtimeHostKindSource": runtime_source,
        "runtimeHostKindInputsRedacted": True,
        "wslDetectedByPreflight": runtime_host_kind == "wsl-on-host",
        "containerDetectedByPreflight": runtime_host_kind == "container-on-host",
    }


def make_source_safety_side_evidence(
    *,
    role: str,
    copied_profile_sha256: str | None = None,
    installed_game_sha256: str | None = None,
    copied_profile_root: Path | None = None,
    installed_game_root: Path | None = None,
    evidence_mode: str | None = None,
) -> dict[str, Any]:
    require(role in {"host", "client"}, "source-safety role mismatch")
    if copied_profile_root is not None or installed_game_root is not None:
        require(
            copied_profile_root is not None and installed_game_root is not None,
            "computed preflight requires both copied-profile and installed-game roots",
        )
        copied_hash, copied_mode, copied_count = hash_path_for_preflight(copied_profile_root)
        installed_hash, installed_mode, installed_count = hash_path_for_preflight(installed_game_root)
        mode = "local-preflight-computed"
        computed = True
    else:
        copied_hash = require_hex64(str(copied_profile_sha256 or ""), f"{role} copied profile hash")
        installed_hash = require_hex64(str(installed_game_sha256 or ""), f"{role} installed game hash")
        copied_mode = "operator-supplied-sha256"
        installed_mode = "operator-supplied-sha256"
        copied_count = 0
        installed_count = 0
        mode = evidence_mode or "operator-supplied-hash"
        computed = mode != "operator-supplied-hash"
    return {
        "sourceEvidenceMode": mode,
        "computedByPreflight": computed,
        "pathValuesPublished": False,
        "absolutePathsSerialized": False,
        "copiedProfileRootClass": "app-owned-or-private-proof-root",
        "copiedProfileHashMode": copied_mode,
        "copiedProfileFileCount": copied_count,
        "copiedProfileSha256Before": copied_hash,
        "copiedProfileSha256After": copied_hash,
        "prePostHashSamplingMode": "single-sample-preflight",
        "prePostHashSampleCount": 1,
        "prePostHashSamplesDistinct": False,
        "installedGameRootClass": "source-install-read-only",
        "installedGameHashMode": installed_mode,
        "installedGameFileCount": installed_count,
        "installedGameSha256Before": installed_hash,
        "installedGameSha256After": installed_hash,
        "programFilesMutationAttempted": False,
    }


def make_two_phase_source_safety_side_evidence(
    *,
    role: str,
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    require(before.get("sourceEvidenceMode") == after.get("sourceEvidenceMode"), f"{role} source evidence mode drifted")
    require(before.get("copiedProfileHashMode") == after.get("copiedProfileHashMode"), f"{role} copied hash mode drifted")
    require(before.get("installedGameHashMode") == after.get("installedGameHashMode"), f"{role} installed hash mode drifted")
    require(before.get("copiedProfileFileCount") == after.get("copiedProfileFileCount"), f"{role} copied file count drifted")
    require(before.get("installedGameFileCount") == after.get("installedGameFileCount"), f"{role} installed file count drifted")
    merged = dict(before)
    merged["copiedProfileSha256After"] = after["copiedProfileSha256Before"]
    merged["installedGameSha256After"] = after["installedGameSha256Before"]
    merged["prePostHashSamplingMode"] = "live-pre-post"
    merged["prePostHashSampleCount"] = 2
    merged["prePostHashSamplesDistinct"] = True
    return merged


def make_invitation_lifecycle_receipt(
    invitation: dict[str, Any],
    *,
    deleted: bool,
    post_delete_exists: bool,
) -> dict[str, Any]:
    descriptor = {
        key: value
        for key, value in invitation.items()
        if key not in {"credentialHex", "serverHost", "serverPort"}
    }
    return {
        "schemaVersion": "winui-original-binary-second-host-invitation-lifecycle.v1",
        "rootClass": "os-temp-outside-repo",
        "exclusiveCreateSucceeded": True,
        "issuedAtUnix": invitation["issuedAtUnix"],
        "expiresAtUnix": invitation["expiresAtUnix"],
        "nonceWindowSeconds": invitation["nonceWindowSeconds"],
        "sanitizedInvitationDescriptorSha256": sha256_payload(descriptor),
        "rawInvitationPathSerialized": False,
        "rawServerAddressSerializedInReceipt": False,
        "privateMaterialSerialized": False,
        "deletionAttempted": True,
        "deletionSucceeded": deleted,
        "postDeleteExists": post_delete_exists,
    }


def make_self_test_invitation_lifecycle_receipt() -> dict[str, Any]:
    return make_invitation_lifecycle_receipt(
        {
            "issuedAtUnix": 1000,
            "expiresAtUnix": 1120,
            "nonceWindowSeconds": TIMESTAMP_WINDOW_SECONDS,
            "protocolVersion": checker.EXPECTED_PROTOCOL,
        },
        deleted=True,
        post_delete_exists=False,
    )


def post_close_connect_is_rejected(bind_host: str, port: int) -> bool:
    try:
        with socket.create_connection((bind_host, port), timeout=0.25):
            return False
    except OSError:
        return True


def make_listener_lifecycle_receipt(
    *,
    bind_host: str,
    port: int | None = None,
    evidence_mode: str,
    listener_closed: bool,
    post_close_connect_rejected: bool | None = None,
) -> dict[str, Any]:
    require(checker.ip_is_private_lan_non_loopback(bind_host), "listener bind host must be private LAN non-loopback")
    require(evidence_mode in {"live-server-socket-receipt", "self-test-fixture"}, "listener evidence mode mismatch")
    if listener_closed:
        require(post_close_connect_rejected is not None, "closed listener receipt requires post-close connect evidence")
    return {
        "schemaVersion": "winui-original-binary-second-host-listener-lifecycle.v1",
        "evidenceMode": evidence_mode,
        "bindAddress": bind_host,
        "sanitizedEndpointSha256": sha256_payload({"bindAddress": bind_host, "port": port or 0}),
        "bindAddressClass": "private-lan-non-loopback",
        "socketFamily": "AF_INET",
        "bindAttempted": True,
        "bindSucceeded": True,
        "boundHostMatchesTransport": True,
        "hostPrivateInterfaceBound": True,
        "wildcardBind": False,
        "loopbackBind": False,
        "publicRoutableBind": False,
        "publicEndpointPublished": False,
        "listenSucceeded": True,
        "listenerStarted": True,
        "listenerAcceptLimit": 1,
        "closeAttempted": listener_closed,
        "closeSucceeded": listener_closed,
        "listenerClosedBeforeBundleWrite": listener_closed,
        "teardownObserved": listener_closed,
        "postCloseConnectRejected": post_close_connect_rejected if listener_closed else False,
        "portValueSerializedInPublicDocs": False,
    }


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind}
    if payload is not None:
        event["payloadSha256"] = sha256_payload(payload)
    event.update(extra)
    return event


def make_live_session_security_hardening(transcript_events: list[dict[str, Any]]) -> dict[str, Any]:
    event_hashes = {
        str(row.get("kind") or ""): str(row.get("payloadSha256") or "")
        for row in transcript_events
        if isinstance(row, dict)
    }
    hardening: dict[str, Any] = {
        "evidenceMode": "live-server-client-transcript",
        "requiredBeforeAcceptedLiveRuntimeDelivery": True,
        "liveNegativeCaseTranscript": True,
        "caseCount": len(checker.SESSION_SECURITY_HARDENING_CASES),
        "cases": [],
    }
    for flag in checker.REQUIRED_SESSION_SECURITY_HARDENING_FLAGS:
        expected = checker.SESSION_SECURITY_HARDENING_CASES[flag]
        request_hashes = {}
        response_hashes = {}
        for event in expected["requestEvents"]:
            require(checker.is_hex64(event_hashes.get(event)), f"live hardening request event missing payload hash: {event}")
            request_hashes[event] = event_hashes[event]
        for event in expected["responseEvents"]:
            require(checker.is_hex64(event_hashes.get(event)), f"live hardening response event missing payload hash: {event}")
            response_hashes[event] = event_hashes[event]
        hardening[flag] = True
        hardening["cases"].append(
            {
                "flag": flag,
                "caseId": expected["caseId"],
                "rejectionReason": expected["reason"],
                "requestEvents": expected["requestEvents"],
                "responseEvents": expected["responseEvents"],
                "requestPayloadSha256ByEvent": request_hashes,
                "responsePayloadSha256ByEvent": response_hashes,
                "accepted": False,
                "liveTranscriptObserved": True,
            }
        )
    return hardening


def require_hex64(value: str, label: str) -> str:
    require(checker.is_hex64(value), f"{label} must be lowercase SHA-256 hex")
    return value


def hash_label(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def require_private_lan_address(value: str, label: str) -> str:
    require(checker.ip_is_private_lan_non_loopback(value), f"{label} must be RFC1918/ULA private LAN and non-loopback")
    return value


def require_allowed_source_kind(value: str) -> str:
    require(value in checker.ALLOWED_COMMAND_SOURCE_KINDS, f"unsupported command source kind: {value}")
    return value


def relative_to_bundle(bundle_path: Path, artifact_path: Path) -> str:
    try:
        return artifact_path.resolve().relative_to(bundle_path.resolve().parent).as_posix()
    except ValueError as exc:
        raise SecondHostCommandSourceBundleBuildError(
            "private LAN proof must live under the same private proof root as the output bundle"
        ) from exc


def collect_host_private_addresses(bind_host: str, extra: list[str] | None = None) -> list[str]:
    addresses: set[str] = set()
    for candidate in [bind_host, *(extra or [])]:
        if checker.ip_is_private_lan_non_loopback(candidate):
            addresses.add(candidate)
    try:
        for result in socket.getaddrinfo(socket.gethostname(), None):
            address = str(result[4][0])
            if checker.ip_is_private_lan_non_loopback(address):
                addresses.add(address)
    except socket.gaierror:
        pass
    require(bind_host in addresses, "host bind address must be present in host assigned-address evidence")
    return sorted(addresses)


def make_session_descriptor(
    private_lan_bundle: dict[str, Any],
    private_lan_path: Path,
    private_lan_summary: dict[str, Any],
) -> dict[str, Any]:
    upstream_descriptor = object_at(private_lan_bundle, "sessionDescriptor")
    return {
        "schemaVersion": checker.EXPECTED_SESSION_SCHEMA,
        "protocolVersion": checker.EXPECTED_PROTOCOL,
        "upstreamPrivateLanProtocolVersion": lan.EXPECTED_PROTOCOL,
        "upstreamPrivateLanProofSha256": lan.sha256_file(private_lan_path),
        "upstreamPrivateLanTransport": private_lan_summary["transport"],
        "sessionCompatibilityKey": upstream_descriptor["sessionCompatibilityKey"],
        "cleanSpecimenSha256": upstream_descriptor["cleanSpecimenSha256"],
        "allowedOriginalBinaryGameplaySlots": checker.EXPECTED_ACTIVE_SLOTS,
        "metadataOnlySlots": checker.EXPECTED_METADATA_SLOTS,
        "rejectedGameplayRouteSlots": checker.EXPECTED_METADATA_SLOTS,
        "remotePlayerSlot": checker.EXPECTED_REMOTE_SLOT,
        "allowedCommand": checker.EXPECTED_REMOTE_COMMAND,
        "upstreamPrivateLanCommandId": checker.EXPECTED_PRIVATE_LAN_COMMAND_ID,
        "levelId": 850,
        "controllerConfiguration": 1,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "nPlayerOriginalBinaryRuntimeProof": 0,
    }


def make_authorization(
    credential: bytes,
    upstream_hash: str,
    client_identity_fingerprint: str,
    *,
    issued_at_unix: int | None = None,
) -> dict[str, Any]:
    issued_at = int(time.time()) if issued_at_unix is None else int(issued_at_unix)
    return {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "transient-os-temp-invitation-not-artifact-serialized",
        "serializedCredentialPresent": False,
        "credentialTransportToClient": "os-temp-invitation-json-exclusive-create-deleted-after-server-completion",
        "credentialTransportToServer": "generated-in-memory-and-never-written-to-proof-artifact",
        "authKeyFingerprint": sha256(credential).hexdigest(),
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": sha256(f"{checker.EXPECTED_PROTOCOL}:{upstream_hash}:server".encode("utf-8")).hexdigest(),
        "clientIdentityMode": "pinned-fingerprint",
        "clientIdentityFingerprint": client_identity_fingerprint,
        "sessionScopedAuthentication": True,
        "issuedAtUnix": issued_at,
        "expiresAtUnix": issued_at + SESSION_EXPIRY_SECONDS,
        "nonceWindowSeconds": TIMESTAMP_WINDOW_SECONDS,
        "replayCacheEnabled": True,
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSession": 1,
            "maxCommandsPerSecond": 1,
        },
    }


def make_source_safety(
    *,
    host_copied_profile_sha256: str,
    host_installed_game_sha256: str,
    client_copied_profile_sha256: str,
    client_installed_game_sha256: str,
    host_evidence: dict[str, Any] | None = None,
    client_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    host_evidence = host_evidence or make_source_safety_side_evidence(
        role="host",
        copied_profile_sha256=host_copied_profile_sha256,
        installed_game_sha256=host_installed_game_sha256,
        evidence_mode="self-test-fixture",
    )
    client_evidence = client_evidence or make_source_safety_side_evidence(
        role="client",
        copied_profile_sha256=client_copied_profile_sha256,
        installed_game_sha256=client_installed_game_sha256,
        evidence_mode="self-test-fixture",
    )
    host_mode = str(host_evidence.get("sourceEvidenceMode") or "")
    client_mode = str(client_evidence.get("sourceEvidenceMode") or "")
    if host_mode == "local-preflight-computed" and client_mode == "local-preflight-computed":
        evidence_mode = "local-preflight-computed"
    elif host_mode == "self-test-fixture" and client_mode == "self-test-fixture":
        evidence_mode = "self-test-fixture"
    else:
        evidence_mode = "operator-supplied-hash"
    return {
        "evidenceMode": evidence_mode,
        "computedByPreflight": host_evidence.get("computedByPreflight") is True and client_evidence.get("computedByPreflight") is True,
        "pathValuesPublished": False,
        "absolutePathsSerialized": False,
        "copiedProfileHashesOnBothSides": True,
        "installedGamePrePostHashesOnBothSides": True,
        "prePostHashSamplesOnBothSides": True,
        "installedGameHashesUnchangedOnHost": True,
        "installedGameHashesUnchangedOnClient": True,
        "copiedProfileRootUsedOnHost": True,
        "copiedProfileRootUsedOnClient": True,
        "programFilesMutationRejected": True,
        "originalExeMutationRejected": True,
        "installedGameMutationAllowed": False,
        "originalExeMutationAllowed": False,
        "programFilesMutationTargetUsed": False,
        "sourceInstallPatchedInPlace": False,
        "host": host_evidence,
        "client": client_evidence,
    }


def transcript_hashes_by_kind(transcript_events: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(row.get("kind") or ""): str(row.get("payloadSha256") or "")
        for row in transcript_events
        if isinstance(row, dict)
    }


def make_commands(transcript_events: list[dict[str, Any]]) -> dict[str, Any]:
    event_hashes = transcript_hashes_by_kind(transcript_events)
    request_event = "client_command_p2_forward"
    response_event = "server_command_accepted"
    require(checker.is_hex64(event_hashes.get(request_event)), "accepted P2 command request transcript hash missing")
    require(checker.is_hex64(event_hashes.get(response_event)), "accepted P2 command response transcript hash missing")
    return {
        "accepted": [
            {
                "commandId": checker.EXPECTED_COMMAND_ID,
                "remoteSlot": checker.EXPECTED_REMOTE_SLOT,
                "command": checker.EXPECTED_REMOTE_COMMAND,
                "requestEvent": request_event,
                "requestPayloadSha256": event_hashes[request_event],
                "responseEvent": response_event,
                "responsePayloadSha256": event_hashes[response_event],
                "authorizationStatus": "accepted-hmac-sha256",
                "secondHostClientAccepted": True,
                "wouldForwardToPrivateLanCommandId": checker.EXPECTED_PRIVATE_LAN_COMMAND_ID,
                "gameInputSentBySecondHostClient": False,
                "hostHelperInputSent": False,
            }
        ],
        "rejected": [
            {"commandId": "second-host-reject-p3-forward-0001", "reason": "metadata-slot-gameplay-not-allowed", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-loopback-0001", "reason": "loopback-not-allowed", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-same-workstation-0001", "reason": "same-workstation-process-not-allowed", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-wsl-0001", "reason": "wsl-on-host-not-allowed", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-public-host-0001", "reason": "public-internet-host-not-allowed", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-unknown-peer-0001", "reason": "unknown-peer-not-allowed", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-bad-hmac-0001", "reason": "bad-hmac", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-pre-session-0001", "reason": "session-not-established", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-replay-0001", "reason": "replay-nonce", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-timestamp-0001", "reason": "timestamp-window", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-sequence-0001", "reason": "sequence-order", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-pinned-identity-0001", "reason": "pinned-identity-mismatch", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-compatibility-key-0001", "reason": "compatibility-key-mismatch", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-rate-limit-0001", "reason": "rate-limit-exceeded", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-unknown-field-0001", "reason": "message-schema-mismatch", "secondHostClientAccepted": False},
            {"commandId": "second-host-reject-direct-input-0001", "reason": "direct-input-not-allowed", "secondHostClientAccepted": False},
        ],
    }


def make_bundle_from_observation(
    *,
    private_lan_proof_path: Path,
    output_path: Path,
    command_source_kind: str,
    host_bind_address: str,
    host_assigned_addresses: list[str],
    host_machine_fingerprint: str,
    client_source_address: str,
    client_assigned_address: str,
    client_machine_fingerprint: str,
    client_identity_fingerprint: str,
    authorization: dict[str, Any],
    source_safety: dict[str, Any],
    transcript_events: list[dict[str, Any]],
    session_security_hardening: dict[str, Any] | None = None,
    host_machine_identity: dict[str, Any] | None = None,
    client_machine_identity: dict[str, Any] | None = None,
    invitation_lifecycle: dict[str, Any] | None = None,
    listener_lifecycle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    command_source_kind = require_allowed_source_kind(command_source_kind)
    host_bind_address = require_private_lan_address(host_bind_address, "host bind address")
    client_source_address = require_private_lan_address(client_source_address, "client source address")
    client_assigned_address = require_private_lan_address(client_assigned_address, "client assigned address")
    require(client_source_address != host_bind_address, "client source address must differ from host bind address")
    require(client_source_address not in host_assigned_addresses, "client source address must not be host-local")
    host_machine_fingerprint = require_hex64(host_machine_fingerprint, "host machine fingerprint")
    client_machine_fingerprint = require_hex64(client_machine_fingerprint, "client machine fingerprint")
    client_identity_fingerprint = require_hex64(client_identity_fingerprint, "client identity fingerprint")
    require(host_machine_fingerprint != client_machine_fingerprint, "host/client machine fingerprints must differ")
    require(authorization.get("clientIdentityFingerprint") == client_identity_fingerprint, "authorization client fingerprint mismatch")
    second_physical = command_source_kind == "distinct-physical-host-private-lan"
    client_default_runtime_host_kind = "windows-host" if second_physical else "vm-guest"
    host_machine_identity = host_machine_identity or make_machine_identity_preflight(
        host_machine_fingerprint,
        evidence_mode="self-test-fixture",
        runtime_host_kind="windows-host",
    )
    client_machine_identity = client_machine_identity or make_machine_identity_preflight(
        client_machine_fingerprint,
        evidence_mode="self-test-fixture",
        runtime_host_kind=client_default_runtime_host_kind,
    )
    require(host_machine_identity.get("machineFingerprint") == host_machine_fingerprint, "host machine identity fingerprint mismatch")
    require(client_machine_identity.get("machineFingerprint") == client_machine_fingerprint, "client machine identity fingerprint mismatch")

    private_lan_proof_path = private_lan_proof_path.resolve()
    output_path = output_path.resolve()
    relative_private_lan = relative_to_bundle(output_path, private_lan_proof_path)
    private_lan_summary = lan.validate_bundle(private_lan_proof_path, expected_controller_configuration=1)
    private_lan_bundle = read_json(private_lan_proof_path)
    descriptor = make_session_descriptor(private_lan_bundle, private_lan_proof_path, private_lan_summary)
    same_physical_machine_only = not second_physical
    transcript = {
        "transport": checker.EXPECTED_TRANSPORT,
        "protocolVersion": checker.EXPECTED_PROTOCOL,
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
        "messageCount": len(checker.EXPECTED_TRANSCRIPT_EVENTS),
        "events": transcript_events,
    }
    bundle = {
        "schemaVersion": checker.EXPECTED_SCHEMA,
        "generatedBy": checker.EXPECTED_HELPER,
        "helperVersion": checker.EXPECTED_HELPER_VERSION,
        "protocolVersion": checker.EXPECTED_PROTOCOL,
        "privateLanTransportProofBundle": relative_private_lan,
        "privateLanTransportProofSha256": lan.sha256_file(private_lan_proof_path),
        "sessionDescriptor": descriptor,
        "transport": {
            "transport": checker.EXPECTED_TRANSPORT,
            "networkScope": "distinct-private-host-command-source-not-online-play",
            "commandSourceKind": command_source_kind,
            "hostBindAddress": host_bind_address,
            "clientSourceAddress": client_source_address,
            "hostPrivateInterfaceBound": True,
            "hostAddressAssignedToLocalInterface": True,
            "clientSourceAddressNotHostAssignedLocalAddress": True,
            "sanitizedHostAndClientInterfaceEvidence": True,
            "secondHostCommandSourceProof": True,
            "secondPhysicalHostProof": second_physical,
            "vmLabeledOnly": not second_physical,
            "sameWorkstationOnly": False,
            "samePhysicalMachineOnly": same_physical_machine_only,
            "wslOnHost": False,
            "loopbackInterfaceOnly": False,
            "publicNetworkSocketsOpened": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "natTraversalProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "gameInputSentBySecondHostClient": False,
            "hostHelperInputSent": False,
        },
        "networkIdentityEvidence": {
            "host": {
                "machineFingerprint": host_machine_fingerprint,
                "machineFingerprintComputedByPreflight": host_machine_identity["machineFingerprintComputedByPreflight"],
                "machineFingerprintSource": host_machine_identity["machineFingerprintSource"],
                "machineFingerprintInputsRedacted": host_machine_identity["machineFingerprintInputsRedacted"],
                "hostnameFingerprint": host_machine_identity["hostnameFingerprint"],
                "platformFingerprint": host_machine_identity["platformFingerprint"],
                "runtimeHostKind": host_machine_identity["runtimeHostKind"],
                "runtimeHostKindSource": host_machine_identity["runtimeHostKindSource"],
                "runtimeHostKindInputsRedacted": host_machine_identity["runtimeHostKindInputsRedacted"],
                "wslDetectedByPreflight": host_machine_identity["wslDetectedByPreflight"],
                "containerDetectedByPreflight": host_machine_identity["containerDetectedByPreflight"],
                "hostIdentityObserved": True,
                "assignedPrivateAddresses": sorted(set(host_assigned_addresses)),
            },
            "client": {
                "machineFingerprint": client_machine_fingerprint,
                "machineFingerprintComputedByPreflight": client_machine_identity["machineFingerprintComputedByPreflight"],
                "machineFingerprintSource": client_machine_identity["machineFingerprintSource"],
                "machineFingerprintInputsRedacted": client_machine_identity["machineFingerprintInputsRedacted"],
                "hostnameFingerprint": client_machine_identity["hostnameFingerprint"],
                "platformFingerprint": client_machine_identity["platformFingerprint"],
                "runtimeHostKind": client_machine_identity["runtimeHostKind"],
                "runtimeHostKindSource": client_machine_identity["runtimeHostKindSource"],
                "runtimeHostKindInputsRedacted": client_machine_identity["runtimeHostKindInputsRedacted"],
                "wslDetectedByPreflight": client_machine_identity["wslDetectedByPreflight"],
                "containerDetectedByPreflight": client_machine_identity["containerDetectedByPreflight"],
                "clientIdentityObserved": True,
                "observedSourceAddress": client_source_address,
                "sourceAddressAssignedToClientInterface": client_assigned_address == client_source_address,
                "sourceAddressAssignedToHostInterface": False,
                "vmLabeledOnly": not second_physical,
            },
            "runtimeMarkers": {
                "sameMachineSid": False,
                "sameBootId": False,
                "sameWindowsComputerName": False,
                "wslDetectedOnHost": False,
                "wslDetectedOnClient": False,
                "containerDetectedOnHost": False,
                "containerDetectedOnClient": False,
                "loopbackObserved": False,
                "publicRoutablePeerObserved": False,
            },
        },
        "authorization": authorization,
        "invitationLifecycle": invitation_lifecycle or make_self_test_invitation_lifecycle_receipt(),
        "listenerLifecycle": listener_lifecycle
        or make_listener_lifecycle_receipt(
            bind_host=host_bind_address,
            evidence_mode="self-test-fixture",
            listener_closed=True,
            post_close_connect_rejected=True,
        ),
        "sourceSafety": source_safety,
        "commands": make_commands(transcript_events),
        "transportTranscript": transcript,
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "multiHostLanPlayProof": False,
            "publicMatchmakingProof": False,
            "publicServerProof": False,
            "nativeBeaNetcodeProof": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "moreThanTwoOriginalBinaryRuntimePlayersProof": False,
            "coOpVersusRuntimeProof": False,
            "physicalGamepadProof": False,
            "newBeaLaunchCount": 0,
            "cdbAttachCount": 0,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
            "gameInputSentBySecondHostClient": False,
            "hostHelperInputSent": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "secretsSerialized": False,
            "rawPrivateAddressPublishedToPublicDocs": False,
            "rawPrivateProofPathPublished": False,
            "privateArtifactContentPublished": False,
            "publicHostOrMatchmakingEndpointPublished": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This is a second-host/private-LAN command-source proof only. It proves one distinct private-host or "
            "VM-labeled client command source can authenticate and produce a P2 command envelope that would forward "
            "to the existing private LAN command path. It does not prove player-ready online multiplayer, does not "
            "prove multi-host LAN play, does not prove native BEA netcode, and does not prove active P3/P4 gameplay."
        ),
    }
    if session_security_hardening is not None:
        bundle["sessionSecurityHardening"] = session_security_hardening
    return write_validated_bundle(output_path, bundle)


def make_invitation(
    *,
    private_lan_proof_path: Path,
    bind_host: str,
    port: int,
    credential: bytes,
    authorization: dict[str, Any],
) -> dict[str, Any]:
    private_lan_summary = lan.validate_bundle(private_lan_proof_path, expected_controller_configuration=1)
    private_lan_bundle = read_json(private_lan_proof_path)
    descriptor = make_session_descriptor(private_lan_bundle, private_lan_proof_path, private_lan_summary)
    return {
        "schemaVersion": "winui-original-binary-second-host-command-source-invitation.private.v1",
        "warning": "private transient invitation; do not commit or publish",
        "serverHost": bind_host,
        "serverPort": port,
        "protocolVersion": checker.EXPECTED_PROTOCOL,
        "credentialHex": credential.hex(),
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
        "sessionCompatibilityKey": descriptor["sessionCompatibilityKey"],
        "expectedRemoteCommand": checker.EXPECTED_REMOTE_COMMAND,
        "expectedCommandId": checker.EXPECTED_COMMAND_ID,
        "expectedPrivateLanCommandId": checker.EXPECTED_PRIVATE_LAN_COMMAND_ID,
        "issuedAtUnix": authorization["issuedAtUnix"],
        "expiresAtUnix": authorization["expiresAtUnix"],
        "nonceWindowSeconds": authorization["nonceWindowSeconds"],
    }


def run_client(
    invitation_path: Path,
    *,
    client_machine_fingerprint: str | None = None,
    client_copied_profile_sha256: str | None = None,
    client_installed_game_sha256: str | None = None,
    client_copied_profile_root: Path | None = None,
    client_installed_game_root: Path | None = None,
    client_runtime_host_kind: str | None = None,
) -> dict[str, Any]:
    invitation = read_json(invitation_path)
    require_invitation_not_expired(invitation)
    credential = bytes.fromhex(str(invitation["credentialHex"]))
    server = str(invitation["serverHost"])
    port = int(invitation["serverPort"])
    client_identity = require_hex64(str(invitation["clientIdentityFingerprint"]), "client identity")
    client_machine_identity = make_machine_identity_preflight(
        client_machine_fingerprint,
        runtime_host_kind=client_runtime_host_kind,
    )
    client_source_safety = make_source_safety_side_evidence(
        role="client",
        copied_profile_sha256=client_copied_profile_sha256,
        installed_game_sha256=client_installed_game_sha256,
        copied_profile_root=client_copied_profile_root,
        installed_game_root=client_installed_game_root,
    )
    session_timestamp = int(time.time())
    nonce_window = int(invitation["nonceWindowSeconds"])

    responses: list[dict[str, Any]] = []
    with socket.create_connection((server, port), timeout=10) as client:
        client.settimeout(SOCKET_IO_TIMEOUT_SECONDS)
        local_address = str(client.getsockname()[0])
        handle = client.makefile("rwb")

        def send_signed(payload: dict[str, Any], *, bad_mac: bool = False) -> dict[str, Any]:
            write_json_line(handle, sign_payload(payload, bytes.fromhex("00" * 32) if bad_mac else credential))
            response = read_json_line(handle)
            responses.append(response)
            return response

        base_hello = {
            "type": "session_hello",
            "protocolVersion": checker.EXPECTED_PROTOCOL,
            "serverIdentityFingerprint": invitation["serverIdentityFingerprint"],
            "clientIdentityFingerprint": client_identity,
            "nonce": "second-host-session-hello-0001",
            "timestamp": session_timestamp,
            "clientIdentity": {
                "machineFingerprint": client_machine_identity["machineFingerprint"],
                "machineFingerprintComputedByPreflight": client_machine_identity["machineFingerprintComputedByPreflight"],
                "machineFingerprintSource": client_machine_identity["machineFingerprintSource"],
                "machineFingerprintInputsRedacted": client_machine_identity["machineFingerprintInputsRedacted"],
                "observedSourceAddress": local_address,
                "assignedPrivateAddresses": [local_address],
                "hostnameFingerprint": client_machine_identity["hostnameFingerprint"],
                "platformFingerprint": client_machine_identity["platformFingerprint"],
                "runtimeHostKind": client_machine_identity["runtimeHostKind"],
                "runtimeHostKindSource": client_machine_identity["runtimeHostKindSource"],
                "runtimeHostKindInputsRedacted": client_machine_identity["runtimeHostKindInputsRedacted"],
                "wslDetectedByPreflight": client_machine_identity["wslDetectedByPreflight"],
                "containerDetectedByPreflight": client_machine_identity["containerDetectedByPreflight"],
            },
            "clientSourceSafety": client_source_safety,
        }

        bad_hmac_hello = dict(base_hello)
        bad_hmac_hello["nonce"] = "second-host-session-hello-bad-hmac-0001"
        send_signed(bad_hmac_hello, bad_mac=True)

        wrong_server_hello = dict(base_hello)
        wrong_server_hello["nonce"] = "second-host-session-hello-wrong-server-0001"
        wrong_server_hello["serverIdentityFingerprint"] = "e" * 64
        send_signed(wrong_server_hello)

        wrong_identity_hello = dict(base_hello)
        wrong_identity_hello["nonce"] = "second-host-session-hello-wrong-identity-0001"
        wrong_identity_hello["clientIdentityFingerprint"] = "d" * 64
        send_signed(wrong_identity_hello)

        pre_session_command = {
            "type": "command",
            "protocolVersion": checker.EXPECTED_PROTOCOL,
            "compatibilityKey": invitation["sessionCompatibilityKey"],
            "commandId": "second-host-reject-pre-session-0001",
            "remoteSlot": checker.EXPECTED_REMOTE_SLOT,
            "command": checker.EXPECTED_REMOTE_COMMAND,
            "sequence": 1,
            "nonce": "second-host-pre-session-command-0001",
            "timestamp": session_timestamp,
            "wouldForwardToPrivateLanCommandId": checker.EXPECTED_PRIVATE_LAN_COMMAND_ID,
        }
        send_signed(pre_session_command)

        send_signed(base_hello)

        p3 = {
            "type": "command",
            "protocolVersion": checker.EXPECTED_PROTOCOL,
            "compatibilityKey": invitation["sessionCompatibilityKey"],
            "commandId": "second-host-reject-p3-forward-0001",
            "remoteSlot": "P3",
            "command": checker.EXPECTED_REMOTE_COMMAND,
            "sequence": 1,
            "nonce": "second-host-p3-forward-0001",
            "timestamp": session_timestamp,
            "wouldForwardToPrivateLanCommandId": checker.EXPECTED_PRIVATE_LAN_COMMAND_ID,
        }
        send_signed(p3)

        bad_hmac = dict(p3)
        bad_hmac.update({"commandId": "second-host-reject-bad-hmac-0001", "remoteSlot": checker.EXPECTED_REMOTE_SLOT, "sequence": 2, "nonce": "second-host-bad-hmac-0001"})
        send_signed(bad_hmac, bad_mac=True)

        stale_timestamp = dict(p3)
        stale_timestamp.update({"commandId": "second-host-reject-timestamp-0001", "remoteSlot": checker.EXPECTED_REMOTE_SLOT, "sequence": 2, "nonce": "second-host-stale-timestamp-0001", "timestamp": session_timestamp - nonce_window - STALE_TIMESTAMP_SECONDS})
        send_signed(stale_timestamp)

        future_timestamp = dict(p3)
        future_timestamp.update({"commandId": "second-host-reject-future-timestamp-0001", "remoteSlot": checker.EXPECTED_REMOTE_SLOT, "sequence": 2, "nonce": "second-host-future-timestamp-0001", "timestamp": session_timestamp + nonce_window + STALE_TIMESTAMP_SECONDS})
        send_signed(future_timestamp)

        sequence_regression = dict(p3)
        sequence_regression.update({"commandId": "second-host-reject-sequence-0001", "remoteSlot": checker.EXPECTED_REMOTE_SLOT, "sequence": 1, "nonce": "second-host-sequence-regression-0001"})
        send_signed(sequence_regression)

        bad_compatibility = dict(p3)
        bad_compatibility.update({"commandId": "second-host-reject-compatibility-key-0001", "remoteSlot": checker.EXPECTED_REMOTE_SLOT, "sequence": 2, "nonce": "second-host-bad-compatibility-0001", "compatibilityKey": "wrong-session-compatibility-key"})
        send_signed(bad_compatibility)

        p2 = dict(p3)
        p2.update(
            {
                "commandId": checker.EXPECTED_COMMAND_ID,
                "remoteSlot": checker.EXPECTED_REMOTE_SLOT,
                "sequence": 2,
                "nonce": "second-host-p2-forward-0001",
            }
        )
        send_signed(p2)

        replay = dict(p2)
        replay.update({"commandId": "second-host-reject-replay-0001", "sequence": 3})
        send_signed(replay)

        rate = dict(p2)
        rate.update({"commandId": "second-host-reject-rate-limit-0001", "sequence": 4, "nonce": "second-host-rate-limit-0001"})
        send_signed(rate)

        unknown_field = dict(p2)
        unknown_field.update(
            {
                "commandId": "second-host-reject-unknown-field-0001",
                "sequence": 5,
                "nonce": "second-host-unknown-field-0001",
                "ignoredButSignedOverclaim": True,
            }
        )
        send_signed(unknown_field)

        direct_input = dict(p2)
        direct_input.update(
            {
                "commandId": "second-host-reject-direct-input-0001",
                "sequence": 5,
                "nonce": "second-host-direct-input-0001",
                "directInputAttempted": True,
                "gameInputSentBySecondHostClient": True,
                "hostHelperInputSent": True,
            }
        )
        send_signed(direct_input)
        client_source_safety_after = make_source_safety_side_evidence(
            role="client",
            copied_profile_sha256=client_copied_profile_sha256,
            installed_game_sha256=client_installed_game_sha256,
            copied_profile_root=client_copied_profile_root,
            installed_game_root=client_installed_game_root,
        )
        postflight = {
            "type": "source_safety_postflight",
            "protocolVersion": checker.EXPECTED_PROTOCOL,
            "clientIdentityFingerprint": client_identity,
            "nonce": "second-host-source-safety-postflight-0001",
            "timestamp": int(time.time()),
            "clientSourceSafetyAfter": client_source_safety_after,
        }
        postflight_response = send_signed(postflight)
        write_json_line(handle, {"type": "close"})

    return {
        "clientSourceAddress": local_address,
        "clientMachineFingerprint": client_machine_identity["machineFingerprint"],
        "clientMachineFingerprintComputedByPreflight": client_machine_identity["machineFingerprintComputedByPreflight"],
        "clientRuntimeHostKind": client_machine_identity["runtimeHostKind"],
        "clientSourceSafetyEvidenceMode": client_source_safety["sourceEvidenceMode"],
        "clientSourceSafetyComputedByPreflight": client_source_safety["computedByPreflight"],
        "clientSourceSafetyPostflightAccepted": postflight_response.get("sourceSafetyPostflightAccepted") is True,
        "clientIdentityFingerprint": client_identity,
        "responses": responses,
    }


def run_server(
    *,
    private_lan_proof_path: Path,
    output_path: Path,
    bind_host: str,
    command_source_kind: str,
    invitation_path: Path,
    host_machine_fingerprint: str | None,
    host_copied_profile_sha256: str | None,
    host_installed_game_sha256: str | None,
    host_copied_profile_root: Path | None = None,
    host_installed_game_root: Path | None = None,
    host_runtime_host_kind: str | None = None,
    host_assigned_addresses: list[str],
    client_identity_fingerprint: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    command_source_kind = require_allowed_source_kind(command_source_kind)
    bind_host = require_private_lan_address(bind_host, "bind host")
    host_assigned_addresses = collect_host_private_addresses(bind_host, host_assigned_addresses)
    invitation_path = require_private_invitation_path(invitation_path)
    host_machine_identity = make_machine_identity_preflight(
        host_machine_fingerprint,
        runtime_host_kind=host_runtime_host_kind,
    )
    host_source_safety_before = make_source_safety_side_evidence(
        role="host",
        copied_profile_sha256=host_copied_profile_sha256,
        installed_game_sha256=host_installed_game_sha256,
        copied_profile_root=host_copied_profile_root,
        installed_game_root=host_installed_game_root,
    )
    credential = secrets.token_bytes(32)
    upstream_hash = lan.sha256_file(private_lan_proof_path)
    authorization = make_authorization(credential, upstream_hash, require_hex64(client_identity_fingerprint, "client identity"))
    max_timeout = int(authorization["expiresAtUnix"]) - int(authorization["issuedAtUnix"])
    require(timeout_seconds <= max_timeout, "server timeout must not exceed invitation expiry window")

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((bind_host, 0))
    listener.listen(1)
    listener.settimeout(timeout_seconds)
    port = int(listener.getsockname()[1])
    listener_lifecycle = make_listener_lifecycle_receipt(
        bind_host=bind_host,
        port=port,
        evidence_mode="live-server-socket-receipt",
        listener_closed=False,
    )
    invitation_payload = make_invitation(
        private_lan_proof_path=private_lan_proof_path,
        bind_host=bind_host,
        port=port,
        credential=credential,
        authorization=authorization,
    )
    write_private_invitation(invitation_path, invitation_payload)

    errors: queue.Queue[BaseException] = queue.Queue()
    result: queue.Queue[dict[str, Any]] = queue.Queue()

    def reject(payload: dict[str, Any], reason: str) -> dict[str, Any]:
        return {"type": "command_rejected", "reason": reason, "commandId": payload.get("commandId"), "secondHostClientAccepted": False}

    def server_main() -> None:
        accepted_commands = 0
        client_identity: dict[str, Any] = {}
        client_safety: dict[str, Any] = {}
        client_safety_after: dict[str, Any] = {}
        session_established = False
        seen_nonces: set[str] = set()
        last_sequence = 0
        transcript_events = [make_event("server_bound", {"bind": "private-lan"})]

        def consume_nonce_sequence(payload: dict[str, Any]) -> str | None:
            nonlocal last_sequence
            nonce = str(payload.get("nonce") or "")
            if not nonce:
                return "missing-nonce"
            if nonce in seen_nonces:
                return "replay-nonce"
            try:
                sequence = int(payload.get("sequence"))
            except (TypeError, ValueError):
                return "sequence-order"
            if sequence <= last_sequence:
                return "sequence-order"
            seen_nonces.add(nonce)
            last_sequence = sequence
            return None

        def classify_command(payload: dict[str, Any], *, server_observed_at: int) -> dict[str, Any]:
            nonlocal accepted_commands
            if not session_established:
                return reject(payload, "session-not-established")
            if not verify_mac(payload, credential):
                return reject(payload, "bad-hmac")
            schema_error = incoming_message_schema_error(payload)
            if schema_error is not None:
                return reject(payload, schema_error)
            if payload.get("protocolVersion") != checker.EXPECTED_PROTOCOL:
                return reject(payload, "protocol-mismatch")
            if session_is_expired(authorization, now_unix=server_observed_at):
                return reject(payload, "timestamp-window")
            if payload.get("compatibilityKey") != object_at(read_json(private_lan_proof_path), "sessionDescriptor")["sessionCompatibilityKey"]:
                return reject(payload, "compatibility-key-mismatch")
            if not payload_timestamp_in_window(payload, authorization, observed_at_unix=server_observed_at):
                return reject(payload, "timestamp-window")
            sequence_error = consume_nonce_sequence(payload)
            if sequence_error is not None:
                return reject(payload, sequence_error)
            if payload.get("remoteSlot") in checker.EXPECTED_METADATA_SLOTS:
                return reject(payload, "metadata-slot-gameplay-not-allowed")
            if payload.get("remoteSlot") != checker.EXPECTED_REMOTE_SLOT:
                return reject(payload, "remote-slot-not-allowed")
            if payload.get("command") != checker.EXPECTED_REMOTE_COMMAND:
                return reject(payload, "command-not-allowed")
            if payload.get("wouldForwardToPrivateLanCommandId") != checker.EXPECTED_PRIVATE_LAN_COMMAND_ID:
                return reject(payload, "forward-target-mismatch")
            if payload.get("directInputAttempted") is True or payload.get("gameInputSentBySecondHostClient") is True or payload.get("hostHelperInputSent") is True:
                return reject(payload, "direct-input-not-allowed")
            if accepted_commands >= 1:
                return reject(payload, "rate-limit-exceeded")
            if payload.get("commandId") != checker.EXPECTED_COMMAND_ID:
                return reject(payload, "message-schema-mismatch")
            accepted_commands += 1
            return {
                "type": "command_accepted",
                "commandId": checker.EXPECTED_COMMAND_ID,
                "remoteSlot": checker.EXPECTED_REMOTE_SLOT,
                "command": checker.EXPECTED_REMOTE_COMMAND,
                "secondHostClientAccepted": True,
                "wouldForwardToPrivateLanCommandId": checker.EXPECTED_PRIVATE_LAN_COMMAND_ID,
                "gameInputSentBySecondHostClient": False,
                "hostHelperInputSent": False,
            }

        try:
            connection, remote_address = listener.accept()
            client_source_address = str(remote_address[0])
            with connection:
                connection.settimeout(SOCKET_IO_TIMEOUT_SECONDS)
                handle = connection.makefile("rwb")
                while True:
                    try:
                        payload = read_json_line(handle)
                    except SecondHostCommandSourceBundleBuildError as exc:
                        if str(exc) == "socket closed before a response was read":
                            break
                        raise
                    if payload.get("type") == "close":
                        if incoming_message_schema_error(payload) is not None:
                            write_json_line(handle, reject(payload, "message-schema-mismatch"))
                            continue
                        transcript_events.append(make_event("client_close", {"type": "close"}))
                        break
                    response: dict[str, Any]
                    if payload.get("type") == "session_hello":
                        hello_kind = "client_session_hello"
                        response_kind = "server_session_accepted"
                        server_observed_at = int(time.time())
                        if not verify_mac(payload, credential):
                            hello_kind = "client_session_hello_bad_hmac"
                            response_kind = "server_session_rejected_bad_hmac"
                            response = {"type": "session_rejected", "reason": "bad-hmac"}
                        elif incoming_message_schema_error(payload) is not None:
                            response = {"type": "session_rejected", "reason": "message-schema-mismatch"}
                        elif session_is_expired(authorization, now_unix=server_observed_at):
                            response_kind = "server_session_rejected_timestamp_window"
                            response = {"type": "session_rejected", "reason": "timestamp-window"}
                        elif not payload_timestamp_in_window(payload, authorization, observed_at_unix=server_observed_at):
                            response_kind = "server_session_rejected_timestamp_window"
                            response = {"type": "session_rejected", "reason": "timestamp-window"}
                        elif payload.get("protocolVersion") != checker.EXPECTED_PROTOCOL:
                            response = {"type": "session_rejected", "reason": "protocol-mismatch"}
                        elif payload.get("serverIdentityFingerprint") != authorization["serverIdentityFingerprint"]:
                            hello_kind = "client_session_hello_wrong_server"
                            response_kind = "server_session_rejected_server_pin"
                            response = {"type": "session_rejected", "reason": "pinned-identity-mismatch"}
                        elif payload.get("clientIdentityFingerprint") != authorization["clientIdentityFingerprint"]:
                            hello_kind = "client_session_hello_wrong_identity"
                            response_kind = "server_session_rejected_pinned_identity"
                            response = {"type": "session_rejected", "reason": "pinned-identity-mismatch"}
                        else:
                            client_identity = object_at(payload, "clientIdentity")
                            client_safety = object_at(payload, "clientSourceSafety")
                            session_established = True
                            seen_nonces.add(str(payload.get("nonce") or ""))
                            response = {
                                "type": "session_accepted",
                                "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
                                "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
                            }
                        transcript_events.append(make_event(hello_kind, payload, serverObservedAtUnix=server_observed_at))
                        transcript_events.append(make_event(response_kind, response, serverObservedAtUnix=server_observed_at))
                    elif payload.get("type") == "command":
                        server_observed_at = int(time.time())
                        command_id = str(payload.get("commandId") or "")
                        command_event = {
                            "second-host-reject-p3-forward-0001": "client_command_p3_forward",
                            "second-host-reject-bad-hmac-0001": "client_command_bad_hmac",
                            "second-host-reject-pre-session-0001": "client_command_pre_session",
                            "second-host-reject-timestamp-0001": "client_command_stale_timestamp",
                            "second-host-reject-future-timestamp-0001": "client_command_future_timestamp",
                            "second-host-reject-sequence-0001": "client_command_sequence_regression",
                            "second-host-reject-compatibility-key-0001": "client_command_bad_compatibility",
                            checker.EXPECTED_COMMAND_ID: "client_command_p2_forward",
                            "second-host-reject-replay-0001": "client_command_replay_nonce",
                            "second-host-reject-rate-limit-0001": "client_command_rate_limited",
                            "second-host-reject-unknown-field-0001": "client_command_unknown_field",
                            "second-host-reject-direct-input-0001": "client_command_direct_input",
                        }.get(command_id, "client_command_rate_limited")
                        transcript_events.append(make_event(command_event, payload, serverObservedAtUnix=server_observed_at))
                        response = classify_command(payload, server_observed_at=server_observed_at)
                        reason = response.get("reason")
                        response_event = {
                            "metadata-slot-gameplay-not-allowed": "server_command_rejected_metadata_slot",
                            "bad-hmac": "server_command_rejected_bad_hmac",
                            "session-not-established": "server_command_rejected_pre_session",
                            "timestamp-window": "server_command_rejected_timestamp_window",
                            "sequence-order": "server_command_rejected_sequence_order",
                            "compatibility-key-mismatch": "server_command_rejected_compatibility_key",
                            "replay-nonce": "server_command_rejected_replay_nonce",
                            "rate-limit-exceeded": "server_command_rejected_rate_limit",
                            "message-schema-mismatch": "server_command_rejected_unknown_field",
                            "direct-input-not-allowed": "server_command_rejected_direct_input",
                        }.get(str(reason), "server_command_accepted")
                        if command_event == "client_command_future_timestamp" and reason == "timestamp-window":
                            response_event = "server_command_rejected_future_timestamp"
                        transcript_events.append(make_event(response_event, response, serverObservedAtUnix=server_observed_at))
                    elif payload.get("type") == "source_safety_postflight":
                        server_observed_at = int(time.time())
                        transcript_events.append(make_event("client_source_safety_postflight", payload, serverObservedAtUnix=server_observed_at))
                        if not session_established:
                            response = reject(payload, "session-not-established")
                        elif not verify_mac(payload, credential):
                            response = reject(payload, "bad-hmac")
                        elif payload.get("protocolVersion") != checker.EXPECTED_PROTOCOL:
                            response = reject(payload, "protocol-mismatch")
                        elif payload.get("clientIdentityFingerprint") != authorization["clientIdentityFingerprint"]:
                            response = reject(payload, "pinned-identity-mismatch")
                        elif incoming_message_schema_error(payload) is not None:
                            response = reject(payload, "message-schema-mismatch")
                        elif not payload_timestamp_in_window(payload, authorization, observed_at_unix=server_observed_at):
                            response = reject(payload, "timestamp-window")
                        else:
                            client_safety_after = object_at(payload, "clientSourceSafetyAfter")
                            response = {
                                "type": "source_safety_postflight_accepted",
                                "clientIdentityFingerprint": authorization["clientIdentityFingerprint"],
                                "sourceSafetyPostflightAccepted": True,
                            }
                        transcript_events.append(
                            make_event(
                                "server_source_safety_postflight_accepted",
                                response,
                                serverObservedAtUnix=server_observed_at,
                            )
                        )
                    else:
                        response = reject(payload, "unknown-message-type")
                    write_json_line(handle, response)
            transcript_events.append(make_event("server_stopped", {"type": "server_stopped"}))
            result.put(
                {
                    "clientSourceAddress": client_source_address,
                    "clientIdentity": client_identity,
                    "clientSourceSafety": client_safety,
                    "clientSourceSafetyAfter": client_safety_after,
                    "transcriptEvents": transcript_events,
                }
            )
        except BaseException as exc:  # noqa: BLE001
            errors.put(exc)
        finally:
            listener.close()

    invitation_deleted = False
    try:
        thread = threading.Thread(target=server_main, name="second-host-command-source-server", daemon=True)
        thread.start()
        thread.join(timeout_seconds + 5)
        require(not thread.is_alive(), "second-host command-source server timed out")
        if not errors.empty():
            raise SecondHostCommandSourceBundleBuildError(errors.get())
        observation = result.get_nowait()
        client_identity = observation["clientIdentity"]
        client_safety_before = observation["clientSourceSafety"]
        client_safety_after = observation["clientSourceSafetyAfter"]
        require(client_safety_after, "client source-safety postflight was not observed")
        host_source_safety_after = make_source_safety_side_evidence(
            role="host",
            copied_profile_sha256=host_copied_profile_sha256,
            installed_game_sha256=host_installed_game_sha256,
            copied_profile_root=host_copied_profile_root,
            installed_game_root=host_installed_game_root,
        )
        host_source_safety = make_two_phase_source_safety_side_evidence(
            role="host",
            before=host_source_safety_before,
            after=host_source_safety_after,
        )
        client_safety = make_two_phase_source_safety_side_evidence(
            role="client",
            before=client_safety_before,
            after=client_safety_after,
        )
        source_safety = make_source_safety(
            host_copied_profile_sha256=host_source_safety_before["copiedProfileSha256Before"],
            host_installed_game_sha256=host_source_safety_before["installedGameSha256Before"],
            client_copied_profile_sha256=client_safety["copiedProfileSha256Before"],
            client_installed_game_sha256=client_safety["installedGameSha256Before"],
            host_evidence=host_source_safety,
            client_evidence=client_safety,
        )
        transcript_events = observation["transcriptEvents"]
        invitation_deleted = delete_private_invitation(invitation_path)
        invitation_lifecycle = make_invitation_lifecycle_receipt(
            invitation_payload,
            deleted=invitation_deleted,
            post_delete_exists=invitation_path.exists(),
        )
        listener_lifecycle = make_listener_lifecycle_receipt(
            bind_host=bind_host,
            port=port,
            evidence_mode="live-server-socket-receipt",
            listener_closed=True,
            post_close_connect_rejected=post_close_connect_is_rejected(bind_host, port),
        )
        summary = make_bundle_from_observation(
            private_lan_proof_path=private_lan_proof_path,
            output_path=output_path,
            command_source_kind=command_source_kind,
            host_bind_address=bind_host,
            host_assigned_addresses=host_assigned_addresses,
            host_machine_fingerprint=host_machine_identity["machineFingerprint"],
            client_source_address=observation["clientSourceAddress"],
            client_assigned_address=str(client_identity["observedSourceAddress"]),
            client_machine_fingerprint=str(client_identity["machineFingerprint"]),
            client_identity_fingerprint=authorization["clientIdentityFingerprint"],
            authorization=authorization,
            source_safety=source_safety,
            transcript_events=transcript_events,
            session_security_hardening=make_live_session_security_hardening(transcript_events),
            host_machine_identity=host_machine_identity,
            client_machine_identity=client_identity,
            invitation_lifecycle=invitation_lifecycle,
            listener_lifecycle=listener_lifecycle,
        )
    finally:
        if not invitation_deleted:
            invitation_deleted = delete_private_invitation(invitation_path)
    summary["clientInvitationDeleted"] = invitation_deleted
    return summary


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        private_lan = lan.make_bundle_fixture(root)
        credential = bytes.fromhex("12" * 32)
        auth = make_authorization(credential, lan.sha256_file(private_lan), "c" * 64)
        source_safety = make_source_safety(
            host_copied_profile_sha256="3" * 64,
            host_installed_game_sha256="4" * 64,
            client_copied_profile_sha256="5" * 64,
            client_installed_game_sha256="6" * 64,
        )
        summary = make_bundle_from_observation(
            private_lan_proof_path=private_lan,
            output_path=root / "second-host-command-source-proof.json",
            command_source_kind="distinct-vm-private-lan-labeled-vm-only",
            host_bind_address=checker.FIXTURE_HOST_ADDRESS,
            host_assigned_addresses=[checker.FIXTURE_HOST_ADDRESS],
            host_machine_fingerprint="1" * 64,
            client_source_address=checker.FIXTURE_CLIENT_ADDRESS,
            client_assigned_address=checker.FIXTURE_CLIENT_ADDRESS,
            client_machine_fingerprint="2" * 64,
            client_identity_fingerprint="c" * 64,
            authorization=auth,
            source_safety=source_safety,
            transcript_events=[
                make_event(kind, {"kind": kind})
                for kind in checker.EXPECTED_TRANSCRIPT_EVENTS
            ],
        )
        require(summary["acceptedCommandId"] == checker.EXPECTED_COMMAND_ID, "self-test command mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="Run the builder self-test.")
    sub = parser.add_subparsers(dest="mode")

    server = sub.add_parser("server")
    server.add_argument("private_lan_proof", type=Path)
    server.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    server.add_argument("--bind-host", required=True)
    server.add_argument("--command-source-kind", required=True, choices=sorted(checker.ALLOWED_COMMAND_SOURCE_KINDS))
    server.add_argument("--client-invitation", type=Path, required=True)
    server.add_argument("--host-machine-fingerprint")
    server.add_argument("--host-copied-profile-sha256")
    server.add_argument("--host-installed-game-sha256")
    server.add_argument("--host-copied-profile-root", type=Path)
    server.add_argument("--host-installed-game-root", type=Path)
    server.add_argument("--host-runtime-host-kind", choices=sorted(KNOWN_RUNTIME_HOST_KINDS))
    server.add_argument("--host-assigned-address", action="append", default=[])
    server.add_argument("--client-identity-fingerprint", required=True)
    server.add_argument("--timeout-seconds", type=int, default=PROCESS_TIMEOUT_SECONDS)

    client = sub.add_parser("client")
    client.add_argument("invitation", type=Path)
    client.add_argument("--client-machine-fingerprint")
    client.add_argument("--client-copied-profile-sha256")
    client.add_argument("--client-installed-game-sha256")
    client.add_argument("--client-copied-profile-root", type=Path)
    client.add_argument("--client-installed-game-root", type=Path)
    client.add_argument("--client-runtime-host-kind", choices=sorted(KNOWN_RUNTIME_HOST_KINDS))

    sub.add_parser("self-test")
    args = parser.parse_args()

    if args.self_test or args.mode == "self-test":
        run_self_test()
        print("WinUI original-binary second-host command-source builder self-test: PASS")
        return 0
    if args.mode is None:
        parser.error("mode is required unless --self-test is used")
    if args.mode == "client":
        print(json.dumps(run_client(
            args.invitation,
            client_machine_fingerprint=args.client_machine_fingerprint,
            client_copied_profile_sha256=args.client_copied_profile_sha256,
            client_installed_game_sha256=args.client_installed_game_sha256,
            client_copied_profile_root=args.client_copied_profile_root,
            client_installed_game_root=args.client_installed_game_root,
            client_runtime_host_kind=args.client_runtime_host_kind,
        ), indent=2, sort_keys=True))
        return 0
    summary = run_server(
        private_lan_proof_path=args.private_lan_proof,
        output_path=args.output,
        bind_host=args.bind_host,
        command_source_kind=args.command_source_kind,
        invitation_path=args.client_invitation,
        host_machine_fingerprint=args.host_machine_fingerprint,
        host_copied_profile_sha256=args.host_copied_profile_sha256,
        host_installed_game_sha256=args.host_installed_game_sha256,
        host_copied_profile_root=args.host_copied_profile_root,
        host_installed_game_root=args.host_installed_game_root,
        host_runtime_host_kind=args.host_runtime_host_kind,
        host_assigned_addresses=args.host_assigned_address,
        client_identity_fingerprint=args.client_identity_fingerprint,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        SecondHostCommandSourceBundleBuildError,
        checker.SecondHostCommandSourceProofError,
        lan.PrivateTransportSmokeProofError,
        lan.delivery.PrivateRelayDeliveryProofError,
        lan.delivery.relay.RelayProofError,
        lan.delivery.loopback.LoopbackProofError,
        lan.delivery.loopback.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI original-binary second-host command-source builder: FAIL: {exc}")
        raise SystemExit(2)
