#!/usr/bin/env python3
"""Build a replay-only decode-window/sliding-source music diagnostic.

This diagnostic is for rejected private music audible-output bundles. It reads
explicit local raw audio JSON/WAV files, timestamped CDB timeline sidecars, and
the local source OGG pair, then asks a narrow question:

Does the audio near the CDB decode instant correlate better with the target
track or with the staged replacement when the source track is allowed to slide?

The output is a sanitized failure/triage diagnostic. It is not materializer
input and does not claim runtime audible output.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

import winui_safe_copy_music_audible_output_materializer as materializer
import winui_safe_copy_music_capture_source_correlation_builder as correlation_builder


SCHEMA = "winui-safe-copy-music-decode-window-correlation-diagnostic.v1"
RUNNER_SCHEMA = "winui-safe-copy-music-decode-window-correlation-runner.v1"
RUNNER_VERSION = "decode-window-sliding-source-runner.v1"
METHOD = "decode-window-sliding-source-rms"
ARM_PHRASE = "BUILD MUSIC DECODE WINDOW CORRELATION"
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
TARGET_RELATIVE = Path("data") / "Music" / TARGET
REPLACEMENT_RELATIVE = Path("data") / "Music" / REPLACEMENT
LEVEL_ID = 100
SELECTION_ID = 2
DEFAULT_SOURCE_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
DEFAULT_CAPTURE_WINDOW_MS = 8000
DEFAULT_SOURCE_STRIDE_MS = 1000
DEFAULT_BUCKET_COUNT = 128
DEFAULT_MIN_ACTIVE_WINDOW_COUNT = 16
DEFAULT_CAPTURE_OFFSETS_MS = [-4000, -2000, 0, 2000, 4000, 8000]
RUNNER_TIMEOUT_SECONDS = 240
NVORBIS_VERSION = "0.10.5"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
FORBIDDEN_PAYLOAD_KEYS = {
    "capturepath",
    "deviceid",
    "devicestableid",
    "endpointid",
    "envelopebuckets",
    "oggbase64",
    "oggbytes",
    "outputjson",
    "outputwav",
    "pcmbase64",
    "privatepath",
    "rawaudio",
    "rawaudiobase64",
    "rawpcm",
    "rawpcmbase64",
    "rawsamples",
    "samples",
    "sourcepath",
    "spectrogram",
    "spectrogrambins",
    "wavbase64",
    "wavbytes",
}
REQUIRED_NON_CLAIMS = [
    "not accepted capture-source correlation",
    "not materializer input",
    "not runtime audible-output proof",
    "not raw audio publication",
    "not raw CDB publication",
    "not private path publication",
    "not source path publication",
    "not arbitrary external OGG compatibility",
    "not all-cue proof",
    "not loop volume or mix proof",
    "not gameplay parity",
    "not online proof",
    "not rebuild parity",
    "no installed-game or original BEA.exe mutation",
]


class DecodeWindowCorrelationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DecodeWindowCorrelationError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object.")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalized_key(value: object) -> str:
    return str(value).replace("_", "").replace("-", "").lower()


def has_forbidden_payload_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if normalized_key(key) in FORBIDDEN_PAYLOAD_KEYS:
                return True
            if has_forbidden_payload_key(child):
                return True
    if isinstance(value, list):
        return any(has_forbidden_payload_key(child) for child in value)
    return False


def has_private_path_text(value: Any) -> bool:
    if isinstance(value, dict):
        return any(has_private_path_text(child) for child in value.values())
    if isinstance(value, list):
        return any(has_private_path_text(child) for child in value)
    if isinstance(value, str):
        lowered = value.lower()
        return (
            ":\\" in value
            or ":/" in value
            or "\\users\\" in lowered
            or "program files" in lowered
            or "steamapps" in lowered
            or str(Path(__file__).resolve().parents[1]).lower() in lowered
        )
    return False


def number_at(value: dict[str, Any], key: str) -> float:
    child = value.get(key)
    require(isinstance(child, (int, float)) and not isinstance(child, bool), f"Missing number: {key}")
    numeric = float(child)
    require(math.isfinite(numeric), f"{key} must be finite.")
    return numeric


def int_at(value: dict[str, Any], key: str) -> int:
    child = value.get(key)
    require(isinstance(child, int) and not isinstance(child, bool), f"Missing integer: {key}")
    return int(child)


def bool_at(value: dict[str, Any], key: str) -> bool:
    child = value.get(key)
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return bool(child)


def string_at(value: dict[str, Any], key: str) -> str:
    child = value.get(key)
    require(isinstance(child, str) and child, f"Missing string: {key}")
    return child


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def validate_sha(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(SHA256_RE.fullmatch(value)), f"{label} must be a SHA-256 hex string.")
    return value.lower()


def validate_timeline(path: Path, *, role: str) -> dict[str, Any]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == materializer.TIMELINE_SCHEMA, f"{role} timeline schema changed.")
    require(payload.get("role") == role, f"{role} timeline role mismatch.")
    require(payload.get("timestampSource") == materializer.TIMESTAMP_SOURCE, f"{role} timestamp source changed.")
    require(bool_at(payload, "cdbLogTimestamped"), f"{role} timeline must be timestamped.")
    require(bool_at(payload, "exactPidCdbObserver"), f"{role} timeline must be exact-PID CDB evidence.")
    require(int_at(payload, "levelId") == LEVEL_ID, f"{role} timeline level mismatch.")
    require(int_at(payload, "selectionId") == SELECTION_ID, f"{role} timeline selection mismatch.")
    require(bool_at(payload, "playSelectionObserved"), f"{role} timeline missing play-selection observation.")
    require(bool_at(payload, "asyncKickPathMatched"), f"{role} timeline missing async kick.")
    require(bool_at(payload, "oggOpenPathMatched"), f"{role} timeline missing Ogg open.")
    require(bool_at(payload, "decodedPcmPositiveRequestObserved"), f"{role} timeline missing decoded PCM read.")
    provenance = payload.get("musicSelectionProvenance")
    require(provenance in materializer.ACCEPTED_MUSIC_PROVENANCE, f"{role} timeline provenance is not accepted.")
    decode_start = materializer.utc_at(payload, "decodeWindowStartUtc")
    decode_end = materializer.utc_at(payload, "decodeWindowEndUtc")
    require(decode_start <= decode_end, f"{role} decode window is invalid.")
    row_counts = object_at(payload, "cdbEvidenceRowCounts")
    return {
        "role": role,
        "decodeWindowStartUtc": materializer.format_utc(decode_start),
        "decodeWindowEndUtc": materializer.format_utc(decode_end),
        "musicSelectionProvenance": provenance,
        "rowCounts": {
            "playSelectionRows": int_at(row_counts, "playSelectionRows"),
            "asyncKickRows": int_at(row_counts, "asyncKickRows"),
            "oggOpenRows": int_at(row_counts, "oggOpenRows"),
            "oggReadRows": int_at(row_counts, "oggReadRows"),
        },
        "_decodeWindowStartAt": decode_start,
        "_decodeWindowEndAt": decode_end,
        "_timelineSha256": materializer.sha256_file(path),
    }


def sanitize_env() -> dict[str, str]:
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
        if any(fragment in key.upper() for fragment in sensitive_fragments):
            continue
        env[key] = value
    return env


CSHARP_RUNNER = r'''
using System.Globalization;
using System.Text.Json;
using NVorbis;

if (args.Length != 12)
{
    Console.Error.WriteLine("usage: DecodeWindowCorrelation <output-json> <target-ogg> <replacement-ogg> <clean-wav> <staged-wav> <clean-decode-offset-ms> <staged-decode-offset-ms> <capture-window-ms> <capture-offsets-csv> <source-stride-ms> <bucket-count> <minimum-active-window-count>");
    return 2;
}

string outputJson = args[0];
string targetOgg = args[1];
string replacementOgg = args[2];
string cleanWav = args[3];
string stagedWav = args[4];
double cleanDecodeOffsetMs = double.Parse(args[5], CultureInfo.InvariantCulture);
double stagedDecodeOffsetMs = double.Parse(args[6], CultureInfo.InvariantCulture);
int captureWindowMs = int.Parse(args[7], CultureInfo.InvariantCulture);
int[] captureOffsetsMs = args[8].Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries).Select(int.Parse).ToArray();
int sourceStrideMs = int.Parse(args[9], CultureInfo.InvariantCulture);
int bucketCount = int.Parse(args[10], CultureInfo.InvariantCulture);
int minimumActiveWindowCount = int.Parse(args[11], CultureInfo.InvariantCulture);

static int FrameFromMs(double milliseconds, int sampleRate)
{
    return (int)Math.Round(milliseconds * sampleRate / 1000.0);
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

static (double[] Samples, int SampleRate) ReadWavMono(string path)
{
    byte[] file = File.ReadAllBytes(path);
    if (file.Length < 44 || file[0] != 'R' || file[1] != 'I' || file[2] != 'F' || file[3] != 'F' || file[8] != 'W')
        throw new InvalidDataException("Input is not a RIFF/WAVE file.");
    ushort formatTag = 0;
    ushort channels = 0;
    int sampleRate = 0;
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
            sampleRate = BitConverter.ToInt32(file, start + 4);
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
    if (channels == 0 || sampleRate <= 0 || bitsPerSample == 0 || data is null)
        throw new InvalidDataException("WAV is missing fmt or data chunk.");
    int bytesPerSample = bitsPerSample / 8;
    int frameBytes = bytesPerSample * channels;
    int frameCount = data.Length / frameBytes;
    var mono = new double[frameCount];
    for (int frame = 0; frame < frameCount; frame++)
    {
        int frameOffset = frame * frameBytes;
        double value = 0.0;
        for (int channel = 0; channel < channels; channel++)
            value += DecodeSample(data, frameOffset + (channel * bytesPerSample), formatTag, bitsPerSample);
        mono[frame] = value / channels;
    }
    return (mono, sampleRate);
}

static (double[] Samples, int SampleRate) ReadOggMono(string path)
{
    using var reader = new VorbisReader(path);
    int channels = reader.Channels;
    int sampleRate = reader.SampleRate;
    var mono = new List<double>(capacity: (int)Math.Min(int.MaxValue, reader.TotalSamples));
    var buffer = new float[channels * 8192];
    while (true)
    {
        int samplesRead = reader.ReadSamples(buffer, 0, buffer.Length);
        if (samplesRead <= 0)
            break;
        int frameCount = samplesRead / channels;
        for (int frame = 0; frame < frameCount; frame++)
        {
            double value = 0.0;
            for (int channel = 0; channel < channels; channel++)
                value += buffer[(frame * channels) + channel];
            mono.Add(value / channels);
        }
    }
    return (mono.ToArray(), sampleRate);
}

static (double[] Vector, int ActiveCount, double Rms, double PeakAbs) SegmentVector(double[] samples, int startFrame, int lengthFrames, int bucketCount)
{
    if (startFrame < 0 || lengthFrames <= 0 || startFrame + lengthFrames > samples.Length)
        throw new ArgumentOutOfRangeException(nameof(startFrame));
    var sumSquares = new double[bucketCount];
    var counts = new long[bucketCount];
    double totalSquares = 0.0;
    double peak = 0.0;
    for (int frame = 0; frame < lengthFrames; frame++)
    {
        double sample = samples[startFrame + frame];
        double abs = Math.Abs(sample);
        peak = Math.Max(peak, abs);
        double square = sample * sample;
        totalSquares += square;
        int bucket = (int)Math.Min(bucketCount - 1, ((long)frame * bucketCount) / lengthFrames);
        sumSquares[bucket] += square;
        counts[bucket]++;
    }
    var vector = new double[bucketCount];
    int activeCount = 0;
    for (int index = 0; index < bucketCount; index++)
    {
        vector[index] = counts[index] == 0 ? 0.0 : Math.Sqrt(sumSquares[index] / counts[index]);
        if (vector[index] > 0.000000001)
            activeCount++;
    }
    double rms = Math.Sqrt(totalSquares / lengthFrames);
    return (vector, activeCount, rms, peak);
}

static double Cosine(double[] left, double[] right)
{
    double numerator = 0.0;
    double leftDen = 0.0;
    double rightDen = 0.0;
    for (int index = 0; index < left.Length; index++)
    {
        numerator += left[index] * right[index];
        leftDen += left[index] * left[index];
        rightDen += right[index] * right[index];
    }
    if (leftDen <= 0.0 || rightDen <= 0.0)
        return 0.0;
    double score = numerator / Math.Sqrt(leftDen * rightDen);
    return Math.Max(-1.0, Math.Min(1.0, score));
}

static object BestSourceMatch(double[] captureVector, (double[] Samples, int SampleRate) source, int windowMs, int strideMs, int bucketCount)
{
    int windowFrames = FrameFromMs(windowMs, source.SampleRate);
    int strideFrames = Math.Max(1, FrameFromMs(strideMs, source.SampleRate));
    if (windowFrames <= 0 || source.Samples.Length < windowFrames)
        throw new InvalidDataException("Source track is shorter than the requested window.");
    double bestScore = double.NegativeInfinity;
    int bestOffsetFrames = 0;
    int sourceWindowCount = 0;
    for (int start = 0; start + windowFrames <= source.Samples.Length; start += strideFrames)
    {
        var sourceVector = SegmentVector(source.Samples, start, windowFrames, bucketCount).Vector;
        double score = Cosine(captureVector, sourceVector);
        if (score > bestScore)
        {
            bestScore = score;
            bestOffsetFrames = start;
        }
        sourceWindowCount++;
    }
    return new
    {
        bestScore,
        bestOffsetMs = (int)Math.Round(bestOffsetFrames * 1000.0 / source.SampleRate),
        sourceWindowCount,
    };
}

var target = ReadOggMono(targetOgg);
var replacement = ReadOggMono(replacementOgg);
var clean = ReadWavMono(cleanWav);
var staged = ReadWavMono(stagedWav);
var rows = new List<object>();

void AddRows(string role, (double[] Samples, int SampleRate) capture, double decodeOffsetMs)
{
    int windowFrames = FrameFromMs(captureWindowMs, capture.SampleRate);
    foreach (int captureOffsetMs in captureOffsetsMs)
    {
        double startMs = decodeOffsetMs + captureOffsetMs;
        int startFrame = FrameFromMs(startMs, capture.SampleRate);
        if (startFrame < 0 || windowFrames <= 0 || startFrame + windowFrames > capture.Samples.Length)
        {
            rows.Add(new
            {
                role,
                captureOffsetMs,
                skipped = true,
                skipReason = "capture-window-out-of-range",
            });
            continue;
        }
        var captureSegment = SegmentVector(capture.Samples, startFrame, windowFrames, bucketCount);
        var targetBest = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(
            JsonSerializer.Serialize(BestSourceMatch(captureSegment.Vector, target, captureWindowMs, sourceStrideMs, bucketCount)))!;
        var replacementBest = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(
            JsonSerializer.Serialize(BestSourceMatch(captureSegment.Vector, replacement, captureWindowMs, sourceStrideMs, bucketCount)))!;
        double targetScore = targetBest["bestScore"].GetDouble();
        double replacementScore = replacementBest["bestScore"].GetDouble();
        rows.Add(new
        {
            role,
            captureOffsetMs,
            skipped = false,
            captureStartMs = startMs,
            captureWindowMs,
            captureActiveWindowCount = captureSegment.ActiveCount,
            captureRms = captureSegment.Rms,
            capturePeakAbs = captureSegment.PeakAbs,
            targetBestScore = targetScore,
            targetBestOffsetMs = targetBest["bestOffsetMs"].GetInt32(),
            targetSourceWindowCount = targetBest["sourceWindowCount"].GetInt32(),
            replacementBestScore = replacementScore,
            replacementBestOffsetMs = replacementBest["bestOffsetMs"].GetInt32(),
            replacementSourceWindowCount = replacementBest["sourceWindowCount"].GetInt32(),
            replacementMinusTarget = replacementScore - targetScore,
            bestMatch = replacementScore > targetScore ? "BEA_02(Master).ogg" : "BEA_04(Master).ogg",
        });
    }
}

AddRows("cleanBaseline", clean, cleanDecodeOffsetMs);
AddRows("stagedPositive", staged, stagedDecodeOffsetMs);

var payload = new
{
    schemaVersion = "winui-safe-copy-music-decode-window-correlation-runner.v1",
    runnerVersion = "decode-window-sliding-source-runner.v1",
    method = "decode-window-sliding-source-rms",
    target = "BEA_04(Master).ogg",
    replacement = "BEA_02(Master).ogg",
    captureWindowMs,
    sourceStrideMs,
    bucketCount,
    minimumActiveWindowCount,
    rawAudioPublished = false,
    sourceAudioPathsPublished = false,
    privateCapturePathsPublished = false,
    analysisRows = rows,
};

Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(outputJson))!);
File.WriteAllText(outputJson, JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine(outputJson);
return 0;
'''


def write_runner(runner_root: Path) -> Path:
    runner_root.mkdir(parents=True, exist_ok=True)
    (runner_root / correlation_builder.RUNNER_MARKER).write_text(
        "tool-owned decode-window correlation runner\n",
        encoding="utf-8",
    )
    project = runner_root / "DecodeWindowCorrelation.csproj"
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


def validate_row(row: dict[str, Any]) -> dict[str, Any]:
    role = string_at(row, "role")
    require(role in {"cleanBaseline", "stagedPositive"}, "Unexpected analysis role.")
    capture_offset = int_at(row, "captureOffsetMs")
    skipped = bool_at(row, "skipped")
    if skipped:
        return {
            "role": role,
            "captureOffsetMs": capture_offset,
            "skipped": True,
            "skipReason": string_at(row, "skipReason"),
        }
    target_score = number_at(row, "targetBestScore")
    replacement_score = number_at(row, "replacementBestScore")
    replacement_minus_target = number_at(row, "replacementMinusTarget")
    require(abs((replacement_score - target_score) - replacement_minus_target) <= 0.000001, "row score margin drifted.")
    best_match = string_at(row, "bestMatch")
    expected_best = REPLACEMENT if replacement_score > target_score else TARGET
    require(best_match == expected_best, "row best match drifted from scores.")
    active_count = int_at(row, "captureActiveWindowCount")
    return {
        "role": role,
        "captureOffsetMs": capture_offset,
        "skipped": False,
        "captureStartMs": number_at(row, "captureStartMs"),
        "captureWindowMs": int_at(row, "captureWindowMs"),
        "captureActiveWindowCount": active_count,
        "captureRms": number_at(row, "captureRms"),
        "capturePeakAbs": number_at(row, "capturePeakAbs"),
        "targetBestScore": target_score,
        "targetBestOffsetMs": int_at(row, "targetBestOffsetMs"),
        "targetSourceWindowCount": int_at(row, "targetSourceWindowCount"),
        "replacementBestScore": replacement_score,
        "replacementBestOffsetMs": int_at(row, "replacementBestOffsetMs"),
        "replacementSourceWindowCount": int_at(row, "replacementSourceWindowCount"),
        "replacementMinusTarget": replacement_minus_target,
        "bestMatch": best_match,
    }


def validate_runner_payload(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == RUNNER_SCHEMA, "Unexpected runner schema.")
    require(payload.get("runnerVersion") == RUNNER_VERSION, "Unexpected runner version.")
    require(payload.get("method") == METHOD, "Unexpected runner method.")
    require(payload.get("target") == TARGET, "Runner target changed.")
    require(payload.get("replacement") == REPLACEMENT, "Runner replacement changed.")
    require(bool_at(payload, "rawAudioPublished") is False, "Runner must not publish raw audio.")
    require(bool_at(payload, "sourceAudioPathsPublished") is False, "Runner must not publish source paths.")
    require(bool_at(payload, "privateCapturePathsPublished") is False, "Runner must not publish private paths.")
    require(not has_private_path_text(payload), "Runner output contains private path-like text.")
    require(not has_forbidden_payload_key(payload), "Runner output contains raw/private payload keys.")
    rows = [validate_row(row) for row in list_at(payload, "analysisRows") if isinstance(row, dict)]
    require(rows, "Runner returned no analysis rows.")
    require(any(row["role"] == "cleanBaseline" for row in rows), "Runner returned no clean baseline rows.")
    require(any(row["role"] == "stagedPositive" for row in rows), "Runner returned no staged positive rows.")
    return {
        "schemaVersion": RUNNER_SCHEMA,
        "runnerVersion": RUNNER_VERSION,
        "method": METHOD,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "captureWindowMs": int_at(payload, "captureWindowMs"),
        "sourceStrideMs": int_at(payload, "sourceStrideMs"),
        "bucketCount": int_at(payload, "bucketCount"),
        "minimumActiveWindowCount": int_at(payload, "minimumActiveWindowCount"),
        "analysisRows": rows,
    }


def best_row(rows: list[dict[str, Any]], *, role: str, prefer_replacement: bool) -> dict[str, Any] | None:
    candidates = [row for row in rows if row["role"] == role and not row["skipped"]]
    if not candidates:
        return None
    key = "replacementMinusTarget" if prefer_replacement else "targetMinusReplacement"
    if prefer_replacement:
        return max(candidates, key=lambda row: float(row["replacementMinusTarget"]))
    return max(candidates, key=lambda row: float(row["targetBestScore"]) - float(row["replacementBestScore"]))


def milliseconds_between(left: Any, right: Any) -> float:
    return (left - right).total_seconds() * 1000.0


def raw_audio_duration_ms(audio_summary: dict[str, Any]) -> float:
    stats = object_at(audio_summary, "audioStats")
    wave_format = object_at(audio_summary, "waveFormat")
    sample_count = number_at(stats, "sampleCount")
    channels = max(1.0, number_at(wave_format, "channels"))
    sample_rate = max(1.0, number_at(wave_format, "sampleRate"))
    return (sample_count / channels / sample_rate) * 1000.0


def build_artifact_from_runner(
    *,
    clean_audio_summary: dict[str, Any],
    staged_audio_summary: dict[str, Any],
    clean_timeline: dict[str, Any],
    staged_timeline: dict[str, Any],
    runner_payload: dict[str, Any],
) -> dict[str, Any]:
    runner = validate_runner_payload(runner_payload)
    rows: list[dict[str, Any]] = runner["analysisRows"]
    clean_best = best_row(rows, role="cleanBaseline", prefer_replacement=False)
    staged_best = best_row(rows, role="stagedPositive", prefer_replacement=True)
    staged_replacement_preferred = staged_best is not None and staged_best["bestMatch"] == REPLACEMENT
    clean_target_preferred = clean_best is not None and clean_best["bestMatch"] == TARGET
    clean_skipped_count = sum(1 for row in rows if row["role"] == "cleanBaseline" and row["skipped"])
    staged_skipped_count = sum(1 for row in rows if row["role"] == "stagedPositive" and row["skipped"])
    clean_row_count = sum(1 for row in rows if row["role"] == "cleanBaseline")
    staged_row_count = sum(1 for row in rows if row["role"] == "stagedPositive")
    clean_decode_offset = milliseconds_between(clean_timeline["_decodeWindowStartAt"], clean_audio_summary["_captureStartAt"])
    staged_decode_offset = milliseconds_between(staged_timeline["_decodeWindowStartAt"], staged_audio_summary["_captureStartAt"])
    clean_duration = raw_audio_duration_ms(clean_audio_summary)
    staged_duration = raw_audio_duration_ms(staged_audio_summary)
    if clean_best is None or staged_best is None:
        conclusion = "decode-window unavailable inside raw audio capture"
    elif staged_replacement_preferred:
        conclusion = "decode-window sliding-source diagnostic prefers the staged replacement track"
    else:
        conclusion = "decode-window sliding-source diagnostic still does not prefer the staged replacement track"
    return {
        "schemaVersion": SCHEMA,
        "diagnosticVersion": "decode-window-correlation-diagnostic.v1",
        "status": "diagnostic-only",
        "presetId": PRESET_ID,
        "levelId": LEVEL_ID,
        "selectionId": SELECTION_ID,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "runtimeAudibleOutputProof": False,
        "method": METHOD,
        "captureWindowMs": runner["captureWindowMs"],
        "sourceStrideMs": runner["sourceStrideMs"],
        "bucketCount": runner["bucketCount"],
        "minimumActiveWindowCount": runner["minimumActiveWindowCount"],
        "cleanDecodeOffsetMs": clean_decode_offset,
        "stagedDecodeOffsetMs": staged_decode_offset,
        "cleanRawAudioDurationMs": clean_duration,
        "stagedRawAudioDurationMs": staged_duration,
        "decodeWindowInsideRawAudioCapture": clean_best is not None and staged_best is not None,
        "cleanTargetPreferredInDecodeWindow": clean_target_preferred,
        "stagedReplacementPreferredInDecodeWindow": staged_replacement_preferred,
        "skippedRowCounts": {
            "cleanBaseline": clean_skipped_count,
            "stagedPositive": staged_skipped_count,
            "cleanBaselineTotal": clean_row_count,
            "stagedPositiveTotal": staged_row_count,
        },
        "cleanBestRow": clean_best,
        "stagedBestRow": staged_best,
        "analysisRows": rows,
        "inputBindings": {
            "cleanAudioJsonSha256": validate_sha(clean_audio_summary["_audioArtifactSha256"], "cleanAudioJsonSha256"),
            "cleanAudioWavSha256": validate_sha(clean_audio_summary["_rawWavSha256"], "cleanAudioWavSha256"),
            "stagedAudioJsonSha256": validate_sha(staged_audio_summary["_audioArtifactSha256"], "stagedAudioJsonSha256"),
            "stagedAudioWavSha256": validate_sha(staged_audio_summary["_rawWavSha256"], "stagedAudioWavSha256"),
            "cleanTimelineSha256": validate_sha(clean_timeline["_timelineSha256"], "cleanTimelineSha256"),
            "stagedTimelineSha256": validate_sha(staged_timeline["_timelineSha256"], "stagedTimelineSha256"),
        },
        "timelineSummary": {
            "cleanBaseline": {
                "musicSelectionProvenance": clean_timeline["musicSelectionProvenance"],
                "rowCounts": clean_timeline["rowCounts"],
            },
            "stagedPositive": {
                "musicSelectionProvenance": staged_timeline["musicSelectionProvenance"],
                "rowCounts": staged_timeline["rowCounts"],
            },
        },
        "diagnosticConclusion": conclusion,
        "claimBoundary": (
            "Replay-only decode-window/sliding-source diagnostic over an existing rejected bundle. "
            "Not accepted capture-source correlation, not materializer input, and not runtime audible-output proof."
        ),
        "nonClaims": REQUIRED_NON_CLAIMS,
    }


def validate_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "Unexpected decode-window diagnostic schema.")
    require(payload.get("status") == "diagnostic-only", "Diagnostic status changed.")
    require(payload.get("presetId") == PRESET_ID, "Preset id changed.")
    require(payload.get("target") == TARGET, "Target track changed.")
    require(payload.get("replacement") == REPLACEMENT, "Replacement track changed.")
    require(payload.get("runtimeAudibleOutputProof") is False, "Diagnostic must not claim audible output.")
    require(payload.get("method") == METHOD, "Diagnostic method changed.")
    require(not has_private_path_text(payload), "Diagnostic contains private path-like text.")
    require(not has_forbidden_payload_key(payload), "Diagnostic contains raw/private payload keys.")
    input_bindings = object_at(payload, "inputBindings")
    for key in {
        "cleanAudioJsonSha256",
        "cleanAudioWavSha256",
        "stagedAudioJsonSha256",
        "stagedAudioWavSha256",
        "cleanTimelineSha256",
        "stagedTimelineSha256",
    }:
        validate_sha(input_bindings.get(key), key)
    clean_best_value = payload.get("cleanBestRow")
    staged_best_value = payload.get("stagedBestRow")
    clean_best = validate_row(clean_best_value) if isinstance(clean_best_value, dict) else None
    staged_best = validate_row(staged_best_value) if isinstance(staged_best_value, dict) else None
    rows = [validate_row(row) for row in list_at(payload, "analysisRows") if isinstance(row, dict)]
    require(rows, "Diagnostic analysis rows missing.")
    inside_capture = bool_at(payload, "decodeWindowInsideRawAudioCapture")
    require(inside_capture == (clean_best is not None and staged_best is not None), "Decode-window availability boolean drifted.")
    if inside_capture:
        require(clean_best is not None, "Diagnostic says decode window is inside capture but has no clean best row.")
        require(staged_best is not None, "Diagnostic says decode window is inside capture but has no staged best row.")
    skipped_counts = object_at(payload, "skippedRowCounts")
    clean_rows = [row for row in rows if row["role"] == "cleanBaseline"]
    staged_rows = [row for row in rows if row["role"] == "stagedPositive"]
    require(int_at(skipped_counts, "cleanBaseline") == sum(1 for row in clean_rows if row["skipped"]), "Clean skipped count drifted.")
    require(int_at(skipped_counts, "stagedPositive") == sum(1 for row in staged_rows if row["skipped"]), "Staged skipped count drifted.")
    require(int_at(skipped_counts, "cleanBaselineTotal") == len(clean_rows), "Clean row total drifted.")
    require(int_at(skipped_counts, "stagedPositiveTotal") == len(staged_rows), "Staged row total drifted.")
    require(
        bool_at(payload, "cleanTargetPreferredInDecodeWindow") == (clean_best is not None and clean_best["bestMatch"] == TARGET),
        "Clean preference boolean drifted.",
    )
    require(
        bool_at(payload, "stagedReplacementPreferredInDecodeWindow")
        == (staged_best is not None and staged_best["bestMatch"] == REPLACEMENT),
        "Staged preference boolean drifted.",
    )
    conclusion = string_at(payload, "diagnosticConclusion")
    if not inside_capture:
        require(conclusion == "decode-window unavailable inside raw audio capture", "Unavailable decode-window conclusion drifted.")
    elif bool_at(payload, "stagedReplacementPreferredInDecodeWindow"):
        require("prefers the staged replacement track" in conclusion, "Replacement-preferred conclusion drifted.")
    else:
        require("still does not prefer the staged replacement track" in conclusion, "Non-replacement conclusion drifted.")
    non_claims = {str(item) for item in list_at(payload, "nonClaims")}
    for token in REQUIRED_NON_CLAIMS:
        require(token in non_claims, f"Missing non-claim: {token}")
    boundary = string_at(payload, "claimBoundary").lower()
    require("not accepted capture-source correlation" in boundary, "Boundary must state this is not accepted capture-source correlation.")
    require("not materializer input" in boundary, "Boundary must state this is not materializer input.")
    require("not runtime audible-output proof" in boundary, "Boundary must state this is not runtime audible-output proof.")
    return {
        "schema": SCHEMA,
        "runtimeAudibleOutputProof": False,
        "decodeWindowInsideRawAudioCapture": inside_capture,
        "cleanBestMatch": clean_best["bestMatch"] if clean_best is not None else "unavailable",
        "stagedBestMatch": staged_best["bestMatch"] if staged_best is not None else "unavailable",
        "cleanMargin": clean_best["targetBestScore"] - clean_best["replacementBestScore"] if clean_best is not None else None,
        "stagedMargin": staged_best["replacementMinusTarget"] if staged_best is not None else None,
        "stagedReplacementPreferredInDecodeWindow": bool_at(payload, "stagedReplacementPreferredInDecodeWindow"),
        "nonClaims": sorted(non_claims),
    }


def run_runner(
    *,
    clean_audio_summary: dict[str, Any],
    staged_audio_summary: dict[str, Any],
    clean_timeline: dict[str, Any],
    staged_timeline: dict[str, Any],
    source_root: Path,
    allowed_output_root: Path,
    capture_window_ms: int,
    capture_offsets_ms: list[int],
    source_stride_ms: int,
    bucket_count: int,
    minimum_active_window_count: int,
    runner_invoker: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    target_path = source_root / TARGET_RELATIVE
    replacement_path = source_root / REPLACEMENT_RELATIVE
    require(target_path.is_file(), f"Missing source target track: {TARGET}")
    require(replacement_path.is_file(), f"Missing source replacement track: {REPLACEMENT}")
    correlation_builder.validate_no_reparse_lexical(target_path)
    correlation_builder.validate_no_reparse_lexical(replacement_path)
    materializer.validate_no_symlink_or_reparse(target_path)
    materializer.validate_no_symlink_or_reparse(replacement_path)
    dotnet = correlation_builder.resolve_dotnet()
    clean_wav = Path(read_json(Path(clean_audio_summary["_audioPath"]))["outputWav"])
    staged_wav = Path(read_json(Path(staged_audio_summary["_audioPath"]))["outputWav"])
    runner_root = Path(tempfile.mkdtemp(prefix="decode-window-correlation-runner-", dir=allowed_output_root))
    try:
        project = write_runner(runner_root)
        runner_output = runner_root / "decode-window-correlation-runner.json"
        command = [
            dotnet,
            "run",
            "--project",
            str(project),
            "--",
            str(runner_output),
            str(target_path),
            str(replacement_path),
            str(clean_wav),
            str(staged_wav),
            f"{milliseconds_between(clean_timeline['_decodeWindowStartAt'], clean_audio_summary['_captureStartAt']):.3f}",
            f"{milliseconds_between(staged_timeline['_decodeWindowStartAt'], staged_audio_summary['_captureStartAt']):.3f}",
            str(capture_window_ms),
            ",".join(str(item) for item in capture_offsets_ms),
            str(source_stride_ms),
            str(bucket_count),
            str(minimum_active_window_count),
        ]
        try:
            result = runner_invoker(
                command,
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
                timeout=RUNNER_TIMEOUT_SECONDS,
                env=sanitize_env(),
            )
        except subprocess.TimeoutExpired as exc:
            raise DecodeWindowCorrelationError("Decode-window correlation runner timed out.") from exc
        if result.returncode != 0:
            raise DecodeWindowCorrelationError("Decode-window correlation runner failed.")
        payload = read_json(runner_output)
        validate_runner_payload(payload)
        return payload
    finally:
        correlation_builder.safe_remove_tool_tree(runner_root)


def build_diagnostic(
    *,
    clean_audio: Path,
    staged_audio: Path,
    clean_timeline: Path,
    staged_timeline: Path,
    source_root: Path,
    allowed_output_root: Path,
    output: Path,
    capture_window_ms: int = DEFAULT_CAPTURE_WINDOW_MS,
    capture_offsets_ms: list[int] | None = None,
    source_stride_ms: int = DEFAULT_SOURCE_STRIDE_MS,
    bucket_count: int = DEFAULT_BUCKET_COUNT,
    minimum_active_window_count: int = DEFAULT_MIN_ACTIVE_WINDOW_COUNT,
    allow_overwrite: bool = False,
    runner_invoker: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    capture_offsets = capture_offsets_ms or list(DEFAULT_CAPTURE_OFFSETS_MS)
    require(capture_window_ms > 0, "capture window must be positive.")
    require(source_stride_ms > 0, "source stride must be positive.")
    require(bucket_count >= 8, "bucket count is too small.")
    require(minimum_active_window_count > 0, "minimum active window count must be positive.")
    try:
        correlation_builder.validate_output_path(
            output=output,
            allowed_output_root=allowed_output_root,
            source_root=source_root,
            allow_overwrite=allow_overwrite,
        )
    except correlation_builder.CaptureSourceCorrelationBuilderError as exc:
        raise DecodeWindowCorrelationError(str(exc)) from exc
    clean_timeline_summary = validate_timeline(clean_timeline, role="cleanBaseline")
    staged_timeline_summary = validate_timeline(staged_timeline, role="stagedPositive")
    try:
        clean_audio_summary = materializer.validate_audio(clean_audio, "cleanBaseline", require_non_silent=True, timeline=clean_timeline_summary)
        staged_audio_summary = materializer.validate_audio(staged_audio, "stagedPositive", require_non_silent=True, timeline=staged_timeline_summary)
        materializer.ensure_same_endpoint_and_format([clean_audio_summary, staged_audio_summary])
    except materializer.MaterializerError as exc:
        raise DecodeWindowCorrelationError(str(exc)) from exc
    clean_audio_summary["_audioPath"] = str(clean_audio)
    staged_audio_summary["_audioPath"] = str(staged_audio)
    runner_payload = run_runner(
        clean_audio_summary=clean_audio_summary,
        staged_audio_summary=staged_audio_summary,
        clean_timeline=clean_timeline_summary,
        staged_timeline=staged_timeline_summary,
        source_root=source_root,
        allowed_output_root=allowed_output_root,
        capture_window_ms=capture_window_ms,
        capture_offsets_ms=capture_offsets,
        source_stride_ms=source_stride_ms,
        bucket_count=bucket_count,
        minimum_active_window_count=minimum_active_window_count,
        runner_invoker=runner_invoker,
    )
    artifact = build_artifact_from_runner(
        clean_audio_summary=clean_audio_summary,
        staged_audio_summary=staged_audio_summary,
        clean_timeline=clean_timeline_summary,
        staged_timeline=staged_timeline_summary,
        runner_payload=runner_payload,
    )
    validate_artifact(artifact)
    write_json(output, artifact)
    return artifact


def runner_fixture() -> dict[str, Any]:
    rows = [
        {
            "role": "cleanBaseline",
            "captureOffsetMs": 0,
            "skipped": False,
            "captureStartMs": 1000.0,
            "captureWindowMs": DEFAULT_CAPTURE_WINDOW_MS,
            "captureActiveWindowCount": 96,
            "captureRms": 0.03,
            "capturePeakAbs": 0.3,
            "targetBestScore": 0.91,
            "targetBestOffsetMs": 41000,
            "targetSourceWindowCount": 120,
            "replacementBestScore": 0.41,
            "replacementBestOffsetMs": 62000,
            "replacementSourceWindowCount": 120,
            "replacementMinusTarget": -0.5,
            "bestMatch": TARGET,
        },
        {
            "role": "stagedPositive",
            "captureOffsetMs": 0,
            "skipped": False,
            "captureStartMs": 1000.0,
            "captureWindowMs": DEFAULT_CAPTURE_WINDOW_MS,
            "captureActiveWindowCount": 97,
            "captureRms": 0.04,
            "capturePeakAbs": 0.4,
            "targetBestScore": 0.38,
            "targetBestOffsetMs": 41000,
            "targetSourceWindowCount": 120,
            "replacementBestScore": 0.88,
            "replacementBestOffsetMs": 64000,
            "replacementSourceWindowCount": 120,
            "replacementMinusTarget": 0.5,
            "bestMatch": REPLACEMENT,
        },
    ]
    return {
        "schemaVersion": RUNNER_SCHEMA,
        "runnerVersion": RUNNER_VERSION,
        "method": METHOD,
        "target": TARGET,
        "replacement": REPLACEMENT,
        "captureWindowMs": DEFAULT_CAPTURE_WINDOW_MS,
        "sourceStrideMs": DEFAULT_SOURCE_STRIDE_MS,
        "bucketCount": DEFAULT_BUCKET_COUNT,
        "minimumActiveWindowCount": DEFAULT_MIN_ACTIVE_WINDOW_COUNT,
        "rawAudioPublished": False,
        "sourceAudioPathsPublished": False,
        "privateCapturePathsPublished": False,
        "analysisRows": rows,
    }


def self_test() -> None:
    import tempfile as _tempfile
    from winui_safe_copy_music_audible_output_materializer_test import write_audio_json
    from winui_safe_copy_music_rejected_replay_diagnostic_check_test import timeline_fixture, write_json

    with _tempfile.TemporaryDirectory(prefix="music-decode-window-self-test-") as temp_dir:
        root = Path(temp_dir)
        clean_audio = write_audio_json(root / "clean" / "cleanBaseline.json", start="2026-06-24T18:50:59Z", end="2026-06-24T18:51:02Z", non_silent=True)
        staged_audio = write_audio_json(root / "staged" / "stagedPositive.json", start="2026-06-24T18:50:59Z", end="2026-06-24T18:51:02Z", non_silent=True)
        clean_live = write_json(root / "clean" / "live.json", {"schemaVersion": "winui-safe-copy-live-runtime-smoke.v1"})
        staged_live = write_json(root / "staged" / "live.json", {"schemaVersion": "winui-safe-copy-live-runtime-smoke.v1"})
        clean_timeline = write_json(root / "clean" / "timeline.json", timeline_fixture(clean_live, role="cleanBaseline"))
        staged_timeline = write_json(root / "staged" / "timeline.json", timeline_fixture(staged_live, role="stagedPositive"))
        source_root = root / "source-game"
        (source_root / "data" / "Music").mkdir(parents=True)
        (source_root / TARGET_RELATIVE).write_bytes(b"OggS-target")
        (source_root / REPLACEMENT_RELATIVE).write_bytes(b"OggS-replacement")
        output_root = root / "out"
        output_root.mkdir()

        def fake_runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            runner_output = Path(command[command.index("--") + 1])
            runner_output.write_text(json.dumps(runner_fixture()), encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

        artifact = build_diagnostic(
            clean_audio=clean_audio,
            staged_audio=staged_audio,
            clean_timeline=clean_timeline,
            staged_timeline=staged_timeline,
            source_root=source_root,
            allowed_output_root=output_root,
            output=output_root / "decode-window-correlation.json",
            runner_invoker=fake_runner,
        )
        validate_artifact(artifact)


def parse_offsets(value: str) -> list[int]:
    if not value.strip():
        return list(DEFAULT_CAPTURE_OFFSETS_MS)
    offsets = [int(item.strip()) for item in value.split(",") if item.strip()]
    require(offsets, "At least one capture offset is required.")
    return offsets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--clean-audio", type=Path)
    parser.add_argument("--staged-audio", type=Path)
    parser.add_argument("--clean-timeline", type=Path)
    parser.add_argument("--staged-timeline", type=Path)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--allowed-output-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--capture-window-ms", type=int, default=DEFAULT_CAPTURE_WINDOW_MS)
    parser.add_argument("--capture-offsets-ms", default=",".join(str(item) for item in DEFAULT_CAPTURE_OFFSETS_MS))
    parser.add_argument("--source-stride-ms", type=int, default=DEFAULT_SOURCE_STRIDE_MS)
    parser.add_argument("--arm-diagnostic", default="")
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music decode-window correlation diagnostic self-test: PASS")
            return 0
        if args.check:
            print(json.dumps(validate_artifact(read_json(args.check)), indent=2, sort_keys=True))
            return 0
        require(args.build, "Use --build, --check, or --self-test.")
        require(args.arm_diagnostic == ARM_PHRASE, f'Refusing diagnostic build without --arm-diagnostic "{ARM_PHRASE}".')
        require(args.clean_audio is not None, "Provide --clean-audio.")
        require(args.staged_audio is not None, "Provide --staged-audio.")
        require(args.clean_timeline is not None, "Provide --clean-timeline.")
        require(args.staged_timeline is not None, "Provide --staged-timeline.")
        require(args.allowed_output_root is not None, "Provide --allowed-output-root.")
        require(args.output is not None, "Provide --output.")
        artifact = build_diagnostic(
            clean_audio=args.clean_audio,
            staged_audio=args.staged_audio,
            clean_timeline=args.clean_timeline,
            staged_timeline=args.staged_timeline,
            source_root=args.source_root,
            allowed_output_root=args.allowed_output_root,
            output=args.output,
            capture_window_ms=args.capture_window_ms,
            capture_offsets_ms=parse_offsets(args.capture_offsets_ms),
            source_stride_ms=args.source_stride_ms,
            allow_overwrite=args.allow_overwrite,
        )
        print(json.dumps(validate_artifact(artifact), indent=2, sort_keys=True))
        return 0
    except (DecodeWindowCorrelationError, materializer.MaterializerError, correlation_builder.CaptureSourceCorrelationBuilderError) as exc:
        print(f"WinUI safe-copy music decode-window correlation diagnostic: FAIL: {materializer.sanitize_error_message(str(exc))}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
