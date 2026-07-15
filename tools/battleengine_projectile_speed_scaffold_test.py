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

    def test_pair_envelope(self) -> None:
        frequency = 10_000_000
        m1 = proj.analyze_projectile_speed(
            attempt=1,
            samples=proj.synthetic_projectile_series(speed=40.0),
            frequency=frequency,
        )
        m2 = proj.analyze_projectile_speed(
            attempt=2,
            samples=proj.synthetic_projectile_series(speed=41.0),
            frequency=frequency,
        )
        envelope = proj.materialize_projectile_pair_envelope(m1, m2)
        self.assertEqual(
            "battleengine-projectile-speed-scalar-response.v0-scaffold",
            envelope["schemaVersion"],
        )

    def test_pair_envelope_rejects_unstable(self) -> None:
        frequency = 10_000_000
        m1 = proj.analyze_projectile_speed(
            attempt=1,
            samples=proj.synthetic_projectile_series(speed=20.0),
            frequency=frequency,
        )
        m2 = proj.analyze_projectile_speed(
            attempt=2,
            samples=proj.synthetic_projectile_series(speed=50.0),
            frequency=frequency,
        )
        with self.assertRaisesRegex(proj.ProjectileScaffoldError, "not stable"):
            proj.materialize_projectile_pair_envelope(m1, m2)


if __name__ == "__main__":
    unittest.main()
