#!/usr/bin/env python3
"""Run every host-supported tools/ test suite and report one summary.

Every supported suite runs, even after a failure. Windows-dependent suites
are explicitly reported as skipped on other hosts, never counted as passes.
Output is streamed as it happens - a summary
is a navigation aid, not a replacement for the failing suite's own report - and
the exit code is non-zero when any suite failed, exactly as the chain was.

Order is the chain's original order and is not a dependency: the suites are
independent, and running them in one process would be wrong, because several
of them compile executables and spawn PowerShell.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import pathlib
import subprocess
import sys
import time
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]

# One entry per command the gate used to chain.  Paths are repository-relative
# and are resolved against ROOT so the gate behaves the same from any cwd.
SUITES: tuple[tuple[str, ...], ...] = (
    ("tools/enumerate_test_assertions.py", "--self-test"),
    ("tools/check_installed_game_claims.py", "--self-test"),
    ("tools/check_installed_game_claims.py", "--check"),
    ("tools/check_registered_screenshots.py", "--self-test"),
    ("tools/check_registered_screenshots.py", "--check"),
    ("tools/enumerate_test_assertions.py", "--check"),
    ("tools/aya_archive_inventory_tests.py",),
    ("tools/cmsh_animation_usage_census_tests.py",),
    ("tools/aya_texture_fidelity_census_tests.py",),
    ("tools/export_game_assets_tests.py",),
    ("rebuild/tools/materialize_retail_assets_tests.py",),
    ("tools/require_windows_host_tests.py",),
    ("tools/runtime_process_identity_probe.py",),
    ("tools/runtime_proof_lab_hygiene_test.py",),
    ("tools/send_game_window_input_probe.py",),
    ("tools/start_cdb_server_probe.py",),
    ("tools/score_frontend_capture_tests.py",),
    ("tools/check_region_overlap_tests.py",),
    ("tools/check_region_overlap.py",),
    ("tools/lab_quarantine_tests.py",),
    ("tools/ghidra_project_backup_tests.py",),
    ("tools/ghidra_promotion_scratch_proof_tests.py",),
    ("tools/ghidra_function_envelope_proof_tests.py",),
    ("tools/ghidra_crt_canary_refutation_tests.py",),
    ("tools/ghidra_cohort_replay_routing_tests.py",),
    ("tools/ghidra_function_batch_proof_tests.py",),
    ("tools/ghidra_global_init_full520_proof_tests.py",),
    ("tools/ghidra_global_init515_live_promotion_tests.py",),
    ("tools/ghidra_text_gap_boundary_mutator_tests.py",),
    ("tools/ghidra_text_gap_boundary_scratch_authority_tests.py",),
    ("tools/ghidra_external_table_gap_boundary_mutator_tests.py",),
    ("tools/ghidra_external_table_gap_boundary_scratch_authority_tests.py",),
    ("tools/ghidra_external_table_gap_boundary_live_authority_tests.py",),
    ("tools/ghidra_jpeg_callback_boundary_mutator_tests.py",),
    ("tools/ghidra_jpeg_callback_boundary_scratch_authority_tests.py",),
    ("tools/ghidra_jpeg_callback_boundary_live_authority_tests.py",),
    ("tools/ghidra_d3dx_gap_boundary_mutator_tests.py",),
    ("tools/ghidra_d3dx_gap_boundary_scratch_authority_tests.py",),
    ("tools/ghidra_d3dx_gap_boundary_current_preparation_authority_tests.py",),
    ("tools/ghidra_d3dx_gap_boundary_live_authority_tests.py",),
    ("tools/ghidra_crt_p0_boundary_mutator_tests.py",),
    ("tools/ghidra_crt_p0_boundary_scratch_authority_tests.py",),
    ("tools/ghidra_crt_p0_boundary_v2_mutator_tests.py",),
    ("tools/ghidra_crt_p0_boundary_scratch_authority_v2_tests.py",),
    ("tools/ghidra_crt_p0_boundary_live_preparation_tests.py",),
    ("tools/ghidra_crt_p0_boundary_live_preparation_v2_tests.py",),
    ("tools/ghidra_crt_p0_boundary_live_authority_v2_tests.py",),
    ("tools/ghidra_crt_eh_parent_range_mutator_tests.py",),
    ("tools/ghidra_crt_eh_parent_range_scratch_authority_tests.py",),
    ("tools/ghidra_crt_eh_parent_range_live_authority_tests.py",),
    ("tools/re_pc_function_body_fragments_tests.py",),
    ("tools/ghidra_function_fragment_range_mutator_tests.py",),
    ("tools/ghidra_function_fragment_range_scratch_authority_tests.py",),
    ("tools/ghidra_function_fragment_range_live_authority_tests.py",),
    ("tools/ttd_pipeline_contract_tests.py",),
    ("tools/ttd_coverage_index_tests.py",),
    ("tools/parity_lab_tests.py",),
    ("tools/export_packets_tests.py",),
    ("tools/re_coverage_ledger_tests.py",),
    ("tools/contract_coverage_tests.py",),
    ("tools/contract_factory_validate_tests.py",),
    ("tools/re_campaign_tests.py",),
    ("tools/re_campaign_historical_ghidra_consumer_tests.py",),
    ("tools/re_campaign_gen32_host_attestation_tests.py",),
    ("tools/re_campaign_historical_source_projection_v2_tests.py",),
    ("tools/re_evidence_register_export_tests.py",),
    ("tools/re_level521_damage_writes_tests.py",),
    ("tools/re_applydamage_primary_reproof_tests.py",),
    ("tools/re_cexplosion_hit_runtime_tests.py",),
    ("tools/re_cround_move_runtime_tests.py",),
    ("tools/re_cround_handle_event_runtime_tests.py",),
    ("tools/re_tokenarchive_dispatch_reproof_tests.py",),
    ("tools/re_mission_native_setpos_reproof_tests.py",),
    ("tools/re_mission_native_unsetobjective_reproof_tests.py",),
    ("tools/re_text_residual_boundary_tests.py",),
    ("tools/re_text_gap_boundary_prep_tests.py",),
    ("tools/re_crt_function_strata_tests.py",),
    ("tools/re_source_unit_census_tests.py",),
    ("tools/re_source_allocation_census_tests.py",),
    ("tools/re_pc_native_source_coordinates_v3_tests.py",),
    ("tools/re_pc_native_source_coordinates_v3_tests.py", "--prove-can-fail"),
    ("tools/re_memory_dump_census_tests.py",),
    ("tools/re_msl_logger_census_tests.py",),
    ("tools/re_console_output_topology_tests.py",),
    ("tools/re_global_init515_campaign_lineage_tests.py",),
    ("tools/re_rtti_vtables_tests.py",),
    ("tools/re_cmech_profile_field_tests.py",),
    ("tools/re_binary_strings_tests.py",),
    # Name-align plates (Gen34–38): keep regression guards in the sweep (Opus).
    ("tools/re_fun_trivial_template_name_align_tests.py",),
    ("tools/re_fun_native_name_align_tests.py",),
    ("tools/probe/test_probe_author.py",),
    ("tools/probe/probe_harness_tests.py",),
    ("tools/probe/probe_harness_tests.py", "--prove-can-fail"),
    ("tools/probe/refute_tests.py",),
    ("tools/probe/compare.py", "--self-check"),
    ("tools/probe/select_probe.py", "--self-check"),
    ("tools/worldheaders_decode.py", "--self-test"),
)

WINDOWS_ONLY = {
    "tools/runtime_process_identity_probe.py": "copies and runs Windows cmd.exe fixtures",
    "tools/send_game_window_input_probe.py": "exercises Windows window/input APIs",
    "tools/start_cdb_server_probe.py": "requires Windows .NET Framework csc.exe",
    "tools/ttd_pipeline_contract_tests.py": "requires powershell.exe, py and cmd.exe fixtures",
}


def format_summary(results: list[dict[str, object]]) -> str:
    """One line per suite, failures repeated at the end so none can be missed."""

    width = max((len(str(row["name"])) for row in results), default=0)
    lines = ["", "tools test summary", "=" * (width + 26)]
    for row in results:
        lines.append(
            "{status:4}  {name:<{width}}  exit={exit:<4} {seconds:>7.1f}s".format(
                status="SKIP" if row.get("skipReason") else "PASS" if row["exitCode"] == 0 else "FAIL",
                name=str(row["name"]),
                width=width,
                exit=str(row["exitCode"]),
                seconds=float(str(row["seconds"])),
            )
        )
        if row.get("skipReason"):
            lines.append(f"      {row['skipReason']}")
    failed = [row for row in results if row["exitCode"] not in (None, 0)]
    skipped = [row for row in results if row.get("skipReason")]
    passed = sum(row["exitCode"] == 0 for row in results)
    lines.append(
        f"{passed} passed, {len(failed)} failed, "
        f"{len(results) - len(skipped)} run"
        + (f", {len(skipped)} skipped (Windows required)" if skipped else "")
    )
    if failed:
        lines.append("failed suites:")
        lines.extend(f"  {row['name']} (exit {row['exitCode']})" for row in failed)
    return "\n".join(lines) + "\n"


def run_suite(command: tuple[str, ...]) -> dict[str, object]:
    """Run one suite to completion, streaming its own output as it goes."""

    arguments = [sys.executable, str(ROOT / command[0]), *command[1:]]
    started = time.monotonic()
    completed = subprocess.run(arguments, cwd=ROOT, check=False)
    return {
        "name": " ".join(command),
        "exitCode": completed.returncode,
        "seconds": time.monotonic() - started,
    }


def run_all(suites: tuple[tuple[str, ...], ...] = SUITES, *, host_os: str | None = None) -> int:
    host_os = os.name if host_os is None else host_os
    results: list[dict[str, object]] = []
    for index, command in enumerate(suites, start=1):
        print(
            f"\n[{index}/{len(suites)}] {' '.join(command)}",
            flush=True,
        )
        if host_os != "nt" and command[0] in WINDOWS_ONLY:
            reason = "Windows host required: " + WINDOWS_ONLY[command[0]]
            print("SKIP " + reason, flush=True)
            results.append({"name": " ".join(command), "exitCode": None,
                            "seconds": 0.0, "skipReason": reason})
        else:
            results.append(run_suite(command))
    print(format_summary(results), flush=True)
    return 1 if any(row["exitCode"] not in (None, 0) for row in results) else 0


class RunToolTestsSelfTest(unittest.TestCase):
    """The property that matters: a failure never stops a later suite running."""

    def test_every_suite_runs_even_when_an_early_one_fails(self) -> None:
        marker = "tools/run_tool_tests.py"
        suites = (
            (marker, "--emit-exit-code", "0"),
            (marker, "--emit-exit-code", "7"),
            (marker, "--emit-exit-code", "0"),
        )
        results = [run_suite(command) for command in suites]

        self.assertEqual([0, 7, 0], [row["exitCode"] for row in results])
        summary = format_summary(results)
        self.assertIn("2 passed, 1 failed, 3 run", summary)
        self.assertIn("failed suites:", summary)
        self.assertIn("(exit 7)", summary)

    def test_the_run_fails_when_any_suite_fails(self) -> None:
        marker = "tools/run_tool_tests.py"
        self.assertEqual(
            0,
            run_all(
                (
                    (marker, "--emit-exit-code", "0"),
                    (marker, "--emit-exit-code", "0"),
                )
            ),
        )
        self.assertEqual(
            1,
            run_all(
                (
                    (marker, "--emit-exit-code", "0"),
                    (marker, "--emit-exit-code", "3"),
                )
            ),
        )

    def test_the_suite_list_matches_the_files_on_disk(self) -> None:
        # A gate that silently skips a suite it cannot find is the failure this
        # runner exists to prevent.
        for command in SUITES:
            with self.subTest(suite=command[0]):
                self.assertTrue((ROOT / command[0]).is_file(), command[0])
        self.assertTrue(set(WINDOWS_ONLY) <= {command[0] for command in SUITES})

    def test_windows_suites_are_reported_without_launching_on_linux(self) -> None:
        windows = tuple((path,) for path in WINDOWS_ONLY)
        portable = ("tools/run_tool_tests.py", "--emit-exit-code", "0")

        def result(command):
            return {"name": " ".join(command), "exitCode": 0, "seconds": 0.0}

        for host, expected in [("posix", [portable]), ("nt", [*windows, portable])]:
            captured = io.StringIO()
            with mock.patch(__name__ + ".run_suite", side_effect=result) as run, contextlib.redirect_stdout(captured):
                self.assertEqual(0, run_all((*windows, portable), host_os=host))
            self.assertEqual(expected, [call.args[0] for call in run.call_args_list])
            if host == "posix":
                self.assertIn("1 passed, 0 failed, 1 run, 4 skipped (Windows required)", captured.getvalue())
            else:
                self.assertIn("5 passed, 0 failed, 5 run", captured.getvalue())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--emit-exit-code",
        type=int,
        default=None,
        help=argparse.SUPPRESS,  # self-test fixture: exit with the given code
    )
    arguments = parser.parse_args(argv)
    if arguments.emit_exit_code is not None:
        return arguments.emit_exit_code
    if arguments.self_test:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(RunToolTestsSelfTest)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    return run_all()


if __name__ == "__main__":
    raise SystemExit(main())
