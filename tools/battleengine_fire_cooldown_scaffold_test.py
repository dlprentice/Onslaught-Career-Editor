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

    def test_energy_drop_edges_recover_cooldown(self) -> None:
        frequency = 10_000_000
        step = frequency // 5  # 200 ms
        series: list[tuple[int, float]] = []
        energy = 2.5
        for i in range(6):
            series.append((i * step, energy))
            energy -= 0.15
        events = fire.fire_edges_from_energy_drops(series, min_drop=0.05)
        metrics = fire.analyze_fire_cooldown(
            attempt=1, events=events, frequency=frequency
        )
        self.assertTrue(metrics.accepted)
        self.assertAlmostEqual(200.0, metrics.median_cooldown_ms, delta=1.0)

    def test_pair_envelope(self) -> None:
        frequency = 10_000_000
        m1 = fire.analyze_fire_cooldown(
            attempt=1,
            events=fire.synthetic_fire_events(count=5, cooldown_ms=200.0),
            frequency=frequency,
        )
        m2 = fire.analyze_fire_cooldown(
            attempt=2,
            events=fire.synthetic_fire_events(count=5, cooldown_ms=210.0),
            frequency=frequency,
        )
        envelope = fire.materialize_fire_pair_envelope(m1, m2)
        self.assertEqual(
            "battleengine-fire-cooldown-scalar-response.v0-scaffold",
            envelope["schemaVersion"],
        )

    def test_pair_envelope_rejects_unstable(self) -> None:
        frequency = 10_000_000
        m1 = fire.analyze_fire_cooldown(
            attempt=1,
            events=fire.synthetic_fire_events(count=5, cooldown_ms=100.0),
            frequency=frequency,
        )
        m2 = fire.analyze_fire_cooldown(
            attempt=2,
            events=fire.synthetic_fire_events(count=5, cooldown_ms=300.0),
            frequency=frequency,
        )
        with self.assertRaisesRegex(fire.FireScaffoldError, "not stable"):
            fire.materialize_fire_pair_envelope(m1, m2)

    def test_rejects_too_few_events(self) -> None:
        events = fire.synthetic_fire_events(count=2)
        with self.assertRaisesRegex(fire.FireScaffoldError, "at least"):
            fire.analyze_fire_cooldown(attempt=1, events=events, frequency=10_000_000)


if __name__ == "__main__":
    unittest.main()
