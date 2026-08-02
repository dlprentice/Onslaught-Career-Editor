#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the probe harness, and a proof that they are capable of failing.

NO TEST HERE LAUNCHES THE GAME.  A fake launcher stands in for ``BEA.exe`` and
writes exactly the artefacts the real engine writes -- ``setuphistory.txt``,
``OnslaughtException.txt``, ``data/Memory/<name>.txt`` -- on a fake clock, so an
oracle with a 90 second timeout is exercised in under a millisecond.  Proving the
harness against the real binary is a later, separate phase.

    python tools/probe/probe_harness_tests.py                # run the suite
    python tools/probe/probe_harness_tests.py --prove-can-fail

THE SECOND MODE IS THE POINT.  A guard that has never been observed failing is
indistinguishable from a guard that is not wired up: this project has already
shipped one check that passed because it could not fail.  ``--prove-can-fail``
breaks each guarded behaviour in turn -- disables the pristine-hash interlock,
neuters the stale-``autoexec.con`` scan, makes teardown skip the file, makes the
``survives`` oracle always agree -- and asserts that the test which guards it
then FAILS.  A mutation that leaves the suite green means that test proves
nothing, and is reported as an error.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from typing import Any, Callable, Optional

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import probe_harness as ph  # noqa: E402


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeClock(ph.Clock):
    """Time only moves when the harness sleeps, so timeouts are instant."""

    def __init__(self) -> None:
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += seconds


class FakeHandle(ph.ProcessHandle):
    """A pretend game.  ``script`` is a list of (at_seconds, action).

    An action is either the string ``"exit"`` (with an optional exit code) or a
    callable taking the working directory -- which is how a fake run writes the
    same files the engine writes.
    """

    def __init__(
        self,
        clock: FakeClock,
        cwd: pathlib.Path,
        script: list[tuple[float, Any]],
    ) -> None:
        self.clock = clock
        self.cwd = cwd
        self.script = sorted(script, key=lambda item: item[0])
        self.start = clock.now()
        self.exit_code: Optional[int] = None
        self.killed = False
        self._done: set[int] = set()

    def _advance(self) -> None:
        elapsed = self.clock.now() - self.start
        for index, (at, action) in enumerate(self.script):
            if index in self._done or elapsed < at:
                continue
            self._done.add(index)
            if isinstance(action, tuple) and action[0] == "exit":
                self.exit_code = action[1]
            elif action == "exit":
                self.exit_code = 0
            else:
                action(self.cwd)

    def poll(self) -> Optional[int]:
        self._advance()
        return self.exit_code

    def kill(self) -> None:
        self.killed = True
        if self.exit_code is None:
            self.exit_code = -1

    @property
    def pid(self) -> int:
        return 4242


class FakeLauncher:
    def __init__(self, clock: FakeClock, script: list[tuple[float, Any]]) -> None:
        self.clock = clock
        self.script = script
        self.calls: list[tuple[str, list[str], str]] = []
        self.handle: Optional[FakeHandle] = None
        self.raise_on_launch: Optional[Exception] = None

    def launch(self, executable, argv, cwd):  # noqa: ANN001 - mirrors the seam
        self.calls.append((str(executable), list(argv), str(cwd)))
        if self.raise_on_launch is not None:
            raise self.raise_on_launch
        self.handle = FakeHandle(self.clock, pathlib.Path(cwd), self.script)
        return self.handle


def writes(relative: str, text: str) -> Callable[[pathlib.Path], None]:
    def action(cwd: pathlib.Path) -> None:
        target = cwd / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    return action


def appends(relative: str, text: str) -> Callable[[pathlib.Path], None]:
    def action(cwd: pathlib.Path) -> None:
        target = cwd / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(text)

    return action


# ---------------------------------------------------------------------------
# Base case with a fake game tree
# ---------------------------------------------------------------------------


class HarnessCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="probe-harness-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.source = self.tmp / "safe-copy"
        (self.source / "data" / "Resources").mkdir(parents=True)
        (self.source / "BEA.exe").write_bytes(b"MZ fake game binary")
        (self.source / ph.SETUP_HISTORY).write_text(
            "Setup started\n", encoding="utf-8"
        )
        (self.source / "data" / "Resources" / "905_res_PC.aya").write_bytes(
            b"AYA original payload"
        )
        self.out = self.tmp / "runs"
        self.scratch = self.tmp / "scratch"
        self.payloads = self.tmp / "payloads"
        self.payloads.mkdir()

    def probe(self, **overrides: Any) -> ph.Probe:
        raw: dict[str, Any] = {
            "name": "unit",
            "level": 100,
            "sourceRoot": str(self.source),
            "autoexec": ["Echo UNIT", "Quit"],
            "oracle": {"kind": "processExit", "timeoutSeconds": 90},
        }
        raw.update(overrides)
        return ph.parse_probe(raw)

    def run_probe(
        self,
        probe: ph.Probe,
        script: list[tuple[float, Any]],
        **kwargs: Any,
    ) -> tuple[dict[str, Any], FakeLauncher]:
        clock = FakeClock()
        launcher = FakeLauncher(clock, script)
        if "launcher" in kwargs:
            launcher = kwargs.pop("launcher")
            launcher.clock = clock
        receipt = ph.run_probe(
            probe,
            manifest_dir=self.tmp,
            out_dir=self.out,
            scratch_parent=self.scratch,
            launcher=launcher,
            clock=clock,
            guard_roots=[self.source, self.scratch],
            poll_seconds=0.25,
            **kwargs,
        )
        return receipt, launcher


# ---------------------------------------------------------------------------
# Manifest parsing -- refusing what it cannot check
# ---------------------------------------------------------------------------


class ManifestTests(HarnessCase):
    def test_unknown_probe_key_is_refused(self) -> None:
        with self.assertRaises(ph.ProbeError) as caught:
            ph.parse_probe(
                {
                    "name": "x",
                    "level": 1,
                    "sourceRoot": ".",
                    "oracle": {"kind": "processExit"},
                    "orcale": {"kind": "processExit"},
                }
            )
        self.assertIn("orcale", str(caught.exception))

    def test_unknown_oracle_kind_is_refused(self) -> None:
        with self.assertRaises(ph.ProbeError) as caught:
            ph.parse_probe(
                {
                    "name": "x",
                    "level": 1,
                    "sourceRoot": ".",
                    "oracle": {"kind": "itWorked"},
                }
            )
        self.assertIn("unknown oracle kind", str(caught.exception))

    def test_file_oracle_without_a_path_is_refused(self) -> None:
        with self.assertRaises(ph.ProbeError):
            ph.parse_probe(
                {
                    "name": "x",
                    "level": 1,
                    "sourceRoot": ".",
                    "oracle": {"kind": "fileAppears"},
                }
            )

    def test_level_in_game_arguments_is_refused(self) -> None:
        with self.assertRaises(ph.ProbeError) as caught:
            ph.parse_probe(
                {
                    "name": "x",
                    "level": 1,
                    "sourceRoot": ".",
                    "gameArguments": ["-skipfmv", "-level", "1"],
                    "oracle": {"kind": "processExit"},
                }
            )
        self.assertIn("-level", str(caught.exception))

    def test_duplicate_probe_names_are_refused(self) -> None:
        manifest = self.tmp / "m.json"
        entry = {
            "name": "dup",
            "level": 1,
            "sourceRoot": ".",
            "oracle": {"kind": "processExit"},
        }
        manifest.write_text(json.dumps({"probes": [entry, entry]}), encoding="utf-8")
        with self.assertRaises(ph.ProbeError) as caught:
            ph.load_manifest(manifest)
        self.assertIn("duplicate", str(caught.exception))

    def test_level_is_always_on_the_command_line(self) -> None:
        probe = self.probe(level=521)
        self.assertEqual(probe.argv[-2:], ("-level", "521"))


# ---------------------------------------------------------------------------
# Source-tree interlocks
# ---------------------------------------------------------------------------


class SourceRootTests(HarnessCase):
    def test_installed_game_path_is_refused(self) -> None:
        fake = self.tmp / "Program Files (x86)" / "Steam" / "steamapps" / "bea"
        fake.mkdir(parents=True)
        (fake / "BEA.exe").write_bytes(b"MZ")
        with self.assertRaises(ph.ProbeError) as caught:
            ph.check_source_root(fake)
        self.assertIn("installed-game path", str(caught.exception))

    def test_installed_game_path_is_refused_even_when_it_does_not_exist(
        self,
    ) -> None:
        """The safety refusal outranks the existence check.

        Found live: a manifest pointing at a Program Files path that is not
        present on this machine was refused with 'source root does not exist',
        which reads as a fixable typo rather than 'you are pointing at the
        user's installed game'.
        """

        absent = self.tmp / "Program Files" / "Steam" / "steamapps" / "nope"
        with self.assertRaises(ph.ProbeError) as caught:
            ph.check_source_root(absent)
        self.assertIn("installed-game path", str(caught.exception))

    def test_source_root_without_bea_exe_is_refused(self) -> None:
        empty = self.tmp / "empty"
        empty.mkdir()
        with self.assertRaises(ph.ProbeError):
            ph.check_source_root(empty)

    def test_refuses_written_pristine_specimen(self) -> None:
        (self.source / "BEA.exe.original.backup").write_bytes(b"NOT PRISTINE")
        with self.assertRaises(ph.ProbeError) as caught:
            ph.check_source_root(self.source)
        self.assertIn("not pristine", str(caught.exception))

    def test_accepts_a_matching_pristine_specimen(self) -> None:
        body = b"pretend pristine specimen"
        (self.source / "BEA.exe.original.backup").write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        original = ph.PRISTINE_SHA256
        ph.PRISTINE_SHA256 = digest
        try:
            witness = ph.check_source_root(self.source)
        finally:
            ph.PRISTINE_SHA256 = original
        self.assertIn("BEA.exe.original.backup", witness)

    def test_a_run_that_writes_to_the_source_tree_is_an_error(self) -> None:
        source = self.source

        def corrupt(_cwd: pathlib.Path) -> None:
            (source / "BEA.exe").write_bytes(b"MZ tampered")

        receipt, _ = self.run_probe(
            self.probe(), [(0.5, corrupt), (1.0, "exit")]
        )
        self.assertEqual(receipt["verdict"], "ERROR")
        self.assertIn("source tree was modified", receipt["failure"])


# ---------------------------------------------------------------------------
# The autoexec.con landmine
# ---------------------------------------------------------------------------


class StaleAutoexecTests(HarnessCase):
    def test_armed_stale_autoexec_stops_the_run(self) -> None:
        (self.source / ph.AUTOEXEC).write_text("Quit\r\n", encoding="ascii")
        receipt, launcher = self.run_probe(self.probe(), [(1.0, "exit")])
        self.assertEqual(receipt["verdict"], "ERROR")
        self.assertIn("stale autoexec.con", receipt["failure"])
        self.assertIn("ARMED", receipt["failure"])
        self.assertEqual(launcher.calls, [], "nothing may launch after a refusal")

    def test_inert_stale_autoexec_is_reported_not_fatal(self) -> None:
        archive = self.tmp / "archived-probe"
        archive.mkdir()
        (archive / ph.AUTOEXEC).write_text("Quit\r\n", encoding="ascii")
        stale = ph.assert_no_stale_autoexec([archive])
        self.assertEqual(len(stale), 1)
        self.assertFalse(stale[0].armed)

    def test_strict_mode_makes_an_inert_file_fatal(self) -> None:
        archive = self.tmp / "archived-probe"
        archive.mkdir()
        (archive / ph.AUTOEXEC).write_text("Quit\r\n", encoding="ascii")
        with self.assertRaises(ph.ProbeError):
            ph.assert_no_stale_autoexec([archive], strict=True)

    def test_armed_means_beside_a_bea_exe(self) -> None:
        armed = self.tmp / "armed"
        armed.mkdir()
        (armed / "BEA.exe").write_bytes(b"MZ")
        (armed / ph.AUTOEXEC).write_text("Quit\r\n", encoding="ascii")
        found = ph.scan_for_stale_autoexec([armed])
        self.assertEqual([s.armed for s in found], [True])


# ---------------------------------------------------------------------------
# Oracles
# ---------------------------------------------------------------------------


class OracleTests(HarnessCase):
    def test_process_exit_oracle_passes_when_the_game_quits(self) -> None:
        receipt, _ = self.run_probe(self.probe(), [(3.0, ("exit", 0))])
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["oracle"]["outcome"], "satisfied")
        self.assertEqual(receipt["oracle"]["exitCode"], 0)

    def test_process_exit_oracle_times_out_when_the_game_hangs(self) -> None:
        probe = self.probe(oracle={"kind": "processExit", "timeoutSeconds": 5})
        receipt, launcher = self.run_probe(probe, [])
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertEqual(receipt["oracle"]["outcome"], "unsatisfied-timeout")
        self.assertTrue(launcher.handle.killed, "a hung game must be killed")

    def test_file_appears_oracle_passes_on_a_console_written_file(self) -> None:
        probe = self.probe(
            oracle={
                "kind": "fileAppears",
                "path": "data/Memory/probe_ok.txt",
                "minBytes": 10,
                "timeoutSeconds": 30,
            },
            collect=["data/Memory/probe_ok.txt"],
        )
        receipt, _ = self.run_probe(
            probe, [(5.0, writes("data/Memory/probe_ok.txt", "heap report " * 10))]
        )
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertIn("probe_ok.txt", receipt["oracle"]["detail"])
        collected = [c["from"] for c in receipt["artefacts"]["collected"]]
        self.assertIn("data/Memory/probe_ok.txt", collected)

    def test_file_appears_oracle_fails_if_the_game_dies_first(self) -> None:
        probe = self.probe(
            oracle={
                "kind": "fileAppears",
                "path": "data/Memory/probe_ok.txt",
                "timeoutSeconds": 30,
            }
        )
        receipt, _ = self.run_probe(probe, [(2.0, ("exit", -1073741819))])
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertEqual(receipt["oracle"]["outcome"], "unsatisfied-process-exited")

    def test_file_appears_oracle_rejects_a_too_small_file(self) -> None:
        probe = self.probe(
            oracle={
                "kind": "fileAppears",
                "path": "out.txt",
                "minBytes": 100,
                "timeoutSeconds": 5,
            }
        )
        receipt, _ = self.run_probe(probe, [(1.0, writes("out.txt", "tiny"))])
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertIn("need >=", receipt["oracle"]["detail"])

    def test_fatal_fault_oracle_is_the_poison_control(self) -> None:
        probe = self.probe(
            oracle={"kind": "fatalFault", "timeoutSeconds": 30}, level=905
        )
        receipt, _ = self.run_probe(
            probe,
            [
                (13.0, writes(ph.EXCEPTION_LOG, "0xC0000005 access violation\n")),
                (13.5, ("exit", -1073741819)),
            ],
        )
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertIn("faulted", receipt["oracle"]["detail"])

    def test_fatal_fault_oracle_fails_when_nothing_faults(self) -> None:
        probe = self.probe(oracle={"kind": "fatalFault", "timeoutSeconds": 5})
        receipt, _ = self.run_probe(probe, [])
        self.assertEqual(receipt["verdict"], "FAIL")

    def test_setup_history_oracle_reads_the_level_load_line(self) -> None:
        probe = self.probe(
            oracle={
                "kind": "setupHistoryContains",
                "text": "Game::LoadLevel 100",
                "timeoutSeconds": 30,
            }
        )
        receipt, _ = self.run_probe(
            probe, [(4.0, appends(ph.SETUP_HISTORY, "Game::LoadLevel 100\n"))]
        )
        self.assertEqual(receipt["verdict"], "PASS")

    def test_survives_oracle_passes_only_at_the_deadline(self) -> None:
        probe = self.probe(oracle={"kind": "survives", "timeoutSeconds": 20})
        receipt, launcher = self.run_probe(probe, [])
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertGreaterEqual(receipt["oracle"]["elapsedSeconds"], 20)
        self.assertTrue(launcher.handle.killed)

    def test_survives_oracle_fails_on_an_early_exit(self) -> None:
        probe = self.probe(oracle={"kind": "survives", "timeoutSeconds": 20})
        receipt, _ = self.run_probe(probe, [(6.0, ("exit", -1073741819))])
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertIn("exited early", receipt["oracle"]["detail"])

    def test_survives_oracle_fails_when_a_fault_log_appears(self) -> None:
        probe = self.probe(oracle={"kind": "survives", "timeoutSeconds": 20})
        receipt, _ = self.run_probe(
            probe, [(6.0, writes(ph.EXCEPTION_LOG, "0xC0000005\n"))]
        )
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertIn("faulted", receipt["oracle"]["detail"])

    def test_all_oracle_requires_every_arm(self) -> None:
        probe = self.probe(
            oracle={
                "kind": "all",
                "timeoutSeconds": 30,
                "of": [
                    {"kind": "setupHistoryContains", "text": "Game::LoadLevel 100"},
                    {"kind": "processExit"},
                ],
            }
        )
        receipt, _ = self.run_probe(probe, [(9.0, ("exit", 0))])
        self.assertEqual(receipt["verdict"], "FAIL")

        receipt2, _ = self.run_probe(
            probe,
            [
                (4.0, appends(ph.SETUP_HISTORY, "Game::LoadLevel 100\n")),
                (9.0, ("exit", 0)),
            ],
        )
        self.assertEqual(receipt2["verdict"], "PASS")


# ---------------------------------------------------------------------------
# The fault gate — did it finish, or did it die?
# ---------------------------------------------------------------------------


class ExitClassificationTests(unittest.TestCase):
    """The pure classifier, away from any run.

    Both directions matter.  A gate that misses a crash manufactures false
    accepts; a gate that calls an ordinary exit a crash gets switched off by the
    third person it inconveniences, and then misses every crash after that.
    """

    def test_access_violation_is_a_fault(self) -> None:
        found = ph.classify_exit_code(0xC0000005)
        self.assertTrue(found["isFault"])
        self.assertEqual(found["status"], "STATUS_ACCESS_VIOLATION")

    def test_the_posix_style_negative_form_is_the_same_code(self) -> None:
        """CPython reports the raw DWORD on Windows and a negative elsewhere.

        -1073741819 and 3221225477 are one access violation, not two, and a
        classifier that only knew the unsigned spelling would pass every fake,
        every wrapper and every POSIX run straight through.
        """

        self.assertEqual(
            ph.classify_exit_code(-1073741819)["status"],
            ph.classify_exit_code(0xC0000005)["status"],
        )

    def test_stack_overflow_and_heap_corruption_are_faults(self) -> None:
        self.assertTrue(ph.classify_exit_code(0xC00000FD)["isFault"])
        self.assertTrue(ph.classify_exit_code(0xC0000374)["isFault"])

    def test_an_unnamed_code_in_the_error_band_is_still_a_fault(self) -> None:
        found = ph.classify_exit_code(0xC0009999)
        self.assertTrue(found["isFault"])
        self.assertIn("unnamed", found["status"])

    def test_zero_is_a_clean_finish(self) -> None:
        self.assertFalse(ph.classify_exit_code(0)["isFault"])

    def test_a_small_nonzero_exit_is_not_a_fault(self) -> None:
        """The game exiting 1 or 3 is a refusal, not a crash.

        Treating it as a crash would veto every legitimate early-exit probe.
        """

        for code in (1, 2, 3, 255):
            self.assertFalse(ph.classify_exit_code(code)["isFault"], code)

    def test_the_harness_own_kill_is_not_called_an_engine_fault(self) -> None:
        """-1 normalises to 0xFFFFFFFF, which has NTSTATUS ERROR severity.

        A blanket 'severity == ERROR' rule would therefore report the harness's
        own timeout kill as an engine crash -- a false accusation that would
        make every hung-game receipt read like a segfault.
        """

        self.assertFalse(ph.classify_exit_code(-1)["isFault"])
        self.assertFalse(ph.classify_exit_code(0xFFFFFFFF)["isFault"])


class FaultGateTests(HarnessCase):
    def test_bare_process_exit_refuses_an_access_violation(self) -> None:
        """THE GAP THIS CLOSES.

        Before 2026-08-01 this exact run reported PASS: the oracle asked only
        'did it exit', and a process that takes an access violation exits.
        """

        receipt, _ = self.run_probe(self.probe(), [(8.0, ("exit", 0xC0000005))])
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(receipt["exitClassification"]["isFault"])
        self.assertEqual(
            receipt["exitClassification"]["status"], "STATUS_ACCESS_VIOLATION"
        )

    def test_bare_process_exit_refuses_the_negative_spelling_too(self) -> None:
        receipt, _ = self.run_probe(self.probe(), [(8.0, ("exit", -1073741819))])
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(receipt["exitClassification"]["isFault"])

    def test_a_clean_exit_still_passes(self) -> None:
        """The gate must not break the ordinary case it sits in front of."""

        receipt, _ = self.run_probe(self.probe(), [(3.0, ("exit", 0))])
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertFalse(receipt["faultGate"]["triggered"])

    def test_a_probe_may_ask_for_the_crash_by_exact_code(self) -> None:
        probe = self.probe(
            oracle={
                "kind": "processExit",
                "expectExitCode": 0xC0000005,
                "timeoutSeconds": 30,
            }
        )
        receipt, _ = self.run_probe(probe, [(8.0, ("exit", 0xC0000005))])
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertTrue(receipt["faultGate"]["triggered"])
        self.assertTrue(receipt["faultGate"]["optedIn"])
        self.assertFalse(receipt["faultGate"]["vetoed"])

    def test_allow_fault_exit_opts_out_of_the_gate(self) -> None:
        probe = self.probe(allowFaultExit=True)
        receipt, _ = self.run_probe(probe, [(8.0, ("exit", 0xC0000005))])
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertTrue(receipt["faultGate"]["optedIn"])

    def test_the_gate_vetoes_a_file_appears_pass_on_a_crashed_run(self) -> None:
        """The laundering case, and the reason the gate is above the oracle.

        The console writes its file, the oracle is satisfied by that file, and
        the engine faults a second later.  Fixing only ``processExit`` would
        leave this run reporting PASS with a fault log sitting next to it.
        """

        probe = self.probe(
            oracle={
                "kind": "fileAppears",
                "path": "data/Memory/probe_ok.txt",
                "timeoutSeconds": 30,
                "settleSeconds": 5,
            }
        )
        receipt, _ = self.run_probe(
            probe,
            [
                (4.0, writes("data/Memory/probe_ok.txt", "heap report")),
                (5.0, writes(ph.EXCEPTION_LOG, "0xC0000005 in CThing::Update\n")),
                (6.0, ("exit", 0)),
            ],
        )
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertEqual(receipt["oracle"]["outcome"], "satisfied-then-faulted")
        self.assertTrue(receipt["faultGate"]["vetoed"])
        self.assertIn("CRASHED", receipt["faultGate"]["detail"])

    def test_without_a_settle_window_the_late_crash_is_not_observed(self) -> None:
        """THE HONEST LIMIT, recorded on purpose rather than papered over.

        Same run, no ``settleSeconds``: the oracle is satisfied the instant the
        file appears and the harness stops looking, so the fault one second
        later is never seen.  That is a NON-OBSERVATION, not an absence, and the
        receipt has to say which -- ``processAliveAtDecision`` is the field that
        stops a reader mistaking the second for the first.
        """

        probe = self.probe(
            oracle={
                "kind": "fileAppears",
                "path": "data/Memory/probe_ok.txt",
                "timeoutSeconds": 30,
            }
        )
        receipt, _ = self.run_probe(
            probe,
            [
                (4.0, writes("data/Memory/probe_ok.txt", "heap report")),
                (5.0, writes(ph.EXCEPTION_LOG, "0xC0000005 in CThing::Update\n")),
            ],
        )
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertTrue(receipt["oracle"]["processAliveAtDecision"])
        self.assertEqual(receipt["oracle"]["settleSeconds"], 0)

    def test_a_settle_window_that_stays_clean_still_passes(self) -> None:
        probe = self.probe(
            oracle={
                "kind": "fileAppears",
                "path": "data/Memory/probe_ok.txt",
                "timeoutSeconds": 30,
                "settleSeconds": 5,
            }
        )
        receipt, _ = self.run_probe(
            probe, [(4.0, writes("data/Memory/probe_ok.txt", "heap report"))]
        )
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["oracle"]["outcome"], "satisfied")
        self.assertGreaterEqual(receipt["oracle"]["settleObserved"], 5.0)

    def test_the_exception_log_vetoes_even_on_a_zero_exit(self) -> None:
        """BEA installs its own handler.  A handler that logs and then exits
        cleanly produces a crash whose exit code is 0, which the code-based
        trigger cannot see at all."""

        receipt, _ = self.run_probe(
            self.probe(),
            [
                (5.0, writes(ph.EXCEPTION_LOG, "fatal\n")),
                (6.0, ("exit", 0)),
            ],
        )
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertFalse(receipt["exitClassification"]["isFault"])
        self.assertTrue(receipt["faultGate"]["vetoed"])

    def test_the_fatal_fault_oracle_is_not_vetoed_by_its_own_subject(self) -> None:
        """The poison control asks for the crash; the gate must not eat it."""

        probe = self.probe(
            oracle={"kind": "fatalFault", "timeoutSeconds": 30}, level=905
        )
        receipt, _ = self.run_probe(
            probe,
            [
                (13.0, writes(ph.EXCEPTION_LOG, "0xC0000005 access violation\n")),
                (14.0, ("exit", 0xC0000005)),
            ],
        )
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertTrue(receipt["faultGate"]["optedIn"])

    def test_the_receipt_says_the_run_crashed_in_words(self) -> None:
        receipt, _ = self.run_probe(self.probe(), [(8.0, ("exit", 0xC0000005))])
        rendered = ph.render_receipt(receipt)
        self.assertIn("Fault gate", rendered)
        self.assertIn("STATUS_ACCESS_VIOLATION", rendered)


# ---------------------------------------------------------------------------
# Staging, diagnosis, teardown, receipts
# ---------------------------------------------------------------------------


class StagingTests(HarnessCase):
    def test_staging_hashes_the_payload_and_what_it_replaced(self) -> None:
        payload = self.payloads / "authored.aya"
        payload.write_bytes(b"AYA authored payload")
        probe = self.probe(
            stage=[
                {
                    "source": str(payload),
                    "dest": "data/Resources/905_res_PC.aya",
                    "expectSha256": hashlib.sha256(
                        b"AYA authored payload"
                    ).hexdigest(),
                }
            ]
        )
        receipt, _ = self.run_probe(probe, [(1.0, "exit")])
        self.assertEqual(receipt["verdict"], "PASS")
        entry = receipt["staging"]["stagedFiles"][0]
        self.assertEqual(
            entry["sha256"], hashlib.sha256(b"AYA authored payload").hexdigest()
        )
        self.assertEqual(
            entry["replacedSha256"],
            hashlib.sha256(b"AYA original payload").hexdigest(),
        )

    def test_a_payload_whose_hash_does_not_match_is_refused(self) -> None:
        payload = self.payloads / "authored.aya"
        payload.write_bytes(b"AYA authored payload")
        probe = self.probe(
            stage=[
                {
                    "source": str(payload),
                    "dest": "data/Resources/905_res_PC.aya",
                    "expectSha256": "00" * 32,
                }
            ]
        )
        receipt, launcher = self.run_probe(probe, [(1.0, "exit")])
        self.assertEqual(receipt["verdict"], "ERROR")
        self.assertIn("manifest expected", receipt["failure"])
        self.assertEqual(launcher.calls, [])

    def test_autoexec_is_written_crlf_ascii_with_a_trailing_terminator(self) -> None:
        captured: dict[str, bytes] = {}

        def grab(cwd: pathlib.Path) -> None:
            captured["body"] = (cwd / ph.AUTOEXEC).read_bytes()

        receipt, _ = self.run_probe(self.probe(), [(0.5, grab), (1.0, "exit")])
        self.assertEqual(captured["body"], b"Echo UNIT\r\nQuit\r\n")
        self.assertEqual(receipt["staging"]["autoexec"]["bytes"], 17)

    def test_the_working_directory_is_pinned_to_the_scratch_root(self) -> None:
        receipt, launcher = self.run_probe(self.probe(), [(1.0, "exit")])
        executable, argv, cwd = launcher.calls[0]
        self.assertEqual(cwd, receipt["scratchRoot"])
        self.assertEqual(pathlib.Path(executable).parent, pathlib.Path(cwd))
        self.assertEqual(argv, ["-skipfmv", "-forcewindowed", "-level", "100"])

    def test_scratch_root_inside_the_source_root_is_refused(self) -> None:
        with self.assertRaises(ph.ProbeError) as caught:
            ph.stage_scratch(
                self.probe(), self.source, self.source / "inner", self.tmp
            )
        self.assertIn("inside the source root", str(caught.exception))

    def test_make_dirs_are_created_before_launch(self) -> None:
        seen: dict[str, bool] = {}

        def look(cwd: pathlib.Path) -> None:
            seen["memory"] = (cwd / "data" / "Memory").is_dir()
            seen["dumps"] = (cwd / "MemoryDumps").is_dir()

        probe = self.probe(makeDirs=["data/Memory", "MemoryDumps"])
        self.run_probe(probe, [(0.5, look), (1.0, "exit")])
        self.assertEqual(seen, {"memory": True, "dumps": True})


class DiagnosisTests(HarnessCase):
    def test_missing_level_load_line_is_called_a_launch_failure(self) -> None:
        probe = self.probe(oracle={"kind": "processExit", "timeoutSeconds": 30})
        receipt, _ = self.run_probe(probe, [(2.0, ("exit", -1073741819))])
        diagnosis = receipt["diagnosis"]
        self.assertFalse(diagnosis["levelLoadLogged"])
        self.assertIn("BEFORE level load", diagnosis["interpretation"])
        self.assertIn("working directory", diagnosis["interpretation"])

    def test_level_load_line_makes_a_negative_result_about_the_payload(self) -> None:
        probe = self.probe(oracle={"kind": "processExit", "timeoutSeconds": 30})
        receipt, _ = self.run_probe(
            probe,
            [
                (2.0, appends(ph.SETUP_HISTORY, "Game::LoadLevel 100\nD3D nego\n")),
                (4.0, ("exit", 0)),
            ],
        )
        diagnosis = receipt["diagnosis"]
        self.assertTrue(diagnosis["levelLoadLogged"])
        self.assertIn("reached level load", diagnosis["interpretation"])

    def test_a_fault_log_is_named_as_a_fault(self) -> None:
        probe = self.probe(oracle={"kind": "processExit", "timeoutSeconds": 30})
        receipt, _ = self.run_probe(
            probe,
            [
                (2.0, writes(ph.EXCEPTION_LOG, "0xC0000005\n")),
                (3.0, ("exit", -1073741819)),
            ],
        )
        self.assertTrue(receipt["diagnosis"]["fatalFaultLogPresent"])
        self.assertIn("fatal fault", receipt["diagnosis"]["interpretation"])


class TeardownTests(HarnessCase):
    def test_teardown_removes_the_scratch_tree(self) -> None:
        receipt, _ = self.run_probe(self.probe(), [(1.0, "exit")])
        self.assertTrue(receipt["teardown"]["verified"])
        self.assertTrue(receipt["teardown"]["removedScratch"])
        self.assertFalse(pathlib.Path(receipt["scratchRoot"]).exists())

    def test_teardown_removes_the_autoexec_even_when_the_tree_is_kept(self) -> None:
        receipt, _ = self.run_probe(
            self.probe(), [(1.0, "exit")], keep_scratch=True
        )
        scratch = pathlib.Path(receipt["scratchRoot"])
        self.assertTrue(scratch.is_dir(), "keep-scratch must keep the tree")
        self.assertFalse(
            (scratch / ph.AUTOEXEC).exists(),
            "the landmine is removed even when the tree is kept",
        )
        self.assertTrue(receipt["teardown"]["removedAutoexec"])

    def test_teardown_runs_even_when_the_launch_throws(self) -> None:
        clock = FakeClock()
        launcher = FakeLauncher(clock, [])
        launcher.raise_on_launch = OSError("the launcher exploded")
        receipt, _ = self.run_probe(self.probe(), [], launcher=launcher)
        self.assertEqual(receipt["verdict"], "ERROR")
        self.assertIn("exploded", receipt["failure"])
        self.assertFalse(pathlib.Path(receipt["scratchRoot"]).exists())

    def test_teardown_failure_is_reported_not_swallowed(self) -> None:
        scratch = self.tmp / "stuck"
        scratch.mkdir()
        (scratch / ph.AUTOEXEC).write_text("Quit\r\n", encoding="ascii")
        original = ph.shutil.rmtree

        def refuse(*_args: Any, **_kwargs: Any) -> None:
            raise OSError("file in use")

        ph.shutil.rmtree = refuse
        try:
            result = ph.teardown(scratch, keep_scratch=False)
        finally:
            ph.shutil.rmtree = original
        self.assertFalse(result["verified"])
        self.assertTrue(result["errors"])


class ReceiptTests(HarnessCase):
    def test_receipt_files_are_written_and_carry_the_required_facts(self) -> None:
        receipt, _ = self.run_probe(self.probe(), [(3.0, ("exit", 0))])
        run_dir = pathlib.Path(receipt["runDirectory"])
        self.assertTrue((run_dir / "receipt.json").is_file())
        text = (run_dir / "receipt.md").read_text(encoding="utf-8")
        for required in (
            "## Staged",
            "## Command",
            "## Oracle",
            "## Diagnosis",
            "## Teardown",
            "-level",
            "sha256",
            "Wall time",
        ):
            self.assertIn(required, text, f"receipt is missing {required!r}")

    def test_a_failing_probe_says_why_in_the_receipt(self) -> None:
        (self.source / ph.AUTOEXEC).write_text("Quit\r\n", encoding="ascii")
        receipt, _ = self.run_probe(self.probe(), [])
        text = ph.render_receipt(receipt)
        self.assertIn("## Failure", text)
        self.assertIn("ERROR", text)

    def test_wall_time_is_recorded(self) -> None:
        receipt, _ = self.run_probe(self.probe(), [(1.0, "exit")])
        self.assertIsInstance(receipt["wallSeconds"], float)


class DryRunTests(HarnessCase):
    def test_dry_run_stages_nothing_and_launches_nothing(self) -> None:
        receipt, launcher = self.run_probe(
            self.probe(), [(1.0, "exit")], dry_run=True
        )
        self.assertEqual(launcher.calls, [])
        self.assertFalse(pathlib.Path(receipt["scratchRoot"]).exists())
        self.assertEqual(receipt["oracle"]["outcome"], "not-evaluated")
        self.assertIn("-level 100", receipt["command"])
        self.assertTrue(
            (pathlib.Path(receipt["runDirectory"]) / "receipt.md").is_file()
        )

    def test_dry_run_still_enforces_the_interlocks(self) -> None:
        (self.source / ph.AUTOEXEC).write_text("Quit\r\n", encoding="ascii")
        receipt, _ = self.run_probe(self.probe(), [], dry_run=True)
        self.assertEqual(receipt["verdict"], "ERROR")


class ExitCodeTests(HarnessCase):
    """The exit code is the only thing an unattended caller reads."""

    def _manifest(self, probe: dict[str, Any]) -> pathlib.Path:
        path = self.tmp / "cli.json"
        path.write_text(json.dumps({"probes": [probe]}), encoding="utf-8")
        return path

    def _argv(self, manifest: pathlib.Path) -> list[str]:
        return [
            str(manifest),
            "--dry-run",
            "--out",
            str(self.out),
            "--scratch",
            str(self.scratch),
        ]

    def test_a_clean_dry_run_exits_zero(self) -> None:
        manifest = self._manifest(
            {
                "name": "ok",
                "level": 100,
                "sourceRoot": str(self.source),
                "oracle": {"kind": "processExit", "timeoutSeconds": 5},
            }
        )
        self.assertEqual(ph.main(self._argv(manifest)), 0)

    def test_a_dry_run_that_hits_an_interlock_does_not_exit_zero(self) -> None:
        """Found live: an ERROR inside a dry run exited 0.

        A refused interlock is exactly what a dry run exists to surface. An
        unattended caller that reads only the exit code would have taken a
        fail-closed refusal for a clean plan.
        """

        manifest = self._manifest(
            {
                "name": "refused",
                "level": 100,
                "sourceRoot": str(self.tmp / "not-a-game"),
                "oracle": {"kind": "processExit", "timeoutSeconds": 5},
            }
        )
        self.assertNotEqual(ph.main(self._argv(manifest)), 0)

    def test_a_bad_manifest_does_not_exit_zero(self) -> None:
        manifest = self.tmp / "broken.json"
        manifest.write_text("{ not json", encoding="utf-8")
        self.assertNotEqual(ph.main(self._argv(manifest)), 0)


class RecordingTests(HarnessCase):
    def test_recording_is_delegated_to_the_existing_script(self) -> None:
        probe = self.probe(record=True, recordSeconds=30)
        command = ph.build_record_command(probe, self.scratch / "x", "trace-1")
        self.assertEqual(command[0], "powershell.exe")
        self.assertIn("ttd_record.ps1", " ".join(command))
        self.assertIn("-TargetRoot", command)
        self.assertIn("-skipfmv,-forcewindowed,-level,100", command)

    def test_a_console_only_probe_needs_no_recording(self) -> None:
        receipt, _ = self.run_probe(self.probe(), [(1.0, "exit")])
        self.assertNotIn("recording", receipt)
        self.assertEqual(receipt["verdict"], "PASS")


# ---------------------------------------------------------------------------
# Proof that the tests above can fail
# ---------------------------------------------------------------------------


def _no_stale_check(_roots, strict=False):  # noqa: ANN001
    return []


def _teardown_that_forgets_the_autoexec(scratch_root, keep_scratch):  # noqa: ANN001
    if not keep_scratch and scratch_root.exists():
        shutil.rmtree(scratch_root)
    return {
        "removedAutoexec": True,
        "removedScratch": not keep_scratch,
        "keptScratch": keep_scratch,
        "verified": True,
        "errors": [],
    }


def _always_agreeable_oracle(oracle, state):  # noqa: ANN001
    return True, "everything is fine"


def _no_source_verification(_source_root, _before):  # noqa: ANN001
    return None


MUTATIONS: list[tuple[str, Callable[[], Callable[[], None]], list[str]]] = []


def _mutation(name: str, tests: list[str]):
    def decorate(fn: Callable[[], Callable[[], None]]):
        MUTATIONS.append((name, fn, tests))
        return fn

    return decorate


@_mutation(
    "pristine-hash interlock accepts anything",
    ["SourceRootTests.test_refuses_written_pristine_specimen"],
)
def _break_pristine() -> Callable[[], None]:
    original = ph.PRISTINE_SHA256
    ph.PRISTINE_SHA256 = hashlib.sha256(b"NOT PRISTINE").hexdigest()

    def undo() -> None:
        ph.PRISTINE_SHA256 = original

    return undo


@_mutation(
    "stale autoexec.con scan finds nothing",
    [
        "StaleAutoexecTests.test_armed_stale_autoexec_stops_the_run",
        "StaleAutoexecTests.test_strict_mode_makes_an_inert_file_fatal",
        "DryRunTests.test_dry_run_still_enforces_the_interlocks",
    ],
)
def _break_stale_scan() -> Callable[[], None]:
    original = ph.assert_no_stale_autoexec
    ph.assert_no_stale_autoexec = _no_stale_check

    def undo() -> None:
        ph.assert_no_stale_autoexec = original

    return undo


@_mutation(
    "teardown leaves the autoexec.con behind",
    ["TeardownTests.test_teardown_removes_the_autoexec_even_when_the_tree_is_kept"],
)
def _break_teardown() -> Callable[[], None]:
    original = ph.teardown
    ph.teardown = _teardown_that_forgets_the_autoexec

    def undo() -> None:
        ph.teardown = original

    return undo


@_mutation(
    "every oracle always agrees",
    [
        "OracleTests.test_survives_oracle_fails_on_an_early_exit",
        "OracleTests.test_survives_oracle_fails_when_a_fault_log_appears",
        "OracleTests.test_fatal_fault_oracle_fails_when_nothing_faults",
        "OracleTests.test_all_oracle_requires_every_arm",
        "OracleTests.test_file_appears_oracle_rejects_a_too_small_file",
    ],
)
def _break_oracle() -> Callable[[], None]:
    original = ph.check_oracle
    ph.check_oracle = _always_agreeable_oracle

    def undo() -> None:
        ph.check_oracle = original

    return undo


@_mutation(
    "source-tree witness is never re-checked",
    ["SourceRootTests.test_a_run_that_writes_to_the_source_tree_is_an_error"],
)
def _break_witness() -> Callable[[], None]:
    original = ph.verify_source_untouched
    ph.verify_source_untouched = _no_source_verification

    def undo() -> None:
        ph.verify_source_untouched = original

    return undo


@_mutation(
    "manifest parser accepts unknown keys",
    ["ManifestTests.test_unknown_probe_key_is_refused"],
)
def _break_parser() -> Callable[[], None]:
    original = set(ph._PROBE_KEYS)
    ph._PROBE_KEYS.add("orcale")

    def undo() -> None:
        ph._PROBE_KEYS.clear()
        ph._PROBE_KEYS.update(original)

    return undo


@_mutation(
    "the installed-game refusal is checked after the existence check",
    [
        "SourceRootTests.test_installed_game_path_is_refused",
        "SourceRootTests."
        "test_installed_game_path_is_refused_even_when_it_does_not_exist",
    ],
)
def _break_installed_game_refusal() -> Callable[[], None]:
    original = ph._FORBIDDEN_FRAGMENTS
    ph._FORBIDDEN_FRAGMENTS = ()

    def undo() -> None:
        ph._FORBIDDEN_FRAGMENTS = original

    return undo


@_mutation(
    "a dry run excuses an errored probe in the exit code",
    [
        "ExitCodeTests.test_a_dry_run_that_hits_an_interlock_does_not_exit_zero",
    ],
)
def _break_exit_code() -> Callable[[], None]:
    original = ph.exit_code_for

    def lenient(receipts):  # noqa: ANN001
        if all(r.get("dryRun") for r in receipts):
            return 0
        return original(receipts)

    ph.exit_code_for = lenient

    def undo() -> None:
        ph.exit_code_for = original

    return undo


@_mutation(
    "the CWD is not pinned to the scratch root",
    ["StagingTests.test_the_working_directory_is_pinned_to_the_scratch_root"],
)
def _break_cwd() -> Callable[[], None]:
    original = ph.Probe.argv

    def argv(self):  # noqa: ANN001
        return tuple(self.game_arguments)

    ph.Probe.argv = property(argv)

    def undo() -> None:
        ph.Probe.argv = original

    return undo


@_mutation(
    "a fault exit code is classified as an ordinary finish",
    [
        "ExitClassificationTests.test_access_violation_is_a_fault",
        "ExitClassificationTests.test_stack_overflow_and_heap_corruption_are_faults",
        "FaultGateTests.test_bare_process_exit_refuses_an_access_violation",
        "FaultGateTests.test_bare_process_exit_refuses_the_negative_spelling_too",
    ],
)
def _break_fault_classification() -> Callable[[], None]:
    """The pre-2026-08-01 behaviour, restored on purpose.

    ``processExit`` asked 'did it exit' and nothing else, so an access violation
    satisfied it.  If the suite stays green with this applied, nothing in it
    actually tests the thing the campaign depends on.
    """

    original = ph.classify_exit_code

    def never_a_fault(code):  # noqa: ANN001
        found = dict(original(code))
        found["isFault"] = False
        found["status"] = None
        return found

    ph.classify_exit_code = never_a_fault

    def undo() -> None:
        ph.classify_exit_code = original

    return undo


@_mutation(
    "the fault gate never vetoes a satisfied oracle",
    [
        "FaultGateTests.test_the_gate_vetoes_a_file_appears_pass_on_a_crashed_run",
        "FaultGateTests.test_the_exception_log_vetoes_even_on_a_zero_exit",
    ],
)
def _break_fault_gate() -> Callable[[], None]:
    """Fix only ``processExit`` and leave every other oracle able to launder a
    crash into a PASS.  This is the half-fix, and it must not look like the
    whole one."""

    original = ph.apply_fault_gate

    def never_veto(probe, oracle_result, diagnosis, classification):  # noqa: ANN001
        gate = dict(original(probe, oracle_result, diagnosis, classification))
        gate["vetoed"] = False
        return gate

    ph.apply_fault_gate = never_veto

    def undo() -> None:
        ph.apply_fault_gate = original

    return undo


@_mutation(
    "the NTSTATUS error band is unbounded, so -1 reads as a crash",
    [
        "ExitClassificationTests."
        "test_the_harness_own_kill_is_not_called_an_engine_fault",
    ],
)
def _break_fault_band() -> Callable[[], None]:
    """The obvious wrong rule: severity == ERROR and nothing else.

    It catches every real crash, which is why it is tempting, and it also
    reports the harness's own timeout kill as an engine fault. A gate that
    accuses the innocent is a gate somebody turns off.
    """

    original = ph._NTSTATUS_ERROR_BAND
    ph._NTSTATUS_ERROR_BAND = (0xC0000000, 0x100000000)

    def undo() -> None:
        ph._NTSTATUS_ERROR_BAND = original

    return undo


def _run_named(names: list[str]) -> unittest.TestResult:
    module = sys.modules[__name__]
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in names:
        class_name, method = name.split(".")
        suite.addTest(getattr(module, class_name)(method))
    return unittest.TextTestRunner(
        stream=io.StringIO(), verbosity=0
    ).run(suite)


def prove_can_fail() -> int:
    """Break each guarded behaviour and require the guarding test to notice."""

    print("proving the tests can fail")
    print("=" * 62)
    survivors = 0
    for name, apply_mutation, tests in MUTATIONS:
        undo = apply_mutation()
        try:
            result = _run_named(tests)
        finally:
            undo()
        broken = len(result.failures) + len(result.errors)
        status = "detected" if broken else "SURVIVED"
        if not broken:
            survivors += 1
        print(
            f"{status:9}  {name}\n"
            f"           {broken}/{result.testsRun} guarding tests failed"
        )
        if not broken:
            print(f"           tests that should have caught it: {tests}")
    print("=" * 62)
    print(
        f"{len(MUTATIONS)} mutations, {len(MUTATIONS) - survivors} detected, "
        f"{survivors} survived"
    )
    if survivors:
        print(
            "\nA SURVIVING MUTATION MEANS THE TEST THAT SHOULD GUARD IT PROVES "
            "NOTHING."
        )
    return 1 if survivors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prove-can-fail", action="store_true")
    args, remaining = parser.parse_known_args()
    if args.prove_can_fail:
        return prove_can_fail()
    result = unittest.main(
        argv=[sys.argv[0], *remaining], exit=False, verbosity=2
    ).result
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
