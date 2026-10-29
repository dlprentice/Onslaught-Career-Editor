#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Run every host-supported tools/ test suite and report one summary.

Every supported suite runs, even after a failure. A suite that cannot run here
(it needs a Windows host, or a submodule checkout that is absent) is reported as
a named SKIP with its reason, never counted as a pass and never as a failure.
Output is streamed as it happens - a summary
is a navigation aid, not a replacement for the failing suite's own report - and
the exit code is non-zero when any suite failed, exactly as the chain was.

Order is not a dependency: the suites are independent, and running them in one
process would be wrong, because several compile executables or spawn engines.
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

# One entry per registered command. Paths are repository-relative
# and are resolved against ROOT so the gate behaves the same from any cwd.
SUITES: tuple[tuple[str, ...], ...] = (
    ("tools/check_installed_game_claims.py", "--self-test"),
    ("tools/check_installed_game_claims.py", "--check"),
    ("tools/check_registered_screenshots.py", "--self-test"),
    ("tools/check_registered_screenshots.py", "--check"),
    # The publication helper behind twelve writers: its own checks were not part of this gate.
    ("tools/safe_generated_output.py", "--self-test"),
    ("tools/safe_generated_output_tests.py",),
    ("tools/aya_archive_inventory_tests.py",),
    ("tools/aya_extractor_source_audit_tests.py",),
    ("tools/cmsh_animation_usage_census_tests.py",),
    ("tools/model_transform_catalog_tests.py",),
    ("tools/level_asset_xref_tests.py",),
    ("tools/cmsh_grammar_walk_tests.py",),
    ("tools/dds_metadata_tests.py",),
    ("tools/content_catalog_tests.py",),
    ("tools/export_asset_catalog_tests.py",),
    ("tools/world_resources_encode_tests.py",),
    ("tools/world_mod_stage_tests.py",),
    ("tools/world_edit_preview_tests.py",),
    ("tools/world_edit_move_tests.py",),
    ("tools/world_thing_index_tests.py",),
    ("tools/aya_texture_fidelity_census_tests.py",),
    ("tools/export_game_assets_tests.py",),
    ("rebuild/tools/materialize_retail_assets_tests.py",),
    ("rebuild/tools/cmsh_static_preview_tests.py",),
    ("tools/score_frontend_capture_tests.py",),
    ("tools/check_region_overlap_tests.py",),
    ("tools/check_region_overlap.py",),
    # Name-align plates (Gen34–38): keep regression guards in the sweep (Opus).
    ("tools/worldheaders_decode.py", "--self-test"),
    # Format, contract and decoder suites.
    ("tools/dds_census_tests.py",),
    ("tools/mission_script_inspect_tests.py",),
    ("tools/worldheaders_decode_tests.py",),
    ("tools/cmsh_skinning_contract_tests.py",),
    ("tools/cmsh_matrix_normal_contract_tests.py",),
    ("tools/battle_engine_config_decode_tests.py",),
    ("tools/gltf_pose_check_tests.py",),
    ("tools/goodie_resource_walk_tests.py",),
    ("tools/xap_bank_walk_tests.py",),
)

# Test files that are deliberately not in SUITES, each with why and where they run instead. The registry self-test fails for any
# *_tests.py (or test_*.py) file that is in neither place, so a new test file cannot silently fall outside the gate.
NOT_IN_THIS_GATE: dict[str, str] = {
    "tools/run_tool_tests.py": "this runner itself: npm run test:tools runs its --self-test before any suite",
    "tools/companion_godot_tests.py": "fake-tool checks of the companion's Godot routes; run by npm run test:companion-tools (part of npm test)",
    "tools/godot_host_tests.py": "engine discovery and process cleanup with fake tools; run by npm run test:godot-host",
    "rebuild/tools/first_flight_tests.py": "the rebuild launcher with fake tools; run by npm run test:godot-host",
    "rebuild/tools/aya_battleengine_identity_analyzer_tests.py":
        "frozen rebuild copy, not built or tested here (its gate is onslaught-godot's); no Toolkit tool imports its module",
    "rebuild/tools/materialize_films_tests.py":
        "frozen rebuild copy, not built or tested here; no Toolkit tool imports its module, and it needs numpy",
    "rebuild/tools/rebuild_gate_tests.py":
        "frozen rebuild copy, not built or tested here; it tests the rebuild gate's report readers, and that gate is not run here",
}

# Directories that hold other checkouts, private data or build output, never this repository's own test files.
_NOT_REPOSITORY_SOURCE = frozenset({
    ".git", ".worktrees", ".claude", "local-data", "local-lab", ".artifacts", "references", "node_modules", "__pycache__",
})


def find_test_files(root: pathlib.Path = ROOT) -> set[str]:
    """Every *_tests.py and test_*.py file below root, repository-relative with forward slashes."""

    found: set[str] = set()
    for directory, names, files in os.walk(root):
        names[:] = [name for name in names if name not in _NOT_REPOSITORY_SOURCE]
        for name in files:
            if name.endswith("_tests.py") or (name.startswith("test_") and name.endswith(".py")):
                found.add(pathlib.Path(directory, name).relative_to(root).as_posix())
    return found


def unregistered_test_files(
    root: pathlib.Path = ROOT, registered: set[str] | None = None, excluded: set[str] | None = None
) -> list[str]:
    """Test files that are neither registered in SUITES nor excluded with a reason."""

    registered = {command[0] for command in SUITES} if registered is None else registered
    excluded = set(NOT_IN_THIS_GATE) if excluded is None else excluded
    return sorted(find_test_files(root) - registered - excluded)

# Suites that need a Windows host, by path, with the reason. None remain since the
# Windows runtime-probe lab moved to the private RE archive; the mechanism stays so a
# future one is reported as skipped rather than counted as a pass.
WINDOWS_ONLY: dict[str, str] = {}

# Suites that need submodule checkouts, by path. Without one the suite is reported as a named SKIP: the audit compares each
# checkout with its pinned commit, so there is nothing to compare when the checkout is absent. A checkout that is present at
# another commit is a real failure and is not skipped here.
NEEDS_SUBMODULES: dict[str, tuple[str, ...]] = {
    "tools/aya_extractor_source_audit_tests.py": ("references/AYAResourceExtractor", "references/Onslaught"),
}


def missing_submodules(path: str, root: pathlib.Path = ROOT) -> list[str]:
    """The submodules a suite needs whose checkout is absent (an initialised submodule has a .git entry)."""

    return [name for name in NEEDS_SUBMODULES.get(path, ()) if not (root / name / ".git").exists()]


def skip_reason(command: tuple[str, ...], host_os: str, root: pathlib.Path = ROOT) -> str | None:
    """Why this suite cannot run on this host and checkout, or None when it can."""

    if host_os != "nt" and command[0] in WINDOWS_ONLY:
        return "Windows host required: " + WINDOWS_ONLY[command[0]]
    missing = missing_submodules(command[0], root)
    if missing:
        return "submodule not initialised: " + ", ".join(missing) + " (git submodule update --init " + " ".join(missing) + ")"
    return None


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
        + (f", {len(skipped)} skipped" if skipped else "")
    )
    if failed:
        lines.append("failed suites:")
        lines.extend(f"  {row['name']} (exit {row['exitCode']})" for row in failed)
    if skipped:
        lines.append("skipped suites (not run, not passed):")
        lines.extend(f"  {row['name']}: {row['skipReason']}" for row in skipped)
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
        reason = skip_reason(command, host_os)
        if reason:
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

    def test_every_test_file_is_registered_or_excluded_with_a_reason(self) -> None:
        # The converse of the check above: a gate also fails when a suite that exists is silently outside it.
        self.assertEqual([], unregistered_test_files(),
                         "a test file is outside the gate: register it in SUITES, or list it in NOT_IN_THIS_GATE with a reason")
        self.assertEqual(set(), {command[0] for command in SUITES} & set(NOT_IN_THIS_GATE), "both registered and excluded")
        self.assertEqual(set(), set(NOT_IN_THIS_GATE) - find_test_files(), "an exclusion names a file that does not exist")
        for path, reason in NOT_IN_THIS_GATE.items():
            with self.subTest(path=path):
                self.assertGreaterEqual(len(reason.split()), 5, "an exclusion needs a reason, not a placeholder")

    def test_a_stray_test_file_is_found_and_other_checkouts_are_not_scanned(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for relative in (
                "tools/known_tests.py", "tools/new_tests.py", "rebuild/tools/stray_tests.py", "tools/test_pytest_style.py",
                "local-data/scratch_tests.py", ".worktrees/other/x_tests.py", "references/Onslaught/y_tests.py",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("")
            self.assertEqual(
                ["rebuild/tools/stray_tests.py", "tools/new_tests.py", "tools/test_pytest_style.py"],
                unregistered_test_files(root, registered={"tools/known_tests.py"}, excluded=set()),
            )
            self.assertEqual([], unregistered_test_files(
                root, registered={"tools/known_tests.py", "tools/new_tests.py", "tools/test_pytest_style.py"},
                excluded={"rebuild/tools/stray_tests.py"}))

    @mock.patch.dict(WINDOWS_ONLY, {f"tools/windows_only_{n}.py": "synthetic" for n in range(4)})
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
                self.assertIn("1 passed, 0 failed, 1 run, 4 skipped", captured.getvalue())
                named = [line for line in captured.getvalue().splitlines()
                         if line.startswith("  tools/windows_only_") and line.endswith(": Windows host required: synthetic")]
                self.assertEqual(4, len(named))                    # each skip is named in the skipped-suites list, with its reason
            else:
                self.assertIn("5 passed, 0 failed, 5 run", captured.getvalue())

    def test_a_missing_submodule_is_a_named_skip_not_a_pass_or_a_failure(self) -> None:
        import tempfile

        suite = "tools/aya_extractor_source_audit_tests.py"
        self.assertIn(suite, {command[0] for command in SUITES})
        self.assertEqual(("references/AYAResourceExtractor", "references/Onslaught"), NEEDS_SUBMODULES[suite])
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for name in NEEDS_SUBMODULES[suite]:
                (root / name).mkdir(parents=True)                      # an empty directory is an uninitialised submodule
            reason = skip_reason((suite,), "posix", root)
            self.assertIn("submodule not initialised", reason)
            for name in NEEDS_SUBMODULES[suite]:
                self.assertIn(name, reason)
            (root / "references/Onslaught/.git").write_text("gitdir: elsewhere\n")
            self.assertEqual(["references/AYAResourceExtractor"], missing_submodules(suite, root))
            (root / "references/AYAResourceExtractor/.git").write_text("gitdir: elsewhere\n")
            self.assertIsNone(skip_reason((suite,), "posix", root))    # both present: the suite runs (and may fail)
        self.assertIsNone(skip_reason(("tools/content_catalog_tests.py",), "posix"))

    def test_skipped_suites_are_counted_and_named_apart_from_passes_and_do_not_fail_the_run(self) -> None:
        reason = "submodule not initialised: references/AYAResourceExtractor (git submodule update --init references/AYAResourceExtractor)"
        results = [
            {"name": "tools/a_tests.py", "exitCode": 0, "seconds": 0.1},
            {"name": "tools/needs_submodule_tests.py", "exitCode": None, "seconds": 0.0, "skipReason": reason},
        ]
        summary = format_summary(results)
        self.assertIn("1 passed, 0 failed, 1 run, 1 skipped", summary)
        self.assertIn("SKIP  tools/needs_submodule_tests.py", summary)
        self.assertIn("skipped suites (not run, not passed):", summary)
        self.assertIn("  tools/needs_submodule_tests.py: " + reason, summary)
        self.assertNotIn("PASS  tools/needs_submodule_tests.py", summary)
        with mock.patch(__name__ + ".run_suite", return_value=results[0]), \
                mock.patch.dict(NEEDS_SUBMODULES, {"tools/needs_submodule_tests.py": ("references/AYAResourceExtractor",)}), \
                mock.patch(__name__ + ".missing_submodules", return_value=["references/AYAResourceExtractor"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, run_all((("tools/needs_submodule_tests.py",),), host_os="posix"))


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
