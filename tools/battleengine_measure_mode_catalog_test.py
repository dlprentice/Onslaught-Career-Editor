#!/usr/bin/env python3
"""Tests for measure mode catalog vs sampler MEASURE_MODES."""

from __future__ import annotations

import unittest

import battleengine_measure_mode_catalog as catalog
import battleengine_walker_trajectory_sampler as sampler


class MeasureModeCatalogTests(unittest.TestCase):
    def test_catalog_covers_sampler_modes(self) -> None:
        self.assertEqual(catalog.mode_names(), frozenset(sampler.MEASURE_MODES))

    def test_energy_offset_constants_present(self) -> None:
        self.assertEqual(0xFC, sampler.BATTLE_ENGINE_ENERGY_OFFSET)
        self.assertEqual(0x100, sampler.BATTLE_ENGINE_SHIELDS_OFFSET)

    def test_catalog_rows_nonempty(self) -> None:
        rows = catalog.catalog_as_dicts()
        self.assertEqual(6, len(rows))
        self.assertTrue(any(r["mode"] == "energy" for r in rows))
        shield = next(r for r in rows if r["mode"] == "shield")
        self.assertEqual("walker", shield["vehicle"])
        self.assertIn("live dual-accept pending", shield["liveStatus"])

    def test_offline_harness_rows_named(self) -> None:
        offline = catalog.offline_harness_dicts()
        names = {row["mode"] for row in offline}
        self.assertIn("coast", names)
        self.assertIn("camera-look", names)
        self.assertIn("fire-cooldown", names)
        self.assertIn("projectile-speed", names)
        self.assertNotIn("shield-rate", names)
        # Offline modes must not collide with live MEASURE_MODES.
        self.assertTrue(names.isdisjoint(catalog.mode_names()))

    def test_full_catalog_report_shape(self) -> None:
        report = catalog.full_catalog_report()
        self.assertEqual(6, len(report["liveMeasureModes"]))
        self.assertEqual(4, len(report["offlineHarnesses"]))
        energy = next(r for r in report["liveMeasureModes"] if r["mode"] == "energy")
        self.assertIn("dual-accepted", energy["liveStatus"])


if __name__ == "__main__":
    unittest.main()
