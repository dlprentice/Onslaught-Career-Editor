#!/usr/bin/env python3
"""Focused tests for the safe-copy live runtime smoke helper allowlist."""

from __future__ import annotations

import ast
from contextlib import redirect_stderr
import datetime as dt
import hashlib
import importlib.util
import io
import json
import os
import re
import shlex
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"


class WinUiSafeCopyLiveRuntimeSmokeTests(unittest.TestCase):
    def script_text(self) -> str:
        return SCRIPT.read_text(encoding="utf-8")

    def live_smoke_module(self):
        spec = importlib.util.spec_from_file_location("winui_safe_copy_live_runtime_smoke", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def parse(self, *arguments: str):
        module = self.live_smoke_module()
        return module, module.parse_args(shlex.split(" ".join(arguments), posix=False))

    def test_morph_canary_protocol_is_unpatched_fixed_and_capture_free(self) -> None:
        module, args = self.parse(
            "--runtime-protocol battleengine-morph-identity-canary-v1",
            "--canary-role noInputControl",
            "--capture-count 0",
        )

        plan = module.validate_runtime_protocol(args)

        self.assertEqual(
            ["-skipfmv", "-level", "850", "-configuration", "2"],
            plan.launch_arguments,
        )
        self.assertEqual([], plan.patch_keys)
        self.assertFalse(plan.apply_windowed_compatibility_patch)
        self.assertEqual(0x21, plan.transform_entry_id)
        self.assertEqual(8, plan.transform_keyboard_device_code)
        self.assertEqual("Q", plan.transform_player1_token)
        self.assertEqual("", plan.transform_player2_token)
        self.assertEqual(0, plan.capture_count)
        self.assertEqual([], plan.input_sequences)
        self.assertFalse(plan.include_modern_graphics)
        self.assertFalse(plan.stage_music_replacement)
        self.assertFalse(plan.allow_background_window_messages)
        self.assertEqual("MORPH_CANARY_READY", plan.required_cdb_log_marker)
        self.assertEqual(60, plan.input_step_delay_ms)
        self.assertEqual(10000, plan.cdb_log_ready_timeout_ms)

    def test_morph_canary_live_boundary_requires_hash_bound_authority_controls(self) -> None:
        module, missing_args = self.parse(
            "--runtime-protocol battleengine-morph-identity-canary-v1",
            "--canary-role noInputControl",
        )
        with tempfile.TemporaryDirectory(prefix="morph-authority-test-") as temp:
            private_parent = Path(temp) / "local-proofs"
            private_parent.mkdir()
            proof_root = private_parent / "battleengine-morph-identity-canary-matrix"
            proof_root.mkdir()
            role_root = proof_root / "no-input-control"
            with self.assertRaisesRegex(ValueError, "authority controls"):
                module.validate_morph_canary_control_inputs(
                    missing_args,
                    role_root,
                    private_parent=private_parent,
                    now=dt.datetime(2026, 7, 12, 20, 0, tzinfo=dt.timezone.utc),
                )

            control_root = private_parent / "battleengine-morph-identity-canary-control-test"
            control_root.mkdir()
            authority_path = control_root / "authority.json"
            leases_path = control_root / "leases.json"
            authority_payload = {
                "schemaVersion": module.morph_authority.AUTHORITY_SCHEMA,
                "actionFamily": module.morph_authority.ACTION_FAMILY,
                "issuedAtUtc": "2026-07-12T20:00:00Z",
                "expiresAtUtc": "2026-07-12T21:00:00Z",
                "proofRoot": str(proof_root),
                "allowedActions": list(module.morph_authority.REQUIRED_ALLOWED_ACTIONS),
                "forbiddenActions": list(module.morph_authority.REQUIRED_FORBIDDEN_ACTIONS),
                "maxSpendUsd": 0,
                "validationGates": list(module.morph_authority.REQUIRED_VALIDATION_GATES),
                "cleanup": module.morph_authority.REQUIRED_CLEANUP,
                "rollback": module.morph_authority.REQUIRED_ROLLBACK,
            }
            lease_payload = {
                "schemaVersion": module.morph_authority.LEASE_SCHEMA,
                "actionFamily": module.morph_authority.ACTION_FAMILY,
                "issuedAtUtc": "2026-07-12T20:00:00Z",
                "expiresAtUtc": "2026-07-12T21:00:00Z",
                "owner": "harness-test",
                "leases": [
                    {
                        "resource": resource,
                        "owner": "harness-test",
                        "exclusive": True,
                        "acquiredAtUtc": "2026-07-12T20:00:00Z",
                        "expiresAtUtc": "2026-07-12T21:00:00Z",
                    }
                    for resource in module.morph_authority.REQUIRED_RESOURCES
                ],
            }
            authority_path.write_text(json.dumps(authority_payload), encoding="utf-8")
            leases_path.write_text(json.dumps(lease_payload), encoding="utf-8")
            authority_digest = hashlib.sha256(authority_path.read_bytes()).hexdigest()
            leases_digest = hashlib.sha256(leases_path.read_bytes()).hexdigest()
            args = module.parse_args([
                "--runtime-protocol", module.MORPH_CANARY_RUNTIME_PROTOCOL,
                "--canary-role", "noInputControl",
                "--canary-authority-file", str(authority_path),
                "--expected-canary-authority-sha256", authority_digest,
                "--canary-leases-file", str(leases_path),
                "--expected-canary-leases-sha256", leases_digest,
            ])
            controls = module.validate_morph_canary_control_inputs(
                args,
                role_root,
                private_parent=private_parent,
                now=dt.datetime(2026, 7, 12, 20, 0, tzinfo=dt.timezone.utc),
            )
            self.assertEqual(authority_digest, controls.authority_sha256)
            args.expected_canary_leases_sha256 = "0" * 64
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                module.validate_morph_canary_control_inputs(
                    args,
                    role_root,
                    private_parent=private_parent,
                    now=dt.datetime(2026, 7, 12, 20, 0, tzinfo=dt.timezone.utc),
                )

    def test_parser_rejects_abbreviated_protocol_and_canary_timing_options(self) -> None:
        module = self.live_smoke_module()
        abbreviated = (
            ["--runtime-prot", "battleengine-morph-identity-canary-v1"],
            ["--runtime-protocol", "battleengine-morph-identity-canary-v1", "--canary-role", "noInputControl", "--input-step-del", "60"],
            ["--runtime-protocol", "battleengine-morph-identity-canary-v1", "--canary-role", "noInputControl", "--cdb-log-ready-time", "10000"],
        )

        for arguments in abbreviated:
            with self.subTest(arguments=arguments), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                module.parse_args(arguments)

    def test_morph_canary_protocol_derives_exact_positive_role_input(self) -> None:
        module, transform_args = self.parse(
            "--runtime-protocol battleengine-morph-identity-canary-v1",
            "--canary-role positiveTransform",
        )
        transform_plan = module.validate_runtime_protocol(transform_args)
        self.assertEqual(["tap:Q"], transform_plan.input_sequences)

        _, repeat_args = self.parse(
            "--runtime-protocol battleengine-morph-identity-canary-v1",
            "--canary-role positiveRepeat",
        )
        repeat_plan = module.validate_runtime_protocol(repeat_args)
        self.assertEqual(["tap:Q"], repeat_plan.input_sequences)

    def test_morph_canary_protocol_rejects_mixed_proof_levers(self) -> None:
        rejected_arguments = (
            "--capture-count 1",
            "--pre-input-capture-count 1",
            "--capture-after-each-input-sequence",
            "--focus-before-pre-input-capture",
            "--input-sequence tap:E",
            "--input-step-delay-ms 61",
            "--allow-background-window-messages --arm-background-window-messages \"ALLOW BACKGROUND BEA WINDOW MESSAGES\"",
            "--level-id 851",
            "--controller-configuration 1",
            "--persist-controller-config-in-options",
            "--bind-forward-qe-for-input-isolation",
            "--bind-fire-qe-for-weapon-handoff",
            "--bind-look-down-qe-for-config2-forward-discovery",
            "--bind-config2-census-row-qe movement-forward",
            "--sharpen-mouse-look",
            "--include-modern-graphics",
            "--extra-patch-key frontend_clear_screen_black",
            "--profile-preset-id split-screen-local",
            "--stage-music-replacement",
            "--music-swap-preset-id use-bea02-for-bea01",
            "--launch-nomusic",
            "--launch-nosound",
            "--cdb-command-file tools\\runtime-probes\\local-multiplayer-level850-observer.cdb.txt",
            "--cdb-log-ready-timeout-ms 11000",
            "--cdb-attach-phase after-launch",
        )

        for rejected in rejected_arguments:
            with self.subTest(arguments=rejected):
                module, args = self.parse(
                    "--runtime-protocol battleengine-morph-identity-canary-v1",
                    "--canary-role noInputControl",
                    rejected,
                )
                with self.assertRaises(ValueError):
                    module.validate_runtime_protocol(args)

    def test_default_protocol_preserves_explicit_armed_background_mode(self) -> None:
        module, args = self.parse(
            "--runtime-protocol default",
            "--allow-background-window-messages",
            "--arm-background-window-messages \"ALLOW BACKGROUND BEA WINDOW MESSAGES\"",
        )

        plan = module.validate_runtime_protocol(args)

        self.assertEqual("default", plan.runtime_protocol)
        self.assertTrue(plan.allow_background_window_messages)
        self.assertEqual(["force_windowed", "resolution_gate"], plan.patch_keys)
        self.assertTrue(plan.apply_windowed_compatibility_patch)
        self.assertEqual(1, plan.capture_count)

    def test_morph_canary_protocol_requires_one_role_and_exact_choice(self) -> None:
        module, args = self.parse("--runtime-protocol battleengine-morph-identity-canary-v1")
        with self.assertRaises(ValueError):
            module.validate_runtime_protocol(args)

        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            module.parse_args(["--runtime-protocol", "battleengine-morph-identity-canary-v2"])

    def test_synthetic_canary_orchestration_propagates_identity_and_skips_capture(self) -> None:
        module, args = self.parse(
            "--runtime-protocol battleengine-morph-identity-canary-v1",
            "--canary-role positiveTransform",
        )
        plan = module.validate_runtime_protocol(args)
        calls: list[tuple[object, ...]] = []
        receipt = "1" * 64
        command = "2" * 64
        marker = "MORPH_CANARY_READY"
        callbacks = {
            "attach_cdb": lambda *values: calls.append(("attach_cdb", *values)),
            "send_input": lambda *values: calls.append(("send_input", *values)) or {"unconfirmedReleaseKeys": []},
            "capture": lambda: calls.append(("capture",)),
            "release_keys": lambda: calls.append(("release_keys",)) or {"status": "failed", "bestEffort": True},
            "cleanup_cdb": lambda *values: calls.append(("cleanup_cdb", *values)),
            "stop_managed": lambda *values: calls.append(("stop_managed", *values)),
            "census": lambda: calls.append(("census",)) or 0,
        }

        result = module.run_synthetic_runtime_orchestration(
            plan,
            callbacks,
            receipt_sha256=receipt,
            command_sha256=command,
            required_marker=marker,
        )

        self.assertEqual(("attach_cdb", receipt, command, marker), calls[0])
        self.assertEqual(("send_input", "tap:Q", receipt, command, marker), calls[1])
        self.assertEqual(("cleanup_cdb", receipt, command, marker), calls[3])
        self.assertEqual(("stop_managed", receipt, command, marker), calls[4])
        self.assertNotIn(("capture",), calls)
        self.assertEqual(
            ["release_keys", "cleanup_cdb", "stop_managed", "census"],
            result["cleanup_order"],
        )
        self.assertEqual({}, result["cleanup_failures"])
        self.assertEqual(0, result["owned_process_count"])
        self.assertTrue(result["keys_released"])
        self.assertEqual({"status": "failed", "bestEffort": True}, result["best_effort_release"])

        held_result = module.run_synthetic_runtime_orchestration(
            plan,
            {
                **callbacks,
                "send_input": lambda *_: {"unconfirmedReleaseKeys": ["Q"]},
                "release_keys": lambda: {"status": "best-effort-sent", "keysReleased": True},
            },
            receipt_sha256=receipt,
            command_sha256=command,
            required_marker=marker,
        )
        self.assertFalse(held_result["keys_released"])

    def test_synthetic_cleanup_continues_after_each_phase_failure(self) -> None:
        module, args = self.parse(
            "--runtime-protocol battleengine-morph-identity-canary-v1",
            "--canary-role positiveTransform",
        )
        plan = module.validate_runtime_protocol(args)
        expected_order = [phase.name for phase in module.CANARY_CLEANUP_PHASE_PLAN]

        with tempfile.TemporaryDirectory() as tmp:
            project = module.write_runner(Path(tmp) / "runner")
            generated = project.with_name("Program.cs").read_text(encoding="utf-8")
        generated_order = re.findall(r"CANARY_CLEANUP_PHASE: ([a-z_]+)", generated)
        self.assertEqual(expected_order, generated_order)
        phase_segments = re.split(r"// CANARY_CLEANUP_PHASE: [a-z_]+", generated)[1:]
        self.assertEqual(len(expected_order), len(phase_segments))
        for phase_name, segment in zip(expected_order, phase_segments, strict=True):
            with self.subTest(generated_phase=phase_name):
                self.assertIn("try", segment)
                self.assertIn("catch (Exception ex)", segment)

        for failing_phase in expected_order:
            calls: list[str] = []

            def phase(name: str, value=None):
                def invoke(*_):
                    calls.append(name)
                    if name == failing_phase:
                        raise RuntimeError(f"injected {name} failure")
                    return value
                return invoke

            result = module.run_synthetic_runtime_orchestration(
                plan,
                {
                    "attach_cdb": lambda *_: None,
                    "send_input": lambda *_: None,
                    "capture": lambda: None,
                    "release_keys": phase("release_keys"),
                    "cleanup_cdb": phase("cleanup_cdb"),
                    "stop_managed": phase("stop_managed"),
                    "census": phase("census", 0),
                },
                receipt_sha256="1" * 64,
                command_sha256="2" * 64,
                required_marker="MORPH_CANARY_READY",
            )

            with self.subTest(failing_phase=failing_phase):
                self.assertEqual(expected_order, calls)
                self.assertEqual(expected_order, result["cleanup_order"])
                self.assertIn(failing_phase, result["cleanup_failures"])

    def test_produced_canary_artifact_matches_task1_cleanup_schema(self) -> None:
        import battleengine_morph_identity_canary as task1
        import battleengine_morph_identity_canary_test as task1_support

        module = self.live_smoke_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = task1_support.build_pe32_fixture(root / "BEA.exe")
            canonical_sha256 = hashlib.sha256(executable.read_bytes()).hexdigest()
            command_path = root / "canary.cdb"
            artifact_path = root / "private-run.json"
            log_path = root / "cdb.log"
            with patch.object(task1, "CANONICAL_SIZE", executable.stat().st_size), patch.object(
                task1, "CANONICAL_SHA256", canonical_sha256
            ):
                rendered = task1.render_private_command(executable, task1_support.TEMPLATE)
                command_path.write_bytes(rendered.text.encode("ascii"))
                produced = module.build_canary_private_artifact_payload(
                    executable_path=executable,
                    template_path=task1_support.TEMPLATE,
                    command_path=command_path,
                    receipt_sha256="1" * 64,
                    rendered=rendered,
                    source_unchanged=True,
                    copy_unchanged=True,
                    keys_released=True,
                    cdb_detached=True,
                    managed_process_stopped=True,
                    owned_process_count=0,
                )
                artifact_path.write_text(json.dumps(produced), encoding="utf-8")
                task1_support.event_log(log_path)

                self.assertEqual(task1._CLEANUP_KEYS, set(produced["cleanup"]))
                materialized = task1.materialize_run(artifact_path, log_path, "positiveTransform")

            self.assertEqual(produced["cleanup"], materialized["cleanup"])
            self.assertNotIn("bestEffortKeyRelease", produced["cleanup"])

    def test_synthetic_default_orchestration_preserves_capture_behavior(self) -> None:
        module, args = self.parse("--runtime-protocol default")
        plan = module.validate_runtime_protocol(args)
        calls: list[str] = []
        callbacks = {
            "attach_cdb": lambda *_: calls.append("attach_cdb"),
            "send_input": lambda *_: calls.append("send_input"),
            "capture": lambda: calls.append("capture"),
            "release_keys": lambda: calls.append("release_keys"),
            "cleanup_cdb": lambda *_: calls.append("cleanup_cdb"),
            "stop_managed": lambda *_: calls.append("stop_managed"),
            "census": lambda: calls.append("census") or 0,
        }

        module.run_synthetic_runtime_orchestration(
            plan,
            callbacks,
            receipt_sha256="",
            command_sha256="",
            required_marker="",
        )

        self.assertEqual(["capture", "release_keys", "cleanup_cdb", "stop_managed", "census"], calls)

    def test_canary_default_artifact_root_is_outside_repo_and_untrackable(self) -> None:
        module, args = self.parse(
            "--runtime-protocol battleengine-morph-identity-canary-v1",
            "--canary-role noInputControl",
        )

        with patch.dict(os.environ, {}, clear=True):
            artifact_root, profiles_root, armed, _, _ = module.select_artifact_root_inputs(args, "stamp")

        self.assertFalse(module.is_same_or_under(artifact_root, module.ROOT))
        self.assertFalse(module.is_same_or_under(profiles_root, module.ROOT))
        self.assertTrue(armed)

    def test_canary_fresh_root_rejects_preplanted_child_and_reparse_signal(self) -> None:
        module = self.live_smoke_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "canary-run"
            root.mkdir()
            (root / "cdb").mkdir()
            with self.assertRaises(ValueError):
                module.create_fresh_canary_artifact_root(root)

            fresh = Path(tmp) / "fresh-run"
            with patch.object(module, "has_reparse_or_symlink_ancestor", return_value=True):
                with self.assertRaises(ValueError):
                    module.create_fresh_canary_artifact_root(fresh)

    def test_canary_digest_set_requires_canonical_equality(self) -> None:
        module = self.live_smoke_module()
        canonical = "a" * 64
        labels = (
            "installed_before",
            "override_before",
            "copied_before",
            "installed_after",
            "override_after",
            "copied_after",
        )
        exact = {label: canonical for label in labels}
        module.validate_canary_digest_set(canonical, **exact)

        for label in labels:
            drifted = dict(exact)
            drifted[label] = "b" * 64
            with self.subTest(label=label), self.assertRaises(ValueError):
                module.validate_canary_digest_set(canonical, **drifted)

    def test_morph_canary_profiles_root_is_canonical_for_private_app_config(self) -> None:
        module = self.live_smoke_module()
        with tempfile.TemporaryDirectory(prefix="morph-app-config-test-") as tmp:
            artifact_root = Path(tmp) / "role"
            app_config_root = artifact_root / "app-config"
            profiles_root = app_config_root / "OnslaughtCareerEditor" / "GameProfiles"

            self.assertEqual(
                app_config_root,
                module.resolve_morph_canary_app_config_root(artifact_root, profiles_root),
            )
            with self.assertRaisesRegex(ValueError, "AppConfig"):
                module.resolve_morph_canary_app_config_root(
                    artifact_root,
                    artifact_root / "GameProfiles",
                )

    def test_morph_canary_profile_path_budget_covers_all_roles_and_max_path(self) -> None:
        module = self.live_smoke_module()
        proof_root = Path("C:\\" + ("p" * 114))
        run_roots = {
            "noInputControl": "no-input-control",
            "positiveTransform": "positive-transform",
            "positiveRepeat": "positive-repeat",
        }
        expected_lengths = {
            "noInputControl": 249,
            "positiveTransform": 251,
            "positiveRepeat": 248,
        }

        for role, run_root_name in run_roots.items():
            profiles_root = (
                proof_root
                / run_root_name
                / "app-config"
                / "OnslaughtCareerEditor"
                / "GameProfiles"
            )
            with self.subTest(role=role):
                self.assertEqual(
                    expected_lengths[role],
                    module.validate_morph_canary_profile_path_budget(profiles_root, role),
                )

        profile_name = module.MORPH_CANARY_PROFILE_NAMES["positiveTransform"]
        sentinel_name = module.MORPH_CANARY_MUTATION_SENTINEL_SAMPLE
        fixed_length = len(str(Path("C:\\") / "x" / profile_name / sentinel_name))

        def profiles_root_for(candidate_length: int) -> Path:
            component_length = candidate_length - fixed_length + 1
            return Path("C:\\") / ("p" * component_length)

        self.assertEqual(
            259,
            module.validate_morph_canary_profile_path_budget(
                profiles_root_for(259),
                "positiveTransform",
            ),
        )
        with self.assertRaisesRegex(ValueError, "legacy Win32 path budget"):
            module.validate_morph_canary_profile_path_budget(
                profiles_root_for(260),
                "positiveTransform",
            )

        non_bmp = chr(0x1F680)
        component_length = 259 - fixed_length + 1
        unicode_profiles_root = Path("C:\\") / (
            ("p" * (component_length - 2)) + (non_bmp * 2)
        )
        unicode_sentinel = unicode_profiles_root / profile_name / sentinel_name
        self.assertEqual(259, len(str(unicode_sentinel)))
        self.assertEqual(
            261,
            len(str(unicode_sentinel).encode("utf-16-le", errors="surrogatepass")) // 2,
        )
        with self.assertRaisesRegex(ValueError, "legacy Win32 path budget"):
            module.validate_morph_canary_profile_path_budget(
                unicode_profiles_root,
                "positiveTransform",
            )

    def test_generated_morph_runner_separates_ambient_and_effective_executables(self) -> None:
        text = self.script_text()

        self.assertIn('env["ONSLAUGHT_APP_CONFIG_ROOT"] = str(canary_app_config_root)', text)
        self.assertIn(
            "string.Equals(installedHashAfter, installedHashBefore, StringComparison.OrdinalIgnoreCase)",
            text,
        )
        self.assertNotIn(
            "!string.Equals(installedHashBefore, canonicalExecutableSha256, StringComparison.OrdinalIgnoreCase)",
            text,
        )
        self.assertNotIn(
            "!string.Equals(copiedExecutableHashBefore, installedHashBefore, StringComparison.OrdinalIgnoreCase)",
            text,
        )

    def test_generated_morph_runner_uses_compact_role_local_profile_names(self) -> None:
        text = self.script_text()

        self.assertIn('"noInputControl" => "mc-c"', text)
        self.assertIn('"positiveTransform" => "mc-p"', text)
        self.assertIn('"positiveRepeat" => "mc-r"', text)
        self.assertIn("ProfileName: roleProfileName", text)
        self.assertNotIn('ProfileName: $"morph-canary-{role}-', text)

    def stable_extra_patch_keys(self) -> set[str]:
        tree = ast.parse(self.script_text(), filename=str(SCRIPT))
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(target, ast.Name) and target.id == "STABLE_EXTRA_PATCH_KEYS" for target in node.targets):
                continue
            return set(ast.literal_eval(node.value))

        self.fail("STABLE_EXTRA_PATCH_KEYS was not found.")

    def test_stable_frontend_color_presets_are_live_smoke_allowlisted(self) -> None:
        keys = self.stable_extra_patch_keys()

        self.assertIn("frontend_clear_screen_dark_red", keys)
        self.assertIn("frontend_clear_screen_dark_green", keys)
        self.assertIn("frontend_clear_screen_black", keys)

    def experimental_extra_patch_keys(self) -> set[str]:
        tree = ast.parse(self.script_text(), filename=str(SCRIPT))
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(target, ast.Name) and target.id == "EXPERIMENTAL_EXTRA_PATCH_KEYS" for target in node.targets):
                continue
            return set(ast.literal_eval(node.value))

        self.fail("EXPERIMENTAL_EXTRA_PATCH_KEYS was not found.")

    def test_free_camera_keyboard_forward_hook_is_experimental_allowlisted(self) -> None:
        keys = self.experimental_extra_patch_keys()

        self.assertIn("free_camera_aurore_gate_bypass", keys)
        self.assertIn("free_camera_keyboard_forward_q_hook", keys)
        self.assertIn("free_camera_keyboard_backward_q_hook", keys)
        self.assertIn("free_camera_keyboard_strafe_left_q_hook", keys)
        self.assertIn("free_camera_keyboard_strafe_right_q_hook", keys)
        self.assertIn("free_camera_keyboard_yaw_left_q_hook", keys)
        self.assertIn("free_camera_keyboard_yaw_right_q_hook", keys)
        self.assertIn("free_camera_keyboard_pitch_up_q_hook", keys)
        self.assertIn("free_camera_keyboard_pitch_down_q_hook", keys)
        self.assertIn("pause_o_scan_initializer_experiment", keys)

    def test_control_option_cli_is_safe_copy_bounded(self) -> None:
        text = self.script_text()

        self.assertIn("--controller-configuration", text)
        self.assertIn("--persist-controller-config-in-options", text)
        self.assertIn("--level-id", text)
        self.assertIn("--sharpen-mouse-look", text)
        self.assertIn("--profile-preset-id", text)
        self.assertIn("--allow-background-window-messages", text)
        self.assertIn("--arm-background-window-messages", text)
        self.assertIn("--pre-input-capture-count", text)
        self.assertIn("--focus-before-pre-input-capture", text)
        self.assertIn("--enable-cdb-observer", text)
        self.assertIn("--arm-cdb-observer", text)
        self.assertIn("--cdb-command-file", text)
        self.assertIn("--cdb-log-ready-timeout-ms", text)
        self.assertIn("--cdb-post-attach-wait-seconds", text)
        self.assertIn("--cdb-attach-phase", text)
        self.assertIn("--bind-forward-qe-for-input-isolation", text)
        self.assertIn("--bind-fire-qe-for-weapon-handoff", text)
        self.assertIn("--bind-look-down-qe-for-config2-forward-discovery", text)
        self.assertIn("--bind-config2-census-row-qe", text)
        self.assertIn("movement-forward", text)
        self.assertIn("look-right", text)
        self.assertIn("ALLOW BACKGROUND BEA WINDOW MESSAGES", text)
        self.assertIn("ATTACH CDB TO SAFE COPY BEA", text)
        self.assertIn("Refusing background-window input without", text)
        self.assertIn("--arm-background-window-messages requires --allow-background-window-messages", text)
        self.assertIn("Refusing CDB observer attach without", text)
        self.assertIn("--arm-cdb-observer requires --enable-cdb-observer", text)
        self.assertIn("args.pre_input_capture_count < 0 or args.pre_input_capture_count > 3", text)
        self.assertIn("args.cdb_log_ready_timeout_ms < 1000 or args.cdb_log_ready_timeout_ms > 30000", text)
        self.assertIn("args.cdb_post_attach_wait_seconds < 0 or args.cdb_post_attach_wait_seconds > 15", text)
        self.assertIn('"after-window", "after-launch"', text)
        self.assertIn("args.level_id < 0 or args.level_id > 9999", text)
        self.assertIn("args.controller_configuration < 0 or args.controller_configuration > 4", text)
        self.assertIn("args.persist_controller_config_in_options and args.controller_configuration == 0", text)
        self.assertIn("qe_lever_count > 1", text)
        self.assertIn("args.bind_fire_qe_for_weapon_handoff", text)
        self.assertIn("args.bind_look_down_qe_for_config2_forward_discovery and args.controller_configuration != 2", text)
        self.assertIn("args.bind_config2_census_row_qe and args.controller_configuration != 2", text)
        self.assertIn('launch_arguments = ["-skipfmv"]', text)
        self.assertIn('launch_arguments.extend(["-level", str(args.level_id)])', text)
        self.assertIn('launch_arguments.extend(["-configuration", str(args.controller_configuration)])', text)
        self.assertIn('env["ONSLAUGHT_LIVE_PERSISTED_CONTROLLER_CONFIG"]', text)

    def test_music_mute_control_launch_args_are_allowlisted(self) -> None:
        module = self.live_smoke_module()

        base = SimpleNamespace(
            level_id=100,
            controller_configuration=0,
            launch_nomusic=False,
            launch_nosound=False,
        )
        self.assertEqual(["-skipfmv", "-level", "100"], module.build_launch_arguments(base))

        no_music = SimpleNamespace(
            level_id=100,
            controller_configuration=0,
            launch_nomusic=True,
            launch_nosound=False,
        )
        self.assertEqual(["-skipfmv", "-level", "100", "-nomusic"], module.build_launch_arguments(no_music))

        no_sound = SimpleNamespace(
            level_id=100,
            controller_configuration=0,
            launch_nomusic=False,
            launch_nosound=True,
        )
        self.assertEqual(["-skipfmv", "-level", "100", "-nosound"], module.build_launch_arguments(no_sound))

        text = self.script_text()
        self.assertIn("--launch-nomusic", text)
        self.assertIn("--launch-nosound", text)
        self.assertIn("args.launch_nomusic and args.launch_nosound", text)

    def test_external_runtime_artifact_base_requires_explicit_arm(self) -> None:
        text = self.script_text()

        self.assertIn('ARTIFACT_BASE_ENV = "ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE"', text)
        self.assertIn('ARTIFACT_BASE_ARM_ENV = "ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE_ARM"', text)
        self.assertIn("artifact_base_env = os.environ.get(ARTIFACT_BASE_ENV", text)
        self.assertIn("artifact_base_arm_env = os.environ.get(ARTIFACT_BASE_ARM_ENV", text)
        self.assertIn("select_artifact_root_inputs", text)
        self.assertIn("explicit_artifact_root = bool(args.artifact_root)", text)
        self.assertIn('profiles_root_raw = Path(args.profiles_root) if args.profiles_root else artifact_root_raw / "GameProfiles"', text)
        self.assertIn("and not explicit_artifact_root", text)
        self.assertIn("artifact_base_arm_env == EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE", text)
        self.assertIn('APPROVED_ARTIFACT_BASE_PARENTS_ENV = "ONSLAUGHT_LIVE_RUNTIME_APPROVED_ARTIFACT_BASE_PARENTS"', text)
        self.assertIn("configured_approved_external_artifact_base_parents", text)
        self.assertIn("outside configured approved private artifact parent", text)
        self.assertIn("Refusing external artifact root without --arm-external-artifact-root", text)
        self.assertIn("ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE_ARM", text)

    def test_external_runtime_artifact_base_selection_is_bounded(self) -> None:
        module = self.live_smoke_module()
        args = SimpleNamespace(
            artifact_root="",
            profiles_root="",
            arm_external_artifact_root="",
        )

        with patch.dict("os.environ", {}, clear=True):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, module.ROOT / "subagents" / "winui-safe-copy-live-runtime" / "stamp")
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertFalse(armed)
            self.assertFalse(env_armed)
            self.assertEqual(artifact_parent, module.ROOT / "subagents" / "winui-safe-copy-live-runtime")

        with patch.dict("os.environ", {module.ARTIFACT_BASE_ENV: r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime"}, clear=True):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, Path(r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime") / "stamp")
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertFalse(armed)
            self.assertFalse(env_armed)
            self.assertEqual(artifact_parent, Path(r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime"))

        with patch.dict(
            "os.environ",
            {
                module.ARTIFACT_BASE_ENV: r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime",
                module.ARTIFACT_BASE_ARM_ENV: module.EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE,
            },
            clear=True,
        ):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, Path(r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime") / "stamp")
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertTrue(armed)
            self.assertTrue(env_armed)
            self.assertEqual(artifact_parent, Path(r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime"))

    def test_env_artifact_base_arm_does_not_authorize_explicit_external_artifact_root(self) -> None:
        module = self.live_smoke_module()
        args = SimpleNamespace(
            artifact_root=r"D:\SomeOtherRuntimeRoot\run1",
            profiles_root="",
            arm_external_artifact_root="",
        )

        with patch.dict(
            "os.environ",
            {
                module.ARTIFACT_BASE_ENV: r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime",
                module.ARTIFACT_BASE_ARM_ENV: module.EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE,
            },
            clear=True,
        ):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, Path(r"D:\SomeOtherRuntimeRoot\run1"))
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertFalse(armed)
            self.assertFalse(env_armed)
            self.assertEqual(artifact_parent, Path(r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime"))

        args.arm_external_artifact_root = module.EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE
        with patch.dict("os.environ", {}, clear=True):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, Path(r"D:\SomeOtherRuntimeRoot\run1"))
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertTrue(armed)
            self.assertFalse(env_armed)
            self.assertEqual(artifact_parent, module.ROOT / "subagents" / "winui-safe-copy-live-runtime")

    def test_approved_external_artifact_parent_rejects_unapproved_roots(self) -> None:
        module = self.live_smoke_module()

        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(
                module.is_approved_external_artifact_parent(
                    Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime")
                )
            )

        with patch.dict("os.environ", {module.APPROVED_ARTIFACT_BASE_PARENTS_ENV: r"Z:\ConfiguredScratch"}, clear=True):
            self.assertTrue(
                module.is_approved_external_artifact_parent(
                    Path(r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime")
                )
            )
            self.assertTrue(
                module.is_approved_external_artifact_parent(
                    Path(r"Z:\ConfiguredScratch\winui-safe-copy-live-runtime\run")
                )
            )
            self.assertFalse(
                module.is_approved_external_artifact_parent(
                    Path(r"D:\SomeOtherRuntimeRoot\winui-safe-copy-live-runtime")
                )
            )

    def test_generated_runner_materializes_control_options_with_narrow_claims(self) -> None:
        text = self.script_text()

        self.assertIn("ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON", text)
        self.assertIn("ONSLAUGHT_LIVE_PROFILE_PRESET_ID", text)
        self.assertIn("ONSLAUGHT_LIVE_SHARPEN_MOUSE_LOOK", text)
        self.assertIn("ONSLAUGHT_LIVE_PERSISTED_CONTROLLER_CONFIG", text)
        self.assertIn("ONSLAUGHT_LIVE_PRE_INPUT_CAPTURE_COUNT", text)
        self.assertIn("ONSLAUGHT_LIVE_FOCUS_BEFORE_PRE_INPUT_CAPTURE", text)
        self.assertIn("ONSLAUGHT_LIVE_ALLOW_BACKGROUND_WINDOW_MESSAGES", text)
        self.assertIn("ONSLAUGHT_LIVE_BACKGROUND_WINDOW_MESSAGES_ARM", text)
        self.assertIn("ONSLAUGHT_LIVE_CDB_OBSERVER_ENABLED", text)
        self.assertIn("ONSLAUGHT_LIVE_CDB_START_SCRIPT", text)
        self.assertIn("ONSLAUGHT_LIVE_CDB_COMMAND_FILE", text)
        self.assertIn("ONSLAUGHT_LIVE_CDB_LOG_PATH", text)
        self.assertIn("ONSLAUGHT_LIVE_CDB_LOG_READY_TIMEOUT_MS", text)
        self.assertIn("ONSLAUGHT_LIVE_CDB_POST_ATTACH_WAIT_SECONDS", text)
        self.assertIn("ONSLAUGHT_LIVE_CDB_ATTACH_PHASE", text)
        self.assertIn("ONSLAUGHT_LIVE_BIND_FORWARD_QE_FOR_INPUT_ISOLATION", text)
        self.assertIn("ONSLAUGHT_LIVE_BIND_FIRE_QE_FOR_WEAPON_HANDOFF", text)
        self.assertIn("ONSLAUGHT_LIVE_BIND_LOOK_DOWN_QE_FOR_CONFIG2_FORWARD_DISCOVERY", text)
        self.assertIn("ONSLAUGHT_LIVE_BIND_CONFIG2_CENSUS_ROW_QE", text)
        self.assertIn("startInfo.ArgumentList.Add(\"-AllowBackgroundWindowMessages\")", text)
        self.assertIn("startInfo.ArgumentList.Add(\"-BackgroundWindowMessagesArm\")", text)
        self.assertIn("allowBackgroundWindowMessages", text)
        self.assertIn("ProfilePresetId: string.IsNullOrWhiteSpace(profilePresetId) ? null : profilePresetId", text)
        self.assertIn("prepared.ProfilePresetId", text)
        self.assertIn("prepared.ProfilePresetDisplayName", text)
        self.assertIn("prepared.ProfilePresetProofStatus", text)
        self.assertIn("prepared.ProfileDefaultControllerConfiguration", text)
        self.assertIn("prepared.ProfileDefaultPersistControllerConfigInOptions", text)
        self.assertIn("prepared.ProfileDefaultSharpenMouseLook", text)
        self.assertIn("GameProfileControlOptionsService.ApplyToSafeCopy", text)
        self.assertIn("GameProfileControlOptionsService.SharperMouseLookSensitivity", text)
        self.assertIn("ControllerConfigP1Override: persistedControllerConfig", text)
        self.assertIn("ControllerConfigP2Override: persistedControllerConfig", text)
        self.assertIn("KeybindRows: inputIsolationKeybindRows", text)
        self.assertIn("Player1Token = \"Q\"", text)
        self.assertIn("Player2Token = \"E\"", text)
        self.assertIn("EntryId = 0x12", text)
        self.assertIn("ActionLabel = \"Fire weapon\"", text)
        self.assertIn("MirrorEntryId = 0x13", text)
        self.assertIn("EntryId = 0x1c", text)
        self.assertIn("Config2CensusRowQe", text)
        self.assertIn('"movement-forward" => ("Movement", "Forward", 0x1f, false)', text)
        self.assertIn('"movement-left" => ("Movement", "Left", 0x1d, false)', text)
        self.assertIn('"movement-right" => ("Movement", "Right", 0x1e, false)', text)
        self.assertIn('"look-right" => ("Look", "Right", 0x1b, true)', text)
        self.assertIn("ActionLabel = \"Down\"", text)
        self.assertIn("controlOptions = controlOptions is null", text)
        self.assertIn("requestedPersistedControllerConfig = persistedControllerConfig > 0", text)
        self.assertIn("requestedControllerConfig = persistedControllerConfig > 0 ? persistedControllerConfig : (int?)null", text)
        self.assertIn("controlOptions.ManifestPath", text)
        self.assertIn("controlOptions.ProofStatus", text)
        self.assertIn("hashBefore = controlOptions.HashBefore", text)
        self.assertIn("hashAfter = controlOptions.HashAfter", text)
        self.assertIn("hashAfterPrepare = copiedDefaultOptionsHashPrepared", text)
        self.assertIn("changedRanges = copiedDefaultOptionsControlOptionDiffs", text)
        self.assertIn("proofLever =", text)
        self.assertIn("requestedWeaponFireQe", text)
        self.assertIn("copied-defaultoptions-input-isolation-forward-qe", text)
        self.assertIn("copied-defaultoptions-weapon-fire-qe", text)
        self.assertIn("copied-defaultoptions-config2-forward-discovery-look-down-qe", text)
        self.assertIn("copied-defaultoptions-config2-census-", text)
        self.assertIn("copied-defaultoptions-mouse-sensitivity-only", text)
        self.assertIn("copied-defaultoptions-controller-config-only", text)
        self.assertIn("copied-defaultoptions-mouse-sensitivity-and-controller-config", text)
        self.assertIn("persisted into the copied defaultoptions.bea", text)
        self.assertIn("not a copied defaultoptions.bea controller-config patch", text)
        self.assertIn("they do not prove improved runtime control feel", text)

    def test_generated_runner_can_attach_cdb_observer_to_exact_pid(self) -> None:
        text = self.script_text()

        self.assertIn("StartCdbObserver(", text)
        self.assertIn('string.Equals(cdbAttachPhase, "after-launch"', text)
        self.assertIn('string.Equals(cdbAttachPhase, "after-window"', text)
        self.assertIn("CleanupCdbObserver", text)
        self.assertIn("CdbLogLength", text)
        self.assertIn("inputCdbWindows", text)
        self.assertIn("logStartByte", text)
        self.assertIn("logEndByte", text)
        self.assertIn("WaitForNoBeaProcesses", text)
        self.assertIn("cdb-observer.json", text)
        self.assertIn("cdbObserverEnabled", text)
        self.assertIn("cdbObserverSucceeded", text)
        self.assertIn("JsonStringIn", text)
        self.assertIn("cdbObserverCleanupSucceeded", text)
        self.assertIn('JsonStringIn(cdbObserverCleanupResult.Value, "status", "stopped", "already-exited")', text)
        self.assertIn('JsonNullableInt(cdbObserverResult.Value, "cdbProcessId").HasValue', text)
        self.assertIn("cdbObserver = cdbObserverEnabled", text)
        self.assertIn("Exact-PID CDB observer attach", text)
        self.assertIn("not uninstrumented gameplay proof", text)
        self.assertIn("not online/network proof", text)
        self.assertIn("cdbObserverSucceeded &&", text)

    def test_cdb_observer_command_file_is_bounded_to_observer_commands(self) -> None:
        text = self.script_text()
        module = self.live_smoke_module()
        command_files = [
            ROOT / "tools" / "runtime-probes" / "local-multiplayer-level850-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "local-multiplayer-level850-input-isolation-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "local-multiplayer-level850-input-state-delta-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "safe-copy-music-selection-decode-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "free-camera-toggle-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "free-camera-movement-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "free-camera-pause-context-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "free-camera-key-census-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "pause-o-scan-initializer-observer.cdb.txt",
            ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-fire-handoff-observer.cdb.txt",
        ]
        command_file = command_files[0]
        input_isolation_command_file = command_files[1]
        input_state_delta_command_file = command_files[2]
        movement_command_file = command_files[5]
        pause_command_file = command_files[6]
        key_census_command_file = command_files[7]
        pause_o_scan_command_file = command_files[8]
        fire_handoff_command_file = command_files[9]
        command_text = command_file.read_text(encoding="utf-8")
        input_isolation_command_text = input_isolation_command_file.read_text(encoding="utf-8")
        input_state_delta_command_text = input_state_delta_command_file.read_text(encoding="utf-8")
        movement_command_text = movement_command_file.read_text(encoding="utf-8")
        pause_command_text = pause_command_file.read_text(encoding="utf-8")
        key_census_command_text = key_census_command_file.read_text(encoding="utf-8")
        pause_o_scan_command_text = pause_o_scan_command_file.read_text(encoding="utf-8")
        fire_handoff_command_text = fire_handoff_command_file.read_text(encoding="utf-8")

        self.assertIn("validate_cdb_observer_command_file", text)
        self.assertIn("Only tracked observer-style .echo/vertarget/lm/u/dd/g commands and bp[/1] print-and-continue commands", text)
        self.assertIn("Refusing CDB observer command file outside tracked tools/runtime-probes", text)
        self.assertIn("OBSERVER_BREAKPOINT_DISALLOWED_RE", text)
        for active_command_file in command_files:
            module.validate_cdb_observer_command_file(active_command_file)

        self.assertIn("CGame__IsMultiplayer", command_text)
        self.assertIn("CWorld__IsMultiplayerMode", command_text)
        self.assertIn("CGame__Render", command_text)
        self.assertIn("CEngine__SetNumViewpoints", command_text)
        self.assertIn("CEngine__SetViewpoint", command_text)
        self.assertIn("CController__SendButtonAction", input_isolation_command_text)
        self.assertIn("CPlayer__ReceiveButtonAction", input_isolation_command_text)
        self.assertIn("CBattleEngineWalkerPart__ForwardEntry", input_state_delta_command_text)
        self.assertIn("CBattleEngineWalkerPart__ForwardStateStore", input_state_delta_command_text)
        self.assertIn("CBattleEngineJetPart__ThrustEntry", input_state_delta_command_text)
        self.assertIn("CBattleEngineJetPart__ThrustStateStore", input_state_delta_command_text)
        self.assertIn("bp 0042e4d0", input_isolation_command_text)
        self.assertIn("bp 004d3110", input_isolation_command_text)
        self.assertIn("bp 00410310", input_state_delta_command_text)
        self.assertIn("bp 00412d80", input_state_delta_command_text)
        self.assertIn("bp 00412ee1", input_state_delta_command_text)
        self.assertIn("FreeCameraKeyboardQRemap_Cave", movement_command_text)
        self.assertIn("CControllableCamera__PrepareForInterpolation_Delta", movement_command_text)
        self.assertIn("CPCController__GetKeyOnce", pause_command_text)
        self.assertIn("PlatformInput__GetKeyOnceCore", pause_command_text)
        self.assertIn("PlatformInput__ConsumeKeyOnce", pause_command_text)
        self.assertIn("key=79", pause_command_text)
        self.assertIn("FreeCameraKeyCensus__GetKeyOnce", key_census_command_text)
        self.assertIn("FreeCameraKeyCensus__GetKeyOnceCore", key_census_command_text)
        self.assertIn("FreeCameraKeyCensus__ConsumeKeyOnce", key_census_command_text)
        self.assertIn("FreeCameraKeyCensus__SendButtonAction", key_census_command_text)
        self.assertIn("FreeCameraKeyCensus__KeyBytes", key_census_command_text)
        self.assertIn("PauseOScan__GetKeyOnce", pause_o_scan_command_text)
        self.assertIn("PauseOScan__SendButtonAction", pause_o_scan_command_text)
        self.assertIn("PauseOScan__Pause", pause_o_scan_command_text)
        self.assertIn("PauseOScan__UnPause", pause_o_scan_command_text)
        self.assertIn("dd 005144cd L1", pause_o_scan_command_text)
        self.assertIn("dd 008892dc L220", pause_o_scan_command_text)
        self.assertIn("FIRE_HANDOFF_HOOK_TARGET", fire_handoff_command_text)
        self.assertIn("CController__SendButtonAction", fire_handoff_command_text)
        self.assertIn("CBattleEngineWalkerPart__FireWeapon", fire_handoff_command_text)
        self.assertIn("CRound__SpawnConfiguredProjectile", fire_handoff_command_text)
        self.assertIn("bp /1 004725d0", command_text)
        self.assertIn("bp /1 0044a020", command_text)
        malicious_lines = [
            '.shell calc.exe',
            'bp 0042e4d0 ".printf \\"ok\\\\n\\"; .shell calc.exe; g"',
            'bp 0042e4d0 "r @eax=1; .printf \\"ok\\\\n\\"; g"',
            'bp 0042e4d0 ".printf \\"ok\\\\n\\"; ed 00400000 1; g"',
            '.dump /ma out.dmp',
            '.writemem out.bin 00400000 00400010',
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for index, malicious_line in enumerate(malicious_lines):
                malicious_file = Path(tmp) / f"bad-{index}.cdb.txt"
                malicious_file.write_text(f"{malicious_line}\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    module.validate_cdb_observer_command_file(malicious_file)

    def test_generated_runner_can_capture_before_scoped_input(self) -> None:
        text = self.script_text()

        self.assertIn("preInputCaptureCount = BoundedIntEnv", text)
        self.assertIn("focusBeforePreInputCapture", text)
        self.assertIn("safe-copy-pre-input-focus.json", text)
        self.assertIn('"wait:1"', text)
        self.assertIn("preInputFocus", text)
        self.assertIn("safe-copy-pre-input-frame.png", text)
        self.assertIn("safe-copy-pre-input-frame-{i + 1:D2}.png", text)
        self.assertIn("preInputCaptureCount", text)

    def test_generated_runner_can_capture_after_each_scoped_input_sequence(self) -> None:
        text = self.script_text()

        self.assertIn("--capture-after-each-input-sequence", text)
        self.assertIn("--after-input-capture-delay-ms", text)
        self.assertIn("ONSLAUGHT_LIVE_CAPTURE_AFTER_EACH_INPUT_SEQUENCE", text)
        self.assertIn("ONSLAUGHT_LIVE_AFTER_INPUT_CAPTURE_DELAY_MS", text)
        self.assertIn("captureAfterEachInputSequence", text)
        self.assertIn("afterInputCaptureDelayMs", text)
        self.assertIn("safe-copy-after-input-{i + 1:D2}-frame.png", text)
        self.assertIn("safe-copy-after-input-{i + 1:D2}-frame.json", text)

    def test_music_swap_preset_runtime_path_uses_appcore_preset_builder(self) -> None:
        text = self.script_text()

        self.assertIn("--music-swap-preset-id", text)
        self.assertIn("MUSIC_SWAP_PRESETS", text)
        self.assertIn("use-bea02-for-bea01", text)
        self.assertIn("use-bea01-for-bea02", text)
        self.assertIn("use-bea02-for-bea04", text)
        self.assertIn("ONSLAUGHT_LIVE_MUSIC_SWAP_PRESET_ID", text)
        self.assertIn("BuildSafeCopyMusicSwapPresetOptions", text)
        self.assertIn("MusicSwapPresetId =", text)
        self.assertIn("stage_music_replacement = args.stage_music_replacement or bool(music_swap_preset_id)", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
