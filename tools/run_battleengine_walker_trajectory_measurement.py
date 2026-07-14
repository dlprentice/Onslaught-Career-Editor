#!/usr/bin/env python3
"""Receipt-bound two-attempt walker trajectory measurement orchestration.

This tool has two explicit modes.  The outer mode invokes the accepted AppCore
safe-copy harness exactly twice.  The observer mode is launched by that harness
after it has created and validated a runtime-process-receipt.  The observer
uses query/read rights only; it never writes target memory or attaches a
debugger.  All emitted material is private raw evidence.  Public behavior
contracts are deliberately outside this tool.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from dataclasses import asdict, replace
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from typing import Callable, Protocol, Sequence

import battleengine_walker_trajectory_sampler as sampler
import runtime_proof_lab_hygiene as proof_hygiene


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = Path(__file__).resolve()
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
FORBIDDEN_PROCESS_RIGHTS = 0x0002 | 0x0008 | 0x0020 | 0x0400
Q_SCAN_CODE = 0x10
Q_VIRTUAL_KEY = 0x51  # VK_Q
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_EXTENDEDKEY = 0x0001
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
BATCH_SIZE = 5
READINESS_DEADLINE_SECONDS = 15
READINESS_POLL_SECONDS = 0.050
READINESS_STABLE_POLLS = 3
OBSERVER_DEADLINE_SECONDS = 90
AGGREGATE_DEADLINE_SECONDS = 600
PREBUILD_SAFETY_BOUND_SECONDS = 150
PROFILE_PREPARATION_BOUND_SECONDS = 120
LAUNCH_RECEIPT_FOCUS_BOUND_SECONDS = 30
CLEANUP_RESERVE_SECONDS = 20
COMPLETE_ATTEMPT_BUDGET_SECONDS = 215
DECLARED_MAXIMUM_SECONDS = 580
WALKER_PROTOCOL = "battleengine-walker-trajectory-v1"
INTERFERENCE_NONCLAIM = (
    "The guard detects receipt, process, module, HWND, and foreground drift; "
    "it does not detect arbitrary human or controller input."
)


class AttemptDeadlineExceeded(RuntimeError):
    pass


class Deadline:
    def __init__(self, seconds: float, *, monotonic: Callable[[], float] = time.monotonic) -> None:
        self._monotonic = monotonic
        self._expires = monotonic() + seconds

    def check(self, label: str = "observer") -> None:
        if self._monotonic() >= self._expires:
            raise AttemptDeadlineExceeded(f"{label} deadline expired")


class NativeApi(Protocol):
    def open_process(self, pid: int, access: int) -> int: ...
    def close_handle(self, handle: int) -> None: ...
    def read_process_memory(self, handle: int, address: int, size: int) -> bytes: ...
    def current_identity(
        self, handle: int, expected: sampler.ReceiptIdentity
    ) -> sampler.ReceiptIdentity: ...
    def foreground_window(self) -> int: ...
    def force_foreground(self, hwnd: int) -> bool: ...
    def send_scan_code(self, scan_code: int, key_up: bool) -> int: ...


class QpcClock:
    def __init__(self) -> None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.QueryPerformanceFrequency.argtypes = [ctypes.POINTER(ctypes.c_longlong)]
        kernel32.QueryPerformanceFrequency.restype = wintypes.BOOL
        kernel32.QueryPerformanceCounter.argtypes = [ctypes.POINTER(ctypes.c_longlong)]
        kernel32.QueryPerformanceCounter.restype = wintypes.BOOL
        frequency = ctypes.c_longlong()
        if not kernel32.QueryPerformanceFrequency(ctypes.byref(frequency)):
            raise ctypes.WinError(ctypes.get_last_error())
        self.frequency = int(frequency.value)
        self._kernel32 = kernel32

    def now(self) -> int:
        value = ctypes.c_longlong()
        if not self._kernel32.QueryPerformanceCounter(ctypes.byref(value)):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(value.value)

    def wait_until(self, target: int) -> int:
        # Sleep for coarse remaining time; busy-spin the last ~2 ms so live
        # cadence does not yield past the slot and collapse into the next bin.
        while True:
            now = self.now()
            remaining = (target - now) / self.frequency
            if remaining <= 0:
                return now
            if remaining > 0.002:
                time.sleep(max(0.0, remaining - 0.001))
            # else busy-spin


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _exact_keys(value: object, expected: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label} property set mismatch")
    return value


def _file_identity(value: object, label: str) -> tuple[Path, str, int]:
    row = _exact_keys(value, {"path", "sha256", "size"}, label)
    path = Path(str(row["path"]))
    digest = str(row["sha256"])
    size = row["size"]
    if not path.is_absolute() or _has_reparse_ancestor(path) or not path.is_file():
        raise ValueError(f"{label} path is not an existing absolute file")
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise ValueError(f"{label} size is invalid")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError(f"{label} SHA-256 is invalid")
    if path.stat().st_size != size or _sha256(path) != digest:
        raise ValueError(f"{label} byte identity mismatch")
    return path.resolve(), digest, size


def _path_is_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0) & 0x400
    )


def _has_reparse_ancestor(path: Path) -> bool:
    # Do not resolve first: resolution would erase the lexical junction/symlink
    # that this check is intended to detect.
    current = Path(os.path.abspath(os.fspath(path)))
    while True:
        if _path_is_reparse(current):
            return True
        if current.parent == current:
            return False
        current = current.parent


def _authorize_private_path(path: Path, authorized_private_root: Path, *, label: str) -> Path:
    lexical = Path(os.path.abspath(os.fspath(path)))
    lexical_root = Path(os.path.abspath(os.fspath(authorized_private_root)))
    if _has_reparse_ancestor(lexical):
        raise ValueError(f"{label} is reparse routed")
    if _has_reparse_ancestor(lexical_root):
        raise ValueError("authorized private root is reparse routed")
    resolved = lexical.resolve(strict=False)
    resolved_root = lexical_root.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"resolved {label} escaped the authorized private root") from exc
    if resolved == resolved_root:
        raise ValueError(f"{label} must be strictly beneath the authorized private root")
    return resolved


def load_receipt(path: Path, expected_sha256: str, *,
                 authorized_private_root: Path | None = None) -> sampler.ReceiptIdentity:
    lexical_path = Path(os.path.abspath(os.fspath(path)))
    if _has_reparse_ancestor(lexical_path):
        raise ValueError("receipt path is reparse routed")
    path = lexical_path.resolve()
    if authorized_private_root is not None:
        path = _authorize_private_path(
            lexical_path, authorized_private_root, label="receipt path"
        )
    if not path.is_file() or _sha256(path) != expected_sha256:
        raise ValueError("receipt SHA-256 mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    root = _exact_keys(payload, {
        "schemaVersion", "runId", "process", "profileManifest", "window", "module",
        "sourceExecutableSha256", "copiedExecutableSha256", "commandTemplateSha256",
        "generatedCommandSha256",
    }, "receipt")
    if root["schemaVersion"] != "runtime-process-receipt.v1":
        raise ValueError("receipt schema mismatch")
    process = _exact_keys(root["process"], {
        "id", "startedAtUtc", "executable", "workingDirectory", "launchArguments"
    }, "receipt process")
    window = _exact_keys(root["window"], {"hwndHex"}, "receipt window")
    module = _exact_keys(root["module"], {"path", "baseAddressHex", "size"}, "receipt module")
    executable, executable_digest, _ = _file_identity(process["executable"], "receipt executable")
    _, manifest_digest, _ = _file_identity(root["profileManifest"], "profile manifest")
    arguments = process["launchArguments"]
    expected_arguments = ["-skipfmv", "-level", "850", "-configuration", "2"]
    if arguments != expected_arguments:
        raise ValueError("receipt launch arguments do not match the locked walker protocol")
    pid = process["id"]
    module_size = module["size"]
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        raise ValueError("receipt PID is invalid")
    if not isinstance(module_size, int) or isinstance(module_size, bool) or module_size <= 0:
        raise ValueError("receipt module size is invalid")
    working_directory = Path(str(process["workingDirectory"]))
    module_path = Path(str(module["path"]))
    if not working_directory.is_absolute() or not module_path.is_absolute():
        raise ValueError("receipt working directory and module path must be absolute")
    if _has_reparse_ancestor(working_directory) or _has_reparse_ancestor(module_path):
        raise ValueError("receipt working directory or module path is reparse routed")
    if executable != module_path.resolve():
        raise ValueError("receipt executable and module paths differ")
    if str(root["copiedExecutableSha256"]) != executable_digest:
        raise ValueError("receipt copied executable digest mismatch")
    source_digest = str(root["sourceExecutableSha256"])
    if source_digest != executable_digest:
        raise ValueError("receipt source/copy digest mismatch")
    try:
        module_base = int(str(module["baseAddressHex"]), 16)
        hwnd = int(str(window["hwndHex"]), 16)
    except ValueError as exc:
        raise ValueError("receipt module base or HWND is invalid") from exc
    if module_base <= 0 or module_base & 3 or hwnd <= 0:
        raise ValueError("receipt module base or HWND is invalid")
    return sampler.ReceiptIdentity(
        receipt_sha256=expected_sha256,
        process_id=pid,
        started_at_utc=str(process["startedAtUtc"]),
        executable_sha256=executable_digest,
        module_path=str(module_path.resolve()),
        module_base=module_base,
        module_size=module_size,
        window_handle=hwnd,
        window_process_id=pid,
        manifest_sha256=manifest_digest,
        launch_arguments=tuple(arguments),
        artifact_root=str(
            Path(authorized_private_root).resolve()
            if authorized_private_root is not None
            else path.parent.resolve()
        ),
        artifact_path=str(path),
        path_is_reparse=False,
    )


def require_absent_outputs(paths: Sequence[Path]) -> None:
    for path in paths:
        if path.exists() or path.is_symlink():
            raise ValueError(f"output already exists: {path}")


class ReceiptPinnedReader:
    def __init__(self, receipt: sampler.ReceiptIdentity, native: NativeApi) -> None:
        self.receipt = receipt
        self.native = native
        self.handle: int | None = None
        self.closed = False

    def open(self) -> None:
        if self.handle is not None or self.closed:
            raise RuntimeError("observer handle lifecycle is invalid")
        rights = PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ
        if rights & FORBIDDEN_PROCESS_RIGHTS:
            raise RuntimeError("observer requested forbidden process rights")
        self.handle = self.native.open_process(self.receipt.process_id, rights)
        if not self.handle:
            raise RuntimeError("OpenProcess failed")

    def read(self, address: int, size: int) -> bytes:
        if self.handle is None or self.closed:
            raise RuntimeError("observer handle is not open")
        if address <= 0 or address > 0xFFFFFFFF or size <= 0 or address + size - 1 > 0xFFFFFFFF:
            raise RuntimeError("ReadProcessMemory range is invalid")
        value = self.native.read_process_memory(self.handle, address, size)
        if len(value) != size:
            raise RuntimeError(f"short ReadProcessMemory result: expected {size}, found {len(value)}")
        return value

    def close(self) -> None:
        if self.handle is not None and not self.closed:
            self.native.close_handle(self.handle)
            self.closed = True
            self.handle = None


class ReceiptRuntimeGuard:
    interference_nonclaim = INTERFERENCE_NONCLAIM

    def __init__(self, receipt: sampler.ReceiptIdentity, receipt_path: Path,
                 receipt_sha256: str, native: NativeApi, handle: int,
                 authorized_private_root: Path) -> None:
        self.receipt = receipt
        self.receipt_path = receipt_path
        self.receipt_sha256 = receipt_sha256
        self.native = native
        self.handle = handle
        self.authorized_private_root = authorized_private_root

    def revalidate_receipt(self) -> bool:
        try:
            disk = load_receipt(
                self.receipt_path, self.receipt_sha256,
                authorized_private_root=self.authorized_private_root,
            )
            sampler.require_receipt_match(self.receipt, disk)
            live = self.native.current_identity(self.handle, disk)
            sampler.require_receipt_match(disk, live)
            return True
        except (OSError, RuntimeError, ValueError):
            return False

    def foreground_matches(self) -> bool:
        return self.native.foreground_window() == self.receipt.window_handle

    def interference_detected(self) -> bool:
        # The adapter intentionally makes no claim about arbitrary human or
        # controller input.  Identity and foreground drift are separate gates.
        return False


class ScanCodeQInput:
    """Legacy direct SendInput path (unit tests / offline). Prefer ExternalHarnessQInput live."""

    def __init__(self, native: NativeApi, window_handle: int) -> None:
        self.native = native
        self.window_handle = window_handle
        self.events: list[tuple[int, bool]] = []
        self.down_confirmed = False
        self.up_confirmed = False

    def key_down(self) -> bool:
        if self.events:
            raise RuntimeError("Q input permits exactly one key-down and one key-up")
        if not self.native.force_foreground(self.window_handle):
            raise RuntimeError("could not foreground the receipt-bound BEA window for Q-down")
        confirmed = self.native.send_scan_code(Q_SCAN_CODE, False) >= 1
        self.events.append((Q_SCAN_CODE, False))
        self.down_confirmed = confirmed
        return confirmed

    def key_up(self) -> bool:
        if self.events != [(Q_SCAN_CODE, False)]:
            raise RuntimeError("Q input permits exactly one key-down and one key-up")
        self.native.force_foreground(self.window_handle)
        confirmed = self.native.send_scan_code(Q_SCAN_CODE, True) >= 1
        self.events.append((Q_SCAN_CODE, True))
        self.up_confirmed = confirmed
        return confirmed


def _marker_handshake(evidence_root: Path, name: str, *, timeout_seconds: float) -> bool:
    request = evidence_root / f"request-{name}.marker"
    ack = evidence_root / f"ack-{name}.marker"
    if ack.exists():
        ack.unlink()
    with request.open("x", encoding="ascii", newline="\n") as stream:
        stream.write("1\n")
        stream.flush()
        os.fsync(stream.fileno())
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if ack.is_file():
            return True
        time.sleep(0.01)
    return False


class ExternalHarnessQInput:
    """Ask the C# AppCore harness to deliver Q via proven SendInputSequence.

    pair-09..12 proved Python SendInput does not move the walker control field
    even with Forward=Q bound and focus restored. The harness already delivers
    focused tap/down/up:Q through tools/send_game_window_input.ps1.
    """

    def __init__(self, evidence_root: Path, *, timeout_seconds: float = 5.0) -> None:
        self.evidence_root = evidence_root
        self.timeout_seconds = timeout_seconds
        self.events: list[tuple[int, bool]] = []
        self.down_confirmed = False
        self.up_confirmed = False

    def _handshake(self, *, down: bool) -> bool:
        name = "q-down" if down else "q-up"
        return _marker_handshake(
            self.evidence_root, name, timeout_seconds=self.timeout_seconds
        )

    def key_down(self) -> bool:
        if self.events:
            raise RuntimeError("Q input permits exactly one key-down and one key-up")
        confirmed = self._handshake(down=True)
        # Harness down:Q,wait:500 already holds Q focused; a short settle is enough
        # before the observer's control-prove wait.
        if confirmed:
            time.sleep(0.25)
        self.events.append((Q_SCAN_CODE, False))
        self.down_confirmed = confirmed
        return confirmed

    def key_up(self) -> bool:
        if self.events != [(Q_SCAN_CODE, False)]:
            raise RuntimeError("Q input permits exactly one key-down and one key-up")
        # Keep Q held after hold samples so residual motion is captured.
        time.sleep(0.5)
        confirmed = self._handshake(down=False)
        self.events.append((Q_SCAN_CODE, True))
        self.up_confirmed = confirmed
        return confirmed


def execute_deadlined_q_batches(
    guard: sampler.RuntimeGuard,
    q_input: sampler.QInput,
    monotonic_tick: Callable[[], int],
    batches: Sequence[Callable[[], object]],
    deadline_check: Callable[[], None],
) -> sampler.InputWindowResult:
    def bounded(batch: Callable[[], object]) -> Callable[[], object]:
        def invoke() -> object:
            deadline_check()
            value = batch()
            deadline_check()
            return value
        return invoke
    deadline_check()
    result = sampler.execute_owned_q_window(
        guard, q_input, monotonic_tick, [bounded(batch) for batch in batches]
    )
    deadline_check()
    return result


def wait_for_runtime_readiness(
    probe: Callable[[], sampler.ReadinessProbe],
    guard: object,
    *,
    deadline_check: Callable[[], None],
    sleep: Callable[[float], None] = time.sleep,
    max_polls: int | None = None,
) -> dict[str, object]:
    """Require three coherent identity-bound ready polls before baseline or Q."""
    consecutive = 0
    polls = 0
    last_not_ready: dict[str, str | None] = {}
    def check_deadline() -> None:
        try:
            deadline_check()
        except AttemptDeadlineExceeded as exc:
            detail = ""
            if last_not_ready:
                key, value = next(iter(last_not_ready.items()))
                detail = f"; last {key}={value}"
            raise AttemptDeadlineExceeded(f"{exc}{detail}") from None
    while True:
        check_deadline()
        if max_polls is not None and polls >= max_polls:
            detail = ""
            if last_not_ready:
                key, value = next(iter(last_not_ready.items()))
                detail = f"; last {key}={value}"
            raise AttemptDeadlineExceeded(
                "readiness deadline expired one poll short of stability" + detail
            )
        if not guard.revalidate_receipt() or not guard.foreground_matches():
            raise sampler.AttemptError("receipt or foreground changed around readiness probe")
        polls += 1
        try:
            value = probe()
        except sampler.RuntimeNotReady as exc:
            not_ready = exc
        else:
            not_ready = None
        if not guard.revalidate_receipt() or not guard.foreground_matches():
            raise sampler.AttemptError("receipt or foreground changed around readiness probe")
        if not_ready is not None:
            consecutive = 0
            last_not_ready = ({"nullHop": not_ready.hop} if not_ready.hop is not None
                              else {"notReadyField": not_ready.field})
        else:
            consecutive += 1
            if consecutive == READINESS_STABLE_POLLS:
                return {
                    "status": "ready", "pollCount": polls,
                    "consecutiveValidPolls": consecutive,
                    "level": value.level, "playerCount": value.player_count,
                    "horizontalSplit": value.horizontal_split,
                    "stateRaw": value.state_raw, "controlRaw": value.control_raw,
                    "lastNotReady": last_not_ready,
                }
        check_deadline()
        sleep(READINESS_POLL_SECONDS)

def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return path.resolve() != root.resolve()
    except ValueError:
        return False


def _validate_closeout(row: dict[str, object], attempt: int, evidence_root: Path) -> None:
    if row.get("attempt") != attempt:
        raise RuntimeError("attempt closeout identity mismatch")
    if row.get("publicProjectionWritten") is not False:
        raise RuntimeError("public projection output is forbidden")
    if row.get("accepted") is True and row.get("harnessExitCode", 0) != 0:
        raise RuntimeError("attempt acceptance contradicts the AppCore harness exit")
    if row.get("accepted") is True and row.get("cooperativeStopRequested") is True:
        raise RuntimeError("attempt acceptance contradicts the aggregate stop request")
    receipt_path = Path(str(row.get("receiptPath", "")))
    digest = str(row.get("receiptSha256", ""))
    if not _is_under(receipt_path, evidence_root) or not receipt_path.is_file():
        raise RuntimeError("attempt receipt escaped its fresh evidence root")
    if _sha256(receipt_path) != digest:
        raise RuntimeError("attempt receipt byte integrity failed")
    phase = row.get("phaseTimestamps")
    phase_names = (
        "profilePreparationStartedTimestamp", "profilePreparationCompletedTimestamp",
        "launchStartedTimestamp", "receiptValidatedTimestamp", "focusAcquiredTimestamp",
        "adapterStartedTimestamp", "cleanupStartedTimestamp", "closeoutWrittenTimestamp",
    )
    if not isinstance(phase, dict) or any(
        not isinstance(phase.get(name), int) or phase[name] <= 0 for name in phase_names
    ):
        raise RuntimeError("attempt phase timestamp receipt is incomplete")
    if any(phase[left] >= phase[right] for left, right in zip(phase_names, phase_names[1:])):
        raise RuntimeError("attempt phase timestamps are not strictly ordered")
    cleanup = row.get("cleanup")
    # Observer Q-up is preferred, but a failed mid-window sample can still release
    # Q via harness backup; that is enough to free attempt two safely.
    if not isinstance(cleanup, dict):
        raise RuntimeError("attempt cleanup gate failed: cleanup receipt missing")
    if cleanup.get("observerQUp") is not True and cleanup.get("backupQUp") is not True:
        raise RuntimeError(
            "attempt cleanup gate failed: neither observer nor backup Q-up confirmed"
        )
    if cleanup.get("backupQUp") not in (True, False):
        raise RuntimeError("backup Q-up truth is absent")
    cleanup_ok = (
        row.get("qUpConfirmed") is True
        and row.get("observerHandleClosed") is True
        and row.get("managedProcessStopped") is True
        and cleanup.get("phaseJobsClosed") is True
        and row.get("ownedProcessCount") == 0
        and row.get("sourceUnchanged") is True
        and row.get("copyUnchanged") is True
    )
    if not cleanup_ok:
        raise RuntimeError("attempt cleanup gate failed; refusing another attempt")


def run_two_attempts(
    private_root: Path,
    invoke: Callable[..., dict[str, object]],
    *,
    authorized_private_root: Path,
    prebuild: Callable[[Path], dict[str, object]],
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, object]:
    """Run at most two attempts and never materialize a public projection."""
    private_root = _authorize_private_path(
        private_root, authorized_private_root, label="two-attempt private root"
    )
    if private_root.exists() or private_root.is_symlink():
        raise ValueError("private two-attempt root already exists")
    private_root.mkdir(parents=True)
    aggregate_started = monotonic()
    aggregate_deadline = aggregate_started + AGGREGATE_DEADLINE_SECONDS
    runner_receipt = prebuild(private_root)
    if any((private_root / f"attempt-{attempt:02d}").exists() for attempt in (1, 2)):
        raise RuntimeError("runner prebuild created an attempt root before passing")
    _validate_prebuild_receipt(runner_receipt, private_root)
    if monotonic() - aggregate_started > PREBUILD_SAFETY_BOUND_SECONDS:
        raise AttemptDeadlineExceeded("runner prebuild exceeded its 150-second safety bound")
    rows: list[dict[str, object]] = []
    receipt_paths: set[str] = set()
    receipt_digests: set[str] = set()
    for attempt in (1, 2):
        remaining = aggregate_deadline - monotonic()
        require_full_attempt_budget(remaining, attempt=attempt)
        attempt_root = private_root / f"attempt-{attempt:02d}"
        profile_root = (
            attempt_root / "profile-app-config" / "OnslaughtCareerEditor" / "GameProfiles"
        )
        evidence_root = attempt_root / "evidence"
        require_absent_outputs((attempt_root, profile_root, evidence_root))
        _revalidate_prebuild_receipt(runner_receipt, private_root)
        row = invoke(attempt, profile_root, evidence_root, runner_receipt, remaining)
        _validate_closeout(row, attempt, evidence_root)
        # After compact evidence and closeout are durable, drop multi-GB game
        # trees and runner build junk under this authorized private root only.
        hygiene_attempt = proof_hygiene.strip_bulky_attempt_tree(
            attempt_root, authorized_private_root=authorized_private_root
        )
        row = dict(row)
        row["labHygiene"] = hygiene_attempt
        if monotonic() > aggregate_deadline:
            raise AttemptDeadlineExceeded(
                "aggregate cooperative decision deadline expired after cleanup closeout"
            )
        receipt_path = str(Path(str(row["receiptPath"])).resolve())
        receipt_digest = str(row["receiptSha256"])
        if receipt_path in receipt_paths or receipt_digest in receipt_digests:
            raise RuntimeError("attempt did not produce a fresh receipt")
        receipt_paths.add(receipt_path)
        receipt_digests.add(receipt_digest)
        rows.append(row)
        if attempt == 1 and row.get("accepted") is not True:
            break
    hygiene_pair = proof_hygiene.strip_runner_build_junk(
        private_root, authorized_private_root=authorized_private_root
    )
    pair_eligible = len(rows) == 2 and all(row.get("accepted") is True for row in rows)
    return {
        "schemaVersion": "battleengine-walker-trajectory-private-pair-closeout.v1",
        "attempts": rows,
        "pairEligible": pair_eligible,
        "publicProjectionWritten": False,
        "interferenceNonclaim": INTERFERENCE_NONCLAIM,
        "aggregateDeadlineSeconds": AGGREGATE_DEADLINE_SECONDS,
        "declaredMaximumSeconds": DECLARED_MAXIMUM_SECONDS,
        "aggregateMarginSeconds": AGGREGATE_DEADLINE_SECONDS - DECLARED_MAXIMUM_SECONDS,
        "completeAttemptBudgetSeconds": COMPLETE_ATTEMPT_BUDGET_SECONDS,
        "prebuild": runner_receipt,
        "labHygiene": hygiene_pair,
    }


def require_full_attempt_budget(remaining_seconds: float, *, attempt: int) -> None:
    if remaining_seconds < COMPLETE_ATTEMPT_BUDGET_SECONDS:
        raise AttemptDeadlineExceeded(
            f"attempt {attempt} refused because the full 215-second attempt budget is unavailable"
        )


def _validate_prebuild_receipt(row: dict[str, object], private_root: Path) -> None:
    if row.get("passed") is not True:
        raise RuntimeError("runner prebuild did not pass")
    if row.get("buildInvocationCount") != 1:
        raise RuntimeError("runner prebuild did not execute exactly one build")
    if row.get("compilerOwnedProcessCount") != 0:
        raise RuntimeError("runner prebuild compiler census is not zero")
    cleanup_receipt = row.get("compilerCleanup")
    if (not isinstance(cleanup_receipt, dict)
            or cleanup_receipt.get("cleanupConfirmed") is not True
            or cleanup_receipt.get("ownedProcessCount") != 0
            or cleanup_receipt.get("residue") != []
            or not isinstance(cleanup_receipt.get("capturedDescendants"), list)):
        raise RuntimeError("runner prebuild descendant cleanup receipt is incomplete")
    before_cleanup = cleanup_receipt.get("jobAccountingBeforeCleanup")
    after_cleanup = cleanup_receipt.get("jobAccountingAfterCleanup")
    if (cleanup_receipt.get("ownershipMode") != "windows-job-object-before-resume"
            or cleanup_receipt.get("jobAssignedBeforeResume") is not True
            or cleanup_receipt.get("jobClosed") is not True
            or not isinstance(before_cleanup, dict)
            or not isinstance(before_cleanup.get("totalProcesses"), int)
            or before_cleanup["totalProcesses"] < 1
            or before_cleanup["totalProcesses"] != len(cleanup_receipt["capturedDescendants"])
            or not isinstance(after_cleanup, dict)
            or after_cleanup.get("activeProcesses") != 0):
        raise RuntimeError("runner prebuild kernel job ownership/zero receipt is incomplete")
    captured_processes = cleanup_receipt["capturedDescendants"]
    build_process_id = row.get("buildProcessId")
    captured_ids: set[int] = set()
    for identity in captured_processes:
        if not isinstance(identity, dict):
            raise RuntimeError("runner prebuild captured process identity is malformed")
        process_id = identity.get("processId")
        if (not isinstance(process_id, int) or process_id <= 0 or process_id in captured_ids
                or not isinstance(identity.get("parentProcessId"), int)
                or not str(identity.get("startedAtUtc", "")).strip()
                or not str(identity.get("executablePath", "")).strip()
                or identity.get("role") not in {"buildRoot", "buildDescendant"}):
            raise RuntimeError("runner prebuild captured process identity is incomplete")
        captured_ids.add(process_id)
    if not isinstance(build_process_id, int) or build_process_id not in captured_ids:
        raise RuntimeError("runner prebuild root process is absent from the cleanup receipt")
    if row.get("exitCode") != 0 or row.get("timedOut") is not False:
        raise RuntimeError("runner prebuild exit/deadline receipt is not successful")
    elapsed = row.get("totalElapsedSeconds")
    if not isinstance(elapsed, (int, float)) or elapsed < 0 or elapsed > PREBUILD_SAFETY_BOUND_SECONDS:
        raise RuntimeError("runner prebuild total generation/build/cleanup safety bound failed")
    phases = row.get("phaseTimestampsUtc")
    phase_names = (
        "generationStarted", "generationCompleted", "buildStarted",
        "buildCompleted", "compilerCleanupCompleted",
    )
    if not isinstance(phases, dict) or any(not str(phases.get(name, "")) for name in phase_names):
        raise RuntimeError("runner prebuild phase timestamps are incomplete")
    try:
        parsed_phases = [dt.datetime.fromisoformat(str(phases[name]).replace("Z", "+00:00"))
                         for name in phase_names]
    except ValueError as exc:
        raise RuntimeError("runner prebuild phase timestamp is invalid") from exc
    if any(left > right for left, right in zip(parsed_phases, parsed_phases[1:])):
        raise RuntimeError("runner prebuild phase timestamps are not ordered")
    sdk = row.get("sdkIdentity")
    if (not isinstance(sdk, dict) or not str(sdk.get("hostPath", "")).strip()
            or not str(sdk.get("version", "")).strip()
            or not str(sdk.get("hostSha256", "")).strip()):
        raise RuntimeError("runner prebuild SDK identity is absent")
    sdk_host = Path(str(sdk["hostPath"]))
    if not sdk_host.is_file() or _sha256(sdk_host) != sdk["hostSha256"]:
        raise RuntimeError("runner prebuild SDK host identity drifted")
    command = [str(value).casefold() for value in row.get("command", [])]
    if len(command) < 2 or command[:2] != ["dotnet", "build"]:
        raise RuntimeError("runner prebuild command is not the single allowed build")
    if "--no-restore" not in command:
        raise RuntimeError("runner prebuild did not disable restore")
    if any(value in {"run", "restore"} for value in command):
        raise RuntimeError("runner prebuild used a forbidden run or restore command")
    required_files = (
        ("sourcePath", "sourceSha256", True),
        ("projectPath", "projectSha256", True),
        ("dllPath", "dllSha256", True),
        ("runtimeConfigPath", "runtimeConfigSha256", True),
        ("depsPath", "depsSha256", True),
        ("receiptPath", "receiptSha256", True),
    )
    for path_key, hash_key, must_be_private in required_files:
        path = Path(str(row.get(path_key, ""))).resolve()
        if (must_be_private and not _is_under(path, private_root.resolve())) or not path.is_file():
            raise RuntimeError(f"runner prebuild {path_key} is absent or outside the pair root")
        if _sha256(path) != row.get(hash_key):
            raise RuntimeError(f"runner prebuild {path_key} hash receipt mismatch")
    dependencies = row.get("dependencyInputs")
    if not isinstance(dependencies, list) or not dependencies:
        raise RuntimeError("runner prebuild dependency input receipt is absent")
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            raise RuntimeError("runner prebuild dependency input receipt is malformed")
        path = Path(str(dependency.get("path", "")))
        if not path.is_file() or _sha256(path) != dependency.get("sha256"):
            raise RuntimeError("runner prebuild dependency input hash mismatch")
    output_root = Path(str(row["dllPath"])).resolve().parent
    outputs = row.get("runnerOutputFiles")
    if not isinstance(outputs, list) or not outputs:
        raise RuntimeError("runner prebuild output-set receipt is absent")
    expected_outputs: dict[str, str] = {}
    for output in outputs:
        if not isinstance(output, dict):
            raise RuntimeError("runner prebuild output-set receipt is malformed")
        relative = str(output.get("relativePath", ""))
        path = (output_root / relative).resolve()
        if not _is_under(path, output_root) or not path.is_file():
            raise RuntimeError("runner prebuild output-set path escaped or disappeared")
        if _sha256(path) != output.get("sha256"):
            raise RuntimeError("runner prebuild output-set hash mismatch")
        expected_outputs[relative] = str(output["sha256"])
    actual_outputs = {
        path.relative_to(output_root).as_posix(): _sha256(path)
        for path in output_root.rglob("*") if path.is_file()
    }
    if actual_outputs != expected_outputs:
        raise RuntimeError("runner prebuild output set drifted")


def _revalidate_prebuild_receipt(row: dict[str, object], private_root: Path) -> None:
    _validate_prebuild_receipt(row, private_root)


class _MODULEENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD), ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD), ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD), ("modBaseAddr", ctypes.POINTER(ctypes.c_ubyte)),
        ("modBaseSize", wintypes.DWORD), ("hModule", wintypes.HMODULE),
        ("szModule", wintypes.WCHAR * 256), ("szExePath", wintypes.WCHAR * 260),
    ]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("ki", _KEYBDINPUT), ("padding", ctypes.c_byte * 32)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", _INPUTUNION)]


class Win32NativeApi:
    """Minimal Win32 backend.  Construction is inert; methods are live actions."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise RuntimeError("walker runtime observation requires Windows")
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
        self.kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.kernel32.OpenProcess.restype = wintypes.HANDLE
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        self.kernel32.ReadProcessMemory.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
        ]
        self.kernel32.ReadProcessMemory.restype = wintypes.BOOL
        self.kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        self.kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        self.kernel32.Module32FirstW.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(_MODULEENTRY32W)
        ]
        self.kernel32.Module32FirstW.restype = wintypes.BOOL
        self.kernel32.QueryFullProcessImageNameW.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)
        ]
        self.kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.kernel32.GetProcessTimes.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
        ]
        self.kernel32.GetProcessTimes.restype = wintypes.BOOL
        self.kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        self.kernel32.LocalFree.restype = ctypes.c_void_p
        self.user32.IsWindow.argtypes = [wintypes.HWND]
        self.user32.IsWindow.restype = wintypes.BOOL
        self.user32.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND, ctypes.POINTER(wintypes.DWORD)
        ]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.user32.GetForegroundWindow.argtypes = []
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        self.user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        self.user32.SetForegroundWindow.restype = wintypes.BOOL
        self.user32.BringWindowToTop.argtypes = [wintypes.HWND]
        self.user32.BringWindowToTop.restype = wintypes.BOOL
        self.user32.SetFocus.argtypes = [wintypes.HWND]
        self.user32.SetFocus.restype = wintypes.HWND
        self.user32.AttachThreadInput.argtypes = [
            wintypes.DWORD, wintypes.DWORD, wintypes.BOOL
        ]
        self.user32.AttachThreadInput.restype = wintypes.BOOL
        self.kernel32.GetCurrentThreadId.argtypes = []
        self.kernel32.GetCurrentThreadId.restype = wintypes.DWORD
        self.user32.SendInput.argtypes = [
            wintypes.UINT, ctypes.POINTER(_INPUT), ctypes.c_int
        ]
        self.user32.SendInput.restype = wintypes.UINT
        self.ntdll.NtQueryInformationProcess.argtypes = [
            wintypes.HANDLE, wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG,
            ctypes.POINTER(wintypes.ULONG),
        ]
        self.ntdll.NtQueryInformationProcess.restype = wintypes.LONG

    def open_process(self, pid: int, access: int) -> int:
        if access != PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ:
            raise RuntimeError("refusing non-read-only process access mask")
        handle = self.kernel32.OpenProcess(access, False, pid)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        return int(handle)

    def close_handle(self, handle: int) -> None:
        if not self.kernel32.CloseHandle(wintypes.HANDLE(handle)):
            raise ctypes.WinError(ctypes.get_last_error())

    def read_process_memory(self, handle: int, address: int, size: int) -> bytes:
        buffer = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t()
        ok = self.kernel32.ReadProcessMemory(
            wintypes.HANDLE(handle), ctypes.c_void_p(address), buffer, size, ctypes.byref(read)
        )
        if not ok:
            raise ctypes.WinError(ctypes.get_last_error())
        return buffer.raw[:read.value]

    def _read_pointer(self, handle: int, address: int, width: int) -> int:
        return int.from_bytes(self.read_process_memory(handle, address, width), "little")

    def _read_unicode(self, handle: int, address: int, width: int) -> str:
        header = self.read_process_memory(handle, address, 4 if width == 4 else 8)
        length = int.from_bytes(header[:2], "little")
        if length & 1 or length > 32766:
            raise RuntimeError("remote UNICODE_STRING length is invalid")
        pointer = self._read_pointer(handle, address + (4 if width == 4 else 8), width)
        if length == 0:
            return ""
        if pointer == 0:
            raise RuntimeError("remote UNICODE_STRING buffer is null")
        return self.read_process_memory(handle, pointer, length).decode("utf-16-le")

    def _process_parameters(self, handle: int) -> tuple[str, tuple[str, ...]]:
        wow64_peb = ctypes.c_void_p()
        returned = wintypes.ULONG()
        status = self.ntdll.NtQueryInformationProcess(
            wintypes.HANDLE(handle), 26, ctypes.byref(wow64_peb), ctypes.sizeof(wow64_peb),
            ctypes.byref(returned),
        )
        if status == 0 and wow64_peb.value:
            width, peb = 4, int(wow64_peb.value)
        else:
            class PBI(ctypes.Structure):
                _fields_ = [("Reserved1", ctypes.c_void_p), ("PebBaseAddress", ctypes.c_void_p),
                            ("Reserved2", ctypes.c_void_p * 2), ("UniqueProcessId", ctypes.c_void_p),
                            ("Reserved3", ctypes.c_void_p)]
            value = PBI()
            status = self.ntdll.NtQueryInformationProcess(
                wintypes.HANDLE(handle), 0, ctypes.byref(value), ctypes.sizeof(value),
                ctypes.byref(returned),
            )
            if status != 0 or not value.PebBaseAddress:
                raise RuntimeError(f"NtQueryInformationProcess failed: 0x{status & 0xffffffff:08x}")
            width, peb = ctypes.sizeof(ctypes.c_void_p), int(value.PebBaseAddress)
        parameters = self._read_pointer(handle, peb + (0x10 if width == 4 else 0x20), width)
        working = self._read_unicode(handle, parameters + (0x24 if width == 4 else 0x38), width)
        command = self._read_unicode(handle, parameters + (0x40 if width == 4 else 0x70), width)
        arguments = tuple(self._parse_windows_command_line(command)[1:])
        return str(Path(working).resolve()), arguments

    def _parse_windows_command_line(self, command: str) -> list[str]:
        shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        argc = ctypes.c_int()
        shell32.CommandLineToArgvW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
        shell32.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
        argv = shell32.CommandLineToArgvW(command, ctypes.byref(argc))
        if not argv:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return [argv[index] for index in range(argc.value)]
        finally:
            self.kernel32.LocalFree(ctypes.cast(argv, ctypes.c_void_p))

    def _module(self, pid: int) -> tuple[str, int, int]:
        snapshot = self.kernel32.CreateToolhelp32Snapshot(
            TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid
        )
        if int(snapshot) == INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            row = _MODULEENTRY32W()
            row.dwSize = ctypes.sizeof(row)
            if not self.kernel32.Module32FirstW(snapshot, ctypes.byref(row)):
                raise ctypes.WinError(ctypes.get_last_error())
            module_base = ctypes.cast(row.modBaseAddr, ctypes.c_void_p).value
            if not module_base:
                raise RuntimeError("live main module has a null base address")
            return str(Path(row.szExePath).resolve()), int(module_base), int(row.modBaseSize)
        finally:
            self.kernel32.CloseHandle(snapshot)

    def _executable_path(self, handle: int) -> str:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not self.kernel32.QueryFullProcessImageNameW(
            wintypes.HANDLE(handle), 0, buffer, ctypes.byref(size)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return str(Path(buffer.value).resolve())

    def _started_at(self, handle: int) -> dt.datetime:
        creation = wintypes.FILETIME()
        exit_time = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        if not self.kernel32.GetProcessTimes(
            wintypes.HANDLE(handle), ctypes.byref(creation), ctypes.byref(exit_time),
            ctypes.byref(kernel), ctypes.byref(user)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        ticks = (int(creation.dwHighDateTime) << 32) | int(creation.dwLowDateTime)
        unix_100ns = ticks - 116444736000000000
        return dt.datetime.fromtimestamp(unix_100ns / 10_000_000, tz=dt.timezone.utc)

    @staticmethod
    def _parse_receipt_start(value: str) -> dt.datetime:
        text = value.strip().replace("Z", "+00:00")
        if "." in text:
            prefix, suffix = text.split(".", 1)
            fraction, zone = suffix.split("+", 1) if "+" in suffix else (suffix, "00:00")
            text = f"{prefix}.{fraction[:6].ljust(6, '0')}+{zone}"
        parsed = dt.datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            raise RuntimeError("receipt process start time lacks a timezone")
        return parsed.astimezone(dt.timezone.utc)

    def current_identity(self, handle: int, expected: sampler.ReceiptIdentity) -> sampler.ReceiptIdentity:
        executable = self._executable_path(handle)
        started = self._started_at(handle)
        expected_started = self._parse_receipt_start(expected.started_at_utc)
        if abs((started - expected_started).total_seconds()) > 0.001:
            raise RuntimeError("process creation/start time changed")
        working, arguments = self._process_parameters(handle)
        module_path, module_base, module_size = self._module(expected.process_id)
        pid = wintypes.DWORD()
        if not self.user32.IsWindow(wintypes.HWND(expected.window_handle)):
            raise RuntimeError("receipt HWND no longer exists")
        self.user32.GetWindowThreadProcessId(wintypes.HWND(expected.window_handle), ctypes.byref(pid))
        if working.casefold() != str(Path(expected.module_path).parent).casefold():
            raise RuntimeError("process working directory changed")
        if executable.casefold() != expected.module_path.casefold():
            raise RuntimeError("process executable path changed")
        return sampler.replace_receipt(
            expected,
            module_path=module_path,
            module_base=module_base,
            module_size=module_size,
            window_process_id=int(pid.value),
            launch_arguments=arguments,
        )

    def foreground_window(self) -> int:
        return int(self.user32.GetForegroundWindow() or 0)

    def force_foreground(self, hwnd: int) -> bool:
        if hwnd <= 0 or not self.user32.IsWindow(wintypes.HWND(hwnd)):
            return False
        if int(self.user32.GetForegroundWindow() or 0) == hwnd:
            return True
        # AttachThreadInput dance: SetForegroundWindow is restricted after the
        # adapter process starts and steals focus from the C# harness.
        current = self.kernel32.GetCurrentThreadId()
        target_tid = self.user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), None)
        attached = False
        if target_tid and target_tid != current:
            attached = bool(self.user32.AttachThreadInput(current, target_tid, True))
        try:
            self.user32.BringWindowToTop(wintypes.HWND(hwnd))
            self.user32.SetForegroundWindow(wintypes.HWND(hwnd))
            self.user32.SetFocus(wintypes.HWND(hwnd))
        finally:
            if attached:
                self.user32.AttachThreadInput(current, target_tid, False)
        return int(self.user32.GetForegroundWindow() or 0) == hwnd

    def send_scan_code(self, scan_code: int, key_up: bool) -> int:
        # Emit both virtual-key and scan-code forms. Some DirectInput paths
        # ignore pure KEYEVENTF_SCANCODE events from a foreign process.
        flags_up = KEYEVENTF_KEYUP if key_up else 0
        events = (
            _INPUT(
                type=1,
                union=_INPUTUNION(
                    ki=_KEYBDINPUT(Q_VIRTUAL_KEY, scan_code, flags_up, 0, 0)
                ),
            ),
            _INPUT(
                type=1,
                union=_INPUTUNION(
                    ki=_KEYBDINPUT(
                        0, scan_code, KEYEVENTF_SCANCODE | flags_up, 0, 0
                    )
                ),
            ),
        )
        array_type = _INPUT * len(events)
        payload = array_type(*events)
        sent = self.user32.SendInput(len(events), payload, ctypes.sizeof(_INPUT))
        return int(sent)


def _sample_batches(reader: ReceiptPinnedReader, guard: ReceiptRuntimeGuard,
                    clock: QpcClock, module_base: int, phase: str, origin: int,
                    phase_offset: int, deadline: Deadline,
                    *, vehicle: str = sampler.VEHICLE_WALKER) -> list[sampler.RawSample]:
    rows: list[sampler.RawSample] = []
    step = sampler.cadence_step_qpc(clock.frequency)
    count = sampler.PHASE_TARGETS[phase]
    for batch_start in range(0, count, BATCH_SIZE):
        deadline.check(phase)
        if not guard.revalidate_receipt() or not guard.foreground_matches():
            raise sampler.AttemptError("receipt or foreground changed around sampling batch")
        for slot in range(batch_start, min(batch_start + BATCH_SIZE, count)):
            target = origin + (phase_offset + slot) * step
            # Stamp the schedule tick at wait completion, before RPM work that
            # can burn most of a 10 ms cadence on a cold chain walk.
            tick = clock.wait_until(target)
            deadline.check(phase)
            rows.append(sampler.read_coherent_sample(
                reader, module_base, tick=tick, phase=phase, slot=slot, vehicle=vehicle
            ))
        if not guard.revalidate_receipt() or not guard.foreground_matches():
            raise sampler.AttemptError("receipt or foreground changed around sampling batch")
        deadline.check(phase)
    return rows


def collect_trace(attempt: int, receipt: sampler.ReceiptIdentity, receipt_path: Path,
                  reader: ReceiptPinnedReader, native: NativeApi, clock: QpcClock,
                  deadline: Deadline, authorized_private_root: Path,
                  *, vehicle: str = sampler.VEHICLE_WALKER) -> tuple[sampler.AttemptTrace, dict[str, object]]:
    if reader.handle is None:
        raise RuntimeError("observer handle is not open")
    guard = ReceiptRuntimeGuard(
        receipt, receipt_path, receipt.receipt_sha256, native, reader.handle,
        authorized_private_root,
    )
    # Live Q is owned by the C# harness (ExternalHarnessQInput). Direct Python
    # SendInput left control==0 and static positions on pairs 09-12.
    q_input = ExternalHarnessQInput(authorized_private_root)
    readiness_deadline = Deadline(READINESS_DEADLINE_SECONDS)
    if not native.force_foreground(receipt.window_handle):
        raise sampler.AttemptError("could not foreground BEA before readiness")
    readiness = wait_for_runtime_readiness(
        lambda: sampler.read_readiness_probe(reader, receipt.module_base),
        guard,
        deadline_check=lambda: (
            deadline.check("observer readiness"),
            readiness_deadline.check("readiness"),
        ),
    )
    if vehicle == sampler.VEHICLE_JET:
        # Level 850 boots walker; Transform (bound to T) morphs into jet.
        if not _marker_handshake(authorized_private_root, "morph", timeout_seconds=8.0):
            raise sampler.AttemptError("morph Transform handshake was not confirmed")
        morph_deadline = time.time() + 25.0
        seen_states: set[int] = set()
        consecutive_jet = 0
        while time.time() < morph_deadline:
            deadline.check("jet morph")
            if not guard.revalidate_receipt() or not guard.foreground_matches():
                raise sampler.AttemptError("receipt or foreground changed during jet morph")
            try:
                # Poll state via walker chain without requiring state==WALKER so
                # morphing (1) and jet (3) remain readable mid-transition.
                probe = sampler.read_coherent_sample(
                    reader, receipt.module_base, tick=clock.now(), phase="baseline",
                    slot=0, vehicle=sampler.VEHICLE_WALKER, require_walker_state=False,
                )
                seen_states.add(int(probe.state_raw))
                if probe.state_raw == sampler.JET_STATE_RAW:
                    consecutive_jet += 1
                else:
                    consecutive_jet = 0
                if consecutive_jet >= 5:
                    readiness = dict(readiness)
                    readiness["vehicle"] = "jet"
                    readiness["stateRaw"] = probe.state_raw
                    readiness["morphStatesSeen"] = sorted(seen_states)
                    break
            except sampler.SampleError:
                consecutive_jet = 0
            time.sleep(0.05)
        else:
            raise sampler.AttemptError(
                "battle engine did not enter jet state after morph; "
                f"states_seen={sorted(seen_states)}"
            )
    if not native.force_foreground(receipt.window_handle):
        raise sampler.AttemptError("could not foreground BEA before Q sampling")
    # Each phase uses a fresh origin. External Q handshakes take seconds; if hold
    # targets stay anchored to pre-Q origin every wait_until returns immediately
    # and the hold window collapses to a few hundred ms with control still 0.
    baseline_origin = clock.now()
    deadline.check("baseline")
    baseline = _sample_batches(
        reader, guard, clock, receipt.module_base, "baseline", baseline_origin, 0, deadline,
        vehicle=vehicle,
    )
    hold_callbacks = []
    hold_rows: list[sampler.RawSample] = []
    step = sampler.cadence_step_qpc(clock.frequency)
    hold_origin_box: list[int] = []
    # Effective key-down edge is when control proves, not when the external
    # handshake finished (handshake + control wait can exceed 250 ms).
    control_edge_box: list[int] = []
    for batch_start in range(0, sampler.PHASE_TARGETS["hold"], BATCH_SIZE):
        def batch(start=batch_start):
            deadline.check("hold")
            if not hold_origin_box:
                # First batch runs only after Q-down inside execute_owned_q_window.
                # Wait until the control store proves Forward before the hold
                # origin so residual settle and late KeyDown delivery do not
                # collapse the steady window to friction decay of a one-shot.
                control_wait_deadline = time.time() + 8.0
                proved = False
                while time.time() < control_wait_deadline:
                    deadline.check("hold")
                    if not guard.revalidate_receipt() or not guard.foreground_matches():
                        raise sampler.AttemptError(
                            "receipt or foreground changed while waiting for Q forward control"
                        )
                    probe_tick = clock.now()
                    probe = sampler.read_coherent_sample(
                        reader, receipt.module_base, tick=probe_tick, phase="hold", slot=0,
                        vehicle=vehicle,
                    )
                    if probe.control_raw == sampler.FORWARD_CONTROL_RAW:
                        proved = True
                        control_edge_box.append(probe_tick)
                        break
                    time.sleep(0.02)
                if not proved:
                    raise sampler.AttemptError(
                        "control field did not enter forward/thrust state after Q-down"
                    )
                hold_origin_box.append(clock.now())
            hold_origin = hold_origin_box[0]
            rows = []
            for slot in range(start, min(start + BATCH_SIZE, sampler.PHASE_TARGETS["hold"])):
                target = hold_origin + slot * step
                tick = clock.wait_until(target)
                deadline.check("hold")
                rows.append(sampler.read_coherent_sample(
                    reader, receipt.module_base, tick=tick, phase="hold", slot=slot,
                    vehicle=vehicle,
                ))
            hold_rows.extend(rows)
            deadline.check("hold")
            return rows
        hold_callbacks.append(batch)
    window = execute_deadlined_q_batches(
        guard, q_input, clock.now, hold_callbacks, lambda: deadline.check("hold")
    )
    release_origin = clock.now()
    release = _sample_batches(
        reader, guard, clock, receipt.module_base, "release", release_origin, 0, deadline,
        vehicle=vehicle,
    )
    run_digest = hashlib.sha256(
        (receipt.receipt_sha256 + str(attempt) + str(baseline_origin)).encode("ascii")
    ).hexdigest()
    down_bracket = window.down_bracket
    if control_edge_box:
        # Latency is measured from control-store prove (input path confirmation),
        # not from the multi-second external handshake start.
        edge = control_edge_box[0]
        down_bracket = (max(0, edge - step), edge)
    # key_up may sleep before the OS up edge; bind release latency to the
    # completed up edge only.
    up_after = window.up_bracket[1]
    up_bracket = (max(0, up_after - step), up_after)
    trace = sampler.AttemptTrace(
        attempt=attempt,
        receipt_sha256=receipt.receipt_sha256,
        run_digest=run_digest,
        frequency=clock.frequency,
        samples={"baseline": baseline, "hold": hold_rows, "release": release},
        down_bracket=down_bracket,
        up_bracket=up_bracket,
        integrity=sampler.AttemptIntegrity(cleanup_confirmed=False),
    )
    return trace, readiness


def _trace_payload(trace: sampler.AttemptTrace, q_input_nonclaim: str) -> dict[str, object]:
    def row(value: sampler.RawSample) -> dict[str, object]:
        return {
            "tick": value.tick, "phase": value.phase, "slot": value.slot,
            "position": list(value.position), "velocity": list(value.velocity),
            "stateRaw": value.state_raw, "controlRaw": value.control_raw,
        }
    return {
        "schemaVersion": "battleengine-walker-trajectory-private-raw.v1",
        "attempt": trace.attempt,
        "receiptSha256": trace.receipt_sha256,
        "runDigest": trace.run_digest,
        "qpcFrequency": trace.frequency,
        "downBracket": list(trace.down_bracket), "upBracket": list(trace.up_bracket),
        "samples": {phase: [row(value) for value in rows] for phase, rows in trace.samples.items()},
        "observerHandleClosed": False,
        "publicProjectionWritten": False,
        "interferenceNonclaim": q_input_nonclaim,
    }


def analyze_provisional_trace(trace: sampler.AttemptTrace) -> sampler.AttemptMetrics:
    """Run the integrated sampler; AppCore cleanup remains a separate final gate."""
    provisional = replace(
        trace,
        integrity=replace(trace.integrity, cleanup_confirmed=True),
    )
    return sampler.analyze_attempt(provisional)


def _metrics_payload(metrics: sampler.AttemptMetrics) -> dict[str, object]:
    return {
        "schemaVersion": "battleengine-walker-trajectory-private-metrics.v1",
        "attempt": metrics.attempt,
        "acceptedBySamplerBeforeAppCoreCleanup": metrics.accepted,
        "metrics": asdict(metrics),
        "calibrationTarget": {
            "sourceNamedPath": "CWalker::Forward -> CWalker::Move scalar response",
            "steamLinkedObservation": "receipt-bound player-0 BattleEngine walker forward response",
            "scope": "latency, acceleration shape, steady scalar speed, and release only",
            "nonclaim": "does not establish directional handling or broader First Flight parity",
        },
        "publicProjectionWritten": False,
    }


def _write_new_json(path: Path, value: object) -> None:
    require_absent_outputs((path,))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def run_observer(args: argparse.Namespace) -> int:
    authorized_root = Path(os.path.abspath(args.authorized_private_root))
    receipt_path = _authorize_private_path(
        Path(args.receipt), authorized_root, label="receipt path"
    )
    raw_path = _authorize_private_path(
        Path(args.raw_output), authorized_root, label="raw output path"
    )
    metrics_path = _authorize_private_path(
        Path(args.metrics_output), authorized_root, label="metrics output path"
    )
    status_path = _authorize_private_path(
        Path(args.status_output), authorized_root, label="status output path"
    )
    require_absent_outputs((raw_path, metrics_path, status_path))
    receipt = load_receipt(
        receipt_path, args.expected_receipt_sha256,
        authorized_private_root=authorized_root,
    )
    native = Win32NativeApi()
    reader = ReceiptPinnedReader(receipt, native)
    failure = ""
    trace = None
    metrics = None
    readiness: dict[str, object] = {"status": "not-ready"}
    q_up_confirmed = False
    deadline = Deadline(OBSERVER_DEADLINE_SECONDS)
    try:
        deadline.check()
        reader.open()
        deadline.check()
        vehicle = getattr(args, "vehicle", sampler.VEHICLE_WALKER) or sampler.VEHICLE_WALKER
        if vehicle not in (sampler.VEHICLE_WALKER, sampler.VEHICLE_JET):
            raise ValueError("vehicle must be walker or jet")
        trace, readiness = collect_trace(
            args.attempt, receipt, receipt_path, reader, native, QpcClock(), deadline,
            authorized_root, vehicle=vehicle,
        )
        deadline.check()
        # collect_trace only returns after execute_owned_q_window confirms key-up.
        # Analysis acceptance is independent; cleanup must still see observer Q-up
        # so a failed attempt can free the pair for attempt two.
        q_up_confirmed = True
        # Persist raw samples before analysis so failed control/schedule gates
        # still leave private evidence for the next tooling fix.
        _write_new_json(raw_path, _trace_payload(trace, INTERFERENCE_NONCLAIM))
        metrics = analyze_provisional_trace(trace)
        _write_new_json(metrics_path, _metrics_payload(metrics))
    except BaseException as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            reader.close()
        except BaseException as exc:
            failure = failure or f"{type(exc).__name__}: {exc}"
        try:
            deadline.check("observer cleanup")
        except BaseException as exc:
            failure = failure or f"{type(exc).__name__}: {exc}"
    _write_new_json(status_path, {
        "schemaVersion": "battleengine-walker-trajectory-private-observer-status.v1",
        "attempt": args.attempt,
        "receiptSha256": receipt.receipt_sha256,
        "qUpConfirmed": q_up_confirmed,
        "observerHandleClosed": reader.closed,
        "samplerAccepted": metrics is not None and metrics.accepted,
        "failure": failure,
        "readiness": readiness,
        "publicProjectionWritten": False,
        "interferenceNonclaim": INTERFERENCE_NONCLAIM,
    })
    return 0 if not failure and trace is not None and metrics is not None and reader.closed else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest="mode", required=True)
    observer = sub.add_parser("observe-one", allow_abbrev=False)
    observer.add_argument("--attempt", type=int, required=True, choices=(1, 2))
    observer.add_argument("--receipt", required=True)
    observer.add_argument("--expected-receipt-sha256", required=True)
    observer.add_argument("--raw-output", required=True)
    observer.add_argument("--metrics-output", required=True)
    observer.add_argument("--status-output", required=True)
    observer.add_argument("--authorized-private-root", required=True)
    observer.add_argument(
        "--vehicle",
        choices=(sampler.VEHICLE_WALKER, sampler.VEHICLE_JET),
        default=sampler.VEHICLE_WALKER,
        help="Vehicle mode for sample state/control chain (default walker).",
    )
    pair = sub.add_parser("run-two", allow_abbrev=False)
    pair.add_argument("--source-root", required=True)
    pair.add_argument("--exe-override", required=True)
    pair.add_argument("--private-root", required=True)
    pair.add_argument("--authorized-private-root", required=True)
    pair.add_argument("--arm-live-bea", required=True)
    pair.add_argument(
        "--vehicle",
        choices=(sampler.VEHICLE_WALKER, sampler.VEHICLE_JET),
        default=sampler.VEHICLE_WALKER,
        help="Vehicle mode: walker (default) or jet (morph + thrust scalar).",
    )
    return parser


def _load_smoke_module():
    path = ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"
    spec = importlib.util.spec_from_file_location("walker_live_smoke", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the hash-bound AppCore runner generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _prebuild_smoke(private_root: Path) -> dict[str, object]:
    smoke = _load_smoke_module()
    return smoke.prebuild_walker_runner(
        private_root, compiler_cleanup=smoke.receipt_owned_compiler_cleanup
    )


def _write_cooperative_stop_request(path: Path, reason: str) -> None:
    with path.open("x", encoding="ascii", newline="\n") as stream:
        stream.write(reason + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _communicate_with_phase_deadlines(
    process: subprocess.Popen[str], evidence_root: Path, stop_request: Path,
    *, aggregate_remaining_seconds: float, monotonic: Callable[[], float] = time.monotonic,
) -> tuple[str, str, str | None]:
    """Signal the lifecycle owner while a bounded synchronous phase is still blocked."""
    attempt_started = monotonic()
    attempt_limit = min(float(aggregate_remaining_seconds), COMPLETE_ATTEMPT_BUDGET_SECONDS)
    phase_limits = {
        "profile": PROFILE_PREPARATION_BOUND_SECONDS,
        "launch": LAUNCH_RECEIPT_FOCUS_BOUND_SECONDS,
    }
    phase_started: dict[str, float] = {}
    stop_reason: str | None = None
    while True:
        now = monotonic()
        for phase in phase_limits:
            started_marker = evidence_root / f"walker-phase-{phase}-started.marker"
            completed_marker = evidence_root / f"walker-phase-{phase}-completed.marker"
            if phase not in phase_started and started_marker.is_file():
                phase_started[phase] = now
            if (stop_reason is None and phase in phase_started and not completed_marker.is_file()
                    and now - phase_started[phase] >= phase_limits[phase]):
                stop_reason = f"walker {phase} phase exceeded its {phase_limits[phase]}-second safety bound"
        if stop_reason is None and now - attempt_started >= attempt_limit:
            stop_reason = "walker attempt exceeded its fixed 215-second cooperative decision deadline"
        if stop_reason is not None and not stop_request.exists():
            _write_cooperative_stop_request(stop_request, stop_reason)
        try:
            stdout, stderr = process.communicate(timeout=0.10)
            return stdout, stderr, stop_reason
        except subprocess.TimeoutExpired:
            continue


def _invoke_smoke(args: argparse.Namespace, attempt: int, profile_root: Path,
                  evidence_root: Path, runner: dict[str, object],
                  remaining_seconds: float) -> dict[str, object]:
    stop_request = Path(str(runner["receiptPath"])).parent / f"attempt-{attempt:02d}-cooperative-stop.request"
    require_absent_outputs((stop_request,))
    command = [
        sys.executable, str(ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"),
        "--runtime-protocol", WALKER_PROTOCOL,
        "--walker-attempt", str(attempt),
        "--walker-prebuilt-runner-dll", str(runner["dllPath"]),
        "--expected-walker-prebuilt-runner-sha256", str(runner["dllSha256"]),
        "--walker-prebuild-receipt", str(runner["receiptPath"]),
        "--expected-walker-prebuild-receipt-sha256", str(runner["receiptSha256"]),
        "--walker-cooperative-stop-file", str(stop_request),
        "--walker-attempt-budget-seconds", str(COMPLETE_ATTEMPT_BUDGET_SECONDS),
        "--walker-deadline-seconds", str(OBSERVER_DEADLINE_SECONDS),
        "--source-root", str(Path(args.source_root).resolve()),
        "--exe-override", str(Path(args.exe_override).resolve()),
        "--profiles-root", str(profile_root),
        "--artifact-root", str(evidence_root),
        "--arm-external-artifact-root", "ALLOW EXTERNAL LIVE SMOKE ARTIFACT ROOT",
        "--arm-external-profiles-root", "ALLOW EXTERNAL LIVE SMOKE PROFILES ROOT",
        "--arm-live-bea", args.arm_live_bea,
        "--timeout-seconds", "20",
    ]
    env = os.environ.copy()
    vehicle = getattr(args, "vehicle", sampler.VEHICLE_WALKER) or sampler.VEHICLE_WALKER
    env["ONSLAUGHT_LIVE_WALKER_VEHICLE"] = vehicle
    started = time.monotonic()
    process = subprocess.Popen(
        command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=env,
    )
    stdout, stderr, stop_reason = _communicate_with_phase_deadlines(
        process, evidence_root, stop_request,
        aggregate_remaining_seconds=remaining_seconds,
    )
    stop_requested = stop_reason is not None
    completed = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    closeout_path = evidence_root / "walker-trajectory-attempt-closeout.json"
    if not closeout_path.is_file():
        raise RuntimeError(
            f"attempt {attempt} AppCore harness exit {completed.returncode} did not write "
            f"the cleanup closeout: {completed.stderr.strip()}"
        )
    row = json.loads(closeout_path.read_text(encoding="utf-8"))
    row["outerElapsedSeconds"] = time.monotonic() - started
    row["cooperativeStopRequested"] = stop_requested
    row["cooperativeStopReason"] = stop_reason
    row["harnessExitCode"] = completed.returncode
    return row


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "observe-one":
        return run_observer(args)
    result = run_two_attempts(
        Path(os.path.abspath(args.private_root)),
        lambda attempt, profile, evidence, runner, remaining: _invoke_smoke(
            args, attempt, profile, evidence, runner, remaining
        ),
        authorized_private_root=Path(os.path.abspath(args.authorized_private_root)),
        prebuild=_prebuild_smoke,
    )
    closeout = _authorize_private_path(
        Path(args.private_root) / "two-attempt-closeout.json",
        Path(args.authorized_private_root),
        label="pair closeout path",
    )
    _write_new_json(closeout, result)
    print(json.dumps({"privateCloseout": str(closeout), "pairEligible": result["pairEligible"]}))
    return 0 if result["pairEligible"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
