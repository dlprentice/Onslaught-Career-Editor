#!/usr/bin/env python3
"""Focused tests for the safe-copy live runtime smoke helper allowlist."""

from __future__ import annotations

import ast
import importlib.util
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
        self.assertIn("artifact_parent_raw = Path(artifact_base_env) if artifact_base_env else default_artifact_parent_raw", text)
        self.assertIn('profiles_root_raw = Path(args.profiles_root) if args.profiles_root else artifact_root_raw / "GameProfiles"', text)
        self.assertIn("and not explicit_artifact_root", text)
        self.assertIn("artifact_base_arm_env == EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE", text)
        self.assertIn('APPROVED_EXTERNAL_ARTIFACT_BASE_PARENTS = (Path(r"G:\\OnslaughtRuntimeProofArchive"),)', text)
        self.assertIn("outside approved private archive parent", text)
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

        with patch.dict("os.environ", {module.ARTIFACT_BASE_ENV: r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime"}, clear=True):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime") / "stamp")
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertFalse(armed)
            self.assertFalse(env_armed)
            self.assertEqual(artifact_parent, Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime"))

        with patch.dict(
            "os.environ",
            {
                module.ARTIFACT_BASE_ENV: r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime",
                module.ARTIFACT_BASE_ARM_ENV: module.EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE,
            },
            clear=True,
        ):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime") / "stamp")
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertTrue(armed)
            self.assertTrue(env_armed)
            self.assertEqual(artifact_parent, Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime"))

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
                module.ARTIFACT_BASE_ENV: r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime",
                module.ARTIFACT_BASE_ARM_ENV: module.EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE,
            },
            clear=True,
        ):
            artifact_root, profiles_root, armed, env_armed, artifact_parent = module.select_artifact_root_inputs(args, "stamp")
            self.assertEqual(artifact_root, Path(r"D:\SomeOtherRuntimeRoot\run1"))
            self.assertEqual(profiles_root, artifact_root / "GameProfiles")
            self.assertFalse(armed)
            self.assertFalse(env_armed)
            self.assertEqual(artifact_parent, Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime"))

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

        self.assertTrue(
            module.is_approved_external_artifact_parent(
                Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime")
            )
        )
        self.assertTrue(
            module.is_approved_external_artifact_parent(
                Path(r"G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime\run")
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
