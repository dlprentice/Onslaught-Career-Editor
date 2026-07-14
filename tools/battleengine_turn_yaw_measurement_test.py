#!/usr/bin/env python3
"""Unit tests for turn/yaw measurement harness (no live BEA)."""

from __future__ import annotations

import math
import unittest

import battleengine_turn_yaw_measurement as turn


class HeadingAndRateTests(unittest.TestCase):
    def test_heading_from_velocity_xz_cardinals(self) -> None:
        self.assertAlmostEqual(0.0, turn.heading_from_velocity_xz(0.0, 1.0), places=6)
        self.assertAlmostEqual(math.pi / 2, turn.heading_from_velocity_xz(1.0, 0.0), places=6)
        self.assertAlmostEqual(-math.pi / 2, turn.heading_from_velocity_xz(-1.0, 0.0), places=6)

    def test_heading_rejects_near_zero_velocity(self) -> None:
        with self.assertRaisesRegex(turn.TurnYawError, "near-zero"):
            turn.heading_from_velocity_xz(0.0, 0.0)

    def test_unwrap_delta_shortest_path_across_pi(self) -> None:
        delta = turn.unwrap_delta(math.pi - 0.1, -math.pi + 0.1)
        self.assertAlmostEqual(0.2, delta, places=6)

    def test_phase_yaw_rates_recover_constant_rate(self) -> None:
        frequency = 10_000_000
        step = frequency // 100  # 10 ms
        rate = 1.5
        samples = []
        heading = 0.0
        for index in range(12):
            samples.append(turn.YawSample(tick=index * step, phase="hold", heading_rad=heading))
            heading += rate * 0.01
        rows = turn.phase_yaw_rates(samples, frequency)
        med = sorted(r for _, r in rows)[len(rows) // 2]
        self.assertAlmostEqual(rate, med, delta=0.05)


class AnalyzeAndEnvelopeTests(unittest.TestCase):
    def test_synthetic_attempt_accepts_and_builds_pair_envelope(self) -> None:
        frequency = 10_000_000
        b1, h1, r1 = turn.synthetic_turn_attempt(attempt=1, steady_rate=1.45)
        b2, h2, r2 = turn.synthetic_turn_attempt(attempt=2, steady_rate=1.48)
        m1 = turn.analyze_turn_attempt(
            attempt=1, baseline=b1, hold=h1, release=r1, frequency=frequency
        )
        m2 = turn.analyze_turn_attempt(
            attempt=2, baseline=b2, hold=h2, release=r2, frequency=frequency
        )
        self.assertTrue(m1.accepted)
        self.assertTrue(m2.accepted)
        self.assertGreater(m1.steady_yaw_rate_rad_s, 1.0)
        envelope = turn.materialize_turn_pair_envelope(m1, m2)
        self.assertEqual(
            "battleengine-walker-turn-yaw-scalar-response.v0-scaffold",
            envelope["schemaVersion"],
        )
        band = envelope["envelope"]["steadyYawRateRadPerSec"]
        self.assertLess(band["lower"], band["upper"])
        self.assertIn("No deterministic Core", " ".join(envelope["nonclaims"]))

    def test_rejects_weak_turn_vs_baseline(self) -> None:
        frequency = 10_000_000
        baseline, hold, release = turn.synthetic_turn_attempt(
            attempt=1, steady_rate=0.05, baseline_rate=0.04
        )
        with self.assertRaisesRegex(turn.TurnYawError, "dominate baseline"):
            turn.analyze_turn_attempt(
                attempt=1,
                baseline=baseline,
                hold=hold,
                release=release,
                frequency=frequency,
            )

    def test_rejects_unstable_pair_envelope(self) -> None:
        frequency = 10_000_000
        b1, h1, r1 = turn.synthetic_turn_attempt(attempt=1, steady_rate=1.0)
        b2, h2, r2 = turn.synthetic_turn_attempt(attempt=2, steady_rate=2.0)
        m1 = turn.analyze_turn_attempt(
            attempt=1, baseline=b1, hold=h1, release=r1, frequency=frequency
        )
        m2 = turn.analyze_turn_attempt(
            attempt=2, baseline=b2, hold=h2, release=r2, frequency=frequency
        )
        with self.assertRaisesRegex(turn.TurnYawError, "not stable"):
            turn.materialize_turn_pair_envelope(m1, m2)

    def test_yaw_axis_offset_hypothesis_is_explicit(self) -> None:
        self.assertEqual(0x278, turn.BATTLE_ENGINE_YAW_AXIS_OFFSET)
        self.assertEqual(1.5, turn.SOURCE_GROUND_TURN_RATE_HYPOTHESIS)


if __name__ == "__main__":
    unittest.main()
