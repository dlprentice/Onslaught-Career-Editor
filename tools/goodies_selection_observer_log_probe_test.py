#!/usr/bin/env python3
"""Focused tests for goodies_selection_observer_log_probe.py."""

from __future__ import annotations

from pathlib import Path
import unittest

import goodies_selection_observer_log_probe as probe


ROOT = Path(__file__).resolve().parents[1]
COMMAND_FILE = ROOT / "tools" / "runtime-probes" / "goodies-selection-observer.cdb.txt"
INPUT_COMMAND_FILE = ROOT / "tools" / "runtime-probes" / "goodies-input-observer.cdb.txt"


class GoodiesSelectionObserverLogProbeTests(unittest.TestCase):
    def test_normal_sequence_report_tracks_coordinates_and_returns(self) -> None:
        report = probe.build_report_from_text(
            "\n".join(
                [
                    "Goodies get_goodie_number x=8 y=0 ret=66",
                    "Goodies get_goodie_number x=9 y=0 ret=67",
                    "Goodies get_goodie_number x=10 y=0 ret=68",
                    "Goodies get_goodie_number x=11 y=0 ret=69",
                    "Goodies get_goodie_number x=12 y=0 ret=70",
                    "Goodies right-probe-after-clamp this=0012ff00 mCX=13 mCY=0",
                    "Goodies get_goodie_number x=13 y=0 ret=74",
                    "Goodies selected-load-gate this=0012ff00 mCX=13 mCY=0",
                    "Goodies StartLoadingGoody this=0012ff00 mCX=13 mCY=0",
                ]
            )
        )

        self.assertEqual("PASS", report["status"])
        self.assertEqual("NORMAL_SEQUENCE_CONFIRMED", report["verdict"])
        self.assertEqual([66, 67, 68, 69, 70, 74], report["returnedGoodieIds"])
        self.assertTrue(report["expectedNormalSequenceObserved"])
        self.assertEqual([], report["hiddenReturnIds"])
        self.assertTrue(report["inputPathObserved"])
        self.assertEqual(0, report["buttonEventCount"])
        self.assertEqual(6, report["coordinateSampleCount"])
        self.assertEqual(3, report["navigationEventCount"])
        self.assertEqual(0, report["debuggerSkippedCommandWarningCount"])

    def test_hidden_ids_are_reported_not_lost(self) -> None:
        report = probe.build_report_from_text(
            "\n".join(
                [
                    "Goodies get_goodie_number x=12 y=0 ret=70",
                    "Goodies get_goodie_number x=13 y=0 ret=71",
                    "Goodies StartLoadingGoody this=0012ff00 mCX=13 mCY=0",
                ]
            )
        )

        self.assertEqual("PASS", report["status"])
        self.assertEqual("HIDDEN_IDS_OBSERVED", report["verdict"])
        self.assertEqual([71], report["hiddenReturnIds"])
        self.assertFalse(report["expectedNormalSequenceObserved"])

    def test_focused_input_observer_events_can_confirm_normal_sequence(self) -> None:
        report = probe.build_report_from_text(
            "\n".join(
                [
                    "Goodies ButtonPressed entry button=44 this=0012ff00 mCX=8 mCY=0",
                    "Goodies right-probe-after-clamp ret=66 this=0012ff00 mCX=8 mCY=0",
                    "Goodies ButtonPressed entry button=44 this=0012ff00 mCX=9 mCY=0",
                    "Goodies right-probe-after-clamp ret=67 this=0012ff00 mCX=9 mCY=0",
                    "Goodies ButtonPressed entry button=44 this=0012ff00 mCX=10 mCY=0",
                    "Goodies right-probe-after-clamp ret=68 this=0012ff00 mCX=10 mCY=0",
                    "Goodies selected-load-gate ret=69 this=0012ff00 mCX=11 mCY=0",
                    "Goodies post-load-state-check ret=70 this=0012ff00 mCX=12 mCY=0",
                    "Goodies mark-selected-old ret=74 this=0012ff00 mCX=13 mCY=0",
                ]
            )
        )

        self.assertEqual("PASS", report["status"])
        self.assertEqual("NORMAL_SEQUENCE_CONFIRMED", report["verdict"])
        self.assertTrue(report["inputPathObserved"])
        self.assertEqual(3, report["buttonEventCount"])
        self.assertEqual(6, report["navigationEventCount"])
        self.assertEqual([66, 67, 68, 69, 70, 74], report["returnedGoodieIds"])

    def test_debugger_skipped_command_warnings_are_counted(self) -> None:
        report = probe.build_report_from_text(
            "\n".join(
                [
                    "Some commands were skipped because previous commands caused target execution inside an event handler.Goodies get_goodie_number x=8 y=0 ret=66",
                    "Some commands were skipped because previous commands caused target execution inside an event handler.Goodies get_goodie_number x=9 y=0 ret=67",
                ]
            )
        )

        self.assertEqual(2, report["debuggerSkippedCommandWarningCount"])
        self.assertFalse(report["inputPathObserved"])

    def test_multiple_cdb_events_on_one_line_are_all_parsed(self) -> None:
        report = probe.build_report_from_text(
            "Goodies ButtonPressed entry button=55 this=0012ff00 mCX=12 mCY=0 "
            "Goodies right-probe-after-clamp ret=70 this=0012ff00 mCX=12 mCY=0 "
            "Goodies ButtonPressed entry button=55 this=0012ff00 mCX=13 mCY=0 "
            "Goodies right-probe-after-clamp ret=74 this=0012ff00 mCX=13 mCY=0"
        )

        self.assertEqual("PASS", report["status"])
        self.assertEqual([70, 74], report["returnedGoodieIds"])
        self.assertEqual(2, report["buttonEventCount"])
        self.assertEqual(2, report["navigationEventCount"])

    def test_cdb_observer_command_file_matches_parser_contract(self) -> None:
        text = COMMAND_FILE.read_text(encoding="utf-8")

        self.assertIn("bp 0045cb80", text)
        self.assertIn("Goodies get_goodie_number x=%d y=%d ret=%d", text)
        self.assertIn("bp 0045cf2a", text)
        self.assertIn("Goodies right-probe-after-clamp", text)
        self.assertIn("bp 0045cf4c", text)
        self.assertIn("Goodies right-backtrack-scan", text)
        self.assertIn("bp 0045d070", text)
        self.assertIn("Goodies selected-load-gate", text)
        self.assertIn("bp 0045c9f0", text)
        self.assertIn("Goodies StartLoadingGoody", text)

    def test_focused_input_observer_avoids_hot_mapper_breakpoint(self) -> None:
        text = INPUT_COMMAND_FILE.read_text(encoding="utf-8")

        self.assertIn("bp 0045cde0", text)
        self.assertIn("Goodies ButtonPressed entry", text)
        self.assertNotIn("bp 0045cb80", text)
        self.assertIn("bp 0045cf2f", text)
        self.assertIn("Goodies right-probe-after-clamp ret=%d", text)
        self.assertIn("bp 0045d075", text)
        self.assertIn("Goodies selected-load-gate ret=%d", text)
        self.assertIn("bp 0045d0d2", text)
        self.assertIn("Goodies mark-selected-old ret=%d", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
