#!/usr/bin/env python3
"""Tests for the WASAPI loopback capture helper code generator."""

from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
