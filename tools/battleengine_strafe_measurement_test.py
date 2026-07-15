#!/usr/bin/env python3
"""Unit tests for strafe/lateral measurement (no live BEA)."""

from __future__ import annotations

import unittest

import battleengine_strafe_measurement as strafe


class StrafeAnalysisTests(unittest.TestCase):
    def test_synthetic_accepts(self) -> None:
        frequency = 10_000_000
        b, h, r = strafe.synthetic_strafe_attempt(attempt=1, steady_speed=2.5)
        m = strafe.analyze_strafe_attempt(
            attempt=1, baseline=b, hold=h, release=r, frequency=frequency
        )
        self.assertTrue(m.accepted)
        self.assertGreater(m.steady_lateral_speed, 2.0)
        self.assertGreater(m.hold_endpoint_displacement, 1.0)

    def test_rejects_static_hold(self) -> None:
        frequency = 10_000_000
        b, h, r = strafe.synthetic_strafe_attempt(
            attempt=1, steady_speed=0.0, baseline_speed=0.0
        )
        with self.assertRaisesRegex(strafe.StrafeError, "positive|dominate|undersampled"):
            strafe.analyze_strafe_attempt(
                attempt=1, baseline=b, hold=h, release=r, frequency=frequency
            )


if __name__ == "__main__":
    unittest.main()
