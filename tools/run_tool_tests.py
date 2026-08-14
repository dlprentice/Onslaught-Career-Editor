#!/usr/bin/env python3
"""Run every tools/ test suite and report one summary.

WHY THIS EXISTS.  ``npm run test:tools`` used to chain thirteen suites with
``&&``.  A failure in the middle meant the suites after it never ran and were
silently unverified: one red suite hid the state of every suite behind it, and
a flaky one could mask a real regression indefinitely (task #158).

So every suite runs, every time.  Output is streamed as it happens - a summary
is a navigation aid, not a replacement for the failing suite's own report - and
the exit code is non-zero when any suite failed, exactly as the chain was.

Order is the chain's original order and is not a dependency: the suites are
independent, and running them in one process would be wrong, because several
of them compile executables and spawn PowerShell.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import time
import unittest


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
    ("tools/export_game_assets_tests.py",),
    ("rebuild/tools/materialize_retail_assets_tests.py",),
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
    ("tools/ttd_pipeline_contract_tests.py",),
    ("tools/parity_lab_tests.py",),
    ("tools/re_coverage_ledger_tests.py",),
    ("tools/re_campaign_tests.py",),
    ("tools/re_evidence_register_export_tests.py",),
    ("tools/re_level521_damage_writes_tests.py",),
    ("tools/re_applydamage_primary_reproof_tests.py",),
    ("tools/re_cexplosion_hit_runtime_tests.py",),
    ("tools/re_cround_move_runtime_tests.py",),
    ("tools/re_cround_handle_event_runtime_tests.py",),
    ("tools/re_tokenarchive_dispatch_reproof_tests.py",),
    ("tools/re_mission_native_setpos_reproof_tests.py",),
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


def format_summary(results: list[dict[str, object]]) -> str:
    """One line per suite, failures repeated at the end so none can be missed."""

    width = max((len(str(row["name"])) for row in results), default=0)
    lines = ["", "tools test summary", "=" * (width + 26)]
    for row in results:
        lines.append(
            "{status:4}  {name:<{width}}  exit={exit:<4} {seconds:>7.1f}s".format(
                status="PASS" if row["exitCode"] == 0 else "FAIL",
                name=str(row["name"]),
                width=width,
                exit=str(row["exitCode"]),
                seconds=float(str(row["seconds"])),
            )
        )
    failed = [row for row in results if row["exitCode"] != 0]
    lines.append(
        f"{len(results) - len(failed)} passed, {len(failed)} failed, "
        f"{len(results)} run"
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


def run_all(suites: tuple[tuple[str, ...], ...] = SUITES) -> int:
    results: list[dict[str, object]] = []
    for index, command in enumerate(suites, start=1):
        print(
            f"\n[{index}/{len(suites)}] {' '.join(command)}",
            flush=True,
        )
        results.append(run_suite(command))
    print(format_summary(results), flush=True)
    return 1 if any(row["exitCode"] != 0 for row in results) else 0


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
