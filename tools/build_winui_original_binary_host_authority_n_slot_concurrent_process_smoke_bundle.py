#!/usr/bin/env python3
"""Build a same-host concurrent four-client N-slot host-authority process smoke proof."""

from __future__ import annotations

import argparse
import hmac
import ipaddress
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

import winui_safe_copy_online_host_authority_n_slot_concurrent_process_smoke_check as check


SCHEMA = check.EXPECTED_SCHEMA
SESSION_SCHEMA = check.EXPECTED_SESSION_SCHEMA
TRANSPORT = check.EXPECTED_TRANSPORT
PROTOCOL = check.EXPECTED_PROTOCOL
HELPER = check.EXPECTED_HELPER
HELPER_VERSION = check.EXPECTED_HELPER_VERSION
EXPECTED_COMMAND = check.EXPECTED_COMMAND
SLOTS = check.EXPECTED_SLOTS
ACTIVE_SLOTS = check.EXPECTED_ACTIVE_SLOTS
METADATA_SLOTS = check.EXPECTED_METADATA_SLOTS
ARRIVAL_ORDER = check.EXPECTED_ARRIVAL_ORDER
CONCURRENCY_MODEL = check.EXPECTED_CONCURRENCY_MODEL
COMMAND_IDS = {
    "P1": check.EXPECTED_P1_COMMAND_ID,
    "P2": check.EXPECTED_P2_COMMAND_ID,
    "P3": check.EXPECTED_P3_COMMAND_ID,
    "P4": check.EXPECTED_P4_COMMAND_ID,
}
SEQUENCES = {
    "P1": check.EXPECTED_P1_SEQUENCE,
    "P2": check.EXPECTED_P2_SEQUENCE,
    "P3": check.EXPECTED_P3_SEQUENCE,
    "P4": check.EXPECTED_P4_SEQUENCE,
}
ARRIVAL_DELAYS = {
    "P4": 0.00,
    "P2": 0.08,
    "P3": 0.16,
    "P1": 0.24,
}
SAFE_CHILD_ENV_KEYS = {"COMSPEC", "PATH", "PATHEXT", "SYSTEMROOT", "TEMP", "TMP", "WINDIR"}
PROCESS_TIMEOUT_SECONDS = 20
SERVER_TIMEOUT_SECONDS = 10


class HostAuthorityNSlotConcurrentProcessSmokeBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostAuthorityNSlotConcurrentProcessSmokeBuildError(message)


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "mac"}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: dict[str, Any], credential: bytes) -> dict[str, Any]:
    signed = dict(payload)
    signed["mac"] = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    return signed


def write_json_line(handle: Any, payload: dict[str, Any]) -> None:
    handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
    handle.flush()


def read_json_line(handle: Any) -> dict[str, Any]:
    line = handle.readline()
    require(bool(line), "host-authority socket closed before response")
    value = json.loads(line.decode("utf-8"))
    require(isinstance(value, dict), "host-authority response was not a JSON object")
    return value


def require_private_bind_host(bind_host: str) -> None:
    try:
        address = ipaddress.ip_address(bind_host)
    except ValueError as exc:
        raise HostAuthorityNSlotConcurrentProcessSmokeBuildError(f"Bind host must be an IP address: {bind_host}") from exc
    require(address.is_private, "Bind host must be private")
    require(not address.is_loopback, "Bind host must be non-loopback")
    require(not address.is_link_local, "Bind host must not be link-local")
    require(not address.is_multicast and not address.is_unspecified, "Bind host must be a concrete private interface address")


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def make_event(kind: str, payload: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"kind": kind, "monotonicNs": time.monotonic_ns()}
    if payload is not None:
        event["payloadSha256"] = check.sha256_payload(payload)
        event["payloadBytes"] = len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")) + 1
    event.update(extra)
    return event


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
        "slotCapacity": 4,
        "acceptedSessionParticipantCount": 4,
        "originalBinaryActiveSlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "participants": [participant(slot) for slot in SLOTS],
    }


def sanitized_child_env() -> dict[str, str]:
    child_env = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in SAFE_CHILD_ENV_KEYS
    }
    child_env["PYTHONIOENCODING"] = "utf-8"
    return child_env


def sensitive_env_key_count(env: dict[str, str]) -> int:
    fragments = ("SECRET", "PASSWORD", "TOKEN", "AUTH", "CREDENTIAL", "APIKEY", "API_KEY")
    return sum(1 for key in env if any(fragment in key.upper() for fragment in fragments))


CLIENT_CODE = r'''
import hmac
import json
import os
import socket
import sys
import time


def canonical_bytes(payload):
    clean = {key: value for key, value in payload.items() if key != "mac"}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload, credential):
    signed = dict(payload)
    signed["mac"] = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
    return signed


def write_json_line(handle, payload):
    handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n")
    handle.flush()


def read_json_line(handle):
    line = handle.readline()
    if not line:
        raise RuntimeError("host closed before response")
    value = json.loads(line.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("host response was not an object")
    return value


def wait_for_path(path, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.exists(path):
            return True
        time.sleep(0.01)
    raise RuntimeError(f"timed out waiting for {path}")


config = json.loads(sys.stdin.read())
credential = bytes.fromhex(config["credentialHex"])
slot = config["slot"]
responses = []
ready_marker = config["readyMarker"]
barrier_release = config["barrierRelease"]
close_release = config["closeRelease"]

with open(ready_marker, "w", encoding="utf-8") as handle:
    json.dump({"slot": slot, "clientProcessId": os.getpid(), "readyMonotonicNs": time.monotonic_ns()}, handle, sort_keys=True)

wait_for_path(barrier_release, float(config["barrierTimeoutSeconds"]))
time.sleep(float(config["arrivalDelaySeconds"]))

with socket.create_connection((config["bindHost"], int(config["port"])), timeout=5) as client:
    handle = client.makefile("rwb")
    hello = {
        "type": "session_hello",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "serverIdentityFingerprint": config["serverIdentityFingerprint"],
        "clientIdentityFingerprint": config["clientIdentityFingerprint"],
        "clientSlot": slot,
        "nonce": f"{slot.lower()}-session-hello-0001",
        "timestamp": int(config["now"]),
    }
    write_json_line(handle, sign_payload(hello, credential))
    session_response = read_json_line(handle)
    responses.append({"label": "session", "type": session_response.get("type"), "reason": session_response.get("reason"), "commandId": session_response.get("commandId")})
    if session_response.get("serverIdentityFingerprint") != config["serverIdentityFingerprint"]:
        raise RuntimeError("server identity mismatch")
    if session_response.get("type") != "session_accepted":
        raise RuntimeError(f"session was not accepted for {slot}: {session_response}")

    command = {
        "type": "command",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "clientSlot": slot,
        "commandId": config["commandId"],
        "command": config["expectedCommand"],
        "sequence": 1,
        "nonce": f"{slot.lower()}-forward-0001",
        "timestamp": int(config["now"]),
        "mappedInputSequence": config["mappedInputSequence"],
        "directGameInputClaim": False,
        "publicMatchmakingClaim": False,
    }
    write_json_line(handle, sign_payload(command, credential))
    response = read_json_line(handle)
    responses.append({
        "label": "accepted" if response.get("type") == "command_accepted" else "rejected-gameplay-route",
        "type": response.get("type"),
        "reason": response.get("reason"),
        "commandId": response.get("commandId"),
        "scheduledTick": response.get("scheduledTick"),
    })

    wait_for_path(close_release, float(config["barrierTimeoutSeconds"]))
    close = {
        "type": "close",
        "protocolVersion": config["protocolVersion"],
        "compatibilityKey": config["compatibilityKey"],
        "clientSlot": slot,
        "nonce": f"{slot.lower()}-close-0001",
        "timestamp": int(config["now"]),
    }
    write_json_line(handle, sign_payload(close, credential))

print(json.dumps({
    "clientProcessId": os.getpid(),
    "slot": slot,
    "clientVerifiedServerIdentity": True,
    "responses": responses,
}, sort_keys=True))
'''


def client_config(
    slot: str,
    *,
    bind_host: str,
    port: int,
    descriptor: dict[str, Any],
    authorization: dict[str, Any],
    credential: bytes,
    proof_root: Path,
    now: int,
) -> dict[str, Any]:
    return {
        "bindHost": bind_host,
        "port": port,
        "protocolVersion": PROTOCOL,
        "compatibilityKey": descriptor["sessionCompatibilityKey"],
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "clientIdentityFingerprint": authorization["clientIdentityFingerprints"][slot],
        "expectedCommand": EXPECTED_COMMAND,
        "now": now,
        "slot": slot,
        "commandId": COMMAND_IDS[slot],
        "mappedInputSequence": SEQUENCES[slot],
        "credentialHex": credential.hex(),
        "arrivalDelaySeconds": ARRIVAL_DELAYS[slot],
        "barrierTimeoutSeconds": SERVER_TIMEOUT_SECONDS,
        "readyMarker": str(proof_root / f"{slot.lower()}-ready.json"),
        "barrierRelease": str(proof_root / "all-clients-ready.release"),
        "closeRelease": str(proof_root / "all-sockets-observed.release"),
    }


def start_client_process(config: dict[str, Any], *, child_env: dict[str, str]) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [sys.executable, "-c", CLIENT_CODE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=child_env,
    )
    require(process.stdin is not None, "client stdin pipe was not created")
    process.stdin.write(json.dumps(config))
    process.stdin.close()
    process.stdin = None
    return process


class HostAuthorityServer:
    def __init__(
        self,
        descriptor: dict[str, Any],
        *,
        credentials: dict[str, bytes],
        authorization: dict[str, Any],
        bind_host: str,
        now: int,
    ) -> None:
        self.descriptor = descriptor
        self.credentials = credentials
        self.authorization = authorization
        self.bind_host = bind_host
        self.now = now
        self.events: list[dict[str, Any]] = []
        self.accepted_commands: list[dict[str, Any]] = []
        self.rejected_commands: list[dict[str, Any]] = []
        self.seen_nonces: set[str] = set()
        self.expected_sequence = {slot: 1 for slot in SLOTS}
        self.accepted_per_slot = {slot: 0 for slot in SLOTS}
        self.accepted_per_tick = {1: 0}
        self.active_connections = 0
        self.max_active_connections = 0
        self.command_count = 0
        self.connection_slots: set[str] = set()
        self.errors: list[str] = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.stop_event = threading.Event()
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((bind_host, 0))
        self.port = int(self.listener.getsockname()[1])
        self.thread = threading.Thread(target=self._server_main, name="n-slot-concurrent-host-authority", daemon=True)
        self.handler_threads: list[threading.Thread] = []

    def start(self) -> None:
        self.thread.start()
        self.events.append(make_event("server_bound", bindHost=self.bind_host, actualBindPort=self.port))

    def stop(self) -> None:
        self.stop_event.set()
        try:
            self.listener.close()
        except OSError:
            pass
        self.thread.join(timeout=5)
        for thread in list(self.handler_threads):
            thread.join(timeout=5)
        require(not self.thread.is_alive(), "host-authority N-slot accept thread did not stop")
        require(all(not thread.is_alive() for thread in self.handler_threads), "host-authority N-slot handler thread did not stop")
        if self.errors:
            raise HostAuthorityNSlotConcurrentProcessSmokeBuildError(self.errors[0])

    def wait_for_socket_concurrency(self) -> None:
        deadline = time.monotonic() + SERVER_TIMEOUT_SECONDS
        with self.condition:
            while self.max_active_connections < 4 and time.monotonic() < deadline:
                self.condition.wait(timeout=0.05)
            require(self.max_active_connections == 4, "server did not observe four simultaneous socket connections")

    def wait_for_all_commands(self) -> None:
        deadline = time.monotonic() + SERVER_TIMEOUT_SECONDS
        with self.condition:
            while self.command_count < 4 and time.monotonic() < deadline:
                self.condition.wait(timeout=0.05)
            require(self.command_count == 4, "server did not observe four commands")

    def _server_main(self) -> None:
        try:
            self.listener.listen(8)
            self.listener.settimeout(0.2)
            while not self.stop_event.is_set():
                with self.lock:
                    done = len(self.connection_slots) >= 4 and self.command_count >= 4 and self.active_connections == 0
                if done:
                    break
                try:
                    conn, addr = self.listener.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                peer_host = str(addr[0])
                if peer_host != self.bind_host:
                    conn.close()
                    with self.lock:
                        self.events.append(make_event("foreign_peer_rejected", peerHost=peer_host))
                    continue
                thread = threading.Thread(target=self._handle_connection, args=(conn, peer_host), daemon=True)
                self.handler_threads.append(thread)
                thread.start()
        except Exception as exc:  # pragma: no cover - surfaced in generated proof failures
            with self.lock:
                self.errors.append(str(exc))
                self.condition.notify_all()

    def _record_connection_open(self, peer_host: str) -> None:
        with self.condition:
            self.active_connections += 1
            self.max_active_connections = max(self.max_active_connections, self.active_connections)
            self.events.append(make_event("socket_connected", peerHost=peer_host, activeConnectionCount=self.active_connections))
            self.events.append(make_event("server_active_connection_count", activeConnectionCount=self.active_connections))
            self.condition.notify_all()

    def _record_connection_close(self) -> None:
        with self.condition:
            self.active_connections -= 1
            self.condition.notify_all()

    def _handle_connection(self, conn: socket.socket, peer_host: str) -> None:
        session_slot: str | None = None
        self._record_connection_open(peer_host)
        try:
            with conn:
                conn.settimeout(5.0)
                handle = conn.makefile("rwb")
                while not self.stop_event.is_set():
                    line = handle.readline()
                    if not line:
                        break
                    payload = json.loads(line.decode("utf-8"))
                    if payload.get("type") == "close":
                        self._handle_close(payload, session_slot)
                        break
                    with self.condition:
                        self.events.append(
                            make_event(
                                "client_message",
                                payload,
                                clientSlot=payload.get("clientSlot"),
                                messageType=payload.get("type"),
                                commandId=payload.get("commandId"),
                            )
                        )
                        response, session_slot = self._handle_payload_locked(payload, session_slot)
                        self.events.append(
                            make_event(
                                "server_response",
                                response,
                                clientSlot=response.get("clientSlot"),
                                responseType=response.get("type"),
                                reason=response.get("reason"),
                                commandId=response.get("commandId"),
                                scheduledTick=response.get("scheduledTick"),
                            )
                        )
                    write_json_line(handle, response)
        except Exception as exc:  # pragma: no cover - surfaced in generated proof failures
            with self.condition:
                self.errors.append(str(exc))
                self.condition.notify_all()
        finally:
            self._record_connection_close()

    def _verify_mac_locked(self, payload: dict[str, Any], credential: bytes) -> bool:
        mac = payload.get("mac")
        if not isinstance(mac, str):
            return False
        expected = hmac.new(credential, canonical_bytes(payload), "sha256").hexdigest()
        return hmac.compare_digest(mac, expected)

    def _base_validate_locked(self, payload: dict[str, Any], *, session_slot: str | None) -> tuple[str | None, dict[str, Any] | None]:
        slot = payload.get("clientSlot")
        if slot not in self.credentials:
            return None, {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "client-slot-not-allowed", "clientSlot": slot}
        slot = str(slot)
        if session_slot is not None and session_slot != slot:
            return slot, {"type": "command_rejected", "reason": "slot-changed-on-connection", "clientSlot": slot}
        if not self._verify_mac_locked(payload, self.credentials[slot]):
            reason = "missing-authentication" if "mac" not in payload else "bad-hmac"
            return slot, {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": reason, "clientSlot": slot}
        timestamp = payload.get("timestamp")
        if not isinstance(timestamp, int) or abs(timestamp - self.now) > int(self.authorization["nonceWindowSeconds"]):
            return slot, {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "expired-timestamp", "clientSlot": slot}
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or not nonce:
            return slot, {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "missing-nonce", "clientSlot": slot}
        if nonce in self.seen_nonces:
            return slot, {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "replay-nonce", "clientSlot": slot}
        self.seen_nonces.add(nonce)
        if payload.get("protocolVersion") != PROTOCOL:
            return slot, {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "protocol-mismatch", "clientSlot": slot}
        if payload.get("compatibilityKey") != self.descriptor["sessionCompatibilityKey"]:
            return slot, {"type": "session_rejected" if payload.get("type") == "session_hello" else "command_rejected", "reason": "session-compatibility-mismatch", "clientSlot": slot}
        return slot, None

    def _handle_payload_locked(self, payload: dict[str, Any], session_slot: str | None) -> tuple[dict[str, Any], str | None]:
        slot, early_response = self._base_validate_locked(payload, session_slot=session_slot)
        if early_response is not None:
            return early_response, session_slot
        require(slot is not None, "validated slot must be present")

        if payload.get("type") == "session_hello":
            if session_slot is not None:
                return {"type": "session_rejected", "reason": "duplicate-session-on-connection", "clientSlot": slot}, session_slot
            if payload.get("serverIdentityFingerprint") != self.authorization["serverIdentityFingerprint"]:
                return {"type": "session_rejected", "reason": "server-identity-mismatch", "clientSlot": slot}, session_slot
            if payload.get("clientIdentityFingerprint") != self.authorization["clientIdentityFingerprints"][slot]:
                return {"type": "session_rejected", "reason": "client-identity-mismatch", "clientSlot": slot}, session_slot
            self.connection_slots.add(slot)
            return {
                "type": "session_accepted",
                "clientSlot": slot,
                "serverIdentityFingerprint": self.authorization["serverIdentityFingerprint"],
            }, slot

        if payload.get("type") != "command":
            return self._reject_command_locked(payload, "unknown-message-type"), session_slot
        if session_slot is None:
            return self._reject_command_locked(payload, "command-before-session"), session_slot
        if payload.get("sequence") != self.expected_sequence[slot]:
            return self._reject_command_locked(payload, "sequence-not-next"), session_slot
        if payload.get("command") != EXPECTED_COMMAND:
            return self._reject_command_locked(payload, "command-not-allowed"), session_slot
        if payload.get("commandId") != COMMAND_IDS[slot]:
            return self._reject_command_locked(payload, "command-id-not-allowed"), session_slot
        if payload.get("mappedInputSequence") != SEQUENCES[slot]:
            return self._reject_command_locked(payload, "mapped-input-sequence-mismatch"), session_slot
        if payload.get("directGameInputClaim") is True:
            return self._reject_command_locked(payload, "direct-input-not-allowed"), session_slot
        if payload.get("publicMatchmakingClaim") is True:
            return self._reject_command_locked(payload, "public-matchmaking-not-allowed"), session_slot
        if slot in METADATA_SLOTS:
            return self._reject_command_locked(payload, "required-for-unproven-original-binary-slots"), session_slot
        if self.accepted_per_slot[slot] >= int(self.authorization["rateLimit"]["maxAcceptedCommandsPerSlot"]):
            return self._reject_command_locked(payload, "slot-rate-limit"), session_slot
        if self.accepted_per_tick[1] >= int(self.authorization["rateLimit"]["maxAcceptedCommandsPerTick"]):
            return self._reject_command_locked(payload, "tick-rate-limit"), session_slot

        tick = 1
        self.expected_sequence[slot] += 1
        self.accepted_per_slot[slot] += 1
        self.accepted_per_tick[tick] += 1
        row = {
            "commandId": payload.get("commandId"),
            "clientSlot": slot,
            "command": EXPECTED_COMMAND,
            "mappedInputSequence": payload.get("mappedInputSequence"),
            "scheduledTick": tick,
            "arrivalOrder": len([r for r in self.accepted_commands + self.rejected_commands if r.get("clientSlot") in SLOTS]) + 1,
            "hostAccepted": True,
            "gameInputSentByNSlotScheduler": False,
            "hostHelperInputSent": False,
        }
        self.accepted_commands.append(row)
        self.command_count += 1
        self.condition.notify_all()
        return {"type": "command_accepted", **row}, session_slot

    def _reject_command_locked(self, payload: dict[str, Any], reason: str) -> dict[str, Any]:
        row = {
            "commandId": payload.get("commandId"),
            "clientSlot": payload.get("clientSlot"),
            "reason": reason,
            "hostAccepted": False,
            "gameInputSentByNSlotScheduler": False,
            "hostHelperInputSent": False,
        }
        if payload.get("clientSlot") in METADATA_SLOTS and reason == "required-for-unproven-original-binary-slots":
            self.rejected_commands.append(row)
        if payload.get("clientSlot") in SLOTS and payload.get("type") == "command":
            self.command_count += 1
            self.condition.notify_all()
        return {"type": "command_rejected", **row}

    def _handle_close(self, payload: dict[str, Any], session_slot: str | None) -> None:
        with self.condition:
            slot, early_response = self._base_validate_locked(payload, session_slot=session_slot)
            require(early_response is None, f"close rejected: {early_response}")
            require(slot == session_slot, "close slot did not match established session")
            self.events.append(make_event("client_close", payload, clientSlot=payload.get("clientSlot")))
            self.condition.notify_all()


def collect_ready_markers(proof_root: Path, processes: dict[str, subprocess.Popen[str]]) -> list[dict[str, Any]]:
    deadline = time.monotonic() + SERVER_TIMEOUT_SECONDS
    marker_by_slot: dict[str, dict[str, Any]] = {}
    while time.monotonic() < deadline and len(marker_by_slot) < 4:
        for slot in ARRIVAL_ORDER:
            if slot in marker_by_slot:
                continue
            marker = proof_root / f"{slot.lower()}-ready.json"
            if marker.exists():
                value = json.loads(marker.read_text(encoding="utf-8"))
                require(isinstance(value, dict), f"{slot} ready marker must be an object")
                require(value.get("slot") == slot, f"{slot} ready marker slot mismatch")
                require(value.get("clientProcessId") == processes[slot].pid, f"{slot} ready marker PID mismatch")
                marker_by_slot[slot] = value
        time.sleep(0.01)
    require(len(marker_by_slot) == 4, "not all client processes reached ready barrier")
    require(all(processes[slot].poll() is None for slot in SLOTS), "all clients must still be alive before barrier release")
    return [
        {
            "clientSlot": slot,
            "clientProcessId": marker_by_slot[slot]["clientProcessId"],
            "readyBeforeBarrierRelease": True,
            "readyMonotonicNs": marker_by_slot[slot]["readyMonotonicNs"],
        }
        for slot in ARRIVAL_ORDER
    ]


def finish_client_process(slot: str, process: subprocess.Popen[str], credentials: dict[str, bytes]) -> dict[str, Any]:
    try:
        stdout, stderr = process.communicate(timeout=PROCESS_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        stdout, stderr = process.communicate(timeout=5)
        raise HostAuthorityNSlotConcurrentProcessSmokeBuildError(f"{slot} client process timed out: {stderr.strip()}") from exc
    for raw_credential in credentials.values():
        credential_hex = raw_credential.hex()
        require(credential_hex not in stdout, f"{slot} stdout leaked a credential")
        require(credential_hex not in stderr, f"{slot} stderr leaked a credential")
    require(process.returncode == 0, f"{slot} client process failed: {stderr.strip()}")
    output = json.loads(stdout.strip())
    require(isinstance(output, dict), f"{slot} client output must be an object")
    require(output.get("clientProcessId") == process.pid, f"{slot} child PID did not match parent-observed PID")
    output["clientExitCode"] = process.returncode
    output["clientProcessIdFromParent"] = process.pid
    output["stdoutBytes"] = len(stdout.encode("utf-8"))
    output["stderrBytes"] = len(stderr.encode("utf-8"))
    return output


def run_host_authority_session(
    descriptor: dict[str, Any],
    *,
    credentials: dict[str, bytes],
    authorization: dict[str, Any],
    bind_host: str,
    proof_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = 2_100_000_000
    child_env = sanitized_child_env()
    require(sensitive_env_key_count(child_env) == 0, "sanitized child environment still has sensitive keys")
    server = HostAuthorityServer(
        descriptor,
        credentials=credentials,
        authorization=authorization,
        bind_host=bind_host,
        now=now,
    )
    processes: dict[str, subprocess.Popen[str]] = {}
    configs: dict[str, dict[str, Any]] = {}
    ready_rows: list[dict[str, Any]] = []
    outputs: dict[str, dict[str, Any]] = {}
    barrier_release = proof_root / "all-clients-ready.release"
    close_release = proof_root / "all-sockets-observed.release"
    try:
        server.start()
        for slot in ARRIVAL_ORDER:
            configs[slot] = client_config(
                slot,
                bind_host=bind_host,
                port=server.port,
                descriptor=descriptor,
                authorization=authorization,
                credential=credentials[slot],
                proof_root=proof_root,
                now=now,
            )
            processes[slot] = start_client_process(configs[slot], child_env=child_env)
            server.events.append(make_event("client_process_started", clientSlot=slot, processId=processes[slot].pid))

        ready_rows = collect_ready_markers(proof_root, processes)
        alive_at_barrier = all(processes[slot].poll() is None for slot in SLOTS)
        require(alive_at_barrier, "all clients must still be alive at barrier release")
        for row in ready_rows:
            server.events.append(make_event("client_barrier_ready", clientSlot=row["clientSlot"], processId=row["clientProcessId"]))
        barrier_release.write_text("release\n", encoding="utf-8")
        barrier_release_ns = time.monotonic_ns()
        server.events.append(make_event("barrier_released", clientReadyBeforeBarrierReleaseCount=len(ready_rows)))
        server.wait_for_socket_concurrency()
        server.wait_for_all_commands()
        close_release.write_text("release\n", encoding="utf-8")
        close_release_ns = time.monotonic_ns()
        server.events.append(make_event("close_barrier_released", activeConnectionCount=server.max_active_connections))

        for slot in ARRIVAL_ORDER:
            outputs[slot] = finish_client_process(slot, processes[slot], credentials)
            server.events.append(make_event("client_process_exited", processId=outputs[slot]["clientProcessId"], clientSlot=slot, exitCode=outputs[slot]["clientExitCode"]))
    finally:
        for process in processes.values():
            if process.poll() is None:
                process.kill()
                try:
                    process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
        server.stop()
    server.events.append(make_event("server_stopped"))

    require(len(server.accepted_commands) == 2, "expected two accepted P1/P2 commands")
    require(len(server.rejected_commands) == 2, "expected two rejected P3/P4 commands")
    require([row["clientSlot"] for row in server.accepted_commands] == ["P2", "P1"], "accepted command arrival order mismatch")
    require([row["clientSlot"] for row in server.rejected_commands] == ["P4", "P3"], "rejected command arrival order mismatch")

    relay_plan = [
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
    scheduler = {
        "schedulerSchema": "host-authority-n-slot-scheduler.v1",
        "declaredSlotCount": 4,
        "slotCapacity": 4,
        "acceptedSessionParticipantCount": 4,
        "originalBinaryRelaySlotCount": 2,
        "acceptedOriginalBinaryGameplayCommandCount": len(server.accepted_commands),
        "rejectedOriginalBinaryGameplayCommandCount": len(server.rejected_commands),
        "acceptedOriginalBinaryGameplaySlots": ACTIVE_SLOTS,
        "metadataOnlySlots": METADATA_SLOTS,
        "rejectedGameplayRouteSlots": METADATA_SLOTS,
        "extraSlotRejectionPolicy": "required-for-unproven-original-binary-slots",
        "arrivalOrder": ARRIVAL_ORDER,
        "deterministicParticipantOrder": SLOTS,
        "deterministicOriginalBinaryRelayOrder": ACTIVE_SLOTS,
        "relayPlan": relay_plan,
        "relayPlanSha256": check.sha256_payload(relay_plan),
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
        "newBeaLaunchCount": 0,
        "cdbAttachCount": 0,
    }
    transport = {
        "transport": TRANSPORT,
        "bindHost": bind_host,
        "actualBindPort": server.port,
        "networkScope": "private-interface-n-slot-concurrent-process-smoke",
        "privateLanInterfaceBound": True,
        "privateLanReachableDuringRun": True,
        "foreignPeersRejectedAfterAccept": True,
        "loopbackInterfaceOnly": False,
        "sameWorkstationClientProcessesOnly": True,
        "sameWorkstationNetworkOnly": False,
        "processSeparatedClients": True,
        "processConcurrencyModel": CONCURRENCY_MODEL,
        "simultaneousClientProcessesProven": 4,
        "clientReadyBeforeBarrierReleaseCount": len(ready_rows),
        "barrierReleaseAfterAllClientsReady": True,
        "maxSimultaneousSocketConnectionsProven": server.max_active_connections,
        "clientProcessCount": 4,
        "publicNetworkSocketsOpened": False,
        "multiHostLanClaim": False,
        "publicMatchmakingClaim": False,
        "publicServerClaim": False,
        "nativeBeaNetcodeClaim": False,
        "natTraversalClaim": False,
        "deterministicSyncClaim": False,
        "rollbackClaim": False,
        "antiCheatClaim": False,
        "physicalGamepadClaim": False,
        "rebuildParityClaim": False,
        "gameInputSentByNSlotScheduler": False,
        "hostHelperInputSent": False,
        "newBeaLaunchCount": 0,
        "cdbAttachCount": 0,
    }
    process_boundary = {
        "processModel": "four-separate-python-client-processes",
        "processConcurrencyModel": CONCURRENCY_MODEL,
        "simultaneousClientProcessesProven": 4,
        "allClientProcessesReadyBeforeBarrierRelease": True,
        "allClientProcessesAliveAtBarrierRelease": alive_at_barrier,
        "allClientSocketsHeldUntilCloseRelease": True,
        "builderProcessId": os.getpid(),
        "clientProcessCount": 4,
        "clientProcesses": [
            {
                "clientSlot": slot,
                "clientProcessId": outputs[slot]["clientProcessId"],
                "clientProcessIdFromParent": outputs[slot]["clientProcessIdFromParent"],
                "clientVerifiedServerIdentity": outputs[slot]["clientVerifiedServerIdentity"],
                "clientExitCode": outputs[slot]["clientExitCode"],
            }
            for slot in ARRIVAL_ORDER
        ],
        "clientProcessIdsDistinctFromBuilder": all(outputs[slot]["clientProcessId"] != os.getpid() for slot in SLOTS),
        "clientProcessIdsDistinctFromEachOther": len({outputs[slot]["clientProcessId"] for slot in SLOTS}) == 4,
        "credentialTransportToClientProcesses": "stdin-ephemeral-not-serialized-to-artifact",
        "clientEnvSensitiveKeyCount": sensitive_env_key_count(child_env),
        "clientCommandLineContainsCredential": False,
        "clientEnvironmentContainsCredential": False,
        "clientStdoutContainsCredential": False,
        "clientStderrContainsCredential": False,
        "sameWorkstationClientProcessesOnly": True,
        "sameWorkstationNetworkOnly": False,
        "multiHostLanClaim": False,
        "clientResponses": {slot: outputs[slot]["responses"] for slot in SLOTS},
    }
    concurrency_proof = {
        "processConcurrencyModel": CONCURRENCY_MODEL,
        "clientReadyBeforeBarrierReleaseCount": len(ready_rows),
        "barrierReleaseAfterAllClientsReady": True,
        "barrierReleaseMonotonicNs": barrier_release_ns,
        "closeBarrierReleaseMonotonicNs": close_release_ns,
        "maxSimultaneousClientProcessesProven": 4,
        "maxSimultaneousSocketConnectionsProven": server.max_active_connections,
        "allClientProcessesAliveAtBarrierRelease": True,
        "allClientSocketsHeldUntilCloseRelease": True,
        "clientProcessTiming": [
            {
                "clientSlot": slot,
                "clientProcessId": outputs[slot]["clientProcessId"],
                "processStartedBeforeBarrierRelease": True,
                "readyBeforeBarrierRelease": True,
                "processExitedAfterBarrierRelease": True,
                "socketOpenedBeforeCloseRelease": True,
                "socketClosedAfterCloseRelease": True,
            }
            for slot in ARRIVAL_ORDER
        ],
    }
    transcript = {
        "transport": TRANSPORT,
        "protocolVersion": PROTOCOL,
        "serverIdentityFingerprint": authorization["serverIdentityFingerprint"],
        "messageCount": 20,
        "events": server.events,
    }
    commands = {
        "acceptedOriginalBinaryGameplay": server.accepted_commands,
        "rejectedOriginalBinaryGameplay": server.rejected_commands,
    }
    return transport, commands, scheduler, process_boundary, concurrency_proof, transcript


def build_bundle(output_path: Path, *, bind_host: str) -> dict[str, Any]:
    require_private_bind_host(bind_host)
    descriptor = make_session_descriptor()
    compatibility_key = sha256(f"{PROTOCOL}:n-slot-concurrent-process-smoke:v1".encode("utf-8")).hexdigest()
    descriptor["sessionCompatibilityKey"] = compatibility_key
    credentials = {slot: os.urandom(32) for slot in SLOTS}
    authorization = {
        "scheme": "HMAC-SHA256",
        "credentialStorage": "ephemeral-not-serialized",
        "serializedCredentialPresent": False,
        "slotCredentialFingerprints": {slot: sha256(value).hexdigest() for slot, value in credentials.items()},
        "serverIdentityMode": "pinned-fingerprint",
        "serverIdentityFingerprint": sha256(f"{PROTOCOL}:server:n-slot-concurrent-process-smoke".encode("utf-8")).hexdigest(),
        "clientIdentityMode": "pinned-slot-fingerprint",
        "clientIdentityFingerprints": {
            slot: sha256(f"{PROTOCOL}:client:{slot}".encode("utf-8")).hexdigest()
            for slot in SLOTS
        },
        "nonceWindowSeconds": 30,
        "replayCacheEnabled": True,
        "replayCacheScope": "slot-nonce-smoke",
        "sequenceEnforced": True,
        "rateLimit": {
            "maxAcceptedCommandsPerSlot": 1,
            "maxAcceptedCommandsPerTick": 2,
        },
        "clockMode": "deterministic-smoke-clock",
        "securityProofScope": "minimal-smoke-hmac-envelope-not-full-session-security-proof",
        "sessionScopedMacCoverageProof": False,
        "maxJsonLineBytesEnforced": False,
        "unknownFieldRejectionProof": False,
        "strictMessageSchemaProof": False,
        "tickBoundMacFieldsProof": False,
    }
    with tempfile.TemporaryDirectory(prefix="bea-n-slot-concurrent-proof-") as tmp:
        proof_root = Path(tmp)
        transport, commands, scheduler, process_boundary, concurrency_proof, transcript = run_host_authority_session(
            descriptor,
            credentials=credentials,
            authorization=authorization,
            bind_host=bind_host,
            proof_root=proof_root,
        )
    bundle = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "sessionDescriptor": descriptor,
        "transport": transport,
        "authorization": authorization,
        "clientProcessBoundary": process_boundary,
        "concurrencyProof": concurrency_proof,
        "commands": commands,
        "hostAuthorityNSlotScheduler": scheduler,
        "transportTranscript": transcript,
        "nPlayerOriginalBinaryRuntimeProof": 0,
        "activeP3P4OriginalBinaryGameplayProof": False,
        "permanentImpossibilityClaim": False,
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
            "Same-workstation-client/private-interface concurrent four-client N-slot scheduler/process smoke only. "
            "This proves four separate local slot-scoped client processes reached a parent-observed ready barrier, "
            "remained alive at release, opened four simultaneous private-interface socket connections, and held those "
            "sockets until a close barrier while only P1/P2 were scheduled into the original-binary relay plan. The "
            "listener is private-LAN reachable during the run, foreign peers are rejected after accept, and the HMAC "
            "layer is a minimal smoke envelope rather than a full session-security proof. It does not launch BEA, does "
            "not attach CDB, does not send host-helper input, does not prove active P3/P4 original-binary gameplay, "
            "and does not prove multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, "
            "rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity."
        ),
    }
    serialized = json.dumps(bundle, indent=2)
    for raw_credential in credentials.values():
        require(raw_credential.hex() not in serialized, "raw credential leaked into serialized proof")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized, encoding="utf-8")
    summary = check.validate_bundle(output_path)
    return {
        "bundle": str(output_path.resolve()),
        "bundleSha256": sha256_file(output_path),
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bind-host", required=True)
    args = parser.parse_args()

    print(json.dumps(build_bundle(args.output.resolve(), bind_host=args.bind_host), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HostAuthorityNSlotConcurrentProcessSmokeBuildError, check.HostAuthorityNSlotProcessSmokeProofError) as exc:
        print(f"WinUI original-binary host-authority N-slot concurrent process smoke bundle build: FAIL: {exc}")
        raise SystemExit(2)
