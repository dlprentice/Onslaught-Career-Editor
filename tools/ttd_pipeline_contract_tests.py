#!/usr/bin/env python3
"""Focused fail-closed checks for the local Time Travel Debugging helpers."""

from __future__ import annotations

import copy
import hashlib
import pathlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import parity_lab  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDER = ROOT / "tools" / "ttd_record.ps1"
WRAPPER = ROOT / "tools" / "Record-GameMoment.ps1"
QUERY = ROOT / "tools" / "ttd_query.ps1"
COVERAGE_WRAPPER = ROOT / "tools" / "Invoke-TtdExecCoverage.ps1"
CALL_CONTEXT_WRAPPER = ROOT / "tools" / "Invoke-TtdCallContextV2.ps1"
DATA_WRITES_WRAPPER = ROOT / "tools" / "Invoke-TtdDataWrites.ps1"
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


class TtdCallContextRelationshipTests(unittest.TestCase):
    """Call-context READY data must preserve exact row relationships."""

    @staticmethod
    def event(
        index: int,
        event_type: str,
        invocation_index: int | None,
        *,
        decoded_return: bool = False,
        association_epoch: int = 0,
    ) -> dict:
        is_return = event_type == "return"
        pc = (
            "0x401002"
            if is_return
            else "0x402000"
            if event_type == "call"
            else "0x401000"
        )
        instruction_target = "0x402005" if is_return else "0x401000"
        fallthrough = "0x402005" if event_type == "call" else "0x0"
        return {
            "event_index": index,
            "event_type": event_type,
            "target_index": 0,
            "invocation_index": invocation_index,
            "association_epoch": str(association_epoch),
            "position": f"0x1:0x{index + 1:X}",
            "previous_position": f"0x1:0x{index:X}",
            "unique_thread_id": "2",
            "os_thread_id": "1234",
            "pc": pc,
            "sp": "0x1000",
            "fp": "0x1100",
            "instruction_target": instruction_target,
            "fallthrough": fallthrough,
            "context_flags": "0x1002F",
            "raw_edx_eax": "0x400000001",
            "basic_return_value_untyped": "0x1",
            "control_registers_valid": True,
            "integer_registers_valid": True,
            "register_views_agree": True,
            "decoded_near_return": decoded_return,
            "registers": {
                "eax": "0x1",
                "ebx": "0x2",
                "ecx": "0x3",
                "edx": "0x4",
                "esi": "0x5",
                "edi": "0x6",
                "ebp": "0x1100",
                "esp": "0x1000",
                "eip": pc,
                "eflags": "0x202",
            },
            "stack": {
                "address": "0x1000",
                "requested_bytes": 4,
                "valid_bytes": 4,
                "query_valid": True,
                "hex": "05204000",
            },
            "instruction_bytes": {
                "address": pc if is_return else "0x0",
                "valid_bytes": 1 if is_return else 0,
                "query_valid": is_return,
                "hex": "C3" if is_return else "",
            },
        }

    @classmethod
    def fixture(cls, *, degraded: bool = False) -> dict:
        gap_free = 0 if degraded else 1
        validated_returns = 0 if degraded else 1
        orphan_returns = 1 if degraded else 0
        barrier_count = 1 if degraded else 0
        return {
            "targets": [
                {
                    "target_index": 0,
                    "entry_rva": "0x1000",
                    "entry_va": "0x401000",
                    "ranges": [
                        {
                            "rva_start": "0x1000",
                            "rva_end_exclusive": "0x1010",
                        }
                    ],
                    "expected_entry_count": "1",
                    "expected_call_count": "1",
                    "expected_return_count": "1",
                    "observed_entry_count": "1",
                    "observed_call_count": "1",
                    "observed_return_count": "1",
                    "observed_call_entry_pair_count": "1",
                    "observed_validated_return_count": str(validated_returns),
                    "observed_orphan_return_count": str(orphan_returns),
                    "observed_gap_free_envelope_count": str(gap_free),
                    "expectations_passed": True,
                }
            ],
            "events": [
                cls.event(0, "call", 0),
                cls.event(1, "entry", 0),
                cls.event(
                    2,
                    "return",
                    None if degraded else 0,
                    decoded_return=True,
                    association_epoch=barrier_count,
                ),
            ],
            "invocations": [
                {
                    "invocation_index": 0,
                    "target_index": 0,
                    "unique_thread_id": "2",
                    "association_epoch": "0",
                    "call_event_index": 0,
                    "entry_event_index": 1,
                    "return_event_index": None if degraded else 2,
                    "grade": (
                        "CALL_ENTRY" if degraded else "CALL_ENTRY_RETURN"
                    ),
                    "call_entry_checks_passed": True,
                    "return_checks_passed": not degraded,
                    "gap_crossed": degraded,
                    "continuity_break_crossed": False,
                }
            ],
            "summary": {
                "call_entry_pair_count": "1",
                "validated_return_count": str(validated_returns),
                "raw_return_count": "1",
                "orphan_return_count": str(orphan_returns),
                "gap_free_envelope_count": str(gap_free),
                "continuity_break_callbacks": "0",
                "association_barrier_count": str(barrier_count),
                "final_association_epoch": str(barrier_count),
                "expectations_passed": True,
                "pairing_expectations_passed": True,
                "ordering_valid": True,
                "contexts_valid": True,
            },
            "gapSummary": {
                "total": str(barrier_count),
                "kind_no_gap": "0",
                "kind_context_switch": "0",
                "kind_unrecorded": str(barrier_count),
                "kind_large": "0",
                "event_SyntheticSequence": "0",
                "event_CodeCacheFlush": "0",
                "event_PreAtomicOperation": "0",
                "event_PotentialAtomicCollision": "0",
                "event_EtwEvent": "0",
                "event_DebugBreak": "0",
                "event_FastFail": "0",
                "event_KernelCall": str(barrier_count),
                "event_SyntheticFallback": "0",
                "event_ExceptionDispatch": "0",
                "event_UnknownInstruction": "0",
                "event_ThreadSuspended": "0",
                "event_SListRollback": "0",
                "event_SyncPoint": "0",
                "event_PauseEmulation": "0",
                "event_StopEmulation": "0",
                "event_Throttled": "0",
            },
            "targetSpecifications": [
                {
                    "target_index": 0,
                    "entry_rva": "0x1000",
                    "entry_va": "0x401000",
                    "expected_entry_count": 1,
                    "expected_call_count": 1,
                    "expected_return_count": 1,
                    "ranges": [
                        {
                            "rva_start": "0x1000",
                            "rva_end_exclusive": "0x1010",
                        }
                    ],
                }
            ],
        }

    def run_relationship_guard(self, fixture: dict) -> subprocess.CompletedProcess:
        """Execute the function body extracted from the shipped wrapper AST."""

        with tempfile.TemporaryDirectory() as temporary:
            fixture_path = pathlib.Path(temporary) / "fixture.json"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            wrapper_literal = str(CALL_CONTEXT_WRAPPER).replace("'", "''")
            fixture_literal = str(fixture_path).replace("'", "''")
            command = (
                "$ErrorActionPreference = 'Stop'; $errors = @(); "
                "$ast = [System.Management.Automation.Language.Parser]::ParseFile("
                f"'{wrapper_literal}', [ref]$null, [ref]$errors); "
                "if ($errors.Count) { Write-Output 'wrapper parse failed'; exit 4 }; "
                "$names = @('Get-RequiredProperty','Get-RequiredScalarProperty',"
                "'Get-RequiredObject','Get-RequiredArray','Get-RequiredBoolean',"
                "'Get-RequiredString',"
                "'Get-RequiredUInt64','Get-RequiredIndex','Get-RequiredUInt32TextScalar',"
                "'Add-UInt64Checked','Get-NullableIndex',"
                "'Get-NullableUInt64','Convert-UnsignedNumericText',"
                "'Convert-ToCanonicalHex','Assert-HexText','Assert-TtdPosition',"
                "'Convert-TtdPositionValue','Compare-TtdPositionValue',"
                "'Get-EventStackReturnAddress','Get-EventRegister',"
                "'Test-EventContextValid','Test-EventDecodedNearReturn',"
                "'Assert-CallContextRelationships'); "
                "foreach ($name in $names) { $node = $ast.Find({ param($candidate) "
                "$candidate -is [System.Management.Automation.Language."
                "FunctionDefinitionAst] -and $candidate.Name -eq $name }, $true); "
                "if ($null -eq $node) { Write-Output \"missing $name\"; exit 4 }; "
                ". ([scriptblock]::Create($node.Extent.Text)) }; "
                f"$fixture = Get-Content -Raw -LiteralPath '{fixture_literal}' "
                "| ConvertFrom-Json -Depth 30; try { $result = "
                "Assert-CallContextRelationships -Targets @($fixture.targets) "
                "-TargetSpecifications @($fixture.targetSpecifications) "
                "-Events @($fixture.events) -Invocations @($fixture.invocations) "
                "-GapSummary $fixture.gapSummary -Summary $fixture.summary "
                "-ExpectedStackBytes 4; "
                "$result | ConvertTo-Json -Compress } "
                "catch { Write-Output $_.Exception.Message; exit 3 }; exit 0"
            )
            return subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    @staticmethod
    def replay_boundary_fixture() -> dict:
        return {
            "metadata": {
                "lifetime_min": "0x1:0x0",
                "lifetime_max": "0x5:0x0",
                "requested_from": "0x1:0x0",
                "requested_to": "0x5:0x0",
                "module_load_sequence": "0x1",
                "module_unload_sequence": "0xFFFFFFFFFFFFFFFE",
                "stack_bytes_requested": 4,
                "event_limit": "100",
            },
            "summary": {
                "stop_reason": "Process",
                "final_position": "0x5:0x1",
                "replay_complete": True,
                "replay_chunks": "1",
                "replay_chunk_steps": "1000000000",
                "entry_callbacks": "1",
                "call_return_callbacks": "2",
                "instructions_executed": "10",
                "steps_executed": "10",
            },
            "events": [
                {"position": "0x2:0x0", "previous_position": "0x1:0x0"},
                {"position": "0x3:0x0", "previous_position": "0x2:0x0"},
                {"position": "0x4:0x0", "previous_position": "0x3:0x0"},
            ],
        }

    def run_replay_boundary_guard(
        self,
        fixture: dict,
        *,
        from_argument: str = "",
        to_argument: str = "",
        event_limit: int = 100,
        event_count: int = 3,
        entry_event_count: int = 1,
        call_return_event_count: int = 2,
    ) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_path = pathlib.Path(temporary) / "fixture.json"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            fixture_literal = str(fixture_path).replace("'", "''")
            from_literal = from_argument.replace("'", "''")
            to_literal = to_argument.replace("'", "''")
            definitions = "".join(
                lift_function(name, CALL_CONTEXT_WRAPPER)
                for name in (
                    "Get-RequiredProperty",
                    "Get-RequiredScalarProperty",
                    "Get-RequiredBoolean",
                    "Get-RequiredString",
                    "Get-RequiredUInt64",
                    "Get-RequiredIndex",
                    "Convert-UnsignedNumericText",
                    "Assert-HexText",
                    "Assert-TtdPosition",
                    "Convert-TtdPositionValue",
                    "Compare-TtdPositionValue",
                    "Assert-CallContextReplayBoundary",
                )
            )
            command = (
                definitions
                + f"$fixture = Get-Content -Raw -LiteralPath '{fixture_literal}' "
                "| ConvertFrom-Json -Depth 20; try { $result = "
                "Assert-CallContextReplayBoundary "
                "-Metadata $fixture.metadata -Summary $fixture.summary "
                "-Events @($fixture.events) "
                f"-RequestedFromArgument '{from_literal}' "
                f"-RequestedToArgument '{to_literal}' "
                "-ExpectedStackBytes 4 "
                f"-ExpectedEventLimit {event_limit} "
                f"-EventCount {event_count} "
                f"-EntryEventCount {entry_event_count} "
                f"-CallAndReturnEventCount {call_return_event_count}; "
                "$result | ConvertTo-Json -Compress } "
                "catch { Write-Output $_.Exception.Message; exit 3 }; exit 0"
            )
            return subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_wrapper_accepts_gap_free_link_and_degraded_orphan_return(self) -> None:
        for degraded in (False, True):
            with self.subTest(degraded=degraded):
                completed = self.run_relationship_guard(
                    self.fixture(degraded=degraded)
                )
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                result = json.loads(completed.stdout.strip().splitlines()[-1])
                self.assertEqual(
                    0 if degraded else 1,
                    result["validatedReturnCount"],
                )
                self.assertEqual(
                    0 if degraded else 1,
                    result["gapFreeEnvelopeCount"],
                )

    def test_wrapper_recomputes_replay_window_limits_and_termination(self) -> None:
        accepted = self.run_replay_boundary_guard(self.replay_boundary_fixture())
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        accepted_result = json.loads(accepted.stdout.strip().splitlines()[-1])
        self.assertTrue(accepted_result["replayComplete"])

        # TTD's long-replay instruction/step counters are known to stop
        # advancing. Call/return callbacks remain independently counted and the
        # collector deliberately permits them to exceed those quarantined
        # counters, bounded by the configured replay-step capacity. This is the
        # shape reproduced by the natural Level 521 ApplyDamage trace.
        stalled_counters = self.replay_boundary_fixture()
        stalled_counters["summary"]["call_return_callbacks"] = "43072740"
        stalled_counters["summary"]["instructions_executed"] = "136541"
        stalled_counters["summary"]["steps_executed"] = "136542"
        accepted = self.run_replay_boundary_guard(stalled_counters)
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        accepted_result = json.loads(accepted.stdout.strip().splitlines()[-1])
        self.assertEqual(43072740, accepted_result["callReturnCallbacks"])

        wrong_stop = self.replay_boundary_fixture()
        wrong_stop["summary"]["stop_reason"] = "Position"

        early_final = self.replay_boundary_fixture()
        early_final["summary"]["final_position"] = "0x4:0x0"

        false_report = self.replay_boundary_fixture()
        false_report["summary"]["replay_complete"] = False

        stack_limit = self.replay_boundary_fixture()
        stack_limit["metadata"]["stack_bytes_requested"] = 8

        event_limit = self.replay_boundary_fixture()
        event_limit["metadata"]["event_limit"] = "99"

        forged_window = self.replay_boundary_fixture()
        forged_window["metadata"]["requested_to"] = "0x4:0x0"

        zero_chunks = self.replay_boundary_fixture()
        zero_chunks["summary"]["replay_chunks"] = "0"

        excessive_chunks = self.replay_boundary_fixture()
        excessive_chunks["summary"]["replay_chunks"] = "1000001"

        wrong_chunk_size = self.replay_boundary_fixture()
        wrong_chunk_size["summary"]["replay_chunk_steps"] = "999"

        missing_entry_callback = self.replay_boundary_fixture()
        missing_entry_callback["summary"]["entry_callbacks"] = "0"

        missing_call_callback = self.replay_boundary_fixture()
        missing_call_callback["summary"]["call_return_callbacks"] = "1"

        excessive_callbacks = self.replay_boundary_fixture()
        excessive_callbacks["summary"]["call_return_callbacks"] = str(2**64 - 1)

        impossible_chunk_capacity = self.replay_boundary_fixture()
        impossible_chunk_capacity["summary"]["instructions_executed"] = "1500000000"
        impossible_chunk_capacity["summary"]["steps_executed"] = "2000000000"

        array_stop = self.replay_boundary_fixture()
        array_stop["summary"]["stop_reason"] = ["Process"]

        impossible_terminal = self.replay_boundary_fixture()
        impossible_terminal["summary"]["final_position"] = "0xFFFFFFFF:0x0"

        event_outside_window = self.replay_boundary_fixture()
        event_outside_window["events"][1]["position"] = "0x10:0x0"
        event_outside_window["events"][2]["previous_position"] = "0x10:0x0"

        previous_before_lifetime = self.replay_boundary_fixture()
        previous_before_lifetime["events"][0]["previous_position"] = "0x0:0x0"

        module_loaded_late = self.replay_boundary_fixture()
        module_loaded_late["metadata"]["module_load_sequence"] = "0x2"

        module_unloaded_in_window = self.replay_boundary_fixture()
        module_unloaded_in_window["metadata"]["module_unload_sequence"] = "0x5"

        for name, fixture, expected in (
            ("stop", wrong_stop, "replay-complete flag disagrees"),
            ("final", early_final, "native replay terminal boundary"),
            ("reported", false_report, "replay-complete flag disagrees"),
            ("stack-limit", stack_limit, "metadata limits disagree"),
            ("event-limit", event_limit, "metadata limits disagree"),
            ("window", forged_window, "metadata window disagrees"),
            ("chunks", zero_chunks, "callbacks or chunk limits"),
            ("excessive-chunks", excessive_chunks, "callbacks or chunk limits"),
            ("chunk-size", wrong_chunk_size, "callbacks or chunk limits"),
            ("entry-callback", missing_entry_callback, "callbacks or chunk limits"),
            ("call-callback", missing_call_callback, "callbacks or chunk limits"),
            ("excessive-callback", excessive_callbacks, "callbacks or chunk limits"),
            (
                "chunk-capacity",
                impossible_chunk_capacity,
                "callbacks or chunk limits",
            ),
            ("array-stop", array_stop, "one scalar JSON value"),
            ("terminal-bound", impossible_terminal, "native replay terminal boundary"),
            ("event-window", event_outside_window, "requested replay window"),
            ("previous-lifetime", previous_before_lifetime, "previous position"),
            ("module-load", module_loaded_late, "module instance that is not active"),
            (
                "module-unload",
                module_unloaded_in_window,
                "module instance that is not active",
            ),
        ):
            with self.subTest(poison=name):
                completed = self.run_replay_boundary_guard(fixture)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(expected, completed.stdout)

        explicit_window = self.replay_boundary_fixture()
        explicit_window["metadata"]["requested_to"] = "0x4:0x0"
        explicit_window["summary"]["stop_reason"] = "Position"
        explicit_window["summary"]["final_position"] = "0x4:0x0"
        explicit = self.run_replay_boundary_guard(
            explicit_window,
            to_argument="0x4:0x0",
        )
        self.assertEqual(0, explicit.returncode, explicit.stdout + explicit.stderr)

    def test_wrapper_rejects_broken_backlinks_and_grade_upgrades(self) -> None:
        broken_backlink = self.fixture()
        broken_backlink["events"][2]["invocation_index"] = 7
        false_gap_free = self.fixture()
        false_gap_free["invocations"][0]["gap_crossed"] = True
        forged_post_gap = self.fixture(degraded=True)
        forged_post_gap["events"][2]["association_epoch"] = "0"
        forged_post_gap["events"][2]["invocation_index"] = 0
        false_aggregate = self.fixture()
        false_aggregate["targets"][0][
            "observed_gap_free_envelope_count"
        ] = "2"

        for name, fixture, expected in (
            ("backlink", broken_backlink, "broken return backlink"),
            ("grade", false_gap_free, "return flag disagrees"),
            ("post-gap", forged_post_gap, "no matching invocation backlink"),
            ("aggregate", false_aggregate, "aggregate counts disagree"),
        ):
            with self.subTest(poison=name):
                completed = self.run_relationship_guard(fixture)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(expected, completed.stdout)

    def test_wrapper_replays_native_lifo_return_association(self) -> None:
        fixture = self.fixture()
        target = fixture["targets"][0]
        for field in (
            "expected_entry_count",
            "expected_call_count",
            "expected_return_count",
            "observed_entry_count",
            "observed_call_count",
            "observed_return_count",
            "observed_call_entry_pair_count",
            "observed_validated_return_count",
            "observed_gap_free_envelope_count",
        ):
            target[field] = "2"
        specification = fixture["targetSpecifications"][0]
        for field in (
            "expected_entry_count",
            "expected_call_count",
            "expected_return_count",
        ):
            specification[field] = 2
        summary = fixture["summary"]
        summary["call_entry_pair_count"] = "2"
        summary["validated_return_count"] = "2"
        summary["raw_return_count"] = "2"
        summary["gap_free_envelope_count"] = "2"

        events = [
            self.event(0, "call", 0),
            self.event(1, "entry", 0),
            self.event(2, "call", 1),
            self.event(3, "entry", 1),
            self.event(4, "return", 1, decoded_return=True),
            self.event(5, "return", 0, decoded_return=True),
        ]

        def bind_stack(event: dict, sp: str, fallthrough: str) -> None:
            event["sp"] = sp
            event["registers"]["esp"] = sp
            event["stack"]["address"] = sp
            value = int(fallthrough, 16)
            event["stack"]["hex"] = value.to_bytes(4, "little").hex().upper()

        events[2]["pc"] = "0x403000"
        events[2]["registers"]["eip"] = "0x403000"
        events[2]["fallthrough"] = "0x403005"
        bind_stack(events[2], "0xFF0", "0x403005")
        bind_stack(events[3], "0xFF0", "0x403005")
        events[4]["instruction_target"] = "0x403005"
        bind_stack(events[4], "0xFF0", "0x403005")
        bind_stack(events[0], "0x1000", "0x402005")
        bind_stack(events[1], "0x1000", "0x402005")
        bind_stack(events[5], "0x1000", "0x402005")
        events[4]["registers"]["eax"] = "0xB"
        events[4]["raw_edx_eax"] = "0x40000000B"
        events[4]["basic_return_value_untyped"] = "0xB"
        events[5]["registers"]["eax"] = "0xA"
        events[5]["raw_edx_eax"] = "0x40000000A"
        events[5]["basic_return_value_untyped"] = "0xA"
        fixture["events"] = events
        invocation = fixture["invocations"][0]
        invocation["return_event_index"] = 5
        fixture["invocations"].append(
            {
                **copy.deepcopy(invocation),
                "invocation_index": 1,
                "call_event_index": 2,
                "entry_event_index": 3,
                "return_event_index": 4,
            }
        )

        accepted = self.run_relationship_guard(fixture)
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

        non_lifo = copy.deepcopy(fixture)
        non_lifo["events"][4]["invocation_index"] = 0
        non_lifo["events"][5]["invocation_index"] = 1
        non_lifo["invocations"][0]["return_event_index"] = 4
        non_lifo["invocations"][1]["return_event_index"] = 5
        first_return = non_lifo["events"][4]
        second_return = non_lifo["events"][5]
        first_return["instruction_target"] = "0x402005"
        bind_stack(first_return, "0x1000", "0x402005")
        second_return["instruction_target"] = "0x403005"
        bind_stack(second_return, "0xFF0", "0x403005")

        rejected = self.run_relationship_guard(non_lifo)
        self.assertEqual(3, rejected.returncode, rejected.stdout + rejected.stderr)
        self.assertIn("native LIFO association", rejected.stdout)

        overwritten_pending = copy.deepcopy(fixture)
        original_events = overwritten_pending["events"]
        overwritten_pending["events"] = [
            original_events[0],
            original_events[2],
            original_events[1],
            original_events[3],
            original_events[4],
            original_events[5],
        ]
        position_steps = (1, 1, 2, 2, 3, 4)
        previous_steps = (0, 0, 1, 1, 2, 3)
        for index, event in enumerate(overwritten_pending["events"]):
            event["event_index"] = index
            event["position"] = f"0x1:0x{position_steps[index]:X}"
            event["previous_position"] = f"0x1:0x{previous_steps[index]:X}"
        overwritten_pending["invocations"][0]["call_event_index"] = 0
        overwritten_pending["invocations"][0]["entry_event_index"] = 2
        overwritten_pending["invocations"][0]["return_event_index"] = 5
        overwritten_pending["invocations"][1]["call_event_index"] = 1
        overwritten_pending["invocations"][1]["entry_event_index"] = 3
        overwritten_pending["invocations"][1]["return_event_index"] = 4
        overwritten_pending["events"][1]["pc"] = "0x402000"
        overwritten_pending["events"][1]["registers"]["eip"] = "0x402000"
        overwritten_pending["events"][1]["fallthrough"] = "0x402005"
        bind_stack(overwritten_pending["events"][1], "0x1000", "0x402005")
        bind_stack(overwritten_pending["events"][3], "0x1000", "0x402005")
        overwritten_pending["events"][4]["instruction_target"] = "0x402005"
        bind_stack(overwritten_pending["events"][4], "0x1000", "0x402005")

        rejected_pending = self.run_relationship_guard(overwritten_pending)
        self.assertEqual(
            3,
            rejected_pending.returncode,
            rejected_pending.stdout + rejected_pending.stderr,
        )
        self.assertIn("native pending-call association", rejected_pending.stdout)

    def test_wrapper_accepts_native_three_byte_c3_capture(self) -> None:
        for valid_bytes, payload in ((2, "C390"), (3, "C39090")):
            with self.subTest(valid_bytes=valid_bytes):
                fixture = self.fixture()
                instruction = fixture["events"][2]["instruction_bytes"]
                instruction["valid_bytes"] = valid_bytes
                instruction["hex"] = payload
                completed = self.run_relationship_guard(fixture)
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

    def test_wrapper_rejects_same_thread_previous_position_forgery(self) -> None:
        fixture = self.fixture()
        fixture["targets"][0]["expected_return_count"] = "2"
        fixture["targets"][0]["observed_return_count"] = "2"
        fixture["targets"][0]["observed_orphan_return_count"] = "1"
        fixture["targetSpecifications"][0]["expected_return_count"] = 2
        fixture["summary"]["raw_return_count"] = "2"
        fixture["summary"]["orphan_return_count"] = "1"
        fixture["events"] = [
            self.event(0, "call", 0),
            self.event(1, "return", None, decoded_return=True),
            self.event(2, "entry", 0),
            self.event(3, "return", 0, decoded_return=True),
        ]
        fixture["events"][2]["previous_position"] = fixture["events"][0][
            "position"
        ]
        fixture["invocations"][0]["entry_event_index"] = 2
        fixture["invocations"][0]["return_event_index"] = 3

        completed = self.run_relationship_guard(fixture)
        self.assertEqual(3, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("impossible same-thread chronology", completed.stdout)

        same_position = copy.deepcopy(fixture)
        same_position["events"][1]["position"] = same_position["events"][0][
            "position"
        ]
        same_position["events"][1]["previous_position"] = same_position["events"][
            0
        ]["previous_position"]
        completed_same = self.run_relationship_guard(same_position)
        self.assertEqual(
            3,
            completed_same.returncode,
            completed_same.stdout + completed_same.stderr,
        )
        self.assertIn("same-thread same-position evidence", completed_same.stdout)

    def test_wrapper_rejects_grouped_call_return_position_collision(self) -> None:
        fixture = self.fixture()
        target = fixture["targets"][0]
        target["expected_entry_count"] = None
        target["expected_call_count"] = None
        target["observed_entry_count"] = "2"
        target["observed_call_count"] = "2"
        specification = fixture["targetSpecifications"][0]
        specification["expected_entry_count"] = None
        specification["expected_call_count"] = None

        events = [
            self.event(0, "call", 0),
            self.event(1, "entry", 0),
            self.event(2, "call", 1),
            self.event(3, "entry", 2),
            self.event(4, "return", 0, decoded_return=True),
        ]
        for event in events[2:]:
            event["position"] = "0x1:0x3"
            event["previous_position"] = "0x1:0x2"
            event["pc"] = "0x401000"
            event["registers"]["eip"] = "0x401000"
        events[2]["fallthrough"] = "0x401005"
        events[2]["stack"]["hex"] = "05014000"
        events[3]["stack"]["hex"] = "05014000"
        events[4]["instruction_bytes"]["address"] = "0x401000"

        fixture["events"] = events
        fixture["invocations"][0]["return_event_index"] = 4
        fixture["invocations"].extend(
            [
                {
                    "invocation_index": 1,
                    "target_index": 0,
                    "unique_thread_id": "2",
                    "association_epoch": "0",
                    "call_event_index": 2,
                    "entry_event_index": None,
                    "return_event_index": None,
                    "grade": "CALL_ONLY",
                    "call_entry_checks_passed": False,
                    "return_checks_passed": False,
                    "gap_crossed": False,
                    "continuity_break_crossed": False,
                },
                {
                    "invocation_index": 2,
                    "target_index": 0,
                    "unique_thread_id": "2",
                    "association_epoch": "0",
                    "call_event_index": None,
                    "entry_event_index": 3,
                    "return_event_index": None,
                    "grade": "ENTRY_ONLY",
                    "call_entry_checks_passed": False,
                    "return_checks_passed": False,
                    "gap_crossed": False,
                    "continuity_break_crossed": False,
                },
            ]
        )

        completed = self.run_relationship_guard(fixture)
        self.assertEqual(3, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("same-thread same-position evidence", completed.stdout)

    def test_wrapper_rejects_raw_semantic_and_summary_forgery(self) -> None:
        decoded_lie = self.fixture()
        decoded_lie["events"][2]["decoded_near_return"] = False

        destination_lie = self.fixture()
        destination_lie["events"][2]["instruction_target"] = "0xDEADBEEF"
        destination_lie["events"][2]["stack"]["hex"] = "EFBEADDE"

        entry_position_lie = self.fixture()
        entry_position_lie["events"][1]["previous_position"] = "0x9:0x9"

        equal_call_entry_position = self.fixture()
        equal_call_entry_position["events"][1]["position"] = "0x1:0x1"

        equal_entry_return_position = self.fixture()
        equal_entry_return_position["events"][2]["position"] = "0x1:0x2"

        entry_identity_lie = self.fixture()
        entry_identity_lie["events"][1]["pc"] = "0x55DE94"
        entry_identity_lie["events"][1]["registers"]["eip"] = "0x55DE94"

        context_lie = self.fixture()
        context_lie["events"][0]["control_registers_valid"] = False

        target_flag_lie = self.fixture()
        target_flag_lie["targets"][0]["expectations_passed"] = False

        target_spec_lie = self.fixture()
        target_spec_lie["targets"][0]["expected_return_count"] = "999"

        gap_total_lie = self.fixture(degraded=True)
        gap_total_lie["gapSummary"]["total"] = "0"

        for name, fixture, expected in (
            ("decoded", decoded_lie, "decoded-return flag disagrees"),
            ("destination", destination_lie, "return flag disagrees"),
            ("entry-position", entry_position_lie, "previous position"),
            (
                "equal-call-entry",
                equal_call_entry_position,
                "same-thread same-position evidence",
            ),
            (
                "equal-entry-return",
                equal_entry_return_position,
                "same-thread same-position evidence",
            ),
            ("entry-identity", entry_identity_lie, "does not identify its selected entry"),
            ("context", context_lie, "context-derived flags disagree"),
            ("target-flag", target_flag_lie, "expectations flag disagrees"),
            ("target-spec", target_spec_lie, "snapshotted target table"),
            ("gap-total", gap_total_lie, "gap total disagrees"),
        ):
            with self.subTest(poison=name):
                completed = self.run_relationship_guard(fixture)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(expected, completed.stdout)

    def test_wrapper_recomputes_raw_context_and_gap_event_partitions(self) -> None:
        register_view_lie = self.fixture()
        register_view_lie["events"][0]["registers"]["eip"] = "0xDEADBEEF"

        context_flag_lie = self.fixture()
        context_flag_lie["events"][0]["context_flags"] = "0x0"

        gap_event_lie = self.fixture(degraded=True)
        gap_event_lie["gapSummary"]["event_KernelCall"] = "0"

        null_event_index = self.fixture()
        null_event_index["events"][0]["event_index"] = None

        event_order_lie = self.fixture()
        event_order_lie["events"][1]["position"] = "0x0:0x0"

        return_range_lie = self.fixture()
        return_range_lie["events"][2]["pc"] = "0x500000"
        return_range_lie["events"][2]["registers"]["eip"] = "0x500000"
        return_range_lie["events"][2]["instruction_bytes"]["address"] = "0x500000"

        for name, fixture, expected in (
            ("register-view", register_view_lie, "context-derived flags disagree"),
            ("context-flags", context_flag_lie, "context-derived flags disagree"),
            ("gap-event", gap_event_lie, "gap total disagrees with its event partition"),
            (
                "null-index",
                null_event_index,
                "must be one scalar non-negative Int32 JSON number",
            ),
            ("event-order", event_order_lie, "previous position"),
            ("return-range", return_range_lie, "outside its selected target range"),
        ):
            with self.subTest(poison=name):
                completed = self.run_relationship_guard(fixture)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(expected, completed.stdout)

    def test_wrapper_rejects_scalar_width_stack_and_chronology_forgery(self) -> None:
        zero_length_call = self.fixture()
        zero_length_call["events"][0]["fallthrough"] = "0x402000"
        zero_length_call["events"][0]["stack"]["hex"] = "00204000"
        zero_length_call["events"][1]["stack"]["hex"] = "00204000"
        zero_length_call["events"][2]["instruction_target"] = "0x402000"
        zero_length_call["events"][2]["stack"]["hex"] = "00204000"

        one_byte_call = self.fixture()
        one_byte_call["events"][0]["fallthrough"] = "0x402001"
        one_byte_call["events"][0]["stack"]["hex"] = "01204000"
        one_byte_call["events"][1]["stack"]["hex"] = "01204000"
        one_byte_call["events"][2]["instruction_target"] = "0x402001"
        one_byte_call["events"][2]["stack"]["hex"] = "01204000"

        non_return_payload = self.fixture()
        non_return_payload["events"][0]["decoded_near_return"] = True
        non_return_payload["events"][0]["instruction_bytes"] = {
            "address": "0x402000",
            "valid_bytes": 1,
            "query_valid": True,
            "hex": "C3",
        }

        oversized_return_payload = self.fixture()
        oversized_return_payload["events"][2]["instruction_bytes"][
            "valid_bytes"
        ] = 4
        oversized_return_payload["events"][2]["instruction_bytes"][
            "hex"
        ] = "C3909090"

        orphan_stack_address = self.fixture(degraded=True)
        orphan_stack_address["events"][2]["stack"]["address"] = "0x100000000"

        object_ranges = self.fixture()
        object_ranges["targets"][0]["ranges"] = object_ranges["targets"][0][
            "ranges"
        ][0]

        forged_edx_eax = self.fixture()
        forged_edx_eax["events"][0]["raw_edx_eax"] = "0x1"

        forged_basic_return = self.fixture()
        forged_basic_return["events"][0]["basic_return_value_untyped"] = "0x2"

        missing_eax = self.fixture()
        del missing_eax["events"][0]["registers"]["eax"]

        over_width_register = self.fixture()
        over_width_register["events"][0]["registers"]["ebx"] = "0x100000000"

        array_index = self.fixture()
        array_index["events"][0]["event_index"] = [0]

        nullable_array_index = self.fixture()
        nullable_array_index["events"][0]["invocation_index"] = [0]

        array_thread = self.fixture()
        array_thread["events"][0]["unique_thread_id"] = ["2"]

        empty_thread = self.fixture()
        empty_thread["invocations"][0]["unique_thread_id"] = ""

        oversized_stack = self.fixture()
        oversized_stack["events"][0]["stack"]["valid_bytes"] = 5
        oversized_stack["events"][0]["stack"]["hex"] = "0520400000"

        wrong_stack_request = self.fixture()
        wrong_stack_request["events"][0]["stack"]["requested_bytes"] = 8

        future_previous_position = self.fixture()
        future_previous_position["events"][0]["previous_position"] = "0x1:0x2"

        for name, fixture, expected in (
            ("zero-length-call", zero_length_call, "does not target its selected entry"),
            ("one-byte-call", one_byte_call, "does not target its selected entry"),
            ("non-return-payload", non_return_payload, "carries return-instruction evidence"),
            ("oversized-return", oversized_return_payload, "native three-byte bound"),
            ("orphan-stack", orphan_stack_address, "stack address disagrees"),
            ("object-ranges", object_ranges, "must be one JSON array"),
            ("raw-edx-eax", forged_edx_eax, "raw EDX:EAX disagrees"),
            ("basic-return", forged_basic_return, "disagrees with EAX"),
            ("missing-eax", missing_eax, "missing or unexpected x86 register"),
            ("over-width", over_width_register, "exceeds x86 width"),
            ("array-index", array_index, "one scalar JSON value"),
            ("nullable-array", nullable_array_index, "one scalar JSON value"),
            ("array-thread", array_thread, "one scalar JSON value"),
            ("empty-thread", empty_thread, "one unsigned decimal JSON string"),
            ("oversized-stack", oversized_stack, "stack extent disagrees"),
            ("wrong-stack-request", wrong_stack_request, "stack extent disagrees"),
            ("future-previous", future_previous_position, "previous position"),
        ):
            with self.subTest(poison=name):
                completed = self.run_relationship_guard(fixture)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(expected, completed.stdout)

    def test_wrapper_recomputes_required_call_entry_pairing(self) -> None:
        fixture = self.fixture()
        fixture["events"][0]["invocation_index"] = 0
        fixture["events"][1]["invocation_index"] = 1
        fixture["events"][2]["invocation_index"] = None
        fixture["invocations"] = [
            {
                "invocation_index": 0,
                "target_index": 0,
                "unique_thread_id": "2",
                "association_epoch": "0",
                "call_event_index": 0,
                "entry_event_index": None,
                "return_event_index": None,
                "grade": "CALL_ONLY",
                "call_entry_checks_passed": False,
                "return_checks_passed": False,
                "gap_crossed": False,
                "continuity_break_crossed": False,
            },
            {
                "invocation_index": 1,
                "target_index": 0,
                "unique_thread_id": "2",
                "association_epoch": "0",
                "call_event_index": None,
                "entry_event_index": 1,
                "return_event_index": None,
                "grade": "ENTRY_ONLY",
                "call_entry_checks_passed": False,
                "return_checks_passed": False,
                "gap_crossed": False,
                "continuity_break_crossed": False,
            },
        ]
        target = fixture["targets"][0]
        target["observed_call_entry_pair_count"] = "0"
        target["observed_validated_return_count"] = "0"
        target["observed_orphan_return_count"] = "1"
        target["observed_gap_free_envelope_count"] = "0"
        summary = fixture["summary"]
        summary["call_entry_pair_count"] = "0"
        summary["validated_return_count"] = "0"
        summary["orphan_return_count"] = "1"
        summary["gap_free_envelope_count"] = "0"
        # Deliberately retain the forged native summary claim.
        summary["pairing_expectations_passed"] = True

        completed = self.run_relationship_guard(fixture)
        self.assertEqual(3, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("pairing", completed.stdout)

    def test_wrapper_rejects_epoch_orphan_and_barrier_forgery(self) -> None:
        forged_epoch = self.fixture()
        forged_epoch["events"][2]["association_epoch"] = "1"
        forged_epoch["gapSummary"]["kind_unrecorded"] = "1"
        forged_epoch["summary"]["association_barrier_count"] = "1"
        forged_epoch["summary"]["final_association_epoch"] = "1"

        missing_orphan = self.fixture(degraded=True)
        missing_orphan["targets"][0]["observed_orphan_return_count"] = "0"
        missing_orphan["summary"]["orphan_return_count"] = "0"

        broken_barrier = self.fixture(degraded=True)
        broken_barrier["summary"]["association_barrier_count"] = "0"

        decreasing_epoch = self.fixture()
        decreasing_epoch["events"][1]["association_epoch"] = "1"

        for name, fixture, expected in (
            ("epoch", forged_epoch, "broken return backlink"),
            ("orphan", missing_orphan, "aggregate counts disagree"),
            ("barrier", broken_barrier, "association-barrier accounting"),
            ("decreasing", decreasing_epoch, "event epochs decrease"),
        ):
            with self.subTest(poison=name):
                completed = self.run_relationship_guard(fixture)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(expected, completed.stdout)

    def test_missing_output_exit_resolver_never_returns_success(self) -> None:
        command = (
            lift_function("Resolve-MissingCallContextExitCode", CALL_CONTEXT_WRAPPER)
            + "$result = [ordered]@{ "
            + "nonzero = Resolve-MissingCallContextExitCode 7; "
            + "silent = Resolve-MissingCallContextExitCode 0 }; "
            + "$result | ConvertTo-Json -Compress"
        )
        completed = subprocess.run(
            ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(7, result["nonzero"])
        self.assertEqual(12, result["silent"])

    def test_collector_failure_without_jsonl_publishes_blocked_boundary(self) -> None:
        system_root = pathlib.Path(os.environ.get("WINDIR", r"C:\Windows"))
        pe32_utility = system_root / "SysWOW64" / "where.exe"
        if not pe32_utility.is_file():
            self.skipTest(f"PE32 test utility not found: {pe32_utility}")

        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace_directory = root / "trace-input"
            trace_directory.mkdir()
            trace = trace_directory / "sample.run"
            trace.write_bytes(b"not-a-real-trace")

            target_directory = root / "target-input"
            target_directory.mkdir()
            target = target_directory / "BEA.exe"
            target.write_bytes(pe32_utility.read_bytes())

            targets = root / "targets.tsv"
            targets.write_text(
                "target_index\tentry_rva\trange_start_rva\t"
                "range_end_rva_exclusive\texpected_entry_count\t"
                "expected_call_count\texpected_return_count\n"
                "0\t0x1000\t0x1000\t0x1001\t0\t0\t0\n",
                encoding="utf-8",
            )

            tool_root = root / "fake-tool"
            tool_directory = tool_root / "bin"
            tool_directory.mkdir(parents=True)
            collector = tool_directory / "ttd_exec_coverage.exe"
            collector.write_bytes(pe32_utility.read_bytes())
            replay = tool_directory / "TTDReplay.dll"
            replay_cpu = tool_directory / "TTDReplayCPU.dll"
            replay.write_bytes(b"fake-replay")
            replay_cpu.write_bytes(b"fake-replay-cpu")

            def sha256(path: pathlib.Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest().upper()

            collector_sha = sha256(collector)
            build_receipt = {
                "schemaVersion": "bea-ttd-exec-coverage-build.v2",
                "collector": {"sha256": collector_sha},
                "runtime": {
                    "version": "test-only",
                    "replaySha256": sha256(replay),
                    "replayCpuSha256": sha256(replay_cpu),
                },
                "reproducibility": {
                    "buildCount": 2,
                    "byteIdentical": True,
                    "distinctOutputRoots": True,
                    "allSelfTestsPassed": True,
                    "pdbAlternatePath": "ttd_exec_coverage.pdb",
                    "isolatedBuilds": [
                        {
                            "root": "test-build-a",
                            "sha256": collector_sha,
                            "selfTest": "PASS",
                        },
                        {
                            "root": "test-build-b",
                            "sha256": collector_sha,
                            "selfTest": "PASS",
                        },
                    ],
                },
            }
            (tool_root / "build-receipt.json").write_text(
                json.dumps(build_receipt, indent=2) + "\n",
                encoding="utf-8",
            )

            output = root / "output"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(CALL_CONTEXT_WRAPPER),
                    "-TraceFile",
                    str(trace),
                    "-TargetExe",
                    str(target),
                    "-TargetsTsv",
                    str(targets),
                    "-OutputDirectory",
                    str(output),
                    "-Collector",
                    str(collector),
                    "-ModuleName",
                    "BEA.exe",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertFalse((output / "call-context.jsonl").exists())
            self.assertFalse((output / "READY").exists())
            self.assertTrue((output / "receipt.json").is_file())
            self.assertTrue((output / "manifest.json").is_file())

            receipt = json.loads((output / "receipt.json").read_text())
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual("BLOCKED", manifest["status"])
            self.assertFalse(receipt["readyEligible"])
            self.assertNotEqual(0, receipt["collectorExitCode"])
            self.assertEqual(receipt["collectorExitCode"], receipt["exitCode"])
            self.assertEqual(receipt["exitCode"], manifest["exitCode"])
            self.assertEqual(completed.returncode, receipt["exitCode"])
            self.assertIsNone(receipt["callContext"])
            self.assertIsNone(receipt["metadata"])
            self.assertIsNone(receipt["gapSummary"])
            self.assertIsNone(receipt["summary"])
            self.assertIsNone(manifest["artifacts"]["callContext"])
            self.assertIsNone(manifest["proof"])
            self.assertEqual(
                "call-context-jsonl-missing",
                receipt["failure"]["code"],
            )
            self.assertEqual(receipt["failure"], manifest["failure"])
            self.assertEqual(sha256(trace), receipt["trace"]["sha256"])
            self.assertEqual(sha256(target), receipt["target"]["sha256"])
            self.assertEqual(
                sha256(output / "receipt.json"),
                manifest["artifacts"]["receipt"]["sha256"],
            )

    def test_native_mode_stays_separate_from_coverage_mode(self) -> None:
        collector = read(COLLECTOR_SOURCE)
        wrapper = read(CALL_CONTEXT_WRAPPER)

        self.assertIn("AnalysisMode::CallContext", collector)
        self.assertIn("ReplaySegmentsSequentially", collector)
        self.assertIn("SetCallReturnCallback", collector)
        self.assertIn("AddMemoryWatchpoint", collector)
        self.assertIn("--mode', 'call-context'", wrapper)
        self.assertIn("bea-ttd-call-context-ready.v3", wrapper)
        self.assertIn("observed_orphan_return_count", wrapper)
        self.assertIn("association_barrier_count", wrapper)
        self.assertIn("final_association_epoch", wrapper)
        self.assertNotIn("--quarantine-counters", wrapper)


class TtdDataWriteRelationshipTests(unittest.TestCase):
    """Data-write READY rows must reproduce exact state transitions."""

    @staticmethod
    def memory(
        hex_value: str,
        *,
        position: str = "0x1:0x10",
        source_sequence: str = "0x1",
    ) -> dict:
        observation_sequence = position.split(":", 1)[0]
        return {
            "address": "0x89D950",
            "valid_bytes": 4,
            "range_count": 1,
            "single_range": True,
            "observation_position": position,
            "observation_sequence": observation_sequence,
            "source_sequence": source_sequence,
            "source_sequence_matches_observation": (
                source_sequence == observation_sequence
            ),
            "query_valid": True,
            "hex": hex_value,
        }

    @staticmethod
    def invalid_memory(position: str = "0x1:0xF") -> dict:
        observation_sequence = position.split(":", 1)[0]
        return {
            "address": "0x0",
            "valid_bytes": 0,
            "range_count": 0,
            "single_range": False,
            "observation_position": position,
            "observation_sequence": observation_sequence,
            "source_sequence": "0x0",
            "source_sequence_matches_observation": False,
            "query_valid": False,
            "hex": "",
        }

    @classmethod
    def event(cls, index: int, event_type: str, value: str) -> dict:
        return {
            "event_index": index,
            "event_type": event_type,
            "target_index": 0,
            "pair_index": 0,
            "intersecting_target_count": 1,
            "continuity_epoch": "0",
            "position": "0x1:0x10",
            "previous_position": "0x1:0xF",
            "unique_thread_id": "2",
            "os_thread_id": "3",
            "pc": "0x401000",
            "sp": "0x1000",
            "fp": "0x1100",
            "access_address": "0x89D950",
            "access_size": "4",
            "context_flags": "0x1002F",
            "control_registers_valid": True,
            "integer_registers_valid": True,
            "register_views_agree": True,
            "registers": {
                "eax": "0x1",
                "ebx": "0x2",
                "ecx": "0x3",
                "edx": "0x4",
                "esi": "0x5",
                "edi": "0x6",
                "ebp": "0x1100",
                "esp": "0x1000",
                "eip": "0x401000",
                "eflags": "0x202",
            },
            "observed_memory": cls.memory(value),
        }

    @classmethod
    def fixture(cls, *, redundant: bool = False) -> dict:
        after = "00000000" if redundant else "17000000"
        return {
            "targets": [
                {
                    "target_index": 0,
                    "address": "0x89D950",
                    "size": 4,
                    "expected_overwrite_count": "1",
                    "expected_write_count": "1",
                    "observed_overwrite_count": "1",
                    "observed_write_count": "1",
                    "observed_pair_count": "1",
                    "initial_memory": cls.memory(
                        "00000000", position="0x1:0xF"
                    ),
                    "final_memory": cls.memory(after),
                    "evidence_grade": "WATCHPOINT_CHAIN_CLOSED",
                    "initial_sequence_matched": True,
                    "final_sequence_matched": True,
                    "event_memory_sequence_sourced": True,
                    "transition_chain_closed": True,
                    "evidence_checks_passed": True,
                    "expectations_passed": True,
                }
            ],
            "events": [
                cls.event(0, "Overwrite", "00000000"),
                cls.event(1, "Write", after),
            ],
            "pairs": [
                {
                    "pair_index": 0,
                    "target_index": 0,
                    "overwrite_event_index": 0,
                    "write_event_index": 1,
                    "continuity_epoch": "0",
                    "grade": "STRUCTURAL_WRITE_PAIR",
                    "checks_passed": True,
                    "changed": not redundant,
                }
            ],
            "summary": {
                "event_count": "2",
                "pair_count": "1",
                "orphan_event_count": "0",
                "pairing_complete": True,
            },
        }

    def run_relationship_guard(
        self,
        fixture: dict,
        *,
        allow_invalid_endpoints: bool = False,
        allow_invalid_event_memory: bool = False,
    ) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_path = pathlib.Path(temporary) / "fixture.json"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            wrapper_literal = str(DATA_WRITES_WRAPPER).replace("'", "''")
            fixture_literal = str(fixture_path).replace("'", "''")
            command = (
                "$ErrorActionPreference = 'Stop'; $errors = @(); "
                "$ast = [System.Management.Automation.Language.Parser]::ParseFile("
                f"'{wrapper_literal}', [ref]$null, [ref]$errors); "
                "if ($errors.Count) { Write-Output 'wrapper parse failed'; exit 4 }; "
                "$names = @('Get-RequiredProperty','Get-RequiredBoolean',"
                "'Get-RequiredUInt64','Get-OptionalUInt64','Get-NullableIndex',"
                "'Assert-HexText','Convert-HexUInt64','Convert-TtdPosition',"
                "'Compare-TtdPosition','Assert-TtdPosition','Assert-MemoryImage',"
                "'Assert-DataWriteRelationships'); foreach ($name in $names) { "
                "$node = $ast.Find({ param($candidate) $candidate -is "
                "[System.Management.Automation.Language.FunctionDefinitionAst] "
                "-and $candidate.Name -eq $name }, $true); if ($null -eq $node) { "
                "Write-Output \"missing $name\"; exit 4 }; . ([scriptblock]::Create("
                "$node.Extent.Text)) }; "
                f"$fixture = Get-Content -Raw -LiteralPath '{fixture_literal}' | "
                "ConvertFrom-Json -Depth 30; try { $result = "
                "Assert-DataWriteRelationships -Targets @($fixture.targets) "
                "-Events @($fixture.events) -Pairs @($fixture.pairs) "
                "-Summary $fixture.summary -ActualFrom '0x1:0xF' "
                "-FinalPosition '0x1:0x10' "
                + ("-AllowInvalidEndpoints " if allow_invalid_endpoints else "")
                + (
                    "-AllowInvalidEventMemory "
                    if allow_invalid_event_memory
                    else ""
                )
                + "; $result | ConvertTo-Json -Compress } "
                "catch { Write-Output $_.Exception.Message; exit 3 }; exit 0"
            )
            return subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_wrapper_accepts_changed_and_redundant_pairs(self) -> None:
        for redundant in (False, True):
            with self.subTest(redundant=redundant):
                completed = self.run_relationship_guard(
                    self.fixture(redundant=redundant)
                )
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                result = json.loads(completed.stdout.strip().splitlines()[-1])
                self.assertEqual(1, result["pairCount"])
                self.assertEqual(0, result["orphanEventCount"])
                self.assertTrue(result["pairingComplete"])
                self.assertTrue(result["endpointQueriesValid"])
                self.assertTrue(result["targetEvidencePassed"])

    def test_wrapper_preserves_blocked_raw_rows_when_endpoints_are_invalid(self) -> None:
        fixture = self.fixture()
        fixture["targets"][0]["initial_memory"] = self.invalid_memory()

        rejected = self.run_relationship_guard(fixture)
        self.assertEqual(3, rejected.returncode, rejected.stdout + rejected.stderr)
        self.assertIn("not a complete single-range", rejected.stdout)

        fixture["targets"][0]["initial_sequence_matched"] = False
        accepted = self.run_relationship_guard(
            fixture,
            allow_invalid_endpoints=True,
        )
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        result = json.loads(accepted.stdout.strip().splitlines()[-1])
        self.assertFalse(result["endpointQueriesValid"])
        self.assertEqual(1, result["pairCount"])
        self.assertTrue(result["targetEvidencePassed"])

    def test_positive_chain_does_not_depend_on_cursor_endpoint_sources(self) -> None:
        fixture = self.fixture()
        for endpoint in (
            fixture["targets"][0]["initial_memory"],
            fixture["targets"][0]["final_memory"],
        ):
            endpoint["source_sequence"] = "0x0"
            endpoint["source_sequence_matches_observation"] = False
        fixture["targets"][0]["initial_sequence_matched"] = False
        fixture["targets"][0]["final_sequence_matched"] = False

        completed = self.run_relationship_guard(fixture)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertTrue(result["endpointQueriesValid"])
        self.assertTrue(result["targetEvidencePassed"])
        self.assertEqual(1, result["pairCount"])

    def test_non_sequence_sourced_event_is_preserved_but_not_promotable(self) -> None:
        fixture = self.fixture()
        fixture["events"][0]["observed_memory"]["source_sequence"] = "0x0"
        fixture["events"][0]["observed_memory"][
            "source_sequence_matches_observation"
        ] = False
        target = fixture["targets"][0]
        target["event_memory_sequence_sourced"] = False
        target["transition_chain_closed"] = False
        target["evidence_checks_passed"] = False
        target["evidence_grade"] = "BLOCKED"

        completed = self.run_relationship_guard(fixture)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(1, result["pairCount"])
        self.assertTrue(result["pairingComplete"])
        self.assertFalse(result["targetEvidencePassed"])

    def test_wrapper_rejects_forged_pair_relationships(self) -> None:
        broken_backlink = self.fixture()
        broken_backlink["events"][1]["pair_index"] = 7
        wrong_pc = self.fixture()
        wrong_pc["events"][1]["pc"] = "0x401001"
        false_changed = self.fixture()
        false_changed["pairs"][0]["changed"] = False
        broken_chain = self.fixture()
        broken_chain["targets"][0]["transition_chain_closed"] = False

        for name, fixture, expected in (
            ("backlink", broken_backlink, "broken event backlinks"),
            ("pc", wrong_pc, "different pc boundary"),
            ("changed", false_changed, "changed flag disagrees"),
            ("chain", broken_chain, "evidence grade disagrees"),
        ):
            with self.subTest(poison=name):
                completed = self.run_relationship_guard(fixture)
                self.assertEqual(
                    3,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )
                self.assertIn(expected, completed.stdout)

    def test_frozen_target_table_is_reparsed_and_bound_to_json_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            table = root / "targets.tsv"
            table.write_text(
                "target_index\taddress\tsize\texpected_overwrite_count\t"
                "expected_write_count\n0\t0x89D950\t4\t1\t1\n",
                encoding="utf-8",
            )
            fixture = self.fixture()
            targets_path = root / "targets.json"

            lifted = "".join(
                lift_function(name, DATA_WRITES_WRAPPER)
                for name in (
                    "Get-RequiredProperty",
                    "Get-RequiredBoolean",
                    "Get-RequiredUInt64",
                    "Get-OptionalUInt64",
                    "Convert-HexUInt64",
                    "Convert-UnsignedLiteral",
                    "Read-DataWriteTargetTable",
                    "Assert-TargetTableMatchesRows",
                )
            )

            def run(targets: list[dict]) -> subprocess.CompletedProcess:
                targets_path.write_text(json.dumps(targets), encoding="utf-8")
                command = (
                    "$ErrorActionPreference='Stop'; "
                    + lifted
                    + f"$table=Read-DataWriteTargetTable '{str(table).replace("'", "''")}'; "
                    + f"$targets=Get-Content -Raw -LiteralPath '{str(targets_path).replace("'", "''")}' | ConvertFrom-Json; "
                    + "try { $result=Assert-TargetTableMatchesRows $table @($targets); "
                    + "$result | ConvertTo-Json -Compress } catch { "
                    + "Write-Output $_.Exception.Message; exit 3 }"
                )
                return subprocess.run(
                    ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )

            good = run(fixture["targets"])
            self.assertEqual(0, good.returncode, good.stdout + good.stderr)
            self.assertEqual("true", good.stdout.strip().lower())

            wrong_address = copy.deepcopy(fixture["targets"])
            wrong_address[0]["address"] = "0x89D954"
            rejected = run(wrong_address)
            self.assertEqual(3, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("disagrees", rejected.stdout)

            wrong_expectation = copy.deepcopy(fixture["targets"])
            wrong_expectation[0]["expected_write_count"] = "2"
            rejected = run(wrong_expectation)
            self.assertEqual(3, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("disagrees", rejected.stdout)

    def test_gap_continuity_and_callback_arithmetic_is_reconciled(self) -> None:
        event_names = (
            "SyntheticSequence",
            "CodeCacheFlush",
            "PreAtomicOperation",
            "PotentialAtomicCollision",
            "EtwEvent",
            "DebugBreak",
            "FastFail",
            "KernelCall",
            "SyntheticFallback",
            "ExceptionDispatch",
            "UnknownInstruction",
            "ThreadSuspended",
            "SListRollback",
            "SyncPoint",
            "PauseEmulation",
            "StopEmulation",
            "Throttled",
        )
        gap = {
            "total": "0",
            "kind_no_gap": "0",
            "kind_context_switch": "0",
            "kind_unrecorded": "0",
            "kind_large": "0",
            **{f"event_{name}": "0" for name in event_names},
        }
        summary = {
            "nontrivial_gap_count": "0",
            "continuity_break_count": "0",
            "truncated": False,
            "callback_failed": False,
            "callback_hits": "2",
        }

        with tempfile.TemporaryDirectory() as temporary:
            fixture_path = pathlib.Path(temporary) / "fixture.json"
            lifted = "".join(
                lift_function(name, DATA_WRITES_WRAPPER)
                for name in (
                    "Get-RequiredProperty",
                    "Get-RequiredBoolean",
                    "Get-RequiredUInt64",
                    "Assert-DataWriteGapAccounting",
                )
            )

            def run(gap_row: dict, summary_row: dict, break_count: int = 0):
                fixture_path.write_text(
                    json.dumps(
                        {
                            "gap": gap_row,
                            "summary": summary_row,
                            "events": [{}, {}],
                            "breaks": [{} for _ in range(break_count)],
                            "relationships": {"allEventEpochsZero": True},
                        }
                    ),
                    encoding="utf-8",
                )
                literal = str(fixture_path).replace("'", "''")
                command = (
                    "$ErrorActionPreference='Stop'; "
                    + lifted
                    + f"$f=Get-Content -Raw -LiteralPath '{literal}' | ConvertFrom-Json; "
                    + "try { Assert-DataWriteGapAccounting $f.gap $f.summary "
                    + "@($f.events) @($f.breaks) $f.relationships | "
                    + "ConvertTo-Json -Compress } catch { "
                    + "Write-Output $_.Exception.Message; exit 3 }"
                )
                return subprocess.run(
                    ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )

            good = run(gap, summary)
            self.assertEqual(0, good.returncode, good.stdout + good.stderr)

            poisoned_gap = copy.deepcopy(gap)
            poisoned_gap["kind_unrecorded"] = "1"
            rejected = run(poisoned_gap, summary)
            self.assertEqual(3, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("gap-kind counts", rejected.stdout)

            poisoned_summary = copy.deepcopy(summary)
            poisoned_summary["callback_hits"] = "3"
            rejected = run(gap, poisoned_summary)
            self.assertEqual(3, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("callback count", rejected.stdout)

            poisoned_summary = copy.deepcopy(summary)
            poisoned_summary["continuity_break_count"] = "1"
            rejected = run(gap, poisoned_summary)
            self.assertEqual(3, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("continuity-break rows", rejected.stdout)

    def test_missing_output_exit_resolver_never_returns_success(self) -> None:
        command = (
            lift_function("Resolve-MissingDataWriteExitCode", DATA_WRITES_WRAPPER)
            + "$result = [ordered]@{ nonzero = "
            + "Resolve-MissingDataWriteExitCode 7; silent = "
            + "Resolve-MissingDataWriteExitCode 0 }; "
            + "$result | ConvertTo-Json -Compress"
        )
        completed = subprocess.run(
            ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(7, result["nonzero"])
        self.assertEqual(12, result["silent"])

    def test_native_mode_and_wrapper_are_separate_and_fail_closed(self) -> None:
        collector = read(COLLECTOR_SOURCE)
        wrapper = read(DATA_WRITES_WRAPPER)

        self.assertIn("AnalysisMode::DataWrites", collector)
        self.assertIn("DataAccessMask::Write | DataAccessMask::Overwrite", collector)
        self.assertIn("ReplaySegmentsSequentially", collector)
        self.assertIn("bea.ttd.data-writes.v3", collector)
        self.assertIn("--mode', 'data-writes'", wrapper)
        self.assertIn("bea-ttd-data-writes-ready.v3", wrapper)
        self.assertIn("instrument-source", wrapper)
        self.assertIn("wrapperSha256=$wrapperFacts.sha256", wrapper)
        self.assertIn("collectorCppSha256=$collectorCppFacts.sha256", wrapper)
        self.assertIn("collectorProjectSha256=$collectorProjectFacts.sha256", wrapper)
        self.assertNotIn("SetCallReturnCallback", wrapper)
        self.assertNotIn("--quarantine-counters", wrapper)
        self.assertIn("DataWriteHistoryIsGapFree(", collector)
        self.assertIn("recorder.NontrivialGapCount()", collector)
        self.assertIn("recorder.ContinuityBreakCount()", collector)
        self.assertIn("DataWriteMemorySourceSequenceMatches", collector)
        self.assertIn("$nontrivialGapCount -eq 0", wrapper)
        self.assertIn("$continuityBreakCount -eq 0", wrapper)
        self.assertIn("WATCHPOINT_CHAIN_CLOSED", wrapper)
        self.assertIn("nontrivialGapCount=$nontrivialGapCount", wrapper)
        self.assertIn("continuityBreakCount=$continuityBreakCount", wrapper)
        # Gap-aware witnessed grade is a distinct marker, never gap-free READY.
        self.assertIn("READY_WITNESSED_WRITES", wrapper)
        self.assertIn("Assert-DataWriteWitnessedWrites", wrapper)
        self.assertIn(
            "bea.ttd.data-writes.witnessed-writes-with-gap-ledger.v1", wrapper
        )
        self.assertIn("writer_pc_outside_body", wrapper)
        self.assertIn(
            "writer_body_ranges_required_when_events_present", wrapper
        )

    def test_witnessed_writes_grade_accepts_gapped_in_body_and_poisons(self) -> None:
        """Witnessed grade tolerates gaps; poisons out-of-body PC and missing ranges."""

        def lift_witnessed() -> str:
            return (
                lift_function("Get-RequiredProperty", DATA_WRITES_WRAPPER)
                + lift_function("Get-RequiredBoolean", DATA_WRITES_WRAPPER)
                + lift_function("Get-RequiredUInt64", DATA_WRITES_WRAPPER)
                + lift_function("Convert-HexUInt64", DATA_WRITES_WRAPPER)
                + lift_function("Assert-HexText", DATA_WRITES_WRAPPER)
                + lift_function(
                    "Get-DataWritesWitnessedPromotionPolicy", DATA_WRITES_WRAPPER
                )
                + lift_function("Parse-WriterBodyRanges", DATA_WRITES_WRAPPER)
                + lift_function("Test-PcInWriterBodyRanges", DATA_WRITES_WRAPPER)
                + lift_function("Assert-DataWriteWitnessedWrites", DATA_WRITES_WRAPPER)
            )

        def run_grade(
            *,
            pc: str = "0x40A944",
            ranges: list[str] | None = None,
            nontrivial: int = 5,
            continuity: int = 9,
            expectations: bool = True,
            evidence: bool = True,
            events: int = 2,
            epochs_zero: bool | None = None,
        ) -> subprocess.CompletedProcess[str]:
            if ranges is None:
                ranges = ["0x40A890:0x40AC25"]
            if epochs_zero is None:
                epochs_zero = events == 0 and nontrivial == 0 and continuity == 0
            range_ps = (
                "@(" + ",".join(f"'{r}'" for r in ranges) + ")"
                if ranges
                else "@()"
            )
            event_block = ""
            for i in range(events):
                event_block += (
                    f"$events += [pscustomobject]@{{ pc = '{pc}'; "
                    f"event_index = {i}; event_type = "
                    f"'{'Overwrite' if i % 2 == 0 else 'Write'}' }}; "
                )
            command = (
                lift_witnessed()
                + "$events = @(); "
                + event_block
                + "$pairs = @([pscustomobject]@{ pair_index = 0 }); "
                + "$summary = [pscustomobject]@{ truncated = $false; "
                + "callback_failed = $false }; "
                + "$gapAccounting = [ordered]@{ reconciled = $true }; "
                + "$relationships = [ordered]@{ targetEvidencePassed = "
                + ("$true" if evidence else "$false")
                + "; pairingComplete = $true; allEventEpochsZero = "
                + ("$true" if epochs_zero else "$false")
                + " }; "
                + f"$ranges = Parse-WriterBodyRanges -Ranges {range_ps}; "
                + "Assert-DataWriteWitnessedWrites -Events $events "
                + "-Pairs $pairs -Summary $summary "
                + "-GapAccounting $gapAccounting -Relationships $relationships "
                + "-ReplayComplete $true -ExactReplayWindow $true "
                + f"-ExpectationsPassed ${'true' if expectations else 'false'} "
                + "-CountersSane $true -OrderingValid $true "
                + "-ContextsValid $true -PairingValid $true "
                + "-SnapshotQueriesValid $true -AmbiguousCallbacks 0 "
                + f"-NontrivialGapCount ([uint64]{nontrivial}) "
                + f"-ContinuityBreakCount ([uint64]{continuity}) "
                + "-WriterBodyRanges $ranges | ConvertTo-Json -Compress -Depth 6"
            )
            return subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        good = run_grade()
        self.assertEqual(0, good.returncode, good.stdout + good.stderr)
        good_json = json.loads(good.stdout.strip().splitlines()[-1])
        self.assertTrue(good_json["eligible"])
        self.assertEqual(
            "bea.ttd.data-writes.witnessed-writes-with-gap-ledger.v1",
            good_json["promotionPolicy"],
        )
        self.assertFalse(good_json["wouldAlsoBeGapFree"])

        # Poison: writer PC outside Damage body.
        poisoned_pc = run_grade(pc="0x401000")
        self.assertEqual(0, poisoned_pc.returncode, poisoned_pc.stdout + poisoned_pc.stderr)
        bad_pc = json.loads(poisoned_pc.stdout.strip().splitlines()[-1])
        self.assertFalse(bad_pc["eligible"])
        self.assertIn("writer_pc_outside_body", bad_pc["reasons"])

        # Poison: events present but no body ranges.
        missing_ranges = run_grade(ranges=[])
        self.assertEqual(
            0, missing_ranges.returncode, missing_ranges.stdout + missing_ranges.stderr
        )
        bad_ranges = json.loads(missing_ranges.stdout.strip().splitlines()[-1])
        self.assertFalse(bad_ranges["eligible"])
        self.assertIn(
            "writer_body_ranges_required_when_events_present", bad_ranges["reasons"]
        )

        # Zero-event control: ranges optional; gaps zero still can be witnessed.
        zero = run_grade(events=0, ranges=[], nontrivial=0, continuity=0)
        self.assertEqual(0, zero.returncode, zero.stdout + zero.stderr)
        zero_json = json.loads(zero.stdout.strip().splitlines()[-1])
        self.assertTrue(zero_json["eligible"])
        self.assertTrue(zero_json["wouldAlsoBeGapFree"])

        # Poison: expectations failed (control field write etc.).
        bad_exp = run_grade(expectations=False)
        self.assertEqual(0, bad_exp.returncode, bad_exp.stdout + bad_exp.stderr)
        bad_exp_json = json.loads(bad_exp.stdout.strip().splitlines()[-1])
        self.assertFalse(bad_exp_json["eligible"])
        self.assertIn("expectations_failed", bad_exp_json["reasons"])


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

    def test_parity_lab_ingest_honours_the_adjudication_the_way_it_honours_quarantine(
        self,
    ) -> None:
        # #153.  Ingest reads the wrapper's verdict, surfaces it in its own
        # column, and refuses a claim that is absent, undeclared, or
        # self-contradictory - the same shape as the #149 quarantine.
        ingest = read(ROOT / "tools" / "parity_lab.py")

        self.assertIn("stop_reason_adjudicated INTEGER NOT NULL", ingest)
        self.assertIn(
            'TTD_ADJUDICABLE_STOP_REASONS = frozenset({"Thread"})', ingest
        )
        self.assertIn("no wrapper adjudication receipt", ingest)
        self.assertIn("was not declared from a recorder ", ingest)
        self.assertIn("contradicts its own coverage", ingest)
        self.assertIn("contradicts its own receipt", ingest)
        # Consumers read the adjudication, never replayComplete - which stays
        # honestly false on an alive-at-stop trace.
        self.assertIn(
            'health = "COMPLETE" if (replay_complete or stop_reason_adjudicated)'
            ' else "ERROR"',
            ingest,
        )
        # The collector's own verdict survives beside the resolved one.
        self.assertIn('"collectorChecksPassed": collector_checks_passed', ingest)
        self.assertIn('"collectorExitCode": payload["collectorExitCode"]', ingest)


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
$PSNativeCommandUseErrorActionPreference = $false
$utf8 = [System.Text.UTF8Encoding]::new($false)
$level = Split-Path -Leaf $OutputDirectory
$plan = Get-Content -Raw -LiteralPath $env:FAKE_PLAN | ConvertFrom-Json
$planned = 0
$entry = $plan.PSObject.Properties[$level]
if ($null -ne $entry) { $planned = [int]$entry.Value }
# FAKE_ADJUDICATED names the levels whose collector REFUSED the run (raw 10)
# and whose terminal-stop adjudication then resolved it to $planned.
$adjudicated = $false
if (-not [string]::IsNullOrWhiteSpace($env:FAKE_ADJUDICATED)) {
    $adjudicated = (@($env:FAKE_ADJUDICATED -split ',') -ccontains $level)
}
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
$collectorExit = $(
    if ($adjudicated) { 10 }
    elseif ($planned -eq 11) { 11 }
    elseif ($planned -eq 0) { 0 }
    else { 10 })
# THE COLLECTOR RUN.  A real native command, so $LASTEXITCODE is left the way
# the real wrapper leaves it - and nothing after this point touches it.
$comSpec = if ([string]::IsNullOrWhiteSpace($env:ComSpec)) { 'cmd.exe' } else { $env:ComSpec }
& $comSpec /c "exit $collectorExit"
[System.IO.Directory]::CreateDirectory($OutputDirectory) | Out-Null
$quarantined = ($planned -eq 11)
$receipt = [ordered]@{
    schemaVersion = 'bea-ttd-exec-coverage-receipt.v2'
    collectorExitCode = $collectorExit
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
# A code no branch of the wrapper can explain, for proving the cross-check
# still bites once the receipt - not $LASTEXITCODE - decides the status.
if ($env:FAKE_STRAY_EXIT -eq $level) { & $comSpec /c "exit 3" }
if ($planned -ne 0) { exit $planned }
"""


class TtdCoverageCampaignContractTests(unittest.TestCase):
    """The campaign runner's receipt gating, resume, and immutability rules.

    Driven entirely against mock trace directories and a fake coverage wrapper:
    no real trace is opened, and the 4.2-hour campaign is never a prerequisite
    for proving that the runner reads the right receipt and refuses to retry.
    """

    LEVELS = ("level100", "level700", "level742")

    @staticmethod
    def fake_trace_hash(level: str) -> str:
        """A 64-hex stand-in.  The shape is load-bearing.

        The runner now refuses a recorder receipt whose traceSha256 is not a
        real hash, so a fixture that writes 'FAKELEVEL100' would be exercising
        the refusal instead of the path under test.
        """

        return (level.upper().encode("ascii").hex() + "0" * 64)[:64].upper()

    def build_sandbox(
        self,
        root: pathlib.Path,
        outcomes: dict[str, str] | None = None,
        levels: tuple[str, ...] | None = None,
        descending_sizes: bool = False,
        hash_states: dict[str, str] | None = None,
    ) -> dict[str, pathlib.Path]:
        outcomes = outcomes or {}
        hash_states = hash_states or {}
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
            receipt = {
                "schemaVersion": "ttd-record-receipt.v3",
                "name": name,
                "guestOutcome": outcomes.get(level, "alive-at-stop"),
                "guestRanCleanly": True,
                "traceSha256": self.fake_trace_hash(level),
                "traceHashState": "present",
                "hashDeferred": None,
                "traceBytes": 16 + index,
            }
            state = hash_states.get(level)
            if state == "deferred":
                receipt["traceSha256"] = None
                receipt["traceHashState"] = "deferred"
                receipt["hashDeferred"] = {
                    "reason": "trace-file-locked-after-completion",
                    "traceFile": str(directory / f"{name}.run"),
                    "traceBytes": 16 + index,
                    "timeoutSeconds": 300,
                    "waitedSeconds": 300.0,
                }
            elif state == "contradictory":
                # A hash AND a deferral: the receipt disagrees with itself.
                receipt["traceHashState"] = "deferred"
            elif state == "absent":
                receipt["traceSha256"] = None
                receipt["traceHashState"] = "no-trace"
            (directory / "receipt.json").write_text(
                json.dumps(receipt), encoding="utf-8"
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
        adjudicated: list[str] | None = None,
        stray_exit_for: str = "",
        extra: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        paths["plan"].write_text(json.dumps(plan or {}), encoding="utf-8")
        environment = dict(os.environ)
        environment["FAKE_LOG"] = str(paths["log"])
        environment["FAKE_PLAN"] = str(paths["plan"])
        environment["FAKE_NO_RECEIPT"] = no_receipt_for
        environment["FAKE_ADJUDICATED"] = ",".join(adjudicated or [])
        environment["FAKE_STRAY_EXIT"] = stray_exit_for
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

    def test_an_adjudicated_thread_stop_is_ok_not_a_failed_trace(self) -> None:
        """#155.  The receipt's resolved exit decides; $LASTEXITCODE cannot.

        The wrapper is invoked IN-PROCESS, and an in-process script only sets
        $LASTEXITCODE by calling `exit`.  On a clean adjudicated run it falls
        off the end, leaving the collector EXE's RAW 10 behind while the
        receipt carries the resolved 0.  The first full campaign labelled 8 of
        66 sound traces 'failed' on exactly that disagreement.
        """
        adjudicated = "level-opening-3m-v1-level742"
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            completed = self.run_campaign(paths, adjudicated=[adjudicated])
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )

            record = self.trace_records(paths["output"])[adjudicated]
            self.assertEqual("ok", record["status"], record["reason"])
            self.assertEqual("", record["reason"])
            # The pair that disagrees, recorded rather than hidden.
            self.assertEqual(0, record["exitCode"])
            self.assertEqual(10, record["collectorExitCode"])
            self.assertEqual(10, record["observedProcessExit"])
            # And the trace's evidence is logged in full, not truncated to a
            # failure line: the run really did produce ranges.
            self.assertTrue(record["stopReasonAdjudicated"])
            self.assertTrue(record["terminalStopAccepted"])
            self.assertTrue(record["markerAssertionsPassed"])
            self.assertFalse(record["replayComplete"])
            self.assertEqual("Thread", record["stopReason"])
            self.assertEqual(6815, record["rangeCount"])
            self.assertEqual("552196", record["coveredBytes"])

    def test_an_adjudicated_quarantine_still_agrees_on_the_resolved_code(
        self,
    ) -> None:
        # Collector 10, adjudicated, counters quarantined -> resolved 11, and
        # the wrapper DOES call exit for a non-zero resolved code, so the
        # observed value is 11 rather than the raw 10.  Both halves of
        # Get-ExpectedProcessExit are exercised.
        adjudicated = "level-opening-3m-v1-level742"
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            completed = self.run_campaign(
                paths, plan={adjudicated: 11}, adjudicated=[adjudicated]
            )
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )
            record = self.trace_records(paths["output"])[adjudicated]
            self.assertEqual("ok", record["status"], record["reason"])
            self.assertEqual(11, record["exitCode"])
            self.assertEqual(10, record["collectorExitCode"])
            self.assertEqual(11, record["observedProcessExit"])
            self.assertTrue(record["countersQuarantined"])

    def test_a_process_exit_no_branch_explains_still_fails_the_trace(
        self,
    ) -> None:
        # The cross-check was loosened, not removed.  Here the wrapper leaves 3
        # behind while its receipt claims a clean 0 from a collector that also
        # exited 0 - a value neither branch can produce - and the trace fails.
        stray = "level-opening-3m-v1-level700"
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            completed = self.run_campaign(paths, stray_exit_for=stray)
            self.assertEqual(1, completed.returncode, completed.stdout)
            records = self.trace_records(paths["output"])
            record = records[stray]
            self.assertEqual("failed", record["status"])
            self.assertEqual(3, record["observedProcessExit"])
            self.assertIn("observed process exit 3", record["reason"])
            # One bad trace is still not a campaign abort.
            self.assertEqual(
                "ok", records["level-opening-3m-v1-level742"]["status"]
            )

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

    def test_a_deferred_recorder_hash_blocks_the_level_it_belongs_to(self) -> None:
        # The receipt now EXISTS for a locked-out trace, which is the fix.  What
        # must not follow is coverage being collected and published against a
        # trace whose own receipt cannot name it.
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(
                pathlib.Path(temporary), hash_states={"level100": "deferred"}
            )
            completed = self.run_campaign(paths)
            self.assertEqual(1, completed.returncode, completed.stdout)
            records = self.trace_records(paths["output"])
            blocked = records["level-opening-3m-v1-level100"]
            self.assertEqual("blocked", blocked["status"])
            self.assertEqual("deferred", blocked["recordedTraceHashState"])
            self.assertIsNone(blocked["recordedTraceSha256"])
            # The block is one command from being cleared, and says which.
            self.assertIn("-HashOnly", blocked["reason"])

            # Blocked, not aborted, and the wrapper was never invoked for it.
            self.assertEqual("ok", records["level-opening-3m-v1-level742"]["status"])
            calls = [row["level"] for row in self.invocations(paths)]
            self.assertNotIn("level-opening-3m-v1-level100", calls)
            self.assertEqual(2, len(calls))

    def test_a_self_contradicting_recorder_hash_is_blocked_too(self) -> None:
        for state, fragment in (
            ("contradictory", "contradicts itself"),
            ("absent", "no usable traceSha256"),
        ):
            with self.subTest(receipt=state), tempfile.TemporaryDirectory() as t:
                paths = self.build_sandbox(
                    pathlib.Path(t), hash_states={"level100": state}
                )
                completed = self.run_campaign(paths)
                self.assertEqual(1, completed.returncode, completed.stdout)
                records = self.trace_records(paths["output"])
                blocked = records["level-opening-3m-v1-level100"]
                self.assertEqual("blocked", blocked["status"])
                self.assertIn(fragment, blocked["reason"])
                self.assertIsNone(blocked["recordedTraceSha256"])

    def test_a_usable_recorder_hash_is_recorded_normalised(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            completed = self.run_campaign(paths)
            self.assertEqual(0, completed.returncode, completed.stdout)
            record = self.trace_records(paths["output"])[
                "level-opening-3m-v1-level100"
            ]
            self.assertEqual("present", record["recordedTraceHashState"])
            self.assertEqual(
                self.fake_trace_hash("level100"), record["recordedTraceSha256"]
            )

    def test_a_level_already_collected_is_not_re_blocked_by_a_later_deferral(
        self,
    ) -> None:
        # The gate gates a FRESH collection.  A level whose coverage was already
        # produced keeps its result: re-litigating a finished run on the state of
        # a receipt read afterwards would throw away good evidence.
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            first = self.run_campaign(paths)
            self.assertEqual(0, first.returncode, first.stdout)

            receipt_path = (
                paths["traces"] / "level-opening-3m-v1-level100" / "receipt.json"
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["traceSha256"] = None
            receipt["traceHashState"] = "deferred"
            receipt["hashDeferred"] = {"reason": "trace-file-locked-after-completion"}
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

            second = self.run_campaign(paths)
            self.assertEqual(0, second.returncode, second.stdout)
            record = self.trace_records(paths["output"])[
                "level-opening-3m-v1-level100"
            ]
            self.assertEqual("skipped", record["status"])
            self.assertEqual("deferred", record["recordedTraceHashState"])

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

    def test_rebuilding_the_log_re_derives_every_line_from_the_receipts(
        self,
    ) -> None:
        # The log is derived data.  When its labels are wrong the fix is to
        # re-derive all of them from the receipts, which is why the rebuild
        # needs neither the wrapper nor the target: it opens no trace.
        adjudicated = "level-opening-3m-v1-level742"
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            first = self.run_campaign(paths, adjudicated=[adjudicated])
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            collected = len(self.invocations(paths))

            # Put the #155 mislabel back into the log by hand, so the rebuild
            # has something wrong to correct.
            rows = self.campaign_log(paths["output"])
            for row in rows:
                if row.get("level") == adjudicated:
                    row["status"] = "failed"
                    row["exitCode"] = 10
                    row["reason"] = (
                        "receipt exitCode 0 disagrees with the observed "
                        "process exit 10"
                    )
            (paths["output"] / "campaign-log.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )
            paths["wrapper"].unlink()
            paths["target"].unlink()

            rebuilt = self.run_campaign(
                paths, extra=["-RebuildLogFromReceipts"]
            )
            self.assertEqual(
                0, rebuilt.returncode, rebuilt.stdout + rebuilt.stderr
            )
            # Not one trace was replayed again.
            self.assertEqual(collected, len(self.invocations(paths)))

            records = self.trace_records(paths["output"])
            self.assertEqual(3, len(records))
            for level, row in records.items():
                self.assertEqual("ok", row["status"], level)
                self.assertEqual("", row["reason"])
                self.assertTrue(row["rebuiltFromReceipt"])
                self.assertEqual(6815, row["rangeCount"])
                # The runner's own observations survive the re-derivation.
                self.assertIsNotNone(row["wallSeconds"])
                self.assertIn("density", row)
            self.assertEqual(0, records[adjudicated]["exitCode"])
            self.assertEqual(10, records[adjudicated]["collectorExitCode"])

            summary = [
                row
                for row in self.campaign_log(paths["output"])
                if row.get("kind") == "campaign-summary"
            ]
            self.assertEqual(1, len(summary))
            self.assertEqual("rebuild-from-receipts", summary[0]["mode"])
            self.assertEqual(3, summary[0]["ok"])
            self.assertEqual(0, summary[0]["failed"])

            # The superseded log is moved aside, never edited away: if the
            # re-derivation is itself wrong, the old labels still prove it.
            superseded = sorted(
                paths["output"].glob("campaign-log.superseded-*.jsonl")
            )
            self.assertEqual(1, len(superseded))
            self.assertIn(
                "disagrees with the observed",
                superseded[0].read_text(encoding="utf-8"),
            )

    def test_a_rebuild_reports_a_level_that_was_never_collected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.build_sandbox(pathlib.Path(temporary))
            self.run_campaign(paths, max_traces=1)
            rebuilt = self.run_campaign(
                paths, extra=["-RebuildLogFromReceipts"]
            )
            self.assertEqual(1, rebuilt.returncode, rebuilt.stdout)
            records = self.trace_records(paths["output"])
            self.assertEqual(1, len(self.invocations(paths)))
            blocked = [
                row for row in records.values() if row["status"] == "blocked"
            ]
            self.assertEqual(2, len(blocked))
            for row in blocked:
                self.assertIn("no coverage output directory", row["reason"])

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

        # #155: the receipt decides the status, and $LASTEXITCODE is only
        # cross-checked against the code that can actually reach it.  The raw
        # collector exit and the wrapper's resolved exit are not that pair.
        self.assertIn("function Get-ExpectedProcessExit {", campaign)
        self.assertIn("THE RECEIPT DECIDES THE STATUS", campaign)
        self.assertNotIn("if ($receiptExit -ne $observedExit) {", campaign)
        # And the log is regenerated from receipts rather than edited.
        self.assertIn("[switch]$RebuildLogFromReceipts", campaign)
        self.assertIn("campaign-log.superseded-", campaign)

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


class TtdHashDeferralContractTests(unittest.TestCase):
    """A finished trace must never be lost to a failed hash.

    Measured 2026-08-02: takes 1 and 2 of level521-native-20260802-0018 finished
    tracing, wrote both completion markers, and were then thrown away by a FIXED
    180 s unlock wait that expired while TTD still held the 3.19 GB and 3.53 GB
    files on the USB-attached G:.  Both receipts had to be reconstructed by hand.
    Take 4 of the same session, 13.5 GB, hashed fine - so this is a race, not a
    size threshold, and raising the constant would not have been a fix.
    """

    LOCK_TIMEOUT_SECONDS = 2

    # Sizes that actually occurred, so the scaling is judged against the run it
    # was written for rather than against round numbers.
    TAKE1_BYTES = 3187671040
    TAKE4_BYTES = 13500000000

    def lift(self, names: tuple[str, ...], body: str) -> subprocess.CompletedProcess:
        command = "$ErrorActionPreference = 'Stop'; Set-StrictMode -Version Latest; "
        for name in names:
            command += lift_function(name, RECORDER)
        command += body
        return subprocess.run(
            ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def budget(self, trace_bytes: int, extra: str = "") -> int:
        completed = self.lift(
            ("Get-TraceUnlockTimeoutSeconds",),
            f"Write-Output (Get-TraceUnlockTimeoutSeconds -TraceBytes {trace_bytes}"
            f"{extra})",
        )
        self.assertEqual(
            0, completed.returncode, completed.stdout + completed.stderr
        )
        return int(completed.stdout.strip())

    def test_the_unlock_budget_scales_with_the_artefact(self) -> None:
        floor = self.budget(0)
        take1 = self.budget(self.TAKE1_BYTES)
        take4 = self.budget(self.TAKE4_BYTES)

        # A 40x size range cannot share one number.  This is the whole defect.
        self.assertGreater(take1, floor)
        self.assertGreater(take4, take1)

        # And it is generous where the old constant was not: take1 died at 180 s.
        self.assertGreater(take1, 180)
        self.assertGreaterEqual(floor, 180)

        # Monotone, so a bigger trace is never given a smaller budget.
        ladder = [self.budget(size) for size in (0, 1 << 20, 1 << 30, 8 << 30)]
        self.assertEqual(ladder, sorted(ladder))

    def test_the_budget_has_a_floor_and_a_cap(self) -> None:
        # A tiny trace gets essentially the fixed finalisation allowance: the
        # per-GiB term contributes nothing measurable below a GiB ...
        self.assertLessEqual(self.budget(1024) - self.budget(0), 1)
        # ... and an absurd one is capped, so a genuinely stuck writer is still
        # reportable rather than an unbounded hang.
        self.assertEqual(self.budget(1 << 50), self.budget(1 << 51))
        self.assertLessEqual(self.budget(1 << 50), 3600)

    def test_the_budget_refuses_incoherent_policy(self) -> None:
        for extra in (
            " -FloorSeconds 600 -MaxSeconds 300",
            " -FloorSeconds 0",
            " -SecondsPerGiB -1",
        ):
            with self.subTest(policy=extra):
                completed = self.lift(
                    ("Get-TraceUnlockTimeoutSeconds",),
                    "try { Get-TraceUnlockTimeoutSeconds -TraceBytes 1024"
                    + extra
                    + "; Write-Output 'ACCEPTED' } catch { Write-Output 'REFUSED' }",
                )
                self.assertIn("REFUSED", completed.stdout)

    def test_a_locked_trace_is_reported_not_thrown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trace = pathlib.Path(temporary) / "locked.run"
            trace.write_bytes(b"T" * 4096)
            literal = str(trace).replace("'", "''")
            # A real sharing violation: the handle denies read sharing for the
            # whole call, exactly as TTD's writer does while it finalises.
            completed = self.lift(
                ("Wait-TtdTraceUnlock",),
                "$held = [IO.File]::Open('"
                + literal
                + "', [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, "
                "[IO.FileShare]::None); "
                "try { $result = Wait-TtdTraceUnlock -Path '"
                + literal
                + f"' -TimeoutSeconds {self.LOCK_TIMEOUT_SECONDS} "
                "-PollMilliseconds 100 } finally { $held.Dispose() }; "
                "Write-Output ($result | ConvertTo-Json -Compress)",
            )
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )
            result = json.loads(completed.stdout)
            self.assertFalse(result["unlocked"])
            self.assertGreaterEqual(
                result["waitedSeconds"], self.LOCK_TIMEOUT_SECONDS
            )
            self.assertEqual(self.LOCK_TIMEOUT_SECONDS, result["timeoutSeconds"])
            self.assertTrue(result["lastError"])

    def test_an_unlocked_trace_returns_at_once_despite_a_huge_budget(self) -> None:
        # The generous deadline must cost nothing on the common case: the poll
        # returns the instant the handle is free, so a small trace is not made
        # to wait for a budget sized for a 13 GB one.
        with tempfile.TemporaryDirectory() as temporary:
            trace = pathlib.Path(temporary) / "free.run"
            trace.write_bytes(b"T" * 4096)
            literal = str(trace).replace("'", "''")
            completed = self.lift(
                ("Wait-TtdTraceUnlock",),
                "$result = Wait-TtdTraceUnlock -Path '"
                + literal
                + "' -TimeoutSeconds 3600; "
                "Write-Output ($result | ConvertTo-Json -Compress)",
            )
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )
            result = json.loads(completed.stdout)
            self.assertTrue(result["unlocked"])
            self.assertLess(result["waitedSeconds"], 5)

    def test_completion_needs_both_of_ttds_own_markers(self) -> None:
        # Verbatim tail of the take-1 .out file, which is the evidence that
        # licensed reconstructing that receipt by hand.
        real_tail = (
            "Tracing started at: Sun Aug  2 00:19:30 2026 (UTC)`n"
            "Simulation time of '' (x86): 58594ms.`n"
            "Tracing completed at: Sun Aug  2 00:20:29 2026 (UTC)`n"
            "Trace dumped to G:\\bea-ttd\\take1\\take1.run"
        )
        cases = {
            "both markers (real take-1 tail)": (real_tail, True),
            "completed only": ("Tracing completed at: Sun Aug  2", False),
            "dumped only": ("Trace dumped to G:\\x.run", False),
            "neither": ("Initializing Time Travel Debugging", False),
            "empty": ("", False),
        }
        for label, (text, expected) in cases.items():
            with self.subTest(out=label):
                completed = self.lift(
                    ("Get-TtdCompletionMarkers",),
                    '$markers = Get-TtdCompletionMarkers -OutText "'
                    + text
                    + '"; Write-Output ($markers | ConvertTo-Json -Compress)',
                )
                self.assertEqual(
                    0, completed.returncode, completed.stdout + completed.stderr
                )
                markers = json.loads(completed.stdout)
                self.assertEqual(expected, markers["traceFinalised"])

    def test_the_recorder_defers_the_hash_instead_of_discarding_the_receipt(
        self,
    ) -> None:
        recorder = read(RECORDER)

        # The fixed wait that cost two receipts is gone, in both its forms.
        self.assertNotIn("(Get-Date).AddSeconds(180)", recorder)
        self.assertNotIn("still locked 180 s after tracing completed", recorder)

        # The budget is computed from the artefact ...
        self.assertIn("Get-TraceUnlockTimeoutSeconds `", recorder)
        self.assertIn("-TraceBytes $final", recorder)

        # ... and expiring it writes a deferred receipt rather than throwing.
        self.assertIn("elseif ($completionMarkers.traceFinalised) {", recorder)
        self.assertIn("$traceHashState = 'deferred'", recorder)
        self.assertIn("$hashDeferred = New-TtdHashDeferral `", recorder)
        self.assertIn("traceHashState       = $traceHashState", recorder)
        self.assertIn("hashDeferred         = $hashDeferred", recorder)

        # The deferral is LICENSED BY EVIDENCE.  A locked trace with no
        # completion markers still refuses to write anything - and the refusal
        # must be a Fail, not a warning.  Asserting the message alone would be
        # satisfied by code that prints it and carries on.
        self.assertIn("cannot be certified complete and no receipt is written", recorder)
        self.assertIn(
            "        Fail (\n"
            '            "TTD trace file was still locked after '
            '$($unlock.waitedSeconds) s of a " +',
            recorder,
        )

        # Degraded, not clean, and not a failure: its own exit code.
        self.assertIn("if ($traceHashState -ceq 'deferred') {", recorder)
        self.assertIn("exit 8", recorder)

        # The deferral branch is reached only after the unlocked branch, so a
        # trace that CAN be hashed always is.
        self.assertLess(
            recorder.index("$traceHashState = 'present'"),
            recorder.index("$traceHashState = 'deferred'"),
        )

    def test_a_deferral_block_names_its_reason_and_its_repair(self) -> None:
        completed = self.lift(
            ("New-TtdHashDeferral", "Get-TtdCompletionMarkers"),
            '$markers = Get-TtdCompletionMarkers -OutText "Tracing completed at: x'
            '`nTrace dumped to y"; '
            "$block = New-TtdHashDeferral "
            "-Reason 'trace-file-locked-after-completion' "
            "-TraceFile 'G:\\bea-ttd\\t\\t.run' -TraceBytes 3187671040 "
            "-TimeoutSeconds 657 -WaitedSeconds 657.4 -Markers $markers "
            "-OutFile 'G:\\bea-ttd\\t\\t.out' -Detail 'used by another process' "
            "-RepairCommand 'pwsh -File ttd_record.ps1 -HashOnly'; "
            "Write-Output ($block | ConvertTo-Json -Compress -Depth 6)",
        )
        self.assertEqual(
            0, completed.returncode, completed.stdout + completed.stderr
        )
        block = json.loads(completed.stdout)
        self.assertEqual("trace-file-locked-after-completion", block["reason"])
        self.assertEqual(3187671040, block["traceBytes"])
        self.assertEqual(657, block["timeoutSeconds"])
        self.assertIn("-HashOnly", block["repairCommand"])
        self.assertTrue(block["completionEvidence"]["tracingCompleted"])
        self.assertTrue(block["completionEvidence"]["traceDumped"])
        # The block must say, in the artefact itself, that its null is not a
        # hash.  A consumer author who reads only the receipt still learns it.
        self.assertIn("MUST NOT be read as a match", block["consumerContract"])


class TtdReceiptRepairModeContractTests(unittest.TestCase):
    """`-HashOnly` closes a deferral without re-recording, and never lies.

    The maintainer had to do this by hand on 2026-08-02 for
    G:\\bea-ttd\\level521-native-20260802-0018-take1 and -take2, whose receipts
    carry a _RECONSTRUCTED block.  Repair mode produces the equivalent
    honestly - and refuses the one operation that would destroy evidence:
    overwriting a hash that was actually measured.
    """

    REAL_HASH = "94032E1AC72BDAFBDE3B1726C05326709DA4AD1FA24762899A3353203A743EEB"

    def build(
        self,
        root: pathlib.Path,
        *,
        state: str = "deferred",
        declared_bytes: int | None = None,
        payload: bytes = b"trace bytes",
    ) -> tuple[pathlib.Path, pathlib.Path]:
        directory = root / "take1"
        directory.mkdir(parents=True)
        trace = directory / "take1.run"
        trace.write_bytes(payload)
        receipt = {
            "schemaVersion": "ttd-record-receipt.v3",
            "guestOutcome": "alive-at-stop",
            "guestRanCleanly": True,
            "name": "take1",
            "traceFile": str(trace),
            "traceBytes": (
                len(payload) if declared_bytes is None else declared_bytes
            ),
            "traceSha256": None,
            "traceHashState": "deferred",
            "hashDeferred": {
                "reason": "trace-file-locked-after-completion",
                "traceFile": str(trace),
                "traceBytes": len(payload),
                "timeoutSeconds": 657,
                "waitedSeconds": 657.4,
                "completionEvidence": {
                    "tracingCompleted": True,
                    "traceDumped": True,
                    "guestExitObserved": False,
                },
            },
            "traceGrew": True,
        }
        if state == "hashed":
            receipt["traceSha256"] = self.REAL_HASH
            receipt["traceHashState"] = "present"
            receipt["hashDeferred"] = None
        elif state == "contradictory":
            receipt["traceSha256"] = self.REAL_HASH
        elif state == "undeclared":
            receipt["traceHashState"] = "no-trace"
            receipt["hashDeferred"] = None
        path = directory / "receipt.json"
        path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return directory, path

    def repair(self, directory: pathlib.Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "pwsh",
                "-NoLogo",
                "-NoProfile",
                "-File",
                str(RECORDER),
                "-HashOnly",
                "-TraceDirectory",
                str(directory),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_repair_completes_a_deferred_receipt_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory, receipt_path = self.build(pathlib.Path(temporary))
            expected = (
                hashlib.sha256((directory / "take1.run").read_bytes())
                .hexdigest()
                .upper()
            )
            completed = self.repair(directory)
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
            self.assertEqual(expected, receipt["traceSha256"])
            self.assertEqual("present", receipt["traceHashState"])
            self.assertIsNone(receipt["hashDeferred"])
            # The deferral is superseded, not erased: the receipt keeps saying
            # its hash was taken after the fact.
            self.assertEqual(
                "trace-file-locked-after-completion",
                receipt["hashRepaired"]["supersededDeferral"]["reason"],
            )
            self.assertIn("PARTIAL", receipt["hashRepaired"]["provenance"])
            self.assertIn("-HashOnly", receipt["hashRepaired"]["tool"])

    def test_repair_refuses_to_overwrite_a_measured_hash(self) -> None:
        # THE ONE OPERATION THAT DESTROYS EVIDENCE.  A hash taken at capture
        # time binds the receipt to the bytes TTD wrote; replacing it with one
        # taken now would silently upgrade a weaker claim into a stronger one.
        with tempfile.TemporaryDirectory() as temporary:
            directory, receipt_path = self.build(
                pathlib.Path(temporary), state="hashed"
            )
            before = receipt_path.read_bytes()
            completed = self.repair(directory)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn(
                "already carries a real trace",
                completed.stdout + completed.stderr,
            )
            self.assertEqual(before, receipt_path.read_bytes())

    def test_repair_refuses_a_receipt_that_never_declared_a_deferral(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory, receipt_path = self.build(
                pathlib.Path(temporary), state="undeclared"
            )
            before = receipt_path.read_bytes()
            completed = self.repair(directory)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn(
                "will not manufacture provenance",
                completed.stdout + completed.stderr,
            )
            self.assertEqual(before, receipt_path.read_bytes())

    def test_repair_refuses_a_receipt_that_contradicts_itself(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory, receipt_path = self.build(
                pathlib.Path(temporary), state="contradictory"
            )
            before = receipt_path.read_bytes()
            completed = self.repair(directory)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("contradicts itself", completed.stdout + completed.stderr)
            self.assertEqual(before, receipt_path.read_bytes())

    def test_repair_refuses_a_trace_that_is_not_the_one_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory, receipt_path = self.build(
                pathlib.Path(temporary), declared_bytes=999999
            )
            before = receipt_path.read_bytes()
            completed = self.repair(directory)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn(
                "Trace size changed since the deferral",
                completed.stdout + completed.stderr,
            )
            self.assertEqual(before, receipt_path.read_bytes())

    def test_repair_leaves_the_receipt_deferred_when_the_trace_is_still_locked(
        self,
    ) -> None:
        # Repair is retryable.  A failed attempt must not consume the deferral.
        with tempfile.TemporaryDirectory() as temporary:
            directory, receipt_path = self.build(pathlib.Path(temporary))
            before = receipt_path.read_bytes()
            literal = str(directory / "take1.run").replace("'", "''")
            command = (
                "$held = [IO.File]::Open('"
                + literal
                + "', [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, "
                "[IO.FileShare]::None); "
                "try { & '"
                + str(RECORDER).replace("'", "''")
                + "' -HashOnly -TraceDirectory '"
                + str(directory).replace("'", "''")
                + "' -UnlockFloorSeconds 1 -UnlockMaxSeconds 2 "
                "-UnlockSecondsPerGiB 0 } "
                "catch { Write-Output \"REFUSED: $($_.Exception.Message)\" } "
                "finally { $held.Dispose() }"
            )
            completed = subprocess.run(
                ["pwsh", "-NoLogo", "-NoProfile", "-Command", command],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertIn("STILL locked", completed.stdout + completed.stderr)
            self.assertEqual(before, receipt_path.read_bytes())


class TtdDeferredReceiptConsumerTests(unittest.TestCase):
    """Every consumer that needs a hash refuses the deferred receipt.

    A null that is merely ignored is worse than the crash it replaced: the
    trace would rejoin the pipeline carrying an unbindable claim.
    """

    def receipt(self, root: pathlib.Path, **overrides) -> pathlib.Path:
        trace = root / "synthetic.run"
        trace.write_bytes(b"T" * 321)
        payload = {
            "schemaVersion": "ttd-record-receipt.v3",
            "name": "synthetic",
            "targetSha256": "A" * 64,
            "traceFile": str(trace),
            "traceBytes": 321,
            "traceSha256": None,
            "traceHashState": "deferred",
            "hashDeferred": {
                "reason": "trace-file-locked-after-completion",
                "timeoutSeconds": 657,
            },
            "recorderVersion": "test",
            "guestOutcome": "alive-at-stop",
            "guestRanCleanly": True,
            "recordedAtUtc": "2026-08-02T00:20:28Z",
        }
        payload.update(overrides)
        path = root / "receipt.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def ingest(self, path: pathlib.Path) -> dict:
        connection = parity_lab.open_database(":memory:")
        try:
            summary, _ = parity_lab.ingest_ttd_receipt(connection, path)
            return summary
        finally:
            connection.close()

    def test_parity_lab_ingests_a_deferred_receipt_but_never_calls_it_complete(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.receipt(pathlib.Path(temporary))
            summary = self.ingest(path)
            # Ingested - the trace does not drop out of the pipeline ...
            self.assertEqual("alive-at-stop", summary["guestOutcome"])
            self.assertTrue(summary["traceSizeMatches"])
            # ... but its null is not a hash, and cannot become one.
            self.assertIsNone(summary["traceSha256"])
            self.assertFalse(summary["traceHashDeclared"])
            self.assertFalse(summary["traceHashMatches"])
            self.assertTrue(summary["traceHashDeferred"])
            self.assertEqual("deferred", summary["traceHashState"])
            self.assertEqual(
                "trace-file-locked-after-completion",
                summary["traceHashDeferredReason"],
            )
            self.assertIsNone(summary["traceArtifact"])
            self.assertEqual("PARTIAL", summary["health"])

    def test_parity_lab_still_refuses_a_v3_receipt_whose_hash_just_vanished(
        self,
    ) -> None:
        # The deferral must be DECLARED.  Silence is still malformed.
        with tempfile.TemporaryDirectory() as temporary:
            path = self.receipt(
                pathlib.Path(temporary), traceHashState=None, hashDeferred=None
            )
            with self.assertRaises(parity_lab.ParityLabError) as caught:
                self.ingest(path)
            self.assertIn("lacks a valid traceSha256", str(caught.exception))

    def test_parity_lab_refuses_a_receipt_that_contradicts_itself(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            trace_hash = (
                hashlib.sha256(b"T" * 321).hexdigest().upper()
            )
            for label, overrides, expected in (
                (
                    "deferred with a hash",
                    {"traceSha256": trace_hash},
                    "declares a deferred trace hash and carries one too",
                ),
                (
                    "deferred with no block",
                    {"hashDeferred": None},
                    "defers its trace hash without a hashDeferred block",
                ),
                (
                    "block with no declaration",
                    {"traceSha256": trace_hash, "traceHashState": "present"},
                    "carries a hashDeferred block without",
                ),
            ):
                with self.subTest(receipt=label):
                    path = self.receipt(root, **overrides)
                    with self.assertRaises(parity_lab.ParityLabError) as caught:
                        self.ingest(path)
                    self.assertIn(expected, str(caught.exception))

    def test_a_hashed_receipt_is_still_complete(self) -> None:
        # The guard must not degrade the healthy case it was added beside.
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            path = self.receipt(
                root,
                traceSha256=hashlib.sha256(b"T" * 321).hexdigest().upper(),
                traceHashState="present",
                hashDeferred=None,
            )
            summary = self.ingest(path)
            self.assertTrue(summary["traceHashMatches"])
            self.assertFalse(summary["traceHashDeferred"])
            self.assertEqual("COMPLETE", summary["health"])


if __name__ == "__main__":
    unittest.main()
