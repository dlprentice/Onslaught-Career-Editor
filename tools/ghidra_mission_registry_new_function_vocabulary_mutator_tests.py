#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
JAVA = REPO / "tools/GhidraApplyMissionRegistryNewFunctionVocabulary.java"


class NewFunctionVocabularyMutatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = JAVA.read_text(encoding="utf-8")

    def test_exact_cohort_and_modes(self) -> None:
        self.assertIn("TARGET_COUNT = 34", self.text)
        self.assertIn('"NEW34_STATIC_C1"', self.text)
        for mode in ("dry", "probe-after-one", "probe-post-inner", "apply", "readback"):
            self.assertIn(f'"{mode}"', self.text)
        for stale in ("DEFAULT_COUNT", "MSG_COUNT", "CLASS3_COUNT", "targets=75"):
            self.assertNotIn(stale, self.text)

    def test_only_name_comment_and_tag_association_writes_exist(self) -> None:
        for allowed in ("function.setName(", "function.setComment(",
                        "function.addTag(", "function.removeTag("):
            self.assertIn(allowed, self.text)
        for forbidden in ("createFunction(", "removeFunction(", "updateFunction(",
                          "setBody(", "setReturn(", "replaceParameters(",
                          "setCallingConvention(", "setCustomVariableStorage(",
                          "clearListing(", "disassemble(", "tag.delete()"):
            self.assertNotIn(forbidden, self.text)

    def test_static_contract_is_loaded_verbatim_with_claim_limits(self) -> None:
        for value in ("STATIC_HYPOTHESIS_ONLY", "C1_CANDIDATE_PARTIAL",
                      "registry-label relation", "Remaining unknowns:",
                      "Cheapest falsifier:", "No runtime reachability",
                      "reconstruction parity is admitted"):
            self.assertIn(value, self.text)
        self.assertIn("not a recovered C++ symbol", self.text)
        self.assertIn("not a recovered C++ symbol or", self.text)

    def test_abi_body_and_parameter_source_are_observed_never_written(self) -> None:
        self.assertIn("body/instruction invariant", self.text)
        self.assertIn("ABI/storage invariant", self.text)
        self.assertIn("parameter.getSource()", self.text)
        self.assertIn("function.getSignatureSource()", self.text)
        self.assertIn("function.getReturn().getVariableStorage()", self.text)

    def test_compensation_restores_exact_pre_without_deleting_existing_tags(self) -> None:
        self.assertIn("function.setName(pre.name, pre.nameSource)", self.text)
        self.assertIn("pre.commentPresent ? pre.comment : null", self.text)
        self.assertIn("COMPENSATING_PRE_RESTORE_COMPLETE", self.text)
        self.assertIn("COMPENSATING_PRE_RESTORE_VERIFIED", self.text)
        self.assertNotIn("removeCreatedTier2TagDefinition", self.text)

    def test_existing_catalog_is_exactly_pinned_pre_and_post(self) -> None:
        for value in ("PRE_TAG_CATALOG_COUNT = 6854", "POST_TAG_CATALOG_COUNT = 6854",
                      "0ac85baaf38153328266bf4c54178f44ad871f273dabba03dfd13aaf4ded1a97",
                      "0cbec4d3c190f2df8be5a3bd67ceeeaa419d3d5d9b20602b7ff9e400ade12971",
                      "post ? 128 : 94", "post ? 109 : 75"):
            self.assertIn(value, self.text)

    def test_external_outputs_are_rejected_before_pre_validation_or_transaction(self) -> None:
        output_preflight = self.text.index("String outputRelative = repositoryRelative(root, out)")
        load_targets = self.text.index("List<Target> targets = loadTargets(root)")
        pre_validation = self.text.index("pre.add(validatePre(target))")
        transaction = self.text.index("currentProgram.startTransaction(")
        self.assertLess(output_preflight, load_targets)
        self.assertLess(output_preflight, pre_validation)
        self.assertLess(output_preflight, transaction)
        self.assertIn("String readyRelative = repositoryRelative(root, receipt)", self.text)

    def test_no_live_backup_or_canonical_project_path_is_embedded(self) -> None:
        for forbidden in (r"C:\Users\david\Ghidra", "BEA-Ghidra-Backups",
                          "reverse-engineering/ghidra/BEA"):
            self.assertNotIn(forbidden, self.text)


if __name__ == "__main__":
    unittest.main()
