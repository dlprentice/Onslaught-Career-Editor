#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Own the one-shot maintainer-Ghidra promotion of the proven 515 boundaries.

This is deliberately specimen-, project-, tool-, manifest-, and campaign-
specific.  The CLI exposes no override for any mutating input.  ``prepare``
proves and backs up the exact PRE state, ``promote`` may spawn the one fixed
mutator exactly once, and ``recover-status`` can only observe and classify the
live project as PRE, POST, or UNKNOWN.  No command restores automatically.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import ctypes
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Callable, Iterator, Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_function_batch_proof as batch  # noqa: E402
import ghidra_function_envelope_proof as envelope  # noqa: E402
import ghidra_global_init_full520_proof as formal  # noqa: E402
import ghidra_project_backup as backup  # noqa: E402
import ghidra_promotion_scratch_proof as scratch  # noqa: E402


SCHEMA = "bea.re.ghidra-global-init515-live-promotion.v1"
PREPARED_SCHEMA = "bea.re.ghidra-global-init515-live-prepared.v1"
OBSERVATION_SCHEMA = "bea.re.ghidra-global-init515-live-observation.v1"
PROCESS_SCHEMA = "bea.re.contained-process.v1"
ATTEMPT_SCHEMA = "bea.re.ghidra-global-init515-live-attempt.v1"
RECOVERY_SCHEMA = "bea.re.ghidra-global-init515-live-recovery.v1"

REPO_ROOT = TOOLS.parent
OWNER_ROOT = REPO_ROOT / "local-lab/global-init515-live-promotion-20260803-v4"
LIVE_PROJECT_ROOT = Path(r"C:\Users\david\Ghidra\Projects")
PROJECT_NAME = "BEA"
PROGRAM_NAME = "BEA.exe"
NATIVE_LOCK = LIVE_PROJECT_ROOT / f"{PROJECT_NAME}.lock"
MUTEX_NAME = "Local\\OnslaughtToolkit.BEA.Ghidra.GlobalInit515.Live.v1"

FORMAL_ROOT = REPO_ROOT / "local-lab/formal-global-init515-proof-20260803-v4"
FORMAL_READY = FORMAL_ROOT / "proof.ready.json"
FORMAL_READY_SHA256 = "0fa28300606f55d96e9e4c4168501c39d8eee25823033042d89339ae58d40729"
FORMAL_OWNER_SHA256 = "2fea029379aaf81df072907a87e142f03e4c1d261d19325933b18823b4fef972"
MANIFEST_SHA256 = "d9b919ee08d9d8becaa10ce2e248c604730fc7cbb97989da1e8e4d632d4e1abd"
LINEAGE_ROOT = REPO_ROOT / "local-lab/global-init515-campaign-lineage-v1-ready"
LINEAGE_READY_SHA256 = "384a9ba709dd9657ca2e06fce427fbc265a8915cb62dc4b992ee6da0ae8e2e8c"
LINEAGE_OWNER_SHA256 = "54e8a92fc01314baaf24e24d03c19aa52adb8b1481ce2ecffb225e4cace61685"
CAMPAIGN_ROOT = (
    REPO_ROOT
    / "local-lab/re-campaign/campaign-2026-08-02-observed40-generation-5-v5-carried-r3-invariant-bound"
)
CAMPAIGN_READY_SHA256 = "5bddceb51c131d9c3a1ac634fd0672d0e9999b7ccab3f65dd2b33b4a68947cde"
CAMPAIGN_REDUCER_ID = "384c325149a4244a5eb48fa70d01bff541584d7b3c5b90b69e4658eed96852d6"

FIXED_TOOL_HASHES = {
    "envelope": "f8a2b456c30969d6b7af480f391f340748db8db65771f239d925b4d0b4ef1201",
    "inventory": "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    "symbols": "6ea0e6ce2669dd9cb325a052df70cd2f84cd5ebc1319cf5ba8c089691d660327",
    "backup": "36969a237eef29fea0daa52fe4a657127bdbbb5091523c9ca7cd92c69566b452",
    "envelopeHelper": "e20d619c39dd0f2037523b4577860b6640ed76b0be058472834a587192b305e8",
    "batchHelper": "f76a3e74bd618ef824b0185ce7bebf7476387381e8ace991af72c38560741afa",
    "formalOwner": FORMAL_OWNER_SHA256,
    "scratchSafety": "895405aea9da78f72901250c7edb4e042ec28fadf6fbf9409d83097f8dd228be",
}
BASE_FUNCTIONS_SHA256 = "26977c69e3530ff9344c6456b3a0dac218775eaf0c1043ac2c89c6a9b95ab368"
BASE_PROGRAM_SHA256 = "eaf62f346c0c0efebb629bef775f519882bfad0aaa61917929d5fda6805c43ad"
PRE_SYMBOLS_SHA256 = "9f736e1c268550371a951315e79ad5bc85058a89127269ac15002cf95155e8c4"
POST_FUNCTIONS_SHA256 = "2e25b287ad5521780286f6b30e92172c84ab4f1e92ac933581593cc0f6cfc542"
POST_PROGRAM_SHA256 = "c8bbbebaee33a0bacf1f762948bd9ff2beb8595a86ac431f6b690c22ef2ae0cb"
POST_SYMBOLS_SHA256 = "02edbc524890117385f14ad74fb7d400c8cfd53c2c0ef08da5bfc1624c03ed29"
APPLY_OUTPUT_SHA256 = "93da623428ad53bd511a656c071ba2f53886c2d99a2f05f592efa5cdc9782c40"
TARGET_COUNT = 515
BASE_OUTSIDE_SYMBOLS = 86091
BASE_OUTSIDE_SYMBOLS_SHA256 = "149b88937826f6a8146eaf24f773fd9bad325b0eacbac576c2a32d4e300649da"

WAIT_OBJECT_0 = 0x00000000
WAIT_ABANDONED = 0x00000080
WAIT_TIMEOUT = 0x00000102
ERROR_ALREADY_EXISTS = 183
TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80


class LivePromotionError(ValueError):
    """A fail-closed live-owner refusal."""


class ProjectState(StrEnum):
    PRE = "PRE"
    POST = "POST"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Authority:
    formal_ready: Path
    manifest: Path
    base_functions: Path
    base_program: Path
    reference_pre_symbols: Path
    reference_post_functions: Path
    reference_post_program: Path
    reference_post_symbols: Path
    envelope_tool: Path
    inventory_tool: Path
    symbol_tool: Path
    formal_owner: Path
    lineage_owner: Path
    campaign_owner: Path
    python: Path
    headless: Path
    java: Path


@dataclass(frozen=True)
class MutexLease:
    name: str
    abandoned: bool


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LivePromotionError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_file(path: Path, expected: str, label: str, *, single_link: bool = False) -> Path:
    try:
        checked = scratch.require_plain_file(path, label, single_link=single_link)
    except (scratch.ProofError, OSError) as exc:
        raise LivePromotionError(str(exc)) from exc
    require(sha256_file(checked) == expected, f"{label} SHA-256 differs: {checked}")
    return checked


def write_json_new(path: Path, value: object) -> None:
    try:
        scratch.write_json_new(path, value)
    except (scratch.ProofError, OSError) as exc:
        raise LivePromotionError(str(exc)) from exc


def write_bytes_new(path: Path, value: bytes) -> None:
    try:
        scratch.write_new(path, value)
    except (scratch.ProofError, OSError) as exc:
        raise LivePromotionError(str(exc)) from exc


def relative_stamp(path: Path, root: Path) -> dict[str, object]:
    path = scratch.require_plain_file(path, "artifact", single_link=True)
    relative = path.relative_to(root.resolve()).as_posix()
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def validate_relative_stamp(value: object, root: Path, label: str) -> Path:
    require(isinstance(value, dict), f"{label} stamp is absent")
    require(set(value) == {"path", "bytes", "sha256"}, f"{label} stamp shape differs")
    relative = value.get("path")
    require(
        isinstance(relative, str)
        and relative
        and not Path(relative).is_absolute()
        and ".." not in Path(relative).parts
        and "\\" not in relative,
        f"{label} stamp path is unsafe",
    )
    path = root / relative
    path = scratch.require_plain_file(path, label, single_link=True)
    require(path.stat().st_size == value.get("bytes"), f"{label} byte count differs")
    require(sha256_file(path) == value.get("sha256"), f"{label} SHA-256 differs")
    return path


def validate_process_receipt(value: object, root: Path, label: str) -> dict[str, object]:
    receipt_path = validate_relative_stamp(value, root, f"{label} receipt")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(receipt.get("schema") == PROCESS_SCHEMA, f"{label} process schema differs")
    require_success(receipt, label)
    validate_relative_stamp(receipt.get("log"), root, f"{label} log")
    return receipt


def validate_observation_receipt(
    value: object,
    root: Path,
    label: str,
    *,
    authority: Authority,
    expected_state: ProjectState,
    expected_project_root: Path,
) -> dict[str, object]:
    observation_path = validate_relative_stamp(value, root, label)
    observation = json.loads(observation_path.read_text(encoding="utf-8"))
    require(observation.get("schema") == OBSERVATION_SCHEMA, f"{label} schema differs")
    require(
        observation.get("projectRoot") == str(expected_project_root.resolve()),
        f"{label} project root differs",
    )
    require(observation.get("rawStable") is True, f"{label} raw stability differs")
    require(
        observation.get("rawBefore", {}).get("root")
        == str(expected_project_root.resolve())
        and observation.get("rawAfter", {}).get("root")
        == str(expected_project_root.resolve()),
        f"{label} raw snapshot roots differ",
    )
    require(
        same_project_snapshot(
            observation.get("rawBefore", {}), observation.get("rawAfter", {})
        ),
        f"{label} raw snapshots differ",
    )
    artifacts = {
        artifact: validate_relative_stamp(
            observation.get(artifact), root, f"{label} {artifact}"
        )
        for artifact in ("functions", "program", "symbols", "symbolsReady")
    }
    reproduced = classify_exports(
        authority=authority,
        functions=artifacts["functions"],
        program=artifacts["program"],
        symbols=artifacts["symbols"],
        symbols_ready=artifacts["symbolsReady"],
        raw_stable=True,
    )
    require(
        reproduced == {"state": expected_state, "reasons": []},
        f"{label} reproduced classification differs",
    )
    require(
        observation.get("classification") == reproduced,
        f"{label} recorded classification differs",
    )
    validate_process_receipt(observation.get("inventoryRun"), root, f"{label} inventory")
    validate_process_receipt(observation.get("symbolRun"), root, f"{label} symbols")
    return observation


def project_snapshot(project_root: Path) -> dict[str, object]:
    try:
        rows = scratch.project_rows_from_disk(project_root, PROJECT_NAME)
    except (scratch.ProofError, OSError) as exc:
        raise LivePromotionError(str(exc)) from exc
    return {
        "root": str(project_root.resolve()),
        "fileCount": len(rows),
        "totalBytes": sum(row[1] for row in rows),
        "fileSetSha256": scratch.canonical_rows_sha(rows),
        "files": [
            {"path": relative, "bytes": size, "sha256": digest}
            for relative, size, digest in rows
        ],
    }


def same_project_snapshot(first: Mapping[str, object], second: Mapping[str, object]) -> bool:
    return all(
        first.get(key) == second.get(key)
        for key in ("fileCount", "totalBytes", "fileSetSha256", "files")
    )


def validate_project_snapshot(value: object, project_root: Path, label: str) -> dict[str, object]:
    require(isinstance(value, dict), f"{label} snapshot is absent")
    actual = project_snapshot(project_root)
    require(same_project_snapshot(value, actual), f"{label} project bytes differ")
    return actual


def require_disjoint_project_files(first: Path, second: Path) -> None:
    try:
        _, first_files = scratch.plain_project_files(first, PROJECT_NAME)
        _, second_files = scratch.plain_project_files(second, PROJECT_NAME)
    except (scratch.ProofError, OSError) as exc:
        raise LivePromotionError(str(exc)) from exc
    first_ids = {(path.stat().st_dev, path.stat().st_ino) for path in first_files}
    second_ids = {(path.stat().st_dev, path.stat().st_ino) for path in second_files}
    require(first_ids.isdisjoint(second_ids), "project copy aliases source file identities")
    for source in first_files:
        for destination in second_files:
            require(not os.path.samefile(source, destination), "project copies alias by samefile")


class _ProcessEntry32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("cntUsage", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", ctypes.c_ulong),
        ("cntThreads", ctypes.c_ulong),
        ("th32ParentProcessID", ctypes.c_ulong),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", ctypes.c_ulong),
        ("szExeFile", ctypes.c_wchar * 260),
    ]


def running_java_processes() -> list[dict[str, object]]:
    require(os.name == "nt", "live Ghidra promotion is Windows-only")
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateToolhelp32Snapshot.argtypes = [ctypes.c_ulong, ctypes.c_ulong]
    kernel32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
    kernel32.Process32FirstW.argtypes = [ctypes.c_void_p, ctypes.POINTER(_ProcessEntry32W)]
    kernel32.Process32FirstW.restype = ctypes.c_int
    kernel32.Process32NextW.argtypes = [ctypes.c_void_p, ctypes.POINTER(_ProcessEntry32W)]
    kernel32.Process32NextW.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        raise LivePromotionError("cannot enumerate processes for Java quiescence")
    entry = _ProcessEntry32W()
    entry.dwSize = ctypes.sizeof(_ProcessEntry32W)
    rows: list[dict[str, object]] = []
    try:
        present = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while present:
            name = entry.szExeFile.casefold()
            if name in {"java.exe", "javaw.exe"}:
                rows.append({"pid": int(entry.th32ProcessID), "name": entry.szExeFile})
            present = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return sorted(rows, key=lambda row: int(row["pid"]))


@contextlib.contextmanager
def exclusive_project_probe(project_root: Path) -> Iterator[int]:
    require(os.name == "nt", "exclusive project probe is Windows-only")
    try:
        _, files = scratch.plain_project_files(project_root, PROJECT_NAME)
    except (scratch.ProofError, OSError) as exc:
        raise LivePromotionError(str(exc)) from exc
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateFileW.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_void_p,
    ]
    kernel32.CreateFileW.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    handles: list[int] = []
    try:
        for path in files:
            handle = kernel32.CreateFileW(
                str(path), 0, 0, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None
            )
            if handle == INVALID_HANDLE_VALUE:
                raise LivePromotionError(f"project file is not exclusively available: {path}")
            handles.append(handle)
        yield len(handles)
    finally:
        for handle in reversed(handles):
            kernel32.CloseHandle(handle)


def assert_quiescent(project_root: Path = LIVE_PROJECT_ROOT) -> dict[str, object]:
    java = running_java_processes()
    require(not java, f"Java/Ghidra process is active: {java}")
    lock = project_root / f"{PROJECT_NAME}.lock"
    require(not os.path.lexists(lock), f"native Ghidra project lock exists: {lock}")
    with exclusive_project_probe(project_root) as opened:
        snapshot = project_snapshot(project_root)
    return {
        "checkedAtUtc": utc_now(),
        "javaProcesses": [],
        "nativeLockAbsent": True,
        "exclusiveFilesProbed": opened,
        "projectFileSetSha256": snapshot["fileSetSha256"],
    }


@contextlib.contextmanager
def acquire_mutex(*, allow_abandoned: bool = False) -> Iterator[MutexLease]:
    require(os.name == "nt", "live Ghidra promotion is Windows-only")
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel32.WaitForSingleObject.restype = ctypes.c_ulong
    kernel32.ReleaseMutex.argtypes = [ctypes.c_void_p]
    kernel32.ReleaseMutex.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    require(bool(handle), "cannot create live-promotion mutex")
    acquired = False
    try:
        result = kernel32.WaitForSingleObject(handle, 0)
        if result == WAIT_TIMEOUT:
            raise LivePromotionError("another live-promotion owner holds the mutex")
        if result == WAIT_ABANDONED:
            acquired = True
            require(allow_abandoned, "live-promotion mutex was abandoned; use recover-status")
            yield MutexLease(MUTEX_NAME, True)
            return
        require(result == WAIT_OBJECT_0, f"live-promotion mutex wait failed: {result}")
        acquired = True
        yield MutexLease(MUTEX_NAME, False)
    finally:
        if acquired:
            kernel32.ReleaseMutex(handle)
        kernel32.CloseHandle(handle)


def load_authority() -> Authority:
    formal_ready = exact_file(FORMAL_READY, FORMAL_READY_SHA256, "formal 515 READY")
    ready = json.loads(formal_ready.read_text(encoding="utf-8"))
    require(ready.get("schema") == formal.SCHEMA, "formal READY schema differs")
    require(ready.get("status") == "READY" and ready.get("verdict") == "SURVIVED", "formal READY is not survived")

    tools = FORMAL_ROOT / "tools"
    fixed = {
        "envelope": tools / "CreateFunctionsFromBoundaryManifest.java",
        "inventory": tools / "ExportFullFunctionInventory.java",
        "symbols": tools / "ExportTargetSymbolInventory.java",
        "backup": TOOLS / "ghidra_project_backup.py",
        "envelopeHelper": TOOLS / "ghidra_function_envelope_proof.py",
        "batchHelper": TOOLS / "ghidra_function_batch_proof.py",
        "formalOwner": tools / "ghidra_global_init_full520_proof.py",
        "scratchSafety": TOOLS / "ghidra_promotion_scratch_proof.py",
    }
    for role, path in fixed.items():
        exact_file(path, FIXED_TOOL_HASHES[role], f"fixed {role} tool")

    manifest = exact_file(
        FORMAL_ROOT / "inputs/admissible515.tsv", MANIFEST_SHA256, "admissible 515 manifest"
    )
    base_functions = exact_file(
        FORMAL_ROOT / "inputs/base-functions.tsv", BASE_FUNCTIONS_SHA256, "base functions"
    )
    base_program = exact_file(
        FORMAL_ROOT / "inputs/base-program.tsv", BASE_PROGRAM_SHA256, "base program"
    )
    reference_pre_symbols = exact_file(
        FORMAL_ROOT / "runs/source-target-symbols-before/target-symbols.tsv",
        PRE_SYMBOLS_SHA256,
        "reference PRE target symbols",
    )
    reference_post_functions = exact_file(
        FORMAL_ROOT / "runs/replica-a-apply-reopened/functions.tsv",
        POST_FUNCTIONS_SHA256,
        "reference POST functions",
    )
    reference_post_program = exact_file(
        FORMAL_ROOT / "runs/replica-a-apply-reopened/program.tsv",
        POST_PROGRAM_SHA256,
        "reference POST program",
    )
    reference_post_symbols = exact_file(
        FORMAL_ROOT / "runs/replica-a-target-symbols/target-symbols.tsv",
        POST_SYMBOLS_SHA256,
        "reference POST target symbols",
    )
    formal.validate_admissible_manifest(manifest)
    envelope.validate_base_inventory(base_functions, base_program)
    formal.validate_applied_inventory(
        base_functions,
        base_program,
        reference_post_functions,
        reference_post_program,
        manifest,
    )

    exact_file(LINEAGE_ROOT / "READY.json", LINEAGE_READY_SHA256, "campaign lineage READY")
    lineage_owner = exact_file(
        LINEAGE_ROOT / "lineage-owner.py", LINEAGE_OWNER_SHA256, "campaign lineage owner"
    )
    campaign_ready = exact_file(
        CAMPAIGN_ROOT / "campaign.ready.json", CAMPAIGN_READY_SHA256, "campaign generation 5 READY"
    )
    campaign_payload = json.loads(campaign_ready.read_text(encoding="utf-8"))
    require(
        campaign_payload.get("generation") == 5
        and campaign_payload.get("reducer", {}).get("id") == CAMPAIGN_REDUCER_ID,
        "campaign generation-5 identity differs",
    )
    campaign_owner = exact_file(
        CAMPAIGN_ROOT / "_reducer/tools/re_campaign.py",
        next(
            row["sha256"]
            for row in campaign_payload["reducer"]["files"]
            if row["path"] == "_reducer/tools/re_campaign.py"
        ),
        "campaign generation-5 frozen reducer",
    )

    toolchain = ready.get("toolchain", {})
    python_spec = toolchain.get("python", {})
    headless_spec = toolchain.get("analyzeHeadless", {})
    java_spec = toolchain.get("java", {})
    python = exact_file(Path(str(python_spec.get("path", ""))), str(python_spec.get("sha256", "")), "frozen Python")
    headless = exact_file(Path(str(headless_spec.get("path", ""))), str(headless_spec.get("sha256", "")), "frozen analyzeHeadless")
    java = exact_file(Path(str(java_spec.get("path", ""))), str(java_spec.get("sha256", "")), "frozen Java")

    project_snapshot(LIVE_PROJECT_ROOT)
    return Authority(
        formal_ready=formal_ready,
        manifest=manifest,
        base_functions=base_functions,
        base_program=base_program,
        reference_pre_symbols=reference_pre_symbols,
        reference_post_functions=reference_post_functions,
        reference_post_program=reference_post_program,
        reference_post_symbols=reference_post_symbols,
        envelope_tool=fixed["envelope"],
        inventory_tool=fixed["inventory"],
        symbol_tool=fixed["symbols"],
        formal_owner=fixed["formalOwner"],
        lineage_owner=lineage_owner,
        campaign_owner=campaign_owner,
        python=python,
        headless=headless,
        java=java,
    )


def environment_for(session_root: Path, authority: Authority) -> tuple[dict[str, str], Path]:
    work = session_root / "work"
    envelope.ensure_plain_directory(work, "live-owner work directory")
    environment = envelope.expected_sanitized_environment(session_root, authority.java)
    for key in ("APPDATA", "LOCALAPPDATA", "TEMP", "USERPROFILE"):
        envelope.ensure_plain_directory(Path(environment[key]), f"runtime {key}")
    settings = Path(environment["APPDATA"]) / "ghidra" / "ghidra_12.1.2_PUBLIC"
    envelope.ensure_plain_directory(settings, "Ghidra runtime settings")
    java_home = settings / "java_home.save"
    expected = f"{authority.java.parent.parent.resolve()}\r\n".encode()
    if java_home.exists():
        require(java_home.read_bytes() == expected, "runtime java_home.save differs")
    else:
        write_bytes_new(java_home, expected)
    environment["BEA_REPO_ROOT"] = str(REPO_ROOT.resolve())
    return environment, work


Spawn = Callable[[list[str], Path, dict[str, str]], tuple[object, int]]
CloseHandle = Callable[[int], None]


def run_contained(
    *,
    session_root: Path,
    run_id: str,
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
    timeout_seconds: int,
    spawn: Spawn = envelope._spawn_contained_process,
    close_handle: CloseHandle = envelope._close_handle,
) -> tuple[dict[str, object], str]:
    run_root = session_root / "runs" / run_id
    require(not run_root.exists(), f"run root already exists: {run_root}")
    envelope.ensure_plain_directory(run_root, f"{run_id} run root")
    log_path = run_root / "headless.partial.log"
    log_path = scratch.require_plain_existing_ancestors(log_path, "partial process log")
    started = utc_now()
    process: object | None = None
    job = 0
    status = "SPAWN_ERROR"
    exit_code: int | None = None
    error = ""
    reader_error = ""
    stream = log_path.open("xb")
    stream.flush()
    os.fsync(stream.fileno())

    def pump() -> None:
        nonlocal reader_error
        try:
            source = getattr(process, "stdout", None)
            if source is None:
                return
            while True:
                chunk = source.read(65536)
                if not chunk:
                    break
                if isinstance(chunk, str):
                    chunk = chunk.encode("utf-8", errors="replace")
                stream.write(chunk)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException as exc:  # reported in the immutable run receipt
            reader_error = f"{type(exc).__name__}: {exc}"

    reader: threading.Thread | None = None
    try:
        process, job = spawn(argv, cwd, environment)
        reader = threading.Thread(target=pump, name=f"{run_id}-log", daemon=True)
        reader.start()
        try:
            exit_code = int(process.wait(timeout=timeout_seconds))
            status = "COMPLETED"
        except subprocess.TimeoutExpired as exc:
            status = "TIMED_OUT"
            error = f"timed out after {timeout_seconds}s"
            if job:
                close_handle(job)
                job = 0
            try:
                exit_code = int(process.wait(timeout=15))
            except subprocess.TimeoutExpired as kill_exc:
                status = "CONTAINMENT_ERROR"
                error = "job tree survived kill-on-close"
                try:
                    process.kill()
                    exit_code = int(process.wait(timeout=15))
                except BaseException as final_exc:
                    error += f"; forced kill failed: {type(final_exc).__name__}: {final_exc}"
    except BaseException as exc:
        status = "SPAWN_ERROR"
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if job:
            close_handle(job)
        if reader is not None:
            reader.join(timeout=15)
            if reader.is_alive():
                reader_error = "log reader did not terminate"
        stream.flush()
        os.fsync(stream.fileno())
        stream.close()

    text = log_path.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
    receipt = {
        "schema": PROCESS_SCHEMA,
        "id": run_id,
        "startedAtUtc": started,
        "completedAtUtc": utc_now(),
        "argv": argv,
        "cwd": str(cwd.resolve()),
        "environment": environment,
        "status": status,
        "exitCode": exit_code,
        "error": error,
        "readerError": reader_error,
        "log": relative_stamp(log_path, session_root),
    }
    receipt_path = run_root / "run.json"
    write_json_new(receipt_path, receipt)
    receipt["receipt"] = relative_stamp(receipt_path, session_root)
    return receipt, text


def require_success(result: Mapping[str, object], label: str) -> None:
    require(result.get("status") == "COMPLETED", f"{label} did not complete")
    require(result.get("exitCode") == 0, f"{label} exit code differs")
    require(not result.get("readerError"), f"{label} log reader failed")


def parse_json_output(text: str, label: str) -> dict[str, object]:
    try:
        value = json.loads(text.strip())
    except json.JSONDecodeError as exc:
        raise LivePromotionError(f"{label} output is not one JSON object") from exc
    require(isinstance(value, dict), f"{label} output is not a JSON mapping")
    return value


def parse_campaign_output(text: str, label: str) -> dict[str, object]:
    line = text.strip()
    prefix = "CAMPAIGN_VERIFIED "
    suffix = f" {CAMPAIGN_ROOT}"
    require(
        line.startswith(prefix) and line.endswith(suffix),
        f"{label} output is not the exact campaign verification line",
    )
    counts_text = line[len(prefix) : -len(suffix)]
    try:
        counts = ast.literal_eval(counts_text)
    except (SyntaxError, ValueError) as exc:
        raise LivePromotionError(f"{label} campaign counts cannot be parsed") from exc
    require(isinstance(counts, dict), f"{label} campaign counts are not a mapping")
    return {"generation": 5, "counts": counts}


def verify_authority_reproductions(
    session_root: Path,
    authority: Authority,
    environment: dict[str, str],
    cwd: Path,
) -> dict[str, object]:
    commands = {
        "formal": [
            str(authority.python), "-I", "-B", str(authority.formal_owner),
            "--verify-ready", str(authority.formal_ready),
        ],
        "lineage": [
            str(authority.python), "-I", "-B", str(authority.lineage_owner),
            "verify", "--bundle", str(LINEAGE_ROOT),
        ],
        # The frozen campaign owner imports sibling reducer modules before it
        # edits sys.path; -I is therefore intentionally not used here.
        "campaign": [
            str(authority.python), "-B", str(authority.campaign_owner),
            "verify", "--campaign", str(CAMPAIGN_ROOT),
        ],
    }
    results: dict[str, object] = {}
    for label, argv in commands.items():
        result, text = run_contained(
            session_root=session_root,
            run_id=f"authority-{label}",
            argv=argv,
            cwd=cwd,
            environment=environment,
            timeout_seconds=1800 if label == "formal" else 180,
        )
        require_success(result, f"{label} authority verifier")
        payload = (
            parse_campaign_output(text, f"{label} authority verifier")
            if label == "campaign"
            else parse_json_output(text, f"{label} authority verifier")
        )
        if label == "formal":
            require(
                payload.get("verdict") == "SURVIVED"
                and payload.get("admissibleTargets") == TARGET_COUNT
                and payload.get("publicationStatus") == "READY",
                "formal authority verifier result differs",
            )
        elif label == "lineage":
            require(
                payload.get("status") == "READY"
                and payload.get("summary", {}).get("rows") == TARGET_COUNT,
                "lineage authority verifier result differs",
            )
        else:
            require(
                payload.get("generation") == 5
                and payload.get("counts", {}).get("functions") == 7595
                and payload.get("counts", {}).get("residuals") == 6618,
                "campaign authority verifier result differs",
            )
        results[label] = {"run": result["receipt"], "result": payload}
    return results


def classify_exports(
    *,
    authority: Authority,
    functions: Path,
    program: Path,
    symbols: Path,
    symbols_ready: Path,
    raw_stable: bool,
) -> dict[str, object]:
    if not raw_stable:
        return {"state": ProjectState.UNKNOWN, "reasons": ["raw project changed during read-only observation"]}

    pre_errors: list[str] = []
    post_errors: list[str] = []
    try:
        require(sha256_file(functions) == BASE_FUNCTIONS_SHA256, "PRE function export hash differs")
        require(sha256_file(program) == BASE_PROGRAM_SHA256, "PRE program export hash differs")
        require(sha256_file(symbols) == PRE_SYMBOLS_SHA256, "PRE target-symbol export hash differs")
        formal.compare_to_base(
            functions, program, authority.base_functions, authority.base_program, "live PRE"
        )
        formal.validate_base_target_symbols(
            symbols,
            symbols_ready,
            tool=authority.symbol_tool,
            manifest=authority.manifest,
        )
    except (LivePromotionError, formal.ProofError, envelope.ProofError, ValueError, OSError) as exc:
        pre_errors.append(str(exc))

    try:
        require(sha256_file(functions) == POST_FUNCTIONS_SHA256, "POST function export hash differs")
        require(sha256_file(program) == POST_PROGRAM_SHA256, "POST program export hash differs")
        require(sha256_file(symbols) == POST_SYMBOLS_SHA256, "POST target-symbol export hash differs")
        _, base_rows = envelope.function_rows(authority.base_functions)
        formal.validate_applied_inventory(
            authority.base_functions,
            authority.base_program,
            functions,
            program,
            authority.manifest,
        )
        formal.validate_applied_target_symbols(
            symbols,
            symbols_ready,
            tool=authority.symbol_tool,
            manifest=authority.manifest,
            base_rows=base_rows,
            base_summary={
                "outsideTargetSymbols": BASE_OUTSIDE_SYMBOLS,
                "outsideTargetSymbolsSha256": BASE_OUTSIDE_SYMBOLS_SHA256,
            },
        )
    except (LivePromotionError, formal.ProofError, envelope.ProofError, ValueError, OSError) as exc:
        post_errors.append(str(exc))

    if not pre_errors and post_errors:
        return {"state": ProjectState.PRE, "reasons": []}
    if not post_errors and pre_errors:
        return {"state": ProjectState.POST, "reasons": []}
    return {
        "state": ProjectState.UNKNOWN,
        "reasons": [
            *(f"PRE: {message}" for message in pre_errors),
            *(f"POST: {message}" for message in post_errors),
        ],
    }


def observe_project(
    *,
    session_root: Path,
    label: str,
    project_root: Path,
    authority: Authority,
    environment: dict[str, str],
    cwd: Path,
) -> dict[str, object]:
    assert_quiescent(project_root)
    raw_before = project_snapshot(project_root)

    inventory_root = session_root / "runs" / f"{label}-inventory"
    functions = inventory_root / "functions.tsv"
    program = inventory_root / "program.tsv"
    inventory_result, inventory_text = run_contained(
        session_root=session_root,
        run_id=f"{label}-inventory",
        argv=envelope.inventory_argv(
            authority.headless, project_root, authority.inventory_tool, functions, program
        ),
        cwd=cwd,
        environment=environment,
        timeout_seconds=600,
    )
    require_success(inventory_result, f"{label} inventory")
    require(functions.is_file() and program.is_file(), f"{label} inventory outputs are absent")
    envelope.require_clean_success_log(inventory_text, f"{label} inventory")
    envelope.require_log_identity(inventory_text, "INVENTORY_TOOL_OK", authority.inventory_tool)

    assert_quiescent(project_root)
    symbol_root = session_root / "runs" / f"{label}-symbols"
    symbols = symbol_root / "target-symbols.tsv"
    symbols_ready = symbol_root / "target-symbols.ready.json"
    symbol_result, symbol_text = run_contained(
        session_root=session_root,
        run_id=f"{label}-symbols",
        argv=batch.target_symbol_argv(
            authority.headless,
            project_root,
            authority.symbol_tool,
            authority.manifest,
            TARGET_COUNT,
            symbols,
            symbols_ready,
        ),
        cwd=cwd,
        environment=environment,
        timeout_seconds=600,
    )
    require_success(symbol_result, f"{label} target-symbol inventory")
    require(symbols.is_file() and symbols_ready.is_file(), f"{label} target-symbol outputs are absent")
    envelope.require_clean_success_log(symbol_text, f"{label} target symbols")
    envelope.require_log_identity(symbol_text, "TARGET_SYMBOL_TOOL_OK", authority.symbol_tool)
    batch.validate_target_symbol_ready(
        symbols_ready,
        symbols,
        tool=authority.symbol_tool,
        manifest=authority.manifest,
        count=TARGET_COUNT,
    )

    assert_quiescent(project_root)
    raw_after = project_snapshot(project_root)
    raw_stable = same_project_snapshot(raw_before, raw_after)
    classification = classify_exports(
        authority=authority,
        functions=functions,
        program=program,
        symbols=symbols,
        symbols_ready=symbols_ready,
        raw_stable=raw_stable,
    )
    receipt = {
        "schema": OBSERVATION_SCHEMA,
        "label": label,
        "observedAtUtc": utc_now(),
        "projectRoot": str(project_root.resolve()),
        "rawBefore": raw_before,
        "rawAfter": raw_after,
        "rawStable": raw_stable,
        "functions": relative_stamp(functions, session_root),
        "program": relative_stamp(program, session_root),
        "symbols": relative_stamp(symbols, session_root),
        "symbolsReady": relative_stamp(symbols_ready, session_root),
        "inventoryRun": inventory_result["receipt"],
        "symbolRun": symbol_result["receipt"],
        "classification": classification,
    }
    receipt_path = session_root / "observations" / f"{label}.json"
    write_json_new(receipt_path, receipt)
    return {**receipt, "receipt": relative_stamp(receipt_path, session_root)}


def require_state(observation: Mapping[str, object], state: ProjectState, label: str) -> None:
    actual = observation.get("classification", {}).get("state")
    require(actual == state, f"{label} is {actual}, expected {state}")


def copy_and_drill(
    *,
    session_root: Path,
    label: str,
    source: Path,
    backup_root: Path,
    restore_root: Path,
    expected_state: ProjectState,
    authority: Authority,
    environment: dict[str, str],
    cwd: Path,
) -> dict[str, object]:
    source_before = project_snapshot(source)
    try:
        copied = backup.copy_project_pair(source, backup_root, PROJECT_NAME)
    except (backup.BackupError, OSError) as exc:
        raise LivePromotionError(f"{label} backup copy failed: {exc}") from exc
    source_after = project_snapshot(source)
    require(same_project_snapshot(source_before, source_after), f"{label} source changed during backup")
    backup_snapshot = project_snapshot(backup_root)
    require(same_project_snapshot(source_before, backup_snapshot), f"{label} backup bytes differ")
    require_disjoint_project_files(source, backup_root)
    backup_observation = observe_project(
        session_root=session_root,
        label=f"{label}-backup",
        project_root=backup_root,
        authority=authority,
        environment=environment,
        cwd=cwd,
    )
    require_state(backup_observation, expected_state, f"{label} backup")

    try:
        backup.copy_project_pair(backup_root, restore_root, PROJECT_NAME)
    except (backup.BackupError, OSError) as exc:
        raise LivePromotionError(f"{label} restore drill copy failed: {exc}") from exc
    restore_snapshot = project_snapshot(restore_root)
    require(same_project_snapshot(source_before, restore_snapshot), f"{label} restore drill bytes differ")
    require_disjoint_project_files(source, restore_root)
    require_disjoint_project_files(backup_root, restore_root)
    restore_observation = observe_project(
        session_root=session_root,
        label=f"{label}-restore",
        project_root=restore_root,
        authority=authority,
        environment=environment,
        cwd=cwd,
    )
    require_state(restore_observation, expected_state, f"{label} restore drill")
    return {
        "sourceSnapshot": source_before,
        "backupRoot": str(backup_root.resolve()),
        "backupSnapshot": backup_snapshot,
        "restoreRoot": str(restore_root.resolve()),
        "restoreSnapshot": restore_snapshot,
        "copyManifest": relative_stamp(copied.manifest_path, session_root),
        "backupObservation": backup_observation["receipt"],
        "restoreObservation": restore_observation["receipt"],
        "expectedState": expected_state,
    }


def authority_summary(authority: Authority) -> dict[str, object]:
    return {
        "formalReady": {"path": str(authority.formal_ready), "sha256": FORMAL_READY_SHA256},
        "manifest": {"path": str(authority.manifest), "sha256": MANIFEST_SHA256, "count": TARGET_COUNT},
        "lineageReady": {"path": str(LINEAGE_ROOT / 'READY.json'), "sha256": LINEAGE_READY_SHA256},
        "campaignReady": {"path": str(CAMPAIGN_ROOT / 'campaign.ready.json'), "sha256": CAMPAIGN_READY_SHA256},
        "program": {
            "name": PROGRAM_NAME,
            "md5": envelope.PROGRAM_MD5,
            "sha256": envelope.PROGRAM_SHA256,
            "imageBase": envelope.IMAGE_BASE,
        },
        "liveProject": str(LIVE_PROJECT_ROOT.resolve()),
    }


def prepare(*, owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    require(not owner_root.exists(), f"live preparation root already exists: {owner_root}")
    with acquire_mutex() as lease:
        authority = load_authority()
        first_quiescence = assert_quiescent()
        envelope.ensure_plain_directory(owner_root, "live preparation root")
        environment, cwd = environment_for(owner_root, authority)
        reproductions = verify_authority_reproductions(owner_root, authority, environment, cwd)
        assert_quiescent()
        initial = observe_project(
            session_root=owner_root,
            label="live-pre-initial",
            project_root=LIVE_PROJECT_ROOT,
            authority=authority,
            environment=environment,
            cwd=cwd,
        )
        require_state(initial, ProjectState.PRE, "maintainer project initial observation")
        preimage = initial["rawAfter"]
        pre_backup = copy_and_drill(
            session_root=owner_root,
            label="pre-live",
            source=LIVE_PROJECT_ROOT,
            backup_root=owner_root / "backups/pre-live",
            restore_root=owner_root / "backups/pre-live-restore-drill",
            expected_state=ProjectState.PRE,
            authority=authority,
            environment=environment,
            cwd=cwd,
        )
        final = observe_project(
            session_root=owner_root,
            label="live-pre-final",
            project_root=LIVE_PROJECT_ROOT,
            authority=authority,
            environment=environment,
            cwd=cwd,
        )
        require_state(final, ProjectState.PRE, "maintainer project final observation")
        require(same_project_snapshot(preimage, final["rawAfter"]), "live PRE raw project changed during preparation")
        final_quiescence = assert_quiescent()
        ready = {
            "schema": PREPARED_SCHEMA,
            "status": "READY",
            "preparedAtUtc": utc_now(),
            "owner": {
                "path": str(Path(__file__).resolve()),
                "sha256": sha256_file(Path(__file__).resolve()),
            },
            "mutex": {"name": lease.name, "abandoned": lease.abandoned},
            "authority": authority_summary(authority),
            "reproductions": reproductions,
            "firstQuiescence": first_quiescence,
            "finalQuiescence": final_quiescence,
            "livePreimage": preimage,
            "initialObservation": initial["receipt"],
            "finalObservation": final["receipt"],
            "preBackup": pre_backup,
            "policies": [
                "No mutating Ghidra process was spawned during preparation.",
                "Only the fixed maintainer project and exact 515 manifest are eligible.",
                "An apply intent permanently forbids retry; recovery is observation-only.",
                "No automatic restore is authorized for PRE, POST, or UNKNOWN.",
            ],
        }
        ready_path = owner_root / "prepared.ready.json"
        write_json_new(ready_path, ready)
        return {**ready, "ready": str(ready_path), "readySha256": sha256_file(ready_path)}


def verify_prepared(owner_root: Path, authority: Authority) -> dict[str, object]:
    try:
        ready_path = scratch.require_plain_file(
            owner_root / "prepared.ready.json",
            "prepared READY",
            single_link=True,
        )
    except (scratch.ProofError, OSError) as exc:
        raise LivePromotionError(str(exc)) from exc
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    require(ready.get("schema") == PREPARED_SCHEMA and ready.get("status") == "READY", "prepared READY identity differs")
    require(ready.get("authority") == authority_summary(authority), "prepared authority differs")
    owner = ready.get("owner", {})
    require(owner.get("path") == str(Path(__file__).resolve()), "prepared owner path differs")
    require(owner.get("sha256") == sha256_file(Path(__file__).resolve()), "prepared owner bytes differ")
    require(
        re.fullmatch(r"\d{4}-\d{2}-\d{2}T[^\s]+", str(ready.get("preparedAtUtc", "")))
        is not None,
        "prepared timestamp differs",
    )
    require(
        ready.get("mutex") == {"name": MUTEX_NAME, "abandoned": False},
        "prepared mutex differs",
    )
    reproductions = ready.get("reproductions")
    require(isinstance(reproductions, dict), "prepared authority reproductions are absent")
    for label in ("formal", "lineage", "campaign"):
        reproduction = reproductions.get(label)
        require(isinstance(reproduction, dict), f"prepared {label} reproduction is absent")
        validate_process_receipt(
            reproduction.get("run"), owner_root, f"prepared {label} authority verifier"
        )
        payload = reproduction.get("result")
        require(isinstance(payload, dict), f"prepared {label} authority result is absent")
        if label == "formal":
            require(
                payload.get("verdict") == "SURVIVED"
                and payload.get("admissibleTargets") == TARGET_COUNT
                and payload.get("publicationStatus") == "READY",
                "prepared formal authority result differs",
            )
        elif label == "lineage":
            require(
                payload.get("status") == "READY"
                and payload.get("summary", {}).get("rows") == TARGET_COUNT,
                "prepared lineage authority result differs",
            )
        else:
            require(
                payload.get("generation") == 5
                and payload.get("counts", {}).get("functions") == 7595
                and payload.get("counts", {}).get("residuals") == 6618,
                "prepared campaign authority result differs",
            )
    live_preimage = ready.get("livePreimage")
    require(
        isinstance(live_preimage, dict)
        and live_preimage.get("root") == str(LIVE_PROJECT_ROOT.resolve())
        and isinstance(live_preimage.get("files"), list)
        and re.fullmatch(r"[0-9a-f]{64}", str(live_preimage.get("fileSetSha256", ""))) is not None,
        "prepared live PRE snapshot is malformed",
    )
    for label in ("firstQuiescence", "finalQuiescence"):
        quiescence = ready.get(label)
        require(isinstance(quiescence, dict), f"prepared {label} is absent")
        require(
            re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T[^\s]+",
                str(quiescence.get("checkedAtUtc", "")),
            )
            is not None
            and quiescence.get("javaProcesses") == []
            and quiescence.get("nativeLockAbsent") is True
            and quiescence.get("exclusiveFilesProbed")
            == live_preimage.get("fileCount")
            and quiescence.get("projectFileSetSha256")
            == live_preimage.get("fileSetSha256"),
            f"prepared {label} differs",
        )
    for label in ("initialObservation", "finalObservation"):
        observation = validate_observation_receipt(
            ready.get(label),
            owner_root,
            label,
            authority=authority,
            expected_state=ProjectState.PRE,
            expected_project_root=LIVE_PROJECT_ROOT,
        )
        require(
            same_project_snapshot(live_preimage, observation.get("rawAfter", {})),
            f"{label} raw PRE snapshot differs",
        )
    pre_backup = ready.get("preBackup")
    require(isinstance(pre_backup, dict), "prepared PRE backup is absent")
    backup_root = Path(str(pre_backup.get("backupRoot", "")))
    restore_root = Path(str(pre_backup.get("restoreRoot", "")))
    require(
        pre_backup.get("expectedState") == ProjectState.PRE,
        "prepared PRE backup expected state differs",
    )
    require(
        len(
            {
                str(LIVE_PROJECT_ROOT.resolve()),
                str(backup_root.resolve()),
                str(restore_root.resolve()),
            }
        )
        == 3,
        "prepared PRE live/backup/restore roots are not disjoint",
    )
    source_snapshot = pre_backup.get("sourceSnapshot")
    backup_snapshot_value = pre_backup.get("backupSnapshot")
    restore_snapshot_value = pre_backup.get("restoreSnapshot")
    require(
        isinstance(source_snapshot, dict)
        and source_snapshot.get("root") == str(LIVE_PROJECT_ROOT.resolve())
        and same_project_snapshot(live_preimage, source_snapshot),
        "prepared PRE source snapshot differs from live preimage",
    )
    require(
        isinstance(backup_snapshot_value, dict)
        and backup_snapshot_value.get("root") == str(backup_root.resolve())
        and isinstance(restore_snapshot_value, dict)
        and restore_snapshot_value.get("root") == str(restore_root.resolve()),
        "prepared PRE backup/restore snapshot roots differ",
    )
    backup_snapshot = validate_project_snapshot(
        backup_snapshot_value, backup_root, "prepared PRE backup"
    )
    restore_snapshot = validate_project_snapshot(
        restore_snapshot_value, restore_root, "prepared PRE restore drill"
    )
    require(
        same_project_snapshot(live_preimage, backup_snapshot)
        and same_project_snapshot(live_preimage, restore_snapshot),
        "prepared PRE backup/restore differs from live preimage",
    )
    require_disjoint_project_files(LIVE_PROJECT_ROOT, backup_root)
    require_disjoint_project_files(LIVE_PROJECT_ROOT, restore_root)
    require_disjoint_project_files(backup_root, restore_root)
    validate_relative_stamp(pre_backup.get("copyManifest"), owner_root, "prepared PRE backup manifest")
    backup_observation = validate_observation_receipt(
        pre_backup.get("backupObservation"),
        owner_root,
        "prepared PRE backup observation",
        authority=authority,
        expected_state=ProjectState.PRE,
        expected_project_root=backup_root,
    )
    restore_observation = validate_observation_receipt(
        pre_backup.get("restoreObservation"),
        owner_root,
        "prepared PRE restore observation",
        authority=authority,
        expected_state=ProjectState.PRE,
        expected_project_root=restore_root,
    )
    require(
        same_project_snapshot(live_preimage, backup_observation["rawAfter"]),
        "prepared PRE backup observation bytes differ",
    )
    require(
        same_project_snapshot(live_preimage, restore_observation["rawAfter"]),
        "prepared PRE restore observation bytes differ",
    )
    return ready


def validate_apply_protocol(
    *,
    authority: Authority,
    process: Mapping[str, object],
    text: str,
    output: Path,
    ready: Path,
) -> dict[str, object]:
    reasons: list[str] = []
    try:
        require_success(process, "live apply")
        require(output.is_file() and ready.is_file(), "live apply artifacts are absent")
        require(sha256_file(output) == APPLY_OUTPUT_SHA256, "live apply TSV differs")
        envelope.require_clean_success_log(text, "live apply")
        envelope.require_log_identity(text, "FUNCTION_ENVELOPE_TOOL_OK", authority.envelope_tool)
        _, base_rows = envelope.function_rows(authority.base_functions)
        formal.validate_output(
            output,
            authority.manifest,
            mode="apply",
            base_rows=base_rows,
        )
        formal.validate_java_ready(
            ready,
            output,
            mode="apply",
            tool=authority.envelope_tool,
            manifest=authority.manifest,
            count=TARGET_COUNT,
        )
    except (LivePromotionError, formal.ProofError, envelope.ProofError, ValueError, OSError) as exc:
        reasons.append(str(exc))
    return {"status": "COMPLETE" if not reasons else "PARTIAL", "reasons": reasons}


def publication_authorized(
    state: ProjectState,
    protocol: Mapping[str, object],
    post_backup: Mapping[str, object] | None,
) -> bool:
    return bool(
        state == ProjectState.POST
        and protocol.get("status") == "COMPLETE"
        and post_backup is not None
    )


def execute_apply_once(
    *,
    promotion_root: Path,
    attempt: Mapping[str, object],
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
    runner: Callable[..., tuple[dict[str, object], str]] = run_contained,
    quiescence: Callable[[], dict[str, object]] = assert_quiescent,
) -> tuple[Path, dict[str, object], str]:
    intent_path = promotion_root / "attempt.started.json"
    require(not intent_path.exists(), "apply intent already exists; mutation retry is forbidden")
    write_json_new(intent_path, dict(attempt))
    quiescence()
    process, text = runner(
        session_root=promotion_root,
        run_id="live-apply",
        argv=argv,
        cwd=cwd,
        environment=environment,
        timeout_seconds=900,
    )
    return intent_path, process, text


def promote(*, owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    promotion_root = owner_root / "promotion"
    require(not promotion_root.exists(), "promotion attempt already exists; use recover-status")
    with acquire_mutex() as lease:
        authority = load_authority()
        prepared = verify_prepared(owner_root, authority)
        assert_quiescent()
        envelope.ensure_plain_directory(promotion_root, "promotion attempt root")
        environment, cwd = environment_for(promotion_root, authority)
        reproductions = verify_authority_reproductions(promotion_root, authority, environment, cwd)
        live_pre = observe_project(
            session_root=promotion_root,
            label="live-immediate-pre",
            project_root=LIVE_PROJECT_ROOT,
            authority=authority,
            environment=environment,
            cwd=cwd,
        )
        require_state(live_pre, ProjectState.PRE, "live immediate preimage")
        require(
            same_project_snapshot(prepared["livePreimage"], live_pre["rawAfter"]),
            "live raw preimage differs from preparation",
        )
        pre_backup = prepared["preBackup"]
        for label, root_key in (("pre-backup-recheck", "backupRoot"), ("pre-restore-recheck", "restoreRoot")):
            observation = observe_project(
                session_root=promotion_root,
                label=label,
                project_root=Path(str(pre_backup[root_key])),
                authority=authority,
                environment=environment,
                cwd=cwd,
            )
            require_state(observation, ProjectState.PRE, label)

        apply_root = promotion_root / "runs/live-apply"
        output = apply_root / "envelopes.tsv"
        java_ready = apply_root / "envelopes.ready.json"
        argv = envelope.envelope_argv(
            authority.headless,
            LIVE_PROJECT_ROOT,
            authority.envelope_tool,
            authority.manifest,
            MANIFEST_SHA256,
            TARGET_COUNT,
            output,
            java_ready,
            "apply",
        )
        attempt = {
            "schema": ATTEMPT_SCHEMA,
            "startedAtUtc": utc_now(),
            "preparedReady": relative_stamp(owner_root / "prepared.ready.json", owner_root),
            "livePreimage": live_pre["rawAfter"],
            "argv": argv,
            "mutationSpawnLimit": 1,
            "retryAuthorized": False,
            "mutex": {"name": lease.name, "abandoned": lease.abandoned},
        }
        intent_path, process, text = execute_apply_once(
            promotion_root=promotion_root,
            attempt=attempt,
            argv=argv,
            cwd=cwd,
            environment=environment,
        )
        protocol = validate_apply_protocol(
            authority=authority,
            process=process,
            text=text,
            output=output,
            ready=java_ready,
        )

        observation: dict[str, object] | None = None
        observation_error = ""
        try:
            assert_quiescent()
            observation = observe_project(
                session_root=promotion_root,
                label="live-post-attempt",
                project_root=LIVE_PROJECT_ROOT,
                authority=authority,
                environment=environment,
                cwd=cwd,
            )
            state = ProjectState(observation["classification"]["state"])
        except (LivePromotionError, formal.ProofError, envelope.ProofError, OSError, ValueError) as exc:
            state = ProjectState.UNKNOWN
            observation_error = str(exc)

        post_backup: dict[str, object] | None = None
        post_backup_error = ""
        if state == ProjectState.POST:
            try:
                post_backup = copy_and_drill(
                    session_root=promotion_root,
                    label="post-live",
                    source=LIVE_PROJECT_ROOT,
                    backup_root=promotion_root / "backups/post-live",
                    restore_root=promotion_root / "backups/post-live-restore-drill",
                    expected_state=ProjectState.POST,
                    authority=authority,
                    environment=environment,
                    cwd=cwd,
                )
            except (LivePromotionError, formal.ProofError, envelope.ProofError, OSError, ValueError) as exc:
                post_backup_error = str(exc)

        can_publish = publication_authorized(state, protocol, post_backup)
        result = {
            "schema": SCHEMA,
            "completedAtUtc": utc_now(),
            "state": state,
            "protocol": protocol,
            "process": process["receipt"],
            "attempt": relative_stamp(intent_path, promotion_root),
            "authorityReproductions": reproductions,
            "observation": observation.get("receipt") if observation else None,
            "observationError": observation_error,
            "postBackup": post_backup,
            "postBackupError": post_backup_error,
            "mutationSpawns": 1,
            "retryAuthorized": False,
            "automaticRestorePerformed": False,
            "campaignPublicationAuthorized": can_publish,
        }
        result_path = promotion_root / "promotion.result.json"
        write_json_new(result_path, result)
        if can_publish:
            ready_payload = {
                **result,
                "status": "READY",
                "result": relative_stamp(result_path, promotion_root),
            }
            ready_path = promotion_root / "promotion.ready.json"
            write_json_new(ready_path, ready_payload)
            result["ready"] = str(ready_path)
            result["readySha256"] = sha256_file(ready_path)
        return result


def recover_status(*, owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    recovery_root = owner_root / "recoveries" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    )
    envelope.ensure_plain_directory(recovery_root, "recovery root")
    state = ProjectState.UNKNOWN
    mutex: dict[str, object] = {"name": MUTEX_NAME, "abandoned": None}
    observation: dict[str, object] | None = None
    backup_status: dict[str, object] | None = None
    busy_reason = ""
    backup_error = ""
    try:
        with acquire_mutex(allow_abandoned=True) as lease:
            mutex = {"name": lease.name, "abandoned": lease.abandoned}
            authority: Authority | None = None
            prepared: dict[str, object] | None = None
            environment: dict[str, str] | None = None
            cwd: Path | None = None
            try:
                authority = load_authority()
                prepared = verify_prepared(owner_root, authority)
                environment, cwd = environment_for(recovery_root, authority)
                assert_quiescent()
                observation = observe_project(
                    session_root=recovery_root,
                    label="live-recovery",
                    project_root=LIVE_PROJECT_ROOT,
                    authority=authority,
                    environment=environment,
                    cwd=cwd,
                )
                state = ProjectState(observation["classification"]["state"])
                if state == ProjectState.PRE:
                    require(
                        same_project_snapshot(
                            prepared["livePreimage"], observation["rawAfter"]
                        ),
                        "recovery live PRE bytes differ from prepared preimage",
                    )
            except (
                LivePromotionError,
                formal.ProofError,
                envelope.ProofError,
                OSError,
                ValueError,
            ) as exc:
                busy_reason = str(exc)
                state = ProjectState.UNKNOWN

            if (
                state == ProjectState.PRE
                and authority is not None
                and prepared is not None
                and environment is not None
                and cwd is not None
            ):
                try:
                    pre = prepared["preBackup"]
                    backup_observation = observe_project(
                        session_root=recovery_root,
                        label="pre-backup-recovery",
                        project_root=Path(str(pre["backupRoot"])),
                        authority=authority,
                        environment=environment,
                        cwd=cwd,
                    )
                    require_state(
                        backup_observation, ProjectState.PRE, "recovery PRE backup"
                    )
                    require(
                        observation is not None
                        and same_project_snapshot(
                            observation["rawAfter"], backup_observation["rawAfter"]
                        ),
                        "recovery PRE backup bytes differ from live PRE",
                    )
                    backup_status = {
                        "state": "PRE",
                        "observation": backup_observation["receipt"],
                    }
                except (
                    LivePromotionError,
                    formal.ProofError,
                    envelope.ProofError,
                    OSError,
                    ValueError,
                ) as exc:
                    backup_error = str(exc)
            elif (
                state == ProjectState.POST
                and authority is not None
                and environment is not None
                and cwd is not None
            ):
                existing = owner_root / "promotion/backups/post-live"
                existing_restore = (
                    owner_root / "promotion/backups/post-live-restore-drill"
                )
                try:
                    if existing.is_dir():
                        post_observation = observe_project(
                            session_root=recovery_root,
                            label="post-backup-recovery",
                            project_root=existing,
                            authority=authority,
                            environment=environment,
                            cwd=cwd,
                        )
                        require_state(
                            post_observation,
                            ProjectState.POST,
                            "recovery POST backup",
                        )
                        require(
                            observation is not None
                            and same_project_snapshot(
                                observation["rawAfter"], post_observation["rawAfter"]
                            ),
                            "recovery POST backup bytes differ from live POST",
                        )
                        require(
                            existing_restore.is_dir(),
                            "recovery POST restore drill is absent",
                        )
                        restore_observation = observe_project(
                            session_root=recovery_root,
                            label="post-restore-recovery",
                            project_root=existing_restore,
                            authority=authority,
                            environment=environment,
                            cwd=cwd,
                        )
                        require_state(
                            restore_observation,
                            ProjectState.POST,
                            "recovery POST restore drill",
                        )
                        require(
                            same_project_snapshot(
                                observation["rawAfter"],
                                restore_observation["rawAfter"],
                            ),
                            "recovery POST restore bytes differ from live POST",
                        )
                        require_disjoint_project_files(
                            LIVE_PROJECT_ROOT, existing
                        )
                        require_disjoint_project_files(
                            LIVE_PROJECT_ROOT, existing_restore
                        )
                        require_disjoint_project_files(
                            existing, existing_restore
                        )
                        backup_status = {
                            "state": "POST",
                            "observation": post_observation["receipt"],
                            "restoreObservation": restore_observation["receipt"],
                        }
                    else:
                        backup_status = copy_and_drill(
                            session_root=recovery_root,
                            label="post-live-recovery",
                            source=LIVE_PROJECT_ROOT,
                            backup_root=recovery_root / "backups/post-live",
                            restore_root=(
                                recovery_root / "backups/post-live-restore-drill"
                            ),
                            expected_state=ProjectState.POST,
                            authority=authority,
                            environment=environment,
                            cwd=cwd,
                        )
                except (
                    LivePromotionError,
                    formal.ProofError,
                    envelope.ProofError,
                    OSError,
                    ValueError,
                ) as exc:
                    backup_error = str(exc)
    except (
        LivePromotionError,
        formal.ProofError,
        envelope.ProofError,
        OSError,
        ValueError,
    ) as exc:
        busy_reason = str(exc)
        state = ProjectState.UNKNOWN

    receipt = {
        "schema": RECOVERY_SCHEMA,
        "observedAtUtc": utc_now(),
        "state": state,
        "mutex": mutex,
        "observation": observation.get("receipt") if observation else None,
        "busyOrObservationError": busy_reason,
        "backupStatus": backup_status,
        "backupError": backup_error,
        "mutationSpawns": 0,
        "retryAuthorized": False,
        "automaticRestorePerformed": False,
    }
    receipt_path = recovery_root / "recovery.ready.json"
    write_json_new(receipt_path, receipt)
    return {**receipt, "ready": str(receipt_path), "readySha256": sha256_file(receipt_path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare")
    subparsers.add_parser("promote")
    subparsers.add_parser("recover-status")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare()
        elif args.command == "promote":
            result = promote()
        else:
            result = recover_status()
    except (
        LivePromotionError,
        formal.ProofError,
        envelope.ProofError,
        scratch.ProofError,
        backup.BackupError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
