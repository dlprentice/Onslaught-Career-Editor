#!/usr/bin/env python3
"""Tests for coast/friction release scaffold (no live BEA)."""

from __future__ import annotations

import unittest

import battleengine_coast_friction_measurement as coast


class CoastFrictionTests(unittest.TestCase):
    def test_synthetic_attempt_and_pair_envelope(self) -> None:
        frequency = 10_000_000
        h1, r1 = coast.synthetic_coast_attempt(attempt=1, half_life_ms=180.0)
        h2, r2 = coast.synthetic_coast_attempt(attempt=2, half_life_ms=200.0)
        m1 = coast.analyze_coast_attempt(
            attempt=1, hold=h1, release=r1, frequency=frequency
        )
        m2 = coast.analyze_coast_attempt(
            attempt=2, hold=h2, release=r2, frequency=frequency
        )
        self.assertTrue(m1.accepted)
        self.assertTrue(m2.accepted)
        self.assertGreater(m1.hold_steady_speed, 1.0)
        self.assertGreater(m1.release_half_life_ms, 50.0)
        envelope = coast.materialize_coast_pair_envelope(m1, m2)
        self.assertEqual(
            "battleengine-coast-friction-response.v0-scaffold",
            envelope["schemaVersion"],
        )

    def test_pair_envelope_rejects_unstable_half_lives(self) -> None:
        frequency = 10_000_000
        h1, r1 = coast.synthetic_coast_attempt(attempt=1, half_life_ms=100.0)
        h2, r2 = coast.synthetic_coast_attempt(attempt=2, half_life_ms=400.0)
        m1 = coast.analyze_coast_attempt(
            attempt=1, hold=h1, release=r1, frequency=frequency
        )
        m2 = coast.analyze_coast_attempt(
            attempt=2, hold=h2, release=r2, frequency=frequency
        )
        with self.assertRaisesRegex(coast.CoastFrictionError, "not stable"):
            coast.materialize_coast_pair_envelope(m1, m2)

    def test_rejects_no_decay(self) -> None:
        frequency = 10_000_000
        step = frequency // 100
        hold = [
            coast.CoastSample(tick=i * step, phase="hold", position=(0.0, 0.0, i * 0.03))
            for i in range(20)
        ]
        # Release continues at full speed — never reaches half.
        release = [
            coast.CoastSample(
                tick=(20 + i) * step,
                phase="release",
                position=(0.0, 0.0, (20 + i) * 0.03),
            )
            for i in range(20)
        ]
        with self.assertRaisesRegex(coast.CoastFrictionError, "half"):
            coast.analyze_coast_attempt(
                attempt=1, hold=hold, release=release, frequency=frequency
            )


if __name__ == "__main__":
    unittest.main()
