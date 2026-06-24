#!/usr/bin/env python3
"""Build and validate the ambient no-BEA process census sidecar.

This producer is deliberately narrow. It does not launch BEA, attach CDB,
capture audio, or claim audible music output. It binds an existing ambient
loopback audio JSON/WAV artifact to process samples that cover that ambient
capture window and proves no BEA.exe process was observed in those samples.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


SCHEMA = "winui-safe-copy-no-bea-process-census.v1"
SAMPLE_SCHEMA = "winui-safe-copy-process-census-samples.v1"
AUDIO_SCHEMA = "audio-loopback-capture.v1"
ROLE = "ambientNoBea"
BEA_IMAGE_NAME = "bea.exe"
NON_CLAIMS = [
    "not audible-output proof",
    "not a BEA launch",
    "not a CDB attach",
    "not a loopback capture",
    "not source-audio correlation",
    "not gameplay parity",
    "not rebuild parity",
    "not no-noticeable-difference parity",
]


class AmbientNoBeaCensusError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AmbientNoBeaCensusError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing JSON input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(payload, dict), f"JSON input must be an object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_utc(value: Any, label: str) -> dt.datetime:
    require(isinstance(value, str), f"{label} must be a UTC timestamp.")
    require(value.endswith("Z") or value.endswith("+00:00"), f"{label} must be a UTC timestamp.")
    try:
        parsed = dt.datetime.fromisoformat(value.removesuffix("Z") + "+00:00" if value.endswith("Z") else value)
    except ValueError as exc:
        raise AmbientNoBeaCensusError(f"{label} is not a valid UTC timestamp.") from exc
    return parsed.astimezone(dt.timezone.utc)


def format_utc(value: dt.datetime) -> str:
    value = value.astimezone(dt.timezone.utc)
    if value.microsecond:
        text = value.isoformat(timespec="milliseconds")
    else:
        text = value.isoformat(timespec="seconds")
    return text.replace("+00:00", "Z")


def same_path(left: Path, right: Path) -> bool:
    return left.resolve() == right.resolve()


def image_basename(value: Any) -> str:
    text = str(value or "").replace("/", "\\")
    return text.rsplit("\\", 1)[-1].lower()


def validate_audio(audio_path: Path) -> dict[str, Any]:
    payload = read_json(audio_path)
    require(payload.get("schemaVersion") == AUDIO_SCHEMA, "Ambient audio schema changed.")
    require(payload.get("status") == "captured", "Ambient audio was not captured.")
    require(payload.get("captureKind") == "wasapi-loopback", "Ambient audio capture kind changed.")
    require(same_path(Path(str(payload.get("outputJson"))), audio_path), "Ambient audio outputJson does not point at the input artifact.")
    wav_path = Path(str(payload.get("outputWav")))
    require(wav_path.is_file(), "Ambient raw WAV artifact is missing.")
    raw_wav_hash = payload.get("rawWavSha256")
    require(isinstance(raw_wav_hash, str) and len(raw_wav_hash) == 64, "Ambient rawWavSha256 is missing.")
    require(raw_wav_hash.lower() == sha256_file(wav_path), "Ambient rawWavSha256 does not match the raw WAV.")
    capture_start = parse_utc(payload.get("captureStartedUtc"), "captureStartedUtc")
    capture_end = parse_utc(payload.get("captureEndedUtc"), "captureEndedUtc")
    require(capture_start < capture_end, "Ambient audio capture window is not positive.")
    return {
        "path": audio_path,
        "payload": payload,
        "captureStart": capture_start,
        "captureEnd": capture_end,
        "artifactSha256": sha256_file(audio_path),
        "wavSha256": raw_wav_hash.lower(),
    }


def validate_samples(sample_payload: dict[str, Any], audio: dict[str, Any]) -> dict[str, Any]:
    require(sample_payload.get("schemaVersion") == SAMPLE_SCHEMA, "Process sample schema changed.")
    samples = sample_payload.get("samples")
    require(isinstance(samples, list) and samples, "Process samples are missing.")

    observed_times: list[dt.datetime] = []
    sample_summaries: list[dict[str, Any]] = []
    bea_matches: list[dict[str, Any]] = []
    for index, sample in enumerate(samples):
        require(isinstance(sample, dict), f"Process sample {index} must be an object.")
        observed_at = parse_utc(sample.get("observedAtUtc"), f"samples[{index}].observedAtUtc")
        processes = sample.get("processes")
        require(isinstance(processes, list), f"samples[{index}].processes must be a list.")
        observed_times.append(observed_at)
        process_count = 0
        for process in processes:
            require(isinstance(process, dict), f"samples[{index}] process row must be an object.")
            process_count += 1
            name = image_basename(process.get("imageName"))
            if name == BEA_IMAGE_NAME:
                bea_matches.append(
                    {
                        "sampleIndex": index,
                        "observedAtUtc": format_utc(observed_at),
                        "pid": process.get("pid"),
                        "imageName": "BEA.exe",
                    }
                )
        sample_summaries.append(
            {
                "observedAtUtc": format_utc(observed_at),
                "processCount": process_count,
            }
        )

    census_start = min(observed_times)
    census_end = max(observed_times)
    require(census_start <= audio["captureStart"], "Process census starts after ambient audio capture starts.")
    require(census_end >= audio["captureEnd"], "Process census ends before ambient audio capture ends.")
    require(not bea_matches, "BEA.exe was observed during the ambient no-BEA census.")
    return {
        "censusStart": census_start,
        "censusEnd": census_end,
        "sampleCount": len(samples),
        "processSampleSummaries": sample_summaries,
        "beaProcessMatches": bea_matches,
    }


def build_sidecar(audio_path: Path, sample_payload: dict[str, Any]) -> dict[str, Any]:
    audio = validate_audio(audio_path)
    samples = validate_samples(sample_payload, audio)
    return {
        "schemaVersion": SCHEMA,
        "role": ROLE,
        "generatedAtUtc": format_utc(dt.datetime.now(dt.timezone.utc)),
        "noBeaProcessObserved": True,
        "audioArtifactSha256": audio["artifactSha256"],
        "audioWavSha256": audio["wavSha256"],
        "censusStartUtc": format_utc(samples["censusStart"]),
        "censusEndUtc": format_utc(samples["censusEnd"]),
        "sampleCount": samples["sampleCount"],
        "processNameNeedles": ["BEA.exe"],
        "processSampleSummaries": samples["processSampleSummaries"],
        "beaProcessMatches": [],
        "claimBoundary": "Ambient process census sidecar only; no BEA launch, audio capture, CDB attach, or audible-output proof.",
        "nonClaims": NON_CLAIMS,
    }


def build_sidecar_from_paths(*, audio_path: Path, sample_path: Path, output: Path) -> dict[str, Any]:
    payload = build_sidecar(audio_path, read_json(sample_path))
    write_json(output, payload)
    return payload


def validate_artifact(payload: dict[str, Any], *, artifact_path: Path | None = None) -> dict[str, Any]:
    if artifact_path is not None:
        payload = read_json(artifact_path)
    require(payload.get("schemaVersion") == SCHEMA, "Ambient no-BEA census schema changed.")
    require(payload.get("role") == ROLE, "Ambient no-BEA census role mismatch.")
    require(payload.get("noBeaProcessObserved") is True, "Ambient no-BEA census did not prove no BEA process.")
    for key in ("audioArtifactSha256", "audioWavSha256"):
        value = payload.get(key)
        require(isinstance(value, str) and len(value) == 64, f"{key} must be a SHA-256 hex string.")
    start = parse_utc(payload.get("censusStartUtc"), "censusStartUtc")
    end = parse_utc(payload.get("censusEndUtc"), "censusEndUtc")
    require(start < end, "Ambient no-BEA census window is not positive.")
    sample_count = payload.get("sampleCount")
    require(isinstance(sample_count, int) and sample_count > 0, "sampleCount must be positive.")
    matches = payload.get("beaProcessMatches")
    require(isinstance(matches, list) and not matches, "BEA process matches must be empty.")
    return {
        "schemaVersion": SCHEMA,
        "role": ROLE,
        "noBeaProcessObserved": True,
        "sampleCount": sample_count,
        "censusStartUtc": payload["censusStartUtc"],
        "censusEndUtc": payload["censusEndUtc"],
    }


def parse_tasklist_csv(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    reader = csv.reader(io.StringIO(text))
    for row in reader:
        if len(row) < 2:
            continue
        image_name = row[0].strip()
        pid_text = row[1].strip()
        if image_name.lower() == "image name":
            continue
        try:
            pid: int | str = int(pid_text)
        except ValueError:
            pid = pid_text
        rows.append({"imageName": image_name, "pid": pid})
    return rows


def capture_process_sample() -> dict[str, Any]:
    result = subprocess.run(["tasklist", "/fo", "csv"], capture_output=True, check=False, text=True)
    require(result.returncode == 0, f"tasklist failed: {result.stderr.strip()}")
    return {
        "observedAtUtc": format_utc(dt.datetime.now(dt.timezone.utc)),
        "processes": parse_tasklist_csv(result.stdout),
    }


def observe_process_samples(*, observe_ms: int, poll_ms: int) -> dict[str, Any]:
    require(observe_ms > 0, "--observe-ms must be positive.")
    require(poll_ms > 0, "--poll-ms must be positive.")
    deadline = time.monotonic() + (observe_ms / 1000.0)
    samples: list[dict[str, Any]] = []
    while True:
        samples.append(capture_process_sample())
        if time.monotonic() >= deadline:
            break
        time.sleep(min(poll_ms / 1000.0, max(0.0, deadline - time.monotonic())))
    return {"schemaVersion": SAMPLE_SCHEMA, "samples": samples}


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="ambient-no-bea-census-") as temp_dir:
        root = Path(temp_dir)
        wav = root / "ambient.wav"
        wav.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt ")
        audio = {
            "schemaVersion": AUDIO_SCHEMA,
            "status": "captured",
            "captureKind": "wasapi-loopback",
            "captureStartedUtc": "2026-06-24T00:00:10Z",
            "captureEndedUtc": "2026-06-24T00:00:20Z",
            "outputJson": str(root / "ambient.json"),
            "outputWav": str(wav),
            "rawWavSha256": sha256_file(wav),
        }
        audio_path = root / "ambient.json"
        write_json(audio_path, audio)
        sample_path = root / "samples.json"
        write_json(
            sample_path,
            {
                "schemaVersion": SAMPLE_SCHEMA,
                "samples": [
                    {"observedAtUtc": "2026-06-24T00:00:09Z", "processes": [{"pid": 1, "imageName": "pwsh.exe"}]},
                    {"observedAtUtc": "2026-06-24T00:00:21Z", "processes": [{"pid": 2, "imageName": "explorer.exe"}]},
                ],
            },
        )
        output = root / "no-bea-census.json"
        payload = build_sidecar_from_paths(audio_path=audio_path, sample_path=sample_path, output=output)
        validate_artifact(payload, artifact_path=output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, help="Ambient audio-loopback JSON artifact.")
    parser.add_argument("--sample-file", type=Path, help="Process sample JSON captured across the ambient audio window.")
    parser.add_argument("--output", type=Path, help="Output no-BEA census sidecar JSON.")
    parser.add_argument("--observe-ms", type=int, default=0, help="Capture process samples for this many milliseconds.")
    parser.add_argument("--poll-ms", type=int, default=250, help="Process sample polling interval for --observe-ms.")
    parser.add_argument("--write-samples", type=Path, help="Optional path to write raw process samples from --observe-ms.")
    parser.add_argument("--check", type=Path, help="Validate an existing no-BEA census sidecar.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("ambient no-BEA census self-test passed")
            return 0
        if args.check:
            summary = validate_artifact(read_json(args.check), artifact_path=args.check)
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0
        require(args.audio is not None and args.output is not None, "--audio and --output are required.")
        if args.sample_file:
            sample_payload = read_json(args.sample_file)
        else:
            require(args.observe_ms > 0, "Either --sample-file or --observe-ms is required.")
            sample_payload = observe_process_samples(observe_ms=args.observe_ms, poll_ms=args.poll_ms)
            if args.write_samples:
                write_json(args.write_samples, sample_payload)
        payload = build_sidecar(args.audio, sample_payload)
        write_json(args.output, payload)
        summary = validate_artifact(payload, artifact_path=args.output)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except AmbientNoBeaCensusError as exc:
        print(f"WinUI safe-copy music ambient no-BEA census: FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
