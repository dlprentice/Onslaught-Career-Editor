#!/usr/bin/env python3
"""Tests for shield rate scaffold."""

from __future__ import annotations

import unittest

import battleengine_shield_scaffold as shield


class ShieldScaffoldTests(unittest.TestCase):
    def test_regen(self) -> None:
        samples = shield.synthetic_shield_series(rate_per_sec=2.0)
        m = shield.analyze_shield_rate(
            attempt=1, samples=samples, frequency=10_000_000, expect_positive=True
        )
        self.assertTrue(m.accepted)
        self.assertGreater(m.steady_rate_per_sec, 1.0)

    def test_pair_envelope(self) -> None:
        frequency = 10_000_000
        m1 = shield.analyze_shield_rate(
            attempt=1,
            samples=shield.synthetic_shield_series(rate_per_sec=2.0),
            frequency=frequency,
        )
        m2 = shield.analyze_shield_rate(
            attempt=2,
            samples=shield.synthetic_shield_series(rate_per_sec=2.1),
            frequency=frequency,
        )
        envelope = shield.materialize_shield_pair_envelope(m1, m2)
        self.assertEqual(
            "battleengine-shield-rate-scalar-response.v0-scaffold",
            envelope["schemaVersion"],
        )
        self.assertEqual("0x100", envelope["offsetHypothesis"]["battleEngineShields"])


if __name__ == "__main__":
    unittest.main()
