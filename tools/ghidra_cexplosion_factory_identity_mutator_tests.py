#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
JAVA = ROOT / "tools" / "GhidraApplyCExplosionFactoryIdentity.java"
INSPECTOR = ROOT / "tools" / "GhidraInspectCExplosionFactoryIdentity.java"
OWNER = ROOT / "reverse-engineering" / "binary-analysis" / "cexplosion-factory-identity-promotion-2026-08-13.md"
MANIFEST = ROOT / "reverse-engineering" / "binary-analysis" / "cexplosion-factory-identity-promotion-2026-08-13.tsv"
REPROOF = ROOT / "local-lab" / "ghidra-cexplosion-identity-scratch-20260813-v7" / "reproof-v7" / "reproof.ready.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CExplosionFactoryIdentityMutatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = JAVA.read_text(encoding="utf-8")
        cls.inspector_text = INSPECTOR.read_text(encoding="utf-8")

    def test_evidence_pins_match(self) -> None:
        for label, path in (("OWNER", OWNER), ("MANIFEST", MANIFEST), ("REPROOF", REPROOF)):
            self.assertRegex(self.text, rf"{label}_BYTES = {path.stat().st_size};")
            self.assertIn(sha(path), self.text)

    def test_mutation_is_one_row_and_field_bounded(self) -> None:
        self.assertIn('private static final String ENTRY = "0x0050ff10";', self.text)
        self.assertIn("function.setName(POST_NAME, SourceType.USER_DEFINED);", self.text)
        self.assertIn("function.getParameters()[0].setName(POST_PARAMETER, SourceType.USER_DEFINED);", self.text)
        self.assertIn("function.setComment(POST_COMMENT);", self.text)
        self.assertIn("setTags(function, POST_TAGS);", self.text)
        self.assertNotIn("createFunction(", self.text)
        self.assertNotIn("removeFunction(", self.text)

    def test_abi_body_and_collision_guards_are_present(self) -> None:
        for needle in (
            "BODY_BYTES_SHA256", "BODY_RANGE_SHA256", "exactInstructions(body)",
            '"parameter storage", "Stack[0x4]:4"', '"return storage", "EAX:4"',
            '"parameter source", SourceType.USER_DEFINED, parameter.getSource()',
            "external interior references", "EXPECTED_CALLERS", "symbols at entry",
            "nameCount(POST_NAME)", "MEMORY_SHA256",
        ):
            self.assertIn(needle, self.text)

    def test_parameter_source_is_measured_and_restored_exactly(self) -> None:
        self.assertIn("final SourceType parameterSource;", self.text)
        self.assertIn("function.getParameters()[0].getSource(), function.getComment()", self.text)
        self.assertIn("setName(pre.parameter, pre.parameterSource);", self.text)
        self.assertIn('parameterStorage\\tparameterSource\\tcallingConvention', self.text)
        self.assertIn('"parameterSourcesChanged\\\": 0"', self.text)
        self.assertIn("parameters[0].getSource()", self.inspector_text)
        self.assertIn('"\\tparameterStorage\\tparameterSource\\tstackParameterBytes',
                      self.inspector_text)

    def test_ready_receipt_uses_only_repository_relative_internal_paths(self) -> None:
        self.assertIn("private static String repositoryRelative(", self.text)
        for needle in (
            'json(toolRelative)', 'json(OWNER_RELATIVE)', 'json(MANIFEST_RELATIVE)',
            'json(REPROOF_RELATIVE)', 'json(outputRelative)',
        ):
            self.assertIn(needle, self.text)
        ready_body = self.text[
            self.text.index("private byte[] buildReady(") :
            self.text.index("private void validateOuter(")
        ]
        self.assertNotIn("getCanonicalPath()", ready_body)
        self.assertNotIn("repositoryRelative(", ready_body)

    def test_output_and_ready_containment_precede_pre_validation_and_transaction(self) -> None:
        run_body = self.text[self.text.index("protected void run()") :]
        output_constructed = run_body.index('File output = newOutput(args[1], "output TSV")')
        ready_constructed = run_body.index('File ready = newOutput(args[2], "READY receipt")')
        output_contained = run_body.index(
            "String outputRelative = repositoryRelative(repositoryRoot, output)"
        )
        ready_contained = run_body.index(
            "String readyRelative = repositoryRelative(repositoryRoot, ready)"
        )
        pre_validated = run_body.index("validatePre();")
        transaction_started = run_body.index("currentProgram.startTransaction(")
        self.assertLess(output_constructed, output_contained)
        self.assertLess(ready_constructed, ready_contained)
        self.assertLess(output_contained, pre_validated)
        self.assertLess(ready_contained, pre_validated)
        self.assertLess(ready_contained, transaction_started)

    def test_external_output_and_ready_paths_fail_closed(self) -> None:
        guard = self.text[
            self.text.index("private static String repositoryRelative(") :
            self.text.index("private static File newOutput(")
        ]
        self.assertIn("require(target.startsWith(root)", guard)
        run_body = self.text[self.text.index("protected void run()") :]
        self.assertEqual(
            run_body.count("repositoryRelative(repositoryRoot, output)"), 1
        )
        self.assertEqual(
            run_body.count("repositoryRelative(repositoryRoot, ready)"), 1
        )

    def test_adverse_modes_publish_no_success_before_failure(self) -> None:
        after_one = self.text.index("CEXPLOSION_FACTORY_IDENTITY_FORCED_AFTER_ONE_FAILURE")
        post_inner = self.text.index("CEXPLOSION_FACTORY_IDENTITY_FORCED_POST_INNER_FAILURE")
        publish_apply = self.text.index("CEXPLOSION_FACTORY_IDENTITY_APPLY_COMPLETE")
        self.assertLess(after_one, publish_apply)
        self.assertLess(post_inner, publish_apply)
        self.assertIn("restorePre(pre);", self.text)
        self.assertIn("validatePre();", self.text[post_inner - 1000 : post_inner])

    def test_all_modes_are_explicit(self) -> None:
        for mode in ("dry", "probe-after-one", "probe-post-inner", "apply", "readback"):
            self.assertIn(f'"{mode}"', self.text)

    def test_post_comment_and_tags_are_exactly_bounded(self) -> None:
        self.assertIn("POST_COMMENT_BYTES = 915", self.text)
        self.assertIn("f512ec67c3b7851821c57906c16b08be05c45d3b525de08ebc27c244dabfc5a8", self.text)
        self.assertIn('"explosion", "factory", "identity-corrected"', self.text)
        post_tags = re.search(r"POST_TAGS = sorted\(Arrays\.asList\((.*?)\)\);", self.text, re.S)
        self.assertIsNotNone(post_tags)
        self.assertNotIn('"pickup"', post_tags.group(1))


if __name__ == "__main__":
    unittest.main()
