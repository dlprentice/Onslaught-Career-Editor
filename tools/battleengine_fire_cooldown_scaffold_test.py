#!/usr/bin/env python3
"""Unit tests for fire cooldown scaffold."""

from __future__ import annotations

import unittest

import battleengine_fire_cooldown_scaffold as fire


class FireScaffoldTests(unittest.TestCase):
    def test_synthetic_accepts(self) -> None:
        events = fire.synthetic_fire_events(count=5, cooldown_ms=200.0)
        m = fire.analyze_fire_cooldown(attempt=1, events=events, frequency=10_000_000)
        self.assertTrue(m.accepted)
        self.assertEqual(5, m.event_count)
        self.assertAlmostEqual(200.0, m.median_cooldown_ms, delta=1.0)

    def test_rejects_too_few_events(self) -> None:
        events = fire.synthetic_fire_events(count=2)
        with self.assertRaisesRegex(fire.FireScaffoldError, "at least"):
            fire.analyze_fire_cooldown(attempt=1, events=events, frequency=10_000_000)


if __name__ == "__main__":
    unittest.main()
