#!/usr/bin/env python3
"""Historical owner for exact Ghidra function-body-envelope proofs.

The tracked CLI is retired and refusal-only. Database-level replay requires a
catalog-guided restore plus the exact frozen owner sealed with the old READY.

This owner is intentionally narrower than live promotion.  It freezes every
input, creates independent scratch clones of the observed40 project, exercises
probe/refutation/receipt-failure controls, and accepts persistence only after a
new read-only Ghidra process reproduces the expected inventory.  It never
accepts or opens the maintainer Ghidra project.
"""

from __future__ import annotations

import argparse
import base64
import csv
import ctypes
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable

from ctypes import wintypes


SCHEMA = "bea.re.ghidra-function-body-envelope-proof.v1"
JAVA_READY_SCHEMA = "bea-ghidra-function-body-envelope.v3"
BACKUP_SCHEMA = "onslaught-ghidra-project-backup.v2"

PROGRAM_NAME = "BEA.exe"
PROJECT_NAME = "BEA"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
IMAGE_BASE = "0x00400000"
LANGUAGE = "x86:LE:32:default"
COMPILER_SPEC = "windows"
TARGET_ENTRY = "0x00542710"
FORBIDDEN_TAIL_ENTRY = "0x00542720"

BASE_PROJECT_FILE_COUNT = 19
BASE_PROJECT_TOTAL_BYTES = 186010501
BASE_PROJECT_FILE_SET_SHA256 = (
    "74db2e939d91046114e767334a55582936eb8c791b8ae3572ad3618658e85717"
)
BASE_FUNCTIONS_SHA256 = (
    "26977c69e3530ff9344c6456b3a0dac218775eaf0c1043ac2c89c6a9b95ab368"
)
BASE_PROGRAM_SHA256 = (
    "eaf62f346c0c0efebb629bef775f519882bfad0aaa61917929d5fda6805c43ad"
)
BASE_FUNCTION_COUNT = 7595
BASE_INSTRUCTION_COUNT = 549864
BASE_MEMORY_SHA256 = (
    "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d"
)
BASE_INSTRUCTION_LAYOUT_SHA256 = (
    "321948029747cdfa1eb7098b0069b3226b80feccbda7b7e6315dad13e2a7d37c"
)

EXPECTED_TOOL_SHA256 = {
    "envelope": "f8a2b456c30969d6b7af480f391f340748db8db65771f239d925b4d0b4ef1201",
    "inventory": "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    "backup": "36969a237eef29fea0daa52fe4a657127bdbbb5091523c9ca7cd92c69566b452",
    "diff": "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460",
}
EXPECTED_TOOL_NAMES = {
    "envelope": "CreateFunctionsFromBoundaryManifest.java",
    "inventory": "ExportFullFunctionInventory.java",
    "backup": "ghidra_project_backup.py",
    "diff": "ghidra_inventory_diff.py",
}
CANARY_MANIFEST_SHA256 = (
    "1ed6b4a39048eedde56e8419bdb346ba37d212f1546c0b28fa8dd1401d589a09"
)
POISON_MANIFEST_SHA256 = (
    "5490532bf95136ee496b3796f514b3ac90e5ef493be7d23187d42f17739218aa"
)
OBSERVED40_READY_SHA256 = (
    "2bd58c84cb0ea907bab22f13cc4bb2a236a403aa12c8409d9c53b7e6b3a62999"
)
CANARY_REFUTATION_READY_SHA256 = (
    "1687e97eae0e2e7e52f70879fbfaf822ca029d942e0793d483751bbcaf300473"
)
BOUNDARY_READY_SHA256 = (
    "53ab9de5bc113ad45d593f3732627860f2639c819d21c771d8369d139a4c6832"
)

ANALYZE_HEADLESS_SHA256 = (
    "dd7b9d17d32ed70a71df82a43a21cdaed6c4ce67064e30f8642c149f81c2ae07"
)
GHIDRA_APPLICATION_PROPERTIES_SHA256 = (
    "80890f309379ef60ecbb376a95448bd79e874145544ffcfabb5ba1835ac8a2cf"
)
HOST_JAVA_SHA256 = (
    "5f6248f9c0f32b38ffaba813819bf3331536a48c7ddc45b18e73acd15a6cf7ef"
)
PYTHON_SHA256 = (
    "fda7026477256845afab371e354c4d512896665f1761939cb5887d0a9dec257a"
)
WINDOWS_COMMAND_PROCESSOR_SHA256 = (
    "8dd1ebb0b969370c70a5ee7f7ee347949aa7046aa5e1a33fcd7b1e9415b21fc3"
)
GHIDRA_DISTRIBUTION = (5226, 914252158, "5e80e03104d22011ff89429d39d2a83d7e5e56dae6e7e6b0fa2d4c08e674500c")
JDK_DISTRIBUTION = (490, 343604705, "af26450b182c8d085ed3efcae7bb3068f1e002b53f2db2f4111910cb455b39bf")
PYTHON_DISTRIBUTION = (11683, 533160307, "e43602c0684213f4fb9e1f1c8de2d38cef55345e9ab7a6b061a0e34b1b131d7e")

CANARY_RANGES = "0x00542710-0x0054271a;0x00542720-0x00542736"
CANARY_BODY_BYTES = "32"
CANARY_RANGE_DIGEST = "f0f8f544b4fc3bdad54cb818a519db949906caf2b798bf0a5cdee84f96f1f2b3"
CANARY_BODY_SHA256 = "cdc88702c69f4171d35d7aa3d4283ef7f788c74dfe7873783496e7e3572f7356"
CANARY_INSTRUCTIONS = "9"
CANARY_RESIDUALS = (
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x00542710-0x0054271A;"
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x00542720-0x00542736"
)
CANARY_QUESTIONS = "Q-7761c6831ebefdbc;Q-e5cfa080a5190045"
CANARY_CONTRACTS = "C-115326b7fef5eebd;C-23cfea59e0f92403"
CANARY_LANE = "PROSPECTIVE_TWO_RANGE_CANARY"
MANIFEST_HEADER = (
    "entry\texpectedRanges\texpectedBodyBytes\texpectedRangeDigest"
    "\texpectedBodyBytesSha256\texpectedInstructionCount\texpectedIsThunk"
    "\texpectedThunkTarget\tforbiddenEntries\tresidualEntityKeys\tquestionIds"
    "\tcontractIds\tpromotionLane"
)

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
CLAIM_BOUNDARY = (
    "This proves only the exact natural Ghidra envelope and manifest-bound function kind for 0x00542710 on two disposable post-observed40 clone pairs.",
    "Java transaction fields are provisional. Probe rollback, poison rollback, receipt-failure rollback, apply persistence, and readback are accepted only from separate reopened processes and full inventories.",
    "No semantic name, signature, behavior contract, batch520 authority, live maintainer-project mutation, or rebuild parity claim follows from this canary alone.",
    "The full inventory is a strong exported semantic boundary, not a digest of every possible Ghidra database record.",
    "This is unsigned machine-local evidence for a trusted quiescent host; it is not portable, hostile-actor-resistant, or proof that the run preceded a historical mutation.",
)
COLD_PACKAGE_PARENT = Path("/srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31")
HISTORICAL_RETIREMENT_MESSAGE = (
    "this tracked function-envelope owner is a frozen Windows-era one-shot and "
    "its bound main-project, poison-project, and retained replica databases are "
    "no longer live inputs. Locate their aliases in a package catalog under "
    f"{COLD_PACKAGE_PARENT}, restore every required tree to fresh empty paths, "
    "and execute the exact frozen owner recorded beside the historical READY; "
    "never substitute the active mutable Linux Ghidra project"
)


class ProofError(ValueError):
    """Raised when the proof cannot satisfy an exact gate."""


class _JobBasicLimitInformation(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class _JobExtendedLimitInformation(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _JobBasicLimitInformation),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _create_kill_on_close_job() -> int:
    if os.name != "nt":
        raise ProofError("Ghidra proof process containment requires Windows")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise ProofError(f"CreateJobObjectW failed: {ctypes.get_last_error()}")
    information = _JobExtendedLimitInformation()
    information.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        job,
        JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
        ctypes.byref(information),
        ctypes.sizeof(information),
    ):
        error = ctypes.get_last_error()
        kernel32.CloseHandle(job)
        raise ProofError(f"SetInformationJobObject failed: {error}")
    return int(job)


def _close_handle(handle: int) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if handle and not kernel32.CloseHandle(wintypes.HANDLE(handle)):
        raise ProofError(f"CloseHandle failed: {ctypes.get_last_error()}")


def _assign_process_to_job(job: int, process: subprocess.Popen) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    process_handle = int(process._handle)  # CPython Windows Popen handle
    if not kernel32.AssignProcessToJobObject(wintypes.HANDLE(job), wintypes.HANDLE(process_handle)):
        raise ProofError(f"AssignProcessToJobObject failed: {ctypes.get_last_error()}")


def _job_child(encoded_argv: str) -> int:
    try:
        decoded = base64.urlsafe_b64decode(encoded_argv.encode("ascii"))
        argv = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProofError("job child argv is malformed") from exc
    if (
        not isinstance(argv, list)
        or not argv
        or any(not isinstance(value, str) or not value for value in argv)
    ):
        raise ProofError("job child argv must be a nonempty string list")
    if sys.stdin.buffer.read(1) != b"G":
        raise ProofError("job child launch gate was not released")
    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL)
    return child.wait()


def _spawn_contained_process(
    argv: list[str], cwd: Path, environment: dict[str, str]
) -> tuple[subprocess.Popen, int]:
    encoded = base64.urlsafe_b64encode(
        json.dumps(argv, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    helper = [
        str(Path(sys.executable).resolve()),
        "-I",
        "-B",
        str(Path(__file__).resolve()),
        "--_job-child",
        encoded,
    ]
    process = subprocess.Popen(
        helper,
        cwd=cwd,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=CREATE_NO_WINDOW,
    )
    job = _create_kill_on_close_job()
    try:
        _assign_process_to_job(job, process)
        assert process.stdin is not None
        process.stdin.write(b"G")
        process.stdin.flush()
        process.stdin.close()
        process.stdin = None
        return process, job
    except BaseException:
        try:
            _close_handle(job)
        finally:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        raise


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def is_reparse_point(path: Path) -> bool:
    info = path.lstat()
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or is_junction() or bool(attributes & reparse_flag)


def require_plain_existing_ancestors(path: Path, label: str) -> Path:
    path = lexical_absolute(path)
    chain = [path, *path.parents]
    for candidate in reversed(chain):
        if not candidate.exists():
            continue
        if is_reparse_point(candidate):
            raise ProofError(f"{label} has a reparse-point ancestor: {candidate}")
        if candidate != path and not candidate.is_dir():
            raise ProofError(f"{label} has a non-directory ancestor: {candidate}")
    return path


def ensure_plain_directory(path: Path, label: str) -> Path:
    path = require_plain_existing_ancestors(path, label)
    missing: list[Path] = []
    cursor = path
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    if not cursor.is_dir() or is_reparse_point(cursor):
        raise ProofError(f"{label} has no plain existing directory ancestor: {cursor}")
    for directory in reversed(missing):
        try:
            directory.mkdir()
        except FileExistsError:
            pass
        if not directory.is_dir() or is_reparse_point(directory):
            raise ProofError(f"{label} directory creation was redirected: {directory}")
    return require_plain_directory(path, label)


def require_plain_file(path: Path, label: str, *, expected_hash: str | None = None) -> Path:
    path = require_plain_existing_ancestors(path, label)
    if not path.is_file() or is_reparse_point(path):
        raise ProofError(f"{label} is not a plain file: {path}")
    if expected_hash is not None and sha256_file(path) != expected_hash:
        raise ProofError(f"{label} SHA-256 is unsupported: {path}")
    return path


def require_plain_directory(path: Path, label: str) -> Path:
    path = require_plain_existing_ancestors(path, label)
    if not path.is_dir() or is_reparse_point(path):
        raise ProofError(f"{label} is not a plain directory: {path}")
    return path


def write_new(path: Path, content: bytes) -> None:
    path = require_plain_existing_ancestors(path, "new output")
    ensure_plain_directory(path.parent, "new output parent")
    if path.exists() or ":" in path.name:
        raise ProofError(f"refusing to overwrite or use an alternate stream: {path}")
    partial = path.parent / f".{path.name}.partial-{uuid.uuid4().hex}"
    try:
        with partial.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(partial, path)
        except FileExistsError as exc:
            raise ProofError(f"refusing to overwrite existing output: {path}") from exc
    finally:
        partial.unlink(missing_ok=True)


def write_json_new(path: Path, value: object) -> None:
    write_new(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def stamp(path: Path, root: Path) -> dict[str, object]:
    path = require_plain_file(path, "artifact")
    try:
        relative = path.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ProofError(f"artifact escapes proof root: {path}") from exc
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def external_stamp(path: Path) -> dict[str, object]:
    path = require_plain_file(path, "external input")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ProofError(f"{label} is not a JSON object: {path}")
    return value


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def program_metrics(path: Path) -> dict[str, str]:
    rows = read_tsv(path)
    if any(set(row) != {"metric", "value"} for row in rows):
        raise ProofError(f"malformed program inventory: {path}")
    result = {row["metric"]: row["value"] for row in rows}
    if len(result) != len(rows):
        raise ProofError(f"duplicate program inventory metric: {path}")
    return result


def function_rows(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        header = reader.fieldnames
        rows = list(reader)
    if not header or "address" not in header:
        raise ProofError(f"malformed function inventory: {path}")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        address = row.get("address", "")
        if not re.fullmatch(r"0x[0-9a-f]{8}", address) or address in result:
            raise ProofError(f"invalid or duplicate function address in {path}: {address}")
        result[address] = row
    return header, result


def validate_base_inventory(functions_path: Path, program_path: Path) -> None:
    if sha256_file(functions_path) != BASE_FUNCTIONS_SHA256:
        raise ProofError("base functions export differs from post-observed40 authority")
    if sha256_file(program_path) != BASE_PROGRAM_SHA256:
        raise ProofError("base program export differs from post-observed40 authority")
    _, functions = function_rows(functions_path)
    metrics = program_metrics(program_path)
    required = {
        "programName": PROGRAM_NAME,
        "executableMD5": PROGRAM_MD5,
        "executableSHA256": PROGRAM_SHA256,
        "imageBase": IMAGE_BASE,
        "language": LANGUAGE,
        "compilerSpec": COMPILER_SPEC,
        "memorySha256": BASE_MEMORY_SHA256,
        "functions": str(BASE_FUNCTION_COUNT),
        "instructions": str(BASE_INSTRUCTION_COUNT),
        "instructionLayoutSha256": BASE_INSTRUCTION_LAYOUT_SHA256,
    }
    for key, expected in required.items():
        if metrics.get(key) != expected:
            raise ProofError(f"base program metric {key} mismatch")
    if len(functions) != BASE_FUNCTION_COUNT or TARGET_ENTRY in functions or FORBIDDEN_TAIL_ENTRY in functions:
        raise ProofError("base function set is not the exact missing-canary state")


def validate_applied_inventory(
    base_functions_path: Path,
    base_program_path: Path,
    after_functions_path: Path,
    after_program_path: Path,
) -> dict[str, str]:
    base_header, before = function_rows(base_functions_path)
    after_header, after = function_rows(after_functions_path)
    if base_header != after_header:
        raise ProofError("function inventory header changed")
    created = sorted(set(after) - set(before))
    destroyed = sorted(set(before) - set(after))
    if created != [TARGET_ENTRY] or destroyed:
        raise ProofError(f"apply changed wrong function set created={created} destroyed={destroyed}")
    for address, row in before.items():
        if after.get(address) != row:
            raise ProofError(f"preexisting function row changed: {address}")
    if FORBIDDEN_TAIL_ENTRY in after:
        raise ProofError("forbidden tail became a separate function")
    row = after[TARGET_ENTRY]
    expected = {
        "address": TARGET_ENTRY,
        "name": "FUN_00542710",
        "nameSource": "DEFAULT",
        "sigSource": "DEFAULT",
        "bodyBytes": CANARY_BODY_BYTES,
        "bodyMin": TARGET_ENTRY,
        "bodyMax": "0x00542735",
        "bodyRanges": "2",
        "bodyDigest": CANARY_RANGE_DIGEST,
        "instrCount": CANARY_INSTRUCTIONS,
        "isThunk": "false",
        "thunkTarget": "",
        "isExternal": "false",
    }
    for field, value in expected.items():
        if row.get(field) != value:
            raise ProofError(f"created row {field} mismatch expected={value!r} actual={row.get(field)!r}")

    before_metrics = program_metrics(base_program_path)
    after_metrics = program_metrics(after_program_path)
    expected_metrics = dict(before_metrics)
    expected_metrics["functions"] = str(BASE_FUNCTION_COUNT + 1)
    if after_metrics != expected_metrics:
        changed = sorted(k for k in set(before_metrics) | set(after_metrics) if before_metrics.get(k) != after_metrics.get(k))
        raise ProofError(f"program metrics changed outside exact function count: {changed}")
    return row


def canonical_range_digest(ranges: Iterable[tuple[int, int]]) -> str:
    digest = hashlib.sha256()
    for start, end_exclusive in ranges:
        digest.update(f"{start:08x}".encode("ascii"))
        digest.update(b":")
        digest.update(f"{end_exclusive - 1:08x}".encode("ascii"))
        digest.update(b";")
    return digest.hexdigest()


def parse_manifest(path: Path, *, expected_hash: str | None = None) -> tuple[list[str], list[list[str]]]:
    content = path.read_bytes()
    if expected_hash is not None and sha256_bytes(content) != expected_hash:
        raise ProofError(f"manifest SHA-256 mismatch: {path}")
    if b"\r" in content or not content.endswith(b"\n") or content.endswith(b"\n\n"):
        raise ProofError(f"manifest canonical line endings mismatch: {path}")
    lines = content.decode("utf-8").splitlines()
    if not lines or lines[0] != MANIFEST_HEADER:
        raise ProofError(f"manifest header mismatch: {path}")
    rows = [line.split("\t") for line in lines[1:]]
    if not rows or any(len(row) != 13 for row in rows):
        raise ProofError(f"manifest row shape mismatch: {path}")
    return lines[0].split("\t"), rows


def validate_canary_inputs(canary: Path, poison: Path) -> None:
    _, canary_rows = parse_manifest(canary, expected_hash=CANARY_MANIFEST_SHA256)
    _, poison_rows = parse_manifest(poison, expected_hash=POISON_MANIFEST_SHA256)
    if len(canary_rows) != 1 or len(poison_rows) != 1:
        raise ProofError("canary and poison must each contain exactly one row")
    canary_row = canary_rows[0]
    poison_row = poison_rows[0]
    if canary_row[:9] != [
        TARGET_ENTRY,
        CANARY_RANGES,
        CANARY_BODY_BYTES,
        CANARY_RANGE_DIGEST,
        CANARY_BODY_SHA256,
        CANARY_INSTRUCTIONS,
        "false",
        "",
        FORBIDDEN_TAIL_ENTRY,
    ]:
        raise ProofError("canary does not bind the exact ordinary two-range envelope")
    if poison_row[0] != TARGET_ENTRY or poison_row[1] != "0x00542710-0x0054271a" or poison_row[6:9] != ["false", "", FORBIDDEN_TAIL_ENTRY]:
        raise ProofError("poison is not the original one-range ordinary-function hypothesis")


def _control_row(base: list[str], **changes: str) -> list[str]:
    columns = MANIFEST_HEADER.split("\t")
    row = dict(zip(columns, base, strict=True))
    row.update(changes)
    return [row[column] for column in columns]


def build_control_manifests(canary: Path, poison: Path) -> dict[str, bytes]:
    _, canary_rows = parse_manifest(canary, expected_hash=CANARY_MANIFEST_SHA256)
    _, poison_rows = parse_manifest(poison, expected_hash=POISON_MANIFEST_SHA256)
    canary_row = canary_rows[0]
    poison_row = poison_rows[0]

    malformed_header = ("wrong\t" + MANIFEST_HEADER.split("\t", 1)[1] + "\n" + "\t".join(canary_row) + "\n").encode()
    trailing_blank = canary.read_bytes() + b"\n"
    one_byte = _control_row(
        canary_row,
        expectedRanges="0x00542710-0x00542711",
        expectedBodyBytes="1",
        expectedRangeDigest=canonical_range_digest([(0x00542710, 0x00542711)]),
        expectedBodyBytesSha256=sha256_bytes(bytes([0xB9])),
        expectedInstructionCount="1",
        forbiddenEntries="",
        promotionLane="INSTRUCTION_COVERAGE_POISON",
    )
    second_overlap = _control_row(
        canary_row,
        entry=FORBIDDEN_TAIL_ENTRY,
        expectedRanges="0x00542720-0x00542721",
        expectedBodyBytes="1",
        expectedRangeDigest="0" * 64,
        expectedBodyBytesSha256="0" * 64,
        expectedInstructionCount="1",
        expectedIsThunk="false",
        expectedThunkTarget="",
        forbiddenEntries="",
        residualEntityKeys="CONTROL:OVERLAP",
        questionIds="Q-CONTROL-OVERLAP",
        contractIds="C-CONTROL-OVERLAP",
        promotionLane="PAIRWISE_BODY_CONFLICT",
    )
    overlap_first = _control_row(canary_row, forbiddenEntries="")
    forbidden_second = list(second_overlap)
    overlap = (MANIFEST_HEADER + "\n" + "\t".join(overlap_first) + "\n" + "\t".join(second_overlap) + "\n").encode()
    forbidden = (MANIFEST_HEADER + "\n" + "\t".join(poison_row) + "\n" + "\t".join(forbidden_second) + "\n").encode()
    instruction = (MANIFEST_HEADER + "\n" + "\t".join(one_byte) + "\n").encode()
    wrong_thunk_kind = _control_row(
        canary_row,
        expectedIsThunk="true",
        expectedThunkTarget=FORBIDDEN_TAIL_ENTRY,
        promotionLane="WRONG_THUNK_KIND_POISON",
    )
    return {
        "wrong-header.tsv": malformed_header,
        "trailing-blank.tsv": trailing_blank,
        "instruction-coverage.tsv": instruction,
        "pairwise-body-conflict.tsv": overlap,
        "forbidden-target-conflict.tsv": forbidden,
        "wrong-thunk-kind.tsv": (MANIFEST_HEADER + "\n" + "\t".join(wrong_thunk_kind) + "\n").encode(),
    }


def tree_rows(root: Path, *, include: Callable[[Path], bool] | None = None) -> list[tuple[str, int, str]]:
    root = require_plain_directory(root, "tree root")
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if is_reparse_point(path):
            raise ProofError(f"tree contains a reparse point: {path}")
        if not path.is_file() or (include is not None and not include(path)):
            continue
        relative = path.relative_to(root).as_posix()
        rows.append((relative, path.stat().st_size, sha256_file(path)))
    return rows


def canonical_rows(rows: Iterable[tuple[str, int, str]]) -> bytes:
    return b"".join(
        f"{digest}\t{size}\t{relative}\n".encode("utf-8")
        for relative, size, digest in sorted(rows)
    )


def rows_digest(rows: Iterable[tuple[str, int, str]]) -> str:
    return sha256_bytes(canonical_rows(rows))


def project_rows(project_root: Path) -> list[tuple[str, int, str]]:
    project_root = require_plain_directory(project_root, "Ghidra project root")
    gpr = project_root / f"{PROJECT_NAME}.gpr"
    rep = project_root / f"{PROJECT_NAME}.rep"
    require_plain_file(gpr, "Ghidra project file")
    require_plain_directory(rep, "Ghidra repository directory")
    rows = [(gpr.name, gpr.stat().st_size, sha256_file(gpr))]
    for relative, size, digest in tree_rows(rep):
        rows.append((f"{rep.name}/{relative}", size, digest))
    return sorted(rows)


def validate_source_project(project_root: Path) -> list[tuple[str, int, str]]:
    rows = project_rows(project_root)
    if (
        len(rows) != BASE_PROJECT_FILE_COUNT
        or sum(row[1] for row in rows) != BASE_PROJECT_TOTAL_BYTES
        or rows_digest(rows) != BASE_PROJECT_FILE_SET_SHA256
    ):
        raise ProofError("source project is not the exact post-observed40 raw project")
    return rows


def parse_distribution_manifest(path: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    prior = ""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split("\t")
        if len(fields) != 3 or not re.fullmatch(r"[0-9a-f]{64}", fields[0]):
            raise ProofError(f"malformed distribution manifest {path}:{number}")
        try:
            size = int(fields[1])
        except ValueError as exc:
            raise ProofError(f"malformed distribution size {path}:{number}") from exc
        relative = fields[2]
        if size < 0 or not relative or relative <= prior or "\\" in relative:
            raise ProofError(f"noncanonical distribution row {path}:{number}")
        prior = relative
        rows.append((relative, size, fields[0]))
    if sha256_bytes(canonical_rows(rows)) != sha256_file(path):
        raise ProofError(f"distribution manifest is not self-canonical: {path}")
    return rows


def verify_distribution(root: Path, manifest: Path, expected: tuple[int, int, str], label: str) -> dict[str, object]:
    expected_rows = parse_distribution_manifest(manifest)
    count, total_bytes, digest = expected
    if len(expected_rows) != count or sum(row[1] for row in expected_rows) != total_bytes or rows_digest(expected_rows) != digest:
        raise ProofError(f"{label} frozen distribution manifest has wrong identity")
    actual_rows = tree_rows(root)
    if actual_rows != expected_rows:
        raise ProofError(f"{label} distribution differs from frozen manifest")
    return {
        "root": str(root.resolve()),
        "fileCount": count,
        "totalBytes": total_bytes,
        "fileSetSha256": digest,
        "manifest": None,
    }


def validate_external_toolchain(headless: Path, java: Path) -> tuple[Path, Path, Path, Path]:
    headless = require_plain_file(headless, "analyzeHeadless", expected_hash=ANALYZE_HEADLESS_SHA256)
    properties = require_plain_file(
        headless.parent.parent / "Ghidra" / "application.properties",
        "Ghidra application properties",
        expected_hash=GHIDRA_APPLICATION_PROPERTIES_SHA256,
    )
    java = require_plain_file(java, "Java executable", expected_hash=HOST_JAVA_SHA256)
    python = require_plain_file(Path(sys.executable), "Python executable", expected_hash=PYTHON_SHA256)
    return headless, properties, java, python


def expected_sanitized_environment(proof_root: Path, java: Path) -> dict[str, str]:
    windows = Path(os.environ.get("SystemRoot", r"C:\Windows")).resolve()
    system32 = windows / "System32"
    cmd = require_plain_file(
        system32 / "cmd.exe", "Windows command processor", expected_hash=WINDOWS_COMMAND_PROCESSOR_SHA256
    )
    runtime = proof_root.resolve() / "runtime-home"
    return {
        "APPDATA": str(runtime / "roaming"),
        "COMSPEC": str(cmd),
        "JAVA_HOME": str(java.resolve().parent.parent),
        "LOCALAPPDATA": str(runtime / "local"),
        "NoDefaultCurrentDirectoryInExePath": "1",
        "PATH": os.pathsep.join((str(java.parent.resolve()), str(system32), str(windows))),
        "PATHEXT": ".COM;.EXE;.BAT;.CMD",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
        "SystemRoot": str(windows),
        "TEMP": str(runtime / "temp"),
        "TMP": str(runtime / "temp"),
        "USERPROFILE": str(runtime / "profile"),
        "WINDIR": str(windows),
    }


def sanitized_environment(proof_root: Path, java: Path) -> dict[str, str]:
    environment = expected_sanitized_environment(proof_root, java)
    for key in ("APPDATA", "LOCALAPPDATA", "TEMP", "USERPROFILE"):
        ensure_plain_directory(Path(environment[key]), f"runtime {key}")
    settings = Path(environment["APPDATA"]) / "ghidra" / "ghidra_12.1.2_PUBLIC"
    ensure_plain_directory(settings, "Ghidra runtime settings")
    write_new(settings / "java_home.save", f"{Path(environment['JAVA_HOME']).resolve()}\r\n".encode())
    return environment


def windows_batch_argv(headless: Path, arguments: list[str]) -> list[str]:
    cmd = Path(r"C:\Windows\System32\cmd.exe")
    require_plain_file(cmd, "Windows command processor", expected_hash=WINDOWS_COMMAND_PROCESSOR_SHA256)
    values = [str(headless.resolve()), *map(str, arguments)]
    for value in values:
        if not value or re.search(r'[\x00\r\n"&|<>^%()!]', value):
            raise ProofError(f"unsafe headless cmd.exe argument: {value!r}")
    return [str(cmd), "/d", "/s", "/c", "call " + subprocess.list2cmdline(values)]


def run_process(
    *,
    proof_root: Path,
    run_id: str,
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
    timeout_seconds: int = 600,
    during_run: Callable[[threading.Event], None] | None = None,
) -> tuple[dict, str]:
    run_root = proof_root / "runs" / run_id
    if run_root.exists():
        raise ProofError(f"run root already exists: {run_root}")
    ensure_plain_directory(run_root, f"{run_id} run root")
    started = utc_now()
    process, job = _spawn_contained_process(argv, cwd, environment)
    callback_error: BaseException | None = None
    callback_thread: threading.Thread | None = None
    callback_stop = threading.Event()
    if during_run is not None:
        def invoke() -> None:
            nonlocal callback_error
            try:
                during_run(callback_stop)
            except BaseException as exc:  # surfaced after the child terminates
                callback_error = exc
        callback_thread = threading.Thread(target=invoke, name=f"{run_id}-control", daemon=True)
        callback_thread.start()
    timed_out: subprocess.TimeoutExpired | None = None
    try:
        output, _ = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        timed_out = exc
        callback_stop.set()
        _close_handle(job)
        job = 0
        try:
            output, _ = process.communicate(timeout=15)
        except subprocess.TimeoutExpired as kill_exc:
            raise ProofError(f"{run_id} job tree survived kill-on-close") from kill_exc
    finally:
        if job:
            _close_handle(job)
            job = 0
    callback_stop.set()
    if callback_thread is not None:
        callback_thread.join(timeout=15)
        if callback_thread.is_alive():
            raise ProofError(f"{run_id} control thread did not terminate")
        if callback_error is not None and timed_out is None:
            raise ProofError(f"{run_id} control failed: {callback_error}") from callback_error
    if timed_out is not None:
        if process.poll() is None:
            raise ProofError(f"{run_id} contained helper is still alive after timeout")
        raise ProofError(f"{run_id} timed out after {timeout_seconds}s") from timed_out
    text = output.decode("utf-8", errors="replace").replace("\r\n", "\n")
    log_path = run_root / "headless.log"
    write_new(log_path, text.encode("utf-8"))
    result = {
        "id": run_id,
        "startedAtUtc": started,
        "completedAtUtc": utc_now(),
        "argv": argv,
        "cwd": str(cwd.resolve()),
        "environment": environment,
        "exitCode": process.returncode,
        "log": stamp(log_path, proof_root),
    }
    return result, text


def finish_run(proof_root: Path, result: dict, *, verdict: str = "SURVIVED", **observations: object) -> dict:
    result = {**result, "verdict": verdict, "observations": observations}
    receipt = proof_root / "runs" / str(result["id"]) / "run.json"
    write_json_new(receipt, result)
    return {**result, "receipt": stamp(receipt, proof_root)}


def require_log_identity(text: str, prefix: str, tool: Path) -> None:
    expected = f"{prefix} path={tool.resolve()} bytes={tool.stat().st_size} sha256={sha256_file(tool)}"
    if text.count(expected) != 1:
        raise ProofError(f"headless log lacks exact tool identity: {expected}")


def require_clean_success_log(text: str, label: str) -> None:
    for marker in ("REPORT SCRIPT ERROR", "FUNCTION_ENVELOPE_MUTATION_TAINTED", "INVENTORY_FAIL"):
        if marker in text:
            raise ProofError(f"{label} success log contains {marker}")


def inventory_argv(
    headless: Path,
    project_root: Path,
    tool: Path,
    functions: Path,
    program: Path,
) -> list[str]:
    return windows_batch_argv(headless, [
        str(project_root.resolve()), PROJECT_NAME,
        "-process", PROGRAM_NAME, "-readOnly", "-noanalysis",
        "-scriptPath", str(tool.parent.resolve()),
        "-postScript", tool.name, str(functions.resolve()), str(program.resolve()),
    ])


def envelope_argv(
    headless: Path,
    project_root: Path,
    tool: Path,
    manifest: Path,
    supplied_hash: str,
    expected_count: int,
    output: Path,
    ready: Path,
    mode: str,
) -> list[str]:
    arguments = [str(project_root.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME]
    if mode == "readback":
        arguments.append("-readOnly")
    arguments.extend([
        "-noanalysis", "-scriptPath", str(tool.parent.resolve()),
        "-postScript", tool.name, str(manifest.resolve()), supplied_hash,
        str(expected_count), str(output.resolve()), str(ready.resolve()), mode,
    ])
    return windows_batch_argv(headless, arguments)


def backup_argv(python: Path, backup_tool: Path, source: Path, destination: Path) -> list[str]:
    return [
        str(python), "-I", "-B", str(backup_tool), "copy",
        str(source.resolve()), str(destination.resolve()), "--project-name", PROJECT_NAME,
    ]


def diff_argv(python: Path, diff_tool: Path, before: Path, after: Path, output: Path) -> list[str]:
    return [
        str(python), "-I", "-B", str(diff_tool), str(before), str(after),
        "--json", str(output.resolve()), "--sample-created", "10",
    ]


def run_inventory(
    *,
    proof_root: Path,
    run_id: str,
    headless: Path,
    project_root: Path,
    inventory_tool: Path,
    cwd: Path,
    environment: dict[str, str],
) -> tuple[dict, Path, Path]:
    run_root = proof_root / "runs" / run_id
    functions = run_root / "functions.tsv"
    program = run_root / "program.tsv"
    before = project_rows(project_root)
    result, text = run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=inventory_argv(headless, project_root, inventory_tool, functions, program),
        cwd=cwd,
        environment=environment,
    )
    if project_rows(project_root) != before:
        raise ProofError(f"{run_id} changed a read-only project")
    if result["exitCode"] != 0 or not functions.is_file() or not program.is_file():
        raise ProofError(f"{run_id} inventory invocation failed")
    require_clean_success_log(text, run_id)
    require_log_identity(text, "INVENTORY_TOOL_OK", inventory_tool)
    match = re.search(r"INVENTORY_OK functions=(\d+) instructions=(\d+)", text)
    if match is None:
        raise ProofError(f"{run_id} lacks inventory sentinel")
    result = finish_run(
        proof_root,
        result,
        functionCount=int(match.group(1)),
        instructionCount=int(match.group(2)),
        functions=stamp(functions, proof_root),
        program=stamp(program, proof_root),
        projectFileSetSha256=rows_digest(before),
    )
    return result, functions, program


def validate_java_ready(ready_path: Path, output_path: Path, *, mode: str, tool: Path, manifest: Path) -> dict:
    ready = read_json(ready_path, "Java envelope READY")
    if ready.get("schemaVersion") != JAVA_READY_SCHEMA or ready.get("mode") != mode:
        raise ProofError(f"Java READY schema/mode mismatch: {ready_path}")
    if ready.get("program") != {
        "name": PROGRAM_NAME,
        "executableMd5": PROGRAM_MD5,
        "executableSha256": PROGRAM_SHA256,
        "imageBase": IMAGE_BASE,
        "language": LANGUAGE,
        "compilerSpec": COMPILER_SPEC,
    }:
        raise ProofError("Java READY program identity mismatch")
    expected_tool = external_stamp(tool)
    if ready.get("tool") != expected_tool:
        raise ProofError("Java READY tool binding mismatch")
    expected_manifest = external_stamp(manifest)
    expected_manifest["expectedCount"] = 1
    if ready.get("manifest") != expected_manifest:
        raise ProofError("Java READY manifest binding mismatch")
    expected_output = external_stamp(output_path)
    if ready.get("output") != expected_output:
        raise ProofError("Java READY output binding mismatch")
    counts = ready.get("counts")
    expected_counts = {
        "probe": {
            "targets": 1,
            "functionsBefore": BASE_FUNCTION_COUNT,
            "functionsTransient": BASE_FUNCTION_COUNT + 1,
            "functionManagerViewAfterNestedTransaction": BASE_FUNCTION_COUNT + 1,
            "instructionsBefore": BASE_INSTRUCTION_COUNT,
            "instructionsAfter": BASE_INSTRUCTION_COUNT,
        },
        "apply": {
            "targets": 1,
            "functionsBefore": BASE_FUNCTION_COUNT,
            "functionsTransient": BASE_FUNCTION_COUNT + 1,
            "functionManagerViewAfterNestedTransaction": BASE_FUNCTION_COUNT + 1,
            "instructionsBefore": BASE_INSTRUCTION_COUNT,
            "instructionsAfter": BASE_INSTRUCTION_COUNT,
        },
        "readback": {
            "targets": 1,
            "functionsBefore": BASE_FUNCTION_COUNT + 1,
            "functionsTransient": BASE_FUNCTION_COUNT + 1,
            "functionManagerViewAfterNestedTransaction": BASE_FUNCTION_COUNT + 1,
            "instructionsBefore": BASE_INSTRUCTION_COUNT,
            "instructionsAfter": BASE_INSTRUCTION_COUNT,
        },
    }[mode]
    if counts != expected_counts:
        raise ProofError(f"Java READY count view mismatch for {mode}")
    expected_flags = {
        "probe": (False, True, False, False, True),
        "apply": (True, False, False, False, True),
        "readback": (False, False, False, True, False),
    }[mode]
    actual_flags = (
        ready.get("commitRequested"),
        ready.get("rollbackRequested"),
        ready.get("transactionEndReturnedCommitted"),
        ready.get("loadedStateVerified"),
        ready.get("reopenVerificationRequired"),
    )
    if actual_flags != expected_flags:
        raise ProofError(f"Java READY provisional transaction flags mismatch for {mode}")
    if ready.get("namesAuthorized") is not False or ready.get("functionKindsBoundByManifest") is not True or ready.get("loadedOrTransientEnvelopesVerified") is not True:
        raise ProofError("Java READY weakened an envelope authority boundary")
    return ready


def validate_envelope_output(path: Path, *, mode: str) -> dict[str, str]:
    rows = read_tsv(path)
    if len(rows) != 1:
        raise ProofError(f"envelope output has wrong row count: {path}")
    row = rows[0]
    expected = {
        "entry": TARGET_ENTRY,
        "status": {"probe": "probed_rollback_requested", "apply": "created_commit_requested", "readback": "verified"}[mode],
        "name": "FUN_00542710",
        "nameSource": "DEFAULT",
        "expectedRanges": CANARY_RANGES,
        "actualRanges": CANARY_RANGES,
        "expectedBodyBytes": CANARY_BODY_BYTES,
        "actualBodyBytes": CANARY_BODY_BYTES,
        "expectedRangeDigest": CANARY_RANGE_DIGEST,
        "actualRangeDigest": CANARY_RANGE_DIGEST,
        "expectedBodyBytesSha256": CANARY_BODY_SHA256,
        "actualBodyBytesSha256": CANARY_BODY_SHA256,
        "expectedInstructionCount": CANARY_INSTRUCTIONS,
        "actualInstructionCount": CANARY_INSTRUCTIONS,
        "expectedIsThunk": "false",
        "actualIsThunk": "false",
        "expectedThunkTarget": "",
        "actualThunkTarget": "",
        "forbiddenEntries": FORBIDDEN_TAIL_ENTRY,
        "residualEntityKeys": CANARY_RESIDUALS,
        "questionIds": CANARY_QUESTIONS,
        "contractIds": CANARY_CONTRACTS,
        "promotionLane": CANARY_LANE,
    }
    for field, value in expected.items():
        if row.get(field) != value:
            raise ProofError(f"envelope output {field} mismatch for {mode}")
    return row


def publish_receipt_failure_poison(
    output: Path,
    *,
    timeout_seconds: float = 120.0,
    stop_event: threading.Event | None = None,
) -> None:
    """Create the final output after Java stages it but before hard-link publish."""
    sentinel = b"RECEIPT_PUBLICATION_RACE_POISON\n"
    deadline = time.monotonic() + timeout_seconds
    partial_pattern = f".{output.name}.partial-*"
    while time.monotonic() < deadline:
        if stop_event is not None and stop_event.is_set():
            raise ProofError("receipt-race watcher was cancelled")
        if list(output.parent.glob(partial_pattern)):
            try:
                with output.open("xb") as stream:
                    stream.write(sentinel)
                    stream.flush()
                    os.fsync(stream.fileno())
                return
            except FileExistsError:
                if output.read_bytes() == sentinel:
                    return
                raise ProofError("receipt-race target was created by an unexpected writer")
        time.sleep(0.001)
    raise ProofError("receipt-race watcher never observed staged output")


def run_envelope(
    *,
    proof_root: Path,
    run_id: str,
    headless: Path,
    project_root: Path,
    tool: Path,
    manifest: Path,
    expected_count: int,
    mode: str,
    cwd: Path,
    environment: dict[str, str],
    supplied_hash: str | None = None,
    precreate_output: bool = False,
    receipt_failure_race: bool = False,
) -> tuple[dict, Path, Path, str]:
    run_root = proof_root / "runs" / run_id
    output = run_root / "envelopes.tsv"
    ready = run_root / "envelopes.ready.json"
    if precreate_output:
        if run_root.exists():
            raise ProofError(f"logical run root already exists: {run_root}")
        ensure_plain_directory(run_root, f"{run_id} logical run root")
        write_new(output, b"UNMANIFESTED_OUTPUT_POISON\n")
        # run_process owns creation of the run directory, so use a sibling execution id.
        execution_id = f"{run_id}-execution"
    else:
        execution_id = run_id
    manifest_hash = supplied_hash or sha256_file(manifest)
    watcher: Callable[[], None] | None = None
    if receipt_failure_race:
        def race(stop_event: threading.Event) -> None:
            publish_receipt_failure_poison(output, stop_event=stop_event)
        watcher = race
    result, text = run_process(
        proof_root=proof_root,
        run_id=execution_id,
        argv=envelope_argv(
            headless, project_root, tool, manifest, manifest_hash,
            expected_count, output, ready, mode,
        ),
        cwd=cwd,
        environment=environment,
        during_run=watcher,
    )
    if precreate_output:
        # Keep the poison and execution receipt together in the proof graph.
        result["logicalRunRoot"] = str(run_root.resolve())
    if "FUNCTION_ENVELOPE_TOOL_OK" in text:
        require_log_identity(text, "FUNCTION_ENVELOPE_TOOL_OK", tool)
    return result, output, ready, text


def validate_prerequisites(observed_ready: Path, refutation_ready: Path, boundary_ready: Path) -> None:
    for path, expected, label in (
        (observed_ready, OBSERVED40_READY_SHA256, "observed40 READY"),
        (refutation_ready, CANARY_REFUTATION_READY_SHA256, "canary refutation READY"),
        (boundary_ready, BOUNDARY_READY_SHA256, "520 boundary READY"),
    ):
        require_plain_file(path, label, expected_hash=expected)
    observed = read_json(observed_ready, "observed40 READY")
    if (
        observed.get("schema") != "bea.re.ghidra-function-promotion-scratch-proof.v4"
        or observed.get("verdict") != "SURVIVED"
        or observed.get("checks", {}).get("functionsAfter") != BASE_FUNCTION_COUNT
        or observed.get("checks", {}).get("instructionCountAfter") != BASE_INSTRUCTION_COUNT
        or observed.get("projects", {}).get("mainScratch", {}).get("finalFileSetSha256")
        != BASE_PROJECT_FILE_SET_SHA256
    ):
        raise ProofError("observed40 authority does not describe the exact source base")
    refutation = read_json(refutation_ready, "canary refutation READY")
    observation = refutation.get("manualObservation", {})
    observed_body = observation.get("observedBody", {})
    if (
        refutation.get("verdict") != "REFUTED_EXACT_ONE_RESIDUAL_BODY"
        or refutation.get("batchGate") != "BLOCKED_PENDING_NEW_TWO_RANGE_CANARY_AUTHORITY"
        or observed_body.get("bytes") != 32
        or observed_body.get("rangeDigest") != CANARY_RANGE_DIGEST
        or observed_body.get("bytesSha256") != CANARY_BODY_SHA256
        or observed_body.get("instructionCount") != 9
        or observation.get("tailEntryAbsent") is not True
    ):
        raise ProofError("canary refutation does not bind the learned two-range hypothesis")
    boundary = read_json(boundary_ready, "520 boundary READY")
    if (
        boundary.get("schema") != "bea.re.crt-text-residual-boundary-targets.v2"
        or boundary.get("count") != 520
        or boundary.get("selection", {}).get("batchAuthorized") is not False
        or boundary.get("canaryRefutation", {}).get("ready", {}).get("sha256")
        != CANARY_REFUTATION_READY_SHA256
    ):
        raise ProofError("520 boundary is not blocked on this exact canary authority")


def invoke_backup_copy(
    *,
    proof_root: Path,
    run_id: str,
    python: Path,
    backup_tool: Path,
    source: Path,
    destination: Path,
    cwd: Path,
    environment: dict[str, str],
) -> dict:
    argv = backup_argv(python, backup_tool, source, destination)
    before = project_rows(source)
    result, text = run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=argv,
        cwd=cwd,
        environment=environment,
    )
    if result["exitCode"] != 0 or project_rows(source) != before:
        raise ProofError(f"{run_id} backup copy failed or source changed")
    manifest_path = destination / "backup_manifest.json"
    manifest = read_json(manifest_path, "backup copy manifest")
    destination_rows = project_rows(destination)
    if (
        manifest.get("schemaVersion") != BACKUP_SCHEMA
        or manifest.get("sourceStable") is not True
        or manifest.get("copyComparison", {}).get("matches") is not True
        or destination_rows != before
        or rows_digest(destination_rows) != BASE_PROJECT_FILE_SET_SHA256
        or text.strip() != (
            f"project={PROJECT_NAME} Files={BASE_PROJECT_FILE_COUNT} Bytes={BASE_PROJECT_TOTAL_BYTES} "
            "MissingCount=0 ExtraCount=0 SizeDiffCount=0 HashDiffCount=0 ReadOnlyOpen=NOT_RUN"
        )
    ):
        raise ProofError(f"{run_id} backup copy receipt is not exact")
    return finish_run(
        proof_root,
        result,
        sourceProjectFileSetSha256=rows_digest(before),
        destinationProjectFileSetSha256=rows_digest(destination_rows),
        backupManifest=stamp(manifest_path, proof_root),
    )


def run_inventory_diff(
    *,
    proof_root: Path,
    run_id: str,
    python: Path,
    diff_tool: Path,
    before: Path,
    after: Path,
    cwd: Path,
    environment: dict[str, str],
) -> tuple[dict, dict]:
    run_root = proof_root / "runs" / run_id
    output = run_root / "inventory-diff.json"
    argv = diff_argv(python, diff_tool, before, after, output)
    result, text = run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=argv,
        cwd=cwd,
        environment=environment,
    )
    payload = read_json(output, "inventory diff")
    counts = payload.get("counts", {})
    dangerous = payload.get("dangerous", {})
    if (
        result["exitCode"] != 0
        or counts.get("before") != BASE_FUNCTION_COUNT
        or counts.get("after") != BASE_FUNCTION_COUNT + 1
        or counts.get("created") != 1
        or counts.get("destroyed") != 0
        or any(counts.get(key) != 0 for key in (
            "boundsChanged", "callingConvChanged", "instrCountChanged", "namesChanged",
            "noReturnChanged", "paramCountChanged", "returnTypeChanged", "sigSourceChanged",
            "signaturesChanged", "thunkFlagChanged",
        ))
        or any(value not in (0, [], {}) for value in dangerous.values())
        or [row.get("address") for row in payload.get("created", [])] != [TARGET_ENTRY]
    ):
        raise ProofError(f"{run_id} inventory diff is not exact")
    return finish_run(
        proof_root,
        result,
        diff=stamp(output, proof_root),
        stdoutSha256=sha256_bytes(text.encode()),
    ), payload


def require_rejection(
    *,
    proof_root: Path,
    result: dict,
    output: Path,
    ready: Path,
    text: str,
    expected_pattern: str,
    precreated_output: bytes | None = None,
    mutation_tainted: bool = False,
) -> dict:
    if result.get("exitCode") != 0:
        raise ProofError(f"{result.get('id', '<unknown>')} rejection process exit code is not exact")
    if text.count("REPORT SCRIPT ERROR") != 1 or re.search(expected_pattern, text) is None:
        raise ProofError(f"{result['id']} lacks exact rejection: {expected_pattern}")
    if "FUNCTION_ENVELOPE_OK" in text:
        raise ProofError(f"{result['id']} emitted a success sentinel after rejection")
    tainted_present = "FUNCTION_ENVELOPE_MUTATION_TAINTED" in text
    if tainted_present != mutation_tainted:
        raise ProofError(f"{result['id']} mutation-taint classification mismatch")
    if precreated_output is None:
        if output.exists() or ready.exists():
            raise ProofError(f"{result['id']} published an output on rejection")
    else:
        if output.read_bytes() != precreated_output or ready.exists():
            raise ProofError(f"{result['id']} altered the deterministic output poison")
    partials = list(output.parent.glob(f".{output.name}.partial-*")) + list(ready.parent.glob(f".{ready.name}.partial-*"))
    if partials:
        raise ProofError(f"{result['id']} left staged receipt files")
    return finish_run(
        proof_root,
        result,
        verdict="REFUTED",
        expectedPattern=expected_pattern,
        scriptErrorCount=1,
        mutationTainted=mutation_tainted,
        outputPublished=False,
        readyPublished=False,
    )


def run_preflight_controls(
    *,
    proof_root: Path,
    replica: str,
    headless: Path,
    project: Path,
    tool: Path,
    canary: Path,
    controls: dict[str, Path],
    cwd: Path,
    environment: dict[str, str],
) -> list[dict]:
    specifications = [
        ("wrong-hash", canary, 1, "0" * 64, r"manifest sha256 mismatch", False),
        ("wrong-count", canary, 2, None, r"manifest count mismatch expected=2 actual=1", False),
        ("wrong-header", controls["wrong-header.tsv"], 1, None, r"manifest header mismatch", False),
        ("trailing-blank", controls["trailing-blank.tsv"], 1, None, r"manifest has a trailing blank row", False),
        ("instruction-coverage", controls["instruction-coverage.tsv"], 1, None, r"INSTRUCTION_COVERAGE_MISMATCH", False),
        ("pairwise-body-conflict", controls["pairwise-body-conflict.tsv"], 2, None, r"expected function bodies overlap", False),
        ("forbidden-target-conflict", controls["forbidden-target-conflict.tsv"], 2, None, r"forbidden entry is another manifest target", False),
        ("preexisting-output", canary, 1, None, r"output TSV already exists", True),
    ]
    receipts: list[dict] = []
    for name, manifest, count, supplied_hash, pattern, precreate in specifications:
        result, output, ready, text = run_envelope(
            proof_root=proof_root,
            run_id=f"{replica}-control-{name}",
            headless=headless,
            project_root=project,
            tool=tool,
            manifest=manifest,
            expected_count=count,
            mode="probe",
            cwd=cwd,
            environment=environment,
            supplied_hash=supplied_hash,
            precreate_output=precreate,
        )
        poison = b"UNMANIFESTED_OUTPUT_POISON\n" if precreate else None
        receipts.append(require_rejection(
            proof_root=proof_root,
            result=result,
            output=output,
            ready=ready,
            text=text,
            expected_pattern=pattern,
            precreated_output=poison,
        ))
    return receipts


def compare_inventory_to_base(functions: Path, program: Path, base_functions: Path, base_program: Path, label: str) -> None:
    if functions.read_bytes() != base_functions.read_bytes() or program.read_bytes() != base_program.read_bytes():
        raise ProofError(f"{label} reopened semantic inventory differs from baseline")


def run_replica(
    *,
    proof_root: Path,
    replica: str,
    headless: Path,
    python: Path,
    source_project: Path,
    tools: dict[str, Path],
    canary: Path,
    poison: Path,
    controls: dict[str, Path],
    base_functions: Path,
    base_program: Path,
    cwd: Path,
    environment: dict[str, str],
) -> dict:
    control_project = proof_root / "projects" / f"{replica}-control"
    apply_project = proof_root / "projects" / f"{replica}-apply"
    runs: list[dict] = []
    runs.append(invoke_backup_copy(
        proof_root=proof_root, run_id=f"{replica}-copy-control", python=python,
        backup_tool=tools["backup"], source=source_project, destination=control_project,
        cwd=cwd, environment=environment,
    ))
    runs.append(invoke_backup_copy(
        proof_root=proof_root, run_id=f"{replica}-copy-apply", python=python,
        backup_tool=tools["backup"], source=source_project, destination=apply_project,
        cwd=cwd, environment=environment,
    ))

    baseline_run, control_base_functions, control_base_program = run_inventory(
        proof_root=proof_root, run_id=f"{replica}-control-baseline", headless=headless,
        project_root=control_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(control_base_functions, control_base_program, base_functions, base_program, f"{replica} control baseline")
    runs.append(baseline_run)
    runs.extend(run_preflight_controls(
        proof_root=proof_root, replica=replica, headless=headless, project=control_project,
        tool=tools["envelope"], canary=canary, controls=controls, cwd=cwd,
        environment=environment,
    ))

    probe_result, probe_output, probe_ready, probe_text = run_envelope(
        proof_root=proof_root, run_id=f"{replica}-probe", headless=headless,
        project_root=control_project, tool=tools["envelope"], manifest=canary,
        expected_count=1, mode="probe", cwd=cwd, environment=environment,
    )
    if probe_result["exitCode"] != 0 or "FUNCTION_ENVELOPE_OK mode=probe" not in probe_text:
        raise ProofError(f"{replica} valid probe failed")
    require_clean_success_log(probe_text, f"{replica} valid probe")
    probe_row = validate_envelope_output(probe_output, mode="probe")
    probe_java = validate_java_ready(probe_ready, probe_output, mode="probe", tool=tools["envelope"], manifest=canary)
    runs.append(finish_run(
        proof_root, probe_result, output=stamp(probe_output, proof_root), ready=stamp(probe_ready, proof_root),
        row=probe_row, javaReady=probe_java,
    ))
    reopened, reopened_functions, reopened_program = run_inventory(
        proof_root=proof_root, run_id=f"{replica}-probe-reopened", headless=headless,
        project_root=control_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(reopened_functions, reopened_program, base_functions, base_program, f"{replica} probe rollback")
    runs.append(reopened)

    poison_result, poison_output, poison_ready, poison_text = run_envelope(
        proof_root=proof_root, run_id=f"{replica}-one-range-poison", headless=headless,
        project_root=control_project, tool=tools["envelope"], manifest=poison,
        expected_count=1, mode="probe", cwd=cwd, environment=environment,
    )
    exact_poison = (
        r"BODY_ENVELOPE_MISMATCH entry=0x00542710 .*"
        r"expectedRanges=0x00542710-0x0054271a actualRanges="
        r"0x00542710-0x0054271a;0x00542720-0x00542736"
    )
    runs.append(require_rejection(
        proof_root=proof_root, result=poison_result, output=poison_output,
        ready=poison_ready, text=poison_text, expected_pattern=exact_poison,
        mutation_tainted=True,
    ))
    poison_reopened, poison_functions, poison_program = run_inventory(
        proof_root=proof_root, run_id=f"{replica}-poison-reopened", headless=headless,
        project_root=control_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(poison_functions, poison_program, base_functions, base_program, f"{replica} poison rollback")
    runs.append(poison_reopened)

    kind_result, kind_output, kind_ready, kind_text = run_envelope(
        proof_root=proof_root, run_id=f"{replica}-wrong-thunk-kind", headless=headless,
        project_root=control_project, tool=tools["envelope"],
        manifest=controls["wrong-thunk-kind.tsv"], expected_count=1, mode="probe",
        cwd=cwd, environment=environment,
    )
    runs.append(require_rejection(
        proof_root=proof_root, result=kind_result, output=kind_output, ready=kind_ready,
        text=kind_text,
        expected_pattern=r"THUNK_KIND_MISMATCH entry=0x00542710 expected=true actual=false",
        mutation_tainted=True,
    ))
    kind_reopened, kind_functions, kind_program = run_inventory(
        proof_root=proof_root, run_id=f"{replica}-wrong-thunk-kind-reopened", headless=headless,
        project_root=control_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(kind_functions, kind_program, base_functions, base_program, f"{replica} thunk-kind rollback")
    runs.append(kind_reopened)

    race_result, race_output, race_ready, race_text = run_envelope(
        proof_root=proof_root, run_id=f"{replica}-receipt-failure", headless=headless,
        project_root=control_project, tool=tools["envelope"], manifest=canary,
        expected_count=1, mode="apply", cwd=cwd, environment=environment,
        receipt_failure_race=True,
    )
    race_sentinel = b"RECEIPT_PUBLICATION_RACE_POISON\n"
    runs.append(require_rejection(
        proof_root=proof_root, result=race_result, output=race_output, ready=race_ready,
        text=race_text, expected_pattern=r"FileAlreadyExistsException|already exists",
        precreated_output=race_sentinel, mutation_tainted=True,
    ))
    race_reopened, race_functions, race_program = run_inventory(
        proof_root=proof_root, run_id=f"{replica}-receipt-failure-reopened", headless=headless,
        project_root=control_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(race_functions, race_program, base_functions, base_program, f"{replica} receipt-failure rollback")
    runs.append(race_reopened)

    apply_baseline, apply_base_functions, apply_base_program = run_inventory(
        proof_root=proof_root, run_id=f"{replica}-apply-baseline", headless=headless,
        project_root=apply_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(apply_base_functions, apply_base_program, base_functions, base_program, f"{replica} apply baseline")
    runs.append(apply_baseline)
    apply_result, apply_output, apply_ready, apply_text = run_envelope(
        proof_root=proof_root, run_id=f"{replica}-apply", headless=headless,
        project_root=apply_project, tool=tools["envelope"], manifest=canary,
        expected_count=1, mode="apply", cwd=cwd, environment=environment,
    )
    if apply_result["exitCode"] != 0 or "FUNCTION_ENVELOPE_OK mode=apply" not in apply_text:
        raise ProofError(f"{replica} valid apply failed")
    require_clean_success_log(apply_text, f"{replica} valid apply")
    apply_row = validate_envelope_output(apply_output, mode="apply")
    apply_java = validate_java_ready(apply_ready, apply_output, mode="apply", tool=tools["envelope"], manifest=canary)
    runs.append(finish_run(
        proof_root, apply_result, output=stamp(apply_output, proof_root), ready=stamp(apply_ready, proof_root),
        row=apply_row, javaReady=apply_java,
    ))

    readback_result, readback_output, readback_ready, readback_text = run_envelope(
        proof_root=proof_root, run_id=f"{replica}-readback", headless=headless,
        project_root=apply_project, tool=tools["envelope"], manifest=canary,
        expected_count=1, mode="readback", cwd=cwd, environment=environment,
    )
    if readback_result["exitCode"] != 0 or "FUNCTION_ENVELOPE_OK mode=readback" not in readback_text:
        raise ProofError(f"{replica} readback failed")
    require_clean_success_log(readback_text, f"{replica} readback")
    readback_row = validate_envelope_output(readback_output, mode="readback")
    readback_java = validate_java_ready(readback_ready, readback_output, mode="readback", tool=tools["envelope"], manifest=canary)
    runs.append(finish_run(
        proof_root, readback_result, output=stamp(readback_output, proof_root), ready=stamp(readback_ready, proof_root),
        row=readback_row, javaReady=readback_java,
    ))
    if {k: v for k, v in apply_row.items() if k not in {"status", "note"}} != {k: v for k, v in readback_row.items() if k not in {"status", "note"}}:
        raise ProofError(f"{replica} apply/readback envelope rows differ")

    after_run, after_functions, after_program = run_inventory(
        proof_root=proof_root, run_id=f"{replica}-apply-reopened", headless=headless,
        project_root=apply_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    created_row = validate_applied_inventory(base_functions, base_program, after_functions, after_program)
    runs.append(after_run)
    diff_run, _ = run_inventory_diff(
        proof_root=proof_root, run_id=f"{replica}-inventory-diff", python=python,
        diff_tool=tools["diff"], before=base_functions, after=after_functions,
        cwd=cwd, environment=environment,
    )
    runs.append(diff_run)
    return {
        "id": replica,
        "controlProject": str(control_project.resolve()),
        "applyProject": str(apply_project.resolve()),
        "runs": [run["receipt"] for run in runs],
        "probeOutput": stamp(probe_output, proof_root),
        "applyOutput": stamp(apply_output, proof_root),
        "readbackOutput": stamp(readback_output, proof_root),
        "afterFunctions": stamp(after_functions, proof_root),
        "afterProgram": stamp(after_program, proof_root),
        "createdRow": created_row,
        "controlProjectFileSetSha256": rows_digest(project_rows(control_project)),
        "applyProjectFileSetSha256": rows_digest(project_rows(apply_project)),
    }


def snapshot_file(source: Path, destination: Path, *, expected_hash: str | None = None) -> dict[str, object]:
    source = require_plain_file(source, "snapshot source")
    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        content = stream.read()
        after = os.fstat(stream.fileno())
    current = source.stat()
    if not os.path.samestat(before, after) or not os.path.samestat(after, current):
        raise ProofError(f"snapshot source identity changed while held open: {source}")
    digest = sha256_bytes(content)
    if expected_hash is not None and digest != expected_hash:
        raise ProofError(f"snapshot source SHA-256 is unsupported: {source}")
    if len(content) != after.st_size:
        raise ProofError(f"snapshot source size changed while held open: {source}")
    write_new(destination, content)
    if source.stat().st_size != len(content) or sha256_file(source) != digest:
        raise ProofError(f"snapshot source changed immediately after publication: {source}")
    return {
        "source": {"path": str(source), "bytes": len(content), "sha256": digest},
        "snapshot": None,
    }


def artifact_items(proof_root: Path, *, ready_name: str = "proof.ready.json") -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for relative, size, digest in tree_rows(proof_root):
        if relative == ready_name:
            continue
        items.append({"path": relative, "bytes": size, "sha256": digest})
    return items


def verify_artifact_items(proof_root: Path, ready: dict) -> None:
    artifacts = ready.get("artifacts")
    if not isinstance(artifacts, dict) or artifacts.get("canonicalization") != "sorted relative path with exact bytes and SHA-256; READY excluded":
        raise ProofError("READY artifact boundary is malformed")
    expected = artifacts.get("items")
    actual = artifact_items(proof_root)
    if expected != actual or artifacts.get("count") != len(actual):
        raise ProofError("READY artifact set differs from current proof tree")


def validate_frozen_stamp(proof_root: Path, value: object, label: str) -> Path:
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise ProofError(f"{label} stamp is malformed")
    relative = value["path"]
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or ":" in relative
        or relative.startswith("/")
    ):
        raise ProofError(f"{label} path is unsafe")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts) or pure.as_posix() != relative:
        raise ProofError(f"{label} path is not canonical POSIX-relative")
    path = proof_root.joinpath(*pure.parts)
    try:
        path.resolve().relative_to(proof_root.resolve())
    except ValueError as exc:
        raise ProofError(f"{label} resolves outside proof root") from exc
    current = stamp(path, proof_root)
    if current != value:
        raise ProofError(f"{label} stamp mismatch")
    ready_path = proof_root / "proof.ready.json"
    if ready_path.is_file():
        ready = read_json(ready_path, "proof READY artifact membership")
        items = ready.get("artifacts", {}).get("items", [])
        index = {
            item.get("path"): item
            for item in items
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        }
        if len(index) != len(items) or index.get(relative) != value:
            raise ProofError(f"{label} stamp is not an exact READY artifact member")
    return path


def compare_replications(proof_root: Path, first: dict, second: dict) -> None:
    for key in ("probeOutput", "applyOutput", "readbackOutput", "afterFunctions", "afterProgram"):
        first_path = validate_frozen_stamp(proof_root, first[key], f"first {key}")
        second_path = validate_frozen_stamp(proof_root, second[key], f"second {key}")
        if first_path.read_bytes() != second_path.read_bytes():
            raise ProofError(f"replications differ semantically at {key}")
    if first.get("createdRow") != second.get("createdRow"):
        raise ProofError("replications produced different created function rows")


def expected_ready_program() -> dict[str, object]:
    return {
        "name": PROGRAM_NAME,
        "md5": PROGRAM_MD5,
        "sha256": PROGRAM_SHA256,
        "imageBase": IMAGE_BASE,
        "language": LANGUAGE,
        "compilerSpec": COMPILER_SPEC,
    }


def expected_ready_manifest() -> dict[str, object]:
    return {
        "entry": TARGET_ENTRY,
        "ranges": CANARY_RANGES,
        "bodyBytes": int(CANARY_BODY_BYTES),
        "rangeDigest": CANARY_RANGE_DIGEST,
        "bodyBytesSha256": CANARY_BODY_SHA256,
        "instructionCount": int(CANARY_INSTRUCTIONS),
        "expectedIsThunk": False,
        "expectedThunkTarget": "",
        "forbiddenEntry": FORBIDDEN_TAIL_ENTRY,
    }


def expected_ready_checks() -> dict[str, object]:
    return {
        "replicationCount": 2,
        "freshControlClones": 2,
        "freshApplyClones": 2,
        "probeRollbackReopenedExact": True,
        "oneRangePoisonRejectedWithoutOutputsAndReopenedExact": True,
        "wrongThunkKindRejectedWithoutOutputsAndReopenedExact": True,
        "receiptPublicationFailureReopenedExact": True,
        "applyPersistedOnlyOnApplyClones": True,
        "separateProcessReadbackExact": True,
        "preexistingFunctionRowsUnchanged": True,
        "onlyCreatedEntry": TARGET_ENTRY,
        "forbiddenTailAbsent": True,
        "functionKind": "ordinary_non_thunk",
        "replicasSemanticallyEquivalent": True,
        "sourceProjectUnchanged": True,
        "batch520Authorized": False,
        "maintainerProjectOpened": False,
    }


def validate_ready_semantic_shape(ready: dict) -> None:
    expected_top = {
        "schema", "status", "verdict", "program",
        "sourceAuthority", "tools", "toolchain", "manifest", "replicas",
        "checks", "claimBoundary", "artifacts",
    }
    if set(ready) != expected_top:
        raise ProofError("proof READY top-level key set is not exact")
    if (
        ready.get("schema") != SCHEMA
        or ready.get("status") != "READY"
        or ready.get("verdict") != "SURVIVED"
        or ready.get("program") != expected_ready_program()
        or ready.get("manifest") != expected_ready_manifest()
        or ready.get("checks") != expected_ready_checks()
        or ready.get("claimBoundary") != list(CLAIM_BOUNDARY)
    ):
        raise ProofError("proof READY semantic object differs from the exact canary claim")
    source = ready.get("sourceAuthority")
    if not isinstance(source, dict) or set(source) != {
        "projectRoot", "projectFileCount", "projectTotalBytes",
        "projectFileSetSha256", "inputs", "sourceBeforeRun", "sourceAfterRun",
    }:
        raise ProofError("proof READY sourceAuthority shape is not exact")
    if (
        source.get("projectFileCount") != BASE_PROJECT_FILE_COUNT
        or source.get("projectTotalBytes") != BASE_PROJECT_TOTAL_BYTES
        or source.get("projectFileSetSha256") != BASE_PROJECT_FILE_SET_SHA256
        or not isinstance(source.get("projectRoot"), str)
        or not isinstance(source.get("inputs"), dict)
        or set(source["inputs"]) != {
            "observed40.ready.json", "canary-refutation.ready.json",
            "boundary520.ready.json", "canary-two-range.tsv",
            "poison-one-range.tsv", "base-functions.tsv", "base-program.tsv",
        }
    ):
        raise ProofError("proof READY source authority values are not exact")
    for record in source["inputs"].values():
        if not isinstance(record, dict) or set(record) != {"source", "snapshot"}:
            raise ProofError("proof READY input graph record is malformed")
    tools = ready.get("tools")
    if not isinstance(tools, dict) or set(tools) != {*EXPECTED_TOOL_SHA256, "runner"}:
        raise ProofError("proof READY tool key set is not exact")
    for record in tools.values():
        if not isinstance(record, dict) or set(record) != {"source", "snapshot"}:
            raise ProofError("proof READY tool graph record is malformed")
    toolchain = ready.get("toolchain")
    if not isinstance(toolchain, dict) or set(toolchain) != {
        "analyzeHeadless", "applicationProperties", "java", "python",
        "ghidraDistribution", "jdkDistribution", "pythonDistribution",
    }:
        raise ProofError("proof READY toolchain key set is not exact")
    for key in ("analyzeHeadless", "applicationProperties", "java", "python"):
        if not isinstance(toolchain[key], dict) or set(toolchain[key]) != {"path", "bytes", "sha256"}:
            raise ProofError(f"proof READY {key} stamp shape is malformed")
    for key in ("ghidraDistribution", "jdkDistribution", "pythonDistribution"):
        if not isinstance(toolchain[key], dict) or set(toolchain[key]) != {
            "root", "fileCount", "totalBytes", "fileSetSha256", "manifest",
        }:
            raise ProofError(f"proof READY {key} shape is malformed")
    replicas = ready.get("replicas")
    if (
        not isinstance(replicas, list)
        or len(replicas) != 2
        or not all(isinstance(item, dict) for item in replicas)
        or [item.get("id") for item in replicas] != ["replica-a", "replica-b"]
    ):
        raise ProofError("proof READY replica identities are not exact")
    replica_keys = {
        "id", "controlProject", "applyProject", "runs", "probeOutput",
        "applyOutput", "readbackOutput", "afterFunctions", "afterProgram",
        "createdRow", "controlProjectFileSetSha256", "applyProjectFileSetSha256",
    }
    for replica in replicas:
        if set(replica) != replica_keys or not isinstance(replica.get("runs"), list) or len(replica["runs"]) != 24:
            raise ProofError("proof READY replica shape is not exact")
    artifacts = ready.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {"canonicalization", "count", "items"}:
        raise ProofError("proof READY artifact shape is not exact")


def validate_derived_project_paths(ready: dict, proof_root: Path, source_project: Path) -> None:
    if ready["sourceAuthority"]["projectRoot"] != str(source_project.resolve()):
        raise ProofError("source project path is not derived from frozen observed40 authority")
    for replica in ready["replicas"]:
        replica_id = replica["id"]
        expected_control = proof_root / "projects" / f"{replica_id}-control"
        expected_apply = proof_root / "projects" / f"{replica_id}-apply"
        if (
            replica["controlProject"] != str(expected_control.resolve())
            or replica["applyProject"] != str(expected_apply.resolve())
        ):
            raise ProofError(f"{replica_id} project path is not derived from proof root")


def default_paths(repo_root: Path) -> dict[str, Path]:
    observed_root = repo_root / "local-lab" / "ghidra-promotion-v2-proof-2026-08-02" / "frozen-tool-proof-v9-alias-state-bound-v4"
    cohort_root = repo_root / "local-lab" / "crt-recursive-cohort-2026-08-02"
    return {
        "source_project": observed_root / "main-project",
        "observed_ready": observed_root / "proof.ready.json",
        "base_functions": observed_root / "runs" / "main-after" / "functions.tsv",
        "base_program": observed_root / "runs" / "main-after" / "program.tsv",
        "refutation_ready": cohort_root / "canary-refutation-v1-ready" / "canary-refutation.ready.json",
        "boundary_ready": cohort_root / "clean520-boundary-v3-canary-refuted" / "boundary-targets.ready.json",
        "canary": repo_root / "local-lab" / "formal-function-envelope-canary-20260803-v3/inputs" / "canary-two-range.tsv",
        "poison": repo_root / "local-lab" / "formal-function-envelope-canary-20260803-v3/inputs" / "poison-one-range.tsv",
        "toolchain": observed_root / "inputs" / "toolchain",
        "headless": Path(r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"),
        "java": Path(r"C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot\bin\java.exe"),
    }


def require_derived_selection(value: Path | None, expected: Path, label: str) -> Path:
    selected = lexical_absolute(value or expected)
    derived = lexical_absolute(expected)
    if selected != derived:
        raise ProofError(f"{label} must use the repository-derived authority path")
    return selected


def run_proof(args: argparse.Namespace) -> dict:
    raise ProofError(HISTORICAL_RETIREMENT_MESSAGE)

    repo_root = require_plain_directory(args.repo_root, "repository root")
    if not (repo_root / "README.MD").is_file() or not (repo_root / "tools").is_dir():
        raise ProofError("repository root is not Onslaught Toolkit")
    if Path(__file__).resolve() != (repo_root / "tools" / Path(__file__).name).resolve():
        raise ProofError("run the formal proof only from the landed repository proof owner")
    defaults = default_paths(repo_root)
    source_project = require_derived_selection(args.source_project, defaults["source_project"], "source project")
    observed_ready = require_derived_selection(args.observed_ready, defaults["observed_ready"], "observed40 READY")
    refutation_ready = require_derived_selection(args.refutation_ready, defaults["refutation_ready"], "canary refutation READY")
    boundary_ready = require_derived_selection(args.boundary_ready, defaults["boundary_ready"], "520 boundary READY")
    canary_source = require_derived_selection(args.canary_manifest, defaults["canary"], "canary manifest")
    poison_source = require_derived_selection(args.poison_manifest, defaults["poison"], "poison manifest")
    base_functions_source = require_derived_selection(args.base_functions, defaults["base_functions"], "base functions")
    base_program_source = require_derived_selection(args.base_program, defaults["base_program"], "base program")
    toolchain_source = require_derived_selection(
        args.toolchain_manifests, defaults["toolchain"], "toolchain manifest directory"
    )
    proof_root = lexical_absolute(args.proof_root)
    local_lab = require_plain_directory(repo_root / "local-lab", "repository local-lab")
    if proof_root.parent.resolve() != local_lab.resolve():
        raise ProofError("proof root must be one new direct child of repository local-lab")
    if proof_root.exists():
        raise ProofError("proof root already exists")
    ensure_plain_directory(proof_root, "proof root")
    for name in ("inputs", "tools", "runs", "projects", "work"):
        ensure_plain_directory(proof_root / name, f"proof {name}")

    source_project = require_plain_directory(source_project, "source project")
    source_rows_before = validate_source_project(source_project)

    validate_prerequisites(observed_ready, refutation_ready, boundary_ready)
    validate_base_inventory(base_functions_source, base_program_source)
    validate_canary_inputs(canary_source, poison_source)

    input_sources = {
        "observed40.ready.json": (observed_ready, OBSERVED40_READY_SHA256),
        "canary-refutation.ready.json": (refutation_ready, CANARY_REFUTATION_READY_SHA256),
        "boundary520.ready.json": (boundary_ready, BOUNDARY_READY_SHA256),
        "canary-two-range.tsv": (canary_source, CANARY_MANIFEST_SHA256),
        "poison-one-range.tsv": (poison_source, POISON_MANIFEST_SHA256),
        "base-functions.tsv": (base_functions_source, BASE_FUNCTIONS_SHA256),
        "base-program.tsv": (base_program_source, BASE_PROGRAM_SHA256),
    }
    source_graph: dict[str, object] = {}
    for name, (source, expected_hash) in input_sources.items():
        destination = proof_root / "inputs" / name
        metadata = snapshot_file(source, destination, expected_hash=expected_hash)
        metadata["snapshot"] = stamp(destination, proof_root)
        source_graph[name] = metadata
    base_functions = proof_root / "inputs" / "base-functions.tsv"
    base_program = proof_root / "inputs" / "base-program.tsv"
    canary = proof_root / "inputs" / "canary-two-range.tsv"
    poison = proof_root / "inputs" / "poison-one-range.tsv"

    tools: dict[str, Path] = {}
    tool_graph: dict[str, object] = {}
    for role, name in EXPECTED_TOOL_NAMES.items():
        source = repo_root / "tools" / name
        destination = proof_root / "tools" / name
        metadata = snapshot_file(source, destination, expected_hash=EXPECTED_TOOL_SHA256[role])
        metadata["snapshot"] = stamp(destination, proof_root)
        tool_graph[role] = metadata
        tools[role] = destination
    runner_source = require_plain_file(Path(__file__), "proof owner")
    runner_destination = proof_root / "tools" / Path(__file__).name
    runner_graph = snapshot_file(runner_source, runner_destination)
    runner_graph["snapshot"] = stamp(runner_destination, proof_root)

    control_paths: dict[str, Path] = {}
    for name, content in build_control_manifests(canary, poison).items():
        path = proof_root / "inputs" / "controls" / name
        write_new(path, content)
        control_paths[name] = path

    toolchain_source = require_plain_directory(toolchain_source, "toolchain manifest source")
    distribution_specs = {
        "ghidra": ("ghidra-files.tsv", GHIDRA_DISTRIBUTION),
        "jdk": ("jdk-files.tsv", JDK_DISTRIBUTION),
        "python": ("python-files.tsv", PYTHON_DISTRIBUTION),
    }
    distribution_manifests: dict[str, Path] = {}
    for label, (name, spec) in distribution_specs.items():
        source = toolchain_source / name
        if sha256_file(source) != spec[2]:
            raise ProofError(f"{label} distribution authority manifest mismatch")
        destination = proof_root / "inputs" / "toolchain" / name
        snapshot_file(source, destination, expected_hash=spec[2])
        distribution_manifests[label] = destination

    headless, properties, java, python = validate_external_toolchain(
        Path(args.analyze_headless or defaults["headless"]),
        Path(args.java or defaults["java"]),
    )
    toolchain = {
        "analyzeHeadless": external_stamp(headless),
        "applicationProperties": external_stamp(properties),
        "java": external_stamp(java),
        "python": external_stamp(python),
    }
    ghidra_distribution = verify_distribution(headless.parent.parent, distribution_manifests["ghidra"], GHIDRA_DISTRIBUTION, "Ghidra")
    jdk_distribution = verify_distribution(java.parent.parent, distribution_manifests["jdk"], JDK_DISTRIBUTION, "JDK")
    python_distribution = verify_distribution(python.parent, distribution_manifests["python"], PYTHON_DISTRIBUTION, "Python")
    for label, record in (
        ("ghidraDistribution", ghidra_distribution),
        ("jdkDistribution", jdk_distribution),
        ("pythonDistribution", python_distribution),
    ):
        key = label.removesuffix("Distribution").lower()
        record["manifest"] = stamp(distribution_manifests[key], proof_root)
        toolchain[label] = record

    environment = sanitized_environment(proof_root, java)
    cwd = proof_root / "work"
    source_before_run, source_before_functions, source_before_program = run_inventory(
        proof_root=proof_root, run_id="source-before", headless=headless,
        project_root=source_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(source_before_functions, source_before_program, base_functions, base_program, "source before")

    replicas = [run_replica(
        proof_root=proof_root, replica=replica, headless=headless, python=python,
        source_project=source_project, tools=tools, canary=canary, poison=poison,
        controls=control_paths, base_functions=base_functions, base_program=base_program,
        cwd=cwd, environment=environment,
    ) for replica in ("replica-a", "replica-b")]
    compare_replications(proof_root, replicas[0], replicas[1])

    source_after_run, source_after_functions, source_after_program = run_inventory(
        proof_root=proof_root, run_id="source-after", headless=headless,
        project_root=source_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_inventory_to_base(source_after_functions, source_after_program, base_functions, base_program, "source after")
    if project_rows(source_project) != source_rows_before:
        raise ProofError("source project changed during proof")

    for label, graph in [*source_graph.items(), *tool_graph.items(), ("runner", runner_graph)]:
        source_stamp = graph.get("source") if isinstance(graph, dict) else None
        source_path = resolve_external_stamp(source_stamp, f"post-run {label} source")
        snapshot_stamp = graph.get("snapshot") if isinstance(graph, dict) else None
        snapshot_path = validate_frozen_stamp(proof_root, snapshot_stamp, f"post-run {label} snapshot")
        if source_path.read_bytes() != snapshot_path.read_bytes():
            raise ProofError(f"post-run {label} source differs from frozen snapshot")
    current_headless, current_properties, current_java, current_python = validate_external_toolchain(
        headless, java
    )
    if (
        external_stamp(current_headless) != toolchain["analyzeHeadless"]
        or external_stamp(current_properties) != toolchain["applicationProperties"]
        or external_stamp(current_java) != toolchain["java"]
        or external_stamp(current_python) != toolchain["python"]
    ):
        raise ProofError("external toolchain changed during proof")
    for label, root, manifest, spec, key in (
        ("Ghidra", headless.parent.parent, distribution_manifests["ghidra"], GHIDRA_DISTRIBUTION, "ghidraDistribution"),
        ("JDK", java.parent.parent, distribution_manifests["jdk"], JDK_DISTRIBUTION, "jdkDistribution"),
        ("Python", python.parent, distribution_manifests["python"], PYTHON_DISTRIBUTION, "pythonDistribution"),
    ):
        authority_name = {
            "Ghidra": "ghidra-files.tsv",
            "JDK": "jdk-files.tsv",
            "Python": "python-files.tsv",
        }[label]
        require_plain_file(
            toolchain_source / authority_name,
            f"post-run {label} distribution authority",
            expected_hash=spec[2],
        )
        current = verify_distribution(root, manifest, spec, label)
        for field in ("root", "fileCount", "totalBytes", "fileSetSha256"):
            if current[field] != toolchain[key][field]:
                raise ProofError(f"{label} distribution changed during proof")

    ready = {
        "schema": SCHEMA,
        "status": "READY",
        "verdict": "SURVIVED",
        "program": expected_ready_program(),
        "sourceAuthority": {
            "projectRoot": str(source_project.resolve()),
            "projectFileCount": len(source_rows_before),
            "projectTotalBytes": sum(row[1] for row in source_rows_before),
            "projectFileSetSha256": rows_digest(source_rows_before),
            "inputs": source_graph,
            "sourceBeforeRun": source_before_run["receipt"],
            "sourceAfterRun": source_after_run["receipt"],
        },
        "tools": {**tool_graph, "runner": runner_graph},
        "toolchain": toolchain,
        "manifest": expected_ready_manifest(),
        "replicas": replicas,
        "checks": expected_ready_checks(),
        "claimBoundary": list(CLAIM_BOUNDARY),
    }
    artifacts = artifact_items(proof_root)
    ready["artifacts"] = {
        "canonicalization": "sorted relative path with exact bytes and SHA-256; READY excluded",
        "count": len(artifacts),
        "items": artifacts,
    }
    validate_ready_semantic_shape(ready)
    ready_path = proof_root / "proof.ready.json"
    write_json_new(ready_path, ready)
    return {"ready": str(ready_path), "readySha256": sha256_file(ready_path), "verdict": "SURVIVED"}


def resolve_external_stamp(value: object, label: str, *, expected_hash: str | None = None) -> Path:
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise ProofError(f"{label} external stamp is malformed")
    path = require_plain_file(Path(str(value["path"])), label)
    if external_stamp(path) != value:
        raise ProofError(f"{label} external stamp differs")
    if expected_hash is not None and value["sha256"] != expected_hash:
        raise ProofError(f"{label} external SHA-256 is unsupported")
    return path


def verify_run_receipt(
    proof_root: Path,
    value: object,
    label: str,
    *,
    expected_id: str | None = None,
    expected_argv: list[str] | None = None,
    expected_cwd: Path | None = None,
    expected_environment: dict[str, str] | None = None,
    expected_verdict: str | None = None,
) -> dict:
    path = validate_frozen_stamp(proof_root, value, label)
    receipt = read_json(path, label)
    log = validate_frozen_stamp(proof_root, receipt.get("log"), f"{label} log")
    expected_keys = {
        "id", "startedAtUtc", "completedAtUtc", "argv", "cwd", "environment",
        "exitCode", "log", "verdict", "observations",
    }
    if "logicalRunRoot" in receipt:
        expected_keys.add("logicalRunRoot")
    if set(receipt) != expected_keys:
        raise ProofError(f"{label} receipt key set is malformed")
    if (
        receipt.get("exitCode") != 0
        or receipt.get("verdict") not in {"SURVIVED", "REFUTED"}
        or not isinstance(receipt.get("observations"), dict)
        or any(
            not isinstance(receipt.get(key), str)
            or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z", receipt[key]) is None
            for key in ("startedAtUtc", "completedAtUtc")
        )
    ):
        raise ProofError(f"{label} receipt verdict is malformed")
    if expected_id is not None and receipt.get("id") != expected_id:
        raise ProofError(f"{label} receipt id mismatch")
    if expected_argv is not None and receipt.get("argv") != expected_argv:
        raise ProofError(f"{label} receipt argv mismatch")
    if expected_cwd is not None and receipt.get("cwd") != str(expected_cwd.resolve()):
        raise ProofError(f"{label} receipt cwd mismatch")
    if expected_environment is not None and receipt.get("environment") != expected_environment:
        raise ProofError(f"{label} receipt environment mismatch")
    if expected_verdict is not None and receipt.get("verdict") != expected_verdict:
        raise ProofError(f"{label} receipt verdict mismatch")
    if not log.read_bytes():
        raise ProofError(f"{label} log is empty")
    return receipt


def expected_replica_run_specs(
    *,
    proof_root: Path,
    replica_id: str,
    headless: Path,
    python: Path,
    source_project: Path,
    tools: dict[str, Path],
    canary: Path,
    poison: Path,
    controls: dict[str, Path],
    base_functions: Path,
) -> list[tuple[str, list[str], str]]:
    control_project = proof_root / "projects" / f"{replica_id}-control"
    apply_project = proof_root / "projects" / f"{replica_id}-apply"
    specs: list[tuple[str, list[str], str]] = [
        (f"{replica_id}-copy-control", backup_argv(python, tools["backup"], source_project, control_project), "SURVIVED"),
        (f"{replica_id}-copy-apply", backup_argv(python, tools["backup"], source_project, apply_project), "SURVIVED"),
    ]

    def inventory(run_id: str, project: Path) -> None:
        root = proof_root / "runs" / run_id
        specs.append((run_id, inventory_argv(
            headless, project, tools["inventory"], root / "functions.tsv", root / "program.tsv"
        ), "SURVIVED"))

    def envelope(
        logical_id: str,
        project: Path,
        manifest: Path,
        count: int,
        mode: str,
        verdict: str,
        *,
        supplied_hash: str | None = None,
        receipt_id: str | None = None,
    ) -> None:
        root = proof_root / "runs" / logical_id
        actual_id = receipt_id or logical_id
        specs.append((actual_id, envelope_argv(
            headless, project, tools["envelope"], manifest,
            supplied_hash or sha256_file(manifest), count,
            root / "envelopes.tsv", root / "envelopes.ready.json", mode,
        ), verdict))

    inventory(f"{replica_id}-control-baseline", control_project)
    envelope(f"{replica_id}-control-wrong-hash", control_project, canary, 1, "probe", "REFUTED", supplied_hash="0" * 64)
    envelope(f"{replica_id}-control-wrong-count", control_project, canary, 2, "probe", "REFUTED")
    envelope(f"{replica_id}-control-wrong-header", control_project, controls["wrong-header.tsv"], 1, "probe", "REFUTED")
    envelope(f"{replica_id}-control-trailing-blank", control_project, controls["trailing-blank.tsv"], 1, "probe", "REFUTED")
    envelope(f"{replica_id}-control-instruction-coverage", control_project, controls["instruction-coverage.tsv"], 1, "probe", "REFUTED")
    envelope(f"{replica_id}-control-pairwise-body-conflict", control_project, controls["pairwise-body-conflict.tsv"], 2, "probe", "REFUTED")
    envelope(f"{replica_id}-control-forbidden-target-conflict", control_project, controls["forbidden-target-conflict.tsv"], 2, "probe", "REFUTED")
    envelope(
        f"{replica_id}-control-preexisting-output", control_project, canary, 1, "probe", "REFUTED",
        receipt_id=f"{replica_id}-control-preexisting-output-execution",
    )
    envelope(f"{replica_id}-probe", control_project, canary, 1, "probe", "SURVIVED")
    inventory(f"{replica_id}-probe-reopened", control_project)
    envelope(f"{replica_id}-one-range-poison", control_project, poison, 1, "probe", "REFUTED")
    inventory(f"{replica_id}-poison-reopened", control_project)
    envelope(f"{replica_id}-wrong-thunk-kind", control_project, controls["wrong-thunk-kind.tsv"], 1, "probe", "REFUTED")
    inventory(f"{replica_id}-wrong-thunk-kind-reopened", control_project)
    envelope(f"{replica_id}-receipt-failure", control_project, canary, 1, "apply", "REFUTED")
    inventory(f"{replica_id}-receipt-failure-reopened", control_project)
    inventory(f"{replica_id}-apply-baseline", apply_project)
    envelope(f"{replica_id}-apply", apply_project, canary, 1, "apply", "SURVIVED")
    envelope(f"{replica_id}-readback", apply_project, canary, 1, "readback", "SURVIVED")
    inventory(f"{replica_id}-apply-reopened", apply_project)
    diff_run = f"{replica_id}-inventory-diff"
    specs.append((diff_run, diff_argv(
        python, tools["diff"], base_functions,
        proof_root / "runs" / f"{replica_id}-apply-reopened" / "functions.tsv",
        proof_root / "runs" / diff_run / "inventory-diff.json",
    ), "SURVIVED"))
    if len(specs) != 24:
        raise ProofError("internal expected replica run spec count is not 24")
    return specs


def require_receipt_stamp_order(receipts: object, run_ids: list[str], label: str) -> list[dict]:
    if not isinstance(receipts, list) or len(receipts) != len(run_ids):
        raise ProofError(f"{label} receipt count mismatch")
    for index, (receipt, run_id) in enumerate(zip(receipts, run_ids, strict=True)):
        if (
            not isinstance(receipt, dict)
            or set(receipt) != {"path", "bytes", "sha256"}
            or receipt.get("path") != f"runs/{run_id}/run.json"
        ):
            raise ProofError(f"{label} receipt order/path mismatch at {index}")
    return receipts


def verify_recorded_replica(
    proof_root: Path,
    replica: dict,
    *,
    headless: Path,
    python: Path,
    source_project: Path,
    tools: dict[str, Path],
    canary: Path,
    poison: Path,
    controls: dict[str, Path],
    base_functions: Path,
    base_program: Path,
    expected_environment: dict[str, str],
) -> None:
    replica_id = replica.get("id")
    if replica_id not in {"replica-a", "replica-b"}:
        raise ProofError("replica id is malformed")
    receipts = replica.get("runs")
    specs = expected_replica_run_specs(
        proof_root=proof_root, replica_id=replica_id, headless=headless,
        python=python, source_project=source_project, tools=tools, canary=canary,
        poison=poison, controls=controls, base_functions=base_functions,
    )
    receipts = require_receipt_stamp_order(
        receipts, [run_id for run_id, _argv, _verdict in specs], replica_id
    )
    expected_evidence_paths = {
        "probeOutput": f"runs/{replica_id}-probe/envelopes.tsv",
        "applyOutput": f"runs/{replica_id}-apply/envelopes.tsv",
        "readbackOutput": f"runs/{replica_id}-readback/envelopes.tsv",
        "afterFunctions": f"runs/{replica_id}-apply-reopened/functions.tsv",
        "afterProgram": f"runs/{replica_id}-apply-reopened/program.tsv",
    }
    for key, expected_path in expected_evidence_paths.items():
        if not isinstance(replica.get(key), dict) or replica[key].get("path") != expected_path:
            raise ProofError(f"{replica_id} {key} path mismatch")
    for index, (receipt_stamp, (run_id, argv, verdict)) in enumerate(zip(receipts, specs, strict=True)):
        receipt = verify_run_receipt(
            proof_root, receipt_stamp, f"{replica_id} run {index}",
            expected_id=run_id, expected_argv=argv,
            expected_cwd=proof_root / "work",
            expected_environment=expected_environment,
            expected_verdict=verdict,
        )
        if run_id.endswith("preexisting-output-execution"):
            logical = proof_root / "runs" / run_id.removesuffix("-execution")
            if receipt.get("logicalRunRoot") != str(logical.resolve()):
                raise ProofError(f"{replica_id} preexisting-output logical root mismatch")
        elif "logicalRunRoot" in receipt:
            raise ProofError(f"{replica_id} unexpected logicalRunRoot at {run_id}")

    for mode in ("probe", "apply", "readback"):
        run_root = proof_root / "runs" / f"{replica_id}-{mode}"
        output = run_root / "envelopes.tsv"
        java_ready = run_root / "envelopes.ready.json"
        validate_envelope_output(output, mode=mode)
        validate_java_ready(java_ready, output, mode=mode, tool=tools["envelope"], manifest=canary)

    base_pairs = (
        f"{replica_id}-control-baseline",
        f"{replica_id}-probe-reopened",
        f"{replica_id}-poison-reopened",
        f"{replica_id}-wrong-thunk-kind-reopened",
        f"{replica_id}-receipt-failure-reopened",
        f"{replica_id}-apply-baseline",
    )
    for run_id in base_pairs:
        compare_inventory_to_base(
            proof_root / "runs" / run_id / "functions.tsv",
            proof_root / "runs" / run_id / "program.tsv",
            base_functions,
            base_program,
            run_id,
        )
    after_functions = validate_frozen_stamp(proof_root, replica.get("afterFunctions"), f"{replica_id} after functions")
    after_program = validate_frozen_stamp(proof_root, replica.get("afterProgram"), f"{replica_id} after program")
    row = validate_applied_inventory(base_functions, base_program, after_functions, after_program)
    if row != replica.get("createdRow"):
        raise ProofError(f"{replica_id} created row does not reproduce")

    poison_root = proof_root / "runs" / f"{replica_id}-one-range-poison"
    if (poison_root / "envelopes.tsv").exists() or (poison_root / "envelopes.ready.json").exists():
        raise ProofError(f"{replica_id} one-range poison has an output")
    poison_log = (poison_root / "headless.log").read_text(encoding="utf-8")
    if (
        poison_log.count("REPORT SCRIPT ERROR") != 1
        or "BODY_ENVELOPE_MISMATCH entry=0x00542710" not in poison_log
        or CANARY_RANGES not in poison_log
        or "FUNCTION_ENVELOPE_MUTATION_TAINTED" not in poison_log
    ):
        raise ProofError(f"{replica_id} one-range poison receipt no longer reproduces")

    kind_root = proof_root / "runs" / f"{replica_id}-wrong-thunk-kind"
    if (kind_root / "envelopes.tsv").exists() or (kind_root / "envelopes.ready.json").exists():
        raise ProofError(f"{replica_id} wrong-thunk-kind control has an output")
    kind_log = (kind_root / "headless.log").read_text(encoding="utf-8")
    if (
        kind_log.count("REPORT SCRIPT ERROR") != 1
        or "THUNK_KIND_MISMATCH entry=0x00542710 expected=true actual=false" not in kind_log
        or "FUNCTION_ENVELOPE_MUTATION_TAINTED" not in kind_log
    ):
        raise ProofError(f"{replica_id} wrong-thunk-kind control no longer reproduces")

    race_root = proof_root / "runs" / f"{replica_id}-receipt-failure"
    if (race_root / "envelopes.tsv").read_bytes() != b"RECEIPT_PUBLICATION_RACE_POISON\n" or (race_root / "envelopes.ready.json").exists():
        raise ProofError(f"{replica_id} receipt-publication poison is not exact")
    race_log = (race_root / "headless.log").read_text(encoding="utf-8")
    if race_log.count("REPORT SCRIPT ERROR") != 1 or "FUNCTION_ENVELOPE_MUTATION_TAINTED" not in race_log:
        raise ProofError(f"{replica_id} receipt-publication failure was not transaction-tainted")

    preexisting_root = proof_root / "runs" / f"{replica_id}-control-preexisting-output"
    if (preexisting_root / "envelopes.tsv").read_bytes() != b"UNMANIFESTED_OUTPUT_POISON\n" or (preexisting_root / "envelopes.ready.json").exists():
        raise ProofError(f"{replica_id} preexisting-output control is not exact")
    for control in (
        "wrong-hash", "wrong-count", "wrong-header", "trailing-blank",
        "instruction-coverage", "pairwise-body-conflict", "forbidden-target-conflict",
    ):
        root = proof_root / "runs" / f"{replica_id}-control-{control}"
        if (root / "envelopes.tsv").exists() or (root / "envelopes.ready.json").exists():
            raise ProofError(f"{replica_id} {control} published an output")
    control_patterns = {
        "wrong-hash": r"manifest sha256 mismatch",
        "wrong-count": r"manifest count mismatch expected=2 actual=1",
        "wrong-header": r"manifest header mismatch",
        "trailing-blank": r"manifest has a trailing blank row",
        "instruction-coverage": r"INSTRUCTION_COVERAGE_MISMATCH",
        "pairwise-body-conflict": r"expected function bodies overlap",
        "forbidden-target-conflict": r"forbidden entry is another manifest target",
    }
    for control, pattern in control_patterns.items():
        log = (proof_root / "runs" / f"{replica_id}-control-{control}" / "headless.log").read_text(encoding="utf-8")
        if log.count("REPORT SCRIPT ERROR") != 1 or re.search(pattern, log) is None or "FUNCTION_ENVELOPE_MUTATION_TAINTED" in log:
            raise ProofError(f"{replica_id} {control} rejection log differs")
    preexisting_log = (
        proof_root / "runs" / f"{replica_id}-control-preexisting-output-execution" / "headless.log"
    ).read_text(encoding="utf-8")
    if preexisting_log.count("REPORT SCRIPT ERROR") != 1 or "output TSV already exists" not in preexisting_log or "FUNCTION_ENVELOPE_MUTATION_TAINTED" in preexisting_log:
        raise ProofError(f"{replica_id} preexisting-output rejection log differs")

    diff = read_json(proof_root / "runs" / f"{replica_id}-inventory-diff" / "inventory-diff.json", f"{replica_id} diff")
    if diff.get("counts", {}).get("created") != 1 or [item.get("address") for item in diff.get("created", [])] != [TARGET_ENTRY]:
        raise ProofError(f"{replica_id} inventory diff changed")


def live_reverify_projects(
    *,
    proof_root: Path,
    ready: dict,
    headless: Path,
    java: Path,
    inventory_tool: Path,
    base_functions: Path,
    base_program: Path,
    source_project: Path,
) -> None:
    projects: list[tuple[str, Path, Path, Path, str]] = [
        ("source-current", source_project, base_functions, base_program, BASE_PROJECT_FILE_SET_SHA256)
    ]
    for replica in ready["replicas"]:
        replica_id = replica["id"]
        projects.append((
            f"{replica_id}-control-current",
            require_plain_directory(
                proof_root / "projects" / f"{replica_id}-control",
                f"{replica_id} control project",
            ),
            base_functions,
            base_program,
            str(replica["controlProjectFileSetSha256"]),
        ))
        projects.append((
            f"{replica_id}-apply-current",
            require_plain_directory(
                proof_root / "projects" / f"{replica_id}-apply",
                f"{replica_id} apply project",
            ),
            validate_frozen_stamp(proof_root, replica["afterFunctions"], f"{replica_id} recorded functions"),
            validate_frozen_stamp(proof_root, replica["afterProgram"], f"{replica_id} recorded program"),
            str(replica["applyProjectFileSetSha256"]),
        ))
    with tempfile.TemporaryDirectory(prefix="bea-envelope-ready-verify-") as temporary:
        verification_root = Path(temporary).resolve()
        ensure_plain_directory(verification_root / "runs", "verification runs")
        ensure_plain_directory(verification_root / "work", "verification work")
        environment = sanitized_environment(verification_root, java)
        for run_id, project, expected_functions, expected_program, expected_raw in projects:
            before = project_rows(project)
            if rows_digest(before) != expected_raw:
                raise ProofError(f"retained {run_id} raw project differs before readback")
            _, functions, program = run_inventory(
                proof_root=verification_root, run_id=run_id, headless=headless,
                project_root=project, inventory_tool=inventory_tool,
                cwd=verification_root / "work", environment=environment,
            )
            if functions.read_bytes() != expected_functions.read_bytes() or program.read_bytes() != expected_program.read_bytes():
                raise ProofError(f"retained {run_id} semantic inventory differs")
            if project_rows(project) != before:
                raise ProofError(f"retained {run_id} changed during read-only verification")


def verify_ready(ready_path: Path) -> dict:
    raise ProofError(HISTORICAL_RETIREMENT_MESSAGE)

    ready_path = require_plain_file(ready_path, "proof READY")
    if ready_path.name != "proof.ready.json":
        raise ProofError("proof READY filename must be exactly proof.ready.json")
    proof_root = ready_path.parent.resolve()
    ready = read_json(ready_path, "proof READY")
    validate_ready_semantic_shape(ready)
    verify_artifact_items(proof_root, ready)

    tools: dict[str, Path] = {}
    for role, expected_hash in EXPECTED_TOOL_SHA256.items():
        record = ready.get("tools", {}).get(role)
        if not isinstance(record, dict):
            raise ProofError(f"missing frozen {role} tool")
        if record.get("snapshot", {}).get("path") != f"tools/{EXPECTED_TOOL_NAMES[role]}":
            raise ProofError(f"frozen {role} tool snapshot path differs")
        snapshot = validate_frozen_stamp(proof_root, record.get("snapshot"), f"frozen {role} tool")
        if sha256_file(snapshot) != expected_hash:
            raise ProofError(f"frozen {role} tool hash is unsupported")
        tools[role] = snapshot
    runner_record = ready.get("tools", {}).get("runner", {})
    if runner_record.get("snapshot", {}).get("path") != f"tools/{Path(__file__).name}":
        raise ProofError("frozen runner snapshot path differs")
    runner = validate_frozen_stamp(proof_root, runner_record.get("snapshot"), "frozen runner")
    if sha256_file(Path(__file__)) != sha256_file(runner):
        raise ProofError("invoke --verify-ready with the exact frozen proof owner")

    source_inputs = ready.get("sourceAuthority", {}).get("inputs", {})
    for name, expected_hash in (
        ("observed40.ready.json", OBSERVED40_READY_SHA256),
        ("canary-refutation.ready.json", CANARY_REFUTATION_READY_SHA256),
        ("boundary520.ready.json", BOUNDARY_READY_SHA256),
        ("canary-two-range.tsv", CANARY_MANIFEST_SHA256),
        ("poison-one-range.tsv", POISON_MANIFEST_SHA256),
        ("base-functions.tsv", BASE_FUNCTIONS_SHA256),
        ("base-program.tsv", BASE_PROGRAM_SHA256),
    ):
        record = source_inputs.get(name)
        if not isinstance(record, dict) or record.get("snapshot", {}).get("path") != f"inputs/{name}":
            raise ProofError(f"frozen {name} snapshot path differs")
        snapshot = validate_frozen_stamp(proof_root, record.get("snapshot") if isinstance(record, dict) else None, f"frozen {name}")
        if sha256_file(snapshot) != expected_hash:
            raise ProofError(f"frozen {name} hash differs")

    observed = proof_root / "inputs" / "observed40.ready.json"
    refutation = proof_root / "inputs" / "canary-refutation.ready.json"
    boundary = proof_root / "inputs" / "boundary520.ready.json"
    canary = proof_root / "inputs" / "canary-two-range.tsv"
    poison = proof_root / "inputs" / "poison-one-range.tsv"
    base_functions = proof_root / "inputs" / "base-functions.tsv"
    base_program = proof_root / "inputs" / "base-program.tsv"
    validate_prerequisites(observed, refutation, boundary)
    validate_base_inventory(base_functions, base_program)
    validate_canary_inputs(canary, poison)
    expected_controls = build_control_manifests(canary, poison)
    for name, content in expected_controls.items():
        path = proof_root / "inputs" / "controls" / name
        if require_plain_file(path, f"frozen {name}").read_bytes() != content:
            raise ProofError(f"frozen control manifest differs: {name}")

    if proof_root.parent.name != "local-lab":
        raise ProofError("proof READY must remain one direct child of repository local-lab")
    repo_root = require_plain_directory(proof_root.parent.parent, "proof repository root")
    if not (repo_root / "README.MD").is_file() or not (repo_root / "tools").is_dir():
        raise ProofError("proof parent is not the Onslaught Toolkit repository")
    derived = default_paths(repo_root)
    source_project = require_plain_directory(derived["source_project"], "derived source project")
    observed_payload = read_json(observed, "frozen observed40 authority")
    observed_project = observed_payload.get("projects", {}).get("mainScratch", {}).get("root")
    if observed_project != str(source_project.resolve()):
        raise ProofError("source project path is not derived from frozen observed40 authority")
    validate_derived_project_paths(ready, proof_root, source_project)

    expected_input_sources = {
        "observed40.ready.json": derived["observed_ready"],
        "canary-refutation.ready.json": derived["refutation_ready"],
        "boundary520.ready.json": derived["boundary_ready"],
        "canary-two-range.tsv": derived["canary"],
        "poison-one-range.tsv": derived["poison"],
        "base-functions.tsv": derived["base_functions"],
        "base-program.tsv": derived["base_program"],
    }
    for name, path in expected_input_sources.items():
        if ready["sourceAuthority"]["inputs"][name]["source"] != external_stamp(path):
            raise ProofError(f"{name} provenance source stamp is not exact")
    for role, name in EXPECTED_TOOL_NAMES.items():
        if ready["tools"][role]["source"] != external_stamp(repo_root / "tools" / name):
            raise ProofError(f"{role} provenance source stamp is not exact")
    if ready["tools"]["runner"]["source"] != external_stamp(repo_root / "tools" / Path(__file__).name):
        raise ProofError("runner provenance source stamp is not exact")

    toolchain = ready.get("toolchain", {})
    headless = resolve_external_stamp(toolchain.get("analyzeHeadless"), "analyzeHeadless", expected_hash=ANALYZE_HEADLESS_SHA256)
    properties = resolve_external_stamp(toolchain.get("applicationProperties"), "Ghidra properties", expected_hash=GHIDRA_APPLICATION_PROPERTIES_SHA256)
    java = resolve_external_stamp(toolchain.get("java"), "Java", expected_hash=HOST_JAVA_SHA256)
    python = resolve_external_stamp(toolchain.get("python"), "Python", expected_hash=PYTHON_SHA256)
    if properties != headless.parent.parent / "Ghidra" / "application.properties":
        raise ProofError("Ghidra launcher/properties roots disagree")
    for label, root, spec, key in (
        ("Ghidra", headless.parent.parent, GHIDRA_DISTRIBUTION, "ghidraDistribution"),
        ("JDK", java.parent.parent, JDK_DISTRIBUTION, "jdkDistribution"),
        ("Python", Path(str(toolchain["python"]["path"])).parent, PYTHON_DISTRIBUTION, "pythonDistribution"),
    ):
        record = toolchain.get(key)
        manifest_name = {
            "Ghidra": "ghidra-files.tsv",
            "JDK": "jdk-files.tsv",
            "Python": "python-files.tsv",
        }[label]
        if not isinstance(record, dict) or record.get("manifest", {}).get("path") != f"inputs/toolchain/{manifest_name}":
            raise ProofError(f"{label} distribution manifest path differs")
        manifest = validate_frozen_stamp(proof_root, record.get("manifest") if isinstance(record, dict) else None, f"{label} manifest")
        current = verify_distribution(root, manifest, spec, label)
        for field in ("root", "fileCount", "totalBytes", "fileSetSha256"):
            if record.get(field) != current[field]:
                raise ProofError(f"{label} distribution READY metadata differs")

    if rows_digest(validate_source_project(source_project)) != ready["sourceAuthority"]["projectFileSetSha256"]:
        raise ProofError("source project READY identity differs")
    for receipt_name in ("sourceBeforeRun", "sourceAfterRun"):
        run_id = "source-before" if receipt_name == "sourceBeforeRun" else "source-after"
        run_root = proof_root / "runs" / run_id
        receipt_stamp = ready["sourceAuthority"][receipt_name]
        if not isinstance(receipt_stamp, dict) or receipt_stamp.get("path") != f"runs/{run_id}/run.json":
            raise ProofError(f"{receipt_name} receipt path mismatch")
        verify_run_receipt(
            proof_root, receipt_stamp, receipt_name,
            expected_id=run_id,
            expected_argv=inventory_argv(
                headless, source_project, tools["inventory"],
                run_root / "functions.tsv", run_root / "program.tsv",
            ),
            expected_cwd=proof_root / "work",
            expected_environment=expected_sanitized_environment(proof_root, java),
            expected_verdict="SURVIVED",
        )
    for run_id in ("source-before", "source-after"):
        compare_inventory_to_base(
            proof_root / "runs" / run_id / "functions.tsv",
            proof_root / "runs" / run_id / "program.tsv",
            base_functions,
            base_program,
            run_id,
        )

    replicas = ready.get("replicas")
    if not isinstance(replicas, list) or [item.get("id") for item in replicas] != ["replica-a", "replica-b"]:
        raise ProofError("proof does not contain two ordered independent replicas")
    for replica in replicas:
        verify_recorded_replica(
            proof_root, replica, headless=headless, python=python,
            source_project=source_project, tools=tools, canary=canary,
            poison=poison,
            controls={name: proof_root / "inputs" / "controls" / name for name in expected_controls},
            base_functions=base_functions, base_program=base_program,
            expected_environment=expected_sanitized_environment(proof_root, java),
        )
    compare_replications(proof_root, replicas[0], replicas[1])
    live_reverify_projects(
        proof_root=proof_root, ready=ready, headless=headless, java=java,
        inventory_tool=tools["inventory"], base_functions=base_functions,
        base_program=base_program, source_project=source_project,
    )
    verify_artifact_items(proof_root, ready)
    return {
        "schema": SCHEMA,
        "verdict": "SURVIVED",
        "ready": str(ready_path),
        "readySha256": sha256_file(ready_path),
        "retainedProjectsReopenedReadOnly": 5,
        "replicas": 2,
        "batch520Authorized": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-ready", type=Path, help="independently verify a frozen proof READY")
    parser.add_argument("--proof-root", type=Path, help="new ignored local-lab proof directory")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-project", type=Path)
    parser.add_argument("--observed-ready", type=Path)
    parser.add_argument("--refutation-ready", type=Path)
    parser.add_argument("--boundary-ready", type=Path)
    parser.add_argument("--canary-manifest", type=Path)
    parser.add_argument("--poison-manifest", type=Path)
    parser.add_argument("--base-functions", type=Path)
    parser.add_argument("--base-program", type=Path)
    parser.add_argument("--toolchain-manifests", type=Path)
    parser.add_argument("--analyze-headless", type=Path)
    parser.add_argument("--java", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) == 2 and arguments[0] == "--_job-child":
        print(f"ERROR: {HISTORICAL_RETIREMENT_MESSAGE}", file=sys.stderr)
        return 2
    parser = build_parser()
    args = parser.parse_args(arguments)
    try:
        if args.verify_ready is not None:
            if args.proof_root is not None:
                raise ProofError("--verify-ready and --proof-root are mutually exclusive")
            result = verify_ready(args.verify_ready)
        else:
            if args.proof_root is None:
                parser.error("--proof-root is required unless --verify-ready is used")
            result = run_proof(args)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ProofError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
