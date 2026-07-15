#!/usr/bin/env python3
"""Tests for energy rate scaffold."""

from __future__ import annotations

import unittest

import battleengine_energy_scaffold as energy


class EnergyScaffoldTests(unittest.TestCase):
    def test_offset_hypothesis_matches_sampler_constants(self) -> None:
        import battleengine_walker_trajectory_sampler as sampler

        self.assertEqual(0xFC, energy.BATTLE_ENGINE_ENERGY_OFFSET)
        self.assertEqual(0x100, energy.BATTLE_ENGINE_SHIELDS_OFFSET)
        self.assertEqual(
            energy.BATTLE_ENGINE_ENERGY_OFFSET, sampler.BATTLE_ENGINE_ENERGY_OFFSET
        )
        self.assertEqual(
            energy.BATTLE_ENGINE_SHIELDS_OFFSET, sampler.BATTLE_ENGINE_SHIELDS_OFFSET
        )

    def test_drain_accepts(self) -> None:
        samples = energy.synthetic_energy_series(rate_per_sec=-3.0)
        m = energy.analyze_energy_rate(
            attempt=1, samples=samples, frequency=10_000_000, expect_negative=True
        )
        self.assertTrue(m.accepted)
        self.assertLess(m.steady_rate_per_sec, -1.0)

    def test_regen_accepts(self) -> None:
        samples = energy.synthetic_energy_series(rate_per_sec=4.0)
        m = energy.analyze_energy_rate(
            attempt=1, samples=samples, frequency=10_000_000, expect_negative=False
        )
        self.assertTrue(m.accepted)
        self.assertGreater(m.steady_rate_per_sec, 1.0)

    def test_pair_envelope_for_drain(self) -> None:
        frequency = 10_000_000
        m1 = energy.analyze_energy_rate(
            attempt=1,
            samples=energy.synthetic_energy_series(rate_per_sec=-3.0),
            frequency=frequency,
            expect_negative=True,
        )
        m2 = energy.analyze_energy_rate(
            attempt=2,
            samples=energy.synthetic_energy_series(rate_per_sec=-3.1),
            frequency=frequency,
            expect_negative=True,
        )
        envelope = energy.materialize_energy_pair_envelope(m1, m2)
        self.assertEqual(
            "battleengine-energy-rate-scalar-response.v0-scaffold",
            envelope["schemaVersion"],
        )
        band = envelope["envelope"]["steadyEnergyRatePerSec"]
        self.assertLess(band["lower"], band["upper"])
        self.assertEqual("0xfc", envelope["offsetHypothesis"]["battleEngineEnergy"])


if __name__ == "__main__":
    unittest.main()
