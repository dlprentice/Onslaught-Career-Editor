#!/usr/bin/env python3
"""Bounded Windows WASAPI loopback capture helper for runtime proof preflights."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "audio-loopback-capture.v1"
ARM_PHRASE = "CAPTURE LOOPBACK AUDIO"
TONE_ARM_PHRASE = "PLAY CALIBRATION TONE"
RUNNER_MARKER = ".onslaught-loopback-capture-runner"
NAUDIO_VERSION = "2.3.0"
DEFAULT_GAME_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")


class LoopbackError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LoopbackError(message)


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def paths_overlap(left: Path, right: Path) -> bool:
    return is_same_or_under(left, right) or is_same_or_under(right, left)


def has_symlink_ancestor(path: Path) -> bool:
    current = path.absolute()
    while True:
        if current.exists() and current.is_symlink():
            return True
        parent = current.parent
        if parent == current:
            return False
        current = parent


def protected_roots() -> list[Path]:
    roots: list[Path] = []
    for key in ("ProgramFiles", "ProgramFiles(x86)"):
        raw = os.environ.get(key)
        if raw:
            candidate = Path(raw)
            if candidate.exists():
                roots.append(candidate.resolve())
    return roots


def resolve_output_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    allowed_root = Path(args.allowed_output_root).resolve()
    output_wav = Path(args.output_wav).resolve()
    output_json = Path(args.output_json).resolve()
    source_game_root = Path(args.source_game_root).resolve()

    require(args.arm_capture_audio == ARM_PHRASE, f'Refusing loopback capture without --arm-capture-audio "{ARM_PHRASE}".')
    require(args.duration_ms >= 100 and args.duration_ms <= 60000, "--duration-ms must be between 100 and 60000.")
    require(allowed_root.exists() and allowed_root.is_dir(), "Allowed output root must already exist.")
    require(output_wav.suffix.lower() == ".wav", "Output WAV path must end in .wav.")
    require(output_json.suffix.lower() == ".json", "Output JSON path must end in .json.")
    require(is_same_or_under(output_wav, allowed_root), "Output WAV must stay under the allowed output root.")
    require(is_same_or_under(output_json, allowed_root), "Output JSON must stay under the allowed output root.")
    require(not has_symlink_ancestor(allowed_root), "Allowed output root must not contain a symlink ancestor.")
    require(not has_symlink_ancestor(output_wav), "Output WAV path must not contain a symlink ancestor.")
    require(not has_symlink_ancestor(output_json), "Output JSON path must not contain a symlink ancestor.")
    require(not output_wav.exists() or args.allow_overwrite, "Output WAV already exists.")
    require(not output_json.exists() or args.allow_overwrite, "Output JSON already exists.")

    if source_game_root.exists():
        require(not paths_overlap(allowed_root, source_game_root), "Allowed output root must not overlap the source game root.")
        require(not is_same_or_under(output_wav, source_game_root), "Output WAV must not be under the source game root.")
        require(not is_same_or_under(output_json, source_game_root), "Output JSON must not be under the source game root.")

    for root in protected_roots():
        require(not paths_overlap(allowed_root, root), "Allowed output root must not overlap Program Files.")
        require(not is_same_or_under(output_wav, root), "Output WAV must not be under Program Files.")
        require(not is_same_or_under(output_json, root), "Output JSON must not be under Program Files.")

    require(output_wav.parent == output_json.parent or is_same_or_under(output_wav.parent, allowed_root), "Output WAV parent escaped allowed root.")
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    return allowed_root, output_wav, output_json, source_game_root


def runner_source() -> str:
    return r'''
using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading.Tasks;
using NAudio.CoreAudioApi;
using NAudio.Wave;
using NAudio.Wave.SampleProviders;

static double DecodeSample(byte[] buffer, int offset, int bytesPerSample, WaveFormatEncoding encoding)
{
    if (bytesPerSample == 4 && encoding == WaveFormatEncoding.IeeeFloat)
    {
        float value = BitConverter.ToSingle(buffer, offset);
        if (float.IsNaN(value) || float.IsInfinity(value))
            return 0.0;
        return Math.Max(-1.0, Math.Min(1.0, value));
    }

    if (encoding == WaveFormatEncoding.Pcm && bytesPerSample == 2)
        return BitConverter.ToInt16(buffer, offset) / 32768.0;

    if (encoding == WaveFormatEncoding.Pcm && bytesPerSample == 4)
        return BitConverter.ToInt32(buffer, offset) / 2147483648.0;

    return 0.0;
}

static object Failure(string outputWav, string outputJson, string message, string exceptionType)
{
    return new
    {
        schemaVersion = "audio-loopback-capture.v1",
        generatedAt = DateTimeOffset.UtcNow,
        status = "failed",
        captureKind = "wasapi-loopback",
        outputWav,
        outputJson,
        error = message,
        errorType = exceptionType,
        claimBoundary = "Loopback capture helper failure; no audible BEA music playback claim.",
        nonClaims = new[]
        {
            "BEA audible playback",
            "source-bound BEA music output",
            "music replacement proof",
            "clean baseline comparison",
            "gameplay parity",
            "rebuild parity"
        }
    };
}

static string Sha256File(string path)
{
    using FileStream stream = File.OpenRead(path);
    byte[] digest = SHA256.HashData(stream);
    return Convert.ToHexString(digest).ToLowerInvariant();
}

if (args.Length != 5)
{
    Console.Error.WriteLine("usage: LoopbackCapture <output-wav> <duration-ms> <output-json> <play-calibration-tone> <tone-gain>");
    return 2;
}

string outputWavPath = Path.GetFullPath(args[0]);
int durationMs = int.Parse(args[1], CultureInfo.InvariantCulture);
string outputJsonPath = Path.GetFullPath(args[2]);
bool playCalibrationTone = string.Equals(args[3], "1", StringComparison.Ordinal);
double toneGain = double.Parse(args[4], CultureInfo.InvariantCulture);

try
{
    Directory.CreateDirectory(Path.GetDirectoryName(outputWavPath)!);
    Directory.CreateDirectory(Path.GetDirectoryName(outputJsonPath)!);

    using var enumerator = new MMDeviceEnumerator();
    using MMDevice device = enumerator.GetDefaultAudioEndpoint(DataFlow.Render, Role.Multimedia);
    using var capture = new WasapiLoopbackCapture(device);

    long bytesRecorded = 0;
    long sampleCount = 0;
    long nonZeroSampleCount = 0;
    double peakAbs = 0.0;
    double sumSquares = 0.0;
    int dataEventCount = 0;
    string statsMode = "unsupported-format";
    var stopwatch = Stopwatch.StartNew();
    var stopped = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);
    DateTimeOffset captureStartedUtc;
    DateTimeOffset captureEndedUtc;

    int bytesPerSample = Math.Max(0, capture.WaveFormat.BitsPerSample / 8);
    bool canDecodeStats =
        bytesPerSample > 0 &&
        (capture.WaveFormat.Encoding == WaveFormatEncoding.IeeeFloat ||
         capture.WaveFormat.Encoding == WaveFormatEncoding.Pcm);
    if (canDecodeStats)
        statsMode = $"{capture.WaveFormat.Encoding}-{capture.WaveFormat.BitsPerSample}-bit";

    await using (var writer = new WaveFileWriter(outputWavPath, capture.WaveFormat))
    {
        capture.DataAvailable += (_, eventArgs) =>
        {
            writer.Write(eventArgs.Buffer, 0, eventArgs.BytesRecorded);
            writer.Flush();
            bytesRecorded += eventArgs.BytesRecorded;
            dataEventCount++;

            if (!canDecodeStats)
                return;

            for (int offset = 0; offset + bytesPerSample <= eventArgs.BytesRecorded; offset += bytesPerSample)
            {
                double sample = DecodeSample(eventArgs.Buffer, offset, bytesPerSample, capture.WaveFormat.Encoding);
                double abs = Math.Abs(sample);
                if (abs > peakAbs)
                    peakAbs = abs;
                if (abs > 0.000001)
                    nonZeroSampleCount++;
                sumSquares += sample * sample;
                sampleCount++;
            }
        };
        capture.RecordingStopped += (_, eventArgs) =>
        {
            if (eventArgs.Exception is null)
                stopped.TrySetResult(0);
            else
                stopped.TrySetException(eventArgs.Exception);
        };

        using var toneOut = playCalibrationTone ? new WaveOutEvent() : null;
        if (toneOut is not null)
        {
            var tone = new SignalGenerator(48000, 2)
            {
                Gain = toneGain,
                Frequency = 880,
                Type = SignalGeneratorType.Sin
            };
            toneOut.Init(tone);
        }

        captureStartedUtc = DateTimeOffset.UtcNow;
        capture.StartRecording();
        toneOut?.Play();
        await Task.Delay(durationMs);
        toneOut?.Stop();
        capture.StopRecording();
        await stopped.Task;
        captureEndedUtc = DateTimeOffset.UtcNow;
        stopwatch.Stop();
    }

    // WaveFileWriter must be disposed before hashing the WAV.
    string rawWavSha256 = Sha256File(outputWavPath);
    double rms = sampleCount > 0 ? Math.Sqrt(sumSquares / sampleCount) : 0.0;
    bool nonSilent = sampleCount > 0 && peakAbs >= 0.001 && rms >= 0.0001;
    var wavInfo = new FileInfo(outputWavPath);
    var payload = new
    {
        schemaVersion = "audio-loopback-capture.v1",
        generatedAt = DateTimeOffset.UtcNow,
        status = "captured",
        captureKind = "wasapi-loopback",
        captureStartedUtc,
        captureEndedUtc,
            outputWav = outputWavPath,
            outputJson = outputJsonPath,
            rawWavSha256 = rawWavSha256,
            requestedDurationMs = durationMs,
        observedDurationMs = (long)stopwatch.Elapsed.TotalMilliseconds,
        device = new
        {
            friendlyName = device.FriendlyName,
            id = device.ID,
            dataFlow = "render",
            role = "multimedia"
        },
        calibration = new
        {
            played = playCalibrationTone,
            frequencyHz = playCalibrationTone ? 880 : 0,
            gain = playCalibrationTone ? toneGain : 0.0,
            note = playCalibrationTone
                ? "Short explicitly armed synthetic tone used only to prove the loopback backend can observe output."
                : "No synthetic tone requested."
        },
        waveFormat = new
        {
            encoding = capture.WaveFormat.Encoding.ToString(),
            sampleRate = capture.WaveFormat.SampleRate,
            channels = capture.WaveFormat.Channels,
            bitsPerSample = capture.WaveFormat.BitsPerSample,
            blockAlign = capture.WaveFormat.BlockAlign,
            averageBytesPerSecond = capture.WaveFormat.AverageBytesPerSecond
        },
        audioStats = new
        {
            statsMode,
            dataEventCount,
            bytesRecorded,
            wavFileBytes = wavInfo.Exists ? wavInfo.Length : 0,
            sampleCount,
            nonZeroSampleCount,
            peakAbs,
            rms,
            nonSilent
        },
        claimBoundary = "Bounded system render-loopback capture only. This does not prove BEA music is audible, source-bound, replaced, or different from a clean baseline.",
        nonClaims = new[]
        {
            "BEA audible playback",
            "source-bound BEA music output",
            "BEA music replacement proof",
            "music replacement proof",
            "clean baseline comparison",
            "CDB selection/decode correlation",
            "arbitrary external OGG compatibility",
            "gameplay parity",
            "rebuild parity"
        }
    };
    string json = JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true });
    File.WriteAllText(outputJsonPath, json);
    Console.WriteLine(json);
    return 0;
}
catch (Exception ex)
{
    var payload = Failure(outputWavPath, outputJsonPath, ex.Message, ex.GetType().FullName ?? ex.GetType().Name);
    string json = JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true });
    File.WriteAllText(outputJsonPath, json);
    Console.WriteLine(json);
    return 2;
}
'''


def write_runner(runner_root: Path) -> Path:
    if runner_root.exists():
        marker = runner_root / RUNNER_MARKER
        require(marker.is_file(), f"Refusing to remove non-tool-owned runner directory: {runner_root}")
        shutil.rmtree(runner_root)
    runner_root.mkdir(parents=True, exist_ok=True)
    (runner_root / RUNNER_MARKER).write_text("tool-owned loopback capture runner\n", encoding="utf-8")
    project = runner_root / "LoopbackCapture.csproj"
    project.write_text(
        f"""<Project Sdk=\"Microsoft.NET.Sdk\">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0-windows10.0.19041.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include=\"NAudio\" Version=\"{NAUDIO_VERSION}\" />
  </ItemGroup>
</Project>
""",
        encoding="utf-8",
    )
    (runner_root / "Program.cs").write_text(runner_source(), encoding="utf-8")
    return project


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object.")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def validate_artifact(path: Path, *, require_non_silent: bool = False) -> dict[str, Any]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == SCHEMA, "Unexpected loopback artifact schema.")
    require(payload.get("status") == "captured", "Loopback capture did not complete.")
    require(payload.get("captureKind") == "wasapi-loopback", "Unexpected capture kind.")
    require(isinstance(payload.get("captureStartedUtc"), str), "captureStartedUtc must be present.")
    require(isinstance(payload.get("captureEndedUtc"), str), "captureEndedUtc must be present.")
    stats = object_at(payload, "audioStats")
    wave_format = object_at(payload, "waveFormat")
    require(int(stats.get("bytesRecorded", 0)) >= 0, "bytesRecorded must be present.")
    require(int(stats.get("wavFileBytes", 0)) > 0, "WAV file bytes must be positive.")
    require(int(wave_format.get("sampleRate", 0)) > 0, "sample rate must be positive.")
    require(int(wave_format.get("channels", 0)) > 0, "channel count must be positive.")
    require("BEA audible playback" in payload.get("nonClaims", []), "non-claims must reject BEA audible playback.")
    non_silent = bool(stats.get("nonSilent"))
    if require_non_silent:
        require(non_silent, "Loopback artifact did not observe non-silent output.")
    return {
        "schema": SCHEMA,
        "status": payload.get("status"),
        "captureKind": payload.get("captureKind"),
        "captureStartedUtc": payload.get("captureStartedUtc"),
        "captureEndedUtc": payload.get("captureEndedUtc"),
        "device": object_at(payload, "device").get("friendlyName"),
        "requestedDurationMs": payload.get("requestedDurationMs"),
        "observedDurationMs": payload.get("observedDurationMs"),
        "sampleRate": wave_format.get("sampleRate"),
        "channels": wave_format.get("channels"),
        "bytesRecorded": stats.get("bytesRecorded"),
        "wavFileBytes": stats.get("wavFileBytes"),
        "sampleCount": stats.get("sampleCount"),
        "peakAbs": stats.get("peakAbs"),
        "rms": stats.get("rms"),
        "nonSilent": non_silent,
        "claimBoundary": payload.get("claimBoundary"),
    }


def capture(args: argparse.Namespace) -> dict[str, Any]:
    allowed_root, output_wav, output_json, _ = resolve_output_paths(args)
    runner_root = allowed_root / "loopback-capture-runner"
    project = write_runner(runner_root)
    build_command = [
        "dotnet",
        "build",
        str(project),
        "--nologo",
    ]
    build_result = subprocess.run(build_command, cwd=ROOT, text=True, capture_output=True, check=False)
    (allowed_root / "loopback-capture-build-stdout.log").write_text(build_result.stdout, encoding="utf-8")
    (allowed_root / "loopback-capture-build-stderr.log").write_text(build_result.stderr, encoding="utf-8")
    if build_result.returncode != 0:
        raise LoopbackError(f"Loopback capture runner build failed: {build_result.stderr.strip() or build_result.stdout.strip()}")

    exe_name = "LoopbackCapture.exe" if os.name == "nt" else "LoopbackCapture"
    runner_exe = runner_root / "bin" / "Debug" / "net10.0-windows10.0.19041.0" / exe_name
    require(runner_exe.is_file(), f"Loopback capture runner executable missing: {runner_exe}")
    run_command = [
        str(runner_exe),
        str(output_wav),
        str(args.duration_ms),
        str(output_json),
        "1" if args.play_calibration_tone else "0",
        f"{args.calibration_tone_gain:.6f}",
    ]
    result = subprocess.run(run_command, cwd=ROOT, text=True, capture_output=True, check=False)
    (allowed_root / "loopback-capture-stdout.log").write_text(result.stdout, encoding="utf-8")
    (allowed_root / "loopback-capture-stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        if output_json.is_file():
            payload = read_json(output_json)
            raise LoopbackError(f"Loopback capture failed closed: {payload.get('error', result.stderr.strip())}")
        raise LoopbackError(f"Loopback capture command failed: {result.stderr.strip() or result.stdout.strip()}")
    return validate_artifact(output_json, require_non_silent=args.require_non_silent)


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        artifact = root / "capture.json"
        wav = root / "capture.wav"
        wav.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt " + (16).to_bytes(4, "little") + b"\x01\x00\x01\x00\x40\x1f\x00\x00\x80>\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
        artifact.write_text(
            json.dumps(
                {
                    "schemaVersion": SCHEMA,
                    "status": "captured",
                    "captureKind": "wasapi-loopback",
                    "captureStartedUtc": "2026-06-22T00:00:00Z",
                    "captureEndedUtc": "2026-06-22T00:00:01Z",
                    "device": {"friendlyName": "self-test"},
                    "waveFormat": {"sampleRate": 8000, "channels": 1},
                    "audioStats": {
                        "bytesRecorded": 0,
                        "wavFileBytes": len(wav.read_bytes()),
                        "sampleCount": 0,
                        "peakAbs": 0.0,
                        "rms": 0.0,
                        "nonSilent": False,
                    },
                    "claimBoundary": "self-test",
                    "nonClaims": ["BEA audible playback"],
                }
            ),
            encoding="utf-8",
        )
        summary = validate_artifact(artifact)
        require(summary["nonSilent"] is False, "Self-test expected silence to remain silence.")
        try:
            validate_artifact(artifact, require_non_silent=True)
        except LoopbackError:
            pass
        else:
            raise LoopbackError("Self-test expected --require-non-silent to fail on silent fixture.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--check", default="", help="Validate an existing loopback capture JSON artifact.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-wav", default="")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--allowed-output-root", default="")
    parser.add_argument("--source-game-root", default=str(DEFAULT_GAME_ROOT))
    parser.add_argument("--duration-ms", type=int, default=1000)
    parser.add_argument("--arm-capture-audio", default="")
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--require-non-silent", action="store_true")
    parser.add_argument("--play-calibration-tone", action="store_true", help="Play a short synthetic tone while capturing, only with --arm-calibration-tone.")
    parser.add_argument("--arm-calibration-tone", default="", help=f"Required with --play-calibration-tone. Exact phrase: {TONE_ARM_PHRASE!r}.")
    parser.add_argument("--calibration-tone-gain", type=float, default=0.03, help="Synthetic tone gain for preflight, 0.001 to 0.2.")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("Audio loopback capture helper self-test: PASS")
            return 0
        if args.check:
            print(json.dumps(validate_artifact(Path(args.check), require_non_silent=args.require_non_silent), indent=2, sort_keys=True))
            return 0
        require(args.capture, "Use --capture, --check, or --self-test.")
        require(args.output_wav and args.output_json and args.allowed_output_root, "--capture requires output paths and --allowed-output-root.")
        if args.play_calibration_tone:
            require(args.arm_calibration_tone == TONE_ARM_PHRASE, f'Refusing calibration tone without --arm-calibration-tone "{TONE_ARM_PHRASE}".')
            require(args.calibration_tone_gain >= 0.001 and args.calibration_tone_gain <= 0.2, "--calibration-tone-gain must be between 0.001 and 0.2.")
        print(json.dumps(capture(args), indent=2, sort_keys=True))
        return 0
    except LoopbackError as exc:
        print(f"Audio loopback capture helper: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
