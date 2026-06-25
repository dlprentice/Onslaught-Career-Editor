#!/usr/bin/env python3
"""Tests for the WASAPI loopback capture helper code generator."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import capture_audio_loopback


class AudioLoopbackCaptureHelperTests(unittest.TestCase):
    def test_runner_hashes_wav_only_after_writer_scope_is_closed(self) -> None:
        source = capture_audio_loopback.runner_source()

        writer_scope = source.index("await using (var writer = new WaveFileWriter(outputWavPath, capture.WaveFormat))")
        hash_line = source.index("string rawWavSha256 = Sha256File(outputWavPath);")
        payload_line = source.index("rawWavSha256 = rawWavSha256,")

        self.assertLess(writer_scope, hash_line)
        self.assertLess(hash_line, payload_line)
        self.assertIn("WaveFileWriter must be disposed before hashing the WAV.", source)

    def test_runner_preserves_wall_clock_gaps_with_silence_padding(self) -> None:
        source = capture_audio_loopback.runner_source()

        self.assertIn("AudioBytesForElapsedMs", source)
        self.assertIn("WriteSilencePadding", source)
        self.assertIn("silencePaddingBytes", source)
        self.assertIn("bytesRecorded = dataBytesWritten", source)
        self.assertIn("wallClockPadding", source)

        started_line = source.index("captureStartedUtc = DateTimeOffset.UtcNow;")
        restart_line = source.index("stopwatch.Restart();")
        start_recording_line = source.index("capture.StartRecording();")
        ended_line = source.index("captureEndedUtc = DateTimeOffset.UtcNow;")
        stop_recording_line = source.index("capture.StopRecording();")
        self.assertLess(started_line, restart_line)
        self.assertLess(restart_line, start_recording_line)
        self.assertLess(ended_line, stop_recording_line)

    def test_validate_rejects_inconsistent_padding_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capture.json"
            payload = {
                "schemaVersion": capture_audio_loopback.SCHEMA,
                "status": "captured",
                "captureKind": "wasapi-loopback",
                "captureStartedUtc": "2026-06-22T00:00:00Z",
                "captureEndedUtc": "2026-06-22T00:00:01Z",
                "requestedDurationMs": 1000,
                "observedDurationMs": 1000,
                "device": {"friendlyName": "self-test"},
                "waveFormat": {"sampleRate": 8000, "channels": 1, "blockAlign": 2, "averageBytesPerSecond": 16000},
                "audioStats": {
                    "bytesRecorded": 16000,
                    "capturedBytes": 1000,
                    "silencePaddingBytes": 1000,
                    "wavFileBytes": 16044,
                    "sampleCount": 8000,
                    "peakAbs": 0.0,
                    "rms": 0.0,
                    "nonSilent": False,
                },
                "wallClockPadding": {
                    "enabled": True,
                    "method": "insert-zero-silence-for-loopback-data-gaps",
                    "capturedBytes": 1000,
                    "silencePaddingBytes": 1000,
                    "dataBytesWritten": 16000,
                    "targetDurationMs": 1000,
                },
                "claimBoundary": "self-test",
                "nonClaims": ["BEA audible playback"],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(capture_audio_loopback.LoopbackError):
                capture_audio_loopback.validate_artifact(path)


if __name__ == "__main__":
    unittest.main()
