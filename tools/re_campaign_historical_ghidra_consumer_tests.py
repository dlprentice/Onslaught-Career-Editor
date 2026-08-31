#!/usr/bin/env python3
"""Focused tests for campaign consumers of retired historical Ghidra trees."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import re_campaign as campaign  # noqa: E402


class HistoricalGhidraCampaignConsumerTests(unittest.TestCase):
    def test_sealed_unsetobjective_campaign_no_longer_reads_a_database(self) -> None:
        proof_root = (
            campaign.REPO_ROOT
            / campaign.MISSION_NATIVE_UNSETOBJECTIVE_PROOF_RELATIVE
        )
        with patch.object(
            campaign.mission_unsetobjective_reproof,
            "derive",
            side_effect=AssertionError("database derivation must not run"),
        ):
            result = campaign._validate_mission_native_unsetobjective_inputs(
                proof_root
            )
        self.assertEqual(
            campaign.MISSION_NATIVE_UNSETOBJECTIVE_PROOF_READY_SHA256,
            result["proofStamp"]["sha256"],
        )

    def test_new_unsetobjective_advance_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "must-not-exist"
            with self.assertRaisesRegex(campaign.CampaignError, "frozen one-shot"):
                campaign.advance_mission_native_unsetobjective_reproof(
                    Path("unused-campaign"), Path("unused-proof"), out
                )
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
