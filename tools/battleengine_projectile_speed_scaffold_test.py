#!/usr/bin/env python3
"""Tests for projectile speed scaffold."""

from __future__ import annotations

import unittest

import battleengine_projectile_speed_scaffold as proj


class ProjectileScaffoldTests(unittest.TestCase):
    def test_synthetic_accepts(self) -> None:
        samples = proj.synthetic_projectile_series(speed=40.0)
        m = proj.analyze_projectile_speed(
            attempt=1, samples=samples, frequency=10_000_000
        )
        self.assertTrue(m.accepted)
        self.assertAlmostEqual(40.0, m.steady_speed, delta=1.0)


if __name__ == "__main__":
    unittest.main()
