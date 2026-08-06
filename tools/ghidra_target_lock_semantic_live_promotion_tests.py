#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused fail-closed tests for the target-lock live-promotion owner."""

from __future__ import annotations

import json
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import ghidra_target_lock_semantic_live_promotion as owner
import ghidra_target_lock_semantic_live_launcher as launcher


class TargetLockLivePromotionTests(unittest.TestCase):
    def test_launcher_requires_external_reviewed_hash(self) -> None:
        with (
            mock.patch.dict(os.environ, {launcher.EXTERNAL_SHA256_ENV: ""}),
            self.assertRaisesRegex(launcher.LaunchError, "absent or malformed"),
        ):
            launcher.require_runtime_boundary()
        with (
            mock.patch.dict(os.environ, {launcher.EXTERNAL_SHA256_ENV: "1" * 64}),
            self.assertRaisesRegex(launcher.LaunchError, "SHA-256 differs"),
        ):
            launcher.require_runtime_boundary()

    def test_launcher_valid_boundary_verifies_full_python_distribution(self) -> None:
        reviewed = launcher.sha256_file(Path(launcher.__file__).resolve())
        distribution = {"fileSetSha256": launcher.PYTHON_DISTRIBUTION[2]}
        with (
            mock.patch.dict(os.environ, {launcher.EXTERNAL_SHA256_ENV: reviewed}),
            mock.patch.object(
                launcher, "verify_python_distribution", return_value=distribution
            ) as verify,
        ):
            actual = launcher.require_runtime_boundary()
        self.assertEqual(actual, (reviewed, distribution))
        verify.assert_called_once_with()

    def test_launcher_rejects_python_distribution_drift(self) -> None:
        with (
            mock.patch.object(launcher, "distribution_tree_rows", return_value=[]),
            self.assertRaisesRegex(launcher.LaunchError, "distribution differs"),
        ):
            launcher.verify_python_distribution()

    def test_launcher_import_path_excludes_repository_tools_and_is_immutable(self) -> None:
        launcher.require_reviewed_import_path()
        finder = launcher.ACTIVE_EXACT_SOURCE_FINDER
        self.assertIsNotNone(finder)
        self.assertIs(sys.meta_path[0], finder)
        prior_meta_path = list(sys.meta_path)
        try:
            sys.meta_path[:] = [*sys.meta_path[1:], finder]
            with self.assertRaisesRegex(launcher.LaunchError, "no longer first"):
                launcher.require_reviewed_import_path()
        finally:
            sys.meta_path[:] = prior_meta_path
        launcher.require_reviewed_import_path()
        before = tuple(sys.path)
        self.assertNotIn(str(launcher.TOOLS), before)
        sys.path.insert(0, str(launcher.TOOLS))
        self.assertEqual(tuple(sys.path), before)
        with tempfile.TemporaryDirectory() as temporary:
            shadow = Path(temporary)
            (shadow / "capstone.py").write_text("raise SystemExit('shadow')\n", encoding="utf-8")
            with self.assertRaisesRegex(launcher.LaunchError, "immutable"):
                sys.path.insert(0, str(shadow))
            self.assertNotIn(str(shadow), sys.path)

    def test_launcher_rejects_capstone_environment_override(self) -> None:
        with (
            mock.patch.dict(os.environ, {"LIBCAPSTONE_PATH": r"C:\unreviewed"}),
            self.assertRaisesRegex(launcher.LaunchError, "forbidden dependency"),
        ):
            launcher.require_capstone_binding()

    def test_launcher_binds_exact_capstone_python_and_native_files(self) -> None:
        binding = launcher.require_capstone_binding()
        self.assertEqual(binding["package"]["sha256"], launcher.CAPSTONE_INIT_SHA256)
        self.assertEqual(binding["x86"]["sha256"], launcher.CAPSTONE_X86_SHA256)
        self.assertEqual(binding["native"]["sha256"], launcher.CAPSTONE_DLL_SHA256)
        self.assertEqual(
            Path(binding["native"]["path"]),
            launcher.CAPSTONE_DLL.resolve(),
        )

    def test_reviewed_test_subprocess_requires_no_site(self) -> None:
        expected = f"REVIEWED_OWNER_TESTS_OK count={launcher.EXPECTED_TEST_COUNT}"
        completed = SimpleNamespace(returncode=0, stdout=expected + "\n", stderr="")
        with mock.patch.object(launcher.subprocess, "run", return_value=completed) as run:
            result = launcher.run_reviewed_tests_subprocess("1" * 64)
        self.assertEqual(result, {"count": launcher.EXPECTED_TEST_COUNT, "status": "PASSED"})
        argv = run.call_args.args[0]
        self.assertEqual(argv[1:4], ["-I", "-B", "-S"])

    def test_hidden_proof_verifier_executes_the_exact_loaded_owner(self) -> None:
        proof_path, proof_sha256 = launcher.EXACT_SOURCE_MODULES[
            "ghidra_target_lock_semantic_proof"
        ]
        observed_argv: list[list[str]] = []
        observed_userprofiles: list[str | None] = []

        def proof_main() -> int:
            observed_argv.append(list(sys.argv))
            observed_userprofiles.append(os.environ.get("USERPROFILE"))
            return 0

        proof = SimpleNamespace(
            __exact_source_path__=str(proof_path.resolve()),
            __exact_source_sha256__=proof_sha256,
            main=proof_main,
        )
        reviewed_owner = SimpleNamespace(
            formal=proof,
            PROOF_READY=launcher.PROOF_READY,
        )
        prior_argv = sys.argv
        isolated_home = r"C:\contained-runtime-home\profile"
        with (
            mock.patch.object(
                launcher, "load_reviewed_owner", return_value=reviewed_owner
            ),
            mock.patch.object(
                launcher, "require_reviewer_home", return_value=launcher.REVIEWER_HOME
            ),
            mock.patch.dict(os.environ, {"USERPROFILE": isolated_home}),
        ):
            self.assertEqual(launcher.run_reviewed_proof_verifier_in_process(), 0)
            self.assertEqual(os.environ.get("USERPROFILE"), isolated_home)
        self.assertIs(sys.argv, prior_argv)
        self.assertEqual(observed_userprofiles, [str(launcher.REVIEWER_HOME)])
        self.assertEqual(
            observed_argv,
            [[str(proof_path), "verify-ready", str(launcher.PROOF_READY)]],
        )

        def failing_proof_main() -> int:
            observed_userprofiles.append(os.environ.get("USERPROFILE"))
            raise RuntimeError("proof failure sentinel")

        proof.main = failing_proof_main
        with (
            mock.patch.object(
                launcher, "load_reviewed_owner", return_value=reviewed_owner
            ),
            mock.patch.object(
                launcher, "require_reviewer_home", return_value=launcher.REVIEWER_HOME
            ),
            mock.patch.dict(os.environ, {"USERPROFILE": isolated_home}),
        ):
            with self.assertRaisesRegex(RuntimeError, "proof failure sentinel"):
                launcher.run_reviewed_proof_verifier_in_process()
            self.assertEqual(os.environ.get("USERPROFILE"), isolated_home)
        self.assertIs(sys.argv, prior_argv)
        self.assertEqual(observed_userprofiles[-1], str(launcher.REVIEWER_HOME))

    def test_reviewer_home_requires_plain_single_link_executables(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary).resolve()
            with (
                mock.patch.object(launcher, "REVIEWER_HOME", home),
                self.assertRaisesRegex(launcher.LaunchError, "parent is absent"),
            ):
                launcher.require_reviewer_home()

            grok = home / ".grok/bin/grok.exe"
            claude = home / ".local/bin/claude.exe"
            grok.parent.mkdir(parents=True)
            claude.parent.mkdir(parents=True)
            grok.write_bytes(b"grok")
            claude.write_bytes(b"claude")
            with mock.patch.object(launcher, "REVIEWER_HOME", home):
                self.assertEqual(launcher.require_reviewer_home(), home)

            hardlink = grok.with_name("grok-hardlink.exe")
            os.link(grok, hardlink)
            with (
                mock.patch.object(launcher, "REVIEWER_HOME", home),
                self.assertRaisesRegex(launcher.LaunchError, "executable is absent or unsafe"),
            ):
                launcher.require_reviewer_home()

    def test_proof_verifier_child_routes_only_through_the_exact_launcher(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            argv = owner.proof_verify_argv(root)
            environment = owner.expected_process_environment(root)
            self.assertEqual(
                environment[owner.EXTERNAL_LAUNCHER_SHA256_ENV],
                os.environ[owner.EXTERNAL_LAUNCHER_SHA256_ENV],
            )
        self.assertEqual(argv[1:5], ["-I", "-B", "-S", "-X"])
        self.assertTrue(argv[5].startswith("pycache_prefix="))
        self.assertEqual(argv[6:], [str(owner.LAUNCHER), "_proof-verify"])
        self.assertNotIn(str(owner.PROOF_OWNER), argv)

        launcher_sha256 = owner.sha256_file(owner.LAUNCHER)
        with mock.patch.dict(
            os.environ,
            {owner.EXTERNAL_LAUNCHER_SHA256_ENV: launcher_sha256},
        ):
            material = owner.verify_spawn_material(argv)
        self.assertEqual(
            material["inputs"]["childEntrypoint"]["sha256"],
            launcher_sha256,
        )
        self.assertEqual(
            material["inputs"]["proofOwner"]["sha256"],
            owner.PROOF_OWNER_SHA256,
        )
        self.assertEqual(
            material["inputs"]["proofReady"]["sha256"],
            owner.PROOF_READY_SHA256,
        )

    def test_proof_verifier_rejects_old_or_malformed_child_grammar_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            valid = owner.proof_verify_argv(root)
            old_direct = [
                str(owner.PYTHON), "-I", "-B", "-S", "-X", valid[5],
                str(owner.PROOF_OWNER), "verify-ready", str(owner.PROOF_READY),
            ]
            malformed = (
                valid + ["extra"],
                valid[:-1] + ["_proof-verify-other"],
                valid[:5] + ["pycache_prefix=relative"] + valid[6:],
                valid[:5] + [str(Path(temporary) / "wrong-name")] + valid[6:],
                old_direct,
            )
            launcher_sha256 = owner.sha256_file(owner.LAUNCHER)
            with mock.patch.dict(
                os.environ,
                {owner.EXTERNAL_LAUNCHER_SHA256_ENV: launcher_sha256},
            ):
                for argv in malformed:
                    with self.subTest(argv=argv):
                        with self.assertRaisesRegex(
                            owner.PromotionError, "proof-verifier child grammar differs"
                        ):
                            owner.verify_spawn_material(argv)

            for value in ("", "1" * 64):
                with (
                    self.subTest(launcher_hash=value),
                    mock.patch.dict(
                        os.environ,
                        {owner.EXTERNAL_LAUNCHER_SHA256_ENV: value},
                    ),
                    self.assertRaises(owner.PromotionError),
                ):
                    owner.expected_process_environment(root)

    def test_launcher_rejects_preloaded_import_shadow(self) -> None:
        name = "codex_exact_source_shadow_probe"
        with mock.patch.dict(sys.modules, {name: SimpleNamespace()}):
            with self.assertRaisesRegex(launcher.LaunchError, "preloaded or shadowed"):
                launcher.reject_preloaded_exact_modules({name: (Path("x"), "0" * 64)})

    def test_exact_source_loader_ignores_valid_timestamp_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "probe.py"
            bad = b"VALUE = 'evil'\n"
            good = b"VALUE = 'good'\n"
            self.assertEqual(len(bad), len(good))
            source.write_bytes(bad)
            original = source.stat()
            py_compile.compile(str(source), doraise=True)
            source.write_bytes(good)
            os.utime(source, ns=(original.st_atime_ns, original.st_mtime_ns))
            loader = launcher.ExactSourceLoader(
                "exact_source_probe", source, launcher.sha256_bytes(good)
            )
            module = SimpleNamespace()
            loader.exec_module(module)
            self.assertEqual(module.VALUE, "good")

    def test_exact_source_loader_rejects_source_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "probe.py"
            source.write_text("VALUE = 1\n", encoding="utf-8")
            loader = launcher.ExactSourceLoader("drift_probe", source, "0" * 64)
            with self.assertRaisesRegex(launcher.LaunchError, "SHA-256 differs"):
                loader.exec_module(SimpleNamespace())

    def test_transitive_rtti_module_is_exact_source_bound(self) -> None:
        path, digest = launcher.EXACT_SOURCE_MODULES["re_rtti_vtables"]
        self.assertEqual(path, launcher.TOOLS / "re_rtti_vtables.py")
        self.assertEqual(
            digest,
            "90071f2536e6f511d647b47fda7d323110374fd6c57b15e5360adaa0fd717d1d",
        )

    def test_apply_argv_is_the_only_mutating_shape(self) -> None:
        output = Path(r"C:\evidence\observations.tsv")
        ready = Path(r"C:\evidence\observations.ready.json")
        command = " ".join(owner.fixed_apply_argv(owner.LIVE_PROJECT, output, ready))
        self.assertNotIn("-readOnly", command)
        self.assertIn(owner.SEMANTIC_TOOL.name, command)
        self.assertIn(owner.PLAN_SHA256, command)
        self.assertIn(owner.EVIDENCE_SHA256, command)
        self.assertRegex(command, r"\sapply$")

    def test_dry_and_readback_are_read_only(self) -> None:
        for mode in ("dry", "readback"):
            with self.subTest(mode=mode):
                command = " ".join(
                    owner.semantic_argv(
                        owner.LIVE_PROJECT,
                        Path(r"C:\evidence\observations.tsv"),
                        Path(r"C:\evidence\observations.ready.json"),
                        mode,
                    )
                )
                self.assertIn("-readOnly", command)
                self.assertRegex(command, rf"\s{mode}$")

    def test_structural_headless_parser_recognizes_real_readonly_option(self) -> None:
        argv = owner.semantic_argv(
            owner.LIVE_PROJECT,
            Path(r"C:\evidence\observations.tsv"),
            Path(r"C:\evidence\observations.ready.json"),
            "dry",
        )
        arguments = owner.parse_headless_batch_argv(argv)
        self.assertEqual(arguments.count("-readOnly"), 1)
        self.assertLess(arguments.index("-readOnly"), arguments.index("-postScript"))

    def test_unknown_semantic_mode_is_rejected(self) -> None:
        with self.assertRaisesRegex(owner.PromotionError, "unsupported read-only semantic mode"):
            owner.semantic_argv(owner.LIVE_PROJECT, Path("x"), Path("y"), "force")

    def test_semantic_argv_rejects_apply(self) -> None:
        with self.assertRaisesRegex(owner.PromotionError, "unsupported read-only semantic mode"):
            owner.semantic_argv(owner.LIVE_PROJECT, Path("x"), Path("y"), "apply")

    def test_run_semantic_rejects_apply_before_process_launch(self) -> None:
        with (
            mock.patch.object(owner, "run_process") as run,
            self.assertRaisesRegex(owner.PromotionError, "read-only"),
        ):
            owner.run_semantic(
                owner.LIVE_PROJECT, Path("root"), "forbidden", "apply",
                Path("cwd"), {},
            )
        run.assert_not_called()

    def test_generic_runner_rejects_apply_before_contained_process(self) -> None:
        argv = owner.fixed_apply_argv(owner.LIVE_PROJECT, Path("x"), Path("y"))
        with (
            mock.patch.object(owner.guard, "run_contained") as contained,
            self.assertRaisesRegex(owner.PromotionError, "grammar differs"),
        ):
            owner.run_process(Path("root"), "forbidden", argv, Path("cwd"), {})
        contained.assert_not_called()

    def test_generic_runner_allows_only_pinned_python_grammars(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            backup = [
                str(owner.PYTHON), "-I", "-B", str(owner.BACKUP_TOOL), "copy",
                str((root / "source").resolve()),
                str((root / "backups/backup").resolve()),
                "--project-name", owner.PROJECT_NAME,
            ]
            owner.require_canonical_nonmutating_process(root, "backup-copy", backup)
            with self.assertRaisesRegex(owner.PromotionError, "unsupported process grammar"):
                owner.require_canonical_nonmutating_process(
                    root,
                    "unexpected",
                    [str(owner.PYTHON), "-I", "-B", str(root / "unexpected.py")],
                )

    def test_backup_destination_cannot_escape_owner_backup_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = (root / "source").resolve()
            for destination in (
                owner.LIVE_PROJECT / "BEA.rep/injected",
                root / "runs/injected",
                root,
            ):
                with self.subTest(destination=destination):
                    argv = [
                        str(owner.PYTHON), "-I", "-B", str(owner.BACKUP_TOOL), "copy",
                        str(source), str(destination.resolve()),
                        "--project-name", owner.PROJECT_NAME,
                    ]
                    with self.assertRaisesRegex(owner.PromotionError, "backup destination"):
                        owner.require_canonical_nonmutating_process(root, "backup-copy", argv)

    def test_run_id_cannot_escape_owner_runs_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            argv = owner.proof_verify_argv(root)
            for run_id in ("../escape", r"nested\escape", "nested/escape", ".", ".."):
                with self.subTest(run_id=run_id):
                    with self.assertRaisesRegex(owner.PromotionError, "run id"):
                        owner.require_canonical_nonmutating_process(root, run_id, argv)

    def test_process_context_cannot_redirect_runtime_or_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment, cwd = owner.environment_for(root)
            argv = owner.inventory_argv(
                owner.LIVE_PROJECT,
                root / "runs/context/functions.tsv",
                root / "runs/context/program.tsv",
            )
            altered = dict(environment)
            altered["APPDATA"] = str(owner.LIVE_PROJECT)
            with (
                mock.patch.object(owner.guard, "run_contained") as contained,
                self.assertRaisesRegex(owner.PromotionError, "environment differs"),
            ):
                owner.run_process(root, "context", argv, cwd, altered)
            contained.assert_not_called()
            with (
                mock.patch.object(owner.guard, "run_contained") as contained,
                self.assertRaisesRegex(owner.PromotionError, "working directory differs"),
            ):
                owner.run_process(root, "context", argv, owner.LIVE_PROJECT, environment)
            contained.assert_not_called()

    def test_fresh_process_context_starts_without_compiled_script_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment, cwd, boundary = owner.create_fresh_process_context(
                root, "fresh-cache"
            )
            context = root / "process-contexts/fresh-cache"
            self.assertEqual(boundary["compiledClassCount"], 0)
            self.assertEqual(boundary["fileCount"], 1)
            self.assertEqual(list(context.rglob("*.class")), [])
            self.assertEqual(
                owner.process_context_boundary(
                    root, "fresh-cache", cwd, environment
                ),
                boundary,
            )
            with self.assertRaisesRegex(owner.PromotionError, "already exists"):
                owner.create_fresh_process_context(root, "fresh-cache")

    def test_process_context_recheck_rejects_compiled_class_poison(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment, cwd, _ = owner.create_fresh_process_context(
                root, "cache-poison"
            )
            poison = (
                Path(environment["APPDATA"])
                / "ghidra/ghidra_12.1.2_PUBLIC/osgi/compiled-bundles/poison/Evil.class"
            )
            poison.parent.mkdir(parents=True)
            poison.write_bytes(b"not trusted bytecode")
            with self.assertRaisesRegex(owner.PromotionError, "not pristine"):
                owner.process_context_boundary(
                    root, "cache-poison", cwd, environment
                )

    def test_nonmutating_runner_uses_run_exclusive_runtime_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment, cwd = owner.environment_for(root)
            argv = owner.inventory_argv(
                owner.LIVE_PROJECT,
                root / "runs/exclusive/functions.tsv",
                root / "runs/exclusive/program.tsv",
            )

            def contained(*, session_root, run_id, argv, cwd, environment, timeout_seconds):
                self.assertEqual(session_root, root)
                self.assertEqual(run_id, "exclusive")
                self.assertEqual(
                    cwd, root / "process-contexts/exclusive/work"
                )
                self.assertIn(
                    str(root / "process-contexts/exclusive/runtime-home"),
                    environment["APPDATA"],
                )
                self.assertEqual(
                    list((root / "process-contexts/exclusive").rglob("*.class")),
                    [],
                )
                return {"receipt": {}}, ""

            with (
                mock.patch.object(owner, "verify_spawn_runtime", return_value={}),
                mock.patch.object(owner.guard, "run_contained", side_effect=contained),
            ):
                owner.run_process(root, "exclusive", argv, cwd, environment)

    def test_script_source_bundle_rejects_added_java_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "tools"
            tools.mkdir()
            source = tools / "OnlyReviewed.java"
            source.write_bytes(b"public class OnlyReviewed {}\n")
            rows = [(source.name, source.stat().st_size, owner.sha256_file(source))]
            manifest = root / "bundle.tsv"
            manifest.write_bytes(owner.guard.envelope.canonical_rows(rows))
            expected = (1, source.stat().st_size, owner.guard.envelope.rows_digest(rows))
            with (
                mock.patch.object(owner, "TOOLS", tools),
                mock.patch.object(owner, "SCRIPT_SOURCE_BUNDLE_MANIFEST", manifest),
                mock.patch.object(
                    owner, "SCRIPT_SOURCE_BUNDLE_MANIFEST_SHA256",
                    owner.sha256_file(manifest),
                ),
                mock.patch.object(owner, "SCRIPT_SOURCE_BUNDLE", expected),
            ):
                owner.verify_ghidra_script_source_bundle()
                (tools / "Unreviewed.java").write_bytes(
                    b"public class Unreviewed {}\n"
                )
                with self.assertRaisesRegex(owner.PromotionError, "bundle differs"):
                    owner.verify_ghidra_script_source_bundle()

    def test_script_source_bundle_rejects_activation_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "tools"
            tools.mkdir()
            source = tools / "OnlyReviewed.java"
            source.write_bytes(b"public class OnlyReviewed {}\n")
            rows = [(source.name, source.stat().st_size, owner.sha256_file(source))]
            manifest = root / "bundle.tsv"
            manifest.write_bytes(owner.guard.envelope.canonical_rows(rows))
            expected = (1, source.stat().st_size, owner.guard.envelope.rows_digest(rows))
            metadata = tools / "META-INF/MANIFEST.MF"
            metadata.parent.mkdir()
            metadata.write_text(
                "Bundle-Activator: UnreviewedActivator\n", encoding="utf-8"
            )
            with (
                mock.patch.object(owner, "TOOLS", tools),
                mock.patch.object(owner, "SCRIPT_SOURCE_BUNDLE_MANIFEST", manifest),
                mock.patch.object(
                    owner, "SCRIPT_SOURCE_BUNDLE_MANIFEST_SHA256",
                    owner.sha256_file(manifest),
                ),
                mock.patch.object(owner, "SCRIPT_SOURCE_BUNDLE", expected),
                self.assertRaisesRegex(owner.PromotionError, "activation inputs"),
            ):
                owner.verify_ghidra_script_source_bundle()

    def test_runtime_distribution_verifier_binds_all_three_frozen_manifests(self) -> None:
        def verified(root, manifest, expected, label):
            return {
                "root": str(root.resolve()),
                "fileCount": expected[0],
                "totalBytes": expected[1],
                "fileSetSha256": expected[2],
                "manifest": None,
            }

        with mock.patch.object(
            owner.guard.envelope, "verify_distribution", side_effect=verified
        ) as verify:
            result = owner.verify_runtime_distributions(
                include_ghidra=True, include_jdk=True, include_python=True
            )
        self.assertEqual(set(result), {"ghidra", "jdk", "python"})
        self.assertEqual(verify.call_count, 3)
        self.assertEqual(
            [call.args[1] for call in verify.call_args_list],
            [
                owner.GHIDRA_DISTRIBUTION_MANIFEST,
                owner.JDK_DISTRIBUTION_MANIFEST,
                owner.PYTHON_DISTRIBUTION_MANIFEST,
            ],
        )

    def test_headless_spawn_revalidates_ghidra_and_jdk_distributions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment, cwd = owner.environment_for(root)
            argv = owner.inventory_argv(
                owner.LIVE_PROJECT,
                root / "runs/distribution/functions.tsv",
                root / "runs/distribution/program.tsv",
            )
            with (
                mock.patch.object(
                    owner, "verify_spawn_runtime",
                    side_effect=owner.PromotionError("distribution drift"),
                ) as verify,
                mock.patch.object(owner.guard, "run_contained") as contained,
                self.assertRaisesRegex(owner.PromotionError, "distribution drift"),
            ):
                owner.run_process(root, "distribution", argv, cwd, environment)
            verify.assert_called_once_with(argv)
            contained.assert_not_called()

    def test_python_spawn_revalidates_python_distribution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment, cwd = owner.environment_for(root)
            argv = owner.proof_verify_argv(root)
            with (
                mock.patch.object(
                    owner, "verify_spawn_runtime",
                    side_effect=owner.PromotionError("python distribution drift"),
                ) as verify,
                mock.patch.object(owner.guard, "run_contained") as contained,
                self.assertRaisesRegex(owner.PromotionError, "python distribution drift"),
            ):
                owner.run_process(root, "proof", argv, cwd, environment)
            verify.assert_called_once_with(argv)
            contained.assert_not_called()

    def test_direct_apply_spawn_boundary_binds_entrypoint_and_inputs(self) -> None:
        argv = owner.fixed_apply_argv(
            owner.LIVE_PROJECT,
            Path(r"C:\evidence\observations.tsv"),
            Path(r"C:\evidence\observations.ready.json"),
        )
        with mock.patch.object(
            owner,
            "verify_runtime_distributions",
            return_value={"ghidra": {}, "jdk": {}, "python": {}},
        ):
            boundary = owner.verify_spawn_runtime(argv)
        inputs = boundary["inputs"]
        self.assertEqual(
            set(inputs),
            {"jobChild", "childEntrypoint", "semanticPlan", "semanticEvidence"},
        )
        self.assertEqual(inputs["childEntrypoint"]["sha256"], owner.SEMANTIC_TOOL_SHA256)
        self.assertEqual(inputs["semanticPlan"]["sha256"], owner.PLAN_SHA256)
        self.assertEqual(inputs["semanticEvidence"]["sha256"], owner.EVIDENCE_SHA256)

    def test_direct_apply_spawn_rejects_truncated_semantic_tail(self) -> None:
        argv = owner.fixed_apply_argv(
            owner.LIVE_PROJECT,
            Path(r"C:\evidence\observations.tsv"),
            Path(r"C:\evidence\observations.ready.json"),
        )
        arguments = owner.parse_headless_batch_argv(argv)
        truncated = owner.batch_argv(arguments[:-1])
        with self.assertRaisesRegex(owner.PromotionError, "arguments are truncated"):
            owner.verify_spawn_material(truncated)

    def test_inline_job_child_executes_bounded_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            process, job = owner.spawn_inline_contained_process(
                [
                    str(owner.PYTHON), "-I", "-B", "-c",
                    "print('INLINE_JOB_CHILD_OK')",
                ],
                Path(temporary),
                dict(os.environ),
            )
            try:
                output, _ = process.communicate(timeout=30)
                self.assertEqual(process.returncode, 0)
                self.assertEqual(output.decode("utf-8").strip(), "INLINE_JOB_CHILD_OK")
            finally:
                owner.guard.envelope._close_handle(job)

    def test_quoted_readonly_substring_cannot_fool_generic_runner(self) -> None:
        argv = owner.batch_argv([
            str(owner.LIVE_PROJECT.resolve()), owner.PROJECT_NAME,
            "-process", owner.PROGRAM_NAME,
            "-noanalysis", "-scriptPath", r"C:\bait -readOnly bait",
            "-postScript", owner.SEMANTIC_TOOL.name, "apply",
        ])
        self.assertIn(" -readOnly ", " ".join(argv))
        with (
            mock.patch.object(owner.guard, "run_contained") as contained,
            self.assertRaisesRegex(owner.PromotionError, "grammar differs"),
        ):
            owner.run_process(Path("root"), "forbidden", argv, Path("cwd"), {})
        contained.assert_not_called()

    def test_readonly_token_consumed_as_log_value_is_rejected(self) -> None:
        argv = owner.batch_argv([
            str(owner.LIVE_PROJECT.resolve()), owner.PROJECT_NAME,
            "-process", owner.PROGRAM_NAME,
            "-log", "-readOnly", "-noanalysis", "-scriptPath", str(owner.TOOLS),
            "-postScript", owner.SEMANTIC_TOOL.name,
            str(owner.PLAN), owner.PLAN_SHA256,
            str(owner.EVIDENCE), owner.EVIDENCE_SHA256,
            r"C:\evidence\observations.tsv",
            r"C:\evidence\observations.ready.json",
            "apply",
        ])
        with (
            mock.patch.object(owner.guard, "run_contained") as contained,
            self.assertRaisesRegex(owner.PromotionError, "grammar differs"),
        ):
            owner.run_process(Path("root"), "forbidden", argv, Path("cwd"), {})
        contained.assert_not_called()

    def test_mutation_census_counts_readonly_token_used_as_log_value(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "runs/log-value-bypass/run.json"
            receipt.parent.mkdir(parents=True)
            argv = owner.batch_argv([
                str(owner.LIVE_PROJECT.resolve()), owner.PROJECT_NAME,
                "-process", owner.PROGRAM_NAME,
                "-log", "-readOnly", "-noanalysis", "-scriptPath", str(owner.TOOLS),
                "-postScript", owner.SEMANTIC_TOOL.name, "apply",
            ])
            receipt.write_text(json.dumps({"argv": argv}), encoding="utf-8")
            with self.assertRaisesRegex(owner.PromotionError, "mutating-process census differs"):
                owner.validate_mutation_census(root, expected=0)

    def test_cmd_metacharacter_injection_is_rejected_and_counted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id = "cmd-injection"
            argv = owner.inventory_argv(
                owner.LIVE_PROJECT,
                root / "runs/cmd-injection/functions.tsv",
                root / "runs/cmd-injection/program.tsv",
            )
            argv[-1] += r"&echo.>C:\Users\david\Ghidra\Projects\injected"
            with (
                mock.patch.object(owner.guard, "run_contained") as contained,
                self.assertRaisesRegex(owner.PromotionError, "serialization"),
            ):
                owner.run_process(root, run_id, argv, root, {})
            contained.assert_not_called()
            receipt = root / "runs/cmd-injection/run.json"
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text(json.dumps({"argv": argv}), encoding="utf-8")
            with self.assertRaisesRegex(owner.PromotionError, "mutating-process census differs"):
                owner.validate_mutation_census(root, expected=0)

    def test_readonly_outputs_must_be_bound_to_exact_run_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            argv = owner.semantic_argv(
                owner.LIVE_PROJECT,
                root / "outside.tsv",
                root / "outside.ready.json",
                "dry",
            )
            with (
                mock.patch.object(owner.guard, "run_contained") as contained,
                self.assertRaisesRegex(owner.PromotionError, "output paths differ"),
            ):
                owner.run_process(root, "bound-run", argv, root, {})
            contained.assert_not_called()

    def test_proof_verifier_uses_empty_alternate_pycache_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "probe.py"
            driver = root / "driver.py"
            bad = b"VALUE = 'evil'\n"
            good = b"VALUE = 'good'\n"
            source.write_bytes(bad)
            original = source.stat()
            py_compile.compile(str(source), doraise=True)
            source.write_bytes(good)
            os.utime(source, ns=(original.st_atime_ns, original.st_mtime_ns))
            driver.write_text(
                "import sys\n"
                f"sys.path.insert(0, {str(root)!r})\n"
                "import probe\n"
                "print(probe.VALUE)\n",
                encoding="utf-8",
            )
            control = subprocess.run(
                [str(owner.PYTHON), "-I", "-B", str(driver)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(control.returncode, 0)
            self.assertEqual(control.stdout.strip(), "evil")
            prefix = owner.proof_pycache_prefix(root)
            proof_argv = owner.proof_verify_argv(root)
            self.assertEqual(
                proof_argv[3:6], ["-S", "-X", f"pycache_prefix={prefix}"]
            )
            self.assertEqual(
                proof_argv[6:], [str(owner.LAUNCHER), "_proof-verify"]
            )
            protected = subprocess.run(
                [
                    str(owner.PYTHON), "-I", "-B", "-X", f"pycache_prefix={prefix}",
                    str(driver),
                ],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(protected.returncode, 0)
            self.assertEqual(protected.stdout.strip(), "good")
            self.assertFalse(prefix.exists())

    def test_hidden_proof_verifier_ignores_cwd_and_pythonpath_shadow(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = "SHADOW_BASE64_EXECUTED"
            (root / "base64.py").write_text(
                f"print({marker!r})\nraise RuntimeError('shadow import')\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(root)
            launcher_sha256 = owner.sha256_file(owner.LAUNCHER)
            environment[owner.EXTERNAL_LAUNCHER_SHA256_ENV] = launcher_sha256

            control = subprocess.run(
                [
                    str(owner.PYTHON), "-B", str(owner.PROOF_OWNER),
                    "verify-ready", str(owner.PROOF_READY),
                ],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertIn(marker, control.stdout + control.stderr)

            proof_argv = owner.proof_verify_argv(root)
            protected = subprocess.run(
                proof_argv,
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            expected = (
                f"READY_VERIFIED status=READY sha256={owner.PROOF_READY_SHA256} "
                "live_mutation_authorized=false"
            )
            self.assertEqual(protected.returncode, 0, protected.stderr)
            self.assertEqual(protected.stdout.strip(), expected)
            self.assertEqual(protected.stderr, "")
            self.assertNotIn(marker, protected.stdout + protected.stderr)
            self.assertFalse(owner.proof_pycache_prefix(root).exists())

    def test_inventory_argv_is_read_only(self) -> None:
        command = " ".join(
            owner.inventory_argv(owner.LIVE_PROJECT, Path("functions.tsv"), Path("program.tsv"))
        )
        self.assertIn("-readOnly", command)
        self.assertIn(owner.INVENTORY_TOOL.name, command)

    def test_classify_inventory_pre_requires_exact_pair(self) -> None:
        paths = {"functions": Path("functions.tsv"), "program": Path("program.tsv")}
        with (
            mock.patch.object(owner, "inventory_paths", return_value=paths),
            mock.patch.object(
                owner,
                "sha256_file",
                side_effect=[owner.PRE_FUNCTIONS_SHA256, owner.PRE_PROGRAM_SHA256],
            ),
            mock.patch.object(owner.formal, "validate_inventory_pair") as validate,
        ):
            state = owner.classify_inventory({}, Path("root"), "pre")
        self.assertEqual(state, owner.ProjectState.PRE)
        validate.assert_called_once()

    def test_classify_inventory_post_requires_exact_pair(self) -> None:
        paths = {"functions": Path("functions.tsv"), "program": Path("program.tsv")}
        with (
            mock.patch.object(owner, "inventory_paths", return_value=paths),
            mock.patch.object(
                owner,
                "sha256_file",
                side_effect=[owner.POST_FUNCTIONS_SHA256, owner.POST_PROGRAM_SHA256],
            ),
            mock.patch.object(owner.formal, "validate_inventory_pair") as validate,
        ):
            state = owner.classify_inventory({}, Path("root"), "post")
        self.assertEqual(state, owner.ProjectState.POST)
        validate.assert_called_once()

    def test_classify_inventory_unknown_does_not_fit(self) -> None:
        paths = {"functions": Path("functions.tsv"), "program": Path("program.tsv")}
        with (
            mock.patch.object(owner, "inventory_paths", return_value=paths),
            mock.patch.object(owner, "sha256_file", side_effect=["1" * 64, "2" * 64]),
        ):
            self.assertEqual(
                owner.classify_inventory({}, Path("root"), "unknown"),
                owner.ProjectState.UNKNOWN,
            )

    def test_apply_protocol_missing_outputs_is_partial(self) -> None:
        process = {
            "status": "COMPLETED",
            "exitCode": 0,
            "readerError": "",
            "argv": owner.fixed_apply_argv(
                owner.LIVE_PROJECT,
                Path(r"C:\missing\observations.tsv"),
                Path(r"C:\missing\observations.ready.json"),
            ),
        }
        semantic, reasons = owner.validate_apply_protocol(
            process,
            "",
            Path(r"C:\missing\observations.tsv"),
            Path(r"C:\missing\observations.ready.json"),
            Path(r"C:\missing"),
            semantic_tool=owner.SEMANTIC_TOOL,
            plan=owner.PLAN,
            evidence=owner.EVIDENCE,
        )
        self.assertIsNone(semantic)
        self.assertEqual(len(reasons), 1)
        self.assertIn("artifacts are absent", reasons[0])

    def test_promotion_root_permanently_blocks_retry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "promotion").mkdir()
            with (
                mock.patch.object(owner, "require_launch_gate", return_value={"gate": "x"}),
                self.assertRaisesRegex(owner.PromotionError, "already exists"),
            ):
                owner.promote(root)

    def test_promotion_root_is_rechecked_inside_mutex(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            @contextmanager
            def concurrent_claim():
                (root / "promotion").mkdir()
                yield SimpleNamespace(name=owner.MUTEX_NAME, abandoned=False)

            with (
                mock.patch.object(owner, "require_launch_gate", return_value={"gate": "x"}),
                mock.patch.object(owner.guard, "acquire_mutex", concurrent_claim),
                self.assertRaisesRegex(owner.PromotionError, "already exists"),
            ):
                owner.promote(root)

    def test_preparation_root_is_rechecked_inside_mutex(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "owner"

            @contextmanager
            def concurrent_claim():
                root.mkdir()
                yield SimpleNamespace(name=owner.MUTEX_NAME, abandoned=False)

            with (
                mock.patch.object(owner, "require_launch_gate", return_value={"gate": "x"}),
                mock.patch.object(owner.guard, "acquire_mutex", concurrent_claim),
                self.assertRaisesRegex(owner.PromotionError, "already exists"),
            ):
                owner.prepare(root)

    def test_preparation_claims_root_exclusively_before_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "owner"

            @contextmanager
            def lease():
                yield SimpleNamespace(name=owner.MUTEX_NAME, abandoned=False)

            def stop_after_claim() -> None:
                self.assertTrue(root.is_dir())
                raise owner.PromotionError("stop after exclusive claim")

            with (
                mock.patch.object(owner, "require_launch_gate", return_value={"gate": "x"}),
                mock.patch.object(owner.guard, "acquire_mutex", lease),
                mock.patch.object(owner, "preflight", side_effect=stop_after_claim),
                mock.patch.object(owner.guard.envelope, "ensure_plain_directory") as legacy,
                self.assertRaisesRegex(owner.PromotionError, "stop after exclusive claim"),
            ):
                owner.prepare(root)
            legacy.assert_not_called()
            self.assertTrue(root.is_dir())

    def test_promote_writes_intent_before_exactly_one_runner_call(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "prepared.ready.json").write_text("{}\n", encoding="utf-8")
            snapshot = {
                "root": str(owner.LIVE_PROJECT.resolve()),
                "fileCount": owner.BASELINE_FILE_COUNT,
                "totalBytes": owner.BASELINE_TOTAL_BYTES,
                "fileSetSha256": owner.BASELINE_FILESET_SHA256,
                "files": [],
            }
            post = {**snapshot, "fileSetSha256": "f" * 64}
            prepared = {
                "livePreimage": snapshot,
                "preBackup": {
                    "backupRoot": str(root / "pre-backup"),
                    "restoreRoot": str(root / "pre-restore"),
                },
                "finalObservation": {"inventory": {}},
            }

            @contextmanager
            def lease():
                yield SimpleNamespace(name=owner.MUTEX_NAME, abandoned=False)

            calls: list[list[str]] = []

            def run_once(
                *, session_root, run_id, argv, cwd, environment,
                timeout_seconds, spawn,
            ):
                self.assertEqual(run_id, "live-apply")
                self.assertEqual(timeout_seconds, 900)
                self.assertTrue((session_root / "attempt.started.json").is_file())
                spawned, job = spawn(argv, cwd, environment)
                self.assertIsNotNone(spawned)
                self.assertEqual(job, 73)
                calls.append(argv)
                return {
                    "argv": argv,
                    "receipt": {"path": "runs/live-apply/run.json", "bytes": 1, "sha256": "0" * 64},
                }, ""

            pre_observation = {"rawAfter": snapshot}
            classification = {"rawAfter": post}
            post_observation = {"rawAfter": post}
            post_backup = {"sourceSnapshot": post}
            bundle_root = root / "promotion/execution-bundle/repo"
            bundle_boundary = {
                "schema": owner.EXECUTION_BUNDLE_SCHEMA,
                "root": str(bundle_root),
                "fileCount": 30,
                "totalBytes": 123,
                "fileSetSha256": "e" * 64,
                "files": [],
                "semanticTool": {"sha256": owner.SEMANTIC_TOOL_SHA256},
                "plan": {"sha256": owner.PLAN_SHA256},
                "evidence": {"sha256": owner.EVIDENCE_SHA256},
                "scriptSourceBundle": {"fileSetSha256": "s" * 64},
            }
            bundle_seal = {
                "schema": owner.EXECUTION_BUNDLE_SEAL_SCHEMA,
                "root": str(bundle_root),
            }
            spawn_material = {
                "inputs": {"jobChild": {"sha256": "h"}},
                "scriptSourceBundle": {"fileSetSha256": "s" * 64},
                "executionBundle": bundle_boundary,
            }
            runtime_boundary = {
                "distributions": {
                    "ghidra": {"fileSetSha256": "g"},
                    "jdk": {"fileSetSha256": "j"},
                    "python": {"fileSetSha256": "p"},
                },
                **spawn_material,
            }
            apply_context = {
                "schema": owner.PROCESS_CONTEXT_SCHEMA,
                "runId": "live-apply",
            }
            quiescence = {
                "checkedAtUtc": "2026-08-04T01:02:03.123456Z",
                "javaProcesses": [],
                "nativeLockAbsent": True,
                "exclusiveFilesProbed": owner.BASELINE_FILE_COUNT,
                "projectFileSetSha256": owner.BASELINE_FILESET_SHA256,
            }
            underlying_process = SimpleNamespace()
            verify_runtime = mock.Mock(return_value=runtime_boundary)
            with (
                mock.patch.object(owner, "require_launch_gate", return_value={"gate": "x"}),
                mock.patch.object(owner.guard, "acquire_mutex", lease),
                mock.patch.object(owner, "preflight", return_value={}),
                mock.patch.object(owner, "load_prepared", return_value=prepared),
                mock.patch.object(
                    owner.guard, "assert_quiescent", return_value=quiescence
                ) as quiescent,
                mock.patch.object(owner.guard, "project_snapshot", return_value=snapshot),
                mock.patch.object(owner.guard, "same_project_snapshot", return_value=True),
                mock.patch.object(owner, "environment_for", return_value=({}, root)),
                mock.patch.multiple(
                    owner,
                    create_fresh_process_context=mock.Mock(
                        return_value=({}, root, apply_context)
                    ),
                    process_context_boundary=mock.Mock(return_value=apply_context),
                    run_proof_verifier=mock.Mock(return_value={}),
                    observe_pre=mock.Mock(return_value=pre_observation),
                    create_live_apply_bundle=mock.Mock(return_value=bundle_boundary),
                    seal_live_apply_bundle=mock.Mock(
                        return_value={"record": bundle_seal, "handles": [81, 82]}
                    ),
                    verify_live_apply_bundle=mock.Mock(return_value=bundle_boundary),
                    verify_live_apply_bundle_seal=mock.Mock(return_value=bundle_seal),
                    seal_exact_file=mock.Mock(return_value=83),
                    close_sealed_handles=mock.Mock(),
                    verify_spawn_runtime=verify_runtime,
                    validate_apply_protocol=mock.Mock(
                        return_value=({"normalizedRows": []}, [])
                    ),
                    classify_project=mock.Mock(
                        return_value=(owner.ProjectState.POST, classification)
                    ),
                    observe_post=mock.Mock(return_value=post_observation),
                    copy_and_drill=mock.Mock(return_value=post_backup),
                    validate_promotion_payload=mock.Mock(),
                    verify_artifacts=mock.Mock(return_value={"status": "READY"}),
                ),
                mock.patch.object(owner, "run_process") as generic_runner,
                mock.patch.object(
                    owner,
                    "spawn_inline_contained_process",
                    return_value=(underlying_process, 73),
                ) as os_spawn,
                mock.patch.object(owner.guard, "run_contained", side_effect=run_once),
            ):
                result = owner.promote(root)
            self.assertEqual(len(calls), 1)
            self.assertEqual(
                verify_runtime.call_args_list,
                [
                    mock.call(calls[0]),
                    mock.call(calls[0]),
                    mock.call(calls[0]),
                ],
            )
            self.assertEqual(quiescent.call_count, 2)
            os_spawn.assert_called_once_with(calls[0], root, {})
            attempt = json.loads(
                (root / "promotion/attempt.started.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                attempt["runtimeBoundary"],
                {**runtime_boundary, "processContext": apply_context},
            )
            generic_runner.assert_not_called()
            self.assertTrue(result["campaignPublicationAuthorized"])
            self.assertEqual(result["preSpawnQuiescence"], quiescence)
            self.assertTrue((root / "promotion/promotion.ready.json").is_file())

    def test_checked_live_apply_spawn_refuses_boundary_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            intent_path = root / "attempt.started.json"
            argv = ["fixed", "apply"]
            context = {"schema": owner.PROCESS_CONTEXT_SCHEMA, "runId": "live-apply"}
            bundle = {"root": str(root / "execution-bundle/repo")}
            runtime = {
                "distributions": {"ghidra": {"sha256": "d" * 64}},
                "inputs": {"childEntrypoint": {"sha256": "a" * 64}},
                "scriptSourceBundle": {"fileSetSha256": "b" * 64},
                "executionBundle": bundle,
            }
            seal = {"schema": owner.EXECUTION_BUNDLE_SEAL_SCHEMA}
            attempt = {
                "argv": argv,
                "runtimeBoundary": {**runtime, "processContext": context},
                "executionBundleSeal": seal,
                "livePreimage": {
                    "fileSetSha256": owner.BASELINE_FILESET_SHA256,
                },
            }
            owner.write_json_new(intent_path, attempt)
            intent_sha256 = owner.sha256_file(intent_path)
            quiescence = {
                "checkedAtUtc": "2026-08-04T01:02:03.123456Z",
                "javaProcesses": [],
                "nativeLockAbsent": True,
                "exclusiveFilesProbed": owner.BASELINE_FILE_COUNT,
                "projectFileSetSha256": owner.BASELINE_FILESET_SHA256,
            }
            cases = (
                (
                    "distribution",
                    {**runtime, "distributions": {"ghidra": {"sha256": "c" * 64}}},
                    context,
                    quiescence,
                ),
                (
                    "material",
                    {**runtime, "inputs": {"childEntrypoint": {"sha256": "c" * 64}}},
                    context,
                    quiescence,
                ),
                (
                    "context",
                    runtime,
                    {**context, "runId": "poisoned"},
                    quiescence,
                ),
                (
                    "project",
                    runtime,
                    context,
                    {**quiescence, "projectFileSetSha256": "d" * 64},
                ),
            )
            for label, actual_runtime, actual_context, actual_quiescence in cases:
                with self.subTest(label=label):
                    state = {
                        "callbackCalls": 0,
                        "delegateCalls": 0,
                        "preSpawnQuiescence": None,
                    }
                    delegate = mock.Mock()
                    with (
                        mock.patch.object(
                            owner, "verify_spawn_runtime", return_value=actual_runtime
                        ),
                        mock.patch.object(
                            owner, "process_context_boundary", return_value=actual_context
                        ),
                        mock.patch.object(
                            owner.guard,
                            "assert_quiescent",
                            return_value=actual_quiescence,
                        ),
                        mock.patch.object(
                            owner,
                            "verify_live_apply_bundle_seal",
                            return_value=seal,
                        ),
                        self.assertRaises(owner.PromotionError),
                    ):
                        owner.checked_live_apply_spawn(
                            root,
                            intent_path,
                            intent_sha256,
                            attempt,
                            argv,
                            root,
                            {},
                            state,
                            delegate,
                        )
                    delegate.assert_not_called()

    def test_checked_live_apply_spawn_uses_disk_intent_and_delegates_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            intent_path = root / "attempt.started.json"
            argv = ["fixed", "apply"]
            context = {"schema": owner.PROCESS_CONTEXT_SCHEMA, "runId": "live-apply"}
            bundle = {"root": str(root / "execution-bundle/repo")}
            runtime = {
                "distributions": {"ghidra": {"sha256": "d" * 64}},
                "inputs": {"childEntrypoint": {"sha256": "a" * 64}},
                "scriptSourceBundle": {"fileSetSha256": "b" * 64},
                "executionBundle": bundle,
            }
            seal = {"schema": owner.EXECUTION_BUNDLE_SEAL_SCHEMA}
            attempt = {
                "argv": argv,
                "runtimeBoundary": {**runtime, "processContext": context},
                "executionBundleSeal": seal,
                "livePreimage": {
                    "fileSetSha256": owner.BASELINE_FILESET_SHA256,
                },
            }
            owner.write_json_new(intent_path, attempt)
            intent_sha256 = owner.sha256_file(intent_path)
            quiescence = {
                "checkedAtUtc": "2026-08-04T01:02:03.123456Z",
                "javaProcesses": [],
                "nativeLockAbsent": True,
                "exclusiveFilesProbed": owner.BASELINE_FILE_COUNT,
                "projectFileSetSha256": owner.BASELINE_FILESET_SHA256,
            }
            state = {
                "callbackCalls": 0,
                "delegateCalls": 0,
                "preSpawnQuiescence": None,
            }
            delegate = mock.Mock(return_value=(SimpleNamespace(), 91))
            with (
                mock.patch.object(owner, "verify_spawn_runtime", return_value=runtime),
                mock.patch.object(
                    owner, "process_context_boundary", return_value=context
                ),
                mock.patch.object(
                    owner, "verify_live_apply_bundle_seal", return_value=seal
                ),
                mock.patch.object(
                    owner.guard, "assert_quiescent", return_value=quiescence
                ),
            ):
                result = owner.checked_live_apply_spawn(
                    root,
                    intent_path,
                    intent_sha256,
                    attempt,
                    argv,
                    root,
                    {},
                    state,
                    delegate,
                )
                self.assertEqual(result[1], 91)
                with self.assertRaisesRegex(owner.PromotionError, "state differs"):
                    owner.checked_live_apply_spawn(
                        root,
                        intent_path,
                        intent_sha256,
                        attempt,
                        argv,
                        root,
                        {},
                        state,
                        delegate,
                    )
            delegate.assert_called_once_with(argv, root, {})

            wrong_expected = {**attempt, "argv": ["different"]}
            fresh_state = {
                "callbackCalls": 0,
                "delegateCalls": 0,
                "preSpawnQuiescence": None,
            }
            second_delegate = mock.Mock()
            with self.assertRaisesRegex(owner.PromotionError, "intent changed"):
                owner.checked_live_apply_spawn(
                    root,
                    intent_path,
                    intent_sha256,
                    wrong_expected,
                    argv,
                    root,
                    {},
                    fresh_state,
                    second_delegate,
                )
            second_delegate.assert_not_called()

    def test_checked_live_apply_spawn_checks_project_last(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            intent_path = root / "attempt.started.json"
            argv = ["fixed", "apply"]
            context = {"schema": owner.PROCESS_CONTEXT_SCHEMA, "runId": "live-apply"}
            runtime = {
                "distributions": {"ghidra": {"sha256": "d" * 64}},
                "inputs": {"childEntrypoint": {"sha256": "a" * 64}},
                "scriptSourceBundle": {"fileSetSha256": "b" * 64},
                "executionBundle": {"root": str(root / "execution-bundle/repo")},
            }
            seal = {"schema": owner.EXECUTION_BUNDLE_SEAL_SCHEMA}
            attempt = {
                "argv": argv,
                "runtimeBoundary": {**runtime, "processContext": context},
                "executionBundleSeal": seal,
                "livePreimage": {
                    "fileSetSha256": owner.BASELINE_FILESET_SHA256,
                },
            }
            owner.write_json_new(intent_path, attempt)
            digest = owner.sha256_file(intent_path)
            order: list[str] = []
            quiescence = {
                "checkedAtUtc": "2026-08-04T01:02:03.123456Z",
                "javaProcesses": [],
                "nativeLockAbsent": True,
                "exclusiveFilesProbed": owner.BASELINE_FILE_COUNT,
                "projectFileSetSha256": owner.BASELINE_FILESET_SHA256,
            }

            def runtime_check(_argv):
                order.append("runtime")
                return runtime

            def context_check(*_args):
                order.append("context")
                return context

            def seal_check(*_args):
                order.append("seal")
                return seal

            def project_check(*_args):
                order.append("project")
                return quiescence

            def delegate(*_args):
                order.append("delegate")
                return SimpleNamespace(), 17

            state = {
                "callbackCalls": 0,
                "delegateCalls": 0,
                "preSpawnQuiescence": None,
            }
            with (
                mock.patch.object(owner, "verify_spawn_runtime", side_effect=runtime_check),
                mock.patch.object(owner, "process_context_boundary", side_effect=context_check),
                mock.patch.object(
                    owner, "verify_live_apply_bundle_seal", side_effect=seal_check
                ),
                mock.patch.object(owner.guard, "assert_quiescent", side_effect=project_check),
            ):
                owner.checked_live_apply_spawn(
                    root,
                    intent_path,
                    digest,
                    attempt,
                    argv,
                    root,
                    {},
                    state,
                    delegate,
                )
            self.assertEqual(order, ["runtime", "context", "seal", "project", "delegate"])

    def test_frozen_intent_refuses_post_spawn_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attempt.started.json"
            original = {"schema": "attempt", "startedAtUtc": "first"}
            owner.write_json_new(path, original)
            digest = owner.sha256_file(path)
            owner.require_frozen_json(path, digest, original, "apply intent")
            path.write_text(
                json.dumps({"schema": "attempt", "startedAtUtc": "second"}) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(owner.PromotionError, "SHA-256 differs"):
                owner.require_frozen_json(path, digest, original, "apply intent after spawn")

    def test_sealed_file_denies_write_and_delete_until_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attempt.started.json"
            path.write_bytes(b"sealed\n")
            digest = owner.sha256_file(path)
            sid = owner.current_user_sid()
            handle = owner.seal_exact_file(path, digest, "sealed test intent")
            try:
                with self.assertRaises(OSError):
                    path.write_bytes(b"poison\n")
                with self.assertRaises(OSError):
                    path.unlink()
                self.assertEqual(path.read_bytes(), b"sealed\n")
            finally:
                owner.close_sealed_handles([handle])
                owner.set_protected_dacl(path, sid, readonly=False)
            path.write_bytes(b"released\n")
            self.assertEqual(path.read_bytes(), b"released\n")

    def test_staged_execution_bundle_is_exact_and_sealed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            promotion_root = Path(temporary) / "promotion"
            promotion_root.mkdir()
            boundary = owner.create_live_apply_bundle(promotion_root)
            bundle_root = Path(boundary["root"])
            lease = owner.seal_live_apply_bundle(bundle_root)
            sid = owner.current_user_sid()
            try:
                self.assertEqual(boundary["fileCount"], 30)
                self.assertEqual(owner.verify_live_apply_bundle(bundle_root), boundary)
                self.assertEqual(
                    owner.verify_live_apply_bundle_seal(bundle_root, lease["record"]),
                    lease["record"],
                )
            finally:
                owner.close_sealed_handles(lease["handles"])
                files = [
                    bundle_root / Path(row["path"]) for row in boundary["files"]
                ]
                directories = owner.execution_bundle_directories(bundle_root, files)
                for item in [*files, *directories]:
                    owner.set_protected_dacl(item, sid, readonly=False)

    def test_verify_refuses_attempt_without_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "promotion").mkdir()
            with (
                mock.patch.object(owner, "require_launch_gate", return_value={"gate": "x"}),
                mock.patch.object(owner, "load_prepared", return_value={"preparedAtUtc": "x"}),
                self.assertRaisesRegex(owner.PromotionError, "do not retry"),
            ):
                owner.verify_artifacts(root)

    def test_quiescence_requires_complete_exact_fields(self) -> None:
        value = {
            "checkedAtUtc": "2026-08-04T01:02:03.123456Z",
            "javaProcesses": [],
            "nativeLockAbsent": True,
            "exclusiveFilesProbed": owner.BASELINE_FILE_COUNT,
            "projectFileSetSha256": owner.BASELINE_FILESET_SHA256,
        }
        owner.validate_quiescence(value, "test", fileset=owner.BASELINE_FILESET_SHA256)
        for key in tuple(value):
            with self.subTest(key=key):
                altered = dict(value)
                altered.pop(key)
                with self.assertRaises(owner.PromotionError):
                    owner.validate_quiescence(
                        altered, "test", fileset=owner.BASELINE_FILESET_SHA256
                    )

    def test_exact_stamp_rejects_valid_content_at_wrong_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected = root / "attempt.started.json"
            alternate = root / "alternate.json"
            expected.write_text("expected", encoding="utf-8")
            alternate.write_text("alternate", encoding="utf-8")
            stamp = owner.relative_stamp(alternate, root)
            with self.assertRaisesRegex(owner.PromotionError, "path differs"):
                owner.validate_exact_stamp(stamp, root, expected, "apply intent")

    def test_preparation_census_ignores_only_promotion_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "promotion/runs/live-apply/run.json"
            receipt.parent.mkdir(parents=True)
            argv = owner.fixed_apply_argv(
                owner.LIVE_PROJECT,
                root / "promotion/runs/live-apply/observations.tsv",
                root / "promotion/runs/live-apply/observations.ready.json",
            )
            receipt.write_text(json.dumps({"argv": argv}), encoding="utf-8")
            owner.write_json_new(
                root / "promotion/attempt.started.json", {"argv": argv}
            )
            owner.validate_mutation_census(root, expected=0, preparation_only=True)
            owner.validate_mutation_census(root, expected=1)

    def test_unexpected_mutator_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "runs/unexpected/run.json"
            receipt.parent.mkdir(parents=True)
            argv = owner.fixed_apply_argv(
                owner.LIVE_PROJECT,
                root / "runs/unexpected/observations.tsv",
                root / "runs/unexpected/observations.ready.json",
            )
            receipt.write_text(json.dumps({"argv": argv}), encoding="utf-8")
            with self.assertRaisesRegex(owner.PromotionError, "receipt path differs"):
                owner.validate_mutation_census(root, expected=1)

    def test_readonly_script_argument_cannot_hide_mutator(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "runs/hidden/run.json"
            receipt.parent.mkdir(parents=True)
            argv = owner.fixed_apply_argv(
                owner.LIVE_PROJECT,
                root / "runs/hidden/observations.tsv",
                root / "runs/hidden/observations.ready.json",
            )
            argv[-1] += " -readOnly"
            receipt.write_text(json.dumps({"argv": argv}), encoding="utf-8")
            with self.assertRaisesRegex(owner.PromotionError, "receipt path differs"):
                owner.validate_mutation_census(root, expected=1)

    def test_failed_promotion_returns_nonzero_after_printing_receipt(self) -> None:
        with (
            mock.patch.object(
                owner,
                "promote",
                return_value={"status": "BLOCKED", "campaignPublicationAuthorized": False},
            ),
            mock.patch("builtins.print"),
        ):
            self.assertEqual(owner.main(["promote"]), 10)


if __name__ == "__main__":
    unittest.main()
