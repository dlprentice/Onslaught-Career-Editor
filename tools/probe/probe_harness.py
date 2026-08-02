#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a list of Battle Engine Aquila probes end to end, unattended, and emit a
receipt for each one.

WHY THIS EXISTS
---------------
Three separate console probes on 2026-08-02 measured nothing, and the reason was
never the engine: the first three arms launched without ``-level`` and sat in the
frontend, where ``autoexec.con`` is never read.  A fourth arm, identical but for
one argument, executed all four console commands.  The difference between an
answer and a wasted afternoon was launch mechanics, not science.

This harness owns the launch mechanics so a probe author never has to.  Given a
probe manifest it stages a scratch copy of the game, places the authored payload
and an ``autoexec.con``, launches with the CWD pinned to the scratch copy, waits
on an oracle the probe itself declares, collects artefacts, tears the scratch
copy down, and writes a receipt.  It runs a list of these without a human.

WHAT IT REFUSES TO DO
---------------------
Every one of these is a rule this project has already paid for once:

  * It never launches out of, or writes into, the source tree it copies from.
    ``local-lab/safe-copy-bea-pristine`` is shared by every other instrument in
    this repository; a probe that mutates it silently poisons them all.  Source
    ``BEA.exe`` and ``BEA.exe.original.backup`` are hashed before AND after each
    run and a difference is a hard failure.
  * It never accepts a source root under Program Files or steamapps.
  * It refuses to run at all if a ``BEA.exe.original.backup`` in the source root
    does not hash to the pristine specimen ``74154bfa…``.
  * It refuses to start while an ARMED stale ``autoexec.con`` exists -- see
    ``scan_for_stale_autoexec`` for what "armed" means and why the check is not
    simply "any file with that name".
  * It removes its own ``autoexec.con`` unconditionally, including on the
    failure path and including when ``--keep-scratch`` preserves everything
    else.  A forgotten one executes silently on every future level load of that
    tree and reads exactly like engine behaviour.
  * It never silently degrades.  Every failure is raised as ``ProbeError``,
    recorded in the receipt with the reason, and reflected in the exit code.

THE CWD IS THE WHOLE BALLGAME.  The game resolves ``autoexec.con``, its data
archives and its sound banks against the process working directory.  Launch it
with the wrong CWD and it dies during sound init, which looks identical to "the
authored archive killed it".  This harness pins the CWD to the staged root and
then, separately, reads ``setuphistory.txt`` so that the two can always be told
apart -- see ``diagnose``.

RECORDING is optional and delegated.  ``tools/ttd_record.ps1`` already owns TTD
capture, its interlocks and its elevation refusal; this harness shells out to it
and never reimplements any of it.  Without recording a probe needs no elevation
and no human, which is the point: console-only probes run today.

Usage
-----
    python tools/probe/probe_harness.py probes.json --dry-run
    python tools/probe/probe_harness.py probes.json --out local-lab/probe-runs
    python tools/probe/probe_harness.py probes.json --only console-smoke

Exit code is 0 only when every probe's oracle was satisfied.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _datetime
import hashlib
import json
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Iterable, Optional, Sequence


ROOT = pathlib.Path(__file__).resolve().parents[2]

# The measurement baseline every byte finding in this project cites.  If this
# file is present in a source root and does not hash to this, something has
# written to it and no probe result taken from that tree can be trusted.
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

# Artefacts the engine writes at the game root that are always meaningful,
# whatever oracle a probe declares.  These are collected for every run.
EXCEPTION_LOG = "OnslaughtException.txt"
SETUP_HISTORY = "setuphistory.txt"
AUTOEXEC = "autoexec.con"

# Directory names never walked when scanning for a stale autoexec.con.
_SCAN_SKIP = {".git", ".vs", "node_modules", "bin", "obj", "__pycache__"}

# NTSTATUS codes a process exits with when it died rather than finished.  Named
# individually because a receipt that says "exited 3221225477" is a number a
# reader has to go look up, and one that says STATUS_ACCESS_VIOLATION is not.
_KNOWN_FAULT_STATUS = {
    0x80000003: "STATUS_BREAKPOINT",
    0x80000004: "STATUS_SINGLE_STEP",
    0xC0000005: "STATUS_ACCESS_VIOLATION",
    0xC0000006: "STATUS_IN_PAGE_ERROR",
    0xC000001D: "STATUS_ILLEGAL_INSTRUCTION",
    0xC0000025: "STATUS_NONCONTINUABLE_EXCEPTION",
    0xC000008C: "STATUS_ARRAY_BOUNDS_EXCEEDED",
    0xC000008E: "STATUS_FLOAT_DIVIDE_BY_ZERO",
    0xC000008F: "STATUS_FLOAT_INEXACT_RESULT",
    0xC0000090: "STATUS_FLOAT_INVALID_OPERATION",
    0xC0000091: "STATUS_FLOAT_OVERFLOW",
    0xC0000093: "STATUS_FLOAT_UNDERFLOW",
    0xC0000094: "STATUS_INTEGER_DIVIDE_BY_ZERO",
    0xC0000095: "STATUS_INTEGER_OVERFLOW",
    0xC0000096: "STATUS_PRIVILEGED_INSTRUCTION",
    0xC00000FD: "STATUS_STACK_OVERFLOW",
    0xC0000135: "STATUS_DLL_NOT_FOUND",
    0xC0000142: "STATUS_DLL_INIT_FAILED",
    0xC0000374: "STATUS_HEAP_CORRUPTION",
    0xC0000409: "STATUS_STACK_BUFFER_OVERRUN",
    0xC000041D: "STATUS_FATAL_USER_CALLBACK_EXCEPTION",
    0xE06D7363: "MSVC C++ exception (0xE06D7363)",
}

# MEASURED 2026-08-02, campaign 01, and it decides how the band below is set.
# Ten runs of BEA.exe at level 100, all ending with a console `Quit`, four of
# them byte-identical arms. The exit codes were:
#
#     baseline     0x80000001, 0x80000001, 1, 1
#     lose         1, 0, 1
#     poison-noop  1, 0x80000001, 1
#
# Three distinct exit codes from identical input, and not one run wrote an
# OnslaughtException.txt. 0x80000001 is STATUS_GUARD_PAGE_VIOLATION by the book,
# and it is what this game returns from a clean, successful, user-requested
# quit -- most likely a message loop returning an uninitialised wParam.
#
# TWO CONSEQUENCES, both load-bearing:
#
#   1. `expectExitCode` is useless against BEA. There is no code to expect.
#   2. DO NOT WIDEN THE BAND TO COVER THE WARNING-SEVERITY RANGE. An
#      adversarial review recommended exactly that, on correct Windows
#      semantics: 0x80000001 and 0x80000002 really are fault statuses, and a
#      gate that misses them really is incomplete. Against this binary it would
#      veto 30% of all clean runs. The generic reasoning is right and the
#      specific answer is wrong, which is why it took a campaign rather than a
#      reading to settle -- the exception log, not the exit code, is the trigger
#      that carries weight here.
#
# The band of Microsoft-defined NTSTATUS values whose severity field is ERROR.
# Anything in it is a death even when this file has no name for it.  The band is
# bounded deliberately: 0xFFFFFFFF also has ERROR severity, and it is what a
# POSIX-style -1 becomes under 32-bit normalisation, so a blanket
# "severity == ERROR" rule would classify the harness's own kill as an engine
# fault.  See classify_exit_code.
_NTSTATUS_ERROR_BAND = (0xC0000000, 0xD0000000)

# Path fragments that mean "this is the user's installed game, not a scratch
# copy".  Matched case-insensitively against the resolved path.
_FORBIDDEN_FRAGMENTS = ("program files", "steamapps", "steam\\steamapps")


class ProbeError(Exception):
    """A fail-closed stop.  Every one of these carries the reason verbatim."""


# ---------------------------------------------------------------------------
# Did it finish, or did it die?
# ---------------------------------------------------------------------------


def classify_exit_code(code: Optional[int]) -> dict[str, Any]:
    """Say whether a process exit was a finish or a death.

    WHY THIS EXISTS.  Until 2026-08-01 the ``processExit`` oracle read
    ``state.exited`` and nothing else, so a probe that declared
    ``{"kind": "processExit"}`` reported PASS when the game took an access
    violation eight seconds in.  At one probe that is a bad afternoon; at a
    hundred it manufactures false accepts wholesale, and the campaign this
    harness exists to run is a hundred.

    THE NORMALISATION MATTERS.  CPython reports a Windows exit code as the raw
    unsigned DWORD, but the same field carries a negative value on POSIX and
    from any fake or wrapper that follows the POSIX convention.  Both are folded
    to 32-bit unsigned before classification so 0xC0000005 and -1073741819 are
    one code, not two.

    THE BAND IS BOUNDED ON PURPOSE.  ``severity == ERROR`` alone would be
    wrong: 0xFFFFFFFF has ERROR severity and is what -1 normalises to, and -1 is
    what this harness's own kill path produces.  Classifying our own termination
    as an engine fault would be a false accusation in the other direction, and a
    fault gate that cries wolf gets switched off.  Only the Microsoft-defined
    0xC0000000-0xCFFFFFFF band, plus the named codes above it, count.
    """

    if code is None:
        return {
            "code": None,
            "unsigned": None,
            "hex": None,
            "isFault": False,
            "status": None,
            "detail": "the process had not exited",
        }

    unsigned = int(code) & 0xFFFFFFFF
    known = _KNOWN_FAULT_STATUS.get(unsigned)
    low, high = _NTSTATUS_ERROR_BAND
    in_band = low <= unsigned < high
    is_fault = known is not None or in_band
    if known is not None:
        status = known
    elif in_band:
        status = "unnamed NTSTATUS error-severity status"
    else:
        status = None

    if is_fault:
        detail = (
            f"exit code 0x{unsigned:08X} is {status} -- the process DIED, it "
            "did not finish"
        )
    elif unsigned == 0:
        detail = "exit code 0 -- a clean finish"
    else:
        detail = (
            f"exit code {unsigned} (0x{unsigned:08X}) -- a non-zero finish, not "
            "a recognised fault"
        )

    return {
        "code": int(code),
        "unsigned": unsigned,
        "hex": f"0x{unsigned:08X}",
        "isFault": is_fault,
        "status": status,
        "detail": detail,
    }


def oracle_expects_a_fault(
    oracle: dict[str, Any], exit_code: Optional[int], trigger: str = "any"
) -> bool:
    """True when this oracle tree asked for the death it got.

    ``trigger`` names WHICH death is being excused, and the two are not the
    same permission:

        "exit-code"  the process exited with an NTSTATUS fault status.
        "fault-log"  ``OnslaughtException.txt`` appeared.

    THREE CORRECTIONS FROM AN ADVERSARIAL PASS, each verified against the real
    code before it was believed:

    1. ``expectExitCode`` used to excuse EVERYTHING, including a fault log, and
       it never checked that the code it named was a fault at all. So
       ``{"kind": "processExit", "expectExitCode": 0}`` -- which reads stricter
       than a bare processExit -- reinstated the exact bug this gate was built
       to fix: the engine's handler writes the log, the process exits 0, and
       the receipt says the probe asked for the crash. Naming an ordinary exit
       code is not asking for a crash, and asking for a specific exit code says
       nothing whatever about a fault log.

    2. A ``fatalFault`` arm inside an ``any`` no longer opts out. Under ``any``
       the composite is satisfied by whichever arm fired, and the gate cannot
       tell which one did -- so ``any(setupHistoryContains, fatalFault)``, a
       perfectly natural exploratory probe, was passing on every crash
       including a launch that died at sound init. Under ``all`` it is
       different: every arm must be satisfied, so a ``fatalFault`` in an
       ``all`` really was satisfied, and it really did ask.

    3. An ``expectExitCode`` that names a non-fault code excuses nothing.
    """

    kind = oracle.get("kind")
    if kind == "fatalFault":
        return True
    if kind == "processExit":
        if trigger == "fault-log":
            return False
        expected = oracle.get("expectExitCode")
        if expected is None or exit_code is None:
            return False
        if (int(expected) & 0xFFFFFFFF) != (int(exit_code) & 0xFFFFFFFF):
            return False
        return bool(classify_exit_code(expected)["isFault"])
    if kind == "all":
        return any(
            oracle_expects_a_fault(sub, exit_code, trigger) for sub in oracle["of"]
        )
    if kind == "any":
        return False
    return False


def apply_fault_gate(
    probe: "Probe",
    oracle_result: dict[str, Any],
    diagnosis: dict[str, Any],
    classification: dict[str, Any],
) -> dict[str, Any]:
    """Veto a satisfied oracle when the run it came from was a crash.

    THE GATE IS ABOVE THE ORACLE, NOT INSIDE IT.  Fixing only ``processExit``
    would leave ``fileAppears`` and ``setupHistoryContains`` able to launder the
    same crash: the console writes its file, the engine faults two seconds
    later, and the oracle -- which only ever looked at the file -- says PASS.
    Every oracle kind passes through here.

    TWO INDEPENDENT TRIGGERS, because there are two ways to die:

      1. The process exits with an NTSTATUS fault code.
      2. ``OnslaughtException.txt`` appears.  This one is not redundant: BEA
         installs its own handler, and a handler that logs and then exits
         cleanly produces a crash with exit code 0.  The code alone cannot see
         that run.

    Either trigger vetoes unless the probe opted in -- ``allowFaultExit``, a
    ``fatalFault`` oracle, or an ``expectExitCode`` naming the exact status.
    """

    blanket = bool(probe.allow_fault_exit)
    code = classification.get("code")

    triggers: list[str] = []
    excused: list[str] = []
    if classification.get("isFault"):
        if blanket or oracle_expects_a_fault(probe.oracle, code, "exit-code"):
            excused.append(classification["detail"])
        else:
            triggers.append(classification["detail"])
    if diagnosis.get("fatalFaultLogPresent"):
        message = (
            f"{EXCEPTION_LOG} was written -- the engine's own handler recorded a "
            "fatal fault, whatever the exit code says"
        )
        if blanket or oracle_expects_a_fault(probe.oracle, code, "fault-log"):
            excused.append(message)
        else:
            triggers.append(message)

    # ``vetoed`` means "this run may not be a PASS", not "the gate is the only
    # thing standing between it and one".  Those come apart when the oracle
    # already caught the fault itself -- a settle window that saw the crash
    # reports satisfied-then-faulted, and the gate agreeing with it is not the
    # gate doing nothing.  ``wasDecisive`` is the narrower fact, and it is the
    # one a campaign summary counts.
    if not triggers:
        return {
            "triggered": bool(excused),
            "vetoed": False,
            "wasDecisive": False,
            "optedIn": bool(excused),
            "triggers": [],
            "excused": excused,
            "detail": (
                "the run faulted and the probe asked for it: " + "; ".join(excused)
                if excused
                else "the run did not fault"
            ),
        }

    # AT LEAST ONE TRIGGER WAS NOT EXCUSED, so the run is vetoed even if the
    # other one was. A probe that asked for an access violation did not thereby
    # ask for a fault log it never mentioned.
    return {
        "triggered": True,
        "vetoed": True,
        "wasDecisive": oracle_result.get("outcome") == "satisfied",
        "optedIn": False,
        "triggers": triggers,
        "excused": excused,
        "detail": (
            "THIS RUN CRASHED and the probe did not declare that it expected to: "
            + "; ".join(triggers)
            + ". A crashed run is not evidence for a claim about what the engine "
            "does; whatever the oracle saw before the fault, it saw on the way "
            "down. Declare 'allowFaultExit': true, or a 'fatalFault' oracle, if "
            "the crash IS the measurement."
        ),
    }


# ---------------------------------------------------------------------------
# Injection seams.  Everything that touches the outside world goes through one
# of these so the tests can drive the harness without launching the game.
# ---------------------------------------------------------------------------


class ProcessHandle:
    """The subset of a running game the harness is allowed to depend on."""

    def poll(self) -> Optional[int]:
        raise NotImplementedError

    def kill(self) -> None:
        raise NotImplementedError

    @property
    def pid(self) -> int:
        raise NotImplementedError


class _SubprocessHandle(ProcessHandle):
    def __init__(self, popen: "subprocess.Popen[bytes]") -> None:
        self._popen = popen

    def poll(self) -> Optional[int]:
        return self._popen.poll()

    def kill(self) -> None:
        if self._popen.poll() is None:
            self._popen.kill()
            try:
                self._popen.wait(timeout=10)
            except subprocess.TimeoutExpired:  # pragma: no cover - OS refusal
                pass

    @property
    def pid(self) -> int:
        return self._popen.pid


class SubprocessLauncher:
    """The real launcher.  The CWD argument is not optional and not defaulted."""

    def launch(
        self, executable: pathlib.Path, argv: Sequence[str], cwd: pathlib.Path
    ) -> ProcessHandle:
        if not cwd.is_dir():
            raise ProbeError(f"working directory does not exist: {cwd}")
        popen = subprocess.Popen(
            [str(executable), *argv],
            cwd=str(cwd),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return _SubprocessHandle(popen)


class Clock:
    """Monotonic time and sleeping, so a timeout can be tested in milliseconds."""

    def now(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


# ---------------------------------------------------------------------------
# Probe manifest
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class StagedFile:
    """One authored file copied into the scratch tree."""

    source: str
    dest: str
    expect_sha256: Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Probe:
    name: str
    level: int
    source_root: str
    oracle: dict[str, Any]
    autoexec: tuple[str, ...] = ()
    stage: tuple[StagedFile, ...] = ()
    make_dirs: tuple[str, ...] = ()
    collect: tuple[str, ...] = ()
    game_arguments: tuple[str, ...] = ("-skipfmv", "-forcewindowed")
    record: bool = False
    record_seconds: int = 45
    note: str = ""
    # Opt out of the fault gate.  Only for a probe whose measurement IS the
    # crash; see apply_fault_gate for why the default cannot be permissive.
    allow_fault_exit: bool = False

    @property
    def argv(self) -> tuple[str, ...]:
        """The exact argument vector.  ``-level`` is appended by the harness and
        is not a probe's to omit: without it the game sits in the frontend and
        ``autoexec.con`` is never read."""

        return (*self.game_arguments, "-level", str(self.level))


_PROBE_KEYS = {
    "name",
    "level",
    "sourceRoot",
    "oracle",
    "autoexec",
    "stage",
    "makeDirs",
    "collect",
    "gameArguments",
    "record",
    "recordSeconds",
    "note",
    "allowFaultExit",
}

ORACLE_KINDS = {
    "processExit",
    "fileAppears",
    "fatalFault",
    "setupHistoryContains",
    "survives",
    "all",
    "any",
}


def parse_probe(raw: dict[str, Any]) -> Probe:
    """Parse one probe, refusing anything it does not understand.

    An unknown key is a hard failure rather than a shrug.  A typo in an oracle
    name that silently defaults is how a probe reports PASS without ever having
    checked anything -- the exact failure mode this project keeps re-learning.
    """

    if not isinstance(raw, dict):
        raise ProbeError(f"probe must be an object, got {type(raw).__name__}")
    unknown = sorted(set(raw) - _PROBE_KEYS)
    if unknown:
        raise ProbeError(f"probe has unknown keys: {', '.join(unknown)}")
    for required in ("name", "level", "sourceRoot", "oracle"):
        if required not in raw:
            raise ProbeError(f"probe is missing required key '{required}'")
    name = str(raw["name"])
    if not name or any(ch in name for ch in '\\/:*?"<>| '):
        raise ProbeError(f"probe name is not a safe directory name: {name!r}")
    if not isinstance(raw["level"], int):
        raise ProbeError(f"{name}: level must be an integer")

    staged: list[StagedFile] = []
    for entry in raw.get("stage", ()):
        if not isinstance(entry, dict) or "source" not in entry or "dest" not in entry:
            raise ProbeError(f"{name}: each stage entry needs 'source' and 'dest'")
        extra = sorted(set(entry) - {"source", "dest", "expectSha256"})
        if extra:
            raise ProbeError(f"{name}: stage entry has unknown keys: {extra}")
        staged.append(
            StagedFile(
                source=str(entry["source"]),
                dest=str(entry["dest"]),
                expect_sha256=(
                    str(entry["expectSha256"]).lower()
                    if entry.get("expectSha256")
                    else None
                ),
            )
        )

    probe = Probe(
        name=name,
        level=int(raw["level"]),
        source_root=str(raw["sourceRoot"]),
        oracle=dict(raw["oracle"]),
        autoexec=tuple(str(line) for line in raw.get("autoexec", ())),
        stage=tuple(staged),
        make_dirs=tuple(str(d) for d in raw.get("makeDirs", ())),
        collect=tuple(str(c) for c in raw.get("collect", ())),
        game_arguments=tuple(
            str(a) for a in raw.get("gameArguments", ("-skipfmv", "-forcewindowed"))
        ),
        record=bool(raw.get("record", False)),
        record_seconds=int(raw.get("recordSeconds", 45)),
        note=str(raw.get("note", "")),
        allow_fault_exit=bool(raw.get("allowFaultExit", False)),
    )
    if "-level" in probe.game_arguments:
        raise ProbeError(
            f"{name}: do not put -level in gameArguments; set the 'level' field"
        )
    validate_oracle(probe.oracle, probe.name)
    return probe


def validate_oracle(oracle: Any, probe_name: str) -> None:
    """Reject an oracle the evaluator would not actually check."""

    if not isinstance(oracle, dict) or "kind" not in oracle:
        raise ProbeError(f"{probe_name}: oracle must be an object with a 'kind'")
    kind = oracle["kind"]
    if kind not in ORACLE_KINDS:
        raise ProbeError(
            f"{probe_name}: unknown oracle kind {kind!r}; "
            f"known kinds are {', '.join(sorted(ORACLE_KINDS))}"
        )
    if kind in ("all", "any"):
        of = oracle.get("of")
        if not isinstance(of, list) or not of:
            raise ProbeError(f"{probe_name}: '{kind}' oracle needs a non-empty 'of'")
        for sub in of:
            validate_oracle(sub, probe_name)
    if kind == "fileAppears" and not oracle.get("path"):
        raise ProbeError(f"{probe_name}: 'fileAppears' oracle needs a 'path'")
    if kind == "setupHistoryContains" and not oracle.get("text"):
        raise ProbeError(f"{probe_name}: 'setupHistoryContains' oracle needs 'text'")
    if kind == "processExit":
        expected = oracle.get("expectExitCode")
        if expected is not None and not isinstance(expected, int):
            raise ProbeError(
                f"{probe_name}: expectExitCode must be an integer, got "
                f"{type(expected).__name__}. A string here would never compare "
                "equal to a real exit code and the oracle would never pass."
            )
    timeout = oracle.get("timeoutSeconds", 90)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ProbeError(f"{probe_name}: timeoutSeconds must be a positive number")
    settle = oracle.get("settleSeconds", 0)
    if not isinstance(settle, (int, float)) or settle < 0:
        raise ProbeError(
            f"{probe_name}: settleSeconds must be zero or a positive number"
        )


def load_manifest(path: pathlib.Path) -> list[Probe]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProbeError(f"{path}: not valid JSON: {exc}") from exc
    probes = raw["probes"] if isinstance(raw, dict) else raw
    if not isinstance(probes, list) or not probes:
        raise ProbeError(f"{path}: expected a non-empty list of probes")
    parsed = [parse_probe(entry) for entry in probes]
    names = [p.name for p in parsed]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ProbeError(f"{path}: duplicate probe names: {', '.join(duplicates)}")
    return parsed


# ---------------------------------------------------------------------------
# Hashing and the source-tree interlock
# ---------------------------------------------------------------------------


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# Files in a source root whose hashes are taken before and after every run.  A
# change in any of them means the harness wrote where it promised not to.
WITNESS_FILES = ("BEA.exe", "BEA.exe.original.backup")


def witness_source(source_root: pathlib.Path) -> dict[str, str]:
    witnesses: dict[str, str] = {}
    for name in WITNESS_FILES:
        candidate = source_root / name
        if candidate.is_file():
            witnesses[name] = sha256_file(candidate)
    return witnesses


def check_source_root(source_root: pathlib.Path) -> dict[str, str]:
    """Every reason to refuse a source root, checked before anything is copied."""

    # ORDER MATTERS.  The installed-game refusal is checked FIRST, before the
    # directory is even required to exist.  A manifest pointing at Program Files
    # must be told it is pointing at the installed game -- not told the path is
    # missing today, which is a message that invites someone to fix the path.
    lowered = str(source_root).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        if fragment in lowered:
            raise ProbeError(
                f"refusing to use an installed-game path as a source root "
                f"(matched {fragment!r}): {source_root}"
            )
    if not source_root.is_dir():
        raise ProbeError(f"source root does not exist: {source_root}")
    if not (source_root / "BEA.exe").is_file():
        raise ProbeError(f"source root has no BEA.exe: {source_root}")
    backup = source_root / "BEA.exe.original.backup"
    if backup.is_file():
        actual = sha256_file(backup)
        if actual != PRISTINE_SHA256:
            raise ProbeError(
                "the pristine specimen in this source root is not pristine: "
                f"{backup} hashes {actual}, expected {PRISTINE_SHA256}. "
                "Every byte finding in this project cites that file; refusing "
                "to measure anything from a tree where it has been written to."
            )
    return witness_source(source_root)


def verify_source_untouched(
    source_root: pathlib.Path, before: dict[str, str]
) -> None:
    after = witness_source(source_root)
    if after != before:
        changed = sorted(
            name
            for name in set(before) | set(after)
            if before.get(name) != after.get(name)
        )
        raise ProbeError(
            f"the source tree was modified by this run -- {', '.join(changed)} "
            f"changed under {source_root}. This must never happen; treat every "
            "result from this session as void."
        )


# ---------------------------------------------------------------------------
# The autoexec.con landmine
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class StaleAutoexec:
    path: str
    armed: bool


def scan_for_stale_autoexec(roots: Iterable[pathlib.Path]) -> list[StaleAutoexec]:
    """Find every ``autoexec.con`` under ``roots`` and say which ones can fire.

    ARMED means the file sits in a directory that also contains ``BEA.exe`` --
    i.e. a directory that can plausibly be a process CWD for the game, which is
    the only place the file has any effect.  An armed stale file is a hard stop.

    INERT means anywhere else: an archived probe input under ``local-lab``, a
    fixture in this repository, a payload staged for a future run.  Those are
    reported but not fatal, because a blanket "no file may ever bear this name"
    rule would make the harness unusable in a repository that deliberately
    preserves past probe inputs -- and a rule that forbids the thing people need
    produces workarounds, not safety.  ``--strict-autoexec`` makes them fatal
    for a caller who wants the blunt version.
    """

    found: list[StaleAutoexec] = []
    for root in roots:
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d.lower() not in _SCAN_SKIP]
            lowered = {f.lower() for f in filenames}
            if AUTOEXEC in lowered:
                here = pathlib.Path(dirpath)
                actual = next(
                    f for f in filenames if f.lower() == AUTOEXEC
                )
                found.append(
                    StaleAutoexec(
                        path=str(here / actual),
                        armed="bea.exe" in lowered,
                    )
                )
    return sorted(found, key=lambda s: s.path)


def assert_no_stale_autoexec(
    roots: Iterable[pathlib.Path], strict: bool = False
) -> list[StaleAutoexec]:
    stale = scan_for_stale_autoexec(roots)
    fatal = [s for s in stale if s.armed or strict]
    if fatal:
        listing = "\n  ".join(
            f"{'ARMED' if s.armed else 'inert'}  {s.path}" for s in fatal
        )
        raise ProbeError(
            "a stale autoexec.con exists and would execute silently on every "
            "level load of that tree, which reads exactly like engine "
            "behaviour. Remove it before running a probe:\n  " + listing
        )
    return stale


# ---------------------------------------------------------------------------
# Oracles
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class RunState:
    """Everything an oracle is allowed to look at, sampled at one instant."""

    scratch_root: pathlib.Path
    exited: bool
    exit_code: Optional[int]
    elapsed: float
    deadline_reached: bool
    # Set from the probe.  An oracle cannot see the probe, and the fault refusal
    # inside processExit has to honour the same opt-out the gate does or a probe
    # that declared allowFaultExit would still be failed one layer lower down.
    allow_fault_exit: bool = False

    def file_size(self, relative: str) -> Optional[int]:
        candidate = self.scratch_root / relative
        try:
            return candidate.stat().st_size if candidate.is_file() else None
        except OSError:  # pragma: no cover - transient sharing violation
            return None

    def read_text(self, relative: str) -> str:
        candidate = self.scratch_root / relative
        if not candidate.is_file():
            return ""
        try:
            return candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:  # pragma: no cover - transient sharing violation
            return ""


def check_oracle(oracle: dict[str, Any], state: RunState) -> tuple[bool, str]:
    """Evaluate one oracle against one sample.  Returns (satisfied, detail)."""

    kind = oracle["kind"]

    if kind == "processExit":
        if not state.exited:
            return False, "process still running"
        expected = oracle.get("expectExitCode")
        classification = classify_exit_code(state.exit_code)
        if expected is not None:
            if (int(expected) & 0xFFFFFFFF) != (state.exit_code or 0) & 0xFFFFFFFF:
                return (
                    False,
                    f"process exited {state.exit_code}, probe expected {expected}",
                )
            return True, f"process exited with the expected code {state.exit_code}"
        # NO expectExitCode.  "It exited" is not "it finished": an access
        # violation exits too.  A bare processExit means a clean finish, and a
        # death has to be asked for by name.
        if classification["isFault"] and not state.allow_fault_exit:
            return False, classification["detail"]
        return True, f"process exited on its own with code {state.exit_code}"

    if kind == "fileAppears":
        relative = str(oracle["path"])
        minimum = int(oracle.get("minBytes", 1))
        size = state.file_size(relative)
        if size is None:
            return False, f"{relative} does not exist"
        if size < minimum:
            return False, f"{relative} is {size} bytes, need >= {minimum}"
        return True, f"{relative} appeared, {size} bytes"

    if kind == "fatalFault":
        size = state.file_size(EXCEPTION_LOG)
        if size is None:
            return False, f"{EXCEPTION_LOG} does not exist"
        return True, f"{EXCEPTION_LOG} written, {size} bytes -- the engine faulted"

    if kind == "setupHistoryContains":
        text = state.read_text(SETUP_HISTORY)
        needle = str(oracle["text"])
        if needle in text:
            return True, f"{SETUP_HISTORY} contains {needle!r}"
        return False, f"{SETUP_HISTORY} does not contain {needle!r}"

    if kind == "survives":
        # The only oracle whose PASS is reaching the deadline.  This is the arm
        # that says "the engine accepted the edit": it must still be alive and
        # must not have written a fault log.
        fault = state.file_size(EXCEPTION_LOG)
        if fault is not None:
            return False, f"{EXCEPTION_LOG} written -- the engine faulted"
        if state.exited:
            return False, f"process exited early with code {state.exit_code}"
        if not state.deadline_reached:
            return False, f"still alive at {state.elapsed:.1f}s, waiting"
        return True, f"survived {state.elapsed:.1f}s with no fault log"

    if kind in ("all", "any"):
        results = [check_oracle(sub, state) for sub in oracle["of"]]
        details = "; ".join(detail for _, detail in results)
        satisfied = (
            all(ok for ok, _ in results)
            if kind == "all"
            else any(ok for ok, _ in results)
        )
        return satisfied, details

    raise ProbeError(f"unknown oracle kind {kind!r}")  # pragma: no cover


def oracle_needs_deadline(oracle: dict[str, Any]) -> bool:
    """True when the oracle can only be decided once the clock runs out."""

    if oracle["kind"] == "survives":
        return True
    if oracle["kind"] in ("all", "any"):
        return any(oracle_needs_deadline(sub) for sub in oracle["of"])
    return False


def wait_for_oracle(
    oracle: dict[str, Any],
    scratch_root: pathlib.Path,
    handle: ProcessHandle,
    clock: Clock,
    poll_seconds: float = 0.25,
    allow_fault_exit: bool = False,
) -> dict[str, Any]:
    """Poll until the oracle is decided, the process dies, or time runs out.

    THE SETTLE WINDOW.  ``fileAppears`` is satisfied the instant the file is
    there, and without ``settleSeconds`` the harness stops looking right then --
    so a game that writes the file and takes an access violation a second later
    is recorded as a clean PASS, and nothing in the receipt ever knew.  The
    oracle was not wrong; it simply stopped watching before the interesting
    part.

    ``settleSeconds`` keeps polling after satisfaction and reports what it saw.
    It defaults to 0 because a silent change to every probe's timing is its own
    kind of surprise, and because a probe whose whole question is "did the file
    appear" is entitled to say so.  What is NOT optional is that the receipt
    records which of the two happened: ``processAliveAtDecision`` true means the
    survival question was never asked, and per this project's own evidence rule
    a non-observation is not an absence.
    """

    timeout = float(oracle.get("timeoutSeconds", 90))
    settle = float(oracle.get("settleSeconds", 0))
    started = clock.now()
    needs_deadline = oracle_needs_deadline(oracle)

    def sample(elapsed: float, exit_code: Optional[int]) -> RunState:
        return RunState(
            scratch_root=scratch_root,
            exited=exit_code is not None,
            exit_code=exit_code,
            elapsed=elapsed,
            deadline_reached=elapsed >= timeout,
            allow_fault_exit=allow_fault_exit,
        )

    def result(
        outcome: str, detail: str, elapsed: float, exit_code: Optional[int], **extra
    ) -> dict[str, Any]:
        return {
            "outcome": outcome,
            "detail": detail,
            "elapsedSeconds": round(elapsed, 3),
            "exitCode": exit_code,
            "processAliveAtDecision": exit_code is None,
            "settleSeconds": settle,
            **extra,
        }

    while True:
        exit_code = handle.poll()
        elapsed = clock.now() - started
        state = sample(elapsed, exit_code)
        satisfied, detail = check_oracle(oracle, state)

        if satisfied and not (needs_deadline and not state.deadline_reached):
            if settle > 0 and exit_code is None:
                return _settle(
                    oracle, scratch_root, handle, clock, poll_seconds,
                    allow_fault_exit, started, settle, detail, sample, result,
                )
            return result("satisfied", detail, elapsed, exit_code)
        if state.exited:
            # A dead process cannot produce new evidence.  Decide now -- but
            # HONOUR ``satisfied``. This branch used to hardcode the unsatisfied
            # outcome while the deadline branch below correctly honoured it, so
            # a composite like any(fileAppears, survives) whose file arm was
            # satisfied at the very sample the process exited cleanly was
            # reported FAIL with a detail reading "appeared".
            return result(
                "satisfied" if satisfied else "unsatisfied-process-exited",
                detail,
                elapsed,
                exit_code,
            )
        if state.deadline_reached:
            return result(
                "satisfied" if satisfied else "unsatisfied-timeout",
                detail,
                elapsed,
                exit_code,
            )
        clock.sleep(poll_seconds)


def _settle(
    oracle: dict[str, Any],
    scratch_root: pathlib.Path,
    handle: ProcessHandle,
    clock: Clock,
    poll_seconds: float,
    allow_fault_exit: bool,
    started: float,
    settle: float,
    detail: str,
    sample: Callable[[float, Optional[int]], RunState],
    result: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Keep watching for ``settle`` seconds after the oracle said yes.

    The oracle's verdict is NOT revisited here -- what it saw, it saw.  What
    this window buys is the fault evidence that arrives afterwards, which the
    gate above then acts on.  A run that satisfies its oracle and dies four
    seconds later is a run whose answer came out of a process that was already
    falling over.
    """

    # A PROBE THAT ASKED FOR THE CRASH STILL GETS IT HERE.  The fault-log check
    # below used to fire unconditionally, so a `fatalFault` oracle -- an oracle
    # whose entire subject IS the crash -- could never pass once a settle window
    # was added, and `allowFaultExit` silently stopped working the moment
    # someone set settleSeconds. The gate said optedIn and this layer failed it
    # anyway; the stricter of two disagreeing layers won by accident.
    excused_log = allow_fault_exit or oracle_expects_a_fault(
        oracle, None, "fault-log"
    )

    settle_started = clock.now()
    while True:
        exit_code = handle.poll()
        elapsed = clock.now() - started
        settled = clock.now() - settle_started
        state = sample(elapsed, exit_code)
        fault_log = state.file_size(EXCEPTION_LOG) is not None and not excused_log
        classification = classify_exit_code(exit_code)
        # Recomputed per sample, not once on entry: an expectExitCode opt-in
        # cannot be evaluated until there IS an exit code to compare against,
        # and on entry to this window there is not one.
        excused_code = allow_fault_exit or oracle_expects_a_fault(
            oracle, exit_code, "exit-code"
        )

        if fault_log or (classification["isFault"] and not excused_code):
            return result(
                "satisfied-then-faulted",
                f"{detail}; then, {settled:.1f}s later, "
                + (
                    f"{EXCEPTION_LOG} appeared"
                    if fault_log
                    else classification["detail"]
                ),
                elapsed,
                exit_code,
                settleObserved=round(settled, 3),
            )
        if exit_code is not None:
            return result(
                "satisfied", detail, elapsed, exit_code,
                settleObserved=round(settled, 3),
            )
        if settled >= settle:
            return result(
                "satisfied", detail, elapsed, exit_code,
                settleObserved=round(settled, 3),
            )
        clock.sleep(poll_seconds)


def diagnose(scratch_root: pathlib.Path, level: int) -> dict[str, Any]:
    """Tell a launch failure apart from an engine failure, every run.

    ``setuphistory.txt`` logs ``Game::LoadLevel <n>`` and then render-method
    negotiation.  If the level-load line is absent the game died before it got
    anywhere near the probe's payload -- almost always a CWD mistake, which
    kills it at sound init and otherwise reads as a clean negative result.
    """

    history = scratch_root / SETUP_HISTORY
    text = (
        history.read_text(encoding="utf-8", errors="replace")
        if history.is_file()
        else ""
    )
    lines = text.splitlines()
    load_marker = f"Game::LoadLevel {level}"
    level_load_logged = load_marker in text
    fault = scratch_root / EXCEPTION_LOG
    fault_present = fault.is_file()

    if fault_present:
        interpretation = (
            f"{EXCEPTION_LOG} was written -- a fatal fault inside the engine"
        )
    elif not text:
        interpretation = (
            f"{SETUP_HISTORY} is absent or empty -- the game did not reach its "
            "own logging; suspect the launch, not the payload"
        )
    elif not level_load_logged:
        interpretation = (
            f"{SETUP_HISTORY} exists but never logged {load_marker!r} -- the "
            "game died BEFORE level load. This is what a wrong working "
            "directory looks like (death at sound init) and it is NOT evidence "
            "about the payload."
        )
    else:
        interpretation = (
            f"{load_marker!r} was logged -- the game reached level load, so a "
            "negative result here is about the payload, not the launch"
        )

    return {
        "levelLoadLogged": level_load_logged,
        "levelLoadMarker": load_marker,
        "fatalFaultLogPresent": fault_present,
        "setupHistoryBytes": len(text),
        "setupHistoryTail": lines[-12:],
        "interpretation": interpretation,
    }


# ---------------------------------------------------------------------------
# Staging and teardown
# ---------------------------------------------------------------------------


def stage_scratch(
    probe: Probe,
    source_root: pathlib.Path,
    scratch_root: pathlib.Path,
    manifest_dir: pathlib.Path,
) -> dict[str, Any]:
    """Copy the game, place the payload and the autoexec, hash what matters."""

    if scratch_root.exists():
        raise ProbeError(f"scratch root already exists: {scratch_root}")
    resolved_source = source_root.resolve()
    resolved_scratch = scratch_root.resolve()
    if resolved_scratch == resolved_source or _is_within(
        resolved_scratch, resolved_source
    ):
        raise ProbeError(
            f"scratch root {scratch_root} is inside the source root "
            f"{source_root}; staging there would write to the tree this "
            "harness promised never to touch"
        )

    scratch_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, scratch_root)

    # THE TWO FILES THE ENGINE SPEAKS THROUGH MUST NOT BE INHERITED.
    # copytree brings the whole source root, and a safe copy is a tree people
    # launch the game out of -- so it accumulates a setuphistory.txt from
    # whatever ran there last. Measured 2026-08-01: the shared safe copy held a
    # setuphistory.txt containing "Game::LoadLevel 100" from an unrelated lane's
    # run. A probe for level 100 that never launched at all would then have
    # inherited that line, and diagnose() would have reported "the game reached
    # level load, so a negative result here is about the payload, not the
    # launch" -- the exact opposite of the truth, from the one check whose whole
    # job is telling a launch failure from an engine failure.
    #
    # An inherited OnslaughtException.txt is worse in the other direction: it
    # would veto every probe run out of that tree as CRASHED, and let a
    # fatalFault poison arm pass at t=0 without the engine ever faulting.
    #
    # Removed rather than truncated: the engine recreates setuphistory.txt on
    # every launch (verified over 10 runs, 10 distinct hashes, none matching the
    # source), and absence is the one state that cannot be mistaken for output.
    inherited: list[dict[str, Any]] = []
    for name in (SETUP_HISTORY, EXCEPTION_LOG):
        stale = scratch_root / name
        if stale.is_file():
            inherited.append(
                {
                    "file": name,
                    "bytes": stale.stat().st_size,
                    "sha256": sha256_file(stale),
                }
            )
            stale.unlink()

    staged: list[dict[str, Any]] = []
    for entry in probe.stage:
        origin = (manifest_dir / entry.source).resolve()
        if not origin.is_file():
            raise ProbeError(f"{probe.name}: staged source not found: {origin}")
        digest = sha256_file(origin)
        if entry.expect_sha256 and digest != entry.expect_sha256:
            raise ProbeError(
                f"{probe.name}: {origin} hashes {digest}, manifest expected "
                f"{entry.expect_sha256}. Refusing to stage a payload that is "
                "not the one the probe was written against."
            )
        destination = scratch_root / entry.dest
        if not _is_within(destination.resolve().parent, resolved_scratch):
            raise ProbeError(
                f"{probe.name}: stage dest escapes the scratch root: {entry.dest}"
            )
        replaced = sha256_file(destination) if destination.is_file() else None
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, destination)
        staged.append(
            {
                "source": str(origin),
                "dest": entry.dest,
                "sha256": digest,
                "replacedSha256": replaced,
                "bytes": origin.stat().st_size,
            }
        )

    for relative in probe.make_dirs:
        target = scratch_root / relative
        if not _is_within(target.resolve(), resolved_scratch):
            raise ProbeError(f"{probe.name}: makeDirs escapes scratch: {relative}")
        target.mkdir(parents=True, exist_ok=True)

    autoexec_record: Optional[dict[str, Any]] = None
    if probe.autoexec:
        # CRLF, ASCII, trailing newline: the parser discards CR and terminates
        # on LF, and the last line needs its terminator like every other.
        body = "\r\n".join(probe.autoexec) + "\r\n"
        autoexec_path = scratch_root / AUTOEXEC
        autoexec_path.write_bytes(body.encode("ascii"))
        autoexec_record = {
            "path": str(autoexec_path),
            "sha256": sha256_file(autoexec_path),
            "bytes": len(body),
            "lines": list(probe.autoexec),
        }

    exe = scratch_root / "BEA.exe"
    return {
        "scratchRoot": str(scratch_root),
        "sourceRoot": str(source_root),
        "executableSha256": sha256_file(exe),
        "stagedFiles": staged,
        "createdDirectories": list(probe.make_dirs),
        "autoexec": autoexec_record,
        "removedInheritedLogs": inherited,
    }


def _is_within(candidate: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        candidate.relative_to(parent)
        return True
    except ValueError:
        return False


def collect_artefacts(
    probe: Probe, scratch_root: pathlib.Path, destination: pathlib.Path
) -> dict[str, Any]:
    """Copy declared artefacts, plus the two the engine always speaks through."""

    destination.mkdir(parents=True, exist_ok=True)
    wanted = list(dict.fromkeys((*probe.collect, SETUP_HISTORY, EXCEPTION_LOG)))
    collected: list[dict[str, Any]] = []
    missing: list[str] = []
    for relative in wanted:
        origin = scratch_root / relative
        if not origin.is_file():
            missing.append(relative)
            continue
        target = destination / relative.replace("\\", "/").replace("/", "__")
        shutil.copy2(origin, target)
        collected.append(
            {
                "from": relative,
                "path": str(target),
                "bytes": target.stat().st_size,
                "sha256": sha256_file(target),
            }
        )
    return {"collected": collected, "missing": missing}


def teardown(
    scratch_root: pathlib.Path, keep_scratch: bool
) -> dict[str, Any]:
    """Remove the scratch tree, and remove the autoexec.con whatever happens.

    ``keep_scratch`` preserves the staged copy for a human to look at, but it
    does NOT preserve the autoexec.con.  That file is the landmine; keeping it
    for inspection is never worth the chance it is forgotten.
    """

    removed_autoexec = False
    autoexec_path = scratch_root / AUTOEXEC
    errors: list[str] = []

    if autoexec_path.is_file():
        try:
            autoexec_path.unlink()
            removed_autoexec = True
        except OSError as exc:
            errors.append(f"could not remove {autoexec_path}: {exc}")

    removed_scratch = False
    if not keep_scratch and scratch_root.exists():
        try:
            shutil.rmtree(scratch_root)
            removed_scratch = True
        except OSError as exc:
            errors.append(f"could not remove {scratch_root}: {exc}")

    # Verify rather than assume.  A teardown that silently half-worked is worse
    # than one that failed loudly.
    still_armed = scratch_root.exists() and (scratch_root / AUTOEXEC).is_file()
    if still_armed:
        errors.append(
            f"{autoexec_path} STILL EXISTS after teardown -- it will execute on "
            "every future level load of that tree"
        )
    verified = not errors

    return {
        "removedAutoexec": removed_autoexec,
        "removedScratch": removed_scratch,
        "keptScratch": keep_scratch and scratch_root.exists(),
        "verified": verified,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------


def render_receipt(receipt: dict[str, Any]) -> str:
    """The receipt a human reads.  Same facts as the JSON, in the house style."""

    probe = receipt["probe"]
    oracle = receipt["oracle"]
    staging = receipt.get("staging") or {}
    lines: list[str] = []
    add = lines.append

    verdict = receipt["verdict"]
    add(f"# Probe `{probe['name']}` — {verdict}")
    add("")
    add(f"Status: {receipt['status']}")
    add(f"Date: {receipt['startedUtc']}")
    add(f"Verdict: **{verdict}** — {oracle.get('detail', 'not evaluated')}")
    add(f"Wall time: {receipt['wallSeconds']:.2f} s")
    if probe.get("note"):
        add(f"Note: {probe['note']}")
    add("")

    add("## Staged")
    add("")
    if receipt.get("dryRun"):
        add("Nothing was staged: this was a dry run.")
        add(f"- source root: `{probe['sourceRoot']}`")
        add(f"- scratch root that would have been used: `{receipt['scratchRoot']}`")
    else:
        add(f"- source root `{staging.get('sourceRoot')}`")
        add(f"- scratch root `{staging.get('scratchRoot')}`")
        add(f"- `BEA.exe` sha256 `{staging.get('executableSha256')}`")
        for entry in staging.get("stagedFiles", ()):
            replaced = entry.get("replacedSha256")
            add(
                f"- `{entry['dest']}` ← `{entry['source']}`, "
                f"{entry['bytes']} bytes, sha256 `{entry['sha256']}`"
                + (f", replacing sha256 `{replaced}`" if replaced else "")
            )
        for directory in staging.get("createdDirectories", ()):
            add(f"- created directory `{directory}`")
        autoexec = staging.get("autoexec")
        if autoexec:
            add(
                f"- `{AUTOEXEC}` {autoexec['bytes']} bytes, sha256 "
                f"`{autoexec['sha256']}`:"
            )
            add("")
            add("```")
            for line in autoexec["lines"]:
                add(line)
            add("```")
        else:
            add(f"- no `{AUTOEXEC}` (this probe declared none)")
    add("")
    for witness, digest in (receipt.get("sourceWitness") or {}).items():
        add(f"- source `{witness}` sha256 `{digest}` (re-verified after the run)")
    add("")

    add("## Command")
    add("")
    add("```")
    add(receipt["command"])
    add(f"# working directory: {receipt['workingDirectory']}")
    add("```")
    add("")
    if receipt.get("recording"):
        recording = receipt["recording"]
        add(f"Recording: {recording['status']} — {recording.get('detail', '')}")
        add("")

    add("## Oracle")
    add("")
    add(f"- kind: `{json.dumps(probe['oracle'])}`")
    add(f"- outcome: **{oracle.get('outcome', 'not-evaluated')}**")
    add(f"- detail: {oracle.get('detail', '—')}")
    if oracle.get("exitCode") is not None:
        add(f"- process exit code: {oracle['exitCode']}")
    add("")

    gate = receipt.get("faultGate")
    classification = receipt.get("exitClassification")
    if gate is not None:
        add("## Fault gate — did it finish, or did it die?")
        add("")
        if classification and classification.get("hex"):
            add(f"- exit code {classification['hex']}: {classification['detail']}")
        for trigger in gate.get("triggers", ()):
            add(f"- trigger: {trigger}")
        if gate["vetoed"]:
            add("")
            add(f"**VETOED — {gate['detail']}**")
        elif gate["triggered"]:
            add(f"- {gate['detail']}")
        else:
            add(f"- {gate['detail']}")
        add("")

    diagnosis = receipt.get("diagnosis")
    if diagnosis:
        add("## Diagnosis — was this even a valid measurement?")
        add("")
        add(f"- level-load logged: {diagnosis['levelLoadLogged']}")
        add(f"- fault log present: {diagnosis['fatalFaultLogPresent']}")
        add(f"- {diagnosis['interpretation']}")
        if diagnosis.get("setupHistoryTail"):
            add("")
            add(f"`{SETUP_HISTORY}` tail:")
            add("")
            add("```")
            lines.extend(diagnosis["setupHistoryTail"])
            add("```")
        add("")

    artefacts = receipt.get("artefacts")
    if artefacts:
        add("## Artefacts")
        add("")
        for entry in artefacts.get("collected", ()):
            add(f"- `{entry['from']}` → `{entry['path']}` ({entry['bytes']} bytes)")
        for name in artefacts.get("missing", ()):
            add(f"- `{name}` — not produced")
        add("")

    add("## Teardown")
    add("")
    down = receipt.get("teardown") or {}
    add(f"- {AUTOEXEC} removed: {down.get('removedAutoexec')}")
    add(f"- scratch tree removed: {down.get('removedScratch')}")
    add(f"- verified: {down.get('verified')}")
    for error in down.get("errors", ()):
        add(f"- **{error}**")
    stale = receipt.get("staleAutoexecScan") or []
    add(f"- pre-run stale {AUTOEXEC} scan: {len(stale)} found, 0 armed")
    for entry in stale:
        add(f"  - inert: `{entry['path']}`")
    add("")

    if receipt.get("failure"):
        add("## Failure")
        add("")
        add(f"**{receipt['failure']}**")
        add("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Running one probe
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    return _datetime.datetime.now(_datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def build_record_command(
    probe: Probe, scratch_root: pathlib.Path, trace_name: str
) -> list[str]:
    """The TTD arm, delegated whole to the script that already owns it.

    This harness deliberately knows nothing about TTD interlocks, drive
    policy, elevation refusal or receipt deferral: ``tools/ttd_record.ps1``
    owns all of it and reimplementing any part would give this lane a second,
    weaker copy of rules that were expensive to get right.
    """

    script = ROOT / "tools" / "ttd_record.ps1"
    if not script.is_file():
        raise ProbeError(f"recording requested but {script} is missing")
    return [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-TargetRoot",
        str(scratch_root),
        "-Name",
        trace_name,
        "-Seconds",
        str(probe.record_seconds),
        "-GameArguments",
        ",".join(probe.argv),
    ]


def run_probe(
    probe: Probe,
    *,
    manifest_dir: pathlib.Path,
    out_dir: pathlib.Path,
    scratch_parent: pathlib.Path,
    launcher: Optional[Any] = None,
    clock: Optional[Clock] = None,
    dry_run: bool = False,
    keep_scratch: bool = False,
    strict_autoexec: bool = False,
    poll_seconds: float = 0.25,
    guard_roots: Optional[Sequence[pathlib.Path]] = None,
) -> dict[str, Any]:
    """Stage, launch, wait, collect, tear down, and return the receipt."""

    launcher = launcher or SubprocessLauncher()
    clock = clock or Clock()
    started_wall = time.monotonic()
    stamp = _datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = out_dir / f"{probe.name}-{stamp}"
    scratch_root = scratch_parent / f"{probe.name}-{stamp}"
    source_root = (manifest_dir / probe.source_root).resolve()

    receipt: dict[str, Any] = {
        "probe": {
            "name": probe.name,
            "level": probe.level,
            "sourceRoot": str(source_root),
            "oracle": probe.oracle,
            "note": probe.note,
            "record": probe.record,
        },
        "startedUtc": _utc_now(),
        "dryRun": dry_run,
        "runDirectory": str(run_dir),
        "scratchRoot": str(scratch_root),
        "workingDirectory": str(scratch_root),
        "command": " ".join(
            shlex.quote(part)
            for part in [str(scratch_root / "BEA.exe"), *probe.argv]
        ),
        "oracle": {},
        "status": "running",
        "verdict": "UNKNOWN",
        "failure": None,
    }

    handle: Optional[ProcessHandle] = None
    staged = False
    try:
        witness = check_source_root(source_root)
        receipt["sourceWitness"] = witness

        roots = list(guard_roots) if guard_roots is not None else [
            source_root,
            scratch_parent,
        ]
        stale = assert_no_stale_autoexec(roots, strict=strict_autoexec)
        receipt["staleAutoexecScan"] = [dataclasses.asdict(s) for s in stale]

        if dry_run:
            receipt["status"] = "dry-run"
            receipt["verdict"] = "NOT RUN (dry run)"
            receipt["oracle"] = {
                "outcome": "not-evaluated",
                "detail": "dry run: nothing was staged and nothing was launched",
            }
            if probe.record:
                receipt["recording"] = {
                    "status": "planned",
                    "detail": " ".join(
                        shlex.quote(p)
                        for p in build_record_command(
                            probe, scratch_root, f"{probe.name}-{stamp}"
                        )
                    ),
                }
            receipt["teardown"] = {
                "removedAutoexec": False,
                "removedScratch": False,
                "verified": True,
                "errors": [],
            }
            return _finish(receipt, started_wall, run_dir, write=True)

        receipt["staging"] = stage_scratch(
            probe, source_root, scratch_root, manifest_dir
        )
        staged = True

        if probe.record:
            command = build_record_command(
                probe, scratch_root, f"{probe.name}-{stamp}"
            )
            receipt["command"] = " ".join(shlex.quote(p) for p in command)
            receipt["recording"] = {
                "status": "delegated",
                "detail": f"tools/ttd_record.ps1 owns this launch; "
                f"trace name {probe.name}-{stamp}",
            }
            handle = launcher.launch(
                pathlib.Path(command[0]), command[1:], scratch_root
            )
        else:
            handle = launcher.launch(
                scratch_root / "BEA.exe", list(probe.argv), scratch_root
            )

        receipt["oracle"] = wait_for_oracle(
            probe.oracle,
            scratch_root,
            handle,
            clock,
            poll_seconds,
            allow_fault_exit=probe.allow_fault_exit,
        )
        receipt["diagnosis"] = diagnose(scratch_root, probe.level)
        receipt["artefacts"] = collect_artefacts(
            probe, scratch_root, run_dir / "artefacts"
        )
        receipt["exitClassification"] = classify_exit_code(
            receipt["oracle"].get("exitCode")
        )
        receipt["faultGate"] = apply_fault_gate(
            probe,
            receipt["oracle"],
            receipt["diagnosis"],
            receipt["exitClassification"],
        )
        satisfied = receipt["oracle"]["outcome"] == "satisfied"
        if receipt["faultGate"]["vetoed"]:
            satisfied = False
        receipt["verdict"] = "PASS" if satisfied else "FAIL"
        receipt["status"] = "complete"

    except ProbeError as exc:
        receipt["status"] = "error"
        receipt["verdict"] = "ERROR"
        receipt["failure"] = str(exc)
    except Exception as exc:  # pragma: no cover - defensive, still fails closed
        receipt["status"] = "error"
        receipt["verdict"] = "ERROR"
        receipt["failure"] = f"{type(exc).__name__}: {exc}"
    finally:
        if handle is not None:
            try:
                if handle.poll() is None:
                    handle.kill()
            except Exception as exc:  # pragma: no cover
                receipt.setdefault("killErrors", []).append(str(exc))
        if staged:
            down = teardown(scratch_root, keep_scratch)
            receipt["teardown"] = down
            if not down["verified"]:
                receipt["status"] = "error"
                receipt["verdict"] = "ERROR"
                receipt["failure"] = (
                    (receipt.get("failure") or "")
                    + " | teardown failed: "
                    + "; ".join(down["errors"])
                ).strip(" |")
            try:
                verify_source_untouched(source_root, receipt.get("sourceWitness", {}))
            except ProbeError as exc:
                receipt["status"] = "error"
                receipt["verdict"] = "ERROR"
                receipt["failure"] = (
                    (receipt.get("failure") or "") + " | " + str(exc)
                ).strip(" |")
        elif "teardown" not in receipt:
            receipt["teardown"] = {
                "removedAutoexec": False,
                "removedScratch": False,
                "verified": True,
                "errors": [],
                "note": "nothing was staged",
            }

    return _finish(receipt, started_wall, run_dir, write=True)


def _finish(
    receipt: dict[str, Any],
    started_wall: float,
    run_dir: pathlib.Path,
    write: bool,
) -> dict[str, Any]:
    receipt["wallSeconds"] = round(time.monotonic() - started_wall, 3)
    receipt["finishedUtc"] = _utc_now()
    if write:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "receipt.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=False) + "\n", encoding="utf-8"
        )
        (run_dir / "receipt.md").write_text(render_receipt(receipt), encoding="utf-8")
    return receipt


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def default_scratch_parent() -> pathlib.Path:
    override = os.environ.get("BEA_PROBE_SCRATCH")
    if override:
        return pathlib.Path(override)
    return pathlib.Path(os.environ.get("TEMP", ".")) / "bea-probe-scratch"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=pathlib.Path, help="probe manifest JSON")
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=ROOT / "local-lab" / "probe-runs",
        help="where receipts and artefacts are written",
    )
    parser.add_argument(
        "--scratch",
        type=pathlib.Path,
        default=None,
        help="parent directory for staged scratch copies",
    )
    parser.add_argument("--only", action="append", default=[], help="probe name")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--keep-scratch",
        action="store_true",
        help="keep the staged tree (autoexec.con is removed regardless)",
    )
    parser.add_argument(
        "--strict-autoexec",
        action="store_true",
        help="treat any autoexec.con anywhere as fatal, not just armed ones",
    )
    args = parser.parse_args(argv)

    try:
        probes = load_manifest(args.manifest)
    except ProbeError as exc:
        print(f"FAIL closed: {exc}", file=sys.stderr)
        return 2

    if args.only:
        wanted = set(args.only)
        unknown = wanted - {p.name for p in probes}
        if unknown:
            print(f"FAIL closed: no such probe: {', '.join(sorted(unknown))}",
                  file=sys.stderr)
            return 2
        probes = [p for p in probes if p.name in wanted]

    scratch_parent = args.scratch or default_scratch_parent()
    manifest_dir = args.manifest.resolve().parent
    receipts = []
    for probe in probes:
        print(f"--- probe {probe.name} (level {probe.level})", flush=True)
        receipt = run_probe(
            probe,
            manifest_dir=manifest_dir,
            out_dir=args.out,
            scratch_parent=scratch_parent,
            dry_run=args.dry_run,
            keep_scratch=args.keep_scratch,
            strict_autoexec=args.strict_autoexec,
        )
        receipts.append(receipt)
        print(
            f"    {receipt['verdict']}: {receipt['oracle'].get('detail', '')}"
            f"  [{receipt['wallSeconds']:.2f}s]  {receipt['runDirectory']}",
            flush=True,
        )
        if receipt.get("failure"):
            print(f"    FAILURE: {receipt['failure']}", file=sys.stderr, flush=True)

    passed = sum(1 for r in receipts if r["verdict"] == "PASS")
    errored = sum(1 for r in receipts if r["verdict"] == "ERROR")
    dry = sum(1 for r in receipts if r.get("dryRun"))
    print(f"\n{passed} passed, {len(receipts) - passed - dry} not passed, "
          f"{dry} dry-run, {errored} errored, {len(receipts)} probes")
    return exit_code_for(receipts)


def exit_code_for(receipts: Sequence[dict[str, Any]]) -> int:
    """The exit code is the only thing an unattended caller reads.

    AN ERROR IS NEVER EXCUSED BY --dry-run.  A refused interlock during a dry
    run is exactly the thing a dry run exists to surface; reporting it in the
    receipt and then exiting 0 would let an unattended caller treat a
    fail-closed refusal as a clean plan.  Measured on the first live dry run of
    this harness, which did precisely that.
    """

    if any(r["verdict"] == "ERROR" for r in receipts):
        return 2
    dry = sum(1 for r in receipts if r.get("dryRun"))
    if dry == len(receipts):
        return 0
    passed = sum(1 for r in receipts if r["verdict"] == "PASS")
    return 0 if passed == len(receipts) - dry else 1


if __name__ == "__main__":
    raise SystemExit(main())
