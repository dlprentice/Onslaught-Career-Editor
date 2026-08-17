#!/usr/bin/env python3
"""Replay frozen campaigns under exact, reviewed historical source inputs.

Generation 24 is immutable, but two later rebuild improvements legitimately
changed source files that older campaign overlays identity-pin.  This launcher
keeps those layers separate: it first proves the exact current source and its
focused tests, then projects only the historical bytes into the frozen
verifier's read path.  It never writes projected bytes to the checkout and
never changes a campaign, proof, reducer, or Ghidra project.
"""

from __future__ import annotations

import argparse
import builtins
import contextlib
import csv
import difflib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

SCHEMA = "bea.re.campaign-historical-source-projection-audit.v2"
OLD_OWNER_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-replay-audit-20260812-v1/historical_source_projection.py"
)
OLD_OWNER_BYTES = 17_579
OLD_OWNER_SHA256 = (
    "e16faa93d2820f7c5a57d135dea1bcfec9818c683f2cca4057b9c43155673aec"
)

ACTOR_HISTORICAL_COMMIT = "e7aa7548fe99ff7866f57955624968b097375e20"
ACTOR_RUNTIME_RELATIVE = Path(
    "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs"
)
ACTOR_RUNTIME_HISTORICAL_BYTES = 31_466
ACTOR_RUNTIME_HISTORICAL_SHA256 = (
    "7942536b60d3bab2d0e534f2030fa74b4329b3bf9c2c19324e244c91aa33597b"
)
ACTOR_RUNTIME_CURRENT_BYTES = 32_010
ACTOR_RUNTIME_CURRENT_SHA256 = (
    "8f8692250e70eea6bea0702dfd56d1c3c90ad17dd8dffd65acf639cec4ba6197"
)
ACTOR_TEST_RELATIVE = Path(
    "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"
)
ACTOR_TEST_HISTORICAL_SOURCE_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-23-cround-handle-event-arm-effects-v1/_reducer/"
    "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"
)
ACTOR_TEST_HISTORICAL_BYTES = 17_883
ACTOR_TEST_HISTORICAL_SHA256 = (
    "2232bde202407035adc81317058b5594ad69e038d0889e8fb2762058d7e7529c"
)
ACTOR_TEST_CURRENT_BYTES = 17_484
ACTOR_TEST_CURRENT_SHA256 = (
    "cb64be81481a0d6712a13d7f7a16449974d38ba047617444b6f96c9d024c2bfc"
)
SIMULATION_TEST_RELATIVE = Path(
    "rebuild/OnslaughtRebuild.Core.Tests/SimulationTests.cs"
)
SIMULATION_TEST_CURRENT_BYTES = 77_231
SIMULATION_TEST_CURRENT_SHA256 = (
    "bbb31414efe6c36e7fd8ba52eafb4135995671863e91b0a59062874c2c40dd06"
)
CURRENT_FOCUSED_FILTER = (
    "FullyQualifiedName~Level100PlayerDamageTests|"
    "FullyQualifiedName~Level100ActorWeaponTests|"
    "FullyQualifiedName~SimulationTests."
    "PlayerProjectilesConsumeReleasedScatterInRetailDrawOrder"
)
PROOF_AUTHOR_BYTES = 41_785
PROOF_AUTHOR_SHA256 = (
    "8e8c22d3dbb31c7464ad47c211a5179d773aabd9dd665aa4960ee7aa7a0b47e9"
)
PROOF_READY_BYTES = 2_529
PROOF_READY_SHA256 = (
    "ffb2e0b8692ddada364a829d52a158841e5d800742c49bd2a1710b2af135869a"
)


TEST_PROJECT_RELATIVE = Path(
    "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj"
)
TEST_OUTPUT_RELATIVE = Path("rebuild/OnslaughtRebuild.Core.Tests/bin/Debug/net8.0")
TEST_OUTPUT_HELD_NAMES = (
    "OnslaughtRebuild.Core.dll",
    "OnslaughtRebuild.Client.dll",
    "OnslaughtRebuild.Headless.dll",
    "OnslaughtRebuild.Core.Tests.dll",
)
TEST_HOST_IMAGE_NAMES = ("testhost.exe", "vstest.console.exe")
FOCUSED_RUN_TIMEOUT_SECONDS = 300
FOCUSED_HANG_TIMEOUT = "120s"
BUILD_LOCK_SIGNATURES = ("MSB3027", "MSB3021", "MSB3026", "The file is locked by")


class ProjectionError(RuntimeError):
    """The current-source, historical-input, or replay gate did not hold."""


class StaleTestHostError(ProjectionError):
    """A surviving test host, not the change under test, blocked the suite.

    A leftover ``testhost`` keeps the test project's output assemblies open, so
    the next build fails its copy step with MSB3027/MSB3021 and ``dotnet test``
    exits non-zero without running a single test.  Reporting that as a test
    failure misattributes an environmental fault to the change under test, so it
    gets its own name and its own message.
    """


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProjectionError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, root: Path) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        display = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        display = os.fspath(resolved)
    return {
        "path": display,
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def _load_old_owner(root: Path) -> ModuleType:
    owner = root / OLD_OWNER_RELATIVE
    require(owner.is_file(), "historical Generation 12 projection owner is missing")
    info = owner.lstat()
    require(
        not owner.is_symlink()
        and not (getattr(info, "st_file_attributes", 0) & 0x400)
        and info.st_nlink == 1
        and (info.st_size, sha256_file(owner))
        == (OLD_OWNER_BYTES, OLD_OWNER_SHA256),
        "historical Generation 12 projection owner identity differs",
    )
    spec = importlib.util.spec_from_file_location(
        "_bea_historical_source_projection_v1", owner
    )
    require(spec is not None and spec.loader is not None, "cannot load v1 owner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exact_bytes(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> bytes:
    require(path.is_file(), f"{label} is missing")
    data = path.read_bytes()
    require(
        (len(data), sha256_bytes(data)) == (expected_bytes, expected_sha256),
        f"{label} identity differs",
    )
    return data


def validate_actor_continuity(
    root: Path, old_owner: ModuleType
) -> tuple[dict[Path, bytes], dict[str, Any]]:
    historical_runtime = old_owner.git_blob(
        root, ACTOR_HISTORICAL_COMMIT, ACTOR_RUNTIME_RELATIVE
    )
    require(
        (len(historical_runtime), sha256_bytes(historical_runtime))
        == (ACTOR_RUNTIME_HISTORICAL_BYTES, ACTOR_RUNTIME_HISTORICAL_SHA256),
        "historical actor-weapon runtime Git blob differs",
    )
    current_runtime = _exact_bytes(
        root / ACTOR_RUNTIME_RELATIVE,
        ACTOR_RUNTIME_CURRENT_BYTES,
        ACTOR_RUNTIME_CURRENT_SHA256,
        "current actor-weapon runtime",
    )

    historical_test_path = root / ACTOR_TEST_HISTORICAL_SOURCE_RELATIVE
    historical_test = _exact_bytes(
        historical_test_path,
        ACTOR_TEST_HISTORICAL_BYTES,
        ACTOR_TEST_HISTORICAL_SHA256,
        "retained historical actor-weapon test input",
    )
    current_test = _exact_bytes(
        root / ACTOR_TEST_RELATIVE,
        ACTOR_TEST_CURRENT_BYTES,
        ACTOR_TEST_CURRENT_SHA256,
        "current actor-weapon test",
    )
    require(
        historical_test.replace(b"\r\n", b"\n") == current_test,
        "historical actor-weapon test does not normalize to current Git bytes",
    )
    require(
        historical_test.count(b"\r\n") == 399
        and historical_test.count(b"\n") == 415,
        "historical actor-weapon mixed-EOL census differs",
    )
    _exact_bytes(
        root / SIMULATION_TEST_RELATIVE,
        SIMULATION_TEST_CURRENT_BYTES,
        SIMULATION_TEST_CURRENT_SHA256,
        "current simulation scatter test owner",
    )

    old_lines = historical_runtime.decode("utf-8").splitlines(keepends=True)
    new_lines = current_runtime.decode("utf-8").splitlines(keepends=True)
    opcodes = difflib.SequenceMatcher(None, old_lines, new_lines).get_opcodes()
    inserted = sum(
        j2 - j1
        for tag, _i1, _i2, j1, j2 in opcodes
        if tag in {"insert", "replace"}
    )
    deleted = sum(
        i2 - i1
        for tag, i1, i2, _j1, _j2 in opcodes
        if tag in {"delete", "replace"}
    )
    retained = sum(i2 - i1 for tag, i1, i2, _j1, _j2 in opcodes if tag == "equal")
    require(
        (inserted, deleted, retained, len(old_lines), len(new_lines))
        == (19, 6, 751, 757, 770),
        "reviewed actor-weapon helper-extraction line relationship differs",
    )

    return (
        {
            ACTOR_RUNTIME_RELATIVE: historical_runtime,
            ACTOR_TEST_RELATIVE: historical_test,
        },
        {
            "historicalCommit": ACTOR_HISTORICAL_COMMIT,
            "historicalRuntime": {
                "path": ACTOR_RUNTIME_RELATIVE.as_posix(),
                "bytes": len(historical_runtime),
                "sha256": sha256_bytes(historical_runtime),
            },
            "currentRuntime": stamp(root / ACTOR_RUNTIME_RELATIVE, root),
            "runtimeRelationship": {
                "classification": "EXACT_REVIEWED_HELPER_EXTRACTION",
                "insertedLines": inserted,
                "deletedLines": deleted,
                "historicalLinesRetained": retained,
                "behaviorEquivalenceClaimedByDiffAlone": False,
            },
            "historicalTest": stamp(historical_test_path, root),
            "currentTest": stamp(root / ACTOR_TEST_RELATIVE, root),
            "testRelationship": {
                "classification": "MIXED_EOL_SNAPSHOT_NORMALIZES_TO_GIT_BYTES",
                "crlfLineEndings": historical_test.count(b"\r\n"),
                "totalLineEndings": historical_test.count(b"\n"),
                "normalizedByteIdentical": True,
            },
            "currentSimulationScatterTest": stamp(
                root / SIMULATION_TEST_RELATIVE, root
            ),
        },
    )


def held_test_outputs(root: Path) -> list[str]:
    """Name every test output assembly a live process still holds open.

    This is the exact condition MSBuild's copy step hits, probed the same way:
    open the destination for writing.  A sharing violation means some process
    still has the assembly mapped.  Anything that is not a sharing violation is
    reported verbatim rather than swallowed, because a probe that cannot answer
    must not look like a clean answer.
    """

    held: list[str] = []
    for name in TEST_OUTPUT_HELD_NAMES:
        path = root / TEST_OUTPUT_RELATIVE / name
        if not path.is_file():
            continue
        try:
            with path.open("r+b"):
                pass
        except PermissionError as exc:
            held.append(f"{name} (locked: {exc.strerror or exc})")
        except OSError as exc:
            held.append(f"{name} (unprobeable: {exc})")
    return held


def live_test_hosts() -> tuple[list[tuple[str, int]], str | None]:
    """Census live test-host images, or say why the census is unavailable."""

    if sys.platform != "win32":
        return [], "process census is implemented for Windows only"
    found: list[tuple[str, int]] = []
    for image in TEST_HOST_IMAGE_NAMES:
        try:
            completed = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {image}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return found, f"tasklist failed for {image}: {exc}"
        if completed.returncode != 0:
            return found, (
                f"tasklist exited {completed.returncode} for {image}: "
                f"{completed.stderr.strip()!r}"
            )
        for row in csv.reader(io.StringIO(completed.stdout)):
            if len(row) >= 2 and row[0].lower() == image.lower():
                try:
                    found.append((row[0], int(row[1])))
                except ValueError:
                    return found, f"tasklist emitted a non-numeric pid: {row!r}"
    return found, None


def _describe_hosts(hosts: list[tuple[str, int]]) -> str:
    return ", ".join(f"{name}({pid})" for name, pid in hosts) or "none"


def preflight_test_host_guard(root: Path) -> None:
    """Refuse to start when a leftover test host already owns the outputs.

    Without this, the build's copy step fails and ``dotnet test`` exits non-zero
    before running a test, which the suite gate would otherwise report as
    "current focused rebuild suite failed".
    """

    held = held_test_outputs(root)
    if not held:
        return
    hosts, census_error = live_test_hosts()
    detail = [
        "STALE_TEST_HOST_DETECTED: the focused rebuild suite was not started "
        "because a live process still holds the test project's output "
        "assemblies open, so the build copy step would fail with "
        "MSB3027/MSB3021 before any test ran.",
        f"held={held}",
        f"testHosts={_describe_hosts(hosts)}",
        f"outputDirectory={(root / TEST_OUTPUT_RELATIVE).as_posix()}",
        "This is an environment fault, not a rebuild failure. Terminate the "
        "reported process tree (taskkill /T /F /PID <pid>) and rerun.",
    ]
    if census_error:
        detail.append(f"processCensusUnavailable={census_error}")
    raise StaleTestHostError(" ".join(detail))


_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9


def _kernel32() -> Any:
    """Return kernel32 with pointer-safe prototypes for the job-object calls."""

    import ctypes
    import ctypes.wintypes as wintypes

    library = ctypes.WinDLL("kernel32", use_last_error=True)
    library.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    library.CreateJobObjectW.restype = ctypes.c_void_p
    library.SetInformationJobObject.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    library.SetInformationJobObject.restype = wintypes.BOOL
    library.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    library.AssignProcessToJobObject.restype = wintypes.BOOL
    library.TerminateJobObject.argtypes = [ctypes.c_void_p, wintypes.UINT]
    library.TerminateJobObject.restype = wintypes.BOOL
    library.CloseHandle.argtypes = [ctypes.c_void_p]
    library.CloseHandle.restype = wintypes.BOOL
    return library


def _extended_limit_structure() -> Any:
    import ctypes

    class BasicLimit(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class ExtendedLimit(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimit),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    return ExtendedLimit


def adopt_process_tree(process: subprocess.Popen[str]) -> tuple[int | None, list[str]]:
    """Put the child in a kill-on-close job object; report what happened.

    ``KILL_ON_JOB_CLOSE`` is the only mechanism that also survives the parent
    dying without running any Python cleanup: the handle closes with the process
    and Windows terminates every process still in the job.  Every failure is
    reported instead of suppressed, so a lane never assumes ownership it does
    not have.
    """

    notes: list[str] = []
    if sys.platform != "win32":
        notes.append("job-object ownership is Windows-only; not adopted")
        return None, notes
    import ctypes

    try:
        kernel32 = _kernel32()
        limit_type = _extended_limit_structure()
    except (OSError, AttributeError) as exc:  # pragma: no cover - CPython ships ctypes
        notes.append(f"job-object interface unavailable: {exc!r}")
        return None, notes
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        notes.append(f"CreateJobObjectW failed: winerror={ctypes.get_last_error()}")
        return None, notes
    limits = limit_type()
    limits.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        job,
        _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(limits),
        ctypes.sizeof(limits),
    ):
        notes.append(
            "SetInformationJobObject(KILL_ON_JOB_CLOSE) failed: "
            f"winerror={ctypes.get_last_error()}"
        )
        kernel32.CloseHandle(job)
        return None, notes
    handle = getattr(process, "_handle", None)
    if handle is None:
        notes.append("child process handle is unavailable; job not assigned")
        kernel32.CloseHandle(job)
        return None, notes
    if not kernel32.AssignProcessToJobObject(job, int(handle)):
        notes.append(
            f"AssignProcessToJobObject failed for pid={process.pid}: "
            f"winerror={ctypes.get_last_error()}"
        )
        kernel32.CloseHandle(job)
        return None, notes
    notes.append(f"job object owns pid={process.pid} with KILL_ON_JOB_CLOSE")
    return int(job), notes


def _close_job(job: int | None) -> list[str]:
    if job is None:
        return []
    import ctypes

    if not _kernel32().CloseHandle(job):
        return [f"CloseHandle(job) failed: winerror={ctypes.get_last_error()}"]
    return ["job handle closed"]


def terminate_process_tree(
    root: Path, process: subprocess.Popen[str], job: int | None
) -> list[str]:
    """Kill the child and every descendant, then verify and report the result.

    Killing only the direct child is what orphans a ``testhost``.  This kills
    the whole tree, waits, re-enumerates, and states plainly whether anything is
    still alive.  Nothing here suppresses an error: a failed kill must be
    visible, because a silently failed kill is how an orphan survives a cleanup
    and poisons the next build.
    """

    report: list[str] = []
    before, census_error = live_test_hosts()
    report.append(f"testHostsBeforeKill={_describe_hosts(before)}")
    if census_error:
        report.append(f"processCensusUnavailable={census_error}")

    if sys.platform == "win32":
        try:
            killed = subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            report.append(
                f"taskkill /T /F /PID {process.pid} exit={killed.returncode} "
                f"stdout={killed.stdout.strip()!r} stderr={killed.stderr.strip()!r}"
            )
        except (OSError, subprocess.SubprocessError) as exc:
            report.append(f"taskkill /T /F /PID {process.pid} raised {exc!r}")
    if job is not None:
        import ctypes

        if _kernel32().TerminateJobObject(job, 1):
            report.append("TerminateJobObject succeeded")
        else:
            report.append(
                f"TerminateJobObject failed: winerror={ctypes.get_last_error()}"
            )
    try:
        process.kill()
    except OSError as exc:
        report.append(f"direct child kill raised {exc!r}")
    try:
        process.wait(timeout=120)
        report.append(f"direct child pid={process.pid} exited")
    except subprocess.TimeoutExpired:
        report.append(f"direct child pid={process.pid} IS STILL ALIVE after kill")

    after, after_error = live_test_hosts()
    held = held_test_outputs(root)
    if after_error:
        report.append(f"processCensusUnavailableAfterKill={after_error}")
    if after or held:
        report.append(
            "STILL ALIVE after cleanup: "
            f"testHosts={_describe_hosts(after)} heldOutputs={held}"
        )
    else:
        report.append("cleanup verified: no test host alive, no output assembly held")
    return report


def run_focused_suite(
    root: Path,
) -> tuple[subprocess.CompletedProcess[str], list[str], Path]:
    """Run the focused rebuild suite so it cannot leave an orphan behind."""

    results = Path(tempfile.mkdtemp(prefix="bea-focused-results-"))
    command = [
        "dotnet",
        "test",
        os.fspath(TEST_PROJECT_RELATIVE),
        "--filter",
        CURRENT_FOCUSED_FILTER,
        "--no-restore",
        "--nologo",
        "--results-directory",
        os.fspath(results),
        "--blame-hang-timeout",
        FOCUSED_HANG_TIMEOUT,
    ]
    environment = os.environ.copy()
    environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    environment["VSTEST_HOST_DEBUG"] = "0"
    process = subprocess.Popen(
        command,
        cwd=root,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    job, notes = adopt_process_tree(process)
    try:
        try:
            stdout, stderr = process.communicate(
                timeout=FOCUSED_RUN_TIMEOUT_SECONDS
            )
        except BaseException as exc:
            notes.extend(terminate_process_tree(root, process, job))
            with contextlib.suppress(Exception):
                process.communicate(timeout=60)
            if isinstance(exc, subprocess.TimeoutExpired):
                raise ProjectionError(
                    "current focused rebuild suite exceeded "
                    f"{FOCUSED_RUN_TIMEOUT_SECONDS}s and its process tree was "
                    f"terminated: results={results.as_posix()} "
                    f"cleanup={'; '.join(notes)}"
                ) from exc
            raise
    finally:
        notes.extend(_close_job(job))
    completed = subprocess.CompletedProcess(
        command, process.returncode, stdout, stderr
    )
    return completed, notes, results


def validate_current(root: Path, old_owner: ModuleType) -> dict[str, Any]:
    preflight_test_host_guard(root)
    completed, cleanup_notes, results = run_focused_suite(root)
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        held = held_test_outputs(root)
        signatures = [
            signature
            for signature in BUILD_LOCK_SIGNATURES
            if signature in output
        ]
        if held or signatures:
            hosts, census_error = live_test_hosts()
            detail = [
                "STALE_TEST_HOST_DETECTED: the focused rebuild suite could not "
                "build because a live process holds the test project's output "
                "assemblies open; no test verdict was produced.",
                f"exit={completed.returncode}",
                f"buildLockSignatures={signatures}",
                f"held={held}",
                f"testHosts={_describe_hosts(hosts)}",
                f"resultsDirectory={results.as_posix()}",
                f"cleanup={'; '.join(cleanup_notes)}",
                "This is an environment fault, not a rebuild failure. Terminate "
                "the reported process tree and rerun.",
            ]
            if census_error:
                detail.append(f"processCensusUnavailable={census_error}")
            raise StaleTestHostError(" ".join(detail))
        raise ProjectionError(
            "current focused rebuild suite failed: "
            f"exit={completed.returncode} results={results.as_posix()} "
            f"tail={output[-1200:]!r}"
        )
    shutil.rmtree(results, ignore_errors=True)
    match = re.search(
        r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)",
        output,
    )
    require(match is not None, "current focused rebuild census is absent")
    failed, passed, skipped, total = map(int, match.groups())
    require(
        (failed, passed, skipped, total) == (0, 30, 0, 30),
        "current focused rebuild census differs",
    )
    proof_author = root / old_owner.PROOF_AUTHOR_RELATIVE
    proof_ready = root / old_owner.PROOF_ROOT_RELATIVE / "proof.ready.json"
    _exact_bytes(
        proof_author,
        PROOF_AUTHOR_BYTES,
        PROOF_AUTHOR_SHA256,
        "frozen player-damage proof author",
    )
    _exact_bytes(
        proof_ready,
        PROOF_READY_BYTES,
        PROOF_READY_SHA256,
        "frozen player-damage proof receipt",
    )
    current_player_test = root / old_owner.TEST_RELATIVE
    require(
        sha256_file(current_player_test) != old_owner.HISTORICAL_TEST_SHA256,
        "current player-damage test unexpectedly equals the historical input",
    )
    return {
        "focusedRebuild": {
            "exitCode": completed.returncode,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": total,
            "filter": CURRENT_FOCUSED_FILTER,
            "stdoutSha256": sha256_bytes(completed.stdout.encode("utf-8")),
            "stderrSha256": sha256_bytes(completed.stderr.encode("utf-8")),
            "runTimeoutSeconds": FOCUSED_RUN_TIMEOUT_SECONDS,
            "hangTimeout": FOCUSED_HANG_TIMEOUT,
            "processTreeOwnership": cleanup_notes,
            "staleTestHostPreflightPassed": True,
        },
        "frozenPlayerDamageProof": {
            "author": stamp(proof_author, root),
            "receipt": stamp(proof_ready, root),
            "expectsHistoricalTestSha256": old_owner.HISTORICAL_TEST_SHA256,
            "currentTestSha256": sha256_file(current_player_test),
            "currentIdentityRejectedByExactInputGate": True,
        },
    }


def is_bootstrap_invocation(arguments: object) -> tuple[list[str], int] | None:
    if not isinstance(arguments, (list, tuple)):
        return None
    values = [os.fspath(value) for value in arguments]
    for index, value in enumerate(values):
        if value.replace("\\", "/").lower().endswith(
            "/re_campaign_frozen_bootstrap.py"
        ):
            return values, index
    return None


def replay_with_projections(
    root: Path,
    projections: dict[Path, bytes],
    campaign: Path,
    mode: str,
    expected_ready_sha256: str,
    expected_reducer_id: str,
    old_owner: ModuleType,
) -> tuple[int, str, str]:
    bootstrap_path = root / old_owner.BOOTSTRAP_RELATIVE
    require(
        (bootstrap_path.stat().st_size, sha256_file(bootstrap_path))
        == (old_owner.BOOTSTRAP_BYTES, old_owner.BOOTSTRAP_SHA256),
        "frozen bootstrap identity differs",
    )
    resolved = {
        os.path.normcase(os.fspath((root / relative).resolve())): data
        for relative, data in projections.items()
    }
    original_path_open = pathlib.Path.open
    original_path_stat = pathlib.Path.stat
    original_builtin_open = builtins.open
    original_subprocess_run = subprocess.run

    def projected_data(path: os.PathLike[str] | str) -> bytes | None:
        key = os.path.normcase(os.path.abspath(os.fspath(path)))
        return resolved.get(key)

    def projected_open(
        self: pathlib.Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        data = projected_data(self)
        if data is None:
            return original_path_open(
                self, mode, buffering, encoding, errors, newline
            )
        if any(flag in mode for flag in "wax+"):
            raise OSError("historical source projection is read-only")
        if "b" in mode:
            return io.BytesIO(data)
        return io.StringIO(
            data.decode(encoding or "utf-8", errors or "strict"), newline=newline
        )

    def projected_stat(
        self: pathlib.Path, *, follow_symlinks: bool = True
    ) -> os.stat_result:
        value = original_path_stat(self, follow_symlinks=follow_symlinks)
        data = projected_data(self)
        if data is None:
            return value
        fields = list(value)
        fields[6] = len(data)
        return os.stat_result(fields)

    def projected_builtin_open(
        file: int | os.PathLike[str] | str,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
        closefd: bool = True,
        opener: Any = None,
    ):
        data = None if isinstance(file, int) else projected_data(file)
        if data is None:
            return original_builtin_open(
                file, mode, buffering, encoding, errors, newline, closefd, opener
            )
        if any(flag in mode for flag in "wax+"):
            raise OSError("historical source projection is read-only")
        if "b" in mode:
            return io.BytesIO(data)
        return io.StringIO(
            data.decode(encoding or "utf-8", errors or "strict"), newline=newline
        )

    wrapper_path = Path(__file__).resolve()

    def projected_subprocess_run(
        arguments: object, *args: object, **kwargs: object
    ):
        detected = is_bootstrap_invocation(arguments)
        if detected is None:
            return original_subprocess_run(arguments, *args, **kwargs)
        values, index = detected
        replacement = [
            sys.executable,
            "-I",
            "-B",
            os.fspath(wrapper_path),
            *values[index + 1 :],
        ]
        return original_subprocess_run(replacement, *args, **kwargs)

    environment_start = os.environ.copy()
    cwd_start = Path.cwd()
    pathlib.Path.open = projected_open
    pathlib.Path.stat = projected_stat
    builtins.open = projected_builtin_open
    try:
        os.environ["BEA_REPO_ROOT"] = os.fspath(root)
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.chdir(root)
        spec = importlib.util.spec_from_file_location(
            "_bea_historical_source_projection_v2_bootstrap", bootstrap_path
        )
        require(spec is not None and spec.loader is not None, "cannot load bootstrap")
        bootstrap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bootstrap)
        bootstrap.ORIGINAL_SUBPROCESS_RUN = projected_subprocess_run
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = bootstrap.main(
                [
                    "--campaign",
                    os.fspath(campaign),
                    "--mode",
                    mode,
                    "--expected-ready-sha256",
                    expected_ready_sha256,
                    "--expected-reducer-id",
                    expected_reducer_id,
                ]
            )
        return exit_code, stdout.getvalue(), stderr.getvalue()
    finally:
        builtins.open = original_builtin_open
        pathlib.Path.open = original_path_open
        pathlib.Path.stat = original_path_stat
        os.chdir(cwd_start)
        os.environ.clear()
        os.environ.update(environment_start)


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing existing audit receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{path.name}.", dir=path.parent))
    try:
        staged = stage / path.name
        staged.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(staged, path)
    finally:
        try:
            stage.rmdir()
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--mode", choices=("full", "integrity"), default="full")
    parser.add_argument("--expected-ready-sha256", required=True)
    parser.add_argument("--expected-reducer-id", required=True)
    parser.add_argument("--check-current", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    try:
        configured = os.environ.get("BEA_REPO_ROOT")
        root = Path(configured).resolve() if configured else Path.cwd().resolve()
        require((root / ".git").exists(), "BEA repository root is not selected")
        campaign = args.campaign
        if not campaign.is_absolute():
            campaign = root / campaign
        campaign = campaign.resolve()
        ready_path = campaign / "campaign.ready.json"
        require(ready_path.is_file(), "campaign READY is missing")
        require(
            sha256_file(ready_path) == args.expected_ready_sha256.lower(),
            "campaign READY differs from the external pin",
        )
        ready = json.loads(ready_path.read_text(encoding="utf-8"))
        require(
            ready.get("reducer", {}).get("id") == args.expected_reducer_id,
            "campaign reducer differs from the external pin",
        )

        old_owner = _load_old_owner(root)
        try:
            historical_player_test, player_continuity = (
                old_owner.validate_continuity(root)
            )
            actor_projections, actor_continuity = validate_actor_continuity(
                root, old_owner
            )
        except old_owner.AuditError as exc:
            raise ProjectionError(str(exc)) from exc
        projections = {
            old_owner.TEST_RELATIVE: historical_player_test,
            **actor_projections,
        }
        current_validation = None
        if args.check_current:
            current_validation = validate_current(root, old_owner)

        before = {
            relative.as_posix(): (root / relative).read_bytes()
            for relative in projections
        }
        exit_code, stdout, stderr = replay_with_projections(
            root,
            projections,
            campaign,
            args.mode,
            args.expected_ready_sha256.lower(),
            args.expected_reducer_id,
            old_owner,
        )
        after = {
            relative.as_posix(): (root / relative).read_bytes()
            for relative in projections
        }
        require(before == after, "current source input changed during replay")
        marker = (
            "CAMPAIGN_VERIFIED"
            if args.mode == "full"
            else "FROZEN_CAMPAIGN_INTEGRITY_VERIFIED"
        )
        require(
            exit_code == 0 and marker in stdout,
            "projected frozen campaign replay failed: "
            f"exit={exit_code} stdout={stdout[-1200:]!r} stderr={stderr[-1200:]!r}",
        )

        receipt = {
            "schema": SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "verdict": "PASS",
            "instrument": stamp(Path(__file__), root),
            "generation12ProjectionOwner": stamp(root / OLD_OWNER_RELATIVE, root),
            "continuity": {
                "playerDamage": player_continuity,
                "actorWeapon": actor_continuity,
            },
            "currentValidation": current_validation,
            "projection": {
                "kind": "IN_MEMORY_READ_ONLY_THREE_FILE",
                "paths": [relative.as_posix() for relative in projections],
                "writesToCheckout": False,
                "frozenArtifactsChanged": False,
            },
            "campaign": {
                "root": os.fspath(campaign),
                "generation": ready.get("generation"),
                "mode": args.mode.upper(),
                "ready": stamp(ready_path, root),
                "reducerId": args.expected_reducer_id,
            },
            "result": {
                "exitCode": exit_code,
                "stdoutSha256": sha256_bytes(stdout.encode("utf-8")),
                "stderrSha256": sha256_bytes(stderr.encode("utf-8")),
                "marker": stdout.strip().splitlines()[-1],
            },
            "limitations": [
                "This proves the frozen campaign only under its exact historical source inputs; it does not repin or reinterpret Generation 24.",
                "Current rebuild behavior is checked only when --check-current is selected and only by the named focused suites.",
                "No executable, Ghidra project, runtime trace, or retail asset is mutated or reinterpreted by this projection.",
            ],
        }
        if args.receipt:
            receipt_path = args.receipt
            if not receipt_path.is_absolute():
                receipt_path = root / receipt_path
            write_receipt(receipt_path.resolve(), receipt)
        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)
        print(
            "HISTORICAL_SOURCE_PROJECTION_V2_PASS "
            f"generation={ready.get('generation')} mode={args.mode} "
            f"projected={len(projections)}"
        )
        return 0
    except (
        ProjectionError,
        OSError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"HISTORICAL_SOURCE_PROJECTION_V2_BLOCKED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
