#!/usr/bin/env python3
"""Build sanitized capture-to-source music correlation adapter artifacts.

This producer is offline proof infrastructure. It reads explicit private clean
and staged loopback artifacts, optionally reads the installed source OGG files
read-only through a private helper runner, and emits the sanitized
`winui-safe-copy-music-capture-source-correlation.v1` adapter consumed by the
music audible-output materializer. It does not launch BEA, attach CDB, capture
audio, patch bytes, or claim runtime audible output.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any, Callable, Iterable

import winui_safe_copy_music_audible_output_materializer as materializer
import winui_safe_copy_music_capture_source_correlation_check as checker


SCHEMA = "winui-safe-copy-music-capture-source-correlation.v1"
ADAPTER_VERSION = "capture-source-correlation-helper.v1"
ARM_PHRASE = "BUILD CAPTURE SOURCE CORRELATION"
RUNNER_MARKER = ".onslaught-capture-source-correlation-runner"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
TARGET_RELATIVE = Path("data") / "Music" / TARGET
REPLACEMENT_RELATIVE = Path("data") / "Music" / REPLACEMENT
LEVEL_ID = 100
HELPER_VERSION = "source-audio-correlation-helper.v1"
NVORBIS_VERSION = "0.10.5"
WINDOW_COUNT = 128
MIN_ACTIVE_WINDOW_COUNT = 16
MIN_ACCEPTED_MARGIN = 0.15
RUNNER_TIMEOUT_SECONDS = 240
DEFAULT_SOURCE_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
METHOD = "bounded-fingerprint"
REPARSE_POINT_ATTRIBUTE = 0x400


class CaptureSourceCorrelationBuilderError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CaptureSourceCorrelationBuilderError(message)


def utc_now_text() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object.")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def lexical_candidates(path: Path) -> Iterable[Path]:
    absolute = Path(os.path.abspath(path))
    if not absolute.parts:
        return
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        yield current


def validate_no_reparse_lexical(path: Path) -> None:
    for candidate in lexical_candidates(path):
        try:
            stats = candidate.lstat()
        except FileNotFoundError:
            continue
        if candidate.is_symlink():
            raise CaptureSourceCorrelationBuilderError(f"Refusing symlinked builder path: {candidate}")
        attrs = getattr(stats, "st_file_attributes", 0)
        if attrs & REPARSE_POINT_ATTRIBUTE:
            raise CaptureSourceCorrelationBuilderError(f"Refusing reparse-point builder path: {candidate}")


def safe_remove_tool_tree(root: Path) -> None:
    validate_no_reparse_lexical(root)
    if not root.exists():
        return
    marker = root / RUNNER_MARKER
    if not marker.is_file():
        require(not any(root.iterdir()), f"Refusing to remove non-tool-owned runner directory: {root}")
        root.rmdir()
        return

    def remove_directory(path: Path) -> None:
        validate_no_reparse_lexical(path)
        for entry in os.scandir(path):
            entry_path = Path(entry.path)
            attrs = getattr(entry.stat(follow_symlinks=False), "st_file_attributes", 0)
            if entry.is_symlink() or attrs & REPARSE_POINT_ATTRIBUTE:
                raise CaptureSourceCorrelationBuilderError(f"Refusing to remove reparse/symlink runner entry: {entry_path}")
            if entry.is_dir(follow_symlinks=False):
                remove_directory(entry_path)
            else:
                entry_path.unlink()
        path.rmdir()

    remove_directory(root)


def resolve_dotnet() -> str:
    dotnet = shutil.which("dotnet")
    require(dotnet is not None, "dotnet executable was not found on PATH.")
    return dotnet


def sanitized_child_env() -> dict[str, str]:
    sensitive_fragments = ("TOKEN", "KEY", "SECRET", "PASSWORD", "AUTH", "COOKIE", "CREDENTIAL", "SESSION")
    allowed = {
        "APPDATA",
        "DOTNET_CLI_HOME",
        "DOTNET_ROOT",
        "LOCALAPPDATA",
        "NUGET_PACKAGES",
        "PATH",
        "PROCESSOR_ARCHITECTURE",
        "ProgramFiles",
        "ProgramFiles(x86)",
        "SystemDrive",
        "SystemRoot",
        "TEMP",
        "TMP",
        "USERPROFILE",
        "WINDIR",
    }
    env: dict[str, str] = {}
    for key in allowed:
        value = os.environ.get(key)
        if value is None:
            continue
        upper_key = key.upper()
        if any(fragment in upper_key for fragment in sensitive_fragments):
            continue
        env[key] = value
    return env


def validate_output_path(*, output: Path, allowed_output_root: Path, source_root: Path, allow_overwrite: bool = False) -> None:
    require(allowed_output_root.exists() and allowed_output_root.is_dir(), "Allowed output root must already exist.")
    validate_no_reparse_lexical(allowed_output_root)
    validate_no_reparse_lexical(output.parent)
    if source_root.exists():
        validate_no_reparse_lexical(source_root)
    if source_root.exists():
        require(not is_same_or_under(allowed_output_root, source_root), "Allowed output root must not be under the source game root.")
        require(not is_same_or_under(source_root, allowed_output_root), "Source game root must not be under the allowed output root.")
        require(not is_same_or_under(output, source_root), "Output must not be under the source game root.")
    require(output.suffix.lower() == ".json", "Output path must end in .json.")
    require(is_same_or_under(output, allowed_output_root), "Output must stay under the allowed output root.")
    require(not output.exists() or allow_overwrite, "Output already exists; use --allow-overwrite.")
    materializer.validate_no_symlink_or_reparse(allowed_output_root)
    materializer.validate_no_symlink_or_reparse(output.parent)


def expand_to_windows(values: Iterable[float], *, label: str) -> list[float]:
    raw = [float(value) for value in values]
    require(bool(raw), f"{label} vector must not be empty.")
    require(all(math.isfinite(value) for value in raw), f"{label} vector contains non-finite values.")
    require(any(abs(value) > 0.000000001 for value in raw), f"{label} vector is silent/zero.")
    if len(raw) == WINDOW_COUNT:
        return raw
    expanded: list[float] = []
    for index in range(WINDOW_COUNT):
        source_index = min(len(raw) - 1, int(index * len(raw) / WINDOW_COUNT))
        expanded.append(raw[source_index])
    return expanded


def active_window_count(values: list[float]) -> int:
    return sum(1 for value in values if abs(value) > 0.000000001)


def cosine(left: list[float], right: list[float]) -> float:
    require(len(left) == WINDOW_COUNT and len(right) == WINDOW_COUNT, "Vector length mismatch.")
    numerator = sum(l * r for l, r in zip(left, right))
    left_den = math.sqrt(sum(l * l for l in left))
    right_den = math.sqrt(sum(r * r for r in right))
    require(left_den > 0.0 and right_den > 0.0, "Cannot score a zero vector.")
    score = numerator / (left_den * right_den)
    return max(-1.0, min(1.0, score))


def score_text(value: float) -> str:
    return f"{value:.6f}"


def validate_audio_inputs(clean_audio: Path, staged_audio: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        clean = materializer.validate_audio(clean_audio, "cleanBaseline", require_non_silent=True, timeline=None)
        staged = materializer.validate_audio(staged_audio, "stagedPositive", require_non_silent=True, timeline=None)
        materializer.ensure_same_endpoint_and_format([clean, staged])
        return clean, staged
    except materializer.MaterializerError as exc:
        raise CaptureSourceCorrelationBuilderError(str(exc)) from exc


def build_adapter_from_vectors(
    *,
    clean_audio: Path,
    staged_audio: Path,
    output: Path,
    allowed_output_root: Path,
    source_root: Path,
    source_target_vector: Iterable[float],
    source_replacement_vector: Iterable[float],
    clean_capture_vector: Iterable[float],
    staged_capture_vector: Iterable[float],
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    validate_output_path(
        output=output,
        allowed_output_root=allowed_output_root,
        source_root=source_root,
        allow_overwrite=allow_overwrite,
    )
    clean_summary, staged_summary = validate_audio_inputs(clean_audio, staged_audio)

    target_vector = expand_to_windows(source_target_vector, label="source target")
    replacement_vector = expand_to_windows(source_replacement_vector, label="source replacement")
    clean_vector = expand_to_windows(clean_capture_vector, label="clean capture")
    staged_vector = expand_to_windows(staged_capture_vector, label="staged capture")

    clean_active = active_window_count(clean_vector)
    staged_active = active_window_count(staged_vector)
    source_target_active = active_window_count(target_vector)
    source_replacement_active = active_window_count(replacement_vector)
    require(source_target_active >= MIN_ACTIVE_WINDOW_COUNT, "source target has too few active windows.")
    require(source_replacement_active >= MIN_ACTIVE_WINDOW_COUNT, "source replacement has too few active windows.")
    require(clean_active >= MIN_ACTIVE_WINDOW_COUNT, "clean baseline has too few active windows.")
    require(staged_active >= MIN_ACTIVE_WINDOW_COUNT, "staged positive has too few active windows.")

    clean_vs_target = cosine(clean_vector, target_vector)
    clean_vs_replacement = cosine(clean_vector, replacement_vector)
    staged_vs_target = cosine(staged_vector, target_vector)
    staged_vs_replacement = cosine(staged_vector, replacement_vector)
    source_cross = cosine(target_vector, replacement_vector)
    source_margin = 1.0 - abs(source_cross)
    require(
        source_margin >= MIN_ACCEPTED_MARGIN,
        (
            "source target/replacement vectors are not distinct enough "
            f"(margin={score_text(source_margin)} minimum={score_text(MIN_ACCEPTED_MARGIN)} cross={score_text(source_cross)})."
        ),
    )

    clean_margin = clean_vs_target - clean_vs_replacement
    staged_margin = staged_vs_replacement - staged_vs_target
    require(
        clean_margin >= MIN_ACCEPTED_MARGIN,
        (
            "clean baseline does not prefer source target strongly enough "
            f"(margin={score_text(clean_margin)} minimum={score_text(MIN_ACCEPTED_MARGIN)} "
            f"target={score_text(clean_vs_target)} replacement={score_text(clean_vs_replacement)})."
        ),
    )
    require(
        staged_margin >= MIN_ACCEPTED_MARGIN,
        (
            "staged positive does not prefer source replacement strongly enough "
            f"(margin={score_text(staged_margin)} minimum={score_text(MIN_ACCEPTED_MARGIN)} "
            f"target={score_text(staged_vs_target)} replacement={score_text(staged_vs_replacement)})."
        ),
    )

    artifact = {
        "schemaVersion": SCHEMA,
        "adapterVersion": ADAPTER_VERSION,
        "generatedAt": utc_now_text(),
        "presetId": PRESET_ID,
        "levelId": LEVEL_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "inputBindings": {
            "cleanAudioJsonSha256": clean_summary["_audioArtifactSha256"],
            "cleanAudioWavSha256": clean_summary["_rawWavSha256"],
            "stagedAudioJsonSha256": staged_summary["_audioArtifactSha256"],
            "stagedAudioWavSha256": staged_summary["_rawWavSha256"],
        },
        "captureAnalysis": {
            "method": METHOD,
            "windowCount": WINDOW_COUNT,
            "minimumActiveWindowCount": MIN_ACTIVE_WINDOW_COUNT,
            "cleanBaselineActiveWindowCount": clean_active,
            "stagedPositiveActiveWindowCount": staged_active,
            "rmsPeakOnly": False,
        },
        "sourceAudioCorrelation": {
            "method": METHOD,
            "fingerprintVersion": HELPER_VERSION,
            "cleanBaselineBestMatch": TARGET,
            "stagedPositiveBestMatch": REPLACEMENT,
            "cleanBaselineTargetCorrelationGtReplacement": True,
            "stagedPositiveReplacementCorrelationGtTarget": True,
            "cleanBaselineMargin": clean_margin,
            "stagedPositiveMargin": staged_margin,
            "minimumAcceptedMargin": MIN_ACCEPTED_MARGIN,
            "rawAudioPublished": False,
            "sourceAudioPathsPublished": False,
            "privateCapturePathsPublished": False,
            "scoreMatrix": {
                "cleanBaselineVsTarget": clean_vs_target,
                "cleanBaselineVsReplacement": clean_vs_replacement,
                "stagedPositiveVsTarget": staged_vs_target,
                "stagedPositiveVsReplacement": staged_vs_replacement,
            },
        },
        "claimBoundary": "Offline capture-to-source correlation adapter only. Not runtime audible-output proof.",
        "nonClaims": sorted(checker.REQUIRED_NON_CLAIMS),
    }
    try:
        checker.validate_artifact(artifact)
    except checker.CorrelationAdapterError as exc:
        raise CaptureSourceCorrelationBuilderError(str(exc)) from exc
    write_json(output, artifact)
    return artifact


CSHARP_RUNNER = r'''
using System.Globalization;
using System.Text.Json;
using NVorbis;

const int WindowCount = 128;

if (args.Length != 5)
{
    Console.Error.WriteLine("usage: CaptureSourceCorrelationVectors <output-json> <target-ogg> <replacement-ogg> <clean-wav> <staged-wav>");
    return 2;
}

static int BucketFor(long frameIndex, long totalFrames)
{
    if (totalFrames <= 0)
        return 0;
    return (int)Math.Min(WindowCount - 1, (frameIndex * WindowCount) / totalFrames);
}

static double[] FinalizeBuckets(double[] sumSquares, long[] counts)
{
    var result = new double[WindowCount];
    for (int index = 0; index < WindowCount; index++)
        result[index] = counts[index] == 0 ? 0.0 : Math.Sqrt(sumSquares[index] / counts[index]);
    return result;
}

static double[] AnalyzeOgg(string path)
{
    using var reader = new VorbisReader(path);
    int channels = reader.Channels;
    long totalFrames = reader.TotalSamples;
    var sumSquares = new double[WindowCount];
    var counts = new long[WindowCount];
    var readBuffer = new float[channels * 8192];
    long frameIndex = 0;
    while (true)
    {
        int samplesRead = reader.ReadSamples(readBuffer, 0, readBuffer.Length);
        if (samplesRead <= 0)
            break;
        int frameCount = samplesRead / channels;
        for (int frame = 0; frame < frameCount; frame++)
        {
            double mono = 0.0;
            for (int channel = 0; channel < channels; channel++)
                mono += readBuffer[(frame * channels) + channel];
            mono /= channels;
            int bucket = BucketFor(frameIndex, totalFrames);
            sumSquares[bucket] += mono * mono;
            counts[bucket]++;
            frameIndex++;
        }
    }
    return FinalizeBuckets(sumSquares, counts);
}

static double DecodeSample(byte[] bytes, int offset, ushort formatTag, ushort bitsPerSample)
{
    if (formatTag == 3 && bitsPerSample == 32)
    {
        float value = BitConverter.ToSingle(bytes, offset);
        if (float.IsNaN(value) || float.IsInfinity(value))
            return 0.0;
        return Math.Max(-1.0, Math.Min(1.0, value));
    }
    if (formatTag == 1 && bitsPerSample == 16)
        return BitConverter.ToInt16(bytes, offset) / 32768.0;
    if (formatTag == 1 && bitsPerSample == 32)
        return BitConverter.ToInt32(bytes, offset) / 2147483648.0;
    throw new InvalidDataException("Unsupported WAV format.");
}

static double[] AnalyzeWav(string path)
{
    byte[] file = File.ReadAllBytes(path);
    if (file.Length < 44 || file[0] != 'R' || file[1] != 'I' || file[2] != 'F' || file[3] != 'F' || file[8] != 'W')
        throw new InvalidDataException("Input is not a RIFF/WAVE file.");
    ushort formatTag = 0;
    ushort channels = 0;
    ushort bitsPerSample = 0;
    byte[]? data = null;
    int offset = 12;
    while (offset + 8 <= file.Length)
    {
        string id = System.Text.Encoding.ASCII.GetString(file, offset, 4);
        int size = BitConverter.ToInt32(file, offset + 4);
        int start = offset + 8;
        int end = start + size;
        if (end > file.Length)
            throw new InvalidDataException("WAV chunk extends past file end.");
        if (id == "fmt ")
        {
            formatTag = BitConverter.ToUInt16(file, start);
            channels = BitConverter.ToUInt16(file, start + 2);
            bitsPerSample = BitConverter.ToUInt16(file, start + 14);
            if (formatTag == 0xFFFE && size >= 40)
                formatTag = BitConverter.ToUInt16(file, start + 24);
        }
        else if (id == "data")
        {
            data = file[start..end];
        }
        offset = end + (size % 2);
    }
    if (channels == 0 || bitsPerSample == 0 || data is null)
        throw new InvalidDataException("WAV is missing fmt or data chunk.");
    int bytesPerSample = bitsPerSample / 8;
    if (bytesPerSample <= 0)
        throw new InvalidDataException("Invalid WAV sample width.");
    int frameBytes = bytesPerSample * channels;
    long totalFrames = data.Length / frameBytes;
    if (totalFrames <= 0)
        throw new InvalidDataException("WAV has no frames.");
    var sumSquares = new double[WindowCount];
    var counts = new long[WindowCount];
    for (long frameIndex = 0; frameIndex < totalFrames; frameIndex++)
    {
        int frameOffset = (int)(frameIndex * frameBytes);
        double mono = 0.0;
        for (int channel = 0; channel < channels; channel++)
            mono += DecodeSample(data, frameOffset + (channel * bytesPerSample), formatTag, bitsPerSample);
        mono /= channels;
        int bucket = BucketFor(frameIndex, totalFrames);
        sumSquares[bucket] += mono * mono;
        counts[bucket]++;
    }
    return FinalizeBuckets(sumSquares, counts);
}

string output = args[0];
var payload = new
{
    sourceTargetVector = AnalyzeOgg(args[1]),
    sourceReplacementVector = AnalyzeOgg(args[2]),
    cleanCaptureVector = AnalyzeWav(args[3]),
    stagedCaptureVector = AnalyzeWav(args[4]),
};
Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output))!);
File.WriteAllText(output, JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine(output);
return 0;
'''


def write_runner(runner_root: Path) -> Path:
    validate_no_reparse_lexical(runner_root)
    require(runner_root.exists() and runner_root.is_dir(), "Runner root must be a freshly created directory.")
    require(not any(runner_root.iterdir()), "Runner root must be empty.")
    (runner_root / RUNNER_MARKER).write_text("tool-owned capture-source correlation runner\n", encoding="utf-8")
    project = runner_root / "CaptureSourceCorrelationVectors.csproj"
    project.write_text(
        f"""<Project Sdk=\"Microsoft.NET.Sdk\">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include=\"NVorbis\" Version=\"{NVORBIS_VERSION}\" />
  </ItemGroup>
</Project>
""",
        encoding="utf-8",
    )
    (runner_root / "Program.cs").write_text(CSHARP_RUNNER, encoding="utf-8")
    return project


def vector_list(payload: dict[str, Any], key: str) -> list[float]:
    value = payload.get(key)
    require(isinstance(value, list), f"Runner output missing vector: {key}")
    return [float(item) for item in value]


def build_adapter_from_paths(
    *,
    clean_audio: Path,
    staged_audio: Path,
    output: Path,
    allowed_output_root: Path,
    source_root: Path,
    allow_overwrite: bool = False,
    runner_invoker: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    validate_output_path(
        output=output,
        allowed_output_root=allowed_output_root,
        source_root=source_root,
        allow_overwrite=allow_overwrite,
    )
    target_path = source_root / TARGET_RELATIVE
    replacement_path = source_root / REPLACEMENT_RELATIVE
    require(target_path.is_file(), f"Missing source target track: {TARGET}")
    require(replacement_path.is_file(), f"Missing source replacement track: {REPLACEMENT}")
    validate_no_reparse_lexical(target_path)
    validate_no_reparse_lexical(replacement_path)
    materializer.validate_no_symlink_or_reparse(target_path)
    materializer.validate_no_symlink_or_reparse(replacement_path)
    clean_summary, staged_summary = validate_audio_inputs(clean_audio, staged_audio)
    clean_wav = Path(read_json(clean_audio)["outputWav"])
    staged_wav = Path(read_json(staged_audio)["outputWav"])

    runner_root = Path(tempfile.mkdtemp(prefix="capture-source-correlation-runner-", dir=allowed_output_root))
    try:
        validate_no_reparse_lexical(runner_root)
        project = write_runner(runner_root)
        vectors_json = runner_root / "capture-source-correlation-vectors.json"
        command = [
            resolve_dotnet(),
            "run",
            "--project",
            str(project),
            "--",
            str(vectors_json),
            str(target_path),
            str(replacement_path),
            str(clean_wav),
            str(staged_wav),
        ]
        try:
            result = runner_invoker(
                command,
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
                timeout=RUNNER_TIMEOUT_SECONDS,
                env=sanitized_child_env(),
            )
        except subprocess.TimeoutExpired as exc:
            raise CaptureSourceCorrelationBuilderError("Capture-source correlation runner timed out.") from exc
        if result.returncode != 0:
            raise CaptureSourceCorrelationBuilderError("Capture-source correlation runner failed.")
        vectors = read_json(vectors_json)
    finally:
        safe_remove_tool_tree(runner_root)
    # Reuse the already validated summaries by making sure the second pass sees
    # the same artifact hashes. This keeps the path-based and vector-based paths
    # identical at the final output boundary.
    require(clean_summary["_audioArtifactSha256"] == materializer.sha256_file(clean_audio), "clean audio JSON hash drifted during builder run.")
    require(staged_summary["_audioArtifactSha256"] == materializer.sha256_file(staged_audio), "staged audio JSON hash drifted during builder run.")
    return build_adapter_from_vectors(
        clean_audio=clean_audio,
        staged_audio=staged_audio,
        output=output,
        allowed_output_root=allowed_output_root,
        source_root=source_root,
        source_target_vector=vector_list(vectors, "sourceTargetVector"),
        source_replacement_vector=vector_list(vectors, "sourceReplacementVector"),
        clean_capture_vector=vector_list(vectors, "cleanCaptureVector"),
        staged_capture_vector=vector_list(vectors, "stagedCaptureVector"),
        allow_overwrite=allow_overwrite,
    )


def _write_pcm16_wav(path: Path, *, sample_value: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(48000)
        samples = [sample_value] * 1024
        import struct

        handle.writeframes(struct.pack("<" + "h" * len(samples), *samples))


def _write_audio_fixture(path: Path, *, sample_value: int) -> Path:
    wav_path = path.with_suffix(".wav")
    _write_pcm16_wav(wav_path, sample_value=sample_value)
    peak = abs(sample_value) / 32768.0
    payload = {
        "schemaVersion": "audio-loopback-capture.v1",
        "status": "captured",
        "captureKind": "wasapi-loopback",
        "captureStartedUtc": "2026-06-22T00:00:00Z",
        "captureEndedUtc": "2026-06-22T00:00:03Z",
        "outputWav": str(wav_path),
        "outputJson": str(path),
        "rawWavSha256": materializer.sha256_file(wav_path),
        "requestedDurationMs": 3000,
        "observedDurationMs": 3000,
        "device": {"friendlyName": "self-test", "id": "endpoint-1", "dataFlow": "render", "role": "multimedia"},
        "calibration": {"played": False},
        "waveFormat": {"sampleRate": 48000, "channels": 2, "bitsPerSample": 16},
        "audioStats": {
            "bytesRecorded": 2048,
            "wavFileBytes": wav_path.stat().st_size,
            "sampleCount": 1024,
            "nonZeroSampleCount": 1024,
            "peakAbs": peak,
            "rms": peak,
            "nonSilent": True,
        },
        "claimBoundary": "self-test loopback fixture only.",
        "nonClaims": ["BEA audible playback"],
    }
    write_json(path, payload)
    return path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        out = root / "out"
        source = root / "source"
        out.mkdir()
        source.mkdir()
        clean = _write_audio_fixture(root / "clean" / "audio.json", sample_value=900)
        staged = _write_audio_fixture(root / "staged" / "audio.json", sample_value=1100)
        artifact = build_adapter_from_vectors(
            clean_audio=clean,
            staged_audio=staged,
            output=out / "capture-source-correlation.json",
            allowed_output_root=out,
            source_root=source,
            source_target_vector=[1.0, 0.0, 0.0, 0.0],
            source_replacement_vector=[0.0, 1.0, 0.0, 0.0],
            clean_capture_vector=[0.95, 0.05, 0.0, 0.0],
            staged_capture_vector=[0.05, 0.95, 0.0, 0.0],
        )
        checker.validate_artifact(artifact)


def sanitize_error_message(message: str) -> str:
    return materializer.sanitize_error_message(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="Build adapter from source OGGs and clean/staged audio JSON artifacts.")
    parser.add_argument("--check", default="", help="Validate an existing adapter artifact.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--clean-audio", type=Path)
    parser.add_argument("--staged-audio", type=Path)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--allowed-output-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--arm-correlation", default="")
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music capture-source correlation builder self-test: PASS")
            return 0
        if args.check:
            print(json.dumps(checker.validate_artifact(checker.read_json(Path(args.check))), indent=2, sort_keys=True))
            return 0
        require(args.build, "Use --build, --check, or --self-test.")
        require(args.arm_correlation == ARM_PHRASE, f'Refusing capture-source correlation build without --arm-correlation "{ARM_PHRASE}".')
        require(args.clean_audio is not None, "Provide --clean-audio.")
        require(args.staged_audio is not None, "Provide --staged-audio.")
        require(args.allowed_output_root is not None, "Provide --allowed-output-root.")
        require(args.output is not None, "Provide --output.")
        artifact = build_adapter_from_paths(
            clean_audio=args.clean_audio,
            staged_audio=args.staged_audio,
            output=args.output,
            allowed_output_root=args.allowed_output_root,
            source_root=args.source_root,
            allow_overwrite=args.allow_overwrite,
        )
        print(json.dumps(checker.validate_artifact(artifact), indent=2, sort_keys=True))
        return 0
    except (CaptureSourceCorrelationBuilderError, checker.CorrelationAdapterError, materializer.MaterializerError) as exc:
        print(f"WinUI safe-copy music capture-source correlation builder: FAIL: {sanitize_error_message(str(exc))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
