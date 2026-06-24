#!/usr/bin/env python3
"""Build or validate source-audio fingerprints for the music audible proof ladder."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "winui-safe-copy-music-source-audio-correlation.v1"
ARM_PHRASE = "FINGERPRINT SOURCE AUDIO"
DEFAULT_SOURCE_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
TRACK_IDS = [REPLACEMENT, TARGET]
NVORBIS_VERSION = "0.10.5"
HELPER_VERSION = "source-audio-correlation-helper.v1"
ENVELOPE_BUCKET_COUNT = 128
MIN_ACTIVE_BUCKET_COUNT = 16
MIN_SOURCE_DISTINCT_MARGIN = 0.15
FORBIDDEN_PAYLOAD_KEYS = {
    "rawpcmbase64",
    "rawpcm",
    "pcmbase64",
    "wavbase64",
    "oggbase64",
    "oggbytes",
    "sourceoggsha256",
    "rawsamples",
    "samples",
    "spectrogram",
    "spectrogrambins",
    "envelopebuckets",
}


class CorrelationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CorrelationError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "Artifact must be a JSON object.")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"Missing list: {key}")
    return child


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
            or "program files" in lowered
            or "steamapps" in lowered
            or str(ROOT).lower() in lowered
        )
    return False


def has_forbidden_payload_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).replace("_", "").replace("-", "").lower()
            if normalized in FORBIDDEN_PAYLOAD_KEYS:
                return True
            if has_forbidden_payload_key(child):
                return True
    elif isinstance(value, list):
        return any(has_forbidden_payload_key(child) for child in value)
    return False


def numeric(value: Any, label: str) -> float:
    require(isinstance(value, (int, float)), f"{label} must be numeric.")
    return float(value)


def validate_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "Unexpected source-audio correlation schema.")
    require(payload.get("helperVersion") == HELPER_VERSION, "Unexpected helper version.")
    require(payload.get("target") == TARGET, "Target track changed.")
    require(payload.get("replacement") == REPLACEMENT, "Replacement track changed.")
    require(payload.get("runtimeAudibleOutputProof") is False, "Source-audio helper must not claim runtime audible output.")
    require(not has_private_path_text(payload), "Artifact contains private path-like text.")
    require(not has_forbidden_payload_key(payload), "Artifact contains raw/private audio payload keys.")

    decode = object_at(payload, "decodeSettings")
    require(decode.get("decoder") == "NVorbis", "Unexpected decoder.")
    require(decode.get("decoderVersion") == NVORBIS_VERSION, "Unexpected decoder version.")
    require(decode.get("channelMix") == "mono-average", "Unexpected channel mix.")
    require(decode.get("envelopeBucketCount") == ENVELOPE_BUCKET_COUNT, "Unexpected envelope bucket count.")
    require(decode.get("fingerprintMaterial") == "track-id|sample-rate|channels|total-frames|quantized-envelope-rms", "Unexpected fingerprint material.")

    tracks = list_at(payload, "tracks")
    require(len(tracks) == 2, "Expected exactly two source tracks.")
    track_ids = sorted(str(track.get("trackId")) for track in tracks if isinstance(track, dict))
    require(track_ids == sorted(TRACK_IDS), "Source track ids changed.")
    fingerprints = []
    for track in tracks:
        require(isinstance(track, dict), "Track row must be an object.")
        require(track.get("trackId") in TRACK_IDS, "Unexpected track id.")
        require(track.get("role") in {"target", "replacement"}, "Unexpected track role.")
        if track.get("trackId") == TARGET:
            require(track.get("role") == "target", "Target track role mismatch.")
        if track.get("trackId") == REPLACEMENT:
            require(track.get("role") == "replacement", "Replacement track role mismatch.")
        require(isinstance(track.get("sampleRate"), int) and track["sampleRate"] > 0, "sampleRate must be positive.")
        require(isinstance(track.get("channels"), int) and track["channels"] > 0, "channels must be positive.")
        require(isinstance(track.get("durationMs"), int) and track["durationMs"] > 0, "durationMs must be positive.")
        require(track.get("envelopeBucketCount") == ENVELOPE_BUCKET_COUNT, "track envelope bucket count changed.")
        require(isinstance(track.get("activeBucketCount"), int) and track["activeBucketCount"] >= MIN_ACTIVE_BUCKET_COUNT, "active bucket count too small.")
        active_ratio = numeric(track.get("activeBucketRatio"), "activeBucketRatio")
        require(0.0 < active_ratio <= 1.0, "active bucket ratio must be normalized and non-zero.")
        require(isinstance(track.get("rms"), (int, float)) and track["rms"] >= 0.0, "rms must be non-negative.")
        require(isinstance(track.get("peakAbs"), (int, float)) and track["peakAbs"] >= 0.0, "peakAbs must be non-negative.")
        fingerprint = track.get("fingerprintSha256")
        require(isinstance(fingerprint, str) and len(fingerprint) == 64, "fingerprint must be a SHA-256 hex string.")
        fingerprints.append(fingerprint)

    source_pair = object_at(payload, "sourcePair")
    require(source_pair.get("fingerprintsDiffer") is True, "Source fingerprints must differ.")
    require(source_pair.get("sourceTracksDistinct") is True, "Source tracks must be marked distinct.")
    require(len(set(fingerprints)) == 2, "Source fingerprints are identical.")
    correlation = numeric(source_pair.get("envelopeCorrelation"), "Envelope correlation")
    require(-1.0 <= correlation <= 1.0, "Envelope correlation must be normalized.")
    margin = numeric(source_pair.get("sourceDistinctMargin"), "sourceDistinctMargin")
    require(margin >= MIN_SOURCE_DISTINCT_MARGIN, "Source distinct margin is too small.")
    require(source_pair.get("minimumRequiredMargin") == MIN_SOURCE_DISTINCT_MARGIN, "Minimum margin changed.")
    score_matrix = object_at(source_pair, "scoreMatrix")
    replacement_self = numeric(score_matrix.get("replacementVsReplacement"), "replacementVsReplacement")
    target_self = numeric(score_matrix.get("targetVsTarget"), "targetVsTarget")
    replacement_cross = numeric(score_matrix.get("replacementVsTarget"), "replacementVsTarget")
    target_cross = numeric(score_matrix.get("targetVsReplacement"), "targetVsReplacement")
    require(replacement_self == 1.0 and target_self == 1.0, "Source self-scores must be 1.0.")
    require(-1.0 <= replacement_cross <= 1.0 and -1.0 <= target_cross <= 1.0, "Cross-scores must be normalized.")
    require(abs(replacement_cross - correlation) <= 0.000001, "Replacement cross-score drifted from envelope correlation.")
    require(abs(target_cross - correlation) <= 0.000001, "Target cross-score drifted from envelope correlation.")
    require(min(replacement_self - abs(replacement_cross), target_self - abs(target_cross)) >= MIN_SOURCE_DISTINCT_MARGIN, "Score margin is too small.")

    non_claims = {str(item) for item in list_at(payload, "nonClaims")}
    for token in {
        "not runtime audible BEA playback",
        "not loopback capture proof",
        "not clean baseline capture proof",
        "not staged positive capture proof",
        "not all music cues",
        "not arbitrary external OGG compatibility",
        "not gameplay parity",
        "not rebuild parity",
    }:
        require(token in non_claims, f"Missing non-claim: {token}")

    return {
        "schema": SCHEMA,
        "trackIds": track_ids,
        "sourceTracksDistinct": True,
        "runtimeAudibleOutputProof": False,
        "envelopeCorrelation": correlation,
        "sourceDistinctMargin": margin,
        "minimumRequiredMargin": MIN_SOURCE_DISTINCT_MARGIN,
    }


def fixture() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA,
        "helperVersion": HELPER_VERSION,
        "generatedAt": "2026-06-22T00:00:00Z",
        "target": TARGET,
        "replacement": REPLACEMENT,
        "runtimeAudibleOutputProof": False,
        "decodeSettings": {
            "decoder": "NVorbis",
            "decoderVersion": NVORBIS_VERSION,
            "channelMix": "mono-average",
            "envelopeBucketCount": ENVELOPE_BUCKET_COUNT,
            "fingerprintMaterial": "track-id|sample-rate|channels|total-frames|quantized-envelope-rms",
        },
        "tracks": [
            {
                "trackId": REPLACEMENT,
                "role": "replacement",
                "sampleRate": 44100,
                "channels": 2,
                "durationMs": 186596,
                "envelopeBucketCount": ENVELOPE_BUCKET_COUNT,
                "activeBucketCount": 119,
                "activeBucketRatio": 0.9296875,
                "rms": 0.102,
                "peakAbs": 0.91,
                "fingerprintSha256": "a" * 64,
            },
            {
                "trackId": TARGET,
                "role": "target",
                "sampleRate": 44100,
                "channels": 2,
                "durationMs": 204000,
                "envelopeBucketCount": ENVELOPE_BUCKET_COUNT,
                "activeBucketCount": 121,
                "activeBucketRatio": 0.9453125,
                "rms": 0.095,
                "peakAbs": 0.88,
                "fingerprintSha256": "b" * 64,
            },
        ],
        "sourcePair": {
            "fingerprintsDiffer": True,
            "sourceTracksDistinct": True,
            "envelopeCorrelation": 0.42,
            "sourceDistinctMargin": 0.58,
            "minimumRequiredMargin": MIN_SOURCE_DISTINCT_MARGIN,
            "scoreMatrix": {
                "replacementVsReplacement": 1.0,
                "targetVsTarget": 1.0,
                "replacementVsTarget": 0.42,
                "targetVsReplacement": 0.42,
            },
        },
        "claimBoundary": "Source-audio fingerprint/correlation reference only. No runtime audible proof.",
        "nonClaims": [
            "not runtime audible BEA playback",
            "not loopback capture proof",
            "not clean baseline capture proof",
            "not staged positive capture proof",
            "not all music cues",
            "not arbitrary external OGG compatibility",
            "not gameplay parity",
            "not rebuild parity",
        ],
    }


def self_test() -> None:
    validate_artifact(fixture())
    for mutator in (
        lambda payload: payload.__setitem__("runtimeAudibleOutputProof", True),
        lambda payload: payload["tracks"][0].__setitem__("sourcePath", str(DEFAULT_SOURCE_ROOT / "data" / "Music" / REPLACEMENT)),
        lambda payload: payload["sourcePair"].__setitem__("fingerprintsDiffer", False),
        lambda payload: payload["sourcePair"].__setitem__("sourceDistinctMargin", 0.01),
        lambda payload: payload["tracks"][0].__setitem__("rawPcmBase64", "AAAA"),
    ):
        payload = fixture()
        mutator(payload)
        try:
            validate_artifact(payload)
        except CorrelationError:
            pass
        else:
            raise CorrelationError("Self-test expected invalid fixture to fail.")


CSHARP_RUNNER = r"""
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using NVorbis;

const int BucketCount = 128;
const double ActiveBucketThresholdRms = 0.0005;

if (args.Length != 3)
{
    Console.Error.WriteLine("usage: SourceAudioFingerprint <output-json> <replacement-ogg> <target-ogg>");
    return 2;
}

string outputJson = args[0];
var inputs = new[]
{
    new { TrackId = "BEA_02(Master).ogg", Role = "replacement", Path = args[1] },
    new { TrackId = "BEA_04(Master).ogg", Role = "target", Path = args[2] },
};

static string Sha256Hex(string text)
{
    byte[] bytes = SHA256.HashData(Encoding.UTF8.GetBytes(text));
    return Convert.ToHexString(bytes).ToLowerInvariant();
}

static (object Row, double[] Buckets, string Fingerprint) Analyze(string trackId, string role, string path)
{
    using var reader = new VorbisReader(path);
    int channels = reader.Channels;
    int sampleRate = reader.SampleRate;
    long totalFrames = reader.TotalSamples;
    var sumSquares = new double[BucketCount];
    var counts = new long[BucketCount];
    var readBuffer = new float[channels * 8192];
    long frameIndex = 0;
    double totalSquare = 0.0;
    double peak = 0.0;
    long totalMonoSamples = 0;

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
            double abs = Math.Abs(mono);
            peak = Math.Max(peak, abs);
            double square = mono * mono;
            totalSquare += square;
            int bucket = totalFrames > 0
                ? (int)Math.Min(BucketCount - 1, (frameIndex * BucketCount) / totalFrames)
                : 0;
            sumSquares[bucket] += square;
            counts[bucket]++;
            frameIndex++;
            totalMonoSamples++;
        }
    }

    var bucketRms = new double[BucketCount];
    for (int index = 0; index < BucketCount; index++)
        bucketRms[index] = counts[index] == 0 ? 0.0 : Math.Sqrt(sumSquares[index] / counts[index]);
    string bucketText = string.Join(",", bucketRms.Select(value => value.ToString("F8", CultureInfo.InvariantCulture)));
    double rms = totalMonoSamples == 0 ? 0.0 : Math.Sqrt(totalSquare / totalMonoSamples);
    int activeBucketCount = bucketRms.Count(value => value > ActiveBucketThresholdRms);
    double activeBucketRatio = (double)activeBucketCount / BucketCount;
    string fingerprint = Sha256Hex($"{trackId}|{sampleRate}|{channels}|{totalFrames}|{bucketText}");
    long durationMs = sampleRate <= 0 ? 0 : (long)Math.Round(totalFrames * 1000.0 / sampleRate);
    object row = new
    {
        trackId,
        role,
        sampleRate,
        channels,
        durationMs,
        envelopeBucketCount = BucketCount,
        activeBucketCount,
        activeBucketRatio,
        rms,
        peakAbs = peak,
        fingerprintSha256 = fingerprint,
    };
    return (row, bucketRms, fingerprint);
}

static double Correlate(double[] left, double[] right)
{
    double leftMean = left.Average();
    double rightMean = right.Average();
    double numerator = 0.0;
    double leftDen = 0.0;
    double rightDen = 0.0;
    for (int index = 0; index < left.Length; index++)
    {
        double l = left[index] - leftMean;
        double r = right[index] - rightMean;
        numerator += l * r;
        leftDen += l * l;
        rightDen += r * r;
    }
    if (leftDen <= 0.0 || rightDen <= 0.0)
        return 0.0;
    return numerator / Math.Sqrt(leftDen * rightDen);
}

var replacement = Analyze(inputs[0].TrackId, inputs[0].Role, inputs[0].Path);
var target = Analyze(inputs[1].TrackId, inputs[1].Role, inputs[1].Path);
double correlation = Correlate(replacement.Buckets, target.Buckets);
bool differ = !string.Equals(replacement.Fingerprint, target.Fingerprint, StringComparison.OrdinalIgnoreCase);
double sourceDistinctMargin = Math.Min(1.0 - Math.Abs(correlation), 1.0 - Math.Abs(correlation));

var payload = new
{
    schemaVersion = "winui-safe-copy-music-source-audio-correlation.v1",
    helperVersion = "source-audio-correlation-helper.v1",
    generatedAt = DateTimeOffset.UtcNow,
    target = "BEA_04(Master).ogg",
    replacement = "BEA_02(Master).ogg",
    runtimeAudibleOutputProof = false,
    decodeSettings = new
    {
        decoder = "NVorbis",
        decoderVersion = "0.10.5",
        channelMix = "mono-average",
        envelopeBucketCount = BucketCount,
        fingerprintMaterial = "track-id|sample-rate|channels|total-frames|quantized-envelope-rms",
    },
    tracks = new[] { replacement.Row, target.Row },
    sourcePair = new
    {
        fingerprintsDiffer = differ,
        sourceTracksDistinct = differ && sourceDistinctMargin >= 0.15,
        envelopeCorrelation = correlation,
        sourceDistinctMargin,
        minimumRequiredMargin = 0.15,
        scoreMatrix = new
        {
            replacementVsReplacement = 1.0,
            targetVsTarget = 1.0,
            replacementVsTarget = correlation,
            targetVsReplacement = correlation,
        },
    },
    claimBoundary = "Source-audio fingerprint/correlation reference only. No runtime audible proof.",
    nonClaims = new[]
    {
        "not runtime audible BEA playback",
        "not loopback capture proof",
        "not clean baseline capture proof",
        "not staged positive capture proof",
        "not all music cues",
        "not arbitrary external OGG compatibility",
        "not gameplay parity",
        "not rebuild parity",
    },
};

Directory.CreateDirectory(Path.GetDirectoryName(outputJson)!);
File.WriteAllText(outputJson, JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine(outputJson);
return differ ? 0 : 2;
"""


def write_runner(runner_root: Path) -> Path:
    runner_root.mkdir(parents=True, exist_ok=True)
    (runner_root / "SourceAudioFingerprint.csproj").write_text(
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
    return runner_root / "SourceAudioFingerprint.csproj"


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def build_artifact(args: argparse.Namespace) -> dict[str, Any]:
    require(args.arm_source_audio == ARM_PHRASE, f'Refusing source-audio fingerprint without --arm-source-audio "{ARM_PHRASE}".')
    source_root = Path(args.source_root).resolve()
    allowed_root = Path(args.allowed_output_root).resolve()
    output_json = Path(args.output_json).resolve()
    require(source_root.is_dir(), "Source game root does not exist.")
    require(allowed_root.exists() and allowed_root.is_dir(), "Allowed output root must already exist.")
    require(is_same_or_under(output_json, allowed_root), "Output JSON must stay under the allowed output root.")
    require(not is_same_or_under(allowed_root, source_root), "Allowed output root must not be under the source game root.")
    require(not is_same_or_under(source_root, allowed_root), "Source game root must not be under the allowed output root.")
    require(output_json.suffix.lower() == ".json", "Output path must end in .json.")
    if output_json.exists():
        require(args.allow_overwrite, "Output JSON already exists; use --allow-overwrite.")

    replacement_path = source_root / "data" / "Music" / REPLACEMENT
    target_path = source_root / "data" / "Music" / TARGET
    require(replacement_path.is_file(), f"Missing replacement track: {REPLACEMENT}")
    require(target_path.is_file(), f"Missing target track: {TARGET}")

    runner_root = allowed_root / "source-audio-fingerprint-runner"
    project = write_runner(runner_root)
    command = ["dotnet", "run", "--project", str(project), "--", str(output_json), str(replacement_path), str(target_path)]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (allowed_root / "source-audio-fingerprint-stdout.log").write_text(result.stdout, encoding="utf-8")
    (allowed_root / "source-audio-fingerprint-stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise CorrelationError(result.stderr.strip() or result.stdout.strip() or "Source-audio fingerprint runner failed.")
    return validate_artifact(read_json(output_json))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fingerprint", action="store_true")
    parser.add_argument("--check", default="")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--allowed-output-root", default="")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--arm-source-audio", default="")
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music source-audio correlation checker self-test: PASS")
            return 0
        if args.check:
            print(json.dumps(validate_artifact(read_json(Path(args.check))), indent=2, sort_keys=True))
            return 0
        require(args.fingerprint, "Use --fingerprint, --check, or --self-test.")
        require(args.allowed_output_root and args.output_json, "--fingerprint requires --allowed-output-root and --output-json.")
        print(json.dumps(build_artifact(args), indent=2, sort_keys=True))
        return 0
    except CorrelationError as exc:
        print(f"WinUI safe-copy music source-audio correlation check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
