#!/usr/bin/env python3
"""Tests for campaign scalar status reporter."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "battleengine_campaign_scalar_status.py"


class CampaignScalarStatusTests(unittest.TestCase):
    def test_reports_dual_accepted_contracts(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        names = {row["name"] for row in payload["scalars"]}
        self.assertIn("walker-forward", names)
        self.assertIn("energy-rate", names)
        dual = [r for r in payload["scalars"] if r["status"] == "dual-accepted"]
        self.assertEqual(6, len(dual))
        self.assertTrue(all(r.get("present") for r in dual))
        self.assertIn("energy-rate", {r["name"] for r in dual})
        shield_scalar = next(r for r in payload["scalars"] if r["name"] == "shield-rate")
        self.assertEqual(
            "sampler-wired+neutral-control-correlation+offset; live pair pending",
            shield_scalar["status"],
        )
        offline = payload.get("offlineHarnesses") or []
        self.assertEqual(4, len(offline))
        self.assertIn("coast", {row["mode"] for row in offline})
        live = payload.get("liveMeasureModes") or []
        self.assertEqual(6, len(live))
        shield = next(row for row in live if row["mode"] == "shield")
        self.assertIn("live dual-accept pending", shield["liveStatus"])


if __name__ == "__main__":
    unittest.main()
