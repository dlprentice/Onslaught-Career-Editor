#!/usr/bin/env python3
"""Guard the public energy live dual-accept checklist."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = (
    ROOT
    / "reverse-engineering"
    / "game-mechanics"
    / "energy-live-dual-accept-checklist.md"
)


class EnergyLiveChecklistTests(unittest.TestCase):
    def test_checklist_present_with_procedure_tokens(self) -> None:
        self.assertTrue(CHECKLIST.is_file())
        text = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("measure energy", text)
        self.assertIn("0xFC", text)
        self.assertIn("materialize_energy_pair_envelope", text)
        self.assertIn("Do not commit GameProfiles", text)


if __name__ == "__main__":
    unittest.main()
