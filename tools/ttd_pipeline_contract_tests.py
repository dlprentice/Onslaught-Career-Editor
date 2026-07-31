#!/usr/bin/env python3
"""Focused fail-closed checks for the local Time Travel Debugging helpers."""

from __future__ import annotations

import copy
import pathlib
import json
import os
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDER = ROOT / "tools" / "ttd_record.ps1"
WRAPPER = ROOT / "tools" / "Record-GameMoment.ps1"
QUERY = ROOT / "tools" / "ttd_query.ps1"
COVERAGE_WRAPPER = ROOT / "tools" / "Invoke-TtdExecCoverage.ps1"
CAMPAIGN = ROOT / "tools" / "Invoke-TtdCoverageCampaign.ps1"
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


# The two-trace stage-1 pilot of 2026-07-31 (local-lab/TTD-PILOT-2026-07-31.md),
# recorded verbatim from the receipts it wrote.  Both traces were replayed from
# the pristine specimen local-lab/safe-copy-bea-pristine/BEA.exe, sha256
# E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4.
#
#   G:\bea-ttd\q-pilot-cov-l742-20260731\receipt.json      exit 10, Thread stop
#   G:\bea-ttd\q-pilot-cov-l700-20260731\receipt.json      exit  0, Process stop
#
# L742 is the falsification case for the terminal-stop clause: its replay
# stopped on a Thread event, so the collector refused it - while the cursor had
# walked PAST the requested end position and both marker assertions held.  A
# second run reproduced all 6,815 ranges byte-identically.  Every one of the 66
# level-opening traces was timer-stopped with the guest still alive
# (guestOutcome 'alive-at-stop'), which is the class the Process-stop
# expectation was never calibrated on.  Keep these values as they are; they are
# the evidence the widened check has to be judged against.
PILOT_L742_SUMMARY = {
    "schema": "bea.ttd.exec-coverage.v1",
    "kind": "summary",
    "range_count": 6815,
    "covered_bytes": "552196",
    "counters_quarantined": False,
    "callback_hits": "1530568011",
    "instructions_executed": "3994296667",
    "steps_executed": "3994296727",
    "stop_reason": "Thread",
    "replay_chunks": "4",
    "replay_chunk_steps": "1000000000",
    "final_position": "0x20DE13:0x0",
    "replay_complete": False,
    "marker_assertions_passed": True,
    "collector_checks_passed": False,
}
PILOT_L742_METADATA = {
    "schema": "bea.ttd.exec-coverage.v1",
    "kind": "metadata",
    "trace_bytes": "8455716864",
    "lifetime_max": "0x20DE12:0x5B8",
    "lifetime_min": "0x34:0x0",
    "requested_from": "0x34:0x0",
    "requested_to": "0x20DE12:0x5B8",
}
PILOT_L700_SUMMARY = {
    "schema": "bea.ttd.exec-coverage.v1",
    "kind": "summary",
    "range_count": 6670,
    "covered_bytes": "551245",
    "counters_quarantined": False,
    "callback_hits": "1691572440",
    "instructions_executed": "4312902942",
    "steps_executed": "4312903002",
    "stop_reason": "Process",
    "replay_chunks": "5",
    "replay_chunk_steps": "1000000000",
    "final_position": "0x1A63E9:0x0",
    "replay_complete": True,
    "marker_assertions_passed": True,
    "collector_checks_passed": True,
}
PILOT_L700_METADATA = {
    "schema": "bea.ttd.exec-coverage.v1",
    "kind": "metadata",
    "trace_bytes": "4592762880",
    "lifetime_max": "0x1A63E8:0x270F",
    "lifetime_min": "0x34:0x0",
    "requested_from": "0x34:0x0",
    "requested_to": "0x1A63E8:0x270F",
}
PILOT_L742_RECEIPT = pathlib.Path(
    r"G:\bea-ttd\q-pilot-cov-l742-20260731\receipt.json"
)
PILOT_L700_RECEIPT = pathlib.Path(
    r"G:\bea-ttd\q-pilot-cov-l700-20260731\receipt.json"
)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def lift_function(name: str, script: pathlib.Path) -> str:
    """PowerShell that dot-sources one function straight out of a real script.

    Lifting through the AST means these tests drive the shipped code rather
    than a copy of it, and go red if the function is renamed or deleted.
    """

    literal = str(script).replace("'", "''")
    return (
        "$errors = @(); "
        "$ast = [System.Management.Automation.Language.Parser]::ParseFile('"
        + literal
        + "', [ref]$null, [ref]$errors); "
        "if ($errors.Count) { Write-Output 'script failed to parse'; exit 4 }; "
        "$found = $ast.Find({ param($node) $node -is "
        "[System.Management.Automation.Language.FunctionDefinitionAst] "
        "-and $node.Name -eq '" + name + "' }, $true); "
        "if ($null -eq $found) { Write-Output '" + name + " is missing'; exit 4 }; "
        ". ([scriptblock]::Create($found.Extent.Text)); "
    )


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


class TtdTerminalStopContractTests(unittest.TestCase):
    """A stop reason is only evidence for the trace class it was calibrated on.

    The collector requires a Process exit to call a replay complete.  That was
    calibrated on run-to-completion traces.  The 66 level-opening traces were
    timer-stopped with the guest still alive and their replays end on a Thread
    event, so the clause fails closed on sound coverage.  Widening it is only
    safe if the widening is opt-in, per-reason, and driven by the trace's own
    recorder receipt - never by the stop reason the replay happened to produce.
    """

    def run_terminal_stop_guard(
        self,
        summary: dict,
        metadata: dict,
        *,
        alive_expected: bool = False,
        base_reason: str = "Process",
    ) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            summary_path = root / "summary.json"
            metadata_path = root / "metadata.json"
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            command = (
                "$ErrorActionPreference = 'Stop'; "
                + lift_function(
                    "Assert-TerminalStopIsAcceptable", COVERAGE_WRAPPER
                )
                + "$summary = Get-Content -Raw -LiteralPath '"
                + str(summary_path).replace("'", "''")
                + "' | ConvertFrom-Json; "
                "$metadata = Get-Content -Raw -LiteralPath '"
                + str(metadata_path).replace("'", "''")
                + "' | ConvertFrom-Json; "
                "$alive = $"
                + ("true" if alive_expected else "false")
                + "; try { $result = Assert-TerminalStopIsAcceptable "
                "-Summary $summary -Metadata $metadata -BaseTerminalReason '"
                + base_reason
                + "' -AliveAtStopExpected:$alive } "
                "catch { Write-Output $_.Exception.Message; exit 3 }; "
                "Write-Output ($result | ConvertTo-Json -Compress); exit 0"
            )
            return subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def adjudicate(self, **kwargs) -> dict:
        completed = self.run_terminal_stop_guard(**kwargs)
        self.assertEqual(
            0, completed.returncode, completed.stdout + completed.stderr
        )
        return json.loads(completed.stdout)

    def test_the_pilot_thread_stop_is_refused_without_the_switch(self) -> None:
        verdict = self.adjudicate(
            summary=PILOT_L742_SUMMARY, metadata=PILOT_L742_METADATA
        )
        self.assertFalse(verdict["terminalStopAccepted"])
        self.assertFalse(verdict["stopReasonAccepted"])
        self.assertEqual("Thread", verdict["stopReason"])
        self.assertEqual(["Process"], verdict["acceptedStopReasons"])
        # The clause that failed is the ONLY one that failed - which is what
        # makes L742 evidence about the check rather than about the trace.
        self.assertTrue(verdict["positionReached"])
        self.assertTrue(verdict["markerAssertionsPassed"])

    def test_the_pilot_thread_stop_is_accepted_with_the_switch(self) -> None:
        verdict = self.adjudicate(
            summary=PILOT_L742_SUMMARY,
            metadata=PILOT_L742_METADATA,
            alive_expected=True,
        )
        self.assertTrue(verdict["terminalStopAccepted"])
        self.assertTrue(verdict["stopReasonAccepted"])
        self.assertFalse(verdict["baseStopReasonMet"])
        self.assertEqual(["Process", "Thread"], verdict["acceptedStopReasons"])
        self.assertTrue(verdict["aliveAtStopExpected"])

    def test_a_clean_process_stop_needs_no_switch_and_is_unchanged_by_it(
        self,
    ) -> None:
        for alive in (False, True):
            with self.subTest(alive_expected=alive):
                verdict = self.adjudicate(
                    summary=PILOT_L700_SUMMARY,
                    metadata=PILOT_L700_METADATA,
                    alive_expected=alive,
                )
                self.assertTrue(verdict["terminalStopAccepted"])
                self.assertTrue(verdict["baseStopReasonMet"])
                self.assertEqual("Process", verdict["stopReason"])

    def test_other_stop_reasons_still_fail_even_with_the_switch(self) -> None:
        # The widening is per-reason.  Anything that is not the declared class's
        # Thread stop keeps failing closed, with the switch or without it.
        for reason in ("Kernel", "Exception", "StepCount", "Invalid", "thread"):
            with self.subTest(stop_reason=reason):
                summary = copy.deepcopy(PILOT_L742_SUMMARY)
                summary["stop_reason"] = reason
                verdict = self.adjudicate(
                    summary=summary,
                    metadata=PILOT_L742_METADATA,
                    alive_expected=True,
                )
                self.assertFalse(verdict["stopReasonAccepted"])
                self.assertFalse(verdict["terminalStopAccepted"])

    def test_a_thread_stop_short_of_the_end_is_refused(self) -> None:
        # The position check does the real work; the switch does not excuse a
        # replay that never reached the requested end.
        summary = copy.deepcopy(PILOT_L742_SUMMARY)
        summary["final_position"] = "0x20DE11:0x0"
        verdict = self.adjudicate(
            summary=summary,
            metadata=PILOT_L742_METADATA,
            alive_expected=True,
        )
        self.assertTrue(verdict["stopReasonAccepted"])
        self.assertFalse(verdict["positionReached"])
        self.assertFalse(verdict["terminalStopAccepted"])

    def test_a_thread_stop_with_a_failed_marker_is_refused(self) -> None:
        summary = copy.deepcopy(PILOT_L742_SUMMARY)
        summary["marker_assertions_passed"] = False
        verdict = self.adjudicate(
            summary=summary,
            metadata=PILOT_L742_METADATA,
            alive_expected=True,
        )
        self.assertFalse(verdict["terminalStopAccepted"])

    def test_the_position_comparison_is_checked_against_the_collectors_own_verdict(
        self,
    ) -> None:
        # If the collector's replay_complete and a position comparison computed
        # here disagree, one of the two is wrong and neither may adjudicate.
        summary = copy.deepcopy(PILOT_L742_SUMMARY)
        summary["replay_complete"] = True
        completed = self.run_terminal_stop_guard(
            summary, PILOT_L742_METADATA, alive_expected=True
        )
        self.assertEqual(3, completed.returncode, completed.stdout)
        self.assertIn("disagrees with its own published evidence", completed.stdout)

    def test_malformed_or_missing_evidence_fails_closed(self) -> None:
        no_stop = copy.deepcopy(PILOT_L742_SUMMARY)
        del no_stop["stop_reason"]
        blank_stop = copy.deepcopy(PILOT_L742_SUMMARY)
        blank_stop["stop_reason"] = "  "
        bad_position = copy.deepcopy(PILOT_L742_SUMMARY)
        bad_position["final_position"] = "not-a-position"
        bad_marker = copy.deepcopy(PILOT_L742_SUMMARY)
        bad_marker["marker_assertions_passed"] = "true"
        for name, summary in (
            ("missing stop_reason", no_stop),
            ("blank stop_reason", blank_stop),
            ("malformed final_position", bad_position),
            ("stringy marker flag", bad_marker),
        ):
            with self.subTest(summary=name):
                completed = self.run_terminal_stop_guard(
                    summary, PILOT_L742_METADATA, alive_expected=True
                )
                self.assertEqual(3, completed.returncode, completed.stdout)

        bad_metadata = copy.deepcopy(PILOT_L742_METADATA)
        del bad_metadata["requested_to"]
        completed = self.run_terminal_stop_guard(
            PILOT_L742_SUMMARY, bad_metadata, alive_expected=True
        )
        self.assertEqual(3, completed.returncode, completed.stdout)

    def resolve_exit(
        self,
        *,
        collector_exit: int,
        terminal_stop: dict,
        quarantined: bool = False,
        alive_expected: bool = False,
    ) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            stop_path = pathlib.Path(temporary) / "terminal-stop.json"
            stop_path.write_text(json.dumps(terminal_stop), encoding="utf-8")
            command = (
                "$ErrorActionPreference = 'Stop'; "
                + lift_function("Resolve-CoverageExitCode", COVERAGE_WRAPPER)
                + "$stop = Get-Content -Raw -LiteralPath '"
                + str(stop_path).replace("'", "''")
                + "' | ConvertFrom-Json; "
                "$result = Resolve-CoverageExitCode -CollectorExitCode "
                + str(collector_exit)
                + " -TerminalStop $stop -CountersQuarantined:$"
                + ("true" if quarantined else "false")
                + " -AliveAtStopExpected:$"
                + ("true" if alive_expected else "false")
                + "; Write-Output ($result | ConvertTo-Json -Compress); exit 0"
            )
            completed = subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(
            0, completed.returncode, completed.stdout + completed.stderr
        )
        return json.loads(completed.stdout)

    def test_exit_ten_is_rewritten_only_for_the_declared_class(self) -> None:
        accepted_thread = self.adjudicate(
            summary=PILOT_L742_SUMMARY,
            metadata=PILOT_L742_METADATA,
            alive_expected=True,
        )
        refused_thread = self.adjudicate(
            summary=PILOT_L742_SUMMARY, metadata=PILOT_L742_METADATA
        )

        # Declared class, sole failing clause: the run is published.
        decision = self.resolve_exit(
            collector_exit=10,
            terminal_stop=accepted_thread,
            alive_expected=True,
        )
        self.assertTrue(decision["stopReasonAdjudicated"])
        self.assertEqual(0, decision["exitCode"])

        # Same receipt, nobody declared the class: exit 10 stands.
        undeclared = self.resolve_exit(
            collector_exit=10, terminal_stop=refused_thread
        )
        self.assertFalse(undeclared["stopReasonAdjudicated"])
        self.assertEqual(10, undeclared["exitCode"])

        # And the declaration is checked HERE too, not merely upstream: an
        # adjudication that says "accepted" must not rewrite an exit code when
        # this call was not told the trace class.  Both halves of the pipeline
        # have to be told, or a future caller that wires only one of them gets
        # a silent widening.
        smuggled = self.resolve_exit(
            collector_exit=10, terminal_stop=accepted_thread
        )
        self.assertFalse(smuggled["stopReasonAdjudicated"])
        self.assertEqual(10, smuggled["exitCode"])

        # A quarantine is not laundered by explaining the stop reason.
        quarantined = self.resolve_exit(
            collector_exit=10,
            terminal_stop=accepted_thread,
            quarantined=True,
            alive_expected=True,
        )
        self.assertTrue(quarantined["stopReasonAdjudicated"])
        self.assertEqual(11, quarantined["exitCode"])

        # Any other failure keeps its exit code, switch or no switch.
        kernel_summary = copy.deepcopy(PILOT_L742_SUMMARY)
        kernel_summary["stop_reason"] = "Kernel"
        kernel_stop = self.adjudicate(
            summary=kernel_summary,
            metadata=PILOT_L742_METADATA,
            alive_expected=True,
        )
        kernel = self.resolve_exit(
            collector_exit=10, terminal_stop=kernel_stop, alive_expected=True
        )
        self.assertFalse(kernel["stopReasonAdjudicated"])
        self.assertEqual(10, kernel["exitCode"])

        for other in (2, 3, 11):
            with self.subTest(collector_exit=other):
                passthrough = self.resolve_exit(
                    collector_exit=other,
                    terminal_stop=accepted_thread,
                    alive_expected=True,
                )
                self.assertFalse(passthrough["stopReasonAdjudicated"])
                self.assertEqual(other, passthrough["exitCode"])

    def test_the_pilot_fixtures_match_the_recorded_receipts(self) -> None:
        # Guards the negative control itself: if these fixtures ever drift from
        # the artifacts they were copied out of, the tests above would keep
        # passing while proving nothing about the real measurement.
        pairs = (
            (PILOT_L742_RECEIPT, PILOT_L742_SUMMARY, PILOT_L742_METADATA),
            (PILOT_L700_RECEIPT, PILOT_L700_SUMMARY, PILOT_L700_METADATA),
        )
        checked = 0
        for path, summary, metadata in pairs:
            if not path.exists():
                continue
            recorded = json.loads(path.read_text(encoding="utf-8-sig"))
            with self.subTest(receipt=path.name, block="summary"):
                for key, value in summary.items():
                    self.assertEqual(value, recorded["summary"][key], key)
            with self.subTest(receipt=path.name, block="metadata"):
                for key, value in metadata.items():
                    self.assertEqual(value, recorded["metadata"][key], key)
            checked += 1
        if checked == 0:
            self.skipTest("pilot coverage receipts are not on this machine")

    def test_coverage_wrapper_wires_the_terminal_stop_adjudication(self) -> None:
        wrapper = read(COVERAGE_WRAPPER)

        self.assertIn("[switch]$ExpectAliveAtStop", wrapper)
        self.assertIn("function Assert-TerminalStopIsAcceptable {", wrapper)
        self.assertIn("function Resolve-CoverageExitCode {", wrapper)
        self.assertIn(
            "-AliveAtStopExpected:$ExpectAliveAtStop",
            wrapper,
        )
        # The expectation is declared by the caller and recorded in the receipt
        # alongside the stop reason that was actually observed.
        self.assertIn("expectAliveAtStop = [bool]$ExpectAliveAtStop", wrapper)
        self.assertIn("terminalStop = $terminalStop", wrapper)
        self.assertIn("stopReasonAdjudicated = $stopReasonAdjudicated", wrapper)
        self.assertIn("exitCode = $effectiveExitCode", wrapper)
        self.assertIn("if ($effectiveExitCode -ne 0) {", wrapper)
        # The adjudication runs after the counter guard, so a quarantined run
        # cannot skip it.
        self.assertLess(
            wrapper.index("Assert-CoverageCountersAreConsistent `"),
            wrapper.index("$terminalStop = Assert-TerminalStopIsAcceptable"),
        )
        # The default is unchanged: Process only, and Position for a window.
        self.assertIn(
            "$baseTerminalReason = if ([string]::IsNullOrWhiteSpace($To)) "
            "{ 'Process' } else { 'Position' }",
            wrapper,
        )


FAKE_COVERAGE_WRAPPER = r"""
param(
    [Parameter(Mandatory = $true)][string]$TraceFile,
    [Parameter(Mandatory = $true)][string]$TargetExe,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [string]$Collector = '',
    [string]$ModuleName = 'BEA.exe',
    [string]$ExpectedBase = '',
    [string]$From = '',
    [string]$To = '',
    [string[]]$MustHitRva = @(),
    [string[]]$MustMissRva = @(),
    [switch]$Sequential,
    [switch]$QuarantineCounters,
    [switch]$ExpectAliveAtStop
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$utf8 = [System.Text.UTF8Encoding]::new($false)
$level = Split-Path -Leaf $OutputDirectory
$plan = Get-Content -Raw -LiteralPath $env:FAKE_PLAN | ConvertFrom-Json
$planned = 0
$entry = $plan.PSObject.Properties[$level]
if ($null -ne $entry) { $planned = [int]$entry.Value }
$invocation = [ordered]@{
    level = $level
    traceFile = $TraceFile
    targetExe = $TargetExe
    outputDirectory = $OutputDirectory
    mustHitRva = @($MustHitRva)
    mustMissRva = @($MustMissRva)
    quarantineCounters = [bool]$QuarantineCounters
    expectAliveAtStop = [bool]$ExpectAliveAtStop
    sequential = [bool]$Sequential
    plannedExit = $planned
}
[System.IO.File]::AppendAllText(
    $env:FAKE_LOG,
    ($invocation | ConvertTo-Json -Compress -Depth 6) + "`n",
    $utf8)
Write-Output "fake coverage run for $level"
if ($env:FAKE_NO_RECEIPT -eq $level) { exit $planned }
[System.IO.Directory]::CreateDirectory($OutputDirectory) | Out-Null
$quarantined = ($planned -eq 11)
$receipt = [ordered]@{
    schemaVersion = 'bea-ttd-exec-coverage-receipt.v2'
    collectorExitCode = $(if ($planned -eq 11) { 11 } elseif ($planned -eq 0) { 0 } else { 10 })
    exitCode = $planned
    replayComplete = ($planned -eq 0 -and -not $ExpectAliveAtStop)
    markerAssertionsPassed = $true
    collectorChecksPassed = ($planned -eq 0 -and -not $ExpectAliveAtStop)
    countersQuarantined = $quarantined
    stopReasonAdjudicated = ($ExpectAliveAtStop -and $planned -ne 10)
    terminalStop = [ordered]@{
        aliveAtStopExpected = [bool]$ExpectAliveAtStop
        stopReason = $(if ($ExpectAliveAtStop) { 'Thread' } else { 'Process' })
        positionReached = $true
        terminalStopAccepted = ($planned -ne 10)
    }
    coverage = [ordered]@{
        rangeCount = 6815
        sha256 = 'FAKE0000000000000000000000000000000000000000000000000000000000'
    }
    summary = [ordered]@{ covered_bytes = '552196' }
    metadata = [ordered]@{
        trace_bytes = '8455716864'
        lifetime_max = '0x20DE12:0x5B8'
        requested_to = '0x20DE12:0x5B8'
    }
    gapSummary = [ordered]@{
        total = '138351764'
        kind_large = '25'
        kind_unrecorded = '644135'
        kind_context_switch = '535861'
        event_KernelCall = '644098'
        event_SyntheticFallback = '137000000'
    }
}
[System.IO.File]::WriteAllText(
    (Join-Path $OutputDirectory 'receipt.json'),
    ($receipt | ConvertTo-Json -Depth 10) + "`n",
    $utf8)
if ($planned -ne 0) { exit $planned }
"""


class TtdCoverageCampaignContractTests(unittest.TestCase):
    """The campaign runner's receipt gating, resume, and immutability rules.

    Driven entirely against mock trace directories and a fake coverage wrapper:
    no real trace is opened, and the 4.2-hour campaign is never a prerequisite
    for proving that the runner reads the right receipt and refuses to retry.
    """

    LEVELS = ("level100", "level700", "level742")

    def build_sandbox(
        self,
        root: pathlib.Path,
        outcomes: dict[str, str] | None = None,
        levels: tuple[str, ...] | None = None,
        descending_sizes: bool = False,
    ) -> dict[str, pathlib.Path]:
        outcomes = outcomes or {}
        levels = levels or self.LEVELS
        traces = root / "traces"
        traces.mkdir(parents=True)
        for index, level in enumerate(levels):
            name = f"level-opening-3m-v1-{level}"
            directory = traces / name
            directory.mkdir()
            # Distinct sizes so -Order Size has something to sort by.  Reversed
            # on request, so that size order and name order disagree and the
            # test can tell which one the runner actually used.
            span = len(levels) - 1 - index if descending_sizes else index
            (directory / f"{name}.run").write_bytes(b"x" * (16 + span))
            (directory / "receipt.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": "ttd-record-receipt.v3",
                        "name": name,
                        "guestOutcome": outcomes.get(level, "alive-at-stop"),
                        "guestRanCleanly": True,
                        "traceSha256": f"FAKE{level.upper()}",
                        "traceBytes": 16 + index,
                    }
                ),
                encoding="utf-8",
            )
        target = root / "BEA.exe"
        target.write_bytes(b"MZ fake target")
        fake_wrapper = root / "fake-coverage.ps1"
        fake_wrapper.write_text(FAKE_COVERAGE_WRAPPER, encoding="utf-8")
        return {
            "traces": traces,
            "target": target,
            "wrapper": fake_wrapper,
            "output": root / "out",
            "log": root / "invocations.jsonl",
            "plan": root / "plan.json",
        }

    def run_campaign(
        self,
        paths: dict[str, pathlib.Path],
        *,
        plan: dict[str, int] | None = None,
        max_traces: int | None = None,
        output: pathlib.Path | None = None,
        no_receipt_for: str = "",
        extra: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        paths["plan"].write_text(json.dumps(plan or {}), encoding="utf-8")
        environment = dict(os.environ)
        environment["FAKE_LOG"] = str(paths["log"])
        environment["FAKE_PLAN"] = str(paths["plan"])
        environment["FAKE_NO_RECEIPT"] = no_receipt_for
        arguments = [
            "pwsh",
            "-NoLogo",
            "-NoProfile",
            "-File",
            str(CAMPAIGN),
            "-TraceRoot",
            str(paths["traces"]),
            "-OutputRoot",
            str(output or paths["output"]),
            "-TargetExe",
            str(paths["target"]),
            "-CoverageWrapper",
            str(paths["wrapper"]),
        ]
        if max_traces is not None:
            arguments += ["-MaxTraces", str(max_traces)]
        arguments += extra or []
        return subprocess.run(
            arguments,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    @staticmethod
    def invocations(paths: dict[str, pathlib.Path]) -> list[dict]:
        if not paths["log"].exists():
            return []
        return [
            json.loads(line)
            for line in paths["log"].read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @staticmethod
    def campaign_log(output: pathlib.Path) -> list[dict]:
        path = output / "campaign-log.jsonl"
        if not path.exists():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @classmethod
    def trace_records(cls, output: pathlib.Path) -> dict[str, dict]:
        return {
            row["level"]: row
            for row in cls.campaign_log(output)
            if row.get("kind") != "campaign-summary"
        }

    @staticmethod
    def snapshot(directory: pathlib.Path) -> list[tuple]:
        return sorted(
            (
                str(path.relative_to(directory)),
                path.stat().st_size,
                path.stat().st_mtime_ns,
            )
            for path in directory.rglob("*")
            if path.is_file()
        )

    def test_the_expectation_comes_from_the_recorder_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(
                pathlib.Path(temporary),
                outcomes={"level100": "exited-clean"},
            )
            completed = self.run_campaign(paths)
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )

            calls = {row["level"]: row for row in self.invocations(paths)}
            self.assertEqual(3, len(calls))
            # alive-at-stop declares the class; anything else does not.
            self.assertFalse(
                calls["level-opening-3m-v1-level100"]["expectAliveAtStop"]
            )
            self.assertTrue(
                calls["level-opening-3m-v1-level700"]["expectAliveAtStop"]
            )
            self.assertTrue(
                calls["level-opening-3m-v1-level742"]["expectAliveAtStop"]
            )
            # -QuarantineCounters is unconditional; the markers are passed.
            for call in calls.values():
                self.assertTrue(call["quarantineCounters"])
                self.assertEqual(["0xF34A0"], call["mustHitRva"])
                self.assertEqual(["0x2D150"], call["mustMissRva"])

            records = self.trace_records(paths["output"])
            self.assertEqual(3, len(records))
            for level, record in records.items():
                self.assertEqual("ok", record["status"], level)
                self.assertEqual(0, record["exitCode"])
                self.assertEqual(6815, record["rangeCount"])
                self.assertEqual("552196", record["coveredBytes"])
            self.assertEqual(
                "exited-clean",
                records["level-opening-3m-v1-level100"]["guestOutcome"],
            )

    def test_a_second_pass_resumes_and_re_runs_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            first = self.run_campaign(paths)
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertEqual(3, len(self.invocations(paths)))

            second = self.run_campaign(paths)
            self.assertEqual(0, second.returncode, second.stdout + second.stderr)
            # Not one extra invocation of the collector.
            self.assertEqual(3, len(self.invocations(paths)))

            log = self.campaign_log(paths["output"])
            resumed = [
                row
                for row in log
                if row.get("kind") != "campaign-summary"
                and row["status"] == "skipped"
            ]
            self.assertEqual(3, len(resumed))
            for row in resumed:
                self.assertIn("already collected", row["reason"])
            summaries = [
                row for row in log if row.get("kind") == "campaign-summary"
            ]
            self.assertEqual(2, len(summaries))
            self.assertEqual(3, summaries[1]["skipped"])
            self.assertEqual(0, summaries[1]["ok"])

    def test_a_quarantined_run_is_acceptable_and_recorded_as_such(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            completed = self.run_campaign(
                paths, plan={"level-opening-3m-v1-level742": 11}
            )
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )
            record = self.trace_records(paths["output"])[
                "level-opening-3m-v1-level742"
            ]
            self.assertEqual("ok", record["status"])
            self.assertEqual(11, record["exitCode"])
            self.assertTrue(record["countersQuarantined"])

            # And it resumes as done, not as something to try again.
            self.run_campaign(paths, plan={"level-opening-3m-v1-level742": 11})
            self.assertEqual(3, len(self.invocations(paths)))

    def test_an_unacceptable_exit_is_recorded_once_and_never_retried(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            plan = {"level-opening-3m-v1-level700": 10}
            first = self.run_campaign(paths, plan=plan)
            self.assertEqual(1, first.returncode, first.stdout + first.stderr)
            records = self.trace_records(paths["output"])
            self.assertEqual(
                "failed", records["level-opening-3m-v1-level700"]["status"]
            )
            self.assertEqual(
                10, records["level-opening-3m-v1-level700"]["exitCode"]
            )
            # The other two traces still ran: one bad trace is not a campaign
            # abort.
            self.assertEqual(
                "ok", records["level-opening-3m-v1-level742"]["status"]
            )
            self.assertEqual(3, len(self.invocations(paths)))

            second = self.run_campaign(paths, plan=plan)
            self.assertEqual(1, second.returncode)
            self.assertEqual(3, len(self.invocations(paths)))
            blocked = [
                row
                for row in self.campaign_log(paths["output"])
                if row.get("kind") != "campaign-summary"
                and row["status"] == "blocked"
            ]
            self.assertEqual(1, len(blocked))
            self.assertIn("not retrying", blocked[0]["reason"])

    def test_a_run_that_writes_no_receipt_is_a_failure_not_a_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            completed = self.run_campaign(
                paths, no_receipt_for="level-opening-3m-v1-level100"
            )
            self.assertEqual(1, completed.returncode, completed.stdout)
            record = self.trace_records(paths["output"])[
                "level-opening-3m-v1-level100"
            ]
            self.assertEqual("failed", record["status"])
            self.assertIn("without writing a receipt", record["reason"])

    def test_a_trace_without_a_usable_recorder_receipt_is_blocked(self) -> None:
        for name, mutate in (
            ("missing", lambda path: path.unlink()),
            (
                "wrong schema",
                lambda path: path.write_text(
                    json.dumps(
                        {
                            "schemaVersion": "ttd-record-receipt.v2",
                            "guestOutcome": "alive-at-stop",
                        }
                    ),
                    encoding="utf-8",
                ),
            ),
            (
                "no guestOutcome",
                lambda path: path.write_text(
                    json.dumps({"schemaVersion": "ttd-record-receipt.v3"}),
                    encoding="utf-8",
                ),
            ),
        ):
            with self.subTest(receipt=name), tempfile.TemporaryDirectory() as t:
                paths = self.build_sandbox(pathlib.Path(t))
                mutate(
                    paths["traces"]
                    / "level-opening-3m-v1-level100"
                    / "receipt.json"
                )
                completed = self.run_campaign(paths)
                self.assertEqual(1, completed.returncode, completed.stdout)
                records = self.trace_records(paths["output"])
                self.assertEqual(
                    "blocked", records["level-opening-3m-v1-level100"]["status"]
                )
                # Blocked, not aborted: the rest of the campaign still runs.
                self.assertEqual(
                    "ok", records["level-opening-3m-v1-level742"]["status"]
                )
                calls = [row["level"] for row in self.invocations(paths)]
                self.assertNotIn("level-opening-3m-v1-level100", calls)
                self.assertEqual(2, len(calls))

    def test_max_traces_bounds_the_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            completed = self.run_campaign(paths, max_traces=1)
            self.assertEqual(0, completed.returncode, completed.stdout)
            self.assertEqual(1, len(self.invocations(paths)))
            self.assertEqual(1, len(self.trace_records(paths["output"])))
            summary = [
                row
                for row in self.campaign_log(paths["output"])
                if row.get("kind") == "campaign-summary"
            ][0]
            self.assertEqual(3, summary["matched"])
            self.assertEqual(1, summary["selected"])

    def test_the_schedule_order_is_deterministic_in_both_modes(self) -> None:
        # Cost is linear in trace bytes (+/-1.7%), so -Order Size runs
        # smallest-first and gets the most traces done per hour if the campaign
        # is interrupted.  Sizes here descend with the name order, so a runner
        # that ignored -Order would pick the other trace.
        for order, expected in (
            ("Name", "level-opening-3m-v1-level100"),
            ("Size", "level-opening-3m-v1-level742"),
        ):
            with self.subTest(order=order), tempfile.TemporaryDirectory() as t:
                paths = self.build_sandbox(
                    pathlib.Path(t), descending_sizes=True
                )
                completed = self.run_campaign(
                    paths, max_traces=1, extra=["-Order", order]
                )
                self.assertEqual(0, completed.returncode, completed.stdout)
                self.assertEqual(
                    [expected], list(self.trace_records(paths["output"]))
                )

    def test_the_log_carries_the_density_metrics_and_no_step_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            self.run_campaign(paths, max_traces=1)
            record = list(self.trace_records(paths["output"]).values())[0]
            density = record["density"]
            self.assertEqual("8455716864", density["traceBytes"])
            self.assertEqual("2154002", density["sequences"])
            self.assertAlmostEqual(
                8455716864 / 2154002, density["traceBytesPerSequence"], places=2
            )
            self.assertAlmostEqual(
                138351764 / 2154002, density["gapEventsPerSequence"], places=2
            )
            self.assertEqual("25", density["kindLarge"])
            self.assertEqual("535861", density["kindContextSwitch"])
            # #149: this engine's step accounting is the thing under suspicion.
            # It must not appear as a logged metric.
            self.assertNotIn("steps", json.dumps(density).lower())

    def test_nothing_is_ever_written_into_a_trace_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            before = self.snapshot(paths["traces"])
            self.run_campaign(paths)
            self.assertEqual(before, self.snapshot(paths["traces"]))

    def test_an_output_root_inside_a_trace_directory_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            inside = (
                paths["traces"] / "level-opening-3m-v1-level700" / "coverage"
            )
            completed = self.run_campaign(paths, output=inside)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn(
                "Traces are immutable",
                completed.stdout + completed.stderr,
            )
            self.assertFalse(inside.exists())
            self.assertEqual([], self.invocations(paths))

    def test_campaign_source_holds_its_stated_rules(self) -> None:
        campaign = read(CAMPAIGN)

        # Sequential is a measurement (0.96x for 2-way), not a preference.
        self.assertIn("0.96x", campaign)
        self.assertIn("$AcceptableExitCodes = @(0, 11)", campaign)
        self.assertIn("ExpectAliveAtStop", campaign)
        self.assertIn("QuarantineCounters = $true", campaign)
        self.assertIn("guestOutcome", campaign)
        self.assertIn("-ceq 'alive-at-stop'", campaign)
        self.assertIn("ttd-record-receipt.v3", campaign)
        self.assertIn("not retrying", campaign)
        self.assertIn("Traces are immutable", campaign)
        # No parallel scheduler.
        self.assertNotIn("ForEach-Object -Parallel", campaign)
        self.assertNotIn("Start-Job", campaign)

        # And no step-count consumption.  Checked against the CODE, with the
        # comments stripped, so that documenting the rule cannot satisfy it.
        body = campaign.split("#>", 1)[1]
        code = "\n".join(
            line
            for line in body.splitlines()
            if not line.lstrip().startswith("#")
        )
        for banned in ("steps_executed", "instructions_executed", "callback_hits"):
            self.assertTrue(
                banned not in code,
                f"the campaign runner must not consume {banned}: "
                "TTD Replay 1.11.584.0 freezes those counters (#149)",
            )
        self.assertIn("steps_executed is not evidence", campaign)


if __name__ == "__main__":
    unittest.main()
