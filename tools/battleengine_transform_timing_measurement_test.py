#!/usr/bin/env python3
"""Unit tests for transform morph timing harness."""

from __future__ import annotations

import unittest

import battleengine_transform_timing_measurement as morph


class TransformTimingTests(unittest.TestCase):
    def test_synthetic_accepts(self) -> None:
        samples, request = morph.synthetic_transform_series(morph_delay_ms=200)
        m = morph.analyze_transform_timing(
            attempt=1, samples=samples, frequency=10_000_000, morph_request_tick=request
        )
        self.assertTrue(m.accepted)
        self.assertGreaterEqual(m.morph_latency_ms[0], 0)
        self.assertGreaterEqual(m.morph_latency_ms[1], m.morph_latency_ms[0])
        self.assertIn(morph.JET_STATE, m.states_seen)

    def test_rejects_no_jet(self) -> None:
        samples = [morph.StateSample(tick=i * 100_000, state_raw=morph.WALKER_STATE) for i in range(40)]
        with self.assertRaisesRegex(morph.TransformTimingError, "jet state"):
            morph.analyze_transform_timing(
                attempt=1,
                samples=samples,
                frequency=10_000_000,
                morph_request_tick=0,
            )


if __name__ == "__main__":
    unittest.main()
