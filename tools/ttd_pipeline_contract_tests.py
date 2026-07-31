#!/usr/bin/env python3
"""Focused fail-closed checks for the local Time Travel Debugging helpers."""

from __future__ import annotations

import pathlib
import json
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDER = ROOT / "tools" / "ttd_record.ps1"
WRAPPER = ROOT / "tools" / "Record-GameMoment.ps1"
QUERY = ROOT / "tools" / "ttd_query.ps1"
COVERAGE_WRAPPER = ROOT / "tools" / "Invoke-TtdExecCoverage.ps1"
COLLECTOR_SOURCE = (
    ROOT / "tools" / "ttd-exec-coverage" / "ttd_exec_coverage.cpp"
)

# Recorded coverage summaries, kept verbatim as falsification evidence.
#
# The two IMPOSSIBLE receipts were published by the pre-fix collector, which
# wrote ICursorView::ReplayResult::StepsExecuted straight through as ground
# truth.  Both report far more accepted execute-watchpoint callbacks than
# executed steps, which cannot happen: a watchpoint execute hit requires an
# executed instruction, and an instruction is a step.
#   local-lab/options-open-manual-01-exec-v1/coverage.jsonl
#   local-lab/frontend-manual-02-exec-v1/coverage.jsonl
# The SOUND receipts are the startup-to-main-menu trace before the fix and the
# post-fix rerun of that same trace, whose chunked 64-bit accumulation lands on
# the identical step total over two chunks.
IMPOSSIBLE_SUMMARY_OPTIONS_OPEN = {
    "callback_hits": "1137340343",
    "instructions_executed": "131110",
    "steps_executed": "131111",
}
IMPOSSIBLE_SUMMARY_FRONTEND_02 = {
    "callback_hits": "245245503",
    "instructions_executed": "137022",
    "steps_executed": "137023",
}
SOUND_SUMMARY_STARTUP = {
    "callback_hits": "715094340",
    "instructions_executed": "1860375340",
    "steps_executed": "1860375400",
}
SOUND_SUMMARY_STARTUP_AFTER_FIX = {
    "callback_hits": "715096876",
    "instructions_executed": "1860375340",
    "steps_executed": "1860375400",
}
# What --quarantine-counters publishes for options-open-manual-01: the three
# counters are ABSENT from the top level and survive only as poisoned evidence.
QUARANTINED_SUMMARY_OPTIONS_OPEN = {
    "counters_quarantined": True,
    "quarantined_counters": {
        "callback_hits": "1137340343",
        "instructions_executed": "131110",
        "steps_executed": "131111",
        "gap_events": "158054070",
        "reason": "ttd-replay-accounting-stopped-advancing",
    },
}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class TtdPipelineContractTests(unittest.TestCase):
    def test_powershell_sources_parse(self) -> None:
        for path in (RECORDER, WRAPPER, QUERY):
            with self.subTest(path=path.name):
                literal = str(path).replace("'", "''")
                command = (
                    f"$path = '{literal}'; $errors = @(); "
                    "[System.Management.Automation.Language.Parser]::ParseFile("
                    "$path, [ref]$null, [ref]$errors) | Out-Null; "
                    "if ($errors.Count) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }"
                )
                completed = subprocess.run(
                    [
                        "pwsh",
                        "-NoLogo",
                        "-NoProfile",
                        "-Command",
                        command,
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

    def test_sources_contain_attach_and_owner_boundaries(self) -> None:
        recorder = read(RECORDER)
        wrapper = read(WRAPPER)

        self.assertIn("if (-not $Attach -and $running.Count -gt 0)", recorder)
        self.assertIn("$ours = @($running | Where-Object { $_.Path -ieq $exe })", recorder)
        self.assertIn("if ($ours.Count -eq 0)", recorder)
        self.assertIn("if ($ours.Count -gt 1)", recorder)
        self.assertIn("if (-not $Attach) {", recorder)
        self.assertIn("| Stop-Process -Force", recorder)
        self.assertIn("THE GAME IS STILL RUNNING", recorder)

        self.assertIn("Where-Object { $_.Path -ieq $exe }", wrapper)
        self.assertIn("'-Name', $Name, '-Attach'", wrapper)
        self.assertIn("$recorderProcess.ExitCode", wrapper)
        self.assertIn("$recorderStart.CreateNoWindow = $false", wrapper)
        self.assertIn("$startInfo.Verb = 'runas'", wrapper)
        self.assertIn("$elevatedProcess.WaitForExit()", wrapper)
        self.assertIn("exit $elevatedProcess.ExitCode", wrapper)
        self.assertLess(
            wrapper.index("$Name -notmatch"),
            wrapper.index("Get-Process -Name 'BEA'"),
        )

    def test_recorder_rejects_stale_or_ambiguous_inputs(self) -> None:
        recorder = read(RECORDER)

        self.assertIn("^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$", recorder)
        self.assertIn("Module-restricted recording is disabled", recorder)
        self.assertIn("Trace output already exists", recorder)
        self.assertIn("Refusing to trace the Steam install", recorder)
        self.assertIn("Refusing to trace a target under", recorder)
        self.assertIn("Unsupported BEA.exe specimen", recorder)
        self.assertIn(
            "E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4",
            recorder,
        )
        self.assertIn("A d3d9 proxy capture appears to be in flight", recorder)
        self.assertIn("Traces must be written to G:", recorder)
        self.assertIn("try {", recorder)
        self.assertIn("catch {", recorder)
        self.assertIn("finally {", recorder)
        self.assertIn("traceGrew", recorder)
        self.assertIn("stoppedForLowSpace", recorder)
        self.assertIn("TTD recorder PID", recorder)
        self.assertIn("cleanup did not complete cleanly", recorder)
        self.assertIn("$recorderEndedWhileTargetAlive", recorder)
        self.assertIn("'max-file-aborted'", recorder)
        self.assertIn("'recorder-ended-early'", recorder)
        self.assertNotIn("$guestExit = [int]$Matches[1]", recorder)
        self.assertIn("$rawGuestExit = [int64]::Parse(", recorder)
        self.assertIn("$rawGuestExit - [int64]4294967296", recorder)
        self.assertIn(
            "$null -ne $StartInfo.PSObject.Properties['ArgumentList']",
            recorder,
        )
        self.assertIn("ConvertTo-WindowsCommandLineArgument", recorder)
        self.assertIn("Set-NativeProcessArguments", recorder)
        self.assertIn("$StartInfo.Arguments =", recorder)
        self.assertIn("schemaVersion        = 'ttd-record-receipt.v3'", recorder)
        self.assertIn("traceSha256", recorder)
        self.assertIn("[IO.FileShare]::Read", recorder)
        self.assertIn("if ($UntilExit) { [datetime]::MaxValue }", recorder)
        self.assertIn("$recorderStarted -and -not $recorder.HasExited", recorder)
        self.assertTrue(recorder.rstrip().endswith("exit 0"))

    def test_native_argument_bridge_round_trips_on_both_powershell_runtimes(
        self,
    ) -> None:
        expected = [
            "",
            "plain",
            "contains space",
            "contains\ttab",
            'embedded"quote',
            r"backslash\before\"quote",
            "trailing\\",
            r"C:\path with spaces\trailing\\",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            echo = root / "echo_args.py"
            echo.write_text(
                "import json, sys\nprint(json.dumps(sys.argv[1:]))\n",
                encoding="utf-8",
            )
            expected_path = root / "expected.json"
            expected_path.write_text(json.dumps(expected), encoding="utf-8")
            harness = root / "round_trip.ps1"
            harness.write_text(
                "param($Recorder, $Python, $Echo, $Expected)\n"
                "$ErrorActionPreference = 'Stop'\n"
                "Set-StrictMode -Version Latest\n"
                "$tokens = $null; $errors = $null\n"
                "$ast = [System.Management.Automation.Language.Parser]::"
                "ParseFile($Recorder, [ref]$tokens, [ref]$errors)\n"
                "if ($errors.Count) { throw ($errors -join \"`n\") }\n"
                "foreach ($name in @("
                "'ConvertTo-WindowsCommandLineArgument',"
                "'Set-NativeProcessArguments')) {\n"
                "  $function = $ast.Find({"
                "param($node) "
                "$node -is "
                "[System.Management.Automation.Language.FunctionDefinitionAst] "
                "-and $node.Name -eq $name"
                "}, $true)\n"
                "  if ($null -eq $function) { throw \"Missing $name\" }\n"
                "  Invoke-Expression $function.Extent.Text\n"
                "}\n"
                "$decoded = Get-Content -LiteralPath $Expected -Raw | "
                "ConvertFrom-Json\n"
                "$arguments = @($Echo)\n"
                "foreach ($item in $decoded) { $arguments += [string]$item }\n"
                "$startInfo = [Diagnostics.ProcessStartInfo]::new()\n"
                "$startInfo.FileName = $Python\n"
                "$startInfo.UseShellExecute = $false\n"
                "$startInfo.RedirectStandardOutput = $true\n"
                "$startInfo.RedirectStandardError = $true\n"
                "Set-NativeProcessArguments "
                "-StartInfo $startInfo -Arguments $arguments\n"
                "$process = [Diagnostics.Process]::new()\n"
                "$process.StartInfo = $startInfo\n"
                "if (-not $process.Start()) { throw 'Process did not start' }\n"
                "$stdout = $process.StandardOutput.ReadToEnd()\n"
                "$stderr = $process.StandardError.ReadToEnd()\n"
                "$process.WaitForExit()\n"
                "if ($process.ExitCode -ne 0) { throw $stderr }\n"
                "$stdout.Trim()\n",
                encoding="utf-8",
            )

            for runtime in ("powershell.exe", "pwsh"):
                with self.subTest(runtime=runtime):
                    completed = subprocess.run(
                        [
                            runtime,
                            "-NoLogo",
                            "-NoProfile",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-File",
                            str(harness),
                            "-Recorder",
                            str(RECORDER),
                            "-Python",
                            subprocess.check_output(
                                ["py", "-3", "-c", "import sys;print(sys.executable)"],
                                text=True,
                            ).strip(),
                            "-Echo",
                            str(echo),
                            "-Expected",
                            str(expected_path),
                        ],
                        cwd=ROOT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(
                        0,
                        completed.returncode,
                        completed.stdout + completed.stderr,
                    )
                    self.assertEqual(expected, json.loads(completed.stdout))

    def test_query_fails_closed_and_never_reuses_output(self) -> None:
        query = read(QUERY)

        self.assertIn("Query output already exists", query)
        self.assertIn('if ($proc.ExitCode -ne 0)', query)
        self.assertIn("KNOWN-ANSWER sentinel never appeared", query)
        self.assertIn("NEGATIVE-CONTROL sentinel never appeared", query)
        self.assertIn("OUTPUT-END sentinel never appeared", query)
        self.assertIn("Name = 'stderr'; Path = $stderrPath", query)
        self.assertIn("$channels.GetEnumerator()", query)
        self.assertIn("PE-header compatibility check did not run", query)
        self.assertIn("Syntax error in", query)
        self.assertIn("Error: Unable to bind name", query)
        self.assertIn("Couldn't resolve error", query)
        self.assertIn("pass count must be preceeded by whitespace error in", query)
        self.assertIn("if (-not $result.ok) { exit 1 }", query)
        self.assertIn("$startInfo.ArgumentList.Add([string]$argument)", query)
        self.assertIn("schemaVersion   = 'ttd-query-result.v3'", query)
        self.assertIn("traceSha256", query)
        self.assertIn("$processStarted -and -not $proc.HasExited", query)
        self.assertLess(
            query.index('$lines.Add(".echo $BODYEND")'),
            query.index('$lines.Add(".echo $END")'),
        )

    def test_query_rejects_a_missing_output_end_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace = root / "sample.run"
            trace.write_bytes(b"trace")
            fake = root / "fake-cdb.cmd"
            fake.write_text(
                "@echo off\n"
                "echo === TTDQUERY BEGIN ===\n"
                "echo one-real-query-line\n"
                "echo === TTDQUERY COMPLETE ===\n"
                "exit /b 0\n",
                encoding="ascii",
            )
            out_dir = root / "query"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(QUERY),
                    "-Trace",
                    str(trace),
                    "-OutDir",
                    str(out_dir),
                    "-CdbPath",
                    str(fake),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                1,
                completed.returncode,
                completed.stdout + completed.stderr,
            )
            result = json.loads(
                (out_dir / "result.json").read_text(encoding="utf-8-sig")
            )
            self.assertFalse(result["ok"])
            self.assertEqual([], result["output"])
            self.assertIn(
                "OUTPUT-END sentinel never appeared - the query output is incomplete",
                result["problems"],
            )

    def test_query_rejects_out_of_order_or_duplicate_markers(self) -> None:
        bad_transcripts = {
            "out-of-order": (
                "echo === TTDQUERY BEGIN ===\n"
                "echo === TTDQUERY COMPLETE ===\n"
                "echo === TTDQUERY OUTPUT END ===\n"
            ),
            "duplicate-output-end": (
                "echo === TTDQUERY BEGIN ===\n"
                "echo === TTDQUERY OUTPUT END ===\n"
                "echo === TTDQUERY OUTPUT END ===\n"
                "echo === TTDQUERY COMPLETE ===\n"
            ),
        }
        for name, transcript in bad_transcripts.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = pathlib.Path(temporary)
                trace = root / "sample.run"
                trace.write_bytes(b"trace")
                fake = root / "fake-cdb.cmd"
                fake.write_text(
                    "@echo off\n" + transcript + "exit /b 0\n",
                    encoding="ascii",
                )
                out_dir = root / "query"
                completed = subprocess.run(
                    [
                        "pwsh",
                        "-NoLogo",
                        "-NoProfile",
                        "-File",
                        str(QUERY),
                        "-Trace",
                        str(trace),
                        "-OutDir",
                        str(out_dir),
                        "-CdbPath",
                        str(fake),
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    1,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                result = json.loads(
                    (out_dir / "result.json").read_text(encoding="utf-8-sig")
                )
                self.assertFalse(result["ok"])
                self.assertEqual([], result["output"])
                self.assertTrue(
                    any(
                        "out of order" in problem or "ambiguous" in problem
                        for problem in result["problems"]
                    ),
                    result["problems"],
                )

    def test_query_ignores_cdb_prompt_echoes_of_exact_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace = root / "sample.run"
            trace.write_bytes(b"trace")
            fake = root / "fake-cdb.cmd"
            fake.write_text(
                "@echo off\n"
                "echo 0:000^> .echo === TTDQUERY BEGIN ===\n"
                "echo === TTDQUERY BEGIN ===\n"
                "echo one-real-query-line\n"
                "echo 0:000^> .echo === TTDQUERY OUTPUT END ===\n"
                "echo === TTDQUERY OUTPUT END ===\n"
                "echo 0:000^> .echo === TTDQUERY COMPLETE ===\n"
                "echo === TTDQUERY COMPLETE ===\n"
                "exit /b 0\n",
                encoding="ascii",
            )
            out_dir = root / "query"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(QUERY),
                    "-Trace",
                    str(trace),
                    "-OutDir",
                    str(out_dir),
                    "-CdbPath",
                    str(fake),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                0,
                completed.returncode,
                completed.stdout + completed.stderr,
            )
            result = json.loads(
                (out_dir / "result.json").read_text(encoding="utf-8-sig")
            )
            self.assertTrue(result["ok"])
            self.assertIn("one-real-query-line", result["output"])

    def test_query_rejects_debugger_command_errors_even_when_debugger_exits_zero(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace = root / "sample.run"
            trace.write_bytes(b"trace")
            fake = root / "fake-cdb.cmd"
            fake.write_text(
                "@echo off\n"
                "echo === TTDQUERY BEGIN ===\n"
                "echo         ^ pass count must be preceeded by whitespace error in 'bad-command'\n"
                "echo === TTDQUERY OUTPUT END ===\n"
                "echo === TTDQUERY COMPLETE ===\n"
                "exit /b 0\n",
                encoding="ascii",
            )
            out_dir = root / "query"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(QUERY),
                    "-Trace",
                    str(trace),
                    "-OutDir",
                    str(out_dir),
                    "-CdbPath",
                    str(fake),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                1,
                completed.returncode,
                completed.stdout + completed.stderr,
            )
            result = (out_dir / "result.json").read_text(encoding="utf-8-sig")
            self.assertIn(
                "debugger reported: pass count must be preceeded by whitespace error in",
                result,
            )

    def test_query_start_failure_reports_the_launch_error_not_cleanup_noise(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace = root / "sample.run"
            trace.write_bytes(b"trace")
            not_executable = root / "not-a-debugger.txt"
            not_executable.write_text("plain text", encoding="ascii")
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(QUERY),
                    "-Trace",
                    str(trace),
                    "-OutDir",
                    str(root / "query"),
                    "-CdbPath",
                    str(not_executable),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            combined = completed.stdout + completed.stderr
            self.assertNotEqual(0, completed.returncode, combined)
            self.assertNotIn(
                "Cannot bind argument to parameter 'Id' because it is null",
                combined,
            )

    def test_query_allows_benign_checksum_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary) / "paths with spaces"
            root.mkdir()
            trace = root / "sample.run"
            trace.write_bytes(b"trace")
            fake = root / "fake-cdb.cmd"
            out_dir = root / "query output"
            log_path = out_dir / "cdb.log"
            command_path = out_dir / "commands.txt"
            fake.write_text(
                "@echo off\n"
                'if /I not "%~1"=="-z" exit /b 41\n'
                f'if /I not "%~2"=="{trace}" exit /b 42\n'
                'if /I not "%~3"=="-logo" exit /b 43\n'
                f'if /I not "%~4"=="{log_path}" exit /b 44\n'
                'if /I not "%~5"=="-cf" exit /b 45\n'
                f'if /I not "%~6"=="{command_path}" exit /b 46\n'
                "echo *** WARNING: Unable to verify checksum for BEA.exe\n"
                "echo === TTDQUERY BEGIN ===\n"
                "echo === TTDQUERY OUTPUT END ===\n"
                "echo === TTDQUERY COMPLETE ===\n"
                "exit /b 0\n",
                encoding="ascii",
            )
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(QUERY),
                    "-Trace",
                    str(trace),
                    "-OutDir",
                    str(out_dir),
                    "-CdbPath",
                    str(fake),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                0,
                completed.returncode,
                completed.stdout + completed.stderr,
            )
            result = json.loads(
                (out_dir / "result.json").read_text(encoding="utf-8-sig")
            )
            self.assertEqual([], result["output"])

    def test_query_warns_for_unrelated_recorded_image_load_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace = root / "sample.run"
            trace.write_bytes(b"trace")
            fake = root / "fake-cdb.cmd"
            fake.write_text(
                "@echo off\n"
                "echo Unable to load image C:\\WINDOWS\\SYSTEM32\\ntdll.dll, Win32 error 0n2\n"
                "echo === TTDQUERY BEGIN ===\n"
                "echo === TTDQUERY OUTPUT END ===\n"
                "echo === TTDQUERY COMPLETE ===\n"
                "exit /b 0\n",
                encoding="ascii",
            )
            out_dir = root / "query"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(QUERY),
                    "-Trace",
                    str(trace),
                    "-OutDir",
                    str(out_dir),
                    "-CdbPath",
                    str(fake),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                0,
                completed.returncode,
                completed.stdout + completed.stderr,
            )
            result = json.loads(
                (out_dir / "result.json").read_text(encoding="utf-8-sig")
            )
            self.assertEqual([], result["problems"])
            self.assertEqual(1, len(result["warnings"]))
            self.assertIn("ntdll.dll", result["warnings"][0])

    def test_negative_control_rejects_module_row_despite_unrelated_warning(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace = root / "sample.run"
            trace.write_bytes(b"trace")
            fake = root / "fake-cdb.cmd"
            fake.write_text(
                "@echo off\n"
                "echo === TTDQUERY BEGIN ===\n"
                "echo === TTDQUERY OUTPUT END ===\n"
                "echo === NEGCONTROL BEGIN ===\n"
                "echo 10000000 10001000 NEGCONTROL-MODULE-THAT-CANNOT-EXIST\n"
                "echo Unable to verify checksum for unrelated.dll\n"
                "echo === TTDQUERY COMPLETE ===\n"
                "exit /b 0\n",
                encoding="ascii",
            )
            out_dir = root / "query"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(QUERY),
                    "-Trace",
                    str(trace),
                    "-OutDir",
                    str(out_dir),
                    "-CdbPath",
                    str(fake),
                    "-NegativeControl",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                1,
                completed.returncode,
                completed.stdout + completed.stderr,
            )
            result = json.loads(
                (out_dir / "result.json").read_text(encoding="utf-8-sig")
            )
            self.assertFalse(result["negativeControl"]["Passed"])
            self.assertIn(
                "NEGATIVE CONTROL FAILED",
                "\n".join(result["problems"]),
            )


class TtdCoverageCounterContractTests(unittest.TestCase):
    """The coverage receipt must not be able to publish impossible counters."""

    def run_counter_guard(
        self, summary: dict, *, quarantine_allowed: bool = False
    ) -> subprocess.CompletedProcess:
        """Drive the shipped guard out of Invoke-TtdExecCoverage.ps1 itself.

        The function body is lifted from the real script through the
        PowerShell AST, so this exercises the pipeline's own code rather than
        a copy of it, and fails loudly if the guard is renamed or deleted.
        """

        with tempfile.TemporaryDirectory() as temporary:
            summary_path = pathlib.Path(temporary) / "summary.json"
            summary_path.write_text(
                json.dumps(summary), encoding="utf-8"
            )
            wrapper_literal = str(COVERAGE_WRAPPER).replace("'", "''")
            summary_literal = str(summary_path).replace("'", "''")
            command = (
                "$ErrorActionPreference = 'Stop'; "
                "$errors = @(); "
                "$ast = [System.Management.Automation.Language.Parser]"
                "::ParseFile('" + wrapper_literal + "', [ref]$null, "
                "[ref]$errors); "
                "if ($errors.Count) { "
                "Write-Output 'coverage wrapper failed to parse'; exit 4 }; "
                "$guard = $ast.Find({ param($node) $node -is "
                "[System.Management.Automation.Language.FunctionDefinitionAst]"
                " -and $node.Name -eq "
                "'Assert-CoverageCountersAreConsistent' }, $true); "
                "if ($null -eq $guard) { "
                "Write-Output 'counter guard is missing'; exit 4 }; "
                ". ([scriptblock]::Create($guard.Extent.Text)); "
                "$summary = Get-Content -Raw -LiteralPath '"
                + summary_literal
                + "' | ConvertFrom-Json; "
                "$allowed = $"
                + ("true" if quarantine_allowed else "false")
                + "; try { Assert-CoverageCountersAreConsistent "
                "-Summary $summary -QuarantineAllowed:$allowed }"
                " catch { Write-Output $_.Exception.Message; exit 3 }; "
                "exit 0"
            )
            return subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_counter_guard_rejects_the_recorded_impossible_receipts(
        self,
    ) -> None:
        for name, summary in (
            ("options-open-manual-01", IMPOSSIBLE_SUMMARY_OPTIONS_OPEN),
            ("frontend-manual-02", IMPOSSIBLE_SUMMARY_FRONTEND_02),
        ):
            with self.subTest(receipt=name):
                completed = self.run_counter_guard(summary)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(
                    "mutually impossible",
                    completed.stdout,
                )
                self.assertIn(
                    summary["steps_executed"],
                    completed.stdout,
                )

    def test_counter_guard_accepts_sound_receipts(self) -> None:
        for name, summary in (
            ("startup-to-main-menu (pre-fix)", SOUND_SUMMARY_STARTUP),
            (
                "startup-to-main-menu (post-fix, two chunks)",
                SOUND_SUMMARY_STARTUP_AFTER_FIX,
            ),
        ):
            with self.subTest(receipt=name):
                completed = self.run_counter_guard(summary)
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

    def test_counter_guard_rejects_malformed_counters(self) -> None:
        missing = dict(SOUND_SUMMARY_STARTUP)
        del missing["steps_executed"]
        malformed = dict(SOUND_SUMMARY_STARTUP)
        malformed["steps_executed"] = "-1"
        for name, summary in (
            ("missing steps_executed", missing),
            ("non-decimal steps_executed", malformed),
        ):
            with self.subTest(summary=name):
                completed = self.run_counter_guard(summary)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

    def test_the_negative_control_fixtures_are_really_impossible(self) -> None:
        # Guards the negative control itself.  If someone ever "tidies" these
        # recorded numbers into consistency, the rejection test above would
        # keep passing while proving nothing, so pin the property that makes
        # them adverse evidence in the first place.
        for name, summary in (
            ("options-open-manual-01", IMPOSSIBLE_SUMMARY_OPTIONS_OPEN),
            ("frontend-manual-02", IMPOSSIBLE_SUMMARY_FRONTEND_02),
        ):
            with self.subTest(receipt=name):
                self.assertGreater(
                    int(summary["callback_hits"]),
                    int(summary["instructions_executed"]),
                )
                self.assertGreater(
                    int(summary["callback_hits"]),
                    int(summary["steps_executed"]),
                )
        for name, summary in (
            ("startup pre-fix", SOUND_SUMMARY_STARTUP),
            ("startup post-fix", SOUND_SUMMARY_STARTUP_AFTER_FIX),
        ):
            with self.subTest(receipt=name):
                self.assertLessEqual(
                    int(summary["callback_hits"]),
                    int(summary["instructions_executed"]),
                )
                self.assertLessEqual(
                    int(summary["instructions_executed"]),
                    int(summary["steps_executed"]),
                )

    def test_quarantine_is_opt_in_and_cannot_have_it_both_ways(self) -> None:
        # Accepted only when the run actually asked for quarantine.
        allowed = self.run_counter_guard(
            QUARANTINED_SUMMARY_OPTIONS_OPEN, quarantine_allowed=True
        )
        self.assertEqual(0, allowed.returncode, allowed.stdout + allowed.stderr)

        # Same receipt, no opt-in: refused.
        unrequested = self.run_counter_guard(QUARANTINED_SUMMARY_OPTIONS_OPEN)
        self.assertEqual(
            3, unrequested.returncode, unrequested.stdout + unrequested.stderr
        )
        self.assertIn("did not request", unrequested.stdout)

        # Quarantined AND carrying live counters: refused even with the opt-in.
        for leaked in (
            "callback_hits",
            "instructions_executed",
            "steps_executed",
        ):
            with self.subTest(leaked=leaked):
                both_ways = dict(QUARANTINED_SUMMARY_OPTIONS_OPEN)
                both_ways[leaked] = QUARANTINED_SUMMARY_OPTIONS_OPEN[
                    "quarantined_counters"
                ][leaked]
                completed = self.run_counter_guard(
                    both_ways, quarantine_allowed=True
                )
                self.assertEqual(
                    3, completed.returncode, completed.stdout + completed.stderr
                )
                self.assertIn("still carries top-level", completed.stdout)

    def test_quarantine_evidence_must_be_complete(self) -> None:
        bare = dict(QUARANTINED_SUMMARY_OPTIONS_OPEN)
        del bare["quarantined_counters"]

        no_reason = json.loads(json.dumps(QUARANTINED_SUMMARY_OPTIONS_OPEN))
        del no_reason["quarantined_counters"]["reason"]

        no_steps = json.loads(json.dumps(QUARANTINED_SUMMARY_OPTIONS_OPEN))
        del no_steps["quarantined_counters"]["steps_executed"]

        not_a_bool = json.loads(json.dumps(QUARANTINED_SUMMARY_OPTIONS_OPEN))
        not_a_bool["counters_quarantined"] = "true"

        for name, summary in (
            ("no evidence block", bare),
            ("no reason", no_reason),
            ("no steps_executed", no_steps),
            ("non-boolean marker", not_a_bool),
        ):
            with self.subTest(summary=name):
                completed = self.run_counter_guard(
                    summary, quarantine_allowed=True
                )
                self.assertEqual(
                    3, completed.returncode, completed.stdout + completed.stderr
                )

    def test_quarantine_does_not_weaken_the_default_path(self) -> None:
        # An impossible receipt that does NOT declare quarantine is refused
        # even when the caller passed -QuarantineCounters: the collector, not
        # the flag, decides what a receipt says.
        for name, summary in (
            ("options-open-manual-01", IMPOSSIBLE_SUMMARY_OPTIONS_OPEN),
            ("frontend-manual-02", IMPOSSIBLE_SUMMARY_FRONTEND_02),
        ):
            with self.subTest(receipt=name):
                completed = self.run_counter_guard(
                    summary, quarantine_allowed=True
                )
                self.assertEqual(
                    3, completed.returncode, completed.stdout + completed.stderr
                )
                self.assertIn("mutually impossible", completed.stdout)

    def test_collector_accumulates_replay_steps_in_64_bit_chunks(self) -> None:
        collector = read(COLLECTOR_SOURCE)

        self.assertIn("constexpr uint64_t kReplayChunkSteps", collector)
        self.assertIn("AccumulateReplayChunks", collector)
        self.assertIn("uint64_t StepsExecuted = 0;", collector)
        self.assertIn("uint64_t InstructionsExecuted = 0;", collector)
        self.assertIn(
            "replay accounting is impossible; refusing to publish ",
            collector,
        )
        self.assertIn('\\"replay_chunks\\":', collector)
        self.assertIn("RunReplayAccountingTests", collector)
        # Quarantine is opt-in; the default still refuses to publish.
        self.assertIn('option == L"--quarantine-counters"', collector)
        self.assertIn("if (!options.QuarantineCounters)", collector)
        self.assertIn("refusing to publish", collector)
        self.assertIn('\\"counters_quarantined\\":true', collector)
        self.assertIn('\\"counters_quarantined\\":false', collector)
        self.assertIn('\\"quarantined_counters\\":{', collector)
        self.assertIn(
            "ttd-replay-accounting-stopped-advancing",
            collector,
        )
        # The single whole-trace call is what truncated; it must be gone.
        self.assertNotIn("cursor->ReplayForward(replayLimit);", collector)
        self.assertNotIn("replayResult.StepsExecuted", collector)
        self.assertNotIn("replayResult.InstructionsExecuted", collector)

    def test_coverage_wrapper_calls_the_counter_guard(self) -> None:
        wrapper = read(COVERAGE_WRAPPER)

        self.assertIn(
            "function Assert-CoverageCountersAreConsistent {",
            wrapper,
        )
        self.assertIn(
            "Assert-CoverageCountersAreConsistent `\n    -Summary $summary `\n"
            "    -QuarantineAllowed:$QuarantineCounters",
            wrapper,
        )
        self.assertLess(
            wrapper.index("Assert-CoverageCountersAreConsistent `"),
            wrapper.index("$coverageFacts = Get-FileFacts -Path $coveragePath"),
        )
        self.assertIn("[switch]$QuarantineCounters", wrapper)
        self.assertIn("$collectorArguments.Add('--quarantine-counters')", wrapper)
        self.assertIn("countersQuarantined = $countersQuarantined", wrapper)

    def test_parity_lab_ingest_rejects_a_receipt_that_claims_both(self) -> None:
        ingest = read(ROOT / "tools" / "parity_lab.py")

        self.assertIn("counters_quarantined", ingest)
        self.assertIn("quarantined but still carries", ingest)
        self.assertIn("lacks quarantined_counters", ingest)
        self.assertIn("lack a reason", ingest)
        self.assertIn('"counterScoring": "unscored" if counters_quarantined', ingest)
        # Nullable so a consumer that wants a number gets nothing, not a lie.
        self.assertIn("callback_hits TEXT,", ingest)
        self.assertNotIn("callback_hits TEXT NOT NULL", ingest)


if __name__ == "__main__":
    unittest.main()
