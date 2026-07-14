#!/usr/bin/env python3
"""Opt-in live playable-copied-game launch/capture/stop proof for the WinUI/AppCore patch path."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any, Callable, Mapping, NamedTuple

import battleengine_morph_identity_authority as morph_authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
ARM_PHRASE = "LAUNCH SAFE COPY BEA"
EXPERIMENTAL_PATCH_ARM_PHRASE = "ALLOW EXPERIMENTAL LIVE SMOKE PATCH"
BACKGROUND_WINDOW_MESSAGES_ARM_PHRASE = "ALLOW BACKGROUND BEA WINDOW MESSAGES"
EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE = "ALLOW EXTERNAL LIVE SMOKE ARTIFACT ROOT"
EXTERNAL_PROFILES_ROOT_ARM_PHRASE = "ALLOW EXTERNAL LIVE SMOKE PROFILES ROOT"
ARTIFACT_BASE_ENV = "ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE"
ARTIFACT_BASE_ARM_ENV = "ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE_ARM"
APPROVED_ARTIFACT_BASE_PARENTS_ENV = "ONSLAUGHT_LIVE_RUNTIME_APPROVED_ARTIFACT_BASE_PARENTS"
# Env-selected default artifact roots are intentionally locally configured.
# Other one-off external roots must use --artifact-root plus the explicit CLI arm.
APPROVED_EXTERNAL_ARTIFACT_BASE_PARENTS: tuple[Path, ...] = ()
CDB_OBSERVER_ARM_PHRASE = "ATTACH CDB TO SAFE COPY BEA"
DEFAULT_RUNTIME_PROTOCOL = "default"
MORPH_CANARY_RUNTIME_PROTOCOL = "battleengine-morph-identity-canary-v1"
WALKER_TRAJECTORY_RUNTIME_PROTOCOL = "battleengine-walker-trajectory-v1"
MORPH_CANARY_ROLES = ("noInputControl", "positiveTransform", "positiveRepeat")
MORPH_CANARY_PROFILE_NAMES = {
    "noInputControl": "mc-c",
    "positiveTransform": "mc-p",
    "positiveRepeat": "mc-r",
}
MORPH_CANARY_MUTATION_SENTINEL_SAMPLE = (
    ".onslaught-directory-guard-" + ("0" * 32) + ".tmp"
)
LEGACY_WIN32_MAX_PATH = 260
MORPH_CANARY_READY_MARKER = "MORPH_CANARY_READY"
RUNNER_MARKER = ".winui-safe-copy-live-runtime-runner"
REPARSE_POINT_FLAG = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
BASE_PATCH_KEYS = ["resolution_gate", "force_windowed"]
MODERN_GRAPHICS_PATCH_KEYS = ["extra_graphics_default_on", "ignore_cardid_tweak_overrides"]
STABLE_EXTRA_PATCH_KEYS = {
    "frontend_clear_screen_dark_red",
    "frontend_clear_screen_dark_green",
    "frontend_clear_screen_black",
    "goodies_gallery_display_unlock",
    "version_overlay_use_patched_format_pointer",
}
EXPERIMENTAL_EXTRA_PATCH_KEYS = {
    "free_camera_aurore_gate_bypass",
    "free_camera_keyboard_forward_q_hook",
    "free_camera_keyboard_backward_q_hook",
    "free_camera_keyboard_strafe_left_q_hook",
    "free_camera_keyboard_strafe_right_q_hook",
    "free_camera_keyboard_yaw_left_q_hook",
    "free_camera_keyboard_yaw_right_q_hook",
    "free_camera_keyboard_pitch_up_q_hook",
    "free_camera_keyboard_pitch_down_q_hook",
    "pause_o_scan_initializer_experiment",
    "skip_auto_toggle",
}
MUSIC_SWAP_PRESETS = {
    "use-bea02-for-bea01": ("BEA_01(Master).ogg", "BEA_02(Master).ogg"),
    "use-bea01-for-bea02": ("BEA_02(Master).ogg", "BEA_01(Master).ogg"),
    "use-bea02-for-bea04": ("BEA_04(Master).ogg", "BEA_02(Master).ogg"),
}
CONFIG2_CENSUS_ROWS = (
    "movement-forward",
    "movement-backward",
    "movement-left",
    "movement-right",
    "look-up",
    "look-down",
    "look-left",
    "look-right",
)


class RuntimeProtocolPlan(NamedTuple):
    runtime_protocol: str
    canary_role: str
    launch_arguments: list[str]
    patch_keys: list[str]
    apply_windowed_compatibility_patch: bool
    transform_entry_id: int | None
    transform_keyboard_device_code: int | None
    transform_player1_token: str
    transform_player2_token: str
    capture_count: int
    input_sequences: list[str]
    include_modern_graphics: bool
    stage_music_replacement: bool
    allow_background_window_messages: bool
    cdb_observer_enabled: bool
    cdb_attach_phase: str
    required_cdb_log_marker: str
    input_step_delay_ms: int
    cdb_log_ready_timeout_ms: int


class CanaryCleanupPhase(NamedTuple):
    name: str
    callback_uses_binding: bool
    failure_label: str
    csharp_action: str
    csharp_failure: str


CANARY_CLEANUP_PHASE_PLAN = (
    CanaryCleanupPhase(
        name="release_keys",
        callback_uses_binding=False,
        failure_label="release-keys",
        csharp_action=r"""
            if (managed is not null && !string.IsNullOrWhiteSpace(receiptSha256))
            {
                string releaseArtifact = Path.Combine(artifactRoot, "input", "canary-release-keys.json");
                if (inputDeliveryAttempted)
                {
                    if (!ValidateCanaryBinding(
                            powershellExe,
                            runtimeIdentityModule,
                            runtimeReceiptPath,
                            receiptSha256,
                            cdbCommandFile,
                            expectedCommandSha256,
                            templatePath,
                            expectedTemplateSha256,
                            true,
                            out string releaseBindingFailure))
                        throw new InvalidOperationException("Runtime binding changed before best-effort key release: " + releaseBindingFailure);
                    AssertFreshCanaryWriteTarget(releaseArtifact, artifactRoot);
                }
                _ = BestEffortReleaseCanaryKeys(
                    inputDeliveryAttempted,
                    powershellExe,
                    inputScript,
                    managed.ProcessId,
                    observedMainWindowHandle,
                    managed.ExecutablePath,
                    managed.WorkingDirectory,
                    inputStepDelayMs,
                    releaseArtifact,
                    runtimeReceiptPath,
                    receiptSha256);
            }
        """,
        csharp_failure="",
    ),
    CanaryCleanupPhase(
        name="validate_cdb",
        callback_uses_binding=True,
        failure_label="cdb-pre-stop",
        csharp_action=r"""
            cdbPreStopResult = ValidateExactCdbObserverForManagedStop(
                cdbAttachResult,
                powershellExe,
                runtimeIdentityModule,
                runtimeReceiptPath,
                receiptSha256,
                cdbCommandFile,
                expectedCommandSha256,
                templatePath,
                expectedTemplateSha256,
                cdbLogPath,
                requiredLogMarker,
                boundCdbLogStream,
                out boundCdbProcess);
            if (!JsonStringIn(cdbPreStopResult, "status", "ready-for-managed-stop"))
                failure = string.IsNullOrWhiteSpace(failure)
                    ? "Exact CDB observer was not bound immediately before managed stop."
                    : failure + " | Exact CDB observer was not bound immediately before managed stop.";
        """,
        csharp_failure=r"""
            cdbPreStopResult = JsonPayload(new { status = "failed", receiptBound = false, processBound = false, error = ex.GetType().Name + ": " + ex.Message });
        """,
    ),
    CanaryCleanupPhase(
        name="stop_managed",
        callback_uses_binding=True,
        failure_label="managed-stop",
        csharp_action=r"""
            stopResult = StopReceiptBoundManagedProcess(
                managed,
                profilesRoot,
                powershellExe,
                runtimeIdentityModule,
                runtimeReceiptPath,
                receiptSha256,
                cdbCommandFile,
                expectedCommandSha256,
                templatePath,
                expectedTemplateSha256,
                out stopReceiptBound,
                out string stopFailure,
                out runnerStopCallBeginTimestamp,
                out runnerStopCallReturnedTimestamp);
            if (managed is not null && !stopReceiptBound)
                failure = string.IsNullOrWhiteSpace(failure)
                    ? "Managed stop was not receipt-bound: " + stopFailure
                    : failure + " | Managed stop was not receipt-bound: " + stopFailure;
            else if (managed is not null && stopResult?.Success != true)
                failure = string.IsNullOrWhiteSpace(failure)
                    ? "Exact managed stop failed: " + (stopResult?.Message ?? "no stop result")
                    : failure + " | Exact managed stop failed: " + (stopResult?.Message ?? "no stop result");
        """,
        csharp_failure=r"""
            stopReceiptBound = false;
        """,
    ),
    CanaryCleanupPhase(
        name="cleanup_cdb",
        callback_uses_binding=True,
        failure_label="cdb-completion",
        csharp_action=r"""
            runnerCdbFinalizationValidationBeginTimestamp = Stopwatch.GetTimestamp();
            try
            {
                cdbCleanupResult = FinalizeExactCdbObserverAfterManagedStop(
                    cdbAttachResult,
                    cdbPreStopResult,
                    boundCdbProcess,
                    boundCdbLogStream,
                    cdbLogLengthAtReadiness,
                    stopReceiptBound,
                    stopResult,
                    cdbLogPath);
            }
            finally
            {
                boundCdbLogStream?.Dispose();
                boundCdbLogStream = null;
            }
            boundCdbProcess = null;
            if (!JsonStringIn(cdbCleanupResult, "status", "exited-after-managed-stop"))
                failure = string.IsNullOrWhiteSpace(failure)
                    ? "Exact CDB observer did not complete after the managed target stop."
                    : failure + " | Exact CDB observer did not complete after the managed target stop.";
        """,
        csharp_failure=r"""
            try { boundCdbProcess?.Dispose(); } catch { }
            boundCdbProcess = null;
            try { boundCdbLogStream?.Dispose(); } catch { }
            boundCdbLogStream = null;
            cdbCleanupResult = JsonPayload(new { status = "failed", receiptBound = false, exited = false, gracefulQuitObserved = false, targetExitEventObserved = false, error = ex.GetType().Name + ": " + ex.Message });
        """,
    ),
    CanaryCleanupPhase(
        name="census",
        callback_uses_binding=False,
        failure_label="census",
        csharp_action=r"""
            censusResult = InspectOwnedProcessCensus(runtimeReceiptPath, managed?.ExecutablePath, cdbAttachResult);
            ownedProcessCount = JsonInt(censusResult, "ownedProcessCount");
            if (!JsonStringIn(censusResult, "status", "clear"))
                failure = string.IsNullOrWhiteSpace(failure)
                    ? "Owned-process census was not clear."
                    : failure + " | Owned-process census was not clear.";
        """,
        csharp_failure=r"""
            ownedProcessCount = -1;
            censusResult = JsonPayload(new { status = "inspection-failed", ownedProcessCount = -1, inspectionFailureCount = 1, error = ex.GetType().Name + ": " + ex.Message });
        """,
    ),
)

CANARY_CLEANUP_FIELDS = (
    "keysReleased",
    "cdbDetached",
    "managedProcessStopped",
    "ownedProcessCount",
)


def render_canary_cleanup_phase_block() -> str:
    blocks: list[str] = []
    for phase in CANARY_CLEANUP_PHASE_PLAN:
        action = textwrap.indent(textwrap.dedent(phase.csharp_action).strip(), " " * 12)
        failure = textwrap.indent(textwrap.dedent(phase.csharp_failure).strip(), " " * 12)
        blocks.append(
            "\n".join(
                (
                    f"        // CANARY_CLEANUP_PHASE: {phase.name}",
                    "        try",
                    "        {",
                    action,
                    "        }",
                    "        catch (Exception ex)",
                    "        {",
                    failure,
                    f'            failure = AppendCleanupFailure(failure, "{phase.failure_label}", ex);',
                    "        }",
                )
            )
        )
    return "\n".join(blocks)


def render_canary_cleanup_object() -> str:
    fields = "\n".join(f"        {field}," for field in CANARY_CLEANUP_FIELDS)
    return "\n".join(("    var canaryCleanup = new", "    {", fields, "    };"))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_arguments = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--runtime-protocol",
        default=DEFAULT_RUNTIME_PROTOCOL,
        choices=(DEFAULT_RUNTIME_PROTOCOL, MORPH_CANARY_RUNTIME_PROTOCOL, WALKER_TRAJECTORY_RUNTIME_PROTOCOL),
    )
    parser.add_argument("--canary-role", default="", choices=("", *MORPH_CANARY_ROLES))
    parser.add_argument("--walker-attempt", type=int, default=0, choices=(0, 1, 2))
    parser.add_argument("--walker-deadline-seconds", type=int, default=45, choices=(45,))
    parser.add_argument("--walker-prebuilt-runner-dll", default="")
    parser.add_argument("--expected-walker-prebuilt-runner-sha256", default="")
    parser.add_argument("--walker-prebuild-receipt", default="")
    parser.add_argument("--expected-walker-prebuild-receipt-sha256", default="")
    parser.add_argument("--walker-cooperative-stop-file", default="")
    parser.add_argument("--walker-attempt-budget-seconds", type=int, default=215, choices=(215,))
    parser.add_argument("--canary-authority-file", default="")
    parser.add_argument("--expected-canary-authority-sha256", default="")
    parser.add_argument("--canary-leases-file", default="")
    parser.add_argument("--expected-canary-leases-sha256", default="")
    parser.add_argument("--source-root", default=str(DEFAULT_GAME_ROOT))
    parser.add_argument("--exe-override", default="")
    parser.add_argument("--profiles-root", default="")
    parser.add_argument("--artifact-root", default="")
    parser.add_argument("--arm-external-artifact-root", default="", help="Required when --artifact-root is outside the repo subagents live-smoke root. External defaults from ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE may instead use ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE_ARM.")
    parser.add_argument("--arm-external-profiles-root", default="", help="Required only when --profiles-root is outside the artifact root and repo subagents live-smoke root.")
    parser.add_argument("--timeout-seconds", type=int, default=12)
    parser.add_argument("--capture-count", type=int, default=1, help="Number of bounded still-frame captures to take after the copied BEA window appears (1-10).")
    parser.add_argument("--pre-input-capture-count", type=int, default=0, help="Optional bounded still-frame captures to take after the copied BEA window appears but before scoped input is sent (0-3).")
    parser.add_argument("--focus-before-pre-input-capture", action="store_true", help="Focus the exact managed BEA window with a no-key wait action before pre-input capture.")
    parser.add_argument("--capture-after-each-input-sequence", action="store_true", help="Capture one bounded frame after each scoped input sequence for adjacent visual-delta proof.")
    parser.add_argument("--after-input-capture-delay-ms", type=int, default=250, help="Delay before each after-input capture when --capture-after-each-input-sequence is used (0-5000 ms).")
    parser.add_argument("--capture-interval-seconds", type=int, default=2, help="Delay between bounded still-frame captures when --capture-count is greater than 1 (0-15 seconds).")
    parser.add_argument("--post-window-delay-seconds", type=int, default=0, help="Delay after the copied BEA window appears before the first capture (0-30 seconds).")
    parser.add_argument("--input-sequence", action="append", default=[], help="Bounded scoped input sequence to send to the exact copied BEA window before capture. May be repeated.")
    parser.add_argument("--input-step-delay-ms", type=int, default=60, help="Delay passed to send_game_window_input.ps1 between input actions (0-1000 ms).")
    parser.add_argument("--allow-background-window-messages", action="store_true", help="Allow exact-HWND background PostMessage input only when the exact arm phrase is also supplied.")
    parser.add_argument("--arm-background-window-messages", default="", help=f"Required with --allow-background-window-messages. Exact phrase: {BACKGROUND_WINDOW_MESSAGES_ARM_PHRASE!r}.")
    parser.add_argument("--enable-cdb-observer", action="store_true", help="Attach x86 CDB to the exact managed copied BEA PID with an observer-only command file.")
    parser.add_argument("--arm-cdb-observer", default="", help=f"Required with --enable-cdb-observer. Exact phrase: {CDB_OBSERVER_ARM_PHRASE!r}.")
    parser.add_argument("--cdb-command-file", default=r"tools\runtime-probes\local-multiplayer-level850-observer.cdb.txt", help="Observer-only CDB command file under tools/runtime-probes or the artifact root.")
    parser.add_argument("--cdb-log-ready-timeout-ms", type=int, default=10000, help="Milliseconds to wait for CDB attach/log readiness (1000-30000).")
    parser.add_argument("--cdb-post-attach-wait-seconds", type=int, default=2, help="Delay after CDB attach before captures/input continue (0-15 seconds).")
    parser.add_argument("--cdb-attach-phase", default="after-window", choices=("after-window", "after-launch"), help="Attach CDB after window observation by default, or immediately after launching the copied process for early startup probes.")
    parser.add_argument("--level-id", type=int, default=0, help="Optional safe-copy launch mission id. Zero means no override.")
    parser.add_argument("--controller-configuration", type=int, default=0, help="Optional safe-copy launch controller configuration preset, 1-4. Zero means no override.")
    parser.add_argument("--persist-controller-config-in-options", action="store_true", help="Also write the selected --controller-configuration value into the generated safe copy's defaultoptions.bea for both players before launch.")
    parser.add_argument("--bind-forward-qe-for-input-isolation", action="store_true", help="Patch only the generated safe copy's defaultoptions.bea so Movement/Forward maps P1=Q and P2=E for a bounded input-isolation probe.")
    parser.add_argument("--bind-fire-qe-for-weapon-handoff", action="store_true", help="Patch only the generated safe copy's defaultoptions.bea so Actions/Fire weapon maps P1=Q and P2=E for a bounded weapon/fire handoff probe.")
    parser.add_argument("--bind-look-down-qe-for-config2-forward-discovery", action="store_true", help="Patch only the generated safe copy's defaultoptions.bea so Look/Down maps P1=Q and P2=E for a bounded config-2 forward-axis discovery probe.")
    parser.add_argument("--bind-config2-census-row-qe", default="", choices=("", *CONFIG2_CENSUS_ROWS), help="Patch one allowlisted copied defaultoptions.bea row so P1=Q and P2=E for a bounded config-2 mapping census.")
    parser.add_argument("--sharpen-mouse-look", action="store_true", help="Patch only the generated safe copy's defaultoptions.bea with the fixed 2.25 mouse sensitivity preset before launch.")
    parser.add_argument("--include-modern-graphics", action="store_true", help="Also apply the stable modern graphics patch rows to the copied BEA.exe.")
    parser.add_argument("--extra-patch-key", action="append", default=[], help="Additional patch catalog key to apply to the copied BEA.exe. May be repeated.")
    parser.add_argument("--arm-experimental-patch-key", default="", help=f"Required when --extra-patch-key selects an experimental row. Exact phrase: {EXPERIMENTAL_PATCH_ARM_PHRASE!r}.")
    parser.add_argument("--profile-preset-id", default="", help="Optional AppCore safe-copy profile preset id to validate and record in the generated manifest.")
    parser.add_argument("--stage-music-replacement", action="store_true", help="Stage one copied-game music replacement before launch.")
    parser.add_argument("--music-swap-preset-id", default="", choices=sorted(MUSIC_SWAP_PRESETS), help="Stage a named copied-track swap preset through the AppCore preset builder before launch.")
    parser.add_argument("--music-target", default="BEA_01(Master).ogg", help="Target .ogg file name under copied data/Music.")
    parser.add_argument("--music-replacement", default="BEA_02(Master).ogg", help="Replacement .ogg file name under source data/Music, or an absolute replacement .ogg path.")
    parser.add_argument("--launch-nomusic", action="store_true", help="Append BEA's -nomusic launch argument for bounded mute-control runtime proof.")
    parser.add_argument("--launch-nosound", action="store_true", help="Append BEA's -nosound launch argument for bounded mute-control runtime proof.")
    parser.add_argument("--arm-live-bea", default="")
    args = parser.parse_args(raw_arguments)
    args._explicit_options = frozenset(
        token.split("=", 1)[0]
        for token in raw_arguments
        if token.startswith("--")
    )
    return args


def build_launch_arguments(args: argparse.Namespace) -> list[str]:
    launch_arguments = ["-skipfmv"]
    if args.level_id:
        launch_arguments.extend(["-level", str(args.level_id)])
    if args.controller_configuration:
        launch_arguments.extend(["-configuration", str(args.controller_configuration)])
    if getattr(args, "launch_nomusic", False):
        launch_arguments.append("-nomusic")
    if getattr(args, "launch_nosound", False):
        launch_arguments.append("-nosound")
    return launch_arguments


def validate_runtime_protocol(args: argparse.Namespace) -> RuntimeProtocolPlan:
    explicit_options = set(getattr(args, "_explicit_options", ()))
    if args.runtime_protocol == DEFAULT_RUNTIME_PROTOCOL:
        patch_keys = list(BASE_PATCH_KEYS)
        if args.include_modern_graphics:
            patch_keys.extend(MODERN_GRAPHICS_PATCH_KEYS)
        patch_keys.extend(key.strip() for key in (args.extra_patch_key or []) if key and key.strip())
        return RuntimeProtocolPlan(
            runtime_protocol=DEFAULT_RUNTIME_PROTOCOL,
            canary_role="",
            launch_arguments=build_launch_arguments(args),
            patch_keys=sorted(set(patch_keys)),
            apply_windowed_compatibility_patch=True,
            transform_entry_id=None,
            transform_keyboard_device_code=None,
            transform_player1_token="",
            transform_player2_token="",
            capture_count=args.capture_count,
            input_sequences=list(args.input_sequence),
            include_modern_graphics=args.include_modern_graphics,
            stage_music_replacement=args.stage_music_replacement or bool(args.music_swap_preset_id.strip()),
            allow_background_window_messages=args.allow_background_window_messages,
            cdb_observer_enabled=args.enable_cdb_observer,
            cdb_attach_phase=args.cdb_attach_phase,
            required_cdb_log_marker="",
            input_step_delay_ms=args.input_step_delay_ms,
            cdb_log_ready_timeout_ms=args.cdb_log_ready_timeout_ms,
        )

    if args.runtime_protocol == WALKER_TRAJECTORY_RUNTIME_PROTOCOL:
        if args.walker_attempt not in (1, 2):
            raise ValueError("--walker-attempt 1 or 2 is required for the walker trajectory protocol.")
        forbidden_options = {
            "--canary-role", "--canary-authority-file", "--expected-canary-authority-sha256",
            "--canary-leases-file", "--expected-canary-leases-sha256", "--capture-count",
            "--pre-input-capture-count", "--focus-before-pre-input-capture",
            "--capture-after-each-input-sequence", "--after-input-capture-delay-ms",
            "--capture-interval-seconds", "--post-window-delay-seconds", "--input-sequence",
            "--input-step-delay-ms", "--allow-background-window-messages",
            "--arm-background-window-messages", "--enable-cdb-observer", "--arm-cdb-observer",
            "--cdb-command-file", "--cdb-log-ready-timeout-ms", "--cdb-post-attach-wait-seconds",
            "--cdb-attach-phase", "--level-id", "--controller-configuration",
            "--persist-controller-config-in-options", "--bind-forward-qe-for-input-isolation",
            "--bind-fire-qe-for-weapon-handoff", "--bind-look-down-qe-for-config2-forward-discovery",
            "--bind-config2-census-row-qe", "--sharpen-mouse-look", "--include-modern-graphics",
            "--extra-patch-key", "--arm-experimental-patch-key", "--profile-preset-id",
            "--stage-music-replacement", "--music-swap-preset-id", "--music-target",
            "--music-replacement", "--launch-nomusic", "--launch-nosound",
        }
        mixed = sorted(explicit_options & forbidden_options)
        if mixed:
            raise ValueError(
                "Walker trajectory protocol derives all proof levers; refusing: "
                + ", ".join(mixed)
            )
        return RuntimeProtocolPlan(
            runtime_protocol=WALKER_TRAJECTORY_RUNTIME_PROTOCOL,
            canary_role="",
            launch_arguments=["-skipfmv", "-level", "850", "-configuration", "2"],
            patch_keys=[],
            apply_windowed_compatibility_patch=False,
            transform_entry_id=None,
            transform_keyboard_device_code=None,
            transform_player1_token="",
            transform_player2_token="",
            capture_count=0,
            input_sequences=[],
            include_modern_graphics=False,
            stage_music_replacement=False,
            allow_background_window_messages=False,
            cdb_observer_enabled=False,
            cdb_attach_phase="after-window",
            required_cdb_log_marker="",
            input_step_delay_ms=0,
            cdb_log_ready_timeout_ms=10000,
        )

    if not args.canary_role:
        raise ValueError("--canary-role is required for the morph identity canary protocol.")

    forbidden_options = {
        "--pre-input-capture-count",
        "--focus-before-pre-input-capture",
        "--capture-after-each-input-sequence",
        "--after-input-capture-delay-ms",
        "--capture-interval-seconds",
        "--post-window-delay-seconds",
        "--input-sequence",
        "--input-step-delay-ms",
        "--allow-background-window-messages",
        "--arm-background-window-messages",
        "--enable-cdb-observer",
        "--arm-cdb-observer",
        "--cdb-command-file",
        "--cdb-log-ready-timeout-ms",
        "--cdb-post-attach-wait-seconds",
        "--cdb-attach-phase",
        "--level-id",
        "--controller-configuration",
        "--persist-controller-config-in-options",
        "--bind-forward-qe-for-input-isolation",
        "--bind-fire-qe-for-weapon-handoff",
        "--bind-look-down-qe-for-config2-forward-discovery",
        "--bind-config2-census-row-qe",
        "--sharpen-mouse-look",
        "--include-modern-graphics",
        "--extra-patch-key",
        "--arm-experimental-patch-key",
        "--profile-preset-id",
        "--stage-music-replacement",
        "--music-swap-preset-id",
        "--music-target",
        "--music-replacement",
        "--launch-nomusic",
        "--launch-nosound",
    }
    mixed_options = sorted(explicit_options & forbidden_options)
    if mixed_options:
        raise ValueError(
            "Morph identity canary protocol derives all proof levers; refusing: "
            + ", ".join(mixed_options)
        )
    if "--capture-count" in explicit_options and args.capture_count != 0:
        raise ValueError("Morph identity canary protocol requires --capture-count 0.")

    role_input = {
        "noInputControl": [],
        "positiveTransform": ["tap:Q"],
        "positiveRepeat": ["tap:Q"],
    }[args.canary_role]
    return RuntimeProtocolPlan(
        runtime_protocol=MORPH_CANARY_RUNTIME_PROTOCOL,
        canary_role=args.canary_role,
        launch_arguments=["-skipfmv", "-level", "850", "-configuration", "2"],
        patch_keys=[],
        apply_windowed_compatibility_patch=False,
        transform_entry_id=0x21,
        transform_keyboard_device_code=8,
        transform_player1_token="Q",
        transform_player2_token="",
        capture_count=0,
        input_sequences=role_input,
        include_modern_graphics=False,
        stage_music_replacement=False,
        allow_background_window_messages=False,
        cdb_observer_enabled=True,
        cdb_attach_phase="after-window",
        required_cdb_log_marker=MORPH_CANARY_READY_MARKER,
        input_step_delay_ms=60,
        cdb_log_ready_timeout_ms=10000,
    )


def validate_morph_canary_control_inputs(
    args: argparse.Namespace,
    artifact_root: Path,
    *,
    private_parent: Path = morph_authority.PRIVATE_PROOF_PARENT,
    now: dt.datetime | None = None,
) -> morph_authority.ControlRecords | None:
    fields = {
        "--canary-authority-file": args.canary_authority_file,
        "--expected-canary-authority-sha256": args.expected_canary_authority_sha256,
        "--canary-leases-file": args.canary_leases_file,
        "--expected-canary-leases-sha256": args.expected_canary_leases_sha256,
    }
    if args.runtime_protocol != MORPH_CANARY_RUNTIME_PROTOCOL:
        supplied = sorted(name for name, value in fields.items() if value)
        if supplied:
            raise ValueError("Canary authority controls require the morph identity protocol: " + ", ".join(supplied))
        return None
    missing = sorted(name for name, value in fields.items() if not value)
    if missing:
        raise ValueError("Morph identity canary requires executor authority controls: " + ", ".join(missing))
    try:
        return morph_authority.load_control_records(
            args.canary_authority_file,
            args.canary_leases_file,
            artifact_root.parent,
            now or dt.datetime.now(dt.timezone.utc),
            private_parent=private_parent,
            expected_authority_sha256=args.expected_canary_authority_sha256,
            expected_leases_sha256=args.expected_canary_leases_sha256,
            proof_root_exists=True,
            minimum_remaining_seconds=morph_authority.MINIMUM_ROLE_AUTHORITY_SECONDS,
        )
    except morph_authority.AuthorityError as exc:
        raise ValueError(f"Morph identity canary authority validation failed: {exc}") from exc


def run_synthetic_runtime_orchestration(
    plan: RuntimeProtocolPlan,
    callbacks: Mapping[str, Callable[..., Any]],
    *,
    receipt_sha256: str,
    command_sha256: str,
    required_marker: str,
) -> dict[str, Any]:
    active_failure = ""
    cleanup_order: list[str] = []
    cleanup_failures: dict[str, str] = {}
    owned_process_count: int | None = None
    input_results: list[Any] = []
    best_effort_release: Any = None
    try:
        if plan.runtime_protocol == MORPH_CANARY_RUNTIME_PROTOCOL:
            observer_ready = callbacks["attach_cdb"](
                receipt_sha256,
                command_sha256,
                required_marker,
            )
            if observer_ready is not True:
                raise RuntimeError("CDB observer did not reach receipt-bound marker readiness.")
            for sequence in plan.input_sequences:
                input_results.append(
                    callbacks["send_input"](
                        sequence,
                        receipt_sha256,
                        command_sha256,
                        required_marker,
                    )
                )
        else:
            for _ in range(plan.capture_count):
                callbacks["capture"]()
    except Exception as exc:  # Synthetic seam records active failures before teardown.
        active_failure = f"{type(exc).__name__}: {exc}"
    finally:
        for phase in CANARY_CLEANUP_PHASE_PLAN:
            cleanup_order.append(phase.name)
            try:
                if phase.callback_uses_binding:
                    value = callbacks[phase.name](receipt_sha256, command_sha256, required_marker)
                else:
                    value = callbacks[phase.name]()
                if phase.name == "release_keys":
                    best_effort_release = value
                if phase.name == "census":
                    owned_process_count = value
            except Exception as exc:
                cleanup_failures[phase.name] = f"{type(exc).__name__}: {exc}"
    keys_released = None
    if plan.runtime_protocol == MORPH_CANARY_RUNTIME_PROTOCOL:
        keys_released = (
            len(input_results) == 0
            if plan.canary_role == "noInputControl"
            else len(input_results) == len(plan.input_sequences)
            and all(
                isinstance(result, Mapping)
                and result.get("unconfirmedReleaseKeys") == []
                for result in input_results
            )
        )
    return {
        "active_failure": active_failure,
        "cleanup_order": cleanup_order,
        "cleanup_failures": cleanup_failures,
        "owned_process_count": owned_process_count,
        "keys_released": keys_released,
        "best_effort_release": best_effort_release,
    }


def run_synthetic_walker_runtime_orchestration(
    callbacks: Mapping[str, Callable[..., Any]],
) -> dict[str, Any]:
    """Exercise the cleanup-first walker lifecycle without native actions."""
    failure = ""
    adapter: dict[str, Any] = {}
    focus_ok = False
    try:
        focus_ok = callbacks["focus"]() is True
        if not focus_ok:
            raise RuntimeError("foreground focus was not confirmed")
        adapter = dict(callbacks["start_adapter"]())
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    cleanup: dict[str, Any] = {}
    for name in ("release_q", "wait_adapter", "stop_managed", "census"):
        try:
            cleanup[name] = callbacks[name]()
        except Exception as exc:
            cleanup[name] = None
            failure = failure or f"{type(exc).__name__}: {exc}"
    succeeded = (
        not failure and focus_ok and adapter.get("exitCode") == 0
        and cleanup.get("release_q") is True
        and cleanup.get("wait_adapter") is True
        and cleanup.get("stop_managed") is True
        and cleanup.get("census") == 0
    )
    return {"succeeded": succeeded, "failure": failure, "adapter": adapter, "cleanup": cleanup}


def run_synthetic_walker_phase_orchestration(
    callbacks: Mapping[str, Callable[..., Any]],
) -> dict[str, Any]:
    """Mirror the generated runner's phase refusal and unconditional cleanup order."""
    failure = ""
    completed: list[str] = []
    try:
        for phase, required in (
            ("profile", 215), ("launch", 95), ("receipt", 65),
            ("focus", 65), ("adapter", 65),
        ):
            callbacks["require_budget"](phase, required)
            callbacks[phase]()
            completed.append(phase)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    cleanup: dict[str, Any] = {}
    for name in ("release_q", "close_adapter", "stop_managed", "census", "closeout"):
        try:
            cleanup[name] = callbacks[name]()
        except Exception as exc:
            cleanup[name] = None
            failure = failure or f"{type(exc).__name__}: {exc}"
    return {"completed": completed, "cleanup": cleanup, "failure": failure,
            "succeeded": not failure and len(completed) == 5}


def run_synthetic_walker_blocked_phase(
    phase: str, limit_seconds: float, callbacks: Mapping[str, Callable[..., Any]],
    monotonic: Callable[[], float],
) -> dict[str, Any]:
    """Drive an in-progress phase across its bound and mirror cleanup-first STOP."""
    started = monotonic()
    stop_signaled = False

    def poll() -> bool:
        nonlocal stop_signaled
        if not stop_signaled and monotonic() - started >= limit_seconds:
            callbacks["signal_stop"](phase)
            stop_signaled = True
        return stop_signaled

    failure = ""
    try:
        callbacks["blocked_work"](poll)
        poll()
        if stop_signaled:
            raise TimeoutError(f"{phase} cooperative deadline expired")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    cleanup: dict[str, Any] = {}
    for name in ("release_q", "close_adapter", "stop_managed", "census", "closeout"):
        try:
            cleanup[name] = callbacks[name]()
        except Exception as exc:
            cleanup[name] = None
            failure = failure or f"{type(exc).__name__}: {exc}"
    accepted = not failure and not stop_signaled
    return {
        "phase": phase, "stopSignaled": stop_signaled, "cleanup": cleanup,
        "failure": failure, "accepted": accepted,
    }


def load_morph_canary_module():
    module_path = ROOT / "tools" / "battleengine_morph_identity_canary.py"
    module_name = "_winui_live_smoke_morph_canary"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load morph canary renderer: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def select_artifact_root_inputs(args: argparse.Namespace, stamp: str) -> tuple[Path, Path, bool, bool, Path]:
    default_artifact_parent_raw = ROOT / "subagents" / "winui-safe-copy-live-runtime"
    artifact_base_env = os.environ.get(ARTIFACT_BASE_ENV, "").strip()
    artifact_base_arm_env = os.environ.get(ARTIFACT_BASE_ARM_ENV, "").strip()
    explicit_artifact_root = bool(args.artifact_root)
    canary_private_default = (
        getattr(args, "runtime_protocol", DEFAULT_RUNTIME_PROTOCOL) == MORPH_CANARY_RUNTIME_PROTOCOL
        and not explicit_artifact_root
        and not artifact_base_env
    )
    canary_private_parent = (
        Path(os.environ.get("LOCALAPPDATA") or tempfile.gettempdir())
        / "OnslaughtToolkit"
        / "private-runtime"
        / "battleengine-morph-identity-canary"
    )
    artifact_parent_raw = (
        Path(artifact_base_env)
        if artifact_base_env
        else canary_private_parent
        if canary_private_default
        else default_artifact_parent_raw
    )
    artifact_root_raw = Path(args.artifact_root) if explicit_artifact_root else artifact_parent_raw / stamp
    profiles_root_raw = Path(args.profiles_root) if args.profiles_root else artifact_root_raw / "GameProfiles"
    cli_external_artifact_armed = args.arm_external_artifact_root == EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE
    env_external_artifact_armed = (
        bool(artifact_base_env)
        and not explicit_artifact_root
        and artifact_base_arm_env == EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE
    )
    return (
        artifact_root_raw,
        profiles_root_raw,
        cli_external_artifact_armed or env_external_artifact_armed or canary_private_default,
        env_external_artifact_armed,
        artifact_parent_raw,
    )


def create_fresh_canary_artifact_root(root: Path) -> Path:
    candidate = root.absolute()
    if candidate.exists():
        raise ValueError(f"Canary artifact root must be fresh and absent: {candidate}")
    if has_reparse_or_symlink_ancestor(candidate):
        raise ValueError("Canary artifact root includes a reparse/symlink path component.")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    if has_reparse_or_symlink_ancestor(candidate.parent):
        raise ValueError("Canary artifact root parent includes a reparse/symlink path component.")
    candidate.mkdir(exist_ok=False)
    if has_reparse_or_symlink_ancestor(candidate):
        raise ValueError("Canary artifact root became reparse/symlink-routed during creation.")
    return candidate.resolve()


def assert_fresh_canary_write_target(target: Path, artifact_root: Path) -> None:
    resolved_root = artifact_root.resolve()
    resolved_target = target.absolute()
    if not is_same_or_under(resolved_target, resolved_root) or resolved_target == resolved_root:
        raise ValueError(f"Canary write target is outside the private artifact root: {resolved_target}")
    if not resolved_root.is_dir() or has_reparse_or_symlink_ancestor(resolved_target):
        raise ValueError("Canary write target includes a missing or reparse/symlink-routed artifact root.")
    if resolved_target.exists():
        raise ValueError(f"Canary write target already exists: {resolved_target}")


def create_fresh_canary_directory(path: Path, artifact_root: Path) -> Path:
    assert_fresh_canary_write_target(path, artifact_root)
    path.mkdir(exist_ok=False)
    if has_reparse_or_symlink_ancestor(path):
        raise ValueError(f"Canary directory became reparse/symlink-routed: {path}")
    return path.resolve()


def write_new_private_bytes(path: Path, data: bytes, artifact_root: Path) -> None:
    assert_fresh_canary_write_target(path, artifact_root)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def write_new_private_text(path: Path, text: str, artifact_root: Path) -> None:
    write_new_private_bytes(path, text.encode("utf-8"), artifact_root)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_canary_digest_set(canonical: str, **digests: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{64}", canonical):
        raise ValueError("Canonical executable digest must be lowercase SHA-256.")
    drifted = sorted(name for name, digest in digests.items() if digest != canonical)
    if drifted:
        raise ValueError("Canary executable digest mismatch: " + ", ".join(drifted))


def resolve_morph_canary_app_config_root(artifact_root: Path, profiles_root: Path) -> Path:
    artifact = artifact_root.absolute().resolve(strict=False)
    app_config_root = artifact / "app-config"
    expected_profiles_root = app_config_root / "OnslaughtCareerEditor" / "GameProfiles"
    actual_profiles_root = profiles_root.absolute().resolve(strict=False)
    if actual_profiles_root != expected_profiles_root.resolve(strict=False):
        raise ValueError("Morph canary profiles root must equal the private AppConfig GameProfiles root.")
    if (
        has_reparse_or_symlink_ancestor(app_config_root)
        or has_reparse_or_symlink_ancestor(actual_profiles_root)
    ):
        raise ValueError("Morph canary AppConfig root must not be reparse or symlink routed.")
    return app_config_root


def validate_morph_canary_profile_path_budget(profiles_root: Path, role: str) -> int:
    try:
        profile_name = MORPH_CANARY_PROFILE_NAMES[role]
    except KeyError as exc:
        raise ValueError(f"Unsupported morph canary role: {role}") from exc
    sentinel_path = (
        profiles_root.absolute().resolve(strict=False)
        / profile_name
        / MORPH_CANARY_MUTATION_SENTINEL_SAMPLE
    )
    path_length = len(
        str(sentinel_path).encode("utf-16-le", errors="surrogatepass")
    ) // 2
    if path_length >= LEGACY_WIN32_MAX_PATH:
        raise ValueError(
            "Morph canary profile mutation sentinel exceeds the legacy Win32 path budget "
            f"({path_length} UTF-16 code units; must be below {LEGACY_WIN32_MAX_PATH})."
        )
    return path_length


def resolve_walker_app_config_root(artifact_root: Path, profiles_root: Path) -> Path:
    artifact = artifact_root.absolute().resolve(strict=False)
    profiles = profiles_root.absolute().resolve(strict=False)
    if profiles.name != "GameProfiles" or profiles.parent.name != "OnslaughtCareerEditor":
        raise ValueError("Walker profiles root must end in OnslaughtCareerEditor/GameProfiles.")
    app_config_root = profiles.parent.parent
    if paths_overlap(app_config_root, artifact):
        raise ValueError("Walker profile and evidence roots must be distinct and non-overlapping.")
    if has_reparse_or_symlink_ancestor(app_config_root) or has_reparse_or_symlink_ancestor(artifact):
        raise ValueError("Walker profile/evidence roots must not be reparse or symlink routed.")
    return app_config_root


def build_canary_private_artifact_payload(
    *,
    executable_path: Path,
    template_path: Path,
    command_path: Path,
    receipt_sha256: str,
    rendered: Any,
    source_unchanged: bool,
    copy_unchanged: bool,
    keys_released: bool,
    cdb_detached: bool,
    managed_process_stopped: bool,
    owned_process_count: int,
) -> dict[str, Any]:
    cleanup_values = {
        "keysReleased": keys_released,
        "cdbDetached": cdb_detached,
        "managedProcessStopped": managed_process_stopped,
        "ownedProcessCount": owned_process_count,
    }
    if tuple(cleanup_values) != CANARY_CLEANUP_FIELDS:
        raise AssertionError("Canary cleanup producer fields drifted from the generated runner schema.")
    return {
        "schema": "winui-original-binary-battleengine-morph-identity-canary-private-run.v1",
        "executablePath": str(executable_path),
        "templatePath": str(template_path),
        "commandPath": str(command_path),
        "receiptSha256": receipt_sha256,
        "commandSha256": rendered.sha256,
        "templateSha256": rendered.template_sha256,
        "executableSha256": rendered.executable_sha256,
        "fingerprints": [
            {
                "event": target.event,
                "rva": target.rva,
                "length": target.size,
                "sha256": target.sha256,
            }
            for target in rendered.targets
        ],
        "sourceUnchanged": source_unchanged,
        "copyUnchanged": copy_unchanged,
        "cleanup": cleanup_values,
    }


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def write_runner(runner_root: Path, *, create_new: bool = False) -> Path:
    runner_root.mkdir(parents=True, exist_ok=not create_new)
    marker_path = runner_root / RUNNER_MARKER
    if create_new:
        with marker_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write("tool-owned runner scratch\n")
    else:
        marker_path.write_text("tool-owned runner scratch\n", encoding="utf-8")
    appcore = ROOT / "OnslaughtCareerEditor.AppCore" / "OnslaughtCareerEditor.AppCore.csproj"
    project = runner_root / "LiveSafeCopySmoke.csproj"
    # AppCore carries NuGet PackageReferences. Generation-phase restore must be
    # allowed so the locked one-build/--no-restore step can compile offline from
    # project.assets.json. Do not set RestoreProjectStyle=None: SDK 10 still needs
    # a real restore graph for ProjectReference packages.
    project_text = f"""<Project Sdk=\"Microsoft.NET.Sdk\">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include=\"{appcore}\" />
  </ItemGroup>
</Project>
"""
    if create_new:
        with project.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(project_text)
    else:
        project.write_text(project_text, encoding="utf-8")
    program = runner_root / "Program.cs"
    program_text = r"""
using System.Diagnostics;
using System.Security.Cryptography;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using Onslaught___Career_Editor;

static string RequiredEnv(string name)
{
    string? value = Environment.GetEnvironmentVariable(name);
    if (string.IsNullOrWhiteSpace(value))
        throw new InvalidOperationException($"{name} is required.");
    return value;
}

static string Sha256File(string path)
{
    using FileStream stream = File.OpenRead(path);
    return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
}

static string HwndHex(IntPtr handle)
{
    long value = handle.ToInt64();
    return value == 0 ? "0x0" : $"0x{value:x}";
}

static JsonElement JsonPayload(object value)
{
    return JsonSerializer.Deserialize<JsonElement>(JsonSerializer.Serialize(value));
}

static object[] SnapshotBeaProcesses()
{
    return Process.GetProcessesByName("BEA")
        .Select(process =>
        {
            string? path = null;
            string? startTime = null;
            string mainWindowHandle = "0x0";
            string? error = null;
            try
            {
                path = process.MainModule?.FileName;
                startTime = process.StartTime.ToString("o");
                mainWindowHandle = HwndHex(process.MainWindowHandle);
            }
            catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                error = ex.GetType().Name + ": " + ex.Message;
            }

            return new
            {
                processId = process.Id,
                path,
                startTime,
                mainWindowHandle,
                error,
            };
        })
        .Cast<object>()
        .ToArray();
}

static object[] WaitForNoBeaProcesses(TimeSpan timeout)
{
    DateTime deadline = DateTime.UtcNow.Add(timeout);
    object[] snapshot = SnapshotBeaProcesses();
    while (snapshot.Length != 0 && DateTime.UtcNow < deadline)
    {
        Thread.Sleep(250);
        snapshot = SnapshotBeaProcesses();
    }

    return snapshot;
}

static SortedDictionary<string, string> SnapshotRelativeHashes(string root, params string[] relativePaths)
{
    string resolvedRoot = Path.GetFullPath(root);
    var hashes = new SortedDictionary<string, string>(StringComparer.OrdinalIgnoreCase);
    foreach (string relativePath in relativePaths)
    {
        string path = Path.GetFullPath(Path.Combine(resolvedRoot, relativePath));
        if (!path.StartsWith(resolvedRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) &&
            !string.Equals(path, resolvedRoot, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException("Snapshot path escaped the requested root.");
        }

        if (File.Exists(path))
        {
            AddHash(hashes, resolvedRoot, path);
            continue;
        }

        if (!Directory.Exists(path))
            continue;

        foreach (string filePath in Directory.GetFiles(path, "*", SearchOption.AllDirectories).OrderBy(x => x, StringComparer.OrdinalIgnoreCase))
            AddHash(hashes, resolvedRoot, filePath);
    }

    return hashes;
}

static void AddHash(SortedDictionary<string, string> hashes, string root, string filePath)
{
    string relative = Path.GetRelativePath(root, filePath).Replace('\\', '/');
    FileInfo info = new(filePath);
    hashes[relative] = $"{info.Length}:{Sha256File(filePath)}";
}

static bool HashMapsEqual(IReadOnlyDictionary<string, string> left, IReadOnlyDictionary<string, string> right)
{
    return left.Count == right.Count &&
        left.All(pair => right.TryGetValue(pair.Key, out string? value) &&
            string.Equals(value, pair.Value, StringComparison.OrdinalIgnoreCase));
}

static int JsonInt(JsonElement element, string propertyName)
{
    if (element.ValueKind != JsonValueKind.Object)
        return 0;

    return element.TryGetProperty(propertyName, out JsonElement property) && property.ValueKind == JsonValueKind.Number && property.TryGetInt32(out int value)
        ? value
        : 0;
}

static bool JsonIntEquals(JsonElement element, string propertyName, int expected)
{
    if (element.ValueKind != JsonValueKind.Object)
        return false;

    return element.TryGetProperty(propertyName, out JsonElement property) &&
        property.ValueKind == JsonValueKind.Number &&
        property.TryGetInt32(out int value) &&
        value == expected;
}

static bool JsonBool(JsonElement element, string propertyName)
{
    if (element.ValueKind != JsonValueKind.Object)
        return false;

    return element.TryGetProperty(propertyName, out JsonElement property) &&
        property.ValueKind is JsonValueKind.True or JsonValueKind.False &&
        property.GetBoolean();
}

static bool JsonStringIn(JsonElement element, string propertyName, params string[] expected)
{
    if (element.ValueKind != JsonValueKind.Object)
        return false;

    if (!element.TryGetProperty(propertyName, out JsonElement property) || property.ValueKind != JsonValueKind.String)
        return false;

    string? value = property.GetString();
    return expected.Any(candidate => string.Equals(candidate, value, StringComparison.OrdinalIgnoreCase));
}

static bool CdbObserverReady(
    JsonElement? attachResult,
    string receiptSha256,
    string commandSha256,
    string logPath,
    string requiredMarker,
    FileStream? retainedLogStream = null)
{
    if (!attachResult.HasValue || attachResult.Value.ValueKind != JsonValueKind.Object)
        return false;

    JsonElement attach = attachResult.Value;
    return JsonStringIn(attach, "status", "attached") &&
        attach.TryGetProperty("helperPayload", out JsonElement helper) &&
        helper.ValueKind == JsonValueKind.Object &&
        JsonStringIn(helper, "status", "marker-ready") &&
        JsonBool(helper, "requiredLogMarkerFound") &&
        JsonStringIn(helper, "targetReceiptSha256", receiptSha256) &&
        JsonStringIn(helper, "commandSha256", commandSha256) &&
        (retainedLogStream is null
            ? HasExactlyOneLogMarkerAtPath(logPath, requiredMarker)
            : HasExactlyOneLogMarker(retainedLogStream, requiredMarker));
}

static JsonElement CaptureSkipped(string reason, string outputPath)
{
    return JsonPayload(new
    {
        schemaVersion = "game-window-capture-helper.v1",
        generatedAt = DateTimeOffset.UtcNow,
        status = "skipped",
        outputPath,
        note = reason
    });
}

static JsonElement InputSkipped(string reason, string sequence)
{
    return JsonPayload(new
    {
        schemaVersion = "game-window-input.v1",
        generatedAt = DateTimeOffset.UtcNow,
        status = "skipped",
        sequence,
        note = reason
    });
}

static JsonElement SendInputSequence(
    string powershellExe,
    string scriptPath,
    int processId,
    string hwndHex,
    string expectedExecutablePath,
    string expectedWorkingDirectory,
    string sequence,
    int stepDelayMs,
    bool allowBackgroundWindowMessages,
    string backgroundWindowMessagesArm,
    string outputJson,
    string runtimeReceiptPath = "",
    string expectedReceiptSha256 = "",
    bool createNewOutput = false)
{
    Directory.CreateDirectory(Path.GetDirectoryName(outputJson)!);
    var startInfo = new ProcessStartInfo
    {
        FileName = powershellExe,
        UseShellExecute = false,
        RedirectStandardOutput = true,
        RedirectStandardError = true,
    };
    startInfo.ArgumentList.Add("-NoProfile");
    startInfo.ArgumentList.Add("-ExecutionPolicy");
    startInfo.ArgumentList.Add("Bypass");
    startInfo.ArgumentList.Add("-File");
    startInfo.ArgumentList.Add(scriptPath);
    startInfo.ArgumentList.Add("-ProcessName");
    startInfo.ArgumentList.Add("BEA.exe");
    startInfo.ArgumentList.Add("-ProcessId");
    startInfo.ArgumentList.Add(processId.ToString(System.Globalization.CultureInfo.InvariantCulture));
    startInfo.ArgumentList.Add("-HwndHex");
    startInfo.ArgumentList.Add(hwndHex);
    startInfo.ArgumentList.Add("-ExpectedExecutablePath");
    startInfo.ArgumentList.Add(expectedExecutablePath);
    startInfo.ArgumentList.Add("-ExpectedWorkingDirectory");
    startInfo.ArgumentList.Add(expectedWorkingDirectory);
    if (!string.IsNullOrWhiteSpace(runtimeReceiptPath))
    {
        startInfo.ArgumentList.Add("-RuntimeReceiptPath");
        startInfo.ArgumentList.Add(runtimeReceiptPath);
        startInfo.ArgumentList.Add("-ExpectedReceiptSha256");
        startInfo.ArgumentList.Add(expectedReceiptSha256);
    }
    startInfo.ArgumentList.Add("-Sequence");
    startInfo.ArgumentList.Add(sequence);
    startInfo.ArgumentList.Add("-StepDelayMs");
    startInfo.ArgumentList.Add(stepDelayMs.ToString(System.Globalization.CultureInfo.InvariantCulture));
    if (allowBackgroundWindowMessages)
    {
        startInfo.ArgumentList.Add("-AllowBackgroundWindowMessages");
        startInfo.ArgumentList.Add("-BackgroundWindowMessagesArm");
        startInfo.ArgumentList.Add(backgroundWindowMessagesArm);
    }

    using Process? process = Process.Start(startInfo);
    if (process is null)
        throw new InvalidOperationException("Could not start the bounded scoped input helper.");

    string stdout = process.StandardOutput.ReadToEnd();
    string stderr = process.StandardError.ReadToEnd();
    process.WaitForExit();

    if (process.ExitCode != 0)
    {
        var failure = new
        {
            schemaVersion = "game-window-input.v1",
            generatedAt = DateTimeOffset.UtcNow,
            status = "failed",
            processId,
            hwndHex,
            sequence,
            exitCode = process.ExitCode,
            stdout,
            stderr,
            note = "Bounded scoped input failed for the exact process/window target."
        };
        string failureJson = JsonSerializer.Serialize(failure, new JsonSerializerOptions { WriteIndented = true });
        if (createNewOutput)
        {
            using FileStream output = new(outputJson, FileMode.CreateNew, FileAccess.Write, FileShare.None);
            using StreamWriter writer = new(output, new UTF8Encoding(false));
            writer.Write(failureJson);
        }
        else
        {
            File.WriteAllText(outputJson, failureJson);
        }
        return JsonSerializer.Deserialize<JsonElement>(failureJson);
    }

    if (createNewOutput)
    {
        using FileStream output = new(outputJson, FileMode.CreateNew, FileAccess.Write, FileShare.None);
        using StreamWriter writer = new(output, new UTF8Encoding(false));
        writer.Write(stdout);
    }
    else
    {
        File.WriteAllText(outputJson, stdout);
    }
    return JsonSerializer.Deserialize<JsonElement>(stdout);
}

static JsonElement CaptureFrame(
    string powershellExe,
    string scriptPath,
    int processId,
    string hwndHex,
    string expectedExecutablePath,
    string expectedWorkingDirectory,
    string allowedOutputRoot,
    string sourceGameRoot,
    string outputPng,
    string outputJson)
{
    Directory.CreateDirectory(Path.GetDirectoryName(outputPng)!);
    Directory.CreateDirectory(Path.GetDirectoryName(outputJson)!);
    var startInfo = new ProcessStartInfo
    {
        FileName = powershellExe,
        UseShellExecute = false,
        RedirectStandardOutput = true,
        RedirectStandardError = true,
    };
    startInfo.ArgumentList.Add("-NoProfile");
    startInfo.ArgumentList.Add("-ExecutionPolicy");
    startInfo.ArgumentList.Add("Bypass");
    startInfo.ArgumentList.Add("-File");
    startInfo.ArgumentList.Add(scriptPath);
    startInfo.ArgumentList.Add("-ProcessId");
    startInfo.ArgumentList.Add(processId.ToString(System.Globalization.CultureInfo.InvariantCulture));
    startInfo.ArgumentList.Add("-HwndHex");
    startInfo.ArgumentList.Add(hwndHex);
    startInfo.ArgumentList.Add("-ExpectedExecutablePath");
    startInfo.ArgumentList.Add(expectedExecutablePath);
    startInfo.ArgumentList.Add("-ExpectedWorkingDirectory");
    startInfo.ArgumentList.Add(expectedWorkingDirectory);
    startInfo.ArgumentList.Add("-AllowedOutputRoot");
    startInfo.ArgumentList.Add(allowedOutputRoot);
    startInfo.ArgumentList.Add("-SourceGameRoot");
    startInfo.ArgumentList.Add(sourceGameRoot);
    startInfo.ArgumentList.Add("-OutputPath");
    startInfo.ArgumentList.Add(outputPng);

    using Process? process = Process.Start(startInfo);
    if (process is null)
        throw new InvalidOperationException("Could not start the bounded frame capture helper.");

    string stdout = process.StandardOutput.ReadToEnd();
    string stderr = process.StandardError.ReadToEnd();
    process.WaitForExit();

    if (process.ExitCode != 0)
    {
        var failure = new
        {
            schemaVersion = "game-window-capture-helper.v1",
            generatedAt = DateTimeOffset.UtcNow,
            status = "failed",
            processId,
            hwndHex,
            outputPath = outputPng,
            exitCode = process.ExitCode,
            stdout,
            stderr,
            note = "One bounded screen-region capture failed for the exact process/window target."
        };
        string failureJson = JsonSerializer.Serialize(failure, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(outputJson, failureJson);
        return JsonSerializer.Deserialize<JsonElement>(failureJson);
    }

    File.WriteAllText(outputJson, stdout);
    return JsonSerializer.Deserialize<JsonElement>(stdout);
}

static long? CdbLogLength(string logPath)
{
    if (string.IsNullOrWhiteSpace(logPath))
        return null;

    try
    {
        return File.Exists(logPath)
            ? new FileInfo(logPath).Length
            : null;
    }
    catch
    {
        return null;
    }
}

static FileStream OpenRetainedCdbLogStream(string logPath)
{
    return new FileStream(
        logPath,
        FileMode.Open,
        FileAccess.Read,
        FileShare.ReadWrite,
        bufferSize: 4096,
        FileOptions.SequentialScan);
}

static bool HasExactlyOneLogMarker(FileStream retainedLogStream, string marker)
{
    if (!retainedLogStream.CanRead || !retainedLogStream.CanSeek)
        return false;
    int count = 0;
    try
    {
        retainedLogStream.Flush();
        retainedLogStream.Seek(0, SeekOrigin.Begin);
        using var reader = new StreamReader(
            retainedLogStream,
            Encoding.UTF8,
            detectEncodingFromByteOrderMarks: true,
            bufferSize: 4096,
            leaveOpen: true);
        string? line;
        while ((line = reader.ReadLine()) is not null)
        {
            if (!string.Equals(line.Trim(), marker, StringComparison.Ordinal))
                continue;
            count++;
            if (count > 1)
                return false;
        }
        return count == 1;
    }
    finally
    {
        retainedLogStream.Seek(0, SeekOrigin.Begin);
    }
}

static bool HasExactlyOneLogMarkerAtPath(string logPath, string marker)
{
    if (!File.Exists(logPath))
        return false;
    using FileStream stream = OpenRetainedCdbLogStream(logPath);
    return HasExactlyOneLogMarker(stream, marker);
}

static bool TryReadFinalizedCdbExitEvidence(
    FileStream retainedLogStream,
    long logLengthAtReadiness,
    int expectedTargetProcessId,
    string expectedCdbExecutablePath,
    out bool cleanupMarkerObserved,
    out bool gracefulQuitObserved,
    out bool targetExitEventObserved,
    out uint targetExitCode,
    out bool terminalRegionDiagnosticClean)
{
    static bool TryParseCdbDebuggerTime(string line)
    {
        var match = System.Text.RegularExpressions.Regex.Match(
            line,
            @"\Adebugger time: (?<weekday>Mon|Tue|Wed|Thu|Fri|Sat|Sun) (?<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) {1,2}(?<day>[1-9]|[12][0-9]|3[01]) (?<hour>[0-9]{2}):(?<minute>[0-9]{2}):(?<second>[0-9]{2})\.(?<millisecond>[0-9]{3}) (?<year>[0-9]{4}) \(UTC (?<sign>[+-]) (?<offsetHour>[0-9]|1[0-4]):(?<offsetMinute>[0-9]{2})\)\z",
            System.Text.RegularExpressions.RegexOptions.CultureInvariant);
        if (!match.Success)
            return false;

        string[] monthNames = { "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
        int month = Array.IndexOf(monthNames, match.Groups["month"].Value) + 1;
        if (month == 0 ||
            !int.TryParse(match.Groups["day"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int day) ||
            !int.TryParse(match.Groups["hour"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int hour) ||
            !int.TryParse(match.Groups["minute"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int minute) ||
            !int.TryParse(match.Groups["second"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int second) ||
            !int.TryParse(match.Groups["millisecond"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int millisecond) ||
            !int.TryParse(match.Groups["year"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int year) ||
            !int.TryParse(match.Groups["offsetHour"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int offsetHour) ||
            !int.TryParse(match.Groups["offsetMinute"].Value, System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out int offsetMinute) ||
            year < 1601 || offsetHour > 14 || offsetMinute > 59 || (offsetHour == 14 && offsetMinute != 0))
            return false;

        try
        {
            var localTime = new DateTime(year, month, day, hour, minute, second, millisecond, DateTimeKind.Unspecified);
            DayOfWeek weekday = match.Groups["weekday"].Value switch
            {
                "Mon" => DayOfWeek.Monday,
                "Tue" => DayOfWeek.Tuesday,
                "Wed" => DayOfWeek.Wednesday,
                "Thu" => DayOfWeek.Thursday,
                "Fri" => DayOfWeek.Friday,
                "Sat" => DayOfWeek.Saturday,
                "Sun" => DayOfWeek.Sunday,
                _ => throw new ArgumentException("Unsupported debugger weekday."),
            };
            if (localTime.DayOfWeek != weekday)
                return false;
            TimeSpan offset = new(offsetHour, offsetMinute, 0);
            if (string.Equals(match.Groups["sign"].Value, "-", StringComparison.Ordinal))
                offset = -offset;
            _ = new DateTimeOffset(localTime, offset);
            return true;
        }
        catch (ArgumentException)
        {
            return false;
        }
    }

    static bool IsKnownBenignPreBeginLine(string line) =>
        System.Text.RegularExpressions.Regex.IsMatch(
            line,
            @"\A[0-9A-Fa-f]{1,8}:[0-9A-Fa-f]{1,8}> \.echo MORPH_CANARY_LASTEVENT_BEGIN; \.lastevent; \.echo MORPH_CANARY_LASTEVENT_END; \.echo MORPH_CANARY_CLEANUP_Q; q\z",
            System.Text.RegularExpressions.RegexOptions.CultureInvariant);

    static bool IsKnownBenignPostQuitLine(string line, string cdbExecutablePath)
    {
        const string prefix = "NatVis script unloaded from '";
        try
        {
            if (!Path.IsPathFullyQualified(cdbExecutablePath))
                return false;
            string? cdbDirectory = Path.GetDirectoryName(Path.GetFullPath(cdbExecutablePath));
            if (string.IsNullOrEmpty(cdbDirectory) ||
                !line.StartsWith(prefix, StringComparison.Ordinal) ||
                !line.EndsWith("'", StringComparison.Ordinal) ||
                line.Length <= prefix.Length + 1)
                return false;

            string unloadedPath = line[prefix.Length..^1];
            if (!Path.IsPathFullyQualified(unloadedPath) ||
                unloadedPath.Any(char.IsControl))
                return false;
            string fileName = Path.GetFileName(unloadedPath);
            if (fileName.Length <= ".natvis".Length ||
                !fileName.EndsWith(".natvis", StringComparison.OrdinalIgnoreCase) ||
                fileName.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0)
                return false;

            string expectedPath = Path.Combine(cdbDirectory, "Visualizers", fileName);
            return string.Equals(unloadedPath, expectedPath, StringComparison.OrdinalIgnoreCase);
        }
        catch (Exception ex) when (ex is ArgumentException or IOException or NotSupportedException)
        {
            return false;
        }
    }

    cleanupMarkerObserved = false;
    gracefulQuitObserved = false;
    targetExitEventObserved = false;
    targetExitCode = 0;
    terminalRegionDiagnosticClean = false;
    if (expectedTargetProcessId <= 0 || logLengthAtReadiness < 0 ||
        string.IsNullOrWhiteSpace(expectedCdbExecutablePath) ||
        !retainedLogStream.CanRead || !retainedLogStream.CanSeek)
        return false;
    const long maximumLogBytes = 16L * 1024L * 1024L;
    string transcript;
    string postReadinessTranscript;
    try
    {
        retainedLogStream.Flush();
        long finalizedLength = retainedLogStream.Length;
        if (finalizedLength < logLengthAtReadiness || finalizedLength > maximumLogBytes)
            return false;
        retainedLogStream.Seek(0, SeekOrigin.Begin);
        byte[] raw = new byte[checked((int)finalizedLength)];
        int totalRead = 0;
        while (totalRead < raw.Length)
        {
            int read = retainedLogStream.Read(raw, totalRead, raw.Length - totalRead);
            if (read == 0)
                return false;
            totalRead += read;
        }
        if (retainedLogStream.ReadByte() != -1 || retainedLogStream.Length != finalizedLength)
            return false;
        retainedLogStream.Seek(0, SeekOrigin.Begin);
        var strictUtf8 = new UTF8Encoding(false, true);
        transcript = strictUtf8.GetString(raw);
        postReadinessTranscript = strictUtf8.GetString(
            raw,
            checked((int)logLengthAtReadiness),
            checked((int)(finalizedLength - logLengthAtReadiness)));
        if (transcript.Length > 0 && transcript[0] == '\uFEFF')
            transcript = transcript[1..];
        if (logLengthAtReadiness == 0 && postReadinessTranscript.Length > 0 && postReadinessTranscript[0] == '\uFEFF')
            postReadinessTranscript = postReadinessTranscript[1..];
    }
    catch (Exception ex) when (ex is IOException or NotSupportedException or ObjectDisposedException or DecoderFallbackException or OverflowException)
    {
        return false;
    }
    const string beginMarker = "MORPH_CANARY_LASTEVENT_BEGIN";
    const string endMarker = "MORPH_CANARY_LASTEVENT_END";
    const string cleanupMarker = "MORPH_CANARY_CLEANUP_Q";
    const string quitMarker = "quit:";
    int beginCount = 0;
    int endCount = 0;
    int cleanupCount = 0;
    int quitCount = 0;
    int beginIndex = -1;
    int endIndex = -1;
    int cleanupIndex = -1;
    int quitIndex = -1;
    int globalLastEventCount = 0;
    int lineIndex = 0;
    bool insideSection = false;
    bool malformedProofLine = false;
    bool terminalRegionStarted = false;
    bool terminalRegionEnded = false;
    var sectionLines = new List<string>();
    var terminalRegionLines = new List<string>();
    foreach (string line in transcript.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None))
    {
        string trimmed = line.Trim();
        bool lastEventLine = trimmed.StartsWith("Last event:", StringComparison.Ordinal);
        bool beginMarkerLine = string.Equals(trimmed, beginMarker, StringComparison.Ordinal);
        bool quitMarkerLine = string.Equals(trimmed, quitMarker, StringComparison.Ordinal);
        if (beginMarkerLine && !terminalRegionStarted)
            terminalRegionStarted = true;
        if (terminalRegionStarted && !terminalRegionEnded && trimmed.Length > 0)
            terminalRegionLines.Add(trimmed);
        if (quitMarkerLine && terminalRegionStarted)
            terminalRegionEnded = true;
        if (lastEventLine)
            globalLastEventCount++;
        if (beginMarkerLine)
        {
            beginCount++;
            beginIndex = lineIndex;
            insideSection = true;
        }
        else if (string.Equals(trimmed, endMarker, StringComparison.Ordinal))
        {
            endCount++;
            endIndex = lineIndex;
            insideSection = false;
        }
        else if (string.Equals(trimmed, cleanupMarker, StringComparison.Ordinal))
        {
            cleanupCount++;
            cleanupIndex = lineIndex;
        }
        else if (string.Equals(trimmed, quitMarker, StringComparison.Ordinal))
        {
            quitCount++;
            quitIndex = lineIndex;
        }
        else if (insideSection)
        {
            sectionLines.Add(trimmed);
        }
        else if (
            lastEventLine ||
            trimmed.StartsWith("debugger time:", StringComparison.OrdinalIgnoreCase) ||
            trimmed.StartsWith("MORPH_CANARY_LASTEVENT_", StringComparison.Ordinal) ||
            trimmed.StartsWith(cleanupMarker, StringComparison.Ordinal) ||
            trimmed.StartsWith(quitMarker, StringComparison.Ordinal))
        {
            malformedProofLine = true;
        }
        lineIndex++;
        if (beginCount > 1 || endCount > 1 || cleanupCount > 1 || quitCount > 1)
            return false;
    }
    bool exactCardinality = beginCount == 1 && endCount == 1 && cleanupCount == 1 && quitCount == 1;
    bool exactOrder = beginIndex < endIndex && endIndex < cleanupIndex && cleanupIndex < quitIndex;
    cleanupMarkerObserved = cleanupCount == 1;
    gracefulQuitObserved = quitCount == 1;
    bool debuggerTimeMatches = sectionLines.Count == 2 && TryParseCdbDebuggerTime(sectionLines[1]);
    if (!exactCardinality || !exactOrder || insideSection || malformedProofLine ||
        globalLastEventCount != 1 || sectionLines.Count != 2 ||
        !debuggerTimeMatches)
        return false;

    bool postReadinessDiagnosticClean = true;
    bool postReadinessBeginSeen = false;
    bool postReadinessQuitSeen = false;
    foreach (string line in postReadinessTranscript.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None))
    {
        string trimmed = line.Trim();
        if (!postReadinessBeginSeen)
        {
            if (string.Equals(trimmed, beginMarker, StringComparison.Ordinal))
                postReadinessBeginSeen = true;
            else if (trimmed.Length > 0 && !IsKnownBenignPreBeginLine(trimmed))
                postReadinessDiagnosticClean = false;
            continue;
        }
        if (!postReadinessQuitSeen)
        {
            if (string.Equals(trimmed, quitMarker, StringComparison.Ordinal))
                postReadinessQuitSeen = true;
            continue;
        }
        if (line.Length > 0 && !IsKnownBenignPostQuitLine(line, expectedCdbExecutablePath))
            postReadinessDiagnosticClean = false;
    }

    terminalRegionDiagnosticClean = terminalRegionStarted && terminalRegionEnded &&
        postReadinessBeginSeen && postReadinessQuitSeen && postReadinessDiagnosticClean &&
        terminalRegionLines.Count == 6 &&
        string.Equals(terminalRegionLines[0], beginMarker, StringComparison.Ordinal) &&
        string.Equals(terminalRegionLines[1], sectionLines[0], StringComparison.Ordinal) &&
        string.Equals(terminalRegionLines[2], sectionLines[1], StringComparison.Ordinal) &&
        string.Equals(terminalRegionLines[3], endMarker, StringComparison.Ordinal) &&
        string.Equals(terminalRegionLines[4], cleanupMarker, StringComparison.Ordinal) &&
        string.Equals(terminalRegionLines[5], quitMarker, StringComparison.Ordinal);

    var match = System.Text.RegularExpressions.Regex.Match(
        sectionLines[0],
        @"\ALast event: (?<eventPid>[0-9A-Fa-f]{1,8})\.(?<threadId>[0-9A-Fa-f]{1,8}): Exit process 0:(?<exitPid>[0-9A-Fa-f]{1,8}), code (?<exitCode>[0-9A-Fa-f]{1,8})\z",
        System.Text.RegularExpressions.RegexOptions.CultureInvariant);
    if (!match.Success ||
        !int.TryParse(
            match.Groups["eventPid"].Value,
            System.Globalization.NumberStyles.AllowHexSpecifier,
            System.Globalization.CultureInfo.InvariantCulture,
            out int eventProcessId) ||
        !int.TryParse(
            match.Groups["exitPid"].Value,
            System.Globalization.NumberStyles.AllowHexSpecifier,
            System.Globalization.CultureInfo.InvariantCulture,
            out int exitProcessId) ||
        !int.TryParse(
            match.Groups["threadId"].Value,
            System.Globalization.NumberStyles.AllowHexSpecifier,
            System.Globalization.CultureInfo.InvariantCulture,
            out int threadId) ||
        !uint.TryParse(
            match.Groups["exitCode"].Value,
            System.Globalization.NumberStyles.AllowHexSpecifier,
            System.Globalization.CultureInfo.InvariantCulture,
            out targetExitCode) ||
        threadId <= 0)
        return false;

    targetExitEventObserved = eventProcessId == expectedTargetProcessId &&
        exitProcessId == expectedTargetProcessId;
    return cleanupMarkerObserved && gracefulQuitObserved && targetExitEventObserved;
}

static bool CdbExitCodeMatchesCleanupEvidence(
    int cdbExitCode,
    uint targetExitCode,
    bool managedForceRequested,
    bool managedExitObserved,
    bool terminalRegionDiagnosticClean)
{
    return cdbExitCode == 0 ||
        (cdbExitCode == -1 && targetExitCode == uint.MaxValue &&
         managedForceRequested && managedExitObserved && terminalRegionDiagnosticClean);
}

static (bool Graceful, string Status, bool CdbExitCodeAccepted, bool CdbExitCodeMatchedForcedTargetTermination) EvaluateFinalizedCdbCleanupEvidence(
    bool cdbExited,
    bool cdbForced,
    bool preStopBound,
    bool processWasRetained,
    bool processIdentityRevalidated,
    bool managedProcessStopped,
    bool finalizedLogAccepted,
    bool targetExitEventObserved,
    bool cleanupMarkerObserved,
    bool gracefulQuitObserved,
    int? cdbExitCode,
    uint targetExitCode,
    bool managedForceRequested,
    bool managedExitObserved,
    bool terminalRegionDiagnosticClean)
{
    bool cdbExitedNormally = cdbExited && cdbExitCode == 0;
    bool cdbExitCodeAccepted = cdbExited && cdbExitCode.HasValue &&
        CdbExitCodeMatchesCleanupEvidence(
            cdbExitCode.Value,
            targetExitCode,
            managedForceRequested,
            managedExitObserved,
            terminalRegionDiagnosticClean);
    bool cdbExitCodeMatchedForcedTargetTermination = cdbExitCodeAccepted && !cdbExitedNormally;
    bool graceful = preStopBound && processWasRetained && processIdentityRevalidated &&
        managedProcessStopped && !cdbForced && cdbExitCodeAccepted && finalizedLogAccepted &&
        targetExitEventObserved && cleanupMarkerObserved && gracefulQuitObserved;
    string status = graceful ? "exited-after-managed-stop" :
        cdbForced && cdbExited ? "forced-stopped-after-timeout" :
        cdbForced ? "forced-stop-failed" :
        !preStopBound ? "exited-without-pre-stop-binding" :
        !managedProcessStopped ? "exited-after-unbound-managed-stop" :
        !cdbExitCodeAccepted ? "cdb-exit-code-unbound" :
        !targetExitEventObserved ? "exited-without-target-exit-event" :
        "exited-without-queued-quit";
    return (graceful, status, cdbExitCodeAccepted, cdbExitCodeMatchedForcedTargetTermination);
}

static JsonElement? TryParseLastJsonPayload(string stdout)
{
    foreach (string line in stdout.Split(new[] { "\r\n", "\n" }, StringSplitOptions.RemoveEmptyEntries).Reverse())
    {
        string trimmed = line.Trim();
        if (!trimmed.StartsWith("{", StringComparison.Ordinal) || !trimmed.EndsWith("}", StringComparison.Ordinal))
            continue;

        try
        {
            using JsonDocument document = JsonDocument.Parse(trimmed);
            return document.RootElement.Clone();
        }
        catch (JsonException)
        {
        }
    }

    return null;
}

static int? JsonNullableInt(JsonElement element, string propertyName)
{
    if (element.ValueKind != JsonValueKind.Object)
        return null;

    return element.TryGetProperty(propertyName, out JsonElement property) &&
        property.ValueKind == JsonValueKind.Number &&
        property.TryGetInt32(out int value)
            ? value
            : null;
}

static JsonElement StartCdbObserver(
    string powershellExe,
    string scriptPath,
    int processId,
    string expectedExecutablePath,
    string expectedWorkingDirectory,
    string appOwnedProfilesRoot,
    string commandFile,
    string logPath,
    int logReadyTimeoutMilliseconds,
    string outputJson,
    string runtimeReceiptPath = "",
    string expectedReceiptSha256 = "",
    string expectedCommandSha256 = "",
    string requiredLogMarker = "",
    bool createNewOutput = false)
{
    Directory.CreateDirectory(Path.GetDirectoryName(logPath)!);
    Directory.CreateDirectory(Path.GetDirectoryName(outputJson)!);
    var startInfo = new ProcessStartInfo
    {
        FileName = powershellExe,
        UseShellExecute = false,
        RedirectStandardOutput = true,
        RedirectStandardError = true,
    };
    startInfo.ArgumentList.Add("-NoProfile");
    startInfo.ArgumentList.Add("-ExecutionPolicy");
    startInfo.ArgumentList.Add("Bypass");
    startInfo.ArgumentList.Add("-File");
    startInfo.ArgumentList.Add(scriptPath);
    startInfo.ArgumentList.Add("-ProcessId");
    startInfo.ArgumentList.Add(processId.ToString(System.Globalization.CultureInfo.InvariantCulture));
    startInfo.ArgumentList.Add("-ExpectedExecutablePath");
    startInfo.ArgumentList.Add(expectedExecutablePath);
    startInfo.ArgumentList.Add("-ExpectedWorkingDirectory");
    startInfo.ArgumentList.Add(expectedWorkingDirectory);
    startInfo.ArgumentList.Add("-AppOwnedProfilesRoot");
    startInfo.ArgumentList.Add(appOwnedProfilesRoot);
    startInfo.ArgumentList.Add("-LogPath");
    startInfo.ArgumentList.Add(logPath);
    startInfo.ArgumentList.Add("-CommandFile");
    startInfo.ArgumentList.Add(commandFile);
    startInfo.ArgumentList.Add("-AllowedCommandRoot");
    startInfo.ArgumentList.Add(Path.GetDirectoryName(commandFile)!);
    startInfo.ArgumentList.Add("-AllowedLogRoot");
    startInfo.ArgumentList.Add(Path.GetDirectoryName(logPath)!);
    startInfo.ArgumentList.Add("-LogReadyTimeoutMilliseconds");
    startInfo.ArgumentList.Add(logReadyTimeoutMilliseconds.ToString(System.Globalization.CultureInfo.InvariantCulture));
    if (!string.IsNullOrWhiteSpace(runtimeReceiptPath))
    {
        startInfo.ArgumentList.Add("-RuntimeReceiptPath");
        startInfo.ArgumentList.Add(runtimeReceiptPath);
        startInfo.ArgumentList.Add("-ExpectedReceiptSha256");
        startInfo.ArgumentList.Add(expectedReceiptSha256);
        startInfo.ArgumentList.Add("-ExpectedCommandSha256");
        startInfo.ArgumentList.Add(expectedCommandSha256);
        startInfo.ArgumentList.Add("-RequiredLogMarker");
        startInfo.ArgumentList.Add(requiredLogMarker);
    }

    using Process? process = Process.Start(startInfo);
    if (process is null)
        throw new InvalidOperationException("Could not start the exact-PID CDB observer helper.");

    string stdout = process.StandardOutput.ReadToEnd();
    string stderr = process.StandardError.ReadToEnd();
    process.WaitForExit();

    JsonElement? helperPayload = TryParseLastJsonPayload(stdout);
    int? cdbProcessId = helperPayload.HasValue ? JsonNullableInt(helperPayload.Value, "cdbProcessId") : null;
    bool logExists = File.Exists(logPath);
    long logSize = logExists ? new FileInfo(logPath).Length : 0;
    bool attached = process.ExitCode == 0 && logExists;
    var payload = new
    {
        schemaVersion = "cdb-observer-attach.v1",
        generatedAt = DateTimeOffset.UtcNow,
        status = attached ? "attached" : "failed",
        targetProcessId = processId,
        cdbProcessId,
        commandFile,
        logPath,
        logExists,
        logSize,
        exitCode = process.ExitCode,
        stdout,
        stderr,
        helperPayload,
        note = "Exact-PID copied-profile CDB observer attach. Command file is expected to use printf/disassembly/continue-style observations only."
    };
    string payloadJson = JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true });
    if (createNewOutput)
    {
        using FileStream output = new(outputJson, FileMode.CreateNew, FileAccess.Write, FileShare.None);
        using StreamWriter writer = new(output, new UTF8Encoding(false));
        writer.Write(payloadJson);
    }
    else
    {
        File.WriteAllText(outputJson, payloadJson);
    }
    return JsonSerializer.Deserialize<JsonElement>(payloadJson);
}

static JsonElement CleanupCdbObserver(int? cdbProcessId)
{
    if (!cdbProcessId.HasValue)
    {
        return JsonPayload(new
        {
            schemaVersion = "cdb-observer-cleanup.v1",
            generatedAt = DateTimeOffset.UtcNow,
            status = "not-started"
        });
    }

    try
    {
        using Process process = Process.GetProcessById(cdbProcessId.Value);
        process.Refresh();
        if (process.HasExited)
        {
            return JsonPayload(new
            {
                schemaVersion = "cdb-observer-cleanup.v1",
                generatedAt = DateTimeOffset.UtcNow,
                status = "already-exited",
                cdbProcessId
            });
        }

        process.Kill(entireProcessTree: true);
        bool exited = process.WaitForExit(3000);
        return JsonPayload(new
        {
            schemaVersion = "cdb-observer-cleanup.v1",
            generatedAt = DateTimeOffset.UtcNow,
            status = exited ? "stopped" : "still-running",
            cdbProcessId
        });
    }
    catch (ArgumentException)
    {
        return JsonPayload(new
        {
            schemaVersion = "cdb-observer-cleanup.v1",
            generatedAt = DateTimeOffset.UtcNow,
            status = "already-exited",
            cdbProcessId
        });
    }
    catch (Exception ex)
    {
        return JsonPayload(new
        {
            schemaVersion = "cdb-observer-cleanup.v1",
            generatedAt = DateTimeOffset.UtcNow,
            status = "failed",
            cdbProcessId,
            error = ex.GetType().Name + ": " + ex.Message
        });
    }
}

static int BoundedIntEnv(string name, int fallback, int min, int max)
{
    string? raw = Environment.GetEnvironmentVariable(name);
    if (!int.TryParse(raw, out int value))
        value = fallback;

    return Math.Clamp(value, min, max);
}

static ConfigurationKeybindRow Config2CensusRowQe(string rowId)
{
    (string GroupLabel, string ActionLabel, int EntryId, bool AllowLookMouse) = rowId.Trim().ToLowerInvariant() switch
    {
        "movement-forward" => ("Movement", "Forward", 0x1f, false),
        "movement-backward" => ("Movement", "Backward", 0x20, false),
        "movement-left" => ("Movement", "Left", 0x1d, false),
        "movement-right" => ("Movement", "Right", 0x1e, false),
        "look-up" => ("Look", "Up", 0x1a, true),
        "look-down" => ("Look", "Down", 0x1c, true),
        "look-left" => ("Look", "Left", 0x19, true),
        "look-right" => ("Look", "Right", 0x1b, true),
        _ => throw new InvalidOperationException($"Unsupported config-2 census row '{rowId}'.")
    };
    return new ConfigurationKeybindRow
    {
        GroupLabel = GroupLabel,
        ActionLabel = ActionLabel,
        EntryId = EntryId,
        KeyboardDeviceCode = 9u,
        AllowLookMouse = AllowLookMouse,
        CurrentPlayer1Token = "",
        CurrentPlayer2Token = "",
        Player1Token = "Q",
        Player2Token = "E"
    };
}

static object[] BuildByteDiffRanges(byte[] before, byte[] after, int maxRanges = 32)
{
    var ranges = new List<object>();
    int limit = Math.Min(before.Length, after.Length);
    int index = 0;
    while (index < limit && ranges.Count < maxRanges)
    {
        if (before[index] == after[index])
        {
            index++;
            continue;
        }

        int start = index;
        var beforeBytes = new List<byte>();
        var afterBytes = new List<byte>();
        while (index < limit && before[index] != after[index])
        {
            beforeBytes.Add(before[index]);
            afterBytes.Add(after[index]);
            index++;
        }

        ranges.Add(new
        {
            offset = start,
            offsetHex = $"0x{start:x}",
            length = index - start,
            beforeHex = Convert.ToHexString(beforeBytes.ToArray()).ToLowerInvariant(),
            afterHex = Convert.ToHexString(afterBytes.ToArray()).ToLowerInvariant()
        });
    }

    if (before.Length != after.Length && ranges.Count < maxRanges)
    {
        ranges.Add(new
        {
            offset = limit,
            offsetHex = $"0x{limit:x}",
            length = Math.Abs(before.Length - after.Length),
            beforeHex = before.Length > after.Length ? "file-has-extra-bytes" : string.Empty,
            afterHex = after.Length > before.Length ? "file-has-extra-bytes" : string.Empty
        });
    }

    return ranges.ToArray();
}

static object[] SnapshotRelativeFileHashes(string root, string searchPattern)
{
    string resolvedRoot = Path.GetFullPath(root);
    return Directory.GetFiles(resolvedRoot, searchPattern, SearchOption.TopDirectoryOnly)
        .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
        .Select(path => new
        {
            relativePath = Path.GetRelativePath(resolvedRoot, path).Replace('\\', '/'),
            size = new FileInfo(path).Length,
            sha256 = Sha256File(path)
        })
        .Cast<object>()
        .ToArray();
}

static object ReceiptFileIdentity(string path)
{
    string resolved = Path.GetFullPath(path);
    FileInfo info = new(resolved);
    return new
    {
        path = resolved,
        sha256 = Sha256File(resolved),
        size = info.Length,
    };
}

static void AssertFreshCanaryWriteTarget(string path, string artifactRoot)
{
    string resolvedRoot = Path.GetFullPath(artifactRoot).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
    string resolvedPath = Path.GetFullPath(path);
    if (!resolvedPath.StartsWith(resolvedRoot, StringComparison.OrdinalIgnoreCase))
        throw new InvalidOperationException("Canary write target escaped the private artifact root.");
    if (File.Exists(resolvedPath) || Directory.Exists(resolvedPath))
        throw new IOException("Canary write target already exists: " + resolvedPath);
    string? current = Path.GetDirectoryName(resolvedPath);
    while (!string.IsNullOrWhiteSpace(current) &&
           current.StartsWith(resolvedRoot, StringComparison.OrdinalIgnoreCase))
    {
        if (File.Exists(current) || Directory.Exists(current))
        {
            FileAttributes attributes = File.GetAttributes(current);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new IOException("Canary write path crosses a reparse point: " + current);
        }
        current = Path.GetDirectoryName(current);
    }
}

static void WriteNewCanaryText(string path, string artifactRoot, string contents)
{
    AssertFreshCanaryWriteTarget(path, artifactRoot);
    using FileStream stream = new(path, FileMode.CreateNew, FileAccess.Write, FileShare.None);
    using StreamWriter writer = new(stream, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    writer.Write(contents);
    writer.Flush();
    stream.Flush(flushToDisk: true);
}

static string WriteRuntimeProcessReceipt(
    string receiptPath,
    string artifactRoot,
    GameProfileManagedProcess managed,
    string manifestPath,
    string hwndHex,
    string[] launchArguments,
    string sourceExecutableSha256,
    string copiedExecutableSha256,
    string commandTemplateSha256,
    string generatedCommandSha256)
{
    using Process process = Process.GetProcessById(managed.ProcessId);
    process.Refresh();
    ProcessModule module = process.MainModule ??
        throw new InvalidOperationException("Could not inspect the managed BEA main module.");
    string startedAtUtc = process.StartTime.ToUniversalTime().ToString("o");
    string modulePath = Path.GetFullPath(module.FileName);
    var receipt = new
    {
        schemaVersion = "runtime-process-receipt.v1",
        runId = Guid.NewGuid().ToString("D"),
        process = new
        {
            id = process.Id,
            startedAtUtc,
            executable = ReceiptFileIdentity(managed.ExecutablePath),
            workingDirectory = Path.GetFullPath(managed.WorkingDirectory),
            launchArguments,
        },
        profileManifest = ReceiptFileIdentity(manifestPath),
        window = new { hwndHex = hwndHex.ToUpperInvariant().Replace("0X", "0x") },
        module = new
        {
            path = modulePath,
            baseAddressHex = $"0x{module.BaseAddress.ToInt64():X}",
            size = module.ModuleMemorySize,
        },
        sourceExecutableSha256,
        copiedExecutableSha256,
        commandTemplateSha256,
        generatedCommandSha256,
    };
    WriteNewCanaryText(
        receiptPath,
        artifactRoot,
        JsonSerializer.Serialize(receipt, new JsonSerializerOptions { WriteIndented = true }));
    return Sha256File(receiptPath);
}

static bool ValidateRuntimeReceipt(
    string powershellExe,
    string runtimeIdentityModule,
    string runtimeReceiptPath,
    string expectedReceiptSha256,
    string expectedCommandSha256,
    string expectedTemplateSha256,
    bool requireWindow,
    out string failure)
{
    try
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = powershellExe,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-NoProfile");
        startInfo.ArgumentList.Add("-Command");
        startInfo.ArgumentList.Add("& { param($modulePath, $receiptPath, $receiptSha256, $requireWindow) Import-Module -Name $modulePath -Force -ErrorAction Stop; $parameters = @{ ReceiptPath = $receiptPath; ExpectedReceiptSha256 = $receiptSha256 }; if ($requireWindow -eq '1') { Assert-RuntimeProcessReceipt @parameters -RequireWindow | Out-Null } else { Assert-RuntimeProcessReceipt @parameters | Out-Null } }");
        startInfo.ArgumentList.Add(runtimeIdentityModule);
        startInfo.ArgumentList.Add(runtimeReceiptPath);
        startInfo.ArgumentList.Add(expectedReceiptSha256);
        startInfo.ArgumentList.Add(requireWindow ? "1" : "0");
        using Process? validator = Process.Start(startInfo);
        if (validator is null)
        {
            failure = "Could not start runtime receipt validator.";
            return false;
        }
        string stdout = validator.StandardOutput.ReadToEnd();
        string stderr = validator.StandardError.ReadToEnd();
        validator.WaitForExit();
        if (validator.ExitCode != 0)
        {
            failure = string.IsNullOrWhiteSpace(stderr) ? stdout : stderr;
            return false;
        }
        using JsonDocument receipt = JsonDocument.Parse(File.ReadAllText(runtimeReceiptPath));
        if (!receipt.RootElement.TryGetProperty("generatedCommandSha256", out JsonElement commandDigest) ||
            !string.Equals(commandDigest.GetString(), expectedCommandSha256, StringComparison.Ordinal) ||
            !string.Equals(
                receipt.RootElement.GetProperty("commandTemplateSha256").GetString(),
                expectedTemplateSha256,
                StringComparison.Ordinal))
        {
            failure = "Runtime receipt command or template digest changed.";
            return false;
        }
        failure = string.Empty;
        return true;
    }
    catch (Exception ex)
    {
        failure = ex.GetType().Name + ": " + ex.Message;
        return false;
    }
}

static bool ValidateCanaryBinding(
    string powershellExe,
    string runtimeIdentityModule,
    string runtimeReceiptPath,
    string expectedReceiptSha256,
    string commandFile,
    string expectedCommandSha256,
    string templatePath,
    string expectedTemplateSha256,
    bool requireWindow,
    out string failure)
{
    if (!ValidateRuntimeReceipt(
            powershellExe,
            runtimeIdentityModule,
            runtimeReceiptPath,
            expectedReceiptSha256,
            expectedCommandSha256,
            expectedTemplateSha256,
            requireWindow,
            out failure))
        return false;
    try
    {
        if (!string.Equals(Sha256File(commandFile), expectedCommandSha256, StringComparison.Ordinal) ||
            !string.Equals(Sha256File(templatePath), expectedTemplateSha256, StringComparison.Ordinal))
        {
            failure = "Rendered command or tracked template digest changed.";
            return false;
        }
        failure = string.Empty;
        return true;
    }
    catch (Exception ex)
    {
        failure = ex.GetType().Name + ": " + ex.Message;
        return false;
    }
}

static JsonElement BestEffortReleaseCanaryKeys(
    bool roleHadInput,
    string powershellExe,
    string inputScript,
    int processId,
    string hwndHex,
    string executablePath,
    string workingDirectory,
    int stepDelayMs,
    string outputJson,
    string runtimeReceiptPath,
    string expectedReceiptSha256)
{
    if (!roleHadInput)
        return JsonPayload(new { status = "not-needed", bestEffort = true });
    try
    {
        JsonElement result = SendInputSequence(
            powershellExe,
            inputScript,
            processId,
            hwndHex,
            executablePath,
            workingDirectory,
            "up:Q",
            stepDelayMs,
            false,
            string.Empty,
            outputJson,
            runtimeReceiptPath,
            expectedReceiptSha256,
            true);
        bool attempted = JsonStringIn(result, "status", "sent");
        return JsonPayload(new { status = attempted ? "best-effort-sent" : "failed", bestEffort = true, result });
    }
    catch (Exception ex)
    {
        return JsonPayload(new { status = "failed", bestEffort = true, error = ex.GetType().Name + ": " + ex.Message });
    }
}

static bool TryReadCdbObserverIdentity(
    JsonElement? attachResult,
    out int cdbProcessId,
    out string cdbStartedAtUtc,
    out string cdbExecutablePath,
    out string logPath,
    out string failure)
{
    cdbProcessId = 0;
    cdbStartedAtUtc = string.Empty;
    cdbExecutablePath = string.Empty;
    logPath = string.Empty;
    failure = string.Empty;
    try
    {
        if (!attachResult.HasValue || attachResult.Value.ValueKind != JsonValueKind.Object ||
            !attachResult.Value.TryGetProperty("helperPayload", out JsonElement helper) ||
            helper.ValueKind != JsonValueKind.Object)
        {
            failure = "CDB attach result did not contain a helper payload.";
            return false;
        }

        int? parsedProcessId = JsonNullableInt(helper, "cdbProcessId");
        string? parsedStartedAtUtc = helper.TryGetProperty("cdbStartedAtUtc", out JsonElement started) &&
            started.ValueKind == JsonValueKind.String ? started.GetString() : null;
        string? parsedExecutablePath = helper.TryGetProperty("cdbExecutablePath", out JsonElement executable) &&
            executable.ValueKind == JsonValueKind.String ? executable.GetString() : null;
        string? helperLogPath = helper.TryGetProperty("logPath", out JsonElement helperLog) &&
            helperLog.ValueKind == JsonValueKind.String ? helperLog.GetString() : null;
        string? attachLogPath = attachResult.Value.TryGetProperty("logPath", out JsonElement attachLog) &&
            attachLog.ValueKind == JsonValueKind.String ? attachLog.GetString() : null;
        if (!parsedProcessId.HasValue || parsedProcessId.Value <= 0 ||
            string.IsNullOrWhiteSpace(parsedStartedAtUtc) ||
            string.IsNullOrWhiteSpace(parsedExecutablePath) ||
            string.IsNullOrWhiteSpace(helperLogPath) ||
            string.IsNullOrWhiteSpace(attachLogPath))
        {
            failure = "CDB attach result did not contain complete process and log identity.";
            return false;
        }
        if (!string.Equals(
                Path.GetFullPath(helperLogPath),
                Path.GetFullPath(attachLogPath),
                StringComparison.OrdinalIgnoreCase))
        {
            failure = "CDB helper and attach log paths differ.";
            return false;
        }

        cdbProcessId = parsedProcessId.Value;
        cdbStartedAtUtc = parsedStartedAtUtc;
        cdbExecutablePath = Path.GetFullPath(parsedExecutablePath);
        logPath = Path.GetFullPath(attachLogPath);
        return true;
    }
    catch (Exception ex)
    {
        failure = ex.GetType().Name + ": " + ex.Message;
        return false;
    }
}

static bool CdbCanaryArgumentsMatch(
    JsonElement? attachResult,
    int expectedTargetProcessId,
    string expectedLogPath,
    string expectedCommandFile)
{
    if (!attachResult.HasValue || attachResult.Value.ValueKind != JsonValueKind.Object ||
        !attachResult.Value.TryGetProperty("helperPayload", out JsonElement helper) ||
        helper.ValueKind != JsonValueKind.Object ||
        !JsonIntEquals(helper, "targetProcessId", expectedTargetProcessId) ||
        !helper.TryGetProperty("remoteServerEnabled", out JsonElement remote) ||
        remote.ValueKind != JsonValueKind.False ||
        !helper.TryGetProperty("effectiveArguments", out JsonElement arguments) ||
        arguments.ValueKind != JsonValueKind.Array || arguments.GetArrayLength() != 11)
        return false;

    string[] expected =
    {
        "-pd",
        "-noshell",
        "-ee",
        "masm",
        "-logo",
        Path.GetFullPath(expectedLogPath),
        "-p",
        expectedTargetProcessId.ToString(System.Globalization.CultureInfo.InvariantCulture),
        "-noio",
        "-cf",
        Path.GetFullPath(expectedCommandFile),
    };
    for (int index = 0; index < expected.Length; index++)
    {
        JsonElement argument = arguments[index];
        if (argument.ValueKind != JsonValueKind.String)
            return false;
        string actual = argument.GetString() ?? string.Empty;
        bool matches = index is 5 or 10
            ? string.Equals(Path.GetFullPath(actual), expected[index], StringComparison.OrdinalIgnoreCase)
            : string.Equals(actual, expected[index], StringComparison.Ordinal);
        if (!matches)
            return false;
    }
    return true;
}

static JsonElement ValidateExactCdbObserverForManagedStop(
    JsonElement? attachResult,
    string powershellExe,
    string runtimeIdentityModule,
    string runtimeReceiptPath,
    string expectedReceiptSha256,
    string commandFile,
    string expectedCommandSha256,
    string templatePath,
    string expectedTemplateSha256,
    string expectedLogPath,
    string requiredLogMarker,
    FileStream? retainedLogStream,
    out Process? boundCdbProcess)
{
    boundCdbProcess = null;
    bool receiptBound = ValidateCanaryBinding(
        powershellExe,
        runtimeIdentityModule,
        runtimeReceiptPath,
        expectedReceiptSha256,
        commandFile,
        expectedCommandSha256,
        templatePath,
        expectedTemplateSha256,
        true,
        out string receiptFailure);
    if (!TryReadCdbObserverIdentity(
            attachResult,
            out int cdbProcessId,
            out string startedAtUtc,
            out string executablePath,
            out string logPath,
            out string identityFailure))
        return JsonPayload(new { status = "identity-missing", receiptBound, processBound = false, receiptFailure, identityFailure });
    int expectedTargetProcessId = attachResult.HasValue
        ? JsonInt(attachResult.Value, "targetProcessId")
        : 0;
    if (!string.Equals(logPath, Path.GetFullPath(expectedLogPath), StringComparison.OrdinalIgnoreCase) ||
        expectedTargetProcessId <= 0 ||
        !CdbCanaryArgumentsMatch(attachResult, expectedTargetProcessId, logPath, commandFile) ||
        retainedLogStream is null ||
        !CdbObserverReady(attachResult, expectedReceiptSha256, expectedCommandSha256, logPath, requiredLogMarker, retainedLogStream))
        return JsonPayload(new { status = "observer-not-ready", receiptBound, processBound = false, receiptFailure, cdbProcessId });
    Process? process = null;
    try
    {
        process = Process.GetProcessById(cdbProcessId);
        process.Refresh();
        if (process.HasExited)
            return JsonPayload(new { status = "already-exited", receiptBound, processBound = false, receiptFailure, cdbProcessId });
        _ = process.SafeHandle;
        DateTime expectedStart = DateTime.ParseExact(
            startedAtUtc,
            "o",
            System.Globalization.CultureInfo.InvariantCulture,
            System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime();
        string actualPath = Path.GetFullPath(process.MainModule?.FileName ?? string.Empty);
        bool processBound = process.StartTime.ToUniversalTime().Ticks == expectedStart.Ticks &&
            string.Equals(actualPath, Path.GetFullPath(executablePath), StringComparison.OrdinalIgnoreCase);
        if (!processBound)
            return JsonPayload(new { status = "identity-mismatch", receiptBound, processBound, receiptFailure, cdbProcessId });
        boundCdbProcess = process;
        process = null;
        if (!receiptBound)
            return JsonPayload(new { status = "receipt-unbound", receiptBound, processBound, receiptFailure, cdbProcessId });
        return JsonPayload(new
        {
            status = "ready-for-managed-stop",
            receiptBound,
            processBound,
            receiptFailure,
            cdbProcessId,
            cdbStartedAtUtc = startedAtUtc,
            cdbExecutablePath = executablePath,
            logPath,
        });
    }
    catch (ArgumentException)
    {
        return JsonPayload(new { status = "already-exited", receiptBound, processBound = false, receiptFailure, cdbProcessId });
    }
    catch (Exception ex)
    {
        return JsonPayload(new { status = "failed", receiptBound, processBound = false, receiptFailure, cdbProcessId, error = ex.GetType().Name + ": " + ex.Message });
    }
    finally
    {
        process?.Dispose();
    }
}

static JsonElement FinalizeExactCdbObserverAfterManagedStop(
    JsonElement? attachResult,
    JsonElement preStopResult,
    Process? boundCdbProcess,
    FileStream? boundCdbLogStream,
    long cdbLogLengthAtReadiness,
    bool stopReceiptBound,
    GameProfileStopResult? stopResult,
    string expectedLogPath)
{
    if (!TryReadCdbObserverIdentity(
            attachResult,
            out int cdbProcessId,
            out string startedAtUtc,
            out string executablePath,
            out string logPath,
            out string identityFailure))
        return JsonPayload(new { status = "identity-missing", receiptBound = false, exited = false, gracefulQuitObserved = false, identityFailure });

    bool preStopBound = JsonStringIn(preStopResult, "status", "ready-for-managed-stop") &&
        JsonBool(preStopResult, "receiptBound") &&
        JsonBool(preStopResult, "processBound") &&
        JsonIntEquals(preStopResult, "cdbProcessId", cdbProcessId) &&
        preStopResult.TryGetProperty("cdbStartedAtUtc", out JsonElement preStopStarted) &&
        preStopStarted.ValueKind == JsonValueKind.String &&
        string.Equals(preStopStarted.GetString(), startedAtUtc, StringComparison.Ordinal) &&
        preStopResult.TryGetProperty("cdbExecutablePath", out JsonElement preStopExecutable) &&
        preStopExecutable.ValueKind == JsonValueKind.String &&
        string.Equals(
            Path.GetFullPath(preStopExecutable.GetString() ?? string.Empty),
            Path.GetFullPath(executablePath),
            StringComparison.OrdinalIgnoreCase) &&
        preStopResult.TryGetProperty("logPath", out JsonElement preStopLog) &&
        preStopLog.ValueKind == JsonValueKind.String &&
        string.Equals(Path.GetFullPath(preStopLog.GetString() ?? string.Empty), logPath, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(logPath, Path.GetFullPath(expectedLogPath), StringComparison.OrdinalIgnoreCase);
    bool managedProcessStopped = stopReceiptBound && stopResult?.Success == true &&
        stopResult.LiveBeforeStop && stopResult.StopRequested && stopResult.ExitObserved &&
        !stopResult.AlreadyGone && stopResult.ExitTime.HasValue;
    bool exited = false;
    bool forced = false;
    bool processWasRetained = boundCdbProcess is not null;
    bool processIdentityRevalidated = false;
    DateTime? observedCdbExitTimeUtc = null;
    int? observedCdbExitCode = null;
    Process? process = boundCdbProcess;
    try
    {
        if (process is null)
            process = Process.GetProcessById(cdbProcessId);
        process.Refresh();
        if (!process.HasExited)
        {
            _ = process.SafeHandle;
            DateTime expectedStart = DateTime.ParseExact(
                startedAtUtc,
                "o",
                System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime();
            string actualPath = Path.GetFullPath(process.MainModule?.FileName ?? string.Empty);
            bool identityMatches = process.StartTime.ToUniversalTime().Ticks == expectedStart.Ticks &&
                string.Equals(actualPath, Path.GetFullPath(executablePath), StringComparison.OrdinalIgnoreCase);
            if (!identityMatches)
                return JsonPayload(new { status = "identity-mismatch", receiptBound = preStopBound && stopReceiptBound, exited = false, gracefulQuitObserved = false, cdbProcessId });
            processIdentityRevalidated = true;

            exited = process.WaitForExit(10000);
            if (!exited)
            {
                forced = true;
                process.Kill(entireProcessTree: false);
                exited = process.WaitForExit(3000);
            }
        }
        else
        {
            exited = true;
            processIdentityRevalidated = processWasRetained;
        }
        if (exited)
        {
            process.Refresh();
            observedCdbExitCode = process.ExitCode;
            observedCdbExitTimeUtc = process.ExitTime.ToUniversalTime();
        }
    }
    catch (ArgumentException)
    {
        return JsonPayload(new { status = "exited-without-retained-handle", receiptBound = false, exited = true, gracefulQuitObserved = false, forced, cdbProcessId });
    }
    catch (Exception ex)
    {
        return JsonPayload(new { status = "failed", receiptBound = preStopBound && stopReceiptBound, exited, gracefulQuitObserved = false, cdbProcessId, error = ex.GetType().Name + ": " + ex.Message });
    }
    finally
    {
        process?.Dispose();
    }

    bool cleanupMarkerObserved = false;
    bool gracefulQuitObserved = false;
    bool targetExitEventObserved = false;
    uint targetExitCode = 0;
    bool terminalRegionDiagnosticClean = false;
    bool cdbExitedNormally = exited && observedCdbExitCode == 0;
    bool finalizedLogAccepted = !forced && exited && managedProcessStopped && stopResult is not null &&
        boundCdbLogStream is not null &&
        TryReadFinalizedCdbExitEvidence(boundCdbLogStream, cdbLogLengthAtReadiness, stopResult.ProcessId, executablePath, out cleanupMarkerObserved, out gracefulQuitObserved, out targetExitEventObserved, out targetExitCode, out terminalRegionDiagnosticClean);
    var cleanupDecision = EvaluateFinalizedCdbCleanupEvidence(
        exited, forced, preStopBound, processWasRetained, processIdentityRevalidated,
        managedProcessStopped, finalizedLogAccepted, targetExitEventObserved,
        cleanupMarkerObserved, gracefulQuitObserved, observedCdbExitCode, targetExitCode,
        stopResult?.ForceRequested == true, stopResult?.ExitObserved == true,
        terminalRegionDiagnosticClean);
    bool graceful = cleanupDecision.Graceful;
    string status = cleanupDecision.Status;
    bool cdbExitCodeAccepted = cleanupDecision.CdbExitCodeAccepted;
    bool cdbExitCodeMatchedForcedTargetTermination = cleanupDecision.CdbExitCodeMatchedForcedTargetTermination;
    return JsonPayload(new
    {
        status,
        receiptBound = preStopBound && stopReceiptBound,
        exited,
        gracefulQuitObserved,
        cleanupMarkerObserved,
        targetExitEventObserved,
        targetExitCode,
        terminalRegionDiagnosticClean,
        cdbExitedNormally,
        cdbExitCodeMatchedForcedTargetTermination,
        cdbExitCodeAccepted,
        processWasRetained,
        processIdentityRevalidated,
        forced,
        cdbProcessId,
        cdbStartedAtUtc = startedAtUtc,
        cdbExecutablePath = executablePath,
        managedExitTimeUtc = stopResult?.ExitTime,
        cdbExitTimeUtc = observedCdbExitTimeUtc,
        cdbExitCode = observedCdbExitCode,
        logPath,
    });
}

static GameProfileStopResult? StopReceiptBoundManagedProcess(
    GameProfileManagedProcess? managed,
    string profilesRoot,
    string powershellExe,
    string runtimeIdentityModule,
    string runtimeReceiptPath,
    string expectedReceiptSha256,
    string commandFile,
    string expectedCommandSha256,
    string templatePath,
    string expectedTemplateSha256,
    out bool receiptBound,
    out string failure,
    out long runnerStopCallBeginTimestamp,
    out long runnerStopCallReturnedTimestamp)
{
    receiptBound = false;
    failure = string.Empty;
    runnerStopCallBeginTimestamp = 0;
    runnerStopCallReturnedTimestamp = 0;
    if (managed is null)
        return null;
    bool requireWindow = true;
    if (File.Exists(runtimeReceiptPath))
    {
        using JsonDocument receipt = JsonDocument.Parse(File.ReadAllText(runtimeReceiptPath));
        requireWindow = !string.Equals(
            receipt.RootElement.GetProperty("window").GetProperty("hwndHex").GetString(),
            "0x0",
            StringComparison.Ordinal);
    }
    receiptBound = ValidateCanaryBinding(
        powershellExe,
        runtimeIdentityModule,
        runtimeReceiptPath,
        expectedReceiptSha256,
        commandFile,
        expectedCommandSha256,
        templatePath,
        expectedTemplateSha256,
        requireWindow,
        out failure);
    runnerStopCallBeginTimestamp = Stopwatch.GetTimestamp();
    GameProfileStopResult result;
    try
    {
        result = GameProfileRuntimeService.StopCopiedProfile(
            managed,
            profilesRoot,
            gracefulTimeout: TimeSpan.FromSeconds(3));
    }
    finally
    {
        runnerStopCallReturnedTimestamp = Stopwatch.GetTimestamp();
    }
    bool exactTerminalStop = result.Success && result.ProcessId == managed.ProcessId &&
        result.LiveBeforeStop && result.StopRequested && result.ExitObserved &&
        !result.AlreadyGone && result.ExitTime.HasValue;
    if (result.Success && !exactTerminalStop)
    {
        failure = "Managed stop reported success without exact live-before-stop, request, exit, and exit-time evidence.";
        return result with { Success = false, Message = failure };
    }
    return result;
}

static JsonElement InspectOwnedProcessCensus(
    string runtimeReceiptPath,
    string? managedExecutablePath,
    JsonElement? cdbAttachResult)
{
    var ownedProcessIds = new HashSet<int>();
    int inspectionFailures = 0;
    string? executablePath = string.IsNullOrWhiteSpace(managedExecutablePath)
        ? null
        : Path.GetFullPath(managedExecutablePath);
    if (File.Exists(runtimeReceiptPath))
    {
        try
        {
            using JsonDocument receipt = JsonDocument.Parse(File.ReadAllText(runtimeReceiptPath));
            executablePath = receipt.RootElement
                .GetProperty("process")
                .GetProperty("executable")
                .GetProperty("path")
                .GetString()!;
        }
        catch
        {
            inspectionFailures++;
        }
    }
    if (!string.IsNullOrWhiteSpace(executablePath))
    {
        foreach (Process process in Process.GetProcessesByName("BEA"))
        {
            using (process)
            {
                try
                {
                    string actualPath = Path.GetFullPath(process.MainModule?.FileName ?? string.Empty);
                    if (!process.HasExited && string.Equals(
                        actualPath,
                        Path.GetFullPath(executablePath),
                        StringComparison.OrdinalIgnoreCase))
                        ownedProcessIds.Add(process.Id);
                }
                catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
                {
                    try
                    {
                        process.Refresh();
                        if (!process.HasExited)
                            inspectionFailures++;
                    }
                    catch
                    {
                        inspectionFailures++;
                    }
                }
            }
        }
    }
    if (cdbAttachResult.HasValue)
    {
        if (!TryReadCdbObserverIdentity(
                cdbAttachResult,
                out int cdbProcessId,
                out string cdbStartedAtUtc,
                out string cdbExecutablePath,
                out _,
                out _))
        {
            inspectionFailures++;
        }
        else
        {
            try
            {
                using Process process = Process.GetProcessById(cdbProcessId);
                process.Refresh();
                if (!process.HasExited)
                {
                    DateTime expectedStart = DateTime.ParseExact(
                        cdbStartedAtUtc,
                        "o",
                        System.Globalization.CultureInfo.InvariantCulture,
                        System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime();
                    string actualPath = Path.GetFullPath(process.MainModule?.FileName ?? string.Empty);
                    if (process.StartTime.ToUniversalTime().Ticks == expectedStart.Ticks &&
                        string.Equals(actualPath, Path.GetFullPath(cdbExecutablePath), StringComparison.OrdinalIgnoreCase))
                        ownedProcessIds.Add(cdbProcessId);
                }
            }
            catch (ArgumentException)
            {
            }
            catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                inspectionFailures++;
            }
        }
    }
    int ownedProcessCount = ownedProcessIds.Count;
    string status = inspectionFailures == 0 && ownedProcessCount == 0 ? "clear" :
        inspectionFailures > 0 ? "inspection-failed" : "not-clear";
    return JsonPayload(new
    {
        status,
        ownedProcessCount,
        inspectionFailureCount = inspectionFailures,
    });
}

static string AppendCleanupFailure(string failure, string phase, Exception ex) =>
    string.IsNullOrWhiteSpace(failure)
        ? $"Cleanup {phase} failed: {ex.GetType().Name}: {ex.Message}"
        : failure + $" | Cleanup {phase} failed: {ex.GetType().Name}: {ex.Message}";

static int RunWalkerProfilePreparationPhase()
{
    string sourceRoot = RequiredEnv("ONSLAUGHT_LIVE_SOURCE_ROOT");
    string profilesRoot = RequiredEnv("ONSLAUGHT_LIVE_PROFILES_ROOT");
    string exeOverride = RequiredEnv("ONSLAUGHT_LIVE_EXE_OVERRIDE");
    string artifactRoot = RequiredEnv("ONSLAUGHT_LIVE_WALKER_AUTHORIZED_ROOT");
    string receiptPath = RequiredEnv("ONSLAUGHT_LIVE_WALKER_PHASE_RECEIPT");
    string[] launchArguments = JsonSerializer.Deserialize<string[]>(
        RequiredEnv("ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON")) ?? Array.Empty<string>();
    try
    {
        GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
            new GameProfilePrepareOptions(
                SourceGameRoot: sourceRoot, OutputRoot: profilesRoot,
                ProfileName: "walker-measurement", ExecutableOverridePath: exeOverride,
                ApplyWindowedCompatibilityPatch: false, AllowByteLayoutOnlyTarget: false,
                IncludeSavegames: false, PatchKeys: Array.Empty<string>(),
                LaunchArguments: launchArguments, ProfilePresetId: null));
        WriteNewCanaryText(receiptPath, artifactRoot, JsonSerializer.Serialize(new {
            passed = true, prepared.TargetGameRoot, prepared.ExecutablePath, prepared.ManifestPath,
        }, new JsonSerializerOptions { WriteIndented = true }));
        return 0;
    }
    catch (Exception ex)
    {
        WriteNewCanaryText(receiptPath, artifactRoot, JsonSerializer.Serialize(new {
            passed = false, failure = ex.GetType().Name + ": " + ex.Message,
        }, new JsonSerializerOptions { WriteIndented = true }));
        return 2;
    }
}

static int RunWalkerLaunchPhase()
{
    string profilesRoot = RequiredEnv("ONSLAUGHT_LIVE_PROFILES_ROOT");
    string profileRoot = RequiredEnv("ONSLAUGHT_LIVE_WALKER_PREPARED_PROFILE_ROOT");
    string artifactRoot = RequiredEnv("ONSLAUGHT_LIVE_WALKER_AUTHORIZED_ROOT");
    string receiptPath = RequiredEnv("ONSLAUGHT_LIVE_WALKER_PHASE_RECEIPT");
    string[] launchArguments = JsonSerializer.Deserialize<string[]>(
        RequiredEnv("ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON")) ?? Array.Empty<string>();
    try
    {
        GameProfileManagedProcess managed = GameProfileRuntimeService.LaunchCopiedProfile(
            new GameProfileLaunchOptions(
                ProfileRoot: profileRoot, AppOwnedProfilesRoot: profilesRoot,
                LaunchArguments: launchArguments));
        WriteNewCanaryText(receiptPath, artifactRoot, JsonSerializer.Serialize(new {
            passed = true, managed.ProcessId, managed.ExecutablePath, managed.WorkingDirectory,
            Arguments = managed.Arguments, managed.StartedAt, managed.ManifestPath,
        }, new JsonSerializerOptions { WriteIndented = true }));
        return 0;
    }
    catch (Exception ex)
    {
        WriteNewCanaryText(receiptPath, artifactRoot, JsonSerializer.Serialize(new {
            passed = false, failure = ex.GetType().Name + ": " + ex.Message,
        }, new JsonSerializerOptions { WriteIndented = true }));
        return 2;
    }
}

static void WaitWalkerOwnedPhase(
    WalkerOwnedPhaseProcess phase, TimeSpan bound, string cooperativeStopFile)
{
    Stopwatch elapsed = Stopwatch.StartNew();
    while (!phase.Process.WaitForExit(100))
    {
        if (File.Exists(cooperativeStopFile) || elapsed.Elapsed >= bound)
        {
            phase.TerminateExactJobAndClose();
            throw new TimeoutException($"Walker {phase.Name} phase exceeded its cooperative safety bound.");
        }
    }
    if (phase.Process.ExitCode != 0)
        throw new InvalidOperationException($"Walker {phase.Name} phase exited with code {phase.Process.ExitCode}.");
}

static int RunWalkerTrajectoryAttempt()
{
    string sourceRoot = RequiredEnv("ONSLAUGHT_LIVE_SOURCE_ROOT");
    string profilesRoot = RequiredEnv("ONSLAUGHT_LIVE_PROFILES_ROOT");
    string artifactRoot = RequiredEnv("ONSLAUGHT_LIVE_WALKER_AUTHORIZED_ROOT");
    string exeOverride = RequiredEnv("ONSLAUGHT_LIVE_EXE_OVERRIDE");
    string inputScript = RequiredEnv("ONSLAUGHT_LIVE_INPUT_SCRIPT");
    string powershellExe = RequiredEnv("ONSLAUGHT_LIVE_POWERSHELL");
    string runtimeReceiptPath = RequiredEnv("ONSLAUGHT_LIVE_RUNTIME_RECEIPT_PATH");
    string runtimeIdentityModule = RequiredEnv("ONSLAUGHT_LIVE_RUNTIME_IDENTITY_MODULE");
    string adapterPath = RequiredEnv("ONSLAUGHT_LIVE_WALKER_ADAPTER_PATH");
    string expectedAdapterSha256 = RequiredEnv("ONSLAUGHT_LIVE_WALKER_ADAPTER_SHA256");
    string pythonExe = RequiredEnv("ONSLAUGHT_LIVE_PYTHON_EXE");
    int attempt = BoundedIntEnv("ONSLAUGHT_LIVE_WALKER_ATTEMPT", 0, 1, 2);
    int lifecycleDeadlineSeconds = BoundedIntEnv("ONSLAUGHT_LIVE_WALKER_DEADLINE_SECONDS", 45, 45, 45);
    int attemptBudgetSeconds = BoundedIntEnv("ONSLAUGHT_LIVE_WALKER_ATTEMPT_BUDGET_SECONDS", 215, 215, 215);
    string cooperativeStopFile = RequiredEnv("ONSLAUGHT_LIVE_WALKER_COOPERATIVE_STOP_FILE");
    Stopwatch attemptDecisionClock = new Stopwatch();
    bool CooperativeStopRequested() => File.Exists(cooperativeStopFile);
    void MarkWalkerPhase(string phase) => WriteNewCanaryText(
        Path.Combine(artifactRoot, $"walker-phase-{phase}.marker"), artifactRoot,
        Stopwatch.GetTimestamp().ToString(System.Globalization.CultureInfo.InvariantCulture));
    void RequireDecisionBudget(string phase, int requiredSeconds)
    {
        if (CooperativeStopRequested())
            throw new TimeoutException($"Walker cooperative deadline expired before {phase}.");
        double remaining = attemptBudgetSeconds - attemptDecisionClock.Elapsed.TotalSeconds;
        if (remaining < requiredSeconds)
            throw new TimeoutException($"Walker refused {phase}; its declared budget plus cleanup reserve is unavailable.");
    }
    string[] launchArguments = JsonSerializer.Deserialize<string[]>(RequiredEnv("ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON")) ?? Array.Empty<string>();
    string[] expectedArguments = { "-skipfmv", "-level", "850", "-configuration", "2" };
    if (!launchArguments.SequenceEqual(expectedArguments, StringComparer.Ordinal))
        throw new InvalidOperationException("Walker trajectory launch arguments drifted from the locked protocol.");
    if (!string.Equals(Sha256File(adapterPath), expectedAdapterSha256, StringComparison.OrdinalIgnoreCase))
        throw new InvalidOperationException("Walker adapter path/hash binding failed.");

    string installedExe = Path.Combine(sourceRoot, "BEA.exe");
    string installedHashBefore = Sha256File(installedExe);
    string overrideHashBefore = Sha256File(exeOverride);
    SortedDictionary<string, string> sourceHashesBefore = SnapshotRelativeHashes(sourceRoot, "defaultoptions.bea", "savegames");
    if (SnapshotBeaProcesses().Length != 0)
        throw new InvalidOperationException("Refusing walker attempt while any BEA.exe process is already running.");

    string preparedTargetGameRoot = string.Empty;
    string preparedExecutablePath = string.Empty;
    string preparedManifestPath = string.Empty;
    WalkerOwnedPhaseProcess? profilePhase = null;
    WalkerOwnedPhaseProcess? launchPhase = null;
    GameProfileManagedProcess? managed = null;
    GameProfileStopResult? stopResult = null;
    Process? adapter = null;
    Task<string>? stdoutTask = null;
    Task<string>? stderrTask = null;
    string receiptSha256 = string.Empty;
    string copiedHashBefore = string.Empty;
    string hwndHex = "0x0";
    string failure = string.Empty;
    string adapterStartedAtUtc = string.Empty;
    string adapterExecutablePath = string.Empty;
    string adapterScriptHashAfter = string.Empty;
    string[] adapterCommand = Array.Empty<string>();
    int? adapterPid = null;
    int? adapterExitCode = null;
    bool adapterDeadlineExpired = false;
    bool adapterExited = false;
    bool adapterKilledAfterCleanup = false;
    bool receiptValidatedAfterAdapter = false;
    bool observerUpBeforeCleanup = false;
    bool phaseJobsClosed = false;
    JsonElement focusResult = JsonPayload(new { status = "not-run" });
    JsonElement qReleaseResult = JsonPayload(new { status = "not-run" });
    JsonElement censusResult = JsonPayload(new { status = "not-run", ownedProcessCount = -1, inspectionFailureCount = 0 });
    long profilePreparationStartedTimestamp = 0;
    long profilePreparationCompletedTimestamp = 0;
    long launchStartedTimestamp = 0;
    long receiptValidatedTimestamp = 0;
    long focusAcquiredTimestamp = 0;
    long adapterStartedTimestamp = 0;
    long cleanupStartedTimestamp = 0;
    long closeoutWrittenTimestamp = 0;
    string rawPath = Path.Combine(artifactRoot, "walker-trajectory-raw.json");
    string metricsPath = Path.Combine(artifactRoot, "walker-trajectory-metrics.json");
    string observerStatusPath = Path.Combine(artifactRoot, "observer-status.json");
    string adapterStdoutPath = Path.Combine(artifactRoot, "adapter-stdout.log");
    string adapterStderrPath = Path.Combine(artifactRoot, "adapter-stderr.log");
    string closeoutPath = Path.Combine(artifactRoot, "walker-trajectory-attempt-closeout.json");
    try
    {
        RequireDecisionBudget("profile preparation", 215);
        attemptDecisionClock.Start();
        profilePreparationStartedTimestamp = Stopwatch.GetTimestamp();
        MarkWalkerPhase("profile-started");
        string profilePhaseReceipt = Path.Combine(artifactRoot, "walker-profile-phase.json");
        profilePhase = WalkerOwnedPhaseProcess.Start("profile", profilePhaseReceipt, null);
        WaitWalkerOwnedPhase(profilePhase, TimeSpan.FromSeconds(120), cooperativeStopFile);
        using (JsonDocument phaseReceipt = JsonDocument.Parse(File.ReadAllText(profilePhaseReceipt)))
        {
            JsonElement row = phaseReceipt.RootElement;
            if (!JsonBool(row, "passed"))
                throw new InvalidOperationException("Walker profile preparation phase did not pass.");
            preparedTargetGameRoot = row.GetProperty("TargetGameRoot").GetString() ?? string.Empty;
            preparedExecutablePath = row.GetProperty("ExecutablePath").GetString() ?? string.Empty;
            preparedManifestPath = row.GetProperty("ManifestPath").GetString() ?? string.Empty;
        }
        profilePhase.RequireZeroAndClose();
        profilePhase = null;
        profilePreparationCompletedTimestamp = Stopwatch.GetTimestamp();
        MarkWalkerPhase("profile-completed");
        copiedHashBefore = Sha256File(preparedExecutablePath);
        if (!string.Equals(copiedHashBefore, overrideHashBefore, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Unpatched copied executable differs from the supplied source executable.");
        RequireDecisionBudget("launch/window/receipt/focus", 95);
        launchStartedTimestamp = Stopwatch.GetTimestamp();
        MarkWalkerPhase("launch-started");
        string launchPhaseReceipt = Path.Combine(artifactRoot, "walker-launch-phase.json");
        launchPhase = WalkerOwnedPhaseProcess.Start(
            "launch", launchPhaseReceipt,
            new Dictionary<string, string> {
                ["ONSLAUGHT_LIVE_WALKER_PREPARED_PROFILE_ROOT"] = preparedTargetGameRoot,
            });
        WaitWalkerOwnedPhase(launchPhase, TimeSpan.FromSeconds(30), cooperativeStopFile);
        using (JsonDocument phaseReceipt = JsonDocument.Parse(File.ReadAllText(launchPhaseReceipt)))
        {
            JsonElement row = phaseReceipt.RootElement;
            if (!JsonBool(row, "passed"))
                throw new InvalidOperationException("Walker launch phase did not pass.");
            managed = new GameProfileManagedProcess(
                ProcessId: row.GetProperty("ProcessId").GetInt32(),
                ExecutablePath: row.GetProperty("ExecutablePath").GetString() ?? string.Empty,
                WorkingDirectory: row.GetProperty("WorkingDirectory").GetString() ?? string.Empty,
                Arguments: row.GetProperty("Arguments").EnumerateArray()
                    .Select(value => value.GetString() ?? string.Empty).ToArray(),
                StartedAt: row.GetProperty("StartedAt").GetDateTimeOffset(),
                ManifestPath: row.GetProperty("ManifestPath").GetString() ?? string.Empty);
        }
        DateTime windowDeadline = DateTime.UtcNow.AddSeconds(12);
        while (DateTime.UtcNow < windowDeadline)
        {
            using Process running = Process.GetProcessById(managed.ProcessId);
            running.Refresh();
            if (running.HasExited)
                break;
            if (running.MainWindowHandle != IntPtr.Zero)
            {
                hwndHex = HwndHex(running.MainWindowHandle);
                break;
            }
            Thread.Sleep(100);
        }
        if (string.Equals(hwndHex, "0x0", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Managed copied BEA did not expose the exact top-level window.");
        RequireDecisionBudget("receipt validation", 65);
        receiptSha256 = WriteRuntimeProcessReceipt(
            runtimeReceiptPath, artifactRoot, managed, preparedManifestPath, hwndHex,
            launchArguments, overrideHashBefore, copiedHashBefore,
            expectedAdapterSha256, expectedAdapterSha256);
        if (!ValidateRuntimeReceipt(
                powershellExe, runtimeIdentityModule, runtimeReceiptPath, receiptSha256,
                expectedAdapterSha256, expectedAdapterSha256, true, out string receiptFailure))
            throw new InvalidOperationException("Walker receipt validation failed: " + receiptFailure);
        receiptValidatedTimestamp = Stopwatch.GetTimestamp();
        RequireDecisionBudget("foreground acquisition", 65);
        focusResult = SendInputSequence(
            powershellExe, inputScript, managed.ProcessId, hwndHex,
            managed.ExecutablePath, managed.WorkingDirectory, "wait:0", 0,
            false, string.Empty, Path.Combine(artifactRoot, "focus-window.json"),
            runtimeReceiptPath, receiptSha256, true);
        if (!JsonStringIn(focusResult, "status", "sent") || !JsonBool(focusResult, "focused"))
            throw new InvalidOperationException("Receipt-bound foreground acquisition failed.");
        focusAcquiredTimestamp = Stopwatch.GetTimestamp();
        MarkWalkerPhase("launch-completed");
        RequireDecisionBudget("launch/window/receipt/focus completion", 65);
        if (!ValidateRuntimeReceipt(
                powershellExe, runtimeIdentityModule, runtimeReceiptPath, receiptSha256,
                expectedAdapterSha256, expectedAdapterSha256, true, out receiptFailure))
            throw new InvalidOperationException("Walker receipt changed before adapter start: " + receiptFailure);
        RequireDecisionBudget("adapter observer", 65);

        var adapterStart = new ProcessStartInfo
        {
            FileName = pythonExe,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            WorkingDirectory = Path.GetDirectoryName(adapterPath)!,
        };
        adapterCommand = new[] {
            adapterPath, "observe-one", "--attempt", attempt.ToString(System.Globalization.CultureInfo.InvariantCulture),
            "--receipt", runtimeReceiptPath, "--expected-receipt-sha256", receiptSha256,
            "--raw-output", rawPath, "--metrics-output", metricsPath,
            "--status-output", observerStatusPath,
            "--authorized-private-root", artifactRoot,
        };
        foreach (string argument in adapterCommand)
            adapterStart.ArgumentList.Add(argument);
        Stopwatch observerLifecycle = Stopwatch.StartNew();
        adapter = Process.Start(adapterStart) ?? throw new InvalidOperationException("Could not start the walker adapter.");
        adapterStartedTimestamp = Stopwatch.GetTimestamp();
        adapterPid = adapter.Id;
        adapterStartedAtUtc = adapter.StartTime.ToUniversalTime().ToString("o");
        adapterExecutablePath = Path.GetFullPath(
            adapter.MainModule?.FileName ?? throw new InvalidOperationException("Could not resolve the live walker adapter host image."));
        if (!string.Equals(adapterExecutablePath, Path.GetFullPath(pythonExe), StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Live walker adapter host image changed from the bound Python executable.");
        stdoutTask = adapter.StandardOutput.ReadToEndAsync();
        stderrTask = adapter.StandardError.ReadToEndAsync();
        int remainingMilliseconds = Math.Max(
            1, (int)(TimeSpan.FromSeconds(lifecycleDeadlineSeconds) - observerLifecycle.Elapsed).TotalMilliseconds);
        Stopwatch adapterWait = Stopwatch.StartNew();
        while (!adapter.HasExited && adapterWait.ElapsedMilliseconds < remainingMilliseconds)
        {
            if (CooperativeStopRequested())
            {
                adapterDeadlineExpired = true;
                failure = "Walker cooperative aggregate deadline expired during observer; entering cleanup.";
                break;
            }
            adapter.WaitForExit(Math.Min(100, Math.Max(1, remainingMilliseconds - (int)adapterWait.ElapsedMilliseconds)));
        }
        adapterExited = adapter.HasExited;
        if (adapterExited)
        {
            adapterExitCode = adapter.ExitCode;
            if (adapterExitCode != 0)
                failure = $"Walker adapter exited with code {adapterExitCode}.";
        }
        else
        {
            if (!adapterDeadlineExpired)
            {
                adapterDeadlineExpired = true;
                failure = "Walker adapter exceeded the AppCore-owned lifecycle deadline.";
            }
        }
    }
    catch (Exception ex)
    {
        failure = string.IsNullOrWhiteSpace(failure)
            ? ex.GetType().Name + ": " + ex.Message
            : failure + " | " + ex.GetType().Name + ": " + ex.Message;
    }
    finally
    {
        cleanupStartedTimestamp = Stopwatch.GetTimestamp();
        Stopwatch cleanupLifecycle = Stopwatch.StartNew();
        // WALKER_CLEANUP_PHASE: release_q
        try
        {
            if (adapter is not null && adapter.HasExited && File.Exists(observerStatusPath))
            {
                using JsonDocument preCleanupStatus = JsonDocument.Parse(File.ReadAllText(observerStatusPath));
                observerUpBeforeCleanup = JsonBool(preCleanupStatus.RootElement, "qUpConfirmed") &&
                    JsonBool(preCleanupStatus.RootElement, "observerHandleClosed");
            }
            if (observerUpBeforeCleanup)
            {
                qReleaseResult = JsonPayload(new {
                    status = "observer-confirmed-up",
                    focused = true,
                    sendInputEventsSent = 0,
                });
            }
            else if (managed is not null && !string.Equals(hwndHex, "0x0", StringComparison.OrdinalIgnoreCase) &&
                !string.IsNullOrWhiteSpace(receiptSha256))
            {
                qReleaseResult = SendInputSequence(
                    powershellExe, inputScript, managed.ProcessId, hwndHex,
                    managed.ExecutablePath, managed.WorkingDirectory, "up:Q", 0,
                    false, string.Empty, Path.Combine(artifactRoot, "cleanup-q-up.json"),
                    runtimeReceiptPath, receiptSha256, true);
            }
        }
        catch (Exception ex) { failure = AppendCleanupFailure(failure, "release_q", ex); }

        // WALKER_CLEANUP_PHASE: close_adapter
        try
        {
            if (adapter is not null && !adapter.HasExited)
            {
                if (!adapter.WaitForExit(2000))
                {
                    adapter.Kill(entireProcessTree: false);
                    adapter.WaitForExit();
                    adapterKilledAfterCleanup = true;
                }
            }
            if (adapter is not null && adapter.HasExited)
            {
                adapterExited = true;
                adapterExitCode ??= adapter.ExitCode;
            }
            string stdout = stdoutTask is null ? string.Empty : stdoutTask.GetAwaiter().GetResult();
            string stderr = stderrTask is null ? string.Empty : stderrTask.GetAwaiter().GetResult();
            WriteNewCanaryText(adapterStdoutPath, artifactRoot, stdout);
            WriteNewCanaryText(adapterStderrPath, artifactRoot, stderr);
            if (managed is not null && !string.IsNullOrWhiteSpace(receiptSha256))
            {
                receiptValidatedAfterAdapter = ValidateRuntimeReceipt(
                    powershellExe, runtimeIdentityModule, runtimeReceiptPath, receiptSha256,
                    expectedAdapterSha256, expectedAdapterSha256, true, out string postAdapterFailure);
                if (!receiptValidatedAfterAdapter)
                    throw new InvalidOperationException("Walker receipt changed after adapter: " + postAdapterFailure);
            }
        }
        catch (Exception ex) { failure = AppendCleanupFailure(failure, "close_adapter", ex); }

        // WALKER_CLEANUP_PHASE: stop_managed
        try
        {
            if (managed is not null)
            {
                if (!string.IsNullOrWhiteSpace(receiptSha256) && !ValidateRuntimeReceipt(
                        powershellExe, runtimeIdentityModule, runtimeReceiptPath, receiptSha256,
                        expectedAdapterSha256, expectedAdapterSha256, true, out string stopBindingFailure))
                    throw new InvalidOperationException("Walker stop receipt validation failed: " + stopBindingFailure);
                stopResult = GameProfileRuntimeService.StopCopiedProfile(
                    managed, profilesRoot, gracefulTimeout: TimeSpan.FromSeconds(3));
            }
        }
        catch (Exception ex) { failure = AppendCleanupFailure(failure, "stop_managed", ex); }

        // WALKER_CLEANUP_PHASE: close_phase_jobs
        try
        {
            if (profilePhase is not null)
                profilePhase.TerminateExactJobAndClose();
            if (launchPhase is not null)
            {
                if (launchPhase.ActiveProcesses == 0)
                    launchPhase.RequireZeroAndClose();
                else
                    launchPhase.TerminateExactJobAndClose();
            }
            phaseJobsClosed = true;
        }
        catch (Exception ex) { failure = AppendCleanupFailure(failure, "close_phase_jobs", ex); }

        // WALKER_CLEANUP_PHASE: census
        try
        {
            censusResult = InspectOwnedProcessCensus(runtimeReceiptPath, managed?.ExecutablePath, null);
            if (!JsonStringIn(censusResult, "status", "clear") || JsonInt(censusResult, "ownedProcessCount") != 0)
                throw new InvalidOperationException("Walker owned-process census was not clear.");
        }
        catch (Exception ex) { failure = AppendCleanupFailure(failure, "census", ex); }
        if (cleanupLifecycle.Elapsed > TimeSpan.FromSeconds(20))
            failure = string.IsNullOrWhiteSpace(failure)
                ? "Walker cleanup exceeded its preserved 20-second safety reserve."
                : failure + " | Walker cleanup exceeded its preserved 20-second safety reserve.";
        if (CooperativeStopRequested())
            failure = string.IsNullOrWhiteSpace(failure)
                ? "Walker cooperative aggregate deadline expired; cleanup closeout completed."
                : failure + " | Walker cooperative aggregate deadline expired; cleanup closeout completed.";
    }

    string installedHashAfter = Sha256File(installedExe);
    string overrideHashAfter = Sha256File(exeOverride);
    SortedDictionary<string, string> sourceHashesAfter = SnapshotRelativeHashes(sourceRoot, "defaultoptions.bea", "savegames");
    string copiedHashAfter = string.IsNullOrWhiteSpace(preparedExecutablePath)
        ? string.Empty : Sha256File(preparedExecutablePath);
    adapterScriptHashAfter = Sha256File(adapterPath);
    bool adapterScriptUnchanged = string.Equals(
        adapterScriptHashAfter, expectedAdapterSha256, StringComparison.OrdinalIgnoreCase);
    bool sourceUnchanged = string.Equals(installedHashBefore, installedHashAfter, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(overrideHashBefore, overrideHashAfter, StringComparison.OrdinalIgnoreCase) &&
        HashMapsEqual(sourceHashesBefore, sourceHashesAfter);
    bool copyUnchanged = !string.IsNullOrWhiteSpace(copiedHashBefore) &&
        string.Equals(copiedHashBefore, copiedHashAfter, StringComparison.OrdinalIgnoreCase);
    bool observerQUp = false;
    bool observerHandleClosed = false;
    bool observerSucceeded = false;
    bool samplerAccepted = false;
    if (File.Exists(observerStatusPath))
    {
        using JsonDocument status = JsonDocument.Parse(File.ReadAllText(observerStatusPath));
        observerQUp = JsonBool(status.RootElement, "qUpConfirmed");
        observerHandleClosed = JsonBool(status.RootElement, "observerHandleClosed");
        samplerAccepted = JsonBool(status.RootElement, "samplerAccepted");
        observerSucceeded = JsonStringIn(status.RootElement, "failure", string.Empty);
    }
    bool backupQUp = JsonStringIn(qReleaseResult, "status", "sent") &&
        JsonIntEquals(qReleaseResult, "sendInputEventsSent", 1);
    bool managedStopped = stopResult?.Success == true && stopResult.ProcessId == managed?.ProcessId &&
        stopResult.LiveBeforeStop && stopResult.StopRequested && stopResult.ExitObserved &&
        !stopResult.AlreadyGone && stopResult.ExitTime.HasValue;
    int ownedProcessCount = JsonInt(censusResult, "ownedProcessCount");
    bool accepted = string.IsNullOrWhiteSpace(failure) && !adapterDeadlineExpired &&
        !adapterKilledAfterCleanup && adapterExitCode == 0 && observerSucceeded && observerQUp &&
        observerHandleClosed && samplerAccepted && managedStopped && ownedProcessCount == 0 &&
        phaseJobsClosed && receiptValidatedAfterAdapter && sourceUnchanged && copyUnchanged &&
        adapterScriptUnchanged && File.Exists(rawPath) && File.Exists(metricsPath);
    closeoutWrittenTimestamp = Stopwatch.GetTimestamp();
    var closeout = new
    {
        schemaVersion = "battleengine-walker-trajectory-private-attempt-closeout.v1",
        attempt,
        accepted,
        receiptPath = runtimeReceiptPath,
        receiptSha256,
        sourceUnchanged,
        copyUnchanged,
        qUpConfirmed = observerQUp || backupQUp,
        observerHandleClosed,
        managedProcessStopped = managedStopped,
        ownedProcessCount,
        publicProjectionWritten = false,
        phaseTimestamps = new {
            profilePreparationStartedTimestamp, profilePreparationCompletedTimestamp,
            launchStartedTimestamp, receiptValidatedTimestamp, focusAcquiredTimestamp,
            adapterStartedTimestamp, cleanupStartedTimestamp, closeoutWrittenTimestamp,
        },
        failure,
        adapter = new
        {
            path = adapterPath,
            sha256 = expectedAdapterSha256,
            pid = adapterPid,
            startedAtUtc = adapterStartedAtUtc,
            executablePath = adapterExecutablePath,
            command = adapterCommand,
            stdoutPath = adapterStdoutPath,
            stderrPath = adapterStderrPath,
            exitCode = adapterExitCode,
            exited = adapterExited,
            deadlineExpired = adapterDeadlineExpired,
            killedAfterQRelease = adapterKilledAfterCleanup,
            scriptHashAfter = adapterScriptHashAfter,
            scriptUnchanged = adapterScriptUnchanged,
        },
        cleanup = new {
            observerQUp, backupQUp, observerHandleClosed, managedStopped, phaseJobsClosed,
            census = censusResult,
        },
        interferenceNonclaim = "Foreground and receipt identity drift are detected; arbitrary human or controller input is not detected.",
    };
    WriteNewCanaryText(
        closeoutPath, artifactRoot,
        JsonSerializer.Serialize(closeout, new JsonSerializerOptions { WriteIndented = true }));
    Console.WriteLine(closeoutPath);
    return accepted ? 0 : 2;
}

static int RunMorphCanary()
{
    string sourceRoot = RequiredEnv("ONSLAUGHT_LIVE_SOURCE_ROOT");
    string profilesRoot = RequiredEnv("ONSLAUGHT_LIVE_PROFILES_ROOT");
    string artifactJson = RequiredEnv("ONSLAUGHT_LIVE_ARTIFACT_JSON");
    string exeOverride = RequiredEnv("ONSLAUGHT_LIVE_EXE_OVERRIDE");
    string inputScript = RequiredEnv("ONSLAUGHT_LIVE_INPUT_SCRIPT");
    string powershellExe = RequiredEnv("ONSLAUGHT_LIVE_POWERSHELL");
    string cdbStartScript = RequiredEnv("ONSLAUGHT_LIVE_CDB_START_SCRIPT");
    string cdbCommandFile = RequiredEnv("ONSLAUGHT_LIVE_CDB_COMMAND_FILE");
    string cdbLogPath = RequiredEnv("ONSLAUGHT_LIVE_CDB_LOG_PATH");
    string runtimeReceiptPath = RequiredEnv("ONSLAUGHT_LIVE_RUNTIME_RECEIPT_PATH");
    string runtimeIdentityModule = RequiredEnv("ONSLAUGHT_LIVE_RUNTIME_IDENTITY_MODULE");
    string expectedCommandSha256 = RequiredEnv("ONSLAUGHT_LIVE_CDB_COMMAND_SHA256");
    string expectedTemplateSha256 = RequiredEnv("ONSLAUGHT_LIVE_CDB_TEMPLATE_SHA256");
    string canonicalExecutableSha256 = RequiredEnv("ONSLAUGHT_LIVE_CANONICAL_EXECUTABLE_SHA256");
    string templatePath = RequiredEnv("ONSLAUGHT_LIVE_CDB_TEMPLATE_PATH");
    string requiredLogMarker = RequiredEnv("ONSLAUGHT_LIVE_CDB_REQUIRED_MARKER");
    string role = RequiredEnv("ONSLAUGHT_LIVE_CANARY_ROLE");
    string artifactRoot = Path.GetDirectoryName(artifactJson)!;
    if (canonicalExecutableSha256.Length != 64 || !canonicalExecutableSha256.All(Uri.IsHexDigit))
        throw new InvalidOperationException("Canonical executable digest is not a SHA-256 digest.");
    if (!string.Equals(RequiredEnv("ONSLAUGHT_LIVE_INPUT_STEP_DELAY_MS"), "60", StringComparison.Ordinal) ||
        !string.Equals(RequiredEnv("ONSLAUGHT_LIVE_CDB_LOG_READY_TIMEOUT_MS"), "10000", StringComparison.Ordinal))
        throw new InvalidOperationException("Morph canary timing inputs drifted from the locked protocol.");
    const int inputStepDelayMs = 60;
    const int cdbLogReadyTimeoutMs = 10000;
    string[] launchArguments = JsonSerializer.Deserialize<string[]>(RequiredEnv("ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON")) ?? Array.Empty<string>();
    string[] inputSequences = JsonSerializer.Deserialize<string[]>(RequiredEnv("ONSLAUGHT_LIVE_INPUT_SEQUENCES_JSON")) ?? Array.Empty<string>();
    JsonElement[] fingerprints = JsonSerializer.Deserialize<JsonElement[]>(RequiredEnv("ONSLAUGHT_LIVE_CDB_FINGERPRINTS_JSON")) ?? Array.Empty<JsonElement>();
    string[] expectedLaunchArguments = { "-skipfmv", "-level", "850", "-configuration", "2" };
    string[] expectedInputSequences = role switch
    {
        "noInputControl" => Array.Empty<string>(),
        "positiveTransform" => new[] { "tap:Q" },
        "positiveRepeat" => new[] { "tap:Q" },
        _ => throw new InvalidOperationException("Unsupported morph canary role."),
    };
    string roleProfileName = role switch
    {
        "noInputControl" => "mc-c",
        "positiveTransform" => "mc-p",
        "positiveRepeat" => "mc-r",
        _ => throw new InvalidOperationException("Unsupported morph canary role."),
    };
    if (!launchArguments.SequenceEqual(expectedLaunchArguments, StringComparer.Ordinal) ||
        !inputSequences.SequenceEqual(expectedInputSequences, StringComparer.Ordinal) ||
        !string.Equals(requiredLogMarker, "MORPH_CANARY_READY", StringComparison.Ordinal))
        throw new InvalidOperationException("Morph canary protocol inputs drifted from the locked plan.");

    string installedExe = Path.Combine(sourceRoot, "BEA.exe");
    string installedHashBefore = Sha256File(installedExe);
    string overrideHashBefore = Sha256File(exeOverride);
    if (!string.Equals(overrideHashBefore, canonicalExecutableSha256, StringComparison.OrdinalIgnoreCase))
        throw new InvalidOperationException("Effective executable override does not match the canonical renderer digest.");
    SortedDictionary<string, string> sourceHashesBefore = SnapshotRelativeHashes(sourceRoot, "defaultoptions.bea", "savegames");
    if (SnapshotBeaProcesses().Length != 0)
        throw new InvalidOperationException("Refusing morph canary while any BEA.exe process is already running.");

    GameProfilePrepareResult? prepared = null;
    GameProfileManagedProcess? managed = null;
    GameProfileStopResult? stopResult = null;
    JsonElement? cdbAttachResult = null;
    Process? boundCdbProcess = null;
    FileStream? boundCdbLogStream = null;
    long cdbLogLengthAtReadiness = -1;
    JsonElement cdbPreStopResult = JsonPayload(new { status = "not-started", receiptBound = false, processBound = false });
    JsonElement cdbCleanupResult = JsonPayload(new { status = "not-started", receiptBound = false, exited = true });
    JsonElement censusResult = JsonPayload(new { status = "not-run", ownedProcessCount = -1, inspectionFailureCount = 0 });
    List<JsonElement> inputResults = new();
    string receiptSha256 = string.Empty;
    string copiedExecutableHashBefore = string.Empty;
    string observedMainWindowHandle = "0x0";
    string failure = string.Empty;
    bool stopReceiptBound = false;
    bool inputDeliveryAttempted = false;
    int ownedProcessCount = -1;
    long runnerStopCallBeginTimestamp = 0;
    long runnerStopCallReturnedTimestamp = 0;
    long runnerCdbFinalizationValidationBeginTimestamp = 0;
    long runnerCompletionDecisionTimestamp = 0;
    try
    {
        bool morphCanaryMode = true;
        prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
            new GameProfilePrepareOptions(
                SourceGameRoot: sourceRoot,
                OutputRoot: profilesRoot,
                ProfileName: roleProfileName,
                ExecutableOverridePath: exeOverride,
                ApplyWindowedCompatibilityPatch: !morphCanaryMode,
                AllowByteLayoutOnlyTarget: false,
                IncludeSavegames: false,
                PatchKeys: Array.Empty<string>(),
                LaunchArguments: launchArguments,
                ProfilePresetId: null));
        copiedExecutableHashBefore = Sha256File(prepared.ExecutablePath);
        if (!string.Equals(copiedExecutableHashBefore, canonicalExecutableSha256, StringComparison.OrdinalIgnoreCase) ||
            !string.Equals(copiedExecutableHashBefore, overrideHashBefore, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Copied executable does not match the canonical renderer digest.");
        _ = GameProfileControlOptionsService.ApplyToSafeCopy(
            new GameProfileControlOptionsRequest(
                ProfileRoot: prepared.TargetGameRoot,
                AppOwnedProfilesRoot: profilesRoot,
                MouseSensitivityOverride: null,
                ControllerConfigP1Override: null,
                ControllerConfigP2Override: null,
                KeybindRows: new[]
                {
                    new ConfigurationKeybindRow
                    {
                        GroupLabel = "Actions",
                        ActionLabel = "Transform",
                        EntryId = 0x21,
                        KeyboardDeviceCode = 8u,
                        CurrentPlayer1Token = "",
                        CurrentPlayer2Token = "",
                        Player1Token = "Q",
                        Player2Token = ""
                    }
                }));
        managed = GameProfileRuntimeService.LaunchCopiedProfile(
            new GameProfileLaunchOptions(
                ProfileRoot: prepared.TargetGameRoot,
                AppOwnedProfilesRoot: profilesRoot,
                LaunchArguments: launchArguments));
        DateTime deadline = DateTime.UtcNow.AddSeconds(BoundedIntEnv("ONSLAUGHT_LIVE_TIMEOUT_SECONDS", 12, 1, 120));
        while (DateTime.UtcNow < deadline)
        {
            using Process running = Process.GetProcessById(managed.ProcessId);
            running.Refresh();
            if (running.HasExited)
                break;
            if (running.MainWindowHandle != IntPtr.Zero)
            {
                observedMainWindowHandle = HwndHex(running.MainWindowHandle);
                break;
            }
            Thread.Sleep(250);
        }
        if (string.Equals(observedMainWindowHandle, "0x0", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Managed copied BEA did not expose an exact top-level window.");
        receiptSha256 = WriteRuntimeProcessReceipt(
            runtimeReceiptPath,
            artifactRoot,
            managed,
            prepared.ManifestPath,
            observedMainWindowHandle,
            launchArguments,
            overrideHashBefore,
            copiedExecutableHashBefore,
            expectedTemplateSha256,
            expectedCommandSha256);
        Environment.SetEnvironmentVariable("ONSLAUGHT_LIVE_RUNTIME_RECEIPT_SHA256", receiptSha256);
        string cdbObserverArtifact = Path.Combine(artifactRoot, "cdb", "cdb-observer.json");
        if (!ValidateCanaryBinding(
                powershellExe,
                runtimeIdentityModule,
                runtimeReceiptPath,
                receiptSha256,
                cdbCommandFile,
                expectedCommandSha256,
                templatePath,
                expectedTemplateSha256,
                true,
                out string attachBindingFailure))
            throw new InvalidOperationException("Runtime binding changed before CDB attach: " + attachBindingFailure);
        AssertFreshCanaryWriteTarget(cdbLogPath, artifactRoot);
        AssertFreshCanaryWriteTarget(cdbObserverArtifact, artifactRoot);
        cdbAttachResult = StartCdbObserver(
            powershellExe,
            cdbStartScript,
            managed.ProcessId,
            managed.ExecutablePath,
            managed.WorkingDirectory,
            profilesRoot,
            cdbCommandFile,
            cdbLogPath,
            cdbLogReadyTimeoutMs,
            cdbObserverArtifact,
            runtimeReceiptPath,
            receiptSha256,
            expectedCommandSha256,
            requiredLogMarker,
            true);
        if (!CdbObserverReady(
                cdbAttachResult,
                receiptSha256,
                expectedCommandSha256,
                cdbLogPath,
                requiredLogMarker))
            throw new InvalidOperationException(
                "CDB observer did not reach receipt-bound marker readiness; refusing input.");
        boundCdbLogStream = OpenRetainedCdbLogStream(cdbLogPath);
        cdbLogLengthAtReadiness = boundCdbLogStream.Length;
        if (!HasExactlyOneLogMarker(boundCdbLogStream, requiredLogMarker))
            throw new InvalidOperationException(
                "Retained CDB log identity did not contain the exact readiness marker.");
        for (int i = 0; i < inputSequences.Length; i++)
        {
            if (!ValidateCanaryBinding(
                powershellExe,
                runtimeIdentityModule,
                runtimeReceiptPath,
                receiptSha256,
                cdbCommandFile,
                expectedCommandSha256,
                templatePath,
                expectedTemplateSha256,
                true,
                out string inputReceiptFailure))
                throw new InvalidOperationException("Runtime receipt changed before input: " + inputReceiptFailure);
            inputDeliveryAttempted = true;
            string inputArtifact = Path.Combine(artifactRoot, "input", $"canary-input-{i + 1:D2}.json");
            AssertFreshCanaryWriteTarget(inputArtifact, artifactRoot);
            inputResults.Add(SendInputSequence(
                powershellExe,
                inputScript,
                managed.ProcessId,
                observedMainWindowHandle,
                managed.ExecutablePath,
                managed.WorkingDirectory,
                inputSequences[i],
                inputStepDelayMs,
                false,
                string.Empty,
                inputArtifact,
                runtimeReceiptPath,
                receiptSha256,
                true));
        }
    }
    catch (Exception ex)
    {
        failure = ex.GetType().Name + ": " + ex.Message;
    }
    finally
    {
        if (managed is not null && prepared is not null && string.IsNullOrWhiteSpace(receiptSha256))
        {
            try
            {
                copiedExecutableHashBefore = string.IsNullOrWhiteSpace(copiedExecutableHashBefore)
                    ? Sha256File(prepared.ExecutablePath)
                    : copiedExecutableHashBefore;
                receiptSha256 = WriteRuntimeProcessReceipt(
                    runtimeReceiptPath,
                    artifactRoot,
                    managed,
                    prepared.ManifestPath,
                    "0x0",
                    launchArguments,
                    overrideHashBefore,
                    copiedExecutableHashBefore,
                    expectedTemplateSha256,
                    expectedCommandSha256);
                Environment.SetEnvironmentVariable("ONSLAUGHT_LIVE_RUNTIME_RECEIPT_SHA256", receiptSha256);
            }
            catch (Exception ex)
            {
                receiptSha256 = string.Empty;
                failure = AppendCleanupFailure(failure, "receipt-materialization", ex);
            }
        }
__CANARY_CLEANUP_PHASE_BLOCK__
    }

    if (!string.IsNullOrWhiteSpace(failure))
    {
        try
        {
            string failureArtifact = Path.Combine(artifactRoot, "canary-failure.json");
            WriteNewCanaryText(
                failureArtifact,
                artifactRoot,
                JsonSerializer.Serialize(new
                {
                    schemaVersion = "winui-original-binary-battleengine-morph-identity-canary-private-failure.v1",
                    role,
                    failure,
                    cdbPreStop = cdbPreStopResult,
                    managedStop = stopResult,
                    cdbCleanup = cdbCleanupResult,
                    processCensus = censusResult,
                }, new JsonSerializerOptions { WriteIndented = true }));
        }
        catch (Exception diagnosticError)
        {
            try
            {
                Console.Error.WriteLine("MORPH_CANARY_ORIGINAL_FAILURE: " + failure);
                Console.Error.WriteLine(
                    "MORPH_CANARY_DIAGNOSTIC_WRITE_FAILURE: " +
                    diagnosticError.GetType().Name + ": " + diagnosticError.Message);
            }
            catch
            {
            }
        }
    }

    if (prepared is null || string.IsNullOrWhiteSpace(receiptSha256))
        throw new InvalidOperationException("Morph canary did not reach receipt materialization. " + failure);
    string installedHashAfter = Sha256File(installedExe);
    string overrideHashAfter = Sha256File(exeOverride);
    SortedDictionary<string, string> sourceHashesAfter = SnapshotRelativeHashes(sourceRoot, "defaultoptions.bea", "savegames");
    string copiedExecutableHashAfter = Sha256File(prepared.ExecutablePath);
    bool canarySourceUnchanged = string.Equals(installedHashAfter, installedHashBefore, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(overrideHashBefore, canonicalExecutableSha256, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(overrideHashAfter, canonicalExecutableSha256, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(overrideHashAfter, overrideHashBefore, StringComparison.OrdinalIgnoreCase) &&
        HashMapsEqual(sourceHashesBefore, sourceHashesAfter);
    bool canaryCopyUnchanged = string.Equals(copiedExecutableHashBefore, canonicalExecutableSha256, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(copiedExecutableHashAfter, canonicalExecutableSha256, StringComparison.OrdinalIgnoreCase) &&
        string.Equals(copiedExecutableHashBefore, copiedExecutableHashAfter, StringComparison.OrdinalIgnoreCase);
    bool canaryCdbReady = JsonStringIn(cdbPreStopResult, "status", "ready-for-managed-stop") &&
        JsonBool(cdbPreStopResult, "receiptBound") &&
        JsonBool(cdbPreStopResult, "processBound");
    bool canaryFocusedInputSucceeded = role == "noInputControl"
        ? inputResults.Count == 0
        : inputResults.Count == expectedInputSequences.Length && inputResults.All(result =>
            JsonStringIn(result, "status", "sent") && JsonBool(result, "focused") &&
            JsonIntEquals(result, "sendInputEventsSent", 2) &&
            JsonIntEquals(result, "scanKeybdEventsSent", 0) &&
            JsonIntEquals(result, "windowMessageEventsSent", 0) &&
            result.TryGetProperty("nativeInputLayout", out JsonElement layout) &&
            JsonBool(layout, "valid") &&
            result.TryGetProperty("sendInputFailures", out JsonElement failures) &&
            failures.ValueKind == JsonValueKind.Array && failures.GetArrayLength() == 0 &&
            result.TryGetProperty("unconfirmedReleaseKeys", out JsonElement keys) &&
            keys.ValueKind == JsonValueKind.Array && keys.GetArrayLength() == 0);
    bool keysReleased = role == "noInputControl"
        ? inputResults.Count == 0
        : inputResults.Count == expectedInputSequences.Length && inputResults.All(result =>
            result.TryGetProperty("unconfirmedReleaseKeys", out JsonElement keys) &&
            keys.ValueKind == JsonValueKind.Array && keys.GetArrayLength() == 0);
    bool cdbDetached = JsonStringIn(cdbCleanupResult, "status", "exited-after-managed-stop") &&
        JsonBool(cdbCleanupResult, "receiptBound") &&
        JsonBool(cdbCleanupResult, "gracefulQuitObserved") &&
        JsonBool(cdbCleanupResult, "targetExitEventObserved") &&
        JsonBool(cdbCleanupResult, "cdbExitCodeAccepted");
    bool managedProcessStopped = stopReceiptBound && stopResult?.Success == true &&
        stopResult.LiveBeforeStop && stopResult.StopRequested && stopResult.ExitObserved &&
        !stopResult.AlreadyGone && stopResult.ExitTime.HasValue;
    bool censusClear = JsonStringIn(censusResult, "status", "clear") &&
        JsonIntEquals(censusResult, "inspectionFailureCount", 0);
__CANARY_CLEANUP_OBJECT__
    var privateArtifact = new
    {
        schema = "winui-original-binary-battleengine-morph-identity-canary-private-run.v1",
        executablePath = prepared.ExecutablePath,
        templatePath,
        commandPath = cdbCommandFile,
        receiptSha256,
        commandSha256 = expectedCommandSha256,
        templateSha256 = expectedTemplateSha256,
        executableSha256 = canonicalExecutableSha256,
        fingerprints,
        sourceUnchanged = canarySourceUnchanged,
        copyUnchanged = canaryCopyUnchanged,
        cleanup = canaryCleanup,
    };
    WriteNewCanaryText(
        artifactJson,
        artifactRoot,
        JsonSerializer.Serialize(privateArtifact, new JsonSerializerOptions { WriteIndented = true }));
    runnerCompletionDecisionTimestamp = Stopwatch.GetTimestamp();
    bool runnerLifecycleOrderValid = runnerStopCallBeginTimestamp > 0 &&
        runnerStopCallBeginTimestamp < runnerStopCallReturnedTimestamp &&
        runnerStopCallReturnedTimestamp < runnerCdbFinalizationValidationBeginTimestamp &&
        runnerCdbFinalizationValidationBeginTimestamp < runnerCompletionDecisionTimestamp;
    var lifecycleDiagnostics = new
    {
        schemaVersion = "winui-original-binary-battleengine-morph-identity-canary-private-cleanup-lifecycle.v1",
        runnerStopCallBeginTimestamp,
        runnerStopCallReturnedTimestamp,
        runnerCdbFinalizationValidationBeginTimestamp,
        runnerCompletionDecisionTimestamp,
        runnerLifecycleOrderValid,
        managedForceRequested = stopResult?.ForceRequested,
        exactForceRequestTimestampAvailable = false,
        limitation = "These monotonic values prove runner call and validation order only, not target-versus-CDB kernel exit order. AppCore does not expose the exact force-request timestamp; the returned ForceRequested fact is retained with before/after runner stop-call milestones.",
        managedStop = stopResult,
        cdbCleanup = cdbCleanupResult,
    };
    WriteNewCanaryText(
        Path.Combine(artifactRoot, "canary-cleanup-lifecycle.json"),
        artifactRoot,
        JsonSerializer.Serialize(lifecycleDiagnostics, new JsonSerializerOptions { WriteIndented = true }));
    bool succeeded = string.IsNullOrWhiteSpace(failure) && canaryCdbReady && canaryFocusedInputSucceeded &&
        canarySourceUnchanged && canaryCopyUnchanged && keysReleased && cdbDetached &&
        managedProcessStopped && runnerLifecycleOrderValid && censusClear && ownedProcessCount == 0;
    Console.WriteLine(artifactJson);
    return succeeded ? 0 : 2;
}

string walkerChildPhase = Environment.GetEnvironmentVariable(
    "ONSLAUGHT_LIVE_WALKER_CHILD_PHASE") ?? string.Empty;
if (string.Equals(walkerChildPhase, "profile", StringComparison.Ordinal))
    return RunWalkerProfilePreparationPhase();
if (string.Equals(walkerChildPhase, "launch", StringComparison.Ordinal))
    return RunWalkerLaunchPhase();

bool walkerTrajectoryMode = string.Equals(
    Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_RUNTIME_PROTOCOL"),
    "battleengine-walker-trajectory-v1",
    StringComparison.Ordinal);
if (walkerTrajectoryMode)
    return RunWalkerTrajectoryAttempt();

bool morphCanaryMode = string.Equals(
    Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_RUNTIME_PROTOCOL"),
    "battleengine-morph-identity-canary-v1",
    StringComparison.Ordinal);
if (morphCanaryMode)
    return RunMorphCanary();

string sourceRoot = RequiredEnv("ONSLAUGHT_LIVE_SOURCE_ROOT");
string profilesRoot = RequiredEnv("ONSLAUGHT_LIVE_PROFILES_ROOT");
string artifactJson = RequiredEnv("ONSLAUGHT_LIVE_ARTIFACT_JSON");
string exeOverride = RequiredEnv("ONSLAUGHT_LIVE_EXE_OVERRIDE");
string captureScript = RequiredEnv("ONSLAUGHT_LIVE_CAPTURE_SCRIPT");
string inputScript = RequiredEnv("ONSLAUGHT_LIVE_INPUT_SCRIPT");
string captureDir = RequiredEnv("ONSLAUGHT_LIVE_CAPTURE_DIR");
string capturePng = RequiredEnv("ONSLAUGHT_LIVE_CAPTURE_PNG");
string captureJson = RequiredEnv("ONSLAUGHT_LIVE_CAPTURE_JSON");
string powershellExe = RequiredEnv("ONSLAUGHT_LIVE_POWERSHELL");
string[] patchKeys = JsonSerializer.Deserialize<string[]>(RequiredEnv("ONSLAUGHT_LIVE_PATCH_KEYS_JSON")) ??
    throw new InvalidOperationException("ONSLAUGHT_LIVE_PATCH_KEYS_JSON did not contain a patch key array.");
string[] inputSequences = JsonSerializer.Deserialize<string[]>(
        Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_INPUT_SEQUENCES_JSON") ?? "[]") ??
    Array.Empty<string>();
string[] launchArguments = JsonSerializer.Deserialize<string[]>(
        Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON") ?? @"[""-skipfmv""]") ??
    new[] { "-skipfmv" };
string profilePresetId = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_PROFILE_PRESET_ID") ?? string.Empty;
bool stageMusicReplacement = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_STAGE_MUSIC_REPLACEMENT"), "1", StringComparison.Ordinal);
bool allowBackgroundWindowMessages = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_ALLOW_BACKGROUND_WINDOW_MESSAGES"), "1", StringComparison.Ordinal);
bool focusBeforePreInputCapture = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_FOCUS_BEFORE_PRE_INPUT_CAPTURE"), "1", StringComparison.Ordinal);
bool captureAfterEachInputSequence = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_CAPTURE_AFTER_EACH_INPUT_SEQUENCE"), "1", StringComparison.Ordinal);
string backgroundWindowMessagesArm = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_BACKGROUND_WINDOW_MESSAGES_ARM") ?? string.Empty;
string musicSwapPresetId = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_MUSIC_SWAP_PRESET_ID") ?? string.Empty;
bool sharpenMouseLook = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_SHARPEN_MOUSE_LOOK"), "1", StringComparison.Ordinal);
bool bindForwardQeForInputIsolation = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_BIND_FORWARD_QE_FOR_INPUT_ISOLATION"), "1", StringComparison.Ordinal);
bool bindFireQeForWeaponHandoff = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_BIND_FIRE_QE_FOR_WEAPON_HANDOFF"), "1", StringComparison.Ordinal);
bool bindLookDownQeForConfig2ForwardDiscovery = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_BIND_LOOK_DOWN_QE_FOR_CONFIG2_FORWARD_DISCOVERY"), "1", StringComparison.Ordinal);
string bindConfig2CensusRowQe = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_BIND_CONFIG2_CENSUS_ROW_QE") ?? string.Empty;
int persistedControllerConfig = int.TryParse(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_PERSISTED_CONTROLLER_CONFIG"), out int parsedPersistedControllerConfig)
    ? parsedPersistedControllerConfig
    : 0;
string musicTarget = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_MUSIC_TARGET") ?? string.Empty;
string musicReplacement = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_MUSIC_REPLACEMENT") ?? string.Empty;
int timeoutSeconds = int.TryParse(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_TIMEOUT_SECONDS"), out int parsed)
    ? parsed
    : 12;
int captureCount = morphCanaryMode ? BoundedIntEnv("ONSLAUGHT_LIVE_CAPTURE_COUNT", 0, 0, 0)
    : BoundedIntEnv("ONSLAUGHT_LIVE_CAPTURE_COUNT", 1, 1, 10);
int preInputCaptureCount = BoundedIntEnv("ONSLAUGHT_LIVE_PRE_INPUT_CAPTURE_COUNT", 0, 0, 3);
int captureIntervalSeconds = BoundedIntEnv("ONSLAUGHT_LIVE_CAPTURE_INTERVAL_SECONDS", 2, 0, 15);
int postWindowDelaySeconds = BoundedIntEnv("ONSLAUGHT_LIVE_POST_WINDOW_DELAY_SECONDS", 0, 0, 30);
int inputStepDelayMs = BoundedIntEnv("ONSLAUGHT_LIVE_INPUT_STEP_DELAY_MS", 60, 0, 1000);
int afterInputCaptureDelayMs = BoundedIntEnv("ONSLAUGHT_LIVE_AFTER_INPUT_CAPTURE_DELAY_MS", 250, 0, 5000);
bool cdbObserverEnabled = string.Equals(Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_CDB_OBSERVER_ENABLED"), "1", StringComparison.Ordinal);
string cdbStartScript = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_CDB_START_SCRIPT") ?? string.Empty;
string cdbCommandFile = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_CDB_COMMAND_FILE") ?? string.Empty;
string cdbLogPath = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_CDB_LOG_PATH") ?? string.Empty;
int cdbLogReadyTimeoutMilliseconds = BoundedIntEnv("ONSLAUGHT_LIVE_CDB_LOG_READY_TIMEOUT_MS", 10000, 1000, 30000);
int cdbPostAttachWaitSeconds = BoundedIntEnv("ONSLAUGHT_LIVE_CDB_POST_ATTACH_WAIT_SECONDS", 2, 0, 15);
string cdbAttachPhase = Environment.GetEnvironmentVariable("ONSLAUGHT_LIVE_CDB_ATTACH_PHASE") ?? "after-window";

string installedExe = Path.Combine(sourceRoot, "BEA.exe");
string installedHashBefore = Sha256File(installedExe);
string overrideHashBefore = Sha256File(exeOverride);
SortedDictionary<string, string> sourceSaveAndOptionsHashesBefore = SnapshotRelativeHashes(sourceRoot, "defaultoptions.bea", "savegames");
object[] processBaselineBefore = SnapshotBeaProcesses();
if (processBaselineBefore.Length != 0)
{
    throw new InvalidOperationException("Refusing live smoke while BEA.exe is already running; close existing game processes first.");
}
string? sourceMusicTargetPath = stageMusicReplacement ? Path.Combine(sourceRoot, "data", "Music", musicTarget) : null;
string? sourceMusicReplacementPath = stageMusicReplacement ? musicReplacement : null;
string? sourceMusicTargetHashBefore = sourceMusicTargetPath is null ? null : Sha256File(sourceMusicTargetPath);
string? sourceMusicReplacementHashBefore = sourceMusicReplacementPath is null ? null : Sha256File(sourceMusicReplacementPath);
GameProfileManagedProcess? managed = null;
GameProfileStopResult? stopResult = null;
int? observedProcessId = null;
bool observedAlive = false;
bool observedExitedBeforeStop = false;
string observedMainWindowHandle = "0x0";
SortedDictionary<string, string>? copiedSaveAndOptionsHashesPrepared = null;
SortedDictionary<string, string>? copiedSaveAndOptionsHashesBefore = null;
SortedDictionary<string, string>? copiedSaveAndOptionsHashesAfter = null;
string? copiedDefaultOptionsHashPrepared = null;
string? copiedDefaultOptionsHashBeforeLaunch = null;
object[]? copiedDefaultOptionsControlOptionDiffs = null;
object[]? copiedDefaultOptionsBackups = null;
List<JsonElement> inputResults = new();
List<object> inputCdbWindows = new();
List<JsonElement> captureResults = new();
JsonElement? preInputFocusResult = null;
JsonElement? cdbObserverResult = null;
JsonElement? cdbObserverCleanupResult = null;
int? cdbObserverProcessId = null;
GameProfileMusicReplacementResult? musicStage = null;
GameProfileControlOptionsResult? controlOptions = null;

try
{
    GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
        new GameProfilePrepareOptions(
            SourceGameRoot: sourceRoot,
            OutputRoot: profilesRoot,
            ProfileName: $"live-safe-copy-{DateTime.UtcNow:yyyyMMdd-HHmmss}",
            ExecutableOverridePath: exeOverride,
            ApplyWindowedCompatibilityPatch: !morphCanaryMode,
            AllowByteLayoutOnlyTarget: false,
            IncludeSavegames: false,
            PatchKeys: patchKeys,
            LaunchArguments: launchArguments,
            ProfilePresetId: string.IsNullOrWhiteSpace(profilePresetId) ? null : profilePresetId));

    string copiedDefaultOptionsPath = Path.Combine(prepared.TargetGameRoot, "defaultoptions.bea");
    copiedSaveAndOptionsHashesPrepared = SnapshotRelativeHashes(prepared.TargetGameRoot, "defaultoptions.bea", "savegames");
    byte[] copiedDefaultOptionsBytesPrepared = File.ReadAllBytes(copiedDefaultOptionsPath);
    copiedDefaultOptionsHashPrepared = Sha256File(copiedDefaultOptionsPath);

    if (sharpenMouseLook || persistedControllerConfig > 0 || bindForwardQeForInputIsolation || bindFireQeForWeaponHandoff || bindLookDownQeForConfig2ForwardDiscovery || !string.IsNullOrWhiteSpace(bindConfig2CensusRowQe))
    {
        List<ConfigurationKeybindRow> keybindRows = new();
        if (bindForwardQeForInputIsolation)
        {
            keybindRows.Add(new ConfigurationKeybindRow
            {
                GroupLabel = "Movement",
                ActionLabel = "Forward",
                EntryId = 0x1f,
                KeyboardDeviceCode = 9u,
                CurrentPlayer1Token = "",
                CurrentPlayer2Token = "",
                Player1Token = "Q",
                Player2Token = "E"
            });
        }
        if (bindFireQeForWeaponHandoff)
        {
            keybindRows.Add(new ConfigurationKeybindRow
            {
                GroupLabel = "Actions",
                ActionLabel = "Fire weapon",
                EntryId = 0x12,
                KeyboardDeviceCode = 10u,
                AllowMouseButtons = true,
                MirrorEntryId = 0x13,
                MirrorKeyboardDeviceCode = 9u,
                CurrentPlayer1Token = "",
                CurrentPlayer2Token = "",
                Player1Token = "Q",
                Player2Token = "E"
            });
        }
        if (bindLookDownQeForConfig2ForwardDiscovery)
        {
            keybindRows.Add(new ConfigurationKeybindRow
            {
                GroupLabel = "Look",
                ActionLabel = "Down",
                EntryId = 0x1c,
                KeyboardDeviceCode = 9u,
                AllowLookMouse = true,
                CurrentPlayer1Token = "",
                CurrentPlayer2Token = "",
                Player1Token = "Q",
                Player2Token = "E"
            });
        }
        if (!string.IsNullOrWhiteSpace(bindConfig2CensusRowQe))
        {
            keybindRows.Add(Config2CensusRowQe(bindConfig2CensusRowQe));
        }
        ConfigurationKeybindRow[]? inputIsolationKeybindRows = keybindRows.Count > 0 ? keybindRows.ToArray() : null;

        controlOptions = GameProfileControlOptionsService.ApplyToSafeCopy(
            new GameProfileControlOptionsRequest(
                ProfileRoot: prepared.TargetGameRoot,
                AppOwnedProfilesRoot: profilesRoot,
                MouseSensitivityOverride: sharpenMouseLook ? GameProfileControlOptionsService.SharperMouseLookSensitivity : null,
                ControllerConfigP1Override: persistedControllerConfig > 0 ? (uint)persistedControllerConfig : null,
                ControllerConfigP2Override: persistedControllerConfig > 0 ? (uint)persistedControllerConfig : null,
                KeybindRows: inputIsolationKeybindRows));
    }

    byte[] copiedDefaultOptionsBytesBeforeLaunch = File.ReadAllBytes(copiedDefaultOptionsPath);
    copiedDefaultOptionsHashBeforeLaunch = Sha256File(copiedDefaultOptionsPath);
    copiedDefaultOptionsControlOptionDiffs = BuildByteDiffRanges(
        copiedDefaultOptionsBytesPrepared,
        copiedDefaultOptionsBytesBeforeLaunch);
    copiedDefaultOptionsBackups = SnapshotRelativeFileHashes(prepared.TargetGameRoot, "defaultoptions.bea.*.bak");

    if (stageMusicReplacement)
    {
        GameProfileMusicReplacementOptions musicOptions = string.IsNullOrWhiteSpace(musicSwapPresetId)
            ? new GameProfileMusicReplacementOptions(
                SafeGameRoot: prepared.TargetGameRoot,
                AppOwnedProfilesRoot: profilesRoot,
                TargetMusicFileName: musicTarget,
                ReplacementOggPath: musicReplacement)
            : GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions(
                prepared.TargetGameRoot,
                profilesRoot,
                musicSwapPresetId);
        musicStage = GameProfileMusicReplacementService.StageReplacement(musicOptions);
    }

    copiedSaveAndOptionsHashesBefore = SnapshotRelativeHashes(prepared.TargetGameRoot, "defaultoptions.bea", "savegames");

    managed = GameProfileRuntimeService.LaunchCopiedProfile(
        new GameProfileLaunchOptions(
            ProfileRoot: prepared.TargetGameRoot,
            AppOwnedProfilesRoot: profilesRoot,
            LaunchArguments: launchArguments));

    observedProcessId = managed.ProcessId;
    if (cdbObserverEnabled && string.Equals(cdbAttachPhase, "after-launch", StringComparison.OrdinalIgnoreCase))
    {
        cdbObserverResult = StartCdbObserver(
            powershellExe,
            cdbStartScript,
            observedProcessId.Value,
            managed.ExecutablePath,
            managed.WorkingDirectory,
            profilesRoot,
            cdbCommandFile,
            cdbLogPath,
            cdbLogReadyTimeoutMilliseconds,
            Path.Combine(captureDir, "cdb-observer.json"));
        cdbObserverProcessId = JsonNullableInt(cdbObserverResult.Value, "cdbProcessId");
        if (cdbPostAttachWaitSeconds > 0)
            Thread.Sleep(TimeSpan.FromSeconds(cdbPostAttachWaitSeconds));
    }
    DateTime deadline = DateTime.UtcNow.AddSeconds(timeoutSeconds);
    while (DateTime.UtcNow < deadline)
    {
        try
        {
            using Process running = Process.GetProcessById(managed.ProcessId);
            observedExitedBeforeStop = running.HasExited;
            if (!running.HasExited)
            {
                observedAlive = true;
                running.Refresh();
                if (running.MainWindowHandle != IntPtr.Zero)
                {
                    observedMainWindowHandle = HwndHex(running.MainWindowHandle);
                    break;
                }
            }
        }
        catch (ArgumentException)
        {
            observedExitedBeforeStop = true;
            break;
        }

        Thread.Sleep(500);
    }

    if (observedProcessId.HasValue && !string.Equals(observedMainWindowHandle, "0x0", StringComparison.OrdinalIgnoreCase))
    {
        if (postWindowDelaySeconds > 0)
            Thread.Sleep(TimeSpan.FromSeconds(postWindowDelaySeconds));

        if (cdbObserverEnabled && string.Equals(cdbAttachPhase, "after-window", StringComparison.OrdinalIgnoreCase))
        {
            cdbObserverResult = StartCdbObserver(
                powershellExe,
                cdbStartScript,
                observedProcessId.Value,
                managed.ExecutablePath,
                managed.WorkingDirectory,
                profilesRoot,
                cdbCommandFile,
                cdbLogPath,
                cdbLogReadyTimeoutMilliseconds,
                Path.Combine(captureDir, "cdb-observer.json"));
            cdbObserverProcessId = JsonNullableInt(cdbObserverResult.Value, "cdbProcessId");
            if (cdbPostAttachWaitSeconds > 0)
                Thread.Sleep(TimeSpan.FromSeconds(cdbPostAttachWaitSeconds));
        }

        if (focusBeforePreInputCapture && preInputCaptureCount > 0)
        {
            preInputFocusResult = SendInputSequence(
                powershellExe,
                inputScript,
                observedProcessId.Value,
                observedMainWindowHandle,
                managed.ExecutablePath,
                managed.WorkingDirectory,
                "wait:1",
                inputStepDelayMs,
                allowBackgroundWindowMessages,
                backgroundWindowMessagesArm,
                Path.Combine(captureDir, "safe-copy-pre-input-focus.json"));
        }

        for (int i = 0; i < preInputCaptureCount; i++)
        {
            string outputPng = i == 0
                ? Path.Combine(captureDir, "safe-copy-pre-input-frame.png")
                : Path.Combine(captureDir, $"safe-copy-pre-input-frame-{i + 1:D2}.png");
            string outputJson = i == 0
                ? Path.Combine(captureDir, "safe-copy-pre-input-frame.json")
                : Path.Combine(captureDir, $"safe-copy-pre-input-frame-{i + 1:D2}.json");

            captureResults.Add(CaptureFrame(
                powershellExe,
                captureScript,
                observedProcessId.Value,
                observedMainWindowHandle,
                managed.ExecutablePath,
                managed.WorkingDirectory,
                captureDir,
                sourceRoot,
                outputPng,
                outputJson));

            if (i + 1 < preInputCaptureCount && captureIntervalSeconds > 0)
                Thread.Sleep(TimeSpan.FromSeconds(captureIntervalSeconds));
        }

        for (int i = 0; i < inputSequences.Length; i++)
        {
            long? cdbLogStartByte = cdbObserverEnabled ? CdbLogLength(cdbLogPath) : null;
            JsonElement inputResult = SendInputSequence(
                powershellExe,
                inputScript,
                observedProcessId.Value,
                observedMainWindowHandle,
                managed.ExecutablePath,
                managed.WorkingDirectory,
                inputSequences[i],
                inputStepDelayMs,
                allowBackgroundWindowMessages,
                backgroundWindowMessagesArm,
                Path.Combine(captureDir, $"safe-copy-input-{i + 1:D2}.json"));
            inputResults.Add(inputResult);
            if (cdbObserverEnabled)
                Thread.Sleep(TimeSpan.FromMilliseconds(Math.Max(250, inputStepDelayMs)));
            long? cdbLogEndByte = cdbObserverEnabled ? CdbLogLength(cdbLogPath) : null;
            if (cdbObserverEnabled)
            {
                inputCdbWindows.Add(new
                {
                    index = i + 1,
                    sequence = inputSequences[i],
                    logPath = cdbLogPath,
                    logStartByte = cdbLogStartByte,
                    logEndByte = cdbLogEndByte,
                    claimBoundary = "Byte offsets into the exact-PID CDB log around one scoped input sequence; used to avoid writing markers into the debugger-owned log."
                });
            }

            if (captureAfterEachInputSequence)
            {
                if (afterInputCaptureDelayMs > 0)
                    Thread.Sleep(TimeSpan.FromMilliseconds(afterInputCaptureDelayMs));

                captureResults.Add(CaptureFrame(
                    powershellExe,
                    captureScript,
                    observedProcessId.Value,
                    observedMainWindowHandle,
                    managed.ExecutablePath,
                    managed.WorkingDirectory,
                    captureDir,
                    sourceRoot,
                    Path.Combine(captureDir, $"safe-copy-after-input-{i + 1:D2}-frame.png"),
                    Path.Combine(captureDir, $"safe-copy-after-input-{i + 1:D2}-frame.json")));
            }
        }

        for (int i = 0; i < captureCount; i++)
        {
            string outputPng = i == 0
                ? capturePng
                : Path.Combine(captureDir, $"safe-copy-frame-{i + 1:D2}.png");
            string outputJson = i == 0
                ? captureJson
                : Path.Combine(captureDir, $"safe-copy-frame-{i + 1:D2}.json");

            captureResults.Add(CaptureFrame(
                powershellExe,
                captureScript,
                observedProcessId.Value,
                observedMainWindowHandle,
                managed.ExecutablePath,
                managed.WorkingDirectory,
                captureDir,
                sourceRoot,
                outputPng,
                outputJson));

            if (i + 1 < captureCount && captureIntervalSeconds > 0)
                Thread.Sleep(TimeSpan.FromSeconds(captureIntervalSeconds));
        }
    }
    else
    {
        foreach (string inputSequence in inputSequences)
            inputResults.Add(InputSkipped("No live managed window was available for scoped input.", inputSequence));
        captureResults.Add(CaptureSkipped("No live managed window was captured before launch observation.", capturePng));
    }

    stopResult = GameProfileRuntimeService.StopCopiedProfile(
        managed,
        profilesRoot,
        gracefulTimeout: TimeSpan.FromSeconds(3));
    cdbObserverCleanupResult = CleanupCdbObserver(cdbObserverProcessId);
    object[] processBaselineAfterStop = WaitForNoBeaProcesses(TimeSpan.FromSeconds(5));

    string installedHashAfter = Sha256File(installedExe);
    string overrideHashAfter = Sha256File(exeOverride);
    SortedDictionary<string, string> sourceSaveAndOptionsHashesAfter = SnapshotRelativeHashes(sourceRoot, "defaultoptions.bea", "savegames");
    copiedSaveAndOptionsHashesAfter = SnapshotRelativeHashes(prepared.TargetGameRoot, "defaultoptions.bea", "savegames");
    string? sourceMusicTargetHashAfter = sourceMusicTargetPath is null ? null : Sha256File(sourceMusicTargetPath);
    string? sourceMusicReplacementHashAfter = sourceMusicReplacementPath is null ? null : Sha256File(sourceMusicReplacementPath);
    bool installedHashUnchanged = string.Equals(installedHashBefore, installedHashAfter, StringComparison.OrdinalIgnoreCase);
    bool overrideHashUnchanged = string.Equals(overrideHashBefore, overrideHashAfter, StringComparison.OrdinalIgnoreCase);
    bool sourceSaveAndOptionsUnchanged = HashMapsEqual(sourceSaveAndOptionsHashesBefore, sourceSaveAndOptionsHashesAfter);
    bool copiedSaveAndOptionsUnchanged = copiedSaveAndOptionsHashesBefore is not null &&
        copiedSaveAndOptionsHashesAfter is not null &&
        HashMapsEqual(copiedSaveAndOptionsHashesBefore, copiedSaveAndOptionsHashesAfter);
    bool sourceMusicTargetHashUnchanged = sourceMusicTargetPath is null ||
        string.Equals(sourceMusicTargetHashBefore, sourceMusicTargetHashAfter, StringComparison.OrdinalIgnoreCase);
    bool sourceMusicReplacementHashUnchanged = sourceMusicReplacementPath is null ||
        string.Equals(sourceMusicReplacementHashBefore, sourceMusicReplacementHashAfter, StringComparison.OrdinalIgnoreCase);
    int inputSequencesSent = inputResults.Count(result =>
        result.TryGetProperty("status", out JsonElement statusEl) &&
        string.Equals(statusEl.GetString(), "sent", StringComparison.OrdinalIgnoreCase));
    int focusedInputSequences = inputResults.Count(result =>
        result.TryGetProperty("status", out JsonElement statusEl) &&
        string.Equals(statusEl.GetString(), "sent", StringComparison.OrdinalIgnoreCase) &&
        JsonBool(result, "focused"));
    int inputActionCount = inputResults.Sum(result => JsonInt(result, "actionCount"));
    int inputKeyEventsSent = inputResults.Sum(result => JsonInt(result, "keyEventsSent"));
    int inputSendInputEventsSent = inputResults.Sum(result => JsonInt(result, "sendInputEventsSent"));
    int inputScanKeybdEventsSent = inputResults.Sum(result => JsonInt(result, "scanKeybdEventsSent"));
    int inputWindowMessageEventsSent = inputResults.Sum(result => JsonInt(result, "windowMessageEventsSent"));
    int inputMouseEventsSent = inputResults.Sum(result => JsonInt(result, "mouseEventsSent"));
    bool cdbObserverCleanupSucceeded = !cdbObserverEnabled ||
        (cdbObserverCleanupResult.HasValue &&
            JsonStringIn(cdbObserverCleanupResult.Value, "status", "stopped", "already-exited"));
    bool cdbObserverSucceeded = !cdbObserverEnabled ||
        (cdbObserverResult.HasValue &&
            JsonNullableInt(cdbObserverResult.Value, "cdbProcessId").HasValue &&
            cdbObserverResult.Value.TryGetProperty("status", out JsonElement cdbStatusEl) &&
            string.Equals(cdbStatusEl.GetString(), "attached", StringComparison.OrdinalIgnoreCase) &&
            cdbObserverCleanupSucceeded);
    var payload = new
    {
        schemaVersion = "winui-safe-copy-live-runtime-smoke.v1",
        generatedAt = DateTimeOffset.UtcNow,
        mutation = true,
        source = new
        {
            sourceRoot,
            installedExeFileName = Path.GetFileName(installedExe),
            installedHashBefore,
            installedHashAfter,
            installedHashUnchanged,
            executableOverrideFileName = Path.GetFileName(exeOverride),
            overrideHashBefore,
            overrideHashAfter,
            overrideHashUnchanged,
            saveAndOptions = new
            {
                before = sourceSaveAndOptionsHashesBefore,
                after = sourceSaveAndOptionsHashesAfter,
                unchanged = sourceSaveAndOptionsUnchanged,
            },
        },
        safeCopy = new
        {
            prepared.TargetGameRoot,
            prepared.ExecutablePath,
            prepared.ManifestPath,
            prepared.ProfilePresetId,
            prepared.ProfilePresetDisplayName,
            prepared.ProfilePresetProofStatus,
            prepared.ProfileDefaultControllerConfiguration,
            prepared.ProfileDefaultPersistControllerConfigInOptions,
            prepared.ProfileDefaultSharpenMouseLook,
            requestedPatchKeys = patchKeys,
            patchKeys = prepared.PatchResult.PatchKeys,
            copiedEntries = prepared.Entries.Count,
            controlOptions = controlOptions is null
                ? null
                : new
                {
                    requestedSharperMouseLook = sharpenMouseLook,
                    requestedPersistedControllerConfig = persistedControllerConfig > 0,
                    requestedControllerConfig = persistedControllerConfig > 0 ? persistedControllerConfig : (int?)null,
                    requestedInputIsolationForwardQe = bindForwardQeForInputIsolation,
                    requestedWeaponFireQe = bindFireQeForWeaponHandoff,
                    requestedConfig2ForwardDiscoveryLookDownQe = bindLookDownQeForConfig2ForwardDiscovery,
                    requestedConfig2CensusRowQe = string.IsNullOrWhiteSpace(bindConfig2CensusRowQe) ? null : bindConfig2CensusRowQe,
                    proofLever = bindForwardQeForInputIsolation
                        ? "copied-defaultoptions-input-isolation-forward-qe"
                        : bindFireQeForWeaponHandoff
                        ? "copied-defaultoptions-weapon-fire-qe"
                        : bindLookDownQeForConfig2ForwardDiscovery
                        ? "copied-defaultoptions-config2-forward-discovery-look-down-qe"
                        : !string.IsNullOrWhiteSpace(bindConfig2CensusRowQe)
                        ? "copied-defaultoptions-config2-census-" + bindConfig2CensusRowQe + "-qe"
                        : sharpenMouseLook && persistedControllerConfig > 0
                        ? "copied-defaultoptions-mouse-sensitivity-and-controller-config"
                        : sharpenMouseLook
                            ? "copied-defaultoptions-mouse-sensitivity-only"
                            : "copied-defaultoptions-controller-config-only",
                    controlOptions.OptionsPath,
                    controlOptions.MouseSensitivity,
                    observedControllerConfigP1 = controlOptions.ControllerConfigP1,
                    observedControllerConfigP2 = controlOptions.ControllerConfigP2,
                    controlOptions.ManifestPath,
                    controlOptions.ProofStatus,
                    controlOptions.Message,
                    hashBefore = controlOptions.HashBefore,
                    hashAfter = controlOptions.HashAfter,
                    hashAfterPrepare = copiedDefaultOptionsHashPrepared,
                    hashBeforeLaunch = copiedDefaultOptionsHashBeforeLaunch,
                    changedAfterPrepare = !string.Equals(copiedDefaultOptionsHashPrepared, copiedDefaultOptionsHashBeforeLaunch, StringComparison.OrdinalIgnoreCase),
                    changedRanges = copiedDefaultOptionsControlOptionDiffs,
                    backups = copiedDefaultOptionsBackups,
                    note = persistedControllerConfig > 0
                        ? "Controller configuration was also persisted into the copied defaultoptions.bea for both players; launch -configuration remains a separate launch-argument proof lever."
                        : "Controller configuration in this artifact is a launch argument proof lever, not a copied defaultoptions.bea controller-config patch."
                },
            saveAndOptions = new
            {
                afterPrepare = copiedSaveAndOptionsHashesPrepared,
                before = copiedSaveAndOptionsHashesBefore,
                after = copiedSaveAndOptionsHashesAfter,
                unchanged = copiedSaveAndOptionsUnchanged,
                note = "Copied safe-game save/options files may change during launch; source save/options unchanged is the source-safety gate."
            },
        },
        musicReplacement = musicStage is null
            ? null
            : new
            {
                musicStage.SchemaVersion,
                MusicSwapPresetId = string.IsNullOrWhiteSpace(musicSwapPresetId) ? null : musicSwapPresetId,
                musicStage.TargetMusicFileName,
                musicStage.TargetRelativePath,
                musicStage.BackupRelativePath,
                ManifestPath = musicStage.ManifestPath,
                SourceTargetFileName = sourceMusicTargetPath is null ? null : Path.GetFileName(sourceMusicTargetPath),
                SourceTargetHashBefore = sourceMusicTargetHashBefore,
                SourceTargetHashAfter = sourceMusicTargetHashAfter,
                SourceTargetHashUnchanged = sourceMusicTargetHashUnchanged,
                SourceReplacementFileName = sourceMusicReplacementPath is null ? null : Path.GetFileName(sourceMusicReplacementPath),
                SourceReplacementHashBefore = sourceMusicReplacementHashBefore,
                SourceReplacementHashAfter = sourceMusicReplacementHashAfter,
                SourceReplacementHashUnchanged = sourceMusicReplacementHashUnchanged,
                musicStage.OriginalSize,
                musicStage.OriginalSha256,
                musicStage.ReplacementSize,
                musicStage.ReplacementSha256,
                targetNowMatchesReplacement = string.Equals(Sha256File(musicStage.TargetPath), musicStage.ReplacementSha256, StringComparison.OrdinalIgnoreCase),
                backupMatchesOriginal = string.Equals(Sha256File(musicStage.BackupPath), musicStage.OriginalSha256, StringComparison.OrdinalIgnoreCase),
            },
        launch = new
        {
            processId = observedProcessId,
            observedAlive,
            observedExitedBeforeStop,
            mainWindowHandle = observedMainWindowHandle,
            managed?.WorkingDirectory,
            requestedArguments = launchArguments,
            arguments = managed?.Arguments,
        },
        processBaseline = new
        {
            beforeLaunch = processBaselineBefore,
            afterStop = processBaselineAfterStop,
            noPreexistingBea = processBaselineBefore.Length == 0,
            noBeaAfterStop = processBaselineAfterStop.Length == 0,
        },
        cdbObserver = cdbObserverEnabled
            ? new
            {
                enabled = true,
                commandFile = cdbCommandFile,
                logPath = cdbLogPath,
                logReadyTimeoutMilliseconds = cdbLogReadyTimeoutMilliseconds,
                postAttachWaitSeconds = cdbPostAttachWaitSeconds,
                attachPhase = cdbAttachPhase,
                result = cdbObserverResult,
                cleanup = cdbObserverCleanupResult,
                claimBoundary = "Exact-PID CDB observer attach for copied-profile runtime evidence only. This can support bounded runtime observations for one instrumented run; it is not uninstrumented gameplay proof, not online/network proof, not controller-assignment proof, not P1/P2 input-isolation proof, and not rebuild parity by itself."
            }
            : null,
        input = inputResults.Count == 0 ? null : inputResults,
        inputCdbWindows = inputCdbWindows.Count == 0 ? null : inputCdbWindows,
        preInputFocus = preInputFocusResult,
        inputPlan = new
        {
            inputSequenceCount = inputSequences.Length,
            inputStepDelayMs,
            allowBackgroundWindowMessages,
            focusBeforePreInputCapture,
        },
        inputSummary = new
        {
            inputSequencesSent,
            focusedInputSequences,
            inputActionCount,
            inputKeyEventsSent,
            inputSendInputEventsSent,
            inputScanKeybdEventsSent,
            inputWindowMessageEventsSent,
            inputMouseEventsSent,
        },
        capture = captureResults[0],
        captures = captureResults,
        capturePlan = new
        {
            captureCount,
            preInputCaptureCount,
            focusBeforePreInputCapture,
            captureAfterEachInputSequence,
            afterInputCaptureDelayMs,
            captureIntervalSeconds,
            postWindowDelaySeconds,
        },
        stop = stopResult,
        claimBoundary = "Live launch/capture/stop smoke with optional bounded scoped input and one or more bounded screen-region captures at verified target window bounds only. Source executable, source defaultoptions.bea/savegames, and optional source music hashes are checked for source-safety; copied game save/options files may change during launch. Optional control options prove only safe-copy launch arguments and copied defaultoptions.bea materialization/read-back; they do not prove improved runtime control feel, analog deadzone behavior, look curves, camera movement, gameplay, menu reach, rendering correctness, visual parity, unoccluded pixels, or rebuild parity unless the focused proof explicitly captures that narrower outcome. Optional music replacement proves staged copied-game file layout survives launch; it does not prove music selection, decode, audible playback, gameplay, menu reach, rendering correctness, visual parity, unoccluded pixels, or rebuild parity unless the focused proof explicitly captures that narrower outcome."
    };

    Directory.CreateDirectory(Path.GetDirectoryName(artifactJson)!);
    File.WriteAllText(artifactJson, JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true }));
    Console.WriteLine(artifactJson);
    bool captureSucceeded = captureResults.Any(result =>
        result.TryGetProperty("status", out JsonElement statusEl) &&
        string.Equals(statusEl.GetString(), "captured", StringComparison.OrdinalIgnoreCase));
    bool inputSucceeded = inputSequences.Length == 0 || inputResults.All(result =>
        result.TryGetProperty("status", out JsonElement statusEl) &&
        string.Equals(statusEl.GetString(), "sent", StringComparison.OrdinalIgnoreCase));
    bool noBeaAfterStop = processBaselineAfterStop.Length == 0;
    bool sourceHashesUnchanged = installedHashUnchanged && overrideHashUnchanged && sourceSaveAndOptionsUnchanged &&
        sourceMusicTargetHashUnchanged && sourceMusicReplacementHashUnchanged;
    return stopResult.Success && observedAlive && captureSucceeded && inputSucceeded && cdbObserverSucceeded &&
        noBeaAfterStop && sourceHashesUnchanged ? 0 : 2;
}
catch
{
    try
    {
        _ = CleanupCdbObserver(cdbObserverProcessId);
    }
    catch
    {
    }

    if (managed is not null)
    {
        try
        {
            _ = GameProfileRuntimeService.StopCopiedProfile(managed, profilesRoot, gracefulTimeout: TimeSpan.FromSeconds(3));
        }
        catch
        {
        }
    }

    throw;
}

sealed class WalkerOwnedPhaseProcess : IDisposable
{
    const uint CREATE_SUSPENDED = 0x00000004;
    const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000;
    readonly IntPtr jobHandle;
    bool closed;

    WalkerOwnedPhaseProcess(string name, Process process, IntPtr jobHandle)
    {
        Name = name;
        Process = process;
        this.jobHandle = jobHandle;
    }

    public string Name { get; }
    public Process Process { get; }
    public uint ActiveProcesses => QueryAccounting().ActiveProcesses;

    public static WalkerOwnedPhaseProcess Start(
        string name, string receiptPath, IReadOnlyDictionary<string, string>? extraEnvironment)
    {
        IntPtr job = CreateJobObjectW(IntPtr.Zero, null);
        if (job == IntPtr.Zero)
            throw new InvalidOperationException("Could not create walker phase ownership job.");
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits = new();
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        if (!SetInformationJobObject(
                job, 9, ref limits, (uint)Marshal.SizeOf<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>()))
        {
            CloseHandle(job);
            throw new InvalidOperationException("Could not bind walker phase job cleanup policy.");
        }

        string phaseName = "ONSLAUGHT_LIVE_WALKER_CHILD_PHASE";
        string receiptName = "ONSLAUGHT_LIVE_WALKER_PHASE_RECEIPT";
        Dictionary<string, string?> prior = new();
        void SetTemporary(string key, string value)
        {
            prior[key] = Environment.GetEnvironmentVariable(key);
            Environment.SetEnvironmentVariable(key, value);
        }
        PROCESS_INFORMATION info = new();
        try
        {
            SetTemporary(phaseName, name);
            SetTemporary(receiptName, receiptPath);
            if (extraEnvironment is not null)
                foreach ((string key, string value) in extraEnvironment)
                    SetTemporary(key, value);
            string host = Environment.ProcessPath ?? throw new InvalidOperationException(
                "Walker phase could not resolve the dotnet host.");
            string assembly = System.Reflection.Assembly.GetExecutingAssembly().Location;
            StringBuilder command = new($"\"{host}\" \"{assembly}\"");
            STARTUPINFO startup = new() { cb = (uint)Marshal.SizeOf<STARTUPINFO>() };
            if (!CreateProcessW(
                    null, command, IntPtr.Zero, IntPtr.Zero, false, CREATE_SUSPENDED,
                    IntPtr.Zero, Environment.CurrentDirectory, ref startup, out info))
                throw new InvalidOperationException("Could not create suspended walker phase process.");
            if (!AssignProcessToJobObject(job, info.hProcess))
                throw new InvalidOperationException("Could not assign walker phase before resume.");
            Process process = Process.GetProcessById((int)info.dwProcessId);
            if (ResumeThread(info.hThread) == uint.MaxValue)
                throw new InvalidOperationException("Could not resume receipt-owned walker phase.");
            return new WalkerOwnedPhaseProcess(name, process, job);
        }
        catch
        {
            if (info.hProcess != IntPtr.Zero)
                _ = TerminateProcess(info.hProcess, 2);
            _ = TerminateJobObject(job, 2);
            CloseHandle(job);
            throw;
        }
        finally
        {
            if (info.hThread != IntPtr.Zero)
                CloseHandle(info.hThread);
            if (info.hProcess != IntPtr.Zero)
                CloseHandle(info.hProcess);
            foreach ((string key, string? value) in prior)
                Environment.SetEnvironmentVariable(key, value);
        }
    }

    public void RequireZeroAndClose()
    {
        if (closed)
            return;
        uint active = ActiveProcesses;
        if (active != 0)
        {
            TerminateExactJobAndClose();
            throw new InvalidOperationException(
                $"Walker {Name} phase left {active} receipt-owned processes.");
        }
        if (!CloseHandle(jobHandle))
            throw new InvalidOperationException("Walker phase job handle did not close.");
        closed = true;
    }

    public void TerminateExactJobAndClose()
    {
        if (closed)
            return;
        Exception? failure = null;
        try
        {
            if (ActiveProcesses > 0 && !TerminateJobObject(jobHandle, 2))
                failure = new InvalidOperationException("Could not terminate exact walker phase job.");
            Stopwatch wait = Stopwatch.StartNew();
            while (ActiveProcesses > 0 && wait.Elapsed < TimeSpan.FromSeconds(5))
                Thread.Sleep(50);
            if (ActiveProcesses > 0)
                failure ??= new InvalidOperationException("Walker phase job did not reach zero.");
        }
        finally
        {
            if (!CloseHandle(jobHandle))
                failure ??= new InvalidOperationException("Walker phase job handle did not close.");
            closed = true;
        }
        if (failure is not null)
            throw failure;
    }

    JOBOBJECT_BASIC_ACCOUNTING_INFORMATION QueryAccounting()
    {
        JOBOBJECT_BASIC_ACCOUNTING_INFORMATION row = new();
        if (!QueryInformationJobObject(
                jobHandle, 1, ref row,
                (uint)Marshal.SizeOf<JOBOBJECT_BASIC_ACCOUNTING_INFORMATION>(), IntPtr.Zero))
            throw new InvalidOperationException("Could not query walker phase job accounting.");
        return row;
    }

    public void Dispose() => TerminateExactJobAndClose();

    [StructLayout(LayoutKind.Sequential)]
    struct STARTUPINFO
    {
        public uint cb; public string? lpReserved; public string? lpDesktop; public string? lpTitle;
        public uint dwX; public uint dwY; public uint dwXSize; public uint dwYSize;
        public uint dwXCountChars; public uint dwYCountChars; public uint dwFillAttribute;
        public uint dwFlags; public ushort wShowWindow; public ushort cbReserved2;
        public IntPtr lpReserved2; public IntPtr hStdInput; public IntPtr hStdOutput; public IntPtr hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct PROCESS_INFORMATION
    {
        public IntPtr hProcess; public IntPtr hThread; public uint dwProcessId; public uint dwThreadId;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct JOBOBJECT_BASIC_LIMIT_INFORMATION
    {
        public long PerProcessUserTimeLimit; public long PerJobUserTimeLimit; public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize; public UIntPtr MaximumWorkingSetSize;
        public uint ActiveProcessLimit; public UIntPtr Affinity; public uint PriorityClass;
        public uint SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct IO_COUNTERS
    {
        public ulong ReadOperationCount; public ulong WriteOperationCount; public ulong OtherOperationCount;
        public ulong ReadTransferCount; public ulong WriteTransferCount; public ulong OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    {
        public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation; public IO_COUNTERS IoInfo;
        public UIntPtr ProcessMemoryLimit; public UIntPtr JobMemoryLimit;
        public UIntPtr PeakProcessMemoryUsed; public UIntPtr PeakJobMemoryUsed;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct JOBOBJECT_BASIC_ACCOUNTING_INFORMATION
    {
        public long TotalUserTime; public long TotalKernelTime; public long ThisPeriodTotalUserTime;
        public long ThisPeriodTotalKernelTime; public uint TotalPageFaultCount; public uint TotalProcesses;
        public uint ActiveProcesses; public uint TotalTerminatedProcesses;
    }

    [DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern IntPtr CreateJobObjectW(IntPtr securityAttributes, string? name);
    [DllImport("kernel32", SetLastError = true)]
    static extern bool SetInformationJobObject(
        IntPtr job, int infoClass, ref JOBOBJECT_EXTENDED_LIMIT_INFORMATION info, uint length);
    [DllImport("kernel32", SetLastError = true)]
    static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
    [DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool CreateProcessW(
        string? applicationName, StringBuilder commandLine, IntPtr processAttributes,
        IntPtr threadAttributes, bool inheritHandles, uint creationFlags, IntPtr environment,
        string currentDirectory, ref STARTUPINFO startup, out PROCESS_INFORMATION processInfo);
    [DllImport("kernel32", SetLastError = true)]
    static extern uint ResumeThread(IntPtr thread);
    [DllImport("kernel32", SetLastError = true)]
    static extern bool TerminateProcess(IntPtr process, uint exitCode);
    [DllImport("kernel32", SetLastError = true)]
    static extern bool TerminateJobObject(IntPtr job, uint exitCode);
    [DllImport("kernel32", SetLastError = true)]
    static extern bool QueryInformationJobObject(
        IntPtr job, int infoClass, ref JOBOBJECT_BASIC_ACCOUNTING_INFORMATION info,
        uint length, IntPtr returnLength);
    [DllImport("kernel32", SetLastError = true)]
    static extern bool CloseHandle(IntPtr handle);
}
"""
    program_text = program_text.replace(
        "__CANARY_CLEANUP_PHASE_BLOCK__",
        render_canary_cleanup_phase_block(),
    ).replace(
        "__CANARY_CLEANUP_OBJECT__",
        render_canary_cleanup_object(),
    )
    if create_new:
        with program.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(program_text)
    else:
        program.write_text(program_text, encoding="utf-8")
    return project


def _run_walker_prebuild_process(
    command: list[str], *, cwd: Path, env: Mapping[str, str], timeout_seconds: float,
) -> tuple[subprocess.CompletedProcess[str], int, dict[str, Any]]:
    job_handle = _create_receipt_owned_build_job()
    kernel32 = _kernel32_process_api()
    process: subprocess.Popen[str] | None = None
    assigned_to_job = False
    ownership_handed_to_cleanup = False
    try:
        process = subprocess.Popen(
            command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=dict(env), creationflags=getattr(subprocess, "CREATE_SUSPENDED", 0x00000004),
        )
        deadline = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=timeout_seconds)
        root_identity = _process_identity(process.pid)
        if root_identity is None:
            raise RuntimeError("dotnet build root identity could not be captured")
        root_identity.update({
            "parentProcessId": os.getpid(),
            "imageName": Path(str(root_identity["executablePath"])).name,
            "role": "buildRoot",
        })
        captured: dict[int, dict[str, Any]] = {process.pid: root_identity}
        if not kernel32.AssignProcessToJobObject(
            job_handle, wintypes.HANDLE(int(process._handle)),
        ):
            raise OSError("could not assign suspended runner build to its receipt-owned job")
        assigned_to_job = True
        _resume_suspended_process(process)
        ownership: dict[str, Any] = {
            "ownershipMode": "windows-job-object-before-resume",
            "jobHandle": int(job_handle),
            "jobAssignedBeforeResume": True,
            "capturedProcesses": captured,
        }
        while True:
            _capture_job_owned_processes(int(job_handle), captured)
            remaining = (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds()
            try:
                stdout, stderr = process.communicate(timeout=max(0.01, min(0.10, remaining)))
                _capture_job_owned_processes(int(job_handle), captured)
                ownership["accountingAtBuildExit"] = _job_accounting(int(job_handle))
                ownership_handed_to_cleanup = True
                return (
                    subprocess.CompletedProcess(command, process.returncode, stdout, stderr),
                    process.pid, ownership,
                )
            except subprocess.TimeoutExpired:
                if remaining > 0:
                    continue
                if not kernel32.TerminateJobObject(job_handle, 124):
                    raise OSError("could not stop the exact receipt-owned runner-build job")
                stdout, stderr = process.communicate()
                _capture_job_owned_processes(int(job_handle), captured)
                ownership["accountingAtBuildExit"] = _job_accounting(int(job_handle))
                ownership["terminatedForPrebuildTimeout"] = True
                ownership_handed_to_cleanup = True
                return subprocess.CompletedProcess(command, 124, stdout, stderr), process.pid, ownership
    finally:
        if not ownership_handed_to_cleanup:
            try:
                if assigned_to_job:
                    kernel32.TerminateJobObject(job_handle, 2)
                elif process is not None:
                    process.kill()
            finally:
                if process is not None:
                    try:
                        process.communicate(timeout=5)
                    except BaseException:
                        pass
                kernel32.CloseHandle(job_handle)


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
    )]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", _IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong), ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD), ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD), ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


def _kernel32_process_api():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.GetProcessTimes.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
        ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateProcess.restype = wintypes.BOOL
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryInformationJobObject.restype = wintypes.BOOL
    kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateJobObject.restype = wintypes.BOOL
    return kernel32


def _create_receipt_owned_build_job() -> int:
    kernel32 = _kernel32_process_api()
    handle = kernel32.CreateJobObjectW(None, None)
    if not handle:
        raise OSError("could not create receipt-owned runner-build job")
    limits = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    limits.BasicLimitInformation.LimitFlags = 0x00002000  # KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        handle, 9, ctypes.byref(limits), ctypes.sizeof(limits),
    ):
        kernel32.CloseHandle(handle)
        raise OSError("could not bind runner-build job cleanup policy")
    return int(handle)


def _resume_suspended_process(process: subprocess.Popen[str]) -> None:
    ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
    ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]
    ntdll.NtResumeProcess.restype = ctypes.c_long
    status = ntdll.NtResumeProcess(wintypes.HANDLE(int(process._handle)))
    if status != 0:
        raise OSError(f"could not resume receipt-owned runner build: NTSTATUS {status:#x}")


def _job_accounting(job_handle: int) -> dict[str, int]:
    kernel32 = _kernel32_process_api()
    row = _JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
    returned = wintypes.DWORD()
    if not kernel32.QueryInformationJobObject(
        wintypes.HANDLE(job_handle), 1, ctypes.byref(row), ctypes.sizeof(row),
        ctypes.byref(returned),
    ):
        raise OSError("could not query receipt-owned runner-build job accounting")
    return {
        "totalProcesses": int(row.TotalProcesses),
        "activeProcesses": int(row.ActiveProcesses),
        "totalTerminatedProcesses": int(row.TotalTerminatedProcesses),
    }


def _job_process_ids(job_handle: int) -> list[int]:
    kernel32 = _kernel32_process_api()
    capacity = 16
    while True:
        size = 8 + capacity * ctypes.sizeof(ctypes.c_size_t)
        buffer = ctypes.create_string_buffer(size)
        returned = wintypes.DWORD()
        if kernel32.QueryInformationJobObject(
            wintypes.HANDLE(job_handle), 3, buffer, size, ctypes.byref(returned),
        ):
            count = wintypes.DWORD.from_buffer(buffer, 4).value
            array_type = ctypes.c_size_t * count
            return [int(pid) for pid in array_type.from_buffer(buffer, 8)]
        required = wintypes.DWORD.from_buffer(buffer, 0).value
        if required <= capacity:
            raise OSError("could not query receipt-owned runner-build job members")
        capacity = int(required)


def _capture_job_owned_processes(
    job_handle: int, captured: dict[int, dict[str, Any]],
) -> None:
    for pid in _job_process_ids(job_handle):
        if pid in captured:
            continue
        identity = _process_identity(pid)
        if identity is None:
            raise RuntimeError("job-owned runner-build process identity could not be captured")
        identity.update({
            "parentProcessId": -1,
            "imageName": Path(str(identity["executablePath"])).name,
            "role": "buildDescendant",
        })
        captured[pid] = identity


def _process_identity(pid: int) -> dict[str, Any] | None:
    if os.name != "nt":
        return None
    kernel32 = _kernel32_process_api()
    handle = kernel32.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return None
        creation = wintypes.FILETIME()
        exit_time = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        if not kernel32.GetProcessTimes(
            handle, ctypes.byref(creation), ctypes.byref(exit_time),
            ctypes.byref(kernel), ctypes.byref(user),
        ):
            return None
        ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        started = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(microseconds=ticks // 10)
        return {"processId": pid, "startedAtUtc": started.isoformat(), "executablePath": buffer.value}
    finally:
        kernel32.CloseHandle(handle)


def receipt_owned_compiler_cleanup(ownership: Mapping[str, Any]) -> Mapping[str, Any]:
    """Terminate the kernel-owned build job; sampling is diagnostic, not completeness proof."""
    failures: list[str] = []
    job_handle = int(ownership.get("jobHandle", 0))
    captured_map = ownership.get("capturedProcesses")
    captured = list(captured_map.values()) if isinstance(captured_map, dict) else []
    before: dict[str, int] = {}
    after: dict[str, int] = {}
    residue: list[dict[str, Any]] = []
    job_closed = False
    try:
        if (ownership.get("ownershipMode") != "windows-job-object-before-resume"
                or ownership.get("jobAssignedBeforeResume") is not True or job_handle <= 0):
            raise RuntimeError("runner-build job ownership receipt is incomplete")
        _capture_job_owned_processes(job_handle, captured_map)
        captured = list(captured_map.values())
        before = _job_accounting(job_handle)
        if before.get("totalProcesses") != len(captured):
            failures.append(
                "runner-build job accounting does not match the captured identity ledger"
            )
        kernel32 = _kernel32_process_api()
        if before["activeProcesses"] > 0 and not kernel32.TerminateJobObject(
            wintypes.HANDLE(job_handle), 2,
        ):
            raise OSError("could not terminate exact receipt-owned runner-build job")
        for _ in range(100):
            after = _job_accounting(job_handle)
            if after["activeProcesses"] == 0:
                break
            time.sleep(0.05)
        if not after or after["activeProcesses"] != 0:
            for pid in _job_process_ids(job_handle):
                identity = _process_identity(pid)
                if identity is not None:
                    residue.append(identity)
            failures.append("receipt-owned runner-build job did not reach zero")
    except Exception as exc:
        failures.append(f"{type(exc).__name__}: {exc}")
    finally:
        if job_handle > 0:
            job_closed = bool(_kernel32_process_api().CloseHandle(wintypes.HANDLE(job_handle)))
            if not job_closed:
                failures.append("receipt-owned runner-build job handle did not close")
    return {
        "ownedProcessCount": len(residue), "capturedDescendants": captured,
        "residue": residue, "cleanupConfirmed": not failures and not residue,
        "failures": failures,
        "ownershipMode": ownership.get("ownershipMode"),
        "jobAssignedBeforeResume": ownership.get("jobAssignedBeforeResume"),
        "jobAccountingBeforeCleanup": before,
        "jobAccountingAfterCleanup": after,
        "jobClosed": job_closed,
    }


def _compiler_cleanup_receipt_complete(
    cleanup: Mapping[str, Any], *, build_process_id: int, build_invocation_count: int,
) -> bool:
    captured = cleanup.get("capturedDescendants")
    residue = cleanup.get("residue")
    if (cleanup.get("ownedProcessCount") != 0 or cleanup.get("cleanupConfirmed") is not True
            or not isinstance(captured, list) or not isinstance(residue, list) or residue):
        return False
    before = cleanup.get("jobAccountingBeforeCleanup")
    after = cleanup.get("jobAccountingAfterCleanup")
    if (cleanup.get("ownershipMode") != "windows-job-object-before-resume"
            or cleanup.get("jobAssignedBeforeResume") is not True
            or cleanup.get("jobClosed") is not True
            or not isinstance(before, dict) or not isinstance(after, dict)
            or not isinstance(before.get("totalProcesses"), int)
            or before["totalProcesses"] < 1
            or before["totalProcesses"] != len(captured)
            or after.get("activeProcesses") != 0):
        return False
    if build_invocation_count == 0:
        return build_process_id == 0 and not captured
    if build_invocation_count != 1 or build_process_id <= 0 or not captured:
        return False
    process_ids: set[int] = set()
    for identity in captured:
        if not isinstance(identity, dict):
            return False
        process_id = identity.get("processId")
        if (not isinstance(process_id, int) or process_id <= 0 or process_id in process_ids
                or not isinstance(identity.get("parentProcessId"), int)
                or not str(identity.get("startedAtUtc", "")).strip()
                or not str(identity.get("executablePath", "")).strip()
                or identity.get("role") not in {"buildRoot", "buildDescendant"}):
            return False
        process_ids.add(process_id)
    return build_process_id in process_ids


def _dotnet_sdk_identity() -> Mapping[str, str]:
    dotnet = shutil.which("dotnet")
    if not dotnet:
        raise RuntimeError("dotnet SDK host was not found")
    result = subprocess.run(
        [dotnet, "--version"], text=True, capture_output=True, check=False, timeout=10,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("dotnet SDK identity query failed")
    host = Path(dotnet).resolve()
    return {
        "hostPath": str(host), "hostSha256": file_sha256(host),
        "version": result.stdout.strip(),
    }


def prebuild_walker_runner(
    pair_root: Path,
    *,
    timeout_seconds: int = 150,
    process_runner: Callable[..., tuple[subprocess.CompletedProcess[str], int, dict[str, Any]]] | None = None,
    compiler_cleanup: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate and build the generic AppCore runner once before any attempt root."""
    if timeout_seconds != 150:
        raise ValueError("walker runner prebuild safety bound is fixed at 150 seconds")
    if compiler_cleanup is None:
        raise ValueError("receipt-owned compiler census/cleanup implementation is required")
    if any((pair_root / f"attempt-{attempt:02d}").exists() for attempt in (1, 2)):
        raise ValueError("walker attempt roots must be absent before runner prebuild")
    generation_started = dt.datetime.now(dt.timezone.utc)
    sdk_identity = dict(_dotnet_sdk_identity())
    runner_root = pair_root / "runner"
    project = write_runner(runner_root, create_new=True)
    program = runner_root / "Program.cs"
    appcore_project = ROOT / "OnslaughtCareerEditor.AppCore" / "OnslaughtCareerEditor.AppCore.csproj"
    dependency_paths = [appcore_project, *sorted(
        path for path in appcore_project.parent.rglob("*.cs")
        if "bin" not in path.parts and "obj" not in path.parts
    )]
    env = os.environ.copy()
    env["MSBUILDDISABLENODEREUSE"] = "1"
    env["DOTNET_CLI_USE_MSBUILD_SERVER"] = "0"
    runner = process_runner or _run_walker_prebuild_process

    # Generation-phase restore produces project.assets.json so the single locked
    # build may keep --no-restore. Restore is not a second build invocation.
    restore_command = [
        "dotnet", "restore", str(project), "--nologo",
        "-p:UseSharedCompilation=false", "-nodeReuse:false",
    ]
    restore_started = dt.datetime.now(dt.timezone.utc)
    generation_elapsed = (restore_started - generation_started).total_seconds()
    restore_stdout = ""
    restore_stderr = ""
    restore_exit_code = 0
    restore_timed_out = False
    if generation_elapsed >= timeout_seconds:
        restore_exit_code = 124
        restore_stderr = "generation exhausted prebuild bound before restore"
        restore_timed_out = True
        restore_ownership: dict[str, Any] = {
            "ownershipMode": "not-started", "jobHandle": 0,
            "jobAssignedBeforeResume": False, "capturedProcesses": {},
        }
        restore_process_id = 0
    else:
        restore_completed_proc, restore_process_id, restore_ownership = runner(
            restore_command, cwd=ROOT, env=env,
            timeout_seconds=max(0.01, timeout_seconds - generation_elapsed),
        )
        restore_exit_code = restore_completed_proc.returncode
        restore_stdout = restore_completed_proc.stdout
        restore_stderr = restore_completed_proc.stderr
        restore_timed_out = restore_exit_code == 124
    restore_completed = dt.datetime.now(dt.timezone.utc)
    restore_cleanup = dict(compiler_cleanup(restore_ownership))
    assets_path = runner_root / "obj" / "project.assets.json"
    restore_ok = (
        not restore_timed_out
        and restore_exit_code == 0
        and assets_path.is_file()
        and _compiler_cleanup_receipt_complete(
            restore_cleanup,
            build_process_id=restore_process_id,
            build_invocation_count=1 if restore_process_id else 0,
        )
    )
    generation_completed = dt.datetime.now(dt.timezone.utc)

    command = [
        "dotnet", "build", str(project), "--configuration", "Release", "--nologo",
        "--no-restore", "-p:UseSharedCompilation=false", "-nodeReuse:false",
    ]
    build_started = dt.datetime.now(dt.timezone.utc)
    build_invocation_count = 0
    elapsed_before_build = (build_started - generation_started).total_seconds()
    if not restore_ok or elapsed_before_build >= timeout_seconds:
        completed = subprocess.CompletedProcess(
            command,
            124 if restore_timed_out or elapsed_before_build >= timeout_seconds else 1,
            restore_stdout,
            restore_stderr or "generation-phase restore failed; refusing --no-restore build",
        )
        build_process_id = 0
        build_ownership = {
            "ownershipMode": "not-started", "jobHandle": 0,
            "jobAssignedBeforeResume": False, "capturedProcesses": {},
        }
    else:
        completed, build_process_id, build_ownership = runner(
            command, cwd=ROOT, env=env,
            timeout_seconds=max(0.01, timeout_seconds - elapsed_before_build),
        )
        build_invocation_count = 1
    timed_out = completed.returncode == 124 or restore_timed_out
    build_completed = dt.datetime.now(dt.timezone.utc)
    cleanup = dict(compiler_cleanup(build_ownership))
    cleanup_completed = dt.datetime.now(dt.timezone.utc)
    completed_at = dt.datetime.now(dt.timezone.utc)
    total_elapsed_seconds = (completed_at - generation_started).total_seconds()
    output_root = runner_root / "bin" / "Release" / "net10.0"
    outputs = {
        "dllPath": output_root / "LiveSafeCopySmoke.dll",
        "runtimeConfigPath": output_root / "LiveSafeCopySmoke.runtimeconfig.json",
        "depsPath": output_root / "LiveSafeCopySmoke.deps.json",
    }
    passed = (
        restore_ok
        and not timed_out
        and total_elapsed_seconds <= 150
        and completed.returncode == 0
        and build_invocation_count == 1
        and _compiler_cleanup_receipt_complete(
            cleanup, build_process_id=build_process_id,
            build_invocation_count=build_invocation_count,
        )
        and all(path.is_file() for path in outputs.values())
    )
    receipt: dict[str, Any] = {
        "schemaVersion": "battleengine-walker-runner-private-build-receipt.v1",
        "passed": passed,
        "safetyBoundSeconds": 150,
        "safetyBoundBasis": "conservative relative to observed combined 88.29-second generation/build/profile interval; compile duration was not separately measured",
        "startedAtUtc": generation_started.isoformat(), "completedAtUtc": completed_at.isoformat(),
        "totalElapsedSeconds": total_elapsed_seconds,
        "phaseTimestampsUtc": {
            "generationStarted": generation_started.isoformat(),
            "generationCompleted": generation_completed.isoformat(),
            "buildStarted": build_started.isoformat(),
            "buildCompleted": build_completed.isoformat(),
            "compilerCleanupCompleted": cleanup_completed.isoformat(),
        },
        "generationRestore": {
            "command": restore_command,
            "exitCode": restore_exit_code,
            "timedOut": restore_timed_out,
            "processId": restore_process_id,
            "startedAtUtc": restore_started.isoformat(),
            "completedAtUtc": restore_completed.isoformat(),
            "assetsPathPresent": assets_path.is_file(),
            "compilerCleanup": restore_cleanup,
            "stdout": restore_stdout,
            "stderr": restore_stderr,
        },
        "command": command, "exitCode": completed.returncode,
        "buildProcessId": build_process_id,
        "buildInvocationCount": build_invocation_count, "timedOut": timed_out,
        "sdkIdentity": sdk_identity,
        "sourcePath": str(program), "sourceSha256": file_sha256(program),
        "projectPath": str(project), "projectSha256": file_sha256(project),
        "dependencyInputs": [
            {"path": str(path), "sha256": file_sha256(path)} for path in dependency_paths
        ],
        "compilerOwnedProcessCount": cleanup.get("ownedProcessCount", -1),
        "compilerCleanup": cleanup,
        "stdout": completed.stdout, "stderr": completed.stderr,
        "runnerOutputFiles": [
            {
                "relativePath": path.relative_to(output_root).as_posix(),
                "sha256": file_sha256(path),
            }
            for path in sorted(output_root.rglob("*")) if path.is_file()
        ] if output_root.is_dir() else [],
    }
    for key, path in outputs.items():
        receipt[key] = str(path)
        receipt[key.replace("Path", "Sha256")] = file_sha256(path) if path.is_file() else ""
    receipt_path = pair_root / "runner-build-receipt.json"
    receipt["receiptPath"] = str(receipt_path)
    write_new_private_text(receipt_path, json.dumps(receipt, indent=2) + "\n", pair_root)
    receipt["receiptSha256"] = file_sha256(receipt_path)
    return receipt


def execute_prebuilt_walker_runner(
    runner_dll: Path,
    expected_sha256: str,
    env: Mapping[str, str],
    *,
    process_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    if not runner_dll.is_file() or file_sha256(runner_dll) != expected_sha256:
        raise ValueError("prebuilt walker runner DLL hash binding failed")
    command = ["dotnet", str(runner_dll)]
    return process_runner(command, cwd=ROOT, text=True, capture_output=True, check=False, env=dict(env))


def validate_prebuilt_walker_build_row(
    row: Mapping[str, Any], receipt_path: Path, receipt_sha256: str,
) -> None:
    if row.get("passed") is not True or row.get("buildInvocationCount") != 1:
        raise ValueError("walker build receipt is not a single passing prebuild")
    cleanup = row.get("compilerCleanup")
    if (row.get("compilerOwnedProcessCount") != 0 or not isinstance(cleanup, dict)
            or not _compiler_cleanup_receipt_complete(
                cleanup,
                build_process_id=int(row.get("buildProcessId", 0)),
                build_invocation_count=int(row.get("buildInvocationCount", 0)),
            )):
        raise ValueError("walker build descendant cleanup receipt is not zero")
    if row.get("receiptPath") != str(receipt_path) or file_sha256(receipt_path) != receipt_sha256:
        raise ValueError("walker build receipt self-location/hash binding failed")
    for path_key, hash_key in (
        ("sourcePath", "sourceSha256"), ("projectPath", "projectSha256"),
        ("dllPath", "dllSha256"), ("runtimeConfigPath", "runtimeConfigSha256"),
        ("depsPath", "depsSha256"),
    ):
        path = Path(str(row.get(path_key, "")))
        if (not path.is_file() or has_reparse_or_symlink_ancestor(path)
                or file_sha256(path) != row.get(hash_key)):
            raise ValueError(f"walker build receipt {path_key} drifted")
    sdk = row.get("sdkIdentity")
    if not isinstance(sdk, dict):
        raise ValueError("walker build SDK identity is absent")
    sdk_host = Path(str(sdk.get("hostPath", "")))
    if not sdk_host.is_file() or file_sha256(sdk_host) != sdk.get("hostSha256"):
        raise ValueError("walker build SDK host identity drifted")
    dependencies = row.get("dependencyInputs")
    if not isinstance(dependencies, list) or not dependencies:
        raise ValueError("walker build dependency receipt is absent")
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            raise ValueError("walker build dependency receipt is malformed")
        path = Path(str(dependency.get("path", "")))
        if not path.is_file() or file_sha256(path) != dependency.get("sha256"):
            raise ValueError("walker build dependency input drifted")
    output_root = Path(str(row["dllPath"])).parent
    expected = {
        str(output["relativePath"]): str(output["sha256"])
        for output in row.get("runnerOutputFiles", []) if isinstance(output, dict)
    }
    actual = {
        path.relative_to(output_root).as_posix(): file_sha256(path)
        for path in output_root.rglob("*") if path.is_file()
    }
    if not expected or expected != actual:
        raise ValueError("walker build output set drifted")


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def configured_approved_external_artifact_base_parents() -> tuple[Path, ...]:
    configured = tuple(
        Path(value.strip().strip('"'))
        for value in os.environ.get(APPROVED_ARTIFACT_BASE_PARENTS_ENV, "").split(os.pathsep)
        if value.strip()
    )
    return APPROVED_EXTERNAL_ARTIFACT_BASE_PARENTS + configured


def is_approved_external_artifact_parent(parent: Path) -> bool:
    return any(is_same_or_under(parent, approved) for approved in configured_approved_external_artifact_base_parents())


def paths_overlap(left: Path, right: Path) -> bool:
    return is_same_or_under(left, right) or is_same_or_under(right, left)


def has_reparse_or_symlink_ancestor(path: Path) -> bool:
    current = path.absolute()
    while True:
        if current.exists():
            try:
                info = current.lstat()
            except OSError:
                return True
            if current.is_symlink() or (getattr(info, "st_file_attributes", 0) & REPARSE_POINT_FLAG):
                return True
        parent = current.parent
        if parent == current:
            return False
        current = parent


OBSERVER_SIMPLE_COMMAND_RE = re.compile(
    r"^(?:"
    r"\.echo [A-Za-z0-9 .:/_=+\-()[\]]+"
    r"|vertarget"
    r"|lm m [A-Za-z0-9_.$-]+"
    r"|u [0-9A-Fa-f`]+ L[0-9A-Fa-f]+"
    r"|dd [0-9A-Fa-fx`@()+\-]+(?: L[0-9A-Fa-fx]+)?"
    r"|g"
    r")$"
)
OBSERVER_BREAKPOINT_RE = re.compile(r'^bp(?: /1)? [0-9A-Fa-f]{8} "(?P<body>.*)"$')
OBSERVER_PRINTF_BODY_RE = re.compile(r'^\.printf "[^"]*"(?:, [^;"]+)?; g$')
OBSERVER_IF_PRINTF_BODY_RE = re.compile(r'^\.if \([^;"]+\) \{ \.printf "[^"]*"(?:, [^;"]+)? \}; g$')
OBSERVER_BREAKPOINT_DISALLOWED_RE = re.compile(
    r"(?i)(?:"
    r"\.shell|\.dump|\.writemem|"
    r"(?:^|[;\s])(?:r|gu|ed|eb|ew|eq|ea|eza|f|m|q|qq|qd|g-)\b"
    r")"
)


def is_observer_breakpoint_command(line: str) -> bool:
    match = OBSERVER_BREAKPOINT_RE.match(line)
    if not match:
        return False
    body = match.group("body")
    if OBSERVER_BREAKPOINT_DISALLOWED_RE.search(body):
        return False
    normalized_body = body.replace(r"\"", '"')
    return bool(OBSERVER_PRINTF_BODY_RE.match(normalized_body) or OBSERVER_IF_PRINTF_BODY_RE.match(normalized_body))


def validate_cdb_observer_command_file(command_file: Path) -> None:
    text = command_file.read_text(encoding="utf-8-sig")
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("*") or line.startswith("#"):
            continue
        if OBSERVER_SIMPLE_COMMAND_RE.match(line) or is_observer_breakpoint_command(line):
            continue
        raise ValueError(
            f"CDB observer command file contains unsupported command on line {line_number}: {raw_line!r}. "
            "Only tracked observer-style .echo/vertarget/lm/u/dd/g commands and bp[/1] print-and-continue commands are allowed by this live smoke helper."
        )


def main() -> int:
    args = parse_args()
    if args.arm_live_bea != ARM_PHRASE:
        print(f"Refusing to launch BEA. Pass --arm-live-bea \"{ARM_PHRASE}\".", file=sys.stderr)
        return 2
    try:
        protocol = validate_runtime_protocol(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    morph_canary_mode = protocol.runtime_protocol == MORPH_CANARY_RUNTIME_PROTOCOL
    walker_trajectory_mode = protocol.runtime_protocol == WALKER_TRAJECTORY_RUNTIME_PROTOCOL
    private_runtime_mode = morph_canary_mode or walker_trajectory_mode

    source_root = Path(args.source_root).resolve()
    exe_override = Path(args.exe_override).resolve() if args.exe_override else source_root / "BEA.exe.original.backup"
    if not source_root.is_dir():
        print(f"Source root does not exist: {source_root}", file=sys.stderr)
        return 2
    if not exe_override.is_file():
        print(f"Executable override does not exist: {exe_override}", file=sys.stderr)
        return 2
    if args.timeout_seconds < 1 or args.timeout_seconds > 120:
        print("--timeout-seconds must be between 1 and 120.", file=sys.stderr)
        return 2
    if protocol.capture_count < 0 or protocol.capture_count > 10 or (not private_runtime_mode and protocol.capture_count < 1):
        print("--capture-count must be 0 for private measurement protocols or between 1 and 10 for default mode.", file=sys.stderr)
        return 2
    if args.pre_input_capture_count < 0 or args.pre_input_capture_count > 3:
        print("--pre-input-capture-count must be between 0 and 3.", file=sys.stderr)
        return 2
    if args.capture_interval_seconds < 0 or args.capture_interval_seconds > 15:
        print("--capture-interval-seconds must be between 0 and 15.", file=sys.stderr)
        return 2
    if args.post_window_delay_seconds < 0 or args.post_window_delay_seconds > 30:
        print("--post-window-delay-seconds must be between 0 and 30.", file=sys.stderr)
        return 2
    if args.input_step_delay_ms < 0 or args.input_step_delay_ms > 1000:
        print("--input-step-delay-ms must be between 0 and 1000.", file=sys.stderr)
        return 2
    if args.after_input_capture_delay_ms < 0 or args.after_input_capture_delay_ms > 5000:
        print("--after-input-capture-delay-ms must be between 0 and 5000.", file=sys.stderr)
        return 2
    if args.level_id < 0 or args.level_id > 9999:
        print("--level-id must be 0 for no override or a mission id from 1 to 9999.", file=sys.stderr)
        return 2
    if args.controller_configuration < 0 or args.controller_configuration > 4:
        print("--controller-configuration must be 0 for no override or a preset from 1 to 4.", file=sys.stderr)
        return 2
    if args.launch_nomusic and args.launch_nosound:
        print("Use only one mute-control launch argument: --launch-nomusic or --launch-nosound.", file=sys.stderr)
        return 2
    if args.persist_controller_config_in_options and args.controller_configuration == 0:
        print("--persist-controller-config-in-options requires --controller-configuration 1..4.", file=sys.stderr)
        return 2
    qe_lever_count = sum(
        1
        for enabled in (
            args.bind_forward_qe_for_input_isolation,
            args.bind_fire_qe_for_weapon_handoff,
            args.bind_look_down_qe_for_config2_forward_discovery,
            bool(args.bind_config2_census_row_qe),
        )
        if enabled
    )
    if qe_lever_count > 1:
        print("Use only one Q/E keybind proof lever per live run.", file=sys.stderr)
        return 2
    if args.bind_look_down_qe_for_config2_forward_discovery and args.controller_configuration != 2:
        print("--bind-look-down-qe-for-config2-forward-discovery requires --controller-configuration 2.", file=sys.stderr)
        return 2
    if args.bind_config2_census_row_qe and args.controller_configuration != 2:
        print("--bind-config2-census-row-qe requires --controller-configuration 2.", file=sys.stderr)
        return 2
    if len(protocol.input_sequences) > 8:
        print("--input-sequence may be repeated at most 8 times.", file=sys.stderr)
        return 2
    if args.allow_background_window_messages and args.arm_background_window_messages != BACKGROUND_WINDOW_MESSAGES_ARM_PHRASE:
        print(
            f"Refusing background-window input without --arm-background-window-messages \"{BACKGROUND_WINDOW_MESSAGES_ARM_PHRASE}\".",
            file=sys.stderr,
        )
        return 2
    if args.arm_background_window_messages and not args.allow_background_window_messages:
        print("--arm-background-window-messages requires --allow-background-window-messages.", file=sys.stderr)
        return 2
    if args.enable_cdb_observer and args.arm_cdb_observer != CDB_OBSERVER_ARM_PHRASE:
        print(
            f"Refusing CDB observer attach without --arm-cdb-observer \"{CDB_OBSERVER_ARM_PHRASE}\".",
            file=sys.stderr,
        )
        return 2
    if args.arm_cdb_observer and not args.enable_cdb_observer:
        print("--arm-cdb-observer requires --enable-cdb-observer.", file=sys.stderr)
        return 2
    if args.cdb_log_ready_timeout_ms < 1000 or args.cdb_log_ready_timeout_ms > 30000:
        print("--cdb-log-ready-timeout-ms must be between 1000 and 30000.", file=sys.stderr)
        return 2
    if args.cdb_post_attach_wait_seconds < 0 or args.cdb_post_attach_wait_seconds > 15:
        print("--cdb-post-attach-wait-seconds must be between 0 and 15.", file=sys.stderr)
        return 2
    for sequence in protocol.input_sequences:
        actions = [part.strip() for part in sequence.replace("\r", ",").replace("\n", ",").replace(";", ",").split(",") if part.strip()]
        if not actions or len(actions) > 32:
            print("Each --input-sequence must contain between 1 and 32 actions.", file=sys.stderr)
            return 2

    patch_keys = list(protocol.patch_keys)
    extra_patch_keys = [key.strip() for key in (args.extra_patch_key or []) if key and key.strip()]
    allowed_extra_keys = STABLE_EXTRA_PATCH_KEYS | EXPERIMENTAL_EXTRA_PATCH_KEYS
    unexpected_extra_keys = sorted(set(extra_patch_keys) - allowed_extra_keys)
    if unexpected_extra_keys:
        print(f"Unsupported --extra-patch-key for this live smoke helper: {', '.join(unexpected_extra_keys)}", file=sys.stderr)
        return 2
    experimental_requested = sorted(set(extra_patch_keys) & EXPERIMENTAL_EXTRA_PATCH_KEYS)
    if experimental_requested and args.arm_experimental_patch_key != EXPERIMENTAL_PATCH_ARM_PHRASE:
        print(
            f"Refusing experimental live-smoke patch keys ({', '.join(experimental_requested)}) without --arm-experimental-patch-key \"{EXPERIMENTAL_PATCH_ARM_PHRASE}\".",
            file=sys.stderr,
        )
        return 2
    patch_keys = sorted({key.strip() for key in patch_keys if key and key.strip()})
    launch_arguments = list(protocol.launch_arguments)
    music_swap_preset_id = args.music_swap_preset_id.strip()
    music_target = args.music_target
    music_replacement = Path(args.music_replacement)
    stage_music_replacement = args.stage_music_replacement or bool(music_swap_preset_id)
    if private_runtime_mode:
        stage_music_replacement = protocol.stage_music_replacement
    if music_swap_preset_id:
        music_target, preset_replacement = MUSIC_SWAP_PRESETS[music_swap_preset_id]
        music_replacement = source_root / "data" / "Music" / preset_replacement
    if not music_replacement.is_absolute():
        music_replacement = source_root / "data" / "Music" / args.music_replacement

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    artifact_root_raw, profiles_root_raw, external_artifact_armed, env_external_artifact_armed, artifact_parent_raw = select_artifact_root_inputs(args, stamp)
    if has_reparse_or_symlink_ancestor(artifact_root_raw) or has_reparse_or_symlink_ancestor(profiles_root_raw):
        print("Refusing artifact/profile roots that include a reparse/symlink path component.", file=sys.stderr)
        return 2
    artifact_root = artifact_root_raw.resolve()
    profiles_root = profiles_root_raw.resolve()
    default_artifact_parent = (ROOT / "subagents" / "winui-safe-copy-live-runtime").resolve()
    if env_external_artifact_armed:
        artifact_parent = artifact_parent_raw.resolve()
        if not is_approved_external_artifact_parent(artifact_parent):
            approved_roots = configured_approved_external_artifact_base_parents()
            approved_roots_display = ", ".join(str(parent) for parent in approved_roots) or f"none configured via {APPROVED_ARTIFACT_BASE_PARENTS_ENV}"
            print(
                f"Refusing {ARTIFACT_BASE_ENV} outside configured approved private artifact parent(s): {approved_roots_display}. Use explicit --artifact-root with --arm-external-artifact-root for other one-off roots.",
                file=sys.stderr,
            )
            return 2
    if not is_same_or_under(artifact_root, default_artifact_parent) and not external_artifact_armed:
        print(
            f"Refusing external artifact root without --arm-external-artifact-root \"{EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE}\" or {ARTIFACT_BASE_ARM_ENV}=\"{EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE}\".",
            file=sys.stderr,
        )
        return 2
    if (
        not is_same_or_under(profiles_root, default_artifact_parent)
        and not is_same_or_under(profiles_root, artifact_root)
        and args.arm_external_profiles_root != EXTERNAL_PROFILES_ROOT_ARM_PHRASE
    ):
        print(
            f"Refusing external profiles root without --arm-external-profiles-root \"{EXTERNAL_PROFILES_ROOT_ARM_PHRASE}\".",
            file=sys.stderr,
        )
        return 2
    if paths_overlap(artifact_root, source_root) or paths_overlap(profiles_root, source_root):
        print("Refusing artifact/profile roots that overlap the source game root.", file=sys.stderr)
        return 2
    canary_app_config_root = None
    if private_runtime_mode:
        try:
            if morph_canary_mode:
                canary_app_config_root = resolve_morph_canary_app_config_root(
                    artifact_root,
                    profiles_root,
                )
                validate_morph_canary_profile_path_budget(profiles_root, protocol.canary_role)
            else:
                canary_app_config_root = resolve_walker_app_config_root(
                    artifact_root,
                    profiles_root,
                )
            validate_morph_canary_control_inputs(args, artifact_root)
            artifact_root = create_fresh_canary_artifact_root(artifact_root_raw)
            profiles_root = profiles_root_raw.resolve()
        except (OSError, ValueError) as exc:
            print(f"Refusing non-fresh canary artifact root: {exc}", file=sys.stderr)
            return 2
    cdb_command_file_raw = Path(args.cdb_command_file)
    cdb_command_file = cdb_command_file_raw if cdb_command_file_raw.is_absolute() else (ROOT / cdb_command_file_raw)
    cdb_command_file = cdb_command_file.resolve()
    runtime_probe_root = (ROOT / "tools" / "runtime-probes").resolve()
    if protocol.cdb_observer_enabled and not morph_canary_mode:
        if not cdb_command_file.is_file():
            print(f"CDB observer command file does not exist: {cdb_command_file}", file=sys.stderr)
            return 2
        if not is_same_or_under(cdb_command_file, runtime_probe_root):
            print("Refusing CDB observer command file outside tracked tools/runtime-probes.", file=sys.stderr)
            return 2
        try:
            validate_cdb_observer_command_file(cdb_command_file)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2

    runner_root_raw = artifact_root_raw / "runner"
    runner_root = artifact_root / "runner"
    artifact_json = artifact_root / (
        "battleengine-morph-identity-canary-private-run.json"
        if morph_canary_mode
        else "walker-trajectory-attempt-closeout.json"
        if walker_trajectory_mode
        else "live-safe-copy-runtime-smoke.json"
    )
    capture_dir = artifact_root / "capture"
    capture_png = capture_dir / "safe-copy-frame.png"
    capture_json = capture_dir / "safe-copy-frame.json"
    cdb_log_path = artifact_root / "cdb" / "windbg.log"
    powershell = shutil.which("pwsh") or shutil.which("powershell") or "powershell"

    rendered_canary_command = None
    if morph_canary_mode:
        try:
            morph_canary = load_morph_canary_module()
            cdb_command_file = artifact_root / "cdb" / "battleengine-morph-identity-canary.cdb.txt"
            create_fresh_canary_directory(cdb_command_file.parent, artifact_root)
            rendered_canary_command = morph_canary.render_private_command(
                exe_override,
                morph_canary.DEFAULT_TEMPLATE,
            )
            validate_canary_digest_set(
                rendered_canary_command.executable_sha256,
                override_before=file_sha256(exe_override),
            )
            write_new_private_bytes(
                cdb_command_file,
                rendered_canary_command.text.encode("ascii"),
                artifact_root,
            )
            create_fresh_canary_directory(artifact_root / "input", artifact_root)
            morph_canary.validate_private_command(
                cdb_command_file,
                exe_override,
                morph_canary.DEFAULT_TEMPLATE,
            )
        except (OSError, ValueError) as exc:
            print(f"Could not materialize locked morph canary CDB command: {exc}", file=sys.stderr)
            return 2

    prebuilt_runner_dll = Path(args.walker_prebuilt_runner_dll) if args.walker_prebuilt_runner_dll else None
    if walker_trajectory_mode and prebuilt_runner_dll is None:
        print("Walker trajectory attempts require the pair-prebuilt runner DLL.", file=sys.stderr)
        return 2
    if prebuilt_runner_dll is not None:
        if not prebuilt_runner_dll.is_absolute() or has_reparse_or_symlink_ancestor(prebuilt_runner_dll):
            print("Refusing a relative or reparse-routed prebuilt runner DLL.", file=sys.stderr)
            return 2
        prebuilt_runner_dll = prebuilt_runner_dll.resolve()
        if (not prebuilt_runner_dll.is_file() or
                file_sha256(prebuilt_runner_dll) != args.expected_walker_prebuilt_runner_sha256):
            print("Prebuilt walker runner DLL hash binding failed.", file=sys.stderr)
            return 2
        build_receipt = Path(args.walker_prebuild_receipt)
        if (not build_receipt.is_absolute() or has_reparse_or_symlink_ancestor(build_receipt)
                or not build_receipt.is_file()
                or file_sha256(build_receipt) != args.expected_walker_prebuild_receipt_sha256):
            print("Prebuilt walker runner build-receipt binding failed.", file=sys.stderr)
            return 2
        try:
            build_row = json.loads(build_receipt.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print("Prebuilt walker runner build receipt is unreadable.", file=sys.stderr)
            return 2
        try:
            validate_prebuilt_walker_build_row(
                build_row, build_receipt, args.expected_walker_prebuild_receipt_sha256
            )
        except ValueError as exc:
            print(f"Prebuilt walker runner build receipt failed revalidation: {exc}", file=sys.stderr)
            return 2
        if (build_row.get("dllPath") != str(prebuilt_runner_dll)
                or build_row.get("dllSha256") != args.expected_walker_prebuilt_runner_sha256):
            print("Prebuilt walker runner build receipt does not bind the requested DLL.", file=sys.stderr)
            return 2
        cooperative_stop_file = Path(args.walker_cooperative_stop_file)
        if (not cooperative_stop_file.is_absolute()
                or has_reparse_or_symlink_ancestor(cooperative_stop_file)
                or cooperative_stop_file.exists()
                or cooperative_stop_file.parent.resolve() != build_receipt.parent.resolve()):
            print("Walker cooperative stop file is not a fresh pair-root target.", file=sys.stderr)
            return 2
    if prebuilt_runner_dll is None and runner_root.exists():
        if private_runtime_mode:
            print(f"Refusing pre-existing canary runner directory: {runner_root}", file=sys.stderr)
            return 2
        if has_reparse_or_symlink_ancestor(runner_root_raw) or has_reparse_or_symlink_ancestor(runner_root):
            print(f"Refusing to remove runner directory through a reparse/symlink path: {runner_root}", file=sys.stderr)
            return 2
        marker = runner_root / RUNNER_MARKER
        if not marker.is_file():
            print(f"Refusing to remove existing non-tool-owned runner directory: {runner_root}", file=sys.stderr)
            return 2
        shutil.rmtree(runner_root)
    project = None if prebuilt_runner_dll is not None else write_runner(
        runner_root, create_new=private_runtime_mode
    )

    env = os.environ.copy()
    env["ONSLAUGHT_LIVE_SOURCE_ROOT"] = str(source_root)
    env["ONSLAUGHT_LIVE_EXE_OVERRIDE"] = str(exe_override)
    env["ONSLAUGHT_LIVE_PROFILES_ROOT"] = str(profiles_root)
    if canary_app_config_root is not None:
        env["ONSLAUGHT_APP_CONFIG_ROOT"] = str(canary_app_config_root)
    env["ONSLAUGHT_LIVE_ARTIFACT_JSON"] = str(artifact_json)
    env["ONSLAUGHT_LIVE_CAPTURE_SCRIPT"] = str(ROOT / "tools" / "capture_game_window.ps1")
    env["ONSLAUGHT_LIVE_INPUT_SCRIPT"] = str(ROOT / "tools" / "send_game_window_input.ps1")
    env["ONSLAUGHT_LIVE_CAPTURE_DIR"] = str(capture_dir)
    env["ONSLAUGHT_LIVE_CAPTURE_PNG"] = str(capture_png)
    env["ONSLAUGHT_LIVE_CAPTURE_JSON"] = str(capture_json)
    env["ONSLAUGHT_LIVE_POWERSHELL"] = powershell
    env["ONSLAUGHT_LIVE_TIMEOUT_SECONDS"] = str(args.timeout_seconds)
    env["ONSLAUGHT_LIVE_RUNTIME_PROTOCOL"] = protocol.runtime_protocol
    env["ONSLAUGHT_LIVE_CANARY_ROLE"] = protocol.canary_role
    env["ONSLAUGHT_LIVE_CAPTURE_COUNT"] = str(protocol.capture_count)
    env["ONSLAUGHT_LIVE_PRE_INPUT_CAPTURE_COUNT"] = str(args.pre_input_capture_count)
    env["ONSLAUGHT_LIVE_CAPTURE_AFTER_EACH_INPUT_SEQUENCE"] = "1" if args.capture_after_each_input_sequence else "0"
    env["ONSLAUGHT_LIVE_AFTER_INPUT_CAPTURE_DELAY_MS"] = str(args.after_input_capture_delay_ms)
    env["ONSLAUGHT_LIVE_CAPTURE_INTERVAL_SECONDS"] = str(args.capture_interval_seconds)
    env["ONSLAUGHT_LIVE_POST_WINDOW_DELAY_SECONDS"] = str(args.post_window_delay_seconds)
    env["ONSLAUGHT_LIVE_INPUT_SEQUENCES_JSON"] = json.dumps(protocol.input_sequences)
    env["ONSLAUGHT_LIVE_ALLOW_BACKGROUND_WINDOW_MESSAGES"] = "1" if protocol.allow_background_window_messages else "0"
    env["ONSLAUGHT_LIVE_FOCUS_BEFORE_PRE_INPUT_CAPTURE"] = "1" if args.focus_before_pre_input_capture else "0"
    env["ONSLAUGHT_LIVE_BACKGROUND_WINDOW_MESSAGES_ARM"] = args.arm_background_window_messages
    env["ONSLAUGHT_LIVE_CDB_OBSERVER_ENABLED"] = "1" if protocol.cdb_observer_enabled else "0"
    env["ONSLAUGHT_LIVE_CDB_START_SCRIPT"] = str(ROOT / "tools" / "start_cdb_server.ps1")
    env["ONSLAUGHT_LIVE_CDB_COMMAND_FILE"] = str(cdb_command_file)
    env["ONSLAUGHT_LIVE_CDB_LOG_PATH"] = str(cdb_log_path)
    env["ONSLAUGHT_LIVE_CDB_LOG_READY_TIMEOUT_MS"] = str(protocol.cdb_log_ready_timeout_ms)
    env["ONSLAUGHT_LIVE_CDB_POST_ATTACH_WAIT_SECONDS"] = str(args.cdb_post_attach_wait_seconds)
    env["ONSLAUGHT_LIVE_CDB_ATTACH_PHASE"] = protocol.cdb_attach_phase
    env["ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON"] = json.dumps(launch_arguments)
    env["ONSLAUGHT_LIVE_INPUT_STEP_DELAY_MS"] = str(protocol.input_step_delay_ms)
    env["ONSLAUGHT_LIVE_PATCH_KEYS_JSON"] = json.dumps(patch_keys)
    env["ONSLAUGHT_LIVE_PROFILE_PRESET_ID"] = args.profile_preset_id.strip()
    env["ONSLAUGHT_LIVE_STAGE_MUSIC_REPLACEMENT"] = "1" if stage_music_replacement else "0"
    env["ONSLAUGHT_LIVE_MUSIC_SWAP_PRESET_ID"] = music_swap_preset_id
    env["ONSLAUGHT_LIVE_SHARPEN_MOUSE_LOOK"] = "1" if args.sharpen_mouse_look else "0"
    env["ONSLAUGHT_LIVE_BIND_FORWARD_QE_FOR_INPUT_ISOLATION"] = "1" if args.bind_forward_qe_for_input_isolation else "0"
    env["ONSLAUGHT_LIVE_BIND_FIRE_QE_FOR_WEAPON_HANDOFF"] = "1" if args.bind_fire_qe_for_weapon_handoff else "0"
    env["ONSLAUGHT_LIVE_BIND_LOOK_DOWN_QE_FOR_CONFIG2_FORWARD_DISCOVERY"] = "1" if args.bind_look_down_qe_for_config2_forward_discovery else "0"
    env["ONSLAUGHT_LIVE_BIND_CONFIG2_CENSUS_ROW_QE"] = args.bind_config2_census_row_qe.strip()
    env["ONSLAUGHT_LIVE_PERSISTED_CONTROLLER_CONFIG"] = str(args.controller_configuration if args.persist_controller_config_in_options else 0)
    env["ONSLAUGHT_LIVE_MUSIC_TARGET"] = music_target
    env["ONSLAUGHT_LIVE_MUSIC_REPLACEMENT"] = str(music_replacement.resolve())
    env["ONSLAUGHT_LIVE_APPLY_WINDOWED_COMPATIBILITY_PATCH"] = "1" if protocol.apply_windowed_compatibility_patch else "0"
    env["ONSLAUGHT_LIVE_RUNTIME_RECEIPT_PATH"] = str(artifact_root / "runtime-process-receipt.json")
    env["ONSLAUGHT_LIVE_RUNTIME_IDENTITY_MODULE"] = str(ROOT / "tools" / "runtime_process_identity.psm1")
    env["ONSLAUGHT_LIVE_CDB_REQUIRED_MARKER"] = protocol.required_cdb_log_marker
    if walker_trajectory_mode:
        walker_adapter = (ROOT / "tools" / "run_battleengine_walker_trajectory_measurement.py").resolve()
        env["ONSLAUGHT_LIVE_WALKER_AUTHORIZED_ROOT"] = str(artifact_root)
        env["ONSLAUGHT_LIVE_WALKER_ADAPTER_PATH"] = str(walker_adapter)
        env["ONSLAUGHT_LIVE_WALKER_ADAPTER_SHA256"] = file_sha256(walker_adapter)
        env["ONSLAUGHT_LIVE_WALKER_ATTEMPT"] = str(args.walker_attempt)
        env["ONSLAUGHT_LIVE_WALKER_DEADLINE_SECONDS"] = str(args.walker_deadline_seconds)
        env["ONSLAUGHT_LIVE_WALKER_ATTEMPT_BUDGET_SECONDS"] = str(args.walker_attempt_budget_seconds)
        env["ONSLAUGHT_LIVE_WALKER_COOPERATIVE_STOP_FILE"] = args.walker_cooperative_stop_file
        env["ONSLAUGHT_LIVE_PYTHON_EXE"] = sys.executable
    if rendered_canary_command is not None:
        morph_canary = load_morph_canary_module()
        env["ONSLAUGHT_LIVE_CDB_COMMAND_SHA256"] = rendered_canary_command.sha256
        env["ONSLAUGHT_LIVE_CDB_TEMPLATE_PATH"] = str(morph_canary.DEFAULT_TEMPLATE)
        env["ONSLAUGHT_LIVE_CDB_TEMPLATE_SHA256"] = rendered_canary_command.template_sha256
        env["ONSLAUGHT_LIVE_CANONICAL_EXECUTABLE_SHA256"] = rendered_canary_command.executable_sha256
        env["ONSLAUGHT_LIVE_CDB_FINGERPRINTS_JSON"] = json.dumps(
            [
                {
                    "event": target.event,
                    "rva": target.rva,
                    "length": target.size,
                    "sha256": target.sha256,
                }
                for target in rendered_canary_command.targets
            ]
        )

    if prebuilt_runner_dll is not None:
        result = execute_prebuilt_walker_runner(
            prebuilt_runner_dll, args.expected_walker_prebuilt_runner_sha256, env
        )
    else:
        command = ["dotnet", "run", "--project", str(project), "--nologo"]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=env)
    if private_runtime_mode:
        write_new_private_text(artifact_root / "dotnet-stdout.log", result.stdout, artifact_root)
        write_new_private_text(artifact_root / "dotnet-stderr.log", result.stderr, artifact_root)
    else:
        (artifact_root / "dotnet-stdout.log").write_text(result.stdout, encoding="utf-8")
        (artifact_root / "dotnet-stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print(json.dumps({"artifact": str(artifact_json), "profilesRoot": str(profiles_root)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
