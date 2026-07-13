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
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from typing import Callable, Protocol, Sequence

import battleengine_walker_trajectory_sampler as sampler


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = Path(__file__).resolve()
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
FORBIDDEN_PROCESS_RIGHTS = 0x0002 | 0x0008 | 0x0020 | 0x0400
Q_SCAN_CODE = 0x10
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
BATCH_SIZE = 5
OBSERVER_DEADLINE_SECONDS = 15
PAIR_DEADLINE_SECONDS = 120
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
        while True:
            now = self.now()
            remaining = (target - now) / self.frequency
            if remaining <= 0:
                return now
            if remaining > 0.002:
                time.sleep(max(0.0, remaining - 0.001))
            else:
                time.sleep(0)


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
    def __init__(self, native: NativeApi) -> None:
        self.native = native
        self.events: list[tuple[int, bool]] = []
        self.down_confirmed = False
        self.up_confirmed = False

    def key_down(self) -> bool:
        if self.events:
            raise RuntimeError("Q input permits exactly one key-down and one key-up")
        confirmed = self.native.send_scan_code(Q_SCAN_CODE, False) == 1
        self.events.append((Q_SCAN_CODE, False))
        self.down_confirmed = confirmed
        return confirmed

    def key_up(self) -> bool:
        if self.events != [(Q_SCAN_CODE, False)]:
            raise RuntimeError("Q input permits exactly one key-down and one key-up")
        confirmed = self.native.send_scan_code(Q_SCAN_CODE, True) == 1
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
    receipt_path = Path(str(row.get("receiptPath", "")))
    digest = str(row.get("receiptSha256", ""))
    if not _is_under(receipt_path, evidence_root) or not receipt_path.is_file():
        raise RuntimeError("attempt receipt escaped its fresh evidence root")
    if _sha256(receipt_path) != digest:
        raise RuntimeError("attempt receipt byte integrity failed")
    cleanup_ok = (
        row.get("qUpConfirmed") is True
        and row.get("observerHandleClosed") is True
        and row.get("managedProcessStopped") is True
        and row.get("ownedProcessCount") == 0
        and row.get("sourceUnchanged") is True
        and row.get("copyUnchanged") is True
    )
    if not cleanup_ok:
        raise RuntimeError("attempt cleanup gate failed; refusing another attempt")


def run_two_attempts(
    private_root: Path,
    invoke: Callable[[int, Path, Path], dict[str, object]],
    *,
    authorized_private_root: Path,
) -> dict[str, object]:
    """Run at most two attempts and never materialize a public projection."""
    private_root = _authorize_private_path(
        private_root, authorized_private_root, label="two-attempt private root"
    )
    if private_root.exists() or private_root.is_symlink():
        raise ValueError("private two-attempt root already exists")
    private_root.mkdir(parents=True)
    deadline = time.monotonic() + PAIR_DEADLINE_SECONDS
    rows: list[dict[str, object]] = []
    receipt_paths: set[str] = set()
    receipt_digests: set[str] = set()
    for attempt in (1, 2):
        if time.monotonic() >= deadline:
            raise AttemptDeadlineExceeded("two-attempt deadline expired")
        attempt_root = private_root / f"attempt-{attempt:02d}"
        profile_root = (
            attempt_root / "profile-app-config" / "OnslaughtCareerEditor" / "GameProfiles"
        )
        evidence_root = attempt_root / "evidence"
        require_absent_outputs((attempt_root, profile_root, evidence_root))
        row = invoke(attempt, profile_root, evidence_root)
        _validate_closeout(row, attempt, evidence_root)
        receipt_path = str(Path(str(row["receiptPath"])).resolve())
        receipt_digest = str(row["receiptSha256"])
        if receipt_path in receipt_paths or receipt_digest in receipt_digests:
            raise RuntimeError("attempt did not produce a fresh receipt")
        receipt_paths.add(receipt_path)
        receipt_digests.add(receipt_digest)
        rows.append(row)
    pair_eligible = len(rows) == 2 and all(row.get("accepted") is True for row in rows)
    return {
        "schemaVersion": "battleengine-walker-trajectory-private-pair-closeout.v1",
        "attempts": rows,
        "pairEligible": pair_eligible,
        "publicProjectionWritten": False,
        "interferenceNonclaim": INTERFERENCE_NONCLAIM,
    }


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

    def send_scan_code(self, scan_code: int, key_up: bool) -> int:
        flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if key_up else 0)
        value = _INPUT(type=1, union=_INPUTUNION(ki=_KEYBDINPUT(0, scan_code, flags, 0, 0)))
        sent = self.user32.SendInput(1, ctypes.byref(value), ctypes.sizeof(value))
        return int(sent)


def _sample_batches(reader: ReceiptPinnedReader, guard: ReceiptRuntimeGuard,
                    clock: QpcClock, module_base: int, phase: str, origin: int,
                    phase_offset: int, deadline: Deadline) -> list[sampler.RawSample]:
    rows: list[sampler.RawSample] = []
    step = round(clock.frequency * sampler.CADENCE_MS / 1000)
    count = sampler.PHASE_TARGETS[phase]
    for batch_start in range(0, count, BATCH_SIZE):
        deadline.check(phase)
        if not guard.revalidate_receipt() or not guard.foreground_matches():
            raise sampler.AttemptError("receipt or foreground changed around sampling batch")
        for slot in range(batch_start, min(batch_start + BATCH_SIZE, count)):
            target = origin + (phase_offset + slot) * step
            clock.wait_until(target)
            deadline.check(phase)
            rows.append(sampler.read_coherent_sample(
                reader, module_base, tick=clock.now(), phase=phase, slot=slot
            ))
        if not guard.revalidate_receipt() or not guard.foreground_matches():
            raise sampler.AttemptError("receipt or foreground changed around sampling batch")
        deadline.check(phase)
    return rows


def collect_trace(attempt: int, receipt: sampler.ReceiptIdentity, receipt_path: Path,
                  reader: ReceiptPinnedReader, native: NativeApi, clock: QpcClock,
                  deadline: Deadline, authorized_private_root: Path) -> sampler.AttemptTrace:
    if reader.handle is None:
        raise RuntimeError("observer handle is not open")
    guard = ReceiptRuntimeGuard(
        receipt, receipt_path, receipt.receipt_sha256, native, reader.handle,
        authorized_private_root,
    )
    q_input = ScanCodeQInput(native)
    origin = clock.now()
    deadline.check("baseline")
    baseline = _sample_batches(
        reader, guard, clock, receipt.module_base, "baseline", origin, 0, deadline
    )
    hold_callbacks = []
    hold_rows: list[sampler.RawSample] = []
    step = round(clock.frequency * sampler.CADENCE_MS / 1000)
    clock.wait_until(origin + sampler.PHASE_TARGETS["baseline"] * step)
    for batch_start in range(0, sampler.PHASE_TARGETS["hold"], BATCH_SIZE):
        def batch(start=batch_start):
            deadline.check("hold")
            rows = []
            for slot in range(start, min(start + BATCH_SIZE, sampler.PHASE_TARGETS["hold"])):
                target = origin + (sampler.PHASE_TARGETS["baseline"] + slot) * step
                clock.wait_until(target)
                deadline.check("hold")
                rows.append(sampler.read_coherent_sample(
                    reader, receipt.module_base, tick=clock.now(), phase="hold", slot=slot
                ))
            hold_rows.extend(rows)
            deadline.check("hold")
            return rows
        hold_callbacks.append(batch)
    window = execute_deadlined_q_batches(
        guard, q_input, clock.now, hold_callbacks, lambda: deadline.check("hold")
    )
    release_offset = sampler.PHASE_TARGETS["baseline"] + sampler.PHASE_TARGETS["hold"]
    release = _sample_batches(
        reader, guard, clock, receipt.module_base, "release", origin, release_offset, deadline
    )
    run_digest = hashlib.sha256(
        (receipt.receipt_sha256 + str(attempt) + str(origin)).encode("ascii")
    ).hexdigest()
    return sampler.AttemptTrace(
        attempt=attempt,
        receipt_sha256=receipt.receipt_sha256,
        run_digest=run_digest,
        frequency=clock.frequency,
        samples={"baseline": baseline, "hold": hold_rows, "release": release},
        down_bracket=window.down_bracket,
        up_bracket=window.up_bracket,
        integrity=sampler.AttemptIntegrity(cleanup_confirmed=False),
    )


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
    q_up_confirmed = False
    deadline = Deadline(OBSERVER_DEADLINE_SECONDS)
    try:
        deadline.check()
        reader.open()
        deadline.check()
        trace = collect_trace(
            args.attempt, receipt, receipt_path, reader, native, QpcClock(), deadline,
            authorized_root,
        )
        deadline.check()
        metrics = analyze_provisional_trace(trace)
        q_up_confirmed = True
        _write_new_json(raw_path, _trace_payload(trace, INTERFERENCE_NONCLAIM))
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
    pair = sub.add_parser("run-two", allow_abbrev=False)
    pair.add_argument("--source-root", required=True)
    pair.add_argument("--exe-override", required=True)
    pair.add_argument("--private-root", required=True)
    pair.add_argument("--authorized-private-root", required=True)
    pair.add_argument("--arm-live-bea", required=True)
    return parser


def _invoke_smoke(args: argparse.Namespace, attempt: int, profile_root: Path,
                  evidence_root: Path) -> dict[str, object]:
    command = [
        sys.executable, str(ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"),
        "--runtime-protocol", WALKER_PROTOCOL,
        "--walker-attempt", str(attempt),
        "--source-root", str(Path(args.source_root).resolve()),
        "--exe-override", str(Path(args.exe_override).resolve()),
        "--profiles-root", str(profile_root),
        "--artifact-root", str(evidence_root),
        "--arm-external-artifact-root", "ALLOW EXTERNAL LIVE SMOKE ARTIFACT ROOT",
        "--arm-external-profiles-root", "ALLOW EXTERNAL LIVE SMOKE PROFILES ROOT",
        "--arm-live-bea", args.arm_live_bea,
        "--timeout-seconds", "12",
    ]
    started = time.monotonic()
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"attempt {attempt} AppCore harness failed with exit {completed.returncode}: "
            f"{completed.stderr.strip()}"
        )
    closeout_path = evidence_root / "walker-trajectory-attempt-closeout.json"
    if not closeout_path.is_file():
        raise RuntimeError("AppCore harness did not write the private attempt closeout")
    row = json.loads(closeout_path.read_text(encoding="utf-8"))
    row["outerElapsedSeconds"] = time.monotonic() - started
    return row


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "observe-one":
        return run_observer(args)
    result = run_two_attempts(
        Path(os.path.abspath(args.private_root)),
        lambda attempt, profile, evidence: _invoke_smoke(args, attempt, profile, evidence),
        authorized_private_root=Path(os.path.abspath(args.authorized_private_root)),
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
