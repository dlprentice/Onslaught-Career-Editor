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
        if opener_start < 0 or start < 0:
            cls.project = None
            return
        opener_end = generated.find("\nstatic ", opener_start + 1)
        end = generated.find("\nstatic ", start + 1)
        if opener_end < 0 or end < 0:
            raise AssertionError("could not isolate generated CDB retained-log helpers")
        opener = generated[opener_start:opener_end]
        method = generated[start:end]
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
            + "\n\nif (args.Length != 4) return 2;\n"
            + "string mode = args[0]; string logPath = args[1];\n"
            + "using FileStream retained = OpenRetainedCdbLogStream(logPath);\n"
            + "long readinessLength = long.Parse(args[3], CultureInfo.InvariantCulture);\n"
            + "if (readinessLength < 0) readinessLength = retained.Length;\n"
            + "bool deleteBlocked = true; bool replacementBlocked = true;\n"
            + "if (mode == \"lock\") {\n"
            + "  string replacement = logPath + \".replacement\"; File.WriteAllText(replacement, \"replacement\");\n"
            + "  try { File.Delete(logPath); deleteBlocked = false; } catch (IOException) { } catch (UnauthorizedAccessException) { }\n"
            + "  try { File.Move(replacement, logPath, true); replacementBlocked = false; } catch (IOException) { } catch (UnauthorizedAccessException) { }\n"
            + "}\n"
            + "bool accepted = TryReadFinalizedCdbExitEvidence(retained, readinessLength, int.Parse(args[2], CultureInfo.InvariantCulture), "
            + "out bool cleanup, out bool quit, out bool exitEvent);\n"
            + 'Console.WriteLine($"{accepted}|{cleanup}|{quit}|{exitEvent}|{deleteBlocked}|{replacementBlocked}");\n'
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
            (0, "True|True|True|True|True|True"),
            self.validate(self.valid_log()),
        )

    def test_accepts_known_cdb_boilerplate_around_proof(self) -> None:
        transcript = (
            "Microsoft (R) Windows Debugger Version 10.0 X86\n"
            "0:004> .echo MORPH_CANARY_LASTEVENT_BEGIN; .lastevent; "
            ".echo MORPH_CANARY_LASTEVENT_END; .echo MORPH_CANARY_CLEANUP_Q; q\n"
            + self.valid_log()
            + "NatVis script unloaded from 'windows.natvis'\n"
        )
        self.assertEqual(0, self.validate(transcript)[0])

    def test_retained_stream_blocks_path_delete_and_replacement(self) -> None:
        code, output = self.validate(self.valid_log(), mode="lock")
        self.assertEqual(0, code)
        self.assertEqual("True|True|True|True|True|True", output)

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
