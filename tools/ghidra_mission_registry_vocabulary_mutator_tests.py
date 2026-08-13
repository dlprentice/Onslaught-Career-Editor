#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
JAVA = REPO / "tools/GhidraApplyMissionRegistryVocabulary.java"


class VocabularyMutatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = JAVA.read_text(encoding="utf-8")

    def test_target_specific_modes_only(self):
        for mode in ("dry", "probe-after-one", "probe-post-inner", "apply", "readback"):
            self.assertIn('"' + mode + '"', self.text)
        self.assertIn("TARGET_COUNT = 75", self.text)
        self.assertIn("DEFAULT_COUNT = 54", self.text)
        self.assertIn("MSG_COUNT = 5", self.text)
        self.assertIn("CLASS3_COUNT = 16", self.text)

    def test_only_metadata_mutation_apis_are_present(self):
        for allowed in ("function.setName(", "function.setComment(",
                        "function.addTag(", "function.removeTag(", "tag.delete()"):
            self.assertIn(allowed, self.text)
        forbidden = ("createFunction(", "removeFunction(", "updateFunction(",
                     "setBody(", "setReturn(", "replaceParameters(",
                     "setCallingConvention(", "setCustomVariableStorage(",
                     "clearListing(", "disassemble(")
        for value in forbidden:
            self.assertNotIn(value, self.text)

    def test_compensating_restore_handles_default_names_comments_tags_and_catalog(self):
        self.assertIn("function.setName(pre.name, pre.nameSource)", self.text)
        self.assertIn("pre.commentPresent ? pre.comment : null", self.text)
        self.assertIn("removeCreatedTier2TagDefinition", self.text)
        self.assertIn("COMPENSATING_PRE_RESTORE_COMPLETE", self.text)
        self.assertIn("COMPENSATING_PRE_RESTORE_VERIFIED", self.text)

    def test_catalog_is_exactly_pinned_pre_and_post(self):
        for value in ("PRE_TAG_CATALOG_COUNT = 6853", "POST_TAG_CATALOG_COUNT = 6854",
                      "script-command-registry", "tier2-script-facing-name",
                      "validateTagCatalog(false)", "validateTagCatalog(true)"):
            self.assertIn(value, self.text)

    def test_empty_tag_sets_require_explicit_sentinel(self):
        self.assertIn('EMPTY_TAGS_SENTINEL = "<EMPTY>"', self.text)
        self.assertIn("PRE tag field must use explicit empty sentinel", self.text)
        self.assertIn('row[9].equals(EMPTY_TAGS_SENTINEL)', self.text)

    def test_msg5_replaces_comments_and_removes_only_refuted_tags(self):
        self.assertIn('if (target.cohort.equals("MSG5")) return messageComment(target)',
                      self.text)
        self.assertIn('target.index == 28) result.remove("callback-message")', self.text)
        self.assertIn('target.index == 36 || target.index == 91) result.remove("fade-event")',
                      self.text)
        self.assertIn("unreviewed MSG5 index", self.text)
        self.assertIn("priority-message` is retained", self.text)
        self.assertIn("`scheduled-event-7d1` remain", self.text)
        self.assertIn('"tagAssociationsRemoved\\\": 3', self.text)

    def test_abi_and_body_are_observed_but_never_written(self):
        self.assertIn("body/instruction invariant", self.text)
        self.assertIn("ABI/storage invariant", self.text)
        self.assertIn("instructionLayoutSha256", self.text)
        self.assertRegex(self.text, r"Parameter\[\] parameters = function\.getParameters\(\)")

    def test_no_live_or_backup_path_is_embedded(self):
        self.assertNotIn(r"C:\Users\david\Ghidra", self.text)
        self.assertNotIn("BEA-Ghidra-Backups", self.text)
        self.assertNotIn("reverse-engineering/ghidra/BEA", self.text)


if __name__ == "__main__":
    unittest.main()
