#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks for tools/script_tables.py: the committed C# tables are the reference's tables, read back from the file itself (not from what
the generator would write), so a stale or hand-edited file is caught either way."""
from __future__ import annotations

import re
import unittest

import script_tables as tables
import world_resources_decode as wrd


class ScriptTables(unittest.TestCase):
    def setUp(self):
        self.text = tables.OUTPUT.read_text(encoding="utf-8")

    def test_the_committed_file_is_what_the_generator_writes(self):
        self.assertEqual(self.text, tables.render())

    def test_the_events_in_the_file_are_the_references(self):
        block = self.text.split("EventNames =")[1].split("];")[0]
        self.assertEqual(re.findall(r'"([a-z_0-9]+)"', block), list(wrd.SCRIPT_EVENT_NAMES))
        self.assertEqual(len(wrd.SCRIPT_EVENT_NAMES), wrd.NUM_SCRIPT_EVENTS)
        self.assertEqual(wrd.SCRIPT_EVENT_NAMES[:5], ("init", "arrived", "timer", "died", "hit"))

    def test_the_natives_in_the_file_are_the_references_in_call_order(self):
        block = self.text.split("Natives =")[1]
        self.assertEqual(re.findall(r'\("([A-Za-z0-9_]+)", "([a-z*]*)"\)', block), list(wrd.SCRIPT_NATIVES))

    def test_a_call_instruction_can_name_every_native(self):
        self.assertLessEqual(len(wrd.SCRIPT_NATIVES), 256)  # the call attribute's low byte
        self.assertEqual(len({name for name, _types in wrd.SCRIPT_NATIVES}), len(wrd.SCRIPT_NATIVES))
        self.assertTrue(all(set(types) <= set("ifsbtp*") for _name, types in wrd.SCRIPT_NATIVES))

    def test_the_file_has_no_game_bytes_only_names(self):
        self.assertNotIn("\r", self.text)
        self.assertTrue(self.text.startswith("// SPDX-License-Identifier: GPL-3.0-only\n"))


if __name__ == "__main__":
    unittest.main()
