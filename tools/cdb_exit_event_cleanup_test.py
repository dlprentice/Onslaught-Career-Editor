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
        start = generated.find("static bool TryReadFinalizedCdbExitEvidence")
        if start < 0:
            cls.project = None
            return
        end = generated.find("\nstatic ", start + 1)
        if end < 0:
            raise AssertionError("could not isolate generated CDB exit-event validator")
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
            + method
            + "\n\nif (args.Length != 2) return 2;\n"
            + "bool accepted = TryReadFinalizedCdbExitEvidence(args[0], int.Parse(args[1], CultureInfo.InvariantCulture), "
            + "out bool cleanup, out bool quit, out bool exitEvent);\n"
            + 'Console.WriteLine($"{accepted}|{cleanup}|{quit}|{exitEvent}");\n'
            + "return accepted ? 0 : 1;\n",
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

    def validate(self, text: str, *, pid: int = TARGET_PID) -> tuple[int, str]:
        self.assertIsNotNone(
            self.project,
            "generated runner is missing TryReadFinalizedCdbExitEvidence",
        )
        log = self.root / f"fixture-{self.id().rsplit('.', 1)[-1]}.log"
        log.write_text(text, encoding="utf-8")
        result = subprocess.run(
            ["dotnet", "run", "--project", str(self.project), "--no-build", "--", str(log), str(pid)],
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
        self.assertEqual((0, "True|True|True|True"), self.validate(self.valid_log()))

    def test_rejects_unrelated_pid(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log(), pid=0x73B5)[0])

    def test_rejects_mismatched_event_pid_fields(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log().replace("73b4.9448", "73b5.9448"))[0])

    def test_rejects_mismatched_exit_process_pid(self) -> None:
        self.assertEqual(1, self.validate(self.valid_log().replace("0:73b4", "0:73b5"))[0])

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

    def test_cdb_and_target_exit_times_are_diagnostics_with_no_order_predicate(self) -> None:
        start = self.generated.index("static JsonElement FinalizeExactCdbObserverAfterManagedStop")
        end = self.generated.index("\nstatic ", start + 1)
        body = self.generated[start:end]
        self.assertIn("managedExitTimeUtc = stopResult?.ExitTime", body)
        self.assertIn("cdbExitTimeUtc = observedCdbExitTimeUtc", body)
        self.assertNotRegex(body, r"(?:managed|cdb)ExitTimeUtc\s*[<>]=?")


if __name__ == "__main__":
    unittest.main(verbosity=2)
