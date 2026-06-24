#!/usr/bin/env python3
"""Tests for the ambient no-BEA process census sidecar producer."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_music_ambient_no_bea_census as census


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_audio_fixture(root: Path, *, start: str = "2026-06-24T00:00:10Z", end: str = "2026-06-24T00:00:20Z") -> Path:
    wav = root / "ambient.wav"
    wav.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt ")
    audio = {
        "schemaVersion": "audio-loopback-capture.v1",
        "status": "captured",
        "captureKind": "wasapi-loopback",
        "captureStartedUtc": start,
        "captureEndedUtc": end,
        "outputJson": str(root / "ambient.json"),
        "outputWav": str(wav),
        "rawWavSha256": sha256_file(wav),
    }
    return write_json(root / "ambient.json", audio)


def write_samples(root: Path, *, include_bea: bool = False) -> Path:
    samples = {
        "schemaVersion": "winui-safe-copy-process-census-samples.v1",
        "samples": [
            {
                "observedAtUtc": "2026-06-24T00:00:09Z",
                "processes": [{"pid": 100, "imageName": "explorer.exe"}],
            },
            {
                "observedAtUtc": "2026-06-24T00:00:15Z",
                "processes": [{"pid": 101, "imageName": "BEA.exe" if include_bea else "notepad.exe"}],
            },
            {
                "observedAtUtc": "2026-06-24T00:00:21Z",
                "processes": [{"pid": 102, "imageName": "pwsh.exe"}],
            },
        ],
    }
    return write_json(root / "samples.json", samples)


class AmbientNoBeaCensusProducerTests(unittest.TestCase):
    def test_builds_materializer_accepted_sidecar_from_audio_and_process_samples(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audio = write_audio_fixture(root)
            samples = write_samples(root)
            output = root / "no-bea-census.json"
            audio_hash = sha256_file(audio)

            payload = census.build_sidecar_from_paths(audio_path=audio, sample_path=samples, output=output)
            summary = census.validate_artifact(payload, artifact_path=output)
            output_exists = output.is_file()

        self.assertEqual("winui-safe-copy-no-bea-process-census.v1", payload["schemaVersion"])
        self.assertEqual("ambientNoBea", payload["role"])
        self.assertTrue(payload["noBeaProcessObserved"])
        self.assertEqual(audio_hash, payload["audioArtifactSha256"])
        self.assertEqual("2026-06-24T00:00:09Z", payload["censusStartUtc"])
        self.assertEqual("2026-06-24T00:00:21Z", payload["censusEndUtc"])
        self.assertEqual(3, summary["sampleCount"])
        self.assertTrue(output_exists)

    def test_rejects_bea_process_in_observed_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audio = write_audio_fixture(root)
            samples = write_samples(root, include_bea=True)

            with self.assertRaises(census.AmbientNoBeaCensusError):
                census.build_sidecar_from_paths(audio_path=audio, sample_path=samples, output=root / "no-bea-census.json")

    def test_accepts_loopback_helper_zero_offset_utc_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audio = write_audio_fixture(
                root,
                start="2026-06-24T00:00:10.1234567+00:00",
                end="2026-06-24T00:00:20.1234567+00:00",
            )
            samples = write_samples(root)
            output = root / "no-bea-census.json"

            payload = census.build_sidecar_from_paths(audio_path=audio, sample_path=samples, output=output)
            summary = census.validate_artifact(payload, artifact_path=output)

        self.assertEqual("2026-06-24T00:00:09Z", payload["censusStartUtc"])
        self.assertEqual(3, summary["sampleCount"])

    def test_cli_self_test_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(Path(census.__file__)), "--self-test"],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("ambient no-BEA census self-test passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
