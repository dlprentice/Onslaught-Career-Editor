#!/usr/bin/env python3
"""Compile and exercise the generated finalized CDB exit-event log validator."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"
TARGET_PID = 0x73B4


def load_smoke_module():
    spec = importlib.util.spec_from_file_location("winui_safe_copy_live_runtime_smoke", SMOKE)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load live runtime smoke helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CdbExitEventCleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="cdb-exit-event-parser-")
        cls.root = Path(cls.temp.name)
        smoke = load_smoke_module()
        project = smoke.write_runner(cls.root / "generated-runner")
        generated = project.with_name("Program.cs").read_text(encoding="utf-8")
        cls.generated = generated
        opener_start = generated.find("static FileStream OpenRetainedCdbLogStream")
        start = generated.find("static bool TryReadFinalizedCdbExitEvidence")
        predicate_start = generated.find("static bool CdbExitCodeMatchesCleanupEvidence")
        evaluator_start = generated.find("static (bool Graceful, string Status, bool CdbExitCodeAccepted, bool CdbExitCodeMatchedForcedTargetTermination) EvaluateFinalizedCdbCleanupEvidence")
        if opener_start < 0 or start < 0 or predicate_start < 0:
            cls.project = None
            return
        opener_end = generated.find("\nstatic ", opener_start + 1)
        end = generated.find("\nstatic ", start + 1)
        predicate_end = generated.find("\nstatic ", predicate_start + 1)
        if opener_end < 0 or end < 0 or predicate_end < 0:
            raise AssertionError("could not isolate generated CDB retained-log helpers")
        opener = generated[opener_start:opener_end]
        method = generated[start:end]
        predicate = generated[predicate_start:predicate_end]
        evaluator = ""
        finalize_harness = ""
        cls.has_finalizer_evaluator = evaluator_start >= 0
        if cls.has_finalizer_evaluator:
            evaluator_end = generated.find("\nstatic ", evaluator_start + 1)
            if evaluator_end < 0:
                raise AssertionError("could not isolate generated CDB finalizer evaluator")
            evaluator = generated[evaluator_start:evaluator_end]
            finalize_harness = (
                'if (mode.StartsWith("finalize-", StringComparison.Ordinal)) {\n'
                '  bool forceRequested = mode.Contains("-force", StringComparison.Ordinal);\n'
                '  bool exitObserved = mode.Contains("-exit", StringComparison.Ordinal);\n'
                '  bool parsed = TryReadFinalizedCdbExitEvidence(retained, readinessLength, 0x73b4, out bool finalCleanup, out bool finalQuit, out bool finalExitEvent, out uint finalTargetExitCode, out bool finalTerminalRegionClean);\n'
                '  var decision = EvaluateFinalizedCdbCleanupEvidence(true, false, true, true, true, true, parsed, finalExitEvent, finalCleanup, finalQuit, int.Parse(args[2], CultureInfo.InvariantCulture), finalTargetExitCode, forceRequested, exitObserved, finalTerminalRegionClean);\n'
                '  Console.WriteLine($"{decision.Graceful}|{decision.Status}|{decision.CdbExitCodeAccepted}|{decision.CdbExitCodeMatchedForcedTargetTermination}|{finalTerminalRegionClean}");\n'
                '  return decision.Graceful ? 0 : 1;\n'
                '}\n'
            )
        harness = cls.root / "parser-harness"
        harness.mkdir()
        (harness / "parser-harness.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            '  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework>'
            '<ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup>\n'
            '</Project>\n',
            encoding="utf-8",
        )
        (harness / "Program.cs").write_text(
            "using System.Globalization;\nusing System.Text;\nusing System.Text.RegularExpressions;\n\n"
            + opener
            + "\n\n"
            + method
            + "\n\n"
            + predicate
            + "\n\n"
            + evaluator
            + "\n\nif (args.Length != 4) return 2;\n"
            + "string mode = args[0]; string logPath = args[1];\n"
            + "using FileStream retained = OpenRetainedCdbLogStream(logPath);\n"
            + "long readinessLength = long.Parse(args[3], CultureInfo.InvariantCulture);\n"
            + "if (readinessLength < 0) readinessLength = 0;\n"
            + finalize_harness
            + "if (mode.StartsWith(\"exit-code-\", StringComparison.Ordinal)) {\n"
            + "  bool forceRequested = mode.Contains(\"-force\", StringComparison.Ordinal);\n"
            + "  bool exitObserved = mode.Contains(\"-exit\", StringComparison.Ordinal);\n"
            + "  bool matched = CdbExitCodeMatchesCleanupEvidence(int.Parse(args[2], CultureInfo.InvariantCulture), checked((uint)readinessLength), forceRequested, exitObserved, true);\n"
            + "  Console.WriteLine(matched); return matched ? 0 : 1;\n"
            + "}\n"
            + "bool deleteBlocked = true; bool replacementBlocked = true;\n"
            + "if (mode == \"lock\") {\n"
            + "  string replacement = logPath + \".replacement\"; File.WriteAllText(replacement, \"replacement\");\n"
            + "  try { File.Delete(logPath); deleteBlocked = false; } catch (IOException) { } catch (UnauthorizedAccessException) { }\n"
            + "  try { File.Move(replacement, logPath, true); replacementBlocked = false; } catch (IOException) { } catch (UnauthorizedAccessException) { }\n"
            + "}\n"
            + "bool accepted = TryReadFinalizedCdbExitEvidence(retained, readinessLength, int.Parse(args[2], CultureInfo.InvariantCulture), "
            + "out bool cleanup, out bool quit, out bool exitEvent, out uint targetExitCode, out bool terminalRegionDiagnosticClean);\n"
            + 'Console.WriteLine($"{accepted}|{cleanup}|{quit}|{exitEvent}|{targetExitCode}|{terminalRegionDiagnosticClean}|{deleteBlocked}|{replacementBlocked}");\n'
            + "return accepted && deleteBlocked && replacementBlocked ? 0 : 1;\n",
            encoding="utf-8",
        )
        cls.project = harness / "parser-harness.csproj"
        build = subprocess.run(
            ["dotnet", "build", str(cls.project), "--nologo", "--verbosity", "quiet"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if build.returncode != 0:
            raise AssertionError(build.stdout + build.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def validate(
        self,
        text: str,
        *,
        pid: int = TARGET_PID,
        mode: str = "parse",
        readiness_length: int = -1,
    ) -> tuple[int, str]:
        self.assertIsNotNone(
            self.project,
            "generated runner is missing TryReadFinalizedCdbExitEvidence",
        )
        log = self.root / f"fixture-{self.id().rsplit('.', 1)[-1]}.log"
        log.write_text(text, encoding="utf-8")
        return self.validate_path(
            log,
            pid=pid,
            mode=mode,
            readiness_length=readiness_length,
        )

    def validate_path(
        self,
        log: Path,
        *,
        pid: int = TARGET_PID,
        mode: str = "parse",
        readiness_length: int = -1,
    ) -> tuple[int, str]:
        result = subprocess.run(
            [
                "dotnet",
                "run",
                "--project",
                str(self.project),
                "--no-build",
                "--",
                mode,
                str(log),
                str(pid),
                str(readiness_length),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        return result.returncode, result.stdout.strip()

    def finalize(
        self,
        text: str,
        *,
        cdb_exit_code: int,
        mode: str,
        readiness_length: int = 0,
    ) -> tuple[int, str]:
        self.assertTrue(
            self.has_finalizer_evaluator,
            "generated runner is missing executable finalized-cleanup evaluator",
        )
        return self.validate(
            text,
            mode=mode,
            pid=cdb_exit_code,
            readiness_length=readiness_length,
        )

    @staticmethod
    def valid_log() -> str:
        return (
            "MORPH_CANARY_LASTEVENT_BEGIN\n"
            "Last event: 73b4.9448: Exit process 0:73b4, code ffffffff\n"
            "  debugger time: Mon Jul 13 10:45:10.061 2026 (UTC - 4:00)\n"
            "MORPH_CANARY_LASTEVENT_END\n"
            "MORPH_CANARY_CLEANUP_Q\n"
            "quit:\n"
        )

    def test_accepts_actual_disposable_exit_process_shape(self) -> None:
        self.assertEqual(
            (0, "True|True|True|True|4294967295|True|True|True"),
            self.validate(self.valid_log()),
        )

    def test_accepts_known_cdb_boilerplate_around_proof(self) -> None:
        startup = "Microsoft (R) Windows Debugger Version 10.0 X86\n"
        transcript = (
            startup
            + "0:004> .echo MORPH_CANARY_LASTEVENT_BEGIN; .lastevent; "
            ".echo MORPH_CANARY_LASTEVENT_END; .echo MORPH_CANARY_CLEANUP_Q; q\n"
            + self.valid_log()
            + "NatVis script unloaded from 'windows.natvis'\n"
        )
        self.assertEqual(
            0,
            self.validate(
                transcript,
                readiness_length=len(startup.encode("utf-8")),
            )[0],
        )

    def test_retained_stream_blocks_path_delete_and_replacement(self) -> None:
        code, output = self.validate(self.valid_log(), mode="lock")
        self.assertEqual(0, code)
        self.assertEqual("True|True|True|True|4294967295|True|True|True", output)

    def test_rejects_exit_status_wider_than_target_process_status(self) -> None:
        malformed = self.valid_log().replace("code ffffffff", "code 00000000ffffffff")
        self.assertEqual(1, self.validate(malformed)[0])

    def test_accepts_exact_forced_target_status_propagation(self) -> None:
        self.assertEqual(
            (0, "True"),
            self.validate(
                self.valid_log(),
                mode="exit-code-force-exit",
                pid=-1,
                readiness_length=0xFFFFFFFF,
            ),
        )

    def test_accepts_zero_cdb_exit_without_forced_target(self) -> None:
        self.assertEqual(
            (0, "True"),
            self.validate(
                self.valid_log(),
                mode="exit-code-normal",
                pid=0,
                readiness_length=0,
            ),
        )

    def test_complete_finalizer_accepts_exact_retry11_terminal_region(self) -> None:
        self.assertEqual(
            (0, "True|exited-after-managed-stop|True|True|True"),
            self.finalize(
                self.valid_log(),
                cdb_exit_code=-1,
                mode="finalize-force-exit",
            ),
        )

    def test_complete_finalizer_rejects_retry11_shape_with_unrelated_cdb_error(self) -> None:
        transcript = self.valid_log().replace(
            "MORPH_CANARY_CLEANUP_Q",
            "Unable to continue, system error 5\nMORPH_CANARY_CLEANUP_Q",
        )
        self.assertEqual(
            (1, "False|cdb-exit-code-unbound|False|False|False"),
            self.finalize(
                transcript,
                cdb_exit_code=-1,
                mode="finalize-force-exit",
            ),
        )

    def test_complete_finalizer_rejects_malformed_terminal_region(self) -> None:
        transcript = self.valid_log().replace(
            "MORPH_CANARY_LASTEVENT_END",
            "ambiguous terminal output\nMORPH_CANARY_LASTEVENT_END",
        )
        code, output = self.finalize(
            transcript,
            cdb_exit_code=-1,
            mode="finalize-force-exit",
        )
        self.assertEqual(1, code)
        self.assertTrue(output.startswith("False|"), output)

    def test_complete_finalizer_preserves_zero_exit_with_unrelated_terminal_diagnostic(self) -> None:
        transcript = self.valid_log().replace(
            "MORPH_CANARY_CLEANUP_Q",
            "Unable to continue, system error 5\nMORPH_CANARY_CLEANUP_Q",
        )
        self.assertEqual(
            (0, "True|exited-after-managed-stop|True|False|False"),
            self.finalize(
                transcript,
                cdb_exit_code=0,
                mode="finalize-exit",
            ),
        )

    def test_complete_finalizer_rejects_unexpected_post_quit_diagnostic(self) -> None:
        transcript = self.valid_log() + "Unable to unload debugger extension\n"
        self.assertEqual(
            (1, "False|cdb-exit-code-unbound|False|False|False"),
            self.finalize(
                transcript,
                cdb_exit_code=-1,
                mode="finalize-force-exit",
            ),
        )

    def test_complete_finalizer_rejects_post_readiness_pre_begin_error(self) -> None:
        transcript = "Unable to continue, system error 5\n" + self.valid_log()
        self.assertEqual(
            (1, "False|cdb-exit-code-unbound|False|False|False"),
            self.finalize(
                transcript,
                cdb_exit_code=-1,
                mode="finalize-force-exit",
            ),
        )

    def test_complete_finalizer_rejects_unrecognized_pre_begin_output(self) -> None:
        transcript = "debugger transport reset\n" + self.valid_log()
        self.assertEqual(
            (1, "False|cdb-exit-code-unbound|False|False|False"),
            self.finalize(
                transcript,
                cdb_exit_code=-1,
                mode="finalize-force-exit",
            ),
        )

    def test_complete_finalizer_ignores_diagnostic_before_readiness_boundary(self) -> None:
        prefix = "Unable to continue, system error 5\n"
        self.assertEqual(
            (0, "True|exited-after-managed-stop|True|True|True"),
            self.finalize(
                prefix + self.valid_log(),
                cdb_exit_code=-1,
                mode="finalize-force-exit",
                readiness_length=len(prefix.encode("utf-8")),
            ),
        )

    def test_complete_finalizer_allows_known_post_quit_shutdown_boilerplate(self) -> None:
        transcript = self.valid_log() + "NatVis script unloaded from 'windows.natvis'\n"
        self.assertEqual(
            (0, "True|exited-after-managed-stop|True|True|True"),
            self.finalize(
                transcript,
                cdb_exit_code=-1,
                mode="finalize-force-exit",
            ),
        )

    def test_complete_finalizer_preserves_zero_exit_with_post_quit_diagnostic(self) -> None:
        transcript = self.valid_log() + "Unable to unload debugger extension\n"
        self.assertEqual(
            (0, "True|exited-after-managed-stop|True|False|False"),
            self.finalize(
                transcript,
                cdb_exit_code=0,
                mode="finalize-exit",
            ),
        )

    def test_rejects_minus_one_without_force_requested(self) -> None:
        self.assertEqual(
            1,
            self.validate(
                self.valid_log(),
                mode="exit-code-exit",
                pid=-1,
                readiness_length=0xFFFFFFFF,
            )[0],
        )

    def test_rejects_minus_one_without_exit_observed(self) -> None:
        self.assertEqual(
            1,
            self.validate(
                self.valid_log(),
                mode="exit-code-force",
                pid=-1,
                readiness_length=0xFFFFFFFF,
            )[0],
        )

    def test_rejects_minus_one_without_matching_target_status(self) -> None:
        self.assertEqual(
            1,
            self.validate(
                self.valid_log(),
                mode="exit-code-force-exit",
                pid=-1,
                readiness_length=0xFFFFFFFE,
            )[0],
        )

    def test_rejects_arbitrary_nonzero_cdb_exit(self) -> None:
        self.assertEqual(
            1,
            self.validate(
                self.valid_log(),
                mode="exit-code-force-exit",
                pid=1,
                readiness_length=1,
            )[0],
        )

    def test_rejects_unrelated_pid(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log(), pid=0x73B5)[0])

    def test_rejects_mismatched_event_pid_fields(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log().replace("73b4.9448", "73b5.9448"))[0])

    def test_rejects_mismatched_exit_process_pid(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log().replace("0:73b4", "0:73b5"))[0])

    def test_rejects_zero_thread_id(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log().replace("73b4.9448", "73b4.0000"))[0])

    def test_rejects_exception_event(self) -> None:
        malformed = self.valid_log().replace(
            "Last event: 73b4.9448: Exit process 0:73b4, code ffffffff",
            "Last event: 73b4.9448: Access violation - code c0000005 (first chance)",
        )
        self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_breakpoint_event(self) -> None:
        malformed = self.valid_log().replace(
            "Last event: 73b4.9448: Exit process 0:73b4, code ffffffff",
            "Last event: 73b4.9448: Break instruction exception - code 80000003",
        )
        self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_missing_section(self) -> None:
        self.assertEqual(1, self.validate("MORPH_CANARY_CLEANUP_Q\nquit:\n")[0])

    def test_rejects_duplicate_section(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log() + self.valid_log())[0])

    def test_rejects_second_global_last_event_outside_section(self) -> None:
        extra = "Last event: 73b4.9448: Exit process 0:73b4, code ffffffff\n"
        self.assertEqual(1, self.validate(extra + self.valid_log())[0])

    def test_rejects_duplicate_begin_marker(self) -> None:
        self.assertEqual(
            1,
            self.validate("MORPH_CANARY_LASTEVENT_BEGIN\n" + self.valid_log())[0],
        )

    def test_rejects_duplicate_end_marker(self) -> None:
        self.assertEqual(
            1,
            self.validate(
                self.valid_log().replace(
                    "MORPH_CANARY_CLEANUP_Q",
                    "MORPH_CANARY_LASTEVENT_END\nMORPH_CANARY_CLEANUP_Q",
                )
            )[0],
        )

    def test_rejects_reversed_section(self) -> None:
        malformed = self.valid_log().replace(
            "MORPH_CANARY_LASTEVENT_BEGIN", "TEMP", 1
        ).replace("MORPH_CANARY_LASTEVENT_END", "MORPH_CANARY_LASTEVENT_BEGIN", 1).replace(
            "TEMP", "MORPH_CANARY_LASTEVENT_END", 1
        )
        self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_malformed_section_payload(self) -> None:
        malformed = self.valid_log().replace("  debugger time:", "unexpected detail:")
        self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_debugger_time_with_trailing_diagnostic(self) -> None:
        malformed = self.valid_log().replace(
            "2026 (UTC - 4:00)",
            "2026 (UTC - 4:00) Unable to continue, system error 5",
        )
        self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_impossible_debugger_calendar_date(self) -> None:
        malformed = self.valid_log().replace("Mon Jul 13", "Mon Feb 31")
        self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_mismatched_debugger_weekday(self) -> None:
        malformed = self.valid_log().replace("Mon Jul 13", "Tue Jul 13")
        self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_zero_and_unsupported_debugger_years(self) -> None:
        for invalid_year in ("0000", "1600"):
            with self.subTest(year=invalid_year):
                malformed = self.valid_log().replace("2026 (UTC", f"{invalid_year} (UTC")
                self.assertEqual(1, self.validate(malformed)[0])

    def test_rejects_invalid_debugger_clock_components(self) -> None:
        replacements = {
            "hour": ("10:45:10.061", "24:45:10.061"),
            "minute": ("10:45:10.061", "10:60:10.061"),
            "second": ("10:45:10.061", "10:45:60.061"),
            "millisecond": ("10:45:10.061", "10:45:10.1000"),
        }
        for name, (old, new) in replacements.items():
            with self.subTest(component=name):
                self.assertEqual(1, self.validate(self.valid_log().replace(old, new))[0])

    def test_rejects_invalid_debugger_utc_offsets(self) -> None:
        for invalid_offset in ("+ 14:59", "- 14:01", "+ 15:00"):
            with self.subTest(offset=invalid_offset):
                malformed = self.valid_log().replace("- 4:00", invalid_offset)
                self.assertEqual(1, self.validate(malformed)[0])

    def test_accepts_maximum_valid_debugger_utc_offset(self) -> None:
        transcript = self.valid_log().replace("- 4:00", "+ 14:00")
        self.assertEqual(0, self.validate(transcript)[0])

    def test_complete_finalizer_rejects_semantically_invalid_debugger_times(self) -> None:
        replacements = {
            "date": ("Mon Jul 13", "Mon Feb 31"),
            "weekday": ("Mon Jul 13", "Tue Jul 13"),
            "year-zero": ("2026 (UTC", "0000 (UTC"),
            "year-unsupported": ("2026 (UTC", "1600 (UTC"),
            "hour": ("10:45:10.061", "24:45:10.061"),
            "minute": ("10:45:10.061", "10:60:10.061"),
            "second": ("10:45:10.061", "10:45:60.061"),
            "millisecond": ("10:45:10.061", "10:45:10.1000"),
            "offset": ("- 4:00", "+ 14:59"),
        }
        for name, (old, new) in replacements.items():
            with self.subTest(case=name):
                code, output = self.finalize(
                    self.valid_log().replace(old, new),
                    cdb_exit_code=-1,
                    mode="finalize-force-exit",
                )
                self.assertEqual(1, code)
                self.assertTrue(output.startswith("False|"), output)

    def test_rejects_proof_like_marker_line_outside_section(self) -> None:
        self.assertEqual(
            1,
            self.validate("MORPH_CANARY_LASTEVENT_BEGIN malformed\n" + self.valid_log())[0],
        )

    def test_rejects_trailing_proof_activity(self) -> None:
        self.assertEqual(
            1,
            self.validate(self.valid_log() + "MORPH_CANARY_CLEANUP_Q trailing\n")[0],
        )

    def test_rejects_cleanup_before_exit_event(self) -> None:
        lines = self.valid_log().splitlines()
        cleanup = lines.pop(4)
        lines.insert(0, cleanup)
        self.assertEqual(1, self.validate("\n".join(lines) + "\n")[0])

    def test_rejects_duplicate_cleanup_marker(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log() + "MORPH_CANARY_CLEANUP_Q\n")[0])

    def test_rejects_duplicate_quit_marker(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log() + "quit:\n")[0])

    def test_rejects_missing_quit_marker(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log().replace("quit:\n", ""))[0])

    def test_rejects_missing_cleanup_marker(self) -> None:
        self.assertEqual(
            1,
            self.validate(self.valid_log().replace("MORPH_CANARY_CLEANUP_Q\n", ""))[0],
        )

    def test_rejects_log_truncated_after_readiness(self) -> None:
        text = self.valid_log()
        self.assertEqual(
            1,
            self.validate(text, readiness_length=1_000_000)[0],
        )

    def test_rejects_oversized_log(self) -> None:
        log = self.root / "oversized.log"
        with log.open("wb") as stream:
            stream.seek(16 * 1024 * 1024)
            stream.write(b"x")
        self.assertEqual(1, self.validate_path(log)[0])

    def test_cdb_and_target_exit_times_are_diagnostics_with_no_order_predicate(self) -> None:
        start = self.generated.index("static JsonElement FinalizeExactCdbObserverAfterManagedStop")
        end = self.generated.index("\nstatic ", start + 1)
        body = self.generated[start:end]
        self.assertIn("managedExitTimeUtc = stopResult?.ExitTime", body)
        self.assertIn("cdbExitTimeUtc = observedCdbExitTimeUtc", body)
        self.assertNotRegex(body, r"(?:managed|cdb)ExitTimeUtc\s*[<>]=?")


if __name__ == "__main__":
    unittest.main(verbosity=2)
