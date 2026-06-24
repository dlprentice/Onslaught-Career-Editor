#!/usr/bin/env python3
"""Opt-in live playable-copied-game launch/capture/stop proof for the WinUI/AppCore patch path."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
ARM_PHRASE = "LAUNCH SAFE COPY BEA"
EXPERIMENTAL_PATCH_ARM_PHRASE = "ALLOW EXPERIMENTAL LIVE SMOKE PATCH"
BACKGROUND_WINDOW_MESSAGES_ARM_PHRASE = "ALLOW BACKGROUND BEA WINDOW MESSAGES"
EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE = "ALLOW EXTERNAL LIVE SMOKE ARTIFACT ROOT"
EXTERNAL_PROFILES_ROOT_ARM_PHRASE = "ALLOW EXTERNAL LIVE SMOKE PROFILES ROOT"
ARTIFACT_BASE_ENV = "ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE"
ARTIFACT_BASE_ARM_ENV = "ONSLAUGHT_LIVE_RUNTIME_ARTIFACT_BASE_ARM"
# Env-selected default artifact roots are intentionally code-pinned. Other
# one-off external roots must use --artifact-root plus the explicit CLI arm.
APPROVED_EXTERNAL_ARTIFACT_BASE_PARENTS = (Path(r"G:\OnslaughtRuntimeProofArchive"),)
CDB_OBSERVER_ARM_PHRASE = "ATTACH CDB TO SAFE COPY BEA"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
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
    return parser.parse_args()


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


def select_artifact_root_inputs(args: argparse.Namespace, stamp: str) -> tuple[Path, Path, bool, bool, Path]:
    default_artifact_parent_raw = ROOT / "subagents" / "winui-safe-copy-live-runtime"
    artifact_base_env = os.environ.get(ARTIFACT_BASE_ENV, "").strip()
    artifact_base_arm_env = os.environ.get(ARTIFACT_BASE_ARM_ENV, "").strip()
    explicit_artifact_root = bool(args.artifact_root)
    artifact_parent_raw = Path(artifact_base_env) if artifact_base_env else default_artifact_parent_raw
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
        cli_external_artifact_armed or env_external_artifact_armed,
        env_external_artifact_armed,
        artifact_parent_raw,
    )


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def write_runner(runner_root: Path) -> Path:
    runner_root.mkdir(parents=True, exist_ok=True)
    (runner_root / RUNNER_MARKER).write_text("tool-owned runner scratch\n", encoding="utf-8")
    appcore = ROOT / "OnslaughtCareerEditor.AppCore" / "OnslaughtCareerEditor.AppCore.csproj"
    project = runner_root / "LiveSafeCopySmoke.csproj"
    project.write_text(
        f"""<Project Sdk=\"Microsoft.NET.Sdk\">
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
""",
        encoding="utf-8",
    )
    program = runner_root / "Program.cs"
    program.write_text(
        r"""
using System.Diagnostics;
using System.Security.Cryptography;
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
    return element.TryGetProperty(propertyName, out JsonElement property) && property.ValueKind == JsonValueKind.Number && property.TryGetInt32(out int value)
        ? value
        : 0;
}

static bool JsonBool(JsonElement element, string propertyName)
{
    return element.TryGetProperty(propertyName, out JsonElement property) &&
        property.ValueKind is JsonValueKind.True or JsonValueKind.False &&
        property.GetBoolean();
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
    string outputJson)
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
        File.WriteAllText(outputJson, failureJson);
        return JsonSerializer.Deserialize<JsonElement>(failureJson);
    }

    File.WriteAllText(outputJson, stdout);
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
    string outputJson)
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
    File.WriteAllText(outputJson, payloadJson);
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
int captureCount = BoundedIntEnv("ONSLAUGHT_LIVE_CAPTURE_COUNT", 1, 1, 10);
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
            ApplyWindowedCompatibilityPatch: true,
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
    bool cdbObserverSucceeded = !cdbObserverEnabled ||
        (cdbObserverResult.HasValue &&
            cdbObserverResult.Value.TryGetProperty("status", out JsonElement cdbStatusEl) &&
            string.Equals(cdbStatusEl.GetString(), "attached", StringComparison.OrdinalIgnoreCase));
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
""",
        encoding="utf-8",
    )
    return project


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def is_approved_external_artifact_parent(parent: Path) -> bool:
    return any(is_same_or_under(parent, approved) for approved in APPROVED_EXTERNAL_ARTIFACT_BASE_PARENTS)


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
    if args.capture_count < 1 or args.capture_count > 10:
        print("--capture-count must be between 1 and 10.", file=sys.stderr)
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
    if len(args.input_sequence) > 8:
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
    for sequence in args.input_sequence:
        actions = [part.strip() for part in sequence.replace("\r", ",").replace("\n", ",").replace(";", ",").split(",") if part.strip()]
        if not actions or len(actions) > 32:
            print("Each --input-sequence must contain between 1 and 32 actions.", file=sys.stderr)
            return 2

    patch_keys = list(BASE_PATCH_KEYS)
    if args.include_modern_graphics:
        patch_keys.extend(MODERN_GRAPHICS_PATCH_KEYS)
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
    patch_keys.extend(extra_patch_keys)
    patch_keys = sorted({key.strip() for key in patch_keys if key and key.strip()})
    launch_arguments = build_launch_arguments(args)
    music_swap_preset_id = args.music_swap_preset_id.strip()
    music_target = args.music_target
    music_replacement = Path(args.music_replacement)
    stage_music_replacement = args.stage_music_replacement or bool(music_swap_preset_id)
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
            approved_roots = ", ".join(str(parent) for parent in APPROVED_EXTERNAL_ARTIFACT_BASE_PARENTS)
            print(
                f"Refusing {ARTIFACT_BASE_ENV} outside approved private archive parent(s): {approved_roots}. Use explicit --artifact-root with --arm-external-artifact-root for other one-off roots.",
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
    cdb_command_file_raw = Path(args.cdb_command_file)
    cdb_command_file = cdb_command_file_raw if cdb_command_file_raw.is_absolute() else (ROOT / cdb_command_file_raw)
    cdb_command_file = cdb_command_file.resolve()
    runtime_probe_root = (ROOT / "tools" / "runtime-probes").resolve()
    if args.enable_cdb_observer:
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
    artifact_json = artifact_root / "live-safe-copy-runtime-smoke.json"
    capture_dir = artifact_root / "capture"
    capture_png = capture_dir / "safe-copy-frame.png"
    capture_json = capture_dir / "safe-copy-frame.json"
    cdb_log_path = artifact_root / "cdb" / "windbg.log"
    powershell = shutil.which("pwsh") or shutil.which("powershell") or "powershell"

    if runner_root.exists():
        if has_reparse_or_symlink_ancestor(runner_root_raw) or has_reparse_or_symlink_ancestor(runner_root):
            print(f"Refusing to remove runner directory through a reparse/symlink path: {runner_root}", file=sys.stderr)
            return 2
        marker = runner_root / RUNNER_MARKER
        if not marker.is_file():
            print(f"Refusing to remove existing non-tool-owned runner directory: {runner_root}", file=sys.stderr)
            return 2
        shutil.rmtree(runner_root)
    project = write_runner(runner_root)

    env = os.environ.copy()
    env["ONSLAUGHT_LIVE_SOURCE_ROOT"] = str(source_root)
    env["ONSLAUGHT_LIVE_EXE_OVERRIDE"] = str(exe_override)
    env["ONSLAUGHT_LIVE_PROFILES_ROOT"] = str(profiles_root)
    env["ONSLAUGHT_LIVE_ARTIFACT_JSON"] = str(artifact_json)
    env["ONSLAUGHT_LIVE_CAPTURE_SCRIPT"] = str(ROOT / "tools" / "capture_game_window.ps1")
    env["ONSLAUGHT_LIVE_INPUT_SCRIPT"] = str(ROOT / "tools" / "send_game_window_input.ps1")
    env["ONSLAUGHT_LIVE_CAPTURE_DIR"] = str(capture_dir)
    env["ONSLAUGHT_LIVE_CAPTURE_PNG"] = str(capture_png)
    env["ONSLAUGHT_LIVE_CAPTURE_JSON"] = str(capture_json)
    env["ONSLAUGHT_LIVE_POWERSHELL"] = powershell
    env["ONSLAUGHT_LIVE_TIMEOUT_SECONDS"] = str(args.timeout_seconds)
    env["ONSLAUGHT_LIVE_CAPTURE_COUNT"] = str(args.capture_count)
    env["ONSLAUGHT_LIVE_PRE_INPUT_CAPTURE_COUNT"] = str(args.pre_input_capture_count)
    env["ONSLAUGHT_LIVE_CAPTURE_AFTER_EACH_INPUT_SEQUENCE"] = "1" if args.capture_after_each_input_sequence else "0"
    env["ONSLAUGHT_LIVE_AFTER_INPUT_CAPTURE_DELAY_MS"] = str(args.after_input_capture_delay_ms)
    env["ONSLAUGHT_LIVE_CAPTURE_INTERVAL_SECONDS"] = str(args.capture_interval_seconds)
    env["ONSLAUGHT_LIVE_POST_WINDOW_DELAY_SECONDS"] = str(args.post_window_delay_seconds)
    env["ONSLAUGHT_LIVE_INPUT_SEQUENCES_JSON"] = json.dumps(args.input_sequence)
    env["ONSLAUGHT_LIVE_ALLOW_BACKGROUND_WINDOW_MESSAGES"] = "1" if args.allow_background_window_messages else "0"
    env["ONSLAUGHT_LIVE_FOCUS_BEFORE_PRE_INPUT_CAPTURE"] = "1" if args.focus_before_pre_input_capture else "0"
    env["ONSLAUGHT_LIVE_BACKGROUND_WINDOW_MESSAGES_ARM"] = args.arm_background_window_messages
    env["ONSLAUGHT_LIVE_CDB_OBSERVER_ENABLED"] = "1" if args.enable_cdb_observer else "0"
    env["ONSLAUGHT_LIVE_CDB_START_SCRIPT"] = str(ROOT / "tools" / "start_cdb_server.ps1")
    env["ONSLAUGHT_LIVE_CDB_COMMAND_FILE"] = str(cdb_command_file)
    env["ONSLAUGHT_LIVE_CDB_LOG_PATH"] = str(cdb_log_path)
    env["ONSLAUGHT_LIVE_CDB_LOG_READY_TIMEOUT_MS"] = str(args.cdb_log_ready_timeout_ms)
    env["ONSLAUGHT_LIVE_CDB_POST_ATTACH_WAIT_SECONDS"] = str(args.cdb_post_attach_wait_seconds)
    env["ONSLAUGHT_LIVE_CDB_ATTACH_PHASE"] = args.cdb_attach_phase
    env["ONSLAUGHT_LIVE_LAUNCH_ARGUMENTS_JSON"] = json.dumps(launch_arguments)
    env["ONSLAUGHT_LIVE_INPUT_STEP_DELAY_MS"] = str(args.input_step_delay_ms)
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

    command = ["dotnet", "run", "--project", str(project), "--nologo"]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=env)
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
