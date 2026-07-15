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


if __name__ == "__main__":
    unittest.main()
